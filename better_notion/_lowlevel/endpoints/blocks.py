"""Blocks API endpoint."""

from __future__ import annotations

from typing import Any


class BlocksEndpoint:
    """Blocks API endpoint.

    Provides methods for interacting with Notion blocks.
    """

    def __init__(self, api: Any) -> None:
        """Initialize the Blocks endpoint.

        Args:
            api: The NotionAPI client instance.
        """
        self._api = api

    async def retrieve(self, block_id: str) -> dict[str, Any]:
        """Retrieve a block object.

        Args:
            block_id: The identifier for the Notion block.

        Returns:
            The block data as a dictionary.

        Raises:
            NotFoundError: If the block doesn't exist.
        """
        raise NotImplementedError("Not yet implemented")

    async def update(self, block_id: str, **kwargs: Any) -> dict[str, Any]:
        """Update a block.

        Args:
            block_id: The identifier for the Notion block.
            **kwargs: Additional block properties to update.

        Returns:
            The updated block data.
        """
        raise NotImplementedError("Not yet implemented")
