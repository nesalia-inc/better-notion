"""
Tests for plugin state management.

This module tests the PluginStateManager class which handles
the enabled/disabled state of official plugins.
"""
from __future__ import annotations

import json
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

from better_notion.plugins.state import PluginStateManager


class TestPluginStateManager:
    """Tests for the PluginStateManager class."""

    def test_state_manager_initialization(self):
        """Test that state manager initializes with default state."""
        with tempfile.TemporaryDirectory() as tmpdir:
            state_file = Path(tmpdir) / "state.json"
            manager = PluginStateManager(state_file)

            assert manager.state_file == state_file
            assert manager._state == {"official_plugins": {}}

    def test_state_manager_creates_directory(self):
        """Test that state manager creates state file directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            state_file = Path(tmpdir) / "subdir" / "state.json"
            manager = PluginStateManager(state_file)

            assert state_file.parent.exists()

    def test_is_enabled_returns_true_by_default(self):
        """Test that plugins are enabled by default."""
        with tempfile.TemporaryDirectory() as tmpdir:
            state_file = Path(tmpdir) / "state.json"
            manager = PluginStateManager(state_file)

            assert manager.is_enabled("productivity") is True
            assert manager.is_enabled("any_plugin") is True

    def test_enable_plugin(self):
        """Test enabling a plugin."""
        with tempfile.TemporaryDirectory() as tmpdir:
            state_file = Path(tmpdir) / "state.json"
            manager = PluginStateManager(state_file)

            # First disable
            manager.disable("productivity")
            assert manager.is_enabled("productivity") is False

            # Then enable
            manager.enable("productivity")
            assert manager.is_enabled("productivity") is True

    def test_disable_plugin(self):
        """Test disabling a plugin."""
        with tempfile.TemporaryDirectory() as tmpdir:
            state_file = Path(tmpdir) / "state.json"
            manager = PluginStateManager(state_file)

            manager.disable("productivity")
            assert manager.is_enabled("productivity") is False

    def test_disable_persists_to_file(self):
        """Test that disabled state persists to file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            state_file = Path(tmpdir) / "state.json"
            manager = PluginStateManager(state_file)

            manager.disable("productivity")

            # Create new manager instance
            manager2 = PluginStateManager(state_file)
            assert manager2.is_enabled("productivity") is False

    def test_enable_persists_to_file(self):
        """Test that enabled state persists to file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            state_file = Path(tmpdir) / "state.json"
            manager = PluginStateManager(state_file)

            manager.disable("productivity")
            manager.enable("productivity")

            # Create new manager instance
            manager2 = PluginStateManager(state_file)
            assert manager2.is_enabled("productivity") is True

    def test_get_plugin_state(self):
        """Test getting state of a specific plugin."""
        with tempfile.TemporaryDirectory() as tmpdir:
            state_file = Path(tmpdir) / "state.json"
            manager = PluginStateManager(state_file)

            # No state initially
            assert manager.get_plugin_state("productivity") is None

            # After disabling
            manager.disable("productivity")
            state = manager.get_plugin_state("productivity")
            assert state is not None
            assert state["state"] == "disabled"
            assert "disabled_at" in state

    def test_get_all_states(self):
        """Test getting all plugin states."""
        with tempfile.TemporaryDirectory() as tmpdir:
            state_file = Path(tmpdir) / "state.json"
            manager = PluginStateManager(state_file)

            manager.disable("productivity")
            manager.disable("organizations")

            all_states = manager.get_all_states()
            assert "productivity" in all_states
            assert "organizations" in all_states
            assert all_states["productivity"]["state"] == "disabled"
            assert all_states["organizations"]["state"] == "disabled"

    def test_multiple_plugins_independent_states(self):
        """Test that multiple plugins have independent states."""
        with tempfile.TemporaryDirectory() as tmpdir:
            state_file = Path(tmpdir) / "state.json"
            manager = PluginStateManager(state_file)

            manager.disable("productivity")
            # organizations should still be enabled
            assert manager.is_enabled("organizations") is True
            assert manager.is_enabled("productivity") is False

    def test_enable_after_disable(self):
        """Test enabling a plugin after disabling."""
        with tempfile.TemporaryDirectory() as tmpdir:
            state_file = Path(tmpdir) / "state.json"
            manager = PluginStateManager(state_file)

            manager.disable("productivity")
            assert manager.is_enabled("productivity") is False

            manager.enable("productivity")
            assert manager.is_enabled("productivity") is True

            # State should be removed from file when enabled
            assert manager.get_plugin_state("productivity") is None

    def test_corrupted_state_file_recovery(self):
        """Test that corrupted state file is handled gracefully."""
        with tempfile.TemporaryDirectory() as tmpdir:
            state_file = Path(tmpdir) / "state.json"

            # Write corrupted JSON
            state_file.write_text("{invalid json")

            manager = PluginStateManager(state_file)
            # Should recover with default state
            assert manager.is_enabled("productivity") is True

    def test_empty_state_file(self):
        """Test that empty state file is handled."""
        with tempfile.TemporaryDirectory() as tmpdir:
            state_file = Path(tmpdir) / "state.json"

            # Write empty JSON
            state_file.write_text("{}")

            manager = PluginStateManager(state_file)
            # Should work normally
            assert manager.is_enabled("productivity") is True
            manager.disable("productivity")
            assert manager.is_enabled("productivity") is False

    def test_state_file_format(self):
        """Test that state file has correct format."""
        with tempfile.TemporaryDirectory() as tmpdir:
            state_file = Path(tmpdir) / "state.json"
            manager = PluginStateManager(state_file)

            manager.disable("productivity")

            # Read file and verify format
            content = json.loads(state_file.read_text())
            assert "official_plugins" in content
            assert "productivity" in content["official_plugins"]
            assert content["official_plugins"]["productivity"]["state"] == "disabled"
            assert "disabled_at" in content["official_plugins"]["productivity"]

    def test_concurrent_managers(self):
        """Test that multiple manager instances can coordinate via file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            state_file = Path(tmpdir) / "state.json"
            manager1 = PluginStateManager(state_file)

            manager1.disable("productivity")

            # Create a NEW manager instance which will read from file
            manager2 = PluginStateManager(state_file)
            # manager2 should see the disabled state
            assert manager2.is_enabled("productivity") is False

            manager2.enable("productivity")

            # Create yet another manager instance
            manager3 = PluginStateManager(state_file)
            # manager3 should see the enabled state
            assert manager3.is_enabled("productivity") is True
