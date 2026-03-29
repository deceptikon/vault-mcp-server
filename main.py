import os
import shutil
import re
import uuid
import json
import requests
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any
from mcp.server.fastmcp import FastMCP

# Initialize FastMCP server
mcp = FastMCP("Vault")

# Get VAULT_PATH from environment variable
PROJECT_ROOT = Path(__file__).resolve().parent.parent
COMMON_VAULT_LOCATIONS = [
    PROJECT_ROOT / ".unihub-vault/UniHubVault",
    Path.home() / "Q/massage.kg/.unihub-vault/UniHubVault",
]

def find_default_vault() -> str:
    for loc in COMMON_VAULT_LOCATIONS:
        if loc.exists():
            return str(loc)
    return "/home/lexx/Q/massage.kg/.unihub-vault/UniHubVault"

DEFAULT_VAULT_PATH = find_default_vault()
VAULT_PATH = os.environ.get("VAULT_PATH", DEFAULT_VAULT_PATH)

# Internal mapping for issue statuses to folder names
STATUS_MAP = {
    "inbox": "10_Inbox",
    "processing": "20_Processing",
    "review": "30_ToReview",
    "finished": "999_Finished"
}

def get_vault_path() -> Path:
    """Returns the resolved Path to the vault root."""
    path = Path(VAULT_PATH).resolve()
    if not path.exists():
        workspace_path = Path.cwd() / ".unihub-vault/UniHubVault"
        if workspace_path.exists():
            return workspace_path.resolve()
    return path

def _is_safe_path(path: Path, root: Path) -> bool:
    """Check if the path is within the root directory."""
    try:
        return os.path.commonpath([str(path.resolve()), str(root.resolve())]) == str(root.resolve())
    except Exception:
        return False

def _find_issue_path(iss_uniq_id: str) -> Optional[Path]:
    """Helper to find an issue's file path by its unique ID."""
    vault_root = get_vault_path()
    for folder in STATUS_MAP.values():
        stage_dir = vault_root / folder
        if not stage_dir.exists(): continue
        for file in stage_dir.glob(f"*{iss_uniq_id}*.md"):
            return file
    return None

def _get_bot_token() -> Optional[str]:
    """Extract bot token from backend/.env"""
    env_path = PROJECT_ROOT / "backend" / ".env"
    if env_path.exists():
        content = env_path.read_text()
        match = re.search(r"TELEGRAM_BOT_TOKEN=([^]+)", content)
        if match: return match.group(1)
    return None

# --- Core Vault Tools ---

@mcp.tool()
def read_note(path: str) -> str:
    """Read a note from the vault."""
    vault_root = get_vault_path()
    full_path = (vault_root / path).resolve()
    if not _is_safe_path(full_path, vault_root):
        return f"Error: Access denied. Path {path} is outside the vault."
    if not full_path.exists(): return f"Error: File not found at {path}"
    try: return full_path.read_text(encoding="utf-8")
    except Exception as e: return f"Error: {str(e)}"

@mcp.tool()
def get_protocol(name: str) -> str:
    """Get a protocol content from the 50_Protocols/ directory."""
    if not name.endswith(".md"):
        filename = f"{name}.md"
    else:
        filename = name
    return read_note(f"50_Protocols/{filename}")

@mcp.tool()
def search_vault(query: str, search_type: str = "keyword") -> str:
    """Search through all .md files in the vault directory."""
    if search_type not in ["keyword", "regex"]:
        return "Error: search_type must be either 'keyword' or 'regex'"
    vault_root = get_vault_path()
    results = []
    try:
        pattern = None
        if search_type == "regex":
            try: pattern = re.compile(query, re.IGNORECASE)
            except re.error as e: return f"Error: Invalid regex pattern: {str(e)}"
        for md_file in vault_root.rglob("*.md"):
            try:
                content = md_file.read_text(encoding="utf-8")
                lines = content.splitlines()
                for i, line in enumerate(lines):
                    match = False
                    if search_type == "keyword":
                        if query.lower() in line.lower(): match = True
                    elif search_type == "regex" and pattern:
                        if pattern.search(line): match = True
                    if match:
                        rel_path = md_file.relative_to(vault_root)
                        results.append(f"{rel_path}:{i+1}: {line.strip()}")
            except (IOError, UnicodeDecodeError): continue
        return "\n".join(results) if results else f"No matches found for {search_type} '{query}'"
    except Exception as e: return f"Error during search: {str(e)}"

