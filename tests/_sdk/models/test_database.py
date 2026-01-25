"""Tests for Database model."""

import pytest
from unittest.mock import AsyncMock, MagicMock

from better_notion._sdk.models.database import Database
from better_notion._sdk.cache import Cache


@pytest.fixture
def mock_client():
    """Create mock NotionClient."""
    client = MagicMock()
    client.api = MagicMock()

    # Mock API methods
    client.api.databases = MagicMock()
    client.api.databases.retrieve = AsyncMock()
    client.api.databases.create = AsyncMock()
    client.api.databases.query = AsyncMock()
    client.api.pages = MagicMock()
    client.api.pages.retrieve = AsyncMock()

    # Setup caches
    client.page_cache = Cache()
    client.database_cache = Cache()
    client._page_cache = client.page_cache
    client._database_cache = client.database_cache

    return client


@pytest.fixture
def database_data():
    """Sample database data from Notion API."""
    return {
        "id": "db-123",
        "object": "database",
        "created_time": "2024-01-01T00:00:00.000Z",
        "last_edited_time": "2024-01-01T00:00:00.000Z",
        "archived": False,
        "title": [
            {
                "type": "text",
                "text": {"content": "Test Database"}
            }
        ],
        "description": [
            {
                "type": "text",
                "text": {"content": "Test Description"}
            }
        ],
        "properties": {
            "Name": {
                "id": "prop-name",
                "type": "title",
                "title": {}
            },
            "Status": {
                "id": "prop-status",
                "type": "select",
                "select": {
                    "options": [
                        {"id": "opt-1", "name": "Not Started", "color": "gray"},
                        {"id": "opt-2", "name": "In Progress", "color": "blue"},
                        {"id": "opt-3", "name": "Done", "color": "green"}
                    ]
                }
            },
            "Priority": {
                "id": "prop-priority",
                "type": "number",
                "number": {"format": "number"}
            }
        },
        "parent": {
            "type": "page_id",
            "page_id": "page-123"
        }
    }


class TestDatabaseInit:
    """Tests for Database initialization."""

    def test_init_with_client_and_data(self, mock_client, database_data):
        """Test initialization with client and data."""
        database = Database(mock_client, database_data)

        assert database.id == "db-123"
        assert database.object == "database"
        assert database._client is mock_client
        assert database._data == database_data

    def test_init_parses_schema(self, mock_client, database_data):
        """Test initialization parses schema."""
        database = Database(mock_client, database_data)

        assert "Name" in database._schema
        assert "Status" in database._schema
        assert "Priority" in database._schema

        assert database._schema["Name"]["type"] == "title"
        assert database._schema["Status"]["type"] == "select"
        assert database._schema["Priority"]["type"] == "number"


class TestDatabaseMetadata:
    """Tests for Database metadata properties."""

    def test_title_property(self, mock_client, database_data):
        """Test title property."""
        database = Database(mock_client, database_data)

        assert database.title == "Test Database"

    def test_title_empty(self, mock_client):
        """Test title with empty title array."""
        data = {
            "id": "db-123",
            "object": "database",
            "title": []
        }
        database = Database(mock_client, data)

        assert database.title == ""

    def test_description_property(self, mock_client, database_data):
        """Test description property."""
        database = Database(mock_client, database_data)

        assert database.description == "Test Description"

    def test_description_empty(self, mock_client):
        """Test description with empty array."""
        data = {
            "id": "db-123",
            "object": "database",
            "description": []
        }
        database = Database(mock_client, data)

        assert database.description == ""

    def test_icon_emoji(self, mock_client):
        """Test icon property with emoji."""
        data = {
            "id": "db-123",
            "object": "database",
            "properties": {},
            "icon": {
                "type": "emoji",
                "emoji": "📊"
            }
        }
        database = Database(mock_client, data)

        assert database.icon == "📊"

    def test_icon_none(self, mock_client):
        """Test icon property when no icon."""
        data = {
            "id": "db-123",
            "object": "database",
            "properties": {}
        }
        database = Database(mock_client, data)

        assert database.icon is None

    def test_cover_external(self, mock_client):
        """Test cover property with external URL."""
        data = {
            "id": "db-123",
            "object": "database",
            "properties": {},
            "cover": {
                "type": "external",
                "external": {"url": "https://example.com/cover.png"}
            }
        }
        database = Database(mock_client, data)

        assert database.cover == "https://example.com/cover.png"

    def test_cover_none(self, mock_client):
        """Test cover property when no cover."""
        data = {
            "id": "db-123",
            "object": "database",
            "properties": {}
        }
        database = Database(mock_client, data)

        assert database.cover is None

    def test_url_property(self, mock_client, database_data):
        """Test URL property."""
        database = Database(mock_client, database_data)

        assert database.url == "https://notion.so/db123"

    def test_archived_property(self, mock_client):
        """Test archived property."""
        data = {
            "id": "db-123",
            "object": "database",
            "properties": {},
            "archived": True
        }
        database = Database(mock_client, data)

        assert database.archived is True

    def test_is_inline_page_parent(self, mock_client):
        """Test is_inline with page parent."""
        data = {
            "id": "db-123",
            "object": "database",
            "properties": {},
            "parent": {"type": "page_id", "page_id": "page-123"}
        }
        database = Database(mock_client, data)

        assert database.is_inline is True

    def test_is_inline_workspace(self, mock_client):
        """Test is_inline with workspace parent."""
        data = {
            "id": "db-123",
            "object": "database",
            "properties": {},
            "parent": {"type": "workspace"}
        }
        database = Database(mock_client, data)

        assert database.is_inline is False


