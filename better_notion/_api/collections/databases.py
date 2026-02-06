"""Database collection."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from better_notion._api import NotionAPI

from better_notion._api.entities import Database


class DatabaseCollection:
    """Collection for managing databases.

    Provides factory methods for creating and retrieving databases as Entity objects.
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
            Database entity with rich methods (query, reload, save, delete).

        Raises:
            NotFoundError: If the database does not exist.
        """
        data = await self._api._request("GET", f"/databases/{database_id}")
        return Database(self._api, data)

    async def query(self, database_id: str, **kwargs: Any) -> list[Any]:
        """Query a database.

        Args:
            database_id: The database ID.
            **kwargs: Query parameters (filter, sorts, start_cursor, etc.).

        Returns:
            List of Page entities from query results.

        Raises:
            NotFoundError: If the database does not exist.
            ValidationError: If the query parameters are invalid.
        """
        from better_notion._api.entities import Page

        data = await self._api._request(
            "POST",
            f"/databases/{database_id}/query",
            json=kwargs,
        )
        results = data.get("results", [])
        return [Page(self._api, page_data) for page_data in results]

    async def create_page(self, database_id: str, **kwargs: Any) -> Any:
        """Create a new page in a database.

        Args:
            database_id: The database ID.
            **kwargs: Page properties.

        Returns:
            Page entity for the created page.

        Raises:
            ValidationError: If the page properties are invalid.
            NotFoundError: If the database does not exist.
        """
        from better_notion._api.entities import Page

        # Ensure parent is set to the database
        page_data = {"parent": {"database_id": database_id}, **kwargs}
        data = await self._api._request("POST", "/pages", json=page_data)
        return Page(self._api, data)

    async def create(
        self,
        parent: dict[str, Any],
        title: str,
        properties: dict[str, Any]
    ) -> Database:
        """Create a new database.

        Args:
            parent: Parent object (e.g., {"type": "page_id", "page_id": "..."})
            title: Database title
            properties: Database schema/properties configuration

        Returns:
            Database entity with rich methods.

        Raises:
            ValidationError: If the database configuration is invalid.
            NotFoundError: If the parent page does not exist.
        """
        # Build title array
        title_array = [{"type": "text", "text": {"content": title}}]

        # Create database request
        database_data = {
            "parent": parent,
            "title": title_array,
            "properties": properties
        }

        data = await self._api._request("POST", "/databases", json=database_data)
        return Database(self._api, data)
