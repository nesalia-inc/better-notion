# Entity-Oriented Architecture

Philosophy and patterns for entity-centric SDK design without Managers/Services.

## Overview

This SDK uses an **entity-oriented architecture** where entities are responsible for their own lifecycle and operations. No intermediate Managers or Services - entities know how to create, load, update, and delete themselves.

### Philosophy

**Not This ❌** (Java/Enterprise style with Managers):
```python
# Managers add unnecessary indirection
page = await client.pages.get(page_id)
await client.pages.create(parent=db, title="New")
await client.blocks.create_text(parent=page, text="Hello")
```

**This ✅** (Entity-centric):
```python
# Entities are autonomous
page = await Page.get(page_id, client=client)
await Page.create(parent=db, title="New", client=client)
await Paragraph.create(parent=page, text="Hello", client=client)
```

## Core Principles

### 1. Entities Are Autonomous

Each entity class knows how to:
- Load itself from Notion (`get()`)
- Create new instances (`create()`)
- Update itself (`update()`)
- Delete itself (`delete()`)

```python
class Page(BaseEntity):
    """A page that manages itself."""

    @classmethod
    async def get(cls, id: str, client: NotionClient) -> "Page":
        """Load this page from Notion."""
        data = await client._api._request("GET", f"/pages/{id}")
        return cls(client, data)

    @classmethod
    async def create(
        cls,
        parent: Database | Page,
        title: str,
        client: NotionClient,
        **properties
    ) -> "Page":
        """Create a new page."""
        data = await client._api.pages.create(
            parent=parent.id,
            title=title,
            properties=properties
        )
        return cls(client, data)

    async def update(self, client: NotionClient, **kwargs) -> None:
        """Update this page."""
        data = await client._api._request(
            "PATCH",
            f"/pages/{self.id}",
            json=kwargs
        )
        self._data.update(data)

    async def delete(self, client: NotionClient) -> None:
        """Delete this page."""
        await client._api._request("DELETE", f"/pages/{self.id}")
```

### 2. Specialized Classes, Not Generic Ones

Instead of generic `Block` with type checks, use specialized classes:

**Not This ❌**:
```python
# Generic block with type flags
if block.is_code:
    print(block.code)  # type: ignore
    print(block.language)  # type: ignore
```

**This ✅**:
```python
# Specialized classes
if isinstance(block, Code):
    print(block.code)  # ✅ Type-safe
    print(block.language)  # ✅
```

### 3. Factory Methods on Classes, Not Base Class

Each specialized class has its own `create()` method:

**Not This ❌**:
```python
# Factory on base Block class
todo = await Block.create_todo(parent=page, text="Fix", client=client)
code = await Block.create_code(parent=page, code="x", client=client)
```

**This ✅**:
```python
# Each class creates itself
todo = await Todo.create(parent=page, text="Fix", client=client)
code = await Code.create(parent=page, code="x", client=client)
```

### 4. Client is Minimal

The `NotionClient` is just a container for:
- Low-level API access
- Shared caches
- Search functionality

```python
class NotionClient:
    """Minimal client - entities manage themselves."""

    def __init__(self, auth: str):
        self._api = NotionAPI(auth=auth)
        self._user_cache = Cache[User]()
        self._database_cache = Cache[Database]()

    # No PageManager, DatabaseManager, etc.
    # Entities handle everything
```

## Entity Classes

### BaseEntity

All entities inherit from `BaseEntity`:

```python
class BaseEntity(ABC):
    """Base class for all Notion entities."""

    def __init__(self, client: NotionClient, data: dict[str, Any]):
        self._client = client
        self._data = data
        self._cache: dict[str, Any] = {}

    @property
    def id(self) -> str:
        return self._data["id"]

    @property
    def object(self) -> str:
        return self._data["object"]

    def _cache_set(self, key: str, value: Any) -> None:
        self._cache[key] = value

    def _cache_get(self, key: str) -> Any | None:
        return self._cache.get(key)

    def _cache_clear(self) -> None:
        self._cache.clear()

    async def parent(self) -> Database | Page | Block | None:
        """Get parent - implemented by subclasses."""
        raise NotImplementedError

    async def children(self) -> AsyncIterator[Block]:
        """Get children - implemented by subclasses."""
        raise NotImplementedError

    async def ancestors(self) -> AsyncIterator[Database | Page | Block]:
        """Walk up hierarchy to root."""
        current = self
        while True:
            parent = await current.parent()
            if parent is None:
                break
            yield parent
            current = parent

    async def descendants(self, max_depth: int | None = None) -> AsyncIterator[Block]:
        """Walk down hierarchy recursively."""
        visited = set()

        async def traverse(entity: BaseEntity, depth: int):
            if max_depth and depth > max_depth:
                return
            if entity.id in visited:
                return
            visited.add(entity.id)
            if entity.object == "block":
                yield entity
            async for child in entity.children():
                async for desc in traverse(child, depth + 1):
                    yield desc

        async for descendant in traverse(self, 0):
            yield descendant
```

