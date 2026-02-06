"""Comment entity for low-level API."""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from better_notion._api import NotionAPI

from better_notion._api.entities.base import Entity


class Comment(Entity):
    """Comment entity from Notion API.

    This is a low-level entity that wraps the raw API response.
    For high-level SDK features, use better_notion._sdk.models.Comment.

    Attributes:
        id: Comment UUID
        object: Object type ("comment")
        parent: Parent object (page or block)
        discussion_id: Discussion thread ID
        created_time: Creation timestamp
        last_edited_time: Last edit timestamp
        created_by: User who created the comment
        rich_text: Rich text content
        attachments: File attachments (optional)
        display_name: Display name configuration (optional)
    """

    def __init__(self, api: "NotionAPI", data: dict[str, Any]) -> None:
        """Initialize a Comment entity.

        Args:
            api: The NotionAPI client instance.
            data: Raw comment data from Notion API.
        """
        super().__init__(api, data)

    @property
    def id(self) -> str:
        """Get comment ID."""
        return self._data.get("id", "")

    @property
    def object(self) -> str:
        """Get object type."""
        return self._data.get("object", "comment")

    @property
    def parent(self) -> dict[str, Any]:
        """Get parent object."""
        return self._data.get("parent", {})

    @property
    def discussion_id(self) -> str:
        """Get discussion thread ID."""
        return self._data.get("discussion_id", "")

    @property
    def created_time(self) -> datetime:
        """Get creation timestamp as datetime.

        Returns:
            Creation timestamp as datetime object.

        Raises:
            ValueError: If created_time is not available in the data.
        """
        from better_notion.utils.helpers import parse_datetime
        created_time_str = self._data.get("created_time")
        if not created_time_str:
            raise ValueError("Comment data missing 'created_time' field")
        return parse_datetime(created_time_str)

    @property
    def last_edited_time(self) -> datetime:
        """Get last edit timestamp as datetime.

        Returns:
            Last edit timestamp as datetime object.

        Raises:
            ValueError: If last_edited_time is not available in the data.
        """
        from better_notion.utils.helpers import parse_datetime
        edited_time_str = self._data.get("last_edited_time")
        if not edited_time_str:
            raise ValueError("Comment data missing 'last_edited_time' field")
        return parse_datetime(edited_time_str)

    @property
    def created_by(self) -> dict[str, Any]:
        """Get creator user object."""
        return self._data.get("created_by", {})

    @property
    def rich_text(self) -> list[dict[str, Any]]:
        """Get rich text content."""
        return self._data.get("rich_text", [])

    @property
    def attachments(self) -> list[dict[str, Any]]:
        """Get file attachments."""
        return self._data.get("attachments", [])

    @property
    def display_name(self) -> dict[str, Any] | None:
        """Get display name configuration."""
        return self._data.get("display_name")

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary.

        Returns:
            The raw comment data dictionary.
        """
        return self._data

    # Instance methods
    async def save(self) -> None:
        """Save changes to Notion.

        Note:
            Notion API does not support comment updates. This method
            raises NotImplementedError for interface consistency with
            other entities (Page, Database, Block).

        Raises:
            NotImplementedError: Comment updates are not supported by Notion API.
        """
        raise NotImplementedError(
            "Comment updates are not supported by the Notion API. "
            "Comments cannot be modified after creation."
        )

    async def delete(self) -> None:
        """Delete this comment.

        Permanently deletes the comment in Notion.

        Raises:
            NotFoundError: If the comment no longer exists.
        """
        await self._api._request("DELETE", f"/comments/{self.id}")

    async def reload(self) -> None:
        """Reload comment data from Notion.

        Fetches the latest comment data and updates the entity.

        Raises:
            NotFoundError: If the comment no longer exists.
        """
        data = await self._api._request("GET", f"/comments/{self.id}")
        self._data = data
