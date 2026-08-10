"""
Auto-Logger - Cross-project error, fix, and change logging with LLM summaries.

Usage from any directory:
    autolog error "Error message"
    autolog fix "What you did to fix it"
    autolog change "Description of change"
    autolog list
    autolog report
"""

import json
import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Optional

import click
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel

from .config import get_config
from .utils import log_info, log_success, log_warning

console = Console()

# Central log storage location
LOGS_DIR = Path.home() / ".foreman_logs"
LOGS_FILE = LOGS_DIR / "logs.json"


# ============================================================================
# Data Models
# ============================================================================

@dataclass
class AutoLogEntry:
    """A single auto-log entry."""
    id: str
    timestamp: str
    log_type: str  # error, fix, change, note, todo
    message: str
    project: str
    project_path: str
    llm_summary: Optional[str] = None
    related_entry_id: Optional[str] = None  # Links fixes to errors
    tags: list[str] = field(default_factory=list)
    metadata: dict = field(default_factory=dict)


# ============================================================================
# Project Detection
# ============================================================================

def detect_project() -> tuple[str, str]:
    """
    Auto-detect project name and path from current directory.

    Checks (in order):
    1. Git repository name
    2. pyproject.toml project name
    3. package.json name
    4. Current directory name

    Returns: (project_name, project_path)
    """
    cwd = Path.cwd()
    project_path = str(cwd)

    # Try git
    git_dir = cwd / ".git"
    if git_dir.exists():
        # Get remote origin or folder name
        try:
            config_file = git_dir / "config"
            if config_file.exists():
                content = config_file.read_text(encoding="utf-8")
                for line in content.split("\n"):
                    if "url = " in line:
                        url = line.split("url = ")[-1].strip()
                        # Extract repo name from URL
                        name = url.rstrip("/").split("/")[-1]
                        if name.endswith(".git"):
                            name = name[:-4]
                        return name, project_path
        except Exception:
            pass

    # Try pyproject.toml
    pyproject = cwd / "pyproject.toml"
    if pyproject.exists():
        try:
            content = pyproject.read_text(encoding="utf-8")
            for line in content.split("\n"):
                if line.strip().startswith("name"):
                    # Extract name = "value"
                    name = line.split("=")[-1].strip().strip('"\'')
                    return name, project_path
        except Exception:
            pass

    # Try package.json
    package_json = cwd / "package.json"
    if package_json.exists():
        try:
            data = json.loads(package_json.read_text(encoding="utf-8"))
            if "name" in data:
                return data["name"], project_path
        except Exception:
            pass

    # Default to directory name
    return cwd.name, project_path


# ============================================================================
# LLM Integration
# ============================================================================

