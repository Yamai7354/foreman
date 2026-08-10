# 🚧 Foreman

A CLI toolkit for developers who juggle a lot of projects: track work sessions
as you go, auto-generate docs and architecture diagrams from your codebase,
scaffold new GitHub repos, and turn tracked work into daily/weekly reports —
all from one command.

## Why

Most of this exists because remembering *what you actually did* across a
dozen side projects is harder than doing the work itself. Foreman logs it as
you go, so a report is a command away instead of an evening of git-log
archaeology.

## Features

- **📋 Workflow tracking** — start/end work sessions, log changes/problems/solutions as you go, see history and elapsed time
- **📈 Reports** — daily, weekly, and per-project reports generated from tracked sessions, with optional LLM-written summaries
- **📝 Documentation** — auto-generate a project overview, API reference, and README from a Python codebase
- **📊 Diagrams** — Mermaid architecture and class diagrams generated straight from your code
- **🐙 GitHub setup** — initialize a repo, generate a `.gitignore` for your stack, add CI/CD workflow templates
- **🔍 Cross-project logging** — `autolog` and `codewatch` track errors/fixes/changes and optionally flag code issues via a local LLM, across *all* your projects, not just one

All tracked data lives in a single SQLite database (`data/foreman.db`), not
loose JSON files — so it's queryable, and it's never something you can
accidentally leave un-gitignored.

## Install

```bash
git clone https://github.com/<your-username>/foreman.git
cd foreman
pip install -e .
```

Copy `config.yaml.example` to `config.yaml` and fill in your GitHub username
and (optionally) a local LLM endpoint for AI-written summaries. Everything
works without an LLM configured — you just get plain generated summaries
instead of AI-written ones.

## Quick start

```bash
# Track a work session
foreman track start "Building the export feature" --project "MyProject"
foreman track log "Added CSV export" --type change
foreman track log "Export was missing the header row" --type problem
foreman track log "Fixed by initializing the writer with fieldnames" --type solution
foreman track end

# Turn it into a report
foreman report daily

# Generate docs + diagrams for any Python project
foreman docs generate ./my-project --output docs
foreman diagram architecture ./my-project --output docs/architecture.md

# Scaffold a new GitHub repo
foreman github init ./my-project "my-project" "A thing I'm building"
```

## Command reference

### Tracking & reports
| Command | What it does |
|---|---|
| `foreman track start "desc" [--project NAME] [--tags TAG]` | Start a work session |
| `foreman track log "message" [--type change\|problem\|solution\|note]` | Log an entry to the active session |
| `foreman track status` | Show the active session and recent entries |
| `foreman track end [--summary "..."]` | End the active session |
| `foreman track history [--days N]` | Show past sessions |
| `foreman report daily [--date YYYY-MM-DD]` | Generate a daily report |
| `foreman report weekly [--week YYYY-MM-DD]` | Generate a weekly report |
| `foreman report project "NAME"` | Generate a report for one project |

### Docs & diagrams
| Command | What it does |
|---|---|
| `foreman docs generate PATH [--output DIR] [--format md\|html]` | Overview + API docs for a project |
| `foreman docs readme PATH` | Generate a README.md |
| `foreman docs api PATH` | Extract just the API reference |
| `foreman diagram architecture PATH [--output FILE]` | Mermaid architecture diagram |
| `foreman diagram classes PATH [--output FILE]` | Mermaid class diagram |

### GitHub
| Command | What it does |
|---|---|
| `foreman github init PATH NAME DESCRIPTION` | Init git, generate `.gitignore`, first commit |
| `foreman github gitignore PATH PROJECT_TYPE` | Generate a `.gitignore` for a stack |
| `foreman github actions PATH WORKFLOW` | Add a CI/CD workflow template |

### Config & cross-project logging
| Command | What it does |
|---|---|
| `foreman config show` | Show current configuration |
| `foreman config set KEY VALUE` | Update and persist a config value |
| `autolog error\|fix\|change "message"` | Log from any project directory |
| `autolog list` / `autolog report` | View/report on cross-project logs |
| `codewatch start [--crawl]` | Watch a project for changes, flag issues via local LLM |

## Configuration

`config.yaml` (gitignored — copy from `config.yaml.example`):

| Key | Purpose |
|---|---|
| `github_username` | Used when scaffolding repos |
| `author_name` / `author_email` | Used in generated docs/reports |
| `llm_enabled` | Turn AI-written summaries on/off |
| `llm_base_url` / `llm_model` | Local LLM endpoint (OpenAI-compatible API) for report/autolog/codewatch summaries |

## License

MIT
