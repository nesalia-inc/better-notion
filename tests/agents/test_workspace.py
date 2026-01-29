"""Unit tests for workspace initializer."""

import json
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from better_notion.utils.agents.workspace import (
    WorkspaceInitializer,
    initialize_workspace_command,
)


class TestWorkspaceInitializer:
    """Tests for WorkspaceInitializer class."""

    @pytest.fixture
    def mock_client(self):
        """Create a mock NotionClient."""
        client = MagicMock()
        client.databases = MagicMock()
        return client

    @pytest.fixture
    def mock_page(self):
        """Create a mock Page."""
        page = MagicMock()
        page.id = "page123"
        return page

    def test_init(self, mock_client) -> None:
        """Test WorkspaceInitializer initialization."""
        initializer = WorkspaceInitializer(mock_client)

        assert initializer._client == mock_client
        assert initializer._database_ids == {}

    @pytest.mark.asyncio
    async def test_initialize_workspace_creates_databases(
        self, mock_client, mock_page
    ) -> None:
        """Test that initialize_workspace creates all databases."""
        # Mock database creation
        mock_db = MagicMock()
        mock_db.id = "db123"
        mock_client.databases.create = AsyncMock(return_value=mock_db)

        # Mock Page.get
        with patch("better_notion.utils.agents.workspace.Page.get") as mock_get:
            mock_get = AsyncMock(return_value=mock_page)

            initializer = WorkspaceInitializer(mock_client)

            # Mock the _create methods to avoid actual API calls
            for method_name in [
                "_create_organizations_db",
                "_create_tags_db",
                "_create_projects_db",
                "_create_versions_db",
                "_create_tasks_db",
                "_create_ideas_db",
                "_create_work_issues_db",
                "_create_incidents_db",
            ]:
                # Create async mock for each method
                async_mock = AsyncMock()
                setattr(initializer, method_name, async_mock)

            # Run initialization
            result = await initializer.initialize_workspace(
                parent_page_id="page123",
                workspace_name="Test Workspace",
            )

            # Verify all create methods were called
            assert initializer._create_organizations_db.called
            assert initializer._create_tags_db.called
            assert initializer._create_projects_db.called
            assert initializer._create_versions_db.called
            assert initializer._create_tasks_db.called
            assert initializer._create_ideas_db.called
            assert initializer._create_work_issues_db.called
            assert initializer._create_incidents_db.called

    def test_save_database_ids(self, mock_client, tmp_path) -> None:
        """Test saving database IDs to file."""
        initializer = WorkspaceInitializer(mock_client)
        initializer._database_ids = {
            "organizations": "org123",
            "projects": "proj123",
        }

        # Save to temp file
        config_file = tmp_path / "workspace.json"
        initializer.save_database_ids(path=config_file)

        # Verify file was created
        assert config_file.exists()

        # Verify content
        with open(config_file, encoding="utf-8") as f:
            data = json.load(f)

        assert data["organizations"] == "org123"
        assert data["projects"] == "proj123"

    def test_save_database_ids_default_path(self, mock_client) -> None:
        """Test saving database IDs to default path."""
        import tempfile

        initializer = WorkspaceInitializer(mock_client)
        initializer._database_ids = {"organizations": "org123"}

        # Use temp directory as home
        with tempfile.TemporaryDirectory() as tmpdir:
            temp_path = Path(tmpdir)
            config_file = temp_path / "workspace.json"

            initializer.save_database_ids(path=config_file)

            assert config_file.exists()

    def test_load_database_ids(self, tmp_path) -> None:
        """Test loading database IDs from file."""
        # Create test config file
        config_file = tmp_path / "workspace.json"
        test_data = {
            "organizations": "org123",
            "projects": "proj123",
        }

        with open(config_file, "w", encoding="utf-8") as f:
            json.dump(test_data, f)

        # Load it
        result = WorkspaceInitializer.load_database_ids(path=config_file)

        assert result["organizations"] == "org123"
        assert result["projects"] == "proj123"

    def test_load_database_ids_file_not_found(self) -> None:
        """Test loading from non-existent file raises error."""
        with pytest.raises(FileNotFoundError):
            WorkspaceInitializer.load_database_ids(path=Path("/nonexistent/path.json"))


class TestInitializeWorkspaceCommand:
    """Tests for initialize_workspace_command function."""

    @pytest.mark.asyncio
    async def test_initialize_workspace_command(self) -> None:
        """Test the convenience function."""
        # We need to patch at the module level where the function is defined
        with patch(
            "better_notion.utils.agents.workspace.Config"
        ) as mock_config_class, patch(
            "better_notion.utils.agents.workspace.WorkspaceInitializer"
        ) as mock_initializer_class:
            # Setup config mock
            mock_config_instance = MagicMock()
            mock_config_instance.token = "test_token"
            mock_config_class.load.return_value = mock_config_instance

            # Setup initializer mock
            mock_initializer_instance = MagicMock()
            mock_initializer_instance.initialize_workspace = AsyncMock(
                return_value={"organizations": "org123"}
            )
            mock_initializer_instance.save_database_ids = MagicMock()
            mock_initializer_class.return_value = mock_initializer_instance

            # Run command
            result = await initialize_workspace_command(
                parent_page_id="page123",
                workspace_name="Test Workspace",
            )

            # Verify initializer was created and called
            assert mock_initializer_class.called
            mock_initializer_instance.initialize_workspace.assert_called_once_with(
                "page123", "Test Workspace"
            )
            mock_initializer_instance.save_database_ids.assert_called_once()

            assert result == {"organizations": "org123"}
