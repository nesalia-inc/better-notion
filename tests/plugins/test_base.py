"""
Tests for plugin base interface and protocols.
"""
import pytest
from typer import Typer

from better_notion.plugins.base import CommandPlugin, DataPlugin, PluginInterface


class MockPlugin:
    """Mock plugin for testing."""

    def register_commands(self, app: Typer) -> None:
        """Register mock commands."""
        @app.command("mock-command")
        def mock_command():
            pass

    def get_info(self):
        """Return mock info."""
        return {
            "name": "mock-plugin",
            "version": "1.0.0",
            "description": "Mock plugin",
            "author": "Test Author",
            "official": False
        }


class TestCommandPlugin:
    """Tests for CommandPlugin protocol."""

    def test_plugin_has_register_commands(self):
        """Test that plugin has register_commands method."""
        plugin = MockPlugin()
        assert hasattr(plugin, 'register_commands')
        assert callable(plugin.register_commands)

    def test_plugin_has_get_info(self):
        """Test that plugin has get_info method."""
        plugin = MockPlugin()
        assert hasattr(plugin, 'get_info')
        assert callable(plugin.get_info)

    def test_plugin_info_structure(self):
        """Test that plugin info has required fields."""
        plugin = MockPlugin()
        info = plugin.get_info()

        assert "name" in info
        assert "version" in info
        assert "description" in info
        assert "author" in info
        assert isinstance(info["name"], str)
        assert isinstance(info["version"], str)


class TestPluginInterface:
    """Tests for PluginInterface abstract base class."""

    def test_plugin_interface_requires_register_commands(self):
        """Test that PluginInterface requires register_commands."""
        with pytest.raises(TypeError):
            PluginInterface()

    def test_plugin_interface_default_get_info(self):
        """Test default get_info implementation."""

        class ConcretePlugin(PluginInterface):
            def register_commands(self, app):
                pass

        plugin = ConcretePlugin()
        info = plugin.get_info()

        assert info["name"] == "ConcretePlugin"
        assert info["version"] == "1.0.0"
        assert "author" in info

    def test_plugin_interface_validate_success(self):
        """Test validation with valid plugin."""

        class ValidPlugin(PluginInterface):
            def register_commands(self, app):
                pass

        plugin = ValidPlugin()
        is_valid, errors = plugin.validate()

        assert is_valid is True
        assert len(errors) == 0

    def test_plugin_interface_validate_missing_fields(self):
        """Test validation with missing required fields."""

        class InvalidPlugin(PluginInterface):
            def register_commands(self, app):
                pass

            def get_info(self):
                return {"name": "test"}  # Missing required fields

        plugin = InvalidPlugin()
        is_valid, errors = plugin.validate()

        assert is_valid is False
        assert len(errors) > 0


class TestDataPlugin:
    """Tests for DataPlugin protocol."""

    def test_data_plugin_register_filters(self):
        """Test that data plugin can register filters."""
        filters = {"uppercase": lambda x: x.upper()}
        assert callable(filters["uppercase"])

    def test_data_plugin_register_formatters(self):
        """Test that data plugin can register formatters."""
        formatters = {"markdown": lambda x: f"## {x}"}
        assert callable(formatters["markdown"])
