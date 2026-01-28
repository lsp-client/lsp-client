from lsp_client.utils.symbol import (
    DocumentSymbolHierarchy,
    DocumentSymbolPath,
    as_pos,
    contains,
    is_narrower,
)
from lsp_client.utils.types import lsp_type


def test_as_pos():
    pos = lsp_type.Position(line=10, character=5)
    assert as_pos(pos) == (10, 5)


def test_contains():
    range_ = lsp_type.Range(
        start=lsp_type.Position(line=1, character=0),
        end=lsp_type.Position(line=3, character=0),
    )
    assert contains(range_, lsp_type.Position(line=1, character=0))
    assert contains(range_, lsp_type.Position(line=2, character=5))
    assert not contains(range_, lsp_type.Position(line=3, character=0))
    assert not contains(range_, lsp_type.Position(line=0, character=0))


def test_is_narrower():
    outer = lsp_type.Range(
        start=lsp_type.Position(line=1, character=0),
        end=lsp_type.Position(line=5, character=0),
    )
    inner = lsp_type.Range(
        start=lsp_type.Position(line=2, character=0),
        end=lsp_type.Position(line=4, character=0),
    )
    assert is_narrower(inner, outer)
    assert is_narrower(outer, outer)
    assert not is_narrower(outer, inner)


def test_document_symbol_path():
    path = DocumentSymbolPath(("root", "child"))
    assert path.format() == "root.child"

    new_path = path / "grandchild"
    assert new_path.symbols == ("root", "child", "grandchild")
    assert new_path.format() == "root.child.grandchild"


def test_document_symbol_hierarchy():
    grandchild1 = lsp_type.DocumentSymbol(
        name="grandchild1",
        kind=lsp_type.SymbolKind.Function,
        range=lsp_type.Range(
            start=lsp_type.Position(line=2, character=0),
            end=lsp_type.Position(line=2, character=10),
        ),
        selection_range=lsp_type.Range(
            start=lsp_type.Position(line=2, character=0),
            end=lsp_type.Position(line=2, character=5),
        ),
    )

    child1 = lsp_type.DocumentSymbol(
        name="child1",
        kind=lsp_type.SymbolKind.Class,
        range=lsp_type.Range(
            start=lsp_type.Position(line=1, character=0),
            end=lsp_type.Position(line=3, character=0),
        ),
        selection_range=lsp_type.Range(
            start=lsp_type.Position(line=1, character=0),
            end=lsp_type.Position(line=1, character=5),
        ),
        children=[grandchild1],
    )

    child2 = lsp_type.DocumentSymbol(
        name="child2",
        kind=lsp_type.SymbolKind.Variable,
        range=lsp_type.Range(
            start=lsp_type.Position(line=4, character=0),
            end=lsp_type.Position(line=4, character=10),
        ),
        selection_range=lsp_type.Range(
            start=lsp_type.Position(line=4, character=0),
            end=lsp_type.Position(line=4, character=5),
        ),
    )

    root = lsp_type.DocumentSymbol(
        name="root",
        kind=lsp_type.SymbolKind.File,
        range=lsp_type.Range(
            start=lsp_type.Position(line=0, character=0),
            end=lsp_type.Position(line=5, character=0),
        ),
        selection_range=lsp_type.Range(
            start=lsp_type.Position(line=0, character=0),
            end=lsp_type.Position(line=0, character=5),
        ),
        children=[child1, child2],
    )

    hierarchy = DocumentSymbolHierarchy(root=root)

    # Test at
    assert hierarchy.at(DocumentSymbolPath(("root", "child1"))) is child1
    assert (
        hierarchy.at(DocumentSymbolPath(("root", "child1", "grandchild1")))
        is grandchild1
    )
    assert hierarchy.at(DocumentSymbolPath(("root", "invalid"))) is None

    # Test get_path
    path = hierarchy.get_path(grandchild1)
    assert path is not None
    assert path.format() == "root.child1.grandchild1"

    path = hierarchy.get_path(root)
    assert path is not None
    assert path.format() == "root"

    # Test at_position
    assert hierarchy.at_position(lsp_type.Position(line=2, character=1)) is grandchild1
    assert hierarchy.at_position(lsp_type.Position(line=1, character=1)) is child1
    assert hierarchy.at_position(lsp_type.Position(line=0, character=1)) is root
    assert hierarchy.at_position(lsp_type.Position(line=3, character=0)) is root
    assert hierarchy.at_position(lsp_type.Position(line=6, character=0)) is None

    # Test traversal
    dfs = list(hierarchy.iter_dfs())
    assert dfs == [root, child1, grandchild1, child2]

    bfs = list(hierarchy.iter_bfs())
    assert bfs == [root, child1, child2, grandchild1]

    # Test flattened
    flattened = hierarchy.flattened
    assert len(flattened) == 4
    assert flattened[DocumentSymbolPath(("root", "child2"))] is child2
