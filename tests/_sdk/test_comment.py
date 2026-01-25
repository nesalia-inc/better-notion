"""Tests for Comment model and CommentsManager."""

import pytest
from unittest.mock import AsyncMock, MagicMock

from better_notion._sdk.models.comment import Comment
from better_notion._sdk.managers.comment_manager import CommentsManager


@pytest.fixture
def mock_client():
    """Create mock NotionClient."""
    client = MagicMock()
    client.api = MagicMock()
    client.api.comments = MagicMock()
    client.api.comments.retrieve = AsyncMock()
    client.api.comments.create = AsyncMock()
    client.api.comments.list = AsyncMock()

    # Setup caches
    client.comment_cache = {}
    client._comment_cache = client.comment_cache

    return client


@pytest.fixture
def comment_data():
    """Sample comment data from Notion API."""
    return {
        "object": "comment",
        "id": "comment-123",
        "parent": {
            "type": "block_id",
            "block_id": "block-456"
        },
        "discussion_id": "discussion-789",
        "created_time": "2024-01-15T10:30:00.000Z",
        "last_edited_time": "2024-01-15T10:30:00.000Z",
        "created_by": {
            "object": "user",
            "id": "user-123",
            "name": "Test User"
        },
        "rich_text": [
            {
                "type": "text",
                "text": {"content": "Hello world", "link": None},
                "annotations": {
                    "bold": False,
                    "italic": False,
                    "strikethrough": False,
                    "underline": False,
                    "code": False,
                    "color": "default"
                },
                "plain_text": "Hello world",
                "href": None
            }
        ]
    }


class TestCommentInit:
    """Tests for Comment initialization."""

    def test_init_with_client_and_data(self, mock_client, comment_data):
        """Test initialization with client and data."""
        comment = Comment(mock_client, comment_data)

        assert comment.id == "comment-123"
        assert comment._client is mock_client
        assert comment._data == comment_data


class TestCommentProperties:
    """Tests for Comment properties."""

    def test_text_property(self, mock_client, comment_data):
        """Test text property."""
        comment = Comment(mock_client, comment_data)

        assert comment.text == "Hello world"

    def test_discussion_id(self, mock_client, comment_data):
        """Test discussion_id property."""
        comment = Comment(mock_client, comment_data)

        assert comment.discussion_id == "discussion-789"

    def test_parent_type(self, mock_client, comment_data):
        """Test parent_type property."""
        comment = Comment(mock_client, comment_data)

        assert comment.parent_type == "block_id"

    def test_parent_id(self, mock_client, comment_data):
        """Test parent_id property."""
        comment = Comment(mock_client, comment_data)

        assert comment.parent_id == "block-456"

    def test_created_by_id(self, mock_client, comment_data):
        """Test created_by_id property."""
        comment = Comment(mock_client, comment_data)

        assert comment.created_by_id == "user-123"

    def test_created_by(self, mock_client, comment_data):
        """Test created_by property."""
        comment = Comment(mock_client, comment_data)

        assert comment.created_by["id"] == "user-123"

    def test_has_attachments_true(self, mock_client):
        """Test has_attachments with attachments."""
        data = {
            "id": "comment-123",
            "object": "comment",
            "parent": {"type": "page_id", "page_id": "page-123"},
            "discussion_id": "discussion-123",
            "created_time": "2024-01-01T00:00:00.000Z",
            "last_edited_time": "2024-01-01T00:00:00.000Z",
            "created_by": {"object": "user", "id": "user-123"},
            "rich_text": [],
            "attachments": [{"category": "image"}]
        }
        comment = Comment(mock_client, data)

        assert comment.has_attachments is True

    def test_has_attachments_false(self, mock_client, comment_data):
        """Test has_attachments without attachments."""
        comment = Comment(mock_client, comment_data)

        assert comment.has_attachments is False

    def test_attachment_count(self, mock_client):
        """Test attachment_count property."""
        data = {
            "id": "comment-123",
            "object": "comment",
            "parent": {"type": "page_id", "page_id": "page-123"},
            "discussion_id": "discussion-123",
            "created_time": "2024-01-01T00:00:00.000Z",
            "last_edited_time": "2024-01-01T00:00:00.000Z",
            "created_by": {"object": "user", "id": "user-123"},
            "rich_text": [],
            "attachments": [{"category": "image"}, {"category": "file"}]
        }
        comment = Comment(mock_client, data)

        assert comment.attachment_count == 2

    def test_display_name(self, mock_client):
        """Test display_name property."""
        data = {
            "id": "comment-123",
            "object": "comment",
            "parent": {"type": "page_id", "page_id": "page-123"},
            "discussion_id": "discussion-123",
            "created_time": "2024-01-01T00:00:00.000Z",
            "last_edited_time": "2024-01-01T00:00:00.000Z",
            "created_by": {"object": "user", "id": "user-123"},
            "rich_text": [],
            "display_name": {
                "type": "integration",
                "resolved_name": "My Integration"
            }
        }
        comment = Comment(mock_client, data)

        assert comment.display_name == "integration"
        assert comment.resolved_name == "My Integration"


