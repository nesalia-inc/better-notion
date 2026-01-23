# Rate Limiting

Notion enforces rate limits on API requests to ensure fair usage. The SDK provides intelligent rate limit tracking and handling with configurable strategies.

## Rate Limit Basics

### Notion Rate Limits

The Notion API has the following rate limits:

| Endpoint | Limit | Window |
|----------|-------|--------|
| **Most endpoints** | 3 requests | 1 second |
| **Search endpoint** | 1 request | 1 second |
| **File uploads** | 3 requests | 1 second |

### Rate Limit Headers

Every Notion API response includes rate limit headers:

```
x-ratelimit-limit: 3
x-ratelimit-remaining: 2
x-ratelimit-reset: 1699999999
x-ratelimit-used: 1
```

**Header Descriptions:**

| Header | Description |
|--------|-------------|
| `x-ratelimit-limit` | Maximum requests per window |
| `x-ratelimit-remaining` | Requests remaining in current window |
| `x-ratelimit-reset` | Unix timestamp when window resets |
| `x-ratelimit-used` | Requests used in current window |

### Rate Limit Error

When the limit is exceeded:

```json
{
  "message": "Rate limited",
  "status": 429
}
```

The response may include a `retry-after` header (seconds to wait).

## Rate Limit Tracking

### RateLimitTracker Class

```python
class RateLimitTracker:
    """
    Track rate limit information from API responses.

    Maintains state about remaining requests and reset time.
    """

    def __init__(self):
        """Initialize empty tracker."""
        self.limit: int | None = None
        self.remaining: int | None = None
        self.reset_time: int | None = None
        self.used: int | None = None

    def update_from_headers(self, headers: dict[str, str]) -> None:
        """
        Update tracker from response headers.

        Args:
            headers: Response headers dict
        """
        self.limit = self._parse_int(headers.get("x-ratelimit-limit"))
        self.remaining = self._parse_int(headers.get("x-ratelimit-remaining"))
        self.reset_time = self._parse_int(headers.get("x-ratelimit-reset"))
        self.used = self._parse_int(headers.get("x-ratelimit-used"))

    def is_rate_limited(self) -> bool:
        """
        Check if currently rate limited.

        Returns:
            True if remaining requests is 0
        """
        return self.remaining is not None and self.remaining <= 0

    def get_reset_wait_time(self) -> float:
        """
        Get seconds to wait until window resets.

        Returns:
            Seconds to wait (0 if not rate limited)
        """
        if not self.is_rate_limited():
            return 0

        if not self.reset_time:
            return 1.0  # Fallback

        now = int(time.time())
        return max(0, self.reset_time - now)

    def _parse_int(self, value: str | None) -> int | None:
        """Parse integer from header value."""
        if value is None:
            return None
        try:
            return int(value)
        except ValueError:
            return None

    def __repr__(self) -> str:
        """String representation of tracker state."""
        return (
            f"RateLimitTracker("
            f"remaining={self.remaining}/{self.limit}, "
            f"reset={self.reset_time}"
            f")"
        )
```

### Usage in HTTP Client

```python
class InstrumentedHTTPClient(HTTPClient):
    """HTTP client with rate limit tracking."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._rate_limit_tracker = RateLimitTracker()

    async def request(self, *args, **kwargs) -> dict:
        """Make request and track rate limits."""
        response = await super().request(*args, **kwargs)

        # Extract and track rate limit headers
        # (Implementation depends on response format)
        self._rate_limit_tracker.update_from_headers(response_headers)

        return response
```

## Rate Limit Strategies

### Strategy Enum

```python
class RateLimitStrategy(Enum):
    """Rate limit handling strategies."""

    WAIT = "wait"
    """Wait and retry automatically (default)."""

    FAIL = "fail"
    """Raise error immediately without retry."""

    PROACTIVE = "proactive"
    """Wait before hitting rate limit (future feature)."""
```

### WAIT Strategy (Default)

**Description:** Automatically wait when rate limited and retry the request.

```python
async def _request_with_wait_strategy(
    request_fn: Callable,
    tracker: RateLimitTracker
) -> dict:
    """
    Execute request with WAIT strategy.

    On 429:
    1. Calculate wait time from retry-after header
    2. Sleep for that duration
    3. Retry request

    Retries up to 3 times.
    """
    last_error = None

    for attempt in range(3):
        try:
            return await request_fn()

        except RateLimitedError as e:
            last_error = e

            # Calculate wait time
            wait_time = e.retry_after or tracker.get_reset_wait_time()

            if wait_time > 0:
                logger.warning(
                    f"Rate limited, waiting {wait_time}s before retry"
                )
                await asyncio.sleep(wait_time)

    raise last_error
```

**Pros:**
- "It just works"
- No manual error handling needed
- Automatic recovery

**Cons:**
- Can pause execution for extended periods
- May mask rate limit issues in code

**When to Use:**
- Most applications
- Scripts and automation
- Background jobs

### FAIL Strategy

**Description:** Raise `RateLimitedError` immediately when rate limited.