@mcp.tool()
def list_notes(directory: str = None) -> str:
    """List all markdown files in the specified directory."""
    vault_root = get_vault_path()
    target_dir = (vault_root / directory).resolve() if directory else vault_root.resolve()
    if not _is_safe_path(target_dir, vault_root):
        return f"Error: Access denied. Path {directory} is outside the vault."
    if not target_dir.exists(): return "Directory not found"
    try:
        notes = [f.name for f in target_dir.glob("*.md") if f.is_file()]
        return "\n".join(sorted(notes)) if notes else "No markdown files found."
    except Exception as e: return f"Error: {str(e)}"

@mcp.tool()
def list_stage_issues(stage: str) -> str:
    """List all issues in a specific stage directory (e.g., '10_Inbox')."""
    valid_stages = list(STATUS_MAP.values())
    if stage not in valid_stages: return f"Error: Invalid stage. Must be one of {valid_stages}"
    return list_notes(stage)

@mcp.tool()
def create_issue(name: str, body: str, tags: List[str] = None) -> str:
    """Create a new issue in the 10_Inbox directory."""
    vault_root = get_vault_path()
    template_path = vault_root / "888_System/Templates/New Issue Template.md"
    if not template_path.exists(): return f"Error: Template not found at {template_path}"
    try:
        template_content = template_path.read_text(encoding="utf-8")
        now = datetime.now()
        iss_uniq_id = str(uuid.uuid4())[:8]
        category = ", ".join(tags) if tags else "issue"
        content = template_content.replace("{{category}}", category)
        content = content.replace("{{date}}", now.strftime("%Y-%m-%d"))
        content = content.replace("{{time}}", now.strftime("%H:%M"))
        desc_placeholder = "- [Provide a brief overview of the issue]"
        if desc_placeholder in content:
            content = content.replace(desc_placeholder, f"- {body}")
        else:
            content += f"\n\n### Context\n{body}"
        content = f"ID: {iss_uniq_id}\n" + content
        filename = f"<~{now.strftime('%d-%b').lower()}~> {iss_uniq_id}_{name}.md"
        target_path = vault_root / "10_Inbox" / filename
        target_path.parent.mkdir(parents=True, exist_ok=True)
        target_path.write_text(content, encoding="utf-8")
        return iss_uniq_id
    except Exception as e: return f"Error: {str(e)}"

@mcp.tool()
def read_issue(iss_uniq_id: str) -> str:
    """Read an issue's content by its unique ID."""
    issue_path = _find_issue_path(iss_uniq_id)
    if not issue_path: return f"Error: Issue {iss_uniq_id} not found."
    try: return issue_path.read_text(encoding="utf-8")
    except Exception as e: return f"Error: {str(e)}"

@mcp.tool()
def update_issue(iss_uniq_id: str, content: str, append: bool = False) -> str:
    """Update an issue's content by its unique ID."""
    issue_path = _find_issue_path(iss_uniq_id)
    if not issue_path: return f"Error: Issue {iss_uniq_id} not found."
    try:
        if append:
            existing = issue_path.read_text(encoding="utf-8")
            new_content = (existing + "\n" if existing and not existing.endswith("\n") else existing) + content
        else:
            new_content = content
        issue_path.write_text(new_content, encoding="utf-8")
        return f"Successfully {{'appended to' if append else 'updated'}} issue {iss_uniq_id}"
    except Exception as e: return f"Error: {str(e)}"

@mcp.tool()
def move_issue(iss_uniq_id: str, target_stage: str) -> str:
    """Move an issue to a different stage (e.g., '20_Processing')."""
    valid_stages = list(STATUS_MAP.values())
    if target_stage not in valid_stages: return f"Error: Invalid stage {target_stage}"
    issue_path = _find_issue_path(iss_uniq_id)
    if not issue_path: return f"Error: Issue {iss_uniq_id} not found."
    vault_root = get_vault_path()
    target_path = vault_root / target_stage / issue_path.name
    target_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        if issue_path != target_path:
            shutil.move(str(issue_path), str(target_path))
        return f"Moved issue {iss_uniq_id} to {target_stage}"
    except Exception as e: return f"Error: {str(e)}"

