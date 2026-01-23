# Databases Overview

## Introduction

A **Database** in Notion is a container for one or more **Data Sources**. Each data source contains pages (rows) with properties (columns) defined by a schema.

**Important Change (September 2025):**
- Previously, databases had a single data source combined with the database
- Now, databases can have **multiple data sources**, each with independent schemas
- Properties are now at the **data source level**, not the database level

## Data Model

### New Structure (Post-September 2025)

```
Database (container)
├── Data Source 1
│   ├── Properties (schema)
│   └── Pages (rows)
├── Data Source 2
│   ├── Properties (schema)
│   └── Pages (rows)
└── Data Source N
    ├── Properties (schema)
    └── Pages (rows)
```

**Key Points:**
- A database can have multiple data sources
- Each data source has its own property schema
- Each data source contains its own set of pages
- Permissions are managed at the database level (not per data source)

### Display Modes

Databases can be displayed in two ways:

1. **Inline Database** (`is_inline: true`)
   - Appears as a block within a page
   - Shows table/board/list/etc. view inline
   - Parent is typically a page

2. **Full-Page Database** (`is_inline: false`)
   - Appears as a full page
   - Takes up the entire page view
   - Can be at workspace level or child of another page

**Constraint:** Workspace-level databases must be full-page databases (not inline).

## Database Object Structure

### Example Database Object

```json
{
  "object": "database",
  "id": "2f26ee68-df30-4251-aad4-8ddc420cba3d",
  "data_sources": [
    {
      "id": "c174b72c-d782-432f-8dc0-b647e1c96df6",
      "name": "Tasks data source"
    }
  ],
  "created_time": "2020-03-17T19:10:04.968Z",
  "created_by": {
    "object": "user",
    "id": "45ee8d13-687b-47ce-a5ca-6e2e45548c4b"
  },
  "last_edited_time": "2020-03-17T21:49:37.913Z",
  "last_edited_by": {
    "object": "user",
    "id": "45ee8d13-687b-47ce-a5ca-6e2e45548c4b"
  },
  "title": [
    {
      "type": "text",
      "text": {
        "content": "Can I create a URL property",
        "link": null
      },
      "annotations": {
        "bold": false,
        "italic": false,
        "strikethrough": false,
        "underline": false,
        "code": false,
        "color": "default"
      },
      "plain_text": "Can I create a URL property",
      "href": null
    }
  ],
  "description": [],
  "icon": {
    "type": "emoji",
    "emoji": "📊"
  },
  "cover": null,
  "parent": {
    "type": "page_id",
    "page_id": "af5f89b5-a8ff-4c56-a5e8-69797d11b9f8"
  },
  "url": "https://www.notion.so/668d797c76fa49349b05ad288df2d136",
  "archived": false,
  "in_trash": false,
  "is_inline": false,
  "public_url": "https://jm-testing.notion.site/p1-6df2c07b"
}
```

## Database Object Fields

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `object` | string | Always `"database"` | `"database"` |
| `id` | string (UUID) | Unique identifier | `"2f26ee68-..."` |
| `data_sources` | array | List of child data sources (id + name) | `[{"id": "...", "name": "Tasks"}]` |
| `created_time` | string (ISO 8601) | Creation timestamp | `"2020-03-17T19:10:04.968Z"` |
| `created_by` | PartialUser | User who created | `{"object": "user", "id": "..."}` |
| `last_edited_time` | string (ISO 8601) | Last edit timestamp | `"2020-03-17T21:49:37.913Z"` |
| `last_edited_by` | PartialUser | User who last edited | `{"object": "user", "id": "..."}` |
| `title` | array of rich text | Database name | `[/* rich text */]` |
| `description` | array of rich text | Database description | `[/* rich text */]` |
| `icon` * | FileObject \| Emoji | Database icon | `{"type": "emoji", "emoji": "📊"}` |
| `cover` * | FileObject | Cover image | `{"type": "external", "external": {...}}` |
| `parent` | object | Parent information | `{"type": "page_id", "page_id": "..."}` |
| `url` | string | Notion URL | `"https://notion.so/..."` |
| `archived` | boolean | Archived status | `false` |
| `in_trash` | boolean | Whether deleted | `false` |
| `is_inline` | boolean | Inline vs full-page | `false` |
| `public_url` | string \| null | Public URL if published | `"https://..."` |

