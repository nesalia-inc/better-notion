# Page Properties

## Overview

Page properties contain structured data about a page. The properties available depend on whether the page is a standalone page or a database entry.

## Property Value Object

Every property value object contains these common fields:

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Property identifier (URL-encoded). Remains constant when property name changes. Can be used instead of name when creating/updating. |
| `type` | string (enum) | The property type. Determines which additional fields are present. |
| `{type}` | object | Type-specific value object (varies by type) |

### Example Property Value

```json
{
  "id": "Z%3ClH",
  "type": "status",
  "status": {
    "id": "86ddb6ec-0627-47f8-800d-b65afd28be13",
    "name": "Not started",
    "color": "default"
  }
}
```

## Property Types

### Complete Type List

1. **Basic Types**
   - `checkbox` - Boolean checkbox
   - `date` - Date or date range
   - `email` - Email address
   - `number` - Numeric value
   - `phone_number` - Phone number
   - `url` - Web address

2. **Selection Types**
   - `select` - Single option from list
   - `status` - Status option (workflow states)
   - `multi_select` - Multiple options from list

3. **Text Types**
   - `title` - Page title (rich text)
   - `rich_text` - Formatted text
   - `verification` - Verification status (wiki pages only)

4. **Reference Types**
   - `people` - Array of users
   - `relation` - Related pages in other databases
   - `files` - Array of file references

5. **Computed Types** (Read-only)
   - `formula` - Computed formula result
   - `rollup` - Aggregation from related pages
   - `created_by` - User who created page
   - `created_time` - Creation timestamp
   - `last_edited_by` - User who last edited
   - `last_edited_time` - Last edit timestamp
   - `unique_id` - Auto-incrementing ID

6. **Unsupported**
   - Other types return `null`

## Type Reference

### Checkbox

**Type:** `checkbox`

Simple boolean value.

**Structure:**
```json
{
  "Task completed": {
    "id": "ZI%40W",
    "type": "checkbox",
    "checkbox": true
  }
}
```

**Update format:**
```json
{
  "properties": {
    "Task completed": {
      "checkbox": true
    }
  }
}
```

**SDK:**
```python
class CheckboxProperty(PropertyValue):
    type: str = "checkbox"
    value: bool

    @property
    def is_checked(self) -> bool:
        return self.value
```

---

### Created By

**Type:** `created_by`

User who created the page. **Read-only.**

**Structure:**
```json
{
  "created_by": {
    "id": "eB_%7D",
    "type": "created_by",
    "created_by": {
      "object": "user",
      "id": "c2f20311-9e54-4d11-8c79-7398424ae41e"
    }
  }
}
```

**SDK:**
```python
class CreatedByProperty(PropertyValue):
    type: str = "created_by"
    value: PartialUser

    @property
    def cannot_be_updated(self) -> bool:
        return True
```

---

### Created Time

**Type:** `created_time`

Timestamp when page was created. **Read-only.**

**Structure:**
```json
{
  "Created time": {
    "id": "eB_%7D",
    "type": "created_time",
    "created_time": "2022-10-24T22:54:00.000Z"
  }
}
```

**SDK:**
```python
class CreatedTimeProperty(PropertyValue):
    type: str = "created_time"
    value: datetime

    @property
    def cannot_be_updated(self) -> bool:
        return True
```

---

### Date

**Type:** `date`

Date or date range.

**Structure:**
```json
{
  "Due date": {
    "id": "M%3BBw",
    "type": "date",
    "date": {
      "start": "2023-02-23",
      "end": null,
      "time_zone": null
    }
  }
}
```

**Fields:**
| Field | Type | Description |
|-------|------|-------------|
| `start` | string (ISO 8601) | Start date/time (required) |
| `end` | string (ISO 8601) \| null | End date/time (for ranges) |
| `time_zone` | string \| null | IANA time zone (e.g., "America/Los_Angeles") |

**Update format:**
```json
{
  "properties": {
    "Due date": {
      "date": {
        "start": "2023-02-23"
      }
    }
  }
}
```

