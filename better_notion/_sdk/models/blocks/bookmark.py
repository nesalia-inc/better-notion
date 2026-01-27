"""Bookmark block model."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from better_notion._sdk.models.block import Block

if TYPE_CHECKING:
    from better_notion._sdk.client import NotionClient


class Bookmark(Block):
    """Bookmark block (saved URL with preview).

    Example:
        >>> bookmark = await Bookmark.create(
        ...     parent=page,
        ...     client=client,
        ...     url="https://example.com"
        ... )
    """

    def __init__(self, client: "NotionClient", data: dict[str, Any]) -> None:
        """Initialize a Bookmark block.

        Args:
            client: NotionClient instance
            data: Raw block data from Notion API
        """
        super().__init__(client, data)

    @property
    def url(self) -> str:
        """Get bookmark URL.

        Returns:
            Bookmark URL
        """
        bookmark_data = self._data.get("bookmark", {})
        return bookmark_data.get("url", "")

    @property
    def caption(self) -> str:
        """Get bookmark caption.

        Returns:
            Bookmark caption text
        """
        bookmark_data = self._data.get("bookmark", {})
        caption_array = bookmark_data.get("caption", [])
        if caption_array and caption_array[0].get("type") == "text":
            return caption_array[0]["text"].get("content", "")
        return ""

    @classmethod
    async def create(
        cls,
        parent: "Page | Block",
        *,
        client: "NotionClient",
        url: str,
        caption: str | None = None,
        **kwargs: Any
    ) -> "Bookmark":
        """Create a new bookmark block.

        Args:
            parent: Parent page or block
            client: NotionClient instance
            url: Bookmark URL
            caption: Optional caption text
            **kwargs: Additional parameters

        Returns:
            Newly created Bookmark block

        Example:
            >>> bookmark = await Bookmark.create(
            ...     parent=page,
            ...     client=client,
            ...     url="https://example.com",
            ...     caption="My bookmark"
            ... )
        """
        from better_notion._api.properties import create_rich_text_array

        # Prepare parent reference
        if hasattr(parent, 'id'):
            parent_id = parent.id
        else:
            raise ValueError("Parent must be a Page or Block object")

        # Build bookmark data
        bookmark_data = {
            "url": url
        }

        # Add caption if provided
        if caption:
            bookmark_data["caption"] = create_rich_text_array(caption)

        # Build bookmark block data
        block_data = {
            "type": "bookmark",
            "bookmark": bookmark_data
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
        return f"Bookmark(url={self.url!r})"
