"""Page manager for page operations."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from better_notion._sdk.client import NotionClient
    from better_notion._sdk.models.page import Page
    from better_notion._sdk.models.database import Database
    from better_notion._sdk.cache import Cache


class PageManager:
    """Ultra-thin wrapper to autonomous Page class.

    All methods delegate to Page class methods.
    The manager only stores and passes the client reference.

    Example:
        >>> # Via manager (recommended)
        >>> page = await client.pages.get(page_id)
        >>>
        >>> # Via entity directly (autonomous)
        >>> page = await Page.get(page_id, client=client)
    """

    def __init__(self, client: "NotionClient") -> None:
        """Initialize page manager.

        Args:
            client: NotionClient instance
        """
        self._client = client

    # ===== CRUD OPERATIONS =====

    async def get(self, page_id: str) -> "Page":
        """Get page by ID.

        Args:
            page_id: Page UUID

        Returns:
            Page object

        Raises:
            PageNotFound: If page doesn't exist

        Example:
            >>> page = await client.pages.get(page_id)
            >>> print(page.title)
        """
        from better_notion._sdk.models.page import Page

        return await Page.get(page_id, client=self._client)

    async def create(
        self,
        parent: "Database | Page",
        title: str,
        **properties: Any
    ) -> "Page":
        """Create a new page.

        Args:
            parent: Parent database or page
            title: Page title
            **properties: Additional property values

        Returns:
            Created Page object

        Example:
            >>> db = await client.databases.get(db_id)
            >>> page = await client.pages.create(
            ...     parent=db,
            ...     title="New Task",
            ...     status="Todo",
            ...     priority=5
            ... )
        """
        from better_notion._sdk.models.page import Page

        return await Page.create(
            parent=parent,
            title=title,
            client=self._client,
            **properties
        )

    # ===== FINDING & QUERYING =====

    async def find(
        self,
        database: "Database",
        **filters: Any
    ) -> list["Page"]:
        """Find pages in database with filters.

        Args:
            database: Database to search in
            **filters: Filter conditions (passed to database.query)

        Returns:
            List of matching Page objects

        Example:
            >>> db = await client.databases.get(db_id)
            >>> pages = await client.pages.find(
            ...     database=db,
            ...     status="In Progress",
            ...     priority__gte=5
            ... )
        """
        # Delegate to database.query
        return await database.query(
            client=self._client,
            **filters
        ).collect()

    async def find_one(
        self,
        database: "Database",
        **filters: Any
    ) -> "Page | None":
        """Find first matching page in database.

        Args:
            database: Database to search in
            **filters: Filter conditions

        Returns:
            First matching Page or None

        Example:
            >>> db = await client.databases.get(db_id)
            >>> page = await client.pages.find_one(
            ...     database=db,
            ...     title="My Task"
            ... )
        """
        return await database.query(
            client=self._client,
            **filters
        ).first()

    # ===== CACHE ACCESS =====

    @property
    def cache(self) -> "Cache[Page]":
        """Access to page cache.

        Returns:
            Cache object for pages

        Example:
            >>> # Check if cached
            >>> if page_id in client.pages.cache:
            ...     page = client.pages.cache[page_id]
            >>>
            >>> # Get without API call
            >>> page = client.pages.cache.get(page_id)
        """
        return self._client._page_cache

    # ===== BULK OPERATIONS =====

    async def get_multiple(
        self,
        page_ids: list[str]
    ) -> list["Page"]:
        """Get multiple pages by IDs.

        Args:
            page_ids: List of page IDs

        Returns:
            List of Page objects (in same order)

        Example:
            >>> page_ids = ["id1", "id2", "id3"]
            >>> pages = await client.pages.get_multiple(page_ids)
        """
        from better_notion._sdk.models.page import Page

        pages = []
        for page_id in page_ids:
            page = await Page.get(page_id, client=self._client)
            pages.append(page)

        return pages
