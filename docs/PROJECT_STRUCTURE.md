# Project filesystem template

Canonical layout for this repo and for new projects. Avoid copying the same boilerplate into every folder.

## Root


| File / folder    | Purpose                                          |
| ---------------- | ------------------------------------------------ |
| `README.md`      | Project overview and how to run it.              |
| `AGENTS.md`      | AI/agent instructions and CLI usage (optional).  |
| `pyproject.toml` | Python package metadata, deps, and entry points. |
| `config.yaml`    | App config (optional; can use env only).         |
| `.env`           | Secrets and env-only config (gitignored).        |
| `.venv/`         | Virtualenv only — no app code or placeholders.   |


## One main package

- Put all app code in a single top-level package (e.g. `tools/`).
- Entry point: define in `pyproject.toml` (e.g. `foreman = "tools.cli:main"`).
- Do **not** add `main.py`, `agent.py`, `planner.py`, `memory.py`, `tool_router.py` to every folder; add them only where that module is actually implemented and used.

## Feature / output directories

Use these for **content or output**, not for duplicate Python stacks:


| Folder       | Use for                                               |
| ------------ | ----------------------------------------------------- |
| `data/`      | Input data, caches, or generated data.                |
| `reports/`   | Generated report artifacts (e.g. daily/weekly).       |
| `docs/`      | Markdown and generated docs (e.g. API, architecture). |
| `website/`   | Static site or front-end assets.                      |
| `templates/` | Jinja/HTML/text templates.                            |


- No need for `requirements.txt`, `config.yaml`, or placeholder `.py` files in these unless that folder is a real Python package.
- A short `README.md` per folder is optional (e.g. “Generated reports go here”).

## Special directories


| Folder     | Use for                                   |
| ---------- | ----------------------------------------- |
| `.agent/`  | Agent workflows and prompts only.         |
| `.github/` | GitHub Actions workflows and repo config. |


## Template checklist for new projects

1. Root: `README.md`, `pyproject.toml`, optional `config.yaml` and `.env`.
2. One main package with real modules and a single CLI entry point.
3. Feature dirs (`data`, `reports`, `docs`, `website`, `templates`) — empty or content only, no boilerplate copies.
4. No `agent.py` / `planner.py` / `memory.py` / `tool_router.py` / `main.py` in every folder; only where that logic lives.

