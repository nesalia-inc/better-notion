"""Test entity classes."""

from __future__ import annotations

from unittest.mock import AsyncMock

import pytest

from better_notion._api import NotionAPI
from better_notion._api.entities import Block, Database, Page, User


class TestEntities:
    """Test suite for entity classes."""

    def test_page_entity_creation(self, mock_api, sample_page_data):
        """Test Page entity creation."""
        page = Page(mock_api, sample_page_data)

        assert page.id == "5c6a28216bb14a7eb6e1c50111515c3d"
        assert page.archived is False
        assert "properties" in page._data

    def test_page_entity_properties(self, sample_page_data):
        """Test Page entity properties."""
        api = NotionAPI(auth="secret_test")
        page = Page(api, sample_page_data)

        assert page.id == sample_page_data["id"]
        assert page.properties == sample_page_data["properties"]

    @pytest.mark.asyncio
    async def test_page_save(self, mock_api, sample_page_data):
        """Test Page save method."""
        mock_api._request = AsyncMock(return_value=sample_page_data)
        page = Page(mock_api, sample_page_data)

        await page.save()

        mock_api._request.assert_called_once_with(
            "PATCH",
            "/pages/5c6a28216bb14a7eb6e1c50111515c3d",
            json={"properties": sample_page_data["properties"]},
        )
        assert page._modified is False

    @pytest.mark.asyncio
    async def test_page_save_not_found(self, mock_api, sample_page_data):
        """Test Page save with NotFoundError."""
        from better_notion._api.errors import NotFoundError

        mock_api._request = AsyncMock(side_effect=NotFoundError("Page not found"))
        page = Page(mock_api, sample_page_data)

        with pytest.raises(NotFoundError):
            await page.save()

    @pytest.mark.asyncio
    async def test_page_delete(self, mock_api, sample_page_data):
        """Test Page delete method."""
        mock_api._request = AsyncMock(return_value={**sample_page_data, "archived": True})
        page = Page(mock_api, sample_page_data)

        await page.delete()

        mock_api._request.assert_called_once_with(
            "PATCH",
            "/pages/5c6a28216bb14a7eb6e1c50111515c3d",
            json={"archived": True},
        )
        assert page._data["archived"] is True

    @pytest.mark.asyncio
    async def test_page_delete_not_found(self, mock_api, sample_page_data):
        """Test Page delete with NotFoundError."""
        from better_notion._api.errors import NotFoundError

        mock_api._request = AsyncMock(side_effect=NotFoundError("Page not found"))
        page = Page(mock_api, sample_page_data)

        with pytest.raises(NotFoundError):
            await page.delete()

    @pytest.mark.asyncio
    async def test_page_reload(self, mock_api, sample_page_data):
        """Test Page reload method."""
        updated_data = {**sample_page_data, "last_edited_time": "2025-01-16T00:00:00.000Z"}
        mock_api._request = AsyncMock(return_value=updated_data)

        page = Page(mock_api, sample_page_data)
        await page.reload()

        mock_api._request.assert_called_once_with("GET", "/pages/5c6a28216bb14a7eb6e1c50111515c3d")
        assert page._data == updated_data
        assert page._modified is False

    @pytest.mark.asyncio
    async def test_page_reload_not_found(self, mock_api, sample_page_data):
        """Test Page reload with NotFoundError."""
        from better_notion._api.errors import NotFoundError

        mock_api._request = AsyncMock(side_effect=NotFoundError("Page not found"))
        page = Page(mock_api, sample_page_data)

        with pytest.raises(NotFoundError):
            await page.reload()

    @pytest.mark.asyncio
    async def test_page_update(self, mock_api, sample_page_data):
        """Test Page update method."""
        page = Page(mock_api, sample_page_data)

        new_properties = {
            "Name": {
                "type": "title",
                "title": [{"text": {"content": "Updated Title"}}]
            }
        }

        await page.update(properties=new_properties)

        # update() now stores in _modified_properties, not _data
        assert page._modified_properties == new_properties
        assert page._modified is True

    @pytest.mark.asyncio
    async def test_page_update_archived(self, mock_api, sample_page_data):
        """Test Page update archived status."""
        page = Page(mock_api, sample_page_data)

        await page.update(archived=True)

        # update() now stores in _modified_properties
        assert page._modified_properties["archived"] is True
        assert page._modified is True

    def test_page_blocks_property(self, mock_api, sample_page_data):
        """Test Page blocks property returns BlockCollection."""
        from better_notion._api.collections import BlockCollection

        page = Page(mock_api, sample_page_data)
        blocks = page.blocks

        assert isinstance(blocks, BlockCollection)
        assert blocks._parent_id == page.id

    def test_block_entity_creation(self, mock_api):
        """Test Block entity creation."""
        block_data = {
            "id": "block_id",
            "type": "paragraph",
            "paragraph": {}
        }
        block = Block(mock_api, block_data)

        assert block.id == "block_id"
        assert block.type == "paragraph"

    @pytest.mark.asyncio
    async def test_block_save(self, mock_api):
        """Test Block save method."""
        block_data = {
            "id": "block_id",
            "type": "paragraph",
            "paragraph": {"text": [{"text": {"content": "Hello"}}]}
        }
        mock_api._request = AsyncMock(return_value=block_data)
        block = Block(mock_api, block_data)

        await block.save()

        mock_api._request.assert_called_once()
        call_args = mock_api._request.call_args
        assert call_args[0][0] == "PATCH"
        assert call_args[0][1] == "/blocks/block_id"
        assert "paragraph" in call_args[1]["json"]
        assert block._modified is False

    @pytest.mark.asyncio
    async def test_block_delete(self, mock_api):
        """Test Block delete method."""
        block_data = {
            "id": "block_id",
            "type": "paragraph",
            "paragraph": {}
        }
        mock_api._request = AsyncMock(return_value={})
        block = Block(mock_api, block_data)

        await block.delete()

        mock_api._request.assert_called_once_with("DELETE", "/blocks/block_id")

    @pytest.mark.asyncio
    async def test_block_reload(self, mock_api):
        """Test Block reload method."""
        block_data = {
            "id": "block_id",
            "type": "paragraph",
            "paragraph": {"text": [{"text": {"content": "Hello"}}]}
        }
        updated_data = {
            "id": "block_id",
            "type": "paragraph",
            "paragraph": {"text": [{"text": {"content": "Hello World"}}]}
        }
        mock_api._request = AsyncMock(return_value=updated_data)

        block = Block(mock_api, block_data)
        await block.reload()

        mock_api._request.assert_called_once_with("GET", "/blocks/block_id")
        assert block._data == updated_data
        assert block._modified is False

    @pytest.mark.asyncio
    async def test_block_content_property(self, mock_api):
        """Test Block content property getter and setter."""
        block_data = {
            "id": "block_id",
            "type": "paragraph",
            "paragraph": {"text": [{"text": {"content": "Hello"}}]}
        }
        block = Block(mock_api, block_data)

        content = block.content
        assert content["text"][0]["text"]["content"] == "Hello"

        new_content = {"text": [{"text": {"content": "New Content"}}]}
        block.content = new_content
        assert block._data["paragraph"] == new_content
        assert block._modified is True

    def test_database_entity_creation(self, mock_api):
        """Test Database entity creation."""
        database_data = {
            "id": "database_id",
            "object": "database",
            "title": [{"type": "text", "text": {"content": "Test"}}],
            "properties": {}
        }
        database = Database(mock_api, database_data)

        assert database.id == "database_id"
        assert database.title == database_data["title"]
        assert database.properties == database_data["properties"]

    def test_user_entity_creation(self, mock_api):
        """Test User entity creation."""
        user_data = {
            "id": "user_id",
            "type": "person",
            "name": "Test User",
            "avatar_url": "https://example.com/avatar.png"
        }
        user = User(mock_api, user_data)

        assert user.id == "user_id"
        assert user.name == "Test User"
        assert user.avatar_url == "https://example.com/avatar.png"
        assert user.type == "person"

    def test_page_entity_repr(self, sample_page_data):
        """Test Page entity string representation."""
        api = NotionAPI(auth="secret_test")
        page = Page(api, sample_page_data)

        assert repr(page) == "Page(id='5c6a28216bb14a7eb6e1c50111515c3d')"

    def test_block_entity_repr(self, mock_api):
        """Test Block entity string representation."""
        block_data = {
            "id": "block_id",
            "type": "paragraph",
        }
        block = Block(mock_api, block_data)

        assert repr(block) == "Block(id='block_id', type='paragraph')"

    def test_database_entity_repr(self, mock_api):
        """Test Database entity string representation."""
        database_data = {
            "id": "database_id",
            "object": "database",
        }
        database = Database(mock_api, database_data)

        assert repr(database) == "Database(id='database_id')"

    def test_user_entity_repr(self, mock_api):
        """Test User entity string representation."""
        user_data = {
            "id": "user_id",
            "name": "Test User",
        }
        user = User(mock_api, user_data)

        assert "user_id" in repr(user)
        assert "Test User" in repr(user)
