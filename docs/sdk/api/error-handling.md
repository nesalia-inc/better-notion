# Error Handling

Comprehensive error handling is essential for a robust SDK. The low-level API maps HTTP errors to semantic exceptions and provides automatic retry with exponential backoff.

## Exception Hierarchy

```
NotionAPIError (base)
├── HTTPError (HTTP errors)
│   ├── ClientError (4xx errors)
│   │   ├── BadRequestError (400)
│   │   ├── UnauthorizedError (401)
│   │   ├── ForbiddenError (403)
│   │   ├── NotFoundError (404)
│   │   ├── ConflictError (409)
│   │   ├── ValidationError (400)
│   │   └── RateLimitedError (429)
│   └── ServerError (5xx errors)
│       ├── InternalServerError (500)
│       ├── BadGatewayError (502)
│       ├── ServiceUnavailableError (503)
│       └── GatewayTimeoutError (504)
├── NetworkError (network issues)
├── ValidationError (validation errors)
└── ConfigurationError (configuration issues)
```

## Base Exception

### NotionAPIError

```python
class NotionAPIError(Exception):
    """
    Base exception for all SDK errors.

    All exceptions inherit from this class,
    allowing you to catch all SDK errors:
    ```python
    try:
        await api.pages.create(...)
    except NotionAPIError as e:
        logger.error(f"SDK error: {e}")
    ```
    """

    def __init__(
        self,
        message: str,
        *,
        status_code: int | None = None,
        response: dict | None = None
    ):
        """
        Initialize exception.

        Args:
            message: Error message
            status_code: HTTP status code (if applicable)
            response: Full API response (if applicable)
        """
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.response = response

    def __repr__(self) -> str:
        """Developer-friendly representation."""
        if self.status_code:
            return f"{self.__class__.__name__}({self.status_code}: {self.message})"
        return f"{self.__class__.__name__}({self.message})"

    def __str__(self) -> str:
        """User-friendly string representation."""
        return self.message
```

## HTTP Errors

### HTTPError (Base)

```python
class HTTPError(NotionAPIError):
    """
    Base class for HTTP errors.

    Raised when the API returns an HTTP error status code.
    """

    def __init__(
        self,
        message: str,
        status_code: int,
        *,
        response: dict | None = None
    ):
        super().__init__(
            message,
            status_code=status_code,
            response=response
        )
```

### Client Errors (4xx)

#### BadRequestError (400)

```python
class BadRequestError(HTTPError):
    """
    400 Bad Request.

    Raised when the request is malformed or contains invalid data.
    """

    def __init__(self, message: str, *, response: dict | None = None):
        super().__init__(message, status_code=400, response=response)
```

**Common Causes:**
- Invalid JSON in request body
- Malformed request parameters
- Missing required fields
- Invalid data types

**Example:**
```python
try:
    await api.pages.create(
        parent=database,
        properties={"invalid": "data"}  # Invalid schema
    )
except BadRequestError as e:
    print(f"Invalid request: {e.message}")
```

#### UnauthorizedError (401)

```python
class UnauthorizedError(HTTPError):
    """
    401 Unauthorized.

    Raised when authentication fails or credentials are invalid.
    """

    def __init__(self, message: str = "Authentication failed", **kwargs):
        super().__init__(message, status_code=401, **kwargs)
```

**Common Causes:**
- Invalid or expired token
- Missing Authorization header
- OAuth token expired

**Example:**
```python
try:
    api = NotionAPI(auth="invalid_token")
    await api.pages.retrieve(page_id)
except UnauthorizedError:
    print("Invalid token, check integration settings")
```

#### ForbiddenError (403)

```python
class ForbiddenError(HTTPError):
    """
    403 Forbidden.

    Raised when the integration lacks permission to access the resource.
    """

    def __init__(self, message: str, **kwargs):
        super().__init__(message, status_code=403, **kwargs)
```

**Common Causes:**
- Integration lacks required capability
- Resource not shared with integration
- User doesn't have access to the page/database

**Example:**
```python
try:
    await api.users.list()  # Requires user info capability
except ForbiddenError:
    print("Enable 'user information' capability in integration settings")
```

#### NotFoundError (404)

```python
class NotFoundError(HTTPError):
    """
    404 Not Found.

    Raised when the requested resource doesn't exist.
    """

    def __init__(self, message: str, **kwargs):
        super().__init__(message, status_code=404, **kwargs)
```

**Example:**
```python
try:
    await api.pages.retrieve(page_id="nonexistent")
except NotFoundError:
    print(f"Page not found: {page_id}")
```

#### Resource-Specific Not Found Errors

```python
class PageNotFoundError(NotFoundError):
    """404 for specific page not found."""
    pass

class DatabaseNotFoundError(NotFoundError):
    """404 for specific database not found."""
    pass

class BlockNotFoundError(NotFoundError):
    """404 for specific block not found."""
    pass

class UserNotFoundError(NotFoundError):
    """404 for specific user not found."""
    pass
```

