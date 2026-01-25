# Database Model

High-level Database SDK model combining BaseEntity, PropertyParsers, Cache, Navigation, and Query Builder.

## Overview

The `Database` model represents a Notion database with intelligent property access, schema introspection, and powerful querying capabilities.

```python
# Access database
database = await client.databases.get(database_id)

# Schema introspection
for prop_name, prop_def in database.schema.items():
    print(f"{prop_name}: {prop_def['type']}")

# Query with Pythonic syntax
pages = await database.query().filter(
    status="In Progress",
    priority__gte=5
).collect()

# Navigation
async for page in database.children:
    print(page.title)
```

## Architecture

### Database Class Structure

```python
# better_notion/_sdk/models/database.py

from better_notion._sdk.models.base import BaseEntity
from better_notion._sdk.implementation.query_builder import DatabaseQuery
from typing import Any

class Database(BaseEntity):
    """SDK Database model with schema and query capabilities."""

    def __init__(self, api: NotionAPI, data: dict[str, Any]) -> None:
        """Initialize database with API response data.

        Args:
            api: Low-level NotionAPI client
            data: Database object from Notion API
        """
        super().__init__(api, data)

        # Cache schema
        self._schema: dict[str, dict[str, Any]] = self._parse_schema()

    @property
    def object(self) -> str:
        """Object type (always "database")."""
        return "database"
```

## Properties

### Metadata Properties

```python
@property
def title(self) -> str:
    """Get database title.

    Returns:
        Database title (empty string if no title)

    Example:
        >>> database.title
        'Project Tasks'
    """
    # Title is in description array
    title_array = self._data.get("title", [])
    if title_array and title_array[0].get("type") == "text":
        return title_array[0]["text"]["content"]
    return ""

@property
def description(self) -> str:
    """Get database description.

    Returns:
        Database description (empty string if no description)
    """
    desc_array = self._data.get("description", [])
    if desc_array and desc_array[0].get("type") == "text":
        return desc_array[0]["text"]["content"]
    return ""

@property
def icon(self) -> str | None:
    """Get database icon (emoji or URL).

    Returns:
        Icon emoji string or URL, or None
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
    """Check if database is inline (appears in parent page).

    Returns:
        True if database is inline
    """
    # Notion doesn't explicitly mark inline vs full-page
    # We infer from parent type
    parent = self._data.get("parent", {})
    return parent.get("type") in ("page_id", "database_id")
```

### Schema Properties

```python
@property
def schema(self) -> dict[str, dict[str, Any]]:
    """Get database property schema.

    Returns:
        Dict mapping property names to their schema definitions

    Example:
        >>> for name, def in database.schema.items():
        ...     print(f"{name}: {def['type']}")

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
        schema[prop_name] = {
            "type": prop_data.get("type"),
            "id": prop_data.get("id")  # Internal UUID
        }

        # Add type-specific info
        prop_type = prop_data.get("type")

        if prop_type == "select":
            options = prop_data.get("select", {}).get("options", [])
            schema[prop_name]["options"] = [opt["name"] for opt in options]

        elif prop_type == "multi_select":
            options = prop_data.get("multi_select", {}).get("options", [])
            schema[prop_name]["options"] = [opt["name"] for opt in options]

        elif prop_type == "number":
            schema[prop_name]["format"] = prop_data.get("number", {}).get("format")

        elif prop_type == "formula":
            schema[prop_name]["expression"] = prop_data.get("formula", {}).get("expression")

        elif prop_type == "relation":
            schema[prop_name]["database_id"] = prop_data.get("relation", {}).get("database_id")
            schema[prop_name]["dual_property"] = prop_data.get("relation", {}).get("dual_property", {}).get("id")

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
        >>> database.get_property_type("Due Date")
        'date'
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
        ['Not Started', 'In Progress', 'Done', 'Blocked']
    """
    prop_name_lower = property_name.lower()

    for name, schema in self._schema.items():
        if name.lower() == prop_name_lower:
            prop_type = schema["type"]

            if prop_type not in ("select", "multi_select"):
                raise ValueError(f"Property '{property_name}' is {prop_type}, not select/multi_select")

            return schema.get("options", [])

    raise ValueError(f"Property '{property_name}' not found")
```

### Configuration Properties

```python
@property
def sort_properties(self) -> list[dict[str, Any]]:
    """Get default sort configuration.

    Returns:
        List of sort configurations
    """
    # Notion databases can have default sort orders
    # This is available in some API responses
    return self._data.get("sorts", [])

def get_default_view(self) -> dict[str, Any] | None:
    """Get default view configuration.

    Returns:
        Default view data or None

    Note:
        Views are not directly exposed in API
        This would require additional endpoint calls
    """
    # Would need to fetch from /databases/{id}?with_views=true
    # Placeholder for future enhancement
    return None
```

## Querying

### Query Builder

