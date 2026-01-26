"""Tests for Page model."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from better_notion._sdk.models.page import Page
from better_notion._sdk.parents import WorkspaceParent, PageParent, DatabaseParent
from better_notion._sdk.cache import Cache


@pytest.fixture
def mock_client():
    """Create mock NotionClient."""
    client = MagicMock()
    client.api = MagicMock()

    # Mock API methods
    client.api.pages = MagicMock()
    client.api.pages.retrieve = AsyncMock()
    client.api.pages.create = AsyncMock()
    client.api.blocks = MagicMock()
    client.api.blocks.children = MagicMock()
    client.api.blocks.children.list = AsyncMock()
    client.api.databases = MagicMock()
    client.api.databases.retrieve = AsyncMock()
    client.api.blocks.retrieve = AsyncMock()

    # Setup caches
    client.page_cache = Cache()
    client.database_cache = Cache()
    client._page_cache = client.page_cache
    client._database_cache = client.database_cache

    return client


@pytest.fixture
def page_data():
    """Sample page data from Notion API."""
    return {
        "id": "page-123",
        "object": "page",
        "created_time": "2024-01-01T00:00:00.000Z",
        "last_edited_time": "2024-01-01T00:00:00.000Z",
        "archived": False,
        "properties": {
            "Name": {
                "id": "title",
                "type": "title",
                "title": [
                    {
                        "type": "text",
                        "text": {"content": "Test Page"}
                    }
                ]
            },
            "Status": {
                "id": "status",
                "type": "select",
                "select": {
                    "id": "opt-1",
                    "name": "In Progress",
                    "color": "blue"
                }
            },
            "Priority": {
                "id": "priority",
                "type": "number",
                "number": 5
            }
        },
        "parent": {
            "type": "database_id",
            "database_id": "db-123"
        },
        "url": "https://notion.so/page-123"
    }


class TestPageInit:
    """Tests for Page initialization."""

    def test_init_with_client_and_data(self, mock_client, page_data):
        """Test initialization with client and data."""
        page = Page(mock_client, page_data)

        assert page.id == "page-123"
        assert page.object == "page"
        assert page._client is mock_client
        assert page._data == page_data

    def test_init_finds_title_property(self, mock_client, page_data):
        """Test initialization finds title property."""
        page = Page(mock_client, page_data)

        assert page._title_property == "Name"


class TestPageMetadata:
    """Tests for Page metadata properties."""

    def test_title_property(self, mock_client, page_data):
        """Test title property."""
        page = Page(mock_client, page_data)

        assert page.title == "Test Page"

    def test_title_empty(self, mock_client):
        """Test title with empty title array."""
        data = {
            "id": "page-123",
            "object": "page",
            "properties": {
                "Name": {
                    "type": "title",
                    "title": []
                }
            }
        }
        page = Page(mock_client, data)

        assert page.title == ""

    def test_url_property(self, mock_client, page_data):
        """Test URL property."""
        page = Page(mock_client, page_data)

        assert page.url == "https://notion.so/page123"

    def test_icon_emoji(self, mock_client):
        """Test icon property with emoji."""
        data = {
            "id": "page-123",
            "object": "page",
            "properties": {},
            "icon": {
                "type": "emoji",
                "emoji": "🚀"
            }
        }
        page = Page(mock_client, data)

        assert page.icon == "🚀"

    def test_icon_external(self, mock_client):
        """Test icon property with external URL."""
        data = {
            "id": "page-123",
            "object": "page",
            "properties": {},
            "icon": {
                "type": "external",
                "external": {"url": "https://example.com/icon.png"}
            }
        }
        page = Page(mock_client, data)

        assert page.icon == "https://example.com/icon.png"

    def test_icon_none(self, mock_client):
        """Test icon property when no icon."""
        data = {
            "id": "page-123",
            "object": "page",
            "properties": {}
        }
        page = Page(mock_client, data)

        assert page.icon is None

    def test_cover_external(self, mock_client):
        """Test cover property with external URL."""
        data = {
            "id": "page-123",
            "object": "page",
            "properties": {},
            "cover": {
                "type": "external",
                "external": {"url": "https://example.com/cover.png"}
            }
        }
        page = Page(mock_client, data)

        assert page.cover == "https://example.com/cover.png"

    def test_cover_none(self, mock_client):
        """Test cover property when no cover."""
        data = {
            "id": "page-123",
            "object": "page",
            "properties": {}
        }
        page = Page(mock_client, data)

        assert page.cover is None

    def test_archived_property(self, mock_client):
        """Test archived property."""
        data = {
            "id": "page-123",
            "object": "page",
            "properties": {},
            "archived": True
        }
        page = Page(mock_client, data)

        assert page.archived is True

    def test_properties_property(self, mock_client, page_data):
        """Test raw properties access."""
        page = Page(mock_client, page_data)

        assert page.properties == page_data["properties"]


class TestPagePropertyAccess:
    """Tests for smart property access."""

    def test_get_property_select(self, mock_client, page_data):
        """Test getting select property."""
        page = Page(mock_client, page_data)

        status = page.get_property("Status")

        assert status == "In Progress"

    def test_get_property_number(self, mock_client, page_data):
        """Test getting number property."""
        page = Page(mock_client, page_data)

        priority = page.get_property("Priority")

        assert priority == 5

    def test_get_property_case_insensitive(self, mock_client, page_data):
        """Test case-insensitive property access."""
        page = Page(mock_client, page_data)

        status = page.get_property("status")

        assert status == "In Progress"

    def test_get_property_with_default(self, mock_client, page_data):
        """Test getting property with default value."""
        page = Page(mock_client, page_data)

        value = page.get_property("Unknown", default="N/A")

        assert value == "N/A"

    def test_get_property_missing_no_default(self, mock_client, page_data):
        """Test getting missing property without default."""
        page = Page(mock_client, page_data)

        value = page.get_property("Unknown")

        assert value is None

    def test_has_property_exists(self, mock_client, page_data):
        """Test has_property when property exists."""
        page = Page(mock_client, page_data)

        assert page.has_property("Status") is True

    def test_has_property_not_exists(self, mock_client, page_data):
        """Test has_property when property doesn't exist."""
        page = Page(mock_client, page_data)

        assert page.has_property("Unknown") is False

    def test_has_property_case_insensitive(self, mock_client, page_data):
        """Test has_property is case-insensitive."""
        page = Page(mock_client, page_data)

        assert page.has_property("status") is True


