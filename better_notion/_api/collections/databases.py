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
            NotImplementedError: Not yet implemented.
        """
        raise NotImplementedError("DatabaseCollection.get() not yet implemented")

    async def query(self, database_id: str, **kwargs: Any) -> Any:
        """Query a database.

        Args:
            database_id: The database ID.
            **kwargs: Query parameters.

        Returns:
            Query results.

        Raises:
            NotImplementedError: Not yet implemented.
        """
        raise NotImplementedError("DatabaseCollection.query() not yet implemented")

    async def create_page(self, database_id: str, **kwargs: Any) -> Page:
        """Create a new page in a database.

        Args:
            database_id: The database ID.
            **kwargs: Page properties.

        Returns:
            The created Page entity.

        Raises:
            NotImplementedError: Not yet implemented.
        """
        raise NotImplementedError("DatabaseCollection.create_page() not yet implemented")
