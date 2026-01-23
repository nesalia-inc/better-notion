# Pagination

Notion API uses cursor-based pagination. The low-level API provides helpers to handle pagination automatically while still giving you manual control when needed.

## Pagination Model

### How It Works

Notion's pagination is based on cursors:

```
First Request:
POST /databases/{id}/query
Response: {results: [...], has_more: true, next_cursor: "abc123"}

Second Request:
POST /databases/{id}/query
Body: {start_cursor: "abc123"}
Response: {results: [...], has_more: false, next_cursor: null}
```

**Key Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `results` | array | Items for current page |
| `next_cursor` | string \| null | Cursor for next page |
| `has_more` | boolean | Whether more results exist |

### PaginatedResponse

```python
class PaginatedResponse:
    """
    Wrapper for paginated API responses.

    Provides:
    - Access to current page results
    - Information about pagination state
    - Helpers for fetching next page
    - Manual cursor management
    """

    def __init__(
        self,
        results: list[dict],
        next_cursor: str | None,
        has_more: bool,
        api: NotionAPI,
        request_fn: Callable,
        request_fn_kwargs: dict
    ):
        """
        Initialize paginated response.

        Args:
            results: Items from current page
            next_cursor: Cursor for next page
            has_more: Whether more pages exist
            api: NotionAPI instance
            request_fn: Function to fetch next page
            request_fn_kwargs: Additional kwargs for request_fn
        """
        self.results = results
        self.next_cursor = next_cursor
        self.has_more = has_more
        self._api = api
        self._request_fn = request_fn
        self._request_fn_kwargs = request_fn_kwargs

    def __iter__(self) -> Iterator:
        """
        Iterate over current page results.

        Note: This only iterates the current page,
        not all pages. Use fetch_all() for that.
        """
        return iter(self.results)

    async def next_page(self) -> "PaginatedResponse":
        """
        Fetch the next page.

        Returns:
            PaginatedResponse for next page

        Raises:
            StopAsyncIteration: If no more pages
        """
        if not self.has_more:
            raise StopAsyncIteration("No more pages")

        # Fetch next page with cursor
        return await self._request_fn(
            start_cursor=self.next_cursor,
            **self._request_fn_kwargs
        )

    async def fetch_all(self) -> list[dict]:
        """
        Fetch all remaining pages.

        Returns:
            List of all items across all pages

        Example:
            ```python
            response = await api.databases.query(database_id)
            all_results = await response.fetch_all()
            # all_results contains items from all pages
            ```
        """
        all_items = list(self.results)

        cursor = self.next_cursor
        has_more = self.has_more

        while has_more and cursor:
            response = await self._request_fn(
                start_cursor=cursor,
                **self._request_fn_kwargs
            )

            all_items.extend(response.results)
            cursor = response.next_cursor
            has_more = response.has_more

        return all_items

    async def pages(self) -> AsyncIterator["PaginatedResponse"]:
        """
        Iterate over all pages.

        Yields:
            PaginatedResponse for each page

        Example:
            ```python
            response = await api.databases.query(database_id)

            async for page_response in response.pages():
                # page_response is PaginatedResponse
                process_page(page_response.results)
            ```
        """
        current = self

        while True:
            yield current

            if not current.has_more:
                break

            current = await current.next_page()

    async def items(self) -> AsyncIterator[dict]:
        """
        Iterate over all items across all pages.

        Yields:
            Individual items from all pages

        Example:
            ```python
            response = await api.databases.query(database_id)

            async for item in response.items():
                # item is from results
                process(item)
            ```
        """
        async for page_response in self.pages():
            for item in page_response.results:
                yield item
```

## Manual Pagination

### Fetching All Pages

```python
async def fetch_all_pages(
    api: NotionAPI,
    database_id: str
) -> list[dict]:
    """
    Manually fetch all pages from database query.

    Returns:
        All items across all pages
    """
    # First page
    response = await api.databases.query(database_id)

    all_results = list(response["results"])

    # Subsequent pages
    while response["has_more"]:
        cursor = response["next_cursor"]
        response = await api.databases.query(
            database_id,
            start_cursor=cursor
        )

        all_results.extend(response["results"])

    return all_results
```

### Cursor Management

```python
async def manual_pagination(
    api: NotionAPI,
    database_id: str
):
    """
    Manual pagination with custom control.
    """
    cursor = None
    page_num = 0

    while True:
        # Fetch page
        response = await api.databases.query(
            database_id,
            start_cursor=cursor,
            page_size=50  # Custom page size
        )

        results = response["results"]
        has_more = response["has_more"]

        # Process page
        print(f"Page {page_num}: {len(results)} results")

        for item in results:
            process(item)

        # Check if done
        if not has_more:
            break

        # Get cursor for next page
        cursor = response["next_cursor"]
        page_num += 1
```

