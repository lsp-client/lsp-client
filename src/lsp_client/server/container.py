from __future__ import annotations

import subprocess
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Literal, final, override

import aioshutil
import anyio
from anyio.abc import AnyByteReceiveStream, AnyByteSendStream
from attrs import Factory, define, field
from loguru import logger

from lsp_client.utils.workspace import Workspace

from .abc import StreamServer
from .error import ServerRuntimeError
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
            target = absolute_path.as_posix()

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

    backend: Literal["docker", "podman", "nerdctl"] | str = "docker"
    """The container backend to use. Can be `docker`, `podman`, `nerdctl` or any OCI-compliant CLI."""

    container_name: str | None = None
    """Optional name for the container."""

    extra_container_args: list[str] | None = None
    """Extra arguments to pass to the container runtime."""

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

    @override
    async def check_availability(self) -> None:
        if not await aioshutil.which(self.backend):
            raise ServerRuntimeError(
                self, f"Container backend '{self.backend}' not found in PATH."
            )

        try:
            await anyio.run_process([self.backend, "image", "inspect", self.image])
        except subprocess.CalledProcessError:
            logger.info("Pulling container image: {}", self.image)
            try:
                await anyio.run_process([self.backend, "pull", self.image])
            except subprocess.CalledProcessError as e:
                raise ServerRuntimeError(
                    self,
                    f"Container backend '{self.backend}' failed to pull image '{self.image}'.",
                ) from e

    def _get_effective_workdir(self, workspace: Workspace) -> str:
        if self.workdir:
            return self.workdir

        match workspace.to_folders():
            case [folder]:
                return BindMount.from_path(folder.path).target
            case _:
                raise ValueError(
                    "Must specify 'workdir' when multiple or no workspace folders are provided."
                )

    def format_args(self, workspace: Workspace) -> list[str]:
        args = ["run", "-i", "--rm"]

        if self.container_name:
            args.extend(("--name", self.container_name))

        args.extend(("--workdir", self._get_effective_workdir(workspace)))

        mounts = list(self.mounts)
        folders = workspace.to_folders()

        mounts.extend(BindMount.from_path(folder.path) for folder in folders)

        for mount in mounts:
            args.extend(("--mount", _format_mount(mount)))

        if self.extra_container_args:
            args.extend(self.extra_container_args)

        args.append(self.image)

        return args

    @override
    async def setup(self, workspace: Workspace) -> None:
        args = self.format_args(workspace)
        logger.debug("Running container runtime with command: {}", args)
        self._local = LocalServer(program=self.backend, args=args)

    @override
    @asynccontextmanager
    async def manage_resources(self, workspace: Workspace) -> AsyncGenerator[None]:
        async with self._local.run_process(workspace):
            yield
