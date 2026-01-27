"""Audio block model."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from better_notion._sdk.models.block import Block

if TYPE_CHECKING:
    from better_notion._sdk.client import NotionClient
from better_notion._api.collections import BlockCollection


class Audio(Block):
    """Audio block (embedded or uploaded audio).

    Example:
        >>> audio = await Audio.create(
        ...     parent=page,
        ...     client=client,
        ...     url="https://example.com/audio.mp3"
        ... )
    """

    def __init__(self, client: "NotionClient", data: dict[str, Any]) -> None:
        """Initialize an Audio block.

        Args:
            client: NotionClient instance
            data: Raw block data from Notion API
        """
        super().__init__(client, data)

    @property
    def url(self) -> str:
        """Get audio URL.

        Returns:
            Audio URL (external or file URL)
        """
        audio_data = self._data.get("audio", {})
        audio_type = audio_data.get("type")

        if audio_type == "external":
            return audio_data.get("external", {}).get("url", "")
        elif audio_type == "file":
            return audio_data.get("file", {}).get("url", "")
        elif audio_type == "secure":
            return audio_data.get("secure", {}).get("url", "")

        return ""

    @classmethod
    async def create(
        cls,
        parent: "Page | Block",
        *,
        client: "NotionClient",
        url: str,
        **kwargs: Any
    ) -> "Audio":
        """Create a new audio block.

        Args:
            parent: Parent page or block
            client: NotionClient instance
            url: Audio URL
            **kwargs: Additional parameters

        Returns:
            Newly created Audio block

        Example:
            >>> audio = await Audio.create(
            ...     parent=page,
            ...     client=client,
            ...     url="https://example.com/audio.mp3"
            ... )
        """
        # Prepare parent reference
        if hasattr(parent, 'id'):
            parent_id = parent.id
        else:
            raise ValueError("Parent must be a Page or Block object")

        # Build audio data
        audio_data = {
            "type": "external",
            "external": {"url": url}
        }

        # Build audio block data
        block_data = {
            "type": "audio",
            "audio": audio_data
        }

        # Create block via API
        blocks = BlockCollection(client.api, parent_id=parent_id)
        

        # Return the created block
        result_data = await blocks.append(children=[block_data])
        return cls.from_data(client, result_data)

    def __repr__(self) -> str:
        """String representation."""
        return f"Audio(url={self.url!r})"
