"""Language-specific LSP clients."""

from __future__ import annotations

from pathlib import Path
from typing import Final, Literal, NamedTuple

from lsp_client.client.abc import Client

from .basedpyright import BasedpyrightClient
from .deno.client import DenoClient
from .gopls import GoplsClient
from .jdtls import JdtlsClient
from .rust_analyzer import RustAnalyzerClient
from .typescript import TypescriptClient

type Language = Literal[
    "go",
    "python",
    "rust",
    "typescript",
    "deno",
    "java",
]

GoClient = GoplsClient
PythonClient = BasedpyrightClient
RustClient = RustAnalyzerClient
TypeScriptClient = TypescriptClient
JavaClient = JdtlsClient

lang_clients: Final[dict[Language, type[Client]]] = {
    "go": GoplsClient,
    "python": BasedpyrightClient,
    "rust": RustAnalyzerClient,
    "typescript": TypescriptClient,
    "deno": DenoClient,
    "java": JdtlsClient,
}


class ClientTarget(NamedTuple):
    client_cls: type[Client]
    project_path: Path


def find_client(path: Path) -> ClientTarget | None:
    """Identify the appropriate client and project root for a given path."""

    candidates = lang_clients.values()

    for client_cls in candidates:
        lang_config = client_cls.get_language_config()
        if root := lang_config.find_project_root(path):
            return ClientTarget(project_path=root, client_cls=client_cls)
    return None
