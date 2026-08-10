# foreman

Project layout follows [docs/PROJECT_STRUCTURE.md](docs/PROJECT_STRUCTURE.md). Do not copy agent/planner/memory/tool_router/main into every folder.  
**Codex:** Same instructions are in [.codex/AGENTS.md](.codex/AGENTS.md) for OpenAI Codex.

## Purpose
Foreman CLI for documentation, diagrams, GitHub setup, and workflow tracking.

## Setup
- Install editable: `pip install -e .`

## Workflows
- Start a work session, log changes, end, and generate reports with `foreman` CLI.
- Configure defaults in `config.yaml`.
- Generate project documentation and diagrams automatically for any python project.

## Commands
### Tracking and Reporting
- `foreman track start "Building new feature" --project "MyProject"`
- `foreman track log "Added authentication module" --type change`
- `foreman track end`
- `foreman track status`
- `foreman report daily`
- `foreman report weekly`

### Documentation and Diagrams
- `foreman docs generate [PROJECT_PATH] [OUTPUT_PATH] [FORMAT]`
- `foreman diagram architecture [PROJECT_PATH] [OUTPUT_PATH] [FORMAT]`
- `foreman diagram classes [PROJECT_PATH] [OUTPUT_PATH]`

### GitHub
- `foreman github init [PROJECT_PATH] [NAME] [DESCRIPTION]`
