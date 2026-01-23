"""Title property builder."""

from __future__ import annotations

from typing import Any

from better_notion._api.properties.base import Property


class Title(Property):
    """Builder for title properties."""

    def __init__(self, name: str = "Name", content: str = "") -> None:
        """Initialize a title property.

        Args:
            name: The property name (default: "Name").
            content: The title content.
        """
        super().__init__(name)
        self._content = content

    def to_dict(self) -> dict[str, Any]:
        """Convert to Notion API format."""
        return {
            "type": "title",
            "title": [
                {
                    "type": "text",
                    "text": {"content": self._content}
                }
            ]
        }
