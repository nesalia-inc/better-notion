# Data Sources

## Overview

**Data Sources** are the individual tables of data that live under a Notion database. Pages are the items (or children) in a data source. Page property values must conform to the property objects laid out in the parent data source object.

### Data Model (Post-September 2025)

```
Database (parent)
└── Data Sources (1 or more)
    ├── Data Source 1
    │   ├── Properties (schema/columns)
    │   └── Pages (rows)
    └── Data Source 2
        ├── Properties (different schema)
        └── Pages (different rows)
```

Previously, databases could only have one data source, so the concepts were combined in the API until 2025.

## Data Source Object

### Object Fields

| Field | Type | Capability | Description | Example |
|-------|------|------------|-------------|---------|
| `object`* | string | None | Always `"data_source"` | `"data_source"` |
| `id`* | string (UUID) | None | Unique identifier | `"2f26ee68-..."` |
| `properties`* | object | None | Schema of properties (rendered as columns) | `{/* properties */}` |
| `parent` | object | Read content | Parent database reference | `{ "type": "database_id", ...}` |
| `database_parent` | object | Read content | Database's parent (data source's grandparent) | `{ "type": "page_id", ...}` |
| `created_time` | string (ISO 8601) | Read content | Creation timestamp | `"2020-03-17T19:10:04.968Z"` |
| `created_by` | PartialUser | Read content | User who created | `{ "object": "user", "id": "..."}` |
| `last_edited_time` | string (ISO 8601) | Read content | Last update timestamp | `"2020-03-17T21:49:37.913Z"` |
| `last_edited_by` | PartialUser | Read content | User who last edited | `{ "object": "user", "id": "..."}` |
| `title` | array of rich text | Read content | Name of the data source | `[/* rich text */]` |
| `description` | array of rich text | Read content | Description | `[/* rich text */]` |
| `icon` | FileObject \| Emoji | None | Data source icon | `{ "type": "emoji", ...}` |
| `archived` | boolean | None | Archived status | `false` |
| `in_trash` | boolean | Read content | Whether deleted | `false` |

* = Available to integrations with any capabilities

### Example Data Source Object

```json
{
  "object": "data_source",
  "id": "2f26ee68-df30-4251-aad4-8ddc420cba3d",
  "parent": {
    "type": "database_id",
    "database_id": "842a0286-cef0-46a8-abba-eac4c8ca644e"
  },
  "database_parent": {
    "type": "page_id",
    "page_id": "af5f89b5-a8ff-4c56-a5e8-69797d11b9f8"
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
  "icon": null,
  "archived": false,
  "in_trash": false,
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
  "properties": {
    "title": {
      "id": "title",
      "name": "Name",
      "type": "title",
      "title": {}
    },
    "status": {
      "id": "status",
      "name": "Status",
      "type": "status",
      "status": {
        "options": [/* ... */]
      }
    }
  }
}
```

### Important: Title vs Data Source Title

**Two different titles exist:**

1. **Data Source Title** (`title` field on data source object) - The overall title for the data source
2. **Title Property** (a property schema with `type: "title"`) - A column that defines page titles

Every data source requires both:
- A data source title (for display in database UI)
- A title property (so each page has a title)

## Data Source APIs

As of API version 2025-09-03, there's a suite of APIs for managing data sources:

- **Create a data source** - Add an additional data source for an existing database
- **Update a data source** - Update attributes, such as the properties, of a data source
- **Retrieve a data source** - Get full data source details
- **Query a data source** - Query pages in a data source

## Data Source Properties

Data source property objects are rendered in the Notion UI as data columns. All data source objects include a child `properties` object composed of individual data source property objects.

**Important:** If you're looking for information about how to work with data source **rows** (actual values), refer to the [Page Properties](../pages/page-properties.md) documentation. The API treats data source rows as pages.

### Property Object Structure

Every data source property object contains:

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `id` | string | Property identifier (short random string, or special IDs like "title") | `"fy:{"` |
| `name` | string | Property name as it appears in Notion | `"Status"` |
| `description` | string | Property description | `"Task completion status"` |
| `type` | string (enum) | Property type | `"rich_text"` |
| `{type}` | object | Type-specific configuration | Varies |

### Property Types

Complete list of data source property types:

#### Checkbox

Rendered as a column with checkboxes. No additional configuration.

```json
{
  "Task complete": {
    "id": "BBla",
    "name": "Task complete",
    "type": "checkbox",
    "checkbox": {}
  }
}
```

