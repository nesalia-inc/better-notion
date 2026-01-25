"""Database model - stub implementation."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, AsyncIterator

from better_notion._sdk.base.entity import BaseEntity

if TYPE_CHECKING:
    from better_notion._sdk.client import NotionClient


class Database(BaseEntity):
    """Notion Database model - stub implementation."""

    def __init__(self, client: "NotionClient", data: dict[str, Any]) -> None:
        """Initialize a Database."""
        super().__init__(client, data)

    async def parent(self) -> "Page | None":
        """Get parent object."""
        # Stub implementation
        return None

    async def children(self) -> AsyncIterator["Page"]:
        """Iterate over child pages."""
        # Stub implementation
        return
        yield  # Make it an async generator

    @property
    def title(self) -> str:
        """Get database title."""
        # Stub implementation
        title_array = self._data.get("title", [])
        if title_array and title_array[0].get("text"):
            return title_array[0]["text"].get("content", "")
        return ""
