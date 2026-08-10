"""
Workflow Tracker - Track work sessions, changes, problems, and solutions.

This module provides tools for logging your development work, tracking what
you're working on, and maintaining a journal of problems and solutions.
"""

import json
import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime, timedelta
from typing import Optional

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from .db import dumps, get_connection, loads
from .utils import (
    format_duration,
    get_date,
    get_timestamp,
    log_info,
    log_success,
    log_warning,
)

console = Console()


# ============================================================================
# Data Models
# ============================================================================

@dataclass
class LogEntry:
    """A single log entry (change, problem, solution, or note)."""
    id: str
    timestamp: str
    type: str  # "change", "problem", "solution", "note"
    message: str
    session_id: Optional[str] = None
    tags: list[str] = field(default_factory=list)
    metadata: dict = field(default_factory=dict)


@dataclass
class WorkSession:
    """A work session with start/end times and associated logs."""
    id: str
    description: str
    project: Optional[str]
    started_at: str
    ended_at: Optional[str] = None
    summary: Optional[str] = None
    tags: list[str] = field(default_factory=list)
    entries: list[str] = field(default_factory=list)  # Log entry IDs
    duration_seconds: float = 0.0


# ============================================================================
# Data Storage
# ============================================================================

def _session_row_to_dict(row) -> dict:
    return {
        "id": row["id"],
        "description": row["description"],
        "project": row["project"],
        "started_at": row["started_at"],
        "ended_at": row["ended_at"],
        "summary": row["summary"],
        "tags": loads(row["tags"]),
        "duration_seconds": row["duration_seconds"],
    }


def _entry_row_to_dict(row) -> dict:
    return {
        "id": row["id"],
        "timestamp": row["timestamp"],
        "type": row["type"],
        "message": row["message"],
        "session_id": row["session_id"],
        "tags": loads(row["tags"]),
        "metadata": json.loads(row["metadata"]) if row["metadata"] else {},
    }


class WorkflowStore:
    """SQLite-backed storage for workflow tracking data (sessions + entries)."""

    def __init__(self):
        self.conn = get_connection()

    def load_sessions(self) -> dict[str, dict]:
        """Load all work sessions, keyed by id."""
        rows = self.conn.execute("SELECT * FROM sessions").fetchall()
        return {row["id"]: _session_row_to_dict(row) for row in rows}

    def load_entries(self) -> dict[str, dict]:
        """Load all log entries, keyed by id."""
        rows = self.conn.execute("SELECT * FROM entries").fetchall()
        return {row["id"]: _entry_row_to_dict(row) for row in rows}

    def get_current_session(self) -> Optional[dict]:
        """Get the current active session, freshly read from `sessions`."""
        row = self.conn.execute(
            "SELECT value FROM meta WHERE key = 'current_session_id'"
        ).fetchone()
        if not row or not row["value"]:
            return None
        session_row = self.conn.execute(
            "SELECT * FROM sessions WHERE id = ?", (row["value"],)
        ).fetchone()
        return _session_row_to_dict(session_row) if session_row else None

    def set_current_session(self, session: Optional[dict]):
        """Mark `session` (or None) as the active session."""
        session_id = session["id"] if session else None
        self.conn.execute(
            "INSERT INTO meta (key, value) VALUES ('current_session_id', ?) "
            "ON CONFLICT(key) DO UPDATE SET value = excluded.value",
            (session_id,),
        )
        self.conn.commit()

    def add_session(self, session: WorkSession):
        """Add a new session."""
        self.conn.execute(
            "INSERT INTO sessions (id, description, project, started_at, "
            "ended_at, summary, tags, duration_seconds) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (session.id, session.description, session.project, session.started_at,
             session.ended_at, session.summary, dumps(session.tags), session.duration_seconds),
        )
        self.conn.commit()

    def update_session(self, session_id: str, updates: dict):
        """Update an existing session."""
        if not updates:
            return
        columns = ", ".join(f"{k} = ?" for k in updates)
        values = list(updates.values()) + [session_id]
        self.conn.execute(f"UPDATE sessions SET {columns} WHERE id = ?", values)
        self.conn.commit()

    def add_entry(self, entry: LogEntry):
        """Add a new log entry, linked to the current session if one is active."""
        self.conn.execute(
            "INSERT INTO entries (id, timestamp, type, message, session_id, "
            "tags, metadata) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (entry.id, entry.timestamp, entry.type, entry.message, entry.session_id,
             dumps(entry.tags), json.dumps(entry.metadata or {})),
        )
        self.conn.commit()

    def get_sessions_in_range(self, start_date: str, end_date: str) -> list[dict]:
        """Get sessions within a date range (inclusive, YYYY-MM-DD)."""
        rows = self.conn.execute(
            "SELECT * FROM sessions WHERE substr(started_at, 1, 10) BETWEEN ? AND ? "
            "ORDER BY started_at",
            (start_date, end_date),
        ).fetchall()
        return [_session_row_to_dict(row) for row in rows]

    def get_entries_for_session(self, session_id: str) -> list[dict]:
        """Get all entries for a session, oldest first."""
        rows = self.conn.execute(
            "SELECT * FROM entries WHERE session_id = ? ORDER BY timestamp",
            (session_id,),
        ).fetchall()
        return [_entry_row_to_dict(row) for row in rows]