## Async Iterators

### PaginatedAsyncIterator

```python
class PaginatedAsyncIterator:
    """
    Async iterator over paginated results.

    Provides Pythonic async iteration over all pages.
    """

    def __init__(
        self,
        first_page: PaginatedResponse
    ):
        """
        Initialize iterator.

        Args:
            first_page: First page response
        """
        self._current_page = first_page
        self._item_index = 0
        self._exhausted = False

    def __aiter__(self) -> "PaginatedAsyncIterator":
        """Async iterator interface."""
        return self

    async def __anext__(self) -> dict:
        """
        Get next item across all pages.

        Yields:
            Next item from results

        Raises:
            StopAsyncIteration: When all items consumed
        """
        # Check if current page has more items
        if self._item_index < len(self._current_page.results):
            item = self._current_page.results[self._item_index]
            self._item_index += 1
            return item

        # Need to fetch next page
        if not self._current_page.has_more:
            raise StopAsyncIteration("No more items")

        # Fetch next page
        self._current_page = await self._current_page.next_page()
        self._item_index = 0

        # Return first item from new page
        item = self._current_page.results[self._item_index]
        self._item_index += 1
        return item
```

### Usage

```python
# Using async iterator
response = await api.databases.query(database_id)

async for item in response.async_iterator():
    process(item)  # Iterates over ALL pages automatically
```

## PaginationHelper

### Helper Functions

```python
class PaginationHelper:
    """Helper functions for pagination."""

    @staticmethod
    async def fetch_all(
        api: NotionAPI,
        endpoint: str,
        **initial_kwargs
    ) -> list[dict]:
        """
        Fetch all pages from an endpoint.

        Args:
            api: NotionAPI instance
            endpoint: Endpoint path (e.g., "/databases/{id}/query")
            **initial_kwargs: Initial request parameters

        Returns:
            All items across all pages
        """
        # Make initial request
        response = await api._request("POST", endpoint, **initial_kwargs)

        all_items = list(response["results"])

        # Fetch remaining pages
        cursor = response.get("next_cursor")
        has_more = response.get("has_more", False)

        while has_more and cursor:
            response = await api._request(
                "POST",
                endpoint,
                start_cursor=cursor
            )

            all_items.extend(response["results"])
            cursor = response.get("next_cursor")
            has_more = response.get("has_more", False)

        return all_items

    @staticmethod
    async def iterate_pages(
        api: NotionAPI,
        endpoint: str,
        **initial_kwargs
    ) -> AsyncIterator[list[dict]]:
        """
        Iterate over pages, yielding each page's results.

        Args:
            api: NotionAPI instance
            endpoint: Endpoint path
            **initial_kwargs: Initial request parameters

        Yields:
            List of items for each page
        """
        cursor = None
        page_num = 0

        while True:
            # Build request
            kwargs = initial_kwargs.copy()
            if cursor:
                kwargs["start_cursor"] = cursor

            # Fetch page
            response = await api._request("POST", endpoint, **kwargs)

            # Yield results
            yield response["results"]

            # Check for more pages
            has_more = response.get("has_more", False)
            if not has_more:
                break

            cursor = response.get("next_cursor")
            page_num += 1
```

## Practical Examples

### Collect All Pages

```python
api = NotionAPI(auth="secret_...")

# Fetch all pages in database
response = await api.databases.query(database_id)
all_pages = await response.fetch_all()

print(f"Total pages: {len(all_pages)}")
```

### Process Large Datasets

```python
async def process_large_database(
    api: NotionAPI,
    database_id: str
) -> None:
    """
    Process a large database without loading all into memory.

    Processes page-by-page.
    """
    # Get first page
    response = await api.databases.query(database_id, page_size=100)

    total_processed = 0

    # Process each page
    async for page_results in response.pages():
        for item in page_results:
            process(item)
            total_processed += 1

        print(f"Processed {total_processed} so far...")

    print(f"Finished! Processed {total_processed} items")
```

### Parallel Fetching

```python
async def parallel_fetch(
    api: NotionAPI,
    database_ids: list[str]
) -> dict[str, list[dict]]:
    """
    Fetch from multiple databases in parallel.

    Uses asyncio.gather for concurrent requests.
    """
    async def fetch_db(db_id: str) -> tuple[str, list]:
        response = await api.databases.query(db_id)
        return db_id, await response.fetch_all()

    # Fetch all databases in parallel
    results = await asyncio.gather(*[
        fetch_db(db_id) for db_id in database_ids
    ])

    return dict(results)
```

## Error Handling

### Pagination Errors

