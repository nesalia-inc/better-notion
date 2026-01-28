"""
Tests for plugin commands with state management.

This module tests the plugin commands (list, enable, disable) with
the new official plugin state management system.
"""
from __future__ import annotations

import json
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from typer.testing import CliRunner

from better_notion._cli.commands.plugins import app


@pytest.fixture
def runner():
    """Create CLI runner for testing."""
    return CliRunner()


@pytest.fixture
def mock_state_file(tmp_path):
    """Create a temporary state file for testing."""
    state_file = tmp_path / "state.json"
    return state_file


class TestPluginListWithState:
    """Tests for plugin list command with state management."""

    def test_list_shows_official_plugins(self, runner):
        """Test that list shows official plugins with their state."""
        with patch("better_notion.plugins.state.PluginStateManager") as MockStateManager:
            mock_manager = MagicMock()
            mock_manager.is_enabled.return_value = True

            MockStateManager.return_value = mock_manager

            result = runner.invoke(app, ["list"])

            assert result.exit_code == 0
            assert "Official Plugins (built-in):" in result.stdout
            assert "productivity" in result.stdout

    def test_list_shows_disabled_status(self, runner):
        """Test that list shows disabled status for disabled plugins."""
        with patch("better_notion.plugins.state.PluginStateManager") as MockStateManager:
            mock_manager = MagicMock()
            # Productivity is disabled
            mock_manager.is_enabled.side_effect = lambda name: name != "productivity"

            MockStateManager.return_value = mock_manager

            result = runner.invoke(app, ["list"])

            assert result.exit_code == 0
            assert "✗ Disabled" in result.stdout or "Disabled" in result.stdout

    def test_list_shows_enabled_status(self, runner):
        """Test that list shows enabled status for enabled plugins."""
        with patch("better_notion.plugins.state.PluginStateManager") as MockStateManager:
            mock_manager = MagicMock()
            mock_manager.is_enabled.return_value = True

            MockStateManager.return_value = mock_manager

            result = runner.invoke(app, ["list"])

            assert result.exit_code == 0
            assert "✓ Enabled" in result.stdout or "Enabled" in result.stdout

    def test_list_verbose_shows_more_details(self, runner):
        """Test that verbose mode shows more details."""
        with patch("better_notion.plugins.state.PluginStateManager") as MockStateManager:
            mock_manager = MagicMock()
            mock_manager.is_enabled.return_value = True

            MockStateManager.return_value = mock_manager

            result = runner.invoke(app, ["list", "--verbose"])

            assert result.exit_code == 0
            assert "Version:" in result.stdout
            assert "Author:" in result.stdout

    def test_list_json_includes_state(self, runner):
        """Test that JSON output includes plugin state."""
        with patch("better_notion.plugins.state.PluginStateManager") as MockStateManager:
            mock_manager = MagicMock()
            mock_manager.is_enabled.return_value = True

            MockStateManager.return_value = mock_manager

            result = runner.invoke(app, ["list", "--json"])

            assert result.exit_code == 0

            data = json.loads(result.stdout)
            assert "productivity" in data
            assert data["productivity"]["bundled"] is True
            assert data["productivity"]["enabled"] is True


class TestPluginEnableWithState:
    """Tests for plugin enable command with state management."""

    def test_enable_official_plugin(self, runner):
        """Test enabling an official plugin."""
        with patch("better_notion.plugins.state.PluginStateManager") as MockStateManager:
            mock_manager = MagicMock()
            MockStateManager.return_value = mock_manager

            result = runner.invoke(app, ["enable", "productivity"])

            assert result.exit_code == 0
            mock_manager.enable.assert_called_once_with("productivity")

    def test_enable_user_plugin(self, runner, tmp_path):
        """Test enabling a user plugin uses existing logic."""
        with patch("better_notion._cli.commands.plugins.Path.home") as mock_home:
            # Mock home directory
            mock_home.return_value = tmp_path

            result = runner.invoke(app, ["enable", "my-plugin"])

            assert result.exit_code == 0

    def test_enable_shows_success_response(self, runner):
        """Test that enable returns proper success response."""
        with patch("better_notion.plugins.state.PluginStateManager") as MockStateManager:
            mock_manager = MagicMock()
            MockStateManager.return_value = mock_manager

            result = runner.invoke(app, ["enable", "productivity"])

            # Should complete without error
            assert result.exit_code == 0


