"""Block entity."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from better_notion._api import NotionAPI


class Block:
    """Represents a Notion block.

    This entity knows its API and can manipulate itself.
    """

    def __init__(self, api: NotionAPI, data: dict[str, Any]) -> None:
        """Initialize a Block entity.

        Args:
            api: The NotionAPI client instance.
            data: Raw block data from Notion API.
        """
        self._api = api
        self._data = data
        self._modified = False

    # Properties
    @property
    def id(self) -> str:
        """Get the block ID."""
        return self._data["id"]

    @property
    def type(self) -> str:
        """Get the block type."""
        return self._data["type"]

    @property
    def content(self) -> Any:
        """Get the block content."""
        raise NotImplementedError("Block.content not yet implemented")

    @content.setter
    def content(self, value: Any) -> None:
        """Set the block content."""
        raise NotImplementedError("Block.content setter not yet implemented")

    # Instance methods
    async def save(self) -> None:
        """Save changes to Notion.

        Raises:
            NotImplementedError: Not yet implemented.
        """
        raise NotImplementedError("Block.save() not yet implemented")

    async def delete(self) -> None:
        """Delete this block.

        Raises:
            NotImplementedError: Not yet implemented.
        """
        raise NotImplementedError("Block.delete() not yet implemented")

    async def reload(self) -> None:
        """Reload block data from Notion.

        Raises:
            NotImplementedError: Not yet implemented.
        """
        raise NotImplementedError("Block.reload() not yet implemented")

    def __repr__(self) -> str:
        """String representation."""
        return f"Block(id={self.id!r}, type={self.type!r})"
