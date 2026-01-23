# API Surface Design

This document defines the public API surface that developers will interact with, including method signatures, return types, and conventions.

## Client Initialization

### NotionClient (High-Level)

```python
class NotionClient:
    """
    High-level client for Notion API with caching and abstractions.
    """

    def __init__(
        self,
        auth: str,
        *,
        max_retries: int = 3,
        retry_backoff: bool = True,
        rate_limit_strategy: Literal["wait", "fail"] = "wait",
        log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = "WARNING"
    ) -> None:
        """
        Initialize the Notion client.

        Args:
            auth: Integration token or OAuth access token
            max_retries: Maximum number of retries for failed requests
            retry_backoff: Enable exponential backoff for retries
            rate_limit_strategy: How to handle rate limiting ("wait" or "fail")
            log_level: Logging level for client
        """

    # Access to managers
    @property
    def pages(self) -> PageManager:
        """Page operations manager."""

    @property
    def databases(self) -> DatabaseManager:
        """Database operations manager."""

    @property
    def blocks(self) -> BlockManager:
        """Block operations manager."""

    @property
    def users(self) -> UserManager:
        """User operations manager."""

    @property
    def search(self) -> SearchManager:
        """Search operations manager."""

    @property
    def comments(self) -> CommentManager:
        """Comment operations manager."""

    @property
    def files(self) -> FileManager:
        """File operations manager."""

    @property
    def workspace(self) -> Workspace:
        """Workspace information and operations."""

    # Access to low-level API
    @property
    def _api(self) -> NotionAPI:
        """Low-level API access (escape hatch)."""
```

### NotionAPI (Low-Level)

```python
class NotionAPI:
    """
    Low-level API client with direct mapping to Notion endpoints.

    Use this when you need precise control or access to new features
    not yet available in the high-level client.
    """

    def __init__(
        self,
        auth: str,
        *,
        timeout: int = 30,
        max_retries: int = 3
    ) -> None:
        """
        Initialize the API client.

        Args:
            auth: Integration token or OAuth access token
            timeout: Request timeout in seconds
            max_retries: Maximum number of retries
        """

    # Endpoint managers
    @property
    def blocks(self) -> BlocksEndpoint:
        """Blocks API endpoints."""

    @property
    def pages(self) -> PagesEndpoint:
        """Pages API endpoints."""

    @property
    def databases(self) -> DatabasesEndpoint:
        """Databases API endpoints."""

    @property
    def users(self) -> UsersEndpoint:
        """Users API endpoints."""

    @property
    def search(self) -> SearchEndpoint:
        """Search API endpoints."""
```

## Pages Manager

