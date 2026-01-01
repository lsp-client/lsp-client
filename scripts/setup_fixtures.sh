#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$SCRIPT_DIR"
REFERENCES_DIR="$PROJECT_ROOT/references"
FIXTURES_DIR="$PROJECT_ROOT/tests/fixtures"

echo "Setting up pyrefly test fixtures..."

if [ ! -d "$REFERENCES_DIR/pyrefly" ]; then
    echo "Cloning pyrefly repository..."
    mkdir -p "$REFERENCES_DIR"
    git clone --depth 1 https://github.com/facebook/pyrefly "$REFERENCES_DIR/pyrefly"
else
    echo "Pyrefly repository already exists at $REFERENCES_DIR/pyrefly"
fi

echo "Creating symbolic links for test fixtures..."
mkdir -p "$FIXTURES_DIR"

if [ ! -e "$FIXTURES_DIR/pyrefly" ]; then
    ln -sf "$REFERENCES_DIR/pyrefly/conformance/third_party" "$FIXTURES_DIR/pyrefly"
    echo "Created symlink: $FIXTURES_DIR/pyrefly -> $REFERENCES_DIR/pyrefly/conformance/third_party"
else
    echo "Fixture symlink already exists: $FIXTURES_DIR/pyrefly"
fi

if [ ! -e "$FIXTURES_DIR/pyrefly_lsp" ]; then
    ln -sf "$REFERENCES_DIR/pyrefly/pyrefly/lib/test/lsp/lsp_interaction/test_files" "$FIXTURES_DIR/pyrefly_lsp"
    echo "Created symlink: $FIXTURES_DIR/pyrefly_lsp -> $REFERENCES_DIR/pyrefly/pyrefly/lib/test/lsp/lsp_interaction/test_files"
else
    echo "Fixture symlink already exists: $FIXTURES_DIR/pyrefly_lsp"
fi

echo "✓ Pyrefly test fixtures setup complete!"