* = Available to integrations with any capabilities

## Data Sources

### What is a Data Source?

A **data source** is a collection of pages with a shared property schema. Previously (before September 2025), databases had only one data source, so the concepts were combined.

**Now:**
- A database can have multiple data sources
- Each data source has its own properties
- Each data source contains its own pages

### Data Source Object (Summary)

```json
{
  "id": "c174b72c-d782-432f-8dc0-b647e1c96df6",
  "name": "Tasks data source"
}
```

**Note:** Use the **Retrieve a data source** endpoint to get full details including properties.

See [Data Sources](./data-sources.md) for complete information.

## Parent Types

Databases can have different parent types:

### 1. Page Parent
```json
{
  "type": "page_id",
  "page_id": "af5f89b5-a8ff-4c56-a5e8-69797d11b9f8"
}
```
- Database is nested under a page
- Can be inline or full-page

### 2. Workspace Parent
```json
{
  "type": "workspace",
  "workspace": true
}
```
- Database is at workspace root level
- **Must be full-page** (cannot be inline)
- Recommended: Have at least one parent page for better permission management

### 3. Block Parent
```json
{
  "type": "block_id",
  "block_id": "7d50a184-5bbe-4d90-8f29-6bec57ed817b"
}
```
- Rare case, database created as child of a block

## Icon and Cover

### Icon

**Types:**
1. **Emoji** - Simple emoji character
2. **External file** - URL to an image
3. **File upload** - Notion-hosted file

**Example (emoji):**
```json
{
  "type": "emoji",
  "emoji": "📊"
}
```

**Example (file):**
```json
{
  "type": "file",
  "file": {
    "url": "https://...",
    "expiry_time": "2024-12-03T19:44:56.932Z"
  }
}
```

### Cover

Cover image (file only, no emoji):

```json
{
  "type": "external",
  "external": {
    "url": "https://example.com/cover.jpg"
  }
}
```

## URLs

### Internal vs Public

| Field | Description | When Present |
|-------|-------------|--------------|
| `url` | Internal Notion URL | Always |
| `public_url` | Published web URL | Only if published to web |

## Working with Databases

### Retrieve Database

```
GET /databases/{database_id}
```

**Returns:** Database object with data sources list

### Query Database Pages

```
POST /databases/{database_id}/query
```

**Returns:** Paginated list of pages in the database

**Note:** You must specify which data source to query when multiple exist.

### Create Database

```
POST /databases
```

**Required parameters:**
- `parent` - Where to create the database
- Data source configuration (properties schema)

### Update Database

```
PATCH /databases/{database_id}
```

**Can update:**
- `title`
- `description`
- `icon`
- `cover`
- `archived` status

**Cannot update:**
- Properties schema (use data source endpoints)
- Parent

### Delete Database

```
DELETE /databases/{database_id}
```

**Note:** This also deletes all data sources and their pages.

## Database vs Pages

| Aspect | Database | Page |
|--------|----------|------|
| **Purpose** | Structured data collection | Content document |
| **Content** | Data sources → Pages with properties | Blocks (rich content) |
| **Structure** | Schema-based properties | Free-form blocks |
| **Display** | Table, board, list, timeline, etc. | Document page |
| **Querying** | Rich filtering, sorting, aggregation | Linear content |

## Permissions

### Access Control

- Permissions are managed at the **database level**
- Individual data sources do **not** have their own permissions
- Users/bots with database access can access all data sources

### Integration Access

For your integration to access a database:
1. Share the database with your integration
2. For relation properties, share related databases too
3. For rollups, ensure access to all related databases

## SDK Architecture Implications

### Database Class

