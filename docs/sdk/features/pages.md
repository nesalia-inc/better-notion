# Pages Feature

Comprehensive documentation of page-related operations and features in the Better Notion SDK.

## Overview

Pages are the primary content containers in Notion. Each page has:
- **Properties**: Structured data fields (title, status, dates, etc.)
- **Content**: Hierarchical blocks that make up the page body
- **Metadata**: Creation time, last edited time, archive status
- **Relationships**: Parent (database or page), children (blocks)

## Features

### Core CRUD Operations

#### Retrieve a Page

```python
# Get page by ID
page = await client.pages.get(page_id)

# Returns rich Page object with:
print(page.title)        # Page title
print(page.url)          # Public URL
print(page.icon)         # Icon (emoji or image)
print(page.cover)        # Cover image
print(page.created_time) # Creation timestamp
print(page.archived)     # Archive status
```

**API Equivalent:** `GET /pages/{page_id}`

**Error Handling:**
- Raises `PageNotFound` if page doesn't exist
- Raises `PermissionError` if no access

#### Create a Page

```python
# Simple creation with title
page = await client.pages.create(
    parent=database,
    title="My New Page"
)

# With properties
page = await client.pages.create(
    parent=database,
    title="Project Plan",
    properties={
        "Status": "In Progress",
        "Priority": "High",
        "Due Date": "2025-02-01"
    }
)

# With content
page = await client.pages.create(
    parent=database,
    title="Document",
    content=[
        Block.paragraph("Introduction"),
        Block.heading("Section 1", level=2),
        Block.bullet_item("Point 1")
    ]
)

# With icon and cover
page = await client.pages.create(
    parent=database,
    title="Important Page",
    icon="🚀",
    cover="https://example.com/image.png"
)
```

**API Equivalent:** `POST /pages`

**Enhancements:**
- `title` parameter maps to title property automatically
- `content` parameter creates blocks automatically
- Icon accepts emoji directly (no conversion needed)

#### Update a Page

```python
# Update title
await client.pages.update(
    page,
    title="New Title"
)

# Update properties
await client.pages.update(
    page,
    properties={
        "Status": "Done",
        "Completed": True
    }
)

# Update icon/cover
await client.pages.update(
    page,
    icon="✅",
    cover="https://example.com/new-cover.png"
)

# Archive/Restore
await client.pages.archive(page)
await client.pages.restore(page)
```

**API Equivalent:** `PATCH /pages/{page_id}`

**Enhancements:**
- Accept Page object or ID
- `title` shortcut avoids property structure
- `archived` boolean parameter

### List Operations

#### List All Pages

```python
# Iterate over all pages in workspace
async for page in client.pages.all():
    print(page.title)

# Collect all pages
all_pages = await client.pages.all().collect()

# With limit
async for page in client.pages.all().limit(100):
    process(page)
```

**API Equivalent:** `POST /search` with empty query

**Why SDK-Exclusive:** API requires search endpoint with specific filter structure. User intent is "get all pages", not "search without query."

#### Filter Pages

```python
# Filter by type
async for page in client.pages.filter(type="page"):
    process(page)

# Filter by archived status
async for page in client.pages.filter(archived=False):
    process(page)

# Combine filters
async for page in client.pages.filter(
    type="page",
    archived=False
):
    process(page)
```

**API Equivalent:** `POST /search` with filter object

**Why SDK-Exclusive:** Transforms complex filter structure into simple parameters.

### Find Operations

#### Find by Title

```python
# Exact match
page = await client.pages.find_by_title("Project Plan")

# Substring match
pages = await client.pages.find_by_title(
    "Project",
    exact=False
)

# Case-insensitive
page = await client.pages.find_by_title(
    "project plan",
    case_sensitive=False
)
```

**API Equivalent:** `POST /search` with query + manual filtering

**Why SDK-Exclusive:**
- Common operation (search by title)
- API returns many results, requires client filtering
- SDK handles search + filtering + return first match

### Hierarchical Navigation

#### Get Parent

```python
# Get parent object (fetches if needed)
parent = await page.parent

# Get parent from cache (no fetch)
parent = page.parent_cached

# Parent can be Database or Page
if isinstance(parent, Database):
    print(f"In database: {parent.title}")
elif isinstance(parent, Page):
    print(f"In page: {parent.title}")
```

**API Equivalent:** `GET /pages/{page_id}` + access `parent` field + additional fetch

**Why SDK-Exclusive:**
- User thinks "get parent", not "get page ID, then fetch parent"
- Handles caching automatically
- Returns typed object (Database or Page), not dict

