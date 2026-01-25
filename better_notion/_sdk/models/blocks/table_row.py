"""Table row block model."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from better_notion._sdk.models.block import Block

if TYPE_CHECKING:
    from better_notion._sdk.client import NotionClient


class TableRow(Block):
    """Table row block (child of Table).

    Example:
        >>> row = await TableRow.create(
        ...     parent=table_block,
        ...     client=client,
        ...     cells=["Task 1", "In Progress", "2024-01-01"]
        ... )
    """

    def __init__(self, client: "NotionClient", data: dict[str, Any]) -> None:
        """Initialize a TableRow block.

        Args:
            client: NotionClient instance
            data: Raw block data from Notion API
        """
        super().__init__(client, data)

    @property
    def cells(self) -> list[str]:
        """Get table row cells.

        Returns:
            List of cell text contents
        """
        row_data = self._data.get("table_row", {})
        cells_data = row_data.get("cells", [])

        # Extract text from each cell
        cell_texts = []
        for cell in cells_data:
            if cell and cell[0].get("type") == "text":
                cell_texts.append(cell[0]["text"].get("content", ""))
            else:
                cell_texts.append("")

        return cell_texts

    @classmethod
    async def create(
        cls,
        parent: "Block",
        *,
        client: "NotionClient",
        cells: list[str],
        **kwargs: Any
    ) -> "TableRow":
        """Create a new table row block.

        Args:
            parent: Parent Table block
            client: NotionClient instance
            cells: List of cell contents
            **kwargs: Additional parameters

        Returns:
            Newly created TableRow block

        Example:
            >>> row = await TableRow.create(
            ...     parent=table,
            ...     client=client,
            ...     cells=["Task 1", "In Progress", "2024-01-01"]
            ... )
        """
        from better_notion._api.properties import RichText

        # Prepare parent reference
        if hasattr(parent, 'id'):
            parent_id = parent.id
        else:
            raise ValueError("Parent must be a Block object")

        # Build cells
        cells_array = []
        for cell_text in cells:
            cells_array.append([{"type": "text", "text": {"content": cell_text}}])

        # Build table row data
        row_data = {
            "cells": cells_array
        }

        # Build table row block data
        block_data = {
            "type": "table_row",
            "table_row": row_data
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
        cells_preview = self.cells[:3] if self.cells else []
        return f"TableRow(cells={cells_preview!r})"
