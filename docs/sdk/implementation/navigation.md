# Navigation

Hierarchical navigation patterns for traversing Notion's tree structure.

## Overview

Notion is fundamentally hierarchical. Understanding and navigating parent-child relationships is crucial for many operations:

```
Workspace (root)
  ├─ Database
  │   └─ Page
  │       └─ Block
  │           └─ Block (child)
  │
  └─ Page (root)
      ├─ Block
      │   ├─ Block (child)
      │   └─ Block (child)
```

### The Problem

Low-level API navigation is verbose and type-unsafe:

```python
# Get parent
parent_id = page_data["parent"]["page_id"]  # or database_id?
parent_data = await api._request("GET", f"/pages/{parent_id}")

# Get children (manual pagination)
cursor = None
while True:
    data = await api._request("GET", f"/blocks/{id}/children", params={"start_cursor": cursor})
    for block_data in data["results"]:
        process(block_data)
    if not data["has_more"]:
        break
    cursor = data["next_cursor"]
```

**Issues**:
- Must know parent type (page_id vs database_id vs workspace)
- Each navigation = 1 API call
- Manual pagination handling
- No way to walk up the tree
- No way to walk down recursively

### The Solution

Intuitive, cached navigation:

```python
page = await client.pages.get(page_id)

# Walk down (direct children)
async for block in page.children:
    print(block.type)

# Walk up (one level)
parent = await page.parent

# Walk up to root
async for ancestor in page.ancestors():
    print(ancestor.title)

# Walk down recursively
async for descendant in page.descendants():
    print(block.type)
```

## Architecture

### Navigation Methods on BaseEntity

All entities inherit navigation capabilities from `BaseEntity`:

```python
class BaseEntity(ABC):
    """Base entity with navigation methods."""

    def __init__(self, client: NotionClient, data: dict[str, Any]) -> None:
        """Initialize entity with client reference.

        Args:
            client: NotionClient instance
            data: Raw API response data
        """
        self._client = client
        self._data = data
        self._cache: dict[str, Any] = {}

    # ===== PARENT =====

    @abstractmethod
    async def parent(self) -> Database | Page | Block | None:
        """Get parent object (fetches if not cached).

        Returns:
            Parent object (Database, Page, or Block)
            None if this is a workspace-level object

        Behavior:
            - First call: Fetch from API, cache result
            - Subsequent calls: Return cached version

        Example:
            >>> parent = await page.parent
            >>> if isinstance(parent, Database):
            ...     print(f"In database: {parent.title}")
        """
        # Check cache first
        cached_parent = self._cache_get("parent")
        if cached_parent:
            return cached_parent

        # Fetch from API (implemented by subclass)
        parent = await self._resolve_parent()

        # Cache result
        if parent:
            self._cache_set("parent", parent)

        return parent

    @property
    def parent_cached(self) -> Database | Page | Block | None:
        """Get parent from cache only (no fetch).

        Returns:
            Cached parent or None if not fetched yet

        Use case:
            Check if parent is available without triggering API call

        Example:
            >>> parent = page.parent_cached
            >>> if parent:
            ...     print(parent.title)  # No API call
            >>> else:
            ...     parent = await page.parent  # Fetch it
        """
        return self._cache_get("parent")

    # ===== CHILDREN =====

    async def children(self) -> AsyncIterator[Block]:
        """Iterate over direct children.

        Yields:
            Child blocks (or pages if parent is database)

        Example:
            >>> async for block in page.children:
            ...     print(block.type)

        Note:
            Handles pagination automatically
        """
        raise NotImplementedError  # Implemented by subclasses

    # ===== ANCESTORS =====

    async def ancestors(self) -> AsyncIterator[Database | Page | Block]:
        """Walk up the hierarchy to root.

        Yields:
            Ancestors from immediate parent to root

        Example:
            >>> # Build breadcrumb path
            >>> path = []
            >>> async for ancestor in page.ancestors():
            ...     title = ancestor.title if hasattr(ancestor, 'title') else 'Workspace'
            ...     path.append(title)
            >>> print(" / ".join(reversed(path)))
            # Output: "Workspace / Database / Section / Page"

        Note:
            - First yielded: immediate parent
            - Last yielded: root (workspace-level)
            - Does NOT include self (use descendants() for that)
            - Stops when parent is None (workspace level)
        """
        current = self

        while True:
            parent = await current.parent

            if parent is None:
                break

            yield parent

            current = parent

    # ===== DESCENDANTS =====

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

        Note:
            - Uses depth-first traversal
            - Respects max_depth to limit traversal
            - Includes self in iteration
            - Protects against cycles (visited tracking)
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
            except NotImplementedError:
                # Entity doesn't support children
                pass

        async for descendant in traverse(self, 0):
            yield descendant
```

