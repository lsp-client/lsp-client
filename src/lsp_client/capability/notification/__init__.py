from __future__ import annotations

from typing import Final

from .did_change_configuration import WithNotifyDidChangeConfiguration
from .did_change_workspace_folders import WithNotifyDidChangeWorkspaceFolders
from .did_create_files import WithNotifyDidCreateFiles
from .did_delete_files import WithNotifyDidDeleteFiles
from .did_rename_files import WithNotifyDidRenameFiles
from .text_document_synchronize import WithNotifyTextDocumentSynchronize

capabilities: Final = (
    WithNotifyDidChangeConfiguration,
    WithNotifyDidChangeWorkspaceFolders,
    WithNotifyDidCreateFiles,
    WithNotifyDidRenameFiles,
    WithNotifyDidDeleteFiles,
    WithNotifyTextDocumentSynchronize,
)

__all__ = [
    "WithNotifyDidChangeConfiguration",
    "WithNotifyDidChangeWorkspaceFolders",
    "WithNotifyDidCreateFiles",
    "WithNotifyDidDeleteFiles",
    "WithNotifyDidRenameFiles",
    "WithNotifyTextDocumentSynchronize",
    "capabilities",
]
