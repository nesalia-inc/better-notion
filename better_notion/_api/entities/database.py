"""Database entity."""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from better_notion._api import NotionAPI
    from better_notion._api.entities import Page


class Database:
    """Represents a Notion database.

    This entity knows its API and can manipulate itself.
    """

    def __init__(self, api: NotionAPI, data: dict[str, Any]) -> None:
        """Initialize a Database entity.

        Args:
            api: The NotionAPI client instance.
            data: Raw database data from Notion API.
        """
        self._api = api
        self._data = data
        self._modified_properties: dict[str, Any] = {}
        self._modified = False

    # Properties
    @property
    def id(self) -> str:
        """Get the database ID."""
        return self._data["id"]

    @property
    def title(self) -> list[dict[str, Any]]:
        """Get the database title."""
        return self._data.get("title", [])

    @property
    def properties(self) -> dict[str, Any]:
        """Get the database properties schema."""
        return self._data["properties"]

    @property
    def created_time(self) -> datetime:
        """Get the creation time."""
        from better_notion.utils.helpers import parse_datetime
        return parse_datetime(self._data["created_time"])

    @property
    def last_edited_time(self) -> datetime:
        """Get the last edited time."""
        from better_notion.utils.helpers import parse_datetime
        return parse_datetime(self._data["last_edited_time"])

    @property
    def archived(self) -> bool:
        """Check if database is archived."""
        return self._data.get("archived", False)

    @property
    def parent(self) -> dict[str, Any]:
        """Get the parent object."""
        return self._data["parent"]

    # Instance methods
    async def query(self, **kwargs: Any) -> list[Page]:
        """Query this database.

        Args:
            **kwargs: Query parameters (filter, sorts, start_cursor, page_size).

        Returns:
            List of Page objects from the query results.

        Raises:
            ValidationError: If query parameters are invalid.
            NotFoundError: If the database no longer exists.
        """
        response = await self._api._request(
            "POST",
            f"/databases/{self.id}/query",
            json=kwargs,
        )

        from better_notion._api.entities import Page
        results = response.get("results", [])
        return [Page(self._api, page_data) for page_data in results]

    async def reload(self) -> None:
        """Reload database data from Notion.

        Fetches the latest database schema and data from Notion.

        Raises:
            NotFoundError: If the database no longer exists.
        """
        data = await self._api._request("GET", f"/databases/{self.id}")
        self._data = data
        self._modified_properties = {}
        self._modified = False

    async def save(self) -> None:
        """Save schema changes to Notion.

        Note: Notion API has limitations on schema updates.
        Some schema changes may require recreating the database.

        Raises:
            ValidationError: If schema is invalid.
            NotFoundError: If database no longer exists.
        """
        if not self._modified:
            return

        # Notion API doesn't support partial schema updates
        # We need to send the full schema
        await self._api._request(
            "PATCH",
            f"/databases/{self.id}",
            json={"properties": self._data["properties"]}
        )

        self._modified_properties = {}
        self._modified = False

    async def delete(self) -> None:
        """Delete (archive) this database.

        Note: This uses DELETE /blocks/{id} because databases are blocks.

        Raises:
            NotFoundError: If the database no longer exists.
        """
        await self._api._request("DELETE", f"/blocks/{self.id}")
        self._data["archived"] = True

    def __repr__(self) -> str:
        """String representation."""
        return f"Database(id={self.id!r})"
