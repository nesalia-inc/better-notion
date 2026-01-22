# Parenting and Structure

## Introduction

Pages, databases, data sources, comments, and blocks are organized in a hierarchical structure within Notion. The **parent** object represents this location relationship consistently throughout the API.

## Parent Object Overview

### General Parenting Rules

| Child Entity | Possible Parents |
|--------------|------------------|
| **Pages** | Pages, data sources, blocks, workspace |
| **Blocks** | Pages, data sources, blocks |
| **Databases** | Pages, blocks, workspace (data sources for wikis) |
| **Data Sources** | Databases, data sources (for linked/external) |
| **Comments** | Pages, blocks |

**Important Changes:**
- Prior to API version `2025-09-03`: Page parents were databases, not data sources
- Post API version `2025-09-03`: Page parents are data sources

**API Creation Constraints:**
Not all parent relationships can be created via the API. For example, databases created via the API must have a page parent. Refer to specific endpoint documentation for current constraints.

## Parent Types

### 1. Database Parent

Used for **data source** objects. Indicates the database that owns the data source.

```json
{
  "type": "database_id",
  "database_id": "d9824bdc-8445-4327-be8b-5b47500af6ce"
}
```

| Field | Type | Description |
|-------|------|-------------|
| `type` | string | Always `"database_id"` |
| `database_id` | string (UUIDv4) | ID of the database |

### 2. Data Source Parent

Used for **page** objects. Indicates the data source that contains the page.

```json
{
  "type": "data_source_id",
  "data_source_id": "1a44be12-0953-4631-b498-9e5817518db8",
  "database_id": "d9824bdc-8445-4327-be8b-5b47500af6ce"
}
```

| Field | Type | Description |
|-------|------|-------------|
| `type` | string | Always `"data_source_id"` |
| `data_source_id` | string (UUIDv4) | ID of the data source |
| `database_id` | string (UUIDv4) | ID of the database (convenience field) |

### 3. Page Parent

Used for pages, blocks, and databases nested under another page.

```json
{
  "type": "page_id",
  "page_id": "59833787-2cf9-4fdf-8782-e53db20768a5"
}
```

| Field | Type | Description |
|-------|------|-------------|
| `type` | string | Always `"page_id"` |
| `page_id` | string (UUIDv4) | ID of the parent page |

### 4. Workspace Parent

Used for top-level pages and databases at the workspace root. Team-level pages also use this parent type.

```json
{
  "type": "workspace",
  "workspace": true
}
```

| Field | Type | Description |
|-------|------|-------------|
| `type` | string | Always `"workspace"` |
| `workspace` | boolean | Always `true` |

**Characteristics:**
- Workspace-level entities are at the root level
- No parent container above them
- Recommended to have at least one parent page for better permission management

### 5. Block Parent

Used for pages created inline in text or nested under blocks like toggles or bullets.

```json
{
  "type": "block_id",
  "block_id": "7d50a184-5bbe-4d90-8f29-6bec57ed817b"
}
```

| Field | Type | Description |
|-------|------|-------------|
| `type` | string | Always `"block_id"` |
| `block_id` | string (UUIDv4) | ID of the parent block |

## Parent Reference Summary

| Parent Type | Typical Children | API Creation Supported |
|-------------|------------------|----------------------|
| `workspace` | Root pages, databases | Yes (with restrictions) |
| `page_id` | Pages, blocks, databases | Yes |
| `block_id` | Pages, blocks | Yes |
| `data_source_id` | Pages | Yes |
| `database_id` | Data sources | Implicit (created with database) |

## SDK Architecture

### Parent Class

