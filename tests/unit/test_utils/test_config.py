from __future__ import annotations

import pytest

"""
Example unit tests for Utils module.

This file demonstrates the expected test structure for testing
utility functions and classes.
"""


class TestConfigurationMap:
    """Tests for ConfigurationMap class."""

    def test_configuration_map_creation(self):
        """Test that ConfigurationMap can be created."""
        from lsp_client.utils.config import ConfigurationMap

        config = ConfigurationMap()
        assert config.global_config == {}
        assert config.scoped_configs == []

    def test_deep_merge_function(self):
        """Test deep merge function."""
        from lsp_client.utils.config import deep_merge

        base = {"a": {"b": 1, "c": 2}}
        update = {"a": {"b": 3, "d": 4}}

        result = deep_merge(base, update)
        assert result["a"]["b"] == 3  # Updated value
        assert result["a"]["c"] == 2  # Preserved value
        assert result["a"]["d"] == 4  # New value


class TestWorkspace:
    """Tests for workspace utilities."""

    def test_format_workspace_path(self):
        """Test formatting workspace from path."""
        from pathlib import Path

        from lsp_client.utils.workspace import format_workspace

        workspace = format_workspace(Path("/test"))
        assert workspace is not None

    def test_format_workspace_string(self):
        """Test formatting workspace from string."""
        from lsp_client.utils.workspace import format_workspace

        workspace = format_workspace("/test")
        assert workspace is not None


class TestURI:
    """Tests for URI utilities."""

    def test_from_local_uri(self):
        """Test creating URI from local path."""
        from pathlib import Path

        from lsp_client.utils.uri import from_local_uri

        path = from_local_uri("file:///test/path")
        assert path == Path("/test/path")

    def test_from_local_uri_with_spaces(self):
        """Test from_local_uri with spaces in path."""
        from pathlib import Path

        from lsp_client.utils.uri import from_local_uri

        path = from_local_uri("file:///test/path%20with%20spaces")
        assert path == Path("/test/path with spaces")


class TestChannel:
    """Tests for channel utilities."""

    @pytest.mark.asyncio
    async def test_oneshot_channel_create(self):
        """Test creating a oneshot channel."""
        from lsp_client.utils.channel import oneshot_channel

        channel = oneshot_channel.create()
        # Just verify it can be created
        assert channel.sender is not None
        assert channel.receiver is not None

    @pytest.mark.asyncio
    async def test_oneshot_table(self):
        """Test oneshot table for dispatching responses."""
        from lsp_client.utils.channel import OneShotTable

        table = OneShotTable()
        table.reserve("request-1")
        # Note: The oneshot table is designed to be used with a receive coroutine
        # The send will only work if there's a pending receive
        # For testing purposes, we verify the reserve and the state
        assert table._pending.get("request-1") is not None


class TestTypes:
    """Tests for type utilities."""

    def test_lsp_type_import(self):
        """Test importing lsp_type from lsprotocol."""
        from lsp_client.utils.types import lsp_type

        assert lsp_type.Position is not None
        assert lsp_type.Range is not None
        assert lsp_type.Location is not None

    def test_position_creation(self):
        """Test creating Position."""
        from lsp_client.utils.types import Position

        pos = Position(line=0, character=0)
        assert pos.line == 0
        assert pos.character == 0

    def test_range_creation(self):
        """Test creating Range."""
        from lsp_client.utils.types import Position, Range

        range_ = Range(
            start=Position(line=0, character=0),
            end=Position(line=0, character=10),
        )
        assert range_.start.line == 0
        assert range_.end.character == 10
