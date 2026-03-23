import os
import shutil
import re
import uuid
from datetime import datetime
from pathlib import Path
from typing import Optional
from mcp.server.fastmcp import FastMCP

# Initialize FastMCP server
mcp = FastMCP("Vault")

# Get VAULT_PATH from environment variable
DEFAULT_VAULT_PATH = "/home/lexx/Q/massage.kg/.unihub-vault/UniHubVault"
VAULT_PATH = os.environ.get("VAULT_PATH", DEFAULT_VAULT_PATH)

def get_vault_path() -> Path:
    if not VAULT_PATH:
        raise ValueError("VAULT_PATH environment variable is not set")
    return Path(VAULT_PATH)

def _find_issue_path(iss_uniq_id: str) -> Optional[Path]:
    """Helper to find an issue's file path by its unique ID."""
    vault_root = get_vault_path()
    valid_stages = ["10_Inbox", "20_Processing", "30_ToReview", "999_Finished"]
    
    for stage in valid_stages:
        stage_dir = vault_root / stage
        if not stage_dir.exists():
            continue
        # Search for files containing the unique ID
        for file in stage_dir.glob(f"*{iss_uniq_id}*.md"):
            return file
    return None

@mcp.tool()
def read_note(path: str) -> str:
    """
    Read a note from the vault.
    
    Args:
        path: The path to the note relative to the vault root (e.g., '10_Inbox/note.md').
    """
    vault_root = get_vault_path()
    full_path = (vault_root / path).resolve()
    
    # Security check: ensure the path is within the vault
    if not str(full_path).startswith(str(vault_root.resolve())):
        return f"Error: Access denied. Path {path} is outside the vault."
    
    if not full_path.exists():
        return f"Error: File not found at {path}"
    
    if not full_path.is_file():
        return f"Error: {path} is not a file"
        
    try:
        return full_path.read_text(encoding="utf-8")
    except Exception as e:
        return f"Error reading file: {str(e)}"

@mcp.tool()
def get_protocol(name: str) -> str:
    """
    Get a protocol content from the 50_Protocols/ directory.
    
    Args:
        name: The name of the protocol (with or without .md extension).
    """
    if not name.endswith(".md"):
        filename = f"{name}.md"
    else:
        filename = name
        
    return read_note(f"50_Protocols/{filename}")

@mcp.tool()
def search_vault(query: str, search_type: str = "keyword") -> str:
    """
    Search through all .md files in the vault directory.
    
    Args:
        query: The search query or regex pattern.
        search_type: The type of search (one of: 'keyword', 'regex').
    """
    if search_type not in ["keyword", "regex"]:
        return "Error: search_type must be either 'keyword' or 'regex'"

    vault_root = get_vault_path()
    results = []

    try:
        pattern = None
        if search_type == "regex":
            try:
                pattern = re.compile(query, re.IGNORECASE)
            except re.error as e:
                return f"Error: Invalid regex pattern: {str(e)}"

        for md_file in vault_root.rglob("*.md"):
            try:
                content = md_file.read_text(encoding="utf-8")
                lines = content.splitlines()
                for i, line in enumerate(lines):
                    match = False
                    if search_type == "keyword":
                        if query.lower() in line.lower():
                            match = True
                    elif search_type == "regex" and pattern:
                        if pattern.search(line):
                            match = True
                    
                    if match:
                        rel_path = md_file.relative_to(vault_root)
                        results.append(f"{rel_path}:{i+1}: {line.strip()}")
            except (IOError, UnicodeDecodeError):
                continue

        if not results:
            return f"No matches found for {search_type} '{query}'"
        
        return "\n".join(results)
    except Exception as e:
        return f"Error during search: {str(e)}"

@mcp.tool()
def list_notes(directory: str = None) -> str:
    """
    List all markdown files in the specified directory (or root if not provided).
    
    Args:
        directory: The directory to list notes from, relative to the vault root.
    """
    vault_root = get_vault_path()
    if directory:
        target_dir = (vault_root / directory).resolve()
        if not str(target_dir).startswith(str(vault_root.resolve())):
            return f"Error: Access denied. Path {directory} is outside the vault."
    else:
        target_dir = vault_root.resolve()

    if not target_dir.exists():
        return f"Error: Directory not found at {directory if directory else 'root'}"

    if not target_dir.is_dir():
        return f"Error: {directory} is not a directory"

    try:
        notes = []
        for file in target_dir.glob("*.md"):
            if file.is_file():
                notes.append(file.name)
        
        if not notes:
            return f"No markdown files found in {directory if directory else 'root'}."
        
        return "\n".join(sorted(notes))
    except Exception as e:
        return f"Error listing notes: {str(e)}"

@mcp.tool()
def list_stage_issues(stage: str) -> str:
    """
    List all issues in a specific stage directory.
    
    Args:
        stage: One of: '10_Inbox', '20_Processing', '30_ToReview', '999_Finished'.
    """
    valid_stages = ["10_Inbox", "20_Processing", "30_ToReview", "999_Finished"]
    if stage not in valid_stages:
        return f"Error: Invalid stage. Must be one of {valid_stages}"
        
    return list_notes(stage)

