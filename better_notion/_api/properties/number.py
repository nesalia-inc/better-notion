"""Number property builder."""

from __future__ import annotations

from typing import Any

from better_notion._api.properties.base import Property


class Number(Property):
    """Builder for number properties."""

    def __init__(self, name: str, value: int | float | None = None) -> None:
        """Initialize a number property.

        Args:
            name: The property name.
            value: The number value.
        """
        super().__init__(name)
        self._value = value

    def to_dict(self) -> dict[str, Any]:
        """Convert to Notion API format."""
        return {
            "type": "number",
            "number": self._value
        }