#### ConflictError (409)

```python
class ConflictError(HTTPError):
    """
    409 Conflict.

    Raised when the request conflicts with current resource state.
    """

    def __init__(self, message: str, **kwargs):
        super().__init__(message, status_code=409, **kwargs)
```

**Common Causes:**
- Concurrent modification conflicts
- Invalid state transition

#### RateLimitedError (429)

```python
class RateLimitedError(HTTPError):
    """
    429 Rate Limited.

    Raised when rate limit is exceeded.

    Attributes:
        retry_after: Seconds to wait before retrying
    """

    def __init__(
        self,
        message: str = "Rate limited",
        *,
        retry_after: int | None = None,
        **kwargs
    ):
        super().__init__(message, status_code=429, **kwargs)
        self.retry_after = retry_after

    def get_wait_time(self) -> int:
        """
        Get recommended wait time in seconds.

        Returns:
            Seconds to wait before retrying
        """
        return self.retry_after or 1
```

**Example:**
```python
try:
    await api.pages.create(...)
except RateLimitedError as e:
    wait_time = e.get_wait_time()
    print(f"Rate limited, wait {wait_time}s before retrying")
    await asyncio.sleep(wait_time)
```

### Server Errors (5xx)

#### ServerError (Base)

```python
class ServerError(HTTPError):
    """
    Base class for 5xx server errors.

    Indicates a problem with Notion's servers.
    """

    def __init__(self, message: str, **kwargs):
        super().__init__(
            message,
            status_code=500,
            **kwargs
        )
```

#### InternalServerError (500)

```python
class InternalServerError(ServerError):
    """
    500 Internal Server Error.

    Unexpected error on Notion's servers.
    """

    def __init__(self, message: str = "Internal server error", **kwargs):
        super().__init__(message, status_code=500, **kwargs)
```

#### BadGatewayError (502)

```python
class BadGatewayError(ServerError):
    """
    502 Bad Gateway.

    Notion API gateway received invalid response from upstream.
    """

    def __init__(self, message: str = "Bad gateway", **kwargs):
        super().__init__(message, status_code=502, **kwargs)
```

#### ServiceUnavailableError (503)

```python
class ServiceUnavailableError(ServerError):
    """
    503 Service Unavailable.

    Notion API temporarily unavailable (maintenance, etc.).
    """

    def __init__(self, message: str = "Service unavailable", **kwargs):
        super().__init__(message, status_code=503, **kwargs)
```

#### GatewayTimeoutError (504)

```python
class GatewayTimeoutError(ServerError):
    """
    504 Gateway Timeout.

    Notion API gateway timed out waiting for upstream.
    """

    def __init__(self, message: str = "Gateway timeout", **kwargs):
        super().__init__(message, status_code=504, **kwargs)
```

## Network Errors

### NetworkError

```python
class NetworkError(NotionAPIError):
    """
    Base class for network-related errors.

    Raised when network communication fails.
    """

    def __init__(
        self,
        message: str,
        *,
        original_error: Exception | None = None
    ):
        super().__init__(message)
        self.original_error = original_error
```

### Specific Network Errors

```python
class ConnectionError(NetworkError):
    """
    Failed to establish connection to Notion API.
    """

    def __init__(self, message: str = "Connection failed", **kwargs):
        super().__init__(message, **kwargs)

class TimeoutError(NetworkError):
    """
    Request timed out.

    This is different from HTTP timeout errors.
    """

    def __init__(self, message: str = "Request timed out", **kwargs):
        super().__init__(message, **kwargs)

class SSLError(NetworkError):
    """
    SSL/TLS certificate validation failed.
    """

    def __init__(self, message: str = "SSL error", **kwargs):
        super().__init__(message, **kwargs)
```

## Validation Errors

### ValidationError

```python
class ValidationError(NotionAPIError):
    """
    Data validation error.

    Raised when input data fails validation before sending to API.
    This is raised client-side, not by the Notion API.
    """

    def __init__(
        self,
        message: str,
        *,
        field: str | None = None,
        value: Any = None,
        **kwargs
    ):
        super().__init__(message, **kwargs)
        self.field = field
        self.value = value
```

**Example:**
```python
# Client-side validation
def validate_page_id(page_id: str) -> None:
    """Validate page ID format."""
    try:
        uuid.UUID(page_id)
    except ValueError:
        raise ValidationError(
            f"Invalid page ID format: {page_id}",
            field="page_id",
            value=page_id
        )

# Usage
validate_page_id("invalid-id")  # Raises ValidationError
```

## Configuration Errors

### ConfigurationError

