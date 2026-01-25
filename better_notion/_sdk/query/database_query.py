"""Database query builder for fluent query construction."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, AsyncIterator

from better_notion._sdk.query.filter_translator import FilterTranslator

if TYPE_CHECKING:
    from better_notion._sdk.client import NotionClient
    from better_notion._sdk.models.page import Page


@dataclass
class SortConfig:
    """Sort configuration."""
    property: str
    direction: str = "ascending"  # or "descending"


class DatabaseQuery:
    """Build and execute Notion database queries.

    Provides fluent interface for building complex queries:
        >>> query = database.query(status="Done")
        >>> query = query.sort("due_date").limit(10)
        >>> pages = await query.collect()

    Example:
        >>> # Simple equality
        >>> pages = await database.query(status="Done")
        >>>
        >>> # Multiple conditions (implicit AND)
        >>> pages = await database.query(
        ...     status="In Progress",
        ...     priority__gte=5
        ... )
        >>>
        >>> # Builder pattern
        >>> pages = await (database.query()
        ...     .filter(status="In Progress")
        ...     .sort("due_date")
        ...     .limit(10)
        ... ).collect()
    """

    def __init__(
        self,
        client: "NotionClient",
        database_id: str,
        schema: dict[str, Any],
        filters: dict[str, Any] | None = None
    ) -> None:
        """Initialize query builder.

        Args:
            client: NotionClient instance
            database_id: Database to query
            schema: Database property schema (for type inference)
            filters: Initial filters from kwargs
        """
        self._client = client
        self._database_id = database_id
        self._schema = schema
        self._filters: list[dict] = []
        self._sorts: list[SortConfig] = []
        self._limit: int | None = None

        # Process initial filters
        if filters:
            for key, value in filters.items():
                self._add_filter(key, value)

    def _add_filter(self, key: str, value: Any) -> None:
        """Add filter from key-value pair.

        Parses operator from key (e.g., "priority__gte")
        and translates to Notion filter format.

        Args:
            key: Property name with optional operator suffix
            value: Filter value
        """
        # Parse key and operator
        if "__" in key:
            prop_name, operator = key.rsplit("__", 1)
        else:
            prop_name, operator = key, "eq"

        # Translate to Notion filter
        filter_dict = FilterTranslator.translate(
            prop_name=prop_name,
            operator=operator,
            value=value,
            schema=self._schema
        )

        self._filters.append(filter_dict)

    def filter(
        self,
        **kwargs: Any
    ) -> "DatabaseQuery":
        """Add filter conditions.

        Args:
            **kwargs: Filter conditions

        Returns:
            self (for chaining)

        Example:
            >>> query.filter(status="Done")
            >>> query.filter(priority__gte=5)
        """
        for key, value in kwargs.items():
            self._add_filter(key, value)
        return self

    def sort(
        self,
        property: str,
        direction: str = "ascending"
    ) -> "DatabaseQuery":
        """Add sort order.

        Args:
            property: Property name to sort by
            direction: "ascending" or "descending"

        Returns:
            self (for chaining)

        Example:
            >>> query.sort("due_date", "ascending")
            >>> query.sort("priority", "descending")

        Raises:
            ValueError: If direction is not "ascending" or "descending"
        """
        if direction not in ("ascending", "descending"):
            raise ValueError(
                f"Direction must be 'ascending' or 'descending', got '{direction}'"
            )

        self._sorts.append(SortConfig(property, direction))
        return self

    def limit(self, n: int) -> "DatabaseQuery":
        """Limit results to n items.

        Args:
            n: Maximum number of results

        Returns:
            self (for chaining)

        Note:
            This is client-side limit (fetches all then truncates)
            For large datasets, break iteration early instead

        Example:
            >>> async for page in query.limit(10):
            ...     process(page)
        """
        if n <= 0:
            raise ValueError(f"Limit must be positive, got {n}")

        self._limit = n
        return self

    async def execute(self) -> AsyncIterator[Page]:
        """Execute query and return async iterator.

        Yields:
            Page objects matching query

        Note:
            Handles pagination automatically
        """
        # Build request body
        body = {}

        # Add filters (combine with AND if multiple)
        if self._filters:
            if len(self._filters) == 1:
                body["filter"] = self._filters[0]
            else:
                body["filter"] = {"and": self._filters}

        # Add sorts
        if self._sorts:
            body["sorts"] = [
                {
                    "property": s.property,
                    "direction": s.direction
                }
                for s in self._sorts
            ]

        # Execute query with pagination
        async def fetch_fn(cursor: str | None) -> dict:
            body_copy = body.copy()
            if cursor:
                body_copy["start_cursor"] = cursor
            return await self._client.api.databases.query(
                database_id=self._database_id,
                **body_copy
            )

        from better_notion._api.utils.pagination import AsyncPaginatedIterator
        from better_notion._sdk.models.page import Page

        # Define item parser
        def item_parser(item_data: dict) -> Page:
            return Page(self._client, item_data)

        iterator = AsyncPaginatedIterator(fetch_fn, item_parser)

        # Apply limit if set
        count = 0
        async for page in iterator:
            if self._limit and count >= self._limit:
                break

            yield page
            count += 1

    # ===== ASYNC ITERATOR =====

    def __aiter__(self) -> AsyncIterator[Page]:
        """Make DatabaseQuery async iterable.

        Example:
            >>> async for page in database.query():
            ...     print(page.title)
        """
        return self.execute()

    # ===== CONVENIENCE METHODS =====

    async def collect(self) -> list[Page]:
        """Collect all results into list.

        Returns:
            List of Page objects

        Warning:
            For large result sets, this consumes significant memory

        Example:
            >>> pages = await database.query(status="Done").collect()
            >>> print(f"Found {len(pages)} pages")
        """
        pages = []
        async for page in self:
            pages.append(page)
        return pages

    async def first(self) -> Page | None:
        """Get first result only.

        Returns:
            First matching Page or None if no results

        Example:
            >>> page = await database.query(status="Done").first()
            >>> if page:
            ...     print(page.title)
        """
        async for page in self:
            return page
        return None

    async def count(self) -> int:
        """Count matching pages.

        Returns:
            Number of matching pages

        Example:
            >>> count = await database.query(status="Done").count()
            >>> print(f"Found {count} done tasks")
        """
        count = 0
        async for _ in self:
            count += 1
        return count

    async def exists(self) -> bool:
        """Check if any pages match query.

        Returns:
            True if at least one result exists

        Example:
            >>> if await database.query(status="Done").exists():
            ...     print("There are done tasks")
        """
        return await self.first() is not None

    def __repr__(self) -> str:
        """String representation."""
        parts = []
        if self._filters:
            parts.append(f"{len(self._filters)} filters")
        if self._sorts:
            parts.append(f"{len(self._sorts)} sorts")
        if self._limit:
            parts.append(f"limit={self._limit}")

        info = ", ".join(parts) if parts else "no filters"
        return f"DatabaseQuery({info})"
