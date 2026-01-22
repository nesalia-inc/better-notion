# Data Sources

## Overview

**Data Sources** are the components within databases that define the schema (properties) and contain pages (rows). Introduced in September 2025, data sources separate the database container from its data schemas.

## Key Concepts

### Database vs Data Source

```
Database (container)
├── Metadata (title, icon, parent)
└── Data Sources (1 or more)
    ├── Data Source 1
    │   ├── Schema (properties)
    │   └── Pages (rows with those properties)
    └── Data Source 2
        ├── Schema (different properties)
        └── Pages (rows with different properties)
```

**Analogy:**
- **Database** = A spreadsheet file (can have multiple sheets)
- **Data Source** = A single sheet with its own columns and rows

### Why Multiple Data Sources?

Use cases for multiple data sources in one database:

1. **Different page types** - Tasks with different property sets
2. **Independent schemas** - Unrelated data in same location
3. **Data segregation** - Separate sets of pages with different needs
4. **Migration scenarios** - Gradual schema changes

## Data Source Object

### Full Data Source Structure

```json
{
  "object": "data_source",
  "id": "c174b72c-d782-432f-8dc0-b647e1c96df6",
  "name": "Tasks data source",
  "parent": {
    "type": "database_id",
    "database_id": "2f26ee68-df30-4251-aad4-8ddc420cba3d"
  },
  "type": "table",
  "properties": [
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
          {
            "id": "58fc84c5-0b72-47bf-8384-8424f6c85916",
            "name": "Not started",
            "color": "default"
          },
          {
            "id": "a5b3c6e0-7d9d-4e1a-9b8f-2c3d4e5f6a7b",
            "name": "In progress",
            "color": "blue"
          }
        ]
      }
    },
    {
      "id": "tags",
      "name": "Tags",
      "type": "multi_select",
      "multi_select": {
        "options": [
          {
            "id": "d6e8f7a6-b5c4-4e2d-9f1a-2b3c4d5e6f7a",
            "name": "Urgent",
            "color": "red"
          }
        ]
      }
    }
  ]
}
```

### Data Source Fields

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `object` | string | Always `"data_source"` | `"data_source"` |
| `id` | string (UUID) | Unique identifier | `"c174b72c-..."` |
| `name` | string | Display name | `"Tasks data source"` |
| `parent` | object | Parent database reference | `{"type": "database_id", ...}` |
| `type` | string | Display type | `"table"`, `"board"`, etc. |
| `properties` | array | Property schema (definitions) | `[/* property objects */]` |

## Data Source Properties

### Property Schema vs Property Values

**Important distinction:**

- **Schema (in data source)** - Defines what properties exist and their types
- **Values (in pages)** - The actual data for each page

**Example:**

**Schema (in data source):**
```json
{
  "id": "status",
  "name": "Status",
  "type": "status",
  "status": {
    "options": [
      {"id": "...", "name": "Not started", "color": "default"},
      {"id": "...", "name": "In progress", "color": "blue"}
    ]
  }
}
```

**Value (in a page):**
```json
{
  "id": "status",
  "type": "status",
  "status": {
    "id": "...",
    "name": "In progress",
    "color": "blue"
  }
}
```

### Property Schema Structure

Every property schema has these common fields:

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Unique identifier (URL-encoded) |
| `name` | string | Display name in UI |
| `type` | string | Property type |
| `{type}` | object | Type-specific configuration |

### Property Types Reference

Complete list of property types and their schema configuration:

#### Title

**Required:** Every data source must have exactly one title property.

```json
{
  "id": "title",
  "name": "Name",
  "type": "title",
  "title": {}
}
```

#### Status

```json
{
  "id": "status",
  "name": "Status",
  "type": "status",
  "status": {
    "options": [
      {
        "id": "uuid",
        "name": "Not started",
        "color": "default"
      },
      {
        "id": "uuid",
        "name": "In progress",
        "color": "blue"
      },
      {
        "id": "uuid",
        "name": "Done",
        "color": "green"
      }
    ],
    "groups": [
      {
        "id": "uuid",
        "name": "To do",
        "color": "gray",
        "option_ids": ["uuid1", "uuid2"]
      }
    ]
  }
}
```

**Colors:** `default`, `gray`, `brown`, `red`, `orange`, `yellow`, `green`, `blue`, `purple`, `pink`

#### Select

```json
{
  "id": "priority",
  "name": "Priority",
  "type": "select",
  "select": {
    "options": [
      {
        "id": "uuid",
        "name": "High",
        "color": "red"
      },
      {
        "id": "uuid",
        "name": "Medium",
        "color": "yellow"
      },
      {
        "id": "uuid",
        "name": "Low",
        "color": "gray"
      }
    ]
  }
}
```

#### Multi-Select

```json
{
  "id": "tags",
  "name": "Tags",
  "type": "multi_select",
  "multi_select": {
    "options": [
      {
        "id": "uuid",
        "name": "Urgent",
        "color": "red"
      },
      {
        "id": "uuid",
        "name": "Bug",
        "color": "orange"
      }
    ]
  }
}
```

