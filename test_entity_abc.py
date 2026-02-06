"""Test Entity ABC implementation."""

import asyncio
from abc import ABC
from datetime import datetime
from unittest.mock import AsyncMock, Mock

from better_notion._api import NotionAPI
from better_notion._api.entities import (
    Block, Comment, Database, Entity, Page, ReadOnlyEntity, User
)


async def test_base_classes_exist():
    """Test that base ABC classes exist."""
    print("[TEST] Base ABC classes exist")

    # Check ReadOnlyEntity exists and is ABC
    assert ReadOnlyEntity is not None
    assert issubclass(ReadOnlyEntity, ABC)
    print("[OK] ReadOnlyEntity is an ABC")

    # Check Entity exists and is ABC
    assert Entity is not None
    assert issubclass(Entity, ABC)
    print("[OK] Entity is an ABC")

    # Check Entity extends ReadOnlyEntity
    assert issubclass(Entity, ReadOnlyEntity)
    print("[OK] Entity extends ReadOnlyEntity")


async def test_entity_classes_inherit_correctly():
    """Test that entity classes inherit from correct base."""
    print("[TEST] Entity classes inherit correctly")

    # Check writable entities extend Entity
    assert issubclass(Page, Entity)
    print("[OK] Page extends Entity")

    assert issubclass(Database, Entity)
    print("[OK] Database extends Entity")

    assert issubclass(Block, Entity)
    print("[OK] Block extends Entity")

    assert issubclass(Comment, Entity)
    print("[OK] Comment extends Entity")

    # Check read-only entities extend ReadOnlyEntity
    assert issubclass(User, ReadOnlyEntity)
    print("[OK] User extends ReadOnlyEntity")

    # User should NOT extend Entity (no save/delete)
    assert not issubclass(User, Entity)
    print("[OK] User does not extend Entity (read-only)")


async def test_entity_has_required_interface():
    """Test that Entity requires all abstract methods."""
    print("[TEST] Entity requires all abstract methods")

    api = Mock(spec=NotionAPI)
    page_data = {
        "id": "page_123",
        "object": "page",
        "created_time": "2025-01-15T10:30:00.000Z",
        "last_edited_time": "2025-01-15T11:00:00.000Z",
        "properties": {},
        "archived": False
    }

    page = Page(api, page_data)

    # Check Entity interface methods exist
    assert hasattr(page, "id")
    assert callable(page.id) or isinstance(page.id, str)
    print("[OK] Entity has id property")

    assert hasattr(page, "save")
    assert callable(page.save)
    print("[OK] Entity has save() method")

    assert hasattr(page, "reload")
    assert callable(page.reload)
    print("[OK] Entity has reload() method")

    assert hasattr(page, "delete")
    assert callable(page.delete)
    print("[OK] Entity has delete() method")

    assert hasattr(page, "__repr__")
    assert callable(page.__repr__)
    print("[OK] Entity has __repr__ method")


async def test_read_only_entity_has_required_interface():
    """Test that ReadOnlyEntity requires basic methods."""
    print("[TEST] ReadOnlyEntity requires basic methods")

    api = Mock(spec=NotionAPI)
    user_data = {
        "id": "user_123",
        "object": "user",
        "name": "Test User",
        "type": "person"
    }

    user = User(api, user_data)

    # Check ReadOnlyEntity interface methods exist
    assert hasattr(user, "id")
    assert user.id == "user_123"
    print("[OK] ReadOnlyEntity has id property")

    assert hasattr(user, "reload")
    assert callable(user.reload)
    print("[OK] ReadOnlyEntity has reload() method")

    assert hasattr(user, "__repr__")
    assert callable(user.__repr__)
    print("[OK] ReadOnlyEntity has __repr__ method")

    # User should NOT have save/delete
    assert not hasattr(user, "save") or not callable(getattr(user, "save", None))
    print("[OK] ReadOnlyEntity does not have save() method")

    assert not hasattr(user, "delete") or not callable(getattr(user, "delete", None))
    print("[OK] ReadOnlyEntity does not have delete() method")


async def test_entity_repr_inherited():
    """Test that __repr__ is inherited from base class."""
    print("[TEST] Entity __repr__ is inherited")

    api = Mock(spec=NotionAPI)

    page_data = {
        "id": "page_123",
        "object": "page",
        "created_time": "2025-01-15T10:30:00.000Z",
        "last_edited_time": "2025-01-15T11:00:00.000Z",
        "properties": {},
        "archived": False
    }

    page = Page(api, page_data)
    repr_str = repr(page)

    # Check __repr__ format from base class
    assert "Page" in repr_str
    assert "page_123" in repr_str
    print(f"[OK] Page __repr__: {repr_str}")

    # Check Database __repr__
    database_data = {
        "id": "db_123",
        "object": "database",
        "created_time": "2025-01-15T10:30:00.000Z",
        "last_edited_time": "2025-01-15T11:00:00.000Z",
        "title": [],
        "properties": {}
    }

    database = Database(api, database_data)
    repr_str = repr(database)

    assert "Database" in repr_str
    assert "db_123" in repr_str
    print(f"[OK] Database __repr__: {repr_str}")


async def test_entity_init_inherited():
    """Test that __init__ is inherited from base class."""
    print("[TEST] Entity __init__ is inherited")

    api = Mock(spec=NotionAPI)

    page_data = {
        "id": "page_123",
        "object": "page",
        "created_time": "2025-01-15T10:30:00.000Z",
        "last_edited_time": "2025-01-15T11:00:00.000Z",
        "properties": {},
        "archived": False
    }

    page = Page(api, page_data)

    # Check that _api and _data are set by base __init__
    assert hasattr(page, "_api")
    assert page._api is api
    print("[OK] Page._api is set by base __init__")

    assert hasattr(page, "_data")
    assert page._data is page_data
    print("[OK] Page._data is set by base __init__")


async def run_all_tests():
    """Run all Entity ABC tests."""
    print("=" * 60)
    print("Testing Entity ABC Implementation (#75)")
    print("=" * 60)

    await test_base_classes_exist()
    await test_entity_classes_inherit_correctly()
    await test_entity_has_required_interface()
    await test_read_only_entity_has_required_interface()
    await test_entity_repr_inherited()
    await test_entity_init_inherited()

    print("=" * 60)
    print("[OK] All Entity ABC tests passed!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(run_all_tests())
