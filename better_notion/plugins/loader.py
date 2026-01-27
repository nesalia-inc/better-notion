"""
Plugin loader for discovering and loading Better Notion CLI plugins.

The plugin loader supports multiple plugin sources:
1. Official plugins (bundled with the package)
2. User plugins (in ~/.notion/plugins/)
3. Local project plugins (in .notion-plugins/)
4. Python package plugins (installed via pip)
"""
from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path
from typing import Any

from better_notion.plugins.base import CommandPlugin


class PluginLoader:
    """
    Discover and load plugins from multiple sources.

    The plugin loader searches for plugins in configured directories
    and loads them into the CLI application.
    """

    DEFAULT_PLUGIN_DIRS = [
        Path.home() / ".notion" / "plugins",
        Path("/usr/local/lib/notion/plugins"),
        Path.cwd() / ".notion-plugins",
    ]

    def __init__(self, plugin_dirs: list[Path] | None = None):
        """
        Initialize the plugin loader.

        Args:
            plugin_dirs: List of directories to search for plugins.
                        If None, uses default directories.
        """
        self.plugin_dirs = plugin_dirs or self.DEFAULT_PLUGIN_DIRS
        self.loaded_plugins: dict[str, CommandPlugin] = {}
        self.plugin_config = self._load_config()

    def _load_config(self) -> dict[str, Any]:
        """Load plugin configuration from ~/.notion/plugin-config.json."""
        config_file = Path.home() / ".notion" / "plugin-config.json"
        if config_file.exists():
            try:
                return json.loads(config_file.read_text())
            except (json.JSONDecodeError, IOError):
                pass
        return self._default_config()

    def _default_config(self) -> dict[str, Any]:
        """Return default plugin configuration."""
        return {
            "plugin_dir": str(Path.home() / ".notion" / "plugins"),
            "auto_update": False,
            "update_interval": 86400,
            "install_location": "user",
            "enable_telemetry": False,
            "default_source": "pypi",
            "official_plugins": {
                "auto_install": [],
                "enabled_by_default": []
            }
        }

    def discover(self) -> list[CommandPlugin]:
        """
        Discover all plugins from configured directories.

        Returns:
            List of discovered plugin instances
        """
        plugins = []

        # Ensure plugin directories exist
        for plugin_dir in self.plugin_dirs:
            if not plugin_dir.exists():
                try:
                    plugin_dir.mkdir(parents=True, exist_ok=True)
                except OSError:
                    # Skip directories we can't create
                    continue

            # Load plugins from directory
            plugins.extend(self._load_from_dir(plugin_dir))

        return plugins

    def _load_from_dir(self, directory: Path) -> list[CommandPlugin]:
        """
        Load plugins from a specific directory.

        Args:
            directory: Directory to search for plugins

        Returns:
            List of loaded plugin instances
        """
        plugins = []

        # Look for Python files
        for plugin_file in directory.glob("*.py"):
            if plugin_file.name.startswith("_"):
                continue

            try:
                plugin = self._load_plugin_file(plugin_file)
                if plugin:
                    plugins.append(plugin)
            except Exception:
                # Skip plugins that fail to load
                continue

        return plugins

    def _load_plugin_file(self, plugin_file: Path) -> CommandPlugin | None:
        """
        Load a plugin from a Python file.

        Args:
            plugin_file: Path to the plugin Python file

        Returns:
            Plugin instance or None if loading fails
        """
        # Load the module
        spec = importlib.util.spec_from_file_location(
            plugin_file.stem,
            plugin_file
        )
        if spec is None or spec.loader is None:
            return None

        module = importlib.util.module_from_spec(spec)
        sys.modules[plugin_file.stem] = module
        spec.loader.exec_module(module)

        # Look for plugin class or function
        if hasattr(module, 'register'):
            # Module has a register function
            class FunctionPlugin:
                def __init__(self, register_func, module_ref):
                    self._register = register_func
                    self._module = module_ref

                def register_commands(self, app):
                    return self._register(app)

                def get_info(self):
                    return getattr(self._module, 'PLUGIN_INFO', {
                        "name": plugin_file.stem,
                        "version": "1.0.0",
                        "description": f"Plugin from {plugin_file.name}",
                        "author": "Unknown",
                        "official": False
                    })

            return FunctionPlugin(module.register, module)

        # Look for Plugin class
        for attr_name in dir(module):
            attr = getattr(module, attr_name)
            if isinstance(attr, type) and attr_name.endswith('Plugin'):
                try:
                    return attr()
                except Exception:
                    continue

        return None

    def load_plugin(self, plugin_name: str) -> CommandPlugin | None:
        """
        Load a specific plugin by name.

        Args:
            plugin_name: Name of the plugin to load

        Returns:
            Plugin instance or None if not found
        """
        if plugin_name in self.loaded_plugins:
            return self.loaded_plugins[plugin_name]

        # Search for plugin
        for plugin in self.discover():
            info = plugin.get_info()
            if info.get("name") == plugin_name:
                self.loaded_plugins[plugin_name] = plugin
                return plugin

        return None

    def get_plugin(self, plugin_name: str) -> CommandPlugin | None:
        """
        Get a loaded plugin by name.

        Args:
            plugin_name: Name of the plugin

        Returns:
            Plugin instance or None if not loaded
        """
        return self.loaded_plugins.get(plugin_name)

    def list_plugins(self) -> dict[str, dict[str, Any]]:
        """
        List all discovered plugins with their metadata.

        Returns:
            Dictionary mapping plugin names to their metadata
        """
        plugins = {}
        for plugin in self.discover():
            info = plugin.get_info()
            name = info.get("name", "unknown")
            plugins[name] = info
        return plugins

    def is_official_plugin(self, plugin_name: str) -> bool:
        """
        Check if a plugin is an official plugin.

        Args:
            plugin_name: Name of the plugin

        Returns:
            True if the plugin is official
        """
        # Check if plugin exists in official plugins directory
        official_dir = Path(__file__).parent / "official"
        if not official_dir.exists():
            return False

        for plugin_file in official_dir.glob("*.py"):
            if plugin_file.stem == plugin_name or plugin_file.stem == f"{plugin_name}_plugin":
                return True

        return False
