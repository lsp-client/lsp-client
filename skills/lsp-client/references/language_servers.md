# Supported Language Servers

## Python Language Servers

### Pyright
- **Module**: `lsp_client.clients.pyright.PyrightClient`
- **Container**: `ghcr.io/lsp-client/pyright:latest`
- **Local**: `pyright-langserver --stdio`
- **Best for**: Type checking, IntelliSense, modern Python features
- **Homepage**: https://microsoft.github.io/pyright/

### Basedpyright
- **Module**: `lsp_client.clients.basedpyright.BasedpyrightClient`
- **Container**: `ghcr.io/lsp-client/basedpyright:latest`
- **Local**: `basedpyright-langserver --stdio`
- **Best for**: Enhanced Pyright fork with additional features

### Pyrefly
- **Module**: `lsp_client.clients.pyrefly.PyreflyClient`
- **Container**: `ghcr.io/lsp-client/pyrefly:latest`
- **Local**: `pyrefly --stdio`
- **Best for**: Fast, lightweight Python analysis

### Ty
- **Module**: `lsp_client.clients.ty.TyClient`
- **Container**: `ghcr.io/lsp-client/ty:latest`
- **Local**: `ty lsp`
- **Best for**: Type-focused Python analysis

## Rust
### Rust Analyzer
- **Module**: `lsp_client.clients.rust_analyzer.RustAnalyzerClient`
- **Container**: `ghcr.io/lsp-client/rust-analyzer:latest`
- **Local**: `rust-analyzer`
- **Best for**: Rust development
- **Homepage**: https://rust-analyzer.github.io/

## TypeScript/JavaScript

### Deno
- **Module**: `lsp_client.clients.deno.DenoClient`
- **Container**: `ghcr.io/lsp-client/deno:latest`
- **Local**: `deno lsp`
- **Best for**: Deno projects, modern TS/JS with built-in tooling

### TypeScript Language Server
- **Module**: `lsp_client.clients.typescript.TypescriptClient`
- **Container**: `ghcr.io/lsp-client/typescript:latest`
- **Local**: `typescript-language-server --stdio`
- **Best for**: Traditional Node.js/TypeScript projects

## Go
### Gopls
- **Module**: `lsp_client.clients.gopls.GoplsClient`
- **Container**: `ghcr.io/lsp-client/gopls:latest`
- **Local**: `gopls`
- **Best for**: Go development
- **Homepage**: https://github.com/golang/tools/tree/master/gopls

## Java
### JDTLS (Eclipse JDT Language Server)
- **Module**: `lsp_client.clients.jdtls.JdtlsClient`
- **Note**: No pre-built container image yet
- **Best for**: Java development

## Quick Selection Guide

| Language | Recommended Client | Why |
|----------|-------------------|-----|
| Python (type-focused) | Pyright | Best type checking, most complete |
| Python (lightweight) | Pyrefly | Fastest startup, minimal overhead |
| Rust | Rust Analyzer | Official, feature-complete |
| TypeScript/Node | TypeScript LS | Industry standard |
| Deno projects | Deno | Integrated tooling |
| Go | Gopls | Official Go team |
| Java | JDTLS | Most complete Java support |
