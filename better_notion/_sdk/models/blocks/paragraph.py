"""Paragraph block model."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from better_notion._sdk.models.block import Block

if TYPE_CHECKING:
    from better_notion._sdk.client import NotionClient


class Paragraph(Block):
    """Paragraph block with text content.

    Example:
        >>> para = await Paragraph.create(
        ...     parent=page,
        ...     client=client,
        ...     text="This is a paragraph"
        ... )
    """

    def __init__(self, client: "NotionClient", data: dict[str, Any]) -> None:
        """Initialize a Paragraph block.

        Args:
            client: NotionClient instance
            data: Raw block data from Notion API
        """
        super().__init__(client, data)

    async def set_text(self, text: str) -> "Paragraph":
        """Set the paragraph text.

        Args:
            text: New text content

        Returns:
            Updated Paragraph block

        Example:
            >>> para = await Paragraph.create(parent=page, client=client, text="Old")
            >>> await para.set_text("New text")
        """
        from better_notion._api.properties import create_rich_text_array

        # Update via API
        updated = await self.update(paragraph={
            "rich_text": create_rich_text_array(text)
        })

        return updated

    @classmethod
    async def create(
        cls,
        parent: "Page | Block",
        *,
        client: "NotionClient",
        text: str,
        **kwargs: Any
    ) -> "Paragraph":
        """Create a new paragraph block.

        Args:
            parent: Parent page or block
            client: NotionClient instance
            text: Paragraph text
            **kwargs: Additional parameters

        Returns:
            Newly created Paragraph block

        Example:
            >>> para = await Paragraph.create(
            ...     parent=page,
            ...     client=client,
            ...     text="Hello, world!"
            ... )
        """
        from better_notion._api.properties import create_rich_text_array

        # Prepare parent reference
        if hasattr(parent, 'id'):
            parent_id = parent.id
            parent_type = "page_id" if parent.object == "page" else "block_id"
        else:
            raise ValueError("Parent must be a Page or Block object")

        # Build paragraph data
        block_data = {
            "type": "paragraph",
            "paragraph": {
                "rich_text": create_rich_text_array(text)
            }
        }

        # Create block via API
        from better_notion._api.collections import BlockCollection
        blocks = BlockCollection(client.api, parent_id=parent_id)
        result_data = await blocks.append(children=[block_data])

        # Return the created block
        return cls.from_data(client, result_data)

    def __repr__(self) -> str:
        """String representation."""
        text_preview = self.text[:30] if self.text else ""
        return f"Paragraph(id={self.id!r}, text={text_preview!r})"
