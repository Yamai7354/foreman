"""
Code Watcher Daemon - Background LLM-powered code analyzer.

Watches code files for changes and uses a small coder LLM to detect
potential issues, automatically logging them via autolog.

Usage:
    codewatch start         # Start watching current project
    codewatch stop          # Stop the daemon
    codewatch status        # Check if running
    codewatch issues        # View detected issues
    codewatch scan .        # One-time scan
"""

import json
import os
import re
import signal
import sys
import threading
import time
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Optional

import click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from .config import get_config
from .utils import log_error, log_info, log_success, log_warning

console = Console()

# Storage paths
LOGS_DIR = Path.home() / ".foreman_logs"
PID_FILE = LOGS_DIR / "codewatch.pid"
ISSUES_FILE = LOGS_DIR / "issues.json"
WATCH_LOG = LOGS_DIR / "codewatch.log"

# Supported file extensions
WATCHED_EXTENSIONS = {
    ".py", ".js", ".ts", ".jsx", ".tsx", ".go", ".rs", ".rb",
    ".java", ".c", ".cpp", ".h", ".hpp", ".cs", ".swift",
    ".css", ".scss", ".html", ".vue", ".svelte"
}

# Language mapping for prompts
EXTENSION_LANGUAGES = {
    ".py": "Python", ".js": "JavaScript", ".ts": "TypeScript",
    ".jsx": "React JSX", ".tsx": "React TSX", ".go": "Go",
    ".rs": "Rust", ".rb": "Ruby", ".java": "Java",
    ".c": "C", ".cpp": "C++", ".h": "C/C++ Header",
    ".hpp": "C++ Header", ".cs": "C#", ".swift": "Swift",
    ".css": "CSS", ".scss": "SCSS", ".html": "HTML",
    ".vue": "Vue", ".svelte": "Svelte"
}

# Default system prompt (can be customized)
DEFAULT_SYSTEM_PROMPT = """You are a code reviewer. Analyze code and report issues as JSON.
Only report actual problems, not style suggestions. Focus on:
- Syntax errors and typos
- Logic bugs and edge cases
- Undefined variables or missing imports
- Security vulnerabilities
- Type mismatches"""

# User can override via environment variable
CUSTOM_PROMPT_FILE = LOGS_DIR / "codewatch_prompt.txt"


# ============================================================================
# Data Models
# ============================================================================

@dataclass
class CodeIssue:
    """A detected code issue."""
    id: str
    timestamp: str
    file_path: str
    line: int
    severity: str  # error, warning, info
    message: str
    llm_explanation: Optional[str] = None
    resolved: bool = False
    project: str = ""


# ============================================================================
# Issue Storage
# ============================================================================

class IssueStore:
    """Manages code issue storage."""

    def __init__(self):
        LOGS_DIR.mkdir(parents=True, exist_ok=True)
        self.issues_file = ISSUES_FILE

    def load_issues(self) -> list[dict]:
        """Load all issues."""
        if self.issues_file.exists():
            try:
                return json.loads(self.issues_file.read_text(encoding="utf-8"))
            except Exception:
                return []
        return []

    def save_issues(self, issues: list[dict]):
        """Save all issues."""
        self.issues_file.write_text(json.dumps(issues, indent=2, default=str), encoding="utf-8")

    def add_issue(self, issue: CodeIssue):
        """Add a new issue."""
        issues = self.load_issues()
        issues.append(asdict(issue))
        self.save_issues(issues)

    def get_issues(self, unresolved_only: bool = False,
                   file_path: Optional[str] = None) -> list[dict]:
        """Get issues with optional filters."""
        issues = self.load_issues()

        if unresolved_only:
            issues = [i for i in issues if not i.get("resolved", False)]
        if file_path:
            issues = [i for i in issues if file_path in i["file_path"]]

        # Sort by timestamp descending
        issues.sort(key=lambda x: x["timestamp"], reverse=True)
        return issues

    def clear_issues_for_file(self, file_path: str):
        """Clear all issues for a specific file (re-scan clears old issues)."""
        issues = self.load_issues()
        issues = [i for i in issues if i["file_path"] != file_path]
        self.save_issues(issues)


