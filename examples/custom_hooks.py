"""Example: Using Server Hooks for Custom Behavior

This example demonstrates how to use the various server lifecycle hooks
to add custom behavior at different stages.
"""

from __future__ import annotations

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import override

import anyio
from attrs import define
from loguru import logger

import lsp_client
from lsp_client.server.local import LocalServer
from lsp_client.server.types import ServerRequest
from lsp_client.utils.channel import Sender
from lsp_client.utils.workspace import Workspace

lsp_client.enable_logging()


@define
class CustomHooksServer(LocalServer):
    """Example server that demonstrates all available hooks."""

    @override
    async def setup(self, workspace: Workspace) -> None:
        """Called before starting server resources."""
        logger.info("🔧 Hook: setup() - Preparing to start server")
        logger.info(f"Workspace: {workspace}")
        await super().setup(workspace)

    @override
    @asynccontextmanager
    async def manage_resources(self, workspace: Workspace) -> AsyncGenerator[None]:
        """Called to manage server resources with lifecycle."""
        logger.info("🚀 Hook: manage_resources() - Starting server process")
        async with super().manage_resources(workspace):
            logger.info("✅ Server process started successfully")
            yield
            logger.info("🛑 Server process cleanup initiated")

    @override
    async def on_started(
        self, workspace: Workspace, sender: Sender[ServerRequest]
    ) -> None:
        """Called after server is ready and dispatch loop is starting."""
        logger.info("🎉 Hook: on_started() - Server is ready to receive requests")
        await super().on_started(workspace, sender)

    @override
    async def on_shutdown(self) -> None:
        """Called before server resources are cleaned up."""
        logger.info("👋 Hook: on_shutdown() - Gracefully shutting down")
        await super().on_shutdown()


async def main() -> None:
    from lsp_client.clients.pyright import PyrightClient

    # Create a custom client using our hook-enabled server
    server = CustomHooksServer(program="pyright-langserver", args=["--stdio"])

    async with PyrightClient(server=server) as client:
        logger.info("💼 Client is running, performing a quick operation...")

        # Do a simple hover request to test the server
        result = await client.request_hover(
            file_path="examples/custom_hooks.py",
            position=lsp_client.Position(0, 0),
        )

        logger.info(f"Hover result: {result is not None}")


if __name__ == "__main__":
    anyio.run(main)
