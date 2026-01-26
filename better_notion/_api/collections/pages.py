"""Page collection."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from better_notion._api import NotionAPI

from better_notion._api.utils import AsyncPaginatedIterator


class PageCollection:
    """Collection for managing pages.

    Provides factory methods for creating and retrieving pages.
    """

    def __init__(self, api: NotionAPI) -> None:
        """Initialize the Page collection.

        Args:
            api: The NotionAPI client instance.
        """
        self._api = api

    async def get(self, page_id: str) -> dict[str, Any]:
        """Retrieve a page by ID.

        Args:
            page_id: The page ID.

        Returns:
            Raw page data dict from Notion API.

        Raises:
            NotFoundError: If the page does not exist.
        """
        return await self._api._request("GET", f"/pages/{page_id}")

    async def create(self, **kwargs: Any) -> dict[str, Any]:
        """Create a new page.

        Args:
            **kwargs: Page properties including parent (required).

        Returns:
            Raw page data dict from Notion API.

        Raises:
            ValidationError: If parent is not provided or invalid.
            BadRequestError: If the request is invalid.
        """
        return await self._api._request("POST", "/pages", json=kwargs)

    async def list(self, database_id: str, **kwargs: Any) -> list[dict[str, Any]]:
        """List pages in a database.

        Args:
            database_id: The database ID.
            **kwargs: Query parameters (filter, sorts, start_cursor, etc.).

        Returns:
            List of raw page data dicts from Notion API (first page only).

        Raises:
            NotFoundError: If the database does not exist.
            ValidationError: If the query parameters are invalid.
        """
        data = await self._api._request(
            "POST",
            f"/databases/{database_id}/query",
            json=kwargs,
        )
        return data.get("results", [])

    def iterate(self, database_id: str, **kwargs: Any) -> AsyncPaginatedIterator[dict[str, Any]]:
        """Iterate over all pages in a database with automatic pagination.

        Args:
            database_id: The database ID.
            **kwargs: Query parameters (filter, sorts, etc.).

        Returns:
            Async iterator that yields raw page data dicts from Notion API.

        Example:
            >>> async for page_data in api.pages.iterate("database_id"):
            ...     print(page_data["id"])

        Note:
            This method does not fetch pages immediately. Pages are fetched
            as you iterate, making it memory-efficient for large datasets.
        """
        async def fetch_fn(cursor: str | None) -> dict[str, Any]:
            query_params = kwargs.copy()
            if cursor:
                query_params["start_cursor"] = cursor
            return await self._api._request(
                "POST",
                f"/databases/{database_id}/query",
                json=query_params,
            )

        return AsyncPaginatedIterator(fetch_fn, lambda data: data)
