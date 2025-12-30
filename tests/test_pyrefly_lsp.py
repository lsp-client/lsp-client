from __future__ import annotations

from pathlib import Path

import pytest

from lsp_client.clients.pyrefly import PyreflyClient
from tests.framework.lsp import lsp_interaction_context

FIXTURES_DIR = Path(__file__).parent / "fixtures" / "pyrefly_lsp"


@pytest.mark.asyncio
async def test_pyrefly_go_to_def_relative():
    # References: references/pyrefly/pyrefly/lib/test/lsp/lsp_interaction/definition.rs:165
    # File: basic/foo_relative.py
    workspace_root = FIXTURES_DIR / "basic"
    async with lsp_interaction_context(
        PyreflyClient,  # ty: ignore[invalid-argument-type]
        workspace_root=workspace_root,
    ) as interaction:
        # (6, 17, "bar.py", 6, 6, 6, 9)
        assertion = await interaction.request_definition("foo_relative.py", 6, 17)
        assertion.expect_definition("bar.py", 6, 6, 6, 9)

        # (8, 9, "bar.py", 7, 4, 7, 7)
        assertion = await interaction.request_definition("foo_relative.py", 8, 9)
        assertion.expect_definition("bar.py", 7, 4, 7, 7)


@pytest.mark.asyncio
async def test_pyrefly_hover_primitive():
    # References: references/pyrefly/pyrefly/lib/test/lsp/lsp_interaction/test_files/primitive_type_test.py
    workspace_root = FIXTURES_DIR
    async with lsp_interaction_context(
        PyreflyClient,  # ty: ignore[invalid-argument-type]
        workspace_root=workspace_root,
    ) as interaction:
        await interaction.create_file("primitive_test.py", "x: int = 1\ny: str = 'hi'")

        assertion = await interaction.request_hover("primitive_test.py", 0, 0)
        assertion.expect_content("int")

        assertion = await interaction.request_hover("primitive_test.py", 1, 0)
        assertion.expect_content("str")
