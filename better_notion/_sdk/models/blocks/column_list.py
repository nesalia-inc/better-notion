"""Column list block model."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from better_notion._sdk.models.block import Block

if TYPE_CHECKING:
    from better_notion._sdk.client import NotionClient


class ColumnList(Block):
    """Column list block (container for columns).

    Example:
        >>> column_list = await ColumnList.create(
        ...     parent=page,
        ...     client=client
        ... )
    """

    def __init__(self, client: "NotionClient", data: dict[str, Any]) -> None:
        """Initialize a ColumnList block.

        Args:
            client: NotionClient instance
            data: Raw block data from Notion API
        """
        super().__init__(client, data)

    @property
    def column_count(self) -> int:
        """Get number of columns.

        Returns:
            Number of child column blocks
        """
        # This would require counting children blocks
        # For now, we can't determine without fetching children
        return 0

    @classmethod
    async def create(
        cls,
        parent: "Page | Block",
        *,
        client: "NotionClient",
        **kwargs: Any
    ) -> "ColumnList":
        """Create a new column list block.

        Args:
            parent: Parent page or block
            client: NotionClient instance
            **kwargs: Additional parameters

        Returns:
            Newly created ColumnList block

        Example:
            >>> column_list = await ColumnList.create(
            ...     parent=page,
            ...     client=client
            ... )
        """
        # Prepare parent reference
        if hasattr(parent, 'id'):
            parent_id = parent.id
        else:
            raise ValueError("Parent must be a Page or Block object")

        # Build column list block data
        block_data = {
            "type": "column_list",
            "column_list": {}
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
        return f"ColumnList(id={self.id!r})"