def generate_summary(log_type: str, message: str) -> Optional[str]:
    """Generate an LLM summary for the log entry using autolog-specific LLM."""
    config = get_config()

    if not config.llm_enabled:
        return None

    prompts = {
        "error": f"Briefly summarize this error (1 sentence, focus on the root cause):\n{message}",
        "fix": f"Briefly summarize this fix (1 sentence, focus on what was done):\n{message}",
        "change": f"Briefly summarize this change (1 sentence, focus on impact):\n{message}",
        "note": None,  # Don't summarize notes
        "todo": None,  # Don't summarize todos
    }

    prompt = prompts.get(log_type)
    if not prompt:
        return None

    try:
        import requests

        # Use autolog-specific LLM settings (can be a smaller/faster model)
        response = requests.post(
            f"{config.llm_autolog_url}/chat/completions",
            json={
                "model": config.llm_autolog_model,
                "messages": [
                    {"role": "system", "content": "You are a concise technical writer. Provide brief, clear summaries. No fluff."},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.3,
                "max_tokens": 100
            },
            timeout=15
        )

        if response.status_code == 200:
            return response.json()["choices"][0]["message"]["content"].strip()
    except Exception as e:
        log_warning(f"LLM unavailable: {e}")

    return None


# ============================================================================
# Storage
# ============================================================================

class AutoLogStore:
    """Manages central log storage."""

    def __init__(self):
        LOGS_DIR.mkdir(parents=True, exist_ok=True)
        self.logs_file = LOGS_FILE

    def load_logs(self) -> list[dict]:
        """Load all log entries."""
        if self.logs_file.exists():
            try:
                return json.loads(self.logs_file.read_text(encoding="utf-8"))
            except Exception:
                return []
        return []

    def save_logs(self, logs: list[dict]):
        """Save all log entries."""
        self.logs_file.write_text(json.dumps(logs, indent=2, default=str), encoding="utf-8")

    def add_entry(self, entry: AutoLogEntry):
        """Add a new log entry."""
        logs = self.load_logs()
        logs.append(asdict(entry))
        self.save_logs(logs)

    def get_recent(self, limit: int = 20, log_type: Optional[str] = None,
                   project: Optional[str] = None) -> list[dict]:
        """Get recent log entries with optional filters."""
        logs = self.load_logs()

        # Filter
        if log_type:
            logs = [entry for entry in logs if entry["log_type"] == log_type]
        if project:
            logs = [entry for entry in logs if project.lower() in entry["project"].lower()]

        # Sort by timestamp descending and limit
        logs.sort(key=lambda x: x["timestamp"], reverse=True)
        return logs[:limit]

    def get_last_error(self, project: Optional[str] = None) -> Optional[dict]:
        """Get the most recent error for linking fixes."""
        errors = self.get_recent(limit=1, log_type="error", project=project)
        return errors[0] if errors else None


# Global store
_store: Optional[AutoLogStore] = None


def get_store() -> AutoLogStore:
    """Get the global store instance."""
    global _store
    if _store is None:
        _store = AutoLogStore()
    return _store


# ============================================================================
# Core Logging Functions
# ============================================================================

def log_entry(log_type: str, message: str, link_to_error: bool = False,
              tags: list[str] = None) -> AutoLogEntry:
    """Log an entry with optional LLM summary."""
    store = get_store()
    project_name, project_path = detect_project()

    # Generate LLM summary
    with console.status("[bold blue]Generating summary...[/]", spinner="dots"):
        llm_summary = generate_summary(log_type, message)

    # Link fixes to most recent error
    related_id = None
    if link_to_error and log_type == "fix":
        last_error = store.get_last_error(project_name)
        if last_error:
            related_id = last_error["id"]

    entry = AutoLogEntry(
        id=str(uuid.uuid4())[:8],
        timestamp=datetime.now().isoformat(),
        log_type=log_type,
        message=message,
        project=project_name,
        project_path=project_path,
        llm_summary=llm_summary,
        related_entry_id=related_id,
        tags=tags or []
    )

    store.add_entry(entry)
    return entry


def display_entry(entry: dict):
    """Display a log entry nicely."""
    icons = {
        "error": "❌",
        "fix": "✅",
        "change": "🔄",
        "note": "📝",
        "todo": "📋"
    }
    colors = {
        "error": "red",
        "fix": "green",
        "change": "blue",
        "note": "yellow",
        "todo": "magenta"
    }

    icon = icons.get(entry["log_type"], "•")
    color = colors.get(entry["log_type"], "white")
    time = entry["timestamp"][11:16]

    console.print(f"[{color}]{icon}[/] [{time}] [bold]{entry['project']}[/]")
    console.print(f"   {entry['message']}")
    if entry.get("llm_summary"):
        console.print(f"   [dim italic]→ {entry['llm_summary']}[/]")
    console.print()


# ============================================================================
# CLI Interface
# ============================================================================

@click.group()
def cli_main():
    """
    🔍 Auto-Logger - Track errors, fixes, and changes across projects.

    Logs are stored centrally at ~/.foreman_logs/
    """
    pass


@cli_main.command("error")
@click.argument("message")
@click.option("--tags", "-t", multiple=True, help="Tags for the entry")
def cmd_error(message: str, tags: tuple):
    """Log an error."""
    entry = log_entry("error", message, tags=list(tags))
    log_success(f"Logged error in [bold]{entry.project}[/]")
    if entry.llm_summary:
        console.print(f"[dim]Summary: {entry.llm_summary}[/]")


@cli_main.command("fix")
@click.argument("message")
@click.option("--tags", "-t", multiple=True, help="Tags for the entry")
@click.option("--link/--no-link", default=True, help="Link to most recent error")
def cmd_fix(message: str, tags: tuple, link: bool):
    """Log a fix/resolution."""
    entry = log_entry("fix", message, link_to_error=link, tags=list(tags))
    log_success(f"Logged fix in [bold]{entry.project}[/]")
    if entry.related_entry_id:
        console.print(f"[dim]Linked to error: {entry.related_entry_id}[/]")
    if entry.llm_summary:
        console.print(f"[dim]Summary: {entry.llm_summary}[/]")


@cli_main.command("change")
@click.argument("message")
@click.option("--tags", "-t", multiple=True, help="Tags for the entry")
def cmd_change(message: str, tags: tuple):
    """Log a change."""
    entry = log_entry("change", message, tags=list(tags))
    log_success(f"Logged change in [bold]{entry.project}[/]")
    if entry.llm_summary:
        console.print(f"[dim]Summary: {entry.llm_summary}[/]")


@cli_main.command("note")
@click.argument("message")
@click.option("--tags", "-t", multiple=True, help="Tags for the entry")
def cmd_note(message: str, tags: tuple):
    """Log a note."""
    entry = log_entry("note", message, tags=list(tags))
    log_success(f"Logged note in [bold]{entry.project}[/]")


@cli_main.command("todo")
@click.argument("message")
@click.option("--tags", "-t", multiple=True, help="Tags for the entry")
def cmd_todo(message: str, tags: tuple):
    """Log a todo item."""
    entry = log_entry("todo", message, tags=list(tags))
    log_success(f"Logged todo in [bold]{entry.project}[/]")


@cli_main.command("list")
@click.option("--type", "-t", "log_type", help="Filter by type (error, fix, change, note, todo)")
@click.option("--project", "-p", help="Filter by project name")
@click.option("--limit", "-n", default=20, help="Number of entries to show")
@click.option("--all", "-a", "show_all", is_flag=True, help="Show all projects")
def cmd_list(log_type: str, project: str, limit: int, show_all: bool):
    """List recent log entries."""
    store = get_store()

    # Default to current project unless --all
    if not show_all and not project:
        project, _ = detect_project()

    entries = store.get_recent(limit=limit, log_type=log_type, project=project)

    if not entries:
        log_info("No log entries found.")
        return

    title = "Recent Logs"
    if project:
        title += f" for {project}"
    if log_type:
        title += f" (type: {log_type})"

    console.print(Panel(f"[bold]{title}[/]", border_style="blue"))
    console.print()

    for entry in entries:
        display_entry(entry)


@cli_main.command("report")
@click.option("--project", "-p", help="Generate report for specific project")
@click.option("--output", "-o", help="Output file path")
def cmd_report(project: str, output: str):
    """Generate a summary report."""
    store = get_store()

    if not project:
        project, _ = detect_project()

    entries = store.get_recent(limit=100, project=project)

    if not entries:
        log_warning(f"No logs found for {project}")
        return

    # Count by type
    errors = [e for e in entries if e["log_type"] == "error"]
    fixes = [e for e in entries if e["log_type"] == "fix"]
    changes = [e for e in entries if e["log_type"] == "change"]
    notes = [e for e in entries if e["log_type"] == "note"]
    todos = [e for e in entries if e["log_type"] == "todo"]

    # Build report
    lines = [
        f"# 📊 Log Report: {project}",
        f"*Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}*",
        "",
        "## Overview",
        "",
        "| Metric | Count |",
        "|--------|-------|",
        f"| Errors | {len(errors)} |",
        f"| Fixes | {len(fixes)} |",
        f"| Changes | {len(changes)} |",
        f"| Notes | {len(notes)} |",
        f"| Todos | {len(todos)} |",
        "",
    ]

    if errors:
        lines.extend(["## ❌ Errors", ""])
        for e in errors[:10]:
            time = e["timestamp"][:16].replace("T", " ")
            lines.append(f"- **[{time}]** {e['message']}")
            if e.get("llm_summary"):
                lines.append(f"  - *{e['llm_summary']}*")
        lines.append("")

    if fixes:
        lines.extend(["## ✅ Fixes", ""])
        for e in fixes[:10]:
            time = e["timestamp"][:16].replace("T", " ")
            lines.append(f"- **[{time}]** {e['message']}")
            if e.get("llm_summary"):
                lines.append(f"  - *{e['llm_summary']}*")
        lines.append("")

    if changes:
        lines.extend(["## 🔄 Changes", ""])
        for e in changes[:10]:
            time = e["timestamp"][:16].replace("T", " ")
            lines.append(f"- [{time}] {e['message']}")
        lines.append("")

    report = "\n".join(lines)

    if output:
        Path(output).write_text(report, encoding="utf-8")
        log_success(f"Report saved to: {output}")
    else:
        console.print(Panel(Markdown(report), title="📊 Log Report", border_style="blue"))


# Also expose via foreman CLI
def register_commands(main_cli):
    """Register autolog commands with the main foreman CLI."""
    main_cli.add_command(cli_main, name="autolog")


if __name__ == "__main__":
    cli_main()
