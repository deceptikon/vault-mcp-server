# Vault MCP Server

A Model Context Protocol (MCP) server for interacting with the UniHub Vault.

## Core Issue Lifecycle Tools

### `create_issue`
Create a new issue.
- **Parameters**:
  - `name`: Short descriptive name for the issue.
  - `body`: Detailed description of the issue.
  - `tags`: Optional list of tags.
- **Returns**: `iss_uniq_id` (8-character unique ID).

### `list_issues`
List all issues with a specific status.
- **Parameters**:
  - `status`: One of `inbox`, `processing`, `review`, `finished`. Defaults to `inbox`.
- **Returns**: A list of issue filenames.

### `start_issue`
Start an issue by moving it to `processing`.
- **Parameters**: `iss_uniq_id` (the 8-character unique ID).
- **Returns**: Issue content and confirmation.

### `finish_issue`
Finish an issue by updating timestamps/tags and moving it to `review`.
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
Move an issue to any valid status.
- **Parameters**:
  - `iss_uniq_id`: The 8-character unique ID.
  - `status`: One of `inbox`, `processing`, `review`, `finished`.

### `read_note`
Read any note from the vault.
- **Parameters**: `path` (relative to vault root)

### `get_protocol`
Get a protocol content.
- **Parameters**: `name` (protocol name)

### `search_vault`
Search through all `.md` files in the vault.
- **Parameters**:
  - `query`: Search term or regex.
  - `search_type`: `keyword` or `regex`.

### `list_notes`
List all markdown files in a specific directory.
- **Parameters**: `directory` (relative to vault root)

## Configuration

Set the `VAULT_PATH` environment variable to point to your UniHub Vault directory.
Default: `/home/lexx/Q/massage.kg/.unihub-vault/UniHubVault`
