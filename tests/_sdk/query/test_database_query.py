"""Tests for DatabaseQuery."""

import pytest
from unittest.mock import AsyncMock, MagicMock

from better_notion._sdk.query.database_query import DatabaseQuery, SortConfig


@pytest.fixture
def mock_client():
    """Create mock NotionClient."""
    client = MagicMock()
    client.api = MagicMock()
    client.api.databases = MagicMock()
    client.api.databases.query = AsyncMock()

    return client


@pytest.fixture
def database_schema():
    """Sample database schema."""
    return {
        "Name": {"id": "name", "type": "title"},
        "Status": {"id": "status", "type": "select"},
        "Priority": {"id": "priority", "type": "number"},
        "DueDate": {"id": "due_date", "type": "date"},
    }


@pytest.fixture
def sample_page_data():
    """Sample page data from Notion API."""
    return {
        "id": "page-123",
        "object": "page",
        "created_time": "2024-01-01T00:00:00.000Z",
        "last_edited_time": "2024-01-01T00:00:00.000Z",
        "archived": False,
        "properties": {
            "Name": {
                "id": "name",
                "type": "title",
                "title": [
                    {
                        "type": "text",
                        "text": {"content": "Test Page"}
                    }
                ]
            }
        }
    }


class TestSortConfig:
    """Tests for SortConfig dataclass."""

    def test_sort_config_creation(self):
        """Test SortConfig creation."""
        config = SortConfig(property="due_date", direction="ascending")

        assert config.property == "due_date"
        assert config.direction == "ascending"

    def test_sort_config_default_direction(self):
        """Test SortConfig default direction."""
        config = SortConfig(property="priority")

        assert config.property == "priority"
        assert config.direction == "ascending"


class TestDatabaseQueryInit:
    """Tests for DatabaseQuery initialization."""

    def test_init_with_client_and_id(self, mock_client, database_schema):
        """Test initialization with client and database ID."""
        query = DatabaseQuery(
            client=mock_client,
            database_id="db-123",
            schema=database_schema
        )

        assert query._client is mock_client
        assert query._database_id == "db-123"
        assert query._schema is database_schema
        assert query._filters == []
        assert query._sorts == []
        assert query._limit is None

    def test_init_with_initial_filters(self, mock_client, database_schema):
        """Test initialization with initial filters."""
        query = DatabaseQuery(
            client=mock_client,
            database_id="db-123",
            schema=database_schema,
            filters={"status": "Done"}
        )

        assert len(query._filters) == 1
        assert query._filters[0] == {
            "property": "status",
            "select": {"equals": "Done"}
        }

    def test_init_with_multiple_initial_filters(self, mock_client, database_schema):
        """Test initialization with multiple initial filters."""
        query = DatabaseQuery(
            client=mock_client,
            database_id="db-123",
            schema=database_schema,
            filters={
                "status": "Done",
                "priority__gte": 5
            }
        )

        assert len(query._filters) == 2

    def test_init_parses_operator_from_key(self, mock_client, database_schema):
        """Test that operator is parsed from key with double underscore."""
        query = DatabaseQuery(
            client=mock_client,
            database_id="db-123",
            schema=database_schema,
            filters={"priority__gte": 5}
        )

        assert len(query._filters) == 1
        assert query._filters[0] == {
            "property": "priority",
            "number": {"greater_than_or_equal_to": 5}
        }


