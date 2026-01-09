from __future__ import annotations

from abc import ABC
from typing import override

from lsp_client.client.abc import Client
from lsp_client.protocol.lang import LanguageConfig
from lsp_client.utils.types import lsp_type


class PythonClientBase(Client, ABC):
    """
    Base class for Python language server clients.

    Provides Python-specific configuration including file extensions (.py, .pyi)
    and common project configuration files (pyproject.toml, setup.py, etc.).

    Subclasses must implement:
        create_default_servers(): Create server runtime instances
        check_server_compatibility(): Verify server version compatibility
    """

    @override
    @classmethod
    def get_language_config(cls) -> LanguageConfig:
        return LanguageConfig(
            kind=lsp_type.LanguageKind.Python,
            suffixes=[".py", ".pyi"],
            project_files=[
                "pyproject.toml",
                "setup.py",
                "setup.cfg",
                "requirements.txt",
                ".python-version",
            ],
        )


class RustClientBase(Client, ABC):
    """
    Base class for Rust language server clients.

    Provides Rust-specific configuration including file extension (.rs)
    and project configuration (Cargo.toml).

    Subclasses must implement:
        create_default_servers(): Create server runtime instances
        check_server_compatibility(): Verify server version compatibility
    """

    @override
    @classmethod
    def get_language_config(cls) -> LanguageConfig:
        return LanguageConfig(
            kind=lsp_type.LanguageKind.Rust,
            suffixes=[".rs"],
            project_files=["Cargo.toml"],
        )


class GoClientBase(Client, ABC):
    """
    Base class for Go language server clients.

    Provides Go-specific configuration including file extension (.go)
    and project configuration (go.mod).

    Subclasses must implement:
        create_default_servers(): Create server runtime instances
        check_server_compatibility(): Verify server version compatibility
    """

    @override
    @classmethod
    def get_language_config(cls) -> LanguageConfig:
        return LanguageConfig(
            kind=lsp_type.LanguageKind.Go,
            suffixes=[".go"],
            project_files=["go.mod"],
        )


class TypeScriptClientBase(Client, ABC):
    """
    Base class for TypeScript/JavaScript language server clients.

    Provides TypeScript-specific configuration including file extensions
    (.ts, .tsx, .js, .jsx, .mjs, .cjs) and project configuration
    (package.json, tsconfig.json, jsconfig.json).

    Subclasses must implement:
        create_default_servers(): Create server runtime instances
        check_server_compatibility(): Verify server version compatibility
    """

    @override
    @classmethod
    def get_language_config(cls) -> LanguageConfig:
        return LanguageConfig(
            kind=lsp_type.LanguageKind.TypeScript,
            suffixes=[".ts", ".tsx", ".js", ".jsx", ".mjs", ".cjs"],
            project_files=["package.json", "tsconfig.json", "jsconfig.json"],
        )


class JavaClientBase(Client, ABC):
    """
    Base class for Java language server clients.

    Provides Java-specific configuration including file extensions (.java)
    and common project configuration files (pom.xml, build.gradle, etc.).

    Subclasses must implement:
        create_default_servers(): Create server runtime instances
        check_server_compatibility(): Verify server version compatibility
    """

    @override
    @classmethod
    def get_language_config(cls) -> LanguageConfig:
        return LanguageConfig(
            kind=lsp_type.LanguageKind.Java,
            suffixes=[".java"],
            project_files=[
                "pom.xml",
                "build.gradle",
                "build.gradle.kts",
                ".project",
                "settings.gradle",
                "settings.gradle.kts",
            ],
        )
