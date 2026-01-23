"""Search API endpoint."""

from __future__ import annotations

from typing import Any


class SearchEndpoint:
    """Search API endpoint.

    Provides methods for searching across Notion.
    """

    def __init__(self, api: Any) -> None:
        """Initialize the Search endpoint.

        Args:
            api: The NotionAPI client instance.
        """
        self._api = api

    async def search(self, **kwargs: Any) -> dict[str, Any]:
        """Search across all pages and databases.

        Args:
            **kwargs: Search parameters (query, filter, etc.).

        Returns:
            The search results.
        """
        raise NotImplementedError("Not yet implemented")
