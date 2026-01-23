"""High-level Notion client with rich abstractions."""

from __future__ import annotations

from typing import Any


class NotionClient:
    """High-level Notion client with caching and rich abstractions.

    This provides a more developer-friendly interface than NotionAPI.

    Example:
        >>> client = NotionClient(token="secret_...")
        >>> page = await client.get_page("page_id")
    """

    def __init__(
        self,
        token: str,
        *,
        cache: bool = True,
    ) -> None:
        """Initialize the Notion client.

        Args:
            token: Notion API token.
            cache: Enable caching.
        """
        from better_notion._api import NotionAPI

        self._api = NotionAPI(auth=token)
        self._cache_enabled = cache

    async def __aenter__(self) -> NotionClient:
        """Async context manager entry."""
        return self

    async def __aexit__(self, *args: Any) -> None:
        """Async context manager exit."""
        await self.close()

    async def close(self) -> None:
        """Close the client and underlying connections."""
        await self._api.close()

    async def get_page(self, page_id: str) -> Any:
        """Get a page with rich abstractions.

        Args:
            page_id: The page identifier.

        Returns:
            Page object.
        """
        raise NotImplementedError("Not yet implemented")
