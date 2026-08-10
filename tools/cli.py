"""
Main CLI entry point for Foreman.

Usage:
    foreman [COMMAND] [OPTIONS]

Commands:
    docs      - Documentation generation tools
    diagram   - Diagram generation tools
    github    - GitHub repository management
    track     - Workflow and session tracking
    report    - Generate reports
    autolog   - Cross-project error/fix/change logging
    config    - Configuration management
"""

import click
from rich.console import Console
from rich.panel import Panel

from .auto_logger import cli_main as autolog_cli
from .code_watcher import cli_main as codewatch_cli
from .utils import log_info, log_success, log_error

console = Console()


@click.group()
@click.version_option(version="1.0.0", prog_name="foreman")
def main():
    """
    🚧 Foreman - Your complete toolkit for managing developer projects.

    Documentation, diagrams, GitHub integration, and workflow tracking.
    """
    pass


# ============================================================================
# Documentation Commands
# ============================================================================

@main.group()
def docs():
    """📝 Documentation generation tools."""
    pass


@docs.command("generate")
@click.argument("project_path", type=click.Path(exists=True))
@click.option("--output", "-o", type=click.Path(), help="Output path for generated docs")
@click.option("--format", "-f", type=click.Choice(["md", "html"]), default="md", help="Output format")
def docs_generate(project_path, output, format):
    """Generate documentation for a project."""
    from .doc_generator import generate_documentation
    generate_documentation(project_path, output, format)


@docs.command("readme")
@click.argument("project_path", type=click.Path(exists=True))
@click.option("--template", "-t", type=str, default="default", help="README template to use")
def docs_readme(project_path, template):
    """Generate a README.md for a project."""
    from .doc_generator import generate_readme
    generate_readme(project_path, template)


@docs.command("api")
@click.argument("project_path", type=click.Path(exists=True))
@click.option("--output", "-o", type=click.Path(), help="Output path for API docs")
def docs_api(project_path, output):
    """Extract API documentation from code."""
    from .doc_generator import generate_api_docs
    generate_api_docs(project_path, output)


# ============================================================================
# Diagram Commands
# ============================================================================

@main.group()
def diagram():
    """📊 Diagram generation tools."""
    pass


@diagram.command("architecture")
@click.argument("project_path", type=click.Path(exists=True))
@click.option("--output", "-o", type=click.Path(), help="Output file path")
@click.option("--format", "-f", type=click.Choice(["mermaid", "svg", "png"]), default="mermaid")
def diagram_architecture(project_path, output, format):
    """Generate architecture diagram from project structure."""
    from .diagram_generator import generate_architecture_diagram
    generate_architecture_diagram(project_path, output, format)


@diagram.command("flowchart")
@click.argument("file_path", type=click.Path(exists=True))
@click.option("--output", "-o", type=click.Path(), help="Output file path")
@click.option("--function", "-fn", type=str, help="Specific function to diagram")
def diagram_flowchart(file_path, output, function):
    """Generate flowchart from code logic."""
    from .diagram_generator import generate_flowchart
    generate_flowchart(file_path, output, function)


@diagram.command("classes")
@click.argument("project_path", type=click.Path(exists=True))
@click.option("--output", "-o", type=click.Path(), help="Output file path")
def diagram_classes(project_path, output):
    """Generate class diagram from project."""
    from .diagram_generator import generate_class_diagram
    generate_class_diagram(project_path, output)


# ============================================================================
# GitHub Commands
# ============================================================================

@main.group()
def github():
    """🐙 GitHub repository management."""
    pass


@github.command("init")
@click.argument("project_path", type=click.Path())
@click.option("--name", "-n", type=str, help="Repository name")
@click.option("--description", "-d", type=str, help="Repository description")
@click.option("--private", is_flag=True, help="Create as private repository")
@click.option("--template", "-t", type=str, default="default", help="Project template to use")
def github_init(project_path, name, description, private, template):
    """Initialize a new GitHub repository."""
    from .github_manager import init_repository
    init_repository(project_path, name, description, private, template)


@github.command("gitignore")
@click.argument("project_path", type=click.Path(exists=True))
@click.option("--type", "-t", "project_type", type=str, help="Project type (auto-detected if not specified)")
def github_gitignore(project_path, project_type):
    """Generate .gitignore for project."""
    from .github_manager import generate_gitignore
    generate_gitignore(project_path, project_type)