```python
from dataclasses import dataclass, field
from typing import Union, Optional
from uuid import UUID
from enum import Enum

class ParentType(str, Enum):
    """Parent type enumeration."""
    WORKSPACE = "workspace"
    PAGE_ID = "page_id"
    BLOCK_ID = "block_id"
    DATA_SOURCE_ID = "data_source_id"
    DATABASE_ID = "database_id"

@dataclass
class WorkspaceParent:
    """Workspace parent (root level)."""
    type: str = "workspace"
    workspace: bool = True

@dataclass
class PageParent:
    """Page parent."""
    type: str = "page_id"
    page_id: UUID = None

@dataclass
class BlockParent:
    """Block parent."""
    type: str = "block_id"
    block_id: UUID = None

@dataclass
class DataSourceParent:
    """Data source parent."""
    type: str = "data_source_id"
    data_source_id: UUID = None
    database_id: Optional[UUID] = None

@dataclass
class DatabaseParent:
    """Database parent."""
    type: str = "database_id"
    database_id: UUID = None

# Union type for all parent types
Parent = Union[
    WorkspaceParent,
    PageParent,
    BlockParent,
    DataSourceParent,
    DatabaseParent
]

def parse_parent(data: dict) -> Parent:
    """
    Parse parent object from API response.

    Args:
        data: Parent object from API

    Returns:
        Appropriate parent subclass
    """
    parent_type = data.get("type")

    if parent_type == "workspace":
        return WorkspaceParent(**data)
    elif parent_type == "page_id":
        return PageParent(**data)
    elif parent_type == "block_id":
        return BlockParent(**data)
    elif parent_type == "data_source_id":
        return DataSourceParent(**data)
    elif parent_type == "database_id":
        return DatabaseParent(**data)
    else:
        raise ValueError(f"Unknown parent type: {parent_type}")
```

### Parent Helper Functions

```python
class ParentHelper:
    """Helper functions for working with parents."""

    @staticmethod
    def workspace() -> WorkspaceParent:
        """Create a workspace parent."""
        return WorkspaceParent()

    @staticmethod
    def page(page_id: str) -> PageParent:
        """Create a page parent."""
        return PageParent(page_id=UUID(page_id))

    @staticmethod
    def block(block_id: str) -> BlockParent:
        """Create a block parent."""
        return BlockParent(block_id=UUID(block_id))

    @staticmethod
    def data_source(data_source_id: str, database_id: Optional[str] = None) -> DataSourceParent:
        """Create a data source parent."""
        return DataSourceParent(
            data_source_id=UUID(data_source_id),
            database_id=UUID(database_id) if database_id else None
        )

    @staticmethod
    def database(database_id: str) -> DatabaseParent:
        """Create a database parent."""
        return DatabaseParent(database_id=UUID(database_id))

    @staticmethod
    def to_dict(parent: Parent) -> dict:
        """
        Convert parent object to API request format.

        Args:
            parent: Parent object

        Returns:
            Dictionary for API request
        """
        if isinstance(parent, WorkspaceParent):
            return {"type": "workspace", "workspace": True}
        elif isinstance(parent, PageParent):
            return {"type": "page_id", "page_id": str(parent.page_id)}
        elif isinstance(parent, BlockParent):
            return {"type": "block_id", "block_id": str(parent.block_id)}
        elif isinstance(parent, DataSourceParent):
            result = {
                "type": "data_source_id",
                "data_source_id": str(parent.data_source_id)
            }
            if parent.database_id:
                result["database_id"] = str(parent.database_id)
            return result
        elif isinstance(parent, DatabaseParent):
            return {"type": "database_id", "database_id": str(parent.database_id)}
        else:
            raise ValueError(f"Unknown parent type: {type(parent)}")
```

### Usage Examples

```python
import better_notion

# Create page with different parents
client = better_notion.Client(auth=token)

# Workspace-level page
page = await client.pages.create(
    parent=ParentHelper.workspace(),
    properties={"title": "Root Page"}
)

# Page under another page
page = await client.pages.create(
    parent=ParentHelper.page(page_id="59833787-2cf9-4fdf-8782-e53db20768a5"),
    properties={"title": "Child Page"}
)

# Page under a block (e.g., in a toggle)
page = await client.pages.create(
    parent=ParentHelper.block(block_id="7d50a184-5bbe-4d90-8f29-6bec57ed817b"),
    properties={"title": "Nested Page"}
)

# Create database under a page
database = await client.databases.create(
    parent=ParentHelper.page(page_id="59833787-2cf9-4fdf-8782-e53db20768a5"),
    title="Tasks",
    data_source=DataSourceConfig(...)
)

# Parse parent from API response
page_data = {
    "parent": {
        "type": "page_id",
        "page_id": "59833787-2cf9-4fdf-8782-e53db20768a5"
    }
}
parent = parse_parent(page_data["parent"])

if isinstance(parent, PageParent):
    print(f"Parent page ID: {parent.page_id}")
```

## Hierarchical Navigation

