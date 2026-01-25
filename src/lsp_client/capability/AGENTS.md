# Capability System

## Overview

A mixin-based system for composing LSP client features. It enables type-safe capability negotiation and automatic registration via Protocol introspection.

## Architecture

### Protocol Pattern

Capabilities are defined as `@runtime_checkable` Protocols. Each capability mixin (e.g., `WithRequestHover`) implements a specific LSP feature and provides a registration method (e.g., `register_text_document_capability`).

### build.py Registration

The `build_client_capabilities` function uses `issubclass(cls, Protocol)` to introspect the client class. If a client inherits from a capability Protocol, its registration method is called to populate the `ClientCapabilities` object sent during initialization.

## Subdirectories

| Directory              | Purpose                                                   |
| ---------------------- | --------------------------------------------------------- |
| `request/`             | Client-to-server requests (e.g., hover, definition)       |
| `notification/`        | Client-to-server notifications (e.g., didOpen, didChange) |
| `server_request/`      | Server-to-client requests (e.g., workspace/configuration) |
| `server_notification/` | Server-to-client notifications (e.g., publishDiagnostics) |
| `diagnostic/`          | Specialized pull-based diagnostic capabilities            |

## WHERE TO LOOK

| Task                | File                          | Notes                                                     |
| ------------------- | ----------------------------- | --------------------------------------------------------- |
| Add new capability  | `request/` or `notification/` | Follow subdirectory AGENTS.md patterns                    |
| Modify registration | `build.py`                    | Update `build_client_capabilities` for new Protocol types |
| Core protocols      | `src/lsp_client/protocol/`    | Base capability protocols and registries                  |