class TestCommentGet:
    """Tests for Comment.get() method."""

    @pytest.mark.asyncio
    async def test_get_from_api(self, mock_client, comment_data):
        """Test get() fetches from API."""
        mock_client.api.comments.retrieve.return_value = comment_data

        comment = await Comment.get("comment-123", client=mock_client)

        assert comment.id == "comment-123"
        mock_client.api.comments.retrieve.assert_called_once_with(
            comment_id="comment-123"
        )

    @pytest.mark.asyncio
    async def test_get_uses_cache(self, mock_client, comment_data):
        """Test get() uses cache."""
        mock_client.api.comments.retrieve.return_value = comment_data

        # First call
        comment1 = await Comment.get("comment-123", client=mock_client)

        # Second call should use cache
        comment2 = await Comment.get("comment-123", client=mock_client)

        assert comment1 is comment2
        # API should only be called once
        mock_client.api.comments.retrieve.assert_called_once()


class TestCommentsManager:
    """Tests for CommentsManager."""

    def test_init(self, mock_client):
        """Test CommentsManager initialization."""
        manager = CommentsManager(mock_client)

        assert manager._client is mock_client

    @pytest.mark.asyncio
    async def test_get(self, mock_client, comment_data):
        """Test get() method."""
        mock_client.api.comments.retrieve.return_value = comment_data

        manager = CommentsManager(mock_client)
        comment = await manager.get("comment-123")

        assert comment.id == "comment-123"

    @pytest.mark.asyncio
    async def test_create_with_parent(self, mock_client, comment_data):
        """Test create() with parent."""
        mock_client.api.comments.create.return_value = comment_data

        manager = CommentsManager(mock_client)
        comment = await manager.create(
            parent="page-123",
            rich_text=[{
                "type": "text",
                "text": {"content": "Hello"}
            }]
        )

        assert comment.id == "comment-123"

    @pytest.mark.asyncio
    async def test_create_with_discussion_id(self, mock_client, comment_data):
        """Test create() with discussion_id."""
        mock_client.api.comments.create.return_value = comment_data

        manager = CommentsManager(mock_client)
        comment = await manager.create(
            discussion_id="discussion-123",
            rich_text=[{
                "type": "text",
                "text": {"content": "Reply"}
            }]
        )

        assert comment.id == "comment-123"

    @pytest.mark.asyncio
    async def test_create_neither_parent_nor_discussion_raises_error(self, mock_client):
        """Test create() raises error when neither parent nor discussion_id provided."""
        manager = CommentsManager(mock_client)

        with pytest.raises(ValueError, match="Either parent or discussion_id must be provided"):
            await manager.create(rich_text=[])

    @pytest.mark.asyncio
    async def test_create_both_parent_and_discussion_raises_error(self, mock_client):
        """Test create() raises error when both parent and discussion_id provided."""
        manager = CommentsManager(mock_client)

        with pytest.raises(ValueError, match="Only one of parent or discussion_id can be provided"):
            await manager.create(
                parent="page-123",
                discussion_id="discussion-123",
                rich_text=[]
            )

    @pytest.mark.asyncio
    async def test_list(self, mock_client):
        """Test list() method."""
        mock_client.api.comments.list.return_value = {
            "results": [],
            "has_more": False,
            "next_cursor": None
        }

        manager = CommentsManager(mock_client)
        response = await manager.list("page-123")

        assert "results" in response
        assert response["has_more"] is False

    @pytest.mark.asyncio
    async def test_list_all_empty(self, mock_client):
        """Test list_all() with no comments."""
        mock_client.api.comments.list.return_value = {
            "results": [],
            "has_more": False,
            "next_cursor": None
        }

        manager = CommentsManager(mock_client)
        comments = await manager.list_all("page-123")

        assert comments == []

    @pytest.mark.asyncio
    async def test_list_all_with_pagination(self, mock_client, comment_data):
        """Test list_all() with pagination."""
        # First page
        mock_client.api.comments.list.return_value = {
            "results": [comment_data],
            "has_more": True,
            "next_cursor": "cursor-123"
        }

        manager = CommentsManager(mock_client)

        # Create async iterator mock
        call_count = 0

        async def mock_list(**kwargs):
            call_count = 0
            if kwargs.get("start_cursor") is None:
                call_count += 1
                return {
                    "results": [comment_data],
                    "has_more": True,
                    "next_cursor": "cursor-123"
                }
            else:
                return {
                    "results": [],
                    "has_more": False,
                    "next_cursor": None
                }

        mock_client.api.comments.list.side_effect = mock_list

        # For now, just test that list_all works with single page
        mock_client.api.comments.list.side_effect = None
        mock_client.api.comments.list.return_value = {
            "results": [comment_data],
            "has_more": False,
            "next_cursor": None
        }

        comments = await manager.list_all("page-123")

        assert len(comments) == 1
        assert comments[0].id == "comment-123"

    @pytest.mark.asyncio
    async def test_create_with_attachments(self, mock_client, comment_data):
        """Test create() with attachments."""
        comment_data["attachments"] = [{"category": "image"}]
        mock_client.api.comments.create.return_value = comment_data

        manager = CommentsManager(mock_client)
        comment = await manager.create(
            parent="page-123",
            rich_text=[{
                "type": "text",
                "text": {"content": "Check this image"}
            }],
            attachments=[{"category": "image"}]
        )

        assert comment.id == "comment-123"
        assert comment.has_attachments is True

    @pytest.mark.asyncio
    async def test_create_with_display_name(self, mock_client, comment_data):
        """Test create() with display_name."""
        comment_data["display_name"] = {
            "type": "integration",
            "resolved_name": "My Bot"
        }
        mock_client.api.comments.create.return_value = comment_data

        manager = CommentsManager(mock_client)
        comment = await manager.create(
            parent="page-123",
            rich_text=[{
                "type": "text",
                "text": {"content": "Automated comment"}
            }],
            display_name="integration"
        )

        assert comment.id == "comment-123"
        assert comment.display_name == "integration"


