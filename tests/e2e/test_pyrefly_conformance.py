from __future__ import annotations

from pathlib import Path

import pytest

from lsp_client.clients.pyrefly import PyreflyClient
from tests.framework.lsp import lsp_interaction_context

# Fixtures are in the parent fixtures directory
FIXTURES_DIR = Path(__file__).parent.parent / "fixtures" / "pyrefly"


@pytest.mark.e2e
@pytest.mark.requires_fixtures
@pytest.mark.asyncio
async def test_pyrefly_conformance_protocols():
    # Use the linked conformance tests directory as workspace
    async with lsp_interaction_context(
        PyreflyClient,  # ty: ignore[invalid-argument-type]
        workspace_root=FIXTURES_DIR,
    ) as interaction:
        # Test definition of 'close' in close_all
        # Line 24: t.close()
        assertion = await interaction.request_definition(
            "protocols_definition.py", 23, 10
        )
        # Should point to SupportsClose.close at line 13
        assertion.expect_definition("protocols_definition.py", 12, 8, 12, 13)

        # Test hover on SupportsClose
        assertion = await interaction.request_hover("protocols_definition.py", 11, 6)
        assertion.expect_content("SupportsClose")


@pytest.mark.e2e
@pytest.mark.requires_fixtures
@pytest.mark.asyncio
async def test_pyrefly_conformance_generics():
    async with lsp_interaction_context(
        PyreflyClient,  # ty: ignore[invalid-argument-type]
        workspace_root=FIXTURES_DIR,
    ) as interaction:
        # Test definition of 'first' in test_first
        # Line 23: assert_type(first(seq_int), int)
        assertion = await interaction.request_definition("generics_basic.py", 22, 16)
        assertion.expect_definition("generics_basic.py", 17, 4, 17, 9)

        # Test hover on TypeVar T
        assertion = await interaction.request_hover("generics_basic.py", 11, 0)
        assertion.expect_content("T")
