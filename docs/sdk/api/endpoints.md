# Endpoints Reference

Complete reference of all low-level API endpoints and their methods.

## Endpoint Structure

Each Notion API endpoint has a corresponding manager class with methods:

```python
class BlocksEndpoint:
    """Blocks API endpoint."""

    def __init__(self, api: NotionAPI):
        self._api = api

    # Methods correspond to API endpoints
    async def retrieve(self, block_id: str) -> dict:
        """GET /blocks/{block_id}"""

    async def children(self) -> BlockChildrenEndpoint:
        """Nested endpoint for children operations."""
```

## Blocks Endpoint

```python
class BlocksEndpoint(EndpointBase):
    """Blocks API operations.

    API Reference: https://developers.notion.com/reference/get-block
    """

    async def retrieve(
        self,
        block_id: str
    ) -> dict:
        """
        Retrieve a block.

        GET /blocks/{block_id}

        Args:
            block_id: Block UUID

        Returns:
            Block object as dict

        Raises:
            BlockNotFoundError: If block doesn't exist
        """
        return await self._api._request(
            "GET",
            f"/blocks/{block_id}"
        )

    @property
    def children(self) -> "BlockChildrenEndpoint":
        """Access children operations."""
        return BlockChildrenEndpoint(self._api)

    async def update(
        self,
        block_id: str,
        block: dict
    ) -> dict:
        """
        Update a block.

        PATCH /blocks/{block_id}

        Args:
            block_id: Block UUID
            block: Block object to update

        Returns:
            Updated block object as dict
        """
        return await self._api._request(
            "PATCH",
            f"/blocks/{block_id}",
            json=block
        )

    async def delete(
        self,
        block_id: str
    ) -> dict:
        """
        Delete a block.

        DELETE /blocks/{block_id}

        Args:
            block_id: Block UUID

        Returns:
            Archived block object as dict
        """
        return await self._api._request(
            "DELETE",
            f"/blocks/{block_id}"
        )


class BlockChildrenEndpoint(EndpointBase):
    """Block children operations."""

    async def list(
        self,
        block_id: str,
        *,
        start_cursor: str | None = None,
        page_size: int | None = None
    ) -> PaginatedResponse:
        """
        Retrieve block children.

        GET /blocks/{block_id}/children

        Args:
            block_id: Parent block UUID
            start_cursor: Pagination cursor
            page_size: Number of results (max: 100)

        Returns:
            PaginatedResponse with results
        """
        params = {}
        if start_cursor:
            params["start_cursor"] = start_cursor
        if page_size:
            params["page_size"] = page_size

        response = await self._api._request(
            "GET",
            f"/blocks/{block_id}/children",
            params=params
        )

        return PaginatedResponse(
            results=response.get("results", []),
            next_cursor=response.get("next_cursor"),
            has_more=response.get("has_more", False),
            api=self._api,
            request_fn=self.list,
            request_fn_kwargs={"block_id": block_id}
        )

    async def append(
        self,
        block_id: str,
        *,
        children: list[dict]
    ) -> dict:
        """
        Append block children.

        PATCH /blocks/{block_id}/children

        Args:
            block_id: Parent block UUID
            children: List of block objects

        Returns:
            Updated block object with children
        """
        return await self._api._request(
            "PATCH",
            f"/blocks/{block_id}/children",
            json={"children": children}
        )
```

## Pages Endpoint

```python
class PagesEndpoint(EndpointBase):
    """Pages API operations.

    API Reference: https://developers.notion.com/reference/get-page
    """

    async def retrieve(
        self,
        page_id: str
    ) -> dict:
        """
        Retrieve a page.

        GET /pages/{page_id}

        Args:
            page_id: Page UUID

        Returns:
            Page object as dict

        Raises:
            PageNotFoundError: If page doesn't exist
        """
        return await self._api._request(
            "GET",
            f"/pages/{page_id}"
        )

    async def create(
        self,
        *,
        parent: dict,
        properties: dict | None = None,
        children: list[dict] | None = None,
        icon: dict | None = None,
        cover: str | None = None
    ) -> dict:
        """
        Create a page.

        POST /pages

        Args:
            parent: Parent object (database or page)
            properties: Page properties
            children: Initial block children
            icon: Page icon (emoji or file)
            cover: Page cover image URL

        Returns:
            Created page object as dict
        """
        body = {"parent": parent}

        if properties:
            body["properties"] = properties
        if children:
            body["children"] = children
        if icon:
            body["icon"] = icon
        if cover:
            body["cover"] = cover

        return await self._api._request(
            "POST",
            "/pages",
            json=body
        )

    async def update(
        self,
        page_id: str,
        *,
        properties: dict | None = None,
        archived: bool | None = None,
        icon: dict | None = None,
        cover: str | None = None
    ) -> dict:
        """
        Update a page.

        PATCH /pages/{page_id}

        Args:
            page_id: Page UUID
            properties: Properties to update
            archived: Archive status
            icon: Page icon
            cover: Page cover URL

        Returns:
            Updated page object as dict
        """
        body = {}

        if properties:
            body["properties"] = properties
        if archived is not None:
            body["archived"] = archived
        if icon:
            body["icon"] = icon
        if cover:
            body["cover"] = cover

        return await self._api._request(
            "PATCH",
            f"/pages/{page_id}",
            json=body
        )

    async def retrieve_property_item(
        self,
        page_id: str,
        property_id: str
    ) -> dict:
        """
        Retrieve a page property item.

        GET /pages/{page_id}/properties/{property_id}

        Args:
            page_id: Page UUID
            property_id: Property UUID

        Returns:
            Property value object

        Raises:
            PropertyNotFoundError: If property doesn't exist
        """
        return await self._api._request(
            "GET",
            f"/pages/{page_id}/properties/{property_id}"
        )
```

