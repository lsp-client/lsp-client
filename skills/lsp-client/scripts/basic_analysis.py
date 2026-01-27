#!/usr/bin/env python3
"""Basic LSP analysis: hover, definition, references for a symbol."""

from pathlib import Path

import anyio

from lsp_client import Position
from lsp_client.clients.pyright import PyrightClient


async def analyze_symbol(file_path: str, line: int, character: int) -> None:
    workspace = Path.cwd()

    async with PyrightClient(workspace=workspace) as client:
        position = Position(line, character)

        print("\n📝 Hover Information:")
        hover = await client.request_hover(file_path=file_path, position=position)
        if hover:
            print(f"Kind: {hover.kind.value}")
            print(f"Value: {hover.value}")

        print("\n🎯 Definition:")
        definitions = await client.request_definition_locations(
            file_path=file_path, position=position
        )
        if definitions:
            for def_loc in definitions:
                file = client.from_uri(def_loc.uri)
                print(
                    f"  {file}:{def_loc.range.start.line}:{def_loc.range.start.character}"
                )

        print("\n🔗 References:")
        refs = await client.request_references(
            file_path=file_path, position=position, include_declaration=False
        )
        if refs:
            for ref in refs:
                file = client.from_uri(ref.uri)
                print(f"  {file}:{ref.range.start.line}:{ref.range.start.character}")


if __name__ == "__main__":
    import sys

    if len(sys.argv) != 4:
        print("Usage: python basic_analysis.py <file_path> <line> <character>")
        print("Example: python basic_analysis.py src/main.py 10 5")
        sys.exit(1)

    anyio.run(analyze_symbol, sys.argv[1], int(sys.argv[2]), int(sys.argv[3]))
