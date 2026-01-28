from __future__ import annotations

from functools import partial
from typing import Any, override

from attrs import define

from lsp_client.capability.notification import (
    WithNotifyDidChangeConfiguration,
    WithNotifyDidCreateFiles,
    WithNotifyDidDeleteFiles,
    WithNotifyDidRenameFiles,
)
from lsp_client.capability.request import (
    WithRequestCallHierarchy,
    WithRequestCodeAction,
    WithRequestCompletion,
    WithRequestDeclaration,
    WithRequestDefinition,
    WithRequestDocumentSymbol,
    WithRequestHover,
    WithRequestReferences,
    WithRequestRename,
    WithRequestSignatureHelp,
    WithRequestTypeDefinition,
    WithRequestWillCreateFiles,
    WithRequestWillDeleteFiles,
    WithRequestWillRenameFiles,
    WithRequestWorkspaceSymbol,
)
from lsp_client.capability.server_notification import (
    WithReceiveLogMessage,
    WithReceiveLogTrace,
    WithReceivePublishDiagnostics,
    WithReceiveShowMessage,
)
from lsp_client.capability.server_request import (
    WithRespondConfigurationRequest,
    WithRespondInlayHintRefresh,
    WithRespondShowDocumentRequest,
    WithRespondShowMessageRequest,
    WithRespondWorkspaceFoldersRequest,
)
from lsp_client.clients.base import PythonClientBase
from lsp_client.server import DefaultServers
from lsp_client.server.container import ContainerServer
from lsp_client.server.local import LocalServer
from lsp_client.utils.install import install_via_commands
from lsp_client.utils.types import lsp_type

PyrightContainerServer = partial(
    ContainerServer, image="ghcr.io/lsp-client/pyright:latest"
)


PyrightLocalServer = partial(
    LocalServer,
    program="pyright-langserver",
    args=["--stdio"],
    ensure_installed=partial(
        install_via_commands,
        "pyright-langserver",
        commands=("npm", "install", "-g", "pyright"),
        error_message=(
            "Could not install pyright-langserver. Please install it manually with 'npm install -g pyright'. "
            "See https://microsoft.github.io/pyright/ for more information."
        ),
    ),
)


@define
class PyrightClient(
    PythonClientBase,
    WithNotifyDidChangeConfiguration,
    WithNotifyDidCreateFiles,
    WithNotifyDidRenameFiles,
    WithNotifyDidDeleteFiles,
    WithRequestCallHierarchy,
    WithRequestCodeAction,
    WithRequestCompletion,
    WithRequestDeclaration,
    WithRequestDefinition,
    WithRequestDocumentSymbol,
    WithRequestHover,
    WithRequestReferences,
    WithRequestRename,
    WithRequestSignatureHelp,
    WithRequestTypeDefinition,
    WithRequestWillCreateFiles,
    WithRequestWillRenameFiles,
    WithRequestWillDeleteFiles,
    WithRequestWorkspaceSymbol,
    WithReceiveLogMessage,
    WithReceiveLogTrace,
    WithReceivePublishDiagnostics,
    WithReceiveShowMessage,
    WithRespondConfigurationRequest,
    WithRespondInlayHintRefresh,
    WithRespondShowDocumentRequest,
    WithRespondShowMessageRequest,
    WithRespondWorkspaceFoldersRequest,
):
    """
    - Language: Python
    - Homepage: https://microsoft.github.io/pyright/
    - Doc: https://microsoft.github.io/pyright/
    - Github: https://github.com/microsoft/pyright
    - VSCode Extension: https://github.com/microsoft/pyright/tree/main/packages/vscode-pyright
    """

    @classmethod
    @override
    def create_default_servers(cls) -> DefaultServers:
        return DefaultServers(
            local=PyrightLocalServer(),
            container=PyrightContainerServer(),
        )

    @override
    def check_server_compatibility(self, info: lsp_type.ServerInfo | None) -> None:
        return

    @override
    def create_default_config(self) -> dict[str, Any] | None:
        """
        https://microsoft.github.io/pyright/#/settings
        """
        return {
            "python": {
                "analysis": {
                    "autoImportCompletions": True,
                    "autoSearchPaths": True,
                    "diagnosticMode": "openFilesOnly",
                    "indexing": True,
                    "typeCheckingMode": "basic",
                    "inlayHints": {
                        "variableTypes": True,
                        "functionReturnTypes": True,
                        "callArgumentNames": True,
                        "pytestParameters": True,
                    },
                }
            }
        }
