# Search Feature

Comprehensive documentation of search-related operations and features in the Better Notion SDK.

## Overview

Search in Notion finds pages and databases by **title only** (not content). The SDK enhances this with:
- Cache-first search for instant results
- Semantic shortcuts for common search patterns
- Hybrid cache/API search
- Fuzzy matching capabilities

**Important:** Notion search only searches titles, not page/block content.

## Features

### Basic Search

#### Search by Query

```python
# Search for pages and databases
async for result in client.search.query("project"):
    if isinstance(result, Page):
        print(f"Page: {result.title}")
    elif isinstance(result, Database):
        print(f"Database: {result.title}")
```

**API Equivalent:** `POST /search` with query parameter

**Enhancements:**
- Async iterator handles pagination
- Returns typed objects (Page or Database)
- No manual result type checking

#### Search with Filters

```python
# Filter by type
async for page in client.search.pages("meeting"):
    print(page.title)

async for database in client.search.databases("tasks"):
    print(database.title)

# Filter options
async for result in client.search.query(
    "project",
    filter={"value": "page", "property": "object"}
):
    process(result)
```

#### Search with Sorting

```python
# Sort by last edited time
async for result in client.search.query(
    "report",
    sort={"direction": "descending", "timestamp": "last_edited_time"}
):
    print(result.title, result.last_edited_time)

# Most recent first
async for result in client.search.query(
    "project",
    sort="recent"
):
    process(result)
```

### SDK-Exclusive Features

#### Cache-First Search

```python
# Search in cache first (instant), fallback to API
results = await client.search.query(
    "project",
    use_cache_first=True
)

# Returns results from:
# 1. Cache (instant) if match found
# 2. API if no cache match
# 3. Combined if partial cache match
```

**Why SDK-Exclusive:**
- Instant results for previously accessed resources
- Reduces API calls for repeated searches
- Hybrid approach balances speed and completeness

#### Search Cache Only

```python
# Search only in cached data (no API call)
results = client.search.search_cache("project")

# Instant but limited to cached resources
for result in results:
    print(result.title)

# Useful for:
# - Autocomplete suggestions
# - Quick lookups
# - Offline scenarios
```

**Why SDK-Exclusive:**
- Instant search in local data
- No network latency
- Useful for real-time suggestions

#### Search by Title (Exact Match)

```python
# Find pages by exact title match
pages = await client.search.find_pages_by_title(
    "Project Plan",
    exact=True
)

# Returns list of matching pages
for page in pages:
    print(f"{page.title} - {page.url}")
```

**Why SDK-Exclusive:**
- Common operation (find by exact name)
- API returns partial matches, requires filtering
- SDK handles exact matching

#### Search by Title (Fuzzy Match)

```python
# Find pages with similar titles
pages = await client.search.find_pages_by_title(
    "proj",
    exact=False,
    case_sensitive=False
)

# Matches: "Project", "Projects", "My Project", etc.
for page in pages:
    print(page.title)
```

**Why SDK-Exclusive:**
- Fuzzy matching more user-friendly
- Case-insensitive by default
- Substring matching

#### Find Databases by Title

```python
# Find databases by exact title
database = await client.search.find_databases_by_title(
    "Tasks"
)

if database:
    print(f"Found: {database.title}")
else:
    print("Not found")

# Partial match
databases = await client.search.find_databases_by_title(
    "task",
    exact=False
)
```

### Advanced Search Patterns

#### Multi-Term Search

```python
# Search with multiple terms
async for result in client.search.query("project plan"):
    # Finds titles with "project" AND "plan"
    print(result.title)

# API behavior: searches for exact phrase
```

#### Search in Specific Context

```python
# Search within specific database
# (SDK enhancement - not directly supported by API)
async def search_in_database(
    database: Database,
    query: str
) -> list[Page]:
    results = []
    async for page in database.pages:
        if query.lower() in page.title.lower():
            results.append(page)
    return results

# Use
tasks = await search_in_database(database, "urgent")
```

#### Search and Filter

```python
# Search then apply additional filters
async for page in client.search.pages("project"):
    if not page.archived:
        if page.get_property("Status") == "Active":
            print(page.title)
```

