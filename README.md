# Vault MCP Server

A Model Context Protocol (MCP) server for interacting with the UniHub Vault.

## Tools

### `read_note`
Read a note from the vault.
- **Parameters**: `path` (relative to vault root)

### `get_protocol`
Get a protocol content from the `50_Protocols/` directory.
- **Parameters**: `name` (protocol name)

### `create_task`
Create a new task in the `10_Inbox` directory using the New Issue Template.
- **Parameters**:
  - `name`: Filename (without extension).
  - `category`: Task category (e.g., "feat", "bug").
  - `context`: Description/context to inject into the task.
- **Logic**:
  - Uses `888_System/Templates/New Issue Template.md`.
  - Replaces `{{category}}`, `{{date}}`, `{{time}}`.
  - Injects `context` into the description area.
  - Saves to `10_Inbox/<~DD-mon~> {name}.md`.

### `move_task`
Move a task file between stage directories.
- **Parameters**:
  - `filename`: Full filename (e.g., `<~23-mar~> feat_mcp_vault_integration.md`).
  - `target_stage`: One of `10_Inbox`, `20_Processing`, `30_ToReview`, `999_Finished`.
- **Logic**: Finds the file in its current stage and moves it to the target stage.

## Configuration

Set the `VAULT_PATH` environment variable to point to your UniHub Vault directory.
Default: `/home/lexx/Q/massage.kg/.unihub-vault/UniHubVault`
