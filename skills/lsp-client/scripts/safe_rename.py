#!/usr/bin/env python3
"""Preview and apply rename refactoring safely."""

from pathlib import Path

import anyio
from lsprotocol.types import SnippetTextEdit, TextDocumentEdit

from lsp_client import Position
from lsp_client.clients.pyright import PyrightClient


async def preview_rename(
    file_path: str, line: int, character: int, new_name: str
) -> None:
    workspace = Path.cwd()

    async with PyrightClient(workspace=workspace) as client:
        position = Position(line, character)

        edits = await client.request_rename_edits(
            file_path=file_path,
            position=position,
            new_name=new_name,
        )

        if edits is None:
            print("❌ Rename not possible at this position")
            return

        print(f"\n📝 Renaming to '{new_name}' will affect:")

        if edits.document_changes:
            for change in edits.document_changes:
                match change:
                    case TextDocumentEdit(text_document=doc, edits=text_edits):
                        uri = doc.uri
                        file = client.from_uri(uri)
                        print(f"\n  📄 {file}: {len(text_edits)} changes")
                        for edit in text_edits:
                            start = edit.range.start
                            end = edit.range.end

                            match edit:
                                case SnippetTextEdit(snippet=snippet):
                                    new_text = snippet.value
                                case _:
                                    new_text = edit.new_text

                            print(
                                f"    Line {start.line}:{start.character}-"
                                f"{end.line}:{end.character} → '{new_text}'"
                            )
        elif edits.changes:
            for uri, text_edits in edits.changes.items():
                file = client.from_uri(uri)
                print(f"\n  📄 {file}: {len(text_edits)} changes")

        print("\n✅ Applying rename...")
        await client.apply_workspace_edit(edits)
        print("✅ Rename completed successfully")


if __name__ == "__main__":
    import sys

    if len(sys.argv) != 5:
        print("Usage: python safe_rename.py <file_path> <line> <character> <new_name>")
        print("Example: python safe_rename.py src/main.py 10 5 new_variable_name")
        sys.exit(1)

    anyio.run(
        preview_rename, sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), sys.argv[4]
    )
