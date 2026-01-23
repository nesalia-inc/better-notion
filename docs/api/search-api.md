# Search API Reference

Complete API reference for the Search operation in the Notion API.

## Overview

The Search endpoint allows you to find pages and data sources shared with your integration by searching their titles. This is particularly useful for:

- Finding content by title or keyword
- Discovering accessible pages and databases
- Building search functionality
- Content discovery and navigation

**Important:** The Search endpoint only searches **titles**, not content within pages or data sources.

---

## Search by Title

Searches all parent or child pages and data sources shared with the integration.

### Endpoint

```
POST https://api.notion.com/v1/search
```

### Body Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `query` | string | No | - | Text to search for in titles |
| `filter` | object | No | - | Filter to pages or data_sources only |
| `sort` | object | No | - | Sort results by timestamp |
| `start_cursor` | string | No | - | Pagination cursor |
| `page_size` | integer | No | 100 | Number of results (max: 100) |

### Query Parameter

```json
{
  "query": "Tuscan kale"
}
```

- Searches for text in page and data source titles
- Case-insensitive substring matching
- Returns all titles containing the query text
- If omitted, returns all shared pages and data sources

### Filter Object

**Search only pages:**
```json
{
  "filter": {
    "property": "object",
    "value": "page"
  }
}
```

**Search only data sources:**
```json
{
  "filter": {
    "property": "object",
    "value": "data_source"
  }
}
```

**Supported values:**
- `page` - Limits results to pages only
- `data_source` - Limits results to data sources only

### Sort Object

```json
{
  "sort": {
    "direction": "descending",
    "timestamp": "last_edited_time"
  }
}
```

**Fields:**
- `direction` - `"ascending"` or `"descending"`
- `timestamp` - Only `"last_edited_time"` is supported

**Default:** Results sorted by most recently edited first (descending)

### Headers

| Header | Type | Required | Description |
|--------|------|----------|-------------|
| `Authorization` | string | Yes | Bearer `{integration_token}` |
| `Content-Type` | string | Yes | `application/json` |
| `Notion-Version` | string | Yes | The API version to use (latest: `2025-09-03`) |

### Required Capabilities

This endpoint requires the **read content** capability.

### Response

Returns a paginated list of page or database objects.

```json
{
  "object": "list",
  "results": [
    {
      "object": "page",
      "id": "59833787-2cf9-4fdf-8782-e53db20768a5",
      "parent": {
        "type": "database_id",
        "database_id": "d9824bdc84454327be8b5b47500af6ce"
      },
      "created_time": "2022-03-01T19:05:00.000Z",
      "last_edited_time": "2022-03-01T19:05:00.000Z",
      "archived": false,
      "in_trash": false,
      "properties": {
        "Name": {
          "id": "title",
          "type": "title",
          "title": [
            {
              "type": "text",
              "text": {
                "content": "Tuscan kale",
                "link": null
              },
              "annotations": {
                "bold": false,
                "italic": false,
                "stries"
              },
              "plain_text": "Tuscan kale",
              "href": null
            }
          ]
        }
      },
      "url": "https://www.notion.so/Tuscan-kale-598337872cf94fdf8782e53db20768a5"
    }
  ],
  "next_cursor": null,
  "has_more": false,
  "type": "page_or_database"
}
```

**Response Fields:**
| Field | Type | Description |
|-------|------|-------------|
| `object` | string | Always `"list"` |
| `results` | array | List of page or database objects |
| `next_cursor` | string | Cursor for next page (if has_more is true) |
| `has_more` | boolean | Whether more results exist |
| `type` | string | Always `"page_or_database"` |

**Important:** Linked databases are deduplicated (excluded from results).

### Pagination

The endpoint uses cursor-based pagination:

1. First request: Call without `start_cursor`
2. Check `has_more` in the response
3. If `has_more` is `true`, use `next_cursor` as `start_cursor` for next request
4. Repeat until `has_more` is `false`

### SDK Implementation

