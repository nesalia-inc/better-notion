# Testing Strategy

Complete guide to writing and organizing tests for the Better Notion SDK.

## Overview

Testing is critical for ensuring code quality and preventing regressions. This document explains our testing philosophy, patterns, and best practices.

---

## Testing Philosophy

### Principles

1. **Fast tests** - Unit tests should be fast (<100ms each)
2. **Isolated** - Tests should not depend on each other
3. **Clear** - Tests should be self-documenting
4. **Comprehensive** - Target ≥80% code coverage
5. **Realistic** - Test real scenarios, not just happy paths

### Test Pyramid

```
        /\
       /  \        Few E2E tests
      /____\       (slow, expensive)
     /      \
    /        \     More integration tests
   /          \    (medium speed)
  /____________\
 /              \  Many unit tests
/                \ (fast, cheap)
```

**Recommended distribution:**
- 70% unit tests
- 20% integration tests
- 10% E2E tests (optional)

---

## Test Organization

### Directory Structure

```
tests/
├── unit/                      # Fast, isolated tests
│   ├── test_http_client.py    # Test HTTP client
│   ├── test_auth.py           # Test authentication
│   ├── test_endpoints.py      # Test endpoints
│   ├── test_pagination.py     # Test pagination
│   ├── test_retry.py          # Test retry logic
│   └── test_rate_limit.py     # Test rate limiting
│
├── integration/               # Tests with dependencies
│   ├── test_api_client.py     # Test full API client
│   └── test_real_api.py       # Test against real Notion (optional)
│
├── fixtures/                  # Test data
│   ├── pages/
│   │   └── page_1.json        # Sample page data
│   ├── databases/
│   │   └── database_1.json    # Sample database data
│   └── responses/
│       └── error_response.json
│
└── conftest.py                # Shared pytest configuration
```

### File Naming

**Pattern:** `test_<module>.py`

**Examples:**
- `test_http_client.py` - Tests for `http.py`
- `test_auth.py` - Tests for `auth.py`
- `test_pages.py` - Tests for `pages.py` endpoint

---

## Test Types

### Unit Tests

**Purpose:** Test individual functions/classes in isolation.

**Characteristics:**
- Fast (<100ms each)
- No network calls
- No external dependencies
- Mock all external interactions

**Location:** `tests/unit/`

**Example:**
```python
import pytest
from unittest.mock import AsyncMock, patch

class TestHTTPClient:
    """Test HTTP client functionality."""

    @pytest.mark.asyncio
    async def test_request_success(self):
        """Test successful HTTP request."""
        # Arrange
        client = HTTPClient()
        mock_response = AsyncMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"id": "test"}

        # Act
        with patch.object(client, "_session") as mock_session:
            mock_session.request.return_value = mock_response
            result = await client.request("GET", "/pages/test")

        # Assert
        assert result == {"id": "test"}
```

### Integration Tests

**Purpose:** Test interactions between components.

**Characteristics:**
- Slower than unit tests
- May use network
- Test real interactions
- Optional: Use test environment

**Location:** `tests/integration/`

**Example:**
```python
import pytest
from better_notion._lowlevel import NotionAPI

@pytest.mark.integration
async def test_retrieve_page_real():
    """Test retrieving a real page."""
    # Arrange
    token = os.getenv("NOTION_TEST_TOKEN")
    if not token:
        pytest.skip("NOTION_TEST_TOKEN not set")

    api = NotionAPI(auth=token)
    page_id = os.getenv("NOTION_TEST_PAGE_ID")

    # Act
    page = await api.pages.retrieve(page_id)

    # Assert
    assert page["id"] == page_id
    assert page["object"] == "page"
```

### E2E Tests (Optional)

**Purpose:** Test complete workflows end-to-end.

**Characteristics:**
- Slow
- Use real Notion API
- Test full user flows
- Mark as `@pytest.mark.e2e`

**Location:** `tests/integration/` or `tests/e2e/`

