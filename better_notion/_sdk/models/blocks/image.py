"""Image block model."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from better_notion._sdk.models.block import Block

if TYPE_CHECKING:
    from better_notion._sdk.client import NotionClient


class Image(Block):
    """Image block (embedded or uploaded image).

    Example:
        >>> image = await Image.create(
        ...     parent=page,
        ...     client=client,
        ...     url="https://example.com/image.png"
        ... )
    """

    def __init__(self, client: "NotionClient", data: dict[str, Any]) -> None:
        """Initialize an Image block.

        Args:
            client: NotionClient instance
            data: Raw block data from Notion API
        """
        super().__init__(client, data)

    @property
    def url(self) -> str:
        """Get image URL.

        Returns:
            Image URL (external or file URL)
        """
        image_data = self._data.get("image", {})
        image_type = image_data.get("type")

        if image_type == "external":
            return image_data.get("external", {}).get("url", "")
        elif image_type == "file":
            return image_data.get("file", {}).get("url", "")
        elif image_type == "secure":
            return image_data.get("secure", {}).get("url", "")

        return ""

    @property
    def caption(self) -> str:
        """Get image caption.

        Returns:
            Image caption text
        """
        image_data = self._data.get("image", {})
        caption_array = image_data.get("caption", [])
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
    ) -> "Image":
        """Create a new image block.

        Args:
            parent: Parent page or block
            client: NotionClient instance
            url: Image URL
            caption: Optional caption text
            **kwargs: Additional parameters

        Returns:
            Newly created Image block

        Example:
            >>> image = await Image.create(
            ...     parent=page,
            ...     client=client,
            ...     url="https://example.com/image.png",
            ...     caption="My image"
            ... )
        """
        from better_notion._api.properties import create_rich_text_array

        # Prepare parent reference
        if hasattr(parent, 'id'):
            parent_id = parent.id
        else:
            raise ValueError("Parent must be a Page or Block object")

        # Build image data
        image_data = {
            "type": "external",
            "external": {"url": url}
        }

        # Add caption if provided
        if caption:
            image_data["caption"] = create_rich_text_array(caption)

        # Build image block data
        block_data = {
            "type": "image",
            "image": image_data
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
        return f"Image(url={self.url!r})"
