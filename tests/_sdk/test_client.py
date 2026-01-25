"""Tests for NotionClient."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from better_notion._sdk.client import NotionClient
from better_notion._sdk.cache import Cache


async def async_iterable(items):
    """Helper to create an async iterable from a list."""
    for item in items:
        yield item


@pytest.fixture
def mock_api():
    """Create mock NotionAPI."""
    api = MagicMock()
    api.search = MagicMock()
    api.search.query = AsyncMock(return_value=async_iterable([]))
    api.users = MagicMock()
    api.users.list = AsyncMock(return_value=async_iterable([]))
    return api


class TestNotionClientInit:
    """Tests for NotionClient initialization."""

    def test_init_with_auth(self, mock_api):
        """Test initialization with auth token."""
        with patch('better_notion._sdk.client.NotionAPI', return_value=mock_api):
            client = NotionClient(auth="test_token")

        assert client._api is mock_api
        assert isinstance(client._user_cache, Cache)
        assert isinstance(client._database_cache, Cache)
        assert isinstance(client._page_cache, Cache)

    def test_init_creates_managers(self, mock_api):
        """Test initialization creates all managers."""
        with patch('better_notion._sdk.client.NotionAPI', return_value=mock_api):
            client = NotionClient(auth="test_token")

        assert hasattr(client, 'pages')
        assert hasattr(client, 'databases')
        assert hasattr(client, 'blocks')
        assert hasattr(client, 'users')


class TestNotionClientManagers:
    """Tests for manager properties."""

    def test_pages_manager(self, mock_api):
        """Test pages manager property."""
        with patch('better_notion._sdk.client.NotionAPI', return_value=mock_api):
            client = NotionClient(auth="test_token")

        assert client.pages is not None
        assert client.pages._client is client

    def test_databases_manager(self, mock_api):
        """Test databases manager property."""
        with patch('better_notion._sdk.client.NotionAPI', return_value=mock_api):
            client = NotionClient(auth="test_token")

        assert client.databases is not None
        assert client.databases._client is client

    def test_blocks_manager(self, mock_api):
        """Test blocks manager property."""
        with patch('better_notion._sdk.client.NotionAPI', return_value=mock_api):
            client = NotionClient(auth="test_token")

        assert client.blocks is not None
        assert client.blocks._client is client

    def test_users_manager(self, mock_api):
        """Test users manager property."""
        with patch('better_notion._sdk.client.NotionAPI', return_value=mock_api):
            client = NotionClient(auth="test_token")

        assert client.users is not None
        assert client.users._client is client


class TestNotionClientCacheAccess:
    """Tests for cache access properties."""

    def test_user_cache_property(self, mock_api):
        """Test user_cache property."""
        with patch('better_notion._sdk.client.NotionAPI', return_value=mock_api):
            client = NotionClient(auth="test_token")

        assert client.user_cache is client._user_cache

    def test_database_cache_property(self, mock_api):
        """Test database_cache property."""
        with patch('better_notion._sdk.client.NotionAPI', return_value=mock_api):
            client = NotionClient(auth="test_token")

        assert client.database_cache is client._database_cache

    def test_page_cache_property(self, mock_api):
        """Test page_cache property."""
        with patch('better_notion._sdk.client.NotionAPI', return_value=mock_api):
            client = NotionClient(auth="test_token")

        assert client.page_cache is client._page_cache


class TestNotionClientAPIAccess:
    """Tests for low-level API access."""

    def test_api_property(self, mock_api):
        """Test api property returns NotionAPI."""
        with patch('better_notion._sdk.client.NotionAPI', return_value=mock_api):
            client = NotionClient(auth="test_token")

        assert client.api is mock_api


class TestNotionClientCacheManagement:
    """Tests for cache management methods."""

    def test_clear_all_caches(self, mock_api):
        """Test clearing all caches."""
        with patch('better_notion._sdk.client.NotionAPI', return_value=mock_api):
            client = NotionClient(auth="test_token")

            # Add items to caches
            client._user_cache.set("user1", "user_data")
            client._database_cache.set("db1", "db_data")
            client._page_cache.set("page1", "page_data")
            client._search_cache["key"] = []

            assert len(client._user_cache) == 1
            assert len(client._database_cache) == 1
            assert len(client._page_cache) == 1

            client.clear_all_caches()

            assert len(client._user_cache) == 0
            assert len(client._database_cache) == 0
            assert len(client._page_cache) == 0
            assert len(client._search_cache) == 0

    def test_get_cache_stats(self, mock_api):
        """Test getting cache statistics."""
        with patch('better_notion._sdk.client.NotionAPI', return_value=mock_api):
            client = NotionClient(auth="test_token")

            # Add some items to test stats
            client._user_cache.set("user1", "data")
            client._user_cache.get("user1")  # hit
            client._user_cache.get("user2")  # miss

            stats = client.get_cache_stats()

            assert "user_cache" in stats
            assert "database_cache" in stats
            assert "page_cache" in stats
            assert "search_cache" in stats

            assert stats["user_cache"]["size"] == 1
            assert stats["user_cache"]["hits"] == 1
            assert stats["user_cache"]["misses"] == 1


class TestNotionClientSearch:
    """Tests for search functionality."""

    @pytest.mark.asyncio
    async def test_search_empty(self, mock_api):
        """Test search with no results."""
        # Create an async iterator mock
        async def search_iterator(*args, **kwargs):
            return
            yield  # Make it an async generator

        mock_api.search.query = search_iterator
        with patch('better_notion._sdk.client.NotionAPI', return_value=mock_api):
            client = NotionClient(auth="test_token")

        results = await client.search()

        assert results == []

    @pytest.mark.asyncio
    async def test_search_with_query(self, mock_api):
        """Test search with query string."""
        # Create an async iterator mock
        async def search_iterator(*args, **kwargs):
            yield {"id": "page1", "object": "page"}
            yield {"id": "page2", "object": "page"}

        mock_api.search.query = search_iterator
        with patch('better_notion._sdk.client.NotionAPI', return_value=mock_api):
            client = NotionClient(auth="test_token")

        results = await client.search(query="test")

        assert len(results) == 2

    @pytest.mark.asyncio
    async def test_search_with_filter(self, mock_api):
        """Test search with filter."""
        # Create an async iterator mock
        async def search_iterator(*args, **kwargs):
            return
            yield  # Make it an async generator

        mock_api.search.query = search_iterator
        with patch('better_notion._sdk.client.NotionAPI', return_value=mock_api):
            client = NotionClient(auth="test_token")

        await client.search(
            query="test",
            filter={"value": "page", "property": "object"}
        )


class TestNotionClientContextManager:
    """Tests for context manager support."""

    @pytest.mark.asyncio
    async def test_context_manager(self, mock_api):
        """Test async context manager."""
        with patch('better_notion._sdk.client.NotionAPI', return_value=mock_api):
            async with NotionClient(auth="test_token") as client:
                # Add to cache
                client._user_cache.set("test", "value")
                assert len(client._user_cache) == 1

            # After exit, cache should be cleared
            assert len(client._user_cache) == 0
