"""Select property builders."""

from __future__ import annotations

from typing import Any

from better_notion._api.properties.base import Property


class Select(Property):
    """Builder for select properties."""

    def __init__(self, name: str, value: str) -> None:
        """Initialize a select property.

        Args:
            name: The property name.
            value: The selected value (must exist in database).
        """
        super().__init__(name)
        self._value = value

    def to_dict(self) -> dict[str, Any]:
        """Convert to Notion API format."""
        return {
            "type": "select",
            "select": {
                "name": self._value
            }
        }


class MultiSelect(Property):
    """Builder for multi-select properties."""

    def __init__(self, name: str, values: list[str]) -> None:
        """Initialize a multi-select property.

        Args:
            name: The property name.
            values: The selected values (must exist in database).
        """
        super().__init__(name)
        self._values = values

    def to_dict(self) -> dict[str, Any]:
        """Convert to Notion API format."""
        return {
            "type": "multi_select",
            "multi_select": [
                {"name": value} for value in self._values
            ]
        }
