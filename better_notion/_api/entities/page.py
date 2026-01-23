"""Page entity."""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from better_notion._api import NotionAPI


class Page:
    """Represents a Notion page.

    This entity knows its API and can manipulate itself.
    """

    def __init__(self, api: NotionAPI, data: dict[str, Any]) -> None:
        """Initialize a Page entity.

        Args:
            api: The NotionAPI client instance.
            data: Raw page data from Notion API.
        """
        self._api = api
        self._data = data
        self._modified = False

    # Properties
    @property
    def id(self) -> str:
        """Get the page ID."""
        return self._data["id"]

    @property
    def created_time(self) -> datetime:
        """Get the creation time."""
        from better_notion.utils.helpers import parse_datetime
        return parse_datetime(self._data["created_time"])

    @property
    def last_edited_time(self) -> datetime:
        """Get the last edited time."""
        from better_notion.utils.helpers import parse_datetime
        return parse_datetime(self._data["last_edited_time"])

    @property
    def archived(self) -> bool:
        """Check if page is archived."""
        return self._data.get("archived", False)

    @property
    def parent(self) -> dict[str, Any]:
        """Get the parent object."""
        return self._data["parent"]

    @property
    def properties(self) -> dict[str, Any]:
        """Get the page properties."""
        return self._data["properties"]

    # Instance methods
    async def save(self) -> None:
        """Save changes to Notion.

        Updates the page properties on Notion.

        Raises:
            NotFoundError: If the page no longer exists.
            ValidationError: If the properties are invalid.
        """
        await self._api._request(
            "PATCH",
            f"/pages/{self.id}",
            json={"properties": self._data["properties"]},
        )
        self._modified = False

    async def delete(self) -> None:
        """Delete (archive) this page.

        Archives the page in Notion.

        Raises:
            NotFoundError: If the page no longer exists.
        """
        await self._api._request(
            "PATCH",
            f"/pages/{self.id}",
            json={"archived": True},
        )
        self._data["archived"] = True

    async def reload(self) -> None:
        """Reload page data from Notion.

        Fetches the latest page data and updates the entity.

        Raises:
            NotFoundError: If the page no longer exists.
        """
        data = await self._api._request("GET", f"/pages/{self.id}")
        self._data = data
        self._modified = False

    async def update(self, **kwargs: Any) -> None:
        """Update page properties.

        Args:
            **kwargs: Properties to update.

        Raises:
            ValidationError: If the properties are invalid.
            NotFoundError: If the page no longer exists.
        """
        # Merge updated properties with existing data
        for key, value in kwargs.items():
            if key not in self._data:
                self._data[key] = value
            elif isinstance(value, dict) and isinstance(self._data[key], dict):
                self._data[key].update(value)
            else:
                self._data[key] = value

        self._modified = True

    # Navigation
    @property
    def blocks(self) -> Any:
        """Get blocks collection for this page.

        Returns:
            BlockCollection configured for this page's children.

        Example:
            >>> page = await api.pages.get("page_id")
            >>> children = await page.blocks.children()
        """
        from better_notion._api.collections import BlockCollection
        return BlockCollection(self._api, parent_id=self.id)

    def __repr__(self) -> str:
        """String representation."""
        return f"Page(id={self.id!r})"