class TestDatabaseSchema:
    """Tests for Database schema properties."""

    def test_schema_property(self, mock_client, database_data):
        """Test schema property."""
        database = Database(mock_client, database_data)

        assert "Name" in database.schema
        assert "Status" in database.schema
        assert "Priority" in database.schema

    def test_schema_includes_select_options(self, mock_client, database_data):
        """Test schema includes select options."""
        database = Database(mock_client, database_data)

        status_schema = database.schema["Status"]
        assert "options" in status_schema
        assert status_schema["options"] == ["Not Started", "In Progress", "Done"]

    def test_schema_includes_number_format(self, mock_client, database_data):
        """Test schema includes number format."""
        database = Database(mock_client, database_data)

        priority_schema = database.schema["Priority"]
        assert "format" in priority_schema

    def test_get_property_type(self, mock_client, database_data):
        """Test getting property type."""
        database = Database(mock_client, database_data)

        assert database.get_property_type("Status") == "select"
        assert database.get_property_type("Priority") == "number"
        assert database.get_property_type("Name") == "title"

    def test_get_property_type_case_insensitive(self, mock_client, database_data):
        """Test get_property_type is case-insensitive."""
        database = Database(mock_client, database_data)

        assert database.get_property_type("status") == "select"
        assert database.get_property_type("STATUS") == "select"

    def test_get_property_type_not_found(self, mock_client, database_data):
        """Test get_property_type with unknown property."""
        database = Database(mock_client, database_data)

        assert database.get_property_type("Unknown") is None

    def test_get_property_options(self, mock_client, database_data):
        """Test getting select options."""
        database = Database(mock_client, database_data)

        options = database.get_property_options("Status")

        assert options == ["Not Started", "In Progress", "Done"]

    def test_get_property_options_not_select(self, mock_client, database_data):
        """Test get_property_options with non-select property."""
        database = Database(mock_client, database_data)

        with pytest.raises(ValueError, match="not select/multi_select"):
            database.get_property_options("Priority")

    def test_get_property_options_not_found(self, mock_client, database_data):
        """Test get_property_options with unknown property."""
        database = Database(mock_client, database_data)

        with pytest.raises(ValueError, match="not found"):
            database.get_property_options("Unknown")

    def test_list_properties(self, mock_client, database_data):
        """Test listing all properties."""
        database = Database(mock_client, database_data)

        props = database.list_properties()

        assert "Name" in props
        assert "Status" in props
        assert "Priority" in props
        assert len(props) == 3

    def test_has_property_exists(self, mock_client, database_data):
        """Test has_property when property exists."""
        database = Database(mock_client, database_data)

        assert database.has_property("Status") is True

    def test_has_property_not_exists(self, mock_client, database_data):
        """Test has_property when property doesn't exist."""
        database = Database(mock_client, database_data)

        assert database.has_property("Unknown") is False

    def test_has_property_case_insensitive(self, mock_client, database_data):
        """Test has_property is case-insensitive."""
        database = Database(mock_client, database_data)

        assert database.has_property("status") is True

    def test_find_property_exact(self, mock_client, database_data):
        """Test find_property with exact match."""
        database = Database(mock_client, database_data)

        schema = database.find_property("Status")

        assert schema is not None
        assert schema["type"] == "select"

    def test_find_property_fuzzy(self, mock_client, database_data):
        """Test find_property with fuzzy match."""
        database = Database(mock_client, database_data)

        schema = database.find_property("stat", fuzzy=True)

        assert schema is not None
        assert schema["type"] == "select"

    def test_find_property_not_found(self, mock_client, database_data):
        """Test find_property with no match."""
        database = Database(mock_client, database_data)

        schema = database.find_property("xyz", fuzzy=True)

        assert schema is None


