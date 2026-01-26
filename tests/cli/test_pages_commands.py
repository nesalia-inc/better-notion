"""
Tests for CLI pages commands.

This module tests the pages commands in the Better Notion CLI.
"""
from __future__ import annotations

import json
from unittest.mock import AsyncMock, MagicMock, patch
from pathlib import Path

import pytest
from typer.testing import CliRunner

from better_notion._cli.commands.pages import app


@pytest.fixture
def runner():
    """Create CLI runner."""
    return CliRunner()


@pytest.fixture
def mock_config():
    """Create mock Config."""
    with patch("better_notion._cli.commands.pages.Config") as mock:
        config = MagicMock()
        config.token = "test_token"
        config.timeout = 30
        mock.load.return_value = config
        yield mock


@pytest.fixture
def mock_client():
    """Create mock NotionClient."""
    client = MagicMock()
    client.api = MagicMock()

    # Mock API methods
    client.api.pages = MagicMock()
    client.api.pages.retrieve = AsyncMock()
    client.api.pages.create = AsyncMock()

    client.api.databases = MagicMock()
    client.api.databases.retrieve = AsyncMock()
    client.api.databases.query = AsyncMock()

    # Setup caches
    client.page_cache = MagicMock()
    client.database_cache = MagicMock()

    # Mock SDK managers
    client.pages = MagicMock()
    client.databases = MagicMock()

    return client


class TestPagesCreate:
    """Tests for pages create command."""

    def test_pages_create_with_root_flag(self, runner, mock_client, mock_config):
        """Test creating a page at workspace root with --root flag."""
        # Mock the page creation
        mock_page = MagicMock()
        mock_page.id = "new-page-id"
        mock_page.title = "Root Page"
        mock_page.url = "https://notion.so/newpageid"
        mock_page.parent = None

        mock_client.pages.create = AsyncMock(return_value=mock_page)

        with patch("better_notion._cli.commands.pages.NotionClient", return_value=mock_client):
            result = runner.invoke(app, ["create", "--root", "--title", "Root Page"])

            # Verify the command succeeded
            assert result.exit_code == 0

            # Verify parent type is workspace
            response_data = json.loads(result.stdout)
            assert response_data["success"] is True
            assert response_data["data"]["id"] == "new-page-id"
            assert response_data["data"]["title"] == "Root Page"
            assert response_data["data"]["parent_type"] == "workspace"

    def test_pages_create_with_parent_id(self, runner, mock_client, mock_config):
        """Test creating a page with --parent flag."""
        # Mock parent database
        mock_parent = MagicMock()
        mock_parent.id = "db-123"
        mock_parent.object = "database"

        # Mock the page creation
        mock_page = MagicMock()
        mock_page.id = "new-page-id"
        mock_page.title = "Child Page"
        mock_page.url = "https://notion.so/newpageid"
        mock_page.parent = mock_parent

        mock_client.databases.get = AsyncMock(return_value=mock_parent)
        mock_client.pages.create = AsyncMock(return_value=mock_page)

        with patch("better_notion._cli.commands.pages.NotionClient", return_value=mock_client):
            result = runner.invoke(app, ["create", "--parent", "db-123", "--title", "Child Page"])

            # Verify the command succeeded
            assert result.exit_code == 0

            # Verify response
            response_data = json.loads(result.stdout)
            assert response_data["success"] is True
            assert response_data["data"]["id"] == "new-page-id"
            assert response_data["data"]["title"] == "Child Page"

    def test_pages_create_requires_title(self, runner, mock_client, mock_config):
        """Test that create command requires --title."""
        with patch("better_notion._cli.commands.pages.NotionClient", return_value=mock_client):
            result = runner.invoke(app, ["create", "--parent", "db-123"])

            # Should fail because --title is required
            assert result.exit_code != 0

    def test_pages_create_root_and_parent_mutually_exclusive(self, runner, mock_client, mock_config):
        """Test that --root and --parent are mutually exclusive."""
        with patch("better_notion._cli.commands.pages.NotionClient", return_value=mock_client):
            result = runner.invoke(
                app,
                ["create", "--root", "--parent", "db-123", "--title", "Test"]
            )

            # Verify the command returns error
            response_data = json.loads(result.stdout)
            assert response_data["success"] is False
            assert response_data["error"]["code"] == "INVALID_ARGUMENT"
            assert "Cannot specify both --root and --parent" in response_data["error"]["message"]

    def test_pages_create_with_properties(self, runner, mock_client, mock_config):
        """Test creating a page with additional properties."""
        # Mock the page creation
        mock_page = MagicMock()
        mock_page.id = "new-page-id"
        mock_page.title = "Page with Props"
        mock_page.url = "https://notion.so/newpageid"
        mock_page.parent = None

        mock_client.pages.create = AsyncMock(return_value=mock_page)

        properties = json.dumps({"custom_prop": "value"})

        with patch("better_notion._cli.commands.pages.NotionClient", return_value=mock_client):
            result = runner.invoke(
                app,
                ["create", "--root", "--title", "Page with Props", "--properties", properties]
            )

            # Verify the command succeeded
            assert result.exit_code == 0

            response_data = json.loads(result.stdout)
            assert response_data["success"] is True
            assert response_data["data"]["title"] == "Page with Props"

    def test_pages_create_with_short_flags(self, runner, mock_client, mock_config):
        """Test creating a page with short flag variants."""
        # Mock the page creation
        mock_page = MagicMock()
        mock_page.id = "new-page-id"
        mock_page.title = "Short Flags"
        mock_page.url = "https://notion.so/newpageid"
        mock_page.parent = None

        mock_client.pages.create = AsyncMock(return_value=mock_page)

        with patch("better_notion._cli.commands.pages.NotionClient", return_value=mock_client):
            result = runner.invoke(app, ["create", "-r", "-t", "Short Flags"])

            # Verify the command succeeded
            assert result.exit_code == 0

            response_data = json.loads(result.stdout)
            assert response_data["success"] is True


