from __future__ import annotations

import subprocess
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Literal, final, override

import anyio
from anyio.abc import AnyByteReceiveStream, AnyByteSendStream
from attrs import Factory, define, field
from loguru import logger

from lsp_client.utils.workspace import Workspace

from .abc import StreamServer
from .local import LocalServer


@define
class MountBase:
    type: str
    target: str
    source: str | None = None
    readonly: bool = False

    def _parts(self) -> list[str]:
        parts = [f"type={self.type}"]
        if self.source:
            parts.append(f"source={self.source}")
        parts.append(f"target={self.target}")
        if self.readonly:
            parts.append("readonly")
        return parts

    def __str__(self) -> str:
        return ",".join(self._parts())


@define
class BindMount(MountBase):
    type: str = "bind"

    bind_propagation: (
        Literal["private", "rprivate", "shared", "rshared", "slave", "rslave"] | None
    ) = None

    def _parts(self) -> list[str]:
        parts = super()._parts()
        if self.bind_propagation:
            parts.append(f"bind-propagation={self.bind_propagation}")

        return parts

    @classmethod
    def from_path(
        cls, path: Path, readonly: bool = False, target: str | None = None
    ) -> BindMount:
        absolute_path = path.resolve()
        source = str(absolute_path)

        if target is None:
            posix_path = absolute_path.as_posix()
            if absolute_path.drive:
                # Handle Windows drive letters: C:/path -> /c/path
                drive = absolute_path.drive.rstrip(":").lower()
                path_without_drive = posix_path[len(absolute_path.drive) :]
                if not path_without_drive.startswith("/"):
                    path_without_drive = "/" + path_without_drive
                target = f"/{drive}{path_without_drive}"
            else:
                target = posix_path

        return cls(source=source, target=target, readonly=readonly)


@define
class VolumeMount(MountBase):
    type: str = "volume"

    volume_driver: str | None = None
    volume_subpath: str | None = None
    volume_nocopy: bool = False
    volume_opt: list[str] | None = None

    def _parts(self) -> list[str]:
        parts = super()._parts()

        if self.volume_driver:
            parts.append(f"volume-driver={self.volume_driver}")
        if self.volume_subpath:
            parts.append(f"volume-subpath={self.volume_subpath}")
        if self.volume_nocopy:
            parts.append("volume-nocopy")
        if self.volume_opt:
            for opt in self.volume_opt:
                parts.append(f"volume-opt={opt}")

        return parts


@define
class TmpfsMount(MountBase):
    type: str = "tmpfs"

    tmpfs_size: int | None = None
    tmpfs_mode: int | None = None

    def _parts(self) -> list[str]:
        parts = super()._parts()

        if self.tmpfs_size is not None:
            parts.append(f"tmpfs-size={self.tmpfs_size}")
        if self.tmpfs_mode is not None:
            parts.append(f"tmpfs-mode={oct(self.tmpfs_mode)}")

        return parts


MountPoint = BindMount | VolumeMount | TmpfsMount

Mount = MountPoint | str | Path


def _format_mount(mount: Mount) -> str:
    if isinstance(mount, Path):
        mount = BindMount.from_path(mount)
    return str(mount)


