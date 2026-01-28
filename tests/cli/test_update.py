"""
Tests for CLI update command.

This module tests the update command functionality in the Better Notion CLI.
"""
from __future__ import annotations

import json
from unittest.mock import MagicMock, patch

import pytest
from typer.testing import CliRunner

from better_notion._cli.commands.update import app


@pytest.fixture
def runner():
    """Create CLI runner for testing."""
    return CliRunner()


class TestUpdateUpgrade:
    """Tests for the update upgrade command."""

    def test_upgrade_without_check_performs_update(self, runner):
        """Test that upgrade command performs pip upgrade."""
        mock_result = MagicMock()
        mock_result.returncode = 0

        with patch("subprocess.run", return_value=mock_result) as mock_run:
            result = runner.invoke(app, ["upgrade"])

            # Verify command executed
            assert result.exit_code == 0

            # Verify pip upgrade was called
            mock_run.assert_called_once()
            call_args = mock_run.call_args
            assert "pip" in call_args[0][0]
            assert "install" in call_args[0][0]
            assert "--upgrade" in call_args[0][0]
            assert "better-notion" in call_args[0][0]

    def test_upgrade_with_check_only_checks(self, runner):
        """Test that upgrade --check only checks for updates."""
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "better-notion (0.9.2)\nAvailable versions: 0.9.2, 0.9.1"

        with patch("subprocess.run", return_value=mock_result) as mock_run:
            result = runner.invoke(app, ["upgrade", "--check"])

            # Verify command executed
            assert result.exit_code == 0

            # Verify pip index was called for checking
            mock_run.assert_called_once()
            call_args = mock_run.call_args
            assert "pip" in call_args[0][0]
            assert "index" in call_args[0][0]
            assert "versions" in call_args[0][0]

    def test_upgrade_shows_success_message(self, runner):
        """Test that upgrade shows success message on successful update."""
        mock_result = MagicMock()
        mock_result.returncode = 0

        with patch("subprocess.run", return_value=mock_result):
            result = runner.invoke(app, ["upgrade"])

            assert result.exit_code == 0
            assert "Successfully updated" in result.stdout

    def test_upgrade_handles_pip_failure(self, runner):
        """Test that upgrade handles pip failure gracefully."""
        mock_result = MagicMock()
        mock_result.returncode = 1

        with patch("subprocess.run", return_value=mock_result) as mock_run:
            result = runner.invoke(app, ["upgrade"])

            # Verify subprocess was still called
            mock_run.assert_called_once()
            # The command should complete without crashing
            # Error message is returned via format_error which outputs JSON

    def test_upgrade_short_flag_check(self, runner):
        """Test that -c flag works for check."""
        mock_result = MagicMock()
        mock_result.returncode = 0

        with patch("subprocess.run", return_value=mock_result) as mock_run:
            result = runner.invoke(app, ["upgrade", "-c"])

            assert result.exit_code == 0
            # Verify check mode was used
            call_args = mock_run.call_args
            assert "index" in call_args[0][0]


class TestUpdateCheck:
    """Tests for the update check command."""

    def test_check_alias_for_upgrade_check(self, runner):
        """Test that check command is alias for upgrade --check."""
        mock_result = MagicMock()
        mock_result.returncode = 0

        with patch("subprocess.run", return_value=mock_result) as mock_run:
            result = runner.invoke(app, ["check"])

            assert result.exit_code == 0
            # Should call pip index versions
            mock_run.assert_called_once()
            call_args = mock_run.call_args
            assert "index" in call_args[0][0]


class TestUpdateSelf:
    """Tests for the update self command."""

    def test_self_alias_for_upgrade(self, runner):
        """Test that self command is alias for upgrade."""
        mock_result = MagicMock()
        mock_result.returncode = 0

        with patch("subprocess.run", return_value=mock_result) as mock_run:
            result = runner.invoke(app, ["self"])

            assert result.exit_code == 0
            # Should call pip install --upgrade
            mock_run.assert_called_once()
            call_args = mock_run.call_args
            assert "--upgrade" in call_args[0][0]


class TestUpdateErrorHandling:
    """Tests for error handling in update command."""

    def test_handles_subprocess_exception(self, runner):
        """Test that subprocess exceptions are handled."""
        with patch("subprocess.run", side_effect=Exception("Subprocess error")):
            result = runner.invoke(app, ["upgrade"])

            # Should handle exception and return error JSON
            # Error is caught and returned via format_error
            assert result.exit_code == 0  # Command doesn't crash, returns error JSON

    def test_check_handles_old_pip_versions(self, runner):
        """Test that check handles older pip versions without index command."""
        mock_result = MagicMock()
        mock_result.returncode = 1  # Simulate pip index not available

        with patch("subprocess.run", return_value=mock_result):
            result = runner.invoke(app, ["upgrade", "--check"])

            # Should show helpful message
            assert result.exit_code == 0
            assert "notion update upgrade" in result.stdout or "pip" in result.stdout.lower()


class TestUpdateOutput:
    """Tests for output formatting."""

    def test_upgrade_shows_progress_message(self, runner):
        """Test that upgrade shows informative messages."""
        mock_result = MagicMock()
        mock_result.returncode = 0

        with patch("subprocess.run", return_value=mock_result):
            result = runner.invoke(app, ["upgrade"])

            # Should show updating message
            assert "Updating" in result.stdout or "better-notion" in result.stdout.lower()

    def test_check_shows_checking_message(self, runner):
        """Test that check shows checking message."""
        mock_result = MagicMock()
        mock_result.returncode = 0

        with patch("subprocess.run", return_value=mock_result):
            result = runner.invoke(app, ["upgrade", "--check"])

            # Should show checking message
            assert "Checking" in result.stdout or "check" in result.stdout.lower()


class TestUpdateIntegration:
    """Integration tests for update command."""

    def test_update_commands_are_accessible(self, runner):
        """Test that all update commands are accessible."""
        # Test that commands exist
        result_upgrade = runner.invoke(app, ["upgrade", "--help"])
        result_check = runner.invoke(app, ["check", "--help"])
        result_self = runner.invoke(app, ["self", "--help"])

        assert result_upgrade.exit_code == 0
        assert result_check.exit_code == 0
        assert result_self.exit_code == 0

    def test_update_help_shows_commands(self, runner):
        """Test that update help shows available commands."""
        result = runner.invoke(app, ["--help"])

        assert result.exit_code == 0
        assert "upgrade" in result.stdout
        assert "check" in result.stdout
        assert "self" in result.stdout

    def test_package_name_is_correct(self, runner):
        """Test that correct package name is used."""
        mock_result = MagicMock()
        mock_result.returncode = 0

        with patch("subprocess.run", return_value=mock_result) as mock_run:
            runner.invoke(app, ["upgrade"])

            # Verify package name
            call_args = mock_run.call_args
            assert "better-notion" in call_args[0][0]
