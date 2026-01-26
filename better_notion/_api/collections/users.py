"""User collection."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from better_notion._api import NotionAPI



class UserCollection:
    """Collection for managing users.

    Provides factory methods for retrieving users.
    """

    def __init__(self, api: NotionAPI) -> None:
        """Initialize the User collection.

        Args:
            api: The NotionAPI client instance.
        """
        self._api = api

    async def get(self, user_id: str) -> dict[str, Any]:
        """Retrieve a user by ID.

        Args:
            user_id: The user ID.

        Returns:
            Raw user data dict from Notion API.

        Raises:
            NotFoundError: If the user does not exist.
        """
        return await self._api._request("GET", f"/users/{user_id}")

    async def list(self) -> list[dict[str, Any]]:
        """List all users.

        Returns:
            List of raw user data dicts from Notion API.
        """
        data = await self._api._request("GET", "/users")
        return data.get("results", [])

    async def me(self) -> dict[str, Any]:
        """Get the current bot user.

        Returns:
            Raw user data dict from Notion API.
        """
        return await self._api._request("GET", "/users/me")
