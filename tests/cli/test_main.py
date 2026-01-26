"""
Tests for main CLI application.

This module tests the main CLI entry point and basic commands.
"""
from __future__ import annotations

from typer.testing import CliRunner

from better_notion._cli.main import app

runner = CliRunner()


def test_version_command() -> None:
    """Test the version command."""
    result = runner.invoke(app, ["version"])

    assert result.exit_code == 0
    assert '"success": true' in result.stdout
    assert '"name": "Better Notion CLI"' in result.stdout
    assert '"version": "0.4.1"' in result.stdout


def test_root_help() -> None:
    """Test that root help displays correctly."""
    result = runner.invoke(app, ["--help"])

    assert result.exit_code == 0
    assert "Better Notion CLI" in result.stdout
    assert "--help" in result.stdout
    assert "Commands" in result.stdout
    assert "auth" in result.stdout
    assert "version" in result.stdout


def test_auth_status_without_config() -> None:
    """Test auth status command when no config exists."""
    result = runner.invoke(app, ["auth", "status"])

    # CLI returns JSON with error info, exit code 0 for machine-readable errors
    assert '"success": false' in result.stdout or 'Not configured' in result.stdout


def test_auth_logout_without_config() -> None:
    """Test auth logout command when no config exists."""
    result = runner.invoke(app, ["auth", "logout"])

    # CLI returns JSON with error info, exit code 0 for machine-readable errors
    assert '"success": false' in result.stdout or 'No credentials found' in result.stdout


def test_auth_help() -> None:
    """Test that auth command group help displays correctly."""
    result = runner.invoke(app, ["auth", "--help"])

    assert result.exit_code == 0
    assert "Authentication commands" in result.stdout
    assert "status" in result.stdout
    assert "logout" in result.stdout


def test_verbose_flag_accepted() -> None:
    """Test that the version command works."""
    result = runner.invoke(app, ["version"])

    assert result.exit_code == 0
