from __future__ import annotations

from collections import deque
from collections.abc import Iterator
from functools import cached_property

from attrs import field, frozen

from lsp_client.utils.types import lsp_type


def as_pos(p: lsp_type.Position) -> tuple[int, int]:
    return (p.line, p.character)


def contains(range: lsp_type.Range, position: lsp_type.Position) -> bool:
    return as_pos(range.start) <= as_pos(position) < as_pos(range.end)


def is_narrower(inner: lsp_type.Range, outer: lsp_type.Range) -> bool:
    return as_pos(inner.start) >= as_pos(outer.start) and as_pos(inner.end) <= as_pos(
        outer.end
    )


DocumentSymbolName = str


@frozen(hash=True)
class DocumentSymbolPath:
    symbols: tuple[DocumentSymbolName, ...] = field(converter=tuple)

    def format(self) -> str:
        return ".".join(self.symbols)

    def __truediv__(self, other: DocumentSymbolName) -> DocumentSymbolPath:
        return DocumentSymbolPath((*self.symbols, other))


@frozen(slots=False)
class DocumentSymbolHierarchy:
    root: lsp_type.DocumentSymbol

    @cached_property
    def _symbol_to_path(self) -> dict[int, DocumentSymbolPath]:
        return {id(s): path for path, s in self.flattened.items()}

    def at(self, path: DocumentSymbolPath) -> lsp_type.DocumentSymbol | None:
        if not path.symbols or path.symbols[0] != self.root.name:
            return None

        current = self.root
        for name in path.symbols[1:]:
            child = next((c for c in current.children or () if c.name == name), None)
            if child is None:
                return None
            current = child
        return current

    def at_position(
        self, position: lsp_type.Position
    ) -> lsp_type.DocumentSymbol | None:
        if not contains(self.root.range, position):
            return None

        current = self.root
        while True:
            best_child = None
            for child in current.children or ():
                if contains(child.range, position) and (
                    best_child is None or is_narrower(child.range, best_child.range)
                ):
                    best_child = child

            if best_child is None:
                return current
            current = best_child

    def get_path(self, symbol: lsp_type.DocumentSymbol) -> DocumentSymbolPath | None:
        return self._symbol_to_path.get(id(symbol))

    @cached_property
    def flattened(self) -> dict[DocumentSymbolPath, lsp_type.DocumentSymbol]:
        result: dict[DocumentSymbolPath, lsp_type.DocumentSymbol] = {}
        stack = [(DocumentSymbolPath((self.root.name,)), self.root)]
        while stack:
            path, node = stack.pop()
            result[path] = node
            if node.children:
                stack.extend(
                    (path / child.name, child)  #
                    for child in reversed(node.children)
                )
        return result

    def iter_dfs(self) -> Iterator[lsp_type.DocumentSymbol]:
        stack = [self.root]
        while stack:
            node = stack.pop()
            yield node
            if node.children:
                stack.extend(node.children)

    def iter_bfs(self) -> Iterator[lsp_type.DocumentSymbol]:
        queue = deque([self.root])
        while queue:
            node = queue.popleft()
            yield node
            if node.children:
                queue.extend(node.children)
