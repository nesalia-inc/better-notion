"""Email property builder."""

from __future__ import annotations

from typing import Any

from better_notion._api.properties.base import Property


class Email(Property):
    """Builder for email properties."""

    def __init__(self, name: str, email: str | None = None) -> None:
        """Initialize an email property.

        Args:
            name: The property name.
            email: The email address.
        """
        super().__init__(name)
        self._email = email

    def to_dict(self) -> dict[str, Any]:
        """Convert to Notion API format."""
        return {
            "type": "email",
            "email": self._email
        }
