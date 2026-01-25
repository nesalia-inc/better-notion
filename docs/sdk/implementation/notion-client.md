# NotionClient

Entry point for the Notion SDK with Managers as thin wrappers to autonomous entities.

## Overview

The `NotionClient` is the main entry point for interacting with Notion. It provides managers that act as **thin wrappers** to the autonomous entity classes (Page, Database, Block, User).

## Architecture

```
NotionClient
├── pages: PageManager (wrapper) → Page.get(), Page.create()
├── databases: DatabaseManager (wrapper) → Database.get(), Database.create()
├── blocks: BlockManager (wrapper) → Block.get(), Code.create(), etc.
└── users: UserManager (wrapper) → User.get(), User.populate_cache()
```

### Key Design: Managers as Wrappers

**Managers are ultra-thin**:
- They delegate ALL logic to entity classes
- Managers provide shortcuts: `client.pages.get()`
- Entities have all logic: `Page.get()`, `Page.create()`

**Both approaches work**:
```python
# Via Manager (recommended, shorter)
page = await client.pages.get(page_id)
new_page = await client.pages.create(database, title="...")

# Via Entity directly (autonomous)
page = await Page.get(page_id, client=client)
new_page = await Page.create(database, title="...", client=client)

# Same result, user's choice
```

## Why This Hybrid Approach?

1. **Convenience**: `client.pages.get()` is shorter and more discoverable
2. **Flexibility**: Can still use `Page.get()` directly when needed
3. **No Duplication**: Managers only wrap, they don't contain logic
4. **Entity Autonomy**: Entities are fully self-contained and reusable

### Manager Implementation Example

```python
class PageManager:
    """Ultra-thin wrapper to autonomous Page class."""

    def __init__(self, client: NotionClient):
        self._client = client

    async def get(self, id: str) -> Page:
        """Get page - delegates to Page.get()."""
        return await Page.get(id, client=self._client)

    async def create(
        self,
        parent: Database | Page,
        title: str,
        **properties
    ) -> Page:
        """Create page - delegates to Page.create()."""
        return await Page.create(
            parent=parent,
            title=title,
            client=self._client,
            **properties
        )

    async def find(
        self,
        database: Database,
        **filters
    ) -> list[Page]:
        """Find pages - delegates to database.query()."""
        return await database.query(
            client=self._client,
            **filters
        ).collect()

    @property
    def cache(self) -> Cache[Page]:
        """Cache access - delegates to client cache."""
        return self._client._page_cache
```

Notice: **Zero logic** in the manager. All it does is delegate.

## NotionClient Structure

