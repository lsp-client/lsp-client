# Available LSP Capabilities

## Request Capabilities

Located in `lsp_client.capability.request`:

### Navigation
- `WithRequestDefinition` - Go to definition (`textDocument/definition`)
- `WithRequestDeclaration` - Go to declaration (`textDocument/declaration`)
- `WithRequestTypeDefinition` - Go to type definition (`textDocument/typeDefinition`)
- `WithRequestImplementation` - Find implementations (`textDocument/implementation`)
- `WithRequestReferences` - Find all references (`textDocument/references`)

### Code Intelligence
- `WithRequestHover` - Show hover information (`textDocument/hover`)
- `WithRequestCompletion` - Code completion (`textDocument/completion`)
- `WithRequestSignatureHelp` - Signature help (`textDocument/signatureHelp`)
- `WithRequestInlayHint` - Inlay hints (`textDocument/inlayHint`)

### Symbols
- `WithRequestDocumentSymbol` - Symbols in document (`textDocument/documentSymbol`)
- `WithRequestWorkspaceSymbol` - Search workspace symbols (`workspace/symbol`)

### Refactoring
- `WithRequestRename` - Rename symbol (`textDocument/rename`)
- `WithRequestCodeAction` - Code actions/quick fixes (`textDocument/codeAction`)
- `WithRequestWorkspaceEdit` - Apply workspace edits

### File Operations
- `WithRequestWillCreateFiles` - Pre-create file hook (`workspace/willCreateFiles`)
- `WithRequestWillDeleteFiles` - Pre-delete file hook (`workspace/willDeleteFiles`)
- `WithRequestWillRenameFiles` - Pre-rename file hook (`workspace/willRenameFiles`)

### Hierarchy
- `WithRequestCallHierarchy` - Call hierarchy (`textDocument/prepareCallHierarchy`, `callHierarchy/incomingCalls`, `callHierarchy/outgoingCalls`)
- `WithRequestTypeHierarchy` - Type hierarchy (`textDocument/prepareTypeHierarchy`, `typeHierarchy/supertypes`, `typeHierarchy/subtypes`)

### Other
- `WithRequestExecuteCommand` - Execute custom commands (`workspace/executeCommand`)
- `WithRequestInlineValue` - Inline values for debugging (`textDocument/inlineValue`)

## Notification Capabilities

Located in `lsp_client.capability.notification`:

- `WithNotifyDidChangeConfiguration` - Notify config changes (`workspace/didChangeConfiguration`)
- `WithNotifyDidCreateFiles` - Notify file creation (`workspace/didCreateFiles`)
- `WithNotifyDidDeleteFiles` - Notify file deletion (`workspace/didDeleteFiles`)
- `WithNotifyDidRenameFiles` - Notify file rename (`workspace/didRenameFiles`)
- `WithNotifyDidChangeWorkspaceFolders` - Notify workspace folder changes (`workspace/didChangeWorkspaceFolders`)

## Server Notification Capabilities

Located in `lsp_client.capability.server_notification` (server → client):

- `WithReceivePublishDiagnostics` - Receive diagnostics (`textDocument/publishDiagnostics`)
- `WithReceiveLogMessage` - Receive log messages (`window/logMessage`)
- `WithReceiveShowMessage` - Receive show message (`window/showMessage`)
- `WithReceiveLogTrace` - Receive trace logs (`$/logTrace`)

## Server Request Capabilities

Located in `lsp_client.capability.server_request` (server → client):

- `WithRespondConfigurationRequest` - Respond to config requests (`workspace/configuration`)
- `WithRespondWorkspaceFoldersRequest` - Respond to workspace folders (`workspace/workspaceFolders`)
- `WithRespondShowMessageRequest` - Respond to message requests (`window/showMessageRequest`)
- `WithRespondShowDocumentRequest` - Respond to show document (`window/showDocument`)
- `WithRespondInlayHintRefresh` - Respond to inlay hint refresh (`workspace/inlayHint/refresh`)

## Commonly Used Combinations

### Basic Python Analysis Client
```python
WithRequestHover
WithRequestDefinition
WithRequestReferences
WithNotifyDidChangeConfiguration
```

### Full-Featured IDE Client
```python
WithRequestHover
WithRequestDefinition
WithRequestReferences
WithRequestCompletion
WithRequestSignatureHelp
WithRequestDocumentSymbol
WithRequestWorkspaceSymbol
WithRequestRename
WithRequestCodeAction
WithReceivePublishDiagnostics
WithNotifyDidChangeConfiguration
```

### Refactoring-Focused Client
```python
WithRequestDefinition
WithRequestReferences
WithRequestRename
WithRequestCodeAction
WithRequestWillRenameFiles
WithNotifyDidRenameFiles
```
