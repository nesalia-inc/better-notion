"""Database entity."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from better_notion._api import NotionAPI


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

    # Instance methods
    async def query(self, **kwargs: Any) -> Any:
        """Query this database.

        Args:
            **kwargs: Query parameters (filter, sort, etc.).

        Returns:
            Query results.

        Raises:
            NotImplementedError: Not yet implemented.
        """
        raise NotImplementedError("Database.query() not yet implemented")

    async def reload(self) -> None:
        """Reload database data from Notion.

        Raises:
            NotImplementedError: Not yet implemented.
        """
        raise NotImplementedError("Database.reload() not yet implemented")

    def __repr__(self) -> str:
        """String representation."""
        return f"Database(id={self.id!r})"
