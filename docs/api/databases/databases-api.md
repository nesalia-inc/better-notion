# Databases API Reference

Complete API reference for all database-related operations in the Notion API.

## Table of Contents

1. [Create a Database](#create-a-database)
2. [Retrieve a Database](#retrieve-a-database)
3. [Update a Database](#update-a-database)
4. [Query a Data Source](#query-a-data-source)
5. [Database vs Data Source Operations](#database-vs-data-source-operations)

---

## Create a Database

Creates a database and its initial data source with the specified properties schema.

### Endpoint

```
POST https://api.notion.com/v1/databases
```

### Body Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `parent` | object | Yes | Parent page or workspace for the database |
| `initial_data_source` | object | Yes | Initial data source configuration |
| `title` | array | No | Title of the database (rich text) |
| `description` | array | No | Description of the database (rich text) |
| `icon` | object | No | Database icon (emoji or file) |
| `cover` | object | No | Cover image for the database |

### Parent Object

**Page parent:**
```json
{
  "parent": {
    "type": "page_id",
    "page_id": "255104cd-477e-808c-b279-d39ab803a7d2"
  }
}
```

**Workspace parent:**
```json
{
  "parent": {
    "type": "workspace",
    "workspace": true
  }
}
```

**Wiki database parent:**
```json
{
  "parent": {
    "type": "wiki_id",
    "wiki_id": "wiki-id-here"
  }
}
```

### Initial Data Source Object

```json
{
  "initial_data_source": {
    "name": "My Task Tracker",
    "properties": {
      "Name": {
        "type": "title",
        "title": {}
      },
      "Status": {
        "type": "status",
        "status": {
          "options": [
            {
              "name": "Not Started",
              "color": "gray"
            },
            {
              "name": "In Progress",
              "color": "blue"
            },
            {
              "name": "Completed",
              "color": "green"
            }
          ]
        }
      },
      "Priority": {
        "type": "select",
        "select": {
          "options": [
            {"name": "Low", "color": "gray"},
            {"name": "Medium", "color": "blue"},
            {"name": "High", "color": "red"}
          ]
        }
      },
      "Due Date": {
        "type": "date",
        "date": {}
      },
      "Assignee": {
        "type": "people",
        "people": {}
      },
      "Tags": {
        "type": "multi_select",
        "multi_select": {
          "options": [
            {"name": "Bug", "color": "red"},
            {"name": "Feature", "color": "blue"},
            {"name": "Improvement", "color": "green"}
          ]
        }
      },
      "Description": {
        "type": "rich_text",
        "rich_text": {}
      },
      "Completed": {
        "type": "checkbox",
        "checkbox": {}
      },
      "Progress": {
        "type": "number",
        "number": {
          "format": "percent"
        }
      }
    }
  }
}
```

### Property Types Reference

For a complete reference on data source properties, see the [Data Sources documentation](./data-sources.md).

**Important:** Creating new status database properties is currently not supported via API.

### Title and Description

Both use rich text array format:

```json
{
  "title": [
    {
      "type": "text",
      "text": {
        "content": "My Task Tracker",
        "link": null
      },
      "annotations": {
        "bold": false,
        "italic": false,
        "strikethrough": false,
        "underline": false,
        "code": false,
        "color": "default"
      }
    }
  ]
}
```

### Icon and Cover

**Icon (emoji):**
```json
{
  "icon": {
    "type": "emoji",
    "emoji": "📊"
  }
}
```

**Icon (external file):**
```json
{
  "icon": {
    "type": "external",
    "external": {
      "url": "https://example.com/icon.png"
    }
  }
}
```

**Cover:**
```json
{
  "cover": {
    "type": "external",
    "external": {
      "url": "https://example.com/cover.jpg"
    }
  }
}
```

### Headers

| Header | Type | Required | Description |
|--------|------|----------|-------------|
| `Authorization` | string | Yes | Bearer `{integration_token}` |
| `Content-Type` | string | Yes | `application/json` |
| `Notion-Version` | string | Yes | The API version to use (latest: `2025-09-03`) |

### Required Capabilities

This endpoint requires the **insert content** capability on the target parent page.

### Limitations

1. **Parent must be a page or workspace** - Cannot create database under other block types
2. **Status properties** - Cannot create new status properties via API
3. **Single data source** - Creates database with one initial data source (use Create Data Source API to add more)

### Response

Returns the created Database object.

```json
{
  "object": "database",
  "id": "248104cd-477e-80fd-b757-e945d38000bd",
  "title": [
    {
      "type": "text",
      "text": {
        "content": "My Task Tracker",
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
      "plain_text": "My Task Tracker",
      "href": null
    }
  ],
  "parent": {
    "type": "page_id",
    "page_id": "255104cd-477e-808c-b279-d39ab803a7d2"
  },
  "is_inline": false,
  "in_trash": false,
  "created_time": "2025-08-07T10:11:07.504-07:00",
  "last_edited_time": "2025-08-10T15:53:11.386-07:00",
  "data_sources": [
    {
      "id": "248104cd-477e-80af-bc30-000bd28de8f9",
      "name": "My Task Tracker"
    }
  ],
  "icon": null,
  "cover": null
}
```

**Note:** The response includes the `data_sources` array with the initial data source ID. Use this ID for subsequent data source operations.

### SDK Implementation

```python
async def create(
    self,
    *,
    parent: Union[str, dict],
    initial_data_source: dict,
    title: Optional[List[dict]] = None,
    description: Optional[List[dict]] = None,
    icon: Optional[dict] = None,
    cover: Optional[dict] = None,
    is_inline: bool = False
) -> Database:
    """
    Create a database with an initial data source.

    Args:
        parent: Parent page ID or parent dict
        initial_data_source: Configuration for the initial data source
        title: Optional database title (rich text array)
        description: Optional database description
        icon: Optional database icon
        cover: Optional cover image
        is_inline: Whether database should be inline

    Returns:
        Created Database object

    Raises:
        ValueError: If properties are invalid
        PermissionError: If lacking insert content capability
    """
    # Build parent object
    if isinstance(parent, str):
        parent = {"type": "page_id", "page_id": parent}

    payload = {
        "parent": parent,
        "initial_data_source": initial_data_source
    }

    if title:
        payload["title"] = title
    if description:
        payload["description"] = description
    if icon:
        payload["icon"] = icon
    if cover:
        payload["cover"] = cover
    if is_inline:
        payload["is_inline"] = True

    response = await self._client.request(
        "POST",
        "/databases",
        json=payload
    )

    return Database.from_dict(response, self._client)

async def create_simple_database(
    self,
    parent: str,
    name: str,
    properties: dict
) -> Database:
    """
    Helper to create a simple database.

    Args:
        parent: Parent page ID
        name: Database name
        properties: Property schema (simplified format)

    Returns:
        Created Database object
    """
    # Build title
    title = [{
        "type": "text",
        "text": {"content": name, "link": None}
    }]

    # Format properties
    formatted_props = {}
    for prop_name, prop_config in properties.items():
        formatted_props[prop_name] = self._format_property_schema(prop_config)

    initial_data_source = {
        "name": name,
        "properties": formatted_props
    }

    return await self.create(
        parent=parent,
        title=title,
        initial_data_source=initial_data_source
    )
```

### Errors

| Status Code | Error | Description |
|-------------|-------|-------------|
| 400 | `bad_request` | Invalid properties or schema |
| 400 | `validation_error` | Attempting to create status property |
| 403 | `missing_permission` | Integration lacks insert content capability |
| 404 | `object_not_found` | Parent page doesn't exist |
| 429 | `rate_limited` | Request rate limit exceeded |

### Example Usage

```python
# Create a task tracker database
database = await client.databases.create(
    parent={
        "type": "page_id",
        "page_id": "parent-page-id"
    },
    title=[{
        "type": "text",
        "text": {"content": "My Task Tracker"}
    }],
    icon={"type": "emoji", "emoji": "📊"},
    initial_data_source={
        "name": "Tasks",
        "properties": {
            "Name": {
                "type": "title",
                "title": {}
            },
            "Status": {
                "type": "select",
                "select": {
                    "options": [
                        {"name": "To Do", "color": "gray"},
                        {"name": "In Progress", "color": "blue"},
                        {"name": "Done", "color": "green"}
                    ]
                }
            },
            "Priority": {
                "type": "select",
                "select": {
                    "options": [
                        {"name": "Low", "color": "gray"},
                        {"name": "Medium", "color": "yellow"},
                        {"name": "High", "color": "red"}
                    ]
                }
            },
            "Due Date": {
                "type": "date",
                "date": {}
            }
        }
    }
)

# Get the data source ID
data_source_id = database.data_sources[0].id
print(f"Database created: {database.id}")
print(f"Data source ID: {data_source_id}")

# Create a simple database
simple_db = await client.databases.create_simple_database(
    parent="page-id",
    name="Contacts",
    properties={
        "Name": {"type": "title"},
        "Email": {"type": "email"},
        "Phone": {"type": "phone"},
        "Company": {"type": "text"}
    }
)
```

---

## Retrieve a Database

Retrieves a Database object for a provided database ID.

### Endpoint

```
GET https://api.notion.com/v1/databases/{database_id}
```

### Path Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `database_id` | string (UUID) | Yes | ID of a Notion database (with or without dashes) |

### Headers

| Header | Type | Required | Description |
|--------|------|----------|-------------|
| `Authorization` | string | Yes | Bearer `{integration_token}` |
| `Notion-Version` | string | Yes | The API version to use (latest: `2025-09-03`) |

### Required Capabilities

This endpoint requires the **read content** capability.

### Response

Returns a Database object containing metadata and references to data sources.

```json
{
  "object": "database",
  "id": "248104cd-477e-80fd-b757-e945d38000bd",
  "title": [
    {
      "type": "text",
      "text": {
        "content": "My Task Tracker",
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
      "plain_text": "My Task Tracker",
      "href": null
    }
  ],
  "parent": {
    "type": "page_id",
    "page_id": "255104cd-477e-808c-b279-d39ab803a7d2"
  },
  "is_inline": false,
  "in_trash": false,
  "created_time": "2025-08-07T10:11:07.504-07:00",
  "last_edited_time": "2025-08-10T15:53:11.386-07:00",
  "data_sources": [
    {
      "id": "248104cd-477e-80af-bc30-000bd28de8f9",
      "name": "My Task Tracker"
    }
  ],
  "icon": null,
  "cover": null
}
```

**Important Notes:**

1. **data_sources array** - Contains IDs and names of all data sources
2. **Property schemas** - Are NOT included (retrieve data source to get schema)
3. **Use data source IDs** - For data source operations (retrieve, update, query)

### Finding Database ID

Navigate to the database URL in Notion:
```
https://www.notion.so/workspace/{database-id}?v=...
                     ^^^^^^^^^^^^^^
                     This is the database ID
```

The ID is a 32-character alphanumeric string (UUIDv4).

### SDK Implementation

```python
async def get(self, database_id: str) -> Database:
    """
    Retrieve a database by ID.

    Args:
        database_id: The UUID of the database

    Returns:
        Database object

    Raises:
        NotFoundError: If database doesn't exist
        PermissionError: If lacking read content capability
    """
    response = await self._client.request(
        "GET",
        f"/databases/{database_id}"
    )

    return Database.from_dict(response, self._client)

async def get_with_data_sources(
    self,
    database_id: str
) -> Database:
    """
    Retrieve a database with all data sources loaded.

    Args:
        database_id: The UUID of the database

    Returns:
        Database object with data sources loaded
    """
    database = await self.get(database_id)

    # Load all data sources
    database.data_sources = []
    for ds_ref in database.data_source_references:
        data_source = await self._client.data_sources.get(ds_ref.id)
        database.data_sources.append(data_source)

    return database
```

### Errors

| Status Code | Error | Description |
|-------------|-------|-------------|
| 404 | `object_not_found` | Database doesn't exist or no access |
| 403 | `missing_permission` | Integration lacks read content capability |
| 429 | `rate_limited` | Request rate limit exceeded |

### Example Usage

```python
# Get a database
database = await client.databases.get("database-id-here")

print(f"Database: {database.title_plain}")
print(f"Parent: {database.parent.type}")
print(f"Data sources: {len(database.data_source_references)}")

# Access data source IDs
for ds in database.data_source_references:
    print(f"  - {ds.name}: {ds.id}")

# Get database with data sources
database_with_sources = await client.databases.get_with_data_sources("database-id")

# Access first data source's properties
if database_with_sources.data_sources:
    first_ds = database_with_sources.data_sources[0]
    print(f"Properties: {list(first_ds.properties.keys())}")
```

---

## Update a Database

Updates the attributes of a database (title, description, icon, cover, parent, etc.).

### Endpoint

```
PATCH https://api.notion.com/v1/databases/{database_id}
```

### Path Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `database_id` | string (UUID) | Yes | ID of a Notion database (with or without dashes) |

### Body Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `parent` | object | No | Move database to new parent |
| `title` | array | No | Updated title (rich text array) |
| `description` | array | No | Updated description (rich text array) |
| `icon` | object | No | Updated icon or null to remove |
| `cover` | object | No | Updated cover or null to remove |
| `is_inline` | boolean | No | Whether database should be inline |
| `in_trash` | boolean | No | Archive/unarchive database |
| `is_locked` | boolean | No | Lock from UI editing |

**Important:** To update data source properties, use the **Update a Data Source** API (not this endpoint).

### Update Title

```json
{
  "title": [
    {
      "type": "text",
      "text": {
        "content": "Updated Database Name"
      }
    }
  ]
}
```

### Update Description

```json
{
  "description": [
    {
      "type": "text",
      "text": {
        "content": "This database tracks all project tasks"
      }
    }
  ]
}
```

### Update Icon

```json
{
  "icon": {
    "type": "emoji",
    "emoji": "✅"
  }
}
```

**Remove icon:**
```json
{
  "icon": null
}
```

### Update Cover

```json
{
  "cover": {
    "type": "external",
    "external": {
      "url": "https://example.com/new-cover.jpg"
    }
  }
}
```

**Remove cover:**
```json
{
  "cover": null
}
```

### Move Database

```json
{
  "parent": {
    "type": "page_id",
    "page_id": "new-parent-page-id"
  }
}
```

### Archive Database

```json
{
  "in_trash": true
}
```

### Lock Database

```json
{
  "is_locked": true
}
```

### Headers

| Header | Type | Required | Description |
|--------|------|----------|-------------|
| `Authorization` | string | Yes | Bearer `{integration_token}` |
| `Content-Type` | string | Yes | `application/json` |
| `Notion-Version` | string | Yes | The API version to use (latest: `2025-09-03`) |

### Required Capabilities

This endpoint requires the **update content** capability.

### Response

Returns the updated Database object.

```json
{
  "object": "database",
  "id": "248104cd-477e-80fd-b757-e945d38000bd",
  "title": [
    {
      "type": "text",
      "text": {
        "content": "My Task Tracker",
        "link": null
      },
      "plain_text": "My Task Tracker",
      "href": null
    }
  ],
  "parent": {
    "type": "page_id",
    "page_id": "255104cd-477e-808c-b279-d39ab803a7d2"
  },
  "is_inline": false,
  "in_trash": false,
  "is_locked": false,
  "created_time": "2025-08-07T10:11:07.504-07:00",
  "last_edited_time": "2025-08-10T15:53:11.386-07:00",
  "data_sources": [
    {
      "id": "248104cd-477e-80af-bc30-000bd28de8f9",
      "name": "My Task Tracker"
    }
  ],
  "icon": null,
  "cover": null
}
```

### SDK Implementation

```python
async def update(
    self,
    database_id: str,
    *,
    title: Optional[List[dict]] = None,
    description: Optional[List[dict]] = None,
    icon: Optional[dict] = None,
    cover: Optional[dict] = None,
    parent: Optional[dict] = None,
    is_inline: Optional[bool] = None,
    in_trash: Optional[bool] = None,
    is_locked: Optional[bool] = None
) -> Database:
    """
    Update a database's attributes.

    Args:
        database_id: The UUID of the database
        title: New title (rich text array)
        description: New description
        icon: New icon or None to remove
        cover: New cover or None to remove
        parent: New parent (move database)
        is_inline: Inline display status
        in_trash: Archive status
        is_locked: Lock from UI editing

    Returns:
        Updated Database object

    Raises:
        NotFoundError: If database doesn't exist
        PermissionError: If lacking update content capability
    """
    payload = {}

    if title is not None:
        payload["title"] = title
    if description is not None:
        payload["description"] = description
    if icon is not None:
        payload["icon"] = icon
    if cover is not None:
        payload["cover"] = cover
    if parent is not None:
        payload["parent"] = parent
    if is_inline is not None:
        payload["is_inline"] = is_inline
    if in_trash is not None:
        payload["in_trash"] = in_trash
    if is_locked is not None:
        payload["is_locked"] = is_locked

    response = await self._client.request(
        "PATCH",
        f"/databases/{database_id}",
        json=payload
    )

    return Database.from_dict(response, self._client)

async def archive(self, database_id: str) -> Database:
    """Archive a database."""
    return await self.update(database_id, in_trash=True)

async def restore(self, database_id: str) -> Database:
    """Restore an archived database."""
    return await self.update(database_id, in_trash=False)
```

### Errors

| Status Code | Error | Description |
|-------------|-------|-------------|
| 400 | `bad_request` | Invalid request format |
| 403 | `missing_permission` | Integration lacks update content capability |
| 404 | `object_not_found` | Database doesn't exist |
| 429 | `rate_limited` | Request rate limit exceeded |

### Example Usage

```python
# Update title and description
database = await client.databases.update(
    database_id="database-id",
    title=[{
        "type": "text",
        "text": {"content": "Updated Name"}
    }],
    description=[{
        "type": "text",
        "text": {"content": "New description"}
    }]
)

# Update icon
database = await client.databases.update(
    database_id="database-id",
    icon={"type": "emoji", "emoji": "🎯"}
)

# Remove cover
database = await client.databases.update(
    database_id="database-id",
    cover=None
)

# Move database
database = await client.databases.update(
    database_id="database-id",
    parent={
        "type": "page_id",
        "page_id": "new-parent-id"
    }
)

# Archive database
database = await client.databases.archive("database-id")

# Lock from UI editing
database = await client.databases.update(
    database_id="database-id",
    is_locked=True
)
```

---

## Query a Data Source

Queries a data source to retrieve pages that match the criteria.

### Endpoint

```
POST https://api.notion.com/v1/data_sources/{data_source_id}/query
```

### Path Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `data_source_id` | string (UUID) | Yes | ID of the data source to query |

### Body Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `filter` | object | No | Filter criteria |
| `sorts` | array | No | Sort order |
| `start_cursor` | string | No | Cursor for pagination |
| `page_size` | integer | No | Number of results (max: 100) |

### Filter Object

```json
{
  "filter": {
    "property": "Status",
    "select": {
      "equals": "In Progress"
    }
  }
}
```

### Sort Object

```json
{
  "sorts": [
    {
      "property": "Due Date",
      "direction": "ascending"
    },
    {
      "property": "Priority",
      "direction": "descending"
    }
  ]
}
```

### Headers

| Header | Type | Required | Description |
|--------|------|----------|-------------|
| `Authorization` | string | Yes | Bearer `{integration_token}` |
| `Content-Type` | string | Yes | `application/json` |
| `Notion-Version` | string | Yes | The API version to use (latest: `2025-09-03`) |

### Response

```json
{
  "object": "list",
  "results": [
    {
      "object": "page",
      "id": "page-id-1",
      "parent": {
        "type": "data_source_id",
        "data_source_id": "data-source-id"
      },
      "properties": {
        "Name": {
          "title": [{"text": {"content": "Task 1"}}]
        },
        "Status": {
          "select": {"name": "In Progress"}
        }
      }
    }
  ],
  "next_cursor": "cursor-string",
  "has_more": false
}
```

### SDK Implementation

```python
async def query_data_source(
    self,
    data_source_id: str,
    *,
    filter: Optional[dict] = None,
    sorts: Optional[List[dict]] = None,
    page_size: int = 100,
    start_cursor: Optional[str] = None
) -> PaginatedResponse:
    """
    Query a data source.

    Args:
        data_source_id: The UUID of the data source
        filter: Optional filter criteria
        sorts: Optional sort configuration
        page_size: Number of results per page
        start_cursor: Pagination cursor

    Returns:
        PaginatedResponse with page results

    Raises:
        NotFoundError: If data source doesn't exist
        PermissionError: If lacking read content capability
    """
    payload = {}

    if filter:
        payload["filter"] = filter
    if sorts:
        payload["sorts"] = sorts
    if page_size:
        payload["page_size"] = page_size
    if start_cursor:
        payload["start_cursor"] = start_cursor

    response = await self._client.request(
        "POST",
        f"/data_sources/{data_source_id}/query",
        json=payload
    )

    return PaginatedResponse(
        results=[
            Page.from_dict(page_data, self._client)
            for page_data in response.get("results", [])
        ],
        has_more=response.get("has_more", False),
        next_cursor=response.get("next_cursor")
    )

async def query_all(
    self,
    data_source_id: str,
    *,
    filter: Optional[dict] = None,
    sorts: Optional[List[dict]] = None
) -> List[Page]:
    """
    Query all pages in a data source (with automatic pagination).

    Args:
        data_source_id: The UUID of the data source
        filter: Optional filter criteria
        sorts: Optional sort configuration

    Returns:
        List of all matching pages
    """
    all_pages = []
    cursor = None
    has_more = True

    while has_more:
        response = await self.query_data_source(
            data_source_id,
            filter=filter,
            sorts=sorts,
            start_cursor=cursor
        )

        all_pages.extend(response.results)
        has_more = response.has_more
        cursor = response.next_cursor

    return all_pages
```

### Errors

| Status Code | Error | Description |
|-------------|-------|-------------|
| 400 | `bad_request` | Invalid filter or sort |
| 403 | `missing_permission` | Integration lacks read content capability |
| 404 | `object_not_found` | Data source doesn't exist |
| 429 | `rate_limited` | Request rate limit exceeded |

### Example Usage

```python
# Query all pages
pages = await client.data_sources.query_all("data-source-id")

# Query with filter
filtered_pages = await client.data_sources.query_all(
    "data-source-id",
    filter={
        "property": "Status",
        "select": {
            "equals": "In Progress"
        }
    }
)

# Query with sorting
sorted_pages = await client.data_sources.query_all(
    "data-source-id",
    sorts=[
        {
            "property": "Due Date",
            "direction": "ascending"
        }
    ]
)

# Paginate manually
cursor = None
while True:
    response = await client.data_sources.query_data_source(
        "data-source-id",
        start_cursor=cursor,
        page_size=50
    )

    for page in response.results:
        process_page(page)

    if not response.has_more:
        break

    cursor = response.next_cursor
```

---

## Database vs Data Source Operations

Understanding the distinction between database and data source operations is critical with the post-September 2025 architecture.

### Database Operations

**Scope:** Database-level attributes

| Operation | Endpoint | Description |
|-----------|----------|-------------|
| Create database | `POST /databases` | Create database + initial data source |
| Retrieve database | `GET /databases/{id}` | Get database metadata |
| Update database | `PATCH /databases/{id}` | Update title, icon, cover, parent |
| Archive database | `PATCH /databases/{id}` | Set `in_trash: true` |

**What you CAN update at database level:**
- Title
- Description
- Icon
- Cover
- Parent (move database)
- `is_inline` status
- `in_trash` (archive)
- `is_locked`

**What you CANNOT update at database level:**
- Data source properties (use Update Data Source)
- Pages within data sources (use Page/Query Data Source APIs)

### Data Source Operations

**Scope:** Individual data source within a database

| Operation | Endpoint | Description |
|-----------|----------|-------------|
| Retrieve data source | `GET /data_sources/{id}` | Get data source with properties |
| Update data source | `PATCH /data_sources/{id}` | Update properties/schema |
| Query data source | `POST /data_sources/{id}/query` | Query pages in data source |
| Create data source | `POST /data_sources` | Add new data source to database |

**What you CAN update at data source level:**
- Properties schema
- Property names
- Property types
- Property options (for select, status, multi_select)

### Common Workflows

#### 1. Create a Database with Pages

```python
# Create database with initial data source
database = await client.databases.create(
    parent="page-id",
    title="Tasks",
    initial_data_source={
        "name": "Tasks",
        "properties": {
            "Name": {"type": "title", "title": {}},
            "Status": {
                "type": "select",
                "select": {
                    "options": [
                        {"name": "To Do"},
                        {"name": "Done"}
                    ]
                }
            }
        }
    }
)

# Get data source ID
data_source_id = database.data_sources[0].id

# Create pages in the data source
page1 = await client.pages.create(
    parent={"type": "data_source_id", "data_source_id": data_source_id},
    properties={
        "Name": {"title": [{"text": {"content": "First Task"}}]},
        "Status": {"select": {"name": "To Do"}}
    }
)
```

#### 2. Query and Update Pages

```python
# Query data source
pages = await client.data_sources.query_all(
    "data-source-id",
    filter={
        "property": "Status",
        "select": {"equals": "To Do"}
    }
)

# Update matching pages
for page in pages:
    await client.pages.update(
        page.id,
        properties={
            "Status": {"select": {"name": "Done"}}
        }
    )
```

#### 3. Update Data Source Schema

```python
# Add new property to data source
updated_ds = await client.data_sources.update(
    "data-source-id",
    properties={
        "Name": {"type": "title", "title": {}},
        "Status": {
            "type": "select",
            "select": {
                "options": [
                    {"name": "To Do"},
                    {"name": "Done"},
                    {"name": "In Progress"}  # New option
                ]
            }
        },
        "Priority": {  # New property
            "type": "select",
            "select": {
                "options": [
                    {"name": "Low"},
                    {"name": "High"}
                ]
            }
        }
    }
)
```

#### 4. Add Second Data Source

```python
# Create additional data source in existing database
new_data_source = await client.data_sources.create(
    database_id="database-id",
    name="Archived Tasks",
    properties={
        "Name": {"type": "title", "title": {}},
        "Completed Date": {"type": "date", "date": {}}
    }
)
```

### Quick Reference

| Task | API | Notes |
|------|-----|-------|
| Create database | `POST /databases` | Includes initial data source |
| Get database info | `GET /databases/{id}` | Returns data source IDs |
| Update database title/icon | `PATCH /databases/{id}` | Database-level only |
| Get data source schema | `GET /data_sources/{id}` | Properties definition |
| Update schema | `PATCH /data_sources/{id}` | Add/edit properties |
| Query pages | `POST /data_sources/{id}/query` | Filter/sort pages |
| Create page | `POST /pages` | Use `data_source_id` as parent |
| Update page | `PATCH /pages/{id}` | Update page properties |

---

## Common Patterns

### Create Task Database with Template

```python
async def create_task_database(
    self,
    parent_page_id: str,
    name: str
) -> Database:
    """Create a ready-to-use task database."""
    database = await self.create(
        parent=parent_page_id,
        title=[{"type": "text", "text": {"content": name}}],
        icon={"type": "emoji", "emoji": "📋"},
        initial_data_source={
            "name": name,
            "properties": {
                "Task": {
                    "type": "title",
                    "title": {}
                },
                "Status": {
                    "type": "select",
                    "select": {
                        "options": [
                            {"name": "Not Started", "color": "gray"},
                            {"name": "In Progress", "color": "blue"},
                            {"name": "Completed", "color": "green"}
                        ]
                    }
                },
                "Priority": {
                    "type": "select",
                    "select": {
                        "options": [
                            {"name": "Low", "color": "gray"},
                            {"name": "Medium", "color": "yellow"},
                            {"name": "High", "color": "red"}
                        ]
                    }
                },
                "Due Date": {
                    "type": "date",
                    "date": {}
                },
                "Assignee": {
                    "type": "people",
                    "people": {}
                },
                "Tags": {
                    "type": "multi_select",
                    "multi_select": {
                        "options": [
                            {"name": "Bug", "color": "red"},
                            {"name": "Feature", "color": "blue"},
                            {"name": "Improvement", "color": "green"}
                        ]
                    }
                }
            }
        }
    )

    return database
```

### Bulk Create Pages

```python
async def bulk_create_pages(
    self,
    data_source_id: str,
    page_data: List[dict]
) -> List[Page]:
    """
    Create multiple pages in a data source.

    Args:
        data_source_id: Target data source
        page_data: List of property dicts

    Returns:
        List of created pages
    """
    created_pages = []

    for data in page_data:
        page = await self._client.pages.create(
            parent={
                "type": "data_source_id",
                "data_source_id": data_source_id
            },
            properties=data
        )
        created_pages.append(page)

    return created_pages
```

### Database Factory

```python
class DatabaseFactory:
    """Factory for creating common database types."""

    @staticmethod
    async def create_task_tracker(client, parent_id: str, name: str) -> Database:
        """Create a task tracking database."""
        # Implementation...

    @staticmethod
    async def create_contact_list(client, parent_id: str, name: str) -> Database:
        """Create a contact database."""
        return await client.databases.create_simple_database(
            parent=parent_id,
            name=name,
            properties={
                "Name": {"type": "title"},
                "Email": {"type": "email"},
                "Phone": {"type": "phone"},
                "Company": {"type": "text"},
                "Tags": {
                    "type": "multi_select",
                    "multi_select": {
                        "options": [
                            {"name": "Customer", "color": "blue"},
                            {"name": "Lead", "color": "green"}
                        ]
                    }
                }
            }
        )

    @staticmethod
    async def create_project_roadmap(client, parent_id: str, name: str) -> Database:
        """Create a project roadmap database."""
        return await client.databases.create_simple_database(
            parent=parent_id,
            name=name,
            properties={
                "Feature": {"type": "title"},
                "Status": {
                    "type": "select",
                    "select": {
                        "options": [
                            {"name": "Backlog", "color": "gray"},
                            {"name": "In Progress", "color": "blue"},
                            {"name": "Shipped", "color": "green"}
                        ]
                    }
                },
                "Sprint": {"type": "select"},
                "Priority": {
                    "type": "select",
                    "select": {
                        "options": [
                            {"name": "P0", "color": "red"},
                            {"name": "P1", "color": "orange"},
                            {"name": "P2", "color": "yellow"}
                        ]
                    }
                },
                "Assignee": {"type": "people"},
                "Due Date": {"type": "date"}
            }
        )
```

---

## Error Handling

### Database Error Classes

```python
class DatabaseAPIError(Exception):
    """Base exception for database API errors."""
    pass

class DatabaseNotFoundError(DatabaseAPIError):
    """Database doesn't exist."""
    pass

class DataSourceNotFoundError(DatabaseAPIError):
    """Data source doesn't exist."""
    pass

class DatabasePermissionError(DatabaseAPIError):
    """Missing required capability."""
    pass

class DatabaseValidationError(DatabaseAPIError):
    """Invalid schema or data."""
    pass

async def handle_database_errors(func):
    """Decorator for database API error handling."""
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except HTTPError as e:
            if e.status == 404:
                raise DatabaseNotFoundError(f"Database not found: {e}")
            elif e.status == 403:
                raise DatabasePermissionError(f"Permission denied: {e}")
            elif e.status == 400:
                raise DatabaseValidationError(f"Invalid request: {e}")
            elif e.status == 429:
                await asyncio.sleep(1)
                return await func(*args, **kwargs)
            else:
                raise DatabaseAPIError(f"Unexpected error: {e}")
    return wrapper
```

---

## Best Practices

1. **Data Source IDs**: Always use `data_source_id` (not `database_id`) for page operations and queries
2. **Schema Validation**: Validate property schemas before creating data sources
3. **Pagination**: Use automatic pagination for large data sources
4. **Error Handling**: Implement proper error handling for 404, 403, 400 responses
5. **Property Types**: Know which property types can be created via API (status properties not supported)
6. **Database vs Data Source**: Understand what operations are database-level vs data source-level
7. **Bulk Operations**: Use batching for creating multiple pages
8. **Filtering**: Use filters at query time rather than fetching all pages
9. **Rate Limiting**: Implement retry logic for rate-limited requests
10. **Archival**: Use `in_trash` to archive (soft delete) databases

---

## Related Documentation

- [Databases Overview](./databases-overview.md) - Database concepts and architecture
- [Data Sources](./data-sources.md) - Data source operations and properties
- [Database Implementation](./database-implementation.md) - SDK implementation guide
- [Users API](../users-api.md) - User information for created_by/last_edited_by
- [Pages API](../pages/pages-api.md) - Creating and updating pages
- [Page Properties](../pages/page-properties.md) - Property value reference