class TestDatabaseQueryFilter:
    """Tests for DatabaseQuery.filter() method."""

    def test_filter_adds_single_condition(self, mock_client, database_schema):
        """Test filter() adds single condition."""
        query = DatabaseQuery(
            client=mock_client,
            database_id="db-123",
            schema=database_schema
        )

        result = query.filter(status="Done")

        assert len(query._filters) == 1
        assert result is query  # Returns self for chaining

    def test_filter_adds_multiple_conditions(self, mock_client, database_schema):
        """Test filter() with multiple conditions."""
        query = DatabaseQuery(
            client=mock_client,
            database_id="db-123",
            schema=database_schema
        )

        query.filter(
            status="Done",
            priority__gte=5
        )

        assert len(query._filters) == 2

    def test_filter_chaining(self, mock_client, database_schema):
        """Test filter() method chaining."""
        query = DatabaseQuery(
            client=mock_client,
            database_id="db-123",
            schema=database_schema
        )

        result = query.filter(status="Done").filter(priority__gte=5)

        assert len(query._filters) == 2
        assert result is query


class TestDatabaseQuerySort:
    """Tests for DatabaseQuery.sort() method."""

    def test_sort_adds_single_sort(self, mock_client, database_schema):
        """Test sort() adds single sort configuration."""
        query = DatabaseQuery(
            client=mock_client,
            database_id="db-123",
            schema=database_schema
        )

        result = query.sort("due_date", "ascending")

        assert len(query._sorts) == 1
        assert query._sorts[0].property == "due_date"
        assert query._sorts[0].direction == "ascending"
        assert result is query  # Returns self for chaining

    def test_sort_default_direction(self, mock_client, database_schema):
        """Test sort() uses ascending as default direction."""
        query = DatabaseQuery(
            client=mock_client,
            database_id="db-123",
            schema=database_schema
        )

        query.sort("priority")

        assert query._sorts[0].direction == "ascending"

    def test_sort_chaining(self, mock_client, database_schema):
        """Test sort() method chaining."""
        query = DatabaseQuery(
            client=mock_client,
            database_id="db-123",
            schema=database_schema
        )

        query.sort("due_date").sort("priority", "descending")

        assert len(query._sorts) == 2

    def test_sort_invalid_direction_raises_error(self, mock_client, database_schema):
        """Test sort() with invalid direction raises ValueError."""
        query = DatabaseQuery(
            client=mock_client,
            database_id="db-123",
            schema=database_schema
        )

        with pytest.raises(ValueError, match="Direction must be 'ascending' or 'descending'"):
            query.sort("priority", "invalid")


class TestDatabaseQueryLimit:
    """Tests for DatabaseQuery.limit() method."""

    def test_limit_sets_max_results(self, mock_client, database_schema):
        """Test limit() sets maximum results."""
        query = DatabaseQuery(
            client=mock_client,
            database_id="db-123",
            schema=database_schema
        )

        result = query.limit(10)

        assert query._limit == 10
        assert result is query  # Returns self for chaining

    def test_limit_zero_raises_error(self, mock_client, database_schema):
        """Test limit(0) raises ValueError."""
        query = DatabaseQuery(
            client=mock_client,
            database_id="db-123",
            schema=database_schema
        )

        with pytest.raises(ValueError, match="Limit must be positive"):
            query.limit(0)

    def test_limit_negative_raises_error(self, mock_client, database_schema):
        """Test limit(-1) raises ValueError."""
        query = DatabaseQuery(
            client=mock_client,
            database_id="db-123",
            schema=database_schema
        )

        with pytest.raises(ValueError, match="Limit must be positive"):
            query.limit(-1)