```python
class ConfigurationError(NotionAPIError):
    """
    Configuration error.

    Raised when SDK is misconfigured.
    """

    def __init__(
        self,
        message: str,
        *,
        parameter: str | None = None,
        **kwargs
    ):
        super().__init__(message, **kwargs)
        self.parameter = parameter
```

**Examples:**
```python
# Invalid timeout
api = NotionAPI(auth=token, timeout=-1)
# Raises ConfigurationError("Timeout must be positive")

# Invalid API version
api = NotionAPI(auth=token, api_version="invalid")
# Raises ConfigurationError("Invalid API version")
```

## Error Mapping

### HTTP Status to Exception

```python
ERROR_MAP = {
    400: BadRequestError,
    401: UnauthorizedError,
    403: ForbiddenError,
    404: NotFoundError,
    409: ConflictError,
    429: RateLimitedError,
    500: InternalServerError,
    502: BadGatewayError,
    503: ServiceUnavailableError,
    504: GatewayTimeoutError,
}

def status_code_to_exception(
    status_code: int,
    message: str,
    response: dict
) -> HTTPError:
    """
    Map HTTP status code to appropriate exception.

    Args:
        status_code: HTTP status code
        message: Error message from response
        response: Full response body

    Returns:
        Appropriate HTTPError subclass
    """
    exception_class = ERROR_MAP.get(
        status_code,
        HTTPError  # Fallback
    )

    return exception_class(
        message,
        status_code=status_code,
        response=response
    )
```

## Error Handling in HTTP Client

```python
async def _request(
    self,
    method: str,
    path: str,
    **kwargs
) -> dict:
    """
    Make HTTP request with error handling.

    Raises:
        HTTPError: For 4xx/5xx responses
        NetworkError: For network failures
        NotionAPIError: For other errors
    """
    try:
        response = await self._http_client.request(
            method,
            path,
            **kwargs
        )

        # Check for HTTP errors
        if response.status_code >= 400:
            raise status_code_to_exception(
                response.status_code,
                response.get("message", "Unknown error"),
                response
            )

        return response

    except httpx.TimeoutException as e:
        # Request timeout
        raise TimeoutError(
            f"Request timed out: {e}",
            original_error=e
        )

    except httpx.NetworkError as e:
        # Connection error
        raise ConnectionError(
            f"Connection failed: {e}",
            original_error=e
        )

    except httpx.HTTPStatusError as e:
        # httpx raised for 4xx/5xx
        # (Shouldn't happen if we check raise_for_status first)
        raise HTTPError(
            f"HTTP error: {e}",
            status_code=e.response.status_code
        )
```

## Best Practices

### 1. Catch Specific Exceptions

```python
# GOOD: Catch specific exceptions
try:
    await api.pages.retrieve(page_id)
except NotFoundError:
    logger.error(f"Page not found: {page_id}")
except RateLimitedError as e:
    logger.warning(f"Rate limited, retry after {e.retry_after}s")
except HTTPError as e:
    logger.error(f"HTTP error {e.status_code}: {e.message}")

# AVOID: Catching base exception (too broad)
try:
    await api.pages.retrieve(page_id)
except Exception:
    pass  # Catches everything, including KeyboardInterrupt
```

### 2. Provide Helpful Error Messages

```python
# GOOD: Contextual error messages
try:
    await api.pages.create(...)
except BadRequestError as e:
    logger.error(
        f"Failed to create page '{title}': {e.message}. "
        f"Check the property schema."
    )

# AVOID: Generic error messages
try:
    await api.pages.create(...)
except Exception as e:
    logger.error(f"Error: {e}")  # Not helpful
```

### 3. Preserve Original Error

```python
# GOOD: Include original error for debugging
try:
    await api.pages.retrieve(page_id)
except ConnectionError as e:
    logger.error(
        f"Connection failed: {e.message}",
        exc_info=e.original_error  # Original exception
    )

# This preserves stack trace and original error details
```

### 4. Use Finally for Cleanup

```python
resource = acquire_resource()
try:
    await api.pages.create(...)

except HTTPError as e:
    logger.error(f"API error: {e}")
    raise

finally:
    # Always cleanup, even on error
    resource.cleanup()
```

### 5. Re-raise with Context

```python
# GOOD: Re-raise with additional context
try:
    await api.pages.create(...)
except NotFoundError as e:
    raise RuntimeError(
        f"Failed to create page in database '{database_id}': {e}"
    ) from e

# Preserves original exception with `from e`
```

## Retry Logic

### Retry Configuration

