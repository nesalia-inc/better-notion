# Testing Strategy

Comprehensive testing strategy for the low-level API including unit tests, integration tests, and test utilities.

## Testing Philosophy

### Principles

1. **No Real API Calls in Unit Tests** - Use mocks for fast, reliable tests
2. **Test Public Contract** - Test against actual API behavior
3. **Isolation** - Each test should be independent
4. **Reproducibility** - Same results every time
5. **Speed** - Unit tests should run in milliseconds
6. **Clarity** - Test names and assertions should be self-documenting

## Test Structure

```
tests/
├── unit/
│   ├── test_http_client.py
│   ├── test_auth.py
│   ├── test_endpoints.py
│   ├── test_pagination.py
│   ├── test_retry.py
│   └── test_errors.py
├── integration/
│   ├── test_api_client.py
│   └── test_rate_limiting.py
├── fixtures/
│   ├── pages/
│   │   ├── page_1.json
│   │   └── page_2.json
│   ├── databases/
│   └── responses/
└── conftest.py
```

## Test Configuration

### pytest.ini

```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
asyncio_mode = auto
addopts =
    -v
    --strict-markers
    --tb=short
    --cov=better_notion
    --cov-report=html
    --cov-report=term-missing
```

### pyproject.toml

```toml
[project.optional-dependencies]
dev = [
    "pytest>=7.0",
    "pytest-asyncio>=0.21.0",
    "pytest-cov>=4.0",
    "pytest-mock>=3.10",
    "httpx-mock>=0.1.0",
]
```

## Fixtures

### conftest.py

```python
import pytest
import httpx
from unittest.mock import AsyncMock, patch

from better_notion.api import NotionAPI
from better_notion.api.auth import BearerAuth

@pytest.fixture
async def mock_api():
    """
    Create a mock NotionAPI for testing.

    The HTTP client is mocked, so no real API calls are made.
    """
    api = NotionAPI(auth="test_secret_...")

    # Mock the HTTP client
    with patch.object(api, '_http') as mock_http:
        mock_request = AsyncMock()
        mock_http.request = mock_request

        yield api

@pytest.fixture
def sample_page_response():
    """Sample page response fixture."""
    return {
        "object": "page",
        "id": "5c6a28216bb14a7eb6e1c50111515c3d",
        "created_time": "2022-03-01T19:05:00.000Z",
        "last_edited_time": "2022-03-01T19:05:00.000Z",
        "archived": False,
        "properties": {
            "Name": {
                "id": "title",
                "type": "title",
                "title": [
                    {
                        "type": "text",
                        "text": {
                            "content": "Test Page"
                        }
                    }
                ]
            }
        }
    }

@pytest.fixture
def sample_database_response():
    """Sample database response fixture."""
    return {
        "object": "database",
        "id": "d9824bdc84454327be8b5b47500af6ce",
        "title": [
            {
                "type": "text",
                "text": {
                    "content": "Tasks"
                }
            }
        ],
        "properties": {...}
    }

@pytest.fixture
def sample_paginated_response():
    """Sample paginated response fixture."""
    return {
        "object": "list",
        "results": [
            {"id": "page-1", "title": "Page 1"},
            {"id": "page-2", "title": "Page 2"}
        ],
        "next_cursor": "cursor_abc123",
        "has_more": True
    }
```

## Unit Tests

### HTTP Client Tests

```python
import pytest
from unittest.mock import AsyncMock, patch
from better_notion.api.http_client import HTTPClient

class TestHTTPClient:
    """Test HTTP client functionality."""

    @pytest.mark.asyncio
    async def test_request_success(self):
        """Test successful HTTP request."""
        client = HTTPClient(base_url="https://api.notion.com/v1")

        # Mock httpx client
        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value = mock_client

            # Mock response
            mock_response = AsyncMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"id": "test"}
            mock_client.request.return_value = mock_response

            result = await client.request("GET", "/pages/test")

            assert result == {"id": "test"}
            mock_client.request.assert_called_once_with(
                "GET",
                "https://api.notion.com/v1/pages/test"
            )

    @pytest.mark.asyncio
    async def test_request_http_error(self):
        """Test HTTP error is raised."""
        client = HTTPClient()

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value = mock_client

            # Mock 404 response
            mock_response = AsyncMock()
            mock_response.status_code = 404
            mock_response.raise_for_status.side_effect = (
                httpx.HTTPStatusError("Not found", request=mock_request)
            )
            mock_client.request.return_value = mock_response

            with pytest.raises(HTTPError) as exc_info:
                await client.request("GET", "/pages/test")

            assert exc_info.value.status_code == 404
```

