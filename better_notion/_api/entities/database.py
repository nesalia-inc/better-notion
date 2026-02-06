"""Database entity."""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from better_notion._api import NotionAPI
    from better_notion._api.entities import Page

from better_notion._api.entities.base import Entity


class Database(Entity):
    """Represents a Notion database.

    This entity knows its API and can manipulate itself.
    """

    # Define valid top-level properties
    VALID_PROPERTIES = {
        "properties",  # Database schema/properties configuration
        "title",       # Database title
        # "parent" is not allowed (immutable)
    }

    def __init__(self, api: NotionAPI, data: dict[str, Any]) -> None:
        """Initialize a Database entity.

        Args:
            api: The NotionAPI client instance.
            data: Raw database data from Notion API.
        """
        super().__init__(api, data)
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
    async def update(self, **kwargs: Any) -> None:
        """Update database properties locally.

        Note:
            This method updates local state only. Call save() to persist
            changes to Notion.

            Database schema updates have limitations in Notion API.
            Some changes may require recreating the database.

        Args:
            **kwargs: Properties to update (properties, title).

        Raises:
            ValueError: If an invalid property name is provided.
            ValueError: If property validation fails.
        """
        # Validate property names
        for key in kwargs:
            if key not in self.VALID_PROPERTIES:
                raise ValueError(
                    f"Invalid database property: {key!r}. "
                    f"Valid properties are: {', '.join(sorted(self.VALID_PROPERTIES))}"
                )

        # Validate and process property values
        validated_kwargs = {}
        for key, value in kwargs.items():
            try:
                validated_value = self._validate_property_value(key, value)
                validated_kwargs[key] = validated_value
            except ValueError as e:
                raise ValueError(f"Invalid value for property '{key}': {e}") from e

        # Update database data
        if "properties" in validated_kwargs:
            self._data["properties"] = validated_kwargs["properties"]

        if "title" in validated_kwargs:
            self._data["title"] = validated_kwargs["title"]

        # Track modified properties
        self._modified_properties.update(validated_kwargs)
        self._modified = True

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

        # Build payload with modified properties
        payload: dict[str, Any] = {}

        if "properties" in self._modified_properties:
            payload["properties"] = self._data["properties"]

        if "title" in self._modified_properties:
            payload["title"] = self._data["title"]

        # Send update to Notion
        await self._api._request(
            "PATCH",
            f"/databases/{self.id}",
            json=payload,
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

    def _validate_property_value(self, name: str, value: Any) -> Any:
        """Validate a property value.

        Args:
            name: Property name
            value: Property value to validate

        Returns:
            Validated/converted value

        Raises:
            ValueError: If value is invalid
        """
        if name == "title":
            # Title should be a list of rich text objects
            if not isinstance(value, list) and value is not None:
                raise ValueError(f"title must be a list, got {type(value).__name__}")
            return value

        elif name == "properties":
            # Properties should be a dict
            if not isinstance(value, dict) and value is not None:
                raise ValueError(f"properties must be a dict, got {type(value).__name__}")
            return value

        return value

    def _validate_property(self, name: str, value: Any) -> Any:
        """Validate an individual property.

        Args:
            name: Property name
            value: Property value to validate

        Returns:
            Validated/converted value

        Raises:
            ValueError: If value is invalid
        """
        # Basic validation for properties
        if name == "properties":
            if value is not None and not isinstance(value, dict):
                raise ValueError(f"properties must be a dict, got {type(value).__name__}")

        elif name == "title":
            if value is not None and not isinstance(value, list):
                raise ValueError(f"title must be a list, got {type(value).__name__}")

        return value