@github.command("actions")
@click.argument("project_path", type=click.Path(exists=True))
@click.option("--workflow", "-w", type=click.Choice(["ci", "deploy", "test"]), default="ci")
def github_actions(project_path, workflow):
    """Add GitHub Actions workflow."""
    from .github_manager import add_github_action
    add_github_action(project_path, workflow)


# ============================================================================
# Workflow Tracking Commands
# ============================================================================

@main.group()
def track():
    """📋 Workflow and session tracking."""
    pass


@track.command("start")
@click.argument("description")
@click.option("--project", "-p", type=str, help="Project name")
@click.option("--tags", "-t", multiple=True, help="Tags for this session")
def track_start(description, project, tags):
    """Start a new work session."""
    from .workflow_tracker import start_session
    start_session(description, project, list(tags))


@track.command("end")
@click.option("--summary", "-s", type=str, help="Session summary")
def track_end(summary):
    """End current work session."""
    from .workflow_tracker import end_session
    end_session(summary)


@track.command("log")
@click.argument("message")
@click.option("--type", "-t", "log_type", type=click.Choice(["change", "problem", "solution", "note"]), default="note")
def track_log(message, log_type):
    """Log a change, problem, or note."""
    from .workflow_tracker import log_entry
    log_entry(message, log_type)


@track.command("status")
def track_status():
    """Show current session status."""
    from .workflow_tracker import show_status
    show_status()


@track.command("history")
@click.option("--days", "-d", type=int, default=7, help="Number of days to show")
def track_history(days):
    """Show session history."""
    from .workflow_tracker import show_history
    show_history(days)


# ============================================================================
# Report Commands
# ============================================================================

@main.group()
def report():
    """📈 Report generation."""
    pass


@report.command("daily")
@click.option("--date", "-d", type=str, help="Date for report (YYYY-MM-DD)")
@click.option("--output", "-o", type=click.Path(), help="Output file path")
def report_daily(date, output):
    """Generate daily report."""
    from .report_agent import generate_daily_report
    generate_daily_report(date, output)


@report.command("weekly")
@click.option("--week", "-w", type=str, help="Week start date (YYYY-MM-DD)")
@click.option("--output", "-o", type=click.Path(), help="Output file path")
def report_weekly(week, output):
    """Generate weekly report."""
    from .report_agent import generate_weekly_report
    generate_weekly_report(week, output)


@report.command("project")
@click.argument("project_name")
@click.option("--output", "-o", type=click.Path(), help="Output file path")
def report_project(project_name, output):
    """Generate project status report."""
    from .report_agent import generate_project_report
    generate_project_report(project_name, output)


# ============================================================================
# Config Commands
# ============================================================================

@main.group()
def config():
    """⚙️ Configuration management."""
    pass


@config.command("show")
def config_show():
    """Show current configuration."""
    from .config import get_config
    cfg = get_config()
    console.print(Panel(
        f"[bold]Project Root:[/bold] {cfg.project_root}\n"
        f"[bold]Author:[/bold] {cfg.author_name}\n"
        f"[bold]GitHub User:[/bold] {cfg.github_username or 'Not set'}\n"
        f"[bold]LLM Enabled:[/bold] {cfg.llm_enabled}\n"
        f"[bold]LLM URL:[/bold] {cfg.llm_base_url}",
        title="⚙️ Configuration",
        border_style="blue"
    ))


@config.command("set")
@click.argument("key")
@click.argument("value")
def config_set(key, value):
    """Set a configuration value and persist it to config.yaml."""
    from .config import get_config

    cfg = get_config()
    settable_keys = {"github_username", "author_name", "author_email",
                      "llm_enabled", "llm_base_url", "llm_model"}

    if key not in settable_keys:
        log_error(f"Unknown or non-settable config key: {key}")
        log_info(f"Settable keys: {', '.join(sorted(settable_keys))}")
        return

    if key == "llm_enabled":
        value = value.strip().lower() in ("true", "1", "yes", "on")

    setattr(cfg, key, value)
    cfg.save(cfg.project_root / "config.yaml")
    log_success(f"Set {key} = {value}")


# ============================================================================
# Auto-Logger Commands
# ============================================================================

main.add_command(autolog_cli, name="autolog")


# ============================================================================
# Code Watcher Commands
# ============================================================================

main.add_command(codewatch_cli, name="codewatch")


if __name__ == "__main__":
    main()