```python
class PageManager:
    """Manager for page operations."""

    # CRUD Operations
    async def get(self, page_id: str) -> Page:
        """
        Retrieve a page by ID.

        Args:
            page_id: Page UUID

        Returns:
            Page object

        Raises:
            PageNotFound: Page doesn't exist
            PermissionError: No access to page
        """

    async def create(
        self,
        parent: Database | Page,
        *,
        title: str | None = None,
        properties: dict[str, Any] | None = None,
        content: list[Block] | None = None,
        icon: str | None = None,
        cover: str | None = None
    ) -> Page:
        """
        Create a new page.

        Args:
            parent: Parent database or page
            title: Page title (maps to title property)
            properties: Additional properties
            content: Initial block content
            icon: Page icon (emoji or URL)
            cover: Page cover image URL

        Returns:
            Created Page object
        """

    async def update(
        self,
        page: Page | str,
        *,
        title: str | None = None,
        properties: dict[str, Any] | None = None,
        icon: str | None = None,
        cover: str | None = None,
        archived: bool | None = None
    ) -> Page:
        """
        Update a page.

        Args:
            page: Page object or ID
            title: New title
            properties: Properties to update
            icon: New icon
            cover: New cover
            archived: Archive status

        Returns:
            Updated Page object
        """

    async def archive(self, page: Page | str) -> None:
        """Archive a page."""

    async def restore(self, page: Page | str) -> None:
        """Restore an archived page."""

    async def move(
        self,
        page: Page | str,
        new_parent: Database | Page,
        *,
        position: str | None = None
    ) -> Page:
        """
        Move page to new parent.

        Args:
            page: Page to move
            new_parent: New parent database or page
            position: Position (e.g., "after:block_id")
        """

    # List Operations
    async def all(self) -> AsyncIterator[Page]:
        """
        Iterate over all pages in workspace.

        Yields:
            Page objects
        """

    async def filter(
        self,
        *,
        type: Literal["page", "database"] | None = None,
        archived: bool | None = None
    ) -> AsyncIterator[Page]:
        """
        Filter pages.

        Args:
            type: Filter by object type
            archived: Filter by archived status

        Yields:
            Page objects
        """

    # Find Operations
    async def find_by_title(
        self,
        title: str,
        *,
        exact: bool = True,
        case_sensitive: bool = False
    ) -> Page | None:
        """
        Find page by title.

        Args:
            title: Title to search for
            exact: Require exact match (vs substring)
            case_sensitive: Match case

        Returns:
            Page if found, None otherwise
        """

    # Bulk Operations
    async def create_bulk(
        self,
        parent: Database,
        data: list[dict[str, Any]]
    ) -> list[Page]:
        """
        Create multiple pages.

        Args:
            parent: Parent database
            data: List of page data dictionaries

        Returns:
            List of created Page objects
        """

    async def update_bulk(
        self,
        pages: list[Page | str],
        *,
        properties: dict[str, Any]
    ) -> list[Page]:
        """
        Update multiple pages with same properties.

        Args:
            pages: List of pages or IDs
            properties: Properties to update on all pages

        Returns:
            List of updated Page objects
        """

    async def archive_bulk(self, pages: list[Page | str]) -> None:
        """Archive multiple pages."""

    async def move_bulk(
        self,
        pages: list[Page | str],
        new_parent: Database,
        *,
        position: str | None = None
    ) -> list[Page]:
        """Move multiple pages to new parent."""

    # Cache
    @property
    def cache(self) -> PageCache:
        """Page cache for instant lookups."""
```

## Page Object

```python
class Page(BaseEntity):
    """
    Represents a Notion page.

    Attributes:
        id: Page UUID
        title: Page title (if title property exists)
        url: Public URL
        icon: Page icon (emoji or URL)
        cover: Page cover image URL
        created_time: Creation timestamp
        last_edited_time: Last edit timestamp
        archived: Archive status
        properties: All properties dict
        parent: Parent object (cached)
    """

    # Property shortcuts
    @property
    def title(self) -> str | None:
        """Get page title from title property."""

    @property
    def url(self) -> str:
        """Get public Notion URL."""

    @property
    def icon(self) -> str | None:
        """Get page icon."""

    @property
    def cover(self) -> str | None:
        """Get page cover image."""

    # Hierarchical navigation
    async def parent(self) -> Database | Page | None:
        """Get parent object (fetches if not cached)."""

    @property
    def parent_cached(self) -> Database | Page | None:
        """Get parent object from cache (no fetch)."""

    async def children(self) -> AsyncIterator[Block]:
        """Iterate over child blocks."""

    async def ancestors(self) -> AsyncIterator[Database | Page]:
        """Walk up the hierarchy to root."""

    async def descendants(self) -> AsyncIterator[Block]:
        """Walk down the hierarchy (all descendant blocks)."""

    async def root(self) -> Database | Page:
        """Get root ancestor (workspace or top-level page)."""

    # Operations
    async def duplicate(
        self,
        parent: Database | Page,
        *,
        title: str | None = None,
        include_children: bool = True
    ) -> Page:
        """
        Duplicate this page.

        Args:
            parent: New parent
            title: New title (defaults to "Copy of {title}")
            include_children: Include all child blocks
        """

    async def move(
        self,
        new_parent: Database | Page,
        *,
        position: str | None = None
    ) -> Page:
        """Move to new parent."""

    async def archive(self) -> None:
        """Archive this page."""

    async def restore(self) -> None:
        """Restore from archive."""

    # Property helpers
    def get_property(
        self,
        name: str,
        default: Any = None
    ) -> Any:
        """
        Get property value by name.

        Performs case-insensitive lookup.
        """

    def find_property(self, name: str) -> Property | None:
        """
        Find property by name (case-insensitive, fuzzy match).
        """
```

