"""Database model with schema introspection and query capabilities."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, AsyncIterator

from better_notion._sdk.base.entity import BaseEntity

if TYPE_CHECKING:
    from better_notion._sdk.client import NotionClient
    from better_notion._sdk.models.page import Page


class Database(BaseEntity):
    """Notion Database with schema and query capabilities.

    This model combines:
    - BaseEntity: Core functionality (id, created_time, cache)
    - Schema introspection: Property definitions and types
    - Navigation: Parent page, child pages
    - Query methods: List properties, check schema

    Example:
        >>> database = await client.databases.get(db_id)
        >>>
        >>> # Schema introspection
        >>> for name, defn in database.schema.items():
        ...     print(f"{name}: {defn['type']}")
        >>>
        >>> # Navigation
        >>> parent = await database.parent()
        >>> async for page in database.children():
        ...     print(page.title)
    """

    def __init__(self, client: "NotionClient", data: dict[str, Any]) -> None:
        """Initialize a Database.

        Args:
            client: NotionClient instance
            data: Raw database data from Notion API
        """
        # Initialize BaseEntity
        super().__init__(client, data)

        # Parse and cache schema
        self._schema: dict[str, dict[str, Any]] = self._parse_schema()

    # ===== CLASS METHODS (AUTONOMOUS ENTITY) =====

    @classmethod
    async def get(
        cls,
        database_id: str,
        *,
        client: "NotionClient"
    ) -> "Database":
        """Get a database by ID.

        Args:
            database_id: Database UUID
            client: NotionClient instance

        Returns:
            Database object

        Behavior:
            - Checks cache first (instant)
            - If cached, return cached version
            - If not cached, fetch from API
            - Stores in cache for next time

        Example:
            >>> database = await Database.get(db_id, client=client)
            >>> print(f"Title: {database.title}")
        """
        # Check global cache first
        if database_id in client.database_cache:
            return client.database_cache[database_id]

        # Fetch from API
        data = await client.api.databases.retrieve(database_id=database_id)
        database = cls(client, data)

        # Cache it
        client.database_cache[database_id] = database

        return database

    @classmethod
    async def create(
        cls,
        parent: "Page",
        *,
        client: "NotionClient",
        title: str,
        properties: dict[str, Any]
    ) -> "Database":
        """Create a new database.

        Args:
            parent: Parent Page
            client: NotionClient instance
            title: Database title
            properties: Property schema configuration

        Returns:
            Newly created Database object

        Example:
            >>> database = await Database.create(
            ...     parent=page,
            ...     client=client,
            ...     title="Tasks",
            ...     properties={
            ...         "Name": {"type": "title"},
            ...         "Status": {"type": "select"}
            ...     }
            ... )
        """
        from better_notion._api.properties import Title

        # Build title array
        title_array = [{"type": "text", "text": {"content": title}}]

        # Create database via API
        data = await client.api.databases.create(
            parent={"type": "page_id", "page_id": parent.id},
            title=title_array,
            properties=properties
        )

        database = cls(client, data)

        # Cache it
        client.database_cache[database.id] = database

        return database

    # ===== METADATA PROPERTIES =====

    @property
    def title(self) -> str:
        """Get database title.

        Returns:
            Database title (empty string if no title)

        Example:
            >>> database.title
            'Project Tasks'
        """
        title_array = self._data.get("title", [])
        if title_array and title_array[0].get("type") == "text":
            return title_array[0]["text"].get("content", "")
        return ""

    @property
    def description(self) -> str:
        """Get database description.

        Returns:
            Database description (empty string if no description)
        """
        desc_array = self._data.get("description", [])
        if desc_array and desc_array[0].get("type") == "text":
            return desc_array[0]["text"].get("content", "")
        return ""

    @property
    def icon(self) -> str | None:
        """Get database icon.

        Returns:
            Emoji string or URL, or None
        """
        icon_data = self._data.get("icon")
        if not icon_data or icon_data.get("type") is None:
            return None

        if icon_data.get("type") == "emoji":
            return icon_data.get("emoji")
        elif icon_data.get("type") == "external":
            return icon_data.get("external", {}).get("url")
        elif icon_data.get("type") == "file":
            return icon_data.get("file", {}).get("url")

        return None

    @property
    def cover(self) -> str | None:
        """Get database cover image URL.

        Returns:
            Cover image URL or None
        """
        cover_data = self._data.get("cover")
        if not cover_data:
            return None

        if cover_data.get("type") == "external":
            return cover_data.get("external", {}).get("url")
        elif cover_data.get("type") == "file":
            return cover_data.get("file", {}).get("url")

        return None

    @property
    def url(self) -> str:
        """Get public Notion URL.

        Returns:
            Public Notion URL for this database
        """
        return f"https://notion.so/{self.id.replace('-', '')}"

    @property
    def archived(self) -> bool:
        """Check if database is archived.

        Returns:
            True if database is archived
        """
        return self._data.get("archived", False)

    @property
    def is_inline(self) -> bool:
        """Check if database is inline (in parent page).

        Returns:
            True if database is inline
        """
        parent = self._data.get("parent", {})
        return parent.get("type") in ("page_id", "database_id")

    # ===== SCHEMA PROPERTIES =====

    @property
    def schema(self) -> dict[str, dict[str, Any]]:
        """Get database property schema.

        Returns:
            Dict mapping property names to their schema definitions

        Example:
            >>> for name, defn in database.schema.items():
            ...     print(f"{name}: {defn['type']}")

        Note:
            Cached after first access for performance
        """
        return self._schema

    def _parse_schema(self) -> dict[str, dict[str, Any]]:
        """Parse property schema from API data.

        Returns:
            Dict of property name → schema definition
        """
        schema = {}

        for prop_name, prop_data in self._data.get("properties", {}).items():
            prop_def = {
                "type": prop_data.get("type"),
                "id": prop_data.get("id")
            }

            # Add type-specific info
            prop_type = prop_data.get("type")

            if prop_type == "select":
                options = prop_data.get("select", {}).get("options", [])
                prop_def["options"] = [opt["name"] for opt in options]

            elif prop_type == "multi_select":
                options = prop_data.get("multi_select", {}).get("options", [])
                prop_def["options"] = [opt["name"] for opt in options]

            elif prop_type == "number":
                prop_def["format"] = prop_data.get("number", {}).get("format")

            elif prop_type == "formula":
                prop_def["expression"] = prop_data.get("formula", {}).get("expression")

            elif prop_type == "relation":
                prop_def["database_id"] = prop_data.get("relation", {}).get("database_id")

            schema[prop_name] = prop_def

        return schema

    def get_property_type(self, property_name: str) -> str | None:
        """Get type of a property.

        Args:
            property_name: Property name (case-insensitive)

        Returns:
            Property type string or None if not found

        Example:
            >>> database.get_property_type("Status")
            'select'
        """
        prop_name_lower = property_name.lower()

        for name, schema in self._schema.items():
            if name.lower() == prop_name_lower:
                return schema["type"]

        return None

    def get_property_options(self, property_name: str) -> list[str]:
        """Get available options for select/multi-select property.

        Args:
            property_name: Property name (case-insensitive)

        Returns:
            List of option names

        Raises:
            ValueError: If property is not select or multi_select

        Example:
            >>> database.get_property_options("Status")
            ['Not Started', 'In Progress', 'Done']
        """
        prop_name_lower = property_name.lower()

        for name, schema in self._schema.items():
            if name.lower() == prop_name_lower:
                prop_type = schema["type"]

                if prop_type not in ("select", "multi_select"):
                    raise ValueError(
                        f"Property '{property_name}' is {prop_type}, "
                        f"not select/multi_select"
                    )

                return schema.get("options", [])

        raise ValueError(f"Property '{property_name}' not found")

    # ===== SCHEMA HELPER METHODS =====

    def list_properties(self) -> list[str]:
        """List all property names.

        Returns:
            List of property names

        Example:
            >>> for prop in database.list_properties():
            ...     print(prop)
        """
        return list(self._schema.keys())

    def has_property(self, property_name: str) -> bool:
        """Check if property exists.

        Args:
            property_name: Property name (case-insensitive)

        Returns:
            True if property exists

        Example:
            >>> if database.has_property("Due Date"):
            ...     print("Has due date")
        """
        prop_name_lower = property_name.lower()
        return any(
            name.lower() == prop_name_lower
            for name in self._schema.keys()
        )

    def find_property(
        self,
        property_name: str,
        fuzzy: bool = False
    ) -> dict[str, Any] | None:
        """Find property schema by name.

        Args:
            property_name: Property name
            fuzzy: Enable fuzzy matching (substring)

        Returns:
            Property schema dict or None

        Example:
            >>> prop = database.find_property("stat", fuzzy=True)
        """
        if not fuzzy:
            prop_name_lower = property_name.lower()
            for name, schema in self._schema.items():
                if name.lower() == prop_name_lower:
                    return schema
            return None

        # Fuzzy matching
        prop_name_lower = property_name.lower()
        for name, schema in self._schema.items():
            if prop_name_lower in name.lower():
                return schema

        return None

    # ===== NAVIGATION =====

    async def parent(self) -> "Page | None":
        """Get parent object (fetches if not cached).

        Returns:
            Parent Page object or None if workspace root

        Behavior:
            - First call: Fetch from API, cache result
            - Subsequent calls: Return cached version (instant)

        Example:
            >>> parent = await database.parent()
            >>> if parent:
            ...     print(f"Database in page: {parent.title}")
        """
        # Check entity cache
        cached_parent = self._cache_get("parent")
        if cached_parent:
            return cached_parent

        # Fetch from API
        parent_data = self._data.get("parent", {})

        if parent_data.get("type") == "page_id":
            page_id = parent_data["page_id"]
            # Check cache first
            if page_id in self._client.page_cache:
                return self._client.page_cache[page_id]
            # Fetch from API
            data = await self._client.api.pages.retrieve(page_id=page_id)
            from better_notion._sdk.models.page import Page
            parent = Page(self._client, data)
        elif parent_data.get("type") == "workspace":
            parent = None
        else:
            parent = None

        # Cache result
        if parent:
            self._cache_set("parent", parent)

        return parent

    async def children(self) -> AsyncIterator["Page"]:
        """Iterate over pages in this database.

        Yields:
            Page objects from this database

        Example:
            >>> async for page in database.children():
            ...     print(page.title)

        Note:
            Uses database query API with automatic pagination
        """
        from better_notion._api.utils.pagination import AsyncPaginatedIterator
        from better_notion._sdk.models.page import Page

        # Define fetch function
        async def fetch_fn(cursor: str | None) -> dict:
            body = {}
            if cursor:
                body["start_cursor"] = cursor

            return await self._client.api.databases.query(
                database_id=self.id,
                **body
            )

        # Define item parser
        def item_parser(item_data: dict) -> Page:
            return Page(self._client, item_data)

        # Use paginated iterator
        iterator = AsyncPaginatedIterator(fetch_fn, item_parser)

        async for page in iterator:
            yield page

    # ===== ANALYTICS =====

    async def count(self) -> int:
        """Count total pages in database.

        Returns:
            Number of pages in database

        Example:
            >>> count = await database.count()
            >>> print(f"Database has {count} pages")
        """
        count = 0
        async for _ in self.children():
            count += 1
        return count

    def __repr__(self) -> str:
        """String representation."""
        title = self.title[:30] if self.title else ""
        return f"Database(id={self.id!r}, title={title!r})"
