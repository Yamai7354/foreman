# foreman (Codex)

When working in this repo, follow these instructions.

## Project

- **Purpose:** Foreman CLI — documentation, diagrams, GitHub setup, and workflow tracking.
- **Layout:** Follow [docs/PROJECT_STRUCTURE.md](../docs/PROJECT_STRUCTURE.md). Do not copy `agent.py` / `planner.py` / `memory.py` / `tool_router.py` / `main.py` into every folder; app code lives in the `tools/` package only.

## Setup

- Install editable: `pip install -e .`
- Config: root `config.yaml` and `.env` for secrets.

## Commands (foreman CLI)

- **Track:** `foreman track start "…" --project "…"` → `foreman track log "…"` → `foreman track end`; `foreman track status`
- **Reports:** `foreman report daily` | `foreman report weekly`
- **Docs:** `foreman docs generate [PROJECT_PATH] [OUTPUT_PATH] [FORMAT]`; `foreman docs readme`; `foreman docs api`
- **Diagrams:** `foreman diagram architecture|classes [PROJECT_PATH] [OUTPUT_PATH] [FORMAT]`
- **GitHub:** `foreman github init [PROJECT_PATH] [NAME] [DESCRIPTION]`

## Codebase

- **Entry point:** `tools.cli:main` (see `pyproject.toml`).
- **Package:** Only `tools*` is the installable package; `data/`, `reports/`, `docs/`, `website/`, `templates/` are content or output dirs, not Python packages.
- **Config:** `tools/config.py` loads root `config.yaml` and `.env`; paths like `data_dir`, `reports_dir` point at those folders.

When adding features, add modules under `tools/` and register commands in `tools/cli.py`; do not add new top-level packages or duplicate the agent/planner/memory stack in other directories.
