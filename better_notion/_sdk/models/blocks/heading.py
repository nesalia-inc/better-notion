"""Heading block model."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from better_notion._sdk.models.block import Block

if TYPE_CHECKING:
    from better_notion._sdk.client import NotionClient


class Heading(Block):
    """Heading block with level and text.

    Example:
        >>> h1 = await Heading.create(
        ...     parent=page,
        ...     client=client,
        ...     text="Introduction",
        ...     level=1
        ... )
    """

    def __init__(self, client: "NotionClient", data: dict[str, Any]) -> None:
        """Initialize a Heading block.

        Args:
            client: NotionClient instance
            data: Raw block data from Notion API
        """
        super().__init__(client, data)

    @property
    def level(self) -> int:
        """Get heading level.

        Returns:
            Heading level (1, 2, or 3)
        """
        if self._block_type == "heading_1":
            return 1
        elif self._block_type == "heading_2":
            return 2
        elif self._block_type == "heading_3":
            return 3
        return 1

    @classmethod
    async def create(
        cls,
        parent: "Page | Block",
        *,
        client: "NotionClient",
        text: str,
        level: int = 1,
        **kwargs: Any
    ) -> "Heading":
        """Create a new heading block.

        Args:
            parent: Parent page or block
            client: NotionClient instance
            text: Heading text
            level: Heading level (1, 2, or 3)
            **kwargs: Additional parameters

        Returns:
            Newly created Heading block

        Example:
            >>> h1 = await Heading.create(
            ...     parent=page,
            ...     client=client,
            ...     text="Introduction",
            ...     level=1
            ... )
        """
        from better_notion._api.properties import create_rich_text_array

        # Prepare parent reference
        if hasattr(parent, 'id'):
            parent_id = parent.id
            parent_type = "page_id" if parent.object == "page" else "block_id"
        else:
            raise ValueError("Parent must be a Page or Block object")

        # Validate level
        if level not in (1, 2, 3):
            raise ValueError("Level must be 1, 2, or 3")

        # Build heading data
        block_type = f"heading_{level}"
        block_data = {
            "type": block_type,
            block_type: {
                "rich_text": create_rich_text_array(text)
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
        return f"Heading(level={self.level}, text={text_preview!r})"
