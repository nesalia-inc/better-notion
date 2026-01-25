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
        from better_notion._api.properties import RichText

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
        return f"Paragraph(id={self.id!r}, text={text_preview!r})"
