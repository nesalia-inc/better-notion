"""Users API endpoint."""

from __future__ import annotations

from typing import Any


class UsersEndpoint:
    """Users API endpoint.

    Provides methods for interacting with Notion users.
    """

    def __init__(self, api: Any) -> None:
        """Initialize the Users endpoint.

        Args:
            api: The NotionAPI client instance.
        """
        self._api = api

    async def retrieve(self, user_id: str) -> dict[str, Any]:
        """Retrieve a user object.

        Args:
            user_id: The identifier for the Notion user.

        Returns:
            The user data as a dictionary.

        Raises:
            NotFoundError: If the user doesn't exist.
        """
        raise NotImplementedError("Not yet implemented")

    async def list(self, **kwargs: Any) -> dict[str, Any]:
        """List all users.

        Args:
            **kwargs: Pagination parameters.

        Returns:
            The list of users.
        """
        raise NotImplementedError("Not yet implemented")
