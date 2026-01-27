"""Embed block model."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from better_notion._sdk.models.block import Block

if TYPE_CHECKING:
    from better_notion._sdk.client import NotionClient
from better_notion._api.collections import BlockCollection


class Embed(Block):
    """Embed block (embedded content from external sources).

    Example:
        >>> embed = await Embed.create(
        ...     parent=page,
        ...     client=client,
        ...     url="https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        ... )
    """

    def __init__(self, client: "NotionClient", data: dict[str, Any]) -> None:
        """Initialize an Embed block.

        Args:
            client: NotionClient instance
            data: Raw block data from Notion API
        """
        super().__init__(client, data)

    @property
    def url(self) -> str:
        """Get embed URL.

        Returns:
            Embed URL
        """
        embed_data = self._data.get("embed", {})
        return embed_data.get("url", "")

    @classmethod
    async def create(
        cls,
        parent: "Page | Block",
        *,
        client: "NotionClient",
        url: str,
        **kwargs: Any
    ) -> "Embed":
        """Create a new embed block.

        Args:
            parent: Parent page or block
            client: NotionClient instance
            url: Embed URL
            **kwargs: Additional parameters

        Returns:
            Newly created Embed block

        Example:
            >>> embed = await Embed.create(
            ...     parent=page,
            ...     client=client,
            ...     url="https://www.youtube.com/watch?v=dQw4w9WgXcQ"
            ... )
        """
        # Prepare parent reference
        if hasattr(parent, 'id'):
            parent_id = parent.id
        else:
            raise ValueError("Parent must be a Page or Block object")

        # Build embed data
        embed_data = {
            "url": url
        }

        # Build embed block data
        block_data = {
            "type": "embed",
            "embed": embed_data
        }

        # Create block via API
        blocks = BlockCollection(client.api, parent_id=parent_id)
        

        # Return the created block
        result_data = await blocks.append(children=[block_data])
        return cls.from_data(client, result_data)

    def __repr__(self) -> str:
        """String representation."""
        return f"Embed(url={self.url!r})"
