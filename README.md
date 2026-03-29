# Vault MCP Server

A Model Context Protocol (MCP) server for interacting with the UniHub Vault - a file-based issue tracking and knowledge management system.

## Quick Start

### Prerequisites

- Python 3.12+
- [`uv`](https://docs.astral.sh/uv/) package manager

### Installation

```bash
uv sync
```

### Running the Server

```bash
uv run python main.py
```

### Configuration

Set the `VAULT_PATH` environment variable to point to your UniHub Vault directory:

```bash
export VAULT_PATH=/path/to/your/vault
```

**Default locations** (checked automatically if `VAULT_PATH` not set):
- `./.unihub-vault/UniHubVault` (relative to project root)
- `~/Q/massage.kg/.unihub-vault/UniHubVault`

---

## MCP Client Configuration

### Claude Desktop

Add to your Claude Desktop config (`~/Library/Application Support/Claude/claude_desktop_config.json` on macOS, or `%APPDATA%\Claude\claude_desktop_config.json` on Windows):

```json
{
  "mcpServers": {
    "vault": {
      "command": "uv",
      "args": ["run", "python", "/absolute/path/to/vault-mcp-server/main.py"],
      "env": {
        "VAULT_PATH": "/home/lexx/Q/massage.kg/.unihub-vault/UniHubVault"
      }
    }
  }
}
```

### Cursor IDE

Add to `.cursor/mcp.json` in your workspace:

```json
{
  "mcpServers": {
    "vault": {
      "command": "uv",
      "args": ["run", "python", "${workspaceFolder}/main.py"],
      "env": {
        "VAULT_PATH": "/home/lexx/Q/massage.kg/.unihub-vault/UniHubVault"
      }
    }
  }
}
```

### Windsurf / Codeium

Add to your MCP settings:

```json
{
  "vault": {
    "command": "uv",
    "args": ["run", "python", "/absolute/path/to/vault-mcp-server/main.py"],
    "env": {
      "VAULT_PATH": "/path/to/vault"
    }
  }
}
```

### Generic MCP Client

```json
{
  "vault": {
    "command": "python",
    "args": ["/absolute/path/to/vault-mcp-server/main.py"],
    "env": {
      "VAULT_PATH": "/path/to/vault"
    }
  }
}
```

---

## Available Tools

### Issue Management (5 tools)

| Tool | Description |
|------|-------------|
| `create_issue(name, body, tags?)` | Create issue in `10_Inbox`, returns 8-char ID |
| `read_issue(iss_uniq_id)` | Read issue content by unique ID |
| `update_issue(iss_uniq_id, content, append?)` | Update or append to issue |
| `move_issue(iss_uniq_id, stage)` | Move issue to stage (`10_Inbox`, `20_Processing`, `30_ToReview`, `999_Finished`) |
| `list_issues(stage?)` | List issues in stage (default: `10_Inbox`) |

### Vault Operations (3 tools)

| Tool | Description |
|------|-------------|
| `read_note(path)` | Read any note from vault (path relative to vault root) |
| `list_notes(directory?)` | List markdown files in directory |
| `search_vault(query)` | Search all `.md` files (auto-detects regex vs keyword) |

### Status (1 tool)

| Tool | Description |
|------|-------------|
| `get_status()` | Dashboard: issues by stage + recently modified notes |

### Telegram (3 tools)

| Tool | Description |
|------|-------------|
| `set_telegram_webhook(url)` | Set bot webhook URL |
| `check_telegram_webhook()` | Check webhook status |
| `poll_telegram_updates()` | Poll and forward updates to local webhook |

---

## Issue Lifecycle

```
10_Inbox → 20_Processing → 30_ToReview → 999_Finished
   ↑            ↑              ↑
 create      move           move
```

### Typical Workflow

```
1. create_issue("Bug in login", "Users can't login with SSO", ["bug", "auth"])
   → Returns: "a1b2c3d4"

2. list_issues("10_Inbox")
   → Shows new issue in inbox

3. read_issue("a1b2c3d4")
   → Returns full issue content

4. move_issue("a1b2c3d4", "20_Processing")
   → Moves to processing stage

5. update_issue("a1b2c3d4", "\n## Investigation\nChecked logs...", append=True)
   → Appends investigation notes

6. move_issue("a1b2c3d4", "30_ToReview")
   → Moves to review when done

7. get_status()
   → Shows overview of all stages
```

### Stage Names

Both full and short names are supported:

| Short | Full |
|-------|------|
| `inbox` | `10_Inbox` |
| `processing` | `20_Processing` |
| `review` | `30_ToReview` |
| `finished` | `999_Finished` |

---

## Tool Examples

### Create and Track an Issue

```
create_issue(name="Add dark mode", body="Users requested dark theme", tags=["feature", "ui"])
→ "f5e4d3c2"

read_issue("f5e4d3c2")
→ Full issue content

update_issue("f5e4d3c2", "\n## Notes\nPriority: high", append=True)
→ "Successfully appended to issue f5e4d3c2"

move_issue("f5e4d3c2", "processing")
→ "Moved issue f5e4d3c2 to 20_Processing"
```

### Search and Read Notes

```
search_vault("authentication")
→ 50_Protocols/Auth.md:5: ## Authentication Flow
  20_Processing/<~15-nov~> abc123_login.md:12: User authentication fails...

read_note("50_Protocols/Auth.md")
→ Full protocol content

list_notes("50_Protocols")
→ Auth.md
   Security.md
   ...
```

### Get Status Overview

```
get_status()
→ ## Vault Status Overview

   ### Issues by Stage

   **10_Inbox**: 3 issue(s)
     - <~15-nov~> abc123_login.md
     - <~16-nov~> def456_search.md
     - <~17-nov~> ghi789_ui.md

   **20_Processing**: 1 issue(s)
     - <~10-nov~> f5e4d3c2_dark_mode.md

   **30_ToReview**: 0 issue(s)

   **999_Finished**: 12 issue(s)
     ...

   ### Recently Modified Notes

     - 20_Processing/<~10-nov~> f5e4d3c2_dark_mode.md (0d ago, 2025-03-29)
     - 50_Protocols/Auth.md (2d ago, 2025-03-27)
```

---

## Running Tests

```bash
uv run python test_issue_tools.py
```

This runs an integration test covering the full issue lifecycle.

---

## Architecture

- **FastMCP** server framework for MCP protocol handling
- **File-based storage** using markdown files in stage directories
- **Path safety** validation to prevent directory traversal
- **Telegram integration** via bot token from `backend/.env`
