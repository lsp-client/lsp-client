from __future__ import annotations

from typing import Final

from .deno import DenoClient
from .gopls import GoplsClient
from .pyrefly import PyreflyClient
from .pyright import PyrightClient
from .rust_analyzer import RustAnalyzerClient
from .ty import TyClient
from .typescript import TypescriptClient

clients: Final = {
    "gopls": GoplsClient,
    "pyrefly": PyreflyClient,
    "pyright": PyrightClient,
    "rust_analyzer": RustAnalyzerClient,
    "deno": DenoClient,
    "typescript": TypescriptClient,
    "ty": TyClient,
}

__all__ = [
    "DenoClient",
    "GoplsClient",
    "PyreflyClient",
    "TyClient",
]
