"""Page model with rich SDK features."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, AsyncIterator, Union

from better_notion._sdk.base.entity import BaseEntity
from better_notion._sdk.parents import Parent, WorkspaceParent, PageParent, DatabaseParent
from better_notion._sdk.properties.parsers import PropertyParser

if TYPE_CHECKING:
    from better_notion._sdk.client import NotionClient
    from better_notion._sdk.models.block import Block


# Import Database at runtime for isinstance checks
from better_notion._sdk.models.database import Database


class Page(BaseEntity):
    """Notion Page with rich SDK features.

    This model combines:
    - BaseEntity: Core functionality (id, created_time, cache)
    - Property Parsers: Intelligent property extraction
    - Navigation: Hierarchical access with caching
    - CRUD: Update, save, delete operations

    Example:
        >>> page = await client.pages.get(page_id)
        >>>
        >>> # Metadata
        >>> print(page.title)
        >>> print(page.url)
        >>>
        >>> # Properties
        >>> status = page.get_property("Status")
        >>>
        >>> # Navigation
        >>> parent = await page.parent()
        >>> async for block in page.children():
        ...     print(block.type)
    """

    def __init__(self, client: "NotionClient", data: dict[str, Any]) -> None:
        """Initialize a Page.

        Args:
            client: NotionClient instance
            data: Raw page data from Notion API
        """
        # Initialize BaseEntity (provides id, created_time, _cache, etc.)
        super().__init__(client, data)

        # Cache the title property name (can vary by database)
        self._title_property: str | None = self._find_title_property()

    # ===== CLASS METHODS (AUTONOMOUS ENTITY) =====

    @classmethod
    async def get(
        cls,
        page_id: str,
        *,
        client: "NotionClient"
    ) -> "Page":
        """Get a page by ID.

        Args:
            page_id: Page UUID
            client: NotionClient instance

        Returns:
            Page object

        Raises:
            NotFoundError: If page doesn't exist

        Behavior:
            - Checks cache first (instant)
            - If cached, return cached version
            - If not cached, fetch from API
            - Stores in cache for next time

        Example:
            >>> page = await Page.get(page_id, client=client)
            >>> print(f"Title: {page.title}")
        """
        # Check global cache first
        if page_id in client.page_cache:
            return client.page_cache[page_id]

        # Fetch from API
        data = await client.api.pages.retrieve(page_id=page_id)
        page = cls(client, data)

        # Cache it
        client.page_cache[page_id] = page

        return page

    @classmethod
    async def create(
        cls,
        parent: Union["Database", "Page", Parent],
        *,
        client: "NotionClient",
        title: str = "",
        properties: dict[str, Any] | None = None,
        **kwargs: Any
    ) -> "Page":
        """Create a new page.

        Args:
            parent: Parent Database, Page, or Parent object (WorkspaceParent, PageParent, DatabaseParent)
            client: NotionClient instance
            title: Page title (optional)
            properties: Additional properties (optional)
            **kwargs: Additional parameters (icon, cover, etc.)

        Returns:
            Newly created Page object

        Example:
            >>> # With database object
            >>> page = await Page.create(
            ...     parent=database,
            ...     client=client,
            ...     title="My Page",
            ...     status="In Progress"
            ... )
            >>>
            >>> # With workspace parent (root level)
            >>> from better_notion._sdk.parents import WorkspaceParent
            >>> page = await Page.create(
            ...     parent=WorkspaceParent(),
            ...     client=client,
            ...     title="Root Page"
            ... )
        """
        from better_notion._api.properties import Title

        # Prepare parent reference
        if isinstance(parent, (Database, Page)):
            # Existing object-based path (real Database or Page instances)
            parent_id = parent.id
            parent_type = "database_id" if parent.object == "database" else "page_id"
            parent_ref = {parent_type: parent_id}
            title_search_parent = parent
        elif isinstance(parent, WorkspaceParent):
            # New workspace parent path (root level)
            parent_ref = {"type": "workspace", "workspace": True}
            title_search_parent = None
        elif isinstance(parent, (PageParent, DatabaseParent)):
            # New explicit parent classes
            parent_ref = {
                "type": parent.type,
                f"{parent.type}": parent.page_id if isinstance(parent, PageParent) else parent.database_id
            }
            title_search_parent = None
        elif hasattr(parent, 'id') and hasattr(parent, 'object'):
            # Duck-typing for mocks and other compatible objects
            parent_id = parent.id
            parent_type = "database_id" if parent.object == "database" else "page_id"
            parent_ref = {parent_type: parent_id}
            title_search_parent = parent
        else:
            raise ValueError(f"Invalid parent type: {type(parent)}")

        # Build properties dict
        props = properties or {}

        # Add title if provided
        if title:
            # Find title property name
            title_prop = cls._find_title_property_in_schema(title_search_parent, client)
            if title_prop:
                props[title_prop] = Title(name=title_prop, content=title).to_dict()

        # Create page via API
        data = await client.api.pages.create(
            parent=parent_ref,
            properties=props,
            **kwargs
        )

        page = cls(client, data)

        # Cache it
        client.page_cache[page.id] = page

        return page

    # ===== METADATA PROPERTIES =====

    @property
    def title(self) -> str:
        """Get page title.

        Returns:
            Page title (empty string if no title)

        Note:
            Automatically finds the first property of type "title"
            No need to know the exact property name

        Example:
            >>> page.title
            'My Page Title'
        """
        result = PropertyParser.get_title(self._data.get("properties", {}))
        return result or ""  # Never None, always str

    @property
    def url(self) -> str:
        """Get public Notion URL.

        Returns:
            Public URL to the page

        Example:
            >>> page.url
            'https://notion.so/1234567890abcdef'
        """
        # Convert UUID to URL format (remove dashes)
        return f"https://notion.so/{self.id.replace('-', '')}"

    @property
    def icon(self) -> str | None:
        """Get page icon.

        Returns:
            Emoji string (e.g., "🚀") or image URL
            None if no icon

        Example:
            >>> page.icon
            '🚀'

        Note:
            Icon can be emoji, external URL, or file URL
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

    @staticmethod
    def format_icon(emoji: str | None = None, external_url: str | None = None) -> dict[str, Any] | None:
        """Format icon for API requests.

        Args:
            emoji: Emoji icon (e.g., "🚀")
            external_url: External image URL

        Returns:
            Icon dict for API or None if neither provided

        Raises:
            ValueError: If both emoji and external_url provided

        Example:
            >>> icon_dict = Page.format_icon(emoji="🚀")
            >>> icon_dict = Page.format_icon(external_url="https://example.com/image.png")
        """
        if emoji is None and external_url is None:
            return None
        if emoji is not None and external_url is not None:
            raise ValueError("Only one of emoji or external_url can be provided")

        if emoji is not None:
            return {"type": "emoji", "emoji": emoji}
        else:
            return {"type": "external", "external": {"url": external_url}}

    @property
    def cover(self) -> str | None:
        """Get page cover image URL.

        Returns:
            Image URL or None if no cover

        Example:
            >>> page.cover
            'https://images.notion.so/...'
        """
        cover_data = self._data.get("cover")

        if not cover_data:
            return None

        if cover_data.get("type") == "external":
            return cover_data.get("external", {}).get("url")

        elif cover_data.get("type") == "file":
            return cover_data.get("file", {}).get("url")

        return None

    @staticmethod
    def format_cover(external_url: str | None = None) -> dict[str, Any] | None:
        """Format cover for API requests.

        Args:
            external_url: External image URL

        Returns:
            Cover dict for API or None if not provided

        Example:
            >>> cover_dict = Page.format_cover(external_url="https://example.com/image.png")
        """
        if external_url is None:
            return None

        return {"type": "external", "external": {"url": external_url}}

    @property
    def archived(self) -> bool:
        """Check if page is archived.

        Returns:
            True if page is archived

        Example:
            >>> if page.archived:
            ...     print("This page is archived")
        """
        return self._data.get("archived", False)

    @property
    def properties(self) -> dict[str, Any]:
        """Get raw properties dict (escape hatch).

        Returns:
            Complete properties dict from Notion API

        Example:
            >>> page.properties
            {
                'Name': {...},
                'Status': {...},
                'Priority': {...}
            }
        """
        return self._data["properties"]

    # ===== SMART PROPERTY ACCESS =====

    def get_property(
        self,
        name: str,
        default: Any = None
    ) -> Any:
        """Get property value with automatic type conversion.

        Args:
            name: Property name (case-insensitive)
            default: Default value if not found

        Returns:
            Typed value based on property type:
            - select → str
            - multi_select → list[str]
            - number → int | float
            - checkbox → bool
            - date → datetime
            - title, text, url, email, phone → str
            - people → list[str] (user IDs)

        Example:
            >>> # Select property → string
            >>> status = page.get_property("Status")
            >>> print(status)
            'In Progress'

            >>> # Number property → int
            >>> priority = page.get_property("Priority")
            >>> print(priority)
            5

            >>> # Multi-select → list
            >>> tags = page.get_property("Tags")
            >>> print(tags)
            ['urgent', 'backend']

            >>> # With default
            >>> value = page.get_property("UnknownField", default="N/A")
        """
        # Find property (case-insensitive)
        prop = PropertyParser._find_property(
            self._data.get("properties", {}),
            name
        )

        if not prop:
            return default

        prop_type = prop.get("type")

        # Route to appropriate parser
        if prop_type == "select":
            return PropertyParser.get_select(self._data["properties"], name)

        elif prop_type == "multi_select":
            return PropertyParser.get_multi_select(self._data["properties"], name)

        elif prop_type == "number":
            return PropertyParser.get_number(self._data["properties"], name)

        elif prop_type == "checkbox":
            return PropertyParser.get_checkbox(self._data["properties"], name)

        elif prop_type == "date":
            return PropertyParser.get_date(self._data["properties"], name)

        elif prop_type in ["title", "rich_text", "text", "url", "email", "phone"]:
            # Text-like properties - use get_title for title type
            if prop_type == "title":
                text = PropertyParser.get_title(self._data["properties"], name)
            else:
                # For other text types, extract plain text
                text = PropertyParser.get_title(self._data["properties"], name)
            return text if text else default

        elif prop_type == "people":
            return PropertyParser.get_people(self._data["properties"], name)

        else:
            # Unknown type, return default
            return default

    def has_property(self, name: str) -> bool:
        """Check if property exists.

        Args:
            name: Property name (case-insensitive)

        Returns:
            True if property exists

        Example:
            >>> if page.has_property("Due Date"):
            ...     due_date = page.get_property("Due Date")
        """
        prop = PropertyParser._find_property(
            self._data.get("properties", {}),
            name
        )
        return prop is not None

    # ===== NAVIGATION =====

    async def parent(self) -> "Database | Page | None":
        """Get parent object (fetches if not cached).

        Returns:
            Parent Database or Page object
            None if this is a workspace-level object

        Behavior:
            - First call: Fetch from API, cache result
            - Subsequent calls: Return cached version (instant)

        Example:
            >>> parent = await page.parent()
            >>>
            >>> if isinstance(parent, Database):
            ...     print(f"In database: {parent.title}")
            ... else:
            ...     print(f"In page: {parent.title}")
        """
        # Check entity cache
        cached_parent = self._cache_get("parent")
        if cached_parent:
            return cached_parent

        # Fetch from API
        parent_data = self._data.get("parent", {})
        parent = await self._resolve_parent(parent_data)

        # Cache result
        if parent:
            self._cache_set("parent", parent)

        return parent

    async def children(self) -> AsyncIterator["Block"]:
        """Iterate over direct child blocks.

        Yields:
            Block objects that are direct children

        Note:
            Handles pagination automatically

        Example:
            >>> async for block in page.children():
            ...     if block.type == "code":
            ...         print(block.code)
        """
        from better_notion._api.utils.pagination import AsyncPaginatedIterator
        from better_notion._sdk.models.block import Block

        # Define fetch function
        async def fetch_fn(cursor: str | None) -> dict:
            params = {}
            if cursor:
                params["start_cursor"] = cursor

            return await self._client.api.blocks.children.list(
                block_id=self.id,
                **params
            )

        # Define item parser
        def item_parser(item_data: dict) -> Block:
            return Block(self._client, item_data)

        # Use paginated iterator
        iterator = AsyncPaginatedIterator(fetch_fn, item_parser)

        async for block in iterator:
            yield block

    # ===== CRUD OPERATIONS =====

    async def save(self) -> "Page":
        """Save changes to Notion.

        Returns:
            Updated page object

        Example:
            >>> await page.update(title="New Title")
            >>> await page.save()
        """
        # Stage changes are handled via update()
        # For now, just reload from API
        data = await self._client.api.pages.retrieve(page_id=self.id)

        # Update local data
        self._data = data

        # Clear cache
        self._cache_clear()

        return self

    # ===== HELPER METHODS =====

    def _find_title_property(self) -> str | None:
        """Find the title property name.

        Notion databases can name the title property anything
        (Name, Title, Task, etc.). This method finds which property
        is of type "title".

        Returns:
            Property name or None if not found
        """
        for prop_name, prop_data in self._data.get("properties", {}).items():
            if prop_data.get("type") == "title":
                return prop_name
        return None

    @classmethod
    def _find_title_property_in_schema(
        cls,
        parent: "Database | Page",
        client: "NotionClient"
    ) -> str | None:
        """Find title property in parent schema.

        Args:
            parent: Parent Database or Page
            client: NotionClient instance

        Returns:
            Title property name or None
        """
        # For now, use a common default
        # In production, would fetch parent's schema
        return "Name"

    async def _resolve_parent(
        self,
        parent_data: dict[str, Any]
    ) -> "Database | Page | None":
        """Resolve parent from API parent data.

        Args:
            parent_data: Parent dict from Notion API

        Returns:
            Parent object (Database or Page)
            None if workspace (no parent)
        """
        from better_notion._sdk.models.database import Database

        parent_type = parent_data.get("type")

        if parent_type == "database_id":
            db_id = parent_data["database_id"]
            # Check cache first
            if db_id in self._client.database_cache:
                return self._client.database_cache[db_id]
            # Fetch from API
            data = await self._client.api.databases.retrieve(database_id=db_id)
            return Database(self._client, data)

        elif parent_type == "page_id":
            page_id = parent_data["page_id"]
            # Check cache first
            if page_id in self._client.page_cache:
                return self._client.page_cache[page_id]
            # Fetch from API
            data = await self._client.api.pages.retrieve(page_id=page_id)
            return Page(self._client, data)

        elif parent_type == "workspace":
            # Root level - no parent
            return None

        elif parent_type == "block_id":
            block_id = parent_data["block_id"]
            # Blocks can have children, treat as page parent
            data = await self._client.api.blocks.retrieve(block_id=block_id)
            # If it's a block that behaves like a page, return Page
            if data.get("type") == "page":
                return Page(self._client, data)
            # Otherwise return as block
            from better_notion._sdk.models.block import Block
            return Block(self._client, data)

        return None

    def __repr__(self) -> str:
        """String representation."""
        title = self.title[:30] if self.title else ""
        return f"Page(id={self.id!r}, title={title!r})"
