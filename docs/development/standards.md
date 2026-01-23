# Code Standards

Complete guide to code style, conventions, and best practices for the Better Notion SDK.

## Overview

This document defines the coding standards that all contributors must follow. Consistent code style makes the codebase easier to read, maintain, and review.

---

## Tooling

We use **ruff** for all code formatting and linting. It replaces multiple tools (black, isort, flake8, etc.).

**Configuration:** In `pyproject.toml`

```toml
[tool.ruff]
line-length = 100
target-version = "py310"

[tool.ruff.lint]
select = ["E", "F", "I", "N", "W", "UP"]
ignore = []

[tool.ruff.format]
quote-style = "double"
indent-style = "space"
```

---

## Naming Conventions

### General Rules

| Type | Convention | Example |
|------|-----------|---------|
| **Modules** | `lowercase_with_underscores` | `http_client.py` |
| **Packages** | `lowercase` or `lowercase_with_underscores` | `utils/` |
| **Classes** | `PascalCase` | `NotionAPI`, `HTTPClient` |
| **Functions/Methods** | `snake_case` | `retrieve_page()`, `is_valid()` |
| **Variables** | `snake_case` | `page_id`, `is_authenticated` |
| **Constants** | `UPPER_SNAKE_CASE` | `MAX_RETRIES`, `API_BASE_URL` |
| **Private** | `_leading_underscore` | `_internal_method()`, `_cache` |
| **Internal modules** | `_leading_underscore` | `_lowlevel/`, `_highlevel/` |

### Examples

```python
# Classes
class NotionAPI: ...
class HTTPClient: ...
class RateLimitedError(NotionAPIError): ...

# Functions and methods
async def retrieve_page(page_id: str) -> dict:
    ...

def is_authenticated() -> bool:
    ...

# Variables
page_id = "abc123"
is_authenticated = True
max_retries = 3

# Constants
MAX_RETRIES = 3
DEFAULT_TIMEOUT = 30
API_BASE_URL = "https://api.notion.com"

# Private
def _internal_method():
    ...

self._cache = {}  # Private attribute
```

---

## Type Hints

**Required for all public functions and methods.**

### Basic Type Hints

```python
from typing import Any

def retrieve_page(page_id: str) -> dict[str, Any]:
    """Retrieve a page by ID."""
    return await self._request("GET", f"/pages/{page_id}")
```

### Use Future Annotations

```python
# At the top of all files
from __future__ import annotations
```

This allows using forward references and removing quotes around types.

### Complex Types

```python
from typing import Optional, Union

def get_page(
    page_id: str,
    expand: Optional[bool] = None
) -> Union[dict, None]:
    ...
```

### Collections

```python
from typing import List, Dict

# Python 3.9+ (preferred)
def get_pages() -> list[dict]:
    ...

# Python 3.8 compatible
from __future__ import annotations  # Enables this
def get_pages() -> list[dict]:
    ...
```

### Async Functions

```python
async def retrieve_async(page_id: str) -> dict:
    """Async function."""
    ...
```

### Return Types

**Always specify return types:**

```python
# GOOD
def get_client() -> HTTPClient:
    return self._http

def get_page_id() -> str | None:  # Python 3.10+
    return self._page_id

# AVOID
def get_client():  # No return type
    return self._http
```

---

## Docstrings

**Use Google-style docstrings.**

### Function Docstrings

```python
def retrieve_page(page_id: str, expand: bool = False) -> dict:
    """Retrieve a page from Notion.

    Args:
        page_id: The unique identifier of the page.
        expand: Whether to expand child objects.

    Returns:
        A dictionary containing the page data.

    Raises:
        NotFoundError: If the page doesn't exist.
        RateLimitedError: If the rate limit is exceeded.
        HTTPError: For other HTTP errors.
    """
    ...
```

### Class Docstrings

```python
class NotionAPI:
    """Low-level Notion API client.

    This provides a 1:1 mapping with the Notion API.
    Use NotionClient for a higher-level interface.

    Attributes:
        auth: Authentication handler.
        pages: Pages endpoint.
        databases: Databases endpoint.

    Example:
        >>> api = NotionAPI(auth="secret_...")
        >>> page = await api.pages.retrieve("page_id")
    """
    ...
```

### Module Docstrings

```python
"""Notion API endpoints.

This module contains endpoint classes for interacting with
the Notion API. Each endpoint corresponds to a Notion API resource.
"""
```

---

## Code Layout

### Imports

**Group imports in this order:**

```python
# 1. Standard library
import asyncio
from logging import getLogger
from typing import Any

# 2. Third-party packages
import httpx
from pydantic import BaseModel

# 3. Local application imports
from better_notion._lowlevel.errors import NotionAPIError
from better_notion.utils.constants import API_BASE_URL
```

