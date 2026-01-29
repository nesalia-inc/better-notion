"""Tests for Agents SDK Plugin managers.

Tests OrganizationManager, ProjectManager, VersionManager, TaskManager,
IdeaManager, WorkIssueManager, and IncidentManager.
"""

import pytest

from better_notion.plugins.official.agents_sdk.managers import (
    IdeaManager,
    IncidentManager,
    OrganizationManager,
    ProjectManager,
    TaskManager,
    VersionManager,
    WorkIssueManager,
)


@pytest.mark.unit
class TestOrganizationManager:
    """Test OrganizationManager."""

    def test_init(self, mock_client):
        """Test manager initialization."""
        manager = OrganizationManager(mock_client)
        assert manager._client == mock_client

    @pytest.mark.asyncio
    async def test_list(self, mock_client):
        """Test listing organizations."""
        # Mock workspace config
        mock_client._workspace_config = {"Organizations": "db-123"}

        # Mock API response
        mock_client._api.databases.query.return_value = {
            "results": [
                {
                    "id": "org-1",
                    "object": "page",
                    "properties": {
                        "Name": {"type": "title", "title": [{"plain_text": "Org 1"}]},
                        "Slug": {"type": "rich_text", "rich_text": []},
                        "Description": {"type": "rich_text", "rich_text": []},
                        "Status": {"type": "select", "select": {"name": "Active"}},
                    },
                },
                {
                    "id": "org-2",
                    "object": "page",
                    "properties": {
                        "Name": {"type": "title", "title": [{"plain_text": "Org 2"}]},
                        "Slug": {"type": "rich_text", "rich_text": []},
                        "Description": {"type": "rich_text", "rich_text": []},
                        "Status": {"type": "select", "select": {"name": "Active"}},
                    },
                },
            ],
        }

        manager = OrganizationManager(mock_client)
        orgs = await manager.list()

        assert len(orgs) == 2
        assert orgs[0].id == "org-1"
        assert orgs[1].id == "org-2"

    @pytest.mark.asyncio
    async def test_list_no_config(self, mock_client):
        """Test listing organizations with no workspace config."""
        mock_client._workspace_config = {}

        manager = OrganizationManager(mock_client)
        orgs = await manager.list()

        assert orgs == []


@pytest.mark.unit
class TestProjectManager:
    """Test ProjectManager."""

    def test_init(self, mock_client):
        """Test manager initialization."""
        manager = ProjectManager(mock_client)
        assert manager._client == mock_client

    @pytest.mark.asyncio
    async def test_list_filtered_by_organization(self, mock_client):
        """Test listing projects filtered by organization."""
        mock_client._workspace_config = {"Projects": "db-123"}

        mock_client._api.databases.query.return_value = {
            "results": [
                {
                    "id": "proj-1",
                    "object": "page",
                    "properties": {
                        "Name": {"type": "title", "title": [{"plain_text": "Project 1"}]},
                        "Status": {"type": "select", "select": {"name": "Active"}},
                        "Role": {"type": "select", "select": {"name": "Developer"}},
                        "Organization": {"type": "relation", "relation": [{"id": "org-1"}]},
                    },
                },
            ],
        }

        manager = ProjectManager(mock_client)
        projects = await manager.list(organization_id="org-1")

        assert len(projects) == 1
        assert projects[0].id == "proj-1"

        # Verify API was called with correct filter
        mock_client._api.databases.query.assert_called_once()
        call_kwargs = mock_client._api.databases.query.call_args.kwargs
        assert call_kwargs["filter"]["relation"]["contains"] == "org-1"


@pytest.mark.unit
class TestVersionManager:
    """Test VersionManager."""

    def test_init(self, mock_client):
        """Test manager initialization."""
        manager = VersionManager(mock_client)
        assert manager._client == mock_client

    @pytest.mark.asyncio
    async def test_list_filtered_by_project(self, mock_client):
        """Test listing versions filtered by project."""
        mock_client._workspace_config = {"Versions": "db-123"}

        mock_client._api.databases.query.return_value = {
            "results": [
                {
                    "id": "ver-1",
                    "object": "page",
                    "properties": {
                        "Version": {"type": "title", "title": [{"plain_text": "v1.0.0"}]},
                        "Status": {"type": "select", "select": {"name": "In Progress"}},
                        "Type": {"type": "select", "select": {"name": "Minor"}},
                        "Progress": {"type": "number", "number": 50},
                        "Project": {"type": "relation", "relation": [{"id": "proj-1"}]},
                    },
                },
            ],
        }

        manager = VersionManager(mock_client)
        versions = await manager.list(project_id="proj-1")

        assert len(versions) == 1
        assert versions[0].id == "ver-1"


