# PageManager

Ultra-thin wrapper to autonomous Page class.

## Overview

`PageManager` is a **zero-logic wrapper** that delegates all operations to the autonomous `Page` class. It provides convenient shortcuts through the `NotionClient` interface.

**Key Principle**: Managers provide syntactic sugar. Entities contain all logic.

```python
# Via Manager (recommended - shorter)
page = await client.pages.get(page_id)

# Via Entity directly (autonomous - same result)
page = await Page.get(page_id, client=client)
```

## Architecture

```
NotionClient
    └── pages: PageManager
              └── delegates to → Page (autonomous)
```

### Manager Responsibilities

1. **Store client reference**: Hold `NotionClient` instance
2. **Delegate to entities**: Pass client to entity class methods
3. **Provide shortcuts**: Convenient method names
4. **Access cache**: Expose client's page cache

### What Managers DON'T Do

- ❌ Contain business logic
- ❌ Store state (except client reference)
- ❌ Make API calls directly
- ❌ Implement filtering or sorting

## Implementation

```python
# better_notion/_sdk/managers/page_manager.py

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from better_notion._sdk.client import NotionClient
    from better_notion._sdk.models.page import Page
    from better_notion._sdk.models.database import Database

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
            >>>
            >>> # Get all cached pages
            >>> all_pages = client.pages.cache.get_all()
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
```

## Usage Examples

### Example 1: Basic CRUD

```python
# Get page
page = await client.pages.get(page_id)
print(f"Title: {page.title}")

# Create page
db = await client.databases.get(db_id)
new_page = await client.pages.create(
    parent=db,
    title="Project Plan",
    status="Planning",
    priority=1
)

# Update page
await new_page.update(
    client=client,
    status="In Progress"
)
```

### Example 2: Finding Pages

```python
# Find by single filter
db = await client.databases.get(db_id)
done_pages = await client.pages.find(
    database=db,
    status="Done"
)

# Find by multiple filters
urgent_pages = await client.pages.find(
    database=db,
    status="Todo",
    priority__gte=8
)

# Find first match
page = await client.pages.find_one(
    database=db,
    title="Specific Task"
)
```

### Example 3: Cache Usage

```python
# Populate cache by querying
db = await client.databases.get(db_id)
pages = await client.pages.find(database=db)

# Check cache stats
stats = client.get_cache_stats()
print(f"Page cache hit rate: {stats['page_cache']['hit_rate']:.1%}")

# Access cache directly
if page_id in client.pages.cache:
    page = client.pages.cache[page_id]  # No API call
```

### Example 4: Bulk Operations

```python
# Get multiple pages
page_ids = ["id1", "id2", "id3"]
pages = await client.pages.get_multiple(page_ids)

# Process all
for page in pages:
    print(f"{page.title}: {page.get_property('Status')}")
```

## Design Decisions

### Q1: Why managers if entities are autonomous?

**Decision**: Both managers and autonomous entities

**Rationale**:
- **Managers**: Convenient, discoverable API (`client.pages.get()`)
- **Autonomous entities**: Reusable, testable without client
- **Best of both**: Familiar pattern + flexibility

```python
# Manager usage (recommended for most cases)
page = await client.pages.get(page_id)

# Direct entity usage (advanced, for special cases)
page = await Page.get(page_id, client=client)

# Both work, same result
```

### Q2: Managers store pages or delegate?

**Decision**: Delegate to Page class

```python
class PageManager:
    async def get(self, page_id: str) -> Page:
        # DELEGATES - no logic here
        return await Page.get(page_id, client=self._client)
```

**Rationale**:
- Single source of truth (Page class)
- No code duplication
- Manager is just a facade
- Entities can be used independently

### Q3: Manager methods mirror entity methods?

**Decision**: Yes, 1-to-1 mapping

```python
# Manager
client.pages.get(id)
client.pages.find(db, **filters)

# Entity
Page.get(id, client=client)
Database.query(client=client, **filters)
```

**Rationale**:
- Consistent API
- Easy to remember
- Manager is just a shortcut to entity

### Q4: Cache location?

**Decision**: In NotionClient, accessed by manager

```python
# In client
self._page_cache = Cache[Page]()

# In manager
@property
def cache(self) -> Cache[Page]:
    return self._client._page_cache
```

**Rationale**:
- Cache owned by client (shared across managers)
- Manager provides convenient access
- Single cache instance per client

## Comparison: Manager vs Entity

### Via Manager (Recommended)

```python
# ✅ Shorter syntax
page = await client.pages.get(page_id)
new_page = await client.pages.create(db, title="...")

# ✅ Discoverable (IDE autocomplete)
client.pages.<TAB>
# .get(), .create(), .find(), .cache

# ✅ Consistent pattern
client.pages.get()
client.databases.get()
client.blocks.get()
```

### Via Entity (Advanced)

```python
# ✅ Autonomous - can be tested without client
page = await Page.get(page_id, client=client)

# ✅ More control
page = Page.from_data(client, data)  # From existing data

# ✅ Reusable in different contexts
async def process_page(page_id: str, client: NotionClient):
    page = await Page.get(page_id, client=client)
    # ...
```

## Best Practices

### DO ✅

```python
# Use managers for typical operations
page = await client.pages.get(page_id)

# Use cache to avoid duplicate calls
if page_id not in client.pages.cache:
    page = await client.pages.get(page_id)

# Use find() for database queries
pages = await client.pages.find(database=db, status="Done")
```

### DON'T ❌

```python
# Don't use manager for entity-specific logic
# Use the page object directly
page = await client.pages.get(page_id)
await page.update(client=client, title="New")  # ✅

# Don't bypass cache unnecessarily
# Bad: Always makes API call
page1 = await Page.get(page_id, client=client)
page2 = await Page.get(page_id, client=client)

# Good: Uses cache
page1 = await client.pages.get(page_id)
page2 = await client.pages.cache.get(page_id)  # Instant
```

## Related Documentation

- [NotionClient](../implementation/notion-client.md) - Client with managers
- [Page Model](../models/page-model.md) - Autonomous Page entity
- [Cache Strategy](../implementation/cache-strategy.md) - Cache implementation
- [Query Builder](../implementation/query-builder.md) - Database querying
