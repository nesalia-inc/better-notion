"""PDF block model."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from better_notion._sdk.models.block import Block

if TYPE_CHECKING:
    from better_notion._sdk.client import NotionClient
from better_notion._api.collections import BlockCollection


class PDF(Block):
    """PDF block (embedded or uploaded PDF).

    Example:
        >>> pdf = await PDF.create(
        ...     parent=page,
        ...     client=client,
        ...     url="https://example.com/document.pdf"
        ... )
    """

    def __init__(self, client: "NotionClient", data: dict[str, Any]) -> None:
        """Initialize a PDF block.

        Args:
            client: NotionClient instance
            data: Raw block data from Notion API
        """
        super().__init__(client, data)

    @property
    def url(self) -> str:
        """Get PDF URL.

        Returns:
            PDF URL (external or file URL)
        """
        pdf_data = self._data.get("pdf", {})
        pdf_type = pdf_data.get("type")

        if pdf_type == "external":
            return pdf_data.get("external", {}).get("url", "")
        elif pdf_type == "file":
            return pdf_data.get("file", {}).get("url", "")
        elif pdf_type == "secure":
            return pdf_data.get("secure", {}).get("url", "")

        return ""

    @classmethod
    async def create(
        cls,
        parent: "Page | Block",
        *,
        client: "NotionClient",
        url: str,
        **kwargs: Any
    ) -> "PDF":
        """Create a new PDF block.

        Args:
            parent: Parent page or block
            client: NotionClient instance
            url: PDF URL
            **kwargs: Additional parameters

        Returns:
            Newly created PDF block

        Example:
            >>> pdf = await PDF.create(
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

        # Build PDF data
        pdf_data = {
            "type": "external",
            "external": {"url": url}
        }

        # Build PDF block data
        block_data = {
            "type": "pdf",
            "pdf": pdf_data
        }

        # Create block via API
        blocks = BlockCollection(client.api, parent_id=parent_id)
        

        # Return the created block
        result_data = await blocks.append(children=[block_data])
        return cls.from_data(client, result_data)

    def __repr__(self) -> str:
        """String representation."""
        return f"PDF(url={self.url!r})"
