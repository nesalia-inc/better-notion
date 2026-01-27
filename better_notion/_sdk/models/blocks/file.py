"""File block model."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from better_notion._sdk.models.block import Block

if TYPE_CHECKING:
    from better_notion._sdk.client import NotionClient
from better_notion._api.collections import BlockCollection


class FileBlock(Block):
    """File block (embedded or uploaded file).

    Example:
        >>> file_block = await FileBlock.create(
        ...     parent=page,
        ...     client=client,
        ...     url="https://example.com/document.pdf"
        ... )
    """

    def __init__(self, client: "NotionClient", data: dict[str, Any]) -> None:
        """Initialize a File block.

        Args:
            client: NotionClient instance
            data: Raw block data from Notion API
        """
        super().__init__(client, data)

    @property
    def url(self) -> str:
        """Get file URL.

        Returns:
            File URL (external or file URL)
        """
        file_data = self._data.get("file", {})
        file_type = file_data.get("type")

        if file_type == "external":
            return file_data.get("external", {}).get("url", "")
        elif file_type == "file":
            return file_data.get("file", {}).get("url", "")
        elif file_type == "secure":
            return file_data.get("secure", {}).get("url", "")

        return ""

    @classmethod
    async def create(
        cls,
        parent: "Page | Block",
        *,
        client: "NotionClient",
        url: str,
        **kwargs: Any
    ) -> "FileBlock":
        """Create a new file block.

        Args:
            parent: Parent page or block
            client: NotionClient instance
            url: File URL
            **kwargs: Additional parameters

        Returns:
            Newly created File block

        Example:
            >>> file_block = await FileBlock.create(
            ...     parent=page,
            ...     client=client,
            ...     url="https://example.com/document.pdf"
            ... )
        """
        # Prepare parent reference
        if hasattr(parent, 'id'):
            parent_id = parent.id
        else:
            raise ValueError("Parent must be a Page or Block object")

        # Build file data
        file_data = {
            "type": "external",
            "external": {"url": url}
        }

        # Build file block data
        block_data = {
            "type": "file",
            "file": file_data
        }

        # Create block via API
        blocks = BlockCollection(client.api, parent_id=parent_id)
        

        # Return the created block
        result_data = await blocks.append(children=[block_data])
        return cls.from_data(client, result_data)

    def __repr__(self) -> str:
        """String representation."""
        return f"FileBlock(url={self.url!r})"
