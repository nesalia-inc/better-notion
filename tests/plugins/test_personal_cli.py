"""Tests for Personal CLI commands.

Tests the CRUD and workflow commands for Domains, Tags, Projects,
Tasks, Routines, and Agenda.
"""

import pytest
from unittest.mock import MagicMock, AsyncMock, patch
from typer.testing import CliRunner

from better_notion.plugins.official.personal_cli import (
    domains_list,
    domains_create,
    tags_list,
    tags_create,
    tags_get,
    tasks_add,
    tasks_list,
    tasks_get,
    tasks_update,
    tasks_done,
    tasks_delete,
    tasks_subtasks,
    tasks_archive,
    projects_list,
    projects_get,
    projects_create,
    projects_delete,
    routines_list,
    routines_create,
    routines_check,
    routines_stats,
    agenda_show,
    agenda_add,
    agenda_timeblock,
    search,
    archive_tasks,
    archive_list,
    archive_restore,
    archive_purge,
    review_daily,
    review_weekly,
    review_monthly,
)


@pytest.fixture
def mock_client():
    """Create a mock NotionClient."""
    from unittest.mock import MagicMock, AsyncMock
    from better_notion._sdk.client import NotionClient

    client = MagicMock(spec=NotionClient)

    # Create mock API with async methods
    mock_api = MagicMock()
    mock_databases = MagicMock()
    mock_databases.query = AsyncMock(return_value={"results": []})
    mock_api.databases = mock_databases
    mock_api._request = AsyncMock(return_value={"results": []})
    client._api = mock_api

    return client


@pytest.mark.integration
class TestDomainsCLI:
    """Test Domains CLI commands."""

    def test_domains_list_empty(self, mock_client, monkeypatch):
        """Test listing domains when no domains exist."""
        from better_notion.plugins.official.personal_cli import get_client

        monkeypatch.setattr(
            "better_notion.plugins.official.personal_cli.get_client",
            lambda: mock_client,
        )

        # Mock workspace config
        monkeypatch.setattr(
            "better_notion.plugins.official.personal_cli.get_workspace_config",
            lambda: {
                "database_ids": {"domains": "db-123"},
                "workspace_id": "test-workspace",
            },
        )

        # mock_client._api.databases.query already returns {"results": []} from fixture

        result = domains_list()

        assert '"count": 0' in result

    def test_domains_list_with_domains(self, mock_client, monkeypatch):
        """Test listing domains with existing domains."""
        from better_notion.plugins.official.personal_cli import get_client

        monkeypatch.setattr(
            "better_notion.plugins.official.personal_cli.get_client",
            lambda: mock_client,
        )

        # Mock workspace config
        monkeypatch.setattr(
            "better_notion.plugins.official.personal_cli.get_workspace_config",
            lambda: {
                "database_ids": {"domains": "db-123"},
                "workspace_id": "test-workspace",
            },
        )

        # Override databases.query to return domain data
        mock_domain_data = {
            "object": "page",
            "id": "domain-123",
            "created_time": "2025-01-15T00:00:00.000Z",
            "last_edited_time": "2025-01-15T00:00:00.000Z",
            "archived": False,
            "properties": {
                "Name": {
                    "type": "title",
                    "title": [{"type": "text", "text": {"content": "Work"}}]
                },
                "Description": {
                    "type": "rich_text",
                    "rich_text": [{"type": "text", "text": {"content": "Professional tasks"}}]
                },
                "Color": {
                    "type": "select",
                    "select": {"name": "Blue"}
                },
            },
        }

        mock_client._api.databases.query = AsyncMock(return_value={"results": [mock_domain_data]})

        result = domains_list()

        assert '"count": 1' in result
        assert "Work" in result

    def test_domains_create(self, mock_client, monkeypatch):
        """Test creating a new domain."""
        from better_notion.plugins.official.personal_cli import get_client
        from better_notion.plugins.official.personal_sdk.models import Domain

        monkeypatch.setattr(
            "better_notion.plugins.official.personal_cli.get_client",
            lambda: mock_client,
        )

        # Mock workspace config
        monkeypatch.setattr(
            "better_notion.plugins.official.personal_cli.get_workspace_config",
            lambda: {
                "database_ids": {"domains": "db-123"},
                "workspace_id": "test-workspace",
            },
        )

        # Mock Domain.create
        mock_domain = MagicMock()
        mock_domain.id = "domain-123"
        mock_domain.name = "Finance"
        mock_domain.description = "Financial management"
        mock_domain.color = "Green"

        with patch.object(Domain, 'create', new_callable=AsyncMock) as mock_create:
            mock_create.return_value = mock_domain

            result = domains_create("Finance", "Financial management", "Green")

            assert "domain-123" in result
            assert "Finance" in result

    def test_domains_list_not_initialized(self, mock_client, monkeypatch):
        """Test listing domains when workspace not initialized."""
        from better_notion.plugins.official.personal_cli import get_client

        monkeypatch.setattr(
            "better_notion.plugins.official.personal_cli.get_client",
            lambda: mock_client,
        )

        # Mock empty workspace config
        monkeypatch.setattr(
            "better_notion.plugins.official.personal_cli.get_workspace_config",
            lambda: {},
        )

        result = domains_list()

        assert "NOT_INITIALIZED" in result


