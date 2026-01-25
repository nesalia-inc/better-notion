"""Todo block model."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from better_notion._sdk.models.block import Block

if TYPE_CHECKING:
    from better_notion._sdk.client import NotionClient


class Todo(Block):
    """Todo (to-do) block with checked state.

    Example:
        >>> todo = await Todo.create(
        ...     parent=page,
        ...     client=client,
        ...     text="Review PR",
        ...     checked=False
        ... )
    """

    def __init__(self, client: "NotionClient", data: dict[str, Any]) -> None:
        """Initialize a Todo block.

        Args:
            client: NotionClient instance
            data: Raw block data from Notion API
        """
        super().__init__(client, data)

    @property
    def checked(self) -> bool:
        """Get checked state.

        Returns:
            True if todo is checked
        """
        todo_data = self._data.get("to_do", {})
        if isinstance(todo_data, dict):
            return todo_data.get("checked", False)
        return False

    async def set_checked(self, checked: bool) -> "Todo":
        """Set the checked state.

        Args:
            checked: New checked state

        Returns:
            Updated Todo block

        Example:
            >>> todo = await Todo.create(parent=page, client=client, text="Task")
            >>> await todo.set_checked(True)
        """
        from better_notion._api.properties import RichText

        # Get current rich text
        todo_data = self._data.get("to_do", {})
        rich_text = todo_data.get("rich_text", [])

        # Update via API
        updated = await self.update(to_do={
            "checked": checked,
            "rich_text": rich_text
        })

        return updated

    @classmethod
    async def create(
        cls,
        parent: "Page | Block",
        *,
        client: "NotionClient",
        text: str,
        checked: bool = False,
        **kwargs: Any
    ) -> "Todo":
        """Create a new todo block.

        Args:
            parent: Parent page or block
            client: NotionClient instance
            text: Todo text
            checked: Whether todo is checked
            **kwargs: Additional parameters

        Returns:
            Newly created Todo block

        Example:
            >>> todo = await Todo.create(
            ...     parent=page,
            ...     client=client,
            ...     text="Review PR",
            ...     checked=False
            ... )
        """
        from better_notion._api.properties import RichText

        # Prepare parent reference
        if hasattr(parent, 'id'):
            parent_id = parent.id
        else:
            raise ValueError("Parent must be a Page or Block object")

        # Build todo block data
        block_data = {
            "type": "to_do",
            "to_do": {
                "rich_text": [RichText[text]],
                "checked": checked
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
        return f"Todo(checked={self.checked}, text={text_preview!r})"
