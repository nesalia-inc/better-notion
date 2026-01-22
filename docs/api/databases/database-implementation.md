# Database Implementation Guide

Technical implementation guide for building the Database and Data Source system in Better Notion SDK.

## Architecture Overview

### Class Hierarchy

```
NotionObject
├── Database (container)
│   ├── DataSourceReference[]
│   ├── PropertiesManager (for database-level props)
│   └── Methods
│       ├── get_data_sources()
│       ├── query_pages()
│       └── create_page()
│
└── DataSource (schema + pages)
    ├── PropertySchema[]
    ├── QueryBuilder
    └── Methods
        ├── query_pages()
        ├── create_page()
        ├── add_property()
        └── update_property()
```

## Core Database Class

```python
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List, Any, Dict
from uuid import UUID
from enum import Enum

class DatabaseType(str, Enum):
    """Database display types."""
    TABLE = "table"
    BOARD = "board"
    LIST = "list"
    TIMELINE = "timeline"
    CALENDAR = "calendar"
    GALLERY = "gallery"

@dataclass
class DataSourceReference:
    """Lightweight reference to a data source."""
    id: UUID
    name: str

    @classmethod
    def from_dict(cls, data: dict) -> "DataSourceReference":
        """Parse from API response."""
        return cls(
            id=UUID(data.get("id")),
            name=data.get("name")
        )

@dataclass
class Database:
    """Notion database object (container)."""
    object: str = "database"
    id: UUID = None
    data_sources: List[DataSourceReference] = field(default_factory=list)
    created_time: Optional[datetime] = None
    last_edited_time: Optional[datetime] = None
    created_by: Optional[Any] = None  # PartialUser
    last_edited_by: Optional[Any] = None  # PartialUser
    title: List[Any] = field(default_factory=list)  # RichTextObject
    description: List[Any] = field(default_factory=list)  # RichTextObject
    icon: Optional[Any] = None  # Icon object
    cover: Optional[str] = None  # Cover URL
    parent: Optional[Any] = None  # Parent object
    url: str = ""
    archived: bool = False
    in_trash: bool = False
    is_inline: bool = False
    public_url: Optional[str] = None

    # Client reference
    _client: Any = field(default=None, init=False, repr=False)

    # Lazy-loaded data sources
    _detailed_data_sources: Optional[List["DataSource"]] = field(
        default=None, init=False, repr=False
    )

    @classmethod
    def from_dict(cls, data: dict, client: Any = None) -> "Database":
        """Parse database from API response."""
        instance = cls()

        # Basic fields
        instance.object = data.get("object")
        instance.id = UUID(data.get("id"))
        instance.created_time = _parse_datetime(data.get("created_time"))
        instance.last_edited_time = _parse_datetime(data.get("last_edited_time"))
        instance.archived = data.get("archived", False)
        instance.in_trash = data.get("in_trash", False)
        instance.is_inline = data.get("is_inline", False)
        instance.url = data.get("url", "")
        instance.public_url = data.get("public_url")

        # Parse data source references
        ds_refs_data = data.get("data_sources", [])
        instance.data_sources = [
            DataSourceReference.from_dict(ref) for ref in ds_refs_data
        ]

        # Title and description (rich text)
        title_data = data.get("title", [])
        instance.title = RichTextParser.parse_array(title_data)

        description_data = data.get("description", [])
        instance.description = RichTextParser.parse_array(description_data)

        # Icon and cover
        instance.icon = Icon.from_dict(data.get("icon"))
        if data.get("cover"):
            cover_data = data["cover"]
            if cover_data.get("type") == "external":
                instance.cover = cover_data["external"]["url"]

        # Parent
        if "parent" in data:
            instance.parent = Parent.from_dict(data["parent"])

        # Store client reference
        instance._client = client

        return instance

    def to_dict(self) -> dict:
        """Convert to API-compatible dict."""
        return {
            "object": self.object,
            "id": str(self.id),
            "archived": self.archived,
            "is_inline": self.is_inline,
            # ... other fields
        }

    # Convenience properties

    @property
    def title_text(self) -> str:
        """Get database title as plain text."""
        return "".join(rt.plain_text for rt in self.title)

    @property
    def description_text(self) -> str:
        """Get database description as plain text."""
        return "".join(rt.plain_text for rt in self.description)

    @property
    def has_multiple_data_sources(self) -> bool:
        """Whether database has multiple data sources."""
        return len(self.data_sources) > 1

    # Data source methods

    async def get_data_sources(self, force_refresh: bool = False) -> List["DataSource"]:
        """Get detailed data source information."""
        if force_refresh or self._detailed_data_sources is None:
            if not self._client:
                raise RuntimeError("Cannot fetch data sources without client")

            data_sources = []
            for ref in self.data_sources:
                ds = await self._client.data_sources.get(str(ref.id))
                data_sources.append(ds)

            self._detailed_data_sources = data_sources

        return self._detailed_data_sources

    async def get_default_data_source(self) -> Optional["DataSource"]:
        """Get the default (first) data source."""
        data_sources = await self.get_data_sources()
        return data_sources[0] if data_sources else None

    async def get_data_source_by_name(self, name: str) -> Optional["DataSource"]:
        """Get data source by name."""
        data_sources = await self.get_data_sources()
        for ds in data_sources:
            if ds.name == name:
                return ds
        return None

    # Query methods

    async def query_pages(
        self,
        data_source_id: Optional[str] = None,
        filter: Optional[dict] = None,
        sorts: Optional[List[dict]] = None,
        start_cursor: Optional[str] = None,
        page_size: int = 100
    ) -> "PaginatedResponse[Page]":
        """Query pages in the database."""
        if not self._client:
            raise RuntimeError("Cannot query without client reference")

        # If no data source specified and only one exists, use it
        if data_source_id is None and len(self.data_sources) == 1:
            data_source_id = str(self.data_sources[0].id)

        return await self._client.databases.query(
            database_id=str(self.id),
            data_source_id=data_source_id,
            filter=filter,
            sorts=sorts,
            start_cursor=start_cursor,
            page_size=page_size
        )

    async def query_all_pages(
        self,
        data_source_id: Optional[str] = None,
        **query_kwargs
    ) -> List[Page]:
        """Query all pages with automatic pagination."""
        all_pages = []
        has_more = True
        cursor = None

        while has_more:
            response = await self.query_pages(
                data_source_id=data_source_id,
                start_cursor=cursor,
                **query_kwargs
            )

            all_pages.extend(response.results)
            has_more = response.has_more
            cursor = response.next_cursor

        return all_pages

    # Update methods

    async def update(
        self,
        title: Optional[str] = None,
        description: Optional[str] = None,
        icon: Optional[dict] = None,
        cover: Optional[str] = None,
        archived: Optional[bool] = None
    ) -> "Database":
        """Update database metadata."""
        if not self._client:
            raise RuntimeError("Cannot update without client reference")

        update_data = {}

        if title is not None:
            update_data["title"] = [
                {"type": "text", "text": {"content": title}}
            ]

        if description is not None:
            update_data["description"] = [
                {"type": "text", "text": {"content": description}}
            ]

        if icon is not None:
            update_data["icon"] = icon

        if cover is not None:
            update_data["cover"] = {
                "type": "external",
                "external": {"url": cover}
            }

        if archived is not None:
            update_data["archived"] = archived

        response = await self._client.databases.update(
            database_id=str(self.id),
            **update_data
        )

        return Database.from_dict(response, self._client)

    async def archive(self) -> "Database":
        """Archive the database."""
        return await self.update(archived=True)

    async def unarchive(self) -> "Database":
        """Unarchive the database."""
        return await self.update(archived=False)

    async def delete(self) -> None:
        """Delete the database."""
        if not self._client:
            raise RuntimeError("Cannot delete without client reference")

        await self._client.databases.delete(str(self.id))

    # Creation helpers

    async def create_page(
        self,
        data_source_id: Optional[str] = None,
        properties: dict = None
    ) -> Page:
        """Create a page in the database."""
        if not self._client:
            raise RuntimeError("Cannot create page without client reference")

        # Use default data source if not specified
        if data_source_id is None:
            if len(self.data_sources) == 1:
                data_source_id = str(self.data_sources[0].id)
            else:
                raise ValueError(
                    "Database has multiple data sources; "
                    "must specify data_source_id"
                )

        return await self._client.pages.create(
            parent={
                "type": "data_source_id",
                "data_source_id": data_source_id
            },
            properties=properties or {}
        )
```

