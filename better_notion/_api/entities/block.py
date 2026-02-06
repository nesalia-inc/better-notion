"""Block entity."""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from better_notion._api import NotionAPI


class Block:
    """Represents a Notion block.

    This entity knows its API and can manipulate itself.
    """

    # Define valid top-level properties
    VALID_PROPERTIES = {
        "content",  # Block content
        "archived",  # Archive status
    }

    def __init__(self, api: NotionAPI, data: dict[str, Any]) -> None:
        """Initialize a Block entity.

        Args:
            api: The NotionAPI client instance.
            data: Raw block data from Notion API.
        """
        self._api = api
        self._data = data
        self._modified_properties: dict[str, Any] = {}
        self._modified = False

    # Properties
    @property
    def id(self) -> str:
        """Get the block ID."""
        return self._data["id"]

    @property
    def created_time(self) -> datetime:
        """Get the creation time.

        Returns:
            Creation timestamp as datetime object.

        Raises:
            ValueError: If created_time is not available in the data.
        """
        from better_notion.utils.helpers import parse_datetime
        created_time_str = self._data.get("created_time")
        if not created_time_str:
            raise ValueError("Block data missing 'created_time' field")
        return parse_datetime(created_time_str)

    @property
    def last_edited_time(self) -> datetime:
        """Get the last edited time.

        Returns:
            Last edited timestamp as datetime object.

        Raises:
            ValueError: If last_edited_time is not available in the data.
        """
        from better_notion.utils.helpers import parse_datetime
        edited_time_str = self._data.get("last_edited_time")
        if not edited_time_str:
            raise ValueError("Block data missing 'last_edited_time' field")
        return parse_datetime(edited_time_str)

    @property
    def archived(self) -> bool:
        """Check if block is archived."""
        return self._data.get("archived", False)

    @property
    def type(self) -> str:
        """Get the block type."""
        return self._data["type"]

    @property
    def content(self) -> Any:
        """Get the block content."""
        from better_notion.utils.helpers import extract_content
        return extract_content(self._data)

    @content.setter
    def content(self, value: Any) -> None:
        """Set the block content."""
        self._data[self._data["type"]] = value
        self._modified = True

    # Instance methods
    async def save(self) -> None:
        """Save changes to Notion.

        Updates the block content on Notion.

        Raises:
            NotFoundError: If the block no longer exists.
            ValidationError: If the block content is invalid.
        """
        block_type = self._data["type"]
        block_content = self._data[block_type]

        await self._api._request(
            "PATCH",
            f"/blocks/{self.id}",
            json={block_type: block_content},
        )
        self._modified = False

    async def delete(self) -> None:
        """Delete this block.

        Permanently deletes the block in Notion.

        Raises:
            NotFoundError: If the block no longer exists.
        """
        await self._api._request("DELETE", f"/blocks/{self.id}")

    async def reload(self) -> None:
        """Reload block data from Notion.

        Fetches the latest block data and updates the entity.

        Raises:
            NotFoundError: If the block no longer exists.
        """
        data = await self._api._request("GET", f"/blocks/{self.id}")
        self._data = data
        self._modified_properties = {}
        self._modified = False

    async def update(self, **kwargs: Any) -> None:
        """Update block properties locally.

        Note:
            This method updates local state only. Call save() to persist
            changes to Notion.

        Args:
            **kwargs: Properties to update (content, archived).

        Raises:
            ValueError: If an invalid property name is provided.
            ValueError: If property validation fails.
        """
        # Validate property names
        for key in kwargs:
            if key not in self.VALID_PROPERTIES:
                raise ValueError(
                    f"Invalid block property: {key!r}. "
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

        # Update block data
        if "content" in validated_kwargs:
            block_type = self._data["type"]
            self._data[block_type] = validated_kwargs["content"]

        if "archived" in validated_kwargs:
            self._data["archived"] = validated_kwargs["archived"]

        # Track modified properties
        self._modified_properties.update(validated_kwargs)
        self._modified = True

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

        elif name == "content":
            # Content can be any valid block content structure
            # We'll do basic type checking
            if not isinstance(value, dict) and value is not None:
                raise ValueError(f"content must be a dict or None, got {type(value).__name__}")
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
        # Basic validation for content
        if name == "content":
            if value is not None and not isinstance(value, dict):
                raise ValueError(f"content must be a dict, got {type(value).__name__}")

        return value

    def __repr__(self) -> str:
        """String representation."""
        return f"Block(id={self.id!r}, type={self.type!r})"
