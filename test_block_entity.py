"""Test Block entity implementation."""

import asyncio
from datetime import datetime, timezone
from unittest.mock import AsyncMock, Mock

from better_notion._api import NotionAPI
from better_notion._api.entities import Block


def test_block_datetime_properties():
    """Test Block datetime properties return datetime objects."""
    print("[TEST] Block datetime properties")

    api = Mock(spec=NotionAPI)

    block_data = {
        "id": "block_123",
        "object": "block",
        "type": "paragraph",
        "created_time": "2025-01-15T10:30:00.000Z",
        "last_edited_time": "2025-01-15T11:00:00.000Z",
        "paragraph": {"rich_text": [{"type": "text", "text": {"content": "Test"}}]}
    }

    block = Block(api, block_data)

    # Test created_time returns datetime
    created = block.created_time
    assert isinstance(created, datetime), f"created_time should be datetime, got {type(created)}"
    assert created.year == 2025
    assert created.month == 1
    assert created.day == 15
    print("[OK] created_time returns datetime")

    # Test last_edited_time returns datetime
    edited = block.last_edited_time
    assert isinstance(edited, datetime), f"last_edited_time should be datetime, got {type(edited)}"
    assert edited.year == 2025
    assert edited.month == 1
    assert edited.day == 15
    print("[OK] last_edited_time returns datetime")

    # Test we can use datetime methods
    assert created.strftime("%Y-%m-%d") == "2025-01-15"
    print("[OK] Can use datetime methods on created_time")


async def test_block_update():
    """Test Block.update() method."""
    print("[TEST] Block.update() method")

    api = Mock(spec=NotionAPI)
    api._request = AsyncMock(return_value={"paragraph": {"rich_text": []}})

    block_data = {
        "id": "block_123",
        "object": "block",
        "type": "paragraph",
        "created_time": "2025-01-15T10:30:00.000Z",
        "last_edited_time": "2025-01-15T11:00:00.000Z",
        "paragraph": {"rich_text": [{"type": "text", "text": {"content": "Original"}}]},
        "archived": False
    }

    block = Block(api, block_data)

    # Test update with archived
    await block.update(archived=True)
    assert block._data["archived"] == True
    await block.save()
    api._request.assert_called_once()
    print("[OK] update() with archived works")

    # Test update with content
    new_content = {"rich_text": [{"type": "text", "text": {"content": "Updated"}}]}
    api._request = AsyncMock(return_value={"paragraph": new_content})

    await block.update(content=new_content)
    assert block._data["paragraph"] == new_content
    print("[OK] update() with content works")


async def test_block_update_validation():
    """Test Block.update() validates property names."""
    print("[TEST] Block.update() validation")

    api = Mock(spec=NotionAPI)
    block_data = {
        "id": "block_123",
        "object": "block",
        "type": "paragraph",
        "created_time": "2025-01-15T10:30:00.000Z",
        "last_edited_time": "2025-01-15T11:00:00.000Z",
        "paragraph": {"rich_text": []},
        "archived": False
    }

    block = Block(api, block_data)

    # Test invalid property name
    try:
        await block.update(invalid_property="value")
        assert False, "Should raise ValueError for invalid property"
    except ValueError as e:
        assert "Invalid block property" in str(e)
        assert "invalid_property" in str(e).lower()
        assert "Valid properties are:" in str(e)
        print(f"[OK] update() validates property names: {e}")

    # Test invalid property value for archived
    try:
        await block.update(archived="not_a_boolean")
        assert False, "Should raise ValueError for non-boolean archived"
    except ValueError as e:
        assert "archived must be a boolean" in str(e)
        print(f"[OK] update() validates archived type: {e}")


