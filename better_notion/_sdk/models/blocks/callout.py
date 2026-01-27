"""Callout block model."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from better_notion._sdk.models.block import Block

if TYPE_CHECKING:
    from better_notion._sdk.client import NotionClient


class Callout(Block):
    """Callout block with icon and text.

    Example:
        >>> callout = await Callout.create(
        ...     parent=page,
        ...     client=client,
        ...     text="Important note!",
        ...     icon="💡"
        ... )
    """

    def __init__(self, client: "NotionClient", data: dict[str, Any]) -> None:
        """Initialize a Callout block.

        Args:
            client: NotionClient instance
            data: Raw block data from Notion API
        """
        super().__init__(client, data)

    @property
    def icon(self) -> str | None:
        """Get callout icon.

        Returns:
            Emoji icon or None
        """
        callout_data = self._data.get("callout", {})
        if isinstance(callout_data, dict):
            icon_data = callout_data.get("icon")
            if icon_data and icon_data.get("type") == "emoji":
                return icon_data.get("emoji")
        return None

    @classmethod
    async def create(
        cls,
        parent: "Page | Block",
        *,
        client: "NotionClient",
        text: str,
        icon: str | None = None,
        **kwargs: Any
    ) -> "Callout":
        """Create a new callout block.

        Args:
            parent: Parent page or block
            client: NotionClient instance
            text: Callout text
            icon: Emoji icon (optional)
            **kwargs: Additional parameters

        Returns:
            Newly created Callout block

        Example:
            >>> callout = await Callout.create(
            ...     parent=page,
            ...     client=client,
            ...     text="Important note!",
            ...     icon="💡"
            ... )
        """
        from better_notion._api.properties import create_rich_text_array

        # Prepare parent reference
        if hasattr(parent, 'id'):
            parent_id = parent.id
        else:
            raise ValueError("Parent must be a Page or Block object")

        # Build callout data
        callout_data = {
            "rich_text": create_rich_text_array(text)
        }

        # Add icon if provided
        if icon:
            callout_data["icon"] = {"type": "emoji", "emoji": icon}

        # Build callout block data
        block_data = {
            "type": "callout",
            "callout": callout_data
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
        icon_str = f" icon={self.icon!r}" if self.icon else ""
        return f"Callout({text_preview!r}{icon_str})"
