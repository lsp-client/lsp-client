from __future__ import annotations

import contextlib
from collections.abc import AsyncGenerator
from pathlib import Path

import pytest

from lsp_client.client.document_state import DocumentStateManager
from lsp_client.protocol.client import CapabilityClientProtocol
from lsp_client.protocol.lang import LanguageConfig
from lsp_client.utils.config import ConfigurationMap
from lsp_client.utils.types import AnyPath, Notification, Request, Response, lsp_type
from lsp_client.utils.workspace import WORKSPACE_ROOT_DIR, Workspace, WorkspaceFolder


class MockClient(CapabilityClientProtocol):
    def __init__(self, workspace: Workspace):
        self.workspace = workspace
        self.config_map = ConfigurationMap()
        self.document_state = DocumentStateManager()

    def get_document_state(self) -> DocumentStateManager:
        return self.document_state

    def get_workspace(self) -> Workspace:
        return self.workspace

    def get_config_map(self) -> ConfigurationMap:
        return self.config_map

    @classmethod
    def get_language_config(cls) -> LanguageConfig:
        return LanguageConfig(
            kind=lsp_type.LanguageKind.Python,
            suffixes=[".py"],
            project_files=["pyproject.toml"],
        )

    @contextlib.asynccontextmanager
    async def open_files(self, *file_paths: AnyPath) -> AsyncGenerator[None]:
        yield

    async def write_file(self, uri: str, content: str) -> None:
        pass

    async def read_file(self, file_path: AnyPath) -> str:
        return ""

    async def request[R](self, req: Request, schema: type[Response[R]]) -> R:
        raise NotImplementedError

    async def notify(self, msg: Notification) -> None:
        pass


def test_capability_client_protocol_as_uri():
    workspace = Workspace()
    path = Path("/test/project")
    workspace[WORKSPACE_ROOT_DIR] = WorkspaceFolder(
        uri=path.as_uri(), name=WORKSPACE_ROOT_DIR
    )
    client = MockClient(workspace)

    # Test absolute path
    abs_path = Path("/test/project/file.py")
    assert client.as_uri(abs_path) == abs_path.as_uri()

    # Test relative path in single-root workspace
    assert client.as_uri("file.py") == abs_path.as_uri()

    # Test invalid absolute path
    with pytest.raises(ValueError, match="is not a valid workspace file path"):
        client.as_uri("/other/path/file.py")


def test_capability_client_protocol_as_uri_multi_root():
    workspace = Workspace()
    path1 = Path("/test/root1")
    path2 = Path("/test/root2")
    workspace["root1"] = WorkspaceFolder(uri=path1.as_uri(), name="root1")
    workspace["root2"] = WorkspaceFolder(uri=path2.as_uri(), name="root2")
    client = MockClient(workspace)

    # Test relative path in multi-root workspace
    assert client.as_uri("root1/file.py") == Path("/test/root1/file.py").as_uri()
    assert client.as_uri("root2/file.py") == Path("/test/root2/file.py").as_uri()

    # Test invalid root
    with pytest.raises(ValueError, match="is not a valid workspace folder"):
        client.as_uri("invalid/file.py")


def test_capability_client_protocol_from_uri():
    workspace = Workspace()
    path = Path("/test/project/file.py")
    workspace[WORKSPACE_ROOT_DIR] = WorkspaceFolder(
        uri=Path("/test/project").as_uri(), name=WORKSPACE_ROOT_DIR
    )
    client = MockClient(workspace)

    uri = path.as_uri()
    assert client.from_uri(uri) == Path("file.py")
    assert client.from_uri(uri, relative=False) == path


def test_capability_client_protocol_from_uri_multi_root():
    workspace = Workspace()
    path1 = Path("/test/root1")
    path2 = Path("/test/root2")
    workspace["root1"] = WorkspaceFolder(uri=path1.as_uri(), name="root1")
    workspace["root2"] = WorkspaceFolder(uri=path2.as_uri(), name="root2")
    client = MockClient(workspace)

    uri1 = Path("/test/root1/file.py").as_uri()
    uri2 = Path("/test/root2/file.py").as_uri()

    assert client.from_uri(uri1, relative=True) == Path("root1/file.py")
    assert client.from_uri(uri2, relative=True) == Path("root2/file.py")
    assert client.from_uri(uri1, relative=False) == Path("/test/root1/file.py")
