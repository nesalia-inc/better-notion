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
        from better_notion.utils.helpers import extract_content
        return extract_content(self._data)

    @content.setter
    def content(self, value: Any) -> None:
        """Set the block content."""
        self._data[self._data["type"]] = value
        self._modified = True

    # Instance methods
    async def save(self) -> None:
        """Save changes to Notion.

        Updates the block content on Notion.

        Raises:
            NotFoundError: If the block no longer exists.
            ValidationError: If the block content is invalid.
        """
        block_type = self._data["type"]
        block_content = self._data[block_type]

        await self._api._request(
            "PATCH",
            f"/blocks/{self.id}",
            json={block_type: block_content},
        )
        self._modified = False

    async def delete(self) -> None:
        """Delete this block.

        Permanently deletes the block in Notion.

        Raises:
            NotFoundError: If the block no longer exists.
        """
        await self._api._request("DELETE", f"/blocks/{self.id}")

    async def reload(self) -> None:
        """Reload block data from Notion.

        Fetches the latest block data and updates the entity.

        Raises:
            NotFoundError: If the block no longer exists.
        """
        data = await self._api._request("GET", f"/blocks/{self.id}")
        self._data = data
        self._modified = False

    def __repr__(self) -> str:
        """String representation."""
        return f"Block(id={self.id!r}, type={self.type!r})"