## Data Source Class

```python
@dataclass
class PropertySchema:
    """Property schema definition from data source."""
    id: str
    name: str
    type: str
    config: dict = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: dict) -> "PropertySchema":
        """Parse property schema."""
        prop_id = data.get("id")
        name = data.get("name")
        prop_type = data.get("type")

        # Type-specific config
        config = data.get(prop_type, {})

        return cls(prop_id, name, prop_type, config)

    def to_dict(self) -> dict:
        """Convert to API format."""
        return {
            "id": self.id,
            "name": self.name,
            "type": self.type,
            self.type: self.config
        }

    @property
    def is_readonly(self) -> bool:
        """Whether this property type is read-only."""
        return self.type in READONLY_PROPERTY_TYPES

    @property
    def options(self) -> Optional[List[dict]]:
        """Get options for select/multi_select/status properties."""
        if self.type in ["select", "multi_select", "status"]:
            return self.config.get("options", [])
        return None

    def get_option_by_name(self, name: str) -> Optional[dict]:
        """Get select option by name."""
        if self.options:
            for opt in self.options:
                if opt.get("name") == name:
                    return opt
        return None

    def get_option_by_id(self, option_id: str) -> Optional[dict]:
        """Get select option by ID."""
        if self.options:
            for opt in self.options:
                if opt.get("id") == option_id:
                    return opt
        return None

READONLY_PROPERTY_TYPES = {
    "created_by",
    "created_time",
    "last_edited_by",
    "last_edited_time",
    "formula",
    "rollup",
    "unique_id",
    "verification"
}

@dataclass
class DataSourceParent:
    """Data source parent (always a database)."""
    type: str = "database_id"
    database_id: Optional[UUID] = None

    @classmethod
    def from_dict(cls, data: dict) -> "DataSourceParent":
        """Parse from API response."""
        return cls(
            type=data.get("type"),
            database_id=UUID(data.get("database_id")) if data.get("database_id") else None
        )

@dataclass
class DataSource:
    """Notion data source object (schema + pages)."""
    object: str = "data_source"
    id: UUID = None
    name: str = ""
    parent: Optional[DataSourceParent] = None
    type: str = "table"  # Display type
    properties: List[PropertySchema] = field(default_factory=list)

    # Client reference
    _client: Any = field(default=None, init=False, repr=False)

    @classmethod
    def from_dict(cls, data: dict, client: Any = None) -> "DataSource":
        """Parse data source from API response."""
        instance = cls()

        instance.object = data.get("object")
        instance.id = UUID(data.get("id"))
        instance.name = data.get("name")
        instance.type = data.get("type", "table")

        # Parent
        if "parent" in data:
            instance.parent = DataSourceParent.from_dict(data["parent"])

        # Parse properties
        properties_data = data.get("properties", [])
        instance.properties = [
            PropertySchema.from_dict(prop) for prop in properties_data
        ]

        instance._client = client
        return instance

    def to_dict(self) -> dict:
        """Convert to API format."""
        return {
            "object": self.object,
            "id": str(self.id),
            "name": self.name,
            "type": self.type,
            "properties": [prop.to_dict() for prop in self.properties]
        }

    @property
    def database_id(self) -> Optional[UUID]:
        """Get parent database ID."""
        if self.parent:
            return self.parent.database_id
        return None

    # Property access

    def get_property_by_name(self, name: str) -> Optional[PropertySchema]:
        """Get property schema by name."""
        for prop in self.properties:
            if prop.name == name:
                return prop
        return None

    def get_property_by_id(self, prop_id: str) -> Optional[PropertySchema]:
        """Get property schema by ID."""
        for prop in self.properties:
            if prop.id == prop_id:
                return prop
        return None

    @property
    def title_property(self) -> Optional[PropertySchema]:
        """Get the title property."""
        return self.get_property_by_id("title")

    @property
    def editable_properties(self) -> List[PropertySchema]:
        """Get list of editable properties."""
        return [p for p in self.properties if not p.is_readonly]

    # Query methods

    async def query_pages(
        self,
        filter: Optional[dict] = None,
        sorts: Optional[List[dict]] = None,
        start_cursor: Optional[str] = None,
        page_size: int = 100
    ) -> "PaginatedResponse[Page]":
        """Query pages in this data source."""
        if not self._client:
            raise RuntimeError("Cannot query without client reference")

        return await self._client.databases.query(
            database_id=str(self.database_id),
            data_source_id=str(self.id),
            filter=filter,
            sorts=sorts,
            start_cursor=start_cursor,
            page_size=page_size
        )

    async def query_all_pages(self, **query_kwargs) -> List[Page]:
        """Query all pages with automatic pagination."""
        all_pages = []
        has_more = True
        cursor = None

        while has_more:
            response = await self.query_pages(
                start_cursor=cursor,
                **query_kwargs
            )

            all_pages.extend(response.results)
            has_more = response.has_more
            cursor = response.next_cursor

        return all_pages

    # Create pages

    async def create_page(self, properties: dict) -> Page:
        """Create a page in this data source."""
        if not self._client:
            raise RuntimeError("Cannot create page without client reference")

        return await self._client.pages.create(
            parent={
                "type": "data_source_id",
                "data_source_id": str(self.id)
            },
            properties=properties
        )

    # Update methods

    async def update(self, **changes) -> "DataSource":
        """Update data source."""
        if not self._client:
            raise RuntimeError("Cannot update without client reference")

        response = await self._client.data_sources.update(
            data_source_id=str(self.id),
            **changes
        )

        return DataSource.from_dict(response, self._client)
```

