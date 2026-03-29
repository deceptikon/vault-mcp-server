# Vault MCP Server - Project Context

## Project Overview

A **Model Context Protocol (MCP) server** for interacting with the UniHub Vault - a file-based issue tracking and knowledge management system. The server exposes tools via the MCP protocol to manage issues through a lifecycle workflow and perform vault operations like searching, reading notes, and getting status overviews.

**Key Technologies:**
- Python 3.12+
- [FastMCP](https://github.com/modelcontextprotocol/python-sdk) - MCP server framework
- `requests` - HTTP client for Telegram API integration
- `uv` - Python package manager

## Project Structure

```
vault-mcp-server/
├── main.py              # MCP server implementation with all tools
├── test_issue_tools.py  # Integration tests for issue workflow
├── pyproject.toml       # Project configuration & dependencies
├── uv.lock              # Dependency lock file
├── .python-version      # Python version (3.12)
└── README.md            # Full documentation with MCP client configs
```

## Building and Running

### Prerequisites
- Python 3.12+ (managed via `.python-version`)
- `uv` package manager

### Installation & Running

```bash
# Install dependencies
uv sync

# Run the MCP server
uv run python main.py
```

### Environment Configuration

Set the `VAULT_PATH` environment variable to point to your UniHub Vault directory:

```bash
export VAULT_PATH=/path/to/your/vault
```

**Default locations** (checked automatically if `VAULT_PATH` not set):
- `./.unihub-vault/UniHubVault` (relative to project root)
- `~/Q/massage.kg/.unihub-vault/UniHubVault`

### Running Tests

```bash
uv run python test_issue_tools.py
```

This runs integration tests covering: create → read → update → move → search → status operations.

## Available MCP Tools (11 total)

### Issue Management (5 tools)

| Tool | Description |
|------|-------------|
| `create_issue(name, body, tags?)` | Create issue in `10_Inbox`, returns 8-char ID |
| `read_issue(iss_uniq_id)` | Read issue content by unique ID |
| `update_issue(iss_uniq_id, content, append?)` | Update or append to issue |
| `move_issue(iss_uniq_id, stage)` | Move to stage (supports short names: inbox, processing, review, finished) |
| `list_issues(stage?)` | List issues in stage (default: `10_Inbox`) |

### Vault Operations (3 tools)

| Tool | Description |
|------|-------------|
| `read_note(path)` | Read any note from vault |
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

## Issue Lifecycle

```
10_Inbox → 20_Processing → 30_ToReview → 999_Finished
   ↑            ↑              ↑
 create      move           move
```

- **Issues** are markdown files named: `<~DD-MMM~> ISSUNIQID_name.md`
- **Unique IDs** are 8-character UUIDs generated on creation
- Issues use a template from `888_System/Templates/New Issue Template.md`
- **Stage names**: Both full (`10_Inbox`) and short (`inbox`) names are supported

## Development Conventions

- **Tool naming**: Snake_case, descriptive verbs (`create_`, `read_`, `update_`, `move_`, `list_`)
- **Error handling**: Tools return `"Error: <message>"` strings on failure
- **Path safety**: `_is_safe_path()` prevents directory traversal attacks
- **Internal helpers**: Prefixed with `_` (e.g., `_find_issue_path`, `_get_bot_token`)
- **Search auto-detection**: `search_vault` detects regex by metacharacters (`.*+?^${}()|[]\`)

## Telegram Configuration

Bot token is read from `backend/.env` file:
```
TELEGRAM_BOT_TOKEN=<your_token>
```

The local webhook endpoint is: `http://localhost:8000/api/v1/telegram/webhook/`

## MCP Client Configuration

See `README.md` for complete configuration examples for:
- Claude Desktop
- Cursor IDE
- Windsurf / Codeium
- Generic MCP clients

Example (Claude Desktop):
```json
{
  "mcpServers": {
    "vault": {
      "command": "uv",
      "args": ["run", "python", "/path/to/vault-mcp-server/main.py"],
      "env": {
        "VAULT_PATH": "/home/lexx/Q/massage.kg/.unihub-vault/UniHubVault"
      }
    }
  }
}
```