```python
async def safe_pagination(
    api: NotionAPI,
    database_id: str
) -> list[dict]:
    """
    Fetch all pages with error handling.

    Continues pagination even if individual pages fail.
    """
    all_items = []
    cursor = None

    while True:
        try:
            response = await api.databases.query(
                database_id,
                start_cursor=cursor
            )

            all_items.extend(response["results"])

            if not response["has_more"]:
                break

            cursor = response["next_cursor"]

        except RateLimitedError as e:
            # Wait and retry same page
            await asyncio.sleep(e.retry_after or 1)
            continue

        except HTTPError as e:
            logger.error(f"Error fetching page: {e}")
            # Decide: stop or continue?
            break

    return all_items
```

## Best Practices

### 1. Use fetch_all() for Small Results

```python
# GOOD: For small result sets
response = await api.databases.query(database_id)
items = await response.fetch_all()  # All items in memory

# AVOID: For large result sets
# Could consume too much memory
```

### 2. Use Async Iterator for Large Results

```python
# GOOD: For large result sets
response = await api.databases.query(database_id)

async for item in response.items():
    process(item)  # Processes one at a time, memory efficient

# AVOID: Loading all into memory if not needed
```

### 3. Always Check has_more

```python
# GOOD: Always check
while response["has_more"]:
    cursor = response["next_cursor"]
    response = await api.databases.query(
        database_id,
        start_cursor=cursor
    )

# AVOID: Assuming fixed number of pages
for i in range(10):  # May miss pages!
    ...
```

### 4. Handle Cursor Validation

```python
# Validate cursor before use
if response["next_cursor"]:
    cursor = response["next_cursor"]
    # Validate it's a string
    assert isinstance(cursor, str)
    # Use cursor
else:
    # No more pages
    break
```

### 5. Log Pagination Progress

```python
async def fetch_with_logging(
    api: NotionAPI,
    database_id: str
) -> list[dict]:
    """Fetch all pages with progress logging."""
    cursor = None
    page_count = 0
    total_items = 0

    while True:
        response = await api.databases.query(
            database_id,
            start_cursor=cursor
        )

        items = response["results"]
        total_items += len(items)

        logger.info(
            f"Page {page_count}: {len(items)} items, "
            f"{total_items} total so far"
        )

        if not response["has_more"]:
            break

        cursor = response["next_cursor"]
        page_count += 1

    logger.info(f"Complete: {total_items} items in {page_count} pages")

    # Convert pages() generator to items()
    # This would yield all items from all pages
```

### 6. Use Appropriate Page Sizes

```python
# For quick preview
response = await api.databases.query(
    database_id,
    page_size=10
)

# For batch processing
response = await api.databases.query(
    database_id,
    page_size=100  # Maximum
)
```

## Performance Considerations

### Memory vs Speed

```python
# Memory efficient (slower)
async for item in response.items():
    process(item)

# Faster (uses more memory)
items = await response.fetch_all()
for item in items:
    process(item)
```

### Network Efficiency

```python
# Fewer requests = slower per item but less overhead
response = await api.databases.query(
    database_id,
    page_size=100  # Max items per request
)

# More requests = faster first page but more overhead
response = await api.databases.query(
    database_id,
    page_size=10
)
```

## Testing Pagination

### Mock Paginated Responses

```python
def create_paginated_response(
    items: list[dict],
    has_more: bool = False,
    next_cursor: str | None = None
) -> dict:
    """Create mock paginated response."""
    return {
        "object": "list",
        "results": items,
        "next_cursor": next_cursor,
        "has_more": has_more
    }

# Use in tests
mock_response = create_paginated_response(
    items=[{"id": "1"}, {"id": "2"}],
    has_more=True,
    next_cursor="cursor_abc"
)
```

### Test Pagination Logic

```python
@pytest.mark.asyncio
async def test_fetch_all():
    """Test fetching all pages."""
    # Mock three pages
    page1 = create_paginated_response(
        items=[{"id": "1"}],
        has_more=True,
        next_cursor="cursor_2"
    )
    page2 = create_paginated_response(
        items=[{"id": "2"}],
        has_more=True,
        next_cursor="cursor_3"
    )
    page3 = create_paginated_response(
        items=[{"id": "3"}],
        has_more=False
    )

    # Setup mock
    mock_api._request.side_effect = [page1, page2, page3]

    # Test
    response = await mock_api.databases.query(database_id)
    all_items = await response.fetch_all()

    assert len(all_items) == 3
```

## Related Documentation

- [Overview](./overview.md) - Low-level API overview
- [Endpoints](./endpoints.md) - Endpoint reference
- [HTTP Client](./http-client.md) - HTTP layer
- [Error Handling](./error-handling.md) - Error handling during pagination

## Next Steps

1. Choose appropriate pagination approach for your use case
2. Consider memory constraints when choosing fetch_all()
3. Use async iterators for large datasets
4. Implement proper error handling during pagination
5. Add logging for progress tracking