**SDK:**
```python
@dataclass
class DateValue:
    """Date value."""
    start: datetime  # or date
    end: Optional[datetime] = None
    time_zone: Optional[str] = None

class DateProperty(PropertyValue):
    type: str = "date"
    value: DateValue
```

---

### Email

**Type:** `email`

Email address string.

**Structure:**
```json
{
  "Email": {
    "id": "y%5C%5E_",
    "type": "email",
    "email": "ada@makenotion.com"
  }
}
```

**Update format:**
```json
{
  "properties": {
    "Email": {
      "email": "user@example.com"
    }
  }
}
```

---

### Files

**Type:** `files`

Array of file references.

**Structure:**
```json
{
  "Blueprint": {
    "id": "tJPS",
    "type": "files",
    "files": [
      {
        "name": "Project blueprint",
        "type": "external",
        "external": {
          "url": "https://www.figma.com/file/..."
        }
      }
    ]
  }
}
```

**Update format:**
```json
{
  "properties": {
    "Files": {
      "files": [
        {
          "name": "My File",
          "external": {"url": "https://example.com/file.pdf"}
        }
      ]
    }
  }
}
```

**Important:** When updating, the entire array replaces existing files.

**SDK:**
```python
@dataclass
class FileReference:
    """File reference."""
    name: str
    type: str  # "external", "file"
    url: str

class FilesProperty(PropertyValue):
    type: str = "files"
    value: List[FileReference]
```

---

### Formula

**Type:** `formula`

Computed formula result. **Read-only.**

**Result types:** `boolean`, `date`, `number`, `string`

**Structure:**
```json
{
  "Days until launch": {
    "id": "CSoE",
    "type": "formula",
    "formula": {
      "type": "number",
      "number": 56
    }
  }
}
```

**SDK:**
```python
class FormulaProperty(PropertyValue):
    type: str = "formula"
    result_type: str  # "boolean", "date", "number", "string"
    value: Any  # Varies by result_type
```

**Note:** For formulas with >25 references, use the Retrieve page property item endpoint.

---

### Last Edited By

**Type:** `last_edited_by`

User who last edited the page. **Read-only.**

**Structure:**
```json
{
  "Last edited by": {
    "id": "uGNN",
    "type": "last_edited_by",
    "last_edited_by": {
      "object": "user",
      "id": "9188c6a5-7381-452f-b3dc-d4865aa89bdf",
      "name": "Test Integration"
    }
  }
}
```

---

### Last Edited Time

**Type:** `last_edited_time`

Timestamp when page was last edited. **Read-only.**

**Structure:**
```json
{
  "Last edited time": {
    "id": "%3Defk",
    "type": "last_edited_time",
    "last_edited_time": "2023-02-24T21:06:00.000Z"
  }
}
```

---

### Multi-Select

**Type:** `multi_select`

Array of select options.

**Structure:**
```json
{
  "Programming language": {
    "id": "QyRn",
    "type": "multi_select",
    "multi_select": [
      {
        "id": "tC;=",
        "name": "TypeScript",
        "color": "purple"
      },
      {
        "id": "e4413a91-9f84-4c4a-a13d-5b4b3ef870bb",
        "name": "JavaScript",
        "color": "red"
      }
    ]
  }
}
```

**Update format:**
```json
{
  "properties": {
    "Tags": {
      "multi_select": [
        {"name": "TypeScript"},
        {"name": "Python"}
      ]
    }
  }
}
```

**Note:** Using `name` automatically adds new options to database schema (if write access).

**Colors:** `blue`, `brown`, `default`, `gray`, `green`, `orange`, `pink`, `purple`, `red`, `yellow`

**SDK:**
```python
@dataclass
class SelectOption:
    """Select option."""
    id: str
    name: str
    color: str

class MultiSelectProperty(PropertyValue):
    type: str = "multi_select"
    value: List[SelectOption]
```

---

### Number

**Type:** `number`

Numeric value.

**Structure:**
```json
{
  "Number of subscribers": {
    "id": "WPj%5E",
    "type": "number",
    "number": 42
  }
}
```

**Update format:**
```json
{
  "properties": {
    "Price": {
      "number": 99.99
    }
  }
}
```

---

### People

**Type:** `people`

Array of user references.

