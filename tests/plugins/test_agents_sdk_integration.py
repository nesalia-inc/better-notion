"""Integration tests for Agents SDK Plugin.

Tests the full plugin registration and workflow.
"""

import pytest

from better_notion.plugins.official.agents_sdk.plugin import AgentsSDKPlugin
from better_notion._sdk.client import NotionClient


@pytest.mark.integration
class TestAgentsSDKPlugin:
    """Test AgentsSDKPlugin registration and workflow."""

    def test_plugin_info(self):
        """Test plugin metadata."""
        plugin = AgentsSDKPlugin()
        info = plugin.get_info()

        assert info["name"] == "agents-sdk"
        assert info["version"] == "1.0.0"
        assert "description" in info
        assert "author" in info

    def test_register_models(self):
        """Test model registration."""
        plugin = AgentsSDKPlugin()
        models = plugin.register_models()

        assert "Organization" in models
        assert "Project" in models
        assert "Version" in models
        assert "Task" in models

    def test_register_caches(self, mock_client):
        """Test cache registration."""
        plugin = AgentsSDKPlugin()
        caches = plugin.register_caches(mock_client)

        assert "organizations" in caches
        assert "projects" in caches
        assert "versions" in caches
        assert "tasks" in caches

    def test_register_managers(self, mock_client):
        """Test manager registration."""
        plugin = AgentsSDKPlugin()
        managers = plugin.register_managers(mock_client)

        assert "organizations" in managers
        assert "projects" in managers
        assert "versions" in managers
        assert "tasks" in managers

    def test_initialize_with_config(self, mock_client, tmp_path):
        """Test plugin initialization with workspace config."""
        import json

        # Create temporary workspace config
        config_file = tmp_path / "workspace.json"
        config_data = {
            "Organizations": "db-org-123",
            "Projects": "db-proj-123",
            "Versions": "db-ver-123",
            "Tasks": "db-task-123",
        }
        config_file.write_text(json.dumps(config_data))

        plugin = AgentsSDKPlugin()

        # Mock Path.home to return tmp_path
        from unittest.mock import patch

        with patch("pathlib.Path", lambda *args, **kwargs: tmp_path):
            plugin.initialize(mock_client)

        assert hasattr(mock_client, "_workspace_config")
        assert mock_client._workspace_config["Organizations"] == "db-org-123"

    def test_initialize_without_config(self, mock_client):
        """Test plugin initialization without workspace config."""
        from unittest.mock import patch

        plugin = AgentsSDKPlugin()

        # Mock Path.home to return non-existent config
        with patch("pathlib.Path.home") as mock_home:
            mock_home.return_value = "/nonexistent"

            plugin.initialize(mock_client)

        assert hasattr(mock_client, "_workspace_config")
        assert mock_client._workspace_config == {}

    def test_client_registration(self, mock_client):
        """Test full client registration workflow."""
        plugin = AgentsSDKPlugin()

        # Register models
        models = plugin.register_models()
        mock_client._plugin_models = {}

        for name, model_class in models.items():
            mock_client._plugin_models[name] = model_class

        assert "Organization" in mock_client._plugin_models
        assert "Project" in mock_client._plugin_models

        # Register caches
        caches = plugin.register_caches(mock_client)
        mock_client._plugin_caches = caches

        assert "organizations" in mock_client._plugin_caches
        assert "projects" in mock_client._plugin_caches

        # Register managers
        managers = plugin.register_managers(mock_client)
        mock_client._plugin_managers = managers

        assert "organizations" in mock_client._plugin_managers
        assert "projects" in mock_client._plugin_managers


@pytest.fixture
def mock_client():
    """Create a mock NotionClient."""
    from unittest.mock import MagicMock

    from better_notion._sdk.client import NotionClient

    client = MagicMock(spec=NotionClient)
    client._api = MagicMock()

    return client
