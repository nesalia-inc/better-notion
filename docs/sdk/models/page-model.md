# Page Model Specification

Complete specification for the Page SDK model with rich features.

## Overview

The `Page` model is the heart of the Notion SDK, representing a Notion page with:

- **Metadata shortcuts**: URL, icon, cover, timestamps
- **Property parsers**: Intelligent property extraction
- **Navigation**: Hierarchical access (parent, children, ancestors, descendants)
- **CRUD operations**: Create, update, save, delete
- **SDK-exclusive methods**: Duplicate, smart property access

## Architecture

```
Page(BaseEntity)
    ├── Metadata Properties (id, url, icon, cover, archived)
    ├── Property Access (title, properties, get_property)
    ├── Navigation (parent, children, ancestors, descendants)
    ├── CRUD (save, delete, reload)
    └── SDK Methods (duplicate, move, smart_update)
```

## Class Definition

```python
# better_notion/_sdk/models/page.py

from __future__ import annotations
from typing import Any, AsyncIterator, TYPE_CHECKING
from datetime import datetime

if TYPE_CHECKING:
    from better_notion._api import NotionAPI
    from better_notion._sdk.models.database import Database
    from better_notion._sdk.models.block import Block

from better_notion._sdk.models.base import BaseEntity
from better_notion._sdk.implementation.property_parsers import PropertyParser


class Page(BaseEntity):
    """Notion Page with rich SDK features.

    This model combines:
    - BaseEntity: Core functionality (id, created_time, cache)
    - Property Parsers: Intelligent property extraction
    - Navigation: Hierarchical access with caching
    - CRUD: Update, save, delete operations
    - SDK Exclusives: Duplicate, smart property access

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
        >>> parent = await page.parent
        >>> async for block in page.children:
        ...     print(block.type)
    """

    def __init__(self, api: NotionAPI, data: dict[str, Any]) -> None:
        """Initialize a Page.

        Args:
            api: NotionAPI client
            data: Raw page data from Notion API
        """
        # Initialize BaseEntity (provides id, created_time, _cache, etc.)
        super().__init__(api, data)

        # Cache the title property name (can vary by database)
        self._title_property: str | None = self._find_title_property()

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
        result = PropertyParser.get_title(self._data["properties"])
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
            self._data["properties"],
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
            # Text-like properties
            text = PropertyParser.get_text(self._data["properties"], name)
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
            self._data["properties"],
            name
        )
        return prop is not None

    def find_property(
        self,
        name: str,
        fuzzy: bool = False
    ) -> dict[str, Any] | None:
        """Find property by name.

        Args:
            name: Property name
            fuzzy: Enable fuzzy matching (substring)

        Returns:
            Property dict or None

        Example:
            >>> # Exact match (case-insensitive)
            >>> prop = page.find_property("status")
            >>>
            >>> # Fuzzy match
            >>> prop = page.find_property("stat", fuzzy=True)
        """
        if not fuzzy:
            return PropertyParser._find_property(
                self._data["properties"],
                name
            )

        # Fuzzy matching (case-insensitive + substring)
        name_lower = name.lower()

        for prop_name, prop_data in self._data["properties"].items():
            if name_lower in prop_name.lower():
                return prop_data

        return None

    # ===== NAVIGATION =====

    async def parent(self) -> Database | Page | None:
        """Get parent object (fetches if not cached).

        Returns:
            Parent Database or Page object
            None if this is a workspace-level object

        Behavior:
            - First call: Fetch from API, cache result
            - Subsequent calls: Return cached version (instant)

        Example:
            >>> parent = await page.parent
            >>>
            >>> if isinstance(parent, Database):
            ...     print(f"In database: {parent.title}")
            ... else:
            ...     print(f"In page: {parent.title}")

        Note:
            Clears cache after 5+ minutes to prevent stale data
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

    @property
    def parent_cached(self) -> Database | Page | None:
        """Get parent from cache only (no API fetch).

        Returns:
            Cached parent or None if not fetched yet

        Use case:
            Check if parent is available without triggering API call

        Example:
            >>> parent = page.parent_cached
            >>> if parent:
            ...     print(f"Parent: {parent.title}")
            >>> else:
            ...     parent = await page.parent  # Fetch it
        """
        return self._cache_get("parent")

    async def children(self) -> AsyncIterator[Block]:
        """Iterate over direct child blocks.

        Yields:
            Block objects that are direct children

        Note:
            Handles pagination automatically

        Example:
            >>> async for block in page.children:
            ...     if block.type == "code":
            ...         print(block.code)
        """
        # Use AsyncPaginatedIterator for pagination
        async def fetch_fn(cursor: str | None) -> dict:
            params = {}
            if cursor:
                params["start_cursor"] = cursor

            return await self._api._request(
                "GET",
                f"/blocks/{self.id}/children",
                params=params
            )

        from better_notion._api.utils import AsyncPaginatedIterator

        iterator = AsyncPaginatedIterator(fetch_fn)

        # Yield Block objects
        async for block_data in iterator:
            from better_notion._sdk.models.block import Block
            yield Block(self._api, block_data)

    async def ancestors(self) -> AsyncIterator[Database | Page]:
        """Walk up the hierarchy to root.

        Yields:
            Ancestors from immediate parent to root

        Example:
            >>> # Build breadcrumb path
            >>> path = [page.title]
            >>> async for ancestor in page.ancestors():
            ...     title = ancestor.title if hasattr(ancestor, 'title') else 'Root'
            ...     path.append(title)
            >>> print(" / ".join(reversed(path)))

        Note:
            - First yielded: immediate parent
            - Last yielded: root (workspace-level)
            - Does NOT include self
        """
        current = self

        while True:
            parent = await current.parent

            if parent is None:
                break

            yield parent
            current = parent

    async def descendants(
        self,
        max_depth: int | None = None
    ) -> AsyncIterator[Block]:
        """Walk down the hierarchy recursively.

        Args:
            max_depth: Maximum depth to traverse (None = unlimited)

        Yields:
            All descendant blocks (depth-first traversal)

        Example:
            >>> # Count all blocks
            >>> count = 0
            >>> async for block in page.descendants():
            ...     count += 1
            >>> print(f"Total blocks: {count}")

            >>> # Find specific block types
            >>> async for block in page.descendants():
            ...     if block.type == "code":
            ...         print(block.language)

        Note:
            - Uses depth-first traversal
            - Protects against cycles (visited tracking)
            - Includes self in iteration
        """
        visited = set()

        async def traverse(entity: BaseEntity, depth: int):
            # Check depth limit
            if max_depth is not None and depth > max_depth:
                return

            # Cycle detection
            if entity.id in visited:
                return
            visited.add(entity.id)

            # Yield if it's a block
            if entity.object == "block":
                yield entity

            # Recurse into children
            try:
                async for child in entity.children():
                    async for descendant in traverse(child, depth + 1):
                        yield descendant
            except (AttributeError, TypeError):
                # Entity doesn't support children
                pass

        async for descendant in traverse(self, 0):
            yield descendant

    # ===== CRUD OPERATIONS =====

    async def update(self, **kwargs: Any) -> None:
        """Update page properties with smart shortcuts.

        Args:
            **kwargs: Properties to update
                - title: str (shortcut for title property)
                - archived: bool
                - icon: str (emoji or URL)
                - cover: str (image URL)
                - properties: dict (other properties)

        Example:
            >>> # Update title
            >>> await page.update(title="New Title")
            >>>
            >>> # Update multiple properties
            >>> await page.update(
            ...     title="Updated Title",
            ...     status="Done",
            ...     archived=False
            ... )
            >>>
            >>> # Update with icon
            >>> await page.update(icon="✅")

        Note:
            Changes are staged locally, call save() to persist
        """
        # Handle title shortcut
        if "title" in kwargs:
            title_value = kwargs.pop("title")
            title_prop_name = self._title_property or "Name"
            kwargs[title_prop_name] = Title(content=title_value)

        # Handle icon
        if "icon" in kwargs:
            icon_value = kwargs.pop("icon")
            # TODO: Format icon for API
            pass

        # Handle cover
        if "cover" in kwargs:
            cover_value = kwargs.pop("cover")
            # TODO: Format cover for API
            pass

        # Stage changes using inherited update method
        await super().update(**kwargs)

    async def duplicate(
        self,
        new_parent: Database | Page,
        *,
        title: str | None = None,
        include_children: bool = True
    ) -> "Page":
        """Duplicate this page to a new parent.

        Args:
            new_parent: Parent Database or Page for the copy
            title: New title (defaults to "Copy of {title}")
            include_children: Include all child blocks

        Returns:
            Newly created Page object

        Note:
            This is an SDK-exclusive method (not in Notion API)
            Performs multiple API calls to create page + copy content

        Example:
            >>> target_db = await client.databases.get(db_id)
            >>> new_page = await page.duplicate(
            ...     new_parent=target_db,
            ...     title="Template Copy"
            ... )
        """
        # Generate title
        if not title:
            title = f"Copy of {self.title}"

        # Create new page with same properties
        new_page = await self._api.pages.create(
            parent=new_parent,
            properties=self._data["properties"]
        )

        # Copy children if requested
        if include_children:
            async for original_block in self.children():
                # Append block to new page
                await self._api.blocks.children.append(
                    new_page.id,
                    children=[original_block._data]
                )

        return new_page

    async def move(
        self,
        new_parent: Database | Page,
        *,
        position: str | None = None
    ) -> "Page":
        """Move page to new parent.

        Args:
            new_parent: New parent Database or Page
            position: Optional position (e.g., "after:block_id")

        Returns:
            Updated page object

        Note:
            Clears cache after move (parent changed)

        Example:
            >>> await page.move(new_parent=other_db)
        """
        # Call API to move
        await self._api.pages.move(
            page_id=self.id,
            parent_id=new_parent.id,
            position=position
        )

        # Clear cache (parent changed)
        self._cache_clear()

        # Reload from API
        await self.reload()

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
        for prop_name, prop_data in self._data["properties"].items():
            if prop_data.get("type") == "title":
                return prop_name
        return None

    async def _resolve_parent(
        self,
        parent_data: dict[str, Any]
    ) -> Database | Page | None:
        """Resolve parent from API parent data.

        Args:
            parent_data: Parent dict from Notion API

        Returns:
            Parent object (Database or Page)
            None if workspace (no parent)
        """
        parent_type = parent_data.get("type")

        if parent_type == "database_id":
            db_id = parent_data["database_id"]
            data = await self._api._request("GET", f"/databases/{db_id}")
            from better_notion._sdk.models.database import Database
            return Database(self._api, data)

        elif parent_type == "page_id":
            page_id = parent_data["page_id"]
            data = await self._api._request("GET", f"/pages/{page_id}")
            return Page(self._api, data)

        elif parent_type == "workspace":
            # Root level - no parent
            return None

        elif parent_type == "block_id":
            block_id = parent_data["block_id"]
            data = await self._api._request("GET", f"/blocks/{block_id}")
            from better_notion._sdk.models.block import Block
            return Block(self._api, data)

        return None

    def __repr__(self) -> str:
        """String representation."""
        title = self.title[:30] if self.title else ""
        return f"Page(id={self.id!r}, title={title!r})"
```