```python
class EntityNavigation:
    """Navigate hierarchical relationships."""

    def __init__(self, client: "Client"):
        self._client = client

    async def get_parent(self, entity: Union[Page, Block, Database]) -> Optional[Union[Page, Block, Database, Workspace]]:
        """
        Get the parent of an entity.

        Args:
            entity: Page, Block, or Database object

        Returns:
            Parent entity or None if workspace parent
        """
        if not entity.parent:
            return None

        parent_type = entity.parent.type

        if parent_type == "workspace":
            return None  # Workspace is the root
        elif parent_type == "page_id":
            return await self._client.pages.get(str(entity.parent.page_id))
        elif parent_type == "block_id":
            return await self._client.blocks.get(str(entity.parent.block_id))
        elif parent_type == "database_id":
            return await self._client.databases.get(str(entity.parent.database_id))
        else:
            raise ValueError(f"Unknown parent type: {parent_type}")

    async def get_ancestors(self, entity: Union[Page, Block]) -> List[Union[Page, Block]]:
        """
        Get all ancestors of an entity (bottom to top).

        Args:
            entity: Page or Block object

        Returns:
            List of ancestor entities
        """
        ancestors = []
        current = entity

        while current.parent and current.parent.type != "workspace":
            parent = await self.get_parent(current)
            if parent is None:
                break
            ancestors.append(parent)
            current = parent

        return ancestors

    async def get_children(
        self,
        entity: Union[Page, Block]
    ) -> List[Union[Page, Block]]:
        """
        Get direct children of an entity.

        Args:
            entity: Page or Block object

        Returns:
            List of child entities
        """
        if isinstance(entity, Page):
            # Get blocks on page
            blocks = await entity.get_children()
            return blocks
        elif isinstance(entity, Block):
            # Get child blocks
            children = await entity.get_children()
            return children
        else:
            return []
```

## Best Practices

### 1. Parent Type Selection

```python
# Good: Organize hierarchy logically
workspace/
└── Projects (page)
    ├── Task Database (database)
    └── Documentation (page)
        └── Guides (pages)

# Avoid: Too many workspace-level items
workspace/
├── Project 1 Database
├── Project 2 Database
├── Project 3 Database
# ... hard to manage permissions
```

### 2. API Creation Constraints

```python
# Check if parent type is supported for creation
# Databases via API: must be page parent
database = await client.databases.create(
    parent=ParentHelper.page(page_id="xxx"),  # OK
    # parent=ParentHelper.workspace(),  # NOT supported via API
    title="Tasks",
    ...
)
```

### 3. Parent Validation

```python
def validate_parent(child_type: str, parent: Parent) -> bool:
    """Validate if parent is compatible with child type."""
    valid_combinations = {
        "page": ["workspace", "page_id", "block_id", "data_source_id"],
        "database": ["workspace", "page_id", "block_id"],
        "block": ["page_id", "data_source_id", "block_id"]
    }

    return parent.type in valid_combinations.get(child_type, [])
```

## Emoji Objects

An **Emoji** object represents an emoji character, typically used as page or database icons.

### Standard Emoji

```json
{
  "type": "emoji",
  "emoji": "😻"
}
```

| Field | Type | Description |
|-------|------|-------------|
| `type` | string | Always `"emoji"` |
| `emoji` | string | The emoji character |

### Custom Emoji

Custom emojis are uploaded and managed in your workspace.

```json
{
  "type": "custom_emoji",
  "custom_emoji": {
    "id": "45ce454c-d427-4f53-9489-e5d0f3d1db6b",
    "name": "bufo",
    "url": "https://s3-us-west-2.amazonaws.com/.../3c6796979c50f4aa.png"
  }
}
```

| Field | Type | Description |
|-------|------|-------------|
| `type` | string | Always `"custom_emoji"` |
| `custom_emoji.id` | string (UUID) | Unique identifier |
| `custom_emoji.name` | string | Custom emoji name |
| `custom_emoji.url` | string | Image URL |

### Emoji SDK Implementation

```python
from typing import Union, Optional
from dataclasses import dataclass

@dataclass
class StandardEmoji:
    """Standard emoji character."""
    type: str = "emoji"
    emoji: str = None

@dataclass
class CustomEmoji:
    """Custom workspace emoji."""
    type: str = "custom_emoji"
    id: UUID = None
    name: str = None
    url: str = None

@dataclass
class CustomEmojiRef:
    """Reference to custom emoji (for updates)."""
    type: str = "custom_emoji"
    id: UUID = None

Emoji = Union[StandardEmoji, CustomEmoji, CustomEmojiRef, None]

def parse_emoji(data: Optional[dict]) -> Optional[Emoji]:
    """Parse emoji object from API response."""
    if not data:
        return None

    emoji_type = data.get("type")

    if emoji_type == "emoji":
        return StandardEmoji(**data)
    elif emoji_type == "custom_emoji":
        return CustomEmoji(**data)
    else:
        return None
```

