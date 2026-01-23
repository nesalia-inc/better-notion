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
from better_notion._api.entities import Block, Page


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

    @pytest.mark.asyncio
    async def test_create_page(self, mock_api, sample_page_data):
        """Test creating a new page."""
        mock_api._request = AsyncMock(return_value=sample_page_data)

        page_data = {
            "parent": {"database_id": "database_id"},
            "properties": {
                "Name": {
                    "type": "title",
                    "title": [{"text": {"content": "New Page"}}]
                }
            }
        }

        page = await mock_api.pages.create(**page_data)

        assert isinstance(page, Page)
        mock_api._request.assert_called_once_with("POST", "/pages", json=page_data)

    @pytest.mark.asyncio
    async def test_create_page_validation_error(self, mock_api):
        """Test creating a page with invalid data raises ValidationError."""
        from better_notion._api.errors import ValidationError

        mock_api._request = AsyncMock(
            side_effect=ValidationError("parent is required")
        )

        with pytest.raises(ValidationError):
            await mock_api.pages.create()

    @pytest.mark.asyncio
    async def test_list_pages(self, mock_api, sample_page_data):
        """Test listing pages in a database."""
        query_response = {
            "results": [
                sample_page_data,
                {
                    **sample_page_data,
                    "id": "another_page_id"
                }
            ],
            "has_more": False
        }
        mock_api._request = AsyncMock(return_value=query_response)

        pages = await mock_api.pages.list("database_id")

        assert len(pages) == 2
        assert all(isinstance(page, Page) for page in pages)
        assert pages[0].id == "5c6a28216bb14a7eb6e1c50111515c3d"
        assert pages[1].id == "another_page_id"

    @pytest.mark.asyncio
    async def test_list_pages_empty(self, mock_api):
        """Test listing pages when database is empty."""
        mock_api._request = AsyncMock(return_value={"results": [], "has_more": False})

        pages = await mock_api.pages.list("database_id")

        assert len(pages) == 0

    @pytest.mark.asyncio
    async def test_list_pages_with_filter(self, mock_api, sample_page_data):
        """Test listing pages with a filter."""
        query_response = {
            "results": [sample_page_data],
            "has_more": False
        }
        mock_api._request = AsyncMock(return_value=query_response)

        filter_param = {
            "property": "Status",
            "select": {"equals": "Done"}
        }

        pages = await mock_api.pages.list("database_id", filter=filter_param)

        assert len(pages) == 1
        mock_api._request.assert_called_once_with(
            "POST",
            "/databases/database_id/query",
            json={"filter": filter_param},
        )


class TestBlockCollection:
    """Test suite for BlockCollection."""

    @pytest.mark.asyncio
    async def test_get_block(self, mock_api):
        """Test retrieving a block by ID."""
        block_data = {
            "id": "block_id",
            "type": "paragraph",
            "paragraph": {"text": [{"text": {"content": "Hello"}}]}
        }
        mock_api._request = AsyncMock(return_value=block_data)

        block = await mock_api.blocks.get("block_id")

        assert isinstance(block, Block)
        assert block.id == "block_id"

    @pytest.mark.asyncio
    async def test_get_block_not_found(self, mock_api):
        """Test retrieving a non-existent block raises NotFoundError."""
        from better_notion._api.errors import NotFoundError

        mock_api._request = AsyncMock(side_effect=NotFoundError("Block not found"))

        with pytest.raises(NotFoundError):
            await mock_api.blocks.get("nonexistent_block_id")

    @pytest.mark.asyncio
    async def test_block_children(self, mock_api):
        """Test getting children blocks."""
        children_response = {
            "results": [
                {
                    "id": "child1",
                    "type": "paragraph",
                    "paragraph": {}
                },
                {
                    "id": "child2",
                    "type": "paragraph",
                    "paragraph": {}
                }
            ]
        }
        mock_api._request = AsyncMock(return_value=children_response)

        blocks = BlockCollection(mock_api, parent_id="parent_id")
        children = await blocks.children()

        assert len(children) == 2
        assert all(isinstance(block, Block) for block in children)
        assert children[0].id == "child1"
        assert children[1].id == "child2"

    @pytest.mark.asyncio
    async def test_block_children_no_parent_id(self, mock_api):
        """Test getting children without parent_id raises ValueError."""
        blocks = BlockCollection(mock_api)

        with pytest.raises(ValueError, match="parent_id is required"):
            await blocks.children()

    @pytest.mark.asyncio
    async def test_block_append(self, mock_api):
        """Test appending a new block."""
        append_response = {
            "results": [
                {
                    "id": "new_block",
                    "type": "paragraph",
                    "paragraph": {"text": [{"text": {"content": "New"}}]}
                }
            ]
        }
        mock_api._request = AsyncMock(return_value=append_response)

        blocks = BlockCollection(mock_api, parent_id="parent_id")
        block_data = {
            "children": [
                {
                    "object": "block",
                    "type": "paragraph",
                    "paragraph": {"text": [{"text": {"content": "New"}}]}
                }
            ]
        }

        block = await blocks.append(**block_data)

        assert isinstance(block, Block)
        mock_api._request.assert_called_once()

    @pytest.mark.asyncio
    async def test_block_append_no_parent_id(self, mock_api):
        """Test appending without parent_id raises ValueError."""
        blocks = BlockCollection(mock_api)

        with pytest.raises(ValueError, match="parent_id is required"):
            await blocks.append()