**Structure:**
```json
{
  "Stakeholders": {
    "id": "%7BLUX",
    "type": "people",
    "people": [
      {
        "object": "user",
        "id": "c2f20311-9e54-4d11-8c79-7398424ae41e",
        "name": "Kimberlee Johnson",
        "avatar_url": null,
        "type": "person",
        "person": {
          "email": "hello@kimberlee.dev"
        }
      }
    ]
  }
}
```

**Update format:**
```json
{
  "properties": {
    "Assignees": {
      "people": [
        {"id": "user-uuid-1"},
        {"id": "user-uuid-2"}
      ]
    }
  }
}
```

**Note:** For >25 people, use Retrieve page property item endpoint.

**SDK:**
```python
class PeopleProperty(PropertyValue):
    type: str = "people"
    value: List[PartialUser]
```

---

### Phone Number

**Type:** `phone_number`

Phone number string (no format enforced).

**Structure:**
```json
{
  "Contact phone": {
    "id": "%5DKhQ",
    "type": "phone_number",
    "phone_number": "415-202-4776"
  }
}
```

**Update format:**
```json
{
  "properties": {
    "Phone": {
      "phone_number": "555-1234"
    }
  }
}
```

---

### Relation

**Type:** `relation`

Array of related page references.

**Structure:**
```json
{
  "Related tasks": {
    "id": "hgMz",
    "type": "relation",
    "relation": [
      {
        "id": "dd456007-6c66-4bba-957e-ea501dcda3a6"
      },
      {
        "id": "0c1f7cb2-8090-4f18-924e-d92965055e32"
      }
    ],
    "has_more": false
  }
}
```

**Update format:**
```json
{
  "properties": {
    "Related tasks": {
      "relation": [
        {"id": "page-uuid-1"},
        {"id": "page-uuid-2"}
      ]
    }
  }
}
```

**Important:**
- Integration must have access to related database
- `has_more: true` indicates >25 relations (use property item endpoint)

**SDK:**
```python
class RelationProperty(PropertyValue):
    type: str = "relation"
    value: List[str]  # Page IDs
    has_more: bool = False
```

---

### Rich Text

**Type:** `rich_text`

Array of rich text objects (formatted text).

**Structure:**
```json
{
  "Description": {
    "id": "HbZT",
    "type": "rich_text",
    "rich_text": [
      {
        "type": "text",
        "text": {
          "content": "Some ",
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
        "plain_text": "Some ",
        "href": null
      },
      {
        "type": "text",
        "text": {
          "content": "formatted text",
          "link": null
        },
        "annotations": {
          "bold": true,
          "italic": false,
          "strikethrough": false,
          "underline": false,
          "code": false,
          "color": "default"
        },
        "plain_text": "formatted text",
        "href": null
      }
    ]
  }
}
```

**Update format:**
```json
{
  "properties": {
    "Description": {
      "rich_text": [
        {
          "type": "text",
          "text": {"content": "New description"}
        }
      ]
    }
  }
}
```

**Note:** For >25 inline page/person references, use property item endpoint.

**SDK:**
```python
class RichTextProperty(PropertyValue):
    type: str = "rich_text"
    value: List[RichTextObject]
```

---

### Rollup

**Type:** `rollup`

Aggregation from related pages. **Read-only.**

**Result types:** `array`, `date`, `incomplete`, `number`, `unsupported`

**Structure:**
```json
{
  "Number of units": {
    "id": "hgMz",
    "type": "rollup",
    "rollup": {
      "type": "number",
      "number": 2,
      "function": "count"
    }
  }
}
```

**Functions:** `average`, `checked`, `count`, `count_per_group`, `count_values`, `date_range`, `earliest_date`, `empty`, `latest_date`, `max`, `median`, `min`, `not_empty`, `percent_checked`, `percent_empty`, `percent_not_empty`, `percent_per_group`, `percent_unchecked`, `range`, `show_original`, `show_unique`, `sum`, `unchecked`, `unique`

**Note:** For >25 references, use property item endpoint. Cannot update via API.

---

### Select

**Type:** `select`

Single option from list.