## Databases Manager

```python
class DatabaseManager:
    """Manager for database operations."""

    # CRUD Operations
    async def get(self, database_id: str) -> Database:
        """Retrieve a database by ID."""

    async def create(
        self,
        parent: Page,
        *,
        title: str,
        properties: dict[str, PropertyConfig],
        description: str | None = None
    ) -> Database:
        """Create a new database."""

    async def update(
        self,
        database: Database,
        *,
        title: str | None = None,
        properties: dict[str, PropertyConfig] | None = None
    ) -> Database:
        """Update database."""

    async def delete(self, database: Database) -> None:
        """Delete a database."""

    # List Operations
    async def all(self) -> AsyncIterator[Database]:
        """Iterate over all databases."""

    # Find Operations
    async def find_by_title(
        self,
        title: str,
        *,
        exact: bool = True
    ) -> Database | None:
        """Find database by title."""

    # Cache
    @property
    def cache(self) -> DatabaseCache:
        """Database cache."""
```

## Database Object

```python
class Database(BaseEntity):
    """
    Represents a Notion database.

    Attributes:
        id: Database UUID
        title: Database title
        description: Optional description
        properties: Property schema dict
    """

    # Query operations
    async def query(
        self,
        **filters: Any
    ) -> AsyncIterator[Page]:
        """
        Query database pages.

        Simple filtering:
            await database.query(status="Done")

        Complex filtering:
            await database.query().filter(
                status="In Progress",
                priority__gte=5
            )

        Returns:
            Async iterator over Page objects
        """

    async def recent(self, days: int = 7) -> list[Page]:
        """Get pages modified in last N days."""

    async def filter_by(
        self,
        property_name: str,
        value: Any
    ) -> list[Page]:
        """Filter pages by property value."""

    async def filter_multiple(
        self,
        **properties: Any
    ) -> list[Page]:
        """Filter by multiple properties."""

    # Pages in database
    async def pages(self) -> AsyncIterator[Page]:
        """Iterate over all pages in database."""

    async def get_page_by_title(
        self,
        title: str,
        *,
        exact: bool = True
    ) -> Page | None:
        """Find page by title in this database."""

    # Property schema
    def get_property(self, name: str) -> PropertyConfig | None:
        """Get property schema by name."""

    def has_property(self, name: str) -> bool:
        """Check if property exists."""

    def get_property_type(self, name: str) -> str | None:
        """Get property type."""

    @property
    def property_names(self) -> list[str]:
        """List all property names."""
```

## Blocks Manager

```python
class BlockManager:
    """Manager for block operations."""

    # CRUD Operations
    async def get(self, block_id: str) -> Block:
        """Retrieve a block."""

    async def update(
        self,
        block: Block,
        **changes: Any
    ) -> Block:
        """Update block."""

    async def delete(self, block: Block) -> None:
        """Delete a block."""

    # Children operations
    async def children(
        self,
        block: Block | str
    ) -> AsyncIterator[Block]:
        """Iterate over block children."""

    async def append(
        self,
        block: Block | str,
        children: list[Block]
    ) -> list[Block]:
        """Append children to block."""

    async def append_children(
        self,
        block: Block | str,
        children: list[Block]
    ) -> list[Block]:
        """Append children (alias)."""

    # Bulk operations
    async def delete_bulk(self, blocks: list[Block]) -> None:
        """Delete multiple blocks."""

    # Cache
    @property
    def cache(self) -> BlockCache:
        """Block cache."""
```

## Block Object

