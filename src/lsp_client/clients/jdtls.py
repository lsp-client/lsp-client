from __future__ import annotations

import shutil
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
    WithRequestRename,
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
from lsp_client.clients.base import JavaClientBase
from lsp_client.server import DefaultServers
from lsp_client.server.container import ContainerServer
from lsp_client.server.local import LocalServer
from lsp_client.utils.install import install_via_commands
from lsp_client.utils.types import lsp_type

JdtlsContainerServer = partial(ContainerServer, image="ghcr.io/lsp-client/jdtls:latest")


def install_cmd() -> list[str]:
    if shutil.which("brew"):
        return ["brew", "install", "jdtls"]
    if shutil.which("pacman"):
        return ["sudo", "pacman", "-S", "jdtls"]
    return []


JdtlsLocalServer = partial(
    LocalServer,
    program="jdtls",
    ensure_installed=partial(
        install_via_commands,
        binary="jdtls",
        commands=install_cmd(),
        error_message=(
            "jdtls not found. Please install Eclipse JDT Language Server (jdtls) and ensure it is in your PATH.\n"
            "- macOS: 'brew install jdtls'\n"
            "- Arch Linux: 'sudo pacman -S jdtls'\n"
            "- Others: See https://github.com/eclipse/eclipse.jdt.ls for manual installation instructions."
        ),
    ),
)


@define
class JdtlsClient(
    JavaClientBase,
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
    WithRequestRename,
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
    - Language: Java
    - Homepage: https://github.com/eclipse/eclipse.jdt.ls
    - Github: https://github.com/eclipse/eclipse.jdt.ls
    - VSCode Extension: https://marketplace.visualstudio.com/items?itemName=redhat.java
    """

    @classmethod
    @override
    def create_default_servers(cls) -> DefaultServers:
        return DefaultServers(
            local=JdtlsLocalServer(),
            container=JdtlsContainerServer(),
        )

    @override
    def check_server_compatibility(self, info: lsp_type.ServerInfo | None) -> None:
        return

    @override
    def create_default_config(self) -> dict[str, Any] | None:
        """
        https://github.com/redhat-developer/vscode-java/blob/master/package.json
        """
        return {
            "java": {
                "format": {
                    "enabled": True,
                },
                "autobuild": {
                    "enabled": True,
                },
                "completion": {
                    "favoriteStaticMembers": [
                        "org.junit.Assert.*",
                        "org.junit.Assume.*",
                        "org.junit.jupiter.*",
                        "org.junit.rules.ExpectedException.*",
                        "org.hamcrest.MatcherAssert.*",
                        "org.hamcrest.Matchers.*",
                        "org.hamcrest.CoreMatchers.*",
                        "java.util.Objects.*",
                        "java.util.Arrays.*",
                        "java.util.Collections.*",
                    ],
                    "importOrder": [
                        "java",
                        "javax",
                        "com",
                        "org",
                    ],
                },
                "signatureHelp": {
                    "enabled": True,
                },
                "contentProvider": {
                    "preferred": "fernflower",
                },
            }
        }
