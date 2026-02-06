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
            Block entity object.

        Raises:
            NotFoundError: If the block does not exist.
        """
        from better_notion._api.entities import Block
        data = await self._api._request("GET", f"/blocks/{block_id}")
        return Block(self._api, data)

    async def update(self, block_id: str, **kwargs: Any) -> Block:
        """Update a block by ID.

        Args:
            block_id: The block ID.
            **kwargs: Block properties to update (varies by block type).
                For text blocks: paragraph, heading_1, heading_2, heading_3, etc.
                For code blocks: code (with language and rich_text)
                For todo blocks: to_do (with checked and rich_text)
                etc.

        Returns:
            Updated Block entity.

        Raises:
            ValidationError: If the request is invalid.
            NotFoundError: If the block does not exist.

        Example:
            >>> # Update a paragraph
            >>> block = await api.blocks.update(
            ...     block_id="block-123",
            ...     paragraph={"rich_text": [{"type": "text", "text": {"content": "New text"}}]}
            ... )
        """
        from better_notion._api.entities import Block
        data = await self._api._request("PATCH", f"/blocks/{block_id}", json=kwargs)
        return Block(self._api, data)

    async def children(self) -> list[Block]:
        """Get children blocks.

        Returns:
            List of child Block entities.

        Raises:
            NotFoundError: If the parent block does not exist.
            ValidationError: If parent_id is not set.
        """
        if not self._parent_id:
            raise ValueError("parent_id is required to get children")

        from better_notion._api.entities import Block
        data = await self._api._request("GET", f"/blocks/{self._parent_id}/children")
        results = data.get("results", [])
        return [Block(self._api, block_data) for block_data in results]

    async def append(self, **kwargs: Any) -> Block:
        """Append a new block.

        Args:
            **kwargs: Block properties including children (required).

        Returns:
            The newly created Block entity.

        Raises:
            ValidationError: If parent_id is not set or request is invalid.
            BadRequestError: If the request is invalid.
        """
        if not self._parent_id:
            raise ValueError("parent_id is required to append blocks")

        from better_notion._api.entities import Block
        data = await self._api._request(
            "PATCH",
            f"/blocks/{self._parent_id}/children",
            json=kwargs,
        )
        # The API returns the updated parent block with new children
        # We need to get the last created child
        children = data.get("results", [])
        if children:
            return Block(self._api, children[-1])
        # If no children returned, we need to fetch the parent's children again
        # For now, just return the first child from the response
        return Block(self._api, data)

    async def delete(self, block_id: str) -> None:
        """Delete a block by ID.

        Args:
            block_id: The block ID.

        Raises:
            NotFoundError: If the block does not exist.
        """
        await self._api._request("DELETE", f"/blocks/{block_id}")
