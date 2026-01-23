"""Databases API endpoint."""

from __future__ import annotations

from typing import Any


class DatabasesEndpoint:
    """Databases API endpoint.

    Provides methods for interacting with Notion databases.
    """

    def __init__(self, api: Any) -> None:
        """Initialize the Databases endpoint.

        Args:
            api: The NotionAPI client instance.
        """
        self._api = api

    async def retrieve(self, database_id: str) -> dict[str, Any]:
        """Retrieve a database object.

        Args:
            database_id: The identifier for the Notion database.

        Returns:
            The database data as a dictionary.

        Raises:
            NotFoundError: If the database doesn't exist.
        """
        raise NotImplementedError("Not yet implemented")

    async def query(self, database_id: str, **kwargs: Any) -> dict[str, Any]:
        """Query a database.

        Args:
            database_id: The identifier for the Notion database.
            **kwargs: Query parameters (filter, sort, etc.).

        Returns:
            The query results.
        """
        raise NotImplementedError("Not yet implemented")
