from __future__ import annotations

from typing import cast

import anyio
import pytest

from lsp_client.clients.pyrefly import PyreflyClient
from lsp_client.utils.types import lsp_type
from tests.framework.lsp import lsp_interaction_context


class CapturedPyreflyClient(PyreflyClient):
    """Subclass of PyreflyClient that captures diagnostics for testing."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.captured_diagnostics = {}
        self.diagnostic_events = {}

    async def _receive_publish_diagnostics(
        self, params: lsp_type.PublishDiagnosticsParams
    ) -> None:
        await super()._receive_publish_diagnostics(params)
        self.captured_diagnostics[params.uri] = params.diagnostics
        if params.uri not in self.diagnostic_events:
            self.diagnostic_events[params.uri] = anyio.Event()
        self.diagnostic_events[params.uri].set()

    async def wait_for_diagnostics(
        self, uri: str, timeout: float = 15.0
    ) -> list[lsp_type.Diagnostic]:
        if uri not in self.diagnostic_events:
            self.diagnostic_events[uri] = anyio.Event()

        with anyio.fail_after(timeout):
            await self.diagnostic_events[uri].wait()

        return self.captured_diagnostics.get(uri, [])


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_pyrefly_completion_representative():
    async with lsp_interaction_context(PyreflyClient) as interaction:  # ty: ignore[invalid-argument-type]
        await interaction.create_file("main.py", "import os\nos.pa")
        assertion = await interaction.request_completion("main.py", 1, 5)
        assertion.expect_label("path")


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_pyrefly_references_representative():
    async with lsp_interaction_context(PyreflyClient) as interaction:  # ty: ignore[invalid-argument-type]
        content = """
def my_func():
    pass

my_func()
my_func()
"""
        await interaction.create_file("refs.py", content)
        # Request references for my_func at its definition (line 1, col 4)
        assertion = await interaction.request_references("refs.py", 1, 4)
        assertion.expect_reference("refs.py", 1, 4, 1, 11)  # definition itself
        assertion.expect_reference("refs.py", 4, 0, 4, 7)  # first call
        assertion.expect_reference("refs.py", 5, 0, 5, 7)  # second call


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_pyrefly_diagnostics_representative():
    # Use the specialized client to capture diagnostics
    config = {
        "pyrefly": {"displayTypeErrors": "force-on", "diagnostics": {"enable": True}}
    }

    async with lsp_interaction_context(CapturedPyreflyClient) as interaction:  # ty: ignore[invalid-argument-type]
        await interaction.client.get_config_map().update_global(config)

        # Add a pyproject.toml to make it a proper project
        await interaction.create_file("pyproject.toml", "[tool.pyrefly]\n")

        await interaction.create_file("diag.py", "x: int = 'not an int'")

        uri = interaction.client.as_uri(interaction.full_path("diag.py"))

        # Ensure file is opened to trigger diagnostics
        async with interaction.client.open_files(interaction.full_path("diag.py")):
            client = cast(CapturedPyreflyClient, interaction.client)
            diagnostics = await client.wait_for_diagnostics(uri)

        assert len(diagnostics) > 0
        messages = [d.message for d in diagnostics]
        assert any("is not assignable to `int`" in m for m in messages)
