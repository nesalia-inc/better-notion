# Project Structure

Complete guide to the Better Notion SDK project organization.

## Overview

This document explains the complete folder structure of the project, what each directory contains, and how to organize code within it.

---

## Directory Tree

```
better-notion/
├── better_notion/              # Main package
│   ├── __init__.py            # Public API exports
│   ├── _lowlevel/             # Low-level API (internal)
│   │   ├── __init__.py
│   │   ├── client.py          # NotionAPI class
│   │   ├── http.py            # HTTP client wrapper
│   │   ├── auth.py            # Authentication handlers
│   │   ├── errors.py          # Exception definitions
│   │   ├── retry.py           # Retry logic
│   │   ├── rate_limit.py      # Rate limiting
│   │   └── endpoints/         # API endpoint classes
│   │       ├── __init__.py
│   │       ├── blocks.py      # Blocks endpoint
│   │       ├── pages.py       # Pages endpoint
│   │       ├── databases.py   # Databases endpoint
│   │       ├── users.py       # Users endpoint
│   │       ├── search.py      # Search endpoint
│   │       └── comments.py    # Comments endpoint
│   ├── _highlevel/            # High-level API (internal)
│   │   ├── __init__.py
│   │   ├── client.py          # NotionClient class
│   │   ├── models/            # Entity models
│   │   │   ├── __init__.py
│   │   │   ├── base.py        # BaseEntity class
│   │   │   ├── page.py        # Page model
│   │   │   ├── database.py    # Database model
│   │   │   ├── block.py       # Block model
│   │   │   ├── user.py        # User model
│   │   │   └── workspace.py   # Workspace model
│   │   ├── cache/             # Caching layer
│   │   │   ├── __init__.py
│   │   │   ├── interface.py   # Cache interface
│   │   │   └── memory.py      # In-memory cache
│   │   └── properties/        # Property helpers
│   │       ├── __init__.py
│   │       └── builder.py     # Property builder
│   └── utils/                 # Shared utilities
│       ├── __init__.py
│       ├── helpers.py         # Helper functions
│       └── constants.py       # Constants
│
├── tests/                     # Test suite
│   ├── unit/                  # Unit tests (no network)
│   │   ├── test_http_client.py
│   │   ├── test_auth.py
│   │   ├── test_endpoints.py
│   │   ├── test_pagination.py
│   │   ├── test_retry.py
│   │   └── test_rate_limit.py
│   ├── integration/           # Integration tests
│   │   ├── test_api_client.py
│   │   └── test_real_api.py
│   ├── fixtures/              # Test data
│   │   ├── pages/
│   │   │   └── page_1.json
│   │   ├── databases/
│   │   │   └── database_1.json
│   │   └── responses/
│   │       └── test_response.json
│   └── conftest.py            # Shared pytest fixtures
│
├── .github/                   # GitHub configuration
│   └── workflows/             # CI/CD workflows
│       ├── ci.yml
│       ├── lint.yml
│       ├── test.yml
│       └── release.yml
│
├── docs/                      # Documentation
│   ├── PROJECT.md             # Project vision
│   ├── README.md              # Documentation navigation
│   ├── api/                   # Notion API reference
│   ├── sdk/                   # SDK design docs
│   ├── cicd/                  # CI/CD documentation
│   └── development/           # This section
│
├── pyproject.toml             # Project configuration
├── pytest.ini                 # Pytest configuration
├── .gitignore                 # Git ignore rules
├── LICENSE                    # MIT License
├── README.md                  # Public README
└── CHANGELOG.md               # Version history
```

---

## Module Responsibilities

### `better_notion/` - Main Package

**Purpose:** All source code for the SDK.

**Key files:**

#### `__init__.py` - Public API Exports

```python
"""
Better Notion SDK - A high-level Python SDK for the Notion API.
"""

# Low-level API
from better_notion._lowlevel import NotionAPI

# High-level API
from better_notion._highlevel import NotionClient

# Exceptions
from better_notion._lowlevel.errors import (
    NotionAPIError,
    HTTPError,
    RateLimitedError,
    NotFoundError,
    # ... etc
)

# Version
__version__ = "0.1.0"
```

**Rules:**
- Only export public API here
- Import from internal modules
- Keep imports minimal

### `_lowlevel/` - Low-Level API

**Purpose:** Direct 1:1 mapping with Notion API. Minimal abstraction.

**Naming:** Underscore prefix = internal module (not public API).

**Files:**