@pytest.mark.integration
class TestTagsCLI:
    """Test Tags CLI commands."""

    def test_tags_list_empty(self, mock_client, monkeypatch):
        """Test listing tags when no tags exist."""
        from better_notion.plugins.official.personal_cli import get_client

        monkeypatch.setattr(
            "better_notion.plugins.official.personal_cli.get_client",
            lambda: mock_client,
        )

        # Mock workspace config
        monkeypatch.setattr(
            "better_notion.plugins.official.personal_cli.get_workspace_config",
            lambda: {
                "database_ids": {"tags": "db-123"},
                "workspace_id": "test-workspace",
            },
        )

        # Mock API response
        mock_response = MagicMock()
        mock_response.get.return_value = {"results": []}
        mock_client._api = MagicMock()
        mock_client._api.databases = MagicMock()
        mock_client._api.databases.query = AsyncMock(return_value=mock_response)

        result = tags_list()

        assert '"count": 0' in result

    def test_tags_create(self, mock_client, monkeypatch):
        """Test creating a new tag."""
        from better_notion.plugins.official.personal_cli import get_client
        from better_notion.plugins.official.personal_sdk.models import Tag

        monkeypatch.setattr(
            "better_notion.plugins.official.personal_cli.get_client",
            lambda: mock_client,
        )

        # Mock workspace config
        monkeypatch.setattr(
            "better_notion.plugins.official.personal_cli.get_workspace_config",
            lambda: {
                "database_ids": {"tags": "db-123"},
                "workspace_id": "test-workspace",
            },
        )

        # Mock Tag.create
        mock_tag = MagicMock()
        mock_tag.id = "tag-123"
        mock_tag.name = "@phone"
        mock_tag.category = "Context"
        mock_tag.color = "Blue"
        mock_tag.description = "Phone tasks"

        with patch.object(Tag, 'create', new_callable=AsyncMock) as mock_create:
            mock_create.return_value = mock_tag

            result = tags_create("@phone", "Context", "Blue")

            assert "tag-123" in result
            assert "@phone" in result


