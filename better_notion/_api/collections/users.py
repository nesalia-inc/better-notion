"""User collection."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from better_notion._api import NotionAPI

from better_notion._api.entities import User


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

    async def get(self, user_id: str) -> User:
        """Retrieve a user by ID.

        Args:
            user_id: The user ID.

        Returns:
            A User entity.

        Raises:
            NotFoundError: If the user does not exist.
        """
        data = await self._api._request("GET", f"/users/{user_id}")
        return User(self._api, data)

    async def list(self) -> list[User]:
        """List all users.

        Returns:
            List of User entities.
        """
        data = await self._api._request("GET", "/users")
        return [User(self._api, user_data) for user_data in data.get("results", [])]

    async def me(self) -> User:
        """Get the current bot user.

        Returns:
            The current User entity.
        """
        data = await self._api._request("GET", "/users/me")
        return User(self._api, data)