#### Search with Pagination

```python
# Explicit pagination control
results = client.search.query("report")

# Get first 10
async for result in results.limit(10):
    print(result.title)

# Collect all
all_results = await results.collect()

# Batch processing
async for batch in results.batch(50):
    # batch is list of 50 results
    process_batch(batch)
```

### Search Helpers

#### Quick Page Find

```python
# Quick helper to find a page
async def find_page(title: str) -> Page | None:
    """Find page by title, returns first match."""
    async for page in client.search.pages(title):
        return page
    return None

# Use
page = await find_page("Meeting Notes")
if page:
    print(f"Found: {page.url}")
```

#### Quick Database Find

```python
async def find_database(title: str) -> Database | None:
    """Find database by title."""
    async for database in client.search.databases(title):
        return database
    return None

# Use
database = await find_database("Tasks")
if database:
    print(f"Found: {database.title}")
```

#### Search All Types

```python
# Search both pages and databases
pages = []
databases = []

async for result in client.search.query("project"):
    if isinstance(result, Page):
        pages.append(result)
    elif isinstance(result, Database):
        databases.append(result)

print(f"Found {len(pages)} pages, {len(databases)} databases")
```

### Cache Search Operations

#### Cache Statistics

```python
# Get cache information
page_cache_size = len(client.pages.cache)
database_cache_size = len(client.databases.cache)

print(f"Cached pages: {page_cache_size}")
print(f"Cached databases: {database_cache_size}")
```

#### Invalidate Search Cache

```python
# Invalidate specific resource from cache
client.pages.cache.invalidate(page_id)
client.databases.cache.invalidate(database_id)

# Clear all caches
client.pages.cache.clear()
client.databases.cache.clear()

# Force refresh
await client.pages.populate_cache()
```

## Search Limitations

### What Search Can Do

- Search page titles
- Search database titles
- Filter by object type (page/database)
- Sort by last_edited_time
- Case-insensitive matching

### What Search Cannot Do

- Search page content (blocks, properties)
- Search block content
- Search property values
- Full-text search
- Search within file attachments
- Regular expressions
- Advanced boolean queries

**For content searching:** Use database queries to search within specific databases/properties.

## Implementation Considerations

### Search Manager

```python
class SearchManager:
    # Basic search
    async def query(
        query: str,
        *,
        filter: dict | None = None,
        sort: dict | None = None,
        use_cache_first: bool = False
    ) -> AsyncIterator[Page | Database]

    # Type-specific search
    async def pages(query: str) -> AsyncIterator[Page]
    async def databases(query: str) -> AsyncIterator[Database]

    # Cache search
    def search_cache(
        query: str,
        *,
        exact: bool = False
    ) -> list[Page | Database]

    # Find helpers
    async def find_pages_by_title(
        title: str,
        *,
        exact: bool = True,
        case_sensitive: bool = False
    ) -> list[Page]

    async def find_databases_by_title(
        title: str,
        *,
        exact: bool = True
    ) -> list[Database] | None
```

### Cache-First Search Strategy

```python
async def query_with_cache(query: str) -> AsyncIterator:
    # 1. Search cache
    cached_results = self.search_cache(query)

    # 2. If cached results found, yield them
    for result in cached_results:
        yield result

    # 3. Search API for remaining
    async for api_result in self.query(query, use_cache_first=False):
        # Check if already in cache results
        if api_result not in cached_results:
            yield api_result
```

### Fuzzy Matching

```python
def fuzzy_match(query: str, title: str) -> bool:
    """Case-insensitive substring match."""
    query_lower = query.lower()
    title_lower = title.lower()

    # Exact match
    if query_lower == title_lower:
        return True

    # Substring match
    if query_lower in title_lower:
        return True

    # Word boundary match
    query_words = query_lower.split()
    title_words = title_lower.split()

    return any(
        q in t
        for q in query_words
        for t in title_words
    )
```

## Performance Considerations

### Optimal Patterns

