"""Bullet list item block model."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from better_notion._sdk.models.block import Block

if TYPE_CHECKING:
    from better_notion._sdk.client import NotionClient


class Bullet(Block):
    """Bulleted list item block.

    Example:
        >>> item = await Bullet.create(
        ...     parent=page,
        ...     client=client,
        ...     text="First item"
        ... )
    """

    def __init__(self, client: "NotionClient", data: dict[str, Any]) -> None:
        """Initialize a Bullet block.

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
    ) -> "Bullet":
        """Create a new bullet list item block.

        Args:
            parent: Parent page or block
            client: NotionClient instance
            text: List item text
            **kwargs: Additional parameters

        Returns:
            Newly created Bullet block

        Example:
            >>> item = await Bullet.create(
            ...     parent=page,
            ...     client=client,
            ...     text="First item"
            ... )
        """
        from better_notion._api.properties import RichText

        # Prepare parent reference
        if hasattr(parent, 'id'):
            parent_id = parent.id
        else:
            raise ValueError("Parent must be a Page or Block object")

        # Build bullet block data
        block_data = {
            "type": "bulleted_list_item",
            "bulleted_list_item": {
                "rich_text": [RichText[text]]
            }
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
        text_preview = self.text[:30] if self.text else ""
        return f"Bullet(text={text_preview!r})"
