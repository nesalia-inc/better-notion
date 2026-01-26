"""Database manager for database operations."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from better_notion._sdk.client import NotionClient
    from better_notion._sdk.models.database import Database
    from better_notion._sdk.models.page import Page
    from better_notion._sdk.cache import Cache


class DatabaseManager:
    """Ultra-thin wrapper to autonomous Database class.

    All methods delegate to Database class methods.
    The manager only stores and passes the client reference.

    Example:
        >>> # Via manager (recommended)
        >>> db = await client.databases.get(db_id)
        >>>
        >>> # Via entity directly (autonomous)
        >>> db = await Database.get(db_id, client=client)
    """

    def __init__(self, client: "NotionClient") -> None:
        """Initialize database manager.

        Args:
            client: NotionClient instance
        """
        self._client = client

    # ===== CRUD OPERATIONS =====

    async def get(self, database_id: str) -> "Database":
        """Get database by ID.

        Args:
            database_id: Database UUID

        Returns:
            Database object

        Raises:
            DatabaseNotFound: If database doesn't exist

        Example:
            >>> db = await client.databases.get(db_id)
            >>> print(f"{db.title}: {len(db.schema)} properties")
        """
        from better_notion._sdk.models.database import Database

        return await Database.get(database_id, client=self._client)

    async def create(
        self,
        parent: "Page",
        title: str,
        schema: dict[str, Any]
    ) -> "Database":
        """Create a new database.

        Args:
            parent: Parent page
            title: Database title
            schema: Property schema

        Returns:
            Created Database object

        Example:
            >>> parent = await client.pages.get(page_id)
            >>> db = await client.databases.create(
            ...     parent=parent,
            ...     title="Tasks",
            ...     schema={
            ...         "Name": {"type": "title"},
            ...         "Status": {"type": "select", "options": [...]}
            ...     }
            ... )
        """
        from better_notion._sdk.models.database import Database

        return await Database.create(
            parent=parent,
            title=title,
            schema=schema,
            client=self._client
        )

    # ===== FINDING =====

    async def find_by_title(
        self,
        title: str
    ) -> "Database | None":
        """Find database by title (case-insensitive).

        Args:
            title: Database title to search for

        Returns:
            Database object or None if not found

        Example:
            >>> db = await client.databases.find_by_title("Tasks")
            >>> if db:
            ...     print(f"Found: {db.title}")
        """
        # Use search API
        results = await self._client.search(
            query=title,
            filter={"value": "database", "property": "object"}
        )

        # results is already a list of Database and Page objects
        for result in results:
            # Check if it's a Database and matches title (case-insensitive)
            if hasattr(result, 'title') and result.title.lower() == title.lower():
                return result

        return None

    # ===== CACHE ACCESS =====

    @property
    def cache(self) -> "Cache[Database]":
        """Access to database cache.

        Returns:
            Cache object for databases

        Example:
            >>> # Check if cached
            >>> if db_id in client.databases.cache:
            ...     db = client.databases.cache[db_id]
        """
        return self._client._database_cache

    # ===== BULK OPERATIONS =====

    async def get_multiple(
        self,
        database_ids: list[str]
    ) -> list["Database"]:
        """Get multiple databases by IDs.

        Args:
            database_ids: List of database IDs

        Returns:
            List of Database objects (in same order)

        Example:
            >>> db_ids = ["id1", "id2", "id3"]
            >>> databases = await client.databases.get_multiple(db_ids)
        """
        from better_notion._sdk.models.database import Database

        databases = []
        for db_id in database_ids:
            database = await Database.get(db_id, client=self._client)
            databases.append(database)

        return databases

    # ===== HELPERS =====

    async def list_all(self) -> list["Database"]:
        """List all databases in workspace.

        Returns:
            List of all Database objects

        Example:
            >>> all_dbs = await client.databases.list_all()
            >>> for db in all_dbs:
            ...     print(f"{db.title}: {len(db.schema)} properties")
        """
        results = await self._client.search(
            filter={"value": "database", "property": "object"}
        )

        # Filter results where 'object' field equals 'database' and convert to Database objects
        from better_notion._sdk.models.database import Database

        databases = []
        for r in results:
            if isinstance(r, Database):
                databases.append(r)

        return databases
