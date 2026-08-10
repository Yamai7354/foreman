"""Smoke tests for the foreman CLI."""

from click.testing import CliRunner

from tools.cli import main


def test_root_help() -> None:
    runner = CliRunner()
    result = runner.invoke(main, ["--help"])
    assert result.exit_code == 0
    assert "Usage:" in result.output
    assert "Commands:" in result.output


def test_core_groups_available() -> None:
    runner = CliRunner()
    result = runner.invoke(main, ["--help"])
    assert result.exit_code == 0
    for command in ("docs", "diagram", "github", "track", "report", "config"):
        assert command in result.output