## Parent Resolution

### Challenge: Variable Parent Types

Notion API returns different parent structures:

```json
// Parent is a database
{
  "parent": {
    "type": "database_id",
    "database_id": "xxx"
  }
}

// Parent is a page
{
  "parent": {
    "type": "page_id",
    "page_id": "yyy"
  }
}

// Parent is workspace (root)
{
  "parent": {
    "type": "workspace",
    "workspace": true
  }
}
```

### Resolution Implementation

```python
async def _resolve_parent(
    self,
    parent_data: dict[str, Any]
) -> Database | Page | Block | None:
    """Resolve parent from API parent data.

    Args:
        parent_data: Parent dict from Notion API

    Returns:
        Parent object (Database, Page, or Block)
        None if workspace (no parent)
    """
    from better_notion._sdk.models.database import Database
    from better_notion._sdk.models.page import Page
    from better_notion._sdk.models.block import Block

    parent_type = parent_data.get("type")

    if parent_type == "database_id":
        # Parent is a Database - use autonomous get
        db_id = parent_data["database_id"]
        return await Database.get(db_id, client=self._client)

    elif parent_type == "page_id":
        # Parent is a Page - use autonomous get
        page_id = parent_data["page_id"]
        return await Page.get(page_id, client=self._client)

    elif parent_type == "block_id":
        # Parent is a Block - use autonomous get
        block_id = parent_data["block_id"]
        return await Block.get(block_id, client=self._client)

    elif parent_type == "workspace":
        # Root level - no parent
        return None

    else:
        # Unknown type
        return None
```

## Children Iteration

### Page Children Implementation

```python
# better_notion/_sdk/models/page.py

class Page(BaseEntity):

    async def children(self) -> AsyncIterator[Block]:
        """Iterate over child blocks.

        Yields:
            Block objects that are direct children of this page

        Example:
            >>> async for block in page.children:
            ...     if block.is_paragraph:
            ...         print(block.text)

        Note:
            Uses async iteration with automatic pagination
        """
        from better_notion._api.utils import AsyncPaginatedIterator
        from better_notion._sdk.models.block import Block

        async def fetch_fn(cursor: str | None) -> dict:
            params = {}
            if cursor:
                params["start_cursor"] = cursor

            return await self._client.api._request(
                "GET",
                f"/blocks/{self.id}/children",
                params=params
            )

        iterator = AsyncPaginatedIterator(fetch_fn)

        async for block_data in iterator:
            yield Block.from_data(self._client, block_data)
```

### Database Children (Pages)

```python
# better_notion/_sdk/models/database.py

class Database(BaseEntity):

    async def children(self) -> AsyncIterator[Page]:
        """Iterate over pages in this database.

        Yields:
            Page objects that belong to this database

        Example:
            >>> async for page in database.children:
            ...     print(page.title)

        Note:
            Equivalent to database.query() without filters
        """
        from better_notion._sdk.models.page import Page

        # Use database query API
        async def fetch_fn(cursor: str | None) -> dict:
            body = {}
            if cursor:
                body["start_cursor"] = cursor

            return await self._client.api._request(
                "POST",
                f"/databases/{self.id}/query",
                json=body
            )

        iterator = AsyncPaginatedIterator(fetch_fn)

        async for page_data in iterator:
            yield Page.from_data(self._client, page_data)
```