@pytest.mark.unit
class TestTaskManager:
    """Test TaskManager."""

    def test_init(self, mock_client):
        """Test manager initialization."""
        manager = TaskManager(mock_client)
        assert manager._client == mock_client

    @pytest.mark.asyncio
    async def test_list_filtered(self, mock_client):
        """Test listing tasks with filters."""
        mock_client._workspace_config = {"Tasks": "db-123"}

        mock_client._api.databases.query.return_value = {
            "results": [
                {
                    "id": "task-1",
                    "object": "page",
                    "properties": {
                        "Title": {"type": "title", "title": [{"plain_text": "Task 1"}]},
                        "Status": {"type": "select", "select": {"name": "In Progress"}},
                        "Type": {"type": "select", "select": {"name": "New Feature"}},
                        "Priority": {"type": "select", "select": {"name": "High"}},
                        "Version": {"type": "relation", "relation": [{"id": "ver-1"}]},
                        "Dependencies": {"type": "relation", "relation": []},
                    },
                },
            ],
        }

        manager = TaskManager(mock_client)
        tasks = await manager.list(version_id="ver-1", status="In Progress")

        assert len(tasks) == 1
        assert tasks[0].id == "task-1"

        # Verify API was called with correct filter
        mock_client._api.databases.query.assert_called_once()
        call_kwargs = mock_client._api.databases.query.call_args.kwargs
        assert call_kwargs["filter"] is not None

    @pytest.mark.asyncio
    async def test_next_ready_task(self, mock_client):
        """Test finding next ready task."""
        mock_client._workspace_config = {"Tasks": "db-123"}

        # Mock API response with backlog tasks
        mock_client._api.databases.query.return_value = {
            "results": [
                {
                    "id": "task-1",
                    "object": "page",
                    "properties": {
                        "Title": {"type": "title", "title": [{"plain_text": "Ready Task"}]},
                        "Status": {"type": "select", "select": {"name": "Backlog"}},
                        "Type": {"type": "select", "select": {"name": "New Feature"}},
                        "Priority": {"type": "select", "select": {"name": "High"}},
                        "Version": {"type": "relation", "relation": [{"id": "ver-1"}]},
                        "Dependencies": {"type": "relation", "relation": []},
                    },
                },
            ],
        }

        manager = TaskManager(mock_client)
        task = await manager.next()

        assert task is not None
        assert task.id == "task-1"

    @pytest.mark.asyncio
    async def test_find_ready_tasks(self, mock_client):
        """Test finding all ready tasks."""
        mock_client._workspace_config = {"Tasks": "db-123"}

        mock_client._api.databases.query.return_value = {
            "results": [
                {
                    "id": "task-1",
                    "object": "page",
                    "properties": {
                        "Title": {"type": "title", "title": [{"plain_text": "Task 1"}]},
                        "Status": {"type": "select", "select": {"name": "Backlog"}},
                        "Type": {"type": "select", "select": {"name": "New Feature"}},
                        "Priority": {"type": "select", "select": {"name": "Medium"}},
                        "Version": {"type": "relation", "relation": [{"id": "ver-1"}]},
                        "Dependencies": {"type": "relation", "relation": []},
                    },
                },
                {
                    "id": "task-2",
                    "object": "page",
                    "properties": {
                        "Title": {"type": "title", "title": [{"plain_text": "Task 2"}]},
                        "Status": {"type": "select", "select": {"name": "Backlog"}},
                        "Type": {"type": "select", "select": {"name": "Bug Fix"}},
                        "Priority": {"type": "select", "select": {"name": "Low"}},
                        "Version": {"type": "relation", "relation": [{"id": "ver-1"}]},
                        "Dependencies": {"type": "relation", "relation": []},
                    },
                },
            ],
        }

        manager = TaskManager(mock_client)
        ready_tasks = await manager.find_ready_tasks()

        assert len(ready_tasks) == 2


@pytest.mark.unit
class TestIdeaManager:
    """Test IdeaManager."""

    def test_init(self, mock_client):
        """Test manager initialization."""
        manager = IdeaManager(mock_client)
        assert manager._client == mock_client

    @pytest.mark.asyncio
    async def test_list_filtered(self, mock_client):
        """Test listing ideas with filters."""
        mock_client._workspace_config = {"Ideas": "db-123"}

        mock_client._api.request.return_value = {
            "results": [
                {
                    "id": "idea-1",
                    "object": "page",
                    "properties": {
                        "Title": {"type": "title", "title": [{"plain_text": "Idea 1"}]},
                        "Category": {"type": "select", "select": {"name": "enhancement"}},
                        "Status": {"type": "select", "select": {"name": "Proposed"}},
                        "Effort Estimate": {"type": "select", "select": {"name": "M"}},
                        "Project": {"type": "relation", "relation": [{"id": "proj-1"}]},
                    },
                },
            ],
        }

        manager = IdeaManager(mock_client)
        ideas = await manager.list(project_id="proj-1", category="enhancement")

        assert len(ideas) == 1
        assert ideas[0].id == "idea-1"

    @pytest.mark.asyncio
    async def test_review_batch(self, mock_client):
        """Test getting a batch of ideas for review."""
        mock_client._workspace_config = {"Ideas": "db-123"}

        mock_client._api.request.return_value = {
            "results": [
                {
                    "id": "idea-1",
                    "object": "page",
                    "properties": {
                        "Title": {"type": "title", "title": [{"plain_text": "Small Idea"}]},
                        "Status": {"type": "select", "select": {"name": "Proposed"}},
                        "Effort Estimate": {"type": "select", "select": {"name": "S"}},
                        "Project": {"type": "relation", "relation": [{"id": "proj-1"}]},
                    },
                },
                {
                    "id": "idea-2",
                    "object": "page",
                    "properties": {
                        "Title": {"type": "title", "title": [{"plain_text": "Large Idea"}]},
                        "Status": {"type": "select", "select": {"name": "Proposed"}},
                        "Effort Estimate": {"type": "select", "select": {"name": "L"}},
                        "Project": {"type": "relation", "relation": [{"id": "proj-1"}]},
                    },
                },
            ],
        }

        manager = IdeaManager(mock_client)
        ideas = await manager.review_batch(count=10)

        assert len(ideas) == 2
        # Should be sorted by effort (S before L)
        assert ideas[0].id == "idea-1"


