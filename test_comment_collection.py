"""Test CommentCollection implementation."""

import asyncio
from unittest.mock import AsyncMock, Mock

from better_notion._api import NotionAPI
from better_notion._api.collections import CommentCollection
from better_notion._api.entities import Comment


async def test_comment_collection_has_get_method():
    """Test CommentCollection has get() method (not retrieve())."""
    print("[TEST] CommentCollection has get() method")

    api = Mock(spec=NotionAPI)
    collection = CommentCollection(api)

    assert hasattr(collection, "get")
    assert callable(collection.get)
    print("[OK] CommentCollection has get() method")

    # Should NOT have retrieve() method
    assert not hasattr(collection, "retrieve") or "retrieve" not in dir(collection)
    print("[OK] CommentCollection does not have retrieve() method")


async def test_comment_collection_get_returns_entity():
    """Test CommentCollection.get() returns Comment entity."""
    print("[TEST] CommentCollection.get() returns Comment entity")

    api = Mock(spec=NotionAPI)

    comment_data = {
        "id": "comment_123",
        "object": "comment",
        "parent": {"type": "page_id", "page_id": "page_123"},
        "discussion_id": "disc_123",
        "created_time": "2025-01-15T10:30:00.000Z",
        "last_edited_time": "2025-01-15T11:00:00.000Z",
        "created_by": {"id": "user_123", "object": "user"},
        "rich_text": [{"type": "text", "text": {"content": "Test comment"}}],
        "attachments": []
    }

    api._request = AsyncMock(return_value=comment_data)

    collection = CommentCollection(api)
    result = await collection.get("comment_123")

    # Check result is Comment entity
    assert isinstance(result, Comment), f"Expected Comment, got {type(result)}"
    assert result.id == "comment_123"
    assert isinstance(result.created_time, datetime)
    print("[OK] get() returns Comment entity with correct properties")


async def test_comment_collection_create_returns_entity():
    """Test CommentCollection.create() returns Comment entity."""
    print("[TEST] CommentCollection.create() returns Comment entity")

    api = Mock(spec=NotionAPI)

    new_comment_data = {
        "id": "new_comment_123",
        "object": "comment",
        "parent": {"type": "page_id", "page_id": "page_123"},
        "discussion_id": "disc_123",
        "created_time": "2025-01-15T10:30:00.000Z",
        "last_edited_time": "2025-01-15T11:00:00.000Z",
        "created_by": {"id": "user_123", "object": "user"},
        "rich_text": [{"type": "text", "text": {"content": "New comment"}}],
        "attachments": []
    }

    api._request = AsyncMock(return_value=new_comment_data)

    collection = CommentCollection(api)
    result = await collection.create(
        parent={"type": "page_id", "page_id": "page_123"},
        rich_text=[{"type": "text", "text": {"content": "New comment"}}]
    )

    # Check result is Comment entity
    assert isinstance(result, Comment), f"Expected Comment, got {type(result)}"
    assert result.id == "new_comment_123"
    print("[OK] create() returns Comment entity")


async def test_comment_collection_list_returns_entities():
    """Test CommentCollection.list() returns dict with list[Comment]."""
    print("[TEST] CommentCollection.list() returns dict with list[Comment]")

    api = Mock(spec=NotionAPI)

    list_data = {
        "object": "list",
        "results": [
            {
                "id": "comment_1",
                "object": "comment",
                "created_time": "2025-01-15T10:30:00.000Z",
                "last_edited_time": "2025-01-15T11:00:00.000Z",
                "rich_text": [{"type": "text", "text": {"content": "Comment 1"}}],
                "attachments": []
            },
            {
                "id": "comment_2",
                "object": "comment",
                "created_time": "2025-01-15T10:31:00.000Z",
                "last_edited_time": "2025-01-15T11:01:00.000Z",
                "rich_text": [{"type": "text", "text": {"content": "Comment 2"}}],
                "attachments": []
            }
        ],
        "has_more": False,
        "next_cursor": None
    }

    api._request = AsyncMock(return_value=list_data)

    collection = CommentCollection(api)
    result = await collection.list(block_id="block_123")

    # Check result structure
    assert isinstance(result, dict), f"Expected dict, got {type(result)}"
    assert "results" in result
    assert isinstance(result["results"], list), f"Expected list in results, got {type(result['results'])}"
    assert len(result["results"]) == 2

    # Check all items are Comment entities
    assert all(isinstance(c, Comment) for c in result["results"]), "All results should be Comment entities"
    assert result["results"][0].id == "comment_1"
    assert result["results"][1].id == "comment_2"
    print("[OK] list() returns dict with list[Comment]")


async def test_comment_collection_delete():
    """Test CommentCollection.delete() method."""
    print("[TEST] CommentCollection.delete() method")

    api = Mock(spec=NotionAPI)
    api._request = AsyncMock(return_value=None)

    collection = CommentCollection(api)
    await collection.delete("comment_123")

    api._request.assert_called_once_with("DELETE", "/comments/comment_123")
    print("[OK] delete() calls API correctly")


async def test_comment_collection_consistency_with_entity():
    """Test CommentCollection methods are consistent with Entity pattern."""
    print("[TEST] CommentCollection consistency with Entity pattern")

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

    api._request = AsyncMock(return_value=comment_data)

    collection = CommentCollection(api)
    comment = await collection.get("comment_123")

    # Test Entity methods exist and work
    assert hasattr(comment, "save")
    assert callable(comment.save)
    print("[OK] Comment from collection has save() method")

    assert hasattr(comment, "delete")
    assert callable(comment.delete)
    print("[OK] Comment from collection has delete() method")

    assert hasattr(comment, "reload")
    assert callable(comment.reload)
    print("[OK] Comment from collection has reload() method")

    # Test Entity properties
    assert hasattr(comment, "id")
    assert comment.id == "comment_123"
    print("[OK] Comment from collection has id property")

    assert hasattr(comment, "rich_text")
    assert isinstance(comment.rich_text, list)
    print("[OK] Comment from collection has rich_text property")

    assert hasattr(comment, "created_time")
    assert isinstance(comment.created_time, datetime)
    print("[OK] Comment from collection has created_time datetime property")


async def run_all_tests():
    """Run all CommentCollection tests."""
    print("=" * 60)
    print("Testing CommentCollection Implementation (#71)")
    print("=" * 60)

    await test_comment_collection_has_get_method()
    await test_comment_collection_get_returns_entity()
    await test_comment_collection_create_returns_entity()
    await test_comment_collection_list_returns_entities()
    await test_comment_collection_delete()
    await test_comment_collection_consistency_with_entity()

    print("=" * 60)
    print("[OK] All CommentCollection tests passed!")
    print("=" * 60)


if __name__ == "__main__":
    from datetime import datetime
    asyncio.run(run_all_tests())
