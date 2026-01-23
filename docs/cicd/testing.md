# Testing in CI/CD

Comprehensive guide to testing in the CI/CD pipeline for the Better Notion SDK.

## Overview

Testing is a critical part of our CI/CD pipeline. We use **pytest** with async support, **pytest-asyncio** for async test execution, and **codecov** for coverage reporting.

## Test Configuration

### pytest Configuration

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
    --tb=short                       # Short traceback format
    --cov=better_notion              # Coverage reporting
    --cov-report=html                # HTML coverage report
    --cov-report=term-missing          # Show missing lines

# Async configuration
asyncio_mode = auto                   # Auto-detect async tests

# Markers
markers =
    unit: Unit tests (no external dependencies)
    integration: Integration tests (may use I/O)
    slow: Slow tests (>1 second)
```

### pyproject.toml Configuration

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

---

## Test Organization

### Directory Structure

```
tests/
├── unit/                          # Fast, isolated tests
│   ├── test_http_client.py
│   ├── test_auth.py
│   ├── test_endpoints.py
│   ├── test_pagination.py
│   └── test_retry.py
├── integration/                   # Tests with external dependencies
│   ├── test_api_client.py
│   └── test_rate_limiting.py
├── fixtures/                      # Test data and fixtures
│   ├── pages/
│   │   └── page_1.json
│   ├── databases/
│   │   └── database_1.json
│   └── responses/
│       └── test_response.json
└── conftest.py                     # Shared pytest configuration
```

---

## Unit Tests in CI

### What Runs in CI

**Files:** All files in `tests/unit/`

**Characteristics:**
- No network calls
- No external dependencies
- Use mocks extensively
- Very fast (<1 second each)
- Test isolated components

### Example Unit Test

```python
import pytest
from unittest.mock import AsyncMock, patch

class TestHTTPClient:
    """Test HTTP client functionality."""

    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_request_success(mock_api):
        """Test successful HTTP request."""
        # Mock HTTP client
        with patch.object(mock_api, '_http') as mock_http:
            mock_request = AsyncMock()
            mock_response = AsyncMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"id": "test"}
            mock_http.request.return_value = mock_response

            result = await mock_api.pages.retrieve("page_id")

            assert result["id"] == "test"
```

### Excluded from CI

- Integration tests (require external services)
- Slow tests (>1 second)
- Manual tests

---

## Integration Tests in CI

### What Runs in CI

**Files:** Selected files in `tests/integration/`

**Characteristics:**
- May use network calls
- Test interactions between components
- Test end-to-end flows
- Longer duration
- May require test environment

### When Integration Tests Run

**Strategy:** Run integration tests separately

**Options:**
1. **Run in CI**: Run on every push but marked as `integration` marker
2. **Run manually**: Only run locally or on demand
3. **Separate workflow**: Different workflow for integration tests

**Decision:** Integration tests run on main branch only (or manually triggered)

### Example Integration Test

```python
import pytest
from better_notion import NotionAPI

@pytest.mark.asyncio
@pytest.mark.integration
async def test_retrieve_page_real():
    """
    Test retrieving a real page.

    Requires NOTION_TOKEN environment variable.
    """
    token = os.getenv("NOTION_TOKEN")
    if not token:
        pytest.skip("NOTION_TOKEN not set")

    api = NotionAPI(auth=token)

    page = await api.pages.retrieve(page_id="real_page_id")

    assert page["id"] == "real_page_id"
```

---

## Coverage in CI

### Coverage Configuration

```yaml
# In .github/workflows/ci.yml
- name: Run pytest with coverage
  run: |
    uv run pytest \
        --cov=better_notion \
        --cov-report=xml \
        --cov-report=html \
        --cov-report=term-missing \
        --cov-fail-under=80 \
        -v

- name: Upload coverage to Codecov
  uses: codecov/codecov-action@v3
  with:
    token: ${{ secrets.CODECOV_TOKEN }}
    files: ./coverage.xml
    flags: unittests
    name: codecov-umbrella
