# Test Fixtures Setup

## Problem

The test framework previously relied on manual symbolic links to `references/pyrefly` which caused issues in CI environments where these symlinks were not available.

## Solution

We implemented a multi-layered approach:

### 1. Automated Setup Script

The `scripts/setup_fixtures.sh` script:
- Clones the pyrefly repository to `references/pyrefly` if not present
- Creates necessary symbolic links to test fixtures
- Is idempotent and safe to run multiple times

### 2. CI Integration

The GitHub Actions CI workflow automatically runs the setup script before tests, ensuring fixtures are always available in CI.

### 3. Graceful Degradation

Tests requiring pyrefly fixtures are marked with `@pytest.mark.requires_fixtures`. If fixtures are unavailable:
- Tests are automatically skipped (not failed)
- Unit and integration tests continue to run normally
- Clear skip message indicates the reason

## Usage

### Local Development

Setup fixtures once:
```bash
bash scripts/setup_fixtures.sh
```

### Running Tests

```bash
# Run all tests (skips fixture-dependent tests if fixtures unavailable)
uv run pytest

# Run only tests that don't require fixtures
uv run pytest -m "not requires_fixtures"

# Run only unit tests
uv run pytest tests/unit/
```

## Implementation Details

### Fixture Availability Check

In `tests/conftest.py`:
- `pytest_runtest_setup` hook checks for fixture availability before running marked tests
- Skips tests with clear message if fixtures are missing
- No impact on tests that don't require fixtures

### Marked Tests

Tests in the following files are marked with `@pytest.mark.requires_fixtures`:
- `tests/e2e/test_pyrefly_conformance.py`
- `tests/e2e/test_pyrefly_lsp.py`

### CI Setup

The CI workflow includes a "Setup test fixtures" step that runs before all tests, ensuring full test coverage in CI while maintaining local flexibility.

## Benefits

1. **CI Compatibility**: Tests run successfully in CI without manual setup
2. **Local Flexibility**: Developers can run tests without fixtures if needed
3. **Clear Communication**: Skip messages clearly indicate why tests were skipped
4. **No Breaking Changes**: Existing test behavior is preserved when fixtures are available
5. **Maintainable**: Single source of truth for fixture setup logic