async def test_block_modified_tracking():
    """Test Block tracks modified properties."""
    print("[TEST] Block modified property tracking")

    api = Mock(spec=NotionAPI)
    api._request = AsyncMock(return_value={"paragraph": {"rich_text": []}})

    block_data = {
        "id": "block_123",
        "object": "block",
        "type": "paragraph",
        "created_time": "2025-01-15T10:30:00.000Z",
        "last_edited_time": "2025-01-15T11:00:00.000Z",
        "paragraph": {"rich_text": []},
        "archived": False
    }

    block = Block(api, block_data)

    # Initially not modified
    assert not block._modified
    assert len(block._modified_properties) == 0

    # After update, should be marked as modified
    await block.update(archived=True)
    assert block._modified
    assert "archived" in block._modified_properties

    # After save, should not be marked as modified
    await block.save()
    assert not block._modified
    print("[OK] update() marks block as modified, save() resets it")


async def test_block_has_valid_properties():
    """Test Block has VALID_PROPERTIES constant."""
    print("[TEST] Block VALID_PROPERTIES")

    api = Mock(spec=NotionAPI)

    block_data = {
        "id": "block_123",
        "created_time": "2025-01-15T10:30:00.000Z",
        "last_edited_time": "2025-01-15T11:00:00.000Z",
        "type": "paragraph",
        "paragraph": {"rich_text": []}
    }

    block = Block(api, block_data)

    # Check VALID_PROPERTIES exists and has correct values
    assert hasattr(block, "VALID_PROPERTIES")
    assert "content" in block.VALID_PROPERTIES
    assert "archived" in block.VALID_PROPERTIES
    print("[OK] VALID_PROPERTIES exists")
    print(f"[OK] VALID_PROPERTIES: {', '.join(sorted(block.VALID_PROPERTIES))}")


async def test_block_has_all_required_features():
    """Test Block has all required features."""
    print("[TEST] Block has all required features")

    api = Mock(spec=NotionAPI)

    block_data = {
        "id": "block_123",
        "type": "paragraph",
        "created_time": "2025-01-15T10:30:00.000Z",
        "last_edited_time": "2025-01-15T11:00:00.000Z",
        "paragraph": {"rich_text": [{"type": "text", "text": {"content": "Test"}}]},
        "archived": False
    }

    block = Block(api, block_data)

    # Check methods exist
    assert hasattr(block, "save")
    assert callable(block.save)
    print("[OK] Block has save() method")

    assert hasattr(block, "delete")
    assert callable(block.delete)
    print("[OK] Block has delete() method")

    assert hasattr(block, "reload")
    assert callable(block.reload)
    print("[OK] Block has reload() method")

    assert hasattr(block, "update")
    assert callable(block.update)
    print("[OK] Block has update() method")

    # Check properties exist
    assert hasattr(block, "id")
    assert block.id == "block_123"
    print("[OK] Block has id property")

    assert hasattr(block, "type")
    assert block.type == "paragraph"
    print("[OK] Block has type property")

    assert hasattr(block, "created_time")
    assert isinstance(block.created_time, datetime)
    print("[OK] Block has created_time datetime property")

    assert hasattr(block, "last_edited_time")
    assert isinstance(block.last_edited_time, datetime)
    print("[OK] Block has last_edited_time datetime property")

    assert hasattr(block, "archived")
    assert isinstance(block.archived, bool)
    print("[OK] Block has archived property")

    # Check validation methods exist
    assert hasattr(block, "_validate_property_value")
    assert callable(block._validate_property_value)
    print("[OK] Block has _validate_property_value() method")

    assert hasattr(block, "_validate_property")
    assert callable(block._validate_property)
    print("[OK] Block has _validate_property() method")


async def run_all_tests():
    """Run all Block entity tests."""
    print("=" * 60)
    print("Testing Block Entity Implementation (#73)")
    print("=" * 60)

    # Synchronous tests
    test_block_datetime_properties()

    # Async tests
    await test_block_update()
    await test_block_update_validation()
    await test_block_modified_tracking()
    await test_block_has_valid_properties()
    await test_block_has_all_required_features()

    print("=" * 60)
    print("[OK] All Block entity tests passed!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(run_all_tests())