**Each group separated by a blank line.**

**Sort within groups alphabetically.**

### Absolute vs Relative Imports

**Prefer absolute imports:**

```python
# GOOD
from better_notion._lowlevel import NotionAPI
from better_notion.utils.helpers import validate_id

# AVOID (except in __init__.py)
from ..client import NotionAPI
from .helpers import validate_id
```

**Exception:** Relative imports OK in `__init__.py` files.

---

## Whitespace

### Blank Lines

**Two blank lines** before:
- Top-level classes
- Top-level functions

**One blank line** before:
- Methods within classes

```python
class MyClass:
    """My class."""

    def method1(self):
        """First method."""
        pass

    def method2(self):
        """Second method."""
        pass


class AnotherClass:
    """Another class."""
    pass
```

### Trailing Whitespace

**No trailing whitespace.**

```python
# GOOD
x = 1

# AVOID
x = 1     ← trailing whitespace here
```

### Maximum Line Length

**Target:** 100 characters

```python
# GOOD
result = await api.pages.retrieve(
    page_id="abc123",
    expand=False
)

# AVOID - Too long
result = await api.pages.retrieve(page_id="abc123", expand=False, include_children=True, recursive=True)
```

---

## String Quotes

**Use double quotes by default.**

```python
# GOOD
message = "Hello, world!"
json_data = '{"key": "value"}'

# SINGLE QUOTES - Use only when string contains double quotes
quote = 'He said "Hello"'
```

---

## Comments

### When to Comment

**Comment WHY, not WHAT.**

```python
# GOOD - Explains why
# Retry with exponential backoff to handle rate limits
await self._retry_with_backoff(request)

# AVOID - Repeats the code
# Set timeout to 30 seconds
timeout = 30
```

### Comment Style

```python
# Inline comment - Separate from code with two spaces
x = 1  # This is a comment

# Block comment - For longer explanations
# This is a longer comment that explains
# a complex concept or algorithm.
# It can span multiple lines.
```

### TODO Comments

```python
# TODO: Add support for OAuth refresh tokens
# FIXME: This doesn't handle edge case X
# HACK: Temporary workaround for issue #123
# NOTE: This is intentional because...
```

---

## Error Handling

### Exception Naming

```python
# Base class
class NotionAPIError(Exception):
    """Base exception for all Notion API errors."""
    pass

# Specific exceptions
class HTTPError(NotionAPIError):
    """Base class for HTTP errors."""
    pass

class NotFoundError(HTTPError):
    """Resource not found (404)."""
    pass

class RateLimitedError(HTTPError):
    """Rate limit exceeded (429)."""
    pass
```

### Raising Exceptions

```python
# GOOD - Specific exception
if not page_id:
    raise ValueError("page_id cannot be empty")

if response.status_code == 404:
    raise NotFoundError(f"Page not found: {page_id}")
```

### Catching Exceptions

```python
# GOOD - Catch specific exceptions
try:
    page = await api.pages.retrieve(page_id)
except NotFoundError:
    logger.error(f"Page not found: {page_id}")
except RateLimitedError as e:
    logger.warning(f"Rate limited: {e}")
    await asyncio.sleep(e.retry_after)

# AVOID - Catching all exceptions
try:
    page = await api.pages.retrieve(page_id)
except Exception:  # Too broad
    pass
```

### Exception Chaining

```python
try:
    response = await self._http.request(...)
except httpx.HTTPError as e:
    # Preserve original exception
    raise HTTPError("HTTP request failed") from e
```

---

## Async/Await Patterns

### Async Functions

```python
# All async functions must be awaitable
async def retrieve_page(page_id: str) -> dict:
    response = await self._http.get(f"/pages/{page_id}")
    return response.json()
```

### Async Context Managers

```python
# GOOD - Use async context managers
async with NotionAPI(auth=token) as api:
    page = await api.pages.retrieve("page_id")
```

### Avoid Blocking Calls

```python
# AVOID - Blocking call in async function
async def get_page():
    time.sleep(1)  # BAD - blocks event loop

# GOOD
async def get_page():
    await asyncio.sleep(1)  # Non-blocking
```

---

## Class Design

### Single Responsibility

```python
# GOOD - Each class has one responsibility
class HTTPClient:
    """Handles HTTP communication only."""
    ...

class RateLimitTracker:
    """Tracks rate limits only."""
    ...

class NotionAPI:
    """Coordinates HTTP, auth, rate limiting."""
    ...
```

### Composition Over Inheritance

```python
# GOOD - Composition
class NotionAPI:
    def __init__(self):
        self._http = HTTPClient()
        self._auth = AuthHandler()
        self._rate_limit = RateLimitTracker()
```