**Structure:**
```json
{
  "Department": {
    "id": "Yc%3FJ",
    "type": "select",
    "select": {
      "id": "ou@_",
      "name": "jQuery",
      "color": "purple"
    }
  }
}
```

**Update format:**
```json
{
  "properties": {
    "Status": {
      "select": {
        "name": "In Progress"
      }
    }
  }
}
```

**Colors:** Same as multi-select.

---

### Status

**Type:** `status`

Status option (workflow states).

**Structure:**
```json
{
  "Status": {
    "id": "Z%3ClH",
    "type": "status",
    "status": {
      "id": "539f2705-6529-42d8-a615-61a7183a92c0",
      "name": "In progress",
      "color": "blue"
    }
  }
}
```

**Update format:**
```json
{
  "properties": {
    "Status": {
      "status": {
        "name": "Not started"
      }
    }
  }
}
```

---

### Title

**Type:** `title`

Page title (rich text array). Every page has a title.

**Structure:**
```json
{
  "Title": {
    "id": "title",
    "type": "title",
    "title": [
      {
        "type": "text",
        "text": {
          "content": "Bug bash",
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
        "plain_text": "Bug bash",
        "href": null
      }
    ]
  }
}
```

**Update format:**
```json
{
  "properties": {
    "Title": {
      "title": [
        {
          "type": "text",
          "text": {"content": "New Title"}
        }
      ]
    }
  }
}
```

**SDK:**
```python
class TitleProperty(PropertyValue):
    type: str = "title"
    value: List[RichTextObject]

    @property
    def plain_text(self) -> str:
        """Get plain text title."""
        return "".join(rt.plain_text for rt in self.value)
```

---

### URL

**Type:** `url`

Web address string.

**Structure:**
```json
{
  "Website": {
    "id": "bB%3D%5B",
    "type": "url",
    "url": "https://developers.notion.com/"
  }
}
```

**Update format:**
```json
{
  "properties": {
    "Website": {
      "url": "https://example.com"
    }
  }
}
```

---

### Unique ID

**Type:** `unique_id`

Auto-incrementing unique ID. **Read-only.**

**Structure:**
```json
{
  "test-ID": {
    "id": "tqqd",
    "type": "unique_id",
    "unique_id": {
      "number": 3,
      "prefix": "RL"
    }
  }
}
```

---

### Verification

**Type:** `verification`

Verification status (wiki pages only). **Read-only** (currently cannot be set via API).

**Structure:**
```json
{
  "Verification": {
    "id": "fpVq",
    "type": "verification",
    "verification": {
      "state": "verified",
      "verified_by": {
        "object": "user",
        "id": "01e46064-d5fb-4444-8ecc-ad47d076f804",
        "name": "User Name"
      },
      "date": {
        "start": "2023-08-01T04:00:00.000Z",
        "end": "2023-10-30T04:00:00.000Z",
        "time_zone": null
      }
    }
  }
}
```

**States:** `verified`, `unverified`

---

## Property Value Limits

For size limitations on property values, refer to the [Notion API limits documentation](https://developers.notion.com/reference/request-limits#limits-for-property-values).

## Updating Properties

### Single Property

```json
{
  "properties": {
    "Status": {
      "status": {"name": "Done"}
    }
  }
}
```

### Multiple Properties

```json
{
  "properties": {
    "Status": {
      "status": {"name": "Done"}
    },
    "Due date": {
      "date": {"start": "2023-12-31"}
    }
  }
}
```

### Clearing a Property

Use `null` to clear select, multi-select, and date properties:

```json
{
  "properties": {
    "Status": null,
    "Tags": null,
    "Due date": null
  }
}
```

## Unsupported Properties

If a property type is not supported by the API, it returns `null`:

```json
{
  "Place": {
    "id": "%60%40Gq",
    "type": "place",
    "place": null
  }
}
```

**Exclude unsupported types when updating.**

## Related Documentation

- [Pages Overview](./pages-overview.md) - Page object structure
- [Property Types](./page-property-types.md) - Detailed property type information
- [Page Implementation](./page-implementation.md) - SDK implementation guide
- [Rich Text Objects](../rich-text-objects.md) - Text formatting in properties

---

**Next:** See [Property Types](./page-property-types.md) for detailed information about each property type.
