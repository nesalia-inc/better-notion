# Low-Level API Overview

The low-level API (`NotionAPI`) provides direct, 1:1 mapping to the Notion REST API with minimal abstraction. It serves as the foundation for the high-level client and can be used independently when precise control is needed.

## Purpose

The low-level API exists to:

1. **Provide complete API coverage** - All Notion endpoints available immediately
2. **Offer precise control** - No hidden magic or transformations
3. **Enable the high-level client** - Foundation for rich abstractions
4. **Support advanced use cases** - When the high-level abstraction gets in the way

## When to Use Low-Level API

### Use Low-Level API When:

- You're already familiar with the Notion API
- You need to use new API features not yet in the high-level client
- You want complete control over request/response handling
- You're migrating from another Notion SDK
- You're building tools that require API-level precision
- Performance is critical and you need to optimize every request

### Use High-Level Client When:

- You want better developer experience
- You prefer object-oriented abstractions
- You want automatic caching and pagination
- You're building standard business applications
- You want to reduce boilerplate code

## Architecture

```
NotionAPI (Low-Level)
    ├── HTTP Client (httpx)
    ├── Authentication (Bearer/OAuth)
    ├── Rate Limiting
    ├── Retry Logic
    ├── Error Handling
    └── Endpoints
        ├── Blocks
        ├── Pages
        ├── Databases
        ├── Users
        └── Search
```

## Core Principles

### 1. API Fidelity

The low-level API maintains 1:1 correspondence with the Notion API:

```python
# Notion API endpoint
GET https://api.notion.com/v1/blocks/{block_id}

# Low-level API method
await api.blocks.retrieve(block_id)
```

### 2. Minimal Transformation

Responses are returned as dictionaries or simple wrapper objects:

```python
# Returns dict (raw API response)
response = await api.blocks.retrieve(block_id)

# Returns PaginatedResponse (minimal wrapper)
response = await api.blocks.children.list(block_id)
# response.results is list of dicts
# response.next_cursor for pagination
```

### 3. Explicit Parameters

All parameters match the Notion API specification exactly:

```python
# Parameters match API documentation
response = await api.blocks.children.append(
    block_id=block_id,
    children=[...]  # Exact API structure
)

# No transformation or smart defaults
```

### 4. No State Management

The low-level API doesn't maintain state between requests:

```python
# No caching
# No object relationships
# No stateful operations
# Each request is independent
```

## Quick Start

### Basic Usage

```python
from better_notion.api import NotionAPI

# Initialize with bot token
api = NotionAPI(auth="secret_...")

# Retrieve a page
page = await api.pages.retrieve(page_id="...")
print(page["title"])  # Access as dict

# Query a database
results = await api.databases.query(
    database_id="...",
    filter={...}  # Exact API filter structure
)
```

### With High-Level Client

```python
from better_notion import NotionClient

# High-level client uses low-level API internally
client = NotionClient(auth="secret_...")

# Access low-level API directly if needed
raw_response = await client._api.pages.retrieve(page_id)
```

## Components

### HTTP Client

Uses **httpx** for async HTTP requests with:
- HTTP/2 support
- Connection pooling
- Automatic decompression
- Timeout handling

**Documentation:** [HTTP Client](./http-client.md)

### Authentication

Supports multiple authentication methods:
- **Bearer Token** (Bot integrations)
- **OAuth 2.0** (Public integrations)

**Documentation:** [Authentication](./authentication.md)

### Rate Limiting

Intelligent rate limit handling:
- Tracks `x-ratelimit-*` headers
- Automatic retry with configurable strategy
- Proactive tracking (future feature)

**Documentation:** [Rate Limiting](./rate-limiting.md)

### Error Handling

Semantic exceptions mapped from HTTP errors:
- `HTTPError` (base)
- `NotFoundError` (404)
- `RateLimitedError` (429)
- `ValidationError` (400)
- And more...

**Documentation:** [Error Handling](./error-handling.md)

### Retry Logic

Automatic retry with exponential backoff:
- Default: 3 attempts
- Configurable backoff factor
- Retry on specific status codes and exceptions

### Pagination

Cursor-based pagination helpers:
- `PaginatedResponse` wrapper
- `PaginationHelper` for fetching all pages
- Manual cursor management

**Documentation:** [Pagination](./pagination.md)

## Endpoints

Each Notion API endpoint has a corresponding method:

```python
# Blocks endpoint
api.blocks.retrieve(block_id)
api.blocks.children.list(block_id)
api.blocks.children.append(block_id, children=[...])
api.blocks.update(block_id, ...)
api.blocks.delete(block_id)

# Pages endpoint
api.pages.retrieve(page_id)
api.pages.create(parent=..., properties=...)
api.pages.update(page_id, ...)
api.pages.retrieve_property_item(page_id, property_id)

# Databases endpoint
api.databases.retrieve(database_id)
api.databases.create(parent=..., title=..., schema=...)
api.databases.update(database_id, ...)
api.databases.query(database_id, filter=..., sort=...)

# Users endpoint
api.users.me()
api.users.retrieve(user_id)
api.users.list()

# Search endpoint
api.search.query(query=..., filter=..., sort=...)
```

