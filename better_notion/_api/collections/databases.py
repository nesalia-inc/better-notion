"""Database collection."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from better_notion._api import NotionAPI


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

    async def get(self, database_id: str) -> dict[str, Any]:
        """Retrieve a database by ID.

        Args:
            database_id: The database ID.

        Returns:
            Raw database data dict from Notion API.

        Raises:
            NotFoundError: If the database does not exist.
        """
        return await self._api._request("GET", f"/databases/{database_id}")

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

    async def create_page(self, database_id: str, **kwargs: Any) -> dict[str, Any]:
        """Create a new page in a database.

        Args:
            database_id: The database ID.
            **kwargs: Page properties.

        Returns:
            Raw page data dict from Notion API.

        Raises:
            ValidationError: If the page properties are invalid.
            NotFoundError: If the database does not exist.
        """
        # Ensure parent is set to the database
        page_data = {"parent": {"database_id": database_id}, **kwargs}
        return await self._api._request("POST", "/pages", json=page_data)

    async def create(
        self,
        parent: dict[str, Any],
        title: str,
        properties: dict[str, Any]
    ) -> dict[str, Any]:
        """Create a new database.

        Args:
            parent: Parent object (e.g., {"type": "page_id", "page_id": "..."})
            title: Database title
            properties: Database schema/properties configuration

        Returns:
            Raw database data dict from Notion API.

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

        return await self._api._request("POST", "/databases", json=database_data)
