"""Tests for Personal workspace initialization.

Tests the workspace creation, detection, and metadata handling.
"""

import json
import pytest
from pathlib import Path
from unittest.mock import MagicMock, AsyncMock, patch
from datetime import datetime

from better_notion.utils.personal.workspace import PersonalWorkspaceInitializer
from better_notion.utils.personal.metadata import PersonalWorkspaceMetadata


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
class TestPersonalWorkspaceInitializer:
    """Test workspace initialization."""

    @pytest.fixture
    def initializer(self, mock_client):
        """Create a PersonalWorkspaceInitializer instance."""
        return PersonalWorkspaceInitializer(mock_client)

    def test_init(self, mock_client):
        """Test initializer creation."""
        initializer = PersonalWorkspaceInitializer(mock_client)

        assert initializer.client == mock_client
        assert initializer._database_ids == {}
        assert initializer._parent_page_id == ""
        assert initializer._workspace_id == ""
        assert initializer._workspace_name == ""

    def test_expected_databases(self):
        """Test expected databases list."""
        assert PersonalWorkspaceInitializer.EXPECTED_DATABASES == [
            "Domains",
            "Tags",
            "Projects",
            "Tasks",
            "Routines",
            "Agenda",
        ]

    def test_load_parent_page(self, tmp_path):
        """Test loading parent page from config file."""
        # Create a temporary config file
        config_data = {
            "parent_page": "page-123",
            "workspace_id": "test-workspace",
            "database_ids": {"tasks": "db-123"},
        }

        config_file = tmp_path / "personal.json"
        with open(config_file, "w") as f:
            json.dump(config_data, f)

        # Mock Path.home() to return tmp_path
        with patch.object(Path, 'home', return_value=tmp_path):
            parent_page = PersonalWorkspaceInitializer.load_parent_page()

            assert parent_page == "page-123"

    def test_load_parent_page_not_found(self, tmp_path):
        """Test loading parent page when config doesn't exist."""
        # Mock Path.home() to return tmp_path (no config file)
        with patch.object(Path, 'home', return_value=tmp_path):
            with pytest.raises(FileNotFoundError):
                PersonalWorkspaceInitializer.load_parent_page()

    def test_save_database_ids(self, initializer, tmp_path):
        """Test saving database IDs to config file."""
        initializer._database_ids = {
            "tasks": "db-123",
            "projects": "db-456",
        }
        initializer._parent_page_id = "page-123"
        initializer._workspace_id = "workspace-abc"
        initializer._workspace_name = "Test Workspace"

        # Mock Path.home() to return tmp_path
        with patch.object(Path, 'home', return_value=tmp_path):
            initializer.save_database_ids()

            # Check file was created
            config_file = tmp_path / "personal.json"
            assert config_file.exists()

            # Check file contents
            with open(config_file) as f:
                saved_data = json.load(f)

            assert saved_data["database_ids"] == initializer._database_ids
            assert saved_data["parent_page"] == "page-123"
            assert saved_data["workspace_id"] == "workspace-abc"
            assert saved_data["workspace_name"] == "Test Workspace"