#### Date

```json
{
  "id": "due_date",
  "name": "Due Date",
  "type": "date",
  "date": {}
}
```

#### Number

```json
{
  "id": "quantity",
  "name": "Quantity",
  "type": "number",
  "number": {
    "format": "number"
  }
}
```

**Formats:** `number`, `phone_number`, `percent`

#### Checkbox

```json
{
  "id": "done",
  "name": "Done",
  "type": "checkbox",
  "checkbox": {}
}
```

#### Email

```json
{
  "id": "email",
  "name": "Email",
  "type": "email",
  "email": {}
}
```

#### Phone Number

```json
{
  "id": "phone",
  "name": "Phone",
  "type": "phone_number",
  "phone_number": {}
}
```

#### URL

```json
{
  "id": "website",
  "name": "Website",
  "type": "url",
  "url": {}
}
```

#### Rich Text

```json
{
  "id": "description",
  "name": "Description",
  "type": "rich_text",
  "rich_text": {}
}
```

#### People

```json
{
  "id": "assignee",
  "name": "Assignee",
  "type": "people",
  "people": {}
}
```

#### Files

```json
{
  "id": "attachments",
  "name": "Attachments",
  "type": "files",
  "files": {}
}
```

#### Relation

```json
{
  "id": "related_tasks",
  "name": "Related Tasks",
  "type": "relation",
  "relation": {
    "database_id": "database-uuid",
    "synced_property_name": "Related Tasks",
    "dual_property": {
      "id": "property-uuid",
      "name": "Related Projects"
    }
  }
}
```

#### Formula

```json
{
  "id": "total",
  "name": "Total",
  "type": "formula",
  "formula": {
    "expression": "prop(\"Price\") * prop(\"Quantity\")"
  }
}
```

#### Rollup

```json
{
  "id": "task_count",
  "name": "Task Count",
  "type": "rollup",
  "rollup": {
    "relation_property_name": "Related Tasks",
    "relation_property_id": "relation-id",
    "rollup_property_name": "Status",
    "rollup_property_id": "status-id",
    "function": "count"
  }
}
```

**Functions:** `average`, `checked`, `count`, `count_values`, `date_range`, `earliest_date`, `empty`, `latest_date`, `max`, `median`, `min`, `not_empty`, `percent_checked`, `percent_empty`, `percent_not_empty`, `range`, `show_unique`, `sum`, `unchecked`, `unique`

#### Created By

```json
{
  "id": "created_by",
  "name": "Created By",
  "type": "created_by",
  "created_by": {}
}
```

#### Created Time

```json
{
  "id": "created_time",
  "name": "Created Time",
  "type": "created_time",
  "created_time": {}
}
```

#### Last Edited By

```json
{
  "id": "last_edited_by",
  "name": "Last Edited By",
  "type": "last_edited_by",
  "last_edited_by": {}
}
```

#### Last Edited Time

```json
{
  "id": "last_edited_time",
  "name": "Last Edited Time",
  "type": "last_edited_time",
  "last_edited_time": {}
}
```

#### Unique ID

```json
{
  "id": "id",
  "name": "ID",
  "type": "unique_id",
  "unique_id": {
    "prefix": "TASK-"
  }
}
```

#### Verification

```json
{
  "id": "verification",
  "name": "Verification",
  "type": "verification",
  "verification": {}
}
```

## Working with Data Sources

### Retrieve Data Source

```
GET /data_sources/{data_source_id}
```

**Returns:** Full data source object with properties

### Update Data Source Properties

```
PATCH /data_sources/{data_source_id}
```

**Can update:**
- Property names
- Property configurations (options for select/status, etc.)
- Add/remove properties (in some cases)

**Cannot update:**
- Property types (changing number to date, etc.)

### Create Data Source

```
POST /databases/{database_id}/data_sources
```

**Required:**
- `name` - Data source name
- `properties` - Initial property schema

### Delete Data Source

```
DELETE /data_sources/{data_source_id}
```

**Warning:** This also deletes all pages in the data source.

## Data Source Types

### Display Types

| Type | Description |
|------|-------------|
| `table` | Table view (default) |
| `board` | Kanban board |
| `list` | Simple list |
| `timeline` | Timeline view |
| `calendar` | Calendar view |
| `gallery` | Image gallery |

**Note:** Display type affects how the data source is shown in the UI, but doesn't affect the API structure.

## Querying Pages by Data Source

When a database has multiple data sources, you must specify which one to query:

```json
POST /databases/{database_id}/query
{
  "data_source": {
    "id": "c174b72c-d782-432f-8dc0-b647e1c96df6"
  },
  "filter": {
    // filter conditions
  }
}
```

If the database has only one data source, you can omit the `data_source` parameter.

## SDK Architecture Implications

### DataSource Class

