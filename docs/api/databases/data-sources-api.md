# Data Sources API Reference

Complete API reference for all data source operations in the Notion API.

**Important:** Data sources are the individual tables within a database container. Each data source has its own property schema and contains pages (rows).

## Table of Contents

1. [Create a Data Source](#create-a-data-source)
2. [Retrieve a Data Source](#retrieve-a-data-source)
3. [Update a Data Source](#update-a-data-source)
4. [Query a Data Source](#query-a-data-source)
5. [Filter Data Source Entries](#filter-data-source-entries)
6. [Sort Data Source Entries](#sort-data-source-entries)
7. [List Data Source Templates](#list-data-source-templates)

---

## Create a Data Source

Adds an additional data source to an existing database.

### Endpoint

```
POST https://api.notion.com/v1/data_sources
```

### Body Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `parent` | object | Yes | Parent database for the data source |
| `properties` | object | Yes | Property schema for the new data source |
| `title` | array | No | Title of the data source (rich text) |
| `icon` | object | No | Icon for the data source |

### Parent Object

```json
{
  "parent": {
    "type": "database_id",
    "database_id": "6ee911d9-189c-4844-93e8-260c1438b6e4"
  }
}
```

### Properties Schema

```json
{
  "properties": {
    "Title": {
      "type": "title",
      "title": {}
    },
    "Count": {
      "type": "number",
      "number": {}
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
    "Tags": {
      "type": "multi_select",
      "multi_select": {
        "options": [
          {"name": "Urgent", "color": "red"},
          {"name": "Feature", "color": "blue"}
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
    "Description": {
      "type": "rich_text",
      "rich_text": {}
    },
    "Completed": {
      "type": "checkbox",
      "checkbox": {}
    },
    "Website": {
      "type": "url",
      "url": {}
    },
    "Email": {
      "type": "email",
      "email": {}
    },
    "Phone": {
      "type": "phone_number",
      "phone_number": {}
    },
    "Files": {
      "type": "files",
      "files": {}
    }
  }
}
```

### Title (Optional)

```json
{
  "title": [
    {
      "type": "text",
      "text": {
        "content": "New child data source"
      }
    }
  ]
}
```

### Icon (Optional)

**Emoji:**
```json
{
  "icon": {
    "type": "emoji",
    "emoji": "📊"
  }
}
```

**External file:**
```json
{
  "icon": {
    "type": "external",
    "external": {
      "url": "https://website.domain/images/image.png"
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

This endpoint requires the **insert content** capability on the parent database.

### Response

Returns the created Data Source object.

```json
{
  "object": "data_source",
  "id": "bc1211cae3f14939ae34260b16f627c",
  "parent": {
    "type": "database_id",
    "database_id": "6ee911d9-189c-4844-93e8-260c1438b6e4"
  },
  "database_parent": {
    "type": "page_id",
    "page_id": "98ad959b-2b6a-4774-80ee-00246fb0ea9b"
  },
  "title": [
    {
      "type": "text",
      "text": {
        "content": "Grocery List"
      }
    }
  ],
  "icon": {
    "type": "emoji",
    "emoji": "🎉"
  },
  "properties": {
    "Title": {
      "id": "title",
      "name": "Title",
      "type": "title",
      "title": {}
    },
    "Count": {
      "id": "J@cT",
      "name": "Count",
      "type": "number",
      "number": {}
    }
  },
  "archived": false,
  "is_inline": false,
  "url": "https://www.notion.so/bc1211cae3f14939ae34260b16f627c"
}
```

**Note:** A standard "table" view is automatically created. Views cannot be customized via API.

### SDK Implementation

```python
async def create(
    self,
    *,
    parent: str,
    properties: dict,
    title: Optional[str] = None,
    icon: Optional[dict] = None
) -> DataSource:
    """
    Create a new data source in a database.

    Args:
        parent: Parent database ID
        properties: Property schema
        title: Optional data source title
        icon: Optional data source icon

    Returns:
        Created DataSource object

    Raises:
        ValueError: If properties are invalid
        PermissionError: If lacking insert content capability
    """
    payload = {
        "parent": {
            "type": "database_id",
            "database_id": parent
        },
        "properties": properties
    }

    if title:
        payload["title"] = [{
            "type": "text",
            "text": {"content": title}
        }]

    if icon:
        payload["icon"] = icon

    response = await self._client.request(
        "POST",
        "/data_sources",
        json=payload
    )

    return DataSource.from_dict(response, self._client)
```

### Errors

| Status Code | Error | Description |
|-------------|-------|-------------|
| 400 | `bad_request` | Invalid properties schema |
| 400 | `validation_error` | Schema too large (>50KB) |
| 403 | `missing_permission` | Integration lacks insert content capability |
| 404 | `object_not_found` | Parent database doesn't exist |
| 429 | `rate_limited` | Request rate limit exceeded |

### Example Usage

```python
# Create a simple data source
data_source = await client.data_sources.create(
    parent="database-id",
    title="Archive",
    properties={
        "Name": {
            "type": "title",
            "title": {}
        },
        "Archived Date": {
            "type": "date",
            "date": {}
        },
        "Reason": {
            "type": "select",
            "select": {
                "options": [
                    {"name": "Completed", "color": "green"},
                    {"name": "Cancelled", "color": "red"}
                ]
            }
        }
    }
)

print(f"Created data source: {data_source.id}")
print(f"URL: {data_source.url}")
```

---

## Retrieve a Data Source

Retrieves a data source object for a provided data source ID.

### Endpoint

```
GET https://api.notion.com/v1/data_sources/{data_source_id}
```

### Path Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `data_source_id` | string (UUID) | Yes | ID of a Notion data source |

### Finding Data Source ID

**Method 1: From Database**
1. Get database ID from URL
2. Call `GET /databases/{database_id}`
3. Extract ID from `data_sources` array

**Method 2: From Notion App**
1. Open database in Notion
2. Click ••• menu → Settings
3. Scroll to "Manage data sources"
4. Click "Copy data source ID"

### Headers

| Header | Type | Required | Description |
|--------|------|----------|-------------|
| `Authorization` | string | Yes | Bearer `{integration_token}` |
| `Notion-Version` | string | Yes | The API version to use (latest: `2025-09-03`) |

### Required Capabilities

This endpoint requires the **read content** capability.

### Response

Returns a Data Source object with properties schema.

```json
{
  "object": "data_source",
  "id": "b55c9c91-384d-452b-81db-d1ef79372b75",
  "parent": {
    "type": "database_id",
    "database_id": "6ee911d9-189c-4844-93e8-260c1438b6e4"
  },
  "database_parent": {
    "type": "page_id",
    "page_id": "98ad959b-2b6a-4774-80ee-00246fb0ea9b"
  },
  "created_time": "2025-08-07T10:11:07.504-07:00",
  "created_by": {
    "object": "user",
    "id": "45ee8d13-687b-47ce-a5ca-6e45548c4b"
  },
  "last_edited_time": "2025-08-10T15:53:11.386-07:00",
  "last_edited_by": {
    "object": "user",
    "id": "45ee8d13-687b-47ce-a5ca-6e45548c4b"
  },
  "title": [
    {
      "type": "text",
      "text": {
        "content": "Grocery List"
      }
    }
  ],
  "description": [],
  "icon": {
    "type": "emoji",
    "emoji": "🎉"
  },
  "cover": {
    "type": "external",
    "external": {
      "url": "https://website.domain/images/image.png"
    }
  },
  "properties": {
    "In stock": {
      "id": "%60%5Bq%3F",
      "name": "In stock",
      "type": "checkbox",
      "checkbox": {}
    },
    "Food group": {
      "id": "A%40Hk",
      "name": "Food group",
      "type": "select",
      "select": {
        "options": [
          {
            "id": "468cc207-2cc3-45f2-9e04-23032f29faab",
            "name": "Vegetable",
            "color": "green"
          },
          {
            "id": "bbcbf1c3-5c72-4021-8e23-60870c19ef9a",
            "name": "Fruit",
            "color": "yellow"
          }
        ]
      }
    },
    "Price": {
      "id": "BJXS",
      "name": "Price",
      "type": "number",
      "number": {
        "format": "dollar"
      }
    },
    "Cost of next trip": {
      "id": "WOd%3B",
      "name": "Cost of next trip",
      "type": "number",
      "number": {}
    },
    "Last ordered": {
      "id": "Jsfb",
      "name": "Last ordered",
      "type": "date",
      "date": {}
    },
    "Recipes": {
      "id": "YfIu",
      "name": "Recipes",
      "type": "relation",
      "relation": {
        "database_id": "68ef4233547c48289bccfe1aebc4cd86",
        "dual_property": {
          "database_id": "6ee911d9-189c-4844-93e8-260c1438b6e4",
          "property_id": "YfIu"
        }
      }
    },
    "Name": {
      "id": "title",
      "name": "Name",
      "type": "title",
      "title": {}
    }
  },
  "archived": false,
  "is_inline": false,
  "url": "https://www.notion.so/Grocery-List-b55c9c9184d452b81dbd1ef79372b75"
}
```

**Important Notes:**
- Contains full property schema (unlike database endpoint)
- Relations require related database to be shared with integration
- Linked data sources are not supported (share original source)

### SDK Implementation

```python
async def get(self, data_source_id: str) -> DataSource:
    """
    Retrieve a data source by ID.

    Args:
        data_source_id: The UUID of the data source

    Returns:
        DataSource object with full schema

    Raises:
        NotFoundError: If data source doesn't exist
        PermissionError: If lacking read content capability
    """
    response = await self._client.request(
        "GET",
        f"/data_sources/{data_source_id}"
    )

    return DataSource.from_dict(response, self._client)
```

### Errors

| Status Code | Error | Description |
|-------------|-------|-------------|
| 404 | `object_not_found` | Data source doesn't exist or no access |
| 403 | `missing_permission` | Integration lacks read content capability |
| 429 | `rate_limited` | Request rate limit exceeded |

### Example Usage

```python
# Get data source
data_source = await client.data_sources.get("data-source-id")

# Print properties
for prop_id, prop in data_source.properties.items():
    print(f"{prop.name}: {prop.type}")

# Get select options
if data_source.properties.get("Status"):
    status_prop = data_source.properties["Status"]
    if status_prop.type == "select":
        for option in status_prop.select.options:
            print(f"  - {option.name} ({option.color})")
```

---

## Update a Data Source

Updates a data source's properties, title, description, icon, or archived status.

### Endpoint

```
PATCH https://api.notion.com/v1/data_sources/{data_source_id}
```

### Path Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `data_source_id` | string (UUID) | Yes | ID of a Notion data source |

### Body Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `properties` | object | No | Updated properties schema |
| `title` | array | No | Updated title (rich text array) |
| `icon` | object | No | New icon or null to remove |
| `in_trash` | boolean | No | Archive/unarchive data source |
| `parent` | object | No | Move to different database |

### Properties Update

**Remove a property:**
```json
{
  "properties": {
    "OldProperty": null
  }
}
```

**Rename a property:**
```json
{
  "properties": {
    "OldName": {
      "name": "NewName"
    }
  }
}
```

**Update property type:**
```json
{
  "properties": {
    "PropertyName": {
      "type": "select",
      "select": {
        "options": [
          {"name": "Option 1", "color": "gray"},
          {"name": "Option 2", "color": "blue"}
        ]
      }
    }
  }
}
```

### Update Title

```json
{
  "title": [
    {
      "type": "text",
      "text": {"content": "New data source title"}
    }
  ]
}
```

### Update/Remove Icon

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

### Archive/Restore

```json
{
  "in_trash": true
}
```

### Move to Different Database

```json
{
  "parent": {
    "type": "database_id",
    "database_id": "new-database-id"
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

This endpoint requires the **update content** capability.

### Limitations

**Cannot update via API:**
- Formula properties
- Status properties
- Synced content properties
- Place properties

**Type Change Behavior:**
- Data is stored as rich text internally
- Notion converts presentation based on type
- Some conversions work (multi_select → people)
- Some lose data (people → file)

### Schema Size Limit

**Recommended maximum: 50KB**

Updates exceeding this limit will be blocked to maintain performance.

### Response

Returns the updated Data Source object.

```json
{
  "object": "data_source",
  "id": "b55c9c91-384d-452b-81db-d1ef79372b75",
  "parent": {
    "type": "database_id",
    "database_id": "6ee911d9-189c-4844-93e8-260c1438b6e4"
  },
  "database_parent": {
    "type": "page_id",
    "page_id": "98ad959b-2b6a-4774-80ee-00246fb0ea9b"
  },
  "title": [
    {
      "type": "text",
      "text": {"content": "New data source title"}
    }
  ],
  "icon": {
    "type": "emoji",
    "emoji": "🎉"
  },
  "properties": {
    "Website": {
      "type": "url",
      "url": {}
    }
  },
  "archived": false,
  "is_inline": false,
  "url": "https://www.notion.so/bc1211cae3f14939ae34260b16f627c"
}
```

### SDK Implementation

```python
async def update(
    self,
    data_source_id: str,
    *,
    properties: Optional[dict] = None,
    title: Optional[str] = None,
    icon: Optional[dict] = None,
    in_trash: Optional[bool] = None,
    parent: Optional[str] = None
) -> DataSource:
    """
    Update a data source.

    Args:
        data_source_id: The UUID of the data source
        properties: Updated properties schema
        title: New title
        icon: New icon or None to remove
        in_trash: Archive status
        parent: New parent database ID (move)

    Returns:
        Updated DataSource object

    Raises:
        NotFoundError: If data source doesn't exist
        PermissionError: If lacking update content capability
    """
    payload = {}

    if properties is not None:
        payload["properties"] = properties
    if title is not None:
        payload["title"] = [{
            "type": "text",
            "text": {"content": title}
        }]
    if icon is not None:
        payload["icon"] = icon
    if in_trash is not None:
        payload["in_trash"] = in_trash
    if parent is not None:
        payload["parent"] = {
            "type": "database_id",
            "database_id": parent
        }

    response = await self._client.request(
        "PATCH",
        f"/data_sources/{data_source_id}",
        json=payload
    )

    return DataSource.from_dict(response, self._client)

async def archive(self, data_source_id: str) -> DataSource:
    """Archive a data source."""
    return await self.update(data_source_id, in_trash=True)

async def restore(self, data_source_id: str) -> DataSource:
    """Restore an archived data source."""
    return await self.update(data_source_id, in_trash=False)
```

### Errors

| Status Code | Error | Description |
|-------------|-------|-------------|
| 400 | `bad_request` | Invalid properties or type change |
| 400 | `validation_error` | Schema too large |
| 403 | `missing_permission` | Integration lacks update content capability |
| 404 | `object_not_found` | Data source doesn't exist |
| 429 | `rate_limited` | Request rate limit exceeded |

### Example Usage

```python
# Add a new property
updated = await client.data_sources.update(
    "data-source-id",
    properties={
        "Name": {"type": "title", "title": {}},
        "Status": {"type": "select", "select": {
            "options": [
                {"name": "To Do", "color": "gray"},
                {"name": "Done", "color": "green"}
            ]
        }},
        "Priority": {  # New property
            "type": "select",
            "select": {
                "options": [
                    {"name": "Low", "color": "gray"},
                    {"name": "High", "color": "red"}
                ]
            }
        }
    }
)

# Remove a property
updated = await client.data_sources.update(
    "data-source-id",
    properties={
        "OldProperty": None
    }
)

# Rename property
updated = await client.data_sources.update(
    "data-source-id",
    properties={
        "Old Name": {"name": "New Name"}
    }
)

# Update title and icon
updated = await client.data_sources.update(
    "data-source-id",
    title="Updated Title",
    icon={"type": "emoji", "emoji": "📋"}
)

# Move to different database
moved = await client.data_sources.update(
    "data-source-id",
    parent="new-database-id"
)
```

---

## Query a Data Source

Gets a list of pages contained in the data source, filtered and ordered according to criteria.

### Endpoint

```
POST https://api.notion.com/v1/data_sources/{data_source_id}/query
```

### Path Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `data_source_id` | string (UUID) | Yes | ID of a Notion data source |

### Query Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `filter_properties` | array | No | Limit response to specific properties |

**Example:**
```
GET /data_sources/{id}/query?filter_properties[]=title&filter_properties[]=status
```

### Body Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `filter` | object | No | Filter conditions |
| `sorts` | array | No | Sort order |
| `start_cursor` | string | No | Pagination cursor |
| `page_size` | integer | No | Results per page (max: 100) |
| `result_type` | string | No | Filter to "page" or "data_source" (wikis only) |

### Filter Object

**Simple filter:**
```json
{
  "filter": {
    "property": "Task completed",
    "checkbox": {
      "equals": true
    }
  }
}
```

**Compound filter (AND):**
```json
{
  "filter": {
    "and": [
      {
        "property": "Done",
        "checkbox": {"equals": true}
      },
      {
        "property": "Working days",
        "number": {"greater_than": 10}
      }
    ]
  }
}
```

**Compound filter (OR):**
```json
{
  "filter": {
    "or": [
      {
        "property": "In stock",
        "checkbox": {"equals": true}
      },
      {
        "property": "Cost of next trip",
        "number": {"greater_than_or_equal_to": 2}
      }
    ]
  }
}
```

**Nested compound:**
```json
{
  "filter": {
    "and": [
      {
        "property": "Done",
        "checkbox": {"equals": true}
      },
      {
        "or": [
          {
            "property": "Tags",
            "rich_text": {"contains": "A"}
          },
          {
            "property": "Tags",
            "rich_text": {"contains": "B"}
          }
        ]
      }
    ]
  }
}
```

### Sort Object

```json
{
  "sorts": [
    {
      "property": "Last ordered",
      "direction": "ascending"
    },
    {
      "property": "Name",
      "direction": "descending"
    }
  ]
}
```

**Timestamp sort:**
```json
{
  "sorts": [
    {
      "timestamp": "created_time",
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

### Required Capabilities

This endpoint requires the **read content** capability.

### Response

```json
{
  "object": "list",
  "results": [
    {
      "object": "page",
      "id": "59833787-2cf9-4fdf-8782-e53db20768a5",
      "created_time": "2022-03-01T19:05:00.000Z",
      "last_edited_time": "2022-03-01T19:05:00.000Z",
      "parent": {
        "type": "data_source_id",
        "data_source_id": "897e5a76ae524b489fdfe71f5945d1af"
      },
      "archived": false,
      "properties": {
        "In stock": {
          "id": "%60%5Bq%3F",
          "type": "checkbox",
          "checkbox": true
        },
        "Name": {
          "id": "title",
          "type": "title",
          "title": [
            {
              "type": "text",
              "text": {
                "content": "Tuscan kale"
              }
            }
          ]
        }
      },
      "url": "https://www.notion.so/Tuscan-kale-598337872cf94fdf8782e53db20768a5"
    }
  ],
  "next_cursor": null,
  "has_more": false,
  "type": "page_or_data_source"
}
```

### Performance Recommendations

1. **Use `filter_properties`** - Limit properties in response
2. **Use specific filters** - Reduce result set size
3. **Divide large data sources** - Split if > several dozen thousand pages
4. **Prune complex properties** - Remove unused formulas/rollups
5. **Use webhooks** - Reduce polling needs

### SDK Implementation

```python
async def query(
    self,
    data_source_id: str,
    *,
    filter: Optional[dict] = None,
    sorts: Optional[List[dict]] = None,
    page_size: int = 100,
    start_cursor: Optional[str] = None,
    filter_properties: Optional[List[str]] = None
) -> PaginatedResponse:
    """
    Query a data source.

    Args:
        data_source_id: The UUID of the data source
        filter: Optional filter criteria
        sorts: Optional sort configuration
        page_size: Number of results per page (max: 100)
        start_cursor: Pagination cursor
        filter_properties: Properties to include in response

    Returns:
        PaginatedResponse with Page objects

    Raises:
        NotFoundError: If data source doesn't exist
        PermissionError: If lacking read content capability
    """
    params = {}
    payload = {}

    if filter_properties:
        # Build query params
        for prop in filter_properties:
            params.setdefault("filter_properties", []).append(prop)

    if page_size:
        payload["page_size"] = page_size
    if start_cursor:
        payload["start_cursor"] = start_cursor
    if filter:
        payload["filter"] = filter
    if sorts:
        payload["sorts"] = sorts

    response = await self._client.request(
        "POST",
        f"/data_sources/{data_source_id}/query",
        params=params,
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
    Query all pages with automatic pagination.

    Args:
        data_source_id: The UUID of the data source
        filter: Optional filter criteria
        sorts: Optional sort configuration

    Returns:
        List of all matching Page objects
    """
    all_pages = []
    cursor = None
    has_more = True

    while has_more:
        response = await self.query(
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
# Simple query
pages = await client.data_sources.query_all("data-source-id")

# Filtered query
pages = await client.data_sources.query_all(
    "data-source-id",
    filter={
        "property": "Status",
        "select": {"equals": "In Progress"}
    }
)

# Compound filter
pages = await client.data_sources.query_all(
    "data-source-id",
    filter={
        "and": [
            {"property": "Done", "checkbox": {"equals": true}},
            {"property": "Priority", "select": {"equals": "High"}}
        ]
    }
)

# Sorted query
pages = await client.data_sources.query_all(
    "data-source-id",
    sorts=[
        {"property": "Due Date", "direction": "ascending"},
        {"property": "Priority", "direction": "descending"}
    ]
)

# Filter properties for performance
pages = await client.data_sources.query(
    "data-source-id",
    filter_properties=["title", "status"]
)

# Manual pagination
cursor = None
while True:
    response = await client.data_sources.query(
        "data-source-id",
        start_cursor=cursor
    )

    for page in response.results:
        process(page)

    if not response.has_more:
        break

    cursor = response.next_cursor
```

---

## Filter Data Source Entries

Complete reference for filter conditions in data source queries.

### Checkbox Filter

```json
{
  "filter": {
    "property": "Task completed",
    "checkbox": {
      "equals": true
    }
  }
}
```

**Conditions:**
- `equals` (boolean)
- `does_not_equal` (boolean)

### Date Filter

```json
{
  "filter": {
    "property": "Due date",
    "date": {
      "on_or_after": "2023-02-08"
    }
  }
}
```

**Conditions:**
- `equals` (ISO 8601 date)
- `before` (ISO 8601 date)
- `after` (ISO 8601 date)
- `on_or_before` (ISO 8601 date)
- `on_or_after` (ISO 8601 date)
- `is_empty` (true)
- `is_not_empty` (true)
- `past_week` ({})
- `past_month` ({})
- `past_year` ({})
- `this_week` ({})
- `next_week` ({})
- `next_month` ({})
- `next_year` ({})

### Files Filter

```json
{
  "filter": {
    "property": "Attachments",
    "files": {
      "is_not_empty": true
    }
  }
}
```

**Conditions:**
- `is_empty` (true)
- `is_not_empty` (true)

### Formula Filter

Matches the formula result type:

```json
{
  "filter": {
    "property": "Deadline",
    "formula": {
      "date": {
        "after": "2021-05-10"
      }
    }
  }
}
```

**Conditions:**
- `checkbox` (checkbox filter)
- `date` (date filter)
- `number` (number filter)
- `string` (rich text filter)

### Multi-Select Filter

```json
{
  "filter": {
    "property": "Tags",
    "multi_select": {
      "contains": "Engineering"
    }
  }
}
```

**Conditions:**
- `contains` (string)
- `does_not_contain` (string)
- `is_empty` (true)
- `is_not_empty` (true)

### Number Filter

```json
{
  "filter": {
    "property": "Estimated days",
    "number": {
      "less_than_or_equal_to": 5
    }
  }
}
```

**Conditions:**
- `equals` (number)
- `does_not_equal` (number)
- `greater_than` (number)
- `greater_than_or_equal_to` (number)
- `less_than` (number)
- `less_than_or_equal_to` (number)
- `is_empty` (true)
- `is_not_empty` (true)

### People Filter

```json
{
  "filter": {
    "property": "Assignee",
    "people": {
      "contains": "user-id-here"
    }
  }
}
```

**Conditions:**
- `contains` (user UUID)
- `does_not_contain` (user UUID)
- `is_empty` (true)
- `is_not_empty` (true)

### Relation Filter

```json
{
  "filter": {
    "property": "Related Tasks",
    "relation": {
      "contains": "page-id-here"
    }
  }
}
```

**Conditions:**
- `contains` (page UUID)
- `does_not_contain` (page UUID)
- `is_empty` (true)
- `is_not_empty` (true)

### Rich Text Filter

```json
{
  "filter": {
    "property": "Description",
    "rich_text": {
      "contains": "keyword"
    }
  }
}
```

**Conditions:**
- `contains` (string)
- `does_not_contain` (string)
- `does_not_equal` (string)
- `ends_with` (string)
- `equals` (string)
- `starts_with` (string)
- `is_empty` (true)
- `is_not_empty` (true)

### Rollup Filter

**Array rollup:**
```json
{
  "filter": {
    "property": "Related tasks",
    "rollup": {
      "any": {
        "rich_text": {
          "contains": "Migrate"
        }
      }
    }
  }
}
```

**Date rollup:**
```json
{
  "filter": {
    "property": "Parent project due date",
    "rollup": {
      "date": {
        "on_or_before": "2023-02-08"
      }
    }
  }
}
```

**Number rollup:**
```json
{
  "filter": {
    "property": "Total days",
    "rollup": {
      "number": {
        "greater_than": 10
      }
    }
  }
}
```

**Conditions (for array):**
- `any` (filter condition)
- `every` (filter condition)
- `none` (filter condition)

### Select Filter

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

**Conditions:**
- `equals` (string)
- `does_not_equal` (string)
- `is_empty` (true)
- `is_not_empty` (true)

### Status Filter

```json
{
  "filter": {
    "property": "Project status",
    "status": {
      "equals": "Not started"
    }
  }
}
```

**Conditions:**
- `equals` (string)
- `does_not_equal` (string)
- `is_empty` (true)
- `is_not_empty` (true)

### Timestamp Filter

```json
{
  "filter": {
    "timestamp": "created_time",
    "created_time": {
      "on_or_before": "2022-10-13"
    }
  }
}
```

**Timestamps:**
- `created_time`
- `last_edited_time`

**Conditions:** (same as date filter)

### Verification Filter

```json
{
  "filter": {
    "property": "Email verification",
    "verification": {
      "status": "verified"
    }
  }
}
```

**Status values:**
- `verified`
- `expired`
- `none`

### Unique ID Filter

```json
{
  "filter": {
    "and": [
      {"property": "ID", "unique_id": {"greater_than": 1}},
      {"property": "ID", "unique_id": {"less_than": 3}}
    ]
  }
}
```

**Conditions:**
- `equals` (number)
- `does_not_equal` (number)
- `greater_than` (number)
- `greater_than_or_equal_to` (number)
- `less_than` (number)
- `less_than_or_equal_to` (number)

---

## Sort Data Source Entries

Sort the results of a data source query.

### Property Sort

```json
{
  "sorts": [
    {
      "property": "Name",
      "direction": "ascending"
    }
  ]
}
```

**Directions:**
- `ascending`
- `descending`

### Timestamp Sort

```json
{
  "sorts": [
    {
      "timestamp": "last_edited_time",
      "direction": "descending"
    }
  ]
}
```

**Timestamps:**
- `created_time`
- `last_edited_time`

### Nested Sort (Multiple Properties)

```json
{
  "sorts": [
    {
      "property": "Food group",
      "direction": "descending"
    },
    {
      "property": "Name",
      "direction": "ascending"
    }
  ]
}
```

**Note:** First sort takes precedence. Items with same first sort value are sorted by second criteria.

### SDK Implementation

```python
async def query_sorted(
    self,
    data_source_id: str,
    *,
    sorts: List[dict]
) -> List[Page]:
    """
    Query with sorting.

    Args:
        data_source_id: The UUID of the data source
        sorts: List of sort configurations

    Returns:
        List of sorted Page objects
    """
    return await self.query_all(
        data_source_id,
        sorts=sorts
    )
```

### Example Usage

```python
# Sort by property
pages = await client.data_sources.query_all(
    "data-source-id",
    sorts=[{
        "property": "Priority",
        "direction": "descending"
    }]
)

# Sort by timestamp
pages = await client.data_sources.query_all(
    "data-source-id",
    sorts=[{
        "timestamp": "created_time",
        "direction": "ascending"
    }]
)

# Multi-level sort
pages = await client.data_sources.query_all(
    "data-source-id",
    sorts=[
        {"property": "Category", "direction": "ascending"},
        {"property": "Name", "direction": "ascending"}
    ]
)
```

---

## List Data Source Templates

Retrieves all page templates available for a data source.

### Endpoint

```
GET https://api.notion.com/v1/data_sources/{data_source_id}/templates
```

### Path Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `data_source_id` | string (UUID) | Yes | ID of the Notion data source |

### Query Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `name` | string | No | Filter by name (case-insensitive substring) |
| `start_cursor` | string | No | Pagination cursor |
| `page_size` | integer | No | Results per page (max: 100) |

### Headers

| Header | Type | Required | Description |
|--------|------|----------|-------------|
| `Authorization` | string | Yes | Bearer `{integration_token}` |
| `Notion-Version` | string | Yes | The API version to use (latest: `2025-09-03`) |

### Response

```json
{
  "templates": [
    {
      "id": "a5da15f6-b853-455d-8827-f906fb52db2b",
      "name": "New Generic Task",
      "is_default": true
    },
    {
      "id": "9cc74169-8dd7-4104-8b36-ed952ac44bd0",
      "name": "New UI Task",
      "is_default": false
    },
    {
      "id": "f2d298e3-efeb-4401-bf4f-67e7b194694f",
      "name": "New Support Task",
      "is_default": false
    }
  ],
  "has_more": false,
  "next_cursor": null
}
```

### SDK Implementation

```python
async def list_templates(
    self,
    data_source_id: str,
    *,
    name: Optional[str] = None,
    page_size: int = 100
) -> List[dict]:
    """
    List templates for a data source.

    Args:
        data_source_id: The UUID of the data source
        name: Optional name filter
        page_size: Results per page

    Returns:
        List of template objects

    Raises:
        NotFoundError: If data source doesn't exist
    """
    params = {"page_size": page_size}

    if name:
        params["name"] = name

    response = await self._client.request(
        "GET",
        f"/data_sources/{data_source_id}/templates",
        params=params
    )

    return response.get("templates", [])
```

### Example Usage

```python
# Get all templates
templates = await client.data_sources.list_templates("data-source-id")

for template in templates:
    print(f"{template['name']} (default: {template['is_default']})")

# Get default template
templates = await client.data_sources.list_templates("data-source-id")
default = next((t for t in templates if t["is_default"]), None)

if default:
    print(f"Default template: {default['name']}")
    # Use template ID to create page
    await client.pages.create(
        parent={"type": "data_source_id", "data_source_id": "data-source-id"},
        properties={"Name": {"title": [{"text": {"content": "New Task"}}]}},
        template={
            "type": "template_id",
            "template_id": default["id"]
        }
    )
```

---

## Common Patterns

### Query with Multiple Filters

```python
async def find_high_priority_overdue(
    self,
    data_source_id: str
) -> List[Page]:
    """Find high priority overdue items."""
    today = datetime.now().date().isoformat()

    return await self.query_all(
        data_source_id,
        filter={
            "and": [
                {
                    "property": "Priority",
                    "select": {"equals": "High"}
                },
                {
                    "property": "Due Date",
                    "date": {"before": today}
                },
                {
                    "property": "Status",
                    "select": {"does_not_equal": "Completed"}
                }
            ]
        },
        sorts=[{
            "property": "Due Date",
            "direction": "ascending"
        }]
    )
```

### Batch Update Based on Query

```python
async def update_matching_pages(
    self,
    data_source_id: str,
    filter: dict,
    updates: dict
) -> List[Page]:
    """Query and update matching pages."""
    pages = await self.query_all(data_source_id, filter=filter)

    updated = []
    for page in pages:
        updated_page = await self._client.pages.update(
            page.id,
            properties=updates
        )
        updated.append(updated_page)

    return updated
```

### Sync External Data

```python
async def sync_external_data(
    self,
    data_source_id: str,
    external_items: List[dict]
) -> dict:
    """Sync external data to Notion data source."""
    # Get existing pages
    existing_pages = await self.query_all(data_source_id)
    existing_by_id = {p.properties["ID"].number: p for p in existing_pages}

    results = {
        "created": 0,
        "updated": 0,
        "unchanged": 0
    }

    for item in external_items:
        item_id = item["id"]

        if item_id in existing_by_id:
            # Update existing
            page = existing_by_id[item_id]
            # Compare and update if changed
            # ...
            results["updated"] += 1
        else:
            # Create new
            await self._client.pages.create(
                parent={
                    "type": "data_source_id",
                    "data_source_id": data_source_id
                },
                properties=item["properties"]
            )
            results["created"] += 1

    return results
```

---

## Best Practices

1. **Use filter_properties** - Only request needed properties for better performance
2. **Filter early** - Use specific filters to reduce result sets
3. **Paginate properly** - Handle has_more/next_cursor for large data sources
4. **Respect schema limits** - Keep schema under 50KB
5. **Share related databases** - For relations to work properly
6. **Optimize complex queries** - Simplify formulas/rollups when possible
7. **Use compound filters** - Combine multiple conditions efficiently
8. **Sort carefully** - First sort criterion takes precedence
9. **Archive unused data** - Archive old properties/data sources to improve performance
10. **Use templates** - Leverage templates for consistent page creation

---

## Related Documentation

- [Databases API Reference](./databases-api.md) - Database-level operations
- [Databases Overview](./databases-overview.md) - Database concepts
- [Data Sources](./data-sources.md) - Data source concepts
- [Users API](../users-api.md) - User information for people properties
- [Pages API](../pages/pages-api.md) - Creating/updating pages
- [Page Properties](../pages/page-properties.md) - Property values reference
