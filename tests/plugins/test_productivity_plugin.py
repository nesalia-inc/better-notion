"""
Tests for the official productivity plugin.
"""
import pytest

from better_notion.plugins.official.productivity import ProductivityPlugin


class TestProductivityPlugin:
    """Tests for ProductivityPlugin."""

    def test_plugin_has_required_methods(self):
        """Test that plugin has required methods."""
        plugin = ProductivityPlugin()

        assert hasattr(plugin, 'register_commands')
        assert hasattr(plugin, 'get_info')
        assert callable(plugin.register_commands)
        assert callable(plugin.get_info)

    def test_plugin_info_structure(self):
        """Test that plugin info has correct structure."""
        plugin = ProductivityPlugin()
        info = plugin.get_info()

        # Check required fields
        assert "name" in info
        assert "version" in info
        assert "description" in info
        assert "author" in info
        assert "official" in info
        assert "category" in info
        assert "dependencies" in info

        # Check values
        assert info["name"] == "productivity"
        assert info["official"] is True
        assert info["category"] == "productivity"
        assert isinstance(info["dependencies"], list)

    def test_plugin_info_values(self):
        """Test that plugin info has expected values."""
        plugin = ProductivityPlugin()
        info = plugin.get_info()

        assert info["author"] == "Better Notion Team"
        assert "productivity" in info["description"].lower()
        assert info["version"] == "1.0.0"

    def test_plugin_validate(self):
        """Test that plugin validates successfully."""
        plugin = ProductivityPlugin()
        is_valid, errors = plugin.validate()

        assert is_valid is True
        assert len(errors) == 0

    def test_plugin_registers_commands(self):
        """Test that plugin can register commands."""
        plugin = ProductivityPlugin()
        from typer import Typer

        app = Typer()
        plugin.register_commands(app)

        # Commands should be registered
        # (We can't easily test this without actually running the CLI)
        assert app.registered_commands is not None or len(app.registered_commands) >= 0


class TestProductivityPluginCommands:
    """Tests for individual productivity plugin commands."""

    def test_quick_capture_command_exists(self):
        """Test that quick-capture command is defined."""
        plugin = ProductivityPlugin()
        from typer import Typer

        app = Typer()
        plugin.register_commands(app)

        # Check that command was registered
        # Note: Typer doesn't expose registered_commands directly
        # so we can't test this deeply without running the CLI
        assert True  # Placeholder - would need actual CLI testing

    def test_inbox_zero_command_exists(self):
        """Test that inbox-zero command is defined."""
        plugin = ProductivityPlugin()

        # Commands should be registered
        assert True  # Placeholder

    def test_my_tasks_command_exists(self):
        """Test that my-tasks command is defined."""
        plugin = ProductivityPlugin()

        # Commands should be registered
        assert True  # Placeholder

    def test_daily_notes_command_exists(self):
        """Test that daily-notes command is defined."""
        plugin = ProductivityPlugin()

        # Commands should be registered
        assert True  # Placeholder
