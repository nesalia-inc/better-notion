"""Breadcrumb block model."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from better_notion._sdk.models.block import Block

if TYPE_CHECKING:
    from better_notion._sdk.client import NotionClient


class Breadcrumb(Block):
    """Breadcrumb block (shows page hierarchy).

    Example:
        >>> breadcrumb = await Breadcrumb.create(
        ...     parent=page,
        ...     client=client
        ... )
    """

    def __init__(self, client: "NotionClient", data: dict[str, Any]) -> None:
        """Initialize a Breadcrumb block.

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
    ) -> "Breadcrumb":
        """Create a new breadcrumb block.

        Args:
            parent: Parent page or block
            client: NotionClient instance
            **kwargs: Additional parameters

        Returns:
            Newly created Breadcrumb block

        Example:
            >>> breadcrumb = await Breadcrumb.create(
            ...     parent=page,
            ...     client=client
            ... )
        """
        # Prepare parent reference
        if hasattr(parent, 'id'):
            parent_id = parent.id
        else:
            raise ValueError("Parent must be a Page or Block object")

        # Build breadcrumb block data
        block_data = {
            "type": "breadcrumb",
            "breadcrumb": {}
        }

        # Create block via API
        data = await client.api.blocks.children.append(
            block_id=parent_id,
            children=[block_data]
        )

        # Return first created block
        result_data = data.get("results", [{}])[0]
        return cls.from_data(client, result_data)

    def __repr__(self) -> str:
        """String representation."""
        return f"Breadcrumb(id={self.id!r})"
