from __future__ import annotations

from pathlib import Path

import pytest

from lsp_client.protocol.lang import LanguageConfig
from lsp_client.utils.types import lsp_type


@pytest.fixture
def tmp_project(tmp_path: Path) -> Path:
    """Create a temporary project structure for testing."""
    project = tmp_path / "workspace" / "project"
    project.mkdir(parents=True)

    (project / "pyproject.toml").write_text("[tool.poetry]\n")
    (project / "src").mkdir()
    (project / "src" / "main.py").write_text("print('hello')\n")
    (project / "src" / "subdir").mkdir()
    (project / "src" / "subdir" / "module.py").write_text("pass\n")

    return project


@pytest.fixture
def python_config() -> LanguageConfig:
    return LanguageConfig(
        kind=lsp_type.LanguageKind.Python,
        suffixes=[".py"],
        project_files=["pyproject.toml", "setup.py"],
    )


def test_find_project_root_from_file(tmp_project: Path, python_config: LanguageConfig):
    file_path = tmp_project / "src" / "main.py"
    result = python_config.find_project_root(file_path)
    assert result == tmp_project


def test_find_project_root_from_nested_file(
    tmp_project: Path, python_config: LanguageConfig
):
    file_path = tmp_project / "src" / "subdir" / "module.py"
    result = python_config.find_project_root(file_path)
    assert result == tmp_project


def test_find_project_root_from_directory(
    tmp_project: Path, python_config: LanguageConfig
):
    dir_path = tmp_project / "src"
    result = python_config.find_project_root(dir_path)
    assert result == tmp_project


def test_find_project_root_not_found(tmp_path: Path, python_config: LanguageConfig):
    file_path = tmp_path / "random" / "file.py"
    file_path.parent.mkdir(parents=True)
    file_path.write_text("pass\n")
    result = python_config.find_project_root(file_path)
    assert result is None


def test_find_project_root_wrong_suffix(
    tmp_project: Path, python_config: LanguageConfig
):
    file_path = tmp_project / "src" / "file.txt"
    file_path.write_text("text\n")
    result = python_config.find_project_root(file_path)
    assert result is None


def test_is_project_root(tmp_path: Path, python_config: LanguageConfig):
    project = tmp_path / "project"
    project.mkdir()
    (project / "pyproject.toml").write_text("[tool.poetry]\n")

    assert python_config.is_project_root(project) is True
    assert python_config.is_project_root(tmp_path) is False


def test_is_project_root_with_exclude(tmp_path: Path):
    config = LanguageConfig(
        kind=lsp_type.LanguageKind.Python,
        suffixes=[".py"],
        project_files=["pyproject.toml"],
        exclude_files=[".git"],
    )
    project = tmp_path / "project"
    project.mkdir()
    (project / "pyproject.toml").write_text("[tool.poetry]\n")
    (project / ".git").mkdir()

    assert config.is_project_root(project) is False


def test_find_project_root_skips_excluded(tmp_path: Path):
    config = LanguageConfig(
        kind=lsp_type.LanguageKind.Python,
        suffixes=[".py"],
        project_files=["pyproject.toml"],
        exclude_files=[".git"],
    )
    outer = tmp_path / "outer"
    inner = tmp_path / "outer" / "inner"
    inner.mkdir(parents=True)

    (outer / "pyproject.toml").write_text("outer")
    (inner / "pyproject.toml").write_text("inner")
    (inner / ".git").mkdir()

    file_path = inner / "main.py"
    file_path.write_text("pass")

    result = config.find_project_root(file_path)
    assert result == outer


def test_find_project_root_with_glob_pattern(tmp_path: Path):
    config = LanguageConfig(
        kind=lsp_type.LanguageKind.Python,
        suffixes=[".py"],
        project_files=["*.toml"],
    )

    project = tmp_path / "project"
    project.mkdir()
    (project / "pyproject.toml").write_text("[tool.poetry]\n")
    file_path = project / "main.py"
    file_path.write_text("pass\n")

    result = config.find_project_root(file_path)
    assert result == project


def test_find_project_root_with_exclude_files(tmp_path: Path):
    config = LanguageConfig(
        kind=lsp_type.LanguageKind.Python,
        suffixes=[".py"],
        project_files=["pyproject.toml"],
        exclude_files=[".git"],
    )

    project = tmp_path / "project"
    project.mkdir()
    (project / "pyproject.toml").write_text("[tool.poetry]\n")
    (project / ".git").mkdir()
    file_path = project / "main.py"
    file_path.write_text("pass\n")

    result = config.find_project_root(file_path)
    assert result is None


def test_find_project_root_with_glob_exclude_pattern(tmp_path: Path):
    config = LanguageConfig(
        kind=lsp_type.LanguageKind.Python,
        suffixes=[".py"],
        project_files=["pyproject.toml"],
        exclude_files=["*.git"],
    )

    project = tmp_path / "project"
    project.mkdir()
    (project / "pyproject.toml").write_text("[tool.poetry]\n")
    (project / ".git").mkdir()
    file_path = project / "main.py"
    file_path.write_text("pass\n")

    result = config.find_project_root(file_path)
    assert result is None
