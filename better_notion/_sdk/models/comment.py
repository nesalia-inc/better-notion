"""Comment model for Notion comments."""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Any

from better_notion._sdk.base.entity import BaseEntity

if TYPE_CHECKING:
    from better_notion._sdk.client import NotionClient


class Comment(BaseEntity):
    """Notion Comment with rich text and attachments.

    This model represents comments on pages or blocks.

    Example:
        >>> comment = await client.comments.get(comment_id)
        >>> print(comment.text)
        >>> print(f"Created by: {comment.created_by_id}")
    """

    def __init__(self, client: "NotionClient", data: dict[str, Any]) -> None:
        """Initialize a Comment.

        Args:
            client: NotionClient instance
            data: Raw comment data from Notion API
        """
        # Initialize BaseEntity
        super().__init__(client, data)

    # ===== CLASS METHODS (AUTONOMOUS ENTITY) =====

    @classmethod
    async def get(
        cls,
        comment_id: str,
        *,
        client: "NotionClient"
    ) -> "Comment":
        """Get a comment by ID.

        Args:
            comment_id: Comment UUID
            client: NotionClient instance

        Returns:
            Comment object

        Behavior:
            - Checks cache first (instant)
            - If not cached, fetch from API

        Example:
            >>> comment = await Comment.get(
            ...     comment_id="comment-123",
            ...     client=client
            ... )
            >>> print(comment.text)
        """
        # Check global cache first
        if comment_id in client.comment_cache:
            return client.comment_cache[comment_id]

        # Fetch from API
        data = await client.api.comments.retrieve(comment_id=comment_id)
        comment = cls(client, data)

        # Cache it
        client.comment_cache[comment_id] = comment

        return comment

    # ===== METADATA PROPERTIES =====

    @property
    def text(self) -> str:
        """Get comment plain text.

        Returns:
            Plain text content of comment

        Example:
            >>> comment.text
            'This looks great!'
        """
        rich_text_array = self._data.get("rich_text", [])
        parts = []
        for text_obj in rich_text_array:
            if text_obj.get("type") == "text":
                text_content = text_obj.get("text", {})
                parts.append(text_content.get("content", ""))
            elif text_obj.get("type") == "mention":
                # Handle mentions
                mention = text_obj.get("mention", {})
                if mention.get("type") == "user":
                    parts.append(f"@{mention.get('user', {}).get('id', 'user')}")
                elif mention.get("type") == "page":
                    parts.append(f"@{mention.get('page', {}).get('id', 'page')}")
                elif mention.get("type") == "database":
                    parts.append(f"@{mention.get('database', {}).get('id', 'database')}")
        return "".join(parts)

    @property
    def discussion_id(self) -> str:
        """Get discussion thread ID.

        Returns:
            Discussion UUID

        Example:
            >>> comment.discussion_id
            'discussion-123'
        """
        return self._data.get("discussion_id", "")

    @property
    def parent_type(self) -> str:
        """Get parent type.

        Returns:
            'page_id' or 'block_id'

        Example:
            >>> comment.parent_type
            'block_id'
        """
        parent = self._data.get("parent", {})
        return parent.get("type", "")

    @property
    def parent_id(self) -> str:
        """Get parent ID (page or block).

        Returns:
            Parent UUID

        Example:
            >>> comment.parent_id
            'page-123'
        """
        parent = self._data.get("parent", {})
        if parent.get("type") == "page_id":
            return parent.get("page_id", "")
        elif parent.get("type") == "block_id":
            return parent.get("block_id", "")
        return ""

    @property
    def created_by_id(self) -> str:
        """Get creator user ID.

        Returns:
            User ID

        Example:
            >>> comment.created_by_id
            'user-123'
        """
        created_by = self._data.get("created_by", {})
        return created_by.get("id", "")

    @property
    def created_by(self) -> dict[str, Any]:
        """Get full creator object.

        Returns:
            User object dict

        Example:
            >>> comment.created_by
            {'object': 'user', 'id': 'user-123', ...}
        """
        return self._data.get("created_by", {})

    @property
    def has_attachments(self) -> bool:
        """Check if comment has attachments.

        Returns:
            True if comment has attachments

        Example:
            >>> comment.has_attachments
            False
        """
        attachments = self._data.get("attachments", [])
        return len(attachments) > 0

    @property
    def attachment_count(self) -> int:
        """Get number of attachments.

        Returns:
            Number of attachments (max 3)

        Example:
            >>> comment.attachment_count
            2
        """
        return len(self._data.get("attachments", []))

    @property
    def display_name(self) -> str | None:
        """Get display name type.

        Returns:
            'integration', 'user', 'custom', or None

        Example:
            >>> comment.display_name
            'integration'
        """
        display_name = self._data.get("display_name", {})
        return display_name.get("type")

    @property
    def resolved_name(self) -> str | None:
        """Get resolved display name.

        Returns:
            Resolved name string or None

        Example:
            >>> comment.resolved_name
            'My Integration'
        """
        display_name = self._data.get("display_name", {})
        return display_name.get("resolved_name")

    # ===== NAVIGATION =====

    async def children(self) -> AsyncIterator["Block"]:
        """Comments don't have children.

        Yields:
            Nothing (comments have no children)

        Example:
            >>> async for _ in comment.children():
            ...     pass  # This won't execute
        """
        # Comments have no children
        return
        yield  # Never reached, but makes this an async generator

    async def parent(self) -> "Page | Block | None":
        """Get parent object (page or block).

        Returns:
            Parent Page or Block object, or None

        Example:
            >>> parent = await comment.parent()
            >>> print(parent.id)
        """
        # Check entity cache
        cached_parent = self._cache_get("parent")
        if cached_parent:
            return cached_parent

        # Fetch based on type
        if self.parent_type == "page_id":
            from better_notion._sdk.models.page import Page
            parent = await Page.get(self.parent_id, client=self._client)
        elif self.parent_type == "block_id":
            from better_notion._sdk.models.block import Block
            parent = await Block.get(self.parent_id, client=self._client)
        else:
            parent = None

        # Cache result
        if parent:
            self._cache_set("parent", parent)

        return parent

    async def creator(self) -> "User":
        """Get comment creator user.

        Returns:
            User object

        Example:
            >>> creator = await comment.creator()
            >>> print(creator.name)
        """
        from better_notion._sdk.models.user import User

        # Check if we have the ID
        user_id = self.created_by_id
        if not user_id:
            raise ValueError("Comment has no creator ID")

        return await User.get(user_id, client=self._client)

    # ===== HELPER METHODS =====

    def __repr__(self) -> str:
        """String representation."""
        text_preview = self.text[:30] if self.text else ""
        return f"Comment(id={self.id!r}, text={text_preview!r})"