```python
from pathlib import Path
from typing import Any

class NotionClient:
    """Notion SDK client with Managers.

    The client provides managers for each entity type and manages
    shared caches. Entity classes are autonomous and can be used
    directly if needed.

    Example:
        >>> # Initialize
        >>> client = NotionClient(auth=os.getenv("NOTION_KEY"))
        >>>
        >>> # Use managers (recommended)
        >>> page = await client.pages.get(page_id)
        >>> database = await client.databases.get(db_id)
        >>>
        >>> # Or use entities directly (advanced)
        >>> page = await Page.get(page_id, client=client)
    """

    def __init__(
        self,
        auth: str,
        base_url: str | None = None,
        timeout: float = 30.0
    ):
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
        self._user_cache: Cache[User] = Cache[User]()
        self._database_cache: Cache[Database] = Cache[Database]()
        self._page_cache: Cache[Page] = Cache[Page]()
        # No cache for Block (too many)

        # Search cache
        self._search_cache: dict[str, list[Page | Database]] = {}

        # Create managers
        self._pages = PageManager(self)
        self._databases = DatabaseManager(self)
        self._blocks = BlockManager(self)
        self._users = UserManager(self)

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

    # ===== DIRECT CACHE ACCESS =====

    @property
    def user_cache(self) -> Cache[User]:
        """Direct access to user cache.

        Example:
            >>> if user_id in client.user_cache:
            ...     user = client.user_cache[user_id]
        """
        return self._user_cache

    @property
    def database_cache(self) -> Cache[Database]:
        """Direct access to database cache."""
        return self._database_cache

    @property
    def page_cache(self) -> Cache[Page]:
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
    ) -> list[Page | Database]:
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
            >>>
            >>> # Search sorted by last edited
            >>> results = await client.search(
            ...     query="Meeting",
            ...     sort={"direction": "descending", "timestamp": "last_edited_time"}
            ... )
        """
        results = []

        async for result in self._api.search.query(
            query=query,
            filter=filter,
            sort=sort
        ):
            obj_type = result.get("object")

            if obj_type == "page":
                results.append(Page(self, result))
            elif obj_type == "database":
                results.append(Database(self, result))

        return results

    async def smart_search(
        self,
        query: str = "",
        types: list[str] | None = None,
        filters: dict[str, Any] | None = None,
        sort: str = "relevance",
        limit: int = 100
    ) -> list[Page | Database | Block]:
        """Advanced search with cache and multiple filters.

        Args:
            query: Search query
            types: Entity types ["page", "database", "block"]
            filters: Additional filters (in_database, created_by, etc.)
            sort: "relevance" or "last_edited"
            limit: Max results

        Returns:
            List of matching entities

        Example:
            >>> # Pages with "API" in specific database
            >>> results = await client.smart_search(
            ...     query="API",
            ...     types=["page"],
            ...     filters={"in_database": db_id},
            ...     limit=20
            ... )
        """
        # Check cache
        cache_key = f"{query}:{types}:{filters}:{sort}:{limit}"
        if cache_key in self._search_cache:
            return self._search_cache[cache_key]

        # Build filter
        filter_obj = {}
        if types and len(types) == 1:
            filter_obj["value"] = types[0]
            filter_obj["property"] = "object"

        # Sort
        sort_obj = None
        if sort == "last_edited":
            sort_obj = {
                "direction": "descending",
                "timestamp": "last_edited_time"
            }

        # Execute search
        results = []
        async for result in self._api.search.query(
            query=query,
            filter=filter_obj if filter_obj else None,
            sort=sort_obj
        ):
            if len(results) >= limit:
                break

            obj_type = result.get("object")

            # Apply additional filters
            if filters:
                if "in_database" in filters:
                    if result.get("parent", {}).get("database_id") != filters["in_database"]:
                        continue
                if "created_by" in filters:
                    if result.get("created_by") != filters["created_by"]:
                        continue

            # Create entity
            if obj_type == "page":
                results.append(Page(self, result))
            elif obj_type == "database":
                results.append(Database(self, result))
            elif obj_type == "block":
                results.append(Block.from_data(self, result))

        # Cache result
        self._search_cache[cache_key] = results

        return results

    # ===== EXPORT =====

    async def export_database(
        self,
        database_id: str,
        format: str = "markdown",
        output_dir: Path | None = None
    ) -> Path:
        """Export entire database to files.

        Args:
            database_id: Database to export
            format: Export format ("markdown", "json", "csv")
            output_dir: Output directory (default: ./export_{title})

        Returns:
            Path to export directory

        Example:
            >>> await client.export_database(
            ...     database_id=db_id,
            ...     format="markdown",
            ...     output_dir=Path("./export")
            ... )
        """
        database = await Database.get(database_id, client=self)

        if output_dir is None:
            output_dir = Path(f"./export_{database.title.replace(' ', '_')}")
        output_dir.mkdir(parents=True, exist_ok=True)

        if format == "markdown":
            async for page in database.query(client=self):
                markdown = await page.to_markdown(client=self)
                filename = f"{page.title.replace('/', '-')}.md"
                (output_dir / filename).write_text(markdown)

        elif format == "json":
            pages = []
            async for page in database.query(client=self):
                pages.append(page._data)

            import json
            (output_dir / "database.json").write_text(
                json.dumps(pages, indent=2)
            )

        elif format == "csv":
            import csv

            rows = []
            async for page in database.query(client=self):
                row = {"id": page.id, "title": page.title}
                for prop in database.schema.keys():
                    value = page.get_property(prop)
                    row[prop] = str(value) if value is not None else ""
                rows.append(row)

            if rows:
                with open(output_dir / "database.csv", "w") as f:
                    writer = csv.DictWriter(f, fieldnames=rows[0].keys())
                    writer.writeheader()
                    writer.writerows(rows)

        return output_dir

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
```

