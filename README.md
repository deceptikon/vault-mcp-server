# Vault MCP Server

A Model Context Protocol (MCP) server for interacting with the UniHub Vault.

## Core Issue Lifecycle Tools

### `create_issue`
Create a new issue in the `10_Inbox` directory.
- **Parameters**:
  - `name`: Short descriptive name for the issue.
  - `body`: Detailed description of the issue.
  - `tags`: Optional list of tags.
- **Returns**: `iss_uniq_id` (8-character unique ID).

### `start_issue`
Start an issue by moving it to `20_Processing`.
- **Parameters**: `iss_uniq_id` (the 8-character unique ID).
- **Returns**: Issue content and confirmation.

### `finish_issue`
Finish an issue by updating timestamps/tags and moving it to `30_ToReview`.
- **Parameters**: `iss_uniq_id` (the 8-character unique ID).

## Other Tools

### `read_issue`
Read an issue's content by its unique ID.
- **Parameters**: `iss_uniq_id`

### `update_issue`
Update or append content to an issue by its unique ID.
- **Parameters**:
  - `iss_uniq_id`: The 8-character unique ID.
  - `content`: New content.
  - `append`: (Boolean) If true, appends to the end of the file.

### `move_issue`
Move an issue to any valid stage directory.
- **Parameters**:
  - `iss_uniq_id`: The 8-character unique ID.
  - `target_stage`: One of `10_Inbox`, `20_Processing`, `30_ToReview`, `999_Finished`.

### `read_note`
Read any note from the vault.
- **Parameters**: `path` (relative to vault root, e.g., `40_Entities/Project.md`)

### `get_protocol`
Get a protocol content from the `50_Protocols/` directory.
- **Parameters**: `name` (protocol name)

### `search_vault`
Search through all `.md` files in the vault.
- **Parameters**:
  - `query`: Search term or regex.
  - `search_type`: `keyword` or `regex`.

### `list_notes`
List all markdown files in a specific directory.
- **Parameters**: `directory` (relative to vault root)

### `list_stage_issues`
List all issues in a specific stage directory (`10_Inbox`, etc.).
- **Parameters**: `stage`

## Configuration

Set the `VAULT_PATH` environment variable to point to your UniHub Vault directory.
Default: `/home/lexx/Q/massage.kg/.unihub-vault/UniHubVault`
