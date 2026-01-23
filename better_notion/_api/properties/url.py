"""URL property builder."""

from __future__ import annotations

from typing import Any

from better_notion._api.properties.base import Property


class URL(Property):
    """Builder for URL properties."""

    def __init__(self, name: str, url: str | None = None) -> None:
        """Initialize a URL property.

        Args:
            name: The property name.
            url: The URL value.
        """
        super().__init__(name)
        self._url = url

    def to_dict(self) -> dict[str, Any]:
        """Convert to Notion API format."""
        return {
            "type": "url",
            "url": self._url
        }
