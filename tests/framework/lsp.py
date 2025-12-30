from __future__ import annotations

import tempfile
from collections.abc import AsyncGenerator, Sequence
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any

import attrs

from lsp_client.capability.request.definition import WithRequestDefinition
from lsp_client.capability.request.hover import WithRequestHover
from lsp_client.client.abc import Client
from lsp_client.utils.types import Position, Range, lsp_type

type LspResponse[R] = R | None


@attrs.define
class LspInteraction[C: Client]:
    client: C
    workspace_root: Path

    def full_path(self, relative_path: str) -> Path:
        return (self.workspace_root / relative_path).resolve()

    async def create_file(self, relative_path: str, content: str) -> Path:
        path = self.full_path(relative_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content)
        return path

    async def request_definition(
        self, relative_path: str, line: int, column: int
    ) -> DefinitionAssertion:
        assert isinstance(self.client, WithRequestDefinition)
        path = self.full_path(relative_path)
        resp = await self.client.request_definition(
            file_path=path,
            position=Position(line=line, character=column),
        )
        return DefinitionAssertion(self, resp)

    async def request_hover(
        self, relative_path: str, line: int, column: int
    ) -> HoverAssertion:
        assert isinstance(self.client, WithRequestHover)
        path = self.full_path(relative_path)
        resp = await self.client.request_hover(
            file_path=path,
            position=Position(line=line, character=column),
        )
        return HoverAssertion(self, resp)


@attrs.define
class DefinitionAssertion:
    interaction: LspInteraction[Any]
    response: (
        lsp_type.Location
        | Sequence[lsp_type.Location]
        | Sequence[lsp_type.LocationLink]
        | None
    )

    def expect_definition(
        self,
        relative_path: str,
        start_line: int,
        start_col: int,
        end_line: int,
        end_col: int,
    ) -> None:
        assert self.response is not None, "Definition response is None"

        expected_path = self.interaction.full_path(relative_path)
        expected_range = Range(
            start=Position(line=start_line, character=start_col),
            end=Position(line=end_line, character=end_col),
        )

        match self.response:
            case lsp_type.Location() as loc:
                actual_path = self.interaction.client.from_uri(loc.uri)
                assert Path(actual_path).resolve() == expected_path, (
                    f"Expected path {expected_path}, got {actual_path}"
                )
                assert loc.range == expected_range
            case list() | Sequence() as locs:
                found = False
                for loc in locs:
                    if isinstance(loc, lsp_type.Location):
                        actual_path = self.interaction.client.from_uri(loc.uri)
                        actual_range = loc.range
                    elif isinstance(loc, lsp_type.LocationLink):
                        actual_path = self.interaction.client.from_uri(loc.target_uri)
                        actual_range = loc.target_selection_range
                    else:
                        continue

                    if (
                        Path(actual_path).resolve() == expected_path
                        and actual_range == expected_range
                    ):
                        found = True
                        break

                assert found, (
                    f"Definition not found at {expected_path}:{expected_range}"
                )
            case _:
                raise TypeError(
                    f"Unexpected definition response type: {type(self.response)}"
                )


@attrs.define
class HoverAssertion:
    interaction: LspInteraction[Any]
    response: lsp_type.MarkupContent | None

    def expect_content(self, pattern: str) -> None:
        assert self.response is not None, "Hover response is None"
        assert pattern in self.response.value, (
            f"Expected '{pattern}' in hover content, got '{self.response.value}'"
        )


@asynccontextmanager
async def lsp_interaction_context[C: Client](
    client_cls: type[C], workspace_root: Path | None = None, **client_kwargs: Any
) -> AsyncGenerator[LspInteraction[C], None]:
    if workspace_root is None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir).resolve()
            async with client_cls(workspace=root, **client_kwargs) as client:
                yield LspInteraction(client=client, workspace_root=root)
    else:
        root = workspace_root.resolve()
        async with client_cls(workspace=root, **client_kwargs) as client:
            yield LspInteraction(client=client, workspace_root=root)
