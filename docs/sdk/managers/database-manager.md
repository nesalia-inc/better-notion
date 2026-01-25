# DatabaseManager

Ultra-thin wrapper to autonomous Database class.

## Overview

`DatabaseManager` is a **zero-logic wrapper** that delegates all operations to the autonomous `Database` class. It provides convenient shortcuts through the `NotionClient` interface.

**Key Principle**: Managers provide syntactic sugar. Entities contain all logic.

```python
# Via Manager (recommended - shorter)
database = await client.databases.get(db_id)

# Via Entity directly (autonomous - same result)
database = await Database.get(db_id, client=client)
```

## Architecture

```
NotionClient
    └── databases: DatabaseManager
              └── delegates to → Database (autonomous)
```

## Implementation

```python
# better_notion/_sdk/managers/database_manager.py

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from better_notion._sdk.client import NotionClient
    from better_notion._sdk.models.database import Database
    from better_notion._sdk.models.page import Page

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

        for result in results:
            if result.object == "database" and result.title.lower() == title.lower():
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
            >>>
            >>> # Get all cached databases
            >>> all_dbs = client.databases.cache.get_all()
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

        return [r for r in results if r.object == "database"]
```

## Usage Examples

### Example 1: Basic CRUD

```python
# Get database
db = await client.databases.get(db_id)
print(f"Database: {db.title}")
print(f"Properties: {', '.join(db.schema.keys())}")

# Create database
parent_page = await client.pages.get(parent_id)
new_db = await client.databases.create(
    parent=parent_page,
    title="Projects",
    schema={
        "Name": {"type": "title"},
        "Status": {"type": "select", "options": [
            {"name": "Planning"},
            {"name": "In Progress"},
            {"name": "Done"}
        ]},
        "Priority": {"type": "number"}
    }
)
```

### Example 2: Finding Databases

```python
# Find by title
db = await client.databases.find_by_title("Tasks")
if db:
    print(f"Found: {db.title}")

# List all databases
all_dbs = await client.databases.list_all()
print(f"Workspace has {len(all_dbs)} databases")
```

### Example 3: Querying via Database

```python
# Get database
db = await client.databases.get(db_id)

# Query with filters (delegates to database.query)
pages = await db.query(
    client=client,
    status="In Progress",
    priority__gte=5
).collect()

for page in pages:
    print(f"{page.title}: {page.get_property('Status')}")
```

### Example 4: Schema Introspection

```python
db = await client.databases.get(db_id)

# Get all properties
for prop_name, prop_def in db.schema.items():
    prop_type = prop_def["type"]
    print(f"{prop_name}: {prop_type}")

# Check if property exists
if "Due Date" in db.schema:
    print("Has due date property")

# Get select options
status_def = db.schema.get("Status", {})
if status_def["type"] == "select":
    options = [opt["name"] for opt in status_def["select"]["options"]]
    print(f"Status options: {', '.join(options)}")
```

## Design Decisions

### Q1: Why list_all() instead of find()?

**Decision**: `list_all()` returns all databases

**Rationale**:
- Databases are typically fewer than pages
- Unlike `find()`, no filters needed
- Clear naming: "list all" vs "find specific"

```python
# List all databases
all_dbs = await client.databases.list_all()

# Find specific pages in database
pages = await client.pages.find(database=db, status="Done")
```

### Q2: Create requires schema?

**Decision**: Yes, schema is required parameter

**Rationale**:
- Database without schema is useless
- Forces explicit schema definition
- Matches Notion API requirements

```python
db = await client.databases.create(
    parent=page,
    title="Tasks",
    schema={  # Required - defines structure
        "Name": {"type": "title"},
        "Status": {"type": "select", ...}
    }
)
```

### Q3: Query in manager or database?

**Decision**: In database, not manager

**Rationale**:
- Query is database-specific
- Database has schema for type inference
- Manager doesn't need query logic

```python
# ✅ Correct: Query via database
db = await client.databases.get(db_id)
pages = await db.query(client=client, status="Done").collect()

# ❌ Wrong: Manager doesn't have query()
pages = await client.databases.query(db_id, status="Done")  # Doesn't exist
```

## Comparison: Manager vs Entity

### Via Manager (Recommended)

```python
# ✅ Shorter syntax
db = await client.databases.get(db_id)
new_db = await client.databases.create(page, title="...", schema={...})

# ✅ Discoverable
client.databases.<TAB>
# .get(), .create(), .find_by_title(), .list_all()
```

### Via Entity (Advanced)

```python
# ✅ Autonomous
db = await Database.get(db_id, client=client)

# ✅ From data
db = Database.from_data(client, data)
```

## Best Practices

### DO ✅

```python
# Use managers for typical operations
db = await client.databases.get(db_id)

# Use cache for frequently accessed databases
if db_id not in client.databases.cache:
    db = await client.databases.get(db_id)

# Query via database object
db = await client.databases.get(db_id)
pages = await db.query(client=client, status="Done").collect()
```

### DON'T ❌

```python
# Don't create databases without schema
# This will fail
db = await client.databases.create(page, title="Tasks")

# Don't forget: queries happen on database, not manager
# Wrong
pages = await client.databases.query(...)  # Doesn't exist

# Right
db = await client.databases.get(db_id)
pages = await db.query(client=client, ...).collect()
```

## Related Documentation

- [NotionClient](../implementation/notion-client.md) - Client with managers
- [Database Model](../models/database-model.md) - Autonomous Database entity
- [Query Builder](../implementation/query-builder.md) - Database querying
- [Cache Strategy](../implementation/cache-strategy.md) - Cache implementation
