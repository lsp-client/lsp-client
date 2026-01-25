# Server Request Capabilities

## Overview
Handles requests initiated by the language server that require a response from the client (e.g., configuration retrieval or edit application).

## Pattern
- **Mixin**: Uses `WithRespond*` Protocols (e.g., `WithRespondApplyEdit`).
- **Hook Registry**: Handlers are registered via `register_server_request_hooks` into the `ServerRequestHookRegistry`.
- **Execution**: The core client routes incoming JSON-RPC requests to the registered `ServerRequestHook.execute` method.

## WHERE TO LOOK
| Task | File | Notes |
| --- | --- | --- |
| Workspace Config | `configuration.py` | Handles `workspace/configuration` |
| Apply Edits | `apply_edit.py` | Handles `workspace/applyEdit` |
| Dynamic Reg | `register_capability.py` | Handles `client/registerCapability` |
| UI Requests | `show_message_request.py` | Handles `window/showMessageRequest` |
| Document Ops | `show_document_request.py` | Handles `window/showDocument` |
| Folder Sync | `workspace_folders.py` | Handles `workspace/workspaceFolders` |
| Refresh Hints | `inlay_hint_refresh.py` | Handles `workspace/inlayHint/refresh` |
