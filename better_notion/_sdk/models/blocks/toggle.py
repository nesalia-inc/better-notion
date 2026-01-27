"""Toggle block model (collapsible accordion)."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from better_notion._sdk.models.block import Block

if TYPE_CHECKING:
    from better_notion._sdk.client import NotionClient
from better_notion._api.collections import BlockCollection


class Toggle(Block):
    """Toggle block (collapsible accordion).

    Example:
        >>> toggle = await Toggle.create(
        ...     parent=page,
        ...     client=client,
        ...     text="Click to expand",
        ...     children=[paragraph_block]
        ... )
    """

    def __init__(self, client: "NotionClient", data: dict[str, Any]) -> None:
        """Initialize a Toggle block.

        Args:
            client: NotionClient instance
            data: Raw block data from Notion API
        """
        super().__init__(client, data)

    @property
    def is_open(self) -> bool:
        """Check if toggle is expanded.

        Returns:
            True if toggle is expanded
        """
        # Notion API doesn't provide toggle state in block data
        # This would need to be tracked separately if needed
        return False

    @classmethod
    async def create(
        cls,
        parent: "Page | Block",
        *,
        client: "NotionClient",
        text: str,
        **kwargs: Any
    ) -> "Toggle":
        """Create a new toggle block.

        Args:
            parent: Parent page or block
            client: NotionClient instance
            text: Toggle text
            **kwargs: Additional parameters

        Returns:
            Newly created Toggle block

        Example:
            >>> toggle = await Toggle.create(
            ...     parent=page,
            ...     client=client,
            ...     text="Click to expand"
            ... )
        """
        # Prepare parent reference
        if hasattr(parent, 'id'):
            parent_id = parent.id
        else:
            raise ValueError("Parent must be a Page or Block object")

        # Build toggle data
        toggle_data = {
            "rich_text": [
                {
                    "type": "text",
                    "text": {"content": text}
                }
            ]
        }

        # Build toggle block data
        block_data = {
            "type": "toggle",
            "toggle": toggle_data
        }

        # Create block via API
        blocks = BlockCollection(client.api, parent_id=parent_id)
        

        # Return the created block
        result_data = await blocks.append(children=[block_data])
        return cls.from_data(client, result_data)

    def __repr__(self) -> str:
        """String representation."""
        text_preview = self.text[:30] if self.text else ""
        return f"Toggle({text_preview!r})"