class TestDatabaseQueryExecute:
    """Tests for DatabaseQuery.execute() method."""

    @pytest.mark.asyncio
    async def test_execute_empty_query(self, mock_client, database_schema, sample_page_data):
        """Test execute() with no filters."""
        mock_client.api.databases.query.return_value = {
            "results": [sample_page_data],
            "has_more": False,
            "next_cursor": None
        }

        query = DatabaseQuery(
            client=mock_client,
            database_id="db-123",
            schema=database_schema
        )

        pages = []
        async for page in query.execute():
            pages.append(page)

        assert len(pages) == 1
        assert pages[0].id == "page-123"

        # Verify API call
        mock_client.api.databases.query.assert_called_once_with(
            database_id="db-123"
        )

    @pytest.mark.asyncio
    async def test_execute_with_single_filter(self, mock_client, database_schema, sample_page_data):
        """Test execute() with single filter."""
        mock_client.api.databases.query.return_value = {
            "results": [sample_page_data],
            "has_more": False,
            "next_cursor": None
        }

        query = DatabaseQuery(
            client=mock_client,
            database_id="db-123",
            schema=database_schema,
            filters={"status": "Done"}
        )

        async for page in query.execute():
            assert page.id == "page-123"

        # Verify API call with filter
        call_args = mock_client.api.databases.query.call_args
        assert call_args[1]["database_id"] == "db-123"
        assert "filter" in call_args[1]
        assert call_args[1]["filter"]["select"]["equals"] == "Done"

    @pytest.mark.asyncio
    async def test_execute_with_multiple_filters(self, mock_client, database_schema, sample_page_data):
        """Test execute() with multiple filters (combined with AND)."""
        mock_client.api.databases.query.return_value = {
            "results": [sample_page_data],
            "has_more": False,
            "next_cursor": None
        }

        query = DatabaseQuery(
            client=mock_client,
            database_id="db-123",
            schema=database_schema
        )
        query.filter(status="Done", priority__gte=5)

        async for page in query.execute():
            assert page.id == "page-123"

        # Verify filters are combined with AND
        call_args = mock_client.api.databases.query.call_args
        assert "filter" in call_args[1]
        assert "and" in call_args[1]["filter"]
        assert len(call_args[1]["filter"]["and"]) == 2

    @pytest.mark.asyncio
    async def test_execute_with_sorts(self, mock_client, database_schema, sample_page_data):
        """Test execute() with sort orders."""
        mock_client.api.databases.query.return_value = {
            "results": [sample_page_data],
            "has_more": False,
            "next_cursor": None
        }

        query = DatabaseQuery(
            client=mock_client,
            database_id="db-123",
            schema=database_schema
        )
        query.sort("due_date", "ascending").sort("priority", "descending")

        async for page in query.execute():
            assert page.id == "page-123"

        # Verify sorts
        call_args = mock_client.api.databases.query.call_args
        assert "sorts" in call_args[1]
        assert len(call_args[1]["sorts"]) == 2
        assert call_args[1]["sorts"][0]["property"] == "due_date"
        assert call_args[1]["sorts"][0]["direction"] == "ascending"
        assert call_args[1]["sorts"][1]["property"] == "priority"
        assert call_args[1]["sorts"][1]["direction"] == "descending"

    @pytest.mark.asyncio
    async def test_execute_with_limit(self, mock_client, database_schema, sample_page_data):
        """Test execute() with limit truncates results."""
        # Create 5 sample pages
        pages_data = [
            {**sample_page_data, "id": f"page-{i}"}
            for i in range(5)
        ]

        mock_client.api.databases.query.return_value = {
            "results": pages_data,
            "has_more": False,
            "next_cursor": None
        }

        query = DatabaseQuery(
            client=mock_client,
            database_id="db-123",
            schema=database_schema
        )
        query.limit(3)

        pages = []
        async for page in query.execute():
            pages.append(page)

        # Should only return 3 pages
        assert len(pages) == 3

    @pytest.mark.asyncio
    async def test_execute_with_pagination(self, mock_client, database_schema, sample_page_data):
        """Test execute() handles pagination."""
        # First page
        first_page = {
            "results": [{**sample_page_data, "id": "page-1"}],
            "has_more": True,
            "next_cursor": "cursor-123"
        }

        # Second page
        second_page = {
            "results": [{**sample_page_data, "id": "page-2"}],
            "has_more": False,
            "next_cursor": None
        }

        mock_client.api.databases.query.side_effect = [first_page, second_page]

        query = DatabaseQuery(
            client=mock_client,
            database_id="db-123",
            schema=database_schema
        )

        pages = []
        async for page in query.execute():
            pages.append(page)

        assert len(pages) == 2
        assert pages[0].id == "page-1"
        assert pages[1].id == "page-2"

        # Verify multiple API calls
        assert mock_client.api.databases.query.call_count == 2

        # Verify second call includes cursor
        second_call_args = mock_client.api.databases.query.call_args_list[1]
        assert second_call_args[1]["start_cursor"] == "cursor-123"


