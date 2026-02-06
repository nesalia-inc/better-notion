"""Test Comment entity implementation."""

import asyncio
from datetime import datetime, timezone
from unittest.mock import AsyncMock, Mock

from better_notion._api import NotionAPI
from better_notion._api.entities import Comment


def test_comment_datetime_properties():
    """Test Comment datetime properties return datetime objects."""
    print("[TEST] Comment datetime properties")

    api = Mock(spec=NotionAPI)

    comment_data = {
        "id": "comment_123",
        "object": "comment",
        "parent": {"type": "page_id", "page_id": "page_123"},
        "discussion_id": "disc_123",
        "created_time": "2025-01-15T10:30:00.000Z",
        "last_edited_time": "2025-01-15T11:00:00.000Z",
        "created_by": {"id": "user_123", "object": "user"},
        "rich_text": [{"type": "text", "text": {"content": "Test"}}],
        "attachments": []
    }

    comment = Comment(api, comment_data)

    # Test created_time returns datetime
    created = comment.created_time
    assert isinstance(created, datetime), f"created_time should be datetime, got {type(created)}"
    assert created.year == 2025
    assert created.month == 1
    assert created.day == 15
    print("[OK] created_time returns datetime")

    # Test last_edited_time returns datetime
    edited = comment.last_edited_time
    assert isinstance(edited, datetime), f"last_edited_time should be datetime, got {type(edited)}"
    assert edited.year == 2025
    assert edited.month == 1
    assert edited.day == 15
    print("[OK] last_edited_time returns datetime")

    # Test we can use datetime methods
    assert created.strftime("%Y-%m-%d") == "2025-01-15"
    print("[OK] Can use datetime methods on created_time")


async def test_comment_save_raises_not_implemented():
    """Test Comment.save() raises NotImplementedError."""
    print("[TEST] Comment.save() raises NotImplementedError")

    api = Mock(spec=NotionAPI)
    comment_data = {
        "id": "comment_123",
        "object": "comment",
        "created_time": "2025-01-15T10:30:00.000Z",
        "rich_text": []
    }

    comment = Comment(api, comment_data)

    try:
        await comment.save()
        assert False, "Should raise NotImplementedError"
    except NotImplementedError as e:
        assert "not supported" in str(e).lower()
        print(f"[OK] save() raises NotImplementedError: {e}")


async def test_comment_delete():
    """Test Comment.delete() method."""
    print("[TEST] Comment.delete() method")

    api = Mock(spec=NotionAPI)
    api._request = AsyncMock(return_value={"archived": True})

    comment_data = {
        "id": "comment_123",
        "object": "comment",
        "created_time": "2025-01-15T10:30:00.000Z",
        "rich_text": []
    }

    comment = Comment(api, comment_data)

    # Test delete() calls API correctly
    await comment.delete()
    api._request.assert_called_once_with("DELETE", "/comments/comment_123")
    print("[OK] delete() calls API correctly")


async def test_comment_reload():
    """Test Comment.reload() method."""
    print("[TEST] Comment.reload() method")

    api = Mock(spec=NotionAPI)

    new_comment_data = {
        "id": "comment_123",
        "object": "comment",
        "created_time": "2025-01-15T10:30:00.000Z",
        "last_edited_time": "2025-01-15T12:00:00.000Z",  # Updated
        "rich_text": [{"type": "text", "text": {"content": "Updated"}}]
    }

    api._request = AsyncMock(return_value=new_comment_data)

    comment_data = {
        "id": "comment_123",
        "object": "comment",
        "created_time": "2025-01-15T10:30:00.000Z",
        "last_edited_time": "2025-01-15T11:00:00.000Z",
        "rich_text": [{"type": "text", "text": {"content": "Original"}}]
    }

    comment = Comment(api, comment_data)

    # Reload should update data
    await comment.reload()
    api._request.assert_called_once_with("GET", "/comments/comment_123")

    # Check data was updated
    assert comment._data == new_comment_data
    assert comment._data["last_edited_time"] == "2025-01-15T12:00:00.000Z"
    print("[OK] reload() updates comment data")


async def test_comment_has_all_required_methods():
    """Test Comment has all required entity methods."""
    print("[TEST] Comment has all required methods")

    api = Mock(spec=NotionAPI)
    comment_data = {
        "id": "comment_123",
        "object": "comment",
        "created_time": "2025-01-15T10:30:00.000Z",
        "last_edited_time": "2025-01-15T11:00:00.000Z",
        "rich_text": []
    }

    comment = Comment(api, comment_data)

    # Check all methods exist
    assert hasattr(comment, "save")
    assert callable(comment.save)
    print("[OK] Comment has save() method")

    assert hasattr(comment, "delete")
    assert callable(comment.delete)
    print("[OK] Comment has delete() method")

    assert hasattr(comment, "reload")
    assert callable(comment.reload)
    print("[OK] Comment has reload() method")

    assert hasattr(comment, "id")
    assert comment.id == "comment_123"
    print("[OK] Comment has id property")

    assert hasattr(comment, "created_time")
    assert isinstance(comment.created_time, datetime)
    print("[OK] Comment has created_time datetime property")

    assert hasattr(comment, "last_edited_time")
    assert isinstance(comment.last_edited_time, datetime)
    print("[OK] Comment has last_edited_time datetime property")


async def run_all_tests():
    """Run all Comment entity tests."""
    print("=" * 60)
    print("Testing Comment Entity Implementation (#72)")
    print("=" * 60)

    # Synchronous tests
    test_comment_datetime_properties()

    # Async tests
    await test_comment_save_raises_not_implemented()
    await test_comment_delete()
    await test_comment_reload()
    await test_comment_has_all_required_methods()

    print("=" * 60)
    print("[OK] All Comment entity tests passed!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(run_all_tests())
