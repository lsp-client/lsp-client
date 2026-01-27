from __future__ import annotations

from collections.abc import Iterator, Sequence
from typing import Protocol, override, runtime_checkable

from lsp_client.capability.request.workspace_edit import WithApplyWorkspaceEdit
from lsp_client.jsonrpc.id import jsonrpc_uuid
from lsp_client.protocol import TextDocumentCapabilityProtocol
from lsp_client.utils.types import AnyPath, Range, lsp_type


@runtime_checkable
class WithRequestCodeAction(
    TextDocumentCapabilityProtocol,
    WithApplyWorkspaceEdit,
    Protocol,
):
    """
    - `textDocument/codeAction` - https://microsoft.github.io/language-server-protocol/specifications/lsp/3.17/specification/#textDocument_codeAction
    - `codeAction/resolve` - https://microsoft.github.io/language-server-protocol/specifications/lsp/3.17/specification/#codeAction_resolve
    """

    @override
    @classmethod
    def iter_methods(cls) -> Iterator[str]:
        yield from super().iter_methods()
        yield from (
            lsp_type.TEXT_DOCUMENT_CODE_ACTION,
            lsp_type.CODE_ACTION_RESOLVE,
        )

    @override
    @classmethod
    def register_text_document_capability(
        cls, cap: lsp_type.TextDocumentClientCapabilities
    ) -> None:
        super().register_text_document_capability(cap)
        cap.code_action = lsp_type.CodeActionClientCapabilities(
            code_action_literal_support=lsp_type.ClientCodeActionLiteralOptions(
                code_action_kind=lsp_type.ClientCodeActionKindOptions(
                    value_set=list(lsp_type.CodeActionKind)
                )
            ),
            is_preferred_support=True,
            disabled_support=True,
            data_support=True,
            resolve_support=lsp_type.ClientCodeActionResolveOptions(
                properties=["edit", "command"]
            ),
        )

    @override
    @classmethod
    def check_server_capability(cls, cap: lsp_type.ServerCapabilities) -> None:
        super().check_server_capability(cap)
        assert cap.code_action_provider

    async def _request_code_action(
        self, params: lsp_type.CodeActionParams
    ) -> lsp_type.CodeActionResult:
        return await self.request(
            lsp_type.CodeActionRequest(
                id=jsonrpc_uuid(),
                params=params,
            ),
            schema=lsp_type.CodeActionResponse,
        )

    async def _request_code_action_resolve(
        self, params: lsp_type.CodeAction
    ) -> lsp_type.CodeAction:
        return await self.request(
            lsp_type.CodeActionResolveRequest(
                id=jsonrpc_uuid(),
                params=params,
            ),
            schema=lsp_type.CodeActionResolveResponse,
        )

    async def request_code_action(
        self,
        file_path: AnyPath,
        range: Range,
        *,
        diagnostics: Sequence[lsp_type.Diagnostic] | None = None,
        only: Sequence[lsp_type.CodeActionKind] | None = None,
        trigger_kind: lsp_type.CodeActionTriggerKind | None = None,
    ) -> Sequence[lsp_type.Command | lsp_type.CodeAction]:
        context = lsp_type.CodeActionContext(
            diagnostics=list(diagnostics) if diagnostics else [],
            only=list(only) if only else None,
            trigger_kind=trigger_kind,
        )

        async with self.open_files(file_path):
            result = await self._request_code_action(
                lsp_type.CodeActionParams(
                    text_document=lsp_type.TextDocumentIdentifier(
                        uri=self.as_uri(file_path)
                    ),
                    range=range,
                    context=context,
                )
            )

        return list(result) if result else []

    async def request_code_action_resolve(
        self,
        code_action: lsp_type.CodeAction,
    ) -> lsp_type.CodeAction:
        return await self._request_code_action_resolve(code_action)

    async def apply_code_action(
        self, item: lsp_type.Command | lsp_type.CodeAction
    ) -> None:
        """
        Apply a code action or command.

        Args:
            item: The code action or command to apply

        Raises:
            RuntimeError: If the client does not have the WithRequestExecuteCommand mixin
        """
        if isinstance(item, lsp_type.Command):
            method = getattr(self, "request_execute_command", None)
            if method is None:
                raise RuntimeError(
                    "executeCommand capability not available. Include WithRequestExecuteCommand mixin."
                )
            await method(item.command, item.arguments)
            return

        if item.disabled:
            return

        if item.edit is None and item.command is None:
            item = await self.request_code_action_resolve(item)

        if item.edit is not None:
            await self.apply_workspace_edit(item.edit)

        if item.command is not None:
            method = getattr(self, "request_execute_command", None)
            if method is None:
                raise RuntimeError(
                    "executeCommand capability not available. Include WithRequestExecuteCommand mixin."
                )
            await method(item.command.command, item.command.arguments)

    async def apply_code_actions(
        self, items: Sequence[lsp_type.Command | lsp_type.CodeAction]
    ) -> None:
        """
        Apply multiple code actions or commands sequentially.

        Args:
            items: The code actions or commands to apply
        """
        for item in items:
            await self.apply_code_action(item)