### Core Entity Classes

#### Page

```python
class Page(BaseEntity):
    """A Notion page."""

    @classmethod
    async def get(cls, id: str, client: NotionClient) -> "Page":
        """Load page from Notion.

        Example:
            >>> page = await Page.get(page_id, client=client)
            >>> print(page.title)
        """
        cached = client._page_cache.get(id)
        if cached:
            return cached

        data = await client._api._request("GET", f"/pages/{id}")
        page = cls(client, data)
        client._page_cache.set(id, page)

        return page

    @classmethod
    async def create(
        cls,
        parent: Database | Page,
        title: str,
        client: NotionClient,
        **properties
    ) -> "Page":
        """Create new page.

        Example:
            >>> # In database
            >>> page = await Page.create(
            ...     parent=database,
            ...     title="Task 1",
            ...     client=client,
            ...     status="Todo"
            ... )

            >>> # Child page
            >>> page = await Page.create(
            ...     parent=parent_page,
            ...     title="Subpage",
            ...     client=client
            ... )
        """
        if isinstance(parent, Database):
            data = await client._api.pages.create(
                parent=parent.id,
                title=title,
                properties=properties
            )
        else:
            data = await client._api.pages.create(
                parent=parent.id,
                title=title
            )

        return cls(client, data)

    @property
    def title(self) -> str:
        """Page title."""
        result = PropertyParser.get_title(self._data["properties"])
        return result or ""

    @property
    def url(self) -> str:
        """Public Notion URL."""
        return f"https://notion.so/{self.id.replace('-', '')}"

    async def parent(self) -> Database | Page | None:
        """Get parent."""
        cached = self._cache_get("parent")
        if cached:
            return cached

        parent_data = self._data.get("parent", {})

        if parent_data.get("type") == "database_id":
            db_id = parent_data["database_id"]
            data = await self._client._api._request("GET", f"/databases/{db_id}")
            parent = Database(self._client, data)
        elif parent_data.get("type") == "page_id":
            page_id = parent_data["page_id"]
            data = await self._client._api._request("GET", f"/pages/{page_id}")
            parent = Page(self._client, data)
        else:
            parent = None

        if parent:
            self._cache_set("parent", parent)

        return parent

    async def children(self) -> AsyncIterator[Block]:
        """Iterate child blocks."""
        async for block_data in self._fetch_children():
            yield Block.from_data(self._client, block_data)

    async def _fetch_children(self) -> AsyncIterator[dict]:
        """Fetch children from API (internal)."""
        from better_notion._api.utils import AsyncPaginatedIterator

        async def fetch_fn(cursor: str | None) -> dict:
            params = {}
            if cursor:
                params["start_cursor"] = cursor
            return await self._client._api._request(
                "GET",
                f"/blocks/{self.id}/children",
                params=params
            )

        iterator = AsyncPaginatedIterator(fetch_fn)
        async for block_data in iterator:
            yield block_data

    async def update(self, client: NotionClient, **kwargs) -> None:
        """Update page properties."""
        data = await client._api._request(
            "PATCH",
            f"/pages/{self.id}",
            json=kwargs
        )
        self._data.update(data)
        self._cache_clear()

    async def delete(self, client: NotionClient) -> None:
        """Delete page."""
        await client._api._request("DELETE", f"/pages/{self.id}")
```

#### Database