---

## Writing Tests

### Test Structure

**AAA Pattern (Arrange-Act-Assert):**

```python
@pytest.mark.asyncio
async def test_retrieve_page_success():
    """Test retrieving a page successfully."""

    # ARRANGE - Set up the test
    page_id = "test_page_id"
    mock_response = {"id": page_id, "object": "page"}

    # ACT - Execute the code being tested
    result = await api.pages.retrieve(page_id)

    # ASSERT - Verify the result
    assert result["id"] == page_id
    assert result["object"] == "page"
```

### Test Names

**Descriptive, tell what they test:**

```python
# GOOD
async def test_retrieve_page_success():
    """Test retrieving a page successfully."""

async def test_retrieve_page_not_found():
    """Test 404 error when page not found."""

async def test_retrieve_page_invalid_id():
    """Test error handling for invalid page ID."""

# AVOID
async def test_page():
    """Test page."""  # Too vague

async def test1():
    """Test 1."""  # Meaningless
```

### Async Tests

**Mark async tests with `@pytest.mark.asyncio`:**

```python
@pytest.mark.asyncio
async def test_async_operation():
    """Test async function."""
    result = await async_function()
    assert result is not None
```

### Markers

**Use pytest markers for test categories:**

```python
@pytest.mark.unit
async def test_unit_test():
    """Unit test."""
    pass

@pytest.mark.integration
async def test_integration_test():
    """Integration test."""
    pass

@pytest.mark.slow
async def test_slow_operation():
    """Slow test."""
    pass
```

**Run specific markers:**
```bash
# Run only unit tests
uv run pytest -m unit

# Skip slow tests
uv run pytest -m "not slow"

# Run integration tests
uv run pytest -m integration
```

---

## Fixtures

### Creating Fixtures

**In `conftest.py`:**

```python
import pytest
from better_notion._lowlevel import NotionAPI
from unittest.mock import AsyncMock, patch

@pytest.fixture
async def mock_api():
    """Create a mock API client for testing."""
    api = NotionAPI(auth="test_token")

    # Mock HTTP client
    with patch.object(api, "_http"):
        yield api
```

### Using Fixtures

```python
async def test_with_fixture(mock_api):
    """Test using fixture."""
    result = await mock_api.pages.retrieve("test_id")
    assert result is not None
```

### Sample Data Fixtures

```python
@pytest.fixture
def sample_page_data():
    """Sample page data for testing."""
    return {
        "id": "test_page_id",
        "object": "page",
        "created_time": "2025-01-01T00:00:00.000Z",
        "last_edited_time": "2025-01-01T00:00:00.000Z",
        "properties": {
            "title": {
                "type": "title",
                "title": [
                    {"type": "text", "text": {"content": "Test Page"}}
                ]
            }
        }
    }
```

---

## Mocking

### Mocking HTTP Calls

```python
from unittest.mock import AsyncMock, patch

async def test_with_mocked_http(mock_api):
    """Test with mocked HTTP client."""
    mock_response = {"id": "test", "object": "page"}

    with patch.object(
        mock_api._http,
        "request",
        return_value=mock_response
    ):
        result = await mock_api.pages.retrieve("test_id")

    assert result["id"] == "test"
```

### Mocking Async Methods

```python
async def test_async_mock():
    """Test with async mock."""
    mock_func = AsyncMock(return_value={"id": "test"})

    result = await mock_func()
    assert result == {"id": "test"}
```

### Mocking Context Managers

```python
async def test_context_manager_mock():
    """Test with mocked context manager."""
    mock_client = AsyncMock()

    async with mock_client:
        mock_client.request.return_value = {"id": "test"}
```

---

## Testing Errors

### Testing Exceptions

```python
import pytest
from better_notion._lowlevel.errors import NotFoundError

async def test_page_not_found():
    """Test 404 error handling."""
    # Arrange
    mock_api._http.request.side_effect = HTTPError(
        "Not found",
        status_code=404
    )

    # Act & Assert
    with pytest.raises(NotFoundError):
        await mock_api.pages.retrieve("nonexistent")
```

