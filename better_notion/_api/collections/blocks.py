"""Block collection."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from better_notion._api import NotionAPI

from better_notion._api.entities import Block


class BlockCollection:
    """Collection for managing blocks.

    Provides factory methods for creating and retrieving blocks.
    """

    def __init__(self, api: NotionAPI, parent_id: str | None = None) -> None:
        """Initialize the Block collection.

        Args:
            api: The NotionAPI client instance.
            parent_id: Optional parent ID for children blocks.
        """
        self._api = api
        self._parent_id = parent_id

    async def get(self, block_id: str) -> Block:
        """Retrieve a block by ID.

        Args:
            block_id: The block ID.

        Returns:
            A Block entity.

        Raises:
            NotImplementedError: Not yet implemented.
        """
        raise NotImplementedError("BlockCollection.get() not yet implemented")

    async def list(self, **kwargs: Any) -> list[Block]:
        """List blocks.

        Args:
            **kwargs: Query parameters.

        Returns:
            List of Block entities.

        Raises:
            NotImplementedError: Not yet implemented.
        """
        raise NotImplementedError("BlockCollection.list() not yet implemented")

    async def children(self) -> list[Block]:
        """Get children blocks.

        Returns:
            List of child Block entities.

        Raises:
            NotImplementedError: Not yet implemented.
        """
        raise NotImplementedError("BlockCollection.children() not yet implemented")

    async def append(self, **kwargs: Any) -> Block:
        """Append a new block.

        Args:
            **kwargs: Block properties.

        Returns:
            The created Block entity.

        Raises:
            NotImplementedError: Not yet implemented.
        """
        raise NotImplementedError("BlockCollection.append() not yet implemented")