#### Get Children

```python
# Iterate over child blocks
async for block in page.children:
    print(block.type, block.content)

# Get children as list
children = await page.children.collect()

# Walk all descendants (nested blocks)
async for block in page.descendants():
    process(block)
```

**API Equivalent:** `GET /blocks/{block_id}/children` + pagination

**Why SDK-Exclusive:**
- `page.children` is more intuitive than `api.blocks.children.list(page_id)`
- Async iterator handles pagination automatically
- `descendants()` walks the entire tree recursively

#### Walk Up Hierarchy

```python
# Get all ancestors to root
async for ancestor in page.ancestors():
    print(f"Parent: {ancestor.title if hasattr(ancestor, 'title') else 'Database'}")

# Get root (workspace database or top-level page)
root = await page.root()
```

**API Equivalent:** Multiple API calls following parent chain

**Why SDK-Exclusive:**
- Abstracts recursive parent traversal
- Handles both Database and Page parents
- Common pattern for breadcrumbs

### Property Access

#### Property Shortcuts

```python
# Direct access to common properties
title = page.title
url = page.url
icon = page.icon
cover = page.cover
created_time = page.created_time
last_edited_time = page.last_edited_time
archived = page.archived

# Access all properties
all_props = page.properties
status = page.properties["Status"]
```

**API Equivalent:** `page["properties"]["Name"]["title"][0]["plain_text"]`

