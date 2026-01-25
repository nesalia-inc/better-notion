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
