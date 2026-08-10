# data

Runtime data for Foreman lives in `foreman.db` — a SQLite database holding
work sessions and log entries (see `tools/db.py` for the schema). It's
gitignored since it's per-installation data, not part of the codebase.

Previously this directory held raw `.json` files directly, which meant
real work-session history could accidentally end up committed if the
`.gitignore` entry was ever missed. The database keeps that data properly
contained to one file that's ignored by default.
