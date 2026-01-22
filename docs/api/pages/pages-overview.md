# Pages Overview

## Introduction

A **Page object** in Notion represents a single page with its property values. Pages are the fundamental content containers in Notion, and they can exist independently or as entries in a database.

## Key Concepts

### Page Structure

Every Notion page contains:
1. **Metadata** - ID, creation/edit times, parent, archived status
2. **Properties** - Data fields (title, status, dates, etc.)
3. **Content** - Blocks that make up the page body
4. **Visual elements** - Icon and cover image

### Page vs Database Entry

Pages can be:
- **Standalone pages** - Created in a workspace or nested under another page
- **Database entries** - Pages that are part of a database, displayed as rows

**Important:** Pages in a database have properties defined by the database schema. Standalone pages typically only have a title property.

### Content vs Properties

- **Properties** - Structured data fields (metadata, status, dates, etc.)
- **Content** - The body of the page made up of blocks

## Page Object Structure

### Example Page Object

```json
{
  "object": "page",
  "id": "be633bf1-dfa0-436d-b259-571129a590e5",
  "created_time": "2022-10-24T22:54:00.000Z",
  "last_edited_time": "2023-03-08T18:25:00.000Z",
  "created_by": {
    "object": "user",
    "id": "c2f20311-9e54-4d11-8c79-7398424ae41e"
  },
  "last_edited_by": {
    "object": "user",
    "id": "9188c6a5-7381-452f-b3dc-d4865aa89bdf"
  },
  "cover": null,
  "icon": {
    "type": "emoji",
    "emoji": "🐞"
  },
  "parent": {
    "type": "database_id",
    "database_id": "a1d8501e-1ac1-43e9-a6bd-ea9fe6c8822b"
  },
  "archived": false,
  "in_trash": false,
  "properties": {
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
  },
  "url": "https://www.notion.so/Bug-bash-be633bf1dfa0436db259571129a590e5",
  "public_url": "https://jm-testing.notion.site/p1-6df2c07bfc6b4c46815ad205d132e22d"
}
```

## Page Object Properties

### Common Fields

| Field | Type | Capability Required | Description |
|-------|------|---------------------|-------------|
| `object` | string | None | Always `"page"` |
| `id` | string (UUIDv4) | None | Unique identifier |
| `created_time` | string (ISO 8601) | Read content | Creation timestamp |
| `created_by` | PartialUser | Read content | User who created the page |
| `last_edited_time` | string (ISO 8601) | Read content | Last edit timestamp |
| `last_edited_by` | PartialUser | Read content | User who last edited |
| `archived` | boolean | None | Archived status |
| `in_trash` | boolean | Read content | Whether page is in trash |
| `cover` | FileObject \| null | Read content | Cover image |
| `icon` * | EmojiObject \| FileObject | None | Page icon |
| `properties` | object | None | Property values |
| `parent` | object | None | Parent information |
| `url` | string | None | Notion URL of the page |
| `public_url` | string \| null | None | Public URL if published |

* = Fields available to integrations with any capabilities

## Parent Object

Pages always have a parent. The parent type determines the page's properties.

### Parent Types

#### 1. Database Parent
```json
{
  "type": "database_id",
  "database_id": "a1d8501e-1ac1-43e9-a6bd-ea9fe6c8822b"
}
```
- Page is an entry in a database
- Properties conform to database schema
- Most common type

#### 2. Page Parent
```json
{
  "type": "page_id",
  "page_id": "59833787-2cf9-4fdf-8782-e53db20768a5"
}
```
- Page is nested under another page
- Only has a title property

#### 3. Workspace Parent
```json
{
  "type": "workspace",
  "workspace": true
}
```
- Root-level page
- Only has a title property

#### 4. Block Parent
```json
{
  "type": "block_id",
  "block_id": "7d50a184-5bbe-4d90-8f29-6bec57ed817b"
}
```
- Rare case, page created as child of a block

## Icon and Cover

### Icon

**Types:**
1. **Emoji** - Simple emoji character
2. **External file** - URL to an image
3. **File upload** - Notion-hosted file (via File Upload API)

**Emoji example:**
```json
{
  "type": "emoji",
  "emoji": "🐞"
}
```

**File example:**
```json
{
  "type": "file",
  "file": {
    "url": "https://...",
    "expiry_time": "2024-12-03T19:44:56.932Z"
  }
}
```

**File upload (for creation/update):**
```json
{
  "type": "file_upload",
  "file_upload": {
    "id": "43833259-72ae-404e-8441-b6577f3159b4"
  }
}
```

### Cover

Similar to icon, but only supports file types (external or file_upload):

```json
{
  "type": "external",
  "external": {
    "url": "https://example.com/cover.jpg"
  }
}
```

## URLs

### `url` vs `public_url`

| Field | Description | When Present |
|-------|-------------|--------------|
| `url` | Internal Notion URL | Always present |
| `public_url` | Published web URL | Only if page is published to web |

**URL format:** `https://www.notion.so/{Title}-{id}` (spaces removed, title truncated)

## Page Properties

Pages contain property values based on their parent:

### Standalone Pages (page_id or workspace parent)
- **Only property:** `title`

### Database Pages (database_id parent)
- **Properties:** Defined by database schema
- **Can include:** title, status, date, select, multi_select, people, etc.

