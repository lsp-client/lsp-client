from __future__ import annotations

from collections import Counter
from collections.abc import Iterable

import anyio
import asyncer
from attrs import Factory, define, frozen
from charset_normalizer import from_bytes

from lsp_client.utils.workspace import from_local_uri


@frozen
class DocumentState:
    """
    Represents the state of a single open document.

    Attributes:
        content: Current text content of the document
        version: Current version number (incremented on each change)
        encoding: The encoding used to decode the document from bytes
    """

    content: str
    version: int
    encoding: str = "utf-8"


@define
class DocumentStateManager:
    """
    Manages mutable state of open text documents.

    Tracks URI -> DocumentState mapping for version increments and content updates.
    Also handles file buffering and reference counting for open files.

    Attributes:
        _states: Maps document URI to its current state
        _ref_counts: Tracks how many times each document is open
    """

    _states: dict[str, DocumentState] = Factory(dict)
    _ref_counts: Counter[str] = Factory(Counter)

    async def open(self, uris: Iterable[str]) -> dict[str, DocumentState]:
        """
        Open files and track state. Only return newly opened documents.

        Args:
            uris: List of file URIs to open

        Returns:
            Dictionary mapping URIs to DocumentState for files that were
            not previously open.
        """
        uris = list(uris)
        # Identify which URIs are actually new
        new_uris = [uri for uri in uris if uri not in self._states]

        # Track reference counts for all requested URIs
        self._ref_counts.update(uris)

        if not new_uris:
            return {}

        new_states: dict[str, DocumentState] = {}

        async def read_file(uri: str) -> None:
            path = from_local_uri(uri)
            content_bytes = await anyio.Path(path).read_bytes()
            if best_match := from_bytes(content_bytes).best():
                content = str(best_match)
                encoding = best_match.encoding
            else:
                raise ValueError(
                    f"Unable to decode file content for {uri}: charset detection failed"
                )

            new_states[uri] = DocumentState(content, version=0, encoding=encoding)

        async with asyncer.create_task_group() as tg:
            for uri in new_uris:
                tg.soonify(read_file)(uri)

        self._states.update(new_states)
        return new_states

    def close(self, uris: Iterable[str]) -> list[str]:
        """
        Close files. Return URIs of files that are really closed (ref count reaches 0).

        Args:
            uris: List of file URIs to close

        Returns:
            List of URIs that were removed from the state manager.
        """
        uris = list(uris)
        self._ref_counts.subtract(uris)

        closed_uris: list[str] = []
        for uri in uris:
            if self._ref_counts[uri] <= 0:
                # Ensure we don't keep negative counts or zero counts for long
                del self._ref_counts[uri]
                if uri in self._states:
                    del self._states[uri]
                    closed_uris.append(uri)

        return closed_uris

    def register(
        self, uri: str, content: str, version: int = 0, encoding: str = "utf-8"
    ) -> DocumentState | None:
        """
        Register a newly opened document manually.

        Args:
            uri: Document URI
            content: Initial document content
            version: Initial version (defaults to 0)
            encoding: Document encoding (defaults to utf-8)

        Returns:
            The newly created DocumentState, or None if the URI is already registered.
        """
        if uri in self._states:
            return None
        state = DocumentState(content=content, version=version, encoding=encoding)
        self._states[uri] = state
        # Manual registration implies a reference count of 1
        self._ref_counts[uri] = 1
        return state

    def unregister(self, uri: str) -> DocumentState | None:
        """
        Unregister a closed document.

        Args:
            uri: Document URI

        Returns:
            The removed DocumentState, or None if the URI was not registered.
        """
        if uri in self._states:
            state = self._states.pop(uri)
            # Force cleanup ref count
            if uri in self._ref_counts:
                del self._ref_counts[uri]
            return state
        return None

    def get_version(self, uri: str) -> int | None:
        """
        Get current version of a document.

        Args:
            uri: Document URI

        Returns:
            Current version number, or None if not registered.
        """
        if state := self._states.get(uri):
            return state.version
        return None

    def get_content(self, uri: str) -> str | None:
        """
        Get current content of a document.

        Args:
            uri: Document URI

        Returns:
            Current document content, or None if not registered.
        """
        if state := self._states.get(uri):
            return state.content
        return None

    def get_encoding(self, uri: str, *, default: str = "utf-8") -> str:
        """
        Get current encoding of a document.

        Args:
            uri: Document URI

        Returns:
            Current document encoding, or the default if not registered.
        """
        if state := self._states.get(uri):
            return state.encoding
        return default

    def increment_version(self, uri: str) -> int | None:
        """
        Increment version and return the new version.

        Args:
            uri: Document URI

        Returns:
            New version number after increment, or None if not registered.
        """
        if state := self._states.get(uri):
            new_version = state.version + 1
            self._states[uri] = DocumentState(
                content=state.content, version=new_version, encoding=state.encoding
            )
            return new_version
        return None

    def update_content(self, uri: str, content: str) -> int | None:
        """
        Update content and increment version atomically.

        Args:
            uri: Document URI
            content: New document content

        Returns:
            New version number after update, or None if not registered.
        """
        if state := self._states.get(uri):
            new_version = state.version + 1
            self._states[uri] = DocumentState(
                content=content, version=new_version, encoding=state.encoding
            )
            return new_version
        return None
