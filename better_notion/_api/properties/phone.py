"""Phone property builder."""

from __future__ import annotations

from typing import Any

from better_notion._api.properties.base import Property


class Phone(Property):
    """Builder for phone number properties."""

    def __init__(self, name: str, phone: str | None = None) -> None:
        """Initialize a phone property.

        Args:
            name: The property name.
            phone: The phone number.
        """
        super().__init__(name)
        self._phone = phone

    def to_dict(self) -> dict[str, Any]:
        """Convert to Notion API format."""
        return {
            "type": "phone_number",
            "phone_number": self._phone
        }
