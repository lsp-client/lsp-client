"""Language-specific LSP clients."""

from __future__ import annotations

from typing import Final, Literal

from lsp_client.client.abc import Client

from .deno.client import DenoClient
from .gopls import GoplsClient
from .pyright import PyrightClient
from .rust_analyzer import RustAnalyzerClient
from .typescript import TypescriptClient

type Language = Literal[
    "go",
    "python",
    "rust",
    "typescript",
    "deno",
]

GoClient = GoplsClient
PythonClient = PyrightClient
RustClient = RustAnalyzerClient
TypeScriptClient = TypescriptClient

lang_clients: Final[dict[Language, type[Client]]] = {
    "go": GoplsClient,
    "python": PyrightClient,
    "rust": RustAnalyzerClient,
    "typescript": TypescriptClient,
    "deno": DenoClient,
}