@pytest.mark.unit
class TestWorkIssueManager:
    """Test WorkIssueManager."""

    def test_init(self, mock_client):
        """Test manager initialization."""
        manager = WorkIssueManager(mock_client)
        assert manager._client == mock_client

    @pytest.mark.asyncio
    async def test_list_filtered(self, mock_client):
        """Test listing work issues with filters."""
        mock_client._workspace_config = {"Work Issues": "db-123"}

        mock_client._api.request.return_value = {
            "results": [
                {
                    "id": "issue-1",
                    "object": "page",
                    "properties": {
                        "Title": {"type": "title", "title": [{"plain_text": "Issue 1"}]},
                        "Type": {"type": "select", "select": {"name": "Technical"}},
                        "Severity": {"type": "select", "select": {"name": "High"}},
                        "Status": {"type": "select", "select": {"name": "Open"}},
                        "Project": {"type": "relation", "relation": [{"id": "proj-1"}]},
                        "Task": {"type": "relation", "relation": [{"id": "task-1"}]},
                    },
                },
            ],
        }

        manager = WorkIssueManager(mock_client)
        issues = await manager.list(project_id="proj-1", severity="High")

        assert len(issues) == 1
        assert issues[0].id == "issue-1"

    @pytest.mark.asyncio
    async def test_find_blockers(self, mock_client):
        """Test finding blocking issues."""
        mock_client._workspace_config = {"Work Issues": "db-123"}

        mock_client._api.request.return_value = {
            "results": [
                {
                    "id": "issue-1",
                    "object": "page",
                    "properties": {
                        "Title": {"type": "title", "title": [{"plain_text": "Blocker"}]},
                        "Severity": {"type": "select", "select": {"name": "Critical"}},
                        "Status": {"type": "select", "select": {"name": "Open"}},
                        "Project": {"type": "relation", "relation": [{"id": "proj-1"}]},
                    },
                },
                {
                    "id": "issue-2",
                    "object": "page",
                    "properties": {
                        "Title": {"type": "title", "title": [{"plain_text": "Minor"}]},
                        "Severity": {"type": "select", "select": {"name": "Low"}},
                        "Status": {"type": "select", "select": {"name": "Open"}},
                        "Project": {"type": "relation", "relation": [{"id": "proj-1"}]},
                    },
                },
            ],
        }

        manager = WorkIssueManager(mock_client)
        blockers = await manager.find_blockers(project_id="proj-1")

        # Should only return High/Critical severity issues
        assert len(blockers) == 1
        assert blockers[0].id == "issue-1"


@pytest.mark.unit
class TestIncidentManager:
    """Test IncidentManager."""

    def test_init(self, mock_client):
        """Test manager initialization."""
        manager = IncidentManager(mock_client)
        assert manager._client == mock_client

    @pytest.mark.asyncio
    async def test_list_filtered(self, mock_client):
        """Test listing incidents with filters."""
        mock_client._workspace_config = {"Incidents": "db-123"}

        mock_client._api.request.return_value = {
            "results": [
                {
                    "id": "incident-1",
                    "object": "page",
                    "properties": {
                        "Title": {"type": "title", "title": [{"plain_text": "Incident 1"}]},
                        "Severity": {"type": "select", "select": {"name": "Critical"}},
                        "Status": {"type": "select", "select": {"name": "Active"}},
                        "Type": {"type": "select", "select": {"name": "Bug"}},
                        "Project": {"type": "relation", "relation": [{"id": "proj-1"}]},
                        "Affected Version": {"type": "relation", "relation": [{"id": "ver-1"}]},
                        "Discovery Date": {"type": "date", "date": {"start": "2025-01-01"}},
                        "Resolved Date": {"type": "date", "date": None},
                    },
                },
            ],
        }

        manager = IncidentManager(mock_client)
        incidents = await manager.list(project_id="proj-1", severity="Critical")

        assert len(incidents) == 1
        assert incidents[0].id == "incident-1"


@pytest.fixture
def mock_client():
    """Create a mock NotionClient."""
    from unittest.mock import MagicMock

    from better_notion._sdk.client import NotionClient

    client = MagicMock(spec=NotionClient)
    client._api = MagicMock()
    client._workspace_config = {}
    client._plugin_caches = {}

    return client