```python
@dataclass
class DataSource:
    """Notion data source object."""
    object: str = "data_source"
    id: UUID = None
    name: str = ""
    parent: Optional[DataSourceParent] = None
    type: str = "table"
    properties: List["PropertySchema"] = field(default_factory=list)

    # Reference to parent database
    _database_id: Optional[UUID] = field(default=None, init=False, repr=False)
    _client: Any = field(default=None, init=False, repr=False)

    @classmethod
    def from_dict(cls, data: dict, client: Any = None) -> "DataSource":
        """Parse from API response."""
        instance = cls()

        instance.object = data.get("object")
        instance.id = UUID(data.get("id"))
        instance.name = data.get("name")
        instance.type = data.get("type", "table")

        # Parent
        parent_data = data.get("parent", {})
        if parent_data.get("type") == "database_id":
            instance._database_id = UUID(parent_data.get("database_id"))

        # Parse properties
        properties_data = data.get("properties", [])
        instance.properties = [
            PropertySchema.from_dict(prop) for prop in properties_data
        ]

        instance._client = client
        return instance

    @property
    def database_id(self) -> UUID:
        """Get parent database ID."""
        return self._database_id

    def get_property_by_name(self, name: str) -> Optional["PropertySchema"]:
        """Get property schema by name."""
        for prop in self.properties:
            if prop.name == name:
                return prop
        return None

    def get_property_by_id(self, prop_id: str) -> Optional["PropertySchema"]:
        """Get property schema by ID."""
        for prop in self.properties:
            if prop.id == prop_id:
                return prop
        return None

    async def query_pages(self, **filters) -> PaginatedResponse[Page]:
        """Query pages in this data source."""
        if not self._client:
            raise RuntimeError("No client reference")

        return await self._client.databases.query(
            database_id=str(self._database_id),
            data_source_id=str(self.id),
            **filters
        )

    async def create_page(self, properties: dict) -> Page:
        """Create a page in this data source."""
        if not self._client:
            raise RuntimeError("No client reference")

        return await self._client.pages.create(
            parent={
                "type": "data_source_id",
                "data_source_id": str(self.id)
            },
            properties=properties
        )
```

### PropertySchema Class

```python
class PropertySchema:
    """Data source property schema definition."""

    def __init__(self, prop_id: str, name: str, prop_type: str, config: dict):
        self.id = prop_id
        self.name = name
        self.type = prop_type
        self.config = config

    @classmethod
    def from_dict(cls, data: dict) -> "PropertySchema":
        """Parse property schema."""
        prop_id = data.get("id")
        name = data.get("name")
        prop_type = data.get("type")

        # Type-specific config
        config = data.get(prop_type, {})

        return cls(prop_id, name, prop_type, config)

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
```

## Usage Examples

```python
# Get a database
database = await client.databases.get(database_id)

# Get data source references
for ref in database.data_sources:
    print(f"Data source: {ref.name} (id: {ref.id})")

# Get detailed data source
data_source = await client.data_sources.get(ref.id)

# Access properties
for prop in data_source.properties:
    print(f"Property: {prop.name} (type: {prop.type})")

# Get specific property
status_prop = data_source.get_property_by_name("Status")
if status_prop:
    print(f"Status options: {status_prop.options}")

# Query pages in data source
pages = await data_source.query_pages(
    filter={
        "property": "Status",
        "status": {
            "equals": "In Progress"
        }
    }
)

# Create page in data source
new_page = await data_source.create_page(
    properties={
        "Name": {
            "title": [{"type": "text", "text": {"content": "New Task"}}]
        },
        "Status": {
            "status": {"name": "Not Started"}
        }
    }
)
```

## Best Practices

### 1. Single vs Multiple Data Sources

**Use single data source when:**
- All pages have the same properties
- Simple data structure
- Most common scenario

**Use multiple data sources when:**
- Different page types need different schemas
- Independent data sets in same location
- Complex data modeling needs

### 2. Property Naming

- Use clear, consistent names
- Avoid commas in select/multi-select values
- Consider future schema changes

### 3. Option Management

For select/multi-select/status:
- Define options upfront when possible
- Use meaningful colors for organization
- Group related status options (using groups in status)

### 4. Relation Design

- Ensure integration has access to both databases
- Use dual properties for bidirectional relations
- Consider rollup performance with many relations

## Migration from Single Data Source

### Before September 2025

```python
# Old: Properties on database
database = await client.databases.get(database_id)
properties = database.properties  # Direct access
```

### After September 2025

```python
# New: Properties on data source
database = await client.databases.get(database_id)
data_source = await client.data_sources.get(database.data_sources[0].id)
properties = data_source.properties  # Via data source
```

### Backward Compatibility

For databases with a single data source:
- Most operations work similarly
- Properties accessible via data source
- Query defaults to the only data source

## Related Documentation

- [Databases Overview](./databases-overview.md) - Database container concept
- [Database Implementation](./database-implementation.md) - SDK implementation
- [Page Properties](../pages/page-properties.md) - Property value types
- [Query Database](https://developers.notion.com/reference/post-database-query) - API query endpoint

---

**Next:** See [Database Implementation](./database-implementation.md) for SDK implementation details.
