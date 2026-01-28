from __future__ import annotations

from functools import partial
from typing import Any, override

from attrs import define

from lsp_client.capability.diagnostic import (
    WithDocumentDiagnostic,
    WithWorkspaceDiagnostic,
)
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
    WithRequestImplementation,
    WithRequestInlayHint,
    WithRequestReferences,
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
from lsp_client.clients.base import RustClientBase
from lsp_client.server import DefaultServers
from lsp_client.server.container import ContainerServer
from lsp_client.server.local import LocalServer
from lsp_client.utils.install import install_via_commands
from lsp_client.utils.types import lsp_type

RustAnalyzerContainerServer = partial(
    ContainerServer, image="ghcr.io/lsp-client/rust-analyzer:latest"
)


RustAnalyzerLocalServer = partial(
    LocalServer,
    program="rust-analyzer",
    ensure_installed=partial(
        install_via_commands,
        "rust-analyzer",
        commands=("rustup", "component", "add", "rust-analyzer"),
        error_message=(
            "Could not install rust-analyzer. Please install it manually with 'rustup component add rust-analyzer'. "
            "See https://rust-analyzer.github.io/ for more information."
        ),
    ),
)


@define
class RustAnalyzerClient(
    RustClientBase,
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
    WithRequestImplementation,
    WithRequestInlayHint,
    WithDocumentDiagnostic,
    WithWorkspaceDiagnostic,
    WithRequestReferences,
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
    - Language: Rust
    - Homepage: https://rust-analyzer.github.io/
    - Doc: https://rust-analyzer.github.io/manual.html
    - Github: https://github.com/rust-lang/rust-analyzer
    - VSCode Extension: https://marketplace.visualstudio.com/items?itemName=rust-lang.rust-analyzer
    """

    @classmethod
    @override
    def create_default_servers(cls) -> DefaultServers:
        return DefaultServers(
            local=RustAnalyzerLocalServer(),
            container=RustAnalyzerContainerServer(),
        )

    @override
    def check_server_compatibility(self, info: lsp_type.ServerInfo | None) -> None:
        return

    @override
    def create_default_config(self) -> dict[str, Any] | None:
        """
        https://rust-analyzer.github.io/book/configuration.html
        """
        return {
            "rust-analyzer": {
                "cargo": {
                    "buildScripts": {"enable": True},
                    "features": "all",
                },
                "checkOnSave": {"enable": True},
                "completion": {
                    "autoimport": {"enable": True},
                    "callable": {"snippets": "fill_arguments"},
                    "postfix": {"enable": True},
                },
                "diagnostics": {
                    "enable": True,
                    "experimental": {"enable": True},
                },
                "hover": {
                    "actions": {
                        "enable": True,
                        "references": {"enable": True},
                    }
                },
                "inlayHints": {
                    "enable": True,
                    "bindingModeHints": {"enable": True},
                    "closureCaptureHints": {"enable": True},
                    "chainingHints": {"enable": True},
                    "closureReturnTypeHints": {"enable": "always"},
                    "lifetimeElisionHints": {"enable": "always"},
                    "discriminantHints": {"enable": "always"},
                    "expressionAdjustmentHints": {"enable": "always"},
                    "parameterHints": {"enable": True},
                    "reborrowHints": {"enable": "always"},
                    "typeHints": {"enable": True},
                },
            }
        }