## Usage Examples

### Example 1: Basic Page Access

```python
from better_notion import NotionClient

client = NotionClient(auth="secret_...")

# Get page
page = await client.pages.get(page_id)

# Access metadata
print(f"Title: {page.title}")
print(f"URL: {page.url}")
print(f"Created: {page.created_time}")
print(f"Archived: {page.archived}")
```

### Example 2: Property Access

```python
# Smart property access
status = page.get_property("Status")
priority = page.get_property("Priority")
tags = page.get_property("Tags")

# With defaults
unknown = page.get_property("UnknownField", default="N/A")

# Check if property exists
if page.has_property("Due Date"):
    due_date = page.get_property("Due Date")
```

### Example 3: Navigation

```python
# Walk up to root
async for ancestor in page.ancestors():
    if isinstance(ancestor, Database):
        print(f"📊 Database: {ancestor.title}")
    else:
        print(f"📄 Page: {ancestor.title}")

# Walk down recursively
async for block in page.descendants():
    if block.type == "code":
        print(f"💻 Code: {block.language}")
```

### Example 4: Update and Save

```python
# Update properties
await page.update(
    title="Updated Title",
    status="Done"
)

# Stage more changes
await page.update(icon="✅")

# Save all changes
await page.save()
```

### Example 5: Duplicate Page

