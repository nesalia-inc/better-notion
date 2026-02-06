"""Page entity."""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from better_notion._api import NotionAPI


class Page:
    """Represents a Notion page.

    This entity knows its API and can manipulate itself.
    """

    # Define valid top-level properties
    VALID_PROPERTIES = {
        "properties",  # Page properties (title, etc.)
        "archived",    # Archive status
        "icon",        # Page icon
        "cover",       # Page cover
        # "parent" is not allowed (immutable)
    }

    def __init__(self, api: NotionAPI, data: dict[str, Any]) -> None:
        """Initialize a Page entity.

        Args:
            api: The NotionAPI client instance.
            data: Raw page data from Notion API.
        """
        self._api = api
        self._data = data
        self._modified_properties: dict[str, Any] = {}
        self._modified = False
        self._schema: dict[str, Any] | None = None  # Cached schema

    # Properties
    @property
    def id(self) -> str:
        """Get the page ID."""
        return self._data["id"]

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
        """Check if page is archived."""
        return self._data.get("archived", False)

    @property
    def parent(self) -> dict[str, Any]:
        """Get the parent object."""
        return self._data["parent"]

    @property
    def properties(self) -> dict[str, Any]:
        """Get the page properties."""
        return self._data["properties"]

    # Instance methods
    async def save(self) -> None:
        """Save changes to Notion.

        Updates the page properties on Notion.

        Raises:
            NotFoundError: If the page no longer exists.
            ValidationError: If the properties are invalid.
        """
        if not self._modified:
            return

        # Send only modified properties in request format
        await self._api._request(
            "PATCH",
            f"/pages/{self.id}",
            json={"properties": self._modified_properties},
        )

        # Clear modified properties after successful save
        self._modified_properties = {}
        self._modified = False

    async def delete(self) -> None:
        """Delete (archive) this page.

        Archives the page in Notion.

        Raises:
            NotFoundError: If the page no longer exists.
        """
        await self._api._request(
            "PATCH",
            f"/pages/{self.id}",
            json={"archived": True},
        )
        self._data["archived"] = True

    async def reload(self) -> None:
        """Reload page data from Notion.

        Fetches the latest page data and updates the entity.

        Raises:
            NotFoundError: If the page no longer exists.
        """
        data = await self._api._request("GET", f"/pages/{self.id}")
        self._data = data
        self._modified_properties = {}
        self._modified = False

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
        if name == "archived":
            if not isinstance(value, bool):
                raise ValueError(f"archived must be a boolean, got {type(value).__name__}")
            return value

        elif name == "icon":
            # Icon can be None, dict, or str (emoji)
            if value is None:
                return None
            if isinstance(value, str):
                return {"type": "emoji", "emoji": value}
            if isinstance(value, dict):
                return value
            raise ValueError(f"icon must be None, str, or dict, got {type(value).__name__}")

        elif name == "cover":
            # Cover can be None, str (URL), or dict
            if value is None:
                return None
            if isinstance(value, str):
                return {"type": "external", "external": {"url": value}}
            if isinstance(value, dict):
                return value
            raise ValueError(f"cover must be None, str, or dict, got {type(value).__name__}")

        elif name == "properties":
            if not isinstance(value, dict):
                raise ValueError(f"properties must be a dict, got {type(value).__name__}")

            # Validate individual property values
            validated = {}
            for prop_name, prop_value in value.items():
                validated[prop_name] = self._validate_property(prop_name, prop_value)
            return validated

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
        # Check if it's a Property builder object with to_dict method
        if hasattr(value, "to_dict"):
            return value

        # Basic type validation for common types
        if name in ("title", "name"):
            if not isinstance(value, str) and not hasattr(value, "to_dict"):
                raise ValueError(f"{name} must be a string or property builder object")

        elif name in ("rich_text", "text"):
            if not isinstance(value, str) and not hasattr(value, "to_dict"):
                raise ValueError(f"{name} must be a string or property builder object")

        return value

    async def update(self, **kwargs: Any) -> None:
        """Update page properties.

        Args:
            **kwargs: Properties to update. If 'properties' is passed as a kwarg,
                     its contents will be unpacked into the modified properties.

        Raises:
            ValueError: If an invalid property name is provided.
            ValueError: If property validation fails.
            ValidationError: If the properties are invalid.
            NotFoundError: If the page no longer exists.
        """
        # Validate property names
        for key in kwargs:
            if key not in self.VALID_PROPERTIES:
                raise ValueError(
                    f"Invalid page property: {key!r}. "
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

        # Special handling for 'properties' kwarg - unpack it
        if "properties" in validated_kwargs:
            self._modified_properties.update(validated_kwargs["properties"])

        # Handle other kwargs normally (e.g., 'archived')
        for key, value in validated_kwargs.items():
            if key != "properties":
                self._modified_properties[key] = value

        # Only mark as modified if we actually added something
        if validated_kwargs:
            self._modified = True

    # Navigation
    @property
    def blocks(self) -> Any:
        """Get blocks collection for this page.

        Returns:
            BlockCollection configured for this page's children.

        Example:
            >>> page = await api.pages.get("page_id")
            >>> children = await page.blocks.children()
        """
        from better_notion._api.collections import BlockCollection
        return BlockCollection(self._api, parent_id=self.id)

    def __repr__(self) -> str:
        """String representation."""
        return f"Page(id={self.id!r})"