```python
async def search(
    self,
    *,
    query: Optional[str] = None,
    filter_type: Optional[str] = None,  # "page" or "data_source"
    sort_direction: Optional[str] = None,  # "ascending" or "descending"
    page_size: int = 100,
    start_cursor: Optional[str] = None
) -> PaginatedResponse:
    """
    Search for pages and data sources by title.

    Args:
        query: Text to search for in titles
        filter_type: Filter to "page" or "data_source" only
        sort_direction: Sort by last_edited_time ("ascending" or "descending")
        page_size: Number of results (max: 100)
        start_cursor: Pagination cursor

    Returns:
        PaginatedResponse with page/database objects

    Raises:
        ValueError: If invalid filter_type or sort_direction
    """
    payload = {}

    if query:
        payload["query"] = query
    if page_size:
        payload["page_size"] = page_size
    if start_cursor:
        payload["start_cursor"] = start_cursor

    if filter_type:
        if filter_type not in ("page", "data_source"):
            raise ValueError("filter_type must be 'page' or 'data_source'")
        payload["filter"] = {
            "property": "object",
            "value": filter_type
        }

    if sort_direction:
        if sort_direction not in ("ascending", "descending"):
            raise ValueError("sort_direction must be 'ascending' or 'descending'")
        payload["sort"] = {
            "direction": sort_direction,
            "timestamp": "last_edited_time"
        }

    response = await self._client.request(
        "POST",
        "/search",
        json=payload
    )

    return PaginatedResponse(
        results=[
            self._parse_result(item) for item in response.get("results", [])
        ],
        has_more=response.get("has_more", False),
        next_cursor=response.get("next_cursor")
    )

def _parse_result(self, data: dict) -> Union[Page, Database]:
    """Parse search result based on object type."""
    if data.get("object") == "page":
        return Page.from_dict(data, self._client)
    elif data.get("object") == "database":
        return Database.from_dict(data, self._client)
    else:
        raise ValueError(f"Unknown object type: {data.get('object')}")

async def search_all(
    self,
    *,
    query: Optional[str] = None,
    filter_type: Optional[str] = None,
    sort_direction: Optional[str] = None
) -> List[Union[Page, Database]]:
    """
    Search with automatic pagination.

    Args:
        query: Text to search for in titles
        filter_type: Filter to "page" or "data_source" only
        sort_direction: Sort by last_edited_time

    Returns:
        List of all matching page/database objects
    """
    all_results = []
    cursor = None
    has_more = True

    while has_more:
        response = await self.search(
            query=query,
            filter_type=filter_type,
            sort_direction=sort_direction,
            start_cursor=cursor
        )

        all_results.extend(response.results)
        has_more = response.has_more
        cursor = response.next_cursor

    return all_results
```

### Errors

| Status Code | Error | Description |
|-------------|-------|-------------|
| 400 | `bad_request` | Invalid filter or sort parameters |
| 400 | `validation_error` | Invalid query parameters |
| 403 | `missing_permission` | Integration lacks read content capability |
| 429 | `rate_limited` | Request rate limit exceeded |

### Example Usage

```python
# Search for pages with "kale" in title
results = await client.search.search(
    query="kale"
)

for result in results.results:
    if isinstance(result, Page):
        title = result.get_title()
        print(f"Page: {title}")
    elif isinstance(result, Database):
        print(f"Database: {result.title_plain}")

# Get all shared pages and databases
all_items = await client.search.search_all()

# Search only pages
pages = await client.search.search(
    query="project",
    filter_type="page"
)

# Search only data sources
databases = await client.search.search(
    query="tasks",
    filter_type="data_source"
)

# Sort by oldest first
oldest_first = await client.search.search(
    query="report",
    sort_direction="ascending"
)

# Paginated search
cursor = None
while True:
    response = await client.search.search(
        query="recipe",
        start_cursor=cursor
    )

    for result in response.results:
        process(result)

    if not response.has_more:
        break

    cursor = response.next_cursor
```

---

## Search Use Cases

### 1. Find Pages by Keyword

```python
async def find_pages_by_keyword(
    self,
    keyword: str
) -> List[Page]:
    """Find all pages containing a keyword in their title."""
    results = await self.search.search_all(
        query=keyword,
        filter_type="page"
    )

    return [r for r in results if isinstance(r, Page)]
```

### 2. Find Databases by Name

```python
async def find_databases(
    self,
    name: str
) -> List[Database]:
    """Find all databases matching a name pattern."""
    results = await self.search.search_all(
        query=name,
        filter_type="data_source"
    )

    return [r for r in results if isinstance(r, Database)]
```

### 3. Get Recently Modified Content

```python
async def get_recently_modified(
    self,
    limit: int = 100
) -> List[Union[Page, Database]]:
    """Get the most recently modified pages and databases."""
    return await self.search.search_all(
        page_size=limit,
        sort_direction="descending"
    )
```

### 4. Build Search Autocomplete

```python
async def autocomplete(
    self,
    search_term: str,
    max_results: int = 10
) -> List[dict]:
    """
    Autocomplete search for UI.

    Returns simplified results for autocomplete suggestions.
    """
    results = await self.search.search(
        query=search_term,
        page_size=max_results
    )

    suggestions = []

    for item in results.results:
        if isinstance(item, Page):
            suggestions.append({
                "type": "page",
                "id": str(item.id),
                "title": item.get_title(),
                "url": item.url
            })
        elif isinstance(item, Database):
            suggestions.append({
                "type": "database",
                "id": str(item.id),
                "title": item.title_plain,
                "url": item.url
            })

    return suggestions
```

