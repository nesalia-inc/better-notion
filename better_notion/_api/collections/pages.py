"""Page collection."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from better_notion._api import NotionAPI

from better_notion._api.entities import Page


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

    async def get(self, page_id: str) -> Page:
        """Retrieve a page by ID.

        Args:
            page_id: The page ID.

        Returns:
            A Page entity.

        Raises:
            NotFoundError: If the page does not exist.
        """
        data = await self._api._request("GET", f"/pages/{page_id}")
        return Page(self._api, data)

    async def create(self, **kwargs: Any) -> Page:
        """Create a new page.

        Args:
            **kwargs: Page properties including parent (required).

        Returns:
            The created Page entity.

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
            List of Page entities.

        Raises:
            NotFoundError: If the database does not exist.
            ValidationError: If the query parameters are invalid.
        """
        data = await self._api._request(
            "POST",
            f"/databases/{database_id}/query",
            json=kwargs,
        )
        return [Page(self._api, page_data) for page_data in data.get("results", [])]
