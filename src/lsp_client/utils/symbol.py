from __future__ import annotations

from collections import deque
from collections.abc import Iterator

from attrs import field, frozen

from lsp_client.utils.types import lsp_type

DocumentSymbolName = str


@frozen(hash=True)
class DocumentSymbolPath:
    symbols: tuple[DocumentSymbolName, ...] = field(converter=tuple)

    def format(self) -> str:
        return ".".join(self.symbols)

    def __truediv__(self, other: DocumentSymbolName) -> DocumentSymbolPath:
        return DocumentSymbolPath((*self.symbols, other))


@frozen
class DocumentSymbolHierarchy:
    root: lsp_type.DocumentSymbol

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

    def flatten(self) -> dict[DocumentSymbolPath, lsp_type.DocumentSymbol]:
        result: dict[DocumentSymbolPath, lsp_type.DocumentSymbol] = {}
        stack = [(DocumentSymbolPath((self.root.name,)), self.root)]
        while stack:
            path, node = stack.pop()
            result[path] = node
            if node.children:
                stack.extend(
                    (path / child.name, child) for child in reversed(node.children)
                )
        return result

    def iter_dfs(self) -> Iterator[lsp_type.DocumentSymbol]:
        stack = [self.root]
        while stack:
            node = stack.pop()
            yield node
            if node.children:
                stack.extend(reversed(node.children))

    def iter_bfs(self) -> Iterator[lsp_type.DocumentSymbol]:
        queue = deque([self.root])
        while queue:
            node = queue.popleft()
            yield node
            if node.children:
                queue.extend(node.children)