### Usage Examples

```python
# Set page icon (create)
await client.pages.create(
    parent=ParentHelper.page(page_id="xxx"),
    properties={"title": "Avocado Page"},
    icon=StandardEmoji(emoji="🥑")
)

# Update page icon
await client.pages.update(
    page_id="xxx",
    icon=StandardEmoji(emoji="🥨")
)

# Set custom emoji icon
await client.pages.update(
    page_id="xxx",
    icon=CustomEmojiRef(id=UUID("45ce454c-d427-4f53-9489-e5d0f3d1db6b"))
)

# In rich text mentions
rich_text = {
    "type": "mention",
    "mention": {
        "type": "custom_emoji",
        "custom_emoji": {
            "id": "45ce454c-d427-4f53-9489-e5d0f3d1db6b",
            "name": "bufo",
            "url": "https://..."
        }
    }
}
```

## Link Previews (Unfurl Attributes)

A **Link Preview** is a real-time excerpt of authenticated content that displays when a user shares an enabled link in Notion. Developers can customize how links from their domains appear.

### Overview

Link Previews can be displayed in two formats:
1. **Full format** - Complete preview with all sections
2. **Mention** - Miniature version using same data

### Unfurl Attribute Object

Link Previews are built from an array of unfurl attribute objects. Each attribute maps to a section of the preview.

```json
{
  "id": "title",
  "name": "Title",
  "type": "inline",
  "inline": {
    "title": {
      "value": "Feature Request: Link Previews",
      "section": "title"
    }
  }
}
```

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Unique identifier (required: `"title"` and `"dev"` must exist) |
| `name` | string | Human-readable name |
| `type` | string | `"inline"` or `"embed"` |
| `inline` / `embed` | object | Sub-type object with value and section |

### Required Attributes

Every Link Preview must include:

1. **Title attribute** - The main heading
```json
{
  "id": "title",
  "name": "Title",
  "type": "inline",
  "inline": {
    "title": {
      "value": "Feature Request: Link Previews",
      "section": "title"
    }
  }
}
```

2. **Dev attribute** - Developer/company attribution
```json
{
  "id": "dev",
  "name": "Developer Name",
  "type": "inline",
  "inline": {
    "plain_text": {
      "value": "Acme Inc",
      "section": "secondary"
    }
  }
}
```

### Inline Sub-types

| Sub-type | Description | Example |
|----------|-------------|---------|
| `color` | RGB color values | `{"value": {"r": 247, "g": 247, "b": 42}, "section": "entity"}` |
| `date` | ISO 8601 date | `{"value": "2022-01-11", "section": "secondary"}` |
| `datetime` | ISO 8601 datetime | `{"value": "2022-01-11T19:53:18.829Z", "section": "secondary"}` |
| `enum` | String with optional color | `{"value": "Ready to Build", "color": {"r": 100, "g": 100, "b": 100}, "section": "primary"}` |
| `plain_text` | Any text content | `{"value": "Description text", "section": "body"}` |
| `title` | Title (required) | `{"value": "Page Title", "section": "title"}` |

### Embed Sub-types

| Sub-type | Description | Example |
|----------|-------------|---------|
| `audio` | Audio file | `{"src_url": "https://...", "audio": {"section": "embed"}}` |
| `html` | HTML in iFrame | `{"src_url": "https://...", "html": {"section": "embed"}}` |
| `image` | Image file | `{"src_url": "https://...", "image": {"section": "avatar"}}` |
| `video` | Video file | `{"src_url": "https://...", "video": {"section": "embed"}}` |

### Sections

The `section` value defines where content appears in the Link Preview.

| Section | Description | Valid Sub-types |
|---------|-------------|-----------------|
| `avatar` | Bottom-left picture | `image`, `plain_text` |
| `background` | Background color | `color` |
| `body` | Main content | `plain_text` |
| `embed` | Large content area | `audio`, `html`, `image`, `pdf`, `video` |
| `entity` | Subheading icon (small) | `color`, `image` |
| `identifier` | Bottom subheading / Mention left | `image`, `plain_text` |
| `primary` | First subheading | `enum`, `date`, `datetime`, `plain_text` |
| `secondary` | Second subheading | `date`, `datetime`, `plain_text` |
| `title` | Main heading (required) | `title` |

