"""User entity."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from better_notion._api import NotionAPI


class User:
    """Represents a Notion user.

    This entity represents user metadata.
    """

    def __init__(self, api: NotionAPI, data: dict[str, Any]) -> None:
        """Initialize a User entity.

        Args:
            api: The NotionAPI client instance.
            data: Raw user data from Notion API.
        """
        self._api = api
        self._data = data

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

    def __repr__(self) -> str:
        """String representation."""
        return f"User(id={self.id!r}, name={self.name!r})"