```python
class Database(BaseEntity):
    """A Notion database."""

    @classmethod
    async def get(cls, id: str, client: NotionClient) -> "Database":
        """Load database from Notion.

        Example:
            >>> db = await Database.get(db_id, client=client)
            >>> print(f"{db.title}: {len(db.schema)} properties")
        """
        cached = client._database_cache.get(id)
        if cached:
            return cached

        data = await client._api._request("GET", f"/databases/{id}")
        database = cls(client, data)
        client._database_cache.set(id, database)

        return database

    @classmethod
    async def create(
        cls,
        parent: Page,
        title: str,
        properties: dict[str, Any],
        client: NotionClient
    ) -> "Database":
        """Create new database.

        Example:
            >>> db = await Database.create(
            ...     parent=page,
            ...     title="Tasks",
            ...     properties={
            ...         "Name": {"type": "title"},
            ...         "Status": {
            ...             "type": "select",
            ...             "options": ["Todo", "Done"]
            ...         }
            ...     },
            ...     client=client
            ... )
        """
        data = await client._api.databases.create(
            parent=parent.id,
            title=title,
            properties=properties
        )
        return cls(client, data)

    def __init__(self, client: NotionClient, data: dict):
        super().__init__(client, data)
        self._schema = self._parse_schema()

    @property
    def title(self) -> str:
        """Database title."""
        title_array = self._data.get("title", [])
        if title_array and title_array[0].get("type") == "text":
            return title_array[0]["text"]["content"]
        return ""

    @property
    def schema(self) -> dict[str, dict[str, Any]]:
        """Property schema."""
        return self._schema

    def _parse_schema(self) -> dict[str, dict[str, Any]]:
        """Parse schema from API data."""
        schema = {}
        for name, prop_data in self._data.get("properties", {}).items():
            schema[name] = {
                "type": prop_data.get("type"),
                "id": prop_data.get("id")
            }
        return schema

    def query(self, client: NotionClient, **filters) -> DatabaseQuery:
        """Create query for this database.

        Example:
            >>> pages = await database.query(
            ...     client=client,
            ...     status="Done"
            ... ).collect()
        """
        return DatabaseQuery(
            api=client._api,
            database_id=self.id,
            schema=self._schema,
            initial_filters=filters
        )

    async def children(self) -> AsyncIterator[Page]:
        """Iterate pages in database."""
        async for page_data in self._query_api(client._api):
            yield Page(self._client, page_data)

    async def _query_api(self, api) -> AsyncIterator[dict]:
        """Query database API (internal)."""
        from better_notion._api.utils import AsyncPaginatedIterator

        async def fetch_fn(cursor: str | None) -> dict:
            body = {}
            if cursor:
                body["start_cursor"] = cursor
            return await api._request(
                "POST",
                f"/databases/{self.id}/query",
                json=body
            )

        iterator = AsyncPaginatedIterator(fetch_fn)
        async for page_data in iterator:
            yield page_data
```

#### User

```python
class User(BaseEntity):
    """A Notion user (person or bot)."""

    @classmethod
    async def get(cls, id: str, client: NotionClient) -> "User":
        """Load user from Notion.

        Example:
            >>> user = await User.get(user_id, client=client)
            >>> print(user.name)
        """
        cached = client._user_cache.get(id)
        if cached:
            return cached

        data = await client._api._request("GET", f"/users/{id}")
        user = cls(client, data)
        client._user_cache.set(id, user)

        return user

    @classmethod
    async def populate_cache(cls, client: NotionClient) -> None:
        """Load all users into cache.

        Example:
            >>> await User.populate_cache(client=client)
            >>> # Now all lookups are instant
            >>> user = client._user_cache.get(user_id)
        """
        client._user_cache.clear()
        async for user_data in client._api.users.list():
            user = User(client, user_data)
            client._user_cache.set(user.id, user)

    @classmethod
    def find_by_email(cls, email: str, client: NotionClient) -> "User | None":
        """Find user by email (searches cache).

        Example:
            >>> user = User.find_by_email("john@example.com", client=client)
        """
        for user in client._user_cache.get_all():
            if user.email == email:
                return user
        return None

    @property
    def name(self) -> str:
        """Display name."""
        return self._data.get("name", "")

    @property
    def email(self) -> str | None:
        """Email (for person users)."""
        if self._data.get("type") == "person":
            return self._data.get("person", {}).get("email")
        return None

    @property
    def is_person(self) -> bool:
        """Is this a person?"""
        return self._data.get("type") == "person"

    @property
    def is_bot(self) -> bool:
        """Is this a bot?"""
        return self._data.get("type") == "bot"
```