**Why SDK-Exclusive:**
- `page.title` vs nested dictionary access
- No need to understand Notion's property structure
- Fail-safe (returns None if property doesn't exist)

#### Smart Property Access

```python
# Find property by name (case-insensitive)
prop = page.find_property("status")  # Finds "Status", "status", "STATUS"

# Get property value with type conversion
status = page.get_property("status")  # Returns typed value
status = page.get_property("status", default="Unknown")

# Check property exists
has_status = page.has_property("Status")
```

**Why SDK-Exclusive:**
- Case-insensitive matching (user-friendly)
- Automatic type conversion (select → value, not dict)
- Safe defaults

### Content Operations

#### Duplicate Page

```python
# Duplicate with all children
new_page = await page.duplicate(
    parent=target_database,
    title="Copy - " + page.title
)

# Duplicate without children
new_page = await page.duplicate(
    parent=target_database,
    include_children=False
)
```

**API Equivalent:** Multiple API calls (create page + recursive block copy)

**Why SDK-Exclusive:**
- Common operation (copy templates)
- Complex to implement manually (recursive block traversal)
- Single method call vs 10+ lines of code

#### Move Page

```python
# Move to new parent
await page.move(new_parent=other_database)

# Move with position
await page.move(
    new_parent=other_page,
    position="after:block_id"
)
```

**API Equivalent:** `PATCH /pages/{page_id}` with parent and position

**Why SDK-Exclusive:**
- Semantic operation ("move") vs technical ("update parent")
- Handles position parameter formatting

### Bulk Operations

#### Bulk Create

```python
# Create multiple pages efficiently
pages = await client.pages.create_bulk(
    parent=database,
    data=[
        {"title": "Task 1", "status": "Todo"},
        {"title": "Task 2", "status": "Todo"},
        {"title": "Task 3", "status": "Todo"},
    ]
)

# Returns list of created Page objects
for page in pages:
    print(f"Created: {page.title}")
```

**API Equivalent:** Multiple `POST /pages` calls with rate limiting

**Why SDK-Exclusive:**
- Bulk operations are common
- SDK handles batching, rate limiting, parallelization
- Single API call from user perspective

#### Bulk Update

```python
# Update multiple pages with same properties
await client.pages.update_bulk(
    pages,
    properties={"Status": "Done"}
)

# Update with different properties
await client.pages.update_bulk(
    [page1, page2, page3],
    properties={"Status": "Archived"}
)
```

**API Equivalent:** Multiple `PATCH /pages/{page_id}` calls

**Why SDK-Exclusive:**
- Common pattern (bulk status updates)
- Automatic rate limiting
- Error aggregation (which ones failed?)

#### Bulk Archive

```python
# Archive multiple pages
await client.pages.archive_bulk([page1, page2, page3])

# Archive all pages in database
pages = await database.pages().collect()
await client.pages.archive_bulk(pages)
```

**API Equivalent:** Multiple `PATCH /pages/{page_id}` with archived=true

#### Bulk Move

```python
# Move multiple pages to new parent
await client.pages.move_bulk(
    pages,
    new_parent=target_database
)

# Move with position
await client.pages.move_bulk(
    pages,
    new_parent=target_database,
    position="first"
)
```

**Why SDK-Exclusive:**
- Reorganizing databases (moving pages)
- Complex to handle manually (rate limits, order)

### Cache Operations

#### Cache Lookup

```python
# Instant lookup (no API call)
page = client.pages.cache.get(page_id)

if page:
    print(f"Cached: {page.title}")
else:
    page = await client.pages.get(page_id)
```

**Why SDK-Exclusive:**
- Avoid repeated API calls for same page
- Instant lookups in loops
- Populated from various sources (query, retrieval, etc.)

#### Check Cache

```python
# Check if page is cached
if page_id in client.pages.cache:
    page = client.pages.cache[page_id]

# Cache size
print(f"Cached pages: {len(client.pages.cache)}")

# Get all cached pages
all_cached = client.pages.cache.get_all()
```

### Advanced Patterns

#### Process Pages with Batching

```python
# Process in batches to avoid memory issues
batch_size = 100

async for page in database.query().batch(batch_size):
    # page is a list of 100 pages
    await process_batch(page)
```

#### Transform Pages

```python
# Map over pages
titles = await database.query().map(lambda p: p.title).collect()

# Filter pages
important = await database.query().filter(
    priority__gte=8
).collect()
```

#### Aggregate Pages

```python
# Count by status
from collections import Counter

status_counts = Counter()
async for page in database.query():
    status_counts[page.get_property("status")] += 1

print(status_counts)
```

## Implementation Considerations

### Page Object Model

```python
class Page(BaseEntity):
    id: str
    title: str | None
    url: str
    icon: str | None
    cover: str | None
    created_time: datetime
    last_edited_time: datetime
    archived: bool
    properties: dict[str, Any]
    parent: Database | Page | None  # Cached

    # Methods
    async def parent(self) -> Database | Page
    async def children(self) -> AsyncIterator[Block]
    async def descendants(self) -> AsyncIterator[Block]
    async def ancestors(self) -> AsyncIterator[Database | Page]
    async def duplicate(...) -> Page
    async def move(...) -> Page
    async def archive() -> None
    async def restore() -> None
```

### Property Resolution

Title property varies by database:
- Can be named "Title", "Name", "Task", etc.
- SDK finds first title-type property
- Caches property ID for subsequent access

### Cache Strategy

**Populate from:**
- `pages.get()` responses
- `databases.query()` results
- `search.query()` results
- Parent references from blocks

**Invalidate on:**
- Explicit `pages.update()`
- Explicit `pages.cache.invalidate()`
- Time-based expiration (optional)

### Pagination Strategy

**List operations:**
- Use async iterators
- Fetch pages on-demand
- Don't load entire result set into memory

**Collection:**
- `.collect()` loads all into list
- Warn for large result sets
- Provide `.batch()` for chunked processing

## Error Scenarios

| Scenario | Error | Solution |
|----------|-------|----------|
| Page doesn't exist | `PageNotFound` | Verify ID, check permissions |
| No access to page | `PermissionError` | Verify integration capabilities |
| Invalid property | `ValidationError` | Check property name, type |
| Rate limit hit | `RateLimited` | SDK retries automatically |
| Network error | `APIError` | SDK retries with backoff |

## Performance Considerations

### Optimal Patterns

```python
# GOOD: Use cache
user = client.users.cache.get(page.created_by_id)

# AVOID: Repeated lookups
user = await client.users.get(page.created_by_id)

# GOOD: Iterate efficiently
async for page in database.query():
    process(page)  # Process one at a time

# AVOID: Load all then process
pages = await database.query().collect()  # Memory intensive
for page in pages:
    process(page)
```

### Cache Warming

```python
# Warm cache for frequently accessed pages
page_ids = ["id1", "id2", "id3"]
for page_id in page_ids:
    await client.pages.get(page_id)  # Populates cache

# Subsequent access is instant
for page_id in page_ids:
    page = client.pages.cache.get(page_id)
```

## Future Enhancements

### Tier 2 (High Priority)
- [ ] Page templates (create from template)
- [ ] Page versions (if API adds support)
- [ ] Property validation before create/update

### Tier 3 (Medium Priority)
- [ ] Page diff (compare two pages)
- [ ] Page merge (merge properties/content)
- [ ] Advanced search (regex, fuzzy match)

### Tier 4 (Future)
- [ ] Real-time page updates (webhooks)
- [ ] Optimistic locking (concurrent edits)
- [ ] Page relationships (graph queries)