### Testing Error Messages

```python
async def test_error_message():
    """Test error message content."""
    with pytest.raises(ValueError) as exc_info:
        raise ValueError("Invalid page ID")

    assert str(exc_info.value) == "Invalid page ID"
```

---

## Testing Edge Cases

### Empty Responses

```python
async def test_empty_response():
    """Test handling of empty response."""
    mock_api._http.request.return_value = {}

    result = await mock_api.pages.retrieve("test_id")

    assert result == {}
```

### Null Values

```python
async def test_null_values():
    """Test handling of null values."""
    mock_api._http.request.return_value = {
        "id": None,
        "properties": None
    }

    result = await mock_api.pages.retrieve("test_id")

    assert result["id"] is None
```

### Large Responses

```python
async def test_large_response():
    """Test handling of large responses."""
    large_list = [{"id": f"item_{i}"} for i in range(1000)]
    mock_api._http.request.return_value = {
        "results": large_list,
        "has_more": False
    }

    result = await mock_api.databases.query("db_id")

    assert len(result["results"]) == 1000
```

---

## Coverage

### Measure Coverage

```bash
# Terminal output
uv run pytest --cov=better_notion --cov-report=term-missing

# HTML report
uv run pytest --cov=better_notion --cov-report=html

# Combined
uv run pytest --cov=better_notion --cov-report=html --cov-report=term-missing
```

### Coverage Targets

| Metric | Target |
|--------|--------|
| **Line coverage** | ≥80% |
| **Branch coverage** | ≥70% |
| **File coverage** | ≥75% |

### View HTML Report

```bash
# Generate report
uv run pytest --cov=better_notion --cov-report=html

# Open in browser
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
start htmlcov/index.html  # Windows
```

---

## Running Tests

### Run All Tests

```bash
uv run pytest
```

### Run Specific Test File

```bash
uv run pytest tests/unit/test_http_client.py
```

### Run Specific Test

```bash
# By name
uv run pytest tests/unit/test_http_client.py::TestHTTPClient::test_request_success

# By keyword expression
uv run pytest -k "test_retrieve_page"
```

### Run with Verbosity

```bash
# Verbose
uv run pytest -v

# Very verbose
uv run pytest -vv

# Show output
uv run pytest -s
```

### Run with Markers

```bash
# Unit tests only
uv run pytest -m unit

# Integration tests only
uv run pytest -m integration

# Exclude slow tests
uv run pytest -m "not slow"
```

### Run Failed Tests Only

```bash
# Run last failed tests
uv run pytest --lf

# Run failed tests first
uv run pytest --ff
```

---

## Test Configuration

### `pytest.ini`

```ini
[pytest]
# Test discovery
python_files = test_*.py
python_classes = Test*
python_functions = test_*

# Output
addopts =
    -v                              # Verbose output
    --strict-markers                # Treat unknown markers as error
    --tb=short                      # Short traceback format
    --cov=better_notion            # Coverage reporting
    --cov-report=html              # HTML coverage report
    --cov-report=term-missing      # Show missing lines

# Async configuration
asyncio_mode = auto                # Auto-detect async tests

# Markers
markers =
    unit: Unit tests (no external dependencies)
    integration: Integration tests (may use I/O)
    slow: Slow tests (>1 second)
    e2e: End-to-end tests
```

---

## Test Checklist

### Before Submitting

- [ ] Unit tests added for new code
- [ ] Integration tests if applicable
- [ ] Edge cases covered
- [ ] Error cases tested
- [ ] All tests pass locally
- [ ] Coverage ≥80%
- [ ] No tests skipped (without reason)

### Test Quality

- [ ] Tests are independent
- [ ] Tests are fast (<100ms each for unit tests)
- [ ] Tests are descriptive (clear names)
- [ ] Tests follow AAA pattern
- [ ] Fixtures used appropriately
- [ ] Mocks used correctly