### Properties

```python
# GOOD - Use properties for computed attributes
class Page:
    @property
    def is_published(self) -> bool:
        """Check if page is published."""
        return self.properties.get("status") == "Published"

# AVOID - Methods for simple attribute access
class Page:
    def is_published(self) -> bool:  # Should be a property
        return self.properties.get("status") == "Published"
```

---

## Logging

### Logging Setup

```python
import logging

logger = logging.getLogger(__name__)

# In code
logger.debug("Debug message")
logger.info("Info message")
logger.warning("Warning message")
logger.error("Error message")
logger.exception("Exception with traceback")
```

### Log Levels

- **DEBUG** - Detailed diagnostic information
- **INFO** - General informational messages
- **WARNING** - Something unexpected but recoverable
- **ERROR** - Error occurred but execution continues
- **EXCEPTION** - Error with exception info

### What to Log

```python
# GOOD - Log useful information
logger.info(f"Retrieving page: {page_id}")
logger.debug(f"Response status: {response.status_code}")
logger.error(f"Failed to retrieve page: {page_id}", exc_info=True)

# AVOID - Log sensitive data
logger.info(f"Using token: {auth_token}")  # BAD - logs token
```

---

## Patterns to Follow

### Dependency Injection

```python
# GOOD - Inject dependencies
class NotionAPI:
    def __init__(
        self,
        http_client: HTTPClient | None = None,
        auth: AuthHandler | None = None
    ):
        self._http = http_client or HTTPClient()
        self._auth = auth or AuthHandler()
```

### Context Managers

```python
# GOOD - Use context managers for resources
async with httpx.AsyncClient() as client:
    response = await client.get(url)
```

### Type Guards

```python
# GOOD - Use type guards
def is_page(obj: dict) -> bool:
    """Check if object is a page."""
    return obj.get("object") == "page"
```

---

## Patterns to Avoid

### Global State

```python
# AVOID - Global state
api = NotionAPI()  # Global instance

def get_page():
    return api.pages.retrieve("...")

# GOOD - Pass dependencies
def get_page(api: NotionAPI):
    return api.pages.retrieve("...")
```

### Magic Numbers

```python
# AVOID - Magic numbers
timeout = 30
max_retries = 3

# GOOD - Use constants
DEFAULT_TIMEOUT = 30
MAX_RETRIES = 3
timeout = DEFAULT_TIMEOUT
max_retries = MAX_RETRIES
```

### Overly Generic Names

```python
# AVOID
def process(data):
    ...

def handle(item):
    ...

# GOOD
def retrieve_page(page_id: str):
    ...

def validate_auth_token(token: str):
    ...
```

---

## Testing Conventions

See [testing-strategy.md](./testing-strategy.md) for detailed testing conventions.

### Basic Pattern

```python
@pytest.mark.asyncio
async def test_retrieve_page_success(mock_api):
    """Test retrieving a page successfully."""
    # Arrange
    page_id = "test_page_id"
    mock_response = {"id": page_id, "object": "page"}

    # Act
    with patch.object(mock_api._http, "request", return_value=mock_response):
        result = await mock_api.pages.retrieve(page_id)

    # Assert
    assert result["id"] == page_id
    assert result["object"] == "page"
```

---

## Review Checklist

Before submitting code, verify:

- [ ] Code follows ruff formatting (`uv run ruff format`)
- [ ] No linting errors (`uv run ruff check`)
- [ ] Type hints on all public functions
- [ ] Docstrings on all public classes/functions
- [ ] No sensitive data in code/logs
- [ ] No commented-out code
- [ ] No overly long lines (>100 chars)
- [ ] Imports properly grouped
- [ ] Naming follows conventions
- [ ] Error handling is appropriate
- [ ] Tests added/updated

---

## Related Documentation

- [project-structure.md](./project-structure.md) - File organization
- [testing-strategy.md](./testing-strategy.md) - Testing patterns
- [debugging.md](./debugging.md) - Debugging techniques

---

## Summary

**Key Standards:**

1. **Naming:** snake_case for functions/variables, PascalCase for classes
2. **Type hints:** Required on all public functions
3. **Docstrings:** Google-style, required for public API
4. **Formatting:** ruff with 100 character line length
5. **Imports:** Absolute, grouped (stdlib → third-party → local)
6. **Comments:** Explain WHY, not WHAT
7. **Errors:** Specific exceptions, proper chaining
8. **Logging:** Structured, no sensitive data

**Remember:**
- Consistency is key
- Code is read more than written
- When in doubt, follow existing patterns

---

**Last Updated:** 2025-01-23