#### Created By

Rendered as a column with people mentions of each row's author. Empty configuration.

```json
{
  "Created by": {
    "id": "%5BJCR",
    "name": "Created by",
    "type": "created_by",
    "created_by": {}
  }
}
```

#### Created Time

Rendered as a column with timestamps of when each row was created. Empty configuration.

```json
{
  "Created time": {
    "id": "XcAf",
    "name": "Created time",
    "type": "created_time",
    "created_time": {}
  }
}
```

#### Date

Rendered as a column with date values. Empty configuration.

```json
{
  "Task due date": {
    "id": "AJP%7D",
    "name": "Task due date",
    "type": "date",
    "date": {}
  }
}
```

#### Email

Rendered as a column with email values. Empty configuration.

```json
{
  "Contact email": {
    "id": "oZbC",
    "name": "Contact email",
    "type": "email",
    "email": {}
  }
}
```

#### Files

Rendered as a column with files (uploaded to Notion or external links). Empty configuration.

```json
{
  "Product image": {
    "id": "pb%3E%5B",
    "name": "Product image",
    "type": "files",
    "files": {}
  }
}
```

#### Formula

Rendered as a column with values derived from a provided expression.

**Formula Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `expression` | string | Formula expression (Notion syntax) |

```json
{
  "Updated price": {
    "id": "YU%7C%40",
    "name": "Updated price",
    "type": "formula",
    "formula": {
      "expression": "{{notion:block_property:BtVS:...}}/2"
    }
  }
}
```

#### Last Edited By

Rendered as a column with people mentions of the person who last edited each row. Empty configuration.

```json
{
  "Last edited by": {
    "id": "...",
    "name": "Last edited by",
    "type": "last_edited_by",
    "last_edited_by": {}
  }
}
```

#### Last Edited Time

Rendered as a column with timestamps of when each row was last edited. Empty configuration.

```json
{
  "Last edited time": {
    "id": "jGdo",
    "name": "Last edited time",
    "type": "last_edited_time",
    "last_edited_time": {}
  }
}
```

#### Multi-Select

Rendered as a column where each row can contain one or multiple options from a defined set.

**Multi-Select Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `options` | array | Available options |

