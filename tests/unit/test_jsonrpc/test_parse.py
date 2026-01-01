from __future__ import annotations

import json
from unittest.mock import AsyncMock

import pytest
from anyio.streams.buffered import BufferedByteReceiveStream

from lsp_client.jsonrpc.exception import JsonRpcParseError, JsonRpcTransportError
from lsp_client.jsonrpc.parse import read_raw_package, write_raw_package
from lsp_client.jsonrpc.types import RawNotification


@pytest.mark.asyncio
async def test_read_raw_package():
    mock_receiver = AsyncMock(spec=BufferedByteReceiveStream)

    # Mock header
    mock_receiver.receive_until.side_effect = [b"Content-Length: 18\r\n", b"\r\n"]
    # Mock body
    body = {"test": "data"}
    mock_receiver.receive_exactly.return_value = json.dumps(body).encode("utf-8")

    result = await read_raw_package(mock_receiver)
    assert result == body
    assert mock_receiver.receive_until.call_count == 2
    mock_receiver.receive_exactly.assert_called_once_with(18)


@pytest.mark.asyncio
async def test_read_raw_package_closed():
    mock_receiver = AsyncMock(spec=BufferedByteReceiveStream)
    mock_receiver.receive_until.return_value = b""

    with pytest.raises(JsonRpcTransportError, match="LSP server process closed"):
        await read_raw_package(mock_receiver)


@pytest.mark.asyncio
async def test_read_raw_package_invalid_header():
    mock_receiver = AsyncMock(spec=BufferedByteReceiveStream)
    mock_receiver.receive_until.return_value = b"Invalid-Header\r\n"

    with pytest.raises(JsonRpcParseError, match="Invalid LSP response header"):
        await read_raw_package(mock_receiver)


@pytest.mark.asyncio
async def test_write_raw_package():
    mock_sender = AsyncMock()
    package: RawNotification = {"jsonrpc": "2.0", "method": "test", "params": None}

    await write_raw_package(mock_sender, package)

    # Check that send was called with correct header and body
    dumped = json.dumps(package).encode("utf-8")
    expected = f"Content-Length: {len(dumped)}\r\n\r\n".encode() + dumped

    mock_sender.send.assert_called_once_with(expected)