```python
class Block(BaseEntity):
    """
    Represents a content block.

    Attributes:
        id: Block UUID
        type: Block type (paragraph, heading_1, etc.)
        content: Type-specific content
        has_children: Whether block has children
    """

    # Type checking
    @property
    def is_paragraph(self) -> bool:
        """Check if paragraph block."""

    @property
    def is_heading(self) -> bool:
        """Check if heading block."""

    @property
    def is_code(self) -> bool:
        """Check if code block."""

    @property
    def is_list(self) -> bool:
        """Check if list item block."""

    # Hierarchical navigation
    async def parent(self) -> Page | Block | None:
        """Get parent object."""

    @property
    def parent_cached(self) -> Page | Block | None:
        """Get parent from cache."""

    async def children(self) -> AsyncIterator[Block]:
        """Iterate over children."""

    async def descendants(self) -> AsyncIterator[Block]:
        """Walk all descendant blocks."""

    # Operations
    async def append_children(
        self,
        blocks: list[Block]
    ) -> list[Block]:
        """Append children blocks."""

    async def clear_children(self) -> None:
        """Delete all children."""

    async def move(
        self,
        new_parent: Page | Block,
        *,
        position: str | None = None
    ) -> Block:
        """Move to new parent."""

    # Type-specific shortcuts
    @property
    def text(self) -> str | None:
        """Get text content (for text-based blocks)."""

    @property
    def level(self) -> int | None:
        """Get heading level (for heading blocks)."""

    @property
    def code(self) -> str | None:
        """Get code content (for code blocks)."""

    @property
    def language(self) -> str | None:
        """Get code language (for code blocks)."""

    # Static factory methods
    @staticmethod
    def paragraph(text: str) -> Block:
        """Create paragraph block."""

    @staticmethod
    def heading(text: str, level: int = 1) -> Block:
        """Create heading block."""

    @staticmethod
    def code(code: str, language: str = "python") -> Block:
        """Create code block."""

    @staticmethod
    def bullet_item(text: str) -> Block:
        """Create bullet list item."""

    @staticmethod
    def numbered_item(text: str) -> Block:
        """Create numbered list item."""
```

## Users Manager

```python
class UserManager:
    """Manager for user operations."""

    # Retrieve operations
    async def me(self) -> User:
        """Get current bot user."""

    async def get(self, user_id: str) -> User:
        """Get user by ID."""

    async def list(
        self,
        *,
        page_size: int = 100
    ) -> AsyncIterator[User]:
        """List all users."""

    # Find operations
    async def find_by_email(self, email: str) -> User | None:
        """Find user by email."""

    async def find_by_name(
        self,
        name: str,
        *,
        exact: bool = True
    ) -> User | None:
        """Find user by name."""

    # Cache management
    async def populate_cache(self) -> None:
        """Load all users into cache."""

    @property
    def cache(self) -> UserCache:
        """User cache for instant lookups."""
```

## User Object

```python
class User(BaseEntity):
    """
    Represents a Notion user.

    Attributes:
        id: User UUID
        type: User type ("person" or "bot")
        name: Display name
        email: Email (for persons)
        avatar_url: Avatar image URL
    """

    @property
    def is_person(self) -> bool:
        """Check if person user."""

    @property
    def is_bot(self) -> bool:
        """Check if bot user."""

    @property
    def email(self) -> str | None:
        """Get email (for persons)."""

    @property
    def display_name(self) -> str:
        """Get display name with fallbacks."""
```

## Search Manager

```python
class SearchManager:
    """Manager for search operations."""

    async def query(
        self,
        query: str,
        *,
        filter: dict[str, Any] | None = None,
        sort: dict[str, Any] | None = None
    ) -> AsyncIterator[Page | Database]:
        """
        Search by query text.

        Args:
            query: Search query
            filter: Filter object
            sort: Sort object

        Yields:
            Page or Database objects
        """

    async def pages(
        self,
        query: str
    ) -> AsyncIterator[Page]:
        """Search pages only."""

    async def databases(
        self,
        query: str
    ) -> AsyncIterator[Database]:
        """Search databases only."""

    def search_cache(
        self,
        query: str,
        *,
        exact: bool = False
    ) -> list[Page | Database]:
        """Search within cached data."""

    async def find_pages_by_title(
        self,
        title: str,
        *,
        exact: bool = True
    ) -> list[Page]:
        """Find pages by title."""

    async def find_databases_by_title(
        self,
        title: str,
        *,
        exact: bool = True
    ) -> list[Database]:
        """Find databases by title."""
```

## Workspace

