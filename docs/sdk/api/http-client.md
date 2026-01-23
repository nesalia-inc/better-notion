# HTTP Client

The HTTP client is the foundation of the low-level API, handling all communication with Notion's servers. We use **httpx** for modern async HTTP with HTTP/2 support.

## Technology Choice: httpx

We chose httpx over alternatives for several reasons:

### Why httpx?

| Feature | httpx | aiohttp | requests+asyncio |
|---------|-------|---------|-----------------|
| **HTTP/2 Support** | ✓ | ✗ | ✗ |
| **Modern API** | ✓ | Legacy | ✗ |
| **Sync + Async** | Same API | Different APIs | No async support |
| **Connection Pooling** | ✓ | ✓ | Limited |
| **Active Development** | ✓ | ✓ | Maintenance mode |
| **Type Hints** | ✓ | Partial | ✓ |
| **Multipart Upload** | ✓ | Complex | ✗ |

### httpx Features We Use

```python
import httpx

# Async client with connection pooling
client = httpx.AsyncClient(
    http2=True,  # HTTP/2 support
    timeout=httpx.Timeout(30.0),
    limits=httpx.Limits(
        max_connections=100,
        max_keepalive_connections=20
    )
)

# Automatic decompression
response = await client.get(url, follow_redirects=True)

# Multipart file uploads
with open("file.pdf", "rb") as f:
    files = {"file": f}
    await client.post(url, files=files)
```

## HTTP Client Interface

### Core Interface

```python
class HTTPClient:
    """
    HTTP client abstraction over httpx.

    Handles:
    - Connection management
    - Timeouts
    - SSL/TLS
    - Compression (gzip, brotli)
    - Redirects
    """

    def __init__(
        self,
        base_url: str = "https://api.notion.com",
        *,
        timeout: int = 30,
        http2: bool = True,
        max_connections: int = 100,
        max_keepalive_connections: int = 20
    ):
        """
        Initialize HTTP client.

        Args:
            base_url: Base URL for Notion API
            timeout: Request timeout in seconds
            http2: Enable HTTP/2
            max_connections: Maximum concurrent connections
            max_keepalive_connections: Maximum keep-alive connections
        """
        self.base_url = base_url.rstrip("/")
        self._client = httpx.AsyncClient(
            base_url=self.base_url,
            timeout=httpx.Timeout(timeout),
            http2=http2,
            limits=httpx.Limits(
                max_connections=max_connections,
                max_keepalive_connections=max_keepalive_connections,
                keepalive_expiry=5.0
            )
        )

    async def request(
        self,
        method: str,
        path: str,
        *,
        headers: dict[str, str] | None = None,
        params: dict[str, Any] | None = None,
        json: dict[str, Any] | None = None,
        content: str | bytes | None = None
    ) -> dict:
        """
        Make an HTTP request.

        Args:
            method: HTTP method (GET, POST, PATCH, DELETE)
            path: Request path (e.g., "/pages/{page_id}")
            headers: Additional headers
            params: Query parameters
            json: JSON body (automatically serialized)
            content: Raw content body

        Returns:
            Parsed JSON response as dict

        Raises:
            HTTPError: For 4xx/5xx responses
            NetworkError: For connection issues
        """
        url = path  # httpx appends to base_url

        response = await self._client.request(
            method=method,
            url=url,
            headers=headers,
            params=params,
            json=json,
            content=content
        )

        # Raise for 4xx/5xx
        response.raise_for_status()

        # Parse JSON
        return response.json()

    async def close(self) -> None:
        """Close the HTTP client and release resources."""
        await self._client.aclose()

    async def __aenter__(self):
        """Async context manager entry."""
        return self

    async def __aexit__(self, *args):
        """Async context manager exit."""
        await self.close()
```

## Configuration

### Timeout Configuration

```python
from httpx import Timeout, TimeoutException

# Global timeout
client = HTTPClient(timeout=30)

# Per-operation timeout
client = HTTPClient(
    timeout=Timeout(
        connect=10.0,  # Connection timeout
        read=30.0,     # Read timeout
        write=30.0,    # Write timeout
        pool=5.0       # Pool timeout
    )
)
```

### Connection Pool Configuration

```python
from httpx import Limits

# Optimized for high throughput
client = HTTPClient(
    max_connections=100,              # Total concurrent
    max_keepalive_connections=20,     # Persistent connections
    keepalive_expiry=5.0              # Close idle after 5s
)

# Optimized for memory
client = HTTPClient(
    max_connections=10,
    max_keepalive_connections=5
)
```

