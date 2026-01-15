from __future__ import annotations

from collections.abc import Iterator
from typing import Protocol, override, runtime_checkable

from lsp_client.protocol import CapabilityClientProtocol, WorkspaceCapabilityProtocol
from lsp_client.utils.types import lsp_type


@runtime_checkable
class WithNotifyDidChangeWorkspaceFolders(
    WorkspaceCapabilityProtocol,
    CapabilityClientProtocol,
    Protocol,
):
    """
    `workspace/didChangeWorkspaceFolders` - https://microsoft.github.io/language-server-protocol/specifications/lsp/3.17/specification/#workspace_didChangeWorkspaceFolders
    """

    @override
    @classmethod
    def iter_methods(cls) -> Iterator[str]:
        yield from super().iter_methods()
        yield from (lsp_type.WORKSPACE_DID_CHANGE_WORKSPACE_FOLDERS,)

    @override
    @classmethod
    def register_workspace_capability(
        cls, cap: lsp_type.WorkspaceClientCapabilities
    ) -> None:
        super().register_workspace_capability(cap)
        cap.workspace_folders = True

    async def notify_did_change_workspace_folders(
        self,
        added: list[lsp_type.WorkspaceFolder],
        removed: list[lsp_type.WorkspaceFolder],
    ) -> None:
        """
        Notify the server that the workspace folders have changed.
        """

        return await self.notify(
            lsp_type.DidChangeWorkspaceFoldersNotification(
                params=lsp_type.DidChangeWorkspaceFoldersParams(
                    event=lsp_type.WorkspaceFoldersChangeEvent(
                        added=added, removed=removed
                    )
                )
            )
        )