## Specialized Block Classes

### Base Block Class

```python
class Block(BaseEntity, ABC):
    """Base class for all block types."""

    @classmethod
    def from_data(cls, client: NotionClient, data: dict) -> Block:
        """Factory to create correct block type from API data.

        Example:
            >>> block = Block.from_data(client, block_data)
            >>> # Returns Paragraph, Code, Todo, etc.
        """
        block_type = data.get("type")

        dispatch = {
            "paragraph": Paragraph,
            "code": Code,
            "heading_1": Heading,
            "heading_2": Heading,
            "heading_3": Heading,
            "image": Image,
            "to_do": Todo,
            "bulleted_list_item": BulletedListItem,
            "numbered_list_item": NumberedListItem,
            "callout": Callout,
            "quote": Quote,
            "toggle": Toggle,
            "divider": Divider,
        }

        block_class = dispatch.get(block_type, GenericBlock)
        return block_class(client, data)

    @classmethod
    async def get(cls, id: str, client: NotionClient) -> Block:
        """Load block from Notion.

        Example:
            >>> block = await Block.get(block_id, client=client)
        """
        data = await client._api._request("GET", f"/blocks/{id}")
        return cls.from_data(client, data)

    @property
    def type(self) -> str:
        """Block type string."""
        return self._data.get("type", "")

    @property
    def has_children(self) -> bool:
        """Does this block have children?"""
        return self._data.get("has_children", False)

    async def children(self) -> AsyncIterator[Block]:
        """Iterate child blocks."""
        from better_notion._api.utils import AsyncPaginatedIterator

        async def fetch_fn(cursor: str | None) -> dict:
            params = {}
            if cursor:
                params["start_cursor"] = cursor
            return await self._client._api._request(
                "GET",
                f"/blocks/{self.id}/children",
                params=params
            )

        iterator = AsyncPaginatedIterator(fetch_fn)
        async for block_data in iterator:
            yield Block.from_data(self._client, block_data)

    def _extract_plain_text(self, rich_text_array: list[dict]) -> str:
        """Extract plain text from rich text array."""
        parts = []
        for text_obj in rich_text_array:
            if text_obj.get("type") == "text":
                parts.append(text_obj["text"].get("content", ""))
        return "".join(parts)
```

### Specialized Block Implementations

See [Block Specialized Classes](../models/blocks-specialized.md) for complete implementation of:
- `Paragraph`
- `Heading` (H1/H2/H3)
- `Code`
- `Todo`
- `BulletedListItem`
- `NumberedListItem`
- `Image`
- `Callout`
- `Quote`
- `Toggle`
- `Divider`

Each class has:
- Type-specific `create()` method
- Type-specific properties
- Type-specific methods

## NotionClient - Minimal Container

```python
class NotionClient:
    """Minimal Notion SDK client.

    The client is just a container for:
    - Low-level API access
    - Shared caches
    - Search functionality

    All entity operations are handled by the entities themselves.
    """

    def __init__(self, auth: str):
        self._api = NotionAPI(auth=auth)

        # Shared caches (accessed by entities)
        self._user_cache = Cache[User]()
        self._database_cache = Cache[Database]()
        self._page_cache = Cache[Page]()
        # No cache for Block (too many)

    @property
    def api(self) -> NotionAPI:
        """Direct API access if needed."""
        return self._api

    async def search(
        self,
        query: str = "",
        filter: dict | None = None
    ) -> list[Page | Database]:
        """Search for pages and databases.

        Example:
            >>> results = await client.search(query="Tasks")
            >>> for item in results:
            ...     if isinstance(item, Page):
            ...         print(f"Page: {item.title}")
        """
        results = []

        async for result in self._api.search.query(query=query, filter=filter):
            obj_type = result.get("object")
            if obj_type == "page":
                results.append(Page(self, result))
            elif obj_type == "database":
                results.append(Database(self, result))

        return results
```

## Usage Examples

### Creating Content