```python
class RetryConfig:
    """Configuration for automatic retry."""

    def __init__(
        self,
        max_attempts: int = 3,
        backoff_factor: float = 0.5,
        retry_on_status: list[int] | None = None,
        retry_on_exceptions: list[type] | None = None
    ):
        self.max_attempts = max_attempts
        self.backoff_factor = backoff_factor

        # Retry on these HTTP status codes
        self.retry_on_status = retry_on_status or [
            429,  # Rate limited
            500,  # Internal server error
            502,  # Bad gateway
            503,  # Service unavailable
            504,  # Gateway timeout
        ]

        # Retry on these exception types
        self.retry_on_exceptions = retry_on_exceptions or [
            TimeoutError,
            ConnectionError,
        ]
```

### Retry Implementation

```python
async def _request_with_retry(
    self,
    request_fn: Callable,
    config: RetryConfig
) -> dict:
    """
    Execute request with retry logic.

    Retries on:
    - Configured HTTP status codes
    - Configured exception types

    Uses exponential backoff between attempts.
    """
    last_exception = None

    for attempt in range(config.max_attempts):
        try:
            return await request_fn()

        except Exception as e:
            last_exception = e

            # Check if we should retry
            should_retry = (
                isinstance(e, tuple(config.retry_on_exceptions)) or
                (isinstance(e, HTTPError) and
                 e.status_code in config.retry_on_status)
            )

            if not should_retry:
                raise

            # Calculate backoff time
            wait_time = config.backoff_factor * (2 ** attempt)

            # Add jitter (±10%)
            jitter = random.uniform(-0.1, 0.1) * wait_time
            wait_time += jitter

            logger.warning(
                f"Request failed (attempt {attempt + 1}/{config.max_attempts}), "
                f"retrying in {wait_time:.2f}s: {e}"
            )

            await asyncio.sleep(wait_time)

    # All retries exhausted
    raise last_exception
```

## Error Messages

### Good Error Messages

```python
# BAD
raise NotFoundError("Not found")

# GOOD: Specific and actionable
raise PageNotFoundError(
    f"Page '{page_id}' not found. "
    f"Verify the page exists and your integration has access."
)
```

### Error Message Templates

```python
class ErrorMessages:
    """Templates for common error messages."""

    @staticmethod
    def page_not_found(page_id: str) -> str:
        return (
            f"Page '{page_id}' not found. "
            f"Make sure the page exists and your integration has access."
        )

    @staticmethod
    def unauthorized(resource: str) -> str:
        return (
            f"Unauthorized to access {resource}. "
            f"Check your integration token and capabilities."
        )

    @staticmethod
    def rate_limited(retry_after: int) -> str:
        return (
            f"Rate limited. Wait {retry_after} seconds before retrying. "
            f"Consider reducing request frequency."
        )

    @staticmethod
    def validation_error(
        field: str,
        value: Any,
        expected: str
    ) -> str:
        return (
            f"Invalid value for '{field}': {value!r}. "
            f"Expected: {expected}"
        )
```

## Error Logging

### Structured Error Logging

```python
import logging
import json

def log_error(
    logger: logging.Logger,
    error: Exception,
    context: dict | None = None
) -> None:
    """Log error with structured information."""
    log_data = {
        "error_type": type(error).__name__,
        "error_message": str(error),
    }

    if isinstance(error, HTTPError):
        log_data["status_code"] = error.status_code

    if context:
        log_data["context"] = context

    logger.error(
        f"{log_data['error_type']}: {log_data['error_message']}",
        extra=log_data
    )
```

## Testing Error Handling

### Testing Error Scenarios

```python
import pytest
from better_notion.api import NotionAPI, NotFoundError

@pytest.mark.asyncio
async def test_page_not_found():
    """Test 404 error handling."""
    api = NotionAPI(auth="test_token")

    # Mock 404 response
    with patch.object(api, '_http_client') as mock:
        mock.request.return_value = MockResponse(
            status_code=404,
            json={"message": "Not found"}
        )

        with pytest.raises(PageNotFoundError):
            await api.pages.retrieve("nonexistent_id")

@pytest.mark.asyncio
async def test_rate_limit_retry():
    """Test rate limit retry logic."""
    api = NotionAPI(
        auth="test_token",
        retry_config=RetryConfig(max_attempts=3)
    )

    with patch.object(api, '_http_client') as mock:
        # First call: 429, second: success
        mock.request.side_effect = [
            MockResponse(status_code=429, ...),
            MockResponse(status_code=200, json={...})
        ]

        result = await api.pages.retrieve("page_id")

        # Should have succeeded after retry
        assert mock.request.call_count == 2
        assert result is not None
```

## Related Documentation

- [Overview](./overview.md) - Low-level API overview
- [HTTP Client](./http-client.md) - HTTP layer
- [Rate Limiting](./rate-limiting.md) - Rate limit error handling
- [Testing](./testing.md) - Testing error scenarios

## Next Steps

1. Implement exception hierarchy
2. Add comprehensive error messages
3. Configure retry logic appropriately
4. Add structured logging
5. Write tests for error scenarios