```python
async def _request_with_fail_strategy(
    request_fn: Callable
) -> dict:
    """
    Execute request with FAIL strategy.

    On 429:
    - Raise RateLimitedError immediately
    - No automatic retry
    """
    try:
        return await request_fn()

    except RateLimitedError as e:
        logger.error(f"Rate limited: {e}")
        raise  # Re-raise without retry
```

**Pros:**
- Explicit about rate limiting
- Application decides how to handle
- Faster feedback

**Cons:**
- Requires error handling in application code
- More boilerplate

**When to Use:**
- Interactive applications (show progress to user)
- Applications with custom retry logic
- When you need to notify user of delays

### PROACTIVE Strategy (Future)

**Description:** Preemptively wait before hitting rate limit.

```python
async def _request_with_proactive_strategy(
    request_fn: Callable,
    tracker: RateLimitTracker,
    threshold: int = 3
) -> dict:
    """
    Execute request with PROACTIVE strategy.

    Before making request:
    1. Check remaining requests
    2. If below threshold, wait for window reset
    3. Then make request

    Prevents hitting rate limit entirely.
    """
    # Check if we should wait
    if tracker.remaining is not None:
        if tracker.remaining <= threshold:
            wait_time = tracker.get_reset_wait_time()

            if wait_time > 0:
                logger.info(
                    f"Approaching rate limit, waiting {wait_time}s"
                )
                await asyncio.sleep(wait_time)

    # Make request
    return await request_fn()
```

**Pros:**
- Never hits rate limit
- Predictable behavior
- Smoother request flow

**Cons:**
- May wait unnecessarily
- Requires accurate tracking
- More complex

**When to Use:** (Future feature)
- High-throughput applications
- Batch operations
- When rate limits are consistently hit

## Configuration

### Default Strategy

```python
from better_notion.api import NotionAPI, RateLimitStrategy

# Default: WAIT strategy
api = NotionAPI(
    auth="secret_...",
    rate_limit_strategy=RateLimitStrategy.WAIT
)
```

### FAIL Strategy

```python
# Fail immediately on rate limit
api = NotionAPI(
    auth="secret_...",
    rate_limit_strategy=RateLimitStrategy.FAIL
)

# Application handles errors
try:
    await api.pages.create(...)
except RateLimitedError as e:
    print(f"Rate limited, please wait {e.retry_after}s")
```

### Custom Retry Configuration

```python
# Combined with retry config
api = NotionAPI(
    auth="secret_...",
    rate_limit_strategy=RateLimitStrategy.WAIT,
    retry_config=RetryConfig(
        max_attempts=5,  # More attempts for rate limits
        retry_on_status=[429]  # Only retry on 429
    )
)
```

## Practical Examples

### Batch Operations with Rate Limits

```python
async def create_pages_with_rate_limiting(
    api: NotionAPI,
    pages: list[dict]
) -> list[dict]:
    """
    Create multiple pages, respecting rate limits.

    Uses WAIT strategy to handle rate limiting automatically.
    """
    results = []

    for page_data in pages:
        # WAIT strategy handles rate limiting
        result = await api.pages.create(**page_data)
        results.append(result)

    return results

# Even with many pages, won't exceed rate limits
pages = [{"title": f"Page {i}"} for i in range(100)]
created = await create_pages_with_rate_limiting(api, pages)
```

### Custom Rate Limit Handling

```python
async def create_pages_with_custom_retry(
    api: NotionAPI,
    pages: list[dict]
) -> list[dict]:
    """
    Create pages with custom rate limit handling.
    """
    results = []

    for page_data in pages:
        while True:
            try:
                result = await api.pages.create(**page_data)
                results.append(result)
                break

            except RateLimitedError as e:
                # Custom wait logic
                wait_time = e.retry_after or 5

                # Show progress
                print(f"Rate limited, waiting {wait_time}s...")

                # Wait and retry
                await asyncio.sleep(wait_time)

    return results
```

### Rate Limit-Aware Scheduling

```python
async def schedule_requests_respecting_limits(
    api: NotionAPI,
    requests: list[Callable]
) -> list:
    """
    Schedule requests to avoid rate limits.

    Uses tracking to space out requests.
    """
    results = []
    tracker = RateLimitTracker()

    for request_fn in requests:
        # Check if we should wait
        if tracker.remaining is not None and tracker.remaining <= 1:
            wait_time = tracker.get_reset_wait_time()
            if wait_time > 0:
                await asyncio.sleep(wait_time)

        # Make request
        result = await request_fn()
        results.append(result)

        # Update tracker
        tracker.update_from_headers(last_headers)

    return results
```

## Monitoring

### Logging Rate Limits

```python
class RateLimitLogging:
    """Log rate limit information."""

    def __init__(self, logger):
        self.logger = logger

    def log_status(self, tracker: RateLimitTracker):
        """Log current rate limit status."""
        self.logger.info(
            f"Rate limit status: {tracker.remaining}/{tracker.limit} remaining",
            extra={
                "limit": tracker.limit,
                "remaining": tracker.remaining,
                "reset_time": tracker.reset_time
            }
        )

    def log_rate_limited(self, error: RateLimitedError):
        """Log rate limit event."""
        self.logger.warning(
            f"Rate limited: retry after {error.retry_after}s",
            extra={
                "retry_after": error.retry_after,
                "status_code": error.status_code
            }
        )
```