### HTTP/2

```python
# Enable HTTP/2 (default)
client = HTTPClient(http2=True)

# Disable HTTP/2
client = HTTPClient(http2=False)

# Benefits of HTTP/2:
# - Multiplexing (multiple requests over one TCP connection)
# - Header compression (HPACK)
# - Server push (when Notion supports it)
# - Reduced latency
```

## Request Building

### Adding Headers

```python
class RequestBuilder:
    """Build HTTP requests with common headers."""

    def __init__(
        self,
        auth: Auth,
        api_version: str
    ):
        self.auth = auth
        self.api_version = api_version

    def build_headers(
        self,
        custom_headers: dict[str, str] | None = None
    ) -> dict[str, str]:
        """
        Build request headers.

        Always includes:
        - Authorization (from auth)
        - Notion-Version
        - Content-Type (for JSON requests)
        """
        headers = {
            "Authorization": self.auth.get_header(),
            "Notion-Version": self.api_version,
            "User-Agent": "better-notion/0.1.0"
        }

        # Add Content-Type for JSON requests
        if not custom_headers or "Content-Type" not in custom_headers:
            headers["Content-Type"] = "application/json"

        # Merge custom headers
        if custom_headers:
            headers.update(custom_headers)

        return headers
```

### URL Building

```python
from urllib.parse import urljoin

def build_url(
    base_url: str,
    path: str,
    params: dict[str, Any] | None = None
) -> str:
    """
    Build complete URL with query parameters.

    Args:
        base_url: Base URL (e.g., "https://api.notion.com/v1")
        path: Path (e.g., "/pages/{page_id}")
        params: Query parameters

    Returns:
        Complete URL
    """
    url = urljoin(base_url, path)

    if params:
        query_string = "&".join(
            f"{k}={v}" for k, v in params.items()
        )
        url = f"{url}?{query_string}"

    return url
```

## Response Handling

### Response Parsing

```python
class ResponseParser:
    """Parse HTTP responses from Notion API."""

    def parse_json(self, response: httpx.Response) -> dict:
        """
        Parse JSON response.

        Args:
            response: httpx Response object

        Returns:
            Parsed JSON as dict

        Raises:
            ValidationError: If response is not valid JSON
        """
        try:
            return response.json()
        except ValueError as e:
            raise ValidationError(
                f"Invalid JSON response: {e}",
                status_code=response.status_code
            ) from e

    def extract_headers(
        self,
        response: httpx.Response
    ) -> dict[str, str]:
        """
        Extract relevant headers from response.

        Focuses on:
        - Rate limit headers
        - Content type
        - Request ID (for debugging)
        """
        return {
            "x-ratelimit-limit": response.headers.get("x-ratelimit-limit"),
            "x-ratelimit-remaining": response.headers.get("x-ratelimit-remaining"),
            "x-ratelimit-reset": response.headers.get("x-ratelimit-reset"),
            "x-ratelimit-used": response.headers.get("x-ratelimit-used"),
            "content-type": response.headers.get("content-type"),
            "x-notion-request-id": response.headers.get("x-notion-request-id")
        }
```

### Error Detection

```python
def is_error_response(response: httpx.Response) -> bool:
    """Check if response indicates an error."""
    return response.status_code >= 400

def is_rate_limited(response: httpx.Response) -> bool:
    """Check if response indicates rate limiting."""
    return response.status_code == 429

def is_server_error(response: httpx.Response) -> bool:
    """Check if response indicates server error."""
    return response.status_code >= 500
```

## Performance Optimizations

### Connection Reuse

httpx automatically reuses connections:

```python
# These requests reuse the same connection
client = HTTPClient()

await client.request("GET", "/pages/page1")
await client.request("GET", "/pages/page2")
await client.request("GET", "/pages/page3")
# All over same TCP connection (HTTP/1.1 keep-alive or HTTP/2)
```

### Concurrent Requests

```python
import asyncio

async def fetch_multiple_pages(
    client: HTTPClient,
    page_ids: list[str]
) -> list[dict]:
    """
    Fetch multiple pages concurrently.

    Uses asyncio.gather for parallel requests.
    """
    tasks = [
        client.request("GET", f"/pages/{page_id}")
        for page_id in page_ids
    ]

    return await asyncio.gather(*tasks)

# Usage
pages = await fetch_multiple_pages(client, ["id1", "id2", "id3"])
```

