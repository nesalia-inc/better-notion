"""Test BaseCollection ABC implementation."""

import asyncio
from abc import ABC
from unittest.mock import AsyncMock, Mock

from better_notion._api import NotionAPI
from better_notion._api.collections import (
    BaseCollection, BlockCollection, CommentCollection, DatabaseCollection,
    EntityCollection, PageCollection
)
from better_notion._api.entities import Block, Comment, Database, Page


async def test_base_classes_exist():
    """Test that base ABC classes exist."""
    print("[TEST] Base ABC classes exist")

    # Check BaseCollection exists and is ABC
    assert BaseCollection is not None
    assert issubclass(BaseCollection, ABC)
    print("[OK] BaseCollection is an ABC")

    # Check EntityCollection exists and is ABC
    assert EntityCollection is not None
    assert issubclass(EntityCollection, ABC)
    print("[OK] EntityCollection is an ABC")

    # Check EntityCollection extends BaseCollection
    assert issubclass(EntityCollection, BaseCollection)
    print("[OK] EntityCollection extends BaseCollection")


async def test_collection_classes_inherit_correctly():
    """Test that collection classes inherit from correct base."""
    print("[TEST] Collection classes inherit correctly")

    # Check collections extend EntityCollection
    assert issubclass(PageCollection, EntityCollection)
    print("[OK] PageCollection extends EntityCollection")

    assert issubclass(DatabaseCollection, EntityCollection)
    print("[OK] DatabaseCollection extends EntityCollection")

    assert issubclass(BlockCollection, EntityCollection)
    print("[OK] BlockCollection extends EntityCollection")

    assert issubclass(CommentCollection, EntityCollection)
    print("[OK] CommentCollection extends EntityCollection")


async def test_entity_collection_has_required_interface():
    """Test that EntityCollection requires all abstract methods."""
    print("[TEST] EntityCollection requires all abstract methods")

    api = Mock(spec=NotionAPI)
    page_data = {
        "id": "page_123",
        "object": "page",
        "created_time": "2025-01-15T10:30:00.000Z",
        "last_edited_time": "2025-01-15T11:00:00.000Z",
        "properties": {},
        "archived": False
    }

    api._request = AsyncMock(return_value=page_data)

    collection = PageCollection(api)

    # Check EntityCollection interface methods exist
    assert hasattr(collection, "get")
    assert callable(collection.get)
    print("[OK] EntityCollection has get() method")

    assert hasattr(collection, "_entity_class")
    print("[OK] EntityCollection has _entity_class property")

    assert hasattr(collection, "_get_path")
    assert callable(collection._get_path)
    print("[OK] EntityCollection has _get_path() method")

    # Check get_many method (inherited)
    assert hasattr(collection, "get_many")
    assert callable(collection.get_many)
    print("[OK] EntityCollection has get_many() method")


async def test_base_collection_has_shared_request_method():
    """Test that BaseCollection provides _request method."""
    print("[TEST] BaseCollection provides _request method")

    api = Mock(spec=NotionAPI)
    page_data = {
        "id": "page_123",
        "object": "page",
        "created_time": "2025-01-15T10:30:00.000Z",
        "last_edited_time": "2025-01-15T11:00:00.000Z",
        "properties": {},
        "archived": False
    }

    api._request = AsyncMock(return_value=page_data)

    collection = PageCollection(api)

    # Check _request method exists
    assert hasattr(collection, "_request")
    assert callable(collection._request)
    print("[OK] BaseCollection has _request() method")


async def test_collection_init_inherited():
    """Test that __init__ is inherited from base class."""
    print("[TEST] Collection __init__ is inherited")

    api = Mock(spec=NotionAPI)

    collection = PageCollection(api)

    # Check that _api is set by base __init__
    assert hasattr(collection, "_api")
    assert collection._api is api
    print("[OK] PageCollection._api is set by base __init__")


async def test_get_many_strong_typing():
    """Test that get_many returns correct type."""
    print("[TEST] get_many returns strongly typed list")

    api = Mock(spec=NotionAPI)

    page1_data = {
        "id": "page_1",
        "object": "page",
        "created_time": "2025-01-15T10:30:00.000Z",
        "last_edited_time": "2025-01-15T11:00:00.000Z",
        "properties": {},
        "archived": False
    }

    page2_data = {
        "id": "page_2",
        "object": "page",
        "created_time": "2025-01-15T10:31:00.000Z",
        "last_edited_time": "2025-01-15T11:01:00.000Z",
        "properties": {},
        "archived": False
    }

    call_count = 0
    async def mock_request(*args, **kwargs):
        nonlocal call_count
        call_count += 1
        if call_count == 1:
            return page1_data
        else:
            return page2_data

    api._request = AsyncMock(side_effect=mock_request)

    collection = PageCollection(api)
    pages = await collection.get_many(["page_1", "page_2"])

    # Check result is list
    assert isinstance(pages, list)
    print("[OK] get_many returns list")

    # Check all items are Page entities
    assert all(isinstance(p, Page) for p in pages)
    print("[OK] get_many returns list[Page]")

    # Check correct number of items
    assert len(pages) == 2
    print("[OK] get_many returns correct number of items")


async def run_all_tests():
    """Run all BaseCollection ABC tests."""
    print("=" * 60)
    print("Testing BaseCollection ABC Implementation (#76)")
    print("=" * 60)

    await test_base_classes_exist()
    await test_collection_classes_inherit_correctly()
    await test_entity_collection_has_required_interface()
    await test_base_collection_has_shared_request_method()
    await test_collection_init_inherited()
    await test_get_many_strong_typing()

    print("=" * 60)
    print("[OK] All BaseCollection ABC tests passed!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(run_all_tests())