### Authentication Tests

```python
class TestBearerAuth:
    """Test Bearer token authentication."""

    def test_valid_token(self):
        """Test valid token format."""
        auth = BearerAuth("secret_abc123...")

        headers = auth.headers

        assert "Authorization" in headers
        assert headers["Authorization"] == "Bearer secret_abc123..."

    def test_invalid_token_format(self):
        """Test invalid token raises error."""
        with pytest.raises(ValueError, match="must start with 'secret_'"):
            BearerAuth("invalid_token")

    def test_token_repr(self):
        """Test token string representation hides full token."""
        auth = BearerAuth("secret_abc123def456...")

        repr_str = repr(auth)

        # Should show preview, not full token
        assert "secret_abc" in repr_str
        assert "secret_abc123def456..." not in repr_str
```

### Endpoint Tests

```python
class TestPagesEndpoint:
    """Test Pages API endpoint."""

    @pytest.mark.asyncio
    async def test_retrieve_page(mock_api, sample_page_response):
        """Test retrieving a page."""
        # Mock successful response
        mock_api._request.return_value = sample_page_response

        page = await mock_api.pages.retrieve(page_id="test_id")

        assert page["id"] == "5c6a28216bb14a7eb6e1c50111515c3d"
        assert page["object"] == "page"

        # Verify request was made correctly
        mock_api._request.assert_called_once_with(
            "GET",
            "/pages/test_id"
        )

    @pytest.mark.asyncio
    async def test_retrieve_page_not_found(mock_api):
        """Test 404 error when page not found."""
        # Mock 404 response
        mock_api._request.side_effect = PageNotFoundError(
            "Page not found",
            status_code=404
        )

        with pytest.raises(PageNotFoundError):
            await mock_api.pages.retrieve(page_id="nonexistent")

    @pytest.mark.asyncio
    async def test_create_page(mock_api):
        """Test creating a page."""
        # Mock response
        mock_api._request.return_value = {
            "id": "new_page_id",
            "object": "page",
            "properties": {...}
        }

        page = await mock_api.pages.create(
            parent={"type": "database_id", "database_id": "db_id"},
            properties={"Name": {"title": [{"text": {"content": "New"}}]}}
        )

        assert page["id"] == "new_page_id"

        # Verify request
        mock_api._request.assert_called_once()
        call_args = mock_api._request.call_args

        assert call_args[0] == "POST"
        assert call_args[1] == "/pages"

        # Verify body
        body = call_args.kwargs["json"]
        assert "parent" in body
        assert "properties" in body
```

### Pagination Tests

