"""Test API collections."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest

from better_notion._api.collections import (
    BlockCollection,
    DatabaseCollection,
    PageCollection,
    UserCollection,
)
from better_notion._api.entities import Page


class TestCollections:
    """Test suite for API collections."""

    def test_pages_collection_initialized(self, mock_api):
        """Test Pages collection is initialized correctly."""
        assert isinstance(mock_api.pages, PageCollection)
        assert mock_api.pages._api is mock_api

    def test_blocks_collection_initialized(self, mock_api):
        """Test Blocks collection is initialized correctly."""
        assert isinstance(mock_api.blocks, BlockCollection)
        assert mock_api.blocks._api is mock_api

    def test_databases_collection_initialized(self, mock_api):
        """Test Databases collection is initialized correctly."""
        assert isinstance(mock_api.databases, DatabaseCollection)
        assert mock_api.databases._api is mock_api

    def test_users_collection_initialized(self, mock_api):
        """Test Users collection is initialized correctly."""
        assert isinstance(mock_api.users, UserCollection)
        assert mock_api.users._api is mock_api


class TestPageCollection:
    """Test suite for PageCollection."""

    @pytest.mark.asyncio
    async def test_get_page(self, mock_api, sample_page_data):
        """Test retrieving a page by ID."""
        # Mock the _request method
        mock_api._request = AsyncMock(return_value=sample_page_data)

        page = await mock_api.pages.get("5c6a28216bb14a7eb6e1c50111515c3d")

        assert isinstance(page, Page)
        assert page.id == "5c6a28216bb14a7eb6e1c50111515c3d"

    @pytest.mark.asyncio
    async def test_get_page_not_found(self, mock_api):
        """Test retrieving a non-existent page raises NotFoundError."""
        from better_notion._api.errors import NotFoundError

        # Mock the _request method to raise NotFoundError
        mock_api._request = AsyncMock(side_effect=NotFoundError("Page not found"))

        with pytest.raises(NotFoundError):
            await mock_api.pages.get("nonexistent_page_id")
