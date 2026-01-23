"""High-level Notion client with caching."""

from __future__ import annotations

from typing import Any

from better_notion._api import NotionAPI


class NotionClient(NotionAPI):
    """High-level Notion client with caching and rich abstractions.

    This is an alias for NotionAPI with future support for caching
    and additional high-level features.

    Example:
        >>> client = NotionClient(token="secret_...")
        >>> page = await client.pages.get("page_id")
        >>> print(page.title)
        >>> await page.delete()
    """

    def __init__(
        self,
        token: str,
        *,
        cache: bool = True,
        **kwargs: Any,
    ) -> None:
        """Initialize the Notion client.

        Args:
            token: Notion API token.
            cache: Enable caching (future feature).
            **kwargs: Additional arguments passed to NotionAPI.
        """
        super().__init__(auth=token, **kwargs)
        self._cache_enabled = cache
