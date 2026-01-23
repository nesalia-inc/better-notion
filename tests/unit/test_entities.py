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