## Databases Endpoint

```python
class DatabasesEndpoint(EndpointBase):
    """Databases API operations.

    API Reference: https://developers.notion.com/reference/get-database
    """

    async def retrieve(
        self,
        database_id: str
    ) -> dict:
        """
        Retrieve a database.

        GET /databases/{database_id}

        Args:
            database_id: Database UUID

        Returns:
            Database object as dict

        Raises:
            DatabaseNotFoundError: If database doesn't exist
        """
        return await self._api._request(
            "GET",
            f"/databases/{database_id}"
        )

    async def create(
        self,
        *,
        parent: dict,
        title: list[dict],
        properties: dict[str, dict]
    ) -> dict:
        """
        Create a database.

        POST /databases

        Args:
            parent: Parent page
            title: Database title (rich text)
            properties: Property schema

        Returns:
            Created database object as dict
        """
        body = {
            "parent": parent,
            "title": title,
            "properties": properties
        }

        return await self._api._request(
            "POST",
            "/databases",
            json=body
        )

    async def update(
        self,
        database_id: str,
        *,
        title: list[dict] | None = None,
        description: list[dict] | None = None,
        properties: dict[str, dict] | None = None
    ) -> dict:
        """
        Update a database.

        PATCH /databases/{database_id}

        Args:
            database_id: Database UUID
            title: Database title
            description: Database description
            properties: Property schema to update

        Returns:
            Updated database object as dict
        """
        body = {}

        if title:
            body["title"] = title
        if description:
            body["description"] = description
        if properties:
            body["properties"] = properties

        return await self._api._request(
            "PATCH",
            f"/databases/{database_id}",
            json=body
        )

    async def query(
        self,
        database_id: str,
        *,
        filter: dict | None = None,
        sort: list[dict] | None = None,
        start_cursor: str | None = None,
        page_size: int | None = None
    ) -> PaginatedResponse:
        """
        Query a database.

        POST /databases/{database_id}/query

        Args:
            database_id: Database UUID
            filter: Query filter object
            sort: Sort objects
            start_cursor: Pagination cursor
            page_size: Number of results (max: 100)

        Returns:
            PaginatedResponse with page objects
        """
        body = {}

        if filter:
            body["filter"] = filter
        if sort:
            body["sort"] = sort
        if start_cursor:
            body["start_cursor"] = start_cursor
        if page_size:
            body["page_size"] = page_size

        response = await self._api._request(
            "POST",
            f"/databases/{database_id}/query",
            json=body
        )

        return PaginatedResponse(
            results=response.get("results", []),
            next_cursor=response.get("next_cursor"),
            has_more=response.get("has_more", False),
            api=self._api,
            request_fn=self.query,
            request_fn_kwargs={"database_id": database_id}
        )
```

## Users Endpoint

```python
class UsersEndpoint(EndpointBase):
    """Users API operations.

    API Reference: https://developers.notion.com/reference/get-user
    """

    async def me(self) -> dict:
        """
        Retrieve your token's bot user.

        GET /users/me

        Returns:
            Bot user object as dict
        """
        return await self._api._request("GET", "/users/me")

    async def retrieve(
        self,
        user_id: str
    ) -> dict:
        """
        Retrieve a user.

        GET /users/{user_id}

        Args:
            user_id: User UUID

        Returns:
            User object as dict

        Raises:
            UserNotFoundError: If user doesn't exist
        """
        return await self._api._request(
            "GET",
            f"/users/{user_id}"
        )

    async def list(
        self,
        *,
        start_cursor: str | None = None,
        page_size: int | None = None
    ) -> PaginatedResponse:
        """
        List all users.

        GET /users

        Args:
            start_cursor: Pagination cursor
            page_size: Number of results (max: 100)

        Returns:
            PaginatedResponse with user objects
        """
        params = {}
        if start_cursor:
            params["start_cursor"] = start_cursor
        if page_size:
            params["page_size"] = page_size

        response = await self._api._request(
            "GET",
            "/users",
            params=params
        )

        return PaginatedResponse(
            results=response.get("results", []),
            next_cursor=response.get("next_cursor"),
            has_more=response.get("has_more", False),
            api=self._api,
            request_fn=self.list,
            request_fn_kwargs={}
        )
```

## Search Endpoint

