"""Tests for Agents CLI commands.

Tests the CRUD and workflow commands for Organizations, Projects,
Versions, and Tasks.
"""

import pytest

from typer.testing import CliRunner

from better_notion.plugins.official.agents_cli import (
    orgs_create,
    orgs_get,
    orgs_list,
    projects_create,
    projects_get,
    projects_list,
    tasks_can_start,
    tasks_claim,
    tasks_complete,
    tasks_create,
    tasks_get,
    tasks_list,
    tasks_next,
    tasks_start,
    versions_create,
    versions_get,
    versions_list,
)


@pytest.mark.integration
class TestOrganizationsCLI:
    """Test Organizations CLI commands."""

    def test_orgs_list(self, mock_client, monkeypatch):
        """Test listing organizations."""
        from better_notion.plugins.official.agents_cli import get_client

        # Mock get_client
        monkeypatch.setattr(
            "better_notion.plugins.official.agents_cli.get_client",
            lambda: mock_client,
        )

        # Mock plugin registration
        def mock_register(plugin):
            mock_client._plugin_models = {}
            mock_client._plugin_caches = {}
            mock_client._plugin_managers = {}

        mock_client.register_sdk_plugin = mock_register

        # Mock manager
        from unittest.mock import MagicMock

        mock_manager = MagicMock()
        mock_manager.list.return_value = []
        mock_client.plugin_manager = lambda name: mock_manager

        result = orgs_list()

        assert "organizations" in result

    def test_orgs_get(self, mock_client, monkeypatch):
        """Test getting an organization."""
        from better_notion.plugins.official.agents_cli import get_client

        monkeypatch.setattr(
            "better_notion.plugins.official.agents_cli.get_client",
            lambda: mock_client,
        )

        # Mock plugin registration
        def mock_register(plugin):
            mock_client._plugin_models = {}
            mock_client._plugin_caches = {}
            mock_client._plugin_managers = {}

        mock_client.register_sdk_plugin = mock_register

        # Mock manager
        from unittest.mock import MagicMock

        mock_org = MagicMock()
        mock_org.id = "org-123"
        mock_org.name = "Test Org"
        mock_org.slug = "test-org"
        mock_org.description = "Test"
        mock_org.repository_url = "https://github.com/test"
        mock_org.status = "Active"

        mock_manager = MagicMock()
        mock_manager.get.return_value = mock_org
        mock_client.plugin_manager = lambda name: mock_manager

        result = orgs_get("org-123")

        assert "org-123" in result

    def test_orgs_create(self, mock_client, monkeypatch):
        """Test creating an organization."""
        from better_notion.plugins.official.agents_cli import get_client

        monkeypatch.setattr(
            "better_notion.plugins.official.agents_cli.get_client",
            lambda: mock_client,
        )

        # Mock plugin registration
        def mock_register(plugin):
            mock_client._plugin_models = {}
            mock_client._plugin_caches = {}
            mock_client._plugin_managers = {}

        mock_client.register_sdk_plugin = mock_register

        # Mock manager
        from unittest.mock import MagicMock

        mock_org = MagicMock()
        mock_org.id = "org-new"
        mock_org.name = "New Org"
        mock_org.slug = "new-org"

        mock_manager = MagicMock()
        mock_manager.create.return_value = mock_org
        mock_client.plugin_manager = lambda name: mock_manager

        result = orgs_create("New Org", slug="new-org")

        assert "created successfully" in result


@pytest.mark.integration
class TestProjectsCLI:
    """Test Projects CLI commands."""

    def test_projects_list(self, mock_client, monkeypatch):
        """Test listing projects."""
        from better_notion.plugins.official.agents_cli import get_client

        monkeypatch.setattr(
            "better_notion.plugins.official.agents_cli.get_client",
            lambda: mock_client,
        )

        # Mock plugin registration
        def mock_register(plugin):
            mock_client._plugin_models = {}
            mock_client._plugin_caches = {}
            mock_client._plugin_managers = {}

        mock_client.register_sdk_plugin = mock_register

        # Mock manager
        from unittest.mock import MagicMock

        mock_manager = MagicMock()
        mock_manager.list.return_value = []
        mock_client.plugin_manager = lambda name: mock_manager

        result = projects_list()

        assert "projects" in result


