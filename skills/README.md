# LSP Client Skills

This directory contains packaged skills for the lsp-client library.

## Available Skills

### lsp-client.skill

Semantic code analysis via LSP. Navigate code (definitions, references, implementations), search symbols, preview refactorings, and get file outlines.

**Use for**:
- Exploring unfamiliar codebases
- Performing safe refactoring
- Symbol search and navigation
- Building custom LSP-powered tools

**Contains**:
- 4 ready-to-use Python scripts for common LSP operations
- Complete capability reference
- Language server selection guide
- Custom client creation template

## Using Skills

Skills are zip archives with a `.skill` extension. They can be:
1. Loaded into AI agents for enhanced capabilities
2. Extracted to access scripts and templates directly
3. Used as reference documentation for the library

## Extracting Skill Contents

```bash
# Extract skill contents
unzip lsp-client.skill -d lsp-client-extracted/

# Or just rename and unzip
cp lsp-client.skill lsp-client.zip
unzip lsp-client.zip
```

## Skill Structure

```
lsp-client/
├── SKILL.md                    # Main skill documentation
├── scripts/                    # Executable Python scripts
│   ├── basic_analysis.py
│   ├── find_all_symbols.py
│   ├── safe_rename.py
│   └── custom_client_template.py
└── references/                 # Reference documentation
    ├── capabilities.md
    └── language_servers.md
```