```

### Coverage Threshold

**Minimum: 80%**

**Rationale:**
- High but achievable
- Ensures good test coverage
- Not so high as to be burdensome

**Enforcement:**
```yaml
# Fails build if coverage below 80%
--cov-fail-under=80
```

### Coverage Report Locations

**In CI:**
- Terminal: Shown in workflow logs
- HTML: Generated as artifact
- Codecov: Uploaded to Codecov

**Artifacts:**
- `coverage/` directory (HTML report)

**Viewing:**
- Download artifact from GitHub Actions run
- Open `coverage/index.html` in browser

---

## Test Speed

### Target Times

| Test Type | Target Time |
|-----------|-------------|
| Unit test | <100ms each |
| Integration test | <5 seconds |
| Full test suite | <2 minutes (per Python version) |

### Optimization Techniques

#### 1. Mock External Dependencies

```python
# GOOD: Mock HTTP client
@pytest.mark.asyncio
async def test_create_page():
    with patch.object(api, '_http') as mock:
        mock.request.return_value = sample_response
        page = await api.pages.create(...)
        assert page["id"] == "expected"

# AVOID: Real HTTP call
@pytest.mark.asyncio
async def test_create_page():
    page = await api.pages.create(...)  # Slow
    assert page["id"] == "expected"
```

#### 2. Use Fixtures for Test Data

```python
@pytest.fixture
def sample_page_data():
    return {
        "id": "test_page_id",
        "object": "page",
        ...
    }

# Use fixture in tests
def test_page_properties(sample_page_data):
    assert sample_page_data["id"] == "test_page_id"
```

#### 3. Run Unit Tests in CI

```yaml
# In .github/workflows/ci.yml
jobs:
  test:
    # Only run unit tests in CI
    steps:
      - name: Run unit tests
        run: uv run pytest tests/unit/
```

---

## Test Execution Order

### Order of Execution

1. **Lint Job** (if present)
   - Runs ruff check
   - Runs ruff format check
   - Fast feedback

2. **Test Job** (runs in parallel if lint passes)
   - Python 3.10 tests
   - Python 3.11 tests
   - Python 3.12 tests
   - Coverage upload

### Parallel Execution

```yaml
lint:
  # Runs independently
  test:
    # Runs in parallel with lint
```

**Benefits:**
- Faster overall pipeline
- Lint provides instant feedback
- Tests run while lint is checking

---

## Test Data in CI

### Using Fixtures

**Don't commit test credentials:**

```python
# AVOID: Hardcoded credentials
def test_with_hardcoded_token():
    api = NotionAPI(auth="secret_...")  # DON'T DO THIS
    ...

# GOOD: Use environment variables
def test_with_env_token():
    token = os.getenv("NOTION_TEST_TOKEN")
    if not token:
        pytest.skip("No test token available")
    api = NotionAPI(auth=token)
    ...
```

### Mock Responses

```python
# Fixtures for API responses
@pytest.fixture
def mock_page_response():
    return {
        "object": "page",
        "id": "5c6a28216bb14a7eb6e1c50111515c3d",
        ...
    }
```

---

## Async Tests

### pytest-asyncio Configuration

```python
# In conftest.py
import pytest
import asyncio

@pytest.fixture(scope="session")
def event_loop_policy():
    """Event loop policy for tests."""
    policy = asyncio.DefaultEventLoopPolicy()
    asyncio.set_event_loop_policy(policy)
    return policy
```

### Async Test Patterns

```python
@pytest.mark.asyncio
async def test_async_operation():
    """Test async operation."""
    # Arrange
    async_func = async_function

    # Act
    result = await async_func()

    # Assert
    assert result is not None
```

---

## Coverage Goals

### Coverage Metrics

| Metric | Target | Rationale |
|--------|--------|------------|
| **Line coverage** | ≥80% | Core functionality tested |
| **Branch coverage** | ≥70% | Conditional logic tested |
| | **File coverage** | ≥75% | Most files have tests |

### Coverage Reports

**Generated in CI:**
- HTML report: `coverage/index.html`
- XML report: `coverage.xml`
- Terminal: Missing lines shown in logs

**Viewing:**
- Download artifacts from GitHub Actions
- Open HTML report locally
- Check Codecov dashboard

---

## Common Test Scenarios

### 1. Unit Test Example

```python
class TestPagesEndpoint:
    """Test suite for Pages endpoint."""

    @pytest.mark.asyncio
    async def test_retrieve_page_happy_path(self, mock_api):
        """Test retrieving a page successfully."""
        # Setup
        mock_api._request.return_value = sample_page_response

        # Act
        page = await mock_api.pages.retrieve("page_id")

        # Assert
        assert page["id"] == "page_id"
```

### 2. Error Handling Test

```python
async def test_retrieve_page_not_found(mock_api):
    """Test 404 error handling."""
    # Setup
    mock_api._request.side_effect = HTTPError(
        "Not found",
        status_code=404
    )

    # Act & Assert
    with pytest.raises(PageNotFoundError):
        await mock_api.pages.retrieve("nonexistent")
