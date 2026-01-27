"""Video block model."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from better_notion._sdk.models.block import Block

if TYPE_CHECKING:
    from better_notion._sdk.client import NotionClient


class Video(Block):
    """Video block (embedded or uploaded video).

    Example:
        >>> video = await Video.create(
        ...     parent=page,
        ...     client=client,
        ...     url="https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        ... )
    """

    def __init__(self, client: "NotionClient", data: dict[str, Any]) -> None:
        """Initialize a Video block.

        Args:
            client: NotionClient instance
            data: Raw block data from Notion API
        """
        super().__init__(client, data)

    @property
    def url(self) -> str:
        """Get video URL.

        Returns:
            Video URL (external or file URL)
        """
        video_data = self._data.get("video", {})
        video_type = video_data.get("type")

        if video_type == "external":
            return video_data.get("external", {}).get("url", "")
        elif video_type == "file":
            return video_data.get("file", {}).get("url", "")
        elif video_type == "secure":
            return video_data.get("secure", {}).get("url", "")

        return ""

    @property
    def caption(self) -> str:
        """Get video caption.

        Returns:
            Video caption text
        """
        video_data = self._data.get("video", {})
        caption_array = video_data.get("caption", [])
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
    ) -> "Video":
        """Create a new video block.

        Args:
            parent: Parent page or block
            client: NotionClient instance
            url: Video URL
            caption: Optional caption text
            **kwargs: Additional parameters

        Returns:
            Newly created Video block

        Example:
            >>> video = await Video.create(
            ...     parent=page,
            ...     client=client,
            ...     url="https://www.youtube.com/watch?v=dQw4w9WgXcQ"
            ... )
        """
        from better_notion._api.properties import create_rich_text_array
        from better_notion._api.collections import BlockCollection

        # Prepare parent reference
        if hasattr(parent, 'id'):
            parent_id = parent.id
        else:
            raise ValueError("Parent must be a Page or Block object")

        # Build video data
        video_data = {
            "type": "external",
            "external": {"url": url}
        }

        # Add caption if provided
        if caption:
            video_data["caption"] = create_rich_text_array(caption)

        # Build video block data
        block_data = {
            "type": "video",
            "video": video_data
        }

        # Create block via API
        blocks = BlockCollection(client.api, parent_id=parent_id)
        

        # Return the created block
        result_data = await blocks.append(children=[block_data])
        return cls.from_data(client, result_data)

    def __repr__(self) -> str:
        """String representation."""
        return f"Video(url={self.url!r})"