@mcp.tool()
def create_issue(name: str, body: str, tags: list[str] = None) -> str:
    """
    Create a new issue in the 10_Inbox directory.
    
    Args:
        name: The name of the issue.
        body: The description/body of the issue.
        tags: Optional list of tags for the issue.
    """
    vault_root = get_vault_path()
    template_path = vault_root / "888_System/Templates/New Issue Template.md"
    
    if not template_path.exists():
        return f"Error: Template not found at {template_path}"
    
    try:
        template_content = template_path.read_text(encoding="utf-8")
        
        now = datetime.now()
        date_str = now.strftime("%Y-%m-%d")
        time_str = now.strftime("%H:%M")
        day_mon = now.strftime("%d-%b").lower()
        
        # Generate unique ID
        iss_uniq_id = str(uuid.uuid4())[:8]
        
        category = ", ".join(tags) if tags else "issue"
        content = template_content.replace("{{category}}", category)
        content = content.replace("{{date}}", date_str)
        content = content.replace("{{time}}", time_str)
        
        # Inject body into description area
        description_placeholder = "- [Provide a brief overview of the issue]"
        if description_placeholder in content:
            content = content.replace(description_placeholder, f"- {body}")
        else:
            content += f"\n\n### Context\n{body}"
            
        # Add Unique ID to the content
        content = f"ID: {iss_uniq_id}\n" + content
            
        filename = f"<~{day_mon}~> {iss_uniq_id}_{name}.md"
        target_path = vault_root / "10_Inbox" / filename
        
        target_path.parent.mkdir(parents=True, exist_ok=True)
        target_path.write_text(content, encoding="utf-8")
        
        return iss_uniq_id
        
    except Exception as e:
        return f"Error creating issue: {str(e)}"

@mcp.tool()
def read_issue(iss_uniq_id: str) -> str:
    """
    Read an issue's content by its unique ID.
    
    Args:
        iss_uniq_id: The unique ID of the issue.
    """
    issue_path = _find_issue_path(iss_uniq_id)
    if not issue_path:
        return f"Error: Issue with ID '{iss_uniq_id}' not found."
        
    try:
        return issue_path.read_text(encoding="utf-8")
    except Exception as e:
        return f"Error reading issue: {str(e)}"

@mcp.tool()
def update_issue(iss_uniq_id: str, content: str, append: bool = False) -> str:
    """
    Update an issue's content by its unique ID.
    
    Args:
        iss_uniq_id: The unique ID of the issue.
        content: The new content (or content to append).
        append: If True, append to existing content instead of overwriting.
    """
    issue_path = _find_issue_path(iss_uniq_id)
    if not issue_path:
        return f"Error: Issue with ID '{iss_uniq_id}' not found."
        
    try:
        if append:
            existing_content = issue_path.read_text(encoding="utf-8")
            if existing_content and not existing_content.endswith("\n"):
                existing_content += "\n"
            new_content = existing_content + content
        else:
            new_content = content
            
        issue_path.write_text(new_content, encoding="utf-8")
        action = "appended to" if append else "updated"
        return f"Successfully {action} issue {iss_uniq_id}"
    except Exception as e:
        return f"Error updating issue: {str(e)}"

@mcp.tool()
def move_issue(iss_uniq_id: str, target_stage: str) -> str:
    """
    Move an issue to a different stage directory by its unique ID.
    
    Args:
        iss_uniq_id: The unique ID of the issue.
        target_stage: One of: '10_Inbox', '20_Processing', '30_ToReview', '999_Finished'.
    """
    valid_stages = ["10_Inbox", "20_Processing", "30_ToReview", "999_Finished"]
    if target_stage not in valid_stages:
        return f"Error: Invalid target stage. Must be one of {valid_stages}"
        
    issue_path = _find_issue_path(iss_uniq_id)
    if not issue_path:
        return f"Error: Issue with ID '{iss_uniq_id}' not found."
        
    vault_root = get_vault_path()
    target_path = vault_root / target_stage / issue_path.name
    
    # Ensure target directory exists
    target_path.parent.mkdir(parents=True, exist_ok=True)
    
    try:
        if issue_path != target_path:
            shutil.move(str(issue_path), str(target_path))
        return f"Moved issue {iss_uniq_id} to {target_stage}"
    except Exception as e:
        return f"Error moving issue: {str(e)}"

@mcp.tool()
def start_issue(iss_uniq_id: str) -> str:
    """
    Start an issue by moving it to 20_Processing.
    
    Args:
        iss_uniq_id: The unique ID of the issue.
    """
    result = move_issue(iss_uniq_id, "20_Processing")
    if result.startswith("Error"):
        return result
        
    # After moving, read the content to return it as part of the "start" action
    content = read_issue(iss_uniq_id)
    return f"Issue {iss_uniq_id} started and moved to 20_Processing.\n\nDetails:\n{content}"

@mcp.tool()
def finish_issue(iss_uniq_id: str) -> str:
    """
    Finish an issue by updating timestamps and moving it to 30_ToReview.
    
    Args:
        iss_uniq_id: The unique ID of the issue.
    """
    issue_path = _find_issue_path(iss_uniq_id)
    if not issue_path:
        return f"Error: Issue with ID '{iss_uniq_id}' not found."
        
    try:
        content = issue_path.read_text(encoding="utf-8")
        now = datetime.now()
        date_str = now.strftime("%Y-%m-%d")
        time_str = now.strftime("%H:%M")
        
        # Update or add finished timestamp
        finished_str = f"%% Finished: {date_str} {time_str} %%"
        if "%% Finished:" in content:
            content = re.sub(r"%% Finished: .*? %%", finished_str, content)
        else:
            content += f"\n{finished_str}"
            
        # Update state tag if it exists
        content = content.replace("#inbox", "#review").replace("#processing", "#review")
        
        issue_path.write_text(content, encoding="utf-8")
        
        return move_issue(iss_uniq_id, "30_ToReview")
    except Exception as e:
        return f"Error finishing issue: {str(e)}"

if __name__ == "__main__":
    mcp.run()
