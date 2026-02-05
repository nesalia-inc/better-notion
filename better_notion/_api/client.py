"""Notion API client."""

from __future__ import annotations

from typing import Any

import httpx

from better_notion._api.collections import (
    BlockCollection,
    CommentCollection,
    DatabaseCollection,
    PageCollection,
    UserCollection,
)
from better_notion._api.errors import NotionAPIError
from better_notion._api.oauth import OAuthTokenHandler


class NotionAPI:
    """Notion API client with object-oriented interface.

    This client provides collections that return entity objects,
    allowing for true object-oriented interaction with Notion.

    Attributes:
        pages: Page collection for managing pages.
        blocks: Block collection for managing blocks.
        databases: Database collection for managing databases.
        users: User collection for managing users.
        comments: Comment collection for managing comments.

    Example:
        >>> api = NotionAPI(auth="secret_...")  # or "ntn_..."
        >>> page = await api.pages.get("page_id")
        >>> print(page.title)
        >>> await page.delete()
    """

    DEFAULT_BASE_URL = "https://api.notion.com/v1"
    DEFAULT_TIMEOUT = 30.0
    DEFAULT_VERSION = "2022-06-28"

    def __init__(
        self,
        auth: str | None = None,
        *,
        auth_handler: OAuthTokenHandler | None = None,
        base_url: str = DEFAULT_BASE_URL,
        timeout: float = DEFAULT_TIMEOUT,
        version: str = DEFAULT_VERSION,
    ) -> None:
        """Initialize the Notion API client.

        Args:
            auth: Notion API token (starts with "secret_" or "ntn_").
                  Required if auth_handler not provided.
            auth_handler: Optional OAuthTokenHandler for OAuth-based authentication.
                         If provided, auth parameter is ignored.
            base_url: Base URL for the API.
            timeout: Request timeout in seconds.
            version: Notion API version.

        Raises:
            ValueError: If neither auth nor auth_handler is provided,
                       or if auth has invalid format.
        """
        if auth_handler:
            self._auth_handler = auth_handler
            self._token = auth_handler.access_token
        elif auth:
            if not (auth.startswith("secret_") or auth.startswith("ntn_")):
                raise ValueError(
                    'Invalid token format. Token must start with "secret_" or "ntn_"'
                )
            self._token = auth
            self._auth_handler = None
        else:
            raise ValueError("Either auth or auth_handler must be provided")

        self._base_url = base_url.rstrip("/") if base_url else self.DEFAULT_BASE_URL
        self._timeout = timeout
        self._version = version

        # Create HTTP client with connection limits for better compatibility
        self._http = httpx.AsyncClient(
            base_url=self._base_url,
            timeout=httpx.Timeout(timeout),
            headers=self._default_headers(),
            limits=httpx.Limits(max_keepalive_connections=1, max_connections=1),
        )

    @property
    def pages(self) -> PageCollection:
        """Page collection for managing pages."""
        return PageCollection(self)

    @property
    def blocks(self) -> BlockCollection:
        """Block collection for managing blocks."""
        return BlockCollection(self)

    @property
    def databases(self) -> DatabaseCollection:
        """Database collection for managing databases."""
        return DatabaseCollection(self)

    @property
    def users(self) -> UserCollection:
        """User collection for managing users."""
        return UserCollection(self)

    @property
    def comments(self) -> CommentCollection:
        """Comment collection for managing comments."""
        return CommentCollection(self)

    async def search(
        self,
        query: str,
        *,
        filter: dict[str, Any] | None = None,
        sort: dict[str, Any] | None = None,
        start_cursor: str | None = None,
    ) -> dict[str, Any]:
        """Search for pages and blocks in the user's Notion workspace.

        Args:
            query: Search query text.
            filter: Optional filter object (e.g., {"value": "page", "property": "object"}).
            sort: Optional sort object.
            start_cursor: Optional cursor for pagination.

        Returns:
            Search results with pages/blocks list.

        Raises:
            ValidationError: If the search parameters are invalid.
        """
        body: dict[str, Any] = {"query": query}

        if filter:
            body["filter"] = filter
        if sort:
            body["sort"] = sort
        if start_cursor:
            body["start_cursor"] = start_cursor

        return await self._request("POST", "/search", json=body)

    def search_iterate(
        self,
        query: str,
        *,
        filter: dict[str, Any] | None = None,
        sort: dict[str, Any] | None = None,
    ):
        """Iterate over all search results with automatic pagination.

        Args:
            query: Search query text.
            filter: Optional filter object.
            sort: Optional sort object.

        Returns:
            Async iterator that yields search results (raw dicts).

        Example:
            >>> async for result in api.search_iterate("my query"):
            ...     if result["object"] == "page":
            ...         print(result["properties"]["title"])

        Note:
            This method does not fetch results immediately. Results are fetched
            as you iterate, making it memory-efficient for large result sets.
        """
        from better_notion._api.utils import AsyncPaginatedIterator

        async def fetch_fn(cursor: str | None) -> dict[str, Any]:
            return await self.search(
                query,
                filter=filter,
                sort=sort,
                start_cursor=cursor,
            )

        return AsyncPaginatedIterator(fetch_fn, lambda data: data)

    def _default_headers(self) -> dict[str, str]:
        """Get default headers for requests.

        Returns:
            Default headers dictionary.
        """
        # Use current token from auth_handler if available
        token = self._auth_handler.access_token if self._auth_handler else self._token
        return {
            "Authorization": f"Bearer {token}",
            "Notion-Version": self._version,
            "Content-Type": "application/json",
        }

    async def _request(
        self,
        method: str,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        json: dict[str, Any] | None = None,
        _retry_count: int = 0,
    ) -> dict[str, Any]:
        """Make an HTTP request to the Notion API.

        Args:
            method: HTTP method.
            path: Request path (will be appended to base_url).
            params: Query parameters.
            json: JSON request body.
            _retry_count: Internal retry counter for token refresh.

        Returns:
            Response data as a dictionary.

        Raises:
            NotionAPIError: For API errors.
        """
        url = path if path.startswith("http") else f"{self._base_url}{path}"

        try:
            response = await self._http.request(
                method=method,
                url=url,
                params=params,
                json=json,
            )
            response.raise_for_status()
            return response.json()

        except httpx.HTTPStatusError as e:
            # Map HTTP errors to NotionAPIError subclasses
            status_code = e.response.status_code

            # Handle 401 Unauthorized with token refresh
            if status_code == 401 and self._auth_handler and self._auth_handler.has_refresh_token and _retry_count == 0:
                try:
                    # Refresh the token
                    await self._auth_handler.refresh(self._http)

                    # Retry the request with new token
                    return await self._request(
                        method,
                        path,
                        params=params,
                        json=json,
                        _retry_count=_retry_count + 1,
                    )
                except Exception:
                    # If refresh fails, fall through to normal 401 handling
                    pass

            if status_code == 400:
                from better_notion._api.errors import BadRequestError
                import json
                import logging
                import uuid

                logger = logging.getLogger(__name__)

                # Generate request ID for tracking
                request_id = uuid.uuid4().hex[:8]
                notion_request_id = e.response.headers.get('x-request-id')

                # Try to extract error details from Notion API response
                try:
                    error_data = e.response.json()
                    error_message = error_data.get("message", "Bad request")
                    error_code = error_data.get("code", "")

                    # Create error with rich context
                    error = BadRequestError(
                        f"{error_code}: {error_message}" if error_code else error_message,
                        request_id=request_id,
                        notion_code=error_code,
                        request_method=method,
                        request_path=path,
                        response_body=error_data,
                    )

                    # Add rich context using Exception.add_note()
                    error.add_note(f"Request ID: {request_id}")
                    if notion_request_id:
                        error.add_note(f"Notion Request ID: {notion_request_id}")
                    error.add_note(f"Operation: {method} {path}")
                    error.add_note(f"Status Code: {status_code}")
                    if error_code:
                        error.add_note(f"Notion Error Code: {error_code}")
                    error.add_note(f"Notion Message: {error_message}")

                    raise error from e

                except json.JSONDecodeError as parse_error:
                    # Response is not valid JSON - fall back to text
                    logger.debug("Failed to parse error response as JSON", exc_info=parse_error)

                    response_text = e.response.text if hasattr(e.response, 'text') else str(e)
                    error = BadRequestError(
                        f"Bad request: {response_text[:500]}",
                        request_id=request_id,
                        request_method=method,
                        request_path=path,
                    )

                    error.add_note(f"Request ID: {request_id}")
                    if notion_request_id:
                        error.add_note(f"Notion Request ID: {notion_request_id}")
                    error.add_note(f"Operation: {method} {path}")
                    error.add_note("Failed to parse error response as JSON")

                    raise error from e

                except Exception as unexpected_error:
                    # Something unexpected happened during error parsing
                    logger.error("Unexpected error while parsing error response", exc_info=unexpected_error)
                    error = BadRequestError(
                        "Bad request: unable to parse error details",
                        request_id=request_id,
                        request_method=method,
                        request_path=path,
                    )

                    error.add_note(f"Request ID: {request_id}")
                    error.add_note(f"Operation: {method} {path}")
                    error.add_note("Unexpected error during error parsing")

                    raise error from unexpected_error
            elif status_code == 401:
                from better_notion._api.errors import UnauthorizedError
                raise UnauthorizedError() from e
            elif status_code == 403:
                from better_notion._api.errors import ForbiddenError
                raise ForbiddenError() from e
            elif status_code == 404:
                from better_notion._api.errors import NotFoundError
                raise NotFoundError() from e
            elif status_code == 409:
                from better_notion._api.errors import ConflictError
                raise ConflictError() from e
            elif status_code == 429:
                from better_notion._api.errors import RateLimitedError
                retry_after = e.response.headers.get("Retry-After")
                raise RateLimitedError(
                    retry_after=int(retry_after) if retry_after else None
                ) from e
            elif status_code >= 500:
                from better_notion._api.errors import InternalServerError
                raise InternalServerError() from e
            else:
                raise NotionAPIError(f"HTTP {status_code}: {e.response.text}") from e

        except httpx.RequestError as e:
            from better_notion._api.errors import NetworkError
            raise NetworkError(f"Network error: {e}") from e

    async def __aenter__(self) -> NotionAPI:
        """Async context manager entry."""
        return self

    async def __aexit__(self, *args: Any) -> None:
        """Cleanup on context exit."""
        await self.close()

    async def close(self) -> None:
        """Close the HTTP client."""
        await self._http.aclose()

