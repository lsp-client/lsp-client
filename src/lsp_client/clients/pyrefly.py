from __future__ import annotations

import sys
from functools import partial
from typing import Any, override

from attrs import define

from lsp_client.capability.notification import (
    WithNotifyDidChangeConfiguration,
)
from lsp_client.capability.request import (
    WithRequestCallHierarchy,
    WithRequestCodeAction,
    WithRequestCompletion,
    WithRequestDeclaration,
    WithRequestDefinition,
    WithRequestDocumentSymbol,
    WithRequestHover,
    WithRequestImplementation,
    WithRequestInlayHint,
    WithRequestReferences,
    WithRequestSignatureHelp,
    WithRequestTypeDefinition,
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

PyreflyContainerServer = partial(
    ContainerServer, image="ghcr.io/lsp-client/pyrefly:latest"
)


PyreflyLocalServer = partial(
    LocalServer,
    program="pyrefly",
    args=["lsp"],
    ensure_installed=partial(
        install_via_commands,
        "pyrefly",
        commands=(sys.executable, "-m", "pip", "install", "pyrefly"),
        error_message=(
            "Could not install pyrefly. Please install it manually with 'pip install pyrefly'. "
            "See https://pyrefly.org/ for more information."
        ),
    ),
)


@define
class PyreflyClient(
    PythonClientBase,
    WithNotifyDidChangeConfiguration,
    WithRequestCallHierarchy,
    WithRequestCodeAction,
    WithRequestCompletion,
    WithRequestDeclaration,
    WithRequestDefinition,
    WithRequestDocumentSymbol,
    WithRequestHover,
    WithRequestImplementation,
    WithRequestInlayHint,
    WithRequestReferences,
    WithRequestSignatureHelp,
    WithRequestTypeDefinition,
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
    - Homepage: https://pyrefly.org/
    - Doc: https://pyrefly.org/en/docs/
    - Github: https://github.com/facebook/pyrefly
    - VSCode Extension: https://github.com/facebook/pyrefly/tree/main/lsp
    """

    @classmethod
    @override
    def create_default_servers(cls) -> DefaultServers:
        return DefaultServers(
            local=PyreflyLocalServer(),
            container=PyreflyContainerServer(),
        )

    @override
    def check_server_compatibility(self, info: lsp_type.ServerInfo | None) -> None:
        return

    @override
    def create_default_config(self) -> dict[str, Any] | None:
        """
        https://pyrefly.org/en/docs/configuration
        """
        return {
            "pyrefly": {
                "inlayHints": {
                    "variableTypes": True,
                    "functionReturnTypes": True,
                    "parameterTypes": True,
                },
                "diagnostics": {
                    "enable": True,
                },
                "completion": {
                    "autoImports": True,
                },
            }
        }
