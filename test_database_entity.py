"""Test Database entity implementation."""

import asyncio
from datetime import datetime, timezone
from unittest.mock import AsyncMock, Mock

from better_notion._api import NotionAPI
from better_notion._api.entities import Database


async def test_database_datetime_properties():
    """Test Database datetime properties return datetime objects."""
    print("[TEST] Database datetime properties")

    api = Mock(spec=NotionAPI)

    database_data = {
        "id": "database_123",
        "object": "database",
        "created_time": "2025-01-15T10:30:00.000Z",
        "last_edited_time": "2025-01-15T11:00:00.000Z",
        "title": [{"type": "text", "text": {"content": "Test Database"}}],
        "properties": {
            "Name": {"title": {}}
        }
    }

    database = Database(api, database_data)

    # Test created_time returns datetime
    created = database.created_time
    assert isinstance(created, datetime), f"created_time should be datetime, got {type(created)}"
    assert created.year == 2025
    assert created.month == 1
    assert created.day == 15
    print("[OK] created_time returns datetime")

    # Test last_edited_time returns datetime
    edited = database.last_edited_time
    assert isinstance(edited, datetime), f"last_edited_time should be datetime, got {type(edited)}"
    assert edited.year == 2025
    assert edited.month == 1
    assert edited.day == 15
    print("[OK] last_edited_time returns datetime")

    # Test we can use datetime methods
    assert created.strftime("%Y-%m-%d") == "2025-01-15"
    print("[OK] Can use datetime methods on created_time")


async def test_database_update():
    """Test Database.update() method."""
    print("[TEST] Database.update() method")

    api = Mock(spec=NotionAPI)
    api._request = AsyncMock(return_value={"title": [], "properties": {}})

    database_data = {
        "id": "database_123",
        "object": "database",
        "created_time": "2025-01-15T10:30:00.000Z",
        "last_edited_time": "2025-01-15T11:00:00.000Z",
        "title": [{"type": "text", "text": {"content": "Original"}}],
        "properties": {
            "Name": {"title": {}}
        }
    }

    database = Database(api, database_data)

    # Test update with title
    new_title = [{"type": "text", "text": {"content": "Updated"}}]
    await database.update(title=new_title)
    assert database._data["title"] == new_title
    print("[OK] update() with title works")

    # Test update with properties
    new_properties = {"Status": {"select": {"options": []}}}
    await database.update(properties=new_properties)
    assert database._data["properties"] == new_properties
    print("[OK] update() with properties works")


async def test_database_update_validation():
    """Test Database.update() validates property names."""
    print("[TEST] Database.update() validation")

    api = Mock(spec=NotionAPI)
    database_data = {
        "id": "database_123",
        "object": "database",
        "created_time": "2025-01-15T10:30:00.000Z",
        "last_edited_time": "2025-01-15T11:00:00.000Z",
        "title": [],
        "properties": {}
    }

    database = Database(api, database_data)

    # Test invalid property name
    try:
        await database.update(invalid_property="value")
        assert False, "Should raise ValueError for invalid property"
    except ValueError as e:
        assert "Invalid database property" in str(e)
        assert "invalid_property" in str(e).lower()
        assert "Valid properties are:" in str(e)
        print(f"[OK] update() validates property names: {e}")

    # Test invalid property value for title
    try:
        await database.update(title="not_a_list")
        assert False, "Should raise ValueError for non-list title"
    except ValueError as e:
        assert "title must be a list" in str(e)
        print(f"[OK] update() validates title type: {e}")

    # Test invalid property value for properties
    try:
        await database.update(properties="not_a_dict")
        assert False, "Should raise ValueError for non-dict properties"
    except ValueError as e:
        assert "properties must be a dict" in str(e)
        print(f"[OK] update() validates properties type: {e}")


