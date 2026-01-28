"""
Plugin state management for Better Notion CLI.

This module handles the state of official plugins (enabled/disabled).
"""
from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any


class PluginStateManager:
    """Manages the enabled/disabled state of official plugins."""

    def __init__(self, state_file: Path | None = None):
        """
        Initialize the plugin state manager.

        Args:
            state_file: Path to the state file. Defaults to ~/.notion/plugins/state.json
        """
        self.state_file = state_file or (Path.home() / ".notion" / "plugins" / "state.json")
        self.state_file.parent.mkdir(parents=True, exist_ok=True)
        self._state = self._load_state()

    def _load_state(self) -> dict[str, Any]:
        """Load state from file."""
        if self.state_file.exists():
            try:
                return json.loads(self.state_file.read_text())
            except (json.JSONDecodeError, IOError):
                pass
        return {"official_plugins": {}}

    def _save_state(self) -> None:
        """Save state to file."""
        self.state_file.write_text(json.dumps(self._state, indent=2))

    def is_enabled(self, plugin_name: str) -> bool:
        """
        Check if a plugin is enabled.

        Args:
            plugin_name: Name of the plugin

        Returns:
            True if the plugin is enabled, False if disabled
        """
        plugin_state = self._state.get("official_plugins", {}).get(plugin_name, {})
        return plugin_state.get("state") != "disabled"

    def enable(self, plugin_name: str) -> None:
        """
        Enable a plugin.

        Args:
            plugin_name: Name of the plugin to enable
        """
        if "official_plugins" not in self._state:
            self._state["official_plugins"] = {}

        # Remove disabled state if it exists
        if plugin_name in self._state["official_plugins"]:
            del self._state["official_plugins"][plugin_name]

        self._save_state()

    def disable(self, plugin_name: str) -> None:
        """
        Disable a plugin.

        Args:
            plugin_name: Name of the plugin to disable
        """
        if "official_plugins" not in self._state:
            self._state["official_plugins"] = {}

        self._state["official_plugins"][plugin_name] = {
            "state": "disabled",
            "disabled_at": datetime.now().isoformat()
        }

        self._save_state()

    def get_plugin_state(self, plugin_name: str) -> dict[str, Any] | None:
        """
        Get the state of a specific plugin.

        Args:
            plugin_name: Name of the plugin

        Returns:
            Plugin state dict or None if no state exists
        """
        return self._state.get("official_plugins", {}).get(plugin_name)

    def get_all_states(self) -> dict[str, dict[str, Any]]:
        """
        Get states of all plugins.

        Returns:
            Dict mapping plugin names to their states
        """
        return self._state.get("official_plugins", {})

    def is_official_plugin(self, plugin_name: str) -> bool:
        """
        Check if a plugin is an official plugin.

        This is a helper that can be used to determine if a plugin
        should be managed through the state system.

        Args:
            plugin_name: Name of the plugin

        Returns:
            True if the plugin is official
        """
        # This will be checked against the OFFICIAL_PLUGINS list
        # For now, return False - the actual check is done elsewhere
        return False
