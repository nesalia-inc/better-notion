"""Checkbox property builder."""

from __future__ import annotations

from typing import Any

from better_notion._api.properties.base import Property


class Checkbox(Property):
    """Builder for checkbox properties."""

    def __init__(self, name: str, checked: bool = False) -> None:
        """Initialize a checkbox property.

        Args:
            name: The property name.
            checked: Whether checkbox is checked.
        """
        super().__init__(name)
        self._checked = checked

    def to_dict(self) -> dict[str, Any]:
        """Convert to Notion API format."""
        return {
            "type": "checkbox",
            "checkbox": self._checked
        }
