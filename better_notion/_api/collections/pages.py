"""Page collection."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from better_notion._api import NotionAPI

from better_notion._api.collections.base import EntityCollection
from better_notion._api.entities import Page
from better_notion._api.utils import AsyncPaginatedIterator


class PageCollection(EntityCollection[Page]):
    """Collection for managing pages.

    Provides factory methods for creating and retrieving pages as Entity objects.
    """

    def __init__(self, api: NotionAPI) -> None:
        """Initialize the Page collection.

        Args:
            api: The NotionAPI client instance.
        """
        super().__init__(api)

    @property
    def _entity_class(self) -> type[Page]:
        """The Page entity class."""
        return Page

    def _get_path(self, id: str) -> str:
        """Get API path for a page."""
        return f"/pages/{id}"

    async def create(self, **kwargs: Any) -> Page:
        """Create a new page.

        Args:
            **kwargs: Page properties including parent (required).

        Returns:
            Page entity with rich methods.

        Raises:
            ValidationError: If parent is not provided or invalid.
            BadRequestError: If the request is invalid.
        """
        data = await self._api._request("POST", "/pages", json=kwargs)
        return Page(self._api, data)

    async def list(self, database_id: str, **kwargs: Any) -> list[Page]:
        """List pages in a database.

        Args:
            database_id: The database ID.
            **kwargs: Query parameters (filter, sorts, start_cursor, etc.).

        Returns:
            List of Page entities (first page only).

        Raises:
            NotFoundError: If the database does not exist.
            ValidationError: If the query parameters are invalid.
        """
        data = await self._api._request(
            "POST",
            f"/databases/{database_id}/query",
            json=kwargs,
        )
        results = data.get("results", [])
        return [Page(self._api, page_data) for page_data in results]

    async def update(self, page_id: str, **kwargs: Any) -> Page:
        """Update a page.

        Args:
            page_id: The page ID.
            **kwargs: Page properties to update.

        Returns:
            Updated Page entity.

        Raises:
            NotFoundError: If the page does not exist.
            BadRequestError: If the request is invalid.
        """
        data = await self._api._request("PATCH", f"/pages/{page_id}", json=kwargs)
        return Page(self._api, data)

    async def delete(self, page_id: str) -> dict[str, Any]:
        """Delete a page.

        Args:
            page_id: The page ID.

        Returns:
            Empty response dict on success.

        Raises:
            NotFoundError: If the page does not exist.

        Note:
            Uses DELETE /blocks/{block_id} endpoint because pages are
            technically blocks in Notion's architecture.
        """
        return await self._api._request("DELETE", f"/blocks/{page_id}")

    async def iterate(
        self, database_id: str, **kwargs: Any
    ) -> AsyncPaginatedIterator:
        """Iterate over all pages in a database with automatic pagination.

        Args:
            database_id: The database ID.
            **kwargs: Query parameters (filter, sorts, etc.).

        Returns:
            Async iterator that yields Page entities.

        Example:
            >>> async for page in api.pages.iterate("database_id"):
            ...     print(page.id)
            ...     await page.save()

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

        async def convert_fn(data: dict[str, Any]) -> Page:
            """Convert raw data to Page entity."""
            results = data.get("results", [])
            return [Page(self._api, page_data) for page_data in results]

        return AsyncPaginatedIterator(fetch_fn, convert_fn)