```python
class TestPagination:
    """Test pagination functionality."""

    @pytest.mark.asyncio
    async def test_paginated_response_iteration(mock_api):
        """Test iterating over current page."""
        from better_notion.api.pagination import PaginatedResponse

        # Create paginated response
        response = PaginatedResponse(
            results=[{"id": "1"}, {"id": "2"}, {"id": "3"}],
            next_cursor="cursor_abc",
            has_more=True,
            api=mock_api,
            request_fn=mock_api.databases.query,
            request_fn_kwargs={"database_id": "db_id"}
        )

        # Test iteration
        items = list(response)
        assert len(items) == 3
        assert items[0]["id"] == "1"

    @pytest.mark.asyncio
    async def test_fetch_all_pages(mock_api):
        """Test fetching all pages."""
        # Mock multiple pages
        page1 = {
            "results": [{"id": "1"}],
            "has_more": True,
            "next_cursor": "cursor_2"
        }
        page2 = {
            "results": [{"id": "2"}],
            "has_more": True,
            "next_cursor": "cursor_3"
        }
        page3 = {
            "results": [{"id": "3"}],
            "has_more": False,
            "next_cursor": None
        }

        mock_api._request.side_effect = [page1, page2, page3]

        # Fetch all
        response = PaginatedResponse(
            results=page1["results"],
            next_cursor=page1["next_cursor"],
            has_more=page1["has_more"],
            api=mock_api,
            request_fn=lambda **kw: mock_api._request("POST", "/databases/db_id/query", **kw),
            request_fn_kwargs={}
        )

        all_items = await response.fetch_all()

        assert len(all_items) == 3
        assert all_items[0]["id"] == "1"
        assert all_items[1]["id"] == "2"
        assert all_items[2]["id"] == "3"

    @pytest.mark.asyncio
    async def test_async_iterator(mock_api):
        """Test async iterator over all items."""
        from better_notion.api.pagination import PaginatedAsyncIterator

        # Mock multiple pages
        page1 = {
            "results": [{"id": "1"}, {"id": "2"}],
            "has_more": True,
            "next_cursor": "cursor_2"
        }
        page2 = {
            "results": [{"id": "3"}],
            "has_more": False,
            "next_cursor": None
        }

        mock_api._request.side_effect = [page1, page2]

        # Create iterator
        response = PaginatedResponse(
            results=page1["results"],
            next_cursor=page1["next_cursor"],
            has_more=page1["has_more"],
            api=mock_api,
            request_fn=lambda **kw: mock_api._request("POST", "/databases/db_id/query", **kw),
            request_fn_kwargs={}
        )

        iterator = PaginatedAsyncIterator(response)

        # Collect all items
        items = []
        async for item in iterator:
            items.append(item)

        assert len(items) == 3
        assert items[0]["id"] == "1"
        assert items[1]["id"] == "2"
        assert items[2]["id"] == "3"
```

### Error Handling Tests

```python
class TestErrorHandling:
    """Test error handling."""

    @pytest.mark.asyncio
    async def test_404_raises_page_not_found(mock_api):
        """Test 404 raises PageNotFoundError."""
        # Mock 404 response
        mock_api._request.side_effect = HTTPError(
            "Not found",
            status_code=404
        )

        with pytest.raises(PageNotFoundError):
            await mock_api.pages.retrieve("nonexistent_id")

    @pytest.mark.asyncio
    async def test_429_rate_limit_retry(mock_api):
        """Test 429 triggers retry logic."""
        # First call: 429, second call: success
        responses = [
            HTTPError("Rate limited", status_code=429, retry_after=1),
            {"id": "page_id", "object": "page"}
        ]

        mock_api._request.side_effect = responses

        # Should retry and succeed
        result = await mock_api.pages.retrieve("page_id")

        assert result["id"] == "page_id"
        assert mock_api._request.call_count == 2

    @pytest.mark.asyncio
    async def test_retry_exhaustion(mock_api):
        """Test retries are exhausted after max attempts."""
        # Always return 429
        mock_api._request.side_effect = HTTPError(
            "Rate limited",
            status_code=429,
            retry_after=1
        )

        with pytest.raises(HTTPError):
            await mock_api.pages.retrieve("page_id")

        # Should have tried max_attempts times
        assert mock_api._request.call_count == 3
```

## Integration Tests

### With Mock Server

```python
import httpx
from httpx import Response

class TestWithMockServer:
    """Integration tests with mock HTTP server."""

    @pytest.mark.asyncio
    async def test_full_request_cycle(self):
        """Test complete request cycle with mock server."""
        # Create mock transport
        def mock_request(request: httpx.Request) -> Response:
            # Validate request
            assert request.method == "GET"
            assert "/pages/test_id" in request.url.path

            # Return mock response
            return Response(
                200,
                json={"id": "test_id", "object": "page"},
                headers={"Content-Type": "application/json"}
            )

        # Create client with mock transport
        transport = httpx.MockTransport(mock_request)
        api = NotionAPI(
            auth="test_token",
            transport=transport
        )

        # Make request
        page = await api.pages.retrieve("test_id")

        assert page["id"] == "test_id"
```

### Fixture-Based Tests

