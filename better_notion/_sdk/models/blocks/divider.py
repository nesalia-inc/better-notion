"""Divider block model."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from better_notion._sdk.models.block import Block

if TYPE_CHECKING:
    from better_notion._sdk.client import NotionClient
from better_notion._api.collections import BlockCollection


class Divider(Block):
    """Divider (horizontal rule) block.

    Example:
        >>> divider = await Divider.create(
        ...     parent=page,
        ...     client=client
        ... )
    """

    def __init__(self, client: "NotionClient", data: dict[str, Any]) -> None:
        """Initialize a Divider block.

        Args:
            client: NotionClient instance
            data: Raw block data from Notion API
        """
        super().__init__(client, data)

    @classmethod
    async def create(
        cls,
        parent: "Page | Block",
        *,
        client: "NotionClient",
        **kwargs: Any
    ) -> "Divider":
        """Create a new divider block.

        Args:
            parent: Parent page or block
            client: NotionClient instance
            **kwargs: Additional parameters

        Returns:
            Newly created Divider block

        Example:
            >>> divider = await Divider.create(
            ...     parent=page,
            ...     client=client
            ... )
        """
        # Prepare parent reference
        if hasattr(parent, 'id'):
            parent_id = parent.id
        else:
            raise ValueError("Parent must be a Page or Block object")

        # Build divider block data
        block_data = {
            "type": "divider",
            "divider": {}
        }

        # Create block via API
        blocks = BlockCollection(client.api, parent_id=parent_id)
        

        # Return the created block
        result_data = await blocks.append(children=[block_data])
        return cls.from_data(client, result_data)

    def __repr__(self) -> str:
        """String representation."""
        return f"Divider(id={self.id!r})"
