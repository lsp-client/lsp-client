from __future__ import annotations

from collections import deque
from collections.abc import Iterator
from functools import cached_property

from attrs import field, frozen

from lsp_client.utils.types import lsp_type


def as_pos(p: lsp_type.Position) -> tuple[int, int]:
    """Return the (line, character) tuple representation of an LSP position."""
    return (p.line, p.character)


def contains(range: lsp_type.Range, position: lsp_type.Position) -> bool:
    """Return True if the given position lies within the half-open LSP range."""
    return as_pos(range.start) <= as_pos(position) < as_pos(range.end)


def is_narrower(inner: lsp_type.Range, outer: lsp_type.Range) -> bool:
    """Return True if the inner range is fully contained within the outer range."""
    return (
        as_pos(inner.start) >= as_pos(outer.start)  #
        and as_pos(inner.end) <= as_pos(outer.end)
    )


DocumentSymbolName = str


@frozen(hash=True)
class DocumentSymbolPath:
    """Represents a hierarchical path to a symbol in a document symbol tree.

    The path is modeled as an ordered sequence of symbol names, starting from
    the root symbol and proceeding through each nested child.
    """

    symbols: list[DocumentSymbolName] = field(converter=list)

    @classmethod
    def from_symbols(cls, *symbol: DocumentSymbolName) -> DocumentSymbolPath:
        """Create a DocumentSymbolPath from the given sequence of symbol names."""
        return cls(list(symbol))

    @classmethod
    def from_str(cls, path_str: str) -> DocumentSymbolPath:
        """Create a DocumentSymbolPath from a dot-separated string representation."""
        return cls(path_str.split("."))

    def format(self) -> str:
        """Return the dot-separated string representation of the path."""
        return ".".join(self.symbols)

    def __truediv__(self, other: DocumentSymbolName) -> DocumentSymbolPath:
        return DocumentSymbolPath.from_symbols(*self.symbols, other)


@frozen(slots=False)
class DocumentSymbolHierarchy:
    """Provides navigation and query helpers for a hierarchical document symbol tree.

    This class wraps a root :class:`lsp_type.DocumentSymbol` and exposes utilities to
    resolve symbols by structured path or source position, flatten the symbol tree,
    and traverse it in depth-first or breadth-first order.

    Attributes
    ----------
    root:
        The root document symbol representing the top-level scope of the document.
    """

    root: lsp_type.DocumentSymbol

    @cached_property
    def _symbol_to_path(self) -> dict[int, DocumentSymbolPath]:
        # NOTE: Using id(s) as a key assumes symbol objects are not copied or recreated.
        # This provides efficient O(1) reverse lookup for symbols obtained from this hierarchy.
        return {id(s): path for path, s in self.flattened.items()}

    def at_path(self, path: DocumentSymbolPath) -> lsp_type.DocumentSymbol | None:
        """Return the symbol at the given path, or None if not found."""
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
        """Return the narrowest symbol containing the given position."""
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
        """Return the path to the given symbol object, or None if not in hierarchy."""
        return self._symbol_to_path.get(id(symbol))

    def get_position(self, symbol: lsp_type.DocumentSymbol) -> lsp_type.Position | None:
        """Return the start position of the given symbol, or None if not in hierarchy."""
        if self._symbol_to_path.get(id(symbol)) is None:
            return None
        return symbol.selection_range.start

    @cached_property
    def flattened(self) -> dict[DocumentSymbolPath, lsp_type.DocumentSymbol]:
        """Return a mapping of all paths to their respective symbols."""
        result: dict[DocumentSymbolPath, lsp_type.DocumentSymbol] = {}
        stack = [(DocumentSymbolPath.from_symbols(self.root.name), self.root)]
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
        """Iterate over all symbols in depth-first order."""
        stack = [self.root]
        while stack:
            node = stack.pop()
            yield node
            if node.children:
                stack.extend(reversed(node.children))

    def iter_bfs(self) -> Iterator[lsp_type.DocumentSymbol]:
        """Iterate over all symbols in breadth-first order."""
        queue = deque([self.root])
        while queue:
            node = queue.popleft()
            yield node
            if node.children:
                queue.extend(node.children)
