# LSP Test Framework Summary

This directory contains a robust LSP (Language Server Protocol) testing framework designed to facilitate integration testing of various language clients and servers.

## Architecture

- **`framework/lsp.py`**: The core testing engine.
  - Utilizes Python 3.12 modern generics (`PEP 695`) and Protocol-based capability detection.
  - `LspInteraction[C]`: Provides a high-level API to interact with the LSP client `C`.
    - Automatically detects client capabilities via `runtime_checkable` protocols (e.g., `WithRequestDefinition`).
    - Leverages built-in capability synchronization mixins, eliminating the need for manual file opening/closing in tests.
  - `DefinitionAssertion` & `HoverAssertion`: Fluent assertion objects for validating LSP responses.
    - `DefinitionAssertion` supports `Location`, `LocationLink`, and sequences of both.
  - `lsp_interaction_context`: An async context manager for safe setup and teardown of the LSP environment.

## Test Categories

1. **Unit Tests**: Standard pytest files checking internal logic.
2. **LSP Integration Tests (`test_*_lsp.py`)**: End-to-end tests that launch a real LSP server and verify capabilities.
3. **Conformance Tests (`test_*_conformance.py`)**: Leverages official test suites (e.g., Pyrefly's third-party conformance tests) to ensure the client-server interaction adheres to language specifications.

## Usage Example

```python
async with lsp_interaction_context(PyreflyClient) as interaction:
    await interaction.create_file("main.py", "def hello(): pass\nhello()")
    
    assertion = await interaction.request_definition("main.py", 1, 0)
    assertion.expect_definition("main.py", 0, 4, 0, 9)
```

## Fixtures & Links

- `tests/fixtures/pyrefly`: Symlinked to `references/pyrefly/conformance/third_party`.
- `tests/fixtures/pyrefly_lsp`: Symlinked to `references/pyrefly/pyrefly/lib/test/lsp/lsp_interaction/test_files`.

These links allow the framework to use actual test files from the server's own repository, ensuring parity between client and server expectations.
