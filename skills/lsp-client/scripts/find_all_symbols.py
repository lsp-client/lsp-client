#!/usr/bin/env python3
"""Find all symbols (functions, classes, variables) in a file or workspace."""

from pathlib import Path

import anyio
from lsprotocol.types import Location

from lsp_client.clients.pyright import PyrightClient


async def find_document_symbols(file_path: str) -> None:
    workspace = Path.cwd()

    async with PyrightClient(workspace=workspace) as client:
        symbols = await client.request_document_symbol_list(file_path=file_path)

        if not symbols:
            print("No symbols found")
            return

        print(f"\n📚 Document Symbols in {file_path}:")
        for symbol in symbols:
            kind = symbol.kind.name
            range_info = f"{symbol.range.start.line}:{symbol.range.start.character}"
            print(f"  {kind:15} {symbol.name:30} @ {range_info}")


async def find_workspace_symbols(query: str) -> None:
    workspace = Path.cwd()

    async with PyrightClient(workspace=workspace) as client:
        symbols = await client.request_workspace_symbol_list(query=query)

        if not symbols:
            print(f"No symbols found matching '{query}'")
            return

        print(f"\n🔍 Workspace Symbols matching '{query}':")
        for symbol in symbols:
            kind = symbol.kind.name
            location = symbol.location
            if isinstance(location, Location):
                file = client.from_uri(location.uri)
                range_info = (
                    f"{location.range.start.line}:{location.range.start.character}"
                )
                print(f"  {kind:15} {symbol.name:30} @ {file}:{range_info}")
            else:
                file = client.from_uri(location.uri)
                print(f"  {kind:15} {symbol.name:30} @ {file}")


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage:")
        print(
            "  Find symbols in file:      python find_all_symbols.py file <file_path>"
        )
        print(
            "  Search workspace symbols:  python find_all_symbols.py workspace <query>"
        )
        print("\nExamples:")
        print("  python find_all_symbols.py file src/main.py")
        print("  python find_all_symbols.py workspace MyClass")
        sys.exit(1)

    mode = sys.argv[1]

    if mode == "file" and len(sys.argv) == 3:
        anyio.run(find_document_symbols, sys.argv[2])
    elif mode == "workspace" and len(sys.argv) == 3:
        anyio.run(find_workspace_symbols, sys.argv[2])
    else:
        print("Invalid arguments")
        sys.exit(1)
