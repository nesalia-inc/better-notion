# Better Notion - Notion API Structure Reference

## Overview

This document describes the fundamental structure and conventions of the Notion API, serving as the foundation for the Better Notion SDK implementation.

## Base Configuration

### API Endpoint
```
Base URL: https://api.notion.com
Protocol: HTTPS (required)
Data Format: JSON
Architecture: RESTful
```

### Authentication

All API requests require authentication via an **Integration Token** (also called Bot Token).

**Token Format:**
```
Authorization: Bearer <secret_bot_token>
```

**Token Source:**
- Created via Integration Settings in Notion
- Workspace admin access required
- Token format: `secret_XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX`

**Implementation for Better Notion:**
```python
class NotionClient:
    def __init__(self, token: str):
        if not token.startswith("secret_"):
            raise InvalidTokenError("Token must start with 'secret_'")
        self.token = token
        self._headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "Notion-Version": "2022-06-28"  # API version
        }
```

## JSON Conventions

### Resource Structure

All top-level resources follow this structure:

```json
{
  "object": "resource_type",  // Type identifier
  "id": "uuid-v4",            // Unique identifier
  "created_time": "ISO-8601",  // Creation timestamp
  "last_edited_time": "ISO-8601",  // Last edit timestamp
  ...                         // Resource-specific properties
}
```

### Property Naming Convention

- **Style:** `snake_case` (not `camelCase` or `kebab-case`)
- **Examples:** `created_time`, `last_edited_time`, `cover_image`

**Better Notion Implementation:**
```python
@dataclass
class NotionObject:
    object: str
    id: UUID4
    created_time: datetime
    last_edited_time: datetime

    def to_dict(self) -> dict:
        """Convert to API-compatible dict with snake_case keys."""
        return asdict(self)
```

### ID Format

**Format:** UUIDv4 (dashes optional in requests)

**Examples:**
```
Full:    33e19cb9-751f-4993-b74d-234d67d0d534
Short:   33e19cb9751f4993b74d234d67d0d534
```

**Better Notion Implementation:**
```python
def normalize_id(id: str) -> str:
    """Accept IDs with or without dashes."""
    # Remove dashes if present
    clean_id = id.replace("-", "")
    # Validate format
    if len(clean_id) != 32:
        raise InvalidIdError(f"Invalid ID format: {id}")
    return clean_id

# Or use UUID library
from uuid import UUID

def parse_id(id: str) -> UUID:
    """Parse ID with or without dashes."""
    return UUID(id)
```

### Temporal Values

**Format:** ISO 8601 strings

**Date Examples:**
```
Date:     2020-08-12
DateTime: 2020-08-12T02:12:33.231Z
```

**Better Notion Implementation:**
```python
from datetime import datetime, date
from dateutil.parser import isoparse

def parse_datetime(iso_string: str) -> datetime:
    """Parse ISO 8601 datetime string."""
    return isoparse(iso_string)

def format_datetime(dt: datetime) -> str:
    """Format datetime to ISO 8601 string."""
    return dt.isoformat(timespec="milliseconds") + "Z"

def parse_date(iso_string: str) -> date:
    """Parse ISO 8601 date string."""
    return datetime.fromisoformat(iso_string).date()

def format_date(d: date) -> str:
    """Format date to ISO 8601 string."""
    return d.isoformat()
```

### Empty Values

**Important:** The Notion API does **NOT** support empty strings (`""`)

**Solution:** Use explicit `null` to unset string values

```json
❌ DON'T:  {"url": ""}
✅ DO:    {"url": null}
```

**Better Notion Implementation:**
```python
def sanitize_value(value: Any) -> Any:
    """
    Convert empty strings to None/null for API compatibility.
    """
    if isinstance(value, str) and value == "":
        return None
    return value

# Example usage
data = {
    "title": sanitize_value(title),      # "" → None
    "url": sanitize_value(url),          # "" → None
    "properties": {...}
}
```

## HTTP Methods & Operations

| Method | Usage | Examples |
|--------|-------|----------|
| `GET` | Retrieve resources | Get page, list users, search |
| `POST` | Create resources or complex queries | Create page, query database, search |
| `PATCH` | Update existing resources | Update page, update database |
| `DELETE` | Remove resources | Delete block, delete page |

## Object Types

### Core Object Types

| Type | Description | Example Endpoints |
|------|-------------|-------------------|
| `database` | Database container | `/databases/{id}` |
| `page` | Page object | `/pages/{id}` |
| `block` | Content block | `/blocks/{id}` |
| `user` | User object | `/users/{id}` |
| `comment` | Comment object | `/comments/{id}` |
| `list` | Paginated list response | All list endpoints |