**Option Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `color` | string (enum) | Color: `blue`, `brown`, `default`, `gray`, `green`, `orange`, `pink`, `purple`, `red`, `yellow` |
| `id` | string | Unique identifier (doesn't change if name changes) |
| `name` | string | Option name (commas not valid; names must be unique ignoring case) |

```json
{
  "Store availability": {
    "id": "flsb",
    "name": "Store availability",
    "type": "multi_select",
    "multi_select": {
      "options": [
        {
          "id": "5de29601-9c24-4b04-8629-0bca891c5120",
          "name": "Duc Loi Market",
          "color": "blue"
        },
        {
          "id": "385890b8-fe15-421b-b214-b02959b0f8d9",
          "name": "Rainbow Grocery",
          "color": "gray"
        },
        {
          "id": "72ac0a6c-9e00-4e8c-80c5-720e4373e0b9",
          "name": "Nijiya Market",
          "color": "purple"
        }
      ]
    }
  }
}
```

#### Number

Rendered as a column with numeric values.

**Number Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `format` | string (enum) | Display format |

**Number Formats:**

`argentine_peso`, `australian_dollar`, `baht`, `canadian_dollar`, `chilean_peso`, `colombian_peso`, `danish_krone`, `dirham`, `dollar`, `euro`, `forint`, `franc`, `hong_kong_dollar`, `koruna`, `krona`, `leu`, `lira`, `mexican_peso`, `new_taiwan_dollar`, `new_zealand_dollar`, `norwegian_krone`, `number`, `number_with_commas`, `percent`, `philippine_peso`, `pound`, `peruvian_sol`, `rand`, `real`, `ringgit`, `riyal`, `ruble`, `rupee`, `rupiah`, `shekel`, `singapore_dollar`, `uruguayan_peso`, `yen`, `yuan`, `won`, `zloty`

```json
{
  "Price": {
    "id": "%7B%5D_P",
    "name": "Price",
    "type": "number",
    "number": {
      "format": "dollar"
    }
  }
}
```

#### People

Rendered as a column with people mentions. Empty configuration.

```json
{
  "Project owner": {
    "id": "FlgQ",
    "name": "Project owner",
    "type": "people",
    "people": {}
  }
}
```

#### Phone Number

Rendered as a column with phone number values. Empty configuration.

```json
{
  "Contact phone number": {
    "id": "ULHa",
    "name": "Contact phone number",
    "type": "phone_number",
    "phone_number": {}
  }
}
```

#### Place

Rendered as a column with location values. Used in conjunction with Map view.

**Place Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `lat` | number | Latitude |
| `lon` | number | Longitude |
| `name` | string \| null | Location name |
| `address` | string \| null | Address |
| `aws_place_id` | string \| null | AWS Place ID (echo only) |
| `google_place_id` | string \| null | Google Place ID (echo only) |

```json
{
  "Place": {
    "id": "Xqz4",
    "name": "Place",
    "type": "place",
    "place": {}
  }
}
```

#### Relation

Rendered as a column with references to pages in another data source.

**Relation Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `data_source_id` | string (UUID) | Related data source ID |
| `dual_property.synced_property_id` | string | ID of corresponding property in related data source |
| `dual_property.synced_property_name` | string | Name of corresponding property in related data source |

```json
{
  "Projects": {
    "id": "~pex",
    "name": "Projects",
    "type": "relation",
    "relation": {
      "data_source_id": "6c4240a9-a3ce-413e-9fd0-8a51a4d0a49b",
      "dual_property": {
        "synced_property_name": "Tasks",
        "synced_property_id": "JU]K"
      }
    }
  }
}
```

**Important:** To retrieve/update relation properties, the related database must be shared with your integration.

#### Rich Text

Rendered as a column with text values. Empty configuration.

```json
{
  "Project description": {
    "id": "NZZ%3B",
    "name": "Project description",
    "type": "rich_text",
    "rich_text": {}
  }
}
```

#### Rollup

Rendered as a column with values rolled up from a related data source.

**Rollup Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `function` | string (enum) | Aggregation function |
| `relation_property_id` | string | ID of related property |
| `relation_property_name` | string | Name of related property |
| `rollup_property_id` | string | ID of property to roll up |
| `rollup_property_name` | string | Name of property to roll up |

**Functions:** `average`, `checked`, `count`, `count_per_group`, `count_values`, `date_range`, `earliest_date`, `empty`, `latest_date`, `max`, `median`, `min`, `not_empty`, `percent_checked`, `percent_empty`, `percent_not_empty`, `percent_per_group`, `percent_unchecked`, `range`, `show_original`, `show_unique`, `sum`, `unchecked`, `unique`

```json
{
  "Estimated total project time": {
    "id": "%5E%7Cy%3C",
    "name": "Estimated total project time",
    "type": "rollup",
    "rollup": {
      "rollup_property_name": "Days to complete",
      "relation_property_name": "Tasks",
      "rollup_property_id": "\\nyY",
      "relation_property_id": "Y]<y",
      "function": "sum"
    }
  }
}
```

#### Select

Rendered as a column where only one option is allowed per row.

**Select Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `options` | array | Available options (same structure as multi-select) |

```json
{
  "Food group": {
    "id": "%40Q%5BM",
    "name": "Food group",
    "type": "select",
    "select": {
      "options": [
        {
          "id": "e28f74fc-83a7-4469-8435-27eb18f9f9de",
          "name": "🥦Vegetable",
          "color": "purple"
        },
        {
          "id": "6132d771-b283-4cd9-ba44-b1ed30477c7f",
          "name": "🍎Fruit",
          "color": "red"
        },
        {
          "id": "fc9ea861-820b-4f2b-bc32-44ed9eca873c",
          "name": "💪Protein",
          "color": "yellow"
        }
      ]
    }
  }
}
```

#### Status

Rendered as a column with status options (similar to select but with groups).

**Status Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `options` | array | Available status options |
| `groups` | array | Groups of status options |

**Option Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `color` | string (enum) | Color |
| `id` | string | Unique identifier |
| `name` | string | Option name (commas not valid; must be unique ignoring case) |

**Group Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `color` | string (enum) | Group color |
| `id` | string | Group identifier |
| `name` | string | Group name |
| `option_ids` | array of UUIDs | IDs of options in the group |

```json
{
  "Status": {
    "id": "biOx",
    "name": "Status",
    "type": "status",
    "status": {
      "options": [
        {
          "id": "034ece9a-384d-4d1f-97f7-7f685b29ae9b",
          "name": "Not started",
          "color": "default"
        },
        {
          "id": "330aeafb-598c-4e1c-bc13-1148aa5963d3",
          "name": "In progress",
          "color": "blue"
        },
        {
          "id": "497e64fb-01e2-41ef-ae2d-8a87a3bb51da",
          "name": "Done",
          "color": "green"
        }
      ],
      "groups": [
        {
          "id": "b9d42483-e576-4858-a26f-ed940a5f678f",
          "name": "To-do",
          "color": "gray",
          "option_ids": [
            "034ece9a-384d-4d1f-97f7-7f685b29ae9b"
          ]
        },
        {
          "id": "cf4952eb-1265-46ec-86ab-4bded4fa2e3b",
          "name": "In progress",
          "color": "blue",
          "option_ids": [
            "330aeafb-598c-4e1c-bc13-1148aa5963d3"
          ]
        },
        {
          "id": "4fa7348e-ae74-46d9-9585-e773caca6f40",
          "name": "Complete",
          "color": "green",
          "option_ids": [
            "497e64fb-01e2-41ef-ae2d-8a87a3bb51da"
          ]
        }
      ]
    }
  }
}
```

**⚠️ Important:** Status property name and options cannot be updated via the API. Update from Notion UI instead.

#### Title

Controls the title that appears at the top of a page when a data source row is opened.

```json
{
  "Project name": {
    "id": "title",
    "name": "Project name",
    "type": "title",
    "title": {}
  }
}
```

**⚠️ Requirement:** All data sources require one, and only one, title property. The API throws errors if you attempt to create/update without a title property, or add/remove the title property.

#### URL

Rendered as a column with URL values. Empty configuration.

```json
{
  "Project URL": {
    "id": "BZKU",
    "name": "Project URL",
    "type": "url",
    "url": {}
  }
}
```

#### Unique ID

Records automatically incremented, enforced unique values across all pages. Useful for task/bug report IDs (e.g., TASK-1234).

**Unique ID Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `prefix` | string | Common prefix (generates special URL like notion.so/TASK-1234) |

```json
{
  "Task ID": {
    "id": "...",
    "name": "Task ID",
    "type": "unique_id",
    "unique_id": {
      "prefix": "TASK"
    }
  }
}
```

## Schema Size Limitation

**Maximum schema size recommendation:** Notion recommends a maximum schema size of **50KB**. Updates to database schemas that are too large will be blocked to help maintain database performance.

## Working with Data Sources

### API Endpoints

#### Create Data Source
```
POST /databases/{database_id}/data_sources
```

**Required:**
- `properties` - Initial property schema (must include title property)

#### Retrieve Data Source
```
GET /data_sources/{data_source_id}
```

**Returns:** Full data source object with properties

#### Update Data Source
```
PATCH /data_sources/{data_source_id}
```

**Can update:**
- Property names
- Property configurations (select/status options, etc.)
- Add/remove properties

**Cannot update:**
- Property type (changing number to date)
- Status property names or options (use Notion UI)

#### Query Data Source
```
POST /data_sources/{data_source_id}/query
```

Query pages in the data source.

### Querying Pages by Data Source

When a database has multiple data sources, specify which one to query:

```json
POST /databases/{database_id}/query
{
  "data_source": {
    "id": "c174b72c-d782-432f-8dc0-b647e1c96df6"
  },
  "filter": {
    "property": "Status",
    "status": {
      "equals": "In Progress"
    }
  }
}
```

If the database has only one data source, the `data_source` parameter can be omitted.

## SDK Architecture

### DataSource Class

```python
@dataclass
class DataSource:
    """Notion data source object."""
    object: str = "data_source"
    id: UUID = None
    title: List[RichTextObject] = field(default_factory=list)
    description: List[RichTextObject] = field(default_factory=list)
    icon: Optional[Icon] = None
    archived: bool = False
    in_trash: bool = False
    created_time: Optional[datetime] = None
    created_by: Optional[PartialUser] = None
    last_edited_time: Optional[datetime] = None
    last_edited_by: Optional[PartialUser] = None
    parent: Optional[DataSourceParent] = None
    database_parent: Optional[Parent] = None
    properties: Dict[str, PropertySchema] = field(default_factory=dict)

    # Client reference
    _client: Any = field(default=None, init=False, repr=False)

    @classmethod
    def from_dict(cls, data: dict, client: Any = None) -> "DataSource":
        """Parse from API response."""
        instance = cls()

        instance.object = data.get("object")
        instance.id = UUID(data.get("id"))
        instance.archived = data.get("archived", False)
        instance.in_trash = data.get("in_trash", False)

        # Title and description
        instance.title = RichTextParser.parse_array(data.get("title", []))
        instance.description = RichTextParser.parse_array(data.get("description", []))

        # Icon
        instance.icon = Icon.from_dict(data.get("icon"))

        # Timestamps
        instance.created_time = _parse_datetime(data.get("created_time"))
        instance.last_edited_time = _parse_datetime(data.get("last_edited_time"))

        # Parent
        if "parent" in data:
            instance.parent = DataSourceParent.from_dict(data["parent"])
        if "database_parent" in data:
            instance.database_parent = Parent.from_dict(data["database_parent"])

        # Parse properties
        properties_data = data.get("properties", {})
        instance.properties = {
            name: PropertySchema.from_dict({**prop, "name": name})
            for name, prop in properties_data.items()
        }

        instance._client = client
        return instance

    @property
    def title_text(self) -> str:
        """Get title as plain text."""
        return "".join(rt.plain_text for rt in self.title)

    @property
    def description_text(self) -> str:
        """Get description as plain text."""
        return "".join(rt.plain_text for rt in self.description)

    def get_property_by_name(self, name: str) -> Optional[PropertySchema]:
        """Get property schema by name."""
        return self.properties.get(name)

    def get_property_by_id(self, prop_id: str) -> Optional[PropertySchema]:
        """Get property schema by ID."""
        for prop in self.properties.values():
            if prop.id == prop_id:
                return prop
        return None

    @property
    def title_property(self) -> Optional[PropertySchema]:
        """Get the title property."""
        return self.get_property_by_id("title")

    async def query_pages(self, **filters) -> PaginatedResponse[Page]:
        """Query pages in this data source."""
        if not self._client:
            raise RuntimeError("No client reference")

        return await self._client.data_sources.query(
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

    def __init__(self, prop_id: str, name: str, prop_type: str,
                 description: str = "", config: dict = None):
        self.id = prop_id
        self.name = name
        self.type = prop_type
        self.description = description
        self.config = config or {}

    @classmethod
    def from_dict(cls, data: dict) -> "PropertySchema":
        """Parse property schema."""
        prop_id = data.get("id")
        name = data.get("name")
        prop_type = data.get("type")
        description = data.get("description", "")

        # Type-specific config
        config = data.get(prop_type, {})

        return cls(prop_id, name, prop_type, description, config)

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

    @property
    def groups(self) -> Optional[List[dict]]:
        """Get groups for status properties."""
        if self.type == "status":
            return self.config.get("groups", [])
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
# Get data source
data_source = await client.data_sources.get(data_source_id)

# Access basic info
print(data_source.title_text)
print(data_source.description_text)
print(f"Properties: {len(data_source.properties)}")

# List properties
for prop_name, prop in data_source.properties.items():
    print(f"  {prop.name}: {prop.type}")
    if prop.options:
        print(f"    Options: {[opt['name'] for opt in prop.options]}")

# Get title property
title_prop = data_source.title_property
if title_prop:
    print(f"Title property: {title_prop.name}")

# Query pages
pages = await data_source.query_pages(
    filter={
        "property": "Status",
        "status": {"equals": "In Progress"}
    }
)

# Create page
new_page = await data_source.create_page(
    properties={
        "Name": {
            "title": [{"type": "text", "text": {"content": "New Task"}}]
        },
        "Status": {"status": {"name": "Not Started"}}
    }
)
```

## Best Practices

### 1. Schema Design

- Keep schema under 50KB for performance
- Use meaningful property names
- Plan property types carefully (changing type is difficult)

### 2. Status Properties

- Define groups to organize related statuses
- Use colors to indicate status categories
- Cannot update names/options via API

### 3. Relations

- Share related databases with integration
- Use dual properties for bidirectional relations
- Consider rollup performance with many relations

### 4. Unique IDs

- Use prefixes for easy identification (TASK-, BUG-, etc.)
- Enables special URLs (notion.so/TASK-1234)
- Useful for external references

## Related Documentation

- [Databases Overview](./databases-overview.md) - Database container
- [Database Implementation](./database-implementation.md) - SDK implementation
- [Page Properties](../pages/page-properties.md) - Property values (data rows)
- [Query Data Source](https://developers.notion.com/reference/post-data-source-query) - API endpoint

---

**Next:** See [Database Implementation](./database-implementation.md) for SDK implementation details.
