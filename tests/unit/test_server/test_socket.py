from __future__ import annotations

import platform
from unittest.mock import AsyncMock, patch

import anyio
import pytest
from anyio.abc import ByteStream

from lsp_client.server.error import ServerRuntimeError
from lsp_client.server.socket import SocketServer


@pytest.mark.asyncio
async def test_socket_server_connect_tcp():
    server = SocketServer(connection=("localhost", 8080))

    mock_stream = AsyncMock(spec=ByteStream)

    with patch("anyio.connect_tcp", return_value=mock_stream) as mock_connect:
        stream = await server.connect()
        assert stream == mock_stream
        mock_connect.assert_called_once_with("localhost", 8080)


@pytest.mark.asyncio
async def test_socket_server_connect_unix():
    if platform.platform().startswith("Windows"):
        pytest.skip("Unix sockets not supported on Windows")

    server = SocketServer(connection="/tmp/test.sock")

    mock_stream = AsyncMock(spec=ByteStream)

    with patch("anyio.connect_unix", return_value=mock_stream) as mock_connect:
        stream = await server.connect()
        assert stream == mock_stream
        mock_connect.assert_called_once_with("/tmp/test.sock")


@pytest.mark.asyncio
async def test_socket_server_connect_unix_windows():
    if not platform.platform().startswith("Windows"):
        pytest.skip("This test is only for Windows")

    server = SocketServer(connection="/tmp/test.sock")

    with pytest.raises(
        ServerRuntimeError, match="Unix sockets are not supported on Windows"
    ):
        await server.connect()


@pytest.mark.asyncio
async def test_socket_server_check_availability_success():
    server = SocketServer(connection=("localhost", 8080))

    mock_stream = AsyncMock(spec=ByteStream)

    with patch("anyio.connect_tcp", return_value=mock_stream):
        await server.check_availability()
        mock_stream.aclose.assert_called_once()


@pytest.mark.asyncio
async def test_socket_server_check_availability_failure():
    server = SocketServer(connection=("localhost", 8080))

    with (
        patch("anyio.connect_tcp", side_effect=anyio.ConnectionFailed()),
        pytest.raises(ServerRuntimeError, match="Failed to connect to socket"),
    ):
        await server.check_availability()


@pytest.mark.asyncio
async def test_socket_server_kill():
    server = SocketServer(connection=("localhost", 8080))
    mock_stream = AsyncMock(spec=ByteStream)
    server._stream = mock_stream

    await server.kill()
    mock_stream.aclose.assert_called_once()
