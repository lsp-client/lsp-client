# Language Server Clients

## Overview
Implementation of language-specific LSP clients using capability mixins and dual-server backends.

## Adding New Language Server

1. **Inherit Base**: Subclass `<Lang>ClientBase` from `base.py` (e.g., `PythonClientBase`).
2. **Add Mixins**: Inherit from `WithRequest*` and `WithNotify*` protocols for desired features.
3. **Define Servers**: Implement `create_default_servers()` returning `DefaultServers(local=..., container=...)`.
4. **Set Config**: Implement `create_default_config()` with optimized server settings.
5. **Register**: Add the new client to `lang_clients` in `lang.py` for project-root discovery.

## Client Pattern

- **Base Classes**: `PythonClientBase`, `RustClientBase`, etc., define language suffixes and project root markers.
- **Dual Servers**: Every client provides a `LocalServer` (subprocess) and `ContainerServer` (Docker).
- **Local Fallback**: `LocalServer` can define an `ensure_installed` hook to auto-install missing binaries.
- **Container First**: `ContainerServer` uses pre-built images from `ghcr.io/lsp-client/*` with auto-path translation.
- **Compatibility**: `check_server_compatibility()` allows version-specific gating or warnings.

## WHERE TO LOOK
| Task | File | Notes |
|------|------|-------|
| Language Bases | `base.py` | Suffixes, project root markers |
| Discovery Logic | `lang.py` | `find_client()`, `lang_clients` registry |
| Python (Pyright) | `pyright.py` | Reference implementation for Python |
| Rust (RA) | `rust_analyzer.py` | Reference implementation for Rust |
| TypeScript | `typescript.py` | Reference implementation for TS/JS |
| Go (Gopls) | `gopls.py` | Reference implementation for Go |
