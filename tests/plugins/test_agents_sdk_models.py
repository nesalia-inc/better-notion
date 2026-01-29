"""Tests for Agents SDK Plugin models.

Tests Organization, Project, Version, and Task models.
"""

import pytest

from better_notion.plugins.official.agents_sdk.models import (
    Organization,
    Project,
    Task,
    Version,
)


@pytest.mark.unit
class TestOrganization:
    """Test Organization model."""

    def test_init(self, mock_client):
        """Test organization initialization."""
        data = {
            "id": "org-123",
            "object": "page",
            "properties": {
                "Name": {
                    "type": "title",
                    "title": [{"plain_text": "Test Org"}],
                },
                "Slug": {
                    "type": "rich_text",
                    "rich_text": [{"plain_text": "test-org"}],
                },
                "Description": {
                    "type": "rich_text",
                    "rich_text": [{"plain_text": "Test description"}],
                },
                "Repository URL": {
                    "type": "url",
                    "url": "https://github.com/test/repo",
                },
                "Status": {
                    "type": "select",
                    "select": {"name": "Active"},
                },
            },
        }

        org = Organization(mock_client, data)

        assert org.id == "org-123"
        assert org.name == "Test Org"
        assert org.slug == "test-org"
        assert org.description == "Test description"
        assert org.repository_url == "https://github.com/test/repo"
        assert org.status == "Active"

    def test_properties_empty(self, mock_client):
        """Test organization with empty properties."""
        data = {
            "id": "org-123",
            "object": "page",
            "properties": {
                "Name": {"type": "title", "title": []},
                "Status": {"type": "select", "select": None},
            },
        }

        org = Organization(mock_client, data)

        assert org.name == ""
        assert org.slug == ""
        assert org.description == ""
        assert org.repository_url is None
        assert org.status == "Unknown"


@pytest.mark.unit
class TestProject:
    """Test Project model."""

    def test_init(self, mock_client):
        """Test project initialization."""
        data = {
            "id": "proj-123",
            "object": "page",
            "properties": {
                "Name": {
                    "type": "title",
                    "title": [{"plain_text": "Test Project"}],
                },
                "Slug": {
                    "type": "rich_text",
                    "rich_text": [{"plain_text": "test-project"}],
                },
                "Description": {
                    "type": "rich_text",
                    "rich_text": [{"plain_text": "Test project description"}],
                },
                "Repository": {
                    "type": "url",
                    "url": "https://github.com/test/project",
                },
                "Status": {
                    "type": "select",
                    "select": {"name": "Active"},
                },
                "Tech Stack": {
                    "type": "multi_select",
                    "multi_select": [
                        {"name": "Python"},
                        {"name": "React"},
                    ],
                },
                "Role": {
                    "type": "select",
                    "select": {"name": "Developer"},
                },
                "Organization": {
                    "type": "relation",
                    "relation": [{"id": "org-123"}],
                },
            },
        }

        project = Project(mock_client, data)

        assert project.id == "proj-123"
        assert project.name == "Test Project"
        assert project.slug == "test-project"
        assert project.description == "Test project description"
        assert project.repository == "https://github.com/test/project"
        assert project.status == "Active"
        assert set(project.tech_stack) == {"Python", "React"}
        assert project.role == "Developer"
        assert project.organization_id == "org-123"


@pytest.mark.unit
class TestVersion:
    """Test Version model."""

    def test_init(self, mock_client):
        """Test version initialization."""
        data = {
            "id": "ver-123",
            "object": "page",
            "properties": {
                "Version": {
                    "type": "title",
                    "title": [{"plain_text": "v1.0.0"}],
                },
                "Status": {
                    "type": "select",
                    "select": {"name": "In Progress"},
                },
                "Type": {
                    "type": "select",
                    "select": {"name": "Minor"},
                },
                "Branch Name": {
                    "type": "rich_text",
                    "rich_text": [{"plain_text": "feature/v1.0.0"}],
                },
                "Progress": {
                    "type": "number",
                    "number": 50,
                },
                "Project": {
                    "type": "relation",
                    "relation": [{"id": "proj-123"}],
                },
            },
        }

        version = Version(mock_client, data)

        assert version.id == "ver-123"
        assert version.name == "v1.0.0"
        assert version.status == "In Progress"
        assert version.version_type == "Minor"
        assert version.branch_name == "feature/v1.0.0"
        assert version.progress == 50
        assert version.project_id == "proj-123"