### Complete Example

```json
[
  {
    "id": "title",
    "name": "Title",
    "type": "inline",
    "inline": {
      "title": {
        "value": "Feature Request: Link Previews",
        "section": "title"
      }
    }
  },
  {
    "id": "dev",
    "name": "Developer Name",
    "type": "inline",
    "inline": {
      "plain_text": {
        "value": "Acme Inc",
        "section": "secondary"
      }
    }
  },
  {
    "id": "state",
    "name": "State",
    "type": "relation",
    "relation": {
      "uri": "acme:item_state/open",
      "mention": {
        "section": "primary"
      }
    }
  },
  {
    "id": "itemId",
    "name": "Item Id",
    "type": "inline",
    "inline": {
      "plain_text": {
        "value": "#23487",
        "section": "identifier"
      }
    }
  },
  {
    "id": "itemIcon",
    "name": "Item Icon",
    "type": "inline",
    "inline": {
      "color": {
        "value": {
          "r": 247,
          "g": 247,
          "b": 42
        },
        "section": "entity"
      }
    }
  },
  {
    "id": "description",
    "name": "Description",
    "type": "inline",
    "inline": {
      "plain_text": {
        "value": "Would love to be able to preview some Acme resources in Notion!",
        "section": "body"
      }
    }
  },
  {
    "id": "updated_at",
    "name": "Updated At",
    "type": "inline",
    "inline": {
      "datetime": {
        "value": "2022-01-11T19:53:18.829Z",
        "section": "secondary"
      }
    }
  },
  {
    "id": "label",
    "name": "Label",
    "type": "inline",
    "inline": {
      "enum": {
        "value": "🔨 Ready to Build",
        "color": {
          "r": 100,
          "g": 100,
          "b": 100
        },
        "section": "primary"
      }
    }
  },
  {
    "id": "media",
    "name": "Embed",
    "embed": {
      "src_url": "https://c.tenor.com/XgaU95K_XiwAAAAC/kermit-typing.gif",
      "image": {
        "section": "embed"
      }
    }
  }
]
```

### Link Preview SDK

