from __future__ import annotations

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Any, override
from unittest.mock import AsyncMock, MagicMock

from anyio.abc import AnyByteReceiveStream, AnyByteSendStream
from attrs import define, field

from lsp_client.server.abc import StreamServer
from lsp_client.utils.channel import Sender
from lsp_client.utils.workspace import Workspace


@define
class MockServer(StreamServer):
    """A mock server for testing without actual LSP server."""

    _send_stream: MagicMock = field(factory=MagicMock)
    _receive_stream: MagicMock = field(factory=MagicMock)
    _responses: dict[str, Any] = field(factory=dict)
    _notifications: list[dict] = field(factory=list)

    @property
    @override
    def send_stream(self) -> AnyByteSendStream:
        return self._send_stream

    @property
    @override
    def receive_stream(self) -> AnyByteReceiveStream:
        return self._receive_stream

    @override
    async def check_availability(self) -> None:
        """Mock availability check - always available."""

    @override
    async def setup(self, workspace: Workspace) -> None:
        """Mock setup."""

    @asynccontextmanager
    @override
    async def manage_resources(self, workspace: Workspace) -> AsyncGenerator[None]:
        """Mock resource management."""
        yield

    @override
    async def on_started(self, workspace: Workspace, sender: Sender) -> None:
        """Mock on_started hook."""

    @override
    async def on_shutdown(self) -> None:
        """Mock shutdown hook."""

    def set_response(self, method: str, response: Any) -> None:
        """Set a mock response for a request method."""
        self._responses[method] = response

    def get_notifications(self) -> list[dict]:
        """Get all received notifications."""
        return self._notifications.copy()

    def clear_notifications(self) -> None:
        """Clear received notifications."""
        self._notifications.clear()


class MockStream:
    """A mock stream for testing."""

    def __init__(self, data: bytes = b""):
        self.data = data
        self._position = 0

    async def read(self, n: int = -1) -> bytes:
        """Read data from the stream."""
        if self._position >= len(self.data):
            return b""
        result = self.data[self._position : self._position + n]
        self._position += len(result)
        return result

    async def write(self, data: bytes) -> int:
        """Write data to the stream."""
        self.data += data
        return len(data)

    async def close(self) -> None:
        """Close the stream."""


class MockProcess:
    """A mock process for testing local servers."""

    def __init__(self, returncode: int = 0):
        self.returncode = returncode
        self.stdin = MockStream()
        self.stdout = MockStream()
        self.stderr = MockStream()

    def kill(self) -> None:
        """Kill the process."""
        self.returncode = -9

    async def aclose(self) -> None:
        """Await close."""


class MockCapabilityBuilder:
    """A mock capability builder for testing."""

    def __init__(self):
        self._capabilities: dict[str, Any] = {}

    def add_capability(self, category: str, capability: str, value: Any) -> None:
        """Add a capability."""
        if category not in self._capabilities:
            self._capabilities[category] = {}
        self._capabilities[category][capability] = value

    def build(self) -> dict[str, Any]:
        """Build the capabilities dict."""
        return self._capabilities


class MockLSPMessageBuilder:
    """A builder for creating LSP messages for testing."""

    def __init__(self):
        self._id = 0

    def new_id(self) -> str:
        """Generate a new message ID."""
        self._id += 1
        return str(self._id)

    def build_request(self, method: str, params: dict | None = None) -> dict[str, Any]:
        """Build a JSON-RPC request."""
        return {
            "jsonrpc": "2.0",
            "id": self.new_id(),
            "method": method,
            "params": params or {},
        }

    def build_notification(
        self, method: str, params: dict | None = None
    ) -> dict[str, Any]:
        """Build a JSON-RPC notification."""
        return {
            "jsonrpc": "2.0",
            "method": method,
            "params": params or {},
        }

    def build_response(self, id: str, result: Any) -> dict[str, Any]:
        """Build a JSON-RPC response."""
        return {
            "jsonrpc": "2.0",
            "id": id,
            "result": result,
        }

    def build_error_response(
        self, id: str, code: int, message: str, data: Any = None
    ) -> dict[str, Any]:
        """Build a JSON-RPC error response."""
        error = {
            "code": code,
            "message": message,
        }
        if data is not None:
            error["data"] = data
        return {
            "jsonrpc": "2.0",
            "id": id,
            "error": error,
        }


class AsyncMockFactory:
    """Factory for creating async mocks."""

    @staticmethod
    def create(return_value: Any = None) -> AsyncMock:
        """Create an async mock with a default return value."""
        mock = AsyncMock()
        mock.return_value = return_value
        return mock

    @staticmethod
    def create_side_effect(side_effect: Any) -> AsyncMock:
        """Create an async mock with a side effect."""
        mock = AsyncMock()
        mock.side_effect = side_effect
        return mock


def create_mock_capability(
    capability_type: str, supported: bool = True
) -> dict[str, Any]:
    """Create a mock capability structure."""
    return {capability_type: supported}


def create_mock_server_capabilities(
    methods: list[str] | None = None,
) -> dict[str, Any]:
    """Create mock server capabilities."""
    methods = methods or []
    capabilities = {
        "completionProvider": {"resolveProvider": False},
        "hoverProvider": True,
        "definitionProvider": True,
        "referencesProvider": True,
        "documentSymbolProvider": True,
        "workspaceSymbolProvider": True,
    }
    # Add methods that are supported
    for method in methods:
        if method not in capabilities:
            capabilities[method] = True
    return capabilities


def create_mock_client_capabilities(
    text_document_sync: str = "incremental",
) -> dict[str, Any]:
    """Create mock client capabilities."""
    return {
        "workspace": {},
        "textDocument": {
            "synchronization": {"dynamicRegistration": True},
        },
        "notebookDocument": {"synchronization": {}},
        "window": {},
        "general": {},
    }
