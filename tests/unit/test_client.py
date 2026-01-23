"""Test the NotionAPI client."""

from __future__ import annotations

from unittest.mock import AsyncMock

import pytest

from better_notion._api import NotionAPI
from better_notion._api.collections import (
    BlockCollection,
    DatabaseCollection,
    PageCollection,
    UserCollection,
)


class TestNotionAPI:
    """Test suite for NotionAPI client."""

    def test_init_with_valid_token(self):
        """Test initialization with valid token."""
        api = NotionAPI(auth="secret_test_token")
        assert api._token == "secret_test_token"
        assert api._base_url == "https://api.notion.com/v1"

    def test_init_with_invalid_token(self):
        """Test initialization fails with invalid token."""
        try:
            NotionAPI(auth="invalid_token")
        except ValueError as e:
            assert 'must start with "secret_"' in str(e)

    def test_default_headers(self):
        """Test default headers are set correctly."""
        api = NotionAPI(auth="secret_test")
        headers = api._default_headers()

        assert headers["Authorization"] == "Bearer secret_test"
        assert headers["Notion-Version"] == "2022-06-28"
        assert headers["Content-Type"] == "application/json"

    def test_custom_base_url(self):
        """Test custom base URL."""
        api = NotionAPI(
            auth="secret_test",
            base_url="https://custom.example.com"
        )
        assert api._base_url == "https://custom.example.com"

    def test_custom_timeout(self):
        """Test custom timeout."""
        api = NotionAPI(auth="secret_test", timeout=60.0)
        assert api._timeout == 60.0

    def test_collections_initialized(self):
        """Test all collections are initialized."""
        api = NotionAPI(auth="secret_test")

        assert isinstance(api.pages, PageCollection)
        assert isinstance(api.blocks, BlockCollection)
        assert isinstance(api.databases, DatabaseCollection)
        assert isinstance(api.users, UserCollection)

    @pytest.mark.asyncio
    async def test_search(self, mock_api, sample_page_data):
        """Test search method."""
        search_response = {
            "results": [sample_page_data],
            "has_more": False
        }
        mock_api._request = AsyncMock(return_value=search_response)

        result = await mock_api.search("test query")

        assert "results" in result
        assert len(result["results"]) == 1
        mock_api._request.assert_called_once_with(
            "POST",
            "/search",
            json={"query": "test query"},
        )

    @pytest.mark.asyncio
    async def test_search_with_filter(self, mock_api, sample_page_data):
        """Test search with filter parameter."""
        search_response = {
            "results": [sample_page_data],
            "has_more": False
        }
        mock_api._request = AsyncMock(return_value=search_response)

        filter_param = {"value": "page", "property": "object"}
        result = await mock_api.search("test query", filter=filter_param)

        assert "results" in result
        assert mock_api._request.call_args[1]["json"]["filter"] == filter_param

    @pytest.mark.asyncio
    async def test_search_iterate_single_page(self, mock_api, sample_page_data):
        """Test search iteration with single page of results."""
        search_response = {
            "results": [sample_page_data],
            "has_more": False
        }
        mock_api._request = AsyncMock(return_value=search_response)

        results = await mock_api.search_iterate("test query").to_list()

        assert len(results) == 1
        assert results[0]["id"] == sample_page_data["id"]

    @pytest.mark.asyncio
    async def test_search_iterate_multiple_pages(self, mock_api, sample_page_data):
        """Test search iteration with multiple pages of results."""
        result2_data = {**sample_page_data, "id": "result2_id"}

        call_count = 0

        async def mock_request(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                return {
                    "results": [sample_page_data],
                    "has_more": True,
                    "next_cursor": "cursor123"
                }
            else:
                return {
                    "results": [result2_data],
                    "has_more": False
                }

        mock_api._request = AsyncMock(side_effect=mock_request)

        results = await mock_api.search_iterate("test query").to_list()

        assert len(results) == 2
        assert results[0]["id"] == sample_page_data["id"]
        assert results[1]["id"] == "result2_id"
