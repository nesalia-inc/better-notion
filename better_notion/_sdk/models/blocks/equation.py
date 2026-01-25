"""Equation block model."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from better_notion._sdk.models.block import Block

if TYPE_CHECKING:
    from better_notion._sdk.client import NotionClient


class Equation(Block):
    """Equation block (LaTeX math).

    Example:
        >>> equation = await Equation.create(
        ...     parent=page,
        ...     client=client,
        ...     expression="E = mc^2"
        ... )
    """

    def __init__(self, client: "NotionClient", data: dict[str, Any]) -> None:
        """Initialize an Equation block.

        Args:
            client: NotionClient instance
            data: Raw block data from Notion API
        """
        super().__init__(client, data)

    @property
    def expression(self) -> str:
        """Get equation expression (LaTeX).

        Returns:
            LaTeX expression string
        """
        equation_data = self._data.get("equation", {})
        return equation_data.get("expression", "")

    @classmethod
    async def create(
        cls,
        parent: "Page | Block",
        *,
        client: "NotionClient",
        expression: str,
        **kwargs: Any
    ) -> "Equation":
        """Create a new equation block.

        Args:
            parent: Parent page or block
            client: NotionClient instance
            expression: LaTeX equation expression
            **kwargs: Additional parameters

        Returns:
            Newly created Equation block

        Example:
            >>> equation = await Equation.create(
            ...     parent=page,
            ...     client=client,
            ...     expression="E = mc^2"
            ... )
        """
        # Prepare parent reference
        if hasattr(parent, 'id'):
            parent_id = parent.id
        else:
            raise ValueError("Parent must be a Page or Block object")

        # Build equation data
        equation_data = {
            "expression": expression
        }

        # Build equation block data
        block_data = {
            "type": "equation",
            "equation": equation_data
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
        expr_preview = self.expression[:20] if self.expression else ""
        return f"Equation({expr_preview!r})"