## Usage Examples

### Example 1: Basic Usage

```python
import os
from better_notion import NotionClient

# Initialize
client = NotionClient(auth=os.getenv("NOTION_KEY"))

# Get page
page = await client.pages.get(page_id)
print(f"Title: {page.title}")

# Get database
database = await client.databases.get(db_id)
print(f"Database: {database.title}")
```

### Example 2: Creating Content

```python
# Get parent database
database = await client.databases.get(db_id)

# Create page
page = await client.pages.create(
    parent=database,
    title="New Task",
    status="Todo",
    priority=5
)

# Add content
await client.blocks.create_paragraph(
    parent=page,
    text="Introduction"
)

code = await client.blocks.create_code(
    parent=page,
    code="print('Hello')",
    language="python"
)
```

### Example 3: Querying

```python
# Get database
database = await client.databases.get(db_id)

# Query with filters
pages = await database.query(client=client)\
    .filter(status="In Progress")\
    .filter(priority__gte=5)\
    .sort("Due Date", "ascending")\
    .limit(10)\
    .collect()

for page in pages:
    print(f"{page.title}")
```

### Example 4: Cache Management

```python
# Populate user cache
await client.users.populate_cache()

# Use cache
pages = await database.query(client=client).collect()
for page in pages:
    creator = client.user_cache.get(page.created_by)
    if creator:
        print(f"Created by: {creator.name}")

# Check stats
stats = client.get_cache_stats()
print(f"Hit rate: {stats['user_cache']['hit_rate']:.1%}")
```

### Example 5: Context Manager

```python
async with NotionClient(auth=os.getenv("NOTION_KEY")) as client:
    # Do work
    page = await client.pages.get(page_id)
    await page.update(client=client, status="Done")

    # Caches auto-cleared on exit
```

## Design Decisions

### Q1: Why Managers if entities are autonomous?

**Decision**: Both Managers and autonomous entities

**Rationale**:
- **Managers**: Clean, discoverable API (`client.pages.get()`)
- **Autonomous entities**: Reusable logic, can be used directly
- **Best of both**: Familiar pattern + flexibility

```python
# Manager usage (recommended)
page = await client.pages.get(page_id)

# Direct entity usage (advanced)
page = await Page.get(page_id, client=client)

# Both work, same result
```

### Q2: Managers store reference or delegate to entities?

**Decision**: Delegate to entity classes

```python
class PageManager:
    async def get(self, id: str) -> Page:
        # Delegates to Page class
        return await Page.get(id, client=self._client)
```

**Rationale**:
- No code duplication
- Single source of truth (entity class)
- Managers are thin facades

### Q3: Client stores managers or creates them?

**Decision**: Create in `__init__`

```python
def __init__(self, auth):
    self._pages = PageManager(self)
    self._databases = DatabaseManager(self)
```

**Rationale**:
- Managers live as long as client
- Single instance per manager
- Simple property access

### Q4: Cache location?

**Decision**: In client, accessed by managers and entities

```python
# In client
self._user_cache = Cache[User]()

# In manager
async def get(self, id):
    cached = self._client._user_cache.get(id)
    ...

# In entity
@classmethod
async def get(cls, id, client):
    cached = client._user_cache.get(id)
    ...
```

**Rationale**:
- Shared between managers and entities
- Single source of cache
- Managed by client (owner)

## Relationship to Entity Classes

```
NotionClient
    │
    ├── owns → caches (_user_cache, etc.)
    │
    └── owns → managers (PageManager, etc.)
              │
              └── delegates to → entity classes (Page, Database, etc.)
```

## Related Documentation

- [PageManager](../managers/page-manager.md) - Page operations
- [DatabaseManager](../managers/database-manager.md) - Database operations
- [BlockManager](../managers/block-manager.md) - Block operations
- [UserManager](../managers/user-manager.md) - User operations
- [Page Model](../models/page-model.md) - Page entity
- [Entity-Oriented Architecture](./entity-oriented-architecture.md) - Overall architecture
