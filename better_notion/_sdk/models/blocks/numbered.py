"""Numbered list item block model."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from better_notion._sdk.models.block import Block

if TYPE_CHECKING:
    from better_notion._sdk.client import NotionClient


class Numbered(Block):
    """Numbered list item block.

    Example:
        >>> item = await Numbered.create(
        ...     parent=page,
        ...     client=client,
        ...     text="First item"
        ... )
    """

    def __init__(self, client: "NotionClient", data: dict[str, Any]) -> None:
        """Initialize a Numbered block.

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
        text: str,
        **kwargs: Any
    ) -> "Numbered":
        """Create a new numbered list item block.

        Args:
            parent: Parent page or block
            client: NotionClient instance
            text: List item text
            **kwargs: Additional parameters

        Returns:
            Newly created Numbered block

        Example:
            >>> item = await Numbered.create(
            ...     parent=page,
            ...     client=client,
            ...     text="First item"
            ... )
        """
        from better_notion._api.properties import create_rich_text_array
        from better_notion._api.collections import BlockCollection

        # Prepare parent reference
        if hasattr(parent, 'id'):
            parent_id = parent.id
        else:
            raise ValueError("Parent must be a Page or Block object")

        # Build numbered block data
        block_data = {
            "type": "numbered_list_item",
            "numbered_list_item": {
                "rich_text": create_rich_text_array(text)
            }
        }

        # Create block via API
        blocks = BlockCollection(client.api, parent_id=parent_id)
        

        # Return the created block
        result_data = await blocks.append(children=[block_data])
        return cls.from_data(client, result_data)

    def __repr__(self) -> str:
        """String representation."""
        text_preview = self.text[:30] if self.text else ""
        return f"Numbered(text={text_preview!r})"