### Metrics Collection

```python
class RateLimitMetrics:
    """Collect rate limit metrics."""

    def __init__(self):
        self.total_requests = 0
        self.rate_limited_count = 0
        self.wait_time_total = 0.0

    def record_request(self) -> None:
        """Record a request."""
        self.total_requests += 1

    def record_rate_limit(self, wait_time: float) -> None:
        """Record a rate limit event."""
        self.rate_limited_count += 1
        self.wait_time_total += wait_time

    def get_statistics(self) -> dict:
        """Get rate limit statistics."""
        return {
            "total_requests": self.total_requests,
            "rate_limited_count": self.rate_limited_count,
            "rate_limit_rate": (
                self.rate_limited_count / self.total_requests
                if self.total_requests > 0 else 0
            ),
            "total_wait_time": self.wait_time_total,
            "average_wait_time": (
                self.wait_time_total / self.rate_limited_count
                if self.rate_limited_count > 0 else 0
            )
        }
```

## Best Practices

### 1. Use WAIT Strategy for Most Cases

```python
# Recommended for most applications
api = NotionAPI(
    auth=token,
    rate_limit_strategy=RateLimitStrategy.WAIT
)
```

### 2. Handle Rate Limits Explicitly When Needed

```python
# When you need custom handling
api = NotionAPI(
    auth=token,
    rate_limit_strategy=RateLimitStrategy.FAIL
)

try:
    await api.pages.create(...)
except RateLimitedError as e:
    # Custom logic (notify user, queue request, etc.)
    await handle_rate_limit(e)
```

### 3. Space Out Requests Manually

```python
# For high-volume operations, add delays
for page_data in pages:
    result = await api.pages.create(**page_data)

    # Small delay between requests
    await asyncio.sleep(0.2)  # 200ms
```

### 4. Monitor Rate Limit Status

```python
# Log rate limit status periodically
async def log_rate_limit_status(api: NotionAPI):
    """Log current rate limit status."""
    tracker = api._rate_limit_tracker

    logger.info(
        f"Rate limit: {tracker.remaining}/{tracker.limit} remaining"
    )

    if tracker.is_rate_limited():
        logger.warning("Currently rate limited!")
```

### 5. Use Batching Where Possible

```python
# Reduce API calls by batching
# Instead of 100 individual requests:
for page in pages:
    await api.pages.archive(page)

# Use batch operation (when available):
await api.pages.archive_bulk(pages)
```

## Common Scenarios

### Scenario 1: High-Volume Data Migration

```python
# Use WAIT strategy + progress tracking
api = NotionAPI(
    auth=token,
    rate_limit_strategy=RateLimitStrategy.WAIT
)

async def migrate_data(items: list) -> None:
    total = len(items)

    for i, item in enumerate(items):
        await api.pages.create(**item)

        if i % 10 == 0:
            print(f"Migrated {i}/{total} items")

    print(f"Migration complete!")
```

### Scenario 2: Interactive Application

```python
# Use FAIL strategy + user notification
api = NotionAPI(
    auth=token,
    rate_limit_strategy=RateLimitStrategy.FAIL
)

async def create_with_ui_feedback(page_data: dict) -> None:
    """Create page with UI feedback."""
    try:
        await api.pages.create(**page_data)

    except RateLimitedError as e:
        # Notify user
        show_message(
            f"Rate limited. Please wait {e.retry_after}s...",
            type="warning"
        )

        # Wait and retry
        await asyncio.sleep(e.retry_after)
        await api.pages.create(**page_data)
```

### Scenario 3: Background Job

```python
# Use WAIT strategy + extensive logging
api = NotionAPI(
    auth=token,
    rate_limit_strategy=RateLimitStrategy.WAIT,
    log_level="DEBUG"  # Detailed logging
)

async def background_job():
    """Background job with rate limit handling."""
    # Logs will show all rate limit events
    await process_large_dataset(api)
```

## Error Handling

### RateLimitedError

```python
class RateLimitedError(HTTPError):
    """Raised when rate limit is exceeded."""

    def __init__(
        self,
        message: str,
        *,
        retry_after: int | None = None,
        **kwargs
    ):
        super().__init__(message, **kwargs)
        self.retry_after = retry_after
```

### Usage

```python
try:
    await api.pages.create(...)
except RateLimitedError as e:
    if e.retry_after:
        print(f"Must wait {e.retry_after} seconds")
    else:
        print("Rate limited, retry time unknown")
```

## Related Documentation

- [Overview](./overview.md) - Low-level API overview
- [HTTP Client](./http-client.md) - HTTP layer
- [Error Handling](./error-handling.md) - Exception hierarchy
- [Testing](./testing.md) - Testing rate limiting

## Next Steps

1. Choose appropriate rate limit strategy for your use case
2. Implement logging to track rate limit events
3. Consider batching for high-volume operations
4. Monitor rate limit metrics in production
