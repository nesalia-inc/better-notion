"""Block manager for block operations."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from better_notion._sdk.client import NotionClient
    from better_notion._sdk.models.block import Block
    from better_notion._sdk.models.page import Page


class BlockManager:
    """Ultra-thin wrapper to autonomous block classes.

    All methods delegate to specialized block classes.
    The manager only stores and passes the client reference.

    Example:
        >>> # Via manager (recommended)
        >>> block = await client.blocks.get(block_id)
        >>> code = await client.blocks.create_code(page, code="print('hi')")
        >>>
        >>> # Via entity directly (autonomous)
        >>> block = await Block.get(block_id, client=client)
        >>> code = await Code.create(parent=page, code="...", client=client)
    """

    def __init__(self, client: "NotionClient") -> None:
        """Initialize block manager.

        Args:
            client: NotionClient instance
        """
        self._client = client

    # ===== GENERIC OPERATIONS =====

    async def get(self, block_id: str) -> "Block":
        """Get block by ID (returns specialized instance).

        Args:
            block_id: Block UUID

        Returns:
            Specialized block object (Code, Todo, Paragraph, etc.)

        Raises:
            BlockNotFound: If block doesn't exist

        Example:
            >>> block = await client.blocks.get(block_id)
            >>> if block.type == "code":
            ...     print(block.code)  # Type-specific access
        """
        from better_notion._sdk.models.block import Block

        return await Block.get(block_id, client=self._client)

    async def delete(self, block: "Block") -> None:
        """Delete a block.

        Args:
            block: Block object to delete

        Example:
            >>> block = await client.blocks.get(block_id)
            >>> await client.blocks.delete(block)
        """
        await block.delete(client=self._client)

    # ===== CODE BLOCKS =====

    async def create_code(
        self,
        parent: "Page | Block",
        code: str,
        language: str = "python",
        **kwargs
    ) -> "Code":
        """Create a code block.

        Args:
            parent: Parent page or block
            code: Code content
            language: Programming language (python, javascript, etc.)
            **kwargs: Additional properties

        Returns:
            Code block object

        Example:
            >>> code = await client.blocks.create_code(
            ...     parent=page,
            ...     code="print('Hello, World!')",
            ...     language="python"
            ... )
        """
        from better_notion._sdk.models.blocks.code import Code

        return await Code.create(
            parent=parent,
            code=code,
            language=language,
            client=self._client,
            **kwargs
        )

    # ===== TODO BLOCKS =====

    async def create_todo(
        self,
        parent: "Page | Block",
        text: str,
        checked: bool = False,
        **kwargs
    ) -> "Todo":
        """Create a to-do block.

        Args:
            parent: Parent page or block
            text: Todo text
            checked: Whether todo is checked
            **kwargs: Additional properties

        Returns:
            Todo block object

        Example:
            >>> todo = await client.blocks.create_todo(
            ...     parent=page,
            ...     text="Review PR",
            ...     checked=False
            ... )
        """
        from better_notion._sdk.models.blocks.todo import Todo

        return await Todo.create(
            parent=parent,
            text=text,
            checked=checked,
            client=self._client,
            **kwargs
        )

    # ===== PARAGRAPH BLOCKS =====

    async def create_paragraph(
        self,
        parent: "Page | Block",
        text: str,
        **kwargs
    ) -> "Paragraph":
        """Create a paragraph block.

        Args:
            parent: Parent page or block
            text: Paragraph text
            **kwargs: Additional properties

        Returns:
            Paragraph block object

        Example:
            >>> para = await client.blocks.create_paragraph(
            ...     parent=page,
            ...     text="This is a paragraph."
            ... )
        """
        from better_notion._sdk.models.blocks.paragraph import Paragraph

        return await Paragraph.create(
            parent=parent,
            text=text,
            client=self._client,
            **kwargs
        )

    # ===== HEADING BLOCKS =====

    async def create_heading(
        self,
        parent: "Page | Block",
        text: str,
        level: int = 1,
        **kwargs
    ) -> "Heading":
        """Create a heading block.

        Args:
            parent: Parent page or block
            text: Heading text
            level: Heading level (1, 2, or 3)
            **kwargs: Additional properties

        Returns:
            Heading block object

        Example:
            >>> h1 = await client.blocks.create_heading(
            ...     parent=page,
            ...     text="Introduction",
            ...     level=1
            ... )
        """
        from better_notion._sdk.models.blocks.heading import Heading

        return await Heading.create(
            parent=parent,
            text=text,
            level=level,
            client=self._client,
            **kwargs
        )

    # ===== BULLET LIST BLOCKS =====

    async def create_bullet(
        self,
        parent: "Page | Block",
        text: str,
        **kwargs
    ) -> "Bullet":
        """Create a bulleted list item block.

        Args:
            parent: Parent page or block
            text: List item text
            **kwargs: Additional properties

        Returns:
            Bullet block object

        Example:
            >>> item = await client.blocks.create_bullet(
            ...     parent=page,
            ...     text="First item"
            ... )
        """
        from better_notion._sdk.models.blocks.bullet import Bullet

        return await Bullet.create(
            parent=parent,
            text=text,
            client=self._client,
            **kwargs
        )

    # ===== NUMBERED LIST BLOCKS =====

    async def create_numbered(
        self,
        parent: "Page | Block",
        text: str,
        **kwargs
    ) -> "Numbered":
        """Create a numbered list item block.

        Args:
            parent: Parent page or block
            text: List item text
            **kwargs: Additional properties

        Returns:
            Numbered block object

        Example:
            >>> item = await client.blocks.create_numbered(
            ...     parent=page,
            ...     text="First item"
            ... )
        """
        from better_notion._sdk.models.blocks.numbered import Numbered

        return await Numbered.create(
            parent=parent,
            text=text,
            client=self._client,
            **kwargs
        )

    # ===== QUOTE BLOCKS =====

    async def create_quote(
        self,
        parent: "Page | Block",
        text: str,
        **kwargs
    ) -> "Quote":
        """Create a quote block.

        Args:
            parent: Parent page or block
            text: Quote text
            **kwargs: Additional properties

        Returns:
            Quote block object

        Example:
            >>> quote = await client.blocks.create_quote(
            ...     parent=page,
            ...     text="Code is poetry."
            ... )
        """
        from better_notion._sdk.models.blocks.quote import Quote

        return await Quote.create(
            parent=parent,
            text=text,
            client=self._client,
            **kwargs
        )

    # ===== DIVIDER BLOCKS =====

    async def create_divider(
        self,
        parent: "Page | Block",
        **kwargs
    ) -> "Divider":
        """Create a divider block.

        Args:
            parent: Parent page or block
            **kwargs: Additional properties

        Returns:
            Divider block object

        Example:
            >>> divider = await client.blocks.create_divider(parent=page)
        """
        from better_notion._sdk.models.blocks.divider import Divider

        return await Divider.create(
            parent=parent,
            client=self._client,
            **kwargs
        )

    # ===== CALLOUT BLOCKS =====

    async def create_callout(
        self,
        parent: "Page | Block",
        text: str,
        icon: str | None = None,
        **kwargs
    ) -> "Callout":
        """Create a callout block.

        Args:
            parent: Parent page or block
            text: Callout text
            icon: Emoji icon (optional)
            **kwargs: Additional properties

        Returns:
            Callout block object

        Example:
            >>> callout = await client.blocks.create_callout(
            ...     parent=page,
            ...     text="Important note!",
            ...     icon="💡"
            ... )
        """
        from better_notion._sdk.models.blocks.callout import Callout

        return await Callout.create(
            parent=parent,
            text=text,
            icon=icon,
            client=self._client,
            **kwargs
        )