class TestDatabaseClassMethods:
    """Tests for Database class methods (autonomous entity)."""

    @pytest.mark.asyncio
    async def test_get_from_api(self, mock_client, database_data):
        """Test Database.get() fetches from API."""
        mock_client.api.databases.retrieve.return_value = database_data

        database = await Database.get(database_id="db-123", client=mock_client)

        assert database.id == "db-123"
        assert database.title == "Test Database"
        mock_client.api.databases.retrieve.assert_called_once_with(database_id="db-123")

    @pytest.mark.asyncio
    async def test_get_uses_cache(self, mock_client, database_data):
        """Test Database.get() uses cache."""
        # Pre-populate cache
        cached_db = Database(mock_client, database_data)
        mock_client.database_cache["db-123"] = cached_db

        database = await Database.get(database_id="db-123", client=mock_client)

        assert database is cached_db
        # API should not be called
        mock_client.api.databases.retrieve.assert_not_called()


class TestDatabaseNavigation:
    """Tests for Database navigation methods."""

    @pytest.mark.asyncio
    async def test_parent_page(self, mock_client, database_data):
        """Test getting parent page."""
        # Mock page fetch with complete page data
        page_data = {
            "id": "page-123",
            "object": "page",
            "created_time": "2024-01-01T00:00:00.000Z",
            "last_edited_time": "2024-01-01T00:00:00.000Z",
            "archived": False,
            "properties": {
                "Name": {
                    "id": "prop-name",
                    "type": "title",
                    "title": [
                        {
                            "type": "text",
                            "text": {"content": "Parent Page"}
                        }
                    ]
                }
            }
        }
        mock_client.api.pages.retrieve.return_value = page_data

        database = Database(mock_client, database_data)
        parent = await database.parent()

        assert parent.id == "page-123"
        assert parent.title == "Parent Page"

    @pytest.mark.asyncio
    async def test_parent_uses_cache(self, mock_client, database_data):
        """Test parent() caches result."""
        page_data = {
            "id": "page-123",
            "object": "page",
            "properties": {
                "Name": {
                    "type": "title",
                    "title": [{"text": {"content": "Parent Page"}}]
                }
            }
        }
        mock_client.api.pages.retrieve.return_value = page_data

        database = Database(mock_client, database_data)

        # First call - fetches from API
        parent1 = await database.parent()

        # Second call - uses cache
        parent2 = await database.parent()

        assert parent1 is parent2
        # API should only be called once
        mock_client.api.pages.retrieve.assert_called_once()

    @pytest.mark.asyncio
    async def test_children_empty(self, mock_client):
        """Test children() with no pages."""
        mock_client.api.databases.query.return_value = {
            "results": [],
            "has_more": False,
            "next_cursor": None
        }

        data = {
            "id": "db-123",
            "object": "database",
            "properties": {}
        }
        database = Database(mock_client, data)

        children = []
        async for child in database.children():
            children.append(child)

        assert len(children) == 0

    @pytest.mark.asyncio
    async def test_children_with_pages(self, mock_client):
        """Test children() with pages."""
        mock_client.api.databases.query.return_value = {
            "results": [
                {
                    "id": "page-1",
                    "object": "page",
                    "properties": {
                        "Name": {
                            "type": "title",
                            "title": [{"text": {"content": "Page 1"}}]
                        }
                    }
                }
            ],
            "has_more": False,
            "next_cursor": None
        }

        data = {
            "id": "db-123",
            "object": "database",
            "properties": {}
        }
        database = Database(mock_client, data)

        children = []
        async for child in database.children():
            children.append(child)

        assert len(children) == 1
        assert children[0].id == "page-1"


class TestDatabaseAnalytics:
    """Tests for Database analytics methods."""

    @pytest.mark.asyncio
    async def test_count(self, mock_client):
        """Test counting pages."""
        mock_client.api.databases.query.return_value = {
            "results": [
                {"id": "page-1", "object": "page", "properties": {}},
                {"id": "page-2", "object": "page", "properties": {}},
                {"id": "page-3", "object": "page", "properties": {}}
            ],
            "has_more": False,
            "next_cursor": None
        }

        data = {
            "id": "db-123",
            "object": "database",
            "properties": {}
        }
        database = Database(mock_client, data)

        count = await database.count()

        assert count == 3


class TestDatabaseRepr:
    """Tests for Database string representation."""

    def test_repr(self, mock_client, database_data):
        """Test __repr__ method."""
        database = Database(mock_client, database_data)

        repr_str = repr(database)

        assert "Database" in repr_str
        assert "db-123" in repr_str
        assert "Test Database" in repr_str
