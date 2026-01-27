from __future__ import annotations

import contextlib
from collections.abc import AsyncGenerator
from typing import Any, override
from unittest.mock import AsyncMock

import pytest

from lsp_client.capability.request.execute_command import WithRequestExecuteCommand
from lsp_client.protocol import CapabilityClientProtocol
from lsp_client.utils.types import Request, Response, lsp_type


class MockClient(WithRequestExecuteCommand, CapabilityClientProtocol):
    request_mock: AsyncMock

    def __init__(self) -> None:
        self.request_mock = AsyncMock()

    @override
    async def request[R](self, req: Request, schema: type[Response[R]]) -> R:
        return await self.request_mock(req, schema)

    @override
    def get_document_state(self) -> Any: ...
    @override
    def get_workspace(self) -> Any: ...
    @override
    def get_config_map(self) -> Any: ...
    @override
    @classmethod
    def get_language_config(cls) -> Any: ...

    @override
    @contextlib.asynccontextmanager
    async def open_files(self, *args: Any, **kwargs: Any) -> AsyncGenerator[None]:
        yield

    @override
    async def write_file(self, *args: Any, **kwargs: Any) -> Any: ...
    @override
    async def read_file(self, *args: Any, **kwargs: Any) -> Any: ...
    @override
    async def notify(self, *args: Any, **kwargs: Any) -> Any: ...


@pytest.mark.asyncio
async def test_request_execute_command() -> None:
    client = MockClient()
    client.request_mock.return_value = "command_result"

    result = await client.request_execute_command("test.command", ["arg1", 42])

    assert result == "command_result"
    client.request_mock.assert_called_once()
    req, schema = client.request_mock.call_args[0]

    assert isinstance(req, lsp_type.ExecuteCommandRequest)
    assert req.method == lsp_type.WORKSPACE_EXECUTE_COMMAND
    assert req.params.command == "test.command"
    assert req.params.arguments == ["arg1", 42]
    assert schema == lsp_type.ExecuteCommandResponse


def test_execute_command_capability_check() -> None:
    class TestClient(WithRequestExecuteCommand):
        @override
        def get_document_state(self) -> Any: ...
        @override
        def get_workspace(self) -> Any: ...
        @override
        def get_config_map(self) -> Any: ...
        @override
        @classmethod
        def get_language_config(cls) -> Any: ...
        @override
        @contextlib.asynccontextmanager
        async def open_files(self, *args: Any, **kwargs: Any) -> AsyncGenerator[None]:
            yield

        @override
        async def request(self, *args: Any, **kwargs: Any) -> Any: ...
        @override
        async def notify(self, *args: Any, **kwargs: Any) -> Any: ...
        @override
        async def read_file(self, *args: Any, **kwargs: Any) -> Any: ...
        @override
        async def write_file(self, *args: Any, **kwargs: Any) -> Any: ...

    caps = lsp_type.ServerCapabilities(
        execute_command_provider=lsp_type.ExecuteCommandOptions(commands=["cmd"])
    )
    TestClient.check_server_capability(caps)

    caps = lsp_type.ServerCapabilities(execute_command_provider=None)
    with pytest.raises(AssertionError):
        TestClient.check_server_capability(caps)
