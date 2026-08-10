"""
SQLite connection and schema for Foreman's workflow tracking data.
Replaces the old data/*.json files (which lived in a folder easy to
gitignore or lose track of) with a real, queryable database.
"""
import json
import sqlite3
from pathlib import Path

from .config import get_config

_SCHEMA = """
CREATE TABLE IF NOT EXISTS sessions (
    id               TEXT PRIMARY KEY,
    description      TEXT NOT NULL,
    project          TEXT,
    started_at       TEXT NOT NULL,
    ended_at         TEXT,
    summary          TEXT,
    tags             TEXT NOT NULL DEFAULT '[]',
    duration_seconds REAL NOT NULL DEFAULT 0.0
);

CREATE TABLE IF NOT EXISTS entries (
    id         TEXT PRIMARY KEY,
    timestamp  TEXT NOT NULL,
    type       TEXT NOT NULL,
    message    TEXT NOT NULL,
    session_id TEXT REFERENCES sessions(id) ON DELETE SET NULL,
    tags       TEXT NOT NULL DEFAULT '[]',
    metadata   TEXT NOT NULL DEFAULT '{}'
);
CREATE INDEX IF NOT EXISTS idx_entries_session ON entries(session_id);
CREATE INDEX IF NOT EXISTS idx_sessions_started ON sessions(started_at);

CREATE TABLE IF NOT EXISTS meta (
    key   TEXT PRIMARY KEY,
    value TEXT
);
"""


def get_db_path() -> Path:
    return get_config().data_dir / "foreman.db"


def get_connection() -> sqlite3.Connection:
    db_path = get_db_path()
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    conn.executescript(_SCHEMA)
    return conn


def dumps(value) -> str:
    return json.dumps(value if value is not None else [])


def loads(value: str):
    return json.loads(value) if value else []