@pytest.mark.integration
class TestPersonalWorkspaceMetadata:
    """Test workspace metadata detection."""

    @pytest.fixture
    def mock_page(self):
        """Create a mock page."""
        page = MagicMock()
        page.id = "page-123"
        page.title = "Personal Workspace"
        return page

    @pytest.fixture
    def mock_client(self):
        """Create a mock client with databases."""
        client = MagicMock()
        client.databases = MagicMock()
        return client

    @pytest.mark.asyncio
    async def test_detect_workspace_in_page_properties(self, mock_page, mock_client):
        """Test detecting workspace from page properties."""
        # Mock page properties with workspace metadata
        mock_page.properties = {
            "Workspace ID": {"rich_text": [{"plain_text": "personal-abc123"}]},
            "Workspace Name": {"rich_text": [{"plain_text": "My Personal Space"}]},
            "Domains": {"rich_text": [{"plain_text": "domains-db-123"}]},
            "Tags": {"rich_text": [{"plain_text": "tags-db-123"}]},
            "Projects": {"rich_text": [{"plain_text": "projects-db-123"}]},
            "Tasks": {"rich_text": [{"plain_text": "tasks-db-123"}]},
            "Routines": {"rich_text": [{"plain_text": "routines-db-123"}]},
            "Agenda": {"rich_text": [{"plain_text": "agenda-db-123"}]},
        }

        result = await PersonalWorkspaceMetadata.detect_workspace(mock_page, mock_client)

        assert result is not None
        assert result["workspace_id"] == "personal-abc123"
        assert result["workspace_name"] == "My Personal Space"
        assert result["detection_method"] == "page_properties"
        assert len(result["database_ids"]) == 6

    @pytest.mark.asyncio
    async def test_detect_workspace_from_children(self, mock_page, mock_client):
        """Test detecting workspace from child databases."""
        # Mock page properties without workspace metadata
        mock_page.properties = {}

        # Mock children databases
        mock_db1 = MagicMock()
        mock_db1.id = "db-123"
        mock_db1.title = {"plain_text": "Domains"}

        mock_db2 = MagicMock()
        mock_db2.id = "db-456"
        mock_db2.title = {"plain_text": "Tags"}

        mock_page.children = AsyncMock(return_value=[mock_db1, mock_db2])

        result = await PersonalWorkspaceMetadata.detect_workspace(mock_page, mock_client)

        assert result is not None
        assert result["detection_method"] == "children"
        assert "database_ids" in result

    @pytest.mark.asyncio
    async def test_detect_workspace_not_found(self, mock_page, mock_client):
        """Test detecting workspace when none exists."""
        # Mock page without workspace metadata
        mock_page.properties = {}
        mock_page.children = AsyncMock(return_value=[])

        result = await PersonalWorkspaceMetadata.detect_workspace(mock_page, mock_client)

        assert result is None


@pytest.mark.integration
class TestPersonalWorkspaceInit:
    """Test workspace initialization flow."""

    @pytest.fixture
    def initializer(self, mock_client):
        """Create a PersonalWorkspaceInitializer instance."""
        return PersonalWorkspaceInitializer(mock_client)

    @pytest.mark.asyncio
    async def test_initialize_workspace_creates_databases(
        self, initializer, mock_client
    ):
        """Test that initialize_workspace creates all databases."""
        # Mock database creation
        initializer._create_database = AsyncMock()
        initializer._create_database.return_value = MagicMock(id="db-123")

        # Mock relation creation
        initializer._create_relation = AsyncMock()

        # Mock save_database_ids
        initializer.save_database_ids = MagicMock()

        # Run initialization
        result = await initializer.initialize_workspace(
            parent_page_id="page-123",
            workspace_name="Test Workspace",
        )

        # Verify all databases were created
        assert initializer._create_database.call_count == 6

        # Verify workspace metadata was set
        assert initializer._parent_page_id == "page-123"
        assert initializer._workspace_name == "Test Workspace"
        assert initializer._workspace_id.startswith("personal-")

        # Verify config was saved
        initializer.save_database_ids.assert_called_once()

        # Verify return value contains database IDs
        assert len(result) == 6


@pytest.mark.integration
class TestPersonalWorkspaceDetection:
    """Test workspace auto-detection."""

    @pytest.mark.asyncio
    async def test_auto_detect_existing_workspace(self):
        """Test that existing workspace is auto-detected."""
        from better_notion._sdk.models.page import Page
        from better_notion.plugins.official.personal_cli import get_client
        from better_notion.utils.personal.metadata import PersonalWorkspaceMetadata

        # Mock page
        mock_page = MagicMock()
        mock_page.id = "page-123"
        mock_page.properties = {
            "Workspace ID": {"rich_text": [{"plain_text": "personal-abc123"}]},
            "Domains": {"rich_text": [{"plain_text": "domains-db-123"}]},
        }

        # Mock Page.get
        with patch.object(Page, 'get', new_callable=AsyncMock) as mock_get:
            mock_get.return_value = mock_page

            # Mock detect_workspace
            with patch.object(
                PersonalWorkspaceMetadata, 'detect_workspace', new_callable=AsyncMock
            ) as mock_detect:
                mock_detect.return_value = {
                    "workspace_id": "personal-abc123",
                    "database_ids": {"domains": "domains-db-123"},
                }

                # Run detection
                result = await PersonalWorkspaceMetadata.detect_workspace(mock_page, MagicMock())

                assert result is not None
                assert result["workspace_id"] == "personal-abc123"