```python
class TestWithFixtures:
    """Tests using JSON fixtures."""

    @pytest.mark.asyncio
    async def test_load_page_fixture(self, mock_api, sample_page_response):
        """Test using JSON fixture."""
        # Load from fixture file
        with open("tests/fixtures/pages/page_1.json") as f:
            fixture_data = json.load(f)

        mock_api._request.return_value = fixture_data

        page = await mock_api.pages.retrieve("page_id")

        assert page["id"] == fixture_data["id"]
        assert page["object"] == "page"
```

## Mock Utilities

### Response Builder

```python
class MockResponseBuilder:
    """Helper to build mock HTTP responses."""

    @staticmethod
    def success(
        status_code: int = 200,
        json_data: dict | None = None
    ) -> dict:
        """Build successful response."""
        response = {
            "status_code": status_code,
            "headers": {
                "Content-Type": "application/json",
                "x-ratelimit-limit": "3",
                "x-ratelimit-remaining": "2",
                "x-ratelimit-reset": "1234567890"
            }
        }

        if json_data:
            response["json"] = json_data

        return response

    @staticmethod
    def error(
        status_code: int,
        message: str
    ) -> dict:
        """Build error response."""
        return {
            "status_code": status_code,
            "json": {
                "message": message,
                "status": status_code
            },
            "headers": {
                "Content-Type": "application/json"
            }
        }

    @staticmethod
    def paginated(
        items: list[dict],
        has_more: bool = False,
        next_cursor: str | None = None
    ) -> dict:
        """Build paginated response."""
        return {
            "json": {
                "object": "list",
                "results": items,
                "next_cursor": next_cursor,
                "has_more": has_more
            },
            "headers": {
                "Content-Type": "application/json"
            }
        }
```

### API Mocker

```python
class NotionAPIMocker:
    """
    Mock NotionAPI with canned responses.

    Usage:
        mocker = NotionAPIMocker()

        # Define responses
        mocker.get_page(page_id, {"id": page_id, ...})

        # Use mock
        with mocker.mock():
            api = NotionAPI(auth="test")
            page = await api.pages.retrieve(page_id)
    """

    def __init__(self):
        self._responses = {}

    def get_page(self, page_id: str, response: dict) -> None:
        """Define mock response for page retrieval."""
        self._responses[("GET", f"/pages/{page_id}")] = response

    def create_page(self, response: dict) -> None:
        """Define mock response for page creation."""
        self._responses[("POST", "/pages")] = response

    def mock(self):
        """Return mock context manager."""
        return patch.object(NotionAPI, "_request", side_effect=self._handle_request)

    async def _handle_request(self, method: str, path: str, **kwargs):
        """Handle mock request."""
        key = (method, path)

        if key in self._responses:
            return self._responses[key]

        # Default 404
        raise HTTPError("Not found", status_code=404)
```

## Test Data Builders

### Page Builder

```python
class PageBuilder:
    """Build test page objects."""

    @staticmethod
    def with_title(title: str) -> dict:
        """Create minimal page with title."""
        return {
            "object": "page",
            "id": str(uuid.uuid4()),
            "created_time": "2022-03-01T19:05:00.000Z",
            "last_edited_time": "2022-03-01T19:05:00.000Z",
            "archived": False,
            "properties": {
                "title": {
                    "id": "title",
                    "type": "title",
                    "title": [
                        {
                            "type": "text",
                            "text": {"content": title}
                        }
                    ]
                }
            }
        }

    @staticmethod
    def with_properties(properties: dict) -> dict:
        """Create page with custom properties."""
        return {
            "object": "page",
            "id": str(uuid.uuid4()),
            "created_time": "2022-03-01T19:05:00.000Z",
            "last_edited_time": "2022-03-01T19:05:00.000Z",
            "archived": False,
            "properties": properties
        }
```

### Database Builder

```python
class DatabaseBuilder:
    """Build test database objects."""

    @staticmethod
    def simple(title: str) -> dict:
        """Create minimal database."""
        return {
            "object": "database",
            "id": str(uuid.uuid4()),
            "title": [
                {
                    "type": "text",
                    "text": {"content": title}
                }
            ],
            "properties": {}
        }

    @staticmethod
    def with_properties(properties: dict[str, dict]) -> dict:
        """Create database with property schema."""
        return {
            "object": "database",
            "id": str(uuid.uuid4()),
            "title": [{"type": "text", "text": {"content": "Test"}}],
            "properties": properties
        }
```