```python
from dataclasses import dataclass, field
from typing import List, Union, Optional, Dict, Any
from datetime import datetime

@dataclass
class Color:
    """RGB color."""
    r: int
    g: int
    b: int

@dataclass
class UnfurlAttribute:
    """Base unfurl attribute."""
    id: str
    name: str
    type: str  # "inline" or "embed"

@dataclass
class TitleValue:
    """Title sub-type value."""
    value: str
    section: str

@dataclass
class PlainTextValue:
    """Plain text sub-type value."""
    value: str
    section: str

@dataclass
class DateTimeValue:
    """Datetime sub-type value."""
    value: datetime
    section: str

@dataclass
class EnumValue:
    """Enum sub-type value."""
    value: str
    section: str
    color: Optional[Color] = None

@dataclass
class ColorValue:
    """Color sub-type value."""
    value: Color
    section: str

@dataclass
class EmbedValue:
    """Embed sub-type value."""
    src_url: str
    # Sub-type specific (audio, html, image, video)
    audio: Optional[Dict] = None
    html: Optional[Dict] = None
    image: Optional[Dict] = None
    video: Optional[Dict] = None

@dataclass
class InlineUnfurl(UnfurlAttribute):
    """Inline unfurl attribute."""
    inline: Union[TitleValue, PlainTextValue, DateTimeValue, EnumValue, ColorValue]

@dataclass
class EmbedUnfurl(UnfurlAttribute):
    """Embed unfurl attribute."""
    embed: EmbedValue

UnfurlAttribute = Union[InlineUnfurl, EmbedUnfurl]

class LinkPreviewBuilder:
    """Builder for creating link preview unfurl attributes."""

    @staticmethod
    def title(value: str) -> InlineUnfurl:
        """Create required title attribute."""
        return InlineUnfurl(
            id="title",
            name="Title",
            type="inline",
            inline=TitleValue(value=value, section="title")
        )

    @staticmethod
    def dev(value: str) -> InlineUnfurl:
        """Create required dev (developer) attribute."""
        return InlineUnfurl(
            id="dev",
            name="Developer Name",
            type="inline",
            inline=PlainTextValue(value=value, section="secondary")
        )

    @staticmethod
    def plain_text(id: str, name: str, value: str, section: str) -> InlineUnfurl:
        """Create a plain text attribute."""
        return InlineUnfurl(
            id=id,
            name=name,
            type="inline",
            inline=PlainTextValue(value=value, section=section)
        )

    @staticmethod
    def datetime(id: str, name: str, value: datetime, section: str = "secondary") -> InlineUnfurl:
        """Create a datetime attribute."""
        return InlineUnfurl(
            id=id,
            name=name,
            type="inline",
            inline=DateTimeValue(value=value, section=section)
        )

    @staticmethod
    def enum(id: str, name: str, value: str, section: str = "primary", color: Optional[Color] = None) -> InlineUnfurl:
        """Create an enum attribute."""
        return InlineUnfurl(
            id=id,
            name=name,
            type="inline",
            inline=EnumValue(value=value, section=section, color=color)
        )

    @staticmethod
    def image(id: str, name: str, src_url: str, section: str = "embed") -> EmbedUnfurl:
        """Create an image embed attribute."""
        return EmbedUnfurl(
            id=id,
            name=name,
            type="embed",
            embed=EmbedValue(src_url=src_url, image={"section": section})
        )

    @staticmethod
    def build(attributes: List[UnfurlAttribute]) -> List[dict]:
        """Build unfurl attributes array for API."""
        result = []
        for attr in attributes:
            data = {
                "id": attr.id,
                "name": attr.name,
                "type": attr.type
            }

            if isinstance(attr, InlineUnfurl):
                if isinstance(attr.inline, TitleValue):
                    data["inline"] = {
                        "title": {
                            "value": attr.inline.value,
                            "section": attr.inline.section
                        }
                    }
                elif isinstance(attr.inline, PlainTextValue):
                    data["inline"] = {
                        "plain_text": {
                            "value": attr.inline.value,
                            "section": attr.inline.section
                        }
                    }
                elif isinstance(attr.inline, DateTimeValue):
                    data["inline"] = {
                        "datetime": {
                            "value": attr.inline.value.isoformat(),
                            "section": attr.inline.section
                        }
                    }
                elif isinstance(attr.inline, EnumValue):
                    enum_data = {
                        "value": attr.inline.value,
                        "section": attr.inline.section
                    }
                    if attr.inline.color:
                        enum_data["color"] = {
                            "r": attr.inline.color.r,
                            "g": attr.inline.color.g,
                            "b": attr.inline.color.b
                        }
                    data["inline"] = {"enum": enum_data}

            elif isinstance(attr, EmbedUnfurl):
                embed_data = {"src_url": attr.embed.src_url}
                if attr.embed.image:
                    embed_data["image"] = attr.embed.image
                if attr.embed.video:
                    embed_data["video"] = attr.embed.video
                if attr.embed.audio:
                    embed_data["audio"] = attr.embed.audio
                if attr.embed.html:
                    embed_data["html"] = attr.embed.html
                data["embed"] = embed_data

            result.append(data)

        return result
```

### Usage Example

```python
from datetime import datetime

# Build link preview for a task
attributes = LinkPreviewBuilder.build([
    LinkPreviewBuilder.title("Feature Request: Link Previews"),
    LinkPreviewBuilder.dev("Acme Inc"),
    LinkPreviewBuilder.plain_text(
        id="itemId",
        name="Item Id",
        value="#23487",
        section="identifier"
    ),
    LinkPreviewBuilder.enum(
        id="status",
        name="Status",
        value="🔨 Ready to Build",
        section="primary",
        color=Color(r=100, g=100, b=100)
    ),
    LinkPreviewBuilder.plain_text(
        id="description",
        name="Description",
        value="Would love to be able to preview resources in Notion!",
        section="body"
    ),
    LinkPreviewBuilder.datetime(
        id="updated_at",
        name="Updated At",
        value=datetime(2022, 1, 11, 19, 53, 18),
        section="secondary"
    ),
    LinkPreviewBuilder.image(
        id="preview",
        name="Preview",
        src_url="https://example.com/preview.gif",
        section="embed"
    )
])

# Send to Notion API (when implementing Link Preview integration)
# ... API call with attributes array
```

## Related Documentation

- [Pages](./pages/pages-overview.md) - Page structure and properties
- [Databases](./databases/databases-overview.md) - Database structure
- [Blocks](./block/blocks-overview.md) - Block hierarchy
- [Rich Text Objects](./rich-text-objects.md) - Mention types
- [Link Preview Integration Guide](https://developers.notion.com/docs/link-preview-introduction) - Build Link Preview integrations

---

**Next:** See [Search](./search.md) for information about searching across all entity types.