class TestPagesGet:
    """Tests for pages get command."""

    def test_pages_get_by_id(self, runner, mock_client, mock_config):
        """Test getting a page by ID."""
        # Mock page data
        mock_page = MagicMock()
        mock_page.id = "page-123"
        mock_page.title = "Test Page"
        mock_page.url = "https://notion.so/page123"
        mock_page.parent = None
        mock_page.created_time = "2024-01-01T00:00:00.000Z"
        mock_page.last_edited_time = "2024-01-01T00:00:00.000Z"
        mock_page.archived = False
        mock_page._data = {"properties": {"Name": {"type": "title"}}}

        mock_client.pages.get = AsyncMock(return_value=mock_page)

        with patch("better_notion._cli.commands.pages.NotionClient", return_value=mock_client):
            result = runner.invoke(app, ["get", "page-123"])

            # Verify the command succeeded
            assert result.exit_code == 0

            response_data = json.loads(result.stdout)
            assert response_data["success"] is True
            assert response_data["data"]["id"] == "page-123"
            assert response_data["data"]["title"] == "Test Page"


class TestPagesDelete:
    """Tests for pages delete command."""

    def test_pages_delete(self, runner, mock_client, mock_config):
        """Test deleting a page."""
        # Mock page
        mock_page = MagicMock()
        mock_page.delete = AsyncMock()

        mock_client.pages.get = AsyncMock(return_value=mock_page)

        with patch("better_notion._cli.commands.pages.NotionClient", return_value=mock_client):
            result = runner.invoke(app, ["delete", "page-123"])

            # Verify the command succeeded
            assert result.exit_code == 0

            response_data = json.loads(result.stdout)
            assert response_data["success"] is True
            assert response_data["data"]["status"] == "deleted"