@mcp.tool()
def start_issue(iss_uniq_id: str) -> str:
    """Start an issue by moving it to 20_Processing."""
    res = move_issue(iss_uniq_id, "20_Processing")
    if res.startswith("Error"):
        return res
    return f"Issue {iss_uniq_id} started.\n\nDetails:\n{read_issue(iss_uniq_id)}"

@mcp.tool()
def finish_issue(iss_uniq_id: str) -> str:
    """Finish an issue by moving it to 30_ToReview."""
    issue_path = _find_issue_path(iss_uniq_id)
    if not issue_path: return f"Error: Issue {iss_uniq_id} not found."
    try:
        content = issue_path.read_text(encoding="utf-8")
        now = datetime.now()
        finished_str = f"%% Finished: {now.strftime('%Y-%m-%d %H:%M')} %%"
        content = re.sub(r"%% Finished: .*? %%", finished_str, content) if "%% Finished:" in content else content + f"\n{finished_str}"
        content = content.replace("#inbox", "#review").replace("#processing", "#review")
        issue_path.write_text(content, encoding="utf-8")
        return move_issue(iss_uniq_id, "30_ToReview")
    except Exception as e: return f"Error: {str(e)}"

# --- Telegram Tools ---

@mcp.tool()
def set_telegram_webhook(url: str) -> str:
    """Set the Telegram bot webhook URL."""
    token = _get_bot_token()
    if not token: return "Error: TELEGRAM_BOT_TOKEN not found"
    try:
        resp = requests.post(f"https://api.telegram.org/bot{token}/setWebhook", data={"url": url}, timeout=10)
        return resp.text
    except Exception as e: return f"Error: {str(e)}"

@mcp.tool()
def check_telegram_webhook() -> str:
    """Check Telegram bot webhook status."""
    token = _get_bot_token()
    if not token: return "Error: TELEGRAM_BOT_TOKEN not found"
    try:
        resp = requests.get(f"https://api.telegram.org/bot{token}/getWebhookInfo", timeout=10)
        return resp.text
    except Exception as e: return f"Error: {str(e)}"

@mcp.tool()
def poll_telegram_updates() -> str:
    """Poll Telegram for updates and forward them to local webhook."""
    token = _get_bot_token()
    if not token: return "Error: TELEGRAM_BOT_TOKEN not found"
    try:
        resp = requests.get(f"https://api.telegram.org/bot{token}/getUpdates", params={"timeout": 1}, timeout=15)
        data = resp.json()
        if not data.get("ok"): return f"Error: {data.get('description')}"
        updates = data.get("result", [])
        if not updates: return "No updates."
        results = []
        webhook_url = "http://localhost:8000/api/v1/telegram/webhook/"
        last_id = 0
        for upd in updates:
            try:
                requests.post(webhook_url, json=upd, timeout=10)
                results.append(f"Forwarded {upd['update_id']}")
                last_id = upd['update_id']
            except Exception as e: results.append(f"Failed {upd['update_id']}: {str(e)}")
        if last_id:
            requests.get(f"https://api.telegram.org/bot{token}/getUpdates", params={"offset": last_id + 1})
        return "\n".join(results)
    except Exception as e: return f"Error: {str(e)}"

@mcp.tool()
def list_issues(status: str = "inbox") -> str:
    """List issues with a specific status (compatibility wrapper)."""
    if status not in STATUS_MAP: return "Error: Invalid status"
    return list_stage_issues(STATUS_MAP[status])

@mcp.tool()
def audit_vault_features() -> str:
    """Audit implementation against vault features."""
    vault_root = get_vault_path()
    summary = ["### Vault Feature Audit Summary\n"]
    key_terms = ["firebase", "authentication", "notification", "password"]
    found = []
    for folder in [STATUS_MAP["inbox"], STATUS_MAP["processing"]]:
        stage = vault_root / folder
        if not stage.exists(): continue
        for f in stage.glob("*.md"):
            try:
                if any(t in f.read_text(encoding="utf-8").lower() for t in key_terms):
                    found.append(f"- [{folder}] {f.name}")
            except: continue
    summary.append("Found issues:" if found else "No active issues.")
    summary.extend(found)
    return "\n".join(summary)

if __name__ == "__main__":
    mcp.run()