### Special Types

| Type | Description |
|------|-------------|
| `page_or_database` | Used in search results |
| `property_item` | Page property values |
| `workspace` | Workspace information |

**Better Notion Type Mapping:**
```python
class ObjectType(str, Enum):
    DATABASE = "database"
    PAGE = "page"
    BLOCK = "block"
    USER = "user"
    COMMENT = "comment"
    LIST = "list"
    PAGE_OR_DATABASE = "page_or_database"
    PROPERTY_ITEM = "property_item"
    WORKSPACE = "workspace"
```

## Pagination

### Paginated Endpoints

The following endpoints support cursor-based pagination:

| Method | Endpoint | Returns |
|--------|----------|---------|
| `GET` | `/users` | List of users |
| `GET` | `/blocks/{id}/children` | List of child blocks |
| `GET` | `/comments/{id}` | List of comments |
| `GET` | `/pages/{id}/properties/{id}` | List of property values |
| `POST` | `/databases/{id}/query` | Database query results |
| `POST` | `/search` | Search results |

### Pagination Response Structure

```json
{
  "object": "list",
  "results": [
    // Array of endpoint-specific objects
  ],
  "has_more": true,
  "next_cursor": "33e19cb9-751f-4993-b74d-234d67d0d534",
  "type": "page_or_database"
}
```

### Response Fields

| Field | Type | Description |
|-------|------|-------------|
| `object` | string | Always `"list"` for paginated responses |
| `results` | array | Array of objects (type varies by endpoint) |
| `has_more` | boolean | `true` if more results available, `false` if end of list |
| `next_cursor` | string \| null | Cursor for next page (only when `has_more: true`) |
| `type` | string | Type of objects in results |
| `{type}` | object | Type-specific pagination info (usually empty object) |

### Request Parameters

**Note:** Parameter location varies by HTTP method

| Parameter | Type | Location | Description |
|-----------|------|----------|-------------|
| `page_size` | number | GET: query string<br>POST: body | Number of items to return<br>**Default:** 10<br>**Maximum:** 100 |
| `start_cursor` | string | GET: query string<br>POST: body | Cursor from previous response for next page |

### Pagination Behavior

**Default Behavior:**
- Returns **10 items per request** by default
- May return fewer items than requested

**Manual Pagination:**

```python
# First request
response = await client.databases.query(database_id)
results = response.results

# Fetch subsequent pages
while response.has_more:
    response = await client.databases.query(
        database_id,
        start_cursor=response.next_cursor
    )
    results.extend(response.results)
```

**Better Notion Automatic Pagination (Recommended):**

```python
# Option 1: Get all results automatically
all_pages = await client.databases.query_all(database_id)

# Option 2: Async iterator for memory efficiency
async for page in client.databases.query_iter(database_id):
    # Process each page as it's fetched
    print(page)

# Option 3: Generator
for page in client.databases.query_generator(database_id):
    print(page)
```

### Pagination Implementation

```python
from dataclasses import dataclass
from typing import Generic, TypeVar, List, Optional

T = TypeVar('T')

@dataclass
class PaginatedResponse(Generic[T]):
    """Generic paginated response from Notion API."""
    object: str = "list"
    results: List[T] = field(default_factory=list)
    has_more: bool = False
    next_cursor: Optional[str] = None
    type: str = ""

    @classmethod
    def from_dict(cls, data: dict, result_type: type[T]) -> "PaginatedResponse[T]":
        """Parse API response into typed objects."""
        results = [result_type.from_dict(r) for r in data.get("results", [])]
        return cls(
            results=results,
            has_more=data.get("has_more", False),
            next_cursor=data.get("next_cursor"),
            type=data.get("type", "")
        )


class AsyncPaginator(Generic[T]):
    """Async iterator for paginated results."""

    def __init__(self, fetch_fn, start_cursor: Optional[str] = None):
        self.fetch_fn = fetch_fn
        self._current_cursor = start_cursor
        self._has_more = True

    def __aiter__(self):
        return self

    async def __anext__(self):
        if not self._has_more:
            raise StopAsyncIteration

        response = await self.fetch_fn(start_cursor=self._current_cursor)

        # Update pagination state
        self._has_more = response.has_more
        self._current_cursor = response.next_cursor

        return response.results
```

## Error Handling

### Expected Error Format

```json
{
  "object": "error",
  "status": number,
  "code": "error_code",
  "message": "Human-readable error message"
}
```

### Common Error Codes

