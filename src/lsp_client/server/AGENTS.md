# Server Backends

## Overview

Server backends manage the lifecycle and communication transport (JSON-RPC over streams) for language servers.

## Server Types

### LocalServer

Runs the language server as a local subprocess.

- **Lifecycle**: Manages process creation, termination, and graceful shutdown.
- **Auto-install**: Supports `ensure_installed` callbacks to install missing servers.
- **Transport**: Communicates via `stdin`/`stdout` pipes.

### ContainerServer

Runs the language server inside an OCI-compliant container (Docker, Podman, nerdctl).

- **Isolation**: Provides environment consistency and security.
- **Path Translation**: Automatically mounts workspace folders and translates host paths to container paths.
- **Backend**: Defaults to `docker`, configurable via `backend` attribute.
- **Gated**: Requires `LSP_CLIENT_ENABLE_CONTAINER=1` environment variable.

## Implementation Guide

### Custom Server Types

To implement a custom backend, inherit from `StreamServer` or the base `Server` class:

1. Implement `manage_resources` async context manager for lifecycle.
2. Provide `send_stream` and `receive_stream` for data transport.
3. Override `check_availability` for pre-flight checks.

### Server Lifecycle Hooks

`StreamServer` provides hooks for fine-grained control:

- `setup()`: Pre-startup initialization.
- `on_started()`: Post-startup, before dispatch loop.
- `on_shutdown()`: Graceful shutdown logic.

## WHERE TO LOOK

| Task              | File           | Notes                                   |
| ----------------- | -------------- | --------------------------------------- |
| Base interfaces   | `abc.py`       | `Server` and `StreamServer` definitions |
| Subprocess logic  | `local.py`     | `LocalServer` implementation            |
| Container logic   | `container.py` | `ContainerServer` and mount handling    |
| Error types       | `error.py`     | `ServerRuntimeError` and variants       |
| Socket transport  | `socket.py`    | TCP/Unix socket server implementation   |
| Default selection | `default.py`   | Logic for picking local vs container    |
