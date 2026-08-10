"""
Report Agent - Generate comprehensive reports from workflow tracking data.

This module aggregates work sessions, changes, problems, and solutions into
easy-to-read reports. Optionally uses an LLM to generate natural summaries.
"""

from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel

from .config import get_config
from .utils import format_duration, get_date, log_info, log_success, log_warning
from .workflow_tracker import (
    get_all_entries_for_sessions,
    get_sessions_for_date,
    get_sessions_for_week,
    get_store,
)

console = Console()


# ============================================================================
# LLM Integration (Optional)
# ============================================================================

def call_llm(prompt: str) -> Optional[str]:
    """Call the local LLM to generate a summary."""
    config = get_config()

    if not config.llm_enabled:
        return None

    try:
        import requests

        response = requests.post(
            f"{config.llm_base_url}/chat/completions",
            json={
                "model": config.llm_model,
                "messages": [
                    {"role": "system", "content": "You are a concise report writer. Summarize the provided work data into a brief, professional summary. Focus on accomplishments, problems solved, and key progress."},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.7,
                "max_tokens": 500
            },
            timeout=30
        )

        if response.status_code == 200:
            return response.json()["choices"][0]["message"]["content"]
    except Exception as e:
        log_warning(f"LLM unavailable: {e}")

    return None


# ============================================================================
# Report Templates
# ============================================================================

def generate_markdown_report(
    title: str,
    subtitle: str,
    sessions: list[dict],
    entries: list[dict],
    llm_summary: Optional[str] = None
) -> str:
    """Generate a markdown report from session and entry data."""

    lines = [
        f"# {title}",
        f"*{subtitle}*",
        "",
    ]

    # LLM Summary (if available)
    if llm_summary:
        lines.extend([
            "## 🤖 AI Summary",
            "",
            llm_summary,
            "",
        ])

    # Overview stats
    total_time = sum(s.get("duration_seconds", 0) for s in sessions if s.get("ended_at"))
    total_sessions = len(sessions)

    # Count entry types
    changes = [e for e in entries if e["type"] == "change"]
    problems = [e for e in entries if e["type"] == "problem"]
    solutions = [e for e in entries if e["type"] == "solution"]
    notes = [e for e in entries if e["type"] == "note"]

    lines.extend([
        "## 📊 Overview",
        "",
        "| Metric | Value |",
        "|--------|-------|",
        f"| Total Sessions | {total_sessions} |",
        f"| Total Time | {format_duration(total_time)} |",
        f"| Changes Made | {len(changes)} |",
        f"| Problems Encountered | {len(problems)} |",
        f"| Solutions Found | {len(solutions)} |",
        f"| Notes Logged | {len(notes)} |",
        "",
    ])

    # Sessions detail
    if sessions:
        lines.extend([
            "## 📅 Sessions",
            "",
        ])

        for session in sessions:
            started = session["started_at"][:16].replace("T", " ")
            duration = format_duration(session.get("duration_seconds", 0)) if session.get("ended_at") else "ongoing"
            project = session.get("project") or "General"

            lines.extend([
                f"### {session['description']}",
                f"- **Project**: {project}",
                f"- **Started**: {started}",
                f"- **Duration**: {duration}",
                "",
            ])

            if session.get("summary"):
                lines.append(f"*{session['summary']}*")
                lines.append("")

    # Changes made
    if changes:
        lines.extend([
            "## 🔄 Changes Made",
            "",
        ])
        for change in changes:
            time = change["timestamp"][11:16]
            lines.append(f"- [{time}] {change['message']}")
        lines.append("")

    # Problems and solutions
    if problems or solutions:
        lines.extend([
            "## ❌ Problems & ✅ Solutions",
            "",
        ])

        # Try to pair problems with solutions
        for problem in problems:
            time = problem["timestamp"][11:16]
            lines.append(f"- ❌ [{time}] **Problem**: {problem['message']}")

        for solution in solutions:
            time = solution["timestamp"][11:16]
            lines.append(f"- ✅ [{time}] **Solution**: {solution['message']}")

        lines.append("")

    # Notes
    if notes:
        lines.extend([
            "## 📝 Notes",
            "",
        ])
        for note in notes:
            time = note["timestamp"][11:16]
            lines.append(f"- [{time}] {note['message']}")
        lines.append("")

    # Footer
    lines.extend([
        "---",
        f"*Generated by Foreman on {get_date()}*"
    ])

    return "\n".join(lines)


# ============================================================================
# CLI Functions
# ============================================================================

def generate_daily_report(date: Optional[str] = None, output: Optional[str] = None):
    """Generate a daily work report."""
    target_date = date or get_date()

    log_info(f"Generating daily report for {target_date}...")

    # Get data
    sessions = get_sessions_for_date(target_date)
    entries = get_all_entries_for_sessions(sessions)

    if not sessions:
        log_warning(f"No sessions found for {target_date}")
        return

    # Try LLM summary
    llm_summary = None
    if sessions:
        prompt = f"""Summarize this day's work (keep it brief, 2-3 sentences):

Date: {target_date}
Sessions: {len(sessions)}
Total changes: {len([e for e in entries if e['type'] == 'change'])}
Problems: {len([e for e in entries if e['type'] == 'problem'])}
Solutions: {len([e for e in entries if e['type'] == 'solution'])}

Session descriptions:
{chr(10).join(f'- {s["description"]}' for s in sessions)}

Key changes:
{chr(10).join(f'- {e["message"]}' for e in entries if e["type"] == "change")[:500]}
"""
        llm_summary = call_llm(prompt)

    # Generate report
    report = generate_markdown_report(
        title=f"📅 Daily Report - {target_date}",
        subtitle=f"Work completed on {target_date}",
        sessions=sessions,
        entries=entries,
        llm_summary=llm_summary
    )

    # Save or display
    if output:
        output_path = Path(output)
    else:
        config = get_config()
        output_path = config.reports_dir / f"daily_{target_date}.md"

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(report, encoding="utf-8")

    log_success(f"Report saved to: {output_path}")

    # Also display
    console.print(Panel(Markdown(report), title="📅 Daily Report", border_style="blue"))


def generate_weekly_report(week_start: Optional[str] = None, output: Optional[str] = None):
    """Generate a weekly work report."""
    if week_start:
        start_date = week_start
    else:
        # Default to current week starting Monday
        today = datetime.now()
        monday = today - timedelta(days=today.weekday())
        start_date = monday.strftime("%Y-%m-%d")

    end_date = (datetime.strptime(start_date, "%Y-%m-%d") + timedelta(days=6)).strftime("%Y-%m-%d")

    log_info(f"Generating weekly report for {start_date} to {end_date}...")

    # Get data
    sessions = get_sessions_for_week(start_date)
    entries = get_all_entries_for_sessions(sessions)

    if not sessions:
        log_warning(f"No sessions found for week of {start_date}")
        return

    # Try LLM summary
    llm_summary = None
    if sessions:
        prompt = f"""Summarize this week's work (keep it brief, 3-4 sentences):

Week: {start_date} to {end_date}
Total sessions: {len(sessions)}
Total changes: {len([e for e in entries if e['type'] == 'change'])}
Problems encountered: {len([e for e in entries if e['type'] == 'problem'])}
Solutions found: {len([e for e in entries if e['type'] == 'solution'])}

Session descriptions:
{chr(10).join(f'- {s["description"]}' for s in sessions)}

Key accomplishments (from change logs):
{chr(10).join(f'- {e["message"]}' for e in entries if e["type"] == "change")[:800]}

Problems solved:
{chr(10).join(f'- {e["message"]}' for e in entries if e["type"] == "solution")[:400]}
"""
        llm_summary = call_llm(prompt)

    # Generate report
    report = generate_markdown_report(
        title="📊 Weekly Report",
        subtitle=f"Work completed from {start_date} to {end_date}",
        sessions=sessions,
        entries=entries,
        llm_summary=llm_summary
    )

    # Save or display
    if output:
        output_path = Path(output)
    else:
        config = get_config()
        output_path = config.reports_dir / f"weekly_{start_date}.md"

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(report, encoding="utf-8")

    log_success(f"Report saved to: {output_path}")

    # Also display
    console.print(Panel(Markdown(report), title="📊 Weekly Report", border_style="green"))


def generate_project_report(project_name: str, output: Optional[str] = None):
    """Generate a project-specific report."""
    log_info(f"Generating report for project: {project_name}...")

    store = get_store()
    all_sessions = store.load_sessions()

    # Filter sessions by project
    project_sessions = [
        s for s in all_sessions.values()
        if s.get("project") and project_name.lower() in s["project"].lower()
    ]

    if not project_sessions:
        log_warning(f"No sessions found for project: {project_name}")
        return

    # Sort by date
    project_sessions.sort(key=lambda x: x["started_at"])

    entries = get_all_entries_for_sessions(project_sessions)

    # Try LLM summary
    llm_summary = None
    prompt = f"""Summarize work on project "{project_name}" (keep it brief, 3-4 sentences):

Total sessions: {len(project_sessions)}
Date range: {project_sessions[0]['started_at'][:10]} to {project_sessions[-1]['started_at'][:10]}
Total changes: {len([e for e in entries if e['type'] == 'change'])}
Problems solved: {len([e for e in entries if e['type'] == 'solution'])}

Session descriptions:
{chr(10).join(f'- {s["description"]}' for s in project_sessions[-10:])}

Key changes:
{chr(10).join(f'- {e["message"]}' for e in entries if e["type"] == "change")[:600]}
"""
    llm_summary = call_llm(prompt)

    # Generate report
    report = generate_markdown_report(
        title=f"🏗️ Project Report: {project_name}",
        subtitle=f"All work completed on {project_name}",
        sessions=project_sessions,
        entries=entries,
        llm_summary=llm_summary
    )

    # Save or display
    if output:
        output_path = Path(output)
    else:
        config = get_config()
        safe_name = project_name.lower().replace(" ", "_")
        output_path = config.reports_dir / f"project_{safe_name}.md"

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(report, encoding="utf-8")

    log_success(f"Report saved to: {output_path}")

    # Also display
    console.print(Panel(Markdown(report), title=f"🏗️ Project: {project_name}", border_style="yellow"))
