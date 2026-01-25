# Request Capabilities

## Overview

Request capabilities implement the client-to-server request-response pattern for LSP features like hover, definition, and references.

## WHERE TO LOOK

| Task                | File                                          | Notes                            |
| ------------------- | --------------------------------------------- | -------------------------------- |
| Add new request     | `src/lsp_client/capability/request/<name>.py` | Follow `WithRequest*` pattern    |
| Register capability | `src/lsp_client/capability/build.py`          | Automatic via `issubclass` check |
| LSP Types           | `lsp_client.utils.types.lsp_type`             | Re-exports from `lsprotocol`     |

## Pattern

Each request capability is a `@runtime_checkable` Protocol named `WithRequest<Name>`.

1. **Inheritance**: Inherit from `TextDocumentCapabilityProtocol` and `CapabilityClientProtocol`.
2. **`iter_methods()`**: Yield the LSP method string (e.g., `textDocument/hover`).
3. **`register_text_document_capability()`**: Configure `TextDocumentClientCapabilities` sent to server.
4. **`check_server_capability()`**: Assert server support in `ServerCapabilities`.
5. **Private `_request_<name>()`**: Low-level JSON-RPC request using `self.request()`.
6. **Public `request_<name>()`**: High-level API with ergonomic types and `open_files` context.

## Adding New Request

1. Create `<name>.py` in this directory.
2. Define `WithRequest<Name>` protocol following the pattern above.
3. Use `lsp_type` for all LSP structures and method names.
4. Implement ergonomic public method (e.g., handling `Location` vs `LocationLink`).
5. Ensure `self.open_files(file_path)` is used for document-synchronized requests.
6. Add unit tests in `tests/unit/capability/request/`.