# Global store instance
_store: Optional[WorkflowStore] = None


def get_store() -> WorkflowStore:
    """Get the global workflow store instance."""
    global _store
    if _store is None:
        _store = WorkflowStore()
    return _store


# ============================================================================
# CLI Functions
# ============================================================================

def start_session(description: str, project: Optional[str] = None, tags: list[str] = None):
    """Start a new work session."""
    store = get_store()

    # Check if there's already an active session
    current = store.get_current_session()
    if current:
        log_warning(f"Session already active: {current['description']}")
        log_info("Use 'foreman track end' to end the current session first.")
        return

    # Create new session
    session = WorkSession(
        id=str(uuid.uuid4())[:8],
        description=description,
        project=project,
        started_at=get_timestamp(),
        tags=tags or []
    )

    store.add_session(session)
    store.set_current_session(asdict(session))

    console.print(Panel(
        f"[bold green]Session Started[/bold green]\n\n"
        f"📝 [bold]{description}[/bold]\n"
        f"🏷️  Project: {project or 'None'}\n"
        f"⏰ Started: {session.started_at}\n"
        f"🔑 ID: {session.id}",
        title="🚀 Work Session",
        border_style="green"
    ))

    log_success("Session started! Use 'foreman track log' to add entries.")


def end_session(summary: Optional[str] = None):
    """End the current work session."""
    store = get_store()

    current = store.get_current_session()
    if not current:
        log_warning("No active session to end.")
        return

    # Calculate duration
    started = datetime.fromisoformat(current["started_at"])
    ended = datetime.now()
    duration = (ended - started).total_seconds()

    # Get entries for this session
    entries = store.get_entries_for_session(current["id"])

    # Generate auto-summary if none provided
    if not summary:
        entry_counts = {}
        for entry in entries:
            etype = entry["type"]
            entry_counts[etype] = entry_counts.get(etype, 0) + 1

        parts = []
        if entry_counts.get("change", 0):
            parts.append(f"{entry_counts['change']} changes")
        if entry_counts.get("problem", 0):
            parts.append(f"{entry_counts['problem']} problems")
        if entry_counts.get("solution", 0):
            parts.append(f"{entry_counts['solution']} solutions")
        if entry_counts.get("note", 0):
            parts.append(f"{entry_counts['note']} notes")

        summary = ", ".join(parts) if parts else "Session completed"

    # Update session
    store.update_session(current["id"], {
        "ended_at": ended.isoformat(),
        "duration_seconds": duration,
        "summary": summary
    })

    store.set_current_session(None)

    console.print(Panel(
        f"[bold blue]Session Ended[/bold blue]\n\n"
        f"📝 {current['description']}\n"
        f"⏱️  Duration: {format_duration(duration)}\n"
        f"📊 {len(entries)} log entries\n"
        f"💬 Summary: {summary}",
        title="✅ Session Complete",
        border_style="blue"
    ))


