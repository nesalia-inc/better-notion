"""Synced block model."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from better_notion._sdk.models.block import Block

if TYPE_CHECKING:
    from better_notion._sdk.client import NotionClient
from better_notion._api.collections import BlockCollection


class SyncedBlock(Block):
    """Synced block (block that can be synced across multiple pages).

    Example:
        >>> synced = await SyncedBlock.create(
        ...     parent=page,
        ...     client=client
        ... )
    """

    def __init__(self, client: "NotionClient", data: dict[str, Any]) -> None:
        """Initialize a SyncedBlock.

        Args:
            client: NotionClient instance
            data: Raw block data from Notion API
        """
        super().__init__(client, data)

    @property
    def synced_from(self) -> str | None:
        """Get original block ID if this is a copy.

        Returns:
            Original block ID or None
        """
        synced_data = self._data.get("synced_block", {})
        return synced_data.get("synced_from")

    @classmethod
    async def create(
        cls,
        parent: "Page | Block",
        *,
        client: "NotionClient",
        **kwargs: Any
    ) -> "SyncedBlock":
        """Create a new synced block.

        Args:
            parent: Parent page or block
            client: NotionClient instance
            **kwargs: Additional parameters

        Returns:
            Newly created SyncedBlock block

        Example:
            >>> synced = await SyncedBlock.create(
            ...     parent=page,
            ...     client=client
            ... )
        """
        # Prepare parent reference
        if hasattr(parent, 'id'):
            parent_id = parent.id
        else:
            raise ValueError("Parent must be a Page or Block object")

        # Build synced block data
        block_data = {
            "type": "synced_block",
            "synced_block": {}
        }

        # Create block via API
        blocks = BlockCollection(client.api, parent_id=parent_id)
        

        # Return the created block
        result_data = await blocks.append(children=[block_data])
        return cls.from_data(client, result_data)

    def __repr__(self) -> str:
        """String representation."""
        return f"SyncedBlock(id={self.id!r})"