```python
@dataclass
class Database:
    """Notion database object."""
    object: str = "database"
    id: UUID = None
    data_sources: List[DataSourceReference] = field(default_factory=list)
    created_time: datetime = None
    last_edited_time: datetime = None
    created_by: PartialUser = None
    last_edited_by: PartialUser = None
    title: List[RichTextObject] = field(default_factory=list)
    description: List[RichTextObject] = field(default_factory=list)
    icon: Optional[Icon] = None
    cover: Optional[str] = None
    parent: Optional[Parent] = None
    url: str = ""
    archived: bool = False
    in_trash: bool = False
    is_inline: bool = False
    public_url: Optional[str] = None

    @property
    def title_text(self) -> str:
        """Get database title as plain text."""
        return "".join(rt.plain_text for rt in self.title)

    @property
    def description_text(self) -> str:
        """Get database description as plain text."""
        return "".join(rt.plain_text for rt in self.description)

    async def get_data_sources(self) -> List[DataSource]:
        """Get detailed data source information."""
        if not self._client:
            raise RuntimeError("No client reference")

        data_sources = []
        for ref in self.data_sources:
            ds = await self._client.data_sources.get(ref.id)
            data_sources.append(ds)

        return data_sources

    async def query_pages(
        self,
        data_source_id: Optional[str] = None,
        **filters
    ) -> PaginatedResponse[Page]:
        """Query pages in the database."""
        if not self._client:
            raise RuntimeError("No client reference")

        return await self._client.databases.query(
            database_id=str(self.id),
            data_source_id=data_source_id,
            **filters
        )
```

### DataSourceReference

```python
@dataclass
class DataSourceReference:
    """Reference to a data source (summary info)."""
    id: UUID
    name: str
```

### Usage Examples

```python
# Get a database
database = await client.databases.get(database_id)

# Access basic info
print(database.title_text)
print(database.is_inline)

# Get detailed data sources
data_sources = await database.get_data_sources()

# Query pages (default data source)
pages = await database.query_pages()

# Query pages from specific data source
pages = await database.query_pages(data_source_id=data_source_id)

# Update database
await client.databases.update(
    database_id=database.id,
    title=[{"type": "text", "text": {"content": "New Title"}}]
)

# Archive database
await client.databases.update(
    database_id=database.id,
    archived=True
)
```

## Best Practices

### 1. Database Organization

**Good:**
```
Workspace
└── Projects (page)
    └── Tasks Database (inline or full-page)
```

**Avoid:**
```
Workspace
└── Tasks Database (workspace root)
```

Reason: Easier permission management with parent page.

### 2. Data Source Design

- Use a single data source when possible (simpler)
- Use multiple data sources for:
  - Different page types in same database
  - Independent property schemas
  - Segregated data sets

### 3. Property Naming

- Use clear, descriptive names
- Avoid commas (not supported in select/multi-select)
- Consider future scalability

### 4. Query Optimization

- Use specific filters to reduce result sets
- Use pagination for large datasets
- Fetch only needed properties

## Migration Notes (September 2025)

### For Existing Integrations

If you used the Notion API before September 2025:

**Old behavior:**
- Database had `properties` field
- Query returned pages directly

**New behavior:**
- Database has `data_sources` array
- Properties are in data source objects
- Query must specify data source (if multiple)

**Compatibility:**
- Old integrations continue to work
- Single data source databases behave similarly
- Update to use new endpoints for full functionality

### Updating Your Code

```python
# Old (pre-September 2025)
database = await client.databases.get(database_id)
properties = database.properties  # Direct access

# New (post-September 2025)
database = await client.databases.get(database_id)
data_source = await client.data_sources.get(database.data_sources[0].id)
properties = data_source.properties  # Via data source
```

## Related Documentation

- [Databases API Reference](./databases-api.md) - Complete API endpoint documentation
- [Data Sources API Reference](./data-sources-api.md) - Complete data source API documentation
- [Data Sources](./data-sources.md) - Data source objects and properties
- [Database Implementation](./database-implementation.md) - SDK implementation guide
- [Page Properties](../pages/page-properties.md) - Property types in detail

---

**Next:** See [Data Sources](./data-sources.md) for detailed information about data sources and their properties.