@pytest.mark.unit
class TestTask:
    """Test Task model."""

    def test_init(self, mock_client):
        """Test task initialization."""
        data = {
            "id": "task-123",
            "object": "page",
            "properties": {
                "Title": {
                    "type": "title",
                    "title": [{"plain_text": "Test Task"}],
                },
                "Status": {
                    "type": "select",
                    "select": {"name": "In Progress"},
                },
                "Type": {
                    "type": "select",
                    "select": {"name": "New Feature"},
                },
                "Priority": {
                    "type": "select",
                    "select": {"name": "High"},
                },
                "Version": {
                    "type": "relation",
                    "relation": [{"id": "ver-123"}],
                },
                "Dependencies": {
                    "type": "relation",
                    "relation": [
                        {"id": "task-001"},
                        {"id": "task-002"},
                    ],
                },
                "Estimated Hours": {
                    "type": "number",
                    "number": 8,
                },
                "Actual Hours": {
                    "type": "number",
                    "number": None,
                },
            },
        }

        task = Task(mock_client, data)

        assert task.id == "task-123"
        assert task.title == "Test Task"
        assert task.status == "In Progress"
        assert task.task_type == "New Feature"
        assert task.priority == "High"
        assert task.version_id == "ver-123"
        assert set(task.dependency_ids) == {"task-001", "task-002"}
        assert task.estimated_hours == 8
        assert task.actual_hours is None

    @pytest.mark.asyncio
    async def test_can_start_no_dependencies(self, mock_client):
        """Test can_start with no dependencies."""
        data = {
            "id": "task-123",
            "object": "page",
            "properties": {
                "Title": {"type": "title", "title": [{"plain_text": "Test"}]},
                "Status": {"type": "select", "select": {"name": "Backlog"}},
                "Type": {"type": "select", "select": {"name": "New Feature"}},
                "Priority": {"type": "select", "select": {"name": "Medium"}},
                "Version": {"type": "relation", "relation": [{"id": "ver-123"}]},
                "Dependencies": {"type": "relation", "relation": []},
            },
        }

        task = Task(mock_client, data)
        assert await task.can_start() is True

    @pytest.mark.asyncio
    async def test_can_start_with_completed_dependencies(self, mock_client, mock_completed_task):
        """Test can_start with completed dependencies."""
        data = {
            "id": "task-123",
            "object": "page",
            "properties": {
                "Title": {"type": "title", "title": [{"plain_text": "Test"}]},
                "Status": {"type": "select", "select": {"name": "Backlog"}},
                "Type": {"type": "select", "select": {"name": "New Feature"}},
                "Priority": {"type": "select", "select": {"name": "Medium"}},
                "Version": {"type": "relation", "relation": [{"id": "ver-123"}]},
                "Dependencies": {
                    "type": "relation",
                    "relation": [{"id": "task-completed"}],
                },
            },
        }

        task = Task(mock_client, data)

        # Mock the dependency fetch
        async def mock_get(dep_id, **kwargs):
            if dep_id == "task-completed":
                return mock_completed_task
            raise Exception("Task not found")

        # Patch Task.get
        import better_notion.plugins.official.agents_sdk.models as models_module
        original_get = models_module.Task.get
        models_module.Task.get = mock_get

        try:
            assert await task.can_start() is True
        finally:
            models_module.Task.get = original_get


@pytest.fixture
def mock_client():
    """Create a mock NotionClient."""
    from better_notion._sdk.client import NotionClient
    from unittest.mock import MagicMock

    client = MagicMock(spec=NotionClient)
    client._api = MagicMock()
    client.plugin_cache = MagicMock(return_value=None)

    return client


@pytest.fixture
def mock_completed_task(mock_client):
    """Create a mock completed task."""
    data = {
        "id": "task-completed",
        "object": "page",
        "properties": {
            "Title": {"type": "title", "title": [{"plain_text": "Completed"}]},
            "Status": {"type": "select", "select": {"name": "Completed"}},
            "Type": {"type": "select", "select": {"name": "New Feature"}},
            "Priority": {"type": "select", "select": {"name": "Medium"}},
            "Version": {"type": "relation", "relation": [{"id": "ver-123"}]},
            "Dependencies": {"type": "relation", "relation": []},
        },
    }

    return Task(mock_client, data)