```python
def query(self, **filters) -> DatabaseQuery:
    """Create query for this database.

    Args:
        **filters: Initial filter conditions

    Returns:
        DatabaseQuery builder object

    Example:
        >>> # Simple query
        >>> pages = await database.query(status="Done").collect()

        >>> # Complex query
        >>> pages = await database.query()
        ...     .filter(status="In Progress")
        ...     .filter(priority__gte=5)
        ...     .sort("Due Date", "ascending")
        ...     .limit(10)
        ...     .collect()
    """
    from better_notion._sdk.implementation.query_builder import DatabaseQuery

    return DatabaseQuery(
        api=self._api,
        database_id=self.id,
        schema=self._schema,
        initial_filters=filters
    )

async def query_all(self) -> list[Page]:
    """Query all pages in database (no filters).

    Returns:
        List of all pages in database

    Example:
        >>> pages = await database.query_all()
        >>> print(f"Total pages: {len(pages)}")
    """
    pages = []

    async for page in self.children():
        pages.append(page)

    return pages

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
```

## Navigation

### Children (Pages)

```python
async def children(self) -> AsyncIterator[Page]:
    """Iterate over pages in this database.

    Yields:
        Page objects from this database

    Example:
        >>> async for page in database.children:
        ...     print(page.title)

    Note:
        Uses database query API with automatic pagination
        Equivalent to query() without filters
    """
    from better_notion._api.utils import AsyncPaginatedIterator
    from better_notion._sdk.models.page import Page

    async def fetch_fn(cursor: str | None) -> dict:
        body = {}
        if cursor:
            body["start_cursor"] = cursor

        return await self._api._request(
            "POST",
            f"/databases/{self.id}/query",
            json=body
        )

    iterator = AsyncPaginatedIterator(fetch_fn)

    async for page_data in iterator:
        yield Page(self._api, page_data)

async def parent(self) -> Page | Block | None:
    """Get parent object (fetches if not cached).

    Returns:
        Parent Page or Block object, or None if workspace root

    Example:
        >>> parent = await database.parent
        >>> if isinstance(parent, Page):
        ...     print(f"Database in page: {parent.title}")
    """
    # Check cache first
    cached_parent = self._cache_get("parent")
    if cached_parent:
        return cached_parent

    # Fetch from API
    parent_data = self._data.get("parent", {})

    if parent_data.get("type") == "page_id":
        page_id = parent_data["page_id"]
        data = await self._api._request("GET", f"/pages/{page_id}")
        from better_notion._sdk.models.page import Page
        parent = Page(self._api, data)
    elif parent_data.get("type") == "workspace":
        parent = None
    else:
        parent = None

    # Cache result
    if parent:
        self._cache_set("parent", parent)

    return parent

@property
def parent_cached(self) -> Page | Block | None:
    """Get parent from cache only (no fetch).

    Returns:
        Cached parent or None if not fetched yet
    """
    return self._cache_get("parent")
```

## CRUD Operations

### Update Database

```python
async def update(self, **kwargs) -> None:
    """Update database metadata.

    Args:
        **kwargs: Fields to update (title, description, icon, cover)

    Example:
        >>> await database.update(
        ...     title="New Title",
        ...     description="Updated description",
        ...     icon="📊"
        ... )

    Note:
        Does NOT update schema/properties
        Use schema management methods for that
    """
    # Build update payload
    updates = {}

    if "title" in kwargs:
        updates["title"] = [
            {"type": "text", "text": {"content": kwargs["title"]}}
        ]

    if "description" in kwargs:
        updates["description"] = [
            {"type": "text", "text": {"content": kwargs["description"]}}
        ]

    if "icon" in kwargs:
        icon = kwargs["icon"]
        if isinstance(icon, str) and len(icon) <= 2:
            # Emoji
            updates["icon"] = {"type": "emoji", "emoji": icon}
        else:
            # URL
            updates["icon"] = {"type": "external", "external": {"url": icon}}

    if "cover" in kwargs:
        updates["cover"] = {"type": "external", "external": {"url": kwargs["cover"]}}

    # Call API
    data = await self._api._request(
        "PATCH",
        f"/databases/{self.id}",
        json=updates
    )

    # Update internal data
    self._data.update(data)

    # Clear schema cache if structure changed
    self._cache_clear()
```

## SDK-Exclusive Methods

### Schema Introspection

```python
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
        ...     pages = await database.query().filter(
        ...         due_date__is_not_empty=True
        ...     ).collect()
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
        fuzzy: Enable fuzzy matching

    Returns:
        Property schema dict or None

    Example:
        >>> prop = database.find_property("stat", fuzzy=True)
        >>> print(prop["type"])  # 'select'
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
```

### Analytics