## Test Markers

### Custom Markers

```python
# In conftest.py
@pytest.mark.unit
def test_something_fast():
    """Unit test - no external dependencies."""
    pass

@pytest.mark.integration
def test_something_slow():
    """Integration test - may involve I/O."""
    pass

@pytest.mark.slow
def test_something_very_slow():
    """Very slow test - may take >1 second."""
    pass
```

### Usage

```python
# Run only unit tests
pytest -m unit

# Skip slow tests
pytest -m "not slow"

# Run only integration tests
pytest -m integration
```

## CI/CD Integration

### GitHub Actions Example

```yaml
# .github/workflows/tests.yml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: "3.10"

      - name: Install dependencies
        run: |
          pip install -e ".[dev]"

      - name: Run tests
        run: |
          pytest --cov=better_notion --cov-report=xml

      - name: Upload coverage
        uses: codecov/codecov-action@v3
```

## Best Practices

### 1. Use Descriptive Test Names

```python
# GOOD: Clear and descriptive
def test_retrieve_page_returns_page_object():
    """Test that retrieving a page returns a page object."""
    pass

# BAD: Vague
def test_page():
    pass
```

### 2. One Assertion Per Test

```python
# GOOD: Single assertion
def test_page_id_format():
    """Test page ID is returned correctly."""
    page = await api.pages.retrieve("page_id")
    assert page["id"] == "page_id"

# AVOID: Multiple assertions
def test_page_all_at_once():
    """Test all page properties at once."""
    page = await api.pages.retrieve("page_id")
    assert page["id"] == "page_id"
    assert page["object"] == "page"
    assert page["archived"] == False
    # If first assertion fails, we don't know about others
```

### 3. Arrange-Act-Assert Pattern

```python
def test_page_retrieval():
    """Test page retrieval following AAA pattern."""
    # Arrange
    page_id = "test_id"
    mock_api._request.return_value = sample_response

    # Act
    page = await mock_api.pages.retrieve(page_id)

    # Assert
    assert page["id"] == page_id
```

### 4. Use Fixtures for Common Data

```python
# GOOD: Reusable fixtures
@pytest.fixture
def sample_page():
    return PageBuilder.with_title("Test Page")

# BAD: Duplicated data
def test_1():
    page = {"id": "...", ...}

def test_2():
    page = {"id": "...", ...}
```

### 5. Mock at the Right Level

```python
# GOOD: Mock HTTP client (lowest level)
with patch.object(api, '_http'):
    # Tests all layers above HTTP client
    pass

# AVOID: Mock the method under test
with patch.object(api.pages, 'retrieve'):
    # Doesn't actually test the method
    pass
```

## Test Documentation

### Docstrings in Tests

```python
class TestPagesEndpoint:
    """Test suite for Pages API endpoint."""

    @pytest.mark.asyncio
    async def test_retrieve_page_happy_path(mock_api):
        """
        Test retrieving a page successfully.

        Scenario:
            - Page exists
            - Integration has access
            - Valid page ID

        Expected:
            - Returns page object
            - Response contains required fields
        """
        # Test implementation
        pass
```

## Performance

### Fast Tests

```python
# Test should run in milliseconds
@pytest.mark.asyncio
async def test_fast_operation(mock_api):
    """This test should complete in <10ms."""
    # Fast mock operation
    mock_api._request.return_value = {"id": "test"}

    result = await mock_api.pages.retrieve("test_id")

    assert result["id"] == "test"
```

### Parallel Test Execution

```python
# Tests that can run in parallel
@pytest.mark.asyncio
async def test_parallel_1(mock_api):
    pass

@pytest.mark.asyncio
async def test_parallel_2(mock_api):
    pass
```

## Related Documentation

- [Overview](./overview.md) - Low-level API overview
- [Endpoints](./endpoints.md) - Endpoint reference
- [HTTP Client](./http-client.md) - HTTP layer testing
- [Error Handling](./error-handling.md) - Testing error scenarios

## Next Steps

1. Set up pytest configuration
2. Create test fixtures for common responses
3. Write unit tests for each endpoint
4. Add integration tests for critical paths
5. Set up CI/CD for automated testing
