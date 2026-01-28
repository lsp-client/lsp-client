from __future__ import annotations

import sys
from functools import partial
from typing import Any, override

from attrs import define

from lsp_client.capability.notification import (
    WithNotifyDidChangeConfiguration,
)
from lsp_client.capability.request import (
    WithDocumentDiagnostic,
    WithRequestCodeAction,
    WithRequestCompletion,
    WithRequestDeclaration,
    WithRequestDefinition,
    WithRequestDocumentSymbol,
    WithRequestHover,
    WithRequestInlayHint,
    WithRequestReferences,
    WithRequestSignatureHelp,
    WithRequestTypeDefinition,
    WithRequestWorkspaceSymbol,
    WithWorkspaceDiagnostic,
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

TyContainerServer = partial(ContainerServer, image="ghcr.io/lsp-client/ty:latest")


TyLocalServer = partial(
    LocalServer,
    program="ty",
    args=["server"],
    ensure_installed=partial(
        install_via_commands,
        "ty",
        commands=(sys.executable, "-m", "pip", "install", "ty"),
        error_message=(
            "Could not install ty. Please install it manually with 'pip install ty' or 'uv tool install ty'. "
            "See https://docs.astral.sh/ty/installation/ for more information."
        ),
    ),
)


@define
class TyClient(
    PythonClientBase,
    WithNotifyDidChangeConfiguration,
    WithRequestCodeAction,
    WithRequestCompletion,
    WithRequestDeclaration,
    WithRequestDefinition,
    WithRequestDocumentSymbol,
    WithRequestHover,
    WithRequestInlayHint,
    WithDocumentDiagnostic,
    WithRequestReferences,
    WithRequestSignatureHelp,
    WithRequestTypeDefinition,
    WithWorkspaceDiagnostic,
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
    - Homepage: https://docs.astral.sh/ty/
    - Doc: https://docs.astral.sh/ty/
    - Github: https://github.com/astral-sh/ty
    - VSCode Extension: https://docs.astral.sh/ty/editors/vscode/
    """

    @classmethod
    @override
    def create_default_servers(cls) -> DefaultServers:
        return DefaultServers(
            local=TyLocalServer(),
            container=TyContainerServer(),
        )

    @override
    def check_server_compatibility(self, info: lsp_type.ServerInfo | None) -> None:
        return

    @override
    def create_default_config(self) -> dict[str, Any] | None:
        """
        https://docs.astral.sh/ty/reference/editor-settings/
        """
        return {
            "ty": {
                "diagnostics": True,
                "completion": True,
            }
        }