class TestPageClassMethods:
    """Tests for Page class methods (autonomous entity)."""

    @pytest.mark.asyncio
    async def test_get_from_api(self, mock_client, page_data):
        """Test Page.get() fetches from API."""
        mock_client.api.pages.retrieve.return_value = page_data

        page = await Page.get(page_id="page-123", client=mock_client)

        assert page.id == "page-123"
        assert page.title == "Test Page"
        mock_client.api.pages.retrieve.assert_called_once_with(page_id="page-123")

    @pytest.mark.asyncio
    async def test_get_uses_cache(self, mock_client, page_data):
        """Test Page.get() uses cache."""
        # Pre-populate cache
        cached_page = Page(mock_client, page_data)
        mock_client.page_cache["page-123"] = cached_page

        page = await Page.get(page_id="page-123", client=mock_client)

        assert page is cached_page
        # API should not be called
        mock_client.api.pages.retrieve.assert_not_called()

    @pytest.mark.asyncio
    async def test_create_page(self, mock_client):
        """Test Page.create() creates new page."""
        new_page_data = {
            "id": "new-page",
            "object": "page",
            "created_time": "2024-01-01T00:00:00.000Z",
            "last_edited_time": "2024-01-01T00:00:00.000Z",
            "archived": False,
            "properties": {
                "Name": {
                    "id": "title",
                    "type": "title",
                    "title": [
                        {
                            "type": "text",
                            "text": {"content": "New Page"}
                        }
                    ]
                }
            }
        }

        mock_client.api.pages.create.return_value = new_page_data

        parent = MagicMock()
        parent.id = "db-123"
        parent.object = "database"

        page = await Page.create(
            parent=parent,
            client=mock_client,
            title="New Page"
        )

        assert page.id == "new-page"
        assert page.title == "New Page"

    @pytest.mark.asyncio
    async def test_create_page_with_workspace_parent(self, mock_client):
        """Test Page.create() with WorkspaceParent."""
        new_page_data = {
            "id": "new-page",
            "object": "page",
            "created_time": "2024-01-01T00:00:00.000Z",
            "last_edited_time": "2024-01-01T00:00:00.000Z",
            "archived": False,
            "properties": {},
            "parent": {
                "type": "workspace",
                "workspace": True
            }
        }

        mock_client.api.pages.create.return_value = new_page_data

        page = await Page.create(
            parent=WorkspaceParent(),
            client=mock_client,
            title="Root Page"
        )

        assert page.id == "new-page"
        # Verify the parent was sent correctly
        mock_client.api.pages.create.assert_called_once()
        call_args = mock_client.api.pages.create.call_args
        assert call_args[1]["parent"] == {"type": "workspace", "workspace": True}

    @pytest.mark.asyncio
    async def test_create_page_with_page_parent_class(self, mock_client):
        """Test Page.create() with PageParent class."""
        new_page_data = {
            "id": "new-page",
            "object": "page",
            "created_time": "2024-01-01T00:00:00.000Z",
            "last_edited_time": "2024-01-01T00:00:00.000Z",
            "archived": False,
            "properties": {},
            "parent": {
                "type": "page_id",
                "page_id": "page-parent-123"
            }
        }

        mock_client.api.pages.create.return_value = new_page_data

        page = await Page.create(
            parent=PageParent(page_id="page-parent-123"),
            client=mock_client,
            title="Child Page"
        )

        assert page.id == "new-page"
        # Verify the parent was sent correctly
        mock_client.api.pages.create.assert_called_once()
        call_args = mock_client.api.pages.create.call_args
        assert call_args[1]["parent"] == {"type": "page_id", "page_id": "page-parent-123"}

    @pytest.mark.asyncio
    async def test_create_page_with_database_parent_class(self, mock_client):
        """Test Page.create() with DatabaseParent class."""
        new_page_data = {
            "id": "new-page",
            "object": "page",
            "created_time": "2024-01-01T00:00:00.000Z",
            "last_edited_time": "2024-01-01T00:00:00.000Z",
            "archived": False,
            "properties": {},
            "parent": {
                "type": "database_id",
                "database_id": "db-parent-123"
            }
        }

        mock_client.api.pages.create.return_value = new_page_data

        page = await Page.create(
            parent=DatabaseParent(database_id="db-parent-123"),
            client=mock_client,
            title="DB Child Page"
        )

        assert page.id == "new-page"
        # Verify the parent was sent correctly
        mock_client.api.pages.create.assert_called_once()
        call_args = mock_client.api.pages.create.call_args
        assert call_args[1]["parent"] == {"type": "database_id", "database_id": "db-parent-123"}

    @pytest.mark.asyncio
    async def test_create_page_with_invalid_parent(self, mock_client):
        """Test Page.create() with invalid parent type."""
        with pytest.raises(ValueError, match="Invalid parent type"):
            await Page.create(
                parent="invalid-parent",
                client=mock_client,
                title="Test Page"
            )


