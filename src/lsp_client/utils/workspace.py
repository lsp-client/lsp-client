from __future__ import annotations

import os
from collections.abc import Mapping
from functools import cached_property
from pathlib import Path
from typing import Final

import attrs
import xxhash

from .types import AnyPath, lsp_type
from .uri import from_local_uri


@attrs.define
class WorkspaceFolder(lsp_type.WorkspaceFolder):
    """
    Represents a workspace folder in the LSP protocol.

    Extends the base LSP WorkspaceFolder with additional properties for
    working with file paths. Provides a cached property for converting
    the URI to a local filesystem path.

    Attributes:
        uri: The URI of the workspace folder
        name: The name of the workspace folder

    Properties:
        path: Returns the local filesystem Path for this workspace folder
    """

    @cached_property
    def path(self) -> Path:
        return from_local_uri(self.uri)


class Workspace(dict[str, WorkspaceFolder]):
    """
    A dictionary mapping workspace folder names to their configurations.

    Provides workspace management functionality for LSP clients, supporting
    multiple workspace folders. Inherits from dict for standard dictionary
    operations while providing LSP-specific helper methods.

    Example:
        workspace = Workspace({
            "root": WorkspaceFolder(uri="file:///project", name="root"),
            "lib": WorkspaceFolder(uri="file:///project/lib", name="lib")
        })
        folders = workspace.to_folders()  # Returns list of WorkspaceFolder
    """

    def to_folders(self) -> list[WorkspaceFolder]:
        return list(self.values())

    @cached_property
    def id(self) -> str:
        items = sorted(self.items())
        return xxhash.xxh32_hexdigest(
            "|".join(f"{name}:{folder.uri}" for name, folder in items)
        )


DEFAULT_WORKSPACE_PATH = Path.cwd()
DEFAULT_WORKSPACE_DIR: Final = "__root__"
DEFAULT_WORKSPACE: Final[Workspace] = Workspace(
    {
        DEFAULT_WORKSPACE_DIR: WorkspaceFolder(
            uri=Path.cwd().as_uri(),
            name=DEFAULT_WORKSPACE_DIR,
        )
    }
)

type RawWorkspace = AnyPath | Mapping[str, AnyPath] | Workspace


def format_workspace(raw: RawWorkspace) -> Workspace:
    match raw:
        case str() | os.PathLike() as root_folder_path:
            return Workspace(
                {
                    DEFAULT_WORKSPACE_DIR: WorkspaceFolder(
                        uri=Path(root_folder_path).as_uri(),
                        name="root",
                    )
                }
            )
        case Workspace() as ws:
            return ws
        case _ as mapping:
            return Workspace(
                {
                    name: WorkspaceFolder(uri=Path(path).as_uri(), name=name)
                    for name, path in mapping.items()
                }
            )