## Usage Examples

### Example 1: Breadcrumbs

```python
async def build_breadcrumb(page: Page) -> str:
    """Build breadcrumb path for a page.

    Args:
        page: Page to build breadcrumb for

    Returns:
        Breadcrumb string like "Workspace / DB / Section / Page"
    """
    parts = []

    # Walk up to root
    async for ancestor in page.ancestors():
        title = ancestor.title if hasattr(ancestor, 'title') else 'Workspace'
        parts.append(title)

    # Reverse to get root → page order
    parts.reverse()
    parts.append(page.title)

    return " / ".join(parts)


# Usage
page = await client.pages.get(page_id)
breadcrumb = await build_breadcrumb(page)
print(breadcrumb)
# Output: "My Workspace / Projects / 2025 / Q1 Planning"
```

### Example 2: Find All Code Blocks

```python
async def find_code_blocks(page: Page) -> list[Block]:
    """Find all code blocks in a page.

    Args:
        page: Page to search

    Returns:
        List of code blocks (including nested)
    """
    code_blocks = []

    async for block in page.descendants():
        if block.type == "code":
            code_blocks.append(block)

    return code_blocks


# Usage
page = await client.pages.get(page_id)
code_blocks = await find_code_blocks(page)

print(f"Found {len(code_blocks)} code blocks")
for block in code_blocks:
    print(f"- {block.code[:50]}...")
```

### Example 3: Calculate Depth

```python
async def get_depth(entity: BaseEntity) -> int:
    """Calculate depth of entity in hierarchy.

    Args:
        entity: Entity to measure

    Returns:
        Depth (0 = root/workspace, 1 = child of root, etc.)
    """
    depth = 0
    async for _ in entity.ancestors():
        depth += 1
    return depth


# Usage
page = await client.pages.get(page_id)
depth = await get_depth(page)

print(f"Page is at depth {depth}")
# Output: "Page is at depth 3"
```

### Example 4: Collect All Pages in Database

```python
async def collect_all_pages(database: Database) -> list[Page]:
    """Collect all pages from database (handles pagination).

    Args:
        database: Database to collect from

    Returns:
        List of all pages
    """
    pages = []

    async for page in database.children():
        pages.append(page)

    return pages


# Usage
database = await client.databases.get(database_id)
all_pages = await collect_all_pages(database)

print(f"Total pages: {len(all_pages)}")
```

### Example 5: Export Page Structure

```python
async def export_structure(page: Page) -> dict:
    """Export page structure as nested dict.

    Args:
        page: Page to export

    Returns:
        Nested dict representing page structure
    """
    result = {
        "id": page.id,
        "title": page.title,
        "type": "page",
        "children": []
    }

    async for block in page.children:
        result["children"].append({
            "id": block.id,
            "type": block.type,
            "has_children": block.has_children
        })

    return result


# Usage
page = await client.pages.get(page_id)
structure = await export_structure(page)

import json
print(json.dumps(structure, indent=2))
```

## Performance Considerations

### Parent Caching

```python
# First call: fetch + cache
parent = await page.parent  # ~300ms

# Subsequent calls: cache hit
parent = await page.parent  # ~0ms

# Sync cache check (no fetch)
parent = page.parent_cached  # ~0ms, no fetch if missing
```

### Descendants Performance

Walking large hierarchies can be expensive:

```python
# ⚠️ WARNING: Could be thousands of blocks
async for block in page.descendants():
    process(block)  # Might take a while
```

**Optimization**: Limit depth

```python
# Only traverse 2 levels deep
async for block in page.descendants(max_depth=2):
    process(block)  # Much faster
```

