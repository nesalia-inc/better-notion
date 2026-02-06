"""Comment collection."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from better_notion._api import NotionAPI
    from better_notion._api.entities import Comment



class CommentCollection:
    """Collection for managing comments.

    Provides factory methods for creating and retrieving comments.
    """

    def __init__(self, api: NotionAPI) -> None:
        """Initialize the Comment collection.

        Args:
            api: The NotionAPI client instance.
        """
        self._api = api

    async def get(self, comment_id: str) -> Comment:
        """Retrieve a comment by ID.

        Args:
            comment_id: The comment ID.

        Returns:
            Comment entity object.

        Raises:
            NotFoundError: If the comment does not exist.
        """
        from better_notion._api.entities import Comment
        data = await self._api._request("GET", f"/comments/{comment_id}")
        return Comment(self._api, data)

    async def create(
        self,
        *,
        parent: dict[str, str] | None = None,
        discussion_id: str | None = None,
        rich_text: list[dict[str, Any]],
        attachments: list[dict[str, Any]] | None = None,
        display_name: dict[str, str] | None = None
    ) -> Comment:
        """Create a new comment.

        Args:
            parent: Parent object (e.g., {"type": "page_id", "page_id": "..."})
            discussion_id: Discussion thread ID (for replies)
            rich_text: Rich text content of the comment
            attachments: Optional file attachments (max 3)
            display_name: Optional display name configuration

        Returns:
            Created Comment entity.

        Raises:
            ValidationError: If the request is invalid.
            BadRequestError: If the request is invalid.
        """
        from better_notion._api.entities import Comment
        payload: dict[str, Any] = {"rich_text": rich_text}

        if parent:
            payload["parent"] = parent

        if discussion_id:
            payload["discussion_id"] = discussion_id

        if attachments:
            payload["attachments"] = attachments

        if display_name:
            payload["display_name"] = display_name

        data = await self._api._request("POST", "/comments", json=payload)
        return Comment(self._api, data)

    async def list(
        self,
        *,
        block_id: str | None = None,
        page_size: int | None = None,
        start_cursor: str | None = None
    ) -> dict[str, Any]:
        """List comments for a block or page.

        Args:
            block_id: Block ID or page ID to get comments for.
            page_size: Number of comments per page (max: 100).
            start_cursor: Pagination cursor.

        Returns:
            Dict with results (list[Comment]), has_more, next_cursor.

        Raises:
            ValidationError: If the request is invalid.
        """
        from better_notion._api.entities import Comment
        params: dict[str, Any] = {}

        if block_id:
            params["block_id"] = block_id

        if page_size is not None:
            params["page_size"] = page_size

        if start_cursor:
            params["start_cursor"] = start_cursor

        data = await self._api._request("GET", "/comments", params=params)
        # Convert results to Comment entities
        results = data.get("results", [])
        data["results"] = [Comment(self._api, comment_data) for comment_data in results]
        return data

    async def delete(self, comment_id: str) -> None:
        """Delete a comment by ID.

        Args:
            comment_id: The comment ID.

        Raises:
            NotFoundError: If the comment does not exist.
        """
        await self._api._request("DELETE", f"/comments/{comment_id}")