```python
# Initialize
client = NotionClient(auth=os.getenv("NOTION_KEY"))

# Get or create parent
page = await Page.get(page_id, client=client)

# Create content - each class manages itself
para = await Paragraph.create(parent=page, text="Introduction", client=client)
h1 = await Heading.create(parent=page, text="Chapter 1", level=1, client=client)
code = await Code.create(
    parent=page,
    code="print('Hello world')",
    language="python",
    client=client
)
todo = await Todo.create(
    parent=page,
    text="Review documentation",
    checked=False,
    client=client
)
```

### Working with Specific Types

```python
# Load page
page = await Page.get(page_id, client=client)

# Iterate with type-specific methods
async for block in page.children:
    if isinstance(block, Todo):
        if not block.checked:
            print(f"Todo: {block.text}")
            await block.check(client=client)

    elif isinstance(block, Code):
        print(f"Code in {block.language}:")
        print(f"  {block.code[:50]}...")

    elif isinstance(block, Heading):
        indent = "#" * block.level
        print(f"{indent} {block.text}")

    elif isinstance(block, Paragraph):
        print(block.text)
```

### Querying Databases

```python
# Get database
db = await Database.get(db_id, client=client)

# Query - database manages its own queries
pages = await db.query(
    client=client,
    status="In Progress",
    priority__gte=5
).sort("Due Date", "ascending").limit(10).collect()

# Process results
for page in pages:
    print(f"{page.title}")

    # Get creator from cache (instant!)
    creator = client._user_cache.get(page.created_by)
    if creator:
        print(f"  Created by: {creator.name}")
```

### Navigation

```python
# Walk up
async for ancestor in page.ancestors():
    if isinstance(ancestor, Database):
        print(f"In database: {ancestor.title}")
    elif isinstance(ancestor, Page):
        print(f"Child of: {ancestor.title}")

# Walk down
async for block in page.descendants():
    if isinstance(block, Code):
        analyze_code(block)
```

## Design Decisions

### Q1: Why no Managers?

**Decision**: Entities manage themselves

**Rationale**:
- ❌ Managers add unnecessary indirection
- ❌ `client.pages.get()` separates object from behavior
- ✅ `Page.get()` keeps object and behavior together
- ✅ More intuitive, less boilerplate

### Q2: Why specialized Block classes?

**Decision**: `Code`, `Todo`, `Paragraph` instead of generic `Block`

**Rationale**:
- ❌ Generic `Block` requires type checks everywhere
- ❌ `if block.is_code: print(block.code)` - not type-safe
- ✅ `isinstance(block, Code)` - type-safe
- ✅ Each class has type-specific methods
- ✅ Better IDE autocomplete

### Q3: Why `client` parameter in methods?

**Decision**: Pass `client` explicitly in mutating operations

**Rationale**:
- Entities need API access for updates
- Could store `self._client` reference
- Explicit is better than implicit
- Clear which operations need API access

```python
# Option A: Store client reference (chosen)
class Page:
    def __init__(self, client: NotionClient, data: dict):
        self._client = client

    async def delete(self, client: NotionClient) -> None:
        await client._api._request("DELETE", f"/pages/{self.id}")

# Option B: Use stored client
class Page:
    async def delete(self) -> None:
        await self._client._api._request("DELETE", f"/pages/{self.id}")
```

We use Option A for now, could switch to Option B.

### Q4: Cache location?

**Decision**: Cache in `NotionClient`, accessed by entities

**Rationale**:
- Shared cache across all entity operations
- Entities access via `client._user_cache`
- Clear ownership

```python
# In entity get() method
cached = client._user_cache.get(id)
if cached:
    return cached

# ... fetch from API ...

client._user_cache.set(id, entity)
```

## Benefits

1. **Intuitive**: `Page.get()` vs `client.pages.get()`
2. **Type-safe**: `isinstance(block, Code)` vs `block.is_code`
3. **Less indirection**: No manager layer
4. **Domain-centric**: Entities represent real Notion objects
5. **Extensible**: Easy to add methods to entities

## Related Documentation

- [Page Model](../models/page-model.md) - Page entity
- [Database Model](../models/database-model.md) - Database entity
- [User Model](../models/user-model.md) - User entity
- [Block Specialized Classes](../models/blocks-specialized.md) - Block types
- [BaseEntity](./base-entity.md) - Foundation class