### Pagination Efficiency

Children iteration uses streaming:

```python
# ✅ GOOD: Stream processing
async for block in page.children():
    process(block)  # Process one at a time, memory efficient

# ❌ BAD: Load all then process
all_blocks = []
async for block in page.children():
    all_blocks.append(block)  # Loads all into memory

for block in all_blocks:
    process(block)  # Could be thousands of items
```

## Design Decisions

### Q1: Should ancestors() include self?

**Decision**: No, only parents

**Rationale**:
- "Ancestors" = those before, not self
- More intuitive for breadcrumbs
- If you want self, use `descendants()` from root

**Example**:
```python
# What we have (NO self)
async for ancestor in page.ancestors():
    # Yields: parent → grandparent → ... → root

# Alternative (WITH self)
async for ancestor in page.ancestors(include_self=True):
    # Yields: self → parent → grandparent → ... → root
```

### Q2: Traversal order for descendants()

**Decision**: Depth-first (pre-order)

**Rationale**:
- Matches document structure (top to bottom)
- More natural for "reading" a page
- Easier to implement recursively

**Example**:
```
Page
├─ Heading 1
│  └─ Paragraph
└─ Heading 2

# Depth-first order:
# Page → Heading 1 → Paragraph → Heading 2
```

### Q3: Cycle detection

**Decision**: Yes, track visited IDs

**Rationale**:
- Notion shouldn't have cycles (it's a tree)
- But defensive programming prevents infinite loops
- Minimal overhead (set of IDs)

**Implementation**:
```python
visited = set()

async def traverse(entity):
    if entity.id in visited:
        return  # Cycle detected, stop

    visited.add(entity.id)
    yield entity

    async for child in entity.children():
        async for desc in traverse(child):
            yield desc
```

## Cache Invalidation

### Invalidating on Move

```python
async def move(self, new_parent, **kwargs):
    """Move entity to new parent."""
    # Call API to move
    await self._api._request(...)

    # IMPORTANT: Clear cached parent
    self._cache_clear()
```

**Why**: After move, the cached parent is stale

### Refreshing Navigation

```python
# Force refresh of parent
page._cache_clear()
parent = await page.parent  # Fresh fetch
```

## Error Handling

### Parent Not Found

```python
parent = await page.parent

# If parent doesn't exist (deleted):
# - Returns None (doesn't raise)
# - Allows graceful degradation
```

### Children Access Errors

```python
try:
    async for block in page.children():
        process(block)
except PermissionError:
    # No access to children
    print("Cannot access page children")
except NotFoundError:
    # Page was deleted
    print("Page no longer exists")
```

## Best Practices

### DO ✅

```python
# Check cache before fetching
parent = page.parent_cached
if parent:
    print(f"In: {parent.title}")
else:
    parent = await page.parent

# Use descendants() for recursive searches
async for block in page.descendants():
    if block.type == "code":
        analyze_code(block)

# Limit depth for large hierarchies
async for block in page.descendants(max_depth=3):
    process(block)
```

### DON'T ❌

```python
# Don't assume parent exists
parent = await page.parent
print(parent.title)  # Could crash if None

# Don't fetch descendants in loop
async for block in page.descendants():
    # BAD: Nested descendants call
    async for sub in block.descendants():
        process(sub)  # O(n²) complexity!

# Don't ignore pagination
children = []
async for child in page.children():
    children.append(child)  # Could be huge
```

## Next Steps

After implementing navigation:

1. **Query Builder** - Transform Python kwargs to Notion filters
2. **Bulk Operations** - Batch operations with rate limiting
3. **Search Enhancement** - Cache-first search patterns

## Related Documentation

- [BaseEntity](./base-entity.md) - Foundation with cache methods
- [Cache Strategy](./cache-strategy.md) - Caching for navigation
- [Page Model](../models/page-model.md) - Page-specific navigation
- [Block Model](../models/block-model.md) - Block-specific navigation
