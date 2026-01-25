"""Comment entity for low-level API."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from better_notion._api import NotionAPI


class Comment:
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
        self._api = api
        self._data = data

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
    def created_time(self) -> str:
        """Get creation timestamp."""
        return self._data.get("created_time", "")

    @property
    def last_edited_time(self) -> str:
        """Get last edit timestamp."""
        return self._data.get("last_edited_time", "")

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
        """Convert to dictionary."""
        return self._data

    def __repr__(self) -> str:
        """String representation."""
        return f"Comment(id={self.id!r})"
