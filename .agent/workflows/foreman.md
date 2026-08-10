---
description: Foreman - Documentation, diagrams, GitHub, and workflow tools
---

# Foreman Workflow

This workflow provides commands for managing your projects and tracking your development work.

## Quick Start

### Start Tracking Your Work

```bash
# Start a work session
foreman track start "Working on [description]" --project "[project-name]"

# Log changes as you work
foreman track log "Added new feature X" --type change
foreman track log "Fixed bug in Y" --type change
foreman track log "Module doesn't load correctly" --type problem
foreman track log "Fixed by updating import path" --type solution

# Check your current session
foreman track status

# End your session
foreman track end --summary "Completed feature X and fixed bug Y"
```

### Generate Reports

```bash
# Daily report (today by default)
foreman report daily

# Weekly report (current week by default)
foreman report weekly

# Project-specific report
foreman report project "Foreman"
```

// turbo

### View History

```bash
foreman track history --days 7
```

## Full Command Reference

### Tracking Commands

- `foreman track start "description"` - Start a new work session
  - `--project/-p` - Associate with a project
  - `--tags/-t` - Add tags (can use multiple times)
- `foreman track end` - End current session
  - `--summary/-s` - Add a summary of what was done
- `foreman track log "message"` - Log an entry
  - `--type/-t` - Type: change, problem, solution, note (default: note)
- `foreman track status` - Show current session
- `foreman track history` - Show past sessions
  - `--days/-d` - Number of days to show (default: 7)

### Report Commands

- `foreman report daily` - Generate daily report
  - `--date/-d` - Specific date (YYYY-MM-DD)
  - `--output/-o` - Custom output path
- `foreman report weekly` - Generate weekly report
  - `--week/-w` - Week start date
  - `--output/-o` - Custom output path
- `foreman report project "name"` - Generate project report
  - `--output/-o` - Custom output path

### Documentation Commands

- `foreman docs generate <path> --output <dir> --format [md|html]` - Auto-generate API documentation and project overview
- `foreman docs readme <path> --template <template_path>` - Generate README.md

### Diagram Commands

- `foreman diagram architecture <path> --output <file> --format [mermaid|svg|png]` - Generate architecture diagram
- `foreman diagram flowchart <file> --output <file>` - Generate flowchart from code
- `foreman diagram classes <path> --output <file>` - Generate class diagram

### GitHub Commands

- `foreman github init <path> <name> <description>` - Initialize GitHub repository
- `foreman github gitignore <path> <project_type>` - Generate .gitignore
- `foreman github actions <path> <workflow_file>` - Add GitHub Actions workflow

### Configuration

- `foreman config show` - Show current configuration
- `foreman config set <key> <value>` - Update configuration

## Tips

1. **Always start a session** before beginning work so changes are properly tracked
2. **Log frequently** - small, specific logs are better than one big summary
3. **Use problem/solution pairs** - this helps build a knowledge base
4. **Generate reports** at end of day/week to maintain documentation