- **`client.py`** - `NotionAPI` class
  - Entry point for low-level API
  - Manages HTTP client, auth, endpoints
  - Very thin wrapper around HTTP

- **`http.py`** - HTTP client wrapper
  - Wraps httpx
  - Handles retries, timeouts
  - Rate limiting integration

- **`auth.py`** - Authentication
  - `BearerAuth` class
  - `OAuthHandler` class (future)
  - Token refresh logic

- **`errors.py`** - Exception hierarchy
  - `NotionAPIError` base class
  - All specific exceptions

- **`retry.py`** - Retry logic
  - `RetryHandler` class
  - Exponential backoff

- **`rate_limit.py`** - Rate limiting
  - `RateLimitTracker` class
  - WAIT/FAIL/PROACTIVE strategies

- **`endpoints/`** - API endpoint classes
  - Each Notion API endpoint = one file
  - `BlocksEndpoint`, `PagesEndpoint`, etc.
  - Simple methods: `retrieve()`, `list()`, `create()`, etc.

### `_highlevel/` - High-Level API

**Purpose:** Rich abstractions, caching, semantic operations.

**Naming:** Underscore prefix = internal module (not public API).

**Files:**

- **`client.py`** - `NotionClient` class
  - Entry point for high-level API
  - Manages cache, models
  - High-level operations

- **`models/`** - Entity models
  - Each Notion entity type = one file
  - `Page`, `Database`, `Block`, `User`, `Workspace`
  - Rich methods and properties

- **`cache/`** - Caching layer
  - `CacheInterface` - Abstract base
  - `MemoryCache` - In-memory implementation
  - Future: RedisCache, etc.

- **`properties/`** - Property helpers
  - `PropertyBuilder` - Build property filters
  - Fluent API for queries

### `utils/` - Shared Utilities

**Purpose:** Helper functions used by both low-level and high-level.

**Files:**

- **`helpers.py`** - Helper functions
  - ID validation
  - Date parsing
  - Type conversion utilities

- **`constants.py`** - Constants
  - API base URL
  - Default timeouts
  - Header names
  - Error codes

### `tests/` - Test Suite

**Purpose:** Comprehensive test coverage.

**Structure mirrors `better_notion/`:**
```
better_notion/_lowlevel/http.py  →  tests/unit/test_http_client.py
better_notion/_lowlevel/auth.py  →  tests/unit/test_auth.py
```

**Files:**

- **`unit/`** - Unit tests
  - Test individual functions/classes
  - No network calls
  - Mock all external dependencies
  - Fast (<100ms each)

- **`integration/`** - Integration tests
  - Test interactions between components
  - May use network
  - Slower but more realistic

- **`fixtures/`** - Test data
  - Sample API responses
  - Mock data generators

- **`conftest.py`** - Shared pytest configuration
  - Global fixtures
  - Pytest hooks
  - Test configuration

---

## File Organization Patterns

### Pattern 1: One Class Per File

**Good:**
```
_lowlevel/endpoints/
├── blocks.py      # class BlocksEndpoint
├── pages.py       # class PagesEndpoint
└── databases.py   # class DatabasesEndpoint
```

**Avoid:**
```
_lowlevel/endpoints.py  # Multiple classes in one file
```

### Pattern 2: Related Classes Together

**Good:**
```
_lowlevel/auth.py
├── class BearerAuth
└── class OAuthHandler  # Related: both authentication
```

### Pattern 3: Tests Mirror Source

**Good:**
```
better_notion/_lowlevel/http.py        tests/unit/test_http_client.py
better_notion/_lowlevel/auth.py        tests/unit/test_auth.py
better_notion/_highlevel/models/page.py  tests/unit/test_models/test_page.py
```

---

## Naming Conventions

### Modules and Packages

- **Packages:** `lowercase_with_underscores` or `alllowercase`
  - `better_notion/`
  - `utils/`

- **Modules:** `lowercase_with_underscores.py`
  - `http_client.py`
  - `rate_limit.py`

- **Internal modules:** `_leading_underscore`
  - `_lowlevel/`
  - `_highlevel/`
  - `auth.py` → `_auth.py` if internal (but we keep in `internal/` package)

### Classes

- **PascalCase**
  ```python
  class NotionAPI: ...
  class HTTPClient: ...
  class RateLimitedError: ...
  ```

### Functions and Variables

- **snake_case**
  ```python
  async def retrieve_page(): ...
  is_authenticated = True
  max_retries = 3
  ```