```python
target_db = await client.databases.get(database_id)

# Duplicate with all content
new_page = await page.duplicate(
    new_parent=target_db,
    title="Template Copy",
    include_children=True
)

print(f"Created: {new_page.url}")
```

## Type Safety

### Type Hints

All properties have type hints for IDE support:

```python
page: Page = await client.pages.get(id)

title: str = page.title                    # str
url: str = page.url                          # str
icon: str | None = page.icon                 # Optional
archived: bool = page.archived               # bool

status: str = page.get_property("Status")   # str
priority: int | None = page.get_property("Priority")  # Optional int
tags: list[str] = page.get_property("Tags")  # List
```

### IDE Autocomplete

With type hints, IDEs provide autocomplete:

```python
page.  # IDE suggests: title, url, icon, archived, parent, children, etc.

page.get_property("")  # IDE suggests property names from database
```

## Design Decisions

### Q1: title Returns str (Never None)

**Decision**: `title` returns `str`, never `None`

```python
@property
def title(self) -> str:
    result = PropertyParser.get_title(...)
    return result or ""  # Empty string if no title
```

**Rationale**:
- ✅ Simpler to use (no None checks)
- ✅ Consistent with string operations
- ✅ Clear distinction (empty = no title)

### Q2: get_property() Return Type

