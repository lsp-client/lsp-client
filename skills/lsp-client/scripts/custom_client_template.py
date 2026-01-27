#!/usr/bin/env python3
"""Template for creating a custom LSP client with selected capabilities."""

from typing import Any

from attrs import define

from lsp_client.capability.notification import (
    WithNotifyDidChangeConfiguration,
)
from lsp_client.capability.request import (
    WithRequestCompletion,
    WithRequestDefinition,
    WithRequestHover,
    WithRequestReferences,
    WithRequestRename,
)
from lsp_client.clients.base import PythonClientBase
from lsp_client.server import ContainerServer, DefaultServers, LocalServer
from lsp_client.utils.types import lsp_type


@define
class MyCustomClient(
    PythonClientBase,
    WithRequestHover,
    WithRequestDefinition,
    WithRequestReferences,
    WithRequestCompletion,
    WithRequestRename,
    WithNotifyDidChangeConfiguration,
):
    """Custom LSP client with selected capabilities.

    This client supports:
    - Hover information
    - Go to definition
    - Find references
    - Code completion
    - Symbol rename
    - Configuration updates
    """

    @classmethod
    def create_default_servers(cls) -> DefaultServers:
        return DefaultServers(
            local=LocalServer(program="pyright-langserver", args=["--stdio"]),
            container=ContainerServer(image="ghcr.io/lsp-client/pyright:latest"),
        )

    def create_default_config(self) -> dict[str, Any] | None:
        return {
            "python": {
                "analysis": {
                    "autoImportCompletions": True,
                    "typeCheckingMode": "basic",
                }
            }
        }

    def check_server_compatibility(self, info: lsp_type.ServerInfo | None) -> None:
        pass


if __name__ == "__main__":
    from pathlib import Path

    import anyio

    from lsp_client import Position

    async def main() -> None:
        workspace = Path.cwd()

        async with MyCustomClient(workspace=workspace) as client:
            hover = await client.request_hover(
                file_path="example.py", position=Position(10, 5)
            )

            if hover:
                print(f"Hover info: {hover.value}")

    anyio.run(main)
