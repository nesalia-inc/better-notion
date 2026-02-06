"""User entity."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from better_notion._api import NotionAPI

from better_notion._api.entities.base import ReadOnlyEntity


class User(ReadOnlyEntity):
    """Represents a Notion user.

    This entity represents user metadata.

    Note:
        User is read-only - does not support save() or delete().
    """

    def __init__(self, api: NotionAPI, data: dict[str, Any]) -> None:
        """Initialize a User entity.

        Args:
            api: The NotionAPI client instance.
            data: Raw user data from Notion API.
        """
        super().__init__(api, data)

    # Properties
    @property
    def id(self) -> str:
        """Get the user ID."""
        return self._data["id"]

    @property
    def name(self) -> str:
        """Get the user name."""
        return self._data.get("name", "")

    @property
    def avatar_url(self) -> str | None:
        """Get the avatar URL."""
        return self._data.get("avatar_url")

    @property
    def type(self) -> str:
        """Get the user type."""
        return self._data["type"]

    async def reload(self) -> None:
        """Reload user data from Notion.

        Fetches the latest user data and updates the entity.

        Raises:
            NotFoundError: If the user no longer exists.
        """
        data = await self._api._request("GET", f"/users/{self.id}")
        self._data = data