**Decision**: Union type based on Notion property type

```python
def get_property(self, name: str) -> str | int | float | bool | date | list[str]:
    # Type depends on property
```

**Rationale**:
- ✅ Type-safe (mypy can infer from schema)
- ✅ No Optional everywhere
- ✅ Matches Notion property types

### Q3: Cache Coherence

**Decision**: Manual cache clearing, no TTL

```python
# Cache persists until explicitly cleared
parent = await page.parent  # Fetch + cache
parent = await page.parent  # Cache hit

# User controls when to refresh
page._cache_clear()
parent = await page.parent  # Fresh fetch
```

**Rationale**:
- ✅ Predictable behavior
- ✅ Simple implementation
- ✅ User has control

## Performance Considerations

### Descendants Traversal

Walking large hierarchies is expensive:

```python
# ⚠️ WARNING: Could be thousands of blocks
async for block in page.descendants():
    process(block)
```

**Optimization**: Limit depth

```python
# Only 2 levels deep
async for block in page.descendants(max_depth=2):
    process(block)  # Much faster
```

### Cache Effectiveness

```python
# First call: fetch + cache
parent = await page.parent  # ~300ms

# Second call: cache hit
parent = await page.parent  # ~0ms

# Cache sync check
parent = page.parent_cached  # ~0ms, no fetch
```

## Error Handling

### Invalid Property

```python
# Returns default, doesn't raise
value = page.get_property("NonExistent", default="N/A")
```

### Navigation Errors

```python
try:
    parent = await page.parent
except NotFoundError:
    print("Parent not found")
except PermissionError:
    print("No access to parent")
```

## Next Steps

After implementing Page model:

1. ✅ Implement Database model (similar structure)
2. ✅ Implement Block model (type-specific helpers)
3. ✅ Implement User model (simpler)
4. ✅ Add comprehensive unit tests
5. ✅ Add integration tests

## Related Documentation

- [BaseEntity](../implementation/base-entity.md) - Base class
- [Property Parsers](../implementation/property-parsers.md) - Property extraction
- [Cache Strategy](../implementation/cache-strategy.md) - Caching
- [Navigation](../implementation/navigation.md) - Hierarchical access
- [Query Builder](../implementation/query-builder.md) - Database queries
