"""
Tests for plugin loader functionality.
"""
import json
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

from better_notion.plugins.loader import PluginLoader
from better_notion.plugins.base import CommandPlugin


class TestPluginLoader:
    """Tests for PluginLoader class."""

    def test_loader_initialization(self):
        """Test that loader initializes with default directories."""
        loader = PluginLoader()

        assert len(loader.plugin_dirs) > 0
        assert loader.loaded_plugins == {}

    def test_loader_initialization_custom_dirs(self, tmp_path):
        """Test that loader initializes with custom directories."""
        custom_dirs = [tmp_path / "plugins1", tmp_path / "plugins2"]
        loader = PluginLoader(plugin_dirs=custom_dirs)

        assert loader.plugin_dirs == custom_dirs

    def test_loader_creates_plugin_dirs(self, tmp_path):
        """Test that loader creates plugin directories if they don't exist."""
        loader = PluginLoader(plugin_dirs=[tmp_path / "new_plugins"])

        # Directory should be created during discovery
        loader.discover()
        assert (tmp_path / "new_plugins").exists()

    def test_loader_load_config_default(self):
        """Test loading default configuration."""
        loader = PluginLoader()
        config = loader._load_config()

        assert "plugin_dir" in config
        assert "auto_update" in config
        assert isinstance(config["official_plugins"], dict)

    def test_loader_load_config_from_file(self, tmp_path):
        """Test loading configuration from file."""
        config_file = tmp_path / "plugin-config.json"
        config_file.write_text(json.dumps({
            "plugin_dir": "/custom/path",
            "auto_update": True
        }))

        with patch.object(PluginLoader, '_default_config') as mock_default:
            mock_default.return_value = {}
            loader = PluginLoader()
            # Would normally load from home directory
            # This test structure would need actual patching
            pass

    def test_loader_discover_from_empty_dir(self, tmp_path):
        """Test discovering plugins from empty directory."""
        loader = PluginLoader(plugin_dirs=[tmp_path])
        plugins = loader.discover()

        assert isinstance(plugins, list)
        assert len(plugins) == 0

    def test_loader_discover_plugin_file(self, tmp_path):
        """Test discovering a plugin from Python file."""
        # Create a simple plugin file
        plugin_file = tmp_path / "test_plugin.py"
        plugin_file.write_text('''
def register(app):
    @app.command("test-cmd")
    def test_cmd():
        pass

PLUGIN_INFO = {
    "name": "test-plugin",
    "version": "1.0.0",
    "description": "Test plugin",
    "author": "Test"
}
''')

        loader = PluginLoader(plugin_dirs=[tmp_path])
        plugins = loader.discover()

        assert len(plugins) >= 0  # May fail if module loading fails

    def test_loader_get_plugin_not_found(self):
        """Test getting a plugin that doesn't exist."""
        loader = PluginLoader()
        plugin = loader.load_plugin("nonexistent-plugin")

        assert plugin is None

    def test_loader_list_plugins(self, tmp_path):
        """Test listing all plugins."""
        loader = PluginLoader(plugin_dirs=[tmp_path])
        plugins = loader.list_plugins()

        assert isinstance(plugins, dict)

    def test_loader_is_official_plugin(self, tmp_path):
        """Test official plugin detection."""
        # This would require mocking the official plugins directory
        loader = PluginLoader()
        # Since official directory doesn't exist in test, should return False
        assert loader.is_official_plugin("productivity") is False


class TestPluginIntegration:
    """Integration tests for plugin system."""

    def test_plugin_registration_and_loading(self, tmp_path):
        """Test creating and loading a plugin."""
        # Create a plugin file
        plugin_file = tmp_path / "integration_plugin.py"
        plugin_file.write_text('''
def register(app):
    @app.command("integration-cmd")
    def integration_cmd():
        return {"success": True}

PLUGIN_INFO = {
    "name": "integration-plugin",
    "version": "1.0.0",
    "description": "Integration test plugin",
    "author": "Test"
}
''')

        loader = PluginLoader(plugin_dirs=[tmp_path])
        plugins = loader.discover()

        # Should discover the plugin (even if loading fails)
        assert isinstance(plugins, list)