@pytest.mark.integration
class TestVersionsCLI:
    """Test Versions CLI commands."""

    def test_versions_list(self, mock_client, monkeypatch):
        """Test listing versions."""
        from better_notion.plugins.official.agents_cli import get_client

        monkeypatch.setattr(
            "better_notion.plugins.official.agents_cli.get_client",
            lambda: mock_client,
        )

        # Mock plugin registration
        def mock_register(plugin):
            mock_client._plugin_models = {}
            mock_client._plugin_caches = {}
            mock_client._plugin_managers = {}

        mock_client.register_sdk_plugin = mock_register

        # Mock manager
        from unittest.mock import MagicMock

        mock_manager = MagicMock()
        mock_manager.list.return_value = []
        mock_client.plugin_manager = lambda name: mock_manager

        result = versions_list()

        assert "versions" in result


@pytest.mark.integration
class TestTasksCLI:
    """Test Tasks CLI commands."""

    def test_tasks_list(self, mock_client, monkeypatch):
        """Test listing tasks."""
        from better_notion.plugins.official.agents_cli import get_client

        monkeypatch.setattr(
            "better_notion.plugins.official.agents_cli.get_client",
            lambda: mock_client,
        )

        # Mock plugin registration
        def mock_register(plugin):
            mock_client._plugin_models = {}
            mock_client._plugin_caches = {}
            mock_client._plugin_managers = {}

        mock_client.register_sdk_plugin = mock_register

        # Mock manager
        from unittest.mock import MagicMock

        mock_manager = MagicMock()
        mock_manager.list.return_value = []
        mock_client.plugin_manager = lambda name: mock_manager

        result = tasks_list()

        assert "tasks" in result

    def test_tasks_next(self, mock_client, monkeypatch):
        """Test finding next task."""
        from better_notion.plugins.official.agents_cli import get_client

        monkeypatch.setattr(
            "better_notion.plugins.official.agents_cli.get_client",
            lambda: mock_client,
        )

        # Mock plugin registration
        def mock_register(plugin):
            mock_client._plugin_models = {}
            mock_client._plugin_caches = {}
            mock_client._plugin_managers = {}

        mock_client.register_sdk_plugin = mock_register

        # Mock manager
        from unittest.mock import MagicMock

        mock_manager = MagicMock()
        mock_manager.next.return_value = None
        mock_client.plugin_manager = lambda name: mock_manager

        result = tasks_next()

        assert "available tasks" in result

    def test_tasks_claim(self, mock_client, monkeypatch):
        """Test claiming a task."""
        from better_notion.plugins.official.agents_cli import get_client, get_or_create_agent_id

        monkeypatch.setattr(
            "better_notion.plugins.official.agents_cli.get_client",
            lambda: mock_client,
        )
        monkeypatch.setattr(
            "better_notion.plugins.official.agents_cli.get_or_create_agent_id",
            lambda: "agent-123",
        )

        # Mock plugin registration
        def mock_register(plugin):
            mock_client._plugin_models = {}
            mock_client._plugin_caches = {}
            mock_client._plugin_managers = {}

        mock_client.register_sdk_plugin = mock_register

        # Mock task
        from unittest.mock import MagicMock, AsyncMock

        mock_task = MagicMock()
        mock_task.id = "task-123"
        mock_task.title = "Test Task"
        mock_task.status = "Claimed"
        mock_task.claim = AsyncMock(return_value=mock_task)

        mock_manager = MagicMock()
        mock_manager.get = AsyncMock(return_value=mock_task)
        mock_client.plugin_manager = lambda name: mock_manager

        result = tasks_claim("task-123")

        assert "claimed" in result

    def test_tasks_start(self, mock_client, monkeypatch):
        """Test starting a task."""
        from better_notion.plugins.official.agents_cli import get_client, get_or_create_agent_id

        monkeypatch.setattr(
            "better_notion.plugins.official.agents_cli.get_client",
            lambda: mock_client,
        )
        monkeypatch.setattr(
            "better_notion.plugins.official.agents_cli.get_or_create_agent_id",
            lambda: "agent-123",
        )

        # Mock plugin registration
        def mock_register(plugin):
            mock_client._plugin_models = {}
            mock_client._plugin_caches = {}
            mock_client._plugin_managers = {}

        mock_client.register_sdk_plugin = mock_register

        # Mock task
        from unittest.mock import MagicMock, AsyncMock

        mock_task = MagicMock()
        mock_task.id = "task-123"
        mock_task.title = "Test Task"
        mock_task.status = "In Progress"
        mock_task.can_start = AsyncMock(return_value=True)
        mock_task.start = AsyncMock(return_value=mock_task)

        mock_manager = MagicMock()
        mock_manager.get = AsyncMock(return_value=mock_task)
        mock_client.plugin_manager = lambda name: mock_manager

        result = tasks_start("task-123")

        assert "started" in result

    def test_tasks_complete(self, mock_client, monkeypatch):
        """Test completing a task."""
        from better_notion.plugins.official.agents_cli import get_client, get_or_create_agent_id

        monkeypatch.setattr(
            "better_notion.plugins.official.agents_cli.get_client",
            lambda: mock_client,
        )
        monkeypatch.setattr(
            "better_notion.plugins.official.agents_cli.get_or_create_agent_id",
            lambda: "agent-123",
        )

        # Mock plugin registration
        def mock_register(plugin):
            mock_client._plugin_models = {}
            mock_client._plugin_caches = {}
            mock_client._plugin_managers = {}

        mock_client.register_sdk_plugin = mock_register

        # Mock task
        from unittest.mock import MagicMock, AsyncMock

        mock_task = MagicMock()
        mock_task.id = "task-123"
        mock_task.title = "Test Task"
        mock_task.status = "Completed"
        mock_task.actual_hours = 3
        mock_task.complete = AsyncMock(return_value=mock_task)

        mock_manager = MagicMock()
        mock_manager.get = AsyncMock(return_value=mock_task)
        mock_client.plugin_manager = lambda name: mock_manager

        result = tasks_complete("task-123", actual_hours=3)

        assert "completed" in result

    def test_tasks_can_start(self, mock_client, monkeypatch):
        """Test checking if task can start."""
        from better_notion.plugins.official.agents_cli import get_client

        monkeypatch.setattr(
            "better_notion.plugins.official.agents_cli.get_client",
            lambda: mock_client,
        )

        # Mock plugin registration
        def mock_register(plugin):
            mock_client._plugin_models = {}
            mock_client._plugin_caches = {}
            mock_client._plugin_managers = {}

        mock_client.register_sdk_plugin = mock_register

        # Mock task
        from unittest.mock import MagicMock, AsyncMock

        mock_task = MagicMock()
        mock_task.id = "task-123"
        mock_task.can_start = AsyncMock(return_value=True)
        mock_task.dependencies = AsyncMock(return_value=[])

        mock_manager = MagicMock()
        mock_manager.get = AsyncMock(return_value=mock_task)
        mock_client.plugin_manager = lambda name: mock_manager

        result = tasks_can_start("task-123")

        assert "can_start" in result


@pytest.fixture
def mock_client():
    """Create a mock NotionClient."""
    from unittest.mock import MagicMock

    from better_notion._sdk.client import NotionClient

    client = MagicMock(spec=NotionClient)
    client._api = MagicMock()

    return client