@pytest.mark.integration
class TestTasksCLI:
    """Test Tasks CLI commands."""

    def test_tasks_add(self, mock_client, monkeypatch):
        """Test adding a new task."""
        from better_notion.plugins.official.personal_cli import get_client
        from better_notion.plugins.official.personal_sdk.models import Task

        monkeypatch.setattr(
            "better_notion.plugins.official.personal_cli.get_client",
            lambda: mock_client,
        )

        # Mock workspace config
        monkeypatch.setattr(
            "better_notion.plugins.official.personal_cli.get_workspace_config",
            lambda: {
                "database_ids": {"tasks": "db-123"},
                "workspace_id": "test-workspace",
            },
        )

        # Mock Task.create
        mock_task = MagicMock()
        mock_task.id = "task-123"
        mock_task.title = "Buy groceries"
        mock_task.priority = "Medium"

        with patch.object(Task, 'create', new_callable=AsyncMock) as mock_create:
            mock_create.return_value = mock_task

            result = tasks_add("Buy groceries", "Medium", None, None, None, None, None, None)

            assert "task-123" in result
            assert "Buy groceries" in result

    def test_tasks_list(self, mock_client, monkeypatch):
        """Test listing tasks."""
        from better_notion.plugins.official.personal_cli import get_client

        monkeypatch.setattr(
            "better_notion.plugins.official.personal_cli.get_client",
            lambda: mock_client,
        )

        # Mock workspace config
        monkeypatch.setattr(
            "better_notion.plugins.official.personal_cli.get_workspace_config",
            lambda: {
                "database_ids": {"tasks": "db-123"},
                "workspace_id": "test-workspace",
            },
        )

        # Mock API response
        mock_task_data = {
            "id": "task-123",
            "properties": {
                "Title": {"title": [{"plain_text": "Buy groceries"}]},
                "Status": {"select": {"name": "Todo"}},
                "Priority": {"select": {"name": "Medium"}},
            },
        }

        mock_response = MagicMock()
        mock_response.get.return_value = {"results": [mock_task_data]}
        mock_client._api = MagicMock()
        mock_client._api.databases = MagicMock()
        mock_client._api.databases.query = AsyncMock(return_value=mock_response)

        result = tasks_list()

        assert "Buy groceries" in result

    def test_tasks_done(self, mock_client, monkeypatch):
        """Test marking a task as done."""
        from better_notion.plugins.official.personal_cli import get_client
        from better_notion.plugins.official.personal_sdk.models import Task

        monkeypatch.setattr(
            "better_notion.plugins.official.personal_cli.get_client",
            lambda: mock_client,
        )

        # Mock workspace config
        monkeypatch.setattr(
            "better_notion.plugins.official.personal_cli.get_workspace_config",
            lambda: {
                "database_ids": {"tasks": "db-123"},
                "workspace_id": "test-workspace",
            },
        )

        # Mock task
        mock_task = MagicMock()
        mock_task.id = "task-123"
        mock_task.mark_done = AsyncMock()

        with patch.object(Task, 'get', new_callable=AsyncMock) as mock_get:
            mock_get.return_value = mock_task

            result = tasks_done("task-123")

            assert "Done" in result
            mock_task.mark_done.assert_called_once()


@pytest.mark.integration
class TestProjectsCLI:
    """Test Projects CLI commands."""

    def test_projects_create(self, mock_client, monkeypatch):
        """Test creating a new project."""
        from better_notion.plugins.official.personal_cli import get_client
        from better_notion.plugins.official.personal_sdk.models import Project

        monkeypatch.setattr(
            "better_notion.plugins.official.personal_cli.get_client",
            lambda: mock_client,
        )

        # Mock workspace config
        monkeypatch.setattr(
            "better_notion.plugins.official.personal_cli.get_workspace_config",
            lambda: {
                "database_ids": {"projects": "db-123", "domains": "domain-123"},
                "workspace_id": "test-workspace",
            },
        )

        # Mock Project.create
        mock_project = MagicMock()
        mock_project.id = "project-123"
        mock_project.name = "Get in shape"

        with patch.object(Project, 'create', new_callable=AsyncMock) as mock_create:
            mock_create.return_value = mock_project

            result = projects_create("Get in shape", "Health", "High", None)

            assert "project-123" in result
            assert "Get in shape" in result


@pytest.mark.integration
class TestRoutinesCLI:
    """Test Routines CLI commands."""

    def test_routines_create(self, mock_client, monkeypatch):
        """Test creating a new routine."""
        from better_notion.plugins.official.personal_cli import get_client
        from better_notion.plugins.official.personal_sdk.models import Routine

        monkeypatch.setattr(
            "better_notion.plugins.official.personal_cli.get_client",
            lambda: mock_client,
        )

        # Mock workspace config
        monkeypatch.setattr(
            "better_notion.plugins.official.personal_cli.get_workspace_config",
            lambda: {
                "database_ids": {"routines": "db-123", "domains": "domain-123"},
                "workspace_id": "test-workspace",
            },
        )

        # Mock Routine.create
        mock_routine = MagicMock()
        mock_routine.id = "routine-123"
        mock_routine.name = "Morning meditation"

        with patch.object(Routine, 'create', new_callable=AsyncMock) as mock_create:
            mock_create.return_value = mock_routine

            result = routines_create("Morning meditation", "Daily", "Health", "Morning", 10)

            assert "routine-123" in result
            assert "Morning meditation" in result

    def test_routines_check(self, mock_client, monkeypatch):
        """Test checking off a routine."""
        from better_notion.plugins.official.personal_cli import get_client
        from better_notion.plugins.official.personal_sdk.models import Routine

        monkeypatch.setattr(
            "better_notion.plugins.official.personal_cli.get_client",
            lambda: mock_client,
        )

        # Mock workspace config
        monkeypatch.setattr(
            "better_notion.plugins.official.personal_cli.get_workspace_config",
            lambda: {
                "database_ids": {"routines": "db-123"},
                "workspace_id": "test-workspace",
            },
        )

        # Mock routine
        mock_routine = MagicMock()
        mock_routine.id = "routine-123"
        mock_routine.check_off = AsyncMock(return_value=1)

        with patch.object(Routine, 'get', new_callable=AsyncMock) as mock_get:
            mock_get.return_value = mock_routine

            result = routines_check("routine-123")

            assert "checked" in result.lower()
            mock_routine.check_off.assert_called_once()