# ============================================================================
# LLM Analysis
# ============================================================================

def get_system_prompt() -> str:
    """Get the system prompt, allowing customization via file."""
    if CUSTOM_PROMPT_FILE.exists():
        try:
            return CUSTOM_PROMPT_FILE.read_text(encoding="utf-8").strip()
        except Exception:
            pass
    return DEFAULT_SYSTEM_PROMPT


def analyze_code(file_path: Path, content: str) -> list[dict]:
    """Analyze code using LLM and return detected issues."""
    config = get_config()

    if not config.llm_enabled:
        return []

    ext = file_path.suffix.lower()
    language = EXTENSION_LANGUAGES.get(ext, "code")

    prompt = f"""Analyze this {language} code for issues. Report ONLY actual problems.

File: {file_path.name}

```{language.lower()}
{content[:4000]}
```

Respond with a JSON array of issues found. Each issue should have:
- "line": line number (integer)
- "severity": "error" or "warning"
- "message": brief description

If no issues found, respond with: []

IMPORTANT: Respond with ONLY valid JSON, no other text."""

    try:
        import requests

        response = requests.post(
            f"{config.llm_codewatch_url}/chat/completions",
            json={
                "model": config.llm_codewatch_model,
                "messages": [
                    {"role": "system", "content": get_system_prompt()},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.1,
                "max_tokens": 500
            },
            timeout=30
        )

        if response.status_code == 200:
            result = response.json()["choices"][0]["message"]["content"].strip()

            # Try to extract JSON from response
            try:
                # Handle markdown code blocks
                if "```" in result:
                    match = re.search(r'```(?:json)?\s*([\s\S]*?)\s*```', result)
                    if match:
                        result = match.group(1)

                issues = json.loads(result)
                if isinstance(issues, list):
                    return issues
            except json.JSONDecodeError:
                pass
    except Exception as e:
        log_to_file(f"LLM error: {e}")

    return []


def log_to_file(message: str):
    """Log message to codewatch log file."""
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(WATCH_LOG, "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] {message}\n")


# ============================================================================
# Project Detection (reuse from auto_logger)
# ============================================================================

def detect_project(path: Path) -> str:
    """Detect project name from path."""
    # Walk up to find project root
    current = path if path.is_dir() else path.parent

    for _ in range(10):  # Max 10 levels up
        if (current / ".git").exists():
            return current.name
        if (current / "pyproject.toml").exists():
            return current.name
        if (current / "package.json").exists():
            return current.name
        parent = current.parent
        if parent == current:
            break
        current = parent

    return path.parent.name


# ============================================================================
# File Watcher
# ============================================================================

class CodeWatchHandler:
    """Handler for file system events."""

    def __init__(self, watch_path: Path):
        self.watch_path = watch_path
        self.store = IssueStore()
        self.pending_files: dict[str, float] = {}
        self.debounce_seconds = 2.0
        self.lock = threading.Lock()

    def should_watch(self, path: Path) -> bool:
        """Check if file should be watched."""
        if not path.is_file():
            return False

        # Skip hidden files and common ignore patterns
        path_str = str(path)
        ignore_patterns = [
            "/__pycache__/", "/node_modules/", "/.git/",
            "/.venv/", "/venv/", "/dist/", "/build/",
            "/.next/", "/.nuxt/", "/coverage/"
        ]
        for pattern in ignore_patterns:
            if pattern in path_str:
                return False

        return path.suffix.lower() in WATCHED_EXTENSIONS

    def on_modified(self, path: Path):
        """Handle file modification."""
        if not self.should_watch(path):
            return

        with self.lock:
            self.pending_files[str(path)] = time.time()

    def process_pending(self):
        """Process files that have been stable for debounce period."""
        now = time.time()
        to_process = []

        with self.lock:
            for file_path, last_modified in list(self.pending_files.items()):
                if now - last_modified >= self.debounce_seconds:
                    to_process.append(file_path)
                    del self.pending_files[file_path]

        for file_path in to_process:
            self.analyze_file(Path(file_path))

    def analyze_file(self, path: Path):
        """Analyze a single file."""
        try:
            content = path.read_text(encoding="utf-8", errors="ignore")
        except Exception as e:
            log_to_file(f"Error reading {path}: {e}")
            return

        log_to_file(f"Analyzing: {path}")

        # Clear old issues for this file
        self.store.clear_issues_for_file(str(path))

        # Get LLM analysis
        issues = analyze_code(path, content)

        if issues:
            project = detect_project(path)

            for issue_data in issues:
                issue = CodeIssue(
                    id=f"{int(time.time())}-{hash(str(path) + str(issue_data.get('line', 0))) % 10000:04d}",
                    timestamp=datetime.now().isoformat(),
                    file_path=str(path),
                    line=issue_data.get("line", 0),
                    severity=issue_data.get("severity", "warning"),
                    message=issue_data.get("message", "Unknown issue"),
                    project=project
                )
                self.store.add_issue(issue)
                log_to_file(f"Issue found: {issue.severity} at line {issue.line}: {issue.message}")

            # Also log to autolog
            try:
                from .auto_logger import log_entry
                log_entry(
                    "issue",
                    f"[{path.name}] Found {len(issues)} issue(s): {issues[0].get('message', '')[:100]}",
                    tags=["codewatch", project]
                )
            except Exception:
                pass  # Autolog integration is optional


# ============================================================================
# Daemon Management
# ============================================================================

def is_daemon_running() -> bool:
    """Check if daemon is running."""
    if not PID_FILE.exists():
        return False

    try:
        pid = int(PID_FILE.read_text(encoding="utf-8").strip())
        os.kill(pid, 0)  # Check if process exists
        return True
    except (ProcessLookupError, ValueError, PermissionError):
        PID_FILE.unlink(missing_ok=True)
        return False


def crawl_all_files(watch_path: Path, handler: 'CodeWatchHandler') -> int:
    """Crawl and analyze all code files in directory."""
    files_scanned = 0

    for file_path in watch_path.rglob("*"):
        if file_path.suffix.lower() in WATCHED_EXTENSIONS and handler.should_watch(file_path):
            log_to_file(f"Crawling: {file_path}")
            handler.analyze_file(file_path)
            files_scanned += 1

    return files_scanned


def start_daemon(watch_path: Path, initial_crawl: bool = False, scan_only: bool = False):
    """Start the watcher daemon."""
    if is_daemon_running():
        log_warning("Daemon is already running")
        return

    LOGS_DIR.mkdir(parents=True, exist_ok=True)

    # Fork to background
    pid = os.fork()
    if pid > 0:
        # Parent process
        PID_FILE.write_text(str(pid), encoding="utf-8")
        log_success(f"Started codewatch daemon (PID: {pid})")
        log_info(f"Watching: {watch_path}")
        if initial_crawl or scan_only:
            log_info("Scanning all files...")
        if scan_only:
            log_info("Scan-only mode: will stop after crawl completes")
        log_info(f"Log file: {WATCH_LOG}")
        return

    # Child process - become daemon
    os.setsid()

    # Redirect stdout/stderr to log
    sys.stdout = open(WATCH_LOG, "a", encoding="utf-8")
    sys.stderr = sys.stdout

    # Set up signal handler
    def handle_signal(signum, frame):
        log_to_file("Received stop signal, shutting down...")
        PID_FILE.unlink(missing_ok=True)
        sys.exit(0)

    signal.signal(signal.SIGTERM, handle_signal)
    signal.signal(signal.SIGINT, handle_signal)

    # Run the watcher (with optional initial crawl)
    run_watcher(watch_path, initial_crawl=initial_crawl, scan_only=scan_only)


def run_watcher(watch_path: Path, initial_crawl: bool = False, scan_only: bool = False):
    """Run the file watcher loop."""
    from watchdog.events import FileSystemEventHandler
    from watchdog.observers import Observer

    handler = CodeWatchHandler(watch_path)

    # Perform initial crawl if requested
    if initial_crawl or scan_only:
        log_to_file("Starting crawl of all files...")
        files_scanned = crawl_all_files(watch_path, handler)
        log_to_file(f"Crawl complete: {files_scanned} files analyzed")

        # If scan-only mode, exit after crawl
        if scan_only:
            store = IssueStore()
            issues = store.get_issues()
            log_to_file(f"Scan complete. Found {len(issues)} total issues.")
            PID_FILE.unlink(missing_ok=True)
            sys.exit(0)

    class WatchdogHandler(FileSystemEventHandler):
        def on_modified(self, event):
            if not event.is_directory:
                handler.on_modified(Path(event.src_path))

        def on_created(self, event):
            if not event.is_directory:
                handler.on_modified(Path(event.src_path))

    observer = Observer()
    observer.schedule(WatchdogHandler(), str(watch_path), recursive=True)
    observer.start()

    log_to_file(f"Started watching: {watch_path}")

    try:
        while True:
            handler.process_pending()
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()

    observer.join()


def stop_daemon():
    """Stop the watcher daemon."""
    if not is_daemon_running():
        log_warning("Daemon is not running")
        return

    try:
        pid = int(PID_FILE.read_text(encoding="utf-8").strip())
        os.kill(pid, signal.SIGTERM)
        PID_FILE.unlink(missing_ok=True)
        log_success("Stopped codewatch daemon")
    except Exception as e:
        log_error(f"Failed to stop daemon: {e}")


# ============================================================================
# CLI Interface
# ============================================================================

@click.group()
def cli_main():
    """
    🔍 Code Watcher - Background LLM-powered code analyzer.

    Watches code files and uses an LLM to detect potential issues.
    """
    pass


@cli_main.command("start")
@click.argument("path", type=click.Path(exists=True), default=".")
@click.option("--crawl", "-c", is_flag=True, help="Crawl and analyze all files before watching")
@click.option("--scan-only", "-s", is_flag=True, help="Scan all files then exit (no watching)")
def cmd_start(path: str, crawl: bool, scan_only: bool):
    """Start the code watcher daemon."""
    watch_path = Path(path).resolve()
    start_daemon(watch_path, initial_crawl=crawl, scan_only=scan_only)



@cli_main.command("stop")
def cmd_stop():
    """Stop the code watcher daemon."""
    stop_daemon()


@cli_main.command("status")
def cmd_status():
    """Check if the daemon is running."""
    if is_daemon_running():
        pid = PID_FILE.read_text(encoding="utf-8").strip()
        log_success(f"Daemon is running (PID: {pid})")
    else:
        log_info("Daemon is not running")


@cli_main.command("issues")
@click.option("--unresolved", "-u", is_flag=True, help="Show only unresolved issues")
@click.option("--file", "-f", "file_path", help="Filter by file path")
@click.option("--limit", "-n", default=20, help="Max issues to show")
def cmd_issues(unresolved: bool, file_path: str, limit: int):
    """View detected issues."""
    store = IssueStore()
    issues = store.get_issues(unresolved_only=unresolved, file_path=file_path)[:limit]

    if not issues:
        log_info("No issues found")
        return

    table = Table(title="🔍 Code Issues")
    table.add_column("Severity", style="bold")
    table.add_column("File", style="cyan")
    table.add_column("Line")
    table.add_column("Message")

    for issue in issues:
        severity = issue["severity"]
        sev_style = "red" if severity == "error" else "yellow"
        file_name = Path(issue["file_path"]).name

        table.add_row(
            f"[{sev_style}]{severity}[/]",
            file_name,
            str(issue.get("line", "?")),
            issue["message"][:60]
        )

    console.print(table)


@cli_main.command("scan")
@click.argument("path", type=click.Path(exists=True), default=".")
@click.option("--extensions", "-e", help="Comma-separated extensions to scan")
def cmd_scan(path: str, extensions: str):
    """Perform a one-time scan of a directory."""
    scan_path = Path(path).resolve()

    if extensions:
        ext_set = {f".{e.strip('.')}" for e in extensions.split(",")}
    else:
        ext_set = WATCHED_EXTENSIONS

    log_info(f"Scanning: {scan_path}")

    handler = CodeWatchHandler(scan_path)
    files_scanned = 0

    with console.status("[bold blue]Scanning files...[/]"):
        for file_path in scan_path.rglob("*"):
            if file_path.suffix.lower() in ext_set and handler.should_watch(file_path):
                handler.analyze_file(file_path)
                files_scanned += 1

    log_success(f"Scanned {files_scanned} files")

    # Show issues found
    store = IssueStore()
    issues = store.get_issues()
    if issues:
        log_warning(f"Found {len(issues)} issue(s). Run 'codewatch issues' to view.")
    else:
        log_success("No issues detected!")


@cli_main.command("clear")
@click.option("--all", "-a", "clear_all", is_flag=True, help="Clear all issues")
@click.option("--file", "-f", "file_path", help="Clear issues for specific file")
def cmd_clear(clear_all: bool, file_path: str):
    """Clear stored issues."""
    store = IssueStore()

    if clear_all:
        store.save_issues([])
        log_success("Cleared all issues")
    elif file_path:
        store.clear_issues_for_file(file_path)
        log_success(f"Cleared issues for: {file_path}")
    else:
        log_error("Specify --all or --file")


@cli_main.command("log")
@click.option("--lines", "-n", default=20, help="Number of lines to show")
@click.option("--follow", "-f", is_flag=True, help="Follow log in real-time (like tail -f)")
def cmd_log(lines: int, follow: bool):
    """View the daemon log."""
    if not WATCH_LOG.exists():
        log_info("No log file found")
        return

    if follow:
        # Stream the log file in real-time
        log_info(f"Following {WATCH_LOG} (Ctrl+C to stop)...")
        try:
            import subprocess
            subprocess.run(["tail", "-f", str(WATCH_LOG)])
        except KeyboardInterrupt:
            pass
        return

    content = WATCH_LOG.read_text(encoding="utf-8").strip().split("\n")
    for line in content[-lines:]:
        console.print(line)



@cli_main.command("prompt")
@click.option("--show", "-s", is_flag=True, help="Show current prompt")
@click.option("--edit", "-e", is_flag=True, help="Edit prompt (opens in editor)")
@click.option("--reset", "-r", is_flag=True, help="Reset to default prompt")
def cmd_prompt(show: bool, edit: bool, reset: bool):
    """Configure the LLM system prompt."""
    LOGS_DIR.mkdir(parents=True, exist_ok=True)

    if reset:
        if CUSTOM_PROMPT_FILE.exists():
            CUSTOM_PROMPT_FILE.unlink()
        log_success("Reset to default prompt")
        return

    if edit:
        # Create file with default if doesn't exist
        if not CUSTOM_PROMPT_FILE.exists():
            CUSTOM_PROMPT_FILE.write_text(DEFAULT_SYSTEM_PROMPT, encoding="utf-8")

        editor = os.getenv("EDITOR", "nano")
        os.system(f"{editor} {CUSTOM_PROMPT_FILE}")
        log_success(f"Prompt saved to: {CUSTOM_PROMPT_FILE}")
        return

    # Default: show current prompt
    current = get_system_prompt()
    console.print(Panel(current, title="Current System Prompt", border_style="blue"))
    console.print(f"\n[dim]Custom prompt file: {CUSTOM_PROMPT_FILE}[/]")


if __name__ == "__main__":
    cli_main()