## Query Builder

```python
class QueryBuilder:
    """Build database queries with fluent interface."""

    def __init__(self, database_id: str, client: Any):
        self.database_id = database_id
        self.client = client
        self.data_source_id: Optional[str] = None
        self.filter: Optional[dict] = None
        self.sorts: List[dict] = []

    def for_data_source(self, data_source_id: str) -> "QueryBuilder":
        """Specify data source to query."""
        self.data_source_id = data_source_id
        return self

    def where(self, filter: dict) -> "QueryBuilder":
        """Add filter condition."""
        if self.filter is None:
            self.filter = filter
        else:
            # Combine with AND
            self.filter = {
                "and": [self.filter, filter]
            }
        return self

    def filter_by_property(
        self,
        property_name: str,
        condition: str,
        value: Any
    ) -> "QueryBuilder":
        """Add property filter."""
        self.filter = {
            "property": property_name,
            condition: value
        }
        return self

    def order_by(self, property_name: str, direction: str = "ascending") -> "QueryBuilder":
        """Add sort order."""
        self.sorts.append({
            "property": property_name,
            "direction": direction
        })
        return self

    async def execute(
        self,
        page_size: int = 100,
        start_cursor: Optional[str] = None
    ) -> "PaginatedResponse[Page]":
        """Execute the query."""
        return await self.client.databases.query(
            database_id=self.database_id,
            data_source_id=self.data_source_id,
            filter=self.filter,
            sorts=self.sorts if self.sorts else None,
            start_cursor=start_cursor,
            page_size=page_size
        )

    async def execute_all(self) -> List[Page]:
        """Execute query and return all results."""
        all_pages = []
        has_more = True
        cursor = None

        while has_more:
            response = await self.execute(start_cursor=cursor)
            all_pages.extend(response.results)
            has_more = response.has_more
            cursor = response.next_cursor

        return all_pages
```

