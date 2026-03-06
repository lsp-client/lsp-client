from __future__ import annotations

import json
import re

from anyio.abc import AnyByteSendStream
from anyio.streams.buffered import BufferedByteReceiveStream

from .convert import package_serialize
from .exception import JsonRpcParseError, JsonRpcTransportError
from .types import RawPackage

CONTENT_LENGTH_HEADER_RE = re.compile(r"Content-Length:\s*(?P<length>\d+)")
"""match lsp header line: `Content-Length: ...\r\n`"""


async def read_raw_package(receiver: BufferedByteReceiveStream) -> RawPackage:
    # when process is closed, the reader will always return b''
    header_bytes = await receiver.receive_until(b"\r\n\r\n", max_bytes=65536)
    if not header_bytes:
        raise JsonRpcTransportError("LSP server process closed")

    header = header_bytes.decode("utf-8")
    if header_match := CONTENT_LENGTH_HEADER_RE.search(header):
        length = int(header_match.group("length"))
    else:
        raise JsonRpcParseError("Missing Content-Length header")

    body_bytes = await receiver.receive_exactly(length)
    return json.loads(body_bytes.decode("utf-8"))


async def write_raw_package(sender: AnyByteSendStream, package: RawPackage) -> None:
    dumped = package_serialize(package).encode("utf-8")
    length = len(dumped)

    headers = f"Content-Type: application/vscode-jsonrpc; charset=utf-8\r\nContent-Length: {length}\r\n\r\n".encode()
    await sender.send(headers + dumped)