**Documentation:** [Endpoints](./endpoints.md)

## Request/Response Flow

```
User Request
    │
    ├─→ Build Request (add headers, auth, etc.)
    │
    ├─→ Check Rate Limits
    │   └─→ Wait if needed
    │
    ├─→ Send HTTP Request (httpx)
    │   └─→ 3 attempts with exponential backoff
    │
    ├─→ Parse Response
    │   ├─→ Check for HTTP errors
    │   ├─→ Update rate limit tracking
    │   └─→ Return parsed JSON
    │
    └─→ Return to User
```

## Configuration

```python
api = NotionAPI(
    auth="secret_...",

    # HTTP configuration
    timeout=30,

    # API version
    api_version="2025-09-03",

    # Retry configuration
    retry_config=RetryConfig(
        max_attempts=3,
        backoff_factor=0.5
    ),

    # Rate limiting strategy
    rate_limit_strategy=RateLimitStrategy.WAIT,

    # Logging
    log_level="INFO",
    log_format="json"
)
```

## Testing

The low-level API is designed for easy testing:

```python
# Use mock recording
api = NotionAPI(
    auth="test_token",
    recording=RecordingMode.REPLAY,
    recording_file="fixtures/cassettes/test.json"
)

# Or use standard mocking
from unittest.mock import patch
with patch('httpx.AsyncClient.request') as mock:
    mock.return_value = mock_response
    result = await api.blocks.retrieve(block_id)
```

**Documentation:** [Testing](./testing.md)

## Migration from Notion API

If you're familiar with the Notion API directly:

| Notion API | Low-Level API |
|------------|---------------|
| `GET /pages/{page_id}` | `api.pages.retrieve(page_id)` |
| `POST /pages` | `api.pages.create(...)` |
| `POST /databases/{id}/query` | `api.databases.query(database_id, ...)` |
| Headers: `Authorization: Bearer token` | Handled automatically |
| Headers: `Notion-Version: 2025-09-03` | `api_version` parameter |

## Comparison: High-Level vs Low-Level

```python
# Low-Level: Raw API interaction
api = NotionAPI(auth=token)
page = await api.pages.retrieve(page_id)
title = page["properties"]["Name"]["title"][0]["plain_text"]

# High-Level: Rich abstractions
client = NotionClient(auth=token)
page = await client.pages.get(page_id)
title = page.title  # Direct property access
```

## Best Practices

### 1. Use Specific Error Handling

```python
try:
    page = await api.pages.retrieve(page_id)
except NotFoundError:
    logger.error(f"Page {page_id} not found")
except RateLimitedError as e:
    logger.warning(f"Rate limited, retry after {e.retry_after}s")
except HTTPError as e:
    logger.error(f"HTTP {e.status_code}: {e.message}")
```

### 2. Check Pagination

```python
response = await api.databases.query(database_id)

# Always check has_more
while response["has_more"]:
    cursor = response["next_cursor"]
    response = await api.databases.query(
        database_id,
        start_cursor=cursor
    )
```

### 3. Handle Rate Limits

```python
# Use WAIT strategy (default)
api = NotionAPI(
    auth=token,
    rate_limit_strategy=RateLimitStrategy.WAIT
)

# Or handle manually
api = NotionAPI(
    auth=token,
    rate_limit_strategy=RateLimitStrategy.FAIL
)

try:
    await api.pages.create(...)
except RateLimitedError as e:
    await asyncio.sleep(e.retry_after)
    await api.pages.create(...)
```

### 4. Log Requests

```python
# Enable debug logging
api = NotionAPI(
    auth=token,
    log_level="DEBUG"
)

# Logs all requests and responses
# Useful for debugging
```

## Performance Considerations

### HTTP/2

The low-level API uses httpx with HTTP/2 support:
- Multiplexing (multiple requests over single connection)
- Server push (when Notion supports it)
- Header compression

### Connection Pooling

httpx maintains a connection pool:
- Reuses connections across requests
- Reduces latency
- Configurable pool size

### Async Operations

All operations are async:
- Non-blocking I/O
- Can handle many concurrent requests
- Compatible with asyncio frameworks

## Versioning

The low-level API supports multiple Notion API versions:

```python
# Default: latest
api = NotionAPI(auth=token)

# Specific version
api = NotionAPI(
    auth=token,
    api_version="2022-06-28"
)
```

Supported versions:
- `2022-06-28`
- `2022-10-16`
- `2023-05-13`
- `2024-04-16`
- `2025-09-03` (latest)

## Related Documentation

- [HTTP Client](./http-client.md) - HTTP layer details
- [Authentication](./authentication.md) - Auth methods
- [Rate Limiting](./rate-limiting.md) - Rate limit handling
- [Error Handling](./error-handling.md) - Exception hierarchy
- [Endpoints](./endpoints.md) - Complete endpoint reference
- [Pagination](./pagination.md) - Pagination patterns
- [Testing](./testing.md) - Testing strategies

## Next Steps

1. Read the [HTTP Client](./http-client.md) documentation to understand the request layer
2. Review [Authentication](./authentication.md) for auth options
3. Check [Endpoints](./endpoints.md) for complete API reference
4. See [Testing](./testing.md) for testing approaches
