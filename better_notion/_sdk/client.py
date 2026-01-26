"""Notion SDK client with Managers as thin wrappers to autonomous entities."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from better_notion._api import NotionAPI
from better_notion._sdk.cache import Cache
from better_notion._sdk.managers import (
    PageManager,
    DatabaseManager,
    BlockManager,
    UserManager,
    CommentsManager,
)


class NotionClient:
    """Notion SDK client with Managers.

    The client provides managers that act as **thin wrappers** to the
    autonomous entity classes (Page, Database, Block, User).

    ## Architecture

    **Managers are ultra-thin**:
    - They delegate ALL logic to entity classes
    - Managers provide shortcuts: `client.pages.get()`
    - Entities have all logic: `Page.get()`, `Page.create()`

    **Both approaches work**:
    ```python
    # Via Manager (recommended, shorter)
    page = await client.pages.get(page_id)

    # Via Entity directly (recommended, autonomous)
    page = await Page.get(page_id, client=client)

    # Same result, user's choice
    ```

    ## Attributes
        pages: Page manager for page operations
        databases: Database manager for database operations
        blocks: Block manager for block operations
        users: User manager for user operations
        comments: Comments manager for comment operations
        api: Direct access to low-level NotionAPI
        page_cache: Direct access to page cache
        database_cache: Direct access to database cache
        user_cache: Direct access to user cache
        comment_cache: Direct access to comment cache

    Example:
        >>> client = NotionClient(auth=os.getenv("NOTION_KEY"))
        >>>
        >>> # Use managers (recommended)
        >>> page = await client.pages.get(page_id)
        >>> database = await client.databases.get(db_id)
        >>>
        >>> # Or use entities directly (autonomous)
        >>> page = await Page.get(page_id, client=client)
    """

    def __init__(
        self,
        auth: str,
        base_url: str | None = None,
        timeout: float = 30.0
    ) -> None:
        """Initialize the Notion client.

        Args:
            auth: Notion API token
            base_url: API base URL (default: production)
            timeout: Request timeout in seconds

        Example:
            >>> client = NotionClient(auth=os.getenv("NOTION_KEY"))
            >>>
            >>> # With custom timeout
            >>> client = NotionClient(
            ...     auth="secret_...",
            ...     timeout=60.0
            ... )
        """
        # Low-level API
        self._api = NotionAPI(
            auth=auth,
            base_url=base_url,
            timeout=timeout
        )

        # Shared caches (accessible by managers and entities)
        self._user_cache: Cache[object] = Cache()
        self._database_cache: Cache[object] = Cache()
        self._page_cache: Cache[object] = Cache()
        self._comment_cache: Cache[object] = Cache()
        # No cache for Block (too many)

        # Search cache
        self._search_cache: dict[str, list[object]] = {}

        # Create managers
        self._pages = PageManager(self)
        self._databases = DatabaseManager(self)
        self._blocks = BlockManager(self)
        self._users = UserManager(self)
        self._comments = CommentsManager(self)

    # ===== MANAGER PROPERTIES =====

    @property
    def pages(self) -> PageManager:
        """Page manager for page operations.

        Example:
            >>> page = await client.pages.get(page_id)
            >>> pages = await client.pages.find(database=db, status="Done")
        """
        return self._pages

    @property
    def databases(self) -> DatabaseManager:
        """Database manager for database operations.

        Example:
            >>> db = await client.databases.get(db_id)
            >>> print(f"{db.title}: {len(db.schema)} properties")
        """
        return self._databases

    @property
    def blocks(self) -> BlockManager:
        """Block manager for block operations.

        Example:
            >>> block = await client.blocks.get(block_id)
            >>> para = await client.blocks.create_paragraph(page, text="Hi")
        """
        return self._blocks

    @property
    def users(self) -> UserManager:
        """User manager for user operations.

        Example:
            >>> user = await client.users.get(user_id)
            >>> await client.users.populate_cache()
            >>> users = client.users.cache.get_all()
        """
        return self._users

    @property
    def comments(self) -> CommentsManager:
        """Comments manager for comment operations.

        Example:
            >>> comment = await client.comments.get(comment_id)
            >>> comment = await client.comments.create(
            ...     parent="page-123",
            ...     rich_text=[{
            ...         "type": "text",
            ...         "text": {"content": "Hello!"}
            ...     }]
            ... )
            >>> comments = await client.comments.list_all("page-123")
        """
        return self._comments

    # ===== DIRECT CACHE ACCESS =====

    @property
    def user_cache(self) -> Cache[object]:
        """Direct access to user cache.

        Example:
            >>> if user_id in client.user_cache:
            ...     user = client.user_cache[user_id]
        """
        return self._user_cache

    @property
    def database_cache(self) -> Cache[object]:
        """Direct access to database cache."""
        return self._database_cache

    @property
    def page_cache(self) -> Cache[object]:
        """Direct access to page cache."""
        return self._page_cache

    # ===== LOW-LEVEL API ACCESS =====

    @property
    def api(self) -> NotionAPI:
        """Direct access to low-level NotionAPI.

        Use only for operations not supported by the SDK.

        Example:
            >>> # Custom raw request
            >>> data = await client.api._request(
            ...     "GET",
            ...     "/custom-endpoint"
            ... )
        """
        return self._api

    # ===== SEARCH =====

    async def search(
        self,
        query: str = "",
        filter: dict | None = None,
        sort: dict | None = None
    ) -> list[object]:
        """Search for pages and databases.

        Args:
            query: Search query string
            filter: Object filter (e.g., {"value": "page", "property": "object"})
            sort: Sort (e.g., {"direction": "descending", "timestamp": "last_edited_time"})

        Returns:
            List of Page and Database objects

        Example:
            >>> # Search for "API"
            >>> results = await client.search(query="API")
            >>>
            >>> # Search only pages
            >>> results = await client.search(
            ...     query="Project",
            ...     filter={"value": "page", "property": "object"}
            ... )
        """
        from better_notion._sdk.models.database import Database
        from better_notion._sdk.models.page import Page

        results = []

        async for result in self._api.search_iterate(
            query=query,
            filter=filter,
            sort=sort
        ):
            obj_type = result.get("object")
            # Convert to proper entity objects
            if obj_type == "database":
                entity = Database(self, result)
            elif obj_type == "page":
                entity = Page(self, result)
            else:
                # For other types (blocks, etc.), return raw dict
                entity = result
            results.append(entity)

        return results

    # ===== CACHE MANAGEMENT =====

    def clear_all_caches(self) -> None:
        """Clear all caches.

        Example:
            >>> client.clear_all_caches()
        """
        self._user_cache.clear()
        self._database_cache.clear()
        self._page_cache.clear()
        self._search_cache.clear()

    def get_cache_stats(self) -> dict[str, dict[str, Any]]:
        """Get statistics for all caches.

        Returns:
            Dict with stats for each cache

        Example:
            >>> stats = client.get_cache_stats()
            >>> print(stats)
            {
                'user_cache': {'hits': 100, 'misses': 5, 'size': 50, 'hit_rate': 0.95},
                ...
            }
        """
        return {
            "user_cache": {
                "hits": self._user_cache.stats.hits,
                "misses": self._user_cache.stats.misses,
                "size": self._user_cache.stats.size,
                "hit_rate": self._user_cache.stats.hit_rate
            },
            "database_cache": {
                "hits": self._database_cache.stats.hits,
                "misses": self._database_cache.stats.misses,
                "size": self._database_cache.stats.size,
                "hit_rate": self._database_cache.stats.hit_rate
            },
            "page_cache": {
                "hits": self._page_cache.stats.hits,
                "misses": self._page_cache.stats.misses,
                "size": self._page_cache.stats.size,
                "hit_rate": self._page_cache.stats.hit_rate
            },
            "search_cache": {
                "size": len(self._search_cache)
            }
        }

    # ===== CONTEXT MANAGER =====

    async def __aenter__(self):
        """Async context manager support.

        Example:
            >>> async with NotionClient(auth="...") as client:
            ...     page = await client.pages.get(page_id)
            ...     # Auto cleanup on exit
        """
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Cleanup on context exit."""
        self.clear_all_caches()