def log_entry(message: str, log_type: str = "note"):
    """Log a change, problem, solution, or note."""
    store = get_store()

    current = store.get_current_session()

    # Create entry
    entry = LogEntry(
        id=str(uuid.uuid4())[:8],
        timestamp=get_timestamp(),
        type=log_type,
        message=message,
        session_id=current["id"] if current else None
    )

    store.add_entry(entry)

    icons = {
        "change": "🔄",
        "problem": "❌",
        "solution": "✅",
        "note": "📝"
    }

    icon = icons.get(log_type, "📝")
    log_success(f"{icon} [{log_type.upper()}] {message}")

    if not current:
        log_warning("No active session - entry logged without session context")


def show_status():
    """Show current session status."""
    store = get_store()

    current = store.get_current_session()
    if not current:
        console.print(Panel(
            "[dim]No active session[/dim]\n\n"
            "Start a new session with:\n"
            "[bold]foreman track start \"Description\"[/bold]",
            title="📋 Status",
            border_style="dim"
        ))
        return

    # Calculate elapsed time
    started = datetime.fromisoformat(current["started_at"])
    elapsed = (datetime.now() - started).total_seconds()

    # Get entries
    entries = store.get_entries_for_session(current["id"])

    # Build entry summary
    entry_lines = []
    for entry in entries[-5:]:  # Show last 5
        icons = {"change": "🔄", "problem": "❌", "solution": "✅", "note": "📝"}
        icon = icons.get(entry["type"], "📝")
        time = entry["timestamp"][11:16]  # HH:MM
        entry_lines.append(f"  {icon} [{time}] {entry['message'][:50]}")

    console.print(Panel(
        f"[bold green]● Active Session[/bold green]\n\n"
        f"📝 {current['description']}\n"
        f"🏷️  Project: {current.get('project') or 'None'}\n"
        f"⏱️  Elapsed: {format_duration(elapsed)}\n"
        f"📊 Entries: {len(entries)}\n\n"
        f"[bold]Recent entries:[/bold]\n" + ("\n".join(entry_lines) if entry_lines else "  [dim]None yet[/dim]"),
        title="📋 Current Session",
        border_style="green"
    ))


def show_history(days: int = 7):
    """Show session history for the past N days."""
    store = get_store()

    end_date = get_date()
    start_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")

    sessions = store.get_sessions_in_range(start_date, end_date)

    if not sessions:
        log_info(f"No sessions found in the last {days} days.")
        return

    table = Table(title=f"📅 Work Sessions (Last {days} Days)")
    table.add_column("Date", style="cyan")
    table.add_column("Duration", style="green")
    table.add_column("Description")
    table.add_column("Project", style="yellow")
    table.add_column("Entries", style="magenta")

    for session in sessions:
        date = session["started_at"][:10]
        duration = format_duration(session.get("duration_seconds", 0))
        entries = store.get_entries_for_session(session["id"])

        table.add_row(
            date,
            duration if session.get("ended_at") else "[dim]ongoing[/dim]",
            session["description"][:40],
            session.get("project") or "-",
            str(len(entries))
        )

    console.print(table)

    # Summary stats
    total_time = sum(s.get("duration_seconds", 0) for s in sessions if s.get("ended_at"))
    console.print(f"\n[bold]Total tracked time:[/bold] {format_duration(total_time)}")


# ============================================================================
# Export Functions (for Report Agent)
# ============================================================================

def get_sessions_for_date(date: str) -> list[dict]:
    """Get all sessions for a specific date."""
    store = get_store()
    return store.get_sessions_in_range(date, date)


def get_sessions_for_week(week_start: str) -> list[dict]:
    """Get all sessions for a week starting from the given date."""
    store = get_store()
    start = datetime.fromisoformat(week_start)
    end = start + timedelta(days=6)
    return store.get_sessions_in_range(week_start, end.strftime("%Y-%m-%d"))


def get_all_entries_for_sessions(sessions: list[dict]) -> list[dict]:
    """Get all log entries for a list of sessions."""
    store = get_store()
    entries = []
    for session in sessions:
        entries.extend(store.get_entries_for_session(session["id"]))
    return entries


def export_session_data(session_id: str) -> dict:
    """Export full session data including entries."""
    store = get_store()
    sessions = store.load_sessions()

    if session_id not in sessions:
        return {}

    session = sessions[session_id]
    session["entry_details"] = store.get_entries_for_session(session_id)
    return session