```python
class Workspace:
    """
    Represents a Notion workspace.

    Attributes:
        id: Workspace ID
        name: Workspace name
        icon: Workspace icon
    """

    # User directory
    async def refresh_users(self) -> None:
        """Refresh user cache."""

    @property
    def users(self) -> list[User]:
        """Get all users from cache."""

    def find_user(
        self,
        *,
        email: str | None = None,
        name: str | None = None
    ) -> User | None:
        """Find user by email or name in cache."""

    # Statistics
    @property
    def statistics(self) -> WorkspaceStatistics:
        """Get workspace statistics."""

    # Resources
    async def databases(self) -> AsyncIterator[Database]:
        """Iterate over all databases."""

    async def pages(self) -> AsyncIterator[Page]:
        """Iterate over all pages."""
```

## Async Iterator Interface

```python
class QueryIterator:
    """
    Async iterator for query results with automatic pagination.

    Usage:
        # Iterate
        async for page in database.query():
            process(page)

        # With limit
        async for page in database.query().limit(10):
            process(page)

        # Collect all
        pages = await database.query().collect()
    """

    async def __aiter__(self) -> AsyncIterator:
        """Async iteration."""

    def limit(self, n: int) -> QueryIterator:
        """Limit results to n items."""

    def sort(
        self,
        property: str,
        direction: Literal["ascending", "descending"]
    ) -> QueryIterator:
        """Sort results."""

    async def collect(self) -> list:
        """Collect all results into list."""

    async def first(self) -> Any | None:
        """Get first result or None."""
```

## Cache Interface

```python
class Cache(Generic[T]):
    """
    Generic cache for entity lookups.

    Args:
        T: Entity type (Page, Database, User, etc.)
    """

    def get(self, id: str) -> T | None:
        """Get entity from cache."""

    def get_all(self) -> list[T]:
        """Get all cached entities."""

    def set(self, id: str, entity: T) -> None:
        """Set entity in cache."""

    def invalidate(self, id: str) -> None:
        """Invalidate cached entity."""

    def clear(self) -> None:
        """Clear all cache."""

    def __contains__(self, id: str) -> bool:
        """Check if entity is cached."""

    def __len__(self) -> int:
        """Get cache size."""
```

## Exceptions

```python
# Base exception
class NotionError(Exception):
    """Base exception for Notion SDK."""

# Not found errors
class NotFoundError(NotionError):
    """Resource not found."""

class PageNotFound(NotFoundError):
    """Page not found."""

class DatabaseNotFound(NotFoundError):
    """Database not found."""

class BlockNotFound(NotFoundError):
    """Block not found."""

class UserNotFound(NotFoundError):
    """User not found."""

# Permission errors
class PermissionError(NotionError):
    """Insufficient permissions."""

# Validation errors
class ValidationError(NotionError):
    """Invalid data provided."""

# Rate limiting
class RateLimited(NotionError):
    """Rate limit exceeded."""

# API errors
class APIError(NotionError):
    """Generic API error."""

    @property
    def status_code(self) -> int:
        """HTTP status code."""

    @property
    def response(self) -> dict:
        """API response body."""
```

## Type Aliases

```python
# Common type aliases
PageID = str
DatabaseID = str
BlockID = str
UserID = str
PropertyID = str

# Property types
PropertyValue = str | int | float | bool | date | User | list[User]
Properties = dict[str, PropertyValue]

# Object types
MaybePage = Page | None
MaybeDatabase = Database | None

# Iterators
PageIterator = AsyncIterator[Page]
DatabaseIterator = AsyncIterator[Database]
BlockIterator = AsyncIterator[Block]
UserIterator = AsyncIterator[User]
```

## Conventions

### Method Naming

- **get**: Retrieve single resource by ID
- **find**: Search for resource by attribute (may return None)
- **list** / **all**: Iterate over all resources
- **filter**: Iterate with filtering
- **create**: Create new resource
- **update**: Update existing resource
- **delete** / **archive**: Remove resource

### Return Types

- Single resources: Return the object (not Optional)
  - Raises exception if not found
- Find operations: Return Optional[T]
- List operations: Return AsyncIterator[T]
- Bulk operations: Return list[T]

### Async Pattern

All I/O operations are async:

```python
async def get(self, id: str) -> Resource:
    """Network operation = async"""

@property
def cache(self) -> Cache:
    """Cache access = sync (no network)"""
```

### Type Hints

Every public method has full type hints:

```python
async def method(
    self,
    required: str,
    optional: str | None = None,
    *args: Any,
    **kwargs: Any
) -> ReturnType:
    ...
```