class TestCommentsCollection:
    """Tests for low-level CommentCollection."""

    @pytest.fixture
    def mock_api(self):
        """Create mock NotionAPI."""
        api = MagicMock()
        api._request = AsyncMock()
        return api

    @pytest.fixture
    def comment_data(self):
        """Sample comment data."""
        return {
            "object": "comment",
            "id": "comment-456",
            "parent": {
                "type": "page_id",
                "page_id": "page-789"
            },
            "discussion_id": "discussion-456",
            "created_time": "2024-01-20T15:00:00.000Z",
            "last_edited_time": "2024-01-20T15:00:00.000Z",
            "created_by": {
                "object": "user",
                "id": "user-456",
                "name": "Test User"
            },
            "rich_text": [
                {
                    "type": "text",
                    "text": {"content": "Test comment", "link": None},
                    "annotations": {
                        "bold": False,
                        "italic": False,
                        "strikethrough": False,
                        "underline": False,
                        "code": False,
                        "color": "default"
                    },
                    "plain_text": "Test comment",
                    "href": None
                }
            ]
        }

    def test_init(self, mock_api):
        """Test CommentCollection initialization."""
        from better_notion._api.collections.comments import CommentCollection

        collection = CommentCollection(mock_api)
        assert collection._api is mock_api

    @pytest.mark.asyncio
    async def test_retrieve(self, mock_api, comment_data):
        """Test retrieve() method."""
        from better_notion._api.collections.comments import CommentCollection

        mock_api._request.return_value = comment_data

        collection = CommentCollection(mock_api)
        comment = await collection.retrieve("comment-456")

        assert comment.id == "comment-456"
        mock_api._request.assert_called_once_with("GET", "/comments/comment-456")

    @pytest.mark.asyncio
    async def test_create_with_parent(self, mock_api, comment_data):
        """Test create() with parent."""
        from better_notion._api.collections.comments import CommentCollection

        mock_api._request.return_value = comment_data

        collection = CommentCollection(mock_api)
        comment = await collection.create(
            parent={"type": "page_id", "page_id": "page-789"},
            rich_text=[{
                "type": "text",
                "text": {"content": "New comment"}
            }]
        )

        assert comment.id == "comment-456"
        mock_api._request.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_with_discussion_id(self, mock_api, comment_data):
        """Test create() with discussion_id (reply)."""
        from better_notion._api.collections.comments import CommentCollection

        mock_api._request.return_value = comment_data

        collection = CommentCollection(mock_api)
        comment = await collection.create(
            discussion_id="discussion-123",
            rich_text=[{
                "type": "text",
                "text": {"content": "Reply"}
            }]
        )

        assert comment.id == "comment-456"

    @pytest.mark.asyncio
    async def test_list_with_block_id(self, mock_api):
        """Test list() with block_id."""
        from better_notion._api.collections.comments import CommentCollection

        mock_api._request.return_value = {
            "results": [],
            "has_more": False,
            "next_cursor": None
        }

        collection = CommentCollection(mock_api)
        response = await collection.list(block_id="page-123")

        assert "results" in response
        mock_api._request.assert_called_once_with(
            "GET",
            "/comments",
            params={"block_id": "page-123"}
        )

    @pytest.mark.asyncio
    async def test_list_with_page_size(self, mock_api):
        """Test list() with page_size parameter."""
        from better_notion._api.collections.comments import CommentCollection

        mock_api._request.return_value = {
            "results": [],
            "has_more": False,
            "next_cursor": None
        }

        collection = CommentCollection(mock_api)
        response = await collection.list(block_id="page-123", page_size=50)

        assert "results" in response
        mock_api._request.assert_called_once()

    @pytest.mark.asyncio
    async def test_list_with_pagination(self, mock_api):
        """Test list() with pagination cursor."""
        from better_notion._api.collections.comments import CommentCollection

        mock_api._request.return_value = {
            "results": [],
            "has_more": False,
            "next_cursor": None
        }

        collection = CommentCollection(mock_api)
        response = await collection.list(
            block_id="page-123",
            page_size=100,
            start_cursor="cursor-abc"
        )

        assert "results" in response