---

## Common Patterns

### Test API Endpoint

```python
class TestPagesEndpoint:
    """Test suite for Pages endpoint."""

    @pytest.mark.asyncio
    async def test_retrieve_success(self, mock_api):
        """Test successful page retrieval."""
        # Arrange
        page_id = "test_id"
        mock_api._http.request.return_value = {
            "id": page_id,
            "object": "page"
        }

        # Act
        result = await mock_api.pages.retrieve(page_id)

        # Assert
        assert result["id"] == page_id
```

### Test Error Handling

```python
@pytest.mark.asyncio
async def test_retrieve_not_found(self, mock_api):
    """Test 404 error handling."""
    # Arrange
    mock_api._http.request.side_effect = HTTPError(
        "Not found",
        status_code=404
    )

    # Act & Assert
    with pytest.raises(NotFoundError):
        await mock_api.pages.retrieve("nonexistent")
```

### Test Pagination

```python
@pytest.mark.asyncio
async def test_fetch_all_pages(self, mock_api):
    """Test fetching all pages with pagination."""
    # Arrange
    page1 = {"results": [{"id": "1"}], "has_more": True, "next_cursor": "cursor1"}
    page2 = {"results": [{"id": "2"}], "has_more": False, "next_cursor": None}
    mock_api._http.request.side_effect = [page1, page2]

    # Act
    response = PaginatedResponse(...)
    all_items = await response.fetch_all()

    # Assert
    assert len(all_items) == 2
    assert all_items[0]["id"] == "1"
    assert all_items[1]["id"] == "2"
```

---

## Testing Best Practices

### Do's

- ✅ Test public API, not implementation details
- ✅ One assertion per test (when possible)
- ✅ Descriptive test names
- ✅ Arrange-Act-Assert pattern
- ✅ Use fixtures for setup
- ✅ Mock external dependencies
- ✅ Test edge cases
- ✅ Test error conditions

### Don'ts

- ❌ Test private methods (test public interface instead)
- ❌ Multiple assertions testing different things
- ❌ Vague test names
- ❌ Hardcoded test data in tests
- ❌ Integration tests for everything
- ❌ Slow unit tests
- ❌ Skipping tests without markers
- ❌ Catching exceptions too broadly

---

## Troubleshooting

### Tests Pass Locally, Fail in CI

**Possible causes:**
- Different Python version
- Missing dependencies
- Environment variables not set
- Race conditions in async tests

**Solutions:**
```bash
# Check Python version
python --version

# Update dependencies
uv sync

# Run with verbose output
uv run pytest -vv

# Run specific test
uv run pytest tests/unit/test_failing.py::test_name -vv
```

### Tests Are Slow

**Solutions:**
- Use more mocking
- Move slow tests to integration/
- Mark slow tests with `@pytest.mark.slow`
- Run in parallel: `pytest -n auto`

### Flakey Tests

**Tests that sometimes fail:**

**Solutions:**
- Add delays for async operations
- Use proper async/await
- Mock time-dependent operations
- Fix race conditions

---

## Related Documentation

- [setup.md](./setup.md) - Environment setup
- [standards.md](./standards.md) - Code conventions
- [debugging.md](./debugging.md) - Debugging tests

---

## Summary

**Testing Strategy:**

1. **70% unit tests** - Fast, isolated, mocked
2. **20% integration tests** - Real interactions
3. **10% E2E tests** - Complete workflows

**Key Principles:**

- Write tests as you write code
- Follow AAA pattern (Arrange-Act-Assert)
- Use descriptive test names
- Mock external dependencies
- Target ≥80% coverage
- Keep tests fast and independent

**Essential Commands:**

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=better_notion

# Run specific test
uv run pytest tests/unit/test_http_client.py

# Run by marker
uv run pytest -m unit

# Run failed tests
uv run pytest --lf
```

---

**Last Updated:** 2025-01-23
