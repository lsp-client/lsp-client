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

- **`framework/mocks.py`**: Mock implementations for testing without real servers.
  - `MockServer`: Mock server for unit testing
  - `MockStream`: Mock stream for testing I/O
  - `MockLSPMessageBuilder`: Builder for creating LSP messages

- **`conftest.py`**: Pytest configuration and shared fixtures.
  - Common fixtures for all tests
  - Test markers configuration

## Test Categories

1. **Unit Tests** (`tests/unit/`): Tests for individual components in isolation
   - `test_client/`: Client module tests (including `test_default_configuration.py`)
   - `test_server/`: Server module tests
   - `test_jsonrpc/`: JSON-RPC layer tests
   - `test_capability/`: Capability system tests
   - `test_utils/`: Utility function tests
   - `test_protocol/`: Protocol layer tests

2. **Integration Tests** (`tests/integration/`): Tests for component interaction
   - `test_clients/`: Client integration tests

3. **End-to-End Tests** (`tests/e2e/`): Tests with real LSP servers
   - `test_lsp_interaction.py`: Complete LSP workflow tests
   - `test_pyrefly_lsp.py`: Pyrefly client LSP interaction tests
   - `test_pyrefly_conformance.py`: Pyrefly conformance tests
   - `test_inspect_clients.py`: Client capability inspection tests

4. **Conformance Tests**: Leverages official test suites (e.g., Pyrefly's third-party conformance tests) to ensure the client-server interaction adheres to language specifications.

5. **Regression Tests** (`tests/regression/`): Tests for specific bug fixes and edge cases.

6. **Performance Tests** (`tests/performance/`): Benchmarking tests for critical paths.

## Usage Example

### Unit Test
```python
def test_request_serialize(self):
    """Test that request serialization works."""
    from lsp_client.jsonrpc.convert import request_serialize
    from lsp_client.utils.types import lsp_type

    request = lsp_type.InitializeRequest(id="initialize", params=...)
    result = request_serialize(request)
    assert result["jsonrpc"] == "2.0"
```

### Integration Test
```python
@pytest.mark.asyncio
async def test_notification_flow(self, mock_server):
    """Test textDocument/didOpen notification flow."""
    # Verify notification handling
    pass
```

### LSP Integration Test
```python
async with lsp_interaction_context(PyreflyClient) as interaction:
    await interaction.create_file("main.py", "def hello(): pass\nhello()")

    assertion = await interaction.request_definition("main.py", 1, 0)
    assertion.expect_definition("main.py", 0, 4, 0, 9)
```

## Fixtures & Links

To run the full test suite including conformance tests, you need to set up the pyrefly test fixtures:

```bash
bash scripts/setup_fixtures.sh
```

This script will:
1. Clone the pyrefly repository to `references/pyrefly`
2. Create symbolic links:
   - `tests/fixtures/pyrefly` → `references/pyrefly/conformance/third_party`
   - `tests/fixtures/pyrefly_lsp` → `references/pyrefly/pyrefly/lib/test/lsp/lsp_interaction/test_files`

These links allow the framework to use actual test files from the pyrefly server's own repository, ensuring parity between client and server expectations.

**Note**: Tests that require these fixtures are marked with `@pytest.mark.requires_fixtures` and will be automatically skipped if the fixtures are not available.

## Test Markers

- `@pytest.mark.unit` - Unit tests
- `@pytest.mark.integration` - Integration tests
- `@pytest.mark.e2e` - End-to-end tests
- `@pytest.mark.regression` - Regression tests
- `@pytest.mark.performance` - Performance tests
- `@pytest.mark.slow` - Slow-running tests
- `@pytest.mark.requires_server` - Requires server installation
- `@pytest.mark.requires_fixtures` - Requires pyrefly fixtures
- `@pytest.mark.asyncio` - Async tests

## Running Tests

```bash
# Run all tests
uv run pytest

# Run specific category
uv run pytest -m unit
uv run pytest -m integration
uv run pytest -m e2e

# Run with coverage
uv run pytest --cov=lsp_client

# Run lint check
uv run ruff check tests/
```

## Current Test Coverage

The test framework currently includes:

- ✅ Unit tests for Client module (`tests/unit/test_client/`)
- ✅ Unit tests for Server module (`tests/unit/test_server/`)
- ✅ Unit tests for JSON-RPC layer (`tests/unit/test_jsonrpc/`)
- ✅ Unit tests for Capability system (`tests/unit/test_capability/`)
- ✅ Unit tests for Utils (`tests/unit/test_utils/`)
- ✅ Integration tests for client-server interaction (`tests/integration/test_clients/`)
- ✅ E2E tests for LSP workflows (`tests/e2e/`)

All tests follow the project's code style guidelines and pass lint checks.