```python
# GOOD: Cache-first for repeated searches
for query in search_terms:
    results = await client.search.query(
        query,
        use_cache_first=True
    )

# AVOID: Repeated API calls for same query
for query in search_terms:
    results = await client.search.query(query)  # Always API call

# GOOD: Cache-only for autocomplete
suggestions = client.search.search_cache(
    user_input
)

# AVOID: API calls for every keystroke
suggestions = await client.search.query(
    user_input
)  # Too many API calls
```

### Search Optimization

**Preload cache:**
```python
# Warm cache before searching
await client.pages.populate_cache()
await client.databases.populate_cache()

# Now searches are instant
results = client.search.search_cache("project")
```

**Limit results:**
```python
# Don't fetch all results if not needed
async for result in client.search.query("project").limit(20):
    process(result)
```

## Advanced Patterns

### Search Autocomplete

```python
# Real-time autocomplete suggestions
async def autocomplete(query: str) -> list[str]:
    """Get title suggestions for autocomplete."""
    if len(query) < 2:
        return []

    results = client.search.search_cache(query, exact=False)
    return [r.title for r in results[:10]]

# Use in UI
suggestions = await autocomplete(user_input)
```

### Search Aggregation

```python
# Aggregate search results by type
async def search_aggregated(query: str) -> dict:
    pages = []
    databases = []

    async for result in client.search.query(query):
        if isinstance(result, Page):
            pages.append(result)
        elif isinstance(result, Database):
            databases.append(result)

    return {
        "pages": pages,
        "databases": databases,
        "total": len(pages) + len(databases)
    }

# Use
results = await search_aggregated("project")
print(f"Found {results['total']} results")
print(f"  Pages: {len(results['pages'])}")
print(f"  Databases: {len(results['databases'])}")
```

### Multi-Query Search

```python
# Search multiple queries
async def search_multiple(queries: list[str]) -> dict:
    results = {}

    for query in queries:
        matching = []
        async for result in client.search.query(query):
            matching.append(result)
        results[query] = matching

    return results

# Use
results = await search_multiple(["project", "task", "meeting"])
for query, items in results.items():
    print(f"{query}: {len(items)} results")
```

### Search with Deduplication

```python
# Search multiple queries, deduplicate results
async def search_unique(queries: list[str]) -> list:
    seen = set()
    unique_results = []

    for query in queries:
        async for result in client.search.query(query):
            if result.id not in seen:
                seen.add(result.id)
                unique_results.append(result)

    return unique_results

# Use
results = await search_unique(["project", "projects"])
print(f"Found {len(results)} unique results")
```

### Search and Transform

```python
# Search and transform results
async def search_as_dicts(query: str) -> list[dict]:
    """Return search results as dictionaries."""
    results = []

    async for item in client.search.query(query):
        if isinstance(item, Page):
            results.append({
                "type": "page",
                "id": str(item.id),
                "title": item.title,
                "url": item.url
            })
        elif isinstance(item, Database):
            results.append({
                "type": "database",
                "id": str(item.id),
                "title": item.title
            })

    return results
```

## Error Scenarios

| Scenario | Error | Solution |
|----------|-------|----------|
| Invalid query | `SearchError` | Check query format |
| Rate limit | `RateLimited` | SDK retries |
| No results | Empty iterator | Handle gracefully |
| Cache miss | Falls back to API | Automatic |

## Integration with Other Features

### Pages

```python
# Find page, then access content
page = await client.search.find_page_by_title("Meeting Notes")
if page:
    async for block in page.children:
        print(block.content)
```

### Databases

```python
# Find database, then query
database = await client.search.find_database_by_title("Tasks")
if database:
    async for page in database.query(status="Done"):
        print(page.title)
```

### Workspace

```python
# Search within workspace context
async def search_workspace(query: str) -> list:
    results = []
    async for item in client.search.query(query):
        results.append(item)
    return results
```

## Future Enhancements

### Tier 2 (High Priority)
- [ ] Search result highlighting
- [ ] Search history
- [ ] Saved searches

### Tier 3 (Medium Priority)
- [ ] Advanced query syntax (AND, OR, NOT)
- [ ] Search within specific date range
- [ ] Relevance scoring

### Tier 4 (Future)
- [ ] Full-text search (if API adds support)
- [ ] Faceted search
- [ ] Search analytics
- [ ] Search suggestions based on usage