class TestDatabaseQueryAsyncIteration:
    """Tests for DatabaseQuery async iteration."""

    @pytest.mark.asyncio
    async def test_aiter_iterates_results(self, mock_client, database_schema, sample_page_data):
        """Test __aiter__ allows async iteration."""
        mock_client.api.databases.query.return_value = {
            "results": [sample_page_data],
            "has_more": False,
            "next_cursor": None
        }

        query = DatabaseQuery(
            client=mock_client,
            database_id="db-123",
            schema=database_schema
        )

        pages = []
        async for page in query:
            pages.append(page)

        assert len(pages) == 1


class TestDatabaseQueryConvenienceMethods:
    """Tests for DatabaseQuery convenience methods."""

    @pytest.mark.asyncio
    async def test_collect_returns_list(self, mock_client, database_schema, sample_page_data):
        """Test collect() returns list of all pages."""
        mock_client.api.databases.query.return_value = {
            "results": [
                {**sample_page_data, "id": "page-1"},
                {**sample_page_data, "id": "page-2"},
            ],
            "has_more": False,
            "next_cursor": None
        }

        query = DatabaseQuery(
            client=mock_client,
            database_id="db-123",
            schema=database_schema
        )

        pages = await query.collect()

        assert len(pages) == 2
        assert pages[0].id == "page-1"
        assert pages[1].id == "page-2"

    @pytest.mark.asyncio
    async def test_collect_empty_results(self, mock_client, database_schema):
        """Test collect() with no results returns empty list."""
        mock_client.api.databases.query.return_value = {
            "results": [],
            "has_more": False,
            "next_cursor": None
        }

        query = DatabaseQuery(
            client=mock_client,
            database_id="db-123",
            schema=database_schema
        )

        pages = await query.collect()

        assert len(pages) == 0

    @pytest.mark.asyncio
    async def test_first_returns_first_page(self, mock_client, database_schema, sample_page_data):
        """Test first() returns first matching page."""
        mock_client.api.databases.query.return_value = {
            "results": [sample_page_data],
            "has_more": False,
            "next_cursor": None
        }

        query = DatabaseQuery(
            client=mock_client,
            database_id="db-123",
            schema=database_schema
        )

        page = await query.first()

        assert page is not None
        assert page.id == "page-123"

    @pytest.mark.asyncio
    async def test_first_no_results_returns_none(self, mock_client, database_schema):
        """Test first() with no results returns None."""
        mock_client.api.databases.query.return_value = {
            "results": [],
            "has_more": False,
            "next_cursor": None
        }

        query = DatabaseQuery(
            client=mock_client,
            database_id="db-123",
            schema=database_schema
        )

        page = await query.first()

        assert page is None

    @pytest.mark.asyncio
    async def test_count_returns_number(self, mock_client, database_schema, sample_page_data):
        """Test count() returns number of matching pages."""
        mock_client.api.databases.query.return_value = {
            "results": [
                {**sample_page_data, "id": "page-1"},
                {**sample_page_data, "id": "page-2"},
                {**sample_page_data, "id": "page-3"},
            ],
            "has_more": False,
            "next_cursor": None
        }

        query = DatabaseQuery(
            client=mock_client,
            database_id="db-123",
            schema=database_schema
        )

        count = await query.count()

        assert count == 3

    @pytest.mark.asyncio
    async def test_count_zero_results(self, mock_client, database_schema):
        """Test count() with no results returns 0."""
        mock_client.api.databases.query.return_value = {
            "results": [],
            "has_more": False,
            "next_cursor": None
        }

        query = DatabaseQuery(
            client=mock_client,
            database_id="db-123",
            schema=database_schema
        )

        count = await query.count()

        assert count == 0

    @pytest.mark.asyncio
    async def test_exists_true(self, mock_client, database_schema, sample_page_data):
        """Test exists() returns True when results exist."""
        mock_client.api.databases.query.return_value = {
            "results": [sample_page_data],
            "has_more": False,
            "next_cursor": None
        }

        query = DatabaseQuery(
            client=mock_client,
            database_id="db-123",
            schema=database_schema
        )

        result = await query.exists()

        assert result is True

    @pytest.mark.asyncio
    async def test_exists_false(self, mock_client, database_schema):
        """Test exists() returns False when no results."""
        mock_client.api.databases.query.return_value = {
            "results": [],
            "has_more": False,
            "next_cursor": None
        }

        query = DatabaseQuery(
            client=mock_client,
            database_id="db-123",
            schema=database_schema
        )

        result = await query.exists()

        assert result is False


