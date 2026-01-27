"""Table block model."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from better_notion._sdk.models.block import Block

if TYPE_CHECKING:
    from better_notion._sdk.client import NotionClient
from better_notion._api.collections import BlockCollection


class Table(Block):
    """Table block for structured data.

    Example:
        >>> table = await Table.create(
        ...     parent=page,
        ...     client=client,
        ...     columns=["Name", "Status", "Due Date"]
        ... )
    """

    def __init__(self, client: "NotionClient", data: dict[str, Any]) -> None:
        """Initialize a Table block.

        Args:
            client: NotionClient instance
            data: Raw block data from Notion API
        """
        super().__init__(client, data)

    @property
    def table_width(self) -> int:
        """Get table width (number of columns).

        Returns:
            Number of columns in table
        """
        table_data = self._data.get("table", {})
        return table_data.get("table_width", 0)

    @property
    def has_column_header(self) -> bool:
        """Check if table has column header.

        Returns:
            True if table has column header
        """
        table_data = self._data.get("table", {})
        return table_data.get("has_column_header", False)

    @property
    def has_row_header(self) -> bool:
        """Check if table has row header.

        Returns:
            True if table has row header
        """
        table_data = self._data.get("table", {})
        return table_data.get("has_row_header", False)

    @classmethod
    async def create(
        cls,
        parent: "Page | Block",
        *,
        client: "NotionClient",
        columns: int | list[str] = 3,
        has_column_header: bool = False,
        has_row_header: bool = False,
        **kwargs: Any
    ) -> "Table":
        """Create a new table block.

        Args:
            parent: Parent page or block
            client: NotionClient instance
            columns: Number of columns or list of column names
            has_column_header: Whether table has column header
            has_row_header: Whether table has row header
            **kwargs: Additional parameters

        Returns:
            Newly created Table block

        Example:
            >>> table = await Table.create(
            ...     parent=page,
            ...     client=client,
            ...     columns=["Name", "Status", "Due Date"],
            ...     has_column_header=True
            ... )
        """
        # Prepare parent reference
        if hasattr(parent, 'id'):
            parent_id = parent.id
        else:
            raise ValueError("Parent must be a Page or Block object")

        # Handle column count
        if isinstance(columns, list):
            column_count = len(columns)
        else:
            column_count = columns

        # Build table data
        table_data = {
            "table_width": column_count,
            "has_column_header": has_column_header,
            "has_row_header": has_row_header
        }

        # Build table block data
        block_data = {
            "type": "table",
            "table": table_data
        }

        # Create block via API
        blocks = BlockCollection(client.api, parent_id=parent_id)
        

        # Return the created block
        result_data = await blocks.append(children=[block_data])
        return cls.from_data(client, result_data)

    def __repr__(self) -> str:
        """String representation."""
        return f"Table(width={self.table_width}, columns={self.has_column_header})"
