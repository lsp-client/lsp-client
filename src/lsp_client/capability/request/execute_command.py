from __future__ import annotations

from collections.abc import Iterator
from typing import Any, Protocol, override, runtime_checkable

from lsp_client.jsonrpc.id import jsonrpc_uuid
from lsp_client.protocol import CapabilityClientProtocol, WorkspaceCapabilityProtocol
from lsp_client.utils.types import lsp_type


@runtime_checkable
class WithRequestExecuteCommand(
    WorkspaceCapabilityProtocol,
    CapabilityClientProtocol,
    Protocol,
):
    """
    `workspace/executeCommand` - https://microsoft.github.io/language-server-protocol/specifications/lsp/3.17/specification/#workspace_executeCommand
    """

    @override
    @classmethod
    def iter_methods(cls) -> Iterator[str]:
        yield from super().iter_methods()
        yield from (lsp_type.WORKSPACE_EXECUTE_COMMAND,)

    @override
    @classmethod
    def register_workspace_capability(
        cls, cap: lsp_type.WorkspaceClientCapabilities
    ) -> None:
        super().register_workspace_capability(cap)
        cap.execute_command = lsp_type.ExecuteCommandClientCapabilities()

    @override
    @classmethod
    def check_server_capability(cls, cap: lsp_type.ServerCapabilities) -> None:
        super().check_server_capability(cap)
        assert cap.execute_command_provider

    async def _request_execute_command(
        self, params: lsp_type.ExecuteCommandParams
    ) -> Any:  # noqa: ANN401
        return await self.request(
            lsp_type.ExecuteCommandRequest(
                id=jsonrpc_uuid(),
                params=params,
            ),
            schema=lsp_type.ExecuteCommandResponse,
        )

    async def request_execute_command(
        self, command: str, arguments: list[Any] | None = None
    ) -> Any:  # noqa: ANN401
        return await self._request_execute_command(
            lsp_type.ExecuteCommandParams(
                command=command,
                arguments=arguments,
            )
        )
