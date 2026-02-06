"""Test BlockCollection implementation."""

import asyncio
from unittest.mock import AsyncMock, Mock

from better_notion._api import NotionAPI
from better_notion._api.collections import BlockCollection
from better_notion._api.entities import Block


async def test_block_collection_get_returns_entity():
    """Test BlockCollection.get() returns Block entity."""
    print("[TEST] BlockCollection.get() returns Block entity")

    api = Mock(spec=NotionAPI)

    block_data = {
        "id": "block_123",
        "object": "block",
        "type": "paragraph",
        "created_time": "2025-01-15T10:30:00.000Z",
        "last_edited_time": "2025-01-15T11:00:00.000Z",
        "paragraph": {"rich_text": [{"type": "text", "text": {"content": "Test"}}]},
        "archived": False
    }

    api._request = AsyncMock(return_value=block_data)

    collection = BlockCollection(api)
    result = await collection.get("block_123")

    # Check result is Block entity
    assert isinstance(result, Block), f"Expected Block, got {type(result)}"
    assert result.id == "block_123"
    assert result.type == "paragraph"
    assert isinstance(result.created_time, datetime)
    print("[OK] get() returns Block entity with correct properties")


async def test_block_collection_children_returns_entities():
    """Test BlockCollection.children() returns list of Block entities."""
    print("[TEST] BlockCollection.children() returns list of Block entities")

    api = Mock(spec=NotionAPI)

    children_data = {
        "object": "list",
        "results": [
            {
                "id": "child_1",
                "type": "paragraph",
                "created_time": "2025-01-15T10:30:00.000Z",
                "last_edited_time": "2025-01-15T11:00:00.000Z",
                "paragraph": {"rich_text": [{"type": "text", "text": {"content": "Child 1"}}]},
                "archived": False
            },
            {
                "id": "child_2",
                "type": "heading_1",
                "created_time": "2025-01-15T10:31:00.000Z",
                "last_edited_time": "2025-01-15T11:01:00.000Z",
                "heading_1": {"rich_text": [{"type": "text", "text": {"content": "Heading"}}]},
                "archived": False
            }
        ]
    }

    api._request = AsyncMock(return_value=children_data)

    collection = BlockCollection(api, parent_id="parent_123")
    results = await collection.children()

    # Check result is list of Block entities
    assert isinstance(results, list), f"Expected list, got {type(results)}"
    assert len(results) == 2
    assert all(isinstance(r, Block) for r in results), "All items should be Block entities"
    assert results[0].id == "child_1"
    assert results[1].id == "child_2"
    print("[OK] children() returns list[Block] with correct entities")


async def test_block_collection_append_returns_entity():
    """Test BlockCollection.append() returns Block entity."""
    print("[TEST] BlockCollection.append() returns Block entity")

    api = Mock(spec=NotionAPI)

    new_block_data = {
        "id": "new_block_123",
        "type": "paragraph",
        "created_time": "2025-01-15T10:30:00.000Z",
        "last_edited_time": "2025-01-15T11:00:00.000Z",
        "paragraph": {"rich_text": [{"type": "text", "text": {"content": "New block"}}]},
        "archived": False
    }

    api._request = AsyncMock(return_value={"results": [new_block_data]})

    collection = BlockCollection(api, parent_id="parent_123")
    result = await collection.append(paragraph={"rich_text": [{"type": "text", "text": {"content": "New block"}}]})

    # Check result is Block entity
    assert isinstance(result, Block), f"Expected Block, got {type(result)}"
    assert result.id == "new_block_123"
    print("[OK] append() returns Block entity")


async def test_block_collection_update_returns_entity():
    """Test BlockCollection.update() returns Block entity."""
    print("[TEST] BlockCollection.update() returns Block entity")

    api = Mock(spec=NotionAPI)

    updated_block_data = {
        "id": "block_123",
        "type": "paragraph",
        "created_time": "2025-01-15T10:30:00.000Z",
        "last_edited_time": "2025-01-15T11:00:00.000Z",
        "paragraph": {"rich_text": [{"type": "text", "text": {"content": "Updated"}}]},
        "archived": False
    }

    api._request = AsyncMock(return_value=updated_block_data)

    collection = BlockCollection(api)
    result = await collection.update("block_123", paragraph={"rich_text": [{"type": "text", "text": {"content": "Updated"}}]})

    # Check result is Block entity
    assert isinstance(result, Block), f"Expected Block, got {type(result)}"
    assert result.id == "block_123"
    print("[OK] update() returns Block entity")


async def test_block_collection_delete():
    """Test BlockCollection.delete() method."""
    print("[TEST] BlockCollection.delete() method")

    api = Mock(spec=NotionAPI)
    api._request = AsyncMock(return_value=None)

    collection = BlockCollection(api)
    await collection.delete("block_123")

    api._request.assert_called_once_with("DELETE", "/blocks/block_123")
    print("[OK] delete() calls API correctly")


async def test_block_collection_consistency_with_entity():
    """Test BlockCollection methods are consistent with Entity pattern."""
    print("[TEST] BlockCollection consistency with Entity pattern")

    api = Mock(spec=NotionAPI)

    block_data = {
        "id": "block_123",
        "type": "paragraph",
        "created_time": "2025-01-15T10:30:00.000Z",
        "last_edited_time": "2025-01-15T11:00:00.000Z",
        "paragraph": {"rich_text": [{"type": "text", "text": {"content": "Test"}}]},
        "archived": False
    }

    api._request = AsyncMock(return_value=block_data)

    collection = BlockCollection(api)
    block = await collection.get("block_123")

    # Test Entity methods exist and work
    assert hasattr(block, "save")
    assert callable(block.save)
    print("[OK] Block from collection has save() method")

    assert hasattr(block, "delete")
    assert callable(block.delete)
    print("[OK] Block from collection has delete() method")

    assert hasattr(block, "reload")
    assert callable(block.reload)
    print("[OK] Block from collection has reload() method")

    assert hasattr(block, "update")
    assert callable(block.update)
    print("[OK] Block from collection has update() method")

    # Test Entity properties
    assert hasattr(block, "id")
    assert block.id == "block_123"
    print("[OK] Block from collection has id property")

    assert hasattr(block, "type")
    assert block.type == "paragraph"
    print("[OK] Block from collection has type property")

    assert hasattr(block, "archived")
    assert isinstance(block.archived, bool)
    print("[OK] Block from collection has archived property")


async def run_all_tests():
    """Run all BlockCollection tests."""
    print("=" * 60)
    print("Testing BlockCollection Implementation (#70)")
    print("=" * 60)

    await test_block_collection_get_returns_entity()
    await test_block_collection_children_returns_entities()
    await test_block_collection_append_returns_entity()
    await test_block_collection_update_returns_entity()
    await test_block_collection_delete()
    await test_block_collection_consistency_with_entity()

    print("=" * 60)
    print("[OK] All BlockCollection tests passed!")
    print("=" * 60)


if __name__ == "__main__":
    from datetime import datetime
    asyncio.run(run_all_tests())