@pytest.mark.integration
class TestAgendaCLI:
    """Test Agenda CLI commands."""

    def test_agenda_show_today(self, mock_client, monkeypatch):
        """Test showing today's agenda."""
        from better_notion.plugins.official.personal_cli import get_client

        monkeypatch.setattr(
            "better_notion.plugins.official.personal_cli.get_client",
            lambda: mock_client,
        )

        # Mock workspace config
        monkeypatch.setattr(
            "better_notion.plugins.official.personal_cli.get_workspace_config",
            lambda: {
                "database_ids": {"agenda": "db-123"},
                "workspace_id": "test-workspace",
            },
        )

        # Mock API response
        mock_response = MagicMock()
        mock_response.get.return_value = {"results": []}
        mock_client._api = MagicMock()
        mock_client._api.databases = MagicMock()
        mock_client._api.databases.query = AsyncMock(return_value=mock_response)

        result = agenda_show()

        assert "agenda" in result.lower()


@pytest.mark.integration
class TestSearchCLI:
    """Test Search CLI command."""

    def test_search(self, mock_client, monkeypatch):
        """Test searching tasks."""
        from better_notion.plugins.official.personal_cli import get_client

        monkeypatch.setattr(
            "better_notion.plugins.official.personal_cli.get_client",
            lambda: mock_client,
        )

        # Mock workspace config
        monkeypatch.setattr(
            "better_notion.plugins.official.personal_cli.get_workspace_config",
            lambda: {
                "database_ids": {"tasks": "db-123"},
                "workspace_id": "test-workspace",
            },
        )

        # Mock API response
        mock_response = MagicMock()
        mock_response.get.return_value = {"results": []}
        mock_client._api = MagicMock()
        mock_client._api.databases = MagicMock()
        mock_client._api.databases.query = AsyncMock(return_value=mock_response)

        result = search("gym")

        assert "results" in result.lower() or "search" in result.lower()


@pytest.mark.integration
class TestArchiveCLI:
    """Test Archive CLI commands."""

    def test_archive_list(self, mock_client, monkeypatch):
        """Test listing archived tasks."""
        from better_notion.plugins.official.personal_cli import get_client

        monkeypatch.setattr(
            "better_notion.plugins.official.personal_cli.get_client",
            lambda: mock_client,
        )

        # Mock workspace config
        monkeypatch.setattr(
            "better_notion.plugins.official.personal_cli.get_workspace_config",
            lambda: {
                "database_ids": {"tasks": "db-123"},
                "workspace_id": "test-workspace",
            },
        )

        # Mock API response
        mock_response = MagicMock()
        mock_response.get.return_value = {"results": []}
        mock_client._api = MagicMock()
        mock_client._api.databases = MagicMock()
        mock_client._api.databases.query = AsyncMock(return_value=mock_response)

        result = archive_list()

        assert "archive" in result.lower()


@pytest.mark.integration
class TestReviewCLI:
    """Test Review CLI commands."""

    def test_review_daily(self):
        """Test daily review command."""
        result = review_daily()

        assert "review" in result.lower()

    def test_review_weekly(self):
        """Test weekly review command."""
        result = review_weekly()

        assert "review" in result.lower()

    def test_review_monthly(self):
        """Test monthly review command."""
        result = review_monthly()

        assert "review" in result.lower()