| Code | Description | HTTP Status |
|------|-------------|-------------|
| `invalid_json` | Invalid JSON in request body | 400 |
| `invalid_request_url` | Invalid request URL | 400 |
| `invalid_request` | Invalid request parameters | 400 |
| `validation_error` | Request body validation error | 400 |
| `missing_version` | Missing Notion-Version header | 400 |
| `unauthorized` | Invalid or missing access token | 401 |
| `restricted_resource` | Not authorized to access this resource | 403 |
| `object_not_found` | Resource does not exist | 404 |
| `conflict_error` | Conflict with current state | 409 |
| `rate_limited` | Request rate limit exceeded | 429 |
| `internal_server_error` | Internal Notion error | 500 |
| `service_unavailable` | Service temporarily unavailable | 503 |

### Better Notion Exception Hierarchy

```python
class NotionError(Exception):
    """Base exception for all Notion API errors."""
    pass

class AuthenticationError(NotionError):
    """Raised when authentication fails (401)."""
    pass

class PermissionError(NotionError):
    """Raised when access is forbidden (403)."""
    pass

class NotFoundError(NotionError):
    """Raised when resource is not found (404)."""
    pass

class ValidationError(NotionError):
    """Raised when request validation fails (400)."""
    pass

class RateLimitError(NotionError):
    """Raised when rate limit is exceeded (429)."""
    pass

class ConflictError(NotionError):
    """Raised when there's a conflict (409)."""
    pass

class APIError(NotionError):
    """Raised for general API errors (5xx)."""
    pass
```

## Rate Limiting

**Current Limits (as of documentation):**
- Rate limits are enforced per integration
- Specific limits not detailed in this section
- SDK should implement retry logic with exponential backoff

**Recommended Implementation:**

```python
import asyncio
from typing import Callable, Any

class RateLimitedClient:
    def __init__(self, max_retries: int = 3):
        self.max_retries = max_retries

    async def request_with_retry(
        self,
        request_fn: Callable,
        *args,
        **kwargs
    ) -> Any:
        """Execute request with automatic retry on rate limit."""
        for attempt in range(self.max_retries):
            try:
                return await request_fn(*args, **kwargs)
            except RateLimitError as e:
                if attempt == self.max_retries - 1:
                    raise

                # Exponential backoff: 2^attempt seconds
                wait_time = 2 ** attempt
                await asyncio.sleep(wait_time)

        raise RateLimitError("Max retries exceeded")
```

## SDK Architecture Implications

### Core Components

1. **HTTP Client**
   - Handle base URL construction
   - Manage authentication headers
   - Implement retry logic
   - Support both sync and async

2. **Object Mappers**
   - Convert JSON responses to typed Python objects
   - Handle snake_case naming
   - Parse ISO 8601 dates
   - Validate UUIDs

3. **Pagination Handler**
   - Automatic pagination option
   - Manual pagination support
   - Memory-efficient streaming

4. **Error Handler**
   - Map HTTP status codes to exceptions
   - Provide meaningful error messages
   - Include request context in errors

### Design Patterns

**Factory Pattern** for object creation:
```python
class NotionObjectFactory:
    @staticmethod
    def create(data: dict) -> NotionObject:
        object_type = data.get("object")

        if object_type == "database":
            return Database.from_dict(data)
        elif object_type == "page":
            return Page.from_dict(data)
        # ... etc
        else:
            raise UnknownObjectType(object_type)
```

**Builder Pattern** for complex queries:
```python
class DatabaseQuery:
    def __init__(self):
        self.filters = []
        self.sorts = []

    def filter(self, property: str, condition: str, value: Any):
        self.filters.append({
            "property": property,
            condition: value
        })
        return self

    def sort_by(self, property: str, direction: str):
        self.sorts.append({
            "property": property,
            "direction": direction
        })
        return self

    def build(self) -> dict:
        return {
            "filter": {"and": self.filters} if self.filters else None,
            "sorts": self.sorts
        }
```

## Summary Checklist

For Better Notion implementation, ensure:

- [ ] All requests use HTTPS and base URL `https://api.notion.com`
- [ ] Integration token format validation (`secret_*`)
- [ ] Snake_case property naming throughout
- [ ] UUID handling with optional dashes
- [ ] ISO 8601 datetime parsing and formatting
- [ ] Empty strings converted to `null`
- [ ] Cursor-based pagination for all list endpoints
- [ ] Automatic retry with exponential backoff for rate limits
- [ ] Comprehensive exception hierarchy
- [ ] Type-safe object mapping
- [ ] Support for both manual and automatic pagination
- [ ] Proper HTTP method usage (GET, POST, PATCH, DELETE)
- [ ] Notion-Version header inclusion

---

**Next Steps:** Refer to individual endpoint documentation for detailed object structures and specific API operations.