### Constants

- **UPPER_SNAKE_CASE**
  ```python
  MAX_RETRIES = 3
  DEFAULT_TIMEOUT = 30
  API_BASE_URL = "https://api.notion.com"
  ```

### Private

- **Leading underscore**
  ```python
  def _internal_method(): ...
  self._cache = {}
  ```

---

## Import Conventions

### Absolute Imports

**Use absolute imports:**
```python
from better_notion._lowlevel import NotionAPI
from better_notion._lowlevel.errors import NotionAPIError
from better_notion.utils.helpers import validate_id
```

**Avoid relative imports:**
```python
from ..client import NotionAPI  # AVOID
from .errors import NotionAPIError  # AVOID (except in __init__.py)
```

### Exception: In `__init__.py` Files

**Relative imports OK in `__init__.py`:**
```python
# _lowlevel/__init__.py
from .client import NotionAPI
from .errors import *
```

### Import Order

**Group imports in this order:**

1. Standard library
2. Third-party packages
3. Local application imports

```python
# 1. Standard library
import asyncio
from logging import getLogger

# 2. Third-party
import httpx
from pydantic import BaseModel

# 3. Local
from better_notion._lowlevel.errors import NotionAPIError
from better_notion.utils.constants import API_BASE_URL
```

---

## Where to Put New Code

### Adding a New Endpoint

1. Create file in `_lowlevel/endpoints/`
   ```python
   # _lowlevel/endpoints/comments.py
   class CommentsEndpoint(EndpointBase):
       async def retrieve(self, comment_id: str) -> dict:
           ...
   ```

2. Import in `_lowlevel/endpoints/__init__.py`
   ```python
   from .comments import CommentsEndpoint
   ```

3. Add to `NotionAPI` client
   ```python
   # _lowlevel/client.py
   @property
   def comments(self) -> CommentsEndpoint:
       return CommentsEndpoint(self)
   ```

4. Create test file
   ```python
   # tests/unit/test_endpoints/test_comments.py
   ```

### Adding a New Model

1. Create file in `_highlevel/models/`
   ```python
   # _highlevel/models/comment.py
   class Comment(BaseModel):
       id: str
       parent: dict
       # ...
   ```

2. Import in `_highlevel/models/__init__.py`

3. Add methods to `NotionClient`
   ```python
   # _highlevel/client.py
   async def get_comment(self, comment_id: str) -> Comment:
       ...
   ```

### Adding a New Utility

1. Add to appropriate file in `utils/`
   - `helpers.py` for functions
   - `constants.py` for constants

2. Import where needed
   ```python
   from better_notion.utils.helpers import validate_id
   ```

---

## Module Visibility

### Public API

**Exported from `better_notion/__init__.py`:**
```python
from better_notion import NotionAPI, NotionClient
from better_notion._lowlevel.errors import NotionAPIError
```

**Stability:** Follows semantic versioning. Breaking changes only in major versions.

### Internal API

**Modules starting with `_`:**
```python
from better_notion._lowlevel import NotionAPI  # Public but via re-export
from better_notion._lowlevel.http import HTTPClient  # Internal, can change
```

**Stability:** Can change at any time. Not part of public API.

### Guideline

- **Use `_` prefix** for modules not in public API
- **Export public API** from `__init__.py`
- **Import internals** directly when needed
- **Document** what's public vs internal

---

## File Size Guidelines

### Target File Sizes

- **Code files:** 200-500 lines per file
- **Test files:** 100-300 lines per file

**If file gets too large (>500 lines):**
- Split into multiple files
- Extract related functionality

**Exceptions:**
- `__init__.py` can be smaller
- Very cohesive classes can be larger

---

## Related Documentation

- [standards.md](./standards.md) - Code style and conventions
- [testing-strategy.md](./testing-strategy.md) - Test organization
- [workflow.md](./workflow.md) - How to work with this structure

---

## Summary

**Key Points:**

1. **Two-level architecture:** `_lowlevel/` and `_highlevel/`
2. **Internal modules:** Use `_` prefix
3. **One class per file:** For endpoints and models
4. **Tests mirror source:** Parallel structure
5. **Absolute imports:** Prefer over relative
6. **Public API:** Export from `__init__.py`

**Questions to ask when adding code:**

- Is this low-level or high-level?
- Where does it belong (which module)?
- What should I name the file?
- Do I need to update `__init__.py`?
- Where do the tests go?

---

**Last Updated:** 2025-01-23
