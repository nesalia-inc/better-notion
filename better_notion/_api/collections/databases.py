"""Database collection."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from better_notion._api import NotionAPI

from better_notion._api.entities import Database, Page


class DatabaseCollection:
    """Collection for managing databases.

    Provides factory methods for creating and retrieving databases.
    """

    def __init__(self, api: NotionAPI) -> None:
        """Initialize the Database collection.

        Args:
            api: The NotionAPI client instance.
        """
        self._api = api

    async def get(self, database_id: str) -> Database:
        """Retrieve a database by ID.

        Args:
            database_id: The database ID.

        Returns:
            A Database entity.

        Raises:
            NotFoundError: If the database does not exist.
        """
        data = await self._api._request("GET", f"/databases/{database_id}")
        return Database(self._api, data)

    async def query(self, database_id: str, **kwargs: Any) -> Any:
        """Query a database.

        Args:
            database_id: The database ID.
            **kwargs: Query parameters (filter, sorts, start_cursor, etc.).

        Returns:
            Query results with pages list.

        Raises:
            NotFoundError: If the database does not exist.
            ValidationError: If the query parameters are invalid.
        """
        return await self._api._request(
            "POST",
            f"/databases/{database_id}/query",
            json=kwargs,
        )

    async def create_page(self, database_id: str, **kwargs: Any) -> Page:
        """Create a new page in a database.

        Args:
            database_id: The database ID.
            **kwargs: Page properties.

        Returns:
            The created Page entity.

        Raises:
            ValidationError: If the page properties are invalid.
            NotFoundError: If the database does not exist.
        """
        # Ensure parent is set to the database
        page_data = {"parent": {"database_id": database_id}, **kwargs}
        data = await self._api._request("POST", "/pages", json=page_data)
        return Page(self._api, data)
