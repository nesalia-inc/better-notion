"""Code block model."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from better_notion._sdk.models.block import Block

if TYPE_CHECKING:
    from better_notion._sdk.client import NotionClient


class Code(Block):
    """Code block with language and content.

    Example:
        >>> code = await Code.create(
        ...     parent=page,
        ...     client=client,
        ...     code="print('Hello, World!')",
        ...     language="python"
        ... )
    """

    def __init__(self, client: "NotionClient", data: dict[str, Any]) -> None:
        """Initialize a Code block.

        Args:
            client: NotionClient instance
            data: Raw block data from Notion API
        """
        super().__init__(client, data)

    @property
    def code(self) -> str:
        """Get code content.

        Returns:
            Code string
        """
        code_data = self._data.get("code", {})
        if not isinstance(code_data, dict):
            return ""

        # Extract plain text from rich_text array
        text_array = code_data.get("rich_text", [])
        parts = []
        for text_obj in text_array:
            if text_obj.get("type") == "text":
                text_content = text_obj.get("text", {})
                parts.append(text_content.get("content", ""))

        return "".join(parts)

    @property
    def language(self) -> str:
        """Get programming language.

        Returns:
            Language string (python, javascript, etc.)
        """
        code_data = self._data.get("code", {})
        if isinstance(code_data, dict):
            return code_data.get("language", "plain text")
        return "plain text"

    @classmethod
    async def create(
        cls,
        parent: "Page | Block",
        *,
        client: "NotionClient",
        code: str,
        language: str = "python",
        **kwargs: Any
    ) -> "Code":
        """Create a new code block.

        Args:
            parent: Parent page or block
            client: NotionClient instance
            code: Code content
            language: Programming language
            **kwargs: Additional parameters

        Returns:
            Newly created Code block

        Example:
            >>> code = await Code.create(
            ...     parent=page,
            ...     client=client,
            ...     code="print('Hello, World!')",
            ...     language="python"
            ... )
        """
        from better_notion._api.properties import RichText

        # Prepare parent reference
        if hasattr(parent, 'id'):
            parent_id = parent.id
        else:
            raise ValueError("Parent must be a Page or Block object")

        # Build code block data
        block_data = {
            "type": "code",
            "code": {
                "rich_text": [RichText[code]],
                "language": language
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
        code_preview = self.code[:30] if self.code else ""
        return f"Code(language={self.language!r}, code={code_preview!r})"