**Example database page properties:**
```json
{
  "properties": {
    "Title": {
      "id": "title",
      "type": "title",
      "title": [/* rich text objects */]
    },
    "Status": {
      "id": "Z%3ClH",
      "type": "status",
      "status": {
        "id": "86ddb6ec-0627-47f8-800d-b65afd28be13",
        "name": "Not started",
        "color": "default"
      }
    },
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
}
```

See [Page Properties](./page-properties.md) for complete details on all property types.

## Content (Blocks)

Page content is not part of the page object itself. It's accessed separately:

### Retrieving Page Content
```
GET /blocks/{page_id}/children
```

### Adding Page Content
```
POST /blocks/{page_id}/children
```

**Example:**
```python
# Get page
page = await client.pages.get(page_id)

# Get page content (blocks)
blocks = await client.blocks.children.list(block_id=page_id)

# Add content to page
await client.blocks.children.append(
    block_id=page_id,
    children=[{
        "object": "block",
        "type": "paragraph",
        "paragraph": {
            "rich_text": [{
                "type": "text",
                "text": {"content": "Hello, world!"}
            }]
        }
    }]
)
```

## SDK Architecture Implications

### Page Class Structure

```python
@dataclass
class Page:
    """Notion page object."""
    object: str = "page"
    id: UUID = None
    created_time: datetime = None
    last_edited_time: datetime = None
    created_by: PartialUser = None
    last_edited_by: PartialUser = None
    archived: bool = False
    in_trash: bool = False
    cover: Optional[FileObject] = None
    icon: Optional[IconObject] = None
    parent: Parent = None
    url: str = ""
    public_url: Optional[str] = None

    # Properties (dynamic based on parent)
    properties: Dict[str, PropertyValue] = field(default_factory=dict)

    # Lazy-loaded content
    _blocks: Optional[List[Block]] = None

    @classmethod
    def from_dict(cls, data: dict, client: Any = None) -> "Page":
        """Parse page from API response."""
        pass

    def get_title(self) -> str:
        """Get page title."""
        title_prop = self.properties.get("title")
        if title_prop:
            return title_prop.plain_text
        return ""

    async def get_blocks(self) -> List[Block]:
        """Lazy load page content."""
        if self._blocks is None:
            self._blocks = await self._client.blocks.children.list(
                block_id=str(self.id)
            )
        return self._blocks
```

### Property Value System

```python
class PropertyValue:
    """Base class for property values."""
    id: str
    type: str

    @classmethod
    def from_dict(cls, data: dict) -> "PropertyValue":
        """Parse property from API response."""
        prop_type = data.get("type")

        if prop_type == "title":
            return TitleProperty.from_dict(data)
        elif prop_type == "status":
            return StatusProperty.from_dict(data)
        # ... etc

class TitleProperty(PropertyValue):
    """Title property."""
    type: str = "title"
    title: List[RichTextObject]

    @property
    def plain_text(self) -> str:
        """Get plain text title."""
        return "".join(rt.plain_text for rt in self.title)

class StatusProperty(PropertyValue):
    """Status property."""
    type: str = "status"
    status: Optional[StatusOption] = None

@dataclass
class StatusOption:
    """Status option."""
    id: str
    name: str
    color: str
```

## Common Operations

### Creating Pages

```python
# Create a page in a database
page = await client.pages.create(
    parent={"type": "database_id", "database_id": database_id},
    properties={
        "Title": {
            "title": [{"type": "text", "text": {"content": "New Page"}}]
        },
        "Status": {
            "status": {"name": "Not Started"}
        }
    }
)
```

### Updating Pages

```python
# Update page properties
updated_page = await client.pages.update(
    page_id=page.id,
    properties={
        "Status": {
            "status": {"name": "In Progress"}
        }
    }
)

# Update icon
await client.pages.update(
    page_id=page.id,
    icon={"type": "emoji", "emoji": "🎉"}
)
```

### Retrieving Pages

```python
# Get a single page
page = await client.pages.get(page_id)

# Get page property
status_prop = await client.pages.properties.get(
    page_id=page_id,
    property_id="status"
)
```

### Archiving/Deleting

```python
# Archive (soft delete)
await client.pages.update(page_id=page.id, archived=True)

# Delete (permanent) - use blocks endpoint
await client.blocks.delete(block_id=page.id)
```

## Permissions

### Integration Capabilities

Properties marked with `*` are available to integrations with any capabilities. Other properties require **read content** capability:

**Always available:**
- `id`
- `object`
- `archived`

**Requires read content:**
- `created_time`
- `created_by`
- `last_edited_time`
- `last_edited_by`
- `in_trash`
- `cover`
- `properties` (when retrieving full page)

### Access Control

- Pages in private databases require integration to be shared
- Page references in relations require access to source database
- Mentions of inaccessible pages show as "Untitled"

## Related Documentation

- [Page Properties](./page-properties.md) - Complete property reference
- [Property Types](./page-property-types.md) - All property type details
- [Page Implementation](./page-implementation.md) - SDK implementation guide
- [Blocks](../block/blocks-overview.md) - Page content (blocks)
- [Rich Text Objects](../rich-text-objects.md) - Text formatting in properties

---

**Next:** See [Page Properties](./page-properties.md) for detailed information about page properties.