```

### 3. Pagination Test

```python
async def test_fetch_all_pages(mock_api):
    """Test fetching all pages with pagination."""
    # Setup: Mock multiple pages
    page1 = {"results": [{"id": "1"}], "has_more": true, ...}
    page2 = {"results": [{"id": "2"}], "has_more": False, ...}

    mock_api._request.side_effect = [page1, page2]

    # Act
    response = PaginatedResponse(...)
    all_items = await response.fetch_all()

    # Assert
    assert len(all_items) == 2
```

---

## Pre-Commit Testing

### Local Testing Before Push

```bash
# Run tests locally
uv run pytest

# Run with coverage
uv run pytest --cov=better_notion

# Run specific test file
uv run pytest tests/unit/test_http_client.py

# Run with verbose output
uv run pytest -vv
```

### Pre-commit Hooks

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.1.0
    hooks:
      - id: ruff
        name: Run ruff linter
      - id: ruff-format
        name: Run ruff formatter

# Install hooks
pre-commit install
```

---

## Test Stability

### Flaky Tests

**Definition:** Tests that intermittently fail due to timing, dependencies, or external factors.

**How to Fix:**
- Add delays for async operations
- Mock external dependencies
- Use fixtures instead of real API calls
- Make tests deterministic

### Example Fix

```python
# FLAKY: Race condition
async def test_page_retrieval():
    page = await api.pages.retrieve(page_id)
    # Sometimes fails due to timing
    assert page["id"] == "page_id"

# FIXED: Add delay and retry
async def test_page_retrieval_stable():
    max_attempts = 3
    for attempt in range(max_attempts):
        try:
            page = await api.pages.retrieve(page_id)
            assert page["id"] == "page_id"
            return
        except HTTPError:
            await asyncio.sleep(0.1)  # Wait between retries
```

---

## Performance

### Test Parallelization

```python
# Run tests in parallel
pytest -n auto -x -v

# Limit parallel workers
pytest -n 4
```

### Test Discovery

```python
# Auto-discover all tests
pytest

# Run specific file
pytest tests/unit/test_http_client.py

# Run specific test
pytest tests/unit/test_http_client.py::TestHTTPClient::test_request_success

# Run with marker
pytest -m unit
```

---

## Continuous Improvement

### Review Test Results

After each CI run:

1. Check coverage report for gaps
2. Identify slow tests
3. Find flaky tests
4. Add tests for uncovered code
5. Optimize slow tests

### Test Metrics Tracking

**Metrics to Monitor:**
- Number of tests over time
- Test success rate
- Coverage trends
- Average test duration
- Most common failures

---

## Troubleshooting

### Common Issues

#### 1. Test Timeout in CI

**Problem:** Tests timeout in CI but pass locally

**Causes:**
- CI environment slower than expected
- Missing dependencies in CI
- Environment variables not set

**Solutions:**
```yaml
# Increase timeout
- name: Run pytest with timeout
  run: |
    uv run pytest --timeout=10
```

#### 2. Import Errors in CI

**Problem:** Tests fail with import errors locally

**Causes:**
- Package not installed
- Wrong Python version
- Wrong working directory

**Solutions:**
```bash
# Ensure you're in venv
source .venv/bin/activate

# Install dependencies
uv sync

# Verify package installed
uv pip list | grep better_notion
```

#### 3. Coverage Not Uploading

**Problem:** Coverage not appearing on Codecov

**Causes:**
- Missing Codecov token
- Coverage XML not found
- Coverage report path issues

**Solutions:**
- Check `CODECOV_TOKEN` secret is set
- Verify `coverage.xml` is generated
- Check coverage file paths

---

## Related Documentation

- [CI Workflows](./ci-workflows.md) - Workflow specifications
- [Overview](./overview.md) - CI/CD strategy
- [Release Process](./releases.md) - Release testing
- [Security](./security.md) - Test environment security

---

## Summary

**In CI, we run:**
- Unit tests (all files in `tests/unit/`)
- Python 3.10, 3.11, 3.12
- Coverage enforcement (≥80%)
- Lint checks (ruff)
- Format checks (ruff format)

**Not run in CI:**
- Integration tests (run separately or manually)
- Slow tests (>1s) - use `@pytest.mark.slow`
- Manual tests - use `@pytest.mark.manual`

**Coverage goals:**
- Line coverage: ≥80%
- Branch coverage: ≥70%
- File coverage: ≥75%
