"""Notion API client."""

from __future__ import annotations

from typing import Any

import httpx

from better_notion._api.collections import (
    BlockCollection,
    DatabaseCollection,
    PageCollection,
    UserCollection,
)
from better_notion._api.errors import NotionAPIError


class NotionAPI:
    """Notion API client with object-oriented interface.

    This client provides collections that return entity objects,
    allowing for true object-oriented interaction with Notion.

    Attributes:
        pages: Page collection for managing pages.
        blocks: Block collection for managing blocks.
        databases: Database collection for managing databases.
        users: User collection for managing users.

    Example:
        >>> api = NotionAPI(auth="secret_...")
        >>> page = await api.pages.get("page_id")
        >>> print(page.title)
        >>> await page.delete()
    """

    DEFAULT_BASE_URL = "https://api.notion.com/v1"
    DEFAULT_TIMEOUT = 30.0
    DEFAULT_VERSION = "2022-06-28"

    def __init__(
        self,
        auth: str,
        *,
        base_url: str = DEFAULT_BASE_URL,
        timeout: float = DEFAULT_TIMEOUT,
        version: str = DEFAULT_VERSION,
    ) -> None:
        """Initialize the Notion API client.

        Args:
            auth: Notion API token (starts with "secret_").
            base_url: Base URL for the API.
            timeout: Request timeout in seconds.
            version: Notion API version.
        """
        if not auth.startswith("secret_"):
            raise ValueError(
                'Invalid token format. Token must start with "secret_"'
            )

        self._token = auth
        self._base_url = base_url.rstrip("/")
        self._timeout = timeout
        self._version = version

        # Create HTTP client
        self._http = httpx.AsyncClient(
            base_url=self._base_url,
            timeout=httpx.Timeout(timeout),
            headers=self._default_headers(),
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
        return {
            "Authorization": f"Bearer {self._token}",
            "Notion-Version": self._version,
            "Content-Type": "application/json",
        }

    async def __aenter__(self) -> NotionAPI:
        """Async context manager entry."""
        return self

    async def __aexit__(self, *args: Any) -> None:
        """Async context manager exit."""
        await self.close()

    async def close(self) -> None:
        """Close the HTTP client."""
        await self._http.aclose()

    async def _request(
        self,
        method: str,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        json: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Make an HTTP request to the Notion API.

        Args:
            method: HTTP method.
            path: Request path (will be appended to base_url).
            params: Query parameters.
            json: JSON request body.

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

            if status_code == 400:
                from better_notion._api.errors import BadRequestError
                raise BadRequestError() from None
            elif status_code == 401:
                from better_notion._api.errors import UnauthorizedError
                raise UnauthorizedError() from None
            elif status_code == 403:
                from better_notion._api.errors import ForbiddenError
                raise ForbiddenError() from None
            elif status_code == 404:
                from better_notion._api.errors import NotFoundError
                raise NotFoundError() from None
            elif status_code == 409:
                from better_notion._api.errors import ConflictError
                raise ConflictError() from None
            elif status_code == 429:
                from better_notion._api.errors import RateLimitedError
                retry_after = e.response.headers.get("Retry-After")
                raise RateLimitedError(
                    retry_after=int(retry_after) if retry_after else None
                ) from None
            elif status_code >= 500:
                from better_notion._api.errors import InternalServerError
                raise InternalServerError() from None
            else:
                raise NotionAPIError(f"HTTP {status_code}: {e.response.text}") from None

        except httpx.RequestError as e:
            from better_notion._api.errors import NetworkError
            raise NetworkError(f"Network error: {e}") from e
