"""Column block model."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from better_notion._sdk.models.block import Block

if TYPE_CHECKING:
    from better_notion._sdk.client import NotionClient


class Column(Block):
    """Column block (child of ColumnList).

    Example:
        >>> column = await Column.create(
        ...     parent=column_list,
        ...     client=client
        ... )
    """

    def __init__(self, client: "NotionClient", data: dict[str, Any]) -> None:
        """Initialize a Column block.

        Args:
            client: NotionClient instance
            data: Raw block data from Notion API
        """
        super().__init__(client, data)

    @property
    def column_ratio(self) -> float | None:
        """Get column width ratio.

        Returns:
            Column width ratio (0-1) or None
        """
        column_data = self._data.get("column", {})
        # Notion doesn't expose ratio in API data
        return None

    @classmethod
    async def create(
        cls,
        parent: "Block",
        *,
        client: "NotionClient",
        **kwargs: Any
    ) -> "Column":
        """Create a new column block.

        Args:
            parent: Parent ColumnList block
            client: NotionClient instance
            **kwargs: Additional parameters

        Returns:
            Newly created Column block

        Example:
            >>> column = await Column.create(
            ...     parent=column_list,
            ...     client=client
            ... )
        """
        # Prepare parent reference
        if hasattr(parent, 'id'):
            parent_id = parent.id
        else:
            raise ValueError("Parent must be a Block object")

        # Build column block data
        block_data = {
            "type": "column",
            "column": {}
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
        return f"Column(id={self.id!r})"
