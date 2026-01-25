# Notification Capabilities

## Overview
Client-to-server fire-and-forget notifications. No response expected from server.

## Pattern
- Define `@runtime_checkable` Protocol `WithNotify<Name>`
- Inherit from `CapabilityClientProtocol` and relevant base protocols
- Use `self.notify(notification_object)` for transmission
- Implement `iter_methods` and `register_*_capability` for auto-discovery

## WHERE TO LOOK
| Task | File | Notes |
| --- | --- | --- |
| Doc Sync | `text_document_synchronize.py` | didOpen, didChange, didClose |
| Config | `did_change_configuration.py` | workspace/didChangeConfiguration |
| Files | `did_create_files.py` | workspace/didCreateFiles |
| Workspace | `did_change_workspace_folders.py` | workspace/didChangeWorkspaceFolders |