### 5. Content Discovery

```python
async def discover_content(
    self,
    keywords: List[str]
) -> dict:
    """
    Discover content by multiple keywords.

    Args:
        keywords: List of keywords to search for

    Returns:
        Dictionary with keywords as keys and matching results
    """
    discovered = {}

    for keyword in keywords:
        results = await self.search.search_all(
            query=keyword
        )

        discovered[keyword] = {
            "pages": [r for r in results if isinstance(r, Page)],
            "databases": [r for r in results if isinstance(r, Database)]
        }

    return discovered
```

### 6. Find All Accessible Content

```python
async def get_all_accessible_content(
    self
) -> dict:
    """
    Get all pages and databases shared with the integration.

    Returns:
        Dictionary with 'pages' and 'databases' lists
    """
    results = await self.search.search_all()

    return {
        "pages": [r for r in results if isinstance(r, Page)],
        "databases": [r for r in results if isinstance(r, Database)]
    }
```

---

## Limitations

### What Search Can Do

- Search page and data source **titles**
- Filter to pages only or data sources only
- Sort by `last_edited_time`
- Paginate through large result sets
- Case-insensitive substring matching

### What Search Cannot Do

- Search content within pages
- Search block content
- Search property values
- Search within file attachments
- Full-text search
- Search archived/trashed content

**For data source queries:** Use the **Query a Data Source** endpoint to search within a specific data source's pages and properties.

---

## Optimization Tips

### 1. Use Specific Filters

```python
# Good: Filter to pages only when you only need pages
pages = await client.search.search(
    query="report",
    filter_type="page"
)

# Avoid: Getting all results and filtering client-side
all_results = await client.search.search(query="report")
pages = [r for r in all_results if isinstance(r, Page)]
```

### 2. Use Reasonable Page Sizes

```python
# Good: Get only what you need
results = await client.search.search(
    query="task",
    page_size=20
)

# Avoid: Getting maximum results if you only need a few
results = await client.search.search(
    query="task",
    page_size=100
)
```

### 3. Sort When Order Matters

```python
# Good: Sort when displaying a list
recent = await client.search.search(
    query="invoice",
    sort_direction="descending"
)

# Skip sorting if order doesn't matter
all = await client.search.search(
    query="invoice"
)
```

### 4. Cache Results When Appropriate

```python
from functools import lru_cache

@lru_cache(maxsize=128)
async def cached_search(self, query: str):
    """Cache search results for common queries."""
    return await self.search.search_all(query=query)
```

---

## Error Handling

### Search Error Classes

```python
class SearchAPIError(Exception):
    """Base exception for search API errors."""
    pass

class SearchValidationError(SearchAPIError):
    """Invalid search parameters."""
    pass

async def handle_search_errors(func):
    """Decorator for search error handling."""
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except HTTPError as e:
            if e.status == 400:
                raise SearchValidationError(f"Invalid request: {e}")
            elif e.status == 403:
                raise PermissionError(f"Permission denied: {e}")
            elif e.status == 429:
                await asyncio.sleep(1)
                return await func(*args, **kwargs)
            else:
                raise SearchAPIError(f"Unexpected error: {e}")
    return wrapper
```

---

## Best Practices

1. **Use Filters** - Limit to pages or data sources when possible
2. **Reasonable Page Sizes** - Request only what you need
3. **Handle Pagination** - Always check has_more/next_cursor
4. **Filter Results** - Check object type when processing results
5. **Sort When Needed** - Add sorting only when order matters
6. **Case Insensitive** - Searches are case-insensitive by default
7. **Specific Queries** - Use specific terms for better results
8. **Cache Common Queries** - Cache frequently used searches
9. **Handle Mixed Results** - Process both Page and Database objects
10. **Error Handling** - Implement proper retry logic for rate limits

---

## Related Documentation

- [Pages API](./pages/pages-api.md) - Page operations
- [Databases API](./databases/databases-api.md) - Database operations
- [Data Sources API](./databases/data-sources-api.md) - Data source queries
- [Rich Text Objects](./rich-text-objects.md) - Text formatting

---

**Search Optimization Tips:**

- Use filters to narrow results
- Limit page_size for faster responses
- Sort only when order matters
- Handle pagination properly
- Cache results when appropriate

**Search Limitations:**

- Only searches **titles**, not content
- Cannot search within page content
- Cannot search property values
- Use Query Data Source for searching within data sources
