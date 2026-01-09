"""Language-specific LSP clients."""

from __future__ import annotations

from typing import Final, Literal

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