```python
class SearchEndpoint(EndpointBase):
    """Search API operations.

    API Reference: https://developers.notion.com/reference/search
    """

    async def query(
        self,
        *,
        query: str | None = None,
        filter: dict | None = None,
        sort: dict | None = None,
        start_cursor: str | None = None,
        page_size: int | None = None
    ) -> PaginatedResponse:
        """
        Search by title.

        POST /search

        Args:
            query: Search query text
            filter: Filter by object type
            sort: Sort by timestamp
            start_cursor: Pagination cursor
            page_size: Number of results (max: 100)

        Returns:
            PaginatedResponse with page/database objects
        """
        body = {}

        if query:
            body["query"] = query
        if filter:
            body["filter"] = filter
        if sort:
            body["sort"] = sort
        if start_cursor:
            body["start_cursor"] = start_cursor
        if page_size:
            body["page_size"] = page_size

        response = await self._api._request(
            "POST",
            "/search",
            json=body
        )

        return PaginatedResponse(
            results=response.get("results", []),
            next_cursor=response.get("next_cursor"),
            has_more=response.get("has_more", False),
            api=self._api,
            request_fn=self.query,
            request_fn_kwargs={}
        )
```

## Comments Endpoint

```python
class CommentsEndpoint(EndpointBase):
    """Comments API operations.

    API Reference: https://developers.notion.com/reference/create-comment
    """

    async def create(
        self,
        *,
        parent: dict,
        discussion_id: str | None = None,
        rich_text: list[dict],
        attachments: list[dict] | None = None
    ) -> dict:
        """
        Create a comment.

        POST /comments

        Args:
            parent: Parent object (page or block)
            discussion_id: Discussion thread UUID (for replies)
            rich_text: Rich text content
            attachments: File attachments (max 3)

        Returns:
            Created comment object as dict
        """
        body = {
            "rich_text": rich_text
        }

        if parent:
            body["parent"] = parent
        if discussion_id:
            body["discussion_id"] = discussion_id
        if attachments:
            body["attachments"] = attachments

        return await self._api._request(
            "POST",
            "/comments",
            json=body
        )

    async def retrieve(
        self,
        comment_id: str
    ) -> dict:
        """
        Retrieve a comment.

        GET /comments/{comment_id}

        Args:
            comment_id: Comment UUID

        Returns:
            Comment object as dict
        """
        return await self._api._request(
            "GET",
            f"/comments/{comment_id}"
        )

    async def list(
        self,
        *,
        block_id: str | None = None,
        start_cursor: str | None = None,
        page_size: int | None = None
    ) -> PaginatedResponse:
        """
        List comments.

        GET /comments

        Args:
            block_id: Block UUID (page or block)
            start_cursor: Pagination cursor
            page_size: Number of results (max: 100)

        Returns:
            PaginatedResponse with comment objects
        """
        params = {}
        if block_id:
            params["block_id"] = block_id
        if start_cursor:
            params["start_cursor"] = start_cursor
        if page_size:
            params["page_size"] = page_size

        response = await self._api._request(
            "GET",
            "/comments",
            params=params
        )

        return PaginatedResponse(
            results=response.get("results", []),
            next_cursor=response.get("next_cursor"),
            has_more=response.get("has_more", False),
            api=self._api,
            request_fn=self.list,
            request_fn_kwargs={}
        )
```

## Base Classes

### EndpointBase

```python
class EndpointBase:
    """Base class for all endpoint managers."""

    def __init__(self, api: NotionAPI):
        """
        Initialize endpoint.

        Args:
            api: NotionAPI instance
        """
        self._api = api

    async def _request(
        self,
        method: str,
        path: str,
        **kwargs
    ) -> dict:
        """
        Make authenticated API request.

        Args:
            method: HTTP method
            path: Request path
            **kwargs: Additional request parameters

        Returns:
            Response dict

        Raises:
            HTTPError: For 4xx/5xx responses
            NetworkError: For network failures
        """
        return await self._api._request(method, path, **kwargs)
```

## Usage Examples

### Basic Usage

```python
api = NotionAPI(auth="secret_...")

# Get a page
page = await api.pages.retrieve(page_id)

# Query a database
results = await api.databases.query(
    database_id=database_id,
    filter={"property": "Status", "select": {"equals": "Done"}}
)
```

### With Pagination

```python
# Manual pagination
response = await api.databases.query(database_id)

results = list(response["results"])

while response["has_more"]:
    cursor = response["next_cursor"]
    response = await api.databases.query(
        database_id,
        start_cursor=cursor
    )
    results.extend(response["results"])
```

### With Error Handling

```python
try:
    page = await api.pages.retrieve(page_id)
except PageNotFoundError:
    print("Page not found")
except RateLimitedError as e:
    print(f"Rate limited, wait {e.retry_after}s")
except HTTPError as e:
    print(f"HTTP {e.status_code}: {e.message}")
```

## Related Documentation

- [Overview](./overview.md) - Low-level API overview
- [HTTP Client](./http-client.md) - HTTP layer
- [Error Handling](./error-handling.md) - Exception details
- [Pagination](./pagination.md) - Pagination helpers
- [Testing](./testing.md) - Testing endpoints

## Next Steps

1. Choose appropriate endpoint for your operation
2. Prepare request parameters according to API spec
3. Handle pagination for list/query operations
4. Implement proper error handling