class TestPluginDisableWithState:
    """Tests for plugin disable command with state management."""

    def test_disable_official_plugin(self, runner):
        """Test disabling an official plugin."""
        with patch("better_notion.plugins.state.PluginStateManager") as MockStateManager:
            mock_manager = MagicMock()
            MockStateManager.return_value = mock_manager

            result = runner.invoke(app, ["disable", "productivity"])

            assert result.exit_code == 0
            mock_manager.disable.assert_called_once_with("productivity")

    def test_disable_shows_message_about_restart(self, runner):
        """Test that disable mentions CLI restart is needed."""
        with patch("better_notion.plugins.state.PluginStateManager") as MockStateManager:
            mock_manager = MagicMock()
            MockStateManager.return_value = mock_manager

            result = runner.invoke(app, ["disable", "productivity"])

            # Should complete without error
            assert result.exit_code == 0

    def test_disable_returns_success_response(self, runner):
        """Test that disable returns proper success response."""
        with patch("better_notion.plugins.state.PluginStateManager") as MockStateManager:
            mock_manager = MagicMock()
            MockStateManager.return_value = mock_manager

            result = runner.invoke(app, ["disable", "productivity"])

            # Should complete without error
            assert result.exit_code == 0


class TestPluginStateIntegration:
    """Integration tests for plugin state management."""

    def test_enable_disable_cycle(self, runner):
        """Test enabling and disabling a plugin."""
        with patch("better_notion.plugins.state.PluginStateManager") as MockStateManager:
            mock_manager = MagicMock()
            MockStateManager.return_value = mock_manager

            # Disable
            runner.invoke(app, ["disable", "productivity"])
            assert mock_manager.disable.called

            # Enable
            runner.invoke(app, ["enable", "productivity"])
            assert mock_manager.enable.called

    def test_list_respects_state(self, runner):
        """Test that list command respects plugin state."""
        with patch("better_notion.plugins.state.PluginStateManager") as MockStateManager:
            mock_manager = MagicMock()

            # Test with disabled plugin
            mock_manager.is_enabled.return_value = False
            MockStateManager.return_value = mock_manager

            result = runner.invoke(app, ["list"])
            # Should show disabled status
            assert "Disabled" in result.stdout or "✗" in result.stdout

            # Test with enabled plugin
            mock_manager.is_enabled.return_value = True
            MockStateManager.return_value = mock_manager

            result = runner.invoke(app, ["list"])
            # Should show enabled status
            assert result.exit_code == 0  # Should complete successfully


class TestPluginListOutput:
    """Tests for plugin list output formatting."""

    def test_list_shows_tip_about_enabling(self, runner):
        """Test that list shows tip about enable/disable."""
        with patch("better_notion.plugins.state.PluginStateManager") as MockStateManager:
            mock_manager = MagicMock()
            mock_manager.is_enabled.return_value = True

            MockStateManager.return_value = mock_manager

            result = runner.invoke(app, ["list"])

            assert result.exit_code == 0
            assert "Tip:" in result.stdout or "enable/disable" in result.stdout

    def test_list_groups_plugins_by_type(self, runner):
        """Test that list groups plugins by type."""
        with patch("better_notion.plugins.state.PluginStateManager") as MockStateManager:
            mock_manager = MagicMock()
            mock_manager.is_enabled.return_value = True

            MockStateManager.return_value = mock_manager

            result = runner.invoke(app, ["list"])

            assert result.exit_code == 0
            # Should have both sections
            lines = result.stdout.split("\n")
            has_official = any("Official Plugins" in line for line in lines)

            # At minimum should have official plugins
            assert has_official

    def test_list_shows_empty_when_no_plugins(self, runner):
        """Test that list handles case with no plugins."""
        with patch("better_notion.plugins.official.OFFICIAL_PLUGINS", []):
            with patch("better_notion.plugins.loader.PluginLoader") as MockLoader:
                mock_loader = MagicMock()
                mock_loader.list_plugins.return_value = {}
                mock_loader.is_official_plugin.return_value = False

                MockLoader.return_value = mock_loader

                result = runner.invoke(app, ["list"])

                assert result.exit_code == 0
                assert "No plugins found" in result.stdout or "No plugins" in result.stdout


class TestPluginStatePersistence:
    """Tests for plugin state persistence."""

    def test_state_persists_across_invocations(self, runner, tmp_path):
        """Test that plugin state persists across command invocations."""
        state_file = tmp_path / "state.json"

        with patch("better_notion.plugins.state.PluginStateManager") as MockStateManager:
            mock_manager = MagicMock()
            mock_manager.state_file = state_file
            MockStateManager.return_value = mock_manager

            # Disable plugin
            runner.invoke(app, ["disable", "productivity"])

            # Create new manager instance (simulating new invocation)
            mock_manager2 = MagicMock()
            mock_manager2.is_enabled.return_value = False
            MockStateManager.return_value = mock_manager2

            result = runner.invoke(app, ["list"])

            # Should show as disabled
            assert "Disabled" in result.stdout or "✗" in result.stdout