@final
@define
class ContainerServer(StreamServer):
    """Runtime for container backend, e.g. `docker` or `podman`."""

    image: str
    """The container image to use."""

    workdir: str | None = None
    """The working directory inside the container."""

    mounts: list[Mount] = Factory(list)
    """List of extra mounts to be mounted inside the container."""

    backend: Literal["docker", "podman"] = "docker"
    """The container backend to use. Can be either `docker` or `podman`."""

    container_name: str | None = None
    """Optional name for the container."""

    extra_container_args: list[str] | None = None
    """Extra arguments to pass to the container runtime."""

    cache: bool = True
    """Whether to reuse an existing container if one exists."""

    _local: LocalServer = field(init=False)

    @property
    @override
    def send_stream(self) -> AnyByteSendStream:
        return self._local.send_stream

    @property
    @override
    def receive_stream(self) -> AnyByteReceiveStream:
        return self._local.receive_stream

    @override
    async def kill(self) -> None:
        await self._local.kill()

    def _generate_hash_name(self, workspace: Workspace) -> str:
        """Generate a deterministic container name for a workspace.

        The name is derived from the workspace ID so that the same workspace
        gets the same container name across sessions, enabling container reuse
        when auto_remove is disabled.
        """
        return f"lsp-server-{workspace.id}"

    async def _container_exists(self, name: str) -> bool:
        """
        Return True only if a container with the given name exists and is in a state
        suitable for reuse (i.e. can be started with `start -ai`).
        """
        try:
            # Query the container's state; Docker/Podman expose it via .State.Status
            result = await anyio.run_process(
                [self.backend, "inspect", "--format={{.State.Status}}", name],
                stdout=subprocess.PIPE,
                stderr=subprocess.DEVNULL,
            )
        except (anyio.ProcessError, FileNotFoundError):
            # Container does not exist or backend is unavailable.
            return False

        state = (result.stdout or b"").decode().strip().lower()
        if state in ("exited", "created"):
            return True

        logger.debug(
            "Container '{}' exists but is in state '{}' which is not suitable for reuse",
            name,
            state or "<unknown>",
        )
        return False

    def _get_expected_mount_targets(self, workspace: Workspace) -> set[str]:
        """
        Get the set of expected mount targets for the current workspace.

        Returns a set of target paths that should be mounted.
        """
        mounts = list(self.mounts)
        folders = workspace.to_folders()

        mounts.extend(
            BindMount.from_path(
                folder.path, readonly=True, target=folder.path.as_posix()
            )
            for folder in folders
        )

        targets = set()
        for mount in mounts:
            if isinstance(mount, Path):
                mount_obj = BindMount.from_path(mount)
                targets.add(mount_obj.target)
            elif isinstance(mount, str):
                # Parse mount string to extract target
                # Format: type=...,source=...,target=...,readonly
                parts = mount.split(",")
                for part in parts:
                    if part.startswith("target="):
                        targets.add(part.split("=", 1)[1])
                        break
            else:
                targets.add(mount.target)

        return targets

    @override
    async def check_availability(self) -> None:
        try:
            await anyio.run_process(
                [self.backend, "pull", self.image],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
        except anyio.ProcessError as e:
            raise RuntimeError(
                f"Container backend '{self.backend}' is not available or image '{self.image}' "
                "could not be pulled."
            ) from e

    def _get_effective_workdir(self, workspace: Workspace) -> str:
        if self.workdir:
            return self.workdir

        folders = workspace.to_folders()
        if len(folders) == 1:
            return folders[0].path.as_posix()

        raise ValueError(
            "Must specify 'workdir' when multiple or no workspace folders are provided."
        )

    def format_args(self, workspace: Workspace) -> list[str]:
        args = ["run", "-i", "--rm"]

        name = self.container_name or self._generate_hash_name(workspace)
        args.extend(("--name", name))

        args.extend(("--workdir", self._get_effective_workdir(workspace)))

        mounts = list(self.mounts)
        folders = workspace.to_folders()

        mounts.extend(
            BindMount.from_path(
                folder.path, readonly=True, target=folder.path.as_posix()
            )
            for folder in folders
        )

        for mount in mounts:
            args.extend(("--mount", _format_mount(mount)))

        if self.extra_container_args:
            args.extend(self.extra_container_args)

        args.append(self.image)

        return args

    @override
    async def setup(self, workspace: Workspace) -> None:
        if self.cache:
            name = self.container_name or self._generate_hash_name(workspace)
            if await self._container_exists(name):
                logger.debug("Reusing existing container: {}", name)
                self._local = LocalServer(
                    program=self.backend, args=["start", "-ai", name]
                )
                return

        args = self.format_args(workspace)
        logger.debug("Running container runtime with command: {}", args)
        self._local = LocalServer(program=self.backend, args=args)

    @override
    @asynccontextmanager
    async def manage_resources(self, workspace: Workspace) -> AsyncGenerator[None]:
        async with self._local.run_process(workspace):
            yield