### Streaming (Future)

For large file uploads/downloads:

```python
# Not implemented in V1, but possible with httpx
async def download_file(url: str) -> AsyncIterator[bytes]:
    """Stream file download."""
    async with httpx.AsyncClient() as client:
        async with client.stream("GET", url) as response:
            async for chunk in response.aiter_bytes():
                yield chunk
```

## Testing Utilities

### Mock Transport

```python
import httpx

class MockTransport(httpx.BaseTransport):
    """Mock transport for testing."""

    def __init__(self, responses: dict):
        """
        Initialize with canned responses.

        Args:
            responses: Map of (method, path) → response
        """
        self.responses = responses

    async def handle_request(self, request: httpx.Request) -> httpx.Response:
        """Return canned response based on request."""
        key = (request.method, request.url.path)

        if key in self.responses:
            return self.responses[key]

        # Default 404
        return httpx.Response(
            status_code=404,
            json={"error": "Not found"}
        )

# Usage in tests
mock_transport = MockTransport({
    ("GET", "/pages/page1"): httpx.Response(
        200,
        json={"id": "page1", "title": "Test"}
    )
})

client = HTTPClient(transport=mock_transport)
response = await client.request("GET", "/pages/page1")
```

## Best Practices

### 1. Always Use Context Manager (for cleanup)

```python
# GOOD
async with HTTPClient() as client:
    await client.request("GET", "/pages/page1")

# AVOID
client = HTTPClient()
await client.request("GET", "/pages/page1")
# Don't forget to close!
```

### 2. Configure Timeouts Appropriately

```python
# For most operations
client = HTTPClient(timeout=30)

# For long-running operations (bulk uploads)
client = HTTPClient(timeout=300)

# For quick operations
client = HTTPClient(timeout=10)
```

### 3. Reuse Client Instances

```python
# GOOD
client = HTTPClient()
for page_id in page_ids:
    await client.request("GET", f"/pages/{page_id}")

# AVOID
for page_id in page_ids:
    client = HTTPClient()  # Wasteful
    await client.request("GET", f"/pages/{page_id}")
```

### 4. Handle Connection Errors

```python
from httpx import ConnectError, ReadTimeout, RemoteProtocolError

try:
    response = await client.request("GET", "/pages/page1")
except ConnectError as e:
    logger.error(f"Failed to connect: {e}")
except ReadTimeout as e:
    logger.error(f"Read timeout: {e}")
except RemoteProtocolError as e:
    logger.error(f"Protocol error: {e}")
```

## Configuration Examples

### Development

```python
# Development: More logging, longer timeouts
client = HTTPClient(
    timeout=60,
    max_connections=10
)
```

### Production

```python
# Production: Optimized for throughput
client = HTTPClient(
    timeout=30,
    http2=True,
    max_connections=100,
    max_keepalive_connections=20
)
```

### Testing

```python
# Testing: Mock transport, no real HTTP
client = HTTPClient(transport=mock_transport)
```

## Monitoring

### Request Logging

```python
import time

class InstrumentedHTTPClient(HTTPClient):
    """HTTP client with request logging."""

    async def request(self, *args, **kwargs) -> dict:
        start = time.time()

        try:
            response = await super().request(*args, **kwargs)
            duration = time.time() - start

            self.logger.info(
                f"Request completed in {duration:.3f}s",
                extra={
                    "method": args[0],
                    "path": args[1],
                    "duration": duration,
                    "status": "success"
                }
            )

            return response
        except Exception as e:
            duration = time.time() - start

            self.logger.error(
                f"Request failed after {duration:.3f}s",
                extra={
                    "method": args[0],
                    "path": args[1],
                    "duration": duration,
                    "status": "error",
                    "error": str(e)
                }
            )
            raise
```

## Related Documentation

- [Overview](./overview.md) - Low-level API overview
- [Authentication](./authentication.md) - Auth headers
- [Rate Limiting](./rate-limiting.md) - Using rate limit headers
- [Error Handling](./error-handling.md) - Error responses
- [Testing](./testing.md) - Mock HTTP client

## Next Steps

1. Choose appropriate timeout values for your use case
2. Configure connection pool size based on expected load
3. Set up logging for monitoring
4. Implement error handling for network issues
