"""
Language-specific configuration for LSP clients.

Provides LanguageConfig for defining language properties including file suffixes,
project markers, and project root detection logic.
"""

from __future__ import annotations

from pathlib import Path

from attrs import Factory, frozen

from lsp_client.utils.workspace import lsp_type


@frozen
class LanguageConfig:
    """Configuration for a programming language in the LSP client."""

    kind: lsp_type.LanguageKind
    """The kind of programming language."""

    suffixes: list[str]
    """File suffixes associated with the language."""

    project_files: list[str]
    """Files that indicate the root of a project for this language."""

    exclude_files: list[str] = Factory(list)
    """Files that indicate a directory should not be considered a project root for this language."""

    def _find_project_root(
        self, dir_path: Path, cwd: Path | None = None
    ) -> Path | None:
        """
        Locate the project root directory starting from ``dir_path``.

        When ``cwd`` is not provided, the search walks *upwards* from
        ``dir_path`` through its parents and returns the first directory that:

        * does not contain any of the patterns in :attr:`exclude_files`, and
        * does contain at least one of the patterns in :attr:`project_files`.

        When ``cwd`` is provided, the search is restricted to directories that
        are within ``cwd`` (i.e. ancestors of ``dir_path`` that are also
        descendants of ``cwd``). In this case the search order is effectively
        from ``cwd`` outward towards ``dir_path`` (closest to ``cwd`` first),
        so that project roots nearer to the workspace root are preferred.

        Directories matching :attr:`exclude_files` are treated differently
        depending on ``cwd``:

        * If ``cwd`` is ``None``, encountering an excluded directory stops the
          search and the method returns ``None``.
        * If ``cwd`` is not ``None``, excluded directories are skipped and the
          search continues in other candidate directories within ``cwd``.

        Parameters
        ----------
        dir_path:
            Directory from which to start searching for a project root.
        cwd:
            Optional workspace root. If provided, ``dir_path`` must be
            relative to ``cwd`` and the search is limited to directories that
            are descendants of ``cwd``.

        Returns
        -------
        Path | None
            The detected project root directory, or ``None`` if no suitable
            directory is found.
        """
        if cwd is not None and not dir_path.is_relative_to(cwd):
            raise ValueError(
                f"Path '{dir_path.resolve()}' is not relative to the specified "
                f"working directory '{cwd.resolve()}'. The path must be within "
                f"the working directory or its subdirectories."
            )

        paths = [dir_path, *dir_path.parents]

        if cwd is not None:
            paths = reversed([p for p in paths if p.is_relative_to(cwd)])

        for path in paths:
            if any(
                next(path.glob(pattern), None) is not None
                for pattern in self.exclude_files
            ):
                if cwd is not None:
                    continue
                return None

            if any(
                next(path.glob(pattern), None) is not None
                for pattern in self.project_files
            ):
                return path

        return None

    def find_project_root(self, path: Path, cwd: Path | None = None) -> Path | None:
        """Determine the project root for the given path.

        The project root is the nearest ancestor directory (including the
        directory of ``path``) that contains any of the ``project_files``
        markers defined for this language, taking into account any
        ``exclude_files`` markers that disqualify a directory as a project
        root.

        Parameters
        ----------
        path:
            A file or directory path for which to locate the project root.
            If a file is given, it must have a suffix listed in
            :attr:`suffixes` or ``None`` is returned.
        cwd:
            Optional current working directory that constrains the search.
            When provided, ``path`` must be relative to ``cwd``, and only
            directories within ``cwd`` are considered as candidates for the
            project root.

        Returns
        -------
        Path | None
            The path to the detected project root directory, or ``None`` if
            no suitable project root can be found.
        """
        if cwd is not None and not path.is_relative_to(cwd):
            raise ValueError(
                f"Path '{path.resolve()}' is not relative to the specified "
                f"working directory '{cwd.resolve()}'. The path must be within "
                f"the working directory or its subdirectories."
            )

        if path.is_file():
            if not any(path.name.endswith(suffix) for suffix in self.suffixes):
                return None
            path = path.parent

        return self._find_project_root(path, cwd)