class TestDatabaseQueryRepr:
    """Tests for DatabaseQuery string representation."""

    def test_repr_with_filters(self, mock_client, database_schema):
        """Test __repr__ includes filter count."""
        query = DatabaseQuery(
            client=mock_client,
            database_id="db-123",
            schema=database_schema
        )
        query.filter(status="Done").filter(priority__gte=5)

        repr_str = repr(query)

        assert "DatabaseQuery" in repr_str
        assert "2 filters" in repr_str

    def test_repr_with_sorts(self, mock_client, database_schema):
        """Test __repr__ includes sort count."""
        query = DatabaseQuery(
            client=mock_client,
            database_id="db-123",
            schema=database_schema
        )
        query.sort("due_date").sort("priority")

        repr_str = repr(query)

        assert "DatabaseQuery" in repr_str
        assert "2 sorts" in repr_str

    def test_repr_with_limit(self, mock_client, database_schema):
        """Test __repr__ includes limit."""
        query = DatabaseQuery(
            client=mock_client,
            database_id="db-123",
            schema=database_schema
        )
        query.limit(10)

        repr_str = repr(query)

        assert "DatabaseQuery" in repr_str
        assert "limit=10" in repr_str

    def test_repr_empty_query(self, mock_client, database_schema):
        """Test __repr__ with empty query."""
        query = DatabaseQuery(
            client=mock_client,
            database_id="db-123",
            schema=database_schema
        )

        repr_str = repr(query)

        assert "DatabaseQuery" in repr_str
        assert "no filters" in repr_str

    def test_repr_combined(self, mock_client, database_schema):
        """Test __repr__ with filters, sorts, and limit."""
        query = DatabaseQuery(
            client=mock_client,
            database_id="db-123",
            schema=database_schema
        )
        query.filter(status="Done").sort("due_date").limit(10)

        repr_str = repr(query)

        assert "DatabaseQuery" in repr_str
        assert "1 filters" in repr_str
        assert "1 sorts" in repr_str
        assert "limit=10" in repr_str


class TestDatabaseQueryChaining:
    """Tests for complete query chaining."""

    @pytest.mark.asyncio
    async def test_full_builder_pattern(self, mock_client, database_schema, sample_page_data):
        """Test complete builder pattern chaining."""
        mock_client.api.databases.query.return_value = {
            "results": [sample_page_data],
            "has_more": False,
            "next_cursor": None
        }

        pages = await (DatabaseQuery(
            client=mock_client,
            database_id="db-123",
            schema=database_schema
        )
        .filter(status="Done")
        .filter(priority__gte=5)
        .sort("due_date")
        .sort("priority", "descending")
        .limit(10)
        .collect())

        assert len(pages) == 1

        # Verify all parameters were sent
        call_args = mock_client.api.databases.query.call_args
        assert "filter" in call_args[1]
        assert "sorts" in call_args[1]
        assert len(call_args[1]["sorts"]) == 2
