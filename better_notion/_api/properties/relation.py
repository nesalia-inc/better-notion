"""Relation property builder."""

from __future__ import annotations

from typing import Any

from better_notion._api.properties.base import Property


class Relation(Property):
    """Builder for relation properties."""

    def __init__(self, name: str, page_ids: list[str]) -> None:
        """Initialize a relation property.

        Args:
            name: The property name (e.g., "Assigned To", "Depends On").
            page_ids: List of related page IDs.
        """
        super().__init__(name)
        self._page_ids = page_ids

    def to_dict(self) -> dict[str, Any]:
        """Convert to Notion API format."""
        return {
            "type": "relation",
            "relation": [{"id": page_id} for page_id in self._page_ids]
        }
