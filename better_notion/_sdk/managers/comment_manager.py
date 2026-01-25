"""CommentsManager for Notion comment operations."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from better_notion._api.utils.pagination import AsyncPaginatedIterator

if TYPE_CHECKING:
    from better_notion._sdk.client import NotionClient
    from better_notion._sdk.models.comment import Comment


class CommentsManager:
    """Manager for comment operations.

    This is a thin wrapper that delegates to Comment entity methods.

    Example:
        >>> comments = await client.comments.list(block_id="page-123")
        >>> comment = await client.comments.get(comment_id="comment-123")
    """

    def __init__(self, client: "NotionClient") -> None:
        """Initialize CommentsManager.

        Args:
            client: NotionClient instance
        """
        self._client = client

    async def get(self, comment_id: str) -> "Comment":
        """Get a comment by ID.

        Args:
            comment_id: Comment UUID

        Returns:
            Comment object

        Example:
            >>> comment = await client.comments.get("comment-123")
        """
        from better_notion._sdk.models.comment import Comment
        return await Comment.get(comment_id, client=self._client)

    async def create(
        self,
        *,
        parent: str | None = None,
        discussion_id: str | None = None,
        rich_text: list[dict[str, Any]],
        attachments: list[dict[str, Any]] | None = None,
        display_name: str | None = None
    ) -> "Comment":
        """Create a comment.

        Args:
            parent: Page ID or block ID (for new discussion)
            discussion_id: Discussion thread ID (to reply to thread)
            rich_text: Comment content (rich text array)
            attachments: Optional file attachments (max 3)
            display_name: Optional display name type

        Returns:
            Created Comment object

        Raises:
            ValueError: If neither parent nor discussion_id provided

        Example:
            >>> comment = await client.comments.create(
            ...     parent="page-123",
            ...     rich_text=[{
            ...         "type": "text",
            ...         "text": {"content": "Hello world"}
            ...     }]
            ... )
        """
        if not parent and not discussion_id:
            raise ValueError("Either parent or discussion_id must be provided")
        if parent and discussion_id:
            raise ValueError("Only one of parent or discussion_id can be provided")

        # Build request payload
        payload = {"rich_text": rich_text}

        if parent:
            # Determine if it's a page or block ID
            # For now, assume it's a page_id (could be enhanced to detect block_id)
            payload["parent"] = {
                "type": "page_id",
                "page_id": parent
            }

        if discussion_id:
            payload["discussion_id"] = discussion_id

        if attachments:
            payload["attachments"] = attachments

        if display_name:
            payload["display_name"] = {"type": display_name}

        # Create via API
        data = await self._client.api.comments.create(
            parent=payload.get("parent"),
            discussion_id=payload.get("discussion_id"),
            rich_text=payload["rich_text"],
            attachments=payload.get("attachments"),
            display_name=payload.get("display_name")
        )

        # Return Comment object
        from better_notion._sdk.models.comment import Comment
        comment = Comment(self._client, data)

        # Cache it
        self._client.comment_cache[comment.id] = comment

        return comment

    async def list(
        self,
        block_id: str,
        *,
        page_size: int = 100,
        start_cursor: str | None = None
    ) -> dict[str, Any]:
        """List comments for a page or block.

        Args:
            block_id: Page ID or block ID
            page_size: Number of comments per page (max: 100)
            start_cursor: Pagination cursor

        Returns:
            Dict with results, has_more, next_cursor

        Example:
            >>> response = await client.comments.list("page-123")
            >>> for comment_data in response["results"]:
            ...     print(comment_data["rich_text"])
        """
        return await self._client.api.comments.list(
            block_id=block_id,
            page_size=page_size,
            start_cursor=start_cursor
        )

    async def list_all(self, block_id: str) -> list["Comment"]:
        """List all comments with automatic pagination.

        Args:
            block_id: Page ID or block ID

        Returns:
            List of all Comment objects

        Example:
            >>> comments = await client.comments.list_all("page-123")
            >>> print(f"Total: {len(comments)}")
        """
        from better_notion._sdk.models.comment import Comment

        # Define fetch function
        async def fetch_fn(cursor: str | None) -> dict:
            return await self.list(block_id, start_cursor=cursor)

        # Define item parser
        def item_parser(item_data: dict) -> Comment:
            return Comment(self._client, item_data)

        # Use paginated iterator
        iterator = AsyncPaginatedIterator(fetch_fn, item_parser)

        # Collect all comments
        comments = []
        async for comment in iterator:
            comments.append(comment)

        return comments
