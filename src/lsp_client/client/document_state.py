from __future__ import annotations

from collections import Counter
from collections.abc import Iterable

import anyio
import asyncer
from attrs import Factory, define, frozen

from lsp_client.utils.workspace import from_local_uri


@frozen
class DocumentState:
    """
    Represents the state of a single open document.

    Attributes:
        content: Current text content of the document
        version: Current version number (incremented on each change)
    """

    content: str
    version: int


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
            # TODO: Handle IO errors gracefully?
            path = from_local_uri(uri)
            content_bytes = await anyio.Path(path).read_bytes()
            content = content_bytes.decode("utf-8")
            new_states[uri] = DocumentState(content=content, version=0)

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

    def register(self, uri: str, content: str, version: int = 0) -> None:
        """
        Register a newly opened document manually.

        Args:
            uri: Document URI
            content: Initial document content
            version: Initial version (defaults to 0)

        Raises:
            KeyError: If the document URI is already registered
        """
        if uri in self._states:
            raise KeyError(f"Document {uri} is already registered in state manager")
        self._states[uri] = DocumentState(content=content, version=version)
        # Manual registration implies a reference count of 1
        self._ref_counts[uri] = 1

    def unregister(self, uri: str) -> None:
        """
        Unregister a closed document.

        Args:
            uri: Document URI

        Raises:
            KeyError: If document URI is not registered
        """
        if uri in self._states:
            del self._states[uri]
            # Force cleanup ref count
            if uri in self._ref_counts:
                del self._ref_counts[uri]
            return
        raise KeyError(f"Document {uri} not found in state manager")

    def get_version(self, uri: str) -> int:
        """
        Get current version of a document.

        Args:
            uri: Document URI

        Returns:
            Current version number

        Raises:
            KeyError: If document URI is not registered
        """
        if state := self._states.get(uri):
            return state.version
        raise KeyError(f"Document {uri} not found in state manager")

    def get_content(self, uri: str) -> str:
        """
        Get current content of a document.

        Args:
            uri: Document URI

        Returns:
            Current document content

        Raises:
            KeyError: If document URI is not registered
        """
        if state := self._states.get(uri):
            return state.content
        raise KeyError(f"Document {uri} not found in state manager")

    def increment_version(self, uri: str) -> int:
        """
        Increment version and return the new version.

        Args:
            uri: Document URI

        Returns:
            New version number after increment

        Raises:
            KeyError: If document URI is not registered
        """
        if state := self._states.get(uri):
            new_version = state.version + 1
            self._states[uri] = DocumentState(
                content=state.content, version=new_version
            )
            return new_version
        raise KeyError(f"Document {uri} not found in state manager")

    def update_content(self, uri: str, content: str) -> int:
        """
        Update content and increment version atomically.

        Args:
            uri: Document URI
            content: New document content

        Returns:
            New version number after update

        Raises:
            KeyError: If document URI is not registered
        """
        if state := self._states.get(uri):
            new_version = state.version + 1
            self._states[uri] = DocumentState(content=content, version=new_version)
            return new_version
        raise KeyError(f"Document {uri} not found in state manager")
