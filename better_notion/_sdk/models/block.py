"""Block model - stub implementation."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, AsyncIterator

from better_notion._sdk.base.entity import BaseEntity

if TYPE_CHECKING:
    from better_notion._sdk.client import NotionClient


class Block(BaseEntity):
    """Notion Block model - stub implementation."""

    def __init__(self, client: "NotionClient", data: dict[str, Any]) -> None:
        """Initialize a Block."""
        super().__init__(client, data)

    async def parent(self) -> "Page | Block | None":
        """Get parent object."""
        # Stub implementation
        return None

    async def children(self) -> AsyncIterator["Block"]:
        """Iterate over child blocks."""
        # Stub implementation
        return
        yield  # Make it an async generator

    @property
    def type(self) -> str:
        """Get block type."""
        return self._data.get("type", "")

    @property
    def code(self) -> str:
        """Get code content for code blocks."""
        # Stub implementation
        return ""

    @property
    def language(self) -> str:
        """Get language for code blocks."""
        # Stub implementation
        return ""
