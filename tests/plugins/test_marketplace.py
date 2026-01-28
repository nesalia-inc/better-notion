"""
Tests for plugin marketplace command.

This module tests the marketplace command in the Better Notion CLI plugin system.
"""
from __future__ import annotations

import json
from unittest.mock import MagicMock, patch

import pytest
from typer.testing import CliRunner

from better_notion._cli.commands.plugins import app


@pytest.fixture
def runner():
    """Create CLI runner for testing."""
    return CliRunner()


def create_mock_plugin_class(plugin_info):
    """Create a mock plugin class with given info."""
    class MockPluginClass:
        def __init__(self):
            """Initialize mock plugin."""
            pass

        def register_commands(self, app):
            """Register commands (mock)."""
            pass

        def get_info(self):
            """Return plugin info."""
            return plugin_info

    return MockPluginClass


class TestMarketplaceCommand:
    """Tests for the plugin marketplace command."""

    def test_marketplace_lists_official_plugins(self, runner):
        """Test that marketplace lists official plugins."""
        mock_plugin_class = create_mock_plugin_class({
            "name": "productivity",
            "version": "1.0.0",
            "description": "Personal productivity helpers",
            "author": "Better Notion Team",
            "official": True,
            "category": "productivity",
            "dependencies": []
        })

        with patch("better_notion.plugins.official.OFFICIAL_PLUGINS", [mock_plugin_class]):
            result = runner.invoke(app, ["marketplace"])

            # Should succeed
            assert result.exit_code == 0

            # Should show marketplace header
            assert "Official Plugins Marketplace" in result.stdout

            # Should show plugin name and description
            assert "productivity" in result.stdout
            assert "Personal productivity helpers" in result.stdout

    def test_marketplace_with_category_filter(self, runner):
        """Test marketplace with category filter."""
        mock_plugin1 = create_mock_plugin_class({
            "name": "productivity",
            "version": "1.0.0",
            "description": "Productivity helpers",
            "author": "Team",
            "official": True,
            "category": "productivity",
            "dependencies": []
        })

        mock_plugin2 = create_mock_plugin_class({
            "name": "organizations",
            "version": "1.0.0",
            "description": "Organization helpers",
            "author": "Team",
            "official": True,
            "category": "organizations",
            "dependencies": []
        })

        with patch("better_notion.plugins.official.OFFICIAL_PLUGINS",
                   [mock_plugin1, mock_plugin2]):
            result = runner.invoke(app, ["marketplace", "--category", "productivity"])

            assert result.exit_code == 0
            assert "productivity" in result.stdout
            assert "organizations" not in result.stdout
            assert "Showing plugins in category: productivity" in result.stdout

    def test_marketplace_with_nonexistent_category(self, runner):
        """Test marketplace with non-existent category."""
        mock_plugin = create_mock_plugin_class({
            "name": "productivity",
            "version": "1.0.0",
            "description": "Productivity helpers",
            "author": "Team",
            "official": True,
            "category": "productivity",
            "dependencies": []
        })

        with patch("better_notion.plugins.official.OFFICIAL_PLUGINS", [mock_plugin]):
            result = runner.invoke(app, ["marketplace", "--category", "nonexistent"])

            assert result.exit_code == 0
            assert "No plugins found in category 'nonexistent'" in result.stdout

    def test_marketplace_verbose_mode(self, runner):
        """Test marketplace with verbose output."""
        mock_plugin = create_mock_plugin_class({
            "name": "productivity",
            "version": "1.0.0",
            "description": "Productivity helpers",
            "author": "Better Notion Team",
            "official": True,
            "category": "productivity",
            "dependencies": [],
            "license": "MIT",
            "homepage": "https://example.com",
            "repository": "https://github.com/example/repo"
        })

        with patch("better_notion.plugins.official.OFFICIAL_PLUGINS", [mock_plugin]):
            result = runner.invoke(app, ["marketplace", "--verbose"])

            assert result.exit_code == 0
            assert "Category: productivity" in result.stdout
            # Check for the checkmark symbol
            assert "Official:" in result.stdout and "Yes" in result.stdout
            # Empty dependencies list is not displayed
            assert "License: MIT" in result.stdout
            assert "Homepage: https://example.com" in result.stdout

    def test_marketplace_json_output(self, runner):
        """Test marketplace with JSON output."""
        mock_plugin = create_mock_plugin_class({
            "name": "productivity",
            "version": "1.0.0",
            "description": "Productivity helpers",
            "author": "Team",
            "official": True,
            "category": "productivity",
            "dependencies": []
        })

        with patch("better_notion.plugins.official.OFFICIAL_PLUGINS", [mock_plugin]):
            result = runner.invoke(app, ["marketplace", "--json"])

            assert result.exit_code == 0

            # Parse JSON
            data = json.loads(result.stdout)
            assert "plugins" in data
            assert len(data["plugins"]) == 1
            assert data["plugins"][0]["name"] == "productivity"

    def test_marketplace_empty_marketplace(self, runner):
        """Test marketplace when no official plugins exist."""
        with patch("better_notion.plugins.official.OFFICIAL_PLUGINS", []):
            result = runner.invoke(app, ["marketplace"])

            assert result.exit_code == 0
            assert "No official plugins available in the marketplace" in result.stdout

    def test_marketplace_short_flags(self, runner):
        """Test marketplace with short flag variants."""
        mock_plugin = create_mock_plugin_class({
            "name": "productivity",
            "version": "1.0.0",
            "description": "Productivity helpers",
            "author": "Team",
            "official": True,
            "category": "productivity",
            "dependencies": []
        })

        # Test -c for category
        with patch("better_notion.plugins.official.OFFICIAL_PLUGINS", [mock_plugin]):
            result = runner.invoke(app, ["marketplace", "-c", "productivity"])
            assert result.exit_code == 0

        # Test -v for verbose
        with patch("better_notion.plugins.official.OFFICIAL_PLUGINS", [mock_plugin]):
            result = runner.invoke(app, ["marketplace", "-v"])
            assert result.exit_code == 0
            assert "Category:" in result.stdout

        # Test -j for JSON
        with patch("better_notion.plugins.official.OFFICIAL_PLUGINS", [mock_plugin]):
            result = runner.invoke(app, ["marketplace", "-j"])
            assert result.exit_code == 0
            data = json.loads(result.stdout)
            assert "plugins" in data

    def test_marketplace_handles_plugin_instantiation_error(self, runner):
        """Test that marketplace handles plugins that fail to instantiate."""

        class BrokenPlugin:
            """Plugin that raises error during instantiation."""

            def __init__(self):
                raise RuntimeError("Cannot instantiate")

            def register_commands(self, app):
                pass

            def get_info(self):
                return {}

        with patch("better_notion.plugins.official.OFFICIAL_PLUGINS", [BrokenPlugin]):
            result = runner.invoke(app, ["marketplace"])

            # Should succeed but show no plugins (due to error handling)
            assert result.exit_code == 0
            assert "Found 0 official plugin(s)" in result.stdout or "No official" in result.stdout

    def test_marketplace_handles_plugin_get_info_error(self, runner):
        """Test that marketplace handles plugins where get_info() fails."""
        mock_plugin = MagicMock()
        mock_plugin.get_info.side_effect = RuntimeError("Cannot get info")

        # Create a class that returns the broken mock
        class BrokenInfoPlugin:
            def __init__(self):
                self.mock = mock_plugin

            def register_commands(self, app):
                pass

            def get_info(self):
                return self.mock.get_info()

        with patch("better_notion.plugins.official.OFFICIAL_PLUGINS", [BrokenInfoPlugin]):
            result = runner.invoke(app, ["marketplace"])

            # Should succeed but skip the failing plugin
            assert result.exit_code == 0

    def test_marketplace_with_dependencies(self, runner):
        """Test marketplace shows plugin dependencies."""
        mock_plugin = create_mock_plugin_class({
            "name": "complex-plugin",
            "version": "1.0.0",
            "description": "A plugin with dependencies",
            "author": "Team",
            "official": True,
            "category": "complex",
            "dependencies": ["requests>=2.0", "click>=8.0"]
        })

        with patch("better_notion.plugins.official.OFFICIAL_PLUGINS", [mock_plugin]):
            result = runner.invoke(app, ["marketplace", "--verbose"])

            assert result.exit_code == 0
            assert "Dependencies: requests>=2.0, click>=8.0" in result.stdout

    def test_marketplace_displays_plugin_count(self, runner):
        """Test that marketplace shows the count of plugins."""
        mock_plugins = [
            create_mock_plugin_class({
                "name": f"plugin-{i}",
                "version": "1.0.0",
                "description": f"Plugin {i}",
                "author": "Team",
                "official": True,
                "category": "test",
                "dependencies": []
            })
            for i in range(1, 4)
        ]

        with patch("better_notion.plugins.official.OFFICIAL_PLUGINS", mock_plugins):
            result = runner.invoke(app, ["marketplace"])

            assert result.exit_code == 0
            assert "Found 3 official plugin(s)" in result.stdout

    def test_marketplace_plugin_numbering(self, runner):
        """Test that marketplace numbers plugins correctly."""
        mock_plugins = [
            create_mock_plugin_class({
                "name": f"plugin-{i}",
                "version": "1.0.0",
                "description": f"Plugin {i}",
                "author": "Team",
                "official": True,
                "category": "test",
                "dependencies": []
            })
            for i in range(1, 4)
        ]

        with patch("better_notion.plugins.official.OFFICIAL_PLUGINS", mock_plugins):
            result = runner.invoke(app, ["marketplace"])

            assert result.exit_code == 0
            assert "1. plugin-1" in result.stdout
            assert "2. plugin-2" in result.stdout
            assert "3. plugin-3" in result.stdout

    def test_marketplace_shows_version_and_author(self, runner):
        """Test that marketplace always shows version and author."""
        mock_plugin = create_mock_plugin_class({
            "name": "test-plugin",
            "version": "2.3.4",
            "description": "Test description",
            "author": "John Doe",
            "official": True,
            "category": "test",
            "dependencies": []
        })

        with patch("better_notion.plugins.official.OFFICIAL_PLUGINS", [mock_plugin]):
            result = runner.invoke(app, ["marketplace"])

            assert result.exit_code == 0
            assert "Version: 2.3.4" in result.stdout
            assert "Author: John Doe" in result.stdout

    def test_marketplace_handles_missing_optional_fields(self, runner):
        """Test marketplace with plugins missing optional metadata."""
        mock_plugin = create_mock_plugin_class({
            "name": "minimal-plugin",
            "version": "1.0.0",
            "description": "Minimal plugin",
            "author": "Team"
            # Missing: official, category, dependencies
        })

        with patch("better_notion.plugins.official.OFFICIAL_PLUGINS", [mock_plugin]):
            result = runner.invoke(app, ["marketplace", "--verbose"])

            assert result.exit_code == 0
            assert "minimal-plugin" in result.stdout
            # Missing category is not displayed in verbose mode
            # The plugin should still be shown
            assert "Version: 1.0.0" in result.stdout
            assert "Author: Team" in result.stdout

    def test_marketplace_shows_tip(self, runner):
        """Test that marketplace shows tip for verbose mode."""
        mock_plugin = create_mock_plugin_class({
            "name": "test-plugin",
            "version": "1.0.0",
            "description": "Test",
            "author": "Team",
            "official": True,
            "category": "test",
            "dependencies": []
        })

        with patch("better_notion.plugins.official.OFFICIAL_PLUGINS", [mock_plugin]):
            result = runner.invoke(app, ["marketplace"])

            assert result.exit_code == 0
            assert "Tip: Use --verbose to see more details" in result.stdout