async def test_database_modified_tracking():
    """Test Database tracks modified properties."""
    print("[TEST] Database modified property tracking")

    api = Mock(spec=NotionAPI)
    api._request = AsyncMock(return_value={"title": [], "properties": {}})

    database_data = {
        "id": "database_123",
        "object": "database",
        "created_time": "2025-01-15T10:30:00.000Z",
        "last_edited_time": "2025-01-15T11:00:00.000Z",
        "title": [],
        "properties": {}
    }

    database = Database(api, database_data)

    # Initially not modified
    assert not database._modified
    assert len(database._modified_properties) == 0

    # After update, should be marked as modified
    await database.update(title=[{"type": "text", "text": {"content": "New"}}])
    assert database._modified
    assert "title" in database._modified_properties

    # After save, should not be marked as modified
    await database.save()
    assert not database._modified
    print("[OK] update() marks database as modified, save() resets it")


async def test_database_has_valid_properties():
    """Test Database has VALID_PROPERTIES constant."""
    print("[TEST] Database VALID_PROPERTIES")

    api = Mock(spec=NotionAPI)

    database_data = {
        "id": "database_123",
        "created_time": "2025-01-15T10:30:00.000Z",
        "last_edited_time": "2025-01-15T11:00:00.000Z",
        "title": [],
        "properties": {}
    }

    database = Database(api, database_data)

    # Check VALID_PROPERTIES exists and has correct values
    assert hasattr(database, "VALID_PROPERTIES")
    assert "properties" in database.VALID_PROPERTIES
    assert "title" in database.VALID_PROPERTIES
    print("[OK] VALID_PROPERTIES exists")
    print(f"[OK] VALID_PROPERTIES: {', '.join(sorted(database.VALID_PROPERTIES))}")


async def test_database_has_all_required_features():
    """Test Database has all required features."""
    print("[TEST] Database has all required features")

    api = Mock(spec=NotionAPI)

    database_data = {
        "id": "database_123",
        "object": "database",
        "created_time": "2025-01-15T10:30:00.000Z",
        "last_edited_time": "2025-01-15T11:00:00.000Z",
        "title": [],
        "properties": {},
        "archived": False
    }

    database = Database(api, database_data)

    # Check methods exist
    assert hasattr(database, "save")
    assert callable(database.save)
    print("[OK] Database has save() method")

    assert hasattr(database, "delete")
    assert callable(database.delete)
    print("[OK] Database has delete() method")

    assert hasattr(database, "reload")
    assert callable(database.reload)
    print("[OK] Database has reload() method")

    assert hasattr(database, "update")
    assert callable(database.update)
    print("[OK] Database has update() method")

    assert hasattr(database, "query")
    assert callable(database.query)
    print("[OK] Database has query() method")

    # Check properties exist
    assert hasattr(database, "id")
    assert database.id == "database_123"
    print("[OK] Database has id property")

    assert hasattr(database, "title")
    assert isinstance(database.title, list)
    print("[OK] Database has title property")

    assert hasattr(database, "properties")
    assert isinstance(database.properties, dict)
    print("[OK] Database has properties property")

    assert hasattr(database, "created_time")
    assert isinstance(database.created_time, datetime)
    print("[OK] Database has created_time datetime property")

    assert hasattr(database, "last_edited_time")
    assert isinstance(database.last_edited_time, datetime)
    print("[OK] Database has last_edited_time datetime property")

    assert hasattr(database, "archived")
    assert isinstance(database.archived, bool)
    print("[OK] Database has archived property")

    # Check validation methods exist
    assert hasattr(database, "_validate_property_value")
    assert callable(database._validate_property_value)
    print("[OK] Database has _validate_property_value() method")

    assert hasattr(database, "_validate_property")
    assert callable(database._validate_property)
    print("[OK] Database has _validate_property() method")


async def run_all_tests():
    """Run all Database entity tests."""
    print("=" * 60)
    print("Testing Database Entity Implementation (#74)")
    print("=" * 60)

    # Synchronous tests
    await test_database_datetime_properties()

    # Async tests
    await test_database_update()
    await test_database_update_validation()
    await test_database_modified_tracking()
    await test_database_has_valid_properties()
    await test_database_has_all_required_features()

    print("=" * 60)
    print("[OK] All Database entity tests passed!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(run_all_tests())