## Usage Examples

### Working with Databases

```python
# Get a database
database = await client.databases.get(database_id)

# Access basic info
print(database.title_text)
print(f"Has {len(database.data_sources)} data source(s)")

# Get data sources
data_sources = await database.get_data_sources()

for ds in data_sources:
    print(f"Data source: {ds.name}")
    print(f"  Properties: {len(ds.properties)}")

# Query pages (default data source)
pages = await database.query_pages()

# Query with filter
pages = await database.query_pages(
    filter={
        "property": "Status",
        "status": {
            "equals": "In Progress"
        }
    }
)

# Create page
new_page = await database.create_page(
    properties={
        "Name": {
            "title": [{"type": "text", "text": {"content": "New Task"}}]
        },
        "Status": {"status": {"name": "Not Started"}}
    }
)
```

### Using Query Builder

```python
# Build complex query
query = QueryBuilder(database_id, client)

query = (query
    .for_data_source(data_source_id)
    .filter_by_property("Status", "equals", "In Progress")
    .filter_by_property("Priority", "equals", "High")
    .order_by("Due Date", "ascending")
)

# Execute
pages = await query.execute()

# Or get all pages
all_pages = await query.execute_all()
```

### Working with Data Sources

```python
# Get data source
data_source = await client.data_sources.get(data_source_id)

# Access properties
for prop in data_source.properties:
    print(f"{prop.name}: {prop.type}")

# Get specific property
status_prop = data_source.get_property_by_name("Status")
if status_prop:
    print(f"Status options: {status_prop.options}")

# Query pages
pages = await data_source.query_pages(
    filter={
        "property": "Status",
        "status": {"equals": "In Progress"}
    }
)

# Create page
page = await data_source.create_page(
    properties={
        "Name": {
            "title": [{"type": "text", "text": {"content": "Task"}}]
        }
    }
)
```