class TestPageNavigation:
    """Tests for Page navigation methods."""

    @pytest.mark.asyncio
    async def test_parent_database(self, mock_client, page_data):
        """Test getting parent database."""
        # Mock database fetch
        db_data = {
            "id": "db-123",
            "object": "database",
            "title": [{"text": {"content": "Test DB"}}]
        }
        mock_client.api.databases.retrieve.return_value = db_data

        page = Page(mock_client, page_data)
        parent = await page.parent()

        assert parent.id == "db-123"
        assert parent.object == "database"

    @pytest.mark.asyncio
    async def test_parent_uses_cache(self, mock_client, page_data):
        """Test parent() caches result."""
        db_data = {
            "id": "db-123",
            "object": "database",
            "title": [{"text": {"content": "Test DB"}}]
        }
        mock_client.api.databases.retrieve.return_value = db_data

        page = Page(mock_client, page_data)

        # First call - fetches from API
        parent1 = await page.parent()

        # Second call - uses cache
        parent2 = await page.parent()

        assert parent1 is parent2
        # API should only be called once
        mock_client.api.databases.retrieve.assert_called_once()

    @pytest.mark.asyncio
    async def test_children_empty(self, mock_client):
        """Test children() with no children."""
        mock_client.api.blocks.children.list.return_value = {
            "results": [],
            "has_more": False,
            "next_cursor": None
        }

        data = {
            "id": "page-123",
            "object": "page",
            "properties": {}
        }
        page = Page(mock_client, data)

        children = []
        async for child in page.children():
            children.append(child)

        assert len(children) == 0

    @pytest.mark.asyncio
    async def test_children_with_blocks(self, mock_client):
        """Test children() with child blocks."""
        mock_client.api.blocks.children.list.return_value = {
            "results": [
                {
                    "id": "block-1",
                    "object": "block",
                    "type": "paragraph",
                    "paragraph": {"text": []}
                }
            ],
            "has_more": False,
            "next_cursor": None
        }

        data = {
            "id": "page-123",
            "object": "page",
            "properties": {}
        }
        page = Page(mock_client, data)

        children = []
        async for child in page.children():
            children.append(child)

        assert len(children) == 1
        assert children[0].id == "block-1"


class TestPageCRUD:
    """Tests for Page CRUD operations."""

    @pytest.mark.asyncio
    async def test_save(self, mock_client, page_data):
        """Test save() reloads from API."""
        updated_data = page_data.copy()
        updated_data["properties"]["Name"]["title"][0]["text"]["content"] = "Updated"

        mock_client.api.pages.retrieve.return_value = updated_data

        page = Page(mock_client, page_data)
        await page.save()

        assert page.title == "Updated"
        mock_client.api.pages.retrieve.assert_called_once_with(page_id="page-123")


class TestPageRepr:
    """Tests for Page string representation."""

    def test_repr(self, mock_client, page_data):
        """Test __repr__ method."""
        page = Page(mock_client, page_data)

        repr_str = repr(page)

        assert "Page" in repr_str
        assert "page-123" in repr_str
        assert "Test Page" in repr_str
