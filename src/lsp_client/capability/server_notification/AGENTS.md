# Server Notification Capabilities

## Overview
Server-to-client notifications are fire-and-forget messages pushed by the server that the client handles passively without returning a response.

## Pattern
- **Mixin**: `WithReceive*` (e.g., `WithReceivePublishDiagnostics`)
- **Hook**: Uses `ServerNotificationHook` registered via `register_server_request_hooks`
- **Execution**: Passive handling in `receive_*` methods, typically logging or updating internal state

## WHERE TO LOOK
| Task | File | Notes |
| --- | --- | --- |
| Diagnostics | `publish_diagnostics.py` | `textDocument/publishDiagnostics` |
| Logging | `log_message.py` | `window/logMessage` |
| UI Messages | `show_message.py` | `window/showMessage` |
| Tracing | `log_trace.py` | `$/logTrace` |
| Registration | `__init__.py` | Exports all server notification mixins |
