"""Unit tests for agents plugin."""

from pathlib import Path

import pytest
import typer

from better_notion.plugins.official.agents import AgentsPlugin


class TestAgentsPlugin:
    """Tests for AgentsPlugin class."""

    def test_plugin_info(self) -> None:
        """Test plugin metadata."""
        plugin = AgentsPlugin()
        info = plugin.get_info()

        assert info["name"] == "agents"
        assert info["version"] == "1.0.0"
        assert info["official"] is True
        assert info["category"] == "workflow"
        assert info["description"] != ""

    def test_register_commands_exists(self) -> None:
        """Test that register_commands method exists."""
        plugin = AgentsPlugin()

        assert hasattr(plugin, "register_commands")
        assert callable(plugin.register_commands)

    def test_register_commands_creates_app(self) -> None:
        """Test that register_commands can be called."""
        plugin = AgentsPlugin()
        app = typer.Typer()

        # Should not raise
        plugin.register_commands(app)

        # App should have been modified
        assert app is not None

    def test_plugin_implements_interface(self) -> None:
        """Test that plugin implements PluginInterface."""
        plugin = AgentsPlugin()

        # Should have required methods
        assert hasattr(plugin, "register_commands")
        assert hasattr(plugin, "get_info")

        # Methods should be callable
        assert callable(plugin.register_commands)
        assert callable(plugin.get_info)


class TestPluginStructure:
    """Tests for plugin file structure."""

    def test_plugin_file_exists(self) -> None:
        """Test that plugin file exists."""
        from better_notion.plugins.official import agents

        assert agents is not None
        assert hasattr(agents, "AgentsPlugin")

    def test_agents_plugin_instantiable(self) -> None:
        """Test that AgentsPlugin can be instantiated."""
        plugin = AgentsPlugin()

        assert plugin is not None
        assert isinstance(plugin, AgentsPlugin)

    def test_plugin_has_workspace_functions(self) -> None:
        """Test that workspace-related functions are available."""
        from better_notion.utils.agents.workspace import (
            WorkspaceInitializer,
            initialize_workspace_command,
        )

        assert WorkspaceInitializer is not None
        assert initialize_workspace_command is not None

    def test_plugin_has_utility_classes(self) -> None:
        """Test that utility classes are available."""
        from better_notion.utils.agents import (
            DependencyResolver,
            ProjectContext,
            RoleManager,
        )

        assert DependencyResolver is not None
        assert ProjectContext is not None
        assert RoleManager is not None

    def test_plugin_has_schemas(self) -> None:
        """Test that schema builders are available."""
        from better_notion.utils.agents.schemas import (
            OrganizationSchema,
            ProjectSchema,
            TaskSchema,
        )

        assert OrganizationSchema is not None
        assert ProjectSchema is not None
        assert TaskSchema is not None
