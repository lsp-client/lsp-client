from __future__ import annotations

from pathlib import Path

import pytest

from lsp_client.client.document_state import DocumentState, DocumentStateManager


def test_document_state_immutable():
    state = DocumentState(content="hello", version=0)
    assert state.content == "hello"
    assert state.version == 0


def test_register_document():
    manager = DocumentStateManager()
    manager.register("file:///test.py", "print('hello')", version=0)

    assert manager.get_version("file:///test.py") == 0
    assert manager.get_content("file:///test.py") == "print('hello')"


def test_unregister_document():
    manager = DocumentStateManager()
    manager.register("file:///test.py", "print('hello')")
    manager.unregister("file:///test.py")

    assert manager.get_version("file:///test.py") is None


def test_increment_version():
    manager = DocumentStateManager()
    manager.register("file:///test.py", "print('hello')", version=0)

    new_version = manager.increment_version("file:///test.py")
    assert new_version == 1
    assert manager.get_version("file:///test.py") == 1
    assert manager.get_content("file:///test.py") == "print('hello')"


def test_update_content():
    manager = DocumentStateManager()
    manager.register("file:///test.py", "print('hello')", version=0)

    new_version = manager.update_content("file:///test.py", "print('world')")
    assert new_version == 1
    assert manager.get_version("file:///test.py") == 1
    assert manager.get_content("file:///test.py") == "print('world')"


def test_multiple_documents():
    manager = DocumentStateManager()
    manager.register("file:///test1.py", "content1", version=0)
    manager.register("file:///test2.py", "content2", version=5)

    assert manager.get_version("file:///test1.py") == 0
    assert manager.get_version("file:///test2.py") == 5

    manager.increment_version("file:///test1.py")
    assert manager.get_version("file:///test1.py") == 1
    assert manager.get_version("file:///test2.py") == 5


def test_get_version_nonexistent():
    manager = DocumentStateManager()
    assert manager.get_version("file:///nonexistent.py") is None


def test_get_content_nonexistent():
    manager = DocumentStateManager()
    assert manager.get_content("file:///nonexistent.py") is None


def test_increment_version_nonexistent():
    manager = DocumentStateManager()
    assert manager.increment_version("file:///nonexistent.py") is None


def test_update_content_nonexistent():
    manager = DocumentStateManager()
    assert manager.update_content("file:///nonexistent.py", "new content") is None


def test_register_document_twice():
    """Test that registering a document twice returns None."""
    manager = DocumentStateManager()
    manager.register("file:///test.py", "print('hello')", version=0)

    assert manager.register("file:///test.py", "print('world')", version=0) is None


def test_unregister_nonexistent_document():
    """Test that unregistering a non-existent document returns None."""
    manager = DocumentStateManager()
    assert manager.unregister("file:///nonexistent.py") is None


@pytest.mark.anyio
async def test_open_multiple_uris(tmp_path: Path):
    """Test opening multiple URIs tracking state and reference counts."""
    manager = DocumentStateManager()
    f1 = tmp_path / "f1.py"
    f2 = tmp_path / "f2.py"
    f1.write_text("content1")
    f2.write_text("content2")
    u1, u2 = f1.as_uri(), f2.as_uri()

    new_docs = await manager.open([u1, u2])
    assert len(new_docs) == 2
    assert new_docs[u1].content == "content1"
    assert new_docs[u2].content == "content2"
    assert manager._ref_counts[u1] == 1
    assert manager._ref_counts[u2] == 1


@pytest.mark.anyio
async def test_open_already_open_files(tmp_path: Path):
    """Test that opening already open files only increments reference counts."""
    manager = DocumentStateManager()
    f1 = tmp_path / "f1.py"
    f1.write_text("content1")
    u1 = f1.as_uri()

    await manager.open([u1])
    new_docs = await manager.open([u1])
    assert len(new_docs) == 0
    assert manager._ref_counts[u1] == 2


def test_close_reference_counting():
    """Test closing files with various reference counts."""
    manager = DocumentStateManager()
    u1 = "file:///test.py"
    manager.register(u1, "content")
    # Manual registration starts with ref count 1
    manager._ref_counts[u1] = 2

    # First close: ref count 2 -> 1, not truly closed
    closed = manager.close([u1])
    assert len(closed) == 0
    assert manager._ref_counts[u1] == 1
    assert u1 in manager._states

    # Second close: ref count 1 -> 0, truly closed
    closed = manager.close([u1])
    assert len(closed) == 1
    assert closed[0] == u1
    assert u1 not in manager._ref_counts
    assert u1 not in manager._states


def test_close_zero_or_negative_ref_count():
    """Test closing URIs that already have zero or negative reference counts."""
    manager = DocumentStateManager()
    u1 = "file:///test.py"
    manager.register(u1, "content")
    manager._ref_counts[u1] = 0

    closed = manager.close([u1])
    assert len(closed) == 1
    assert closed[0] == u1
    assert u1 not in manager._ref_counts
    assert u1 not in manager._states


@pytest.mark.anyio
async def test_open_non_utf8_encoding(tmp_path: Path):
    """Test opening a file with non-UTF-8 encoding."""
    manager = DocumentStateManager()
    f1 = tmp_path / "f1.py"
    content = "这是一个测试文件，包含一些中文字符以测试编码检测功能。"  # noqa: RUF001
    f1.write_bytes(content.encode("gbk"))
    u1 = f1.as_uri()

    new_docs = await manager.open([u1])
    assert len(new_docs) == 1
    assert new_docs[u1].content == content
    assert new_docs[u1].encoding.lower() in ("gbk", "gb2312", "cp936", "gb18030")
    assert manager.get_encoding(u1).lower() in ("gbk", "gb2312", "cp936", "gb18030")
