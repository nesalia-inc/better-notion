"""Block model with type-specific content access and navigation."""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Any, AsyncIterator

from better_notion._sdk.base.entity import BaseEntity

if TYPE_CHECKING:
    from better_notion._sdk.client import NotionClient


class Block(BaseEntity):
    """Generic Block model - base for all specialized blocks.

    This is the base class for all block types. Returns specialized
    instances based on block type (Code, Todo, Paragraph, etc.).

    Example:
        >>> # Get block (returns specialized instance)
        >>> block = await Block.get(block_id, client=client)
        >>>
        >>> # Type checking
        >>> if block.is_code:
        ...     print(block.code)  # Code-specific property
    """

    def __init__(self, client: "NotionClient", data: dict[str, Any]) -> None:
        """Initialize block with client and API response data.

        Args:
            client: NotionClient instance
            data: Block object from Notion API
        """
        # Initialize BaseEntity
        super().__init__(client, data)

        # Cache block type for frequent access
        self._block_type = self._data.get("type", "")

    # ===== CLASS METHODS (AUTONOMOUS ENTITY) =====

    @classmethod
    async def get(
        cls,
        block_id: str,
        *,
        client: "NotionClient"
    ) -> "Block":
        """Get block by ID.

        Args:
            block_id: Block UUID
            client: NotionClient instance

        Returns:
            Specialized block instance (Code, Todo, Paragraph, etc.)

        Example:
            >>> block = await Block.get(block_id, client=client)
        """
        # Fetch from API
        data = await client.api.blocks.retrieve(block_id=block_id)

        # Return specialized instance based on type
        return cls.from_data(client, data)

    @classmethod
    def from_data(
        cls,
        client: "NotionClient",
        data: dict[str, Any]
    ) -> "Block":
        """Create specialized block instance from API data.

        Args:
            client: NotionClient instance
            data: Raw API response data

        Returns:
            Specialized block instance (Code, Todo, etc.)

        Example:
            >>> block = Block.from_data(client, api_data)
        """
        from better_notion._sdk.models.blocks.audio import Audio
        from better_notion._sdk.models.blocks.bookmark import Bookmark
        from better_notion._sdk.models.blocks.breadcrumb import Breadcrumb
        from better_notion._sdk.models.blocks.bullet import Bullet
        from better_notion._sdk.models.blocks.callout import Callout
        from better_notion._sdk.models.blocks.code import Code
        from better_notion._sdk.models.blocks.column import Column
        from better_notion._sdk.models.blocks.column_list import ColumnList
        from better_notion._sdk.models.blocks.divider import Divider
        from better_notion._sdk.models.blocks.embed import Embed
        from better_notion._sdk.models.blocks.equation import Equation
        from better_notion._sdk.models.blocks.file import FileBlock
        from better_notion._sdk.models.blocks.heading import Heading
        from better_notion._sdk.models.blocks.image import Image
        from better_notion._sdk.models.blocks.numbered import Numbered
        from better_notion._sdk.models.blocks.paragraph import Paragraph
        from better_notion._sdk.models.blocks.pdf import PDF
        from better_notion._sdk.models.blocks.quote import Quote
        from better_notion._sdk.models.blocks.synced_block import SyncedBlock
        from better_notion._sdk.models.blocks.table import Table
        from better_notion._sdk.models.blocks.table_row import TableRow
        from better_notion._sdk.models.blocks.template import Template
        from better_notion._sdk.models.blocks.todo import Todo
        from better_notion._sdk.models.blocks.toggle import Toggle
        from better_notion._sdk.models.blocks.video import Video

        block_type = data.get("type", "")

        # Map to specialized class
        block_classes = {
            # Text blocks
            "paragraph": Paragraph,
            "heading_1": Heading,
            "heading_2": Heading,
            "heading_3": Heading,
            "code": Code,
            "quote": Quote,
            # List blocks
            "bulleted_list_item": Bullet,
            "numbered_list_item": Numbered,
            "to_do": Todo,
            "toggle": Toggle,
            # Media blocks
            "image": Image,
            "video": Video,
            "audio": Audio,
            "file": FileBlock,
            "pdf": PDF,
            # Embed blocks
            "bookmark": Bookmark,
            "embed": Embed,
            "equation": Equation,
            # Layout blocks
            "divider": Divider,
            "callout": Callout,
            "quote": Quote,
            "column_list": ColumnList,
            "column": Column,
            # Table blocks
            "table": Table,
            "table_row": TableRow,
            # Special blocks
            "breadcrumb": Breadcrumb,
            "synced_block": SyncedBlock,
            "template": Template,
        }

        block_class = block_classes.get(block_type, cls)
        return block_class(client, data)

    # ===== METADATA PROPERTIES =====

    @property
    def type(self) -> str:
        """Get block type.

        Returns:
            Block type string

        Example:
            >>> block.type
            'heading_1'
        """
        return self._block_type

    @property
    def has_children(self) -> bool:
        """Check if block has children.

        Returns:
            True if block has children blocks

        Example:
            >>> if block.has_children:
            ...     async for child in block.children:
            ...         print(child.type)
        """
        return self._data.get("has_children", False)

    @property
    def archived(self) -> bool:
        """Check if block is archived.

        Returns:
            True if block is archived
        """
        return self._data.get("archived", False)

    @property
    def created_by(self) -> str:
        """Get ID of user who created block.

        Returns:
            User ID

        Note:
            Use client.users.cache.get() to get User object
        """
        return self._data.get("created_by", "")

    @property
    def last_edited_by(self) -> str:
        """Get ID of user who last edited block.

        Returns:
            User ID
        """
        return self._data.get("last_edited_by", "")

    @property
    def created_time(self) -> datetime:
        """Get creation timestamp.

        Returns:
            Creation datetime
        """
        ts = self._data.get("created_time", "")
        return datetime.fromisoformat(ts.replace('Z', '+00:00'))

    @property
    def last_edited_time(self) -> datetime:
        """Get last edit timestamp.

        Returns:
            Last edit datetime
        """
        ts = self._data.get("last_edited_time", "")
        return datetime.fromisoformat(ts.replace('Z', '+00:00'))

    # ===== TYPE CHECKERS =====

    # Text blocks
    @property
    def is_paragraph(self) -> bool:
        """Check if block is a paragraph."""
        return self._block_type == "paragraph"

    @property
    def is_heading(self) -> bool:
        """Check if block is any heading (1, 2, or 3)."""
        return self._block_type in ("heading_1", "heading_2", "heading_3")

    @property
    def is_heading_1(self) -> bool:
        """Check if block is heading level 1."""
        return self._block_type == "heading_1"

    @property
    def is_heading_2(self) -> bool:
        """Check if block is heading level 2."""
        return self._block_type == "heading_2"

    @property
    def is_heading_3(self) -> bool:
        """Check if block is heading level 3."""
        return self._block_type == "heading_3"

    @property
    def is_code(self) -> bool:
        """Check if block is a code block."""
        return self._block_type == "code"

    @property
    def is_todo(self) -> bool:
        """Check if block is a to-do."""
        return self._block_type == "to_do"

    @property
    def is_bullet(self) -> bool:
        """Check if block is a bulleted list item."""
        return self._block_type == "bulleted_list_item"

    @property
    def is_numbered(self) -> bool:
        """Check if block is a numbered list item."""
        return self._block_type == "numbered_list_item"

    @property
    def is_quote(self) -> bool:
        """Check if block is a quote."""
        return self._block_type == "quote"

    @property
    def is_divider(self) -> bool:
        """Check if block is a divider."""
        return self._block_type == "divider"

    @property
    def is_callout(self) -> bool:
        """Check if block is a callout."""
        return self._block_type == "callout"

    # ===== GENERIC CONTENT PROPERTIES =====

    @property
    def text(self) -> str:
        """Get plain text content (for text-based blocks).

        Returns:
            Plain text content

        Note:
            Works for paragraph, heading, todo, quote, etc.
        """
        if not self._block_type:
            return ""

        content = self._data.get(self._block_type, {})
        if not isinstance(content, dict):
            return ""

        # Get text array from rich_text
        text_array = content.get("rich_text", [])
        if not text_array:
            return ""

        # Extract plain text from rich text array
        parts = []
        for text_obj in text_array:
            if text_obj.get("type") == "text":
                text_content = text_obj.get("text", {})
                parts.append(text_content.get("content", ""))

        return "".join(parts)

    # ===== NAVIGATION =====

    async def parent(self) -> "Page | Block | None":
        """Get parent object (fetches if not cached).

        Returns:
            Parent Page or Block object, or None

        Example:
            >>> parent = await block.parent()
            >>> if parent:
            ...     print(f"Parent type: {parent.type}")
        """
        # Check entity cache
        cached_parent = self._cache_get("parent")
        if cached_parent:
            return cached_parent

        # Fetch from API
        parent_data = self._data.get("parent", {})
        parent_type = parent_data.get("type")

        if parent_type == "page_id":
            page_id = parent_data["page_id"]
            # Check cache first
            if page_id in self._client.page_cache:
                return self._client.page_cache[page_id]
            # Fetch from API
            data = await self._client.api.pages.retrieve(page_id=page_id)
            from better_notion._sdk.models.page import Page
            parent = Page(self._client, data)

        elif parent_type == "block_id":
            block_id = parent_data["block_id"]
            # Fetch from API (returns specialized block)
            parent = await Block.get(block_id, client=self._client)

        elif parent_type == "workspace":
            parent = None

        else:
            parent = None

        # Cache result
        if parent:
            self._cache_set("parent", parent)

        return parent

    async def children(self) -> AsyncIterator["Block"]:
        """Iterate over child blocks.

        Yields:
            Block objects that are children

        Example:
            >>> async for child in block.children():
            ...     print(child.type)

        Note:
            Handles pagination automatically
        """
        from better_notion._api.utils.pagination import AsyncPaginatedIterator

        # Define fetch function
        async def fetch_fn(cursor: str | None) -> dict:
            params = {}
            if cursor:
                params["start_cursor"] = cursor

            return await self._client.api.blocks.children.list(
                block_id=self.id,
                **params
            )

        # Define item parser
        def item_parser(item_data: dict) -> Block:
            return Block.from_data(self._client, item_data)

        # Use paginated iterator
        iterator = AsyncPaginatedIterator(fetch_fn, item_parser)

        async for block in iterator:
            yield block

    # ===== CRUD OPERATIONS =====

    async def update(self, **kwargs: Any) -> "Block":
        """Update this block.

        Args:
            **kwargs: Block properties to update (varies by block type).
                For text blocks: paragraph, heading_1, heading_2, heading_3, etc.
                For code blocks: code (with language and rich_text)
                For todo blocks: to_do (with checked and rich_text)
                etc.

        Returns:
            Updated block object

        Example:
            >>> # Update paragraph text
            >>> await block.update(
            ...     paragraph={"rich_text": [{"type": "text", "text": {"content": "New text"}}]}
            ... )
            >>>
            >>> # Update todo checked state
            >>> await block.update(to_do={"checked": True, "rich_text": [...]})
        """
        from better_notion._api.properties import RichText

        # Call low-level API
        data = await self._client.api.blocks.update(block_id=self.id, **kwargs)

        # Update local data
        self._data = data

        # Clear cache
        self._cache_clear()

        # Return specialized instance
        return Block.from_data(self._client, data)

    async def delete(self) -> None:
        """Delete this block.

        Example:
            >>> await block.delete()
        """
        await self._client.api.blocks.delete(block_id=self.id)

    def __repr__(self) -> str:
        """String representation."""
        return f"Block(id={self.id!r}, type={self.type!r})"