### Creating Databases

```python
# Create database with data source
database = await client.databases.create(
    parent={"type": "page_id", "page_id": parent_page_id},
    title=[{"type": "text", "text": {"content": "Tasks"}}],
    properties=[
        {
            "id": "title",
            "name": "Name",
            "type": "title",
            "title": {}
        },
        {
            "id": "status",
            "name": "Status",
            "type": "status",
            "status": {
                "options": [
                    {"name": "Not Started", "color": "default"},
                    {"name": "In Progress", "color": "blue"},
                    {"name": "Done", "color": "green"}
                ]
            }
        }
    ]
)
```

## Implementation Checklist

### Database Classes
- [ ] `Database` class with all fields
- [ ] `DataSourceReference` class
- [ ] `DataSource` class with full schema support
- [ ] `PropertySchema` class
- [ ] `DataSourceParent` class

### Query System
- [ ] `QueryBuilder` class
- [ ] Filter building helpers
- [ ] Sort building helpers
- [ ] Pagination support

### CRUD Operations
- [ ] Retrieve database
- [ ] Retrieve data source
- [ ] Query database pages
- [ ] Create database
- [ ] Update database/data source
- [ ] Delete database

### Helpers
- [ ] Property access helpers
- [ ] Multi data source handling
- [ ] Default data source detection
- [ ] Validation helpers

### Testing
- [ ] Unit tests for Database class
- [ ] Unit tests for DataSource class
- [ ] Tests for QueryBuilder
- [ ] Integration tests with API
- [ ] Tests for CRUD operations
- [ ] Tests for multi data source scenarios

---

**Related Documentation:**
- [Databases Overview](./databases-overview.md) - Database concepts
- [Data Sources](./data-sources.md) - Data source details
- [Page Properties](../pages/page-properties.md) - Property types
