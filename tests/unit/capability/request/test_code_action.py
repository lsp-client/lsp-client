from __future__ import annotations

import contextlib
from collections.abc import AsyncGenerator
from typing import Any, override
from unittest.mock import AsyncMock, MagicMock

import pytest

from lsp_client.capability.request.code_action import WithRequestCodeAction
from lsp_client.protocol import CapabilityClientProtocol
from lsp_client.utils.types import Request, Response, lsp_type


class MockCodeActionClient(WithRequestCodeAction, CapabilityClientProtocol):
    request_mock: AsyncMock
    apply_workspace_edit_mock: AsyncMock
    request_execute_command_mock: AsyncMock
    workspace: MagicMock

    def __init__(self) -> None:
        self.request_mock = AsyncMock()
        self.apply_workspace_edit_mock = AsyncMock()
        self.request_execute_command_mock = AsyncMock()
        self.workspace = MagicMock()
        self.workspace.values.return_value = []

    @override
    async def request[R](self, req: Request, schema: type[Response[R]]) -> R:
        return await self.request_mock(req, schema)

    @override
    async def apply_workspace_edit(self, edit: lsp_type.WorkspaceEdit) -> None:
        await self.apply_workspace_edit_mock(edit)

    async def request_execute_command(
        self, command: str, arguments: list[Any] | None = None
    ) -> Any:
        return await self.request_execute_command_mock(command, arguments)

    @override
    def get_document_state(self) -> Any: ...
    @override
    def get_workspace(self) -> Any:
        return self.workspace

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

    @override
    def as_uri(self, file_path: Any) -> str:
        return f"file://{file_path}"


@pytest.mark.asyncio
async def test_apply_code_action_command_only() -> None:
    client = MockCodeActionClient()
    command = lsp_type.Command(title="Test", command="test.command", arguments=["arg1"])

    await client.apply_code_action(command)

    client.request_execute_command_mock.assert_called_once_with(
        "test.command", ["arg1"]
    )


@pytest.mark.asyncio
async def test_apply_code_action_code_action_edit_only() -> None:
    client = MockCodeActionClient()
    edit = lsp_type.WorkspaceEdit(changes={"file1": []})
    action = lsp_type.CodeAction(title="Test", edit=edit)

    await client.apply_code_action(action)

    client.apply_workspace_edit_mock.assert_called_once_with(edit)
    client.request_execute_command_mock.assert_not_called()


@pytest.mark.asyncio
async def test_apply_code_action_code_action_command_only() -> None:
    client = MockCodeActionClient()
    command = lsp_type.Command(title="Test", command="test.command", arguments=["arg1"])
    action = lsp_type.CodeAction(title="Test", command=command)

    await client.apply_code_action(action)

    client.apply_workspace_edit_mock.assert_not_called()
    client.request_execute_command_mock.assert_called_once_with(
        "test.command", ["arg1"]
    )


@pytest.mark.asyncio
async def test_apply_code_action_both_edit_and_command() -> None:
    client = MockCodeActionClient()
    edit = lsp_type.WorkspaceEdit(changes={"file1": []})
    command = lsp_type.Command(title="Test", command="test.command", arguments=["arg1"])
    action = lsp_type.CodeAction(title="Test", edit=edit, command=command)

    await client.apply_code_action(action)

    client.apply_workspace_edit_mock.assert_called_once_with(edit)
    client.request_execute_command_mock.assert_called_once_with(
        "test.command", ["arg1"]
    )


@pytest.mark.asyncio
async def test_apply_code_action_lazy_resolve() -> None:
    client = MockCodeActionClient()
    action = lsp_type.CodeAction(title="Test")

    resolved_edit = lsp_type.WorkspaceEdit(changes={"file2": []})
    resolved_action = lsp_type.CodeAction(title="Test", edit=resolved_edit)
    client.request_mock.return_value = resolved_action

    await client.apply_code_action(action)

    client.request_mock.assert_called_once()
    req, _ = client.request_mock.call_args[0]
    assert isinstance(req, lsp_type.CodeActionResolveRequest)

    client.apply_workspace_edit_mock.assert_called_once_with(resolved_edit)


@pytest.mark.asyncio
async def test_apply_code_action_disabled() -> None:
    client = MockCodeActionClient()
    action = lsp_type.CodeAction(
        title="Test", disabled=lsp_type.CodeActionDisabled(reason="reason")
    )

    await client.apply_code_action(action)

    client.apply_workspace_edit_mock.assert_not_called()
    client.request_execute_command_mock.assert_not_called()
    client.request_mock.assert_not_called()


@pytest.mark.asyncio
async def test_apply_code_actions_multiple() -> None:
    client = MockCodeActionClient()
    action1 = lsp_type.CodeAction(title="Action 1", edit=lsp_type.WorkspaceEdit())
    action2 = lsp_type.Command(title="Command 2", command="cmd2")

    await client.apply_code_actions([action1, action2])

    client.apply_workspace_edit_mock.assert_called_once()
    client.request_execute_command_mock.assert_called_once_with("cmd2", None)


@pytest.mark.asyncio
async def test_apply_code_action_missing_execute_command_capability() -> None:
    class PartialClient(WithRequestCodeAction, CapabilityClientProtocol):
        apply_workspace_edit_mock: AsyncMock

        def __init__(self) -> None:
            self.apply_workspace_edit_mock = AsyncMock()

        @override
        async def request[R](self, req: Request, schema: type[Response[R]]) -> R:
            raise NotImplementedError()

        @override
        async def apply_workspace_edit(self, edit: lsp_type.WorkspaceEdit) -> None:
            await self.apply_workspace_edit_mock(edit)

        @override
        def get_document_state(self) -> Any:
            raise NotImplementedError()

        @override
        def get_workspace(self) -> Any:
            raise NotImplementedError()

        @override
        def get_config_map(self) -> Any:
            raise NotImplementedError()

        @override
        @classmethod
        def get_language_config(cls) -> Any:
            raise NotImplementedError()

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
        @override
        def as_uri(self, file_path: Any) -> str:
            return ""

    client = PartialClient()
    command = lsp_type.Command(title="Test", command="test.command")

    with pytest.raises(RuntimeError, match="executeCommand capability not available"):
        await client.apply_code_action(command)
