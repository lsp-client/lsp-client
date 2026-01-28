from __future__ import annotations

from functools import partial
from typing import Any, override

from attrs import define

from lsp_client.capability.notification import WithNotifyDidChangeConfiguration
from lsp_client.capability.request import (
    WithRequestCallHierarchy,
    WithRequestCodeAction,
    WithRequestCompletion,
    WithRequestDefinition,
    WithRequestDocumentSymbol,
    WithRequestHover,
    WithRequestImplementation,
    WithRequestInlayHint,
    WithRequestReferences,
    WithRequestSignatureHelp,
    WithRequestTypeDefinition,
    WithRequestTypeHierarchy,
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
from lsp_client.clients.base import GoClientBase
from lsp_client.server import DefaultServers
from lsp_client.server.container import ContainerServer
from lsp_client.server.local import LocalServer
from lsp_client.utils.install import install_via_commands
from lsp_client.utils.types import lsp_type

GoplsContainerServer = partial(ContainerServer, image="ghcr.io/lsp-client/gopls:latest")
GoplsLocalServer = partial(
    LocalServer,
    program="gopls",
    args=["serve"],
    ensure_installed=partial(
        install_via_commands,
        binary="gopls",
        commands=("go", "install", "golang.org/x/tools/gopls@latest"),
        error_message=(
            "Could not install gopls. Please install it manually with 'go install golang.org/x/tools/gopls@latest'. "
            "See https://github.com/golang/tools/tree/master/gopls for more information."
        ),
    ),
)


@define
class GoplsClient(
    GoClientBase,
    WithNotifyDidChangeConfiguration,
    WithRequestCallHierarchy,
    WithRequestCodeAction,
    WithRequestCompletion,
    WithRequestDefinition,
    WithRequestDocumentSymbol,
    WithRequestHover,
    WithRequestImplementation,
    WithRequestInlayHint,
    WithRequestReferences,
    WithRequestSignatureHelp,
    WithRequestTypeDefinition,
    WithRequestTypeHierarchy,
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
    - Language: Go
    - Homepage: https://pkg.go.dev/golang.org/x/tools/gopls
    - Doc: https://github.com/golang/tools/blob/master/gopls/README.md
    - Github: https://github.com/golang/tools/tree/master/gopls
    - VSCode Extension: https://marketplace.visualstudio.com/items?itemName=golang.go
    """

    @classmethod
    @override
    def create_default_servers(cls) -> DefaultServers:
        return DefaultServers(
            local=GoplsLocalServer(),
            container=GoplsContainerServer(),
        )

    @override
    def check_server_compatibility(self, info: lsp_type.ServerInfo | None) -> None:
        return

    @override
    def create_default_config(self) -> dict[str, Any] | None:
        """
        https://go.googlesource.com/tools/+/refs/heads/gopls-release-branch.0.5/gopls/doc/settings.md#settings
        """

        return {
            "gopls": {
                # https://go.dev/gopls/inlayHints
                "hints": {
                    "assignVariableTypes": True,
                    "compositeLiteralFields": True,
                    "compositeLiteralTypes": True,
                    "constantValues": True,
                    "functionTypeParameters": True,
                    "parameterNames": True,
                    "rangeVariableTypes": True,
                },
                # https://go.dev/gopls/settings#diagnosticsdelay-timeduration
                "diagnosticsDelay": "100ms",
                "matcher": "Fuzzy",
                "usePlaceholders": True,
                "semanticTokens": True,
            }
        }
