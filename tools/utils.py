"""
Shared utility functions for Foreman.
"""

import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax
from rich.table import Table

# Windows consoles often default stdout/stderr to a legacy codepage (e.g.
# cp1252) that can't encode the Unicode symbols (checkmarks, emoji) used
# throughout this CLI's output, crashing with UnicodeEncodeError. Force
# UTF-8 so output works the same on every platform.
if sys.platform == "win32":
    for _stream in (sys.stdout, sys.stderr):
        if hasattr(_stream, "reconfigure"):
            _stream.reconfigure(encoding="utf-8", errors="replace")

console = Console()


def log_info(message: str):
    """Print an info message."""
    console.print(f"[blue]ℹ[/blue] {message}")


def log_success(message: str):
    """Print a success message."""
    console.print(f"[green]✓[/green] {message}")


def log_warning(message: str):
    """Print a warning message."""
    console.print(f"[yellow]⚠[/yellow] {message}")


def log_error(message: str):
    """Print an error message."""
    console.print(f"[red]✗[/red] {message}")


def load_json(path: Path) -> dict:
    """Load JSON data from a file."""
    if path.exists():
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_json(path: Path, data: dict, indent: int = 2):
    """Save JSON data to a file."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=indent, default=str)


def get_timestamp() -> str:
    """Get current timestamp in ISO format."""
    return datetime.now().isoformat()


def get_date() -> str:
    """Get current date in YYYY-MM-DD format."""
    return datetime.now().strftime("%Y-%m-%d")


def format_duration(seconds: float) -> str:
    """Format a duration in seconds to a human-readable string."""
    if seconds < 60:
        return f"{int(seconds)}s"
    elif seconds < 3600:
        mins = int(seconds // 60)
        secs = int(seconds % 60)
        return f"{mins}m {secs}s"
    else:
        hours = int(seconds // 3600)
        mins = int((seconds % 3600) // 60)
        return f"{hours}h {mins}m"


def get_project_type(project_path: Path) -> str:
    """Detect the type of project based on files present."""
    indicators = {
        "python": ["requirements.txt", "pyproject.toml", "setup.py", "*.py"],
        "node": ["package.json", "node_modules"],
        "rust": ["Cargo.toml"],
        "go": ["go.mod"],
        "web": ["index.html", "*.html"],
    }

    detected = []
    for ptype, files in indicators.items():
        for pattern in files:
            if "*" in pattern:
                if list(project_path.glob(pattern)):
                    detected.append(ptype)
                    break
            elif (project_path / pattern).exists():
                detected.append(ptype)
                break

    if not detected:
        return "unknown"
    return detected[0] if len(detected) == 1 else "mixed"


def display_panel(title: str, content: str, style: str = "blue"):
    """Display content in a styled panel."""
    console.print(Panel(content, title=title, border_style=style))


def display_code(code: str, language: str = "python"):
    """Display syntax-highlighted code."""
    syntax = Syntax(code, language, theme="monokai", line_numbers=True)
    console.print(syntax)


def display_table(title: str, columns: list[str], rows: list[list[Any]]):
    """Display data in a table format."""
    table = Table(title=title)
    for col in columns:
        table.add_column(col)
    for row in rows:
        table.add_row(*[str(item) for item in row])
    console.print(table)


def find_python_files(directory: Path) -> list[Path]:
    """Find all Python files in a directory."""
    return list(directory.rglob("*.py"))


def find_js_files(directory: Path) -> list[Path]:
    """Find all JavaScript files in a directory."""
    return list(directory.rglob("*.js")) + list(directory.rglob("*.ts"))


def read_file_safely(path: Path) -> Optional[str]:
    """Read a file, returning None if it doesn't exist or can't be read."""
    try:
        return path.read_text(encoding="utf-8")
    except Exception:
        return None