```python
async def get_stats(self) -> dict[str, Any]:
    """Get database statistics.

    Returns:
        Dict with count, properties, etc.

    Example:
        >>> stats = await database.get_stats()
        >>> print(f"Pages: {stats['page_count']}")
        >>> print(f"Properties: {stats['property_count']}")
    """
    page_count = await self.count()

    return {
        "id": self.id,
        "title": self.title,
        "page_count": page_count,
        "property_count": len(self._schema),
        "property_types": {
            prop_type: sum(1 for s in self._schema.values() if s["type"] == prop_type)
            for prop_type in set(s["type"] for s in self._schema.values())
        },
        "is_inline": self.is_inline,
        "archived": self.archived
    }
```

## Usage Examples

### Example 1: Schema Discovery

```python
async def explore_database(database_id: str):
    """Explore database structure."""
    database = await client.databases.get(database_id)

    print(f"Database: {database.title}")
    print(f"Description: {database.description}")
    print(f"\nProperties ({len(database.schema)}):")

    for prop_name, prop_def in database.schema.items():
        prop_type = prop_def["type"]

        if prop_type in ("select", "multi_select"):
            options = prop_def.get("options", [])
            print(f"  • {prop_name}: {prop_type} ({', '.join(options)})")
        else:
            print(f"  • {prop_name}: {prop_type}")
```

### Example 2: Advanced Querying

```python
async def get_high_priority_tasks(database_id: str):
    """Get high priority incomplete tasks."""
    database = await client.databases.get(database_id)

    pages = await database.query().filter(
        status__in=["Not Started", "In Progress"],
        priority__gte=7,
        due_date__before=datetime(2025, 2, 1)
    ).sort("priority", "descending").limit(20).collect()

    return pages
```

### Example 3: Property Type Discovery

```python
async def safe_filter(database: Database, property_name: str, value: Any):
    """Filter with type checking."""
    prop_type = database.get_property_type(property_name)

    if not prop_type:
        raise ValueError(f"Property '{property_name}' not found")

    # Build appropriate filter based on type
    if prop_type == "select":
        return await database.query(**{property_name: value}).collect()
    elif prop_type == "number":
        return await database.query(**{f"{property_name}__gte": value}).collect()
    # ... etc
```

## Design Decisions

### Q1: Should schema be cached?

**Decision**: Yes, cache on initialization

**Rationale**:
- Schema rarely changes during database lifetime
- Frequently accessed (every query needs it)
- Small memory footprint (~1-5 KB)

```python
def __init__(self, api, data):
    super().__init__(api, data)
    self._schema = self._parse_schema()  # Parse once
```

### Q2: Case-insensitive property names?

**Decision**: Yes, in all schema methods

**Rationale**:
- Notion property names are user-defined
- Users may not remember exact casing
- Consistent with Page model behavior

```python
# All work
database.get_property_type("Status")
database.get_property_type("status")
database.get_property_type("STATUS")
```

### Q3: query() vs children()?

**Decision**: Both, with different purposes

- `query()`: Full filtering, sorting, limiting
- `children()`: Simple iteration over all pages

```python
# With filters
pages = await database.query(status="Done").collect()

# All pages
async for page in database.children():
    print(page.title)
```

### Q4: Schema mutation methods?

**Decision**: NOT in initial version

**Rationale**:
- Schema changes are destructive operations
- Better handled via low-level API initially
- Can add SDK helpers later once pattern established

```python
# ❌ NOT in initial SDK
await database.add_property("NewField", type="number")

# ✅ Use low-level API for now
await api.databases.update(database_id, properties=[...])
```

## Type Safety

### Property Type Guarantees

```python
def get_property_type(self, property_name: str) -> str | None:
    """Returns one of the Notion property types:

    'title' | 'rich_text' | 'number' | 'select' | 'multi_select' |
    'date' | 'checkbox' | 'url' | 'email' | 'phone' |
    'formula' | 'relation' | 'rollup' | 'people' | 'files' |
    'created_time' | 'created_by' | 'last_edited_time' | 'last_edited_by'
    """
```

### Schema Inference for Query Builder

```python
# Query builder uses schema for type inference
query = database.query(status="Done")
# Database knows "status" is select → uses select.equals

query = database.query(priority__gte=5)
# Database knows "priority" is number → uses number.greater_than_or_equal_to
```

## Error Handling

### Property Not Found

```python
prop_type = database.get_property_type("NonExistent")
# Returns None (doesn't raise)

if prop_type is None:
    print("Property not found")
```

### Wrong Property Type

```python
try:
    options = database.get_property_options("Count")
except ValueError as e:
    print(e)  # "Property 'Count' is number, not select/multi_select"
```

## Next Steps

After Database model:

1. **Block Model** - Content blocks with type-specific access
2. **User Model** - User with profile information
3. **Managers** - High-level managers that use these models

## Related Documentation

- [BaseEntity](../implementation/base-entity.md) - Foundation class
- [Query Builder](../implementation/query-builder.md) - Query implementation
- [Page Model](./page-model.md) - Database children (pages)
- [Navigation](../implementation/navigation.md) - Hierarchical traversal
