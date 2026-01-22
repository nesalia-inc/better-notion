# Rich Text Objects

Official Notion API documentation for rich text objects used throughout the API.

## Overview

Notion uses rich text objects to represent styled and formatted content across blocks. Rich text allows for various styling decisions such as italics, font size, font color, hyperlinks, and code blocks.

**Key Points:**
- Rich text objects are included in block objects
- Not all block types support rich text
- Blocks return an **array** of rich text objects
- Each object includes a `plain_text` property for easy access to unformatted text

## Rich Text Object Structure

Every rich text object contains the following fields:

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `type` | string (enum) | The type of rich text object. Possible values: `"text"`, `"mention"`, `"equation"` | `"text"` |
| `text` \| `mention` \| `equation` | object | Type-specific configuration (varies by type) | See below |
| `annotations` | object | Styling information | See below |
| `plain_text` | string | Plain text without annotations | `"Some words "` |
| `href` | string (optional) | URL of any link or mention | `"https://notion.so/..."`

## Annotation Object

All rich text objects contain an `annotations` object that sets the styling.

### Annotation Properties

| Property | Type | Description | Example |
|----------|------|-------------|---------|
| `bold` | boolean | Whether the text is bolded | `true` |
| `italic` | boolean | Whether the text is italicized | `true` |
| `strikethrough` | boolean | Whether the text is struck through | `false` |
| `underline` | boolean | Whether the text is underlined | `false` |
| `code` | boolean | Whether the text is code style (monospace) | `true` |
| `color` | string (enum) | Color of the text | `"green"` |

### Color Values

**Text Colors:**
- `blue`
- `brown`
- `gray`
- `green`
- `orange`
- `pink`
- `purple`
- `red`
- `yellow`
- `default`

**Background Colors:**
- `blue_background`
- `brown_background`
- `gray_background`
- `green_background`
- `orange_background`
- `pink_background`
- `purple_background`
- `red_background`
- `yellow_background`
- `default`

### Example Annotation Object

```json
{
  "bold": true,
  "italic": false,
  "strikethrough": false,
  "underline": false,
  "code": false,
  "color": "blue"
}
```

---

## Rich Text Types

### 1. Text

**Type:** `"text"`

The most common rich text type for plain text with optional formatting and links.

#### Text Object Properties

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `content` | string | The actual text content | `"Some words "` |
| `link` | object (optional) | Link information if text is a hyperlink, otherwise `null` | `{ "url": "https://..." }` |

#### Link Object Structure

```json
{
  "url": "https://developers.notion.com/"
}
```

#### Example: Text Without Link

```json
{
  "type": "text",
  "text": {
    "content": "This is an ",
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
  "plain_text": "This is an ",
  "href": null
}
```

#### Example: Text With Link

```json
{
  "type": "text",
  "text": {
    "content": "inline link",
    "link": {
      "url": "https://developers.notion.com/"
    }
  },
  "annotations": {
    "bold": false,
    "italic": false,
    "strikethrough": false,
    "underline": false,
    "code": false,
    "color": "default"
  },
  "plain_text": "inline link",
  "href": "https://developers.notion.com/"
}
```

**Note:** When text contains a link, it's typically styled with `underline: true` and `color: "blue"` in the annotations.

---

### 2. Equation

**Type:** `"equation"`

Notion supports inline LaTeX equations as rich text objects.

#### Equation Object Properties

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `expression` | string | The LaTeX string representing the inline equation | `"E = mc^2"` |

#### Example Equation

```json
{
  "type": "equation",
  "equation": {
    "expression": "E = mc^2"
  },
  "annotations": {
    "bold": false,
    "italic": false,
    "strikethrough": false,
    "underline": false,
    "code": false,
    "color": "default"
  },
  "plain_text": "E = mc^2",
  "href": null
}
```

**Note:** Equations always have `"code": true` in annotations.

#### Complex Equation Example

```json
{
  "type": "equation",
  "equation": {
    "expression": "\\frac{{ - b \\pm \\sqrt {b^2 - 4ac} }}{{2a}}"
  },
  "annotations": {
    "bold": false,
    "italic": false,
    "strikethrough": false,
    "underline": false,
    "code": true,
    "color": "default"
  },
  "plain_text": "\\frac{{ - b \\pm \\sqrt {b^2 - 4ac} }}{{2a}}",
  "href": null
}
```

---

### 3. Mention

**Type:** `"mention"`

Mention objects represent inline mentions of databases, dates, link previews, pages, template placeholders, or users.

#### Mention Object Properties

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `type` | string (enum) | The mention type. Possible values: `"database"`, `"date"`, `"link_preview"`, `"page"`, `"template_mention"`, `"user"` | `"user"` |
| `database` \| `date` \| `link_preview` \| `page` \| `template_mention` \| `user` | object | Type-specific configuration (varies by mention type) | See below |

#### Mention Types

---

##### 3.1 Database Mention

**Type:** `"database"`

Contains a reference to a Notion database.

##### Database Mention Properties

| Field | Type | Description |
|-------|------|-------------|
| `id` | string (UUIDv4) | The database ID |

##### Access Behavior

If the integration doesn't have access to the mentioned database:
- Only the `id` is returned
- `plain_text` appears as `"Untitled"`
- Default annotation values

##### Example Database Mention

```json
{
  "type": "mention",
  "mention": {
    "type": "database",
    "database": {
      "id": "a1d8501e-1ac1-43e9-a6bd-ea9fe6c8822b"
    }
  },
  "annotations": {
    "bold": false,
    "italic": false,
    "strikethrough": false,
    "underline": false,
    "code": false,
    "color": "default"
  },
  "plain_text": "Database with test things",
  "href": "https://www.notion.so/a1d8501e1ac143e9a6bdea9fe6c8822b"
}
```

---

##### 3.2 Date Mention

**Type:** `"date"`

Contains a date property value object.

##### Date Mention Properties

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `start` | string (ISO 8601) | Start date/time | `"2022-12-16"` |
| `end` | string (ISO 8601) \| null | End date/time (for ranges) | `null` |

##### Example Date Mention

```json
{
  "type": "mention",
  "mention": {
    "type": "date",
    "date": {
      "start": "2022-12-16",
      "end": null
    }
  },
  "annotations": {
    "bold": false,
    "italic": false,
    "strikethrough": false,
    "underline": false,
    "code": false,
    "color": "default"
  },
  "plain_text": "2022-12-16",
  "href": null
}
```

---

##### 3.3 Link Preview Mention

**Type:** `"link_preview"`

A shared link preview as an inline mention.

##### Link Preview Mention Properties

| Field | Type | Description |
|-------|------|-------------|
| `url` | string | The URL used to create the link preview |

##### Example Link Preview Mention

```json
{
  "type": "mention",
  "mention": {
    "type": "link_preview",
    "link_preview": {
      "url": "https://workspace.slack.com/archives/C04PF0F9QSD/p1671139297838409"
    }
  },
  "annotations": {
    "bold": false,
    "italic": false,
    "strikethrough": false,
    "underline": false,
    "code": false,
    "color": "default"
  },
  "plain_text": "https://workspace.slack.com/archives/C04PF0F9QSD/p1671139297838409",
  "href": "https://workspace.slack.com/archives/C04PF0F9QSD/p1671139297838409"
}
```

---

##### 3.4 Page Mention

**Type:** `"page"`

Contains a reference to a Notion page.

##### Page Mention Properties

| Field | Type | Description |
|-------|------|-------------|
| `id` | string (UUIDv4) | The page ID |

##### Access Behavior

If the integration doesn't have access to the mentioned page:
- Only the `id` is returned
- `plain_text` appears as `"Untitled"`
- Default annotation values

##### Example Page Mention

```json
{
  "type": "mention",
  "mention": {
    "type": "page",
    "page": {
      "id": "3c612f56-fdd0-4a30-a4d6-bda7d7426309"
    }
  },
  "annotations": {
    "bold": false,
    "italic": false,
    "strikethrough": false,
    "underline": false,
    "code": false,
    "color": "default"
  },
  "plain_text": "This is a test page",
  "href": "https://www.notion.so/3c612f56fdd04a30a4d6bda7d7426309"
}
```

---

##### 3.5 Template Mention

**Type:** `"template_mention"`

Placeholder mentions in template buttons that populate when a template is duplicated.

##### Template Mention Structure

Contains a nested `template_mention` object with its own `type` field:

- `"template_mention_date"` - Date placeholders
- `"template_mention_user"` - User placeholders

---

###### Template Mention: Date

**Type:** `"template_mention_date"`

| Field | Type | Description | Possible Values |
|-------|------|-------------|-----------------|
| `template_mention_date` | string (enum) | The date placeholder type | `"today"`, `"now"` |

##### Example Template Date Mention

```json
{
  "type": "mention",
  "mention": {
    "type": "template_mention",
    "template_mention": {
      "type": "template_mention_date",
      "template_mention_date": "today"
    }
  },
  "annotations": {
    "bold": false,
    "italic": false,
    "strikethrough": false,
    "underline": false,
    "code": false,
    "color": "default"
  },
  "plain_text": "@Today",
  "href": null
}
```

---

###### Template Mention: User

**Type:** `"template_mention_user"`

| Field | Type | Description | Possible Values |
|-------|------|-------------|-----------------|
| `template_mention_user` | string (enum) | The user placeholder type | `"me"` |

##### Example Template User Mention

```json
{
  "type": "mention",
  "mention": {
    "type": "template_mention",
    "template_mention": {
      "type": "template_mention_user",
      "template_mention_user": "me"
    }
  },
  "annotations": {
    "bold": false,
    "italic": false,
    "strikethrough": false,
    "underline": false,
    "code": false,
    "color": "default"
  },
  "plain_text": "@Me",
  "href": null
}
```

---

##### 3.6 User Mention

**Type:** `"user"`

Contains a reference to a Notion user.

##### User Mention Properties

| Field | Type | Description |
|-------|------|-------------|
| `object` | string | Always `"user"` |
| `id` | string (UUIDv4) | The user ID |

##### Access Behavior

If the integration doesn't have access to the mentioned user:
- `plain_text` reads as `"@Anonymous"`
- Update integration capabilities to gain access

##### Example User Mention

```json
{
  "type": "mention",
  "mention": {
    "type": "user",
    "user": {
      "object": "user",
      "id": "b2e19928-b427-4aad-9a9d-fde65479b1d9"
    }
  },
  "annotations": {
    "bold": false,
    "italic": false,
    "strikethrough": false,
    "underline": false,
    "code": false,
    "color": "default"
  },
  "plain_text": "@Anonymous",
  "href": null
}
```

---

## SDK Implementation

### Rich Text Object Enum

```python
from enum import Enum

class RichTextType(str, Enum):
    """Types of rich text objects."""
    TEXT = "text"
    MENTION = "mention"
    EQUATION = "equation"

class MentionType(str, Enum):
    """Types of mentions."""
    DATABASE = "database"
    DATE = "date"
    LINK_PREVIEW = "link_preview"
    PAGE = "page"
    TEMPLATE_MENTION = "template_mention"
    USER = "user"

class TemplateMentionType(str, Enum):
    """Types of template mentions."""
    DATE = "template_mention_date"
    USER = "template_mention_user"

class RichTextColor(str, Enum):
    """Rich text colors."""
    # Text colors
    BLUE = "blue"
    BROWN = "brown"
    GRAY = "gray"
    GREEN = "green"
    ORANGE = "orange"
    PINK = "pink"
    PURPLE = "purple"
    RED = "red"
    YELLOW = "yellow"
    DEFAULT = "default"

    # Background colors
    BLUE_BACKGROUND = "blue_background"
    BROWN_BACKGROUND = "brown_background"
    GRAY_BACKGROUND = "gray_background"
    GREEN_BACKGROUND = "green_background"
    ORANGE_BACKGROUND = "orange_background"
    PINK_BACKGROUND = "pink_background"
    PURPLE_BACKGROUND = "purple_background"
    RED_BACKGROUND = "red_background"
    YELLOW_BACKGROUND = "yellow_background"
```

### Rich Text Object Classes

```python
from dataclasses import dataclass, field
from typing import Optional, List
from uuid import UUID
from datetime import datetime

@dataclass
class Annotations:
    """Rich text annotations for styling."""
    bold: bool = False
    italic: bool = False
    strikethrough: bool = False
    underline: bool = False
    code: bool = False
    color: RichTextColor = RichTextColor.DEFAULT

@dataclass
class RichTextObject:
    """Base class for rich text objects."""
    type: RichTextType
    annotations: Annotations = field(default_factory=Annotations)
    plain_text: str = ""
    href: Optional[str] = None

    def to_dict(self) -> dict:
        """Convert to API-compatible dict."""
        raise NotImplementedError

@dataclass
class TextObject(RichTextObject):
    """Plain text rich text object."""
    type: RichTextType = RichTextType.TEXT
    content: str = ""
    link: Optional[dict] = None  # {"url": "..."} or None

    def to_dict(self) -> dict:
        """Convert to API-compatible dict."""
        return {
            "type": self.type.value,
            "text": {
                "content": self.content,
                "link": self.link
            },
            "annotations": {
                "bold": self.annotations.bold,
                "italic": self.annotations.italic,
                "strikethrough": self.annotations.strikethrough,
                "underline": self.annotations.underline,
                "code": self.annotations.code,
                "color": self.annotations.color.value
            },
            "plain_text": self.plain_text,
            "href": self.href
        }

@dataclass
class EquationObject(RichTextObject):
    """Equation rich text object."""
    type: RichTextType = RichTextType.EQUATION
    expression: str = ""

    def __post_init__(self):
        """Equations always have code style."""
        self.annotations.code = True

    def to_dict(self) -> dict:
        """Convert to API-compatible dict."""
        return {
            "type": self.type.value,
            "equation": {
                "expression": self.expression
            },
            "annotations": {
                "bold": self.annotations.bold,
                "italic": self.annotations.italic,
                "strikethrough": self.annotations.strikethrough,
                "underline": self.annotations.underline,
                "code": self.annotations.code,
                "color": self.annotations.color.value
            },
            "plain_text": self.plain_text,
            "href": self.href
        }

@dataclass
class MentionObject(RichTextObject):
    """Base mention object."""
    type: RichTextType = RichTextType.MENTION
    mention_type: MentionType = None

    def to_dict(self) -> dict:
        """Convert to API-compatible dict."""
        raise NotImplementedError

@dataclass
class DatabaseMention(MentionObject):
    """Database mention."""
    mention_type: MentionType = MentionType.DATABASE
    database_id: UUID = None

    def to_dict(self) -> dict:
        """Convert to API-compatible dict."""
        return {
            "type": self.type.value,
            "mention": {
                "type": self.mention_type.value,
                "database": {
                    "id": str(self.database_id)
                }
            },
            "annotations": {
                "bold": self.annotations.bold,
                "italic": self.annotations.italic,
                "strikethrough": self.annotations.strikethrough,
                "underline": self.annotations.underline,
                "code": self.annotations.code,
                "color": self.annotations.color.value
            },
            "plain_text": self.plain_text,
            "href": self.href
        }

@dataclass
class DateMention(MentionObject):
    """Date mention."""
    mention_type: MentionType = MentionType.DATE
    start: str = ""  # ISO 8601 date
    end: Optional[str] = None  # ISO 8601 date

    def to_dict(self) -> dict:
        """Convert to API-compatible dict."""
        return {
            "type": self.type.value,
            "mention": {
                "type": self.mention_type.value,
                "date": {
                    "start": self.start,
                    "end": self.end
                }
            },
            "annotations": {
                "bold": self.annotations.bold,
                "italic": self.annotations.italic,
                "strikethrough": self.annotations.strikethrough,
                "underline": self.annotations.underline,
                "code": self.annotations.code,
                "color": self.annotations.color.value
            },
            "plain_text": self.plain_text,
            "href": self.href
        }

@dataclass
class LinkPreviewMention(MentionObject):
    """Link preview mention."""
    mention_type: MentionType = MentionType.LINK_PREVIEW
    url: str = ""

    def to_dict(self) -> dict:
        """Convert to API-compatible dict."""
        return {
            "type": self.type.value,
            "mention": {
                "type": self.mention_type.value,
                "link_preview": {
                    "url": self.url
                }
            },
            "annotations": {
                "bold": self.annotations.bold,
                "italic": self.annotations.italic,
                "strikethrough": self.annotations.strikethrough,
                "underline": self.annotations.underline,
                "code": self.annotations.code,
                "color": self.annotations.color.value
            },
            "plain_text": self.plain_text,
            "href": self.href
        }

@dataclass
class PageMention(MentionObject):
    """Page mention."""
    mention_type: MentionType = MentionType.PAGE
    page_id: UUID = None

    def to_dict(self) -> dict:
        """Convert to API-compatible dict."""
        return {
            "type": self.type.value,
            "mention": {
                "type": self.mention_type.value,
                "page": {
                    "id": str(self.page_id)
                }
            },
            "annotations": {
                "bold": self.annotations.bold,
                "italic": self.annotations.italic,
                "strikethrough": self.annotations.strikethrough,
                "underline": self.annotations.underline,
                "code": self.annotations.code,
                "color": self.annotations.color.value
            },
            "plain_text": self.plain_text,
            "href": self.href
        }

@dataclass
class UserMention(MentionObject):
    """User mention."""
    mention_type: MentionType = MentionType.USER
    user_id: UUID = None

    def to_dict(self) -> dict:
        """Convert to API-compatible dict."""
        return {
            "type": self.type.value,
            "mention": {
                "type": self.mention_type.value,
                "user": {
                    "object": "user",
                    "id": str(self.user_id)
                }
            },
            "annotations": {
                "bold": self.annotations.bold,
                "italic": self.annotations.italic,
                "strikethrough": self.annotations.strikethrough,
                "underline": self.annotations.underline,
                "code": self.annotations.code,
                "color": self.annotations.color.value
            },
            "plain_text": self.plain_text,
            "href": self.href
        }

@dataclass
class TemplateDateMention(MentionObject):
    """Template mention for date placeholders."""
    mention_type: MentionType = MentionType.TEMPLATE_MENTION
    template_type: TemplateMentionType = TemplateMentionType.DATE
    value: str = "today"  # "today" or "now"

    def to_dict(self) -> dict:
        """Convert to API-compatible dict."""
        return {
            "type": self.type.value,
            "mention": {
                "type": self.mention_type.value,
                "template_mention": {
                    "type": self.template_type.value,
                    "template_mention_date": self.value
                }
            },
            "annotations": {
                "bold": self.annotations.bold,
                "italic": self.annotations.italic,
                "strikethrough": self.annotations.strikethrough,
                "underline": self.annotations.underline,
                "code": self.annotations.code,
                "color": self.annotations.color.value
            },
            "plain_text": self.plain_text,
            "href": self.href
        }

@dataclass
class TemplateUserMention(MentionObject):
    """Template mention for user placeholders."""
    mention_type: MentionType = MentionType.TEMPLATE_MENTION
    template_type: TemplateMentionType = TemplateMentionType.USER
    value: str = "me"  # Always "me"

    def to_dict(self) -> dict:
        """Convert to API-compatible dict."""
        return {
            "type": self.type.value,
            "mention": {
                "type": self.mention_type.value,
                "template_mention": {
                    "type": self.template_type.value,
                    "template_mention_user": self.value
                }
            },
            "annotations": {
                "bold": self.annotations.bold,
                "italic": self.annotations.italic,
                "strikethrough": self.annotations.strikethrough,
                "underline": self.annotations.underline,
                "code": self.annotations.code,
                "color": self.annotations.color.value
            },
            "plain_text": self.plain_text,
            "href": self.href
        }
```

### Rich Text Parser

```python
class RichTextParser:
    """Parse rich text objects from API responses."""

    @staticmethod
    def parse(data: dict) -> RichTextObject:
        """Parse a single rich text object."""
        obj_type = RichTextType(data.get("type"))

        # Parse annotations
        annotations_data = data.get("annotations", {})
        annotations = Annotations(
            bold=annotations_data.get("bold", False),
            italic=annotations_data.get("italic", False),
            strikethrough=annotations_data.get("strikethrough", False),
            underline=annotations_data.get("underline", False),
            code=annotations_data.get("code", False),
            color=RichTextColor(annotations_data.get("color", "default"))
        )

        # Common fields
        plain_text = data.get("plain_text", "")
        href = data.get("href")

        # Parse type-specific data
        if obj_type == RichTextType.TEXT:
            text_data = data.get("text", {})
            return TextObject(
                content=text_data.get("content", ""),
                link=text_data.get("link"),
                annotations=annotations,
                plain_text=plain_text,
                href=href
            )

        elif obj_type == RichTextType.EQUATION:
            equation_data = data.get("equation", {})
            return EquationObject(
                expression=equation_data.get("expression", ""),
                annotations=annotations,
                plain_text=plain_text,
                href=href
            )

        elif obj_type == RichTextType.MENTION:
            mention_data = data.get("mention", {})
            mention_type = MentionType(mention_data.get("type"))

            if mention_type == MentionType.DATABASE:
                db_data = mention_data.get("database", {})
                return DatabaseMention(
                    database_id=UUID(db_data.get("id")),
                    annotations=annotations,
                    plain_text=plain_text,
                    href=href
                )

            elif mention_type == MentionType.DATE:
                date_data = mention_data.get("date", {})
                return DateMention(
                    start=date_data.get("start", ""),
                    end=date_data.get("end"),
                    annotations=annotations,
                    plain_text=plain_text,
                    href=href
                )

            elif mention_type == MentionType.LINK_PREVIEW:
                lp_data = mention_data.get("link_preview", {})
                return LinkPreviewMention(
                    url=lp_data.get("url", ""),
                    annotations=annotations,
                    plain_text=plain_text,
                    href=href
                )

            elif mention_type == MentionType.PAGE:
                page_data = mention_data.get("page", {})
                return PageMention(
                    page_id=UUID(page_data.get("id")),
                    annotations=annotations,
                    plain_text=plain_text,
                    href=href
                )

            elif mention_type == MentionType.USER:
                user_data = mention_data.get("user", {})
                return UserMention(
                    user_id=UUID(user_data.get("id")),
                    annotations=annotations,
                    plain_text=plain_text,
                    href=href
                )

            elif mention_type == MentionType.TEMPLATE_MENTION:
                tm_data = mention_data.get("template_mention", {})
                tm_type = TemplateMentionType(tm_data.get("type"))

                if tm_type == TemplateMentionType.DATE:
                    return TemplateDateMention(
                        value=tm_data.get("template_mention_date", "today"),
                        annotations=annotations,
                        plain_text=plain_text,
                        href=href
                    )
                elif tm_type == TemplateMentionType.USER:
                    return TemplateUserMention(
                        value=tm_data.get("template_mention_user", "me"),
                        annotations=annotations,
                        plain_text=plain_text,
                        href=href
                    )

        raise ValueError(f"Unknown rich text object type: {obj_type}")

    @staticmethod
    def parse_array(data: List[dict]) -> List[RichTextObject]:
        """Parse an array of rich text objects."""
        return [RichTextParser.parse(item) for item in data]
```

### Usage Examples

```python
# Parse rich text from API response
api_response = {
    "rich_text": [
        {
            "type": "text",
            "text": {
                "content": "Hello, ",
                "link": None
            },
            "annotations": {
                "bold": False,
                "italic": False,
                "strikethrough": False,
                "underline": False,
                "code": False,
                "color": "default"
            },
            "plain_text": "Hello, ",
            "href": None
        },
        {
            "type": "mention",
            "mention": {
                "type": "user",
                "user": {
                    "object": "user",
                    "id": "b2e19928-b427-4aad-9a9d-fde65479b1d9"
                }
            },
            "annotations": {
                "bold": False,
                "italic": False,
                "strikethrough": False,
                "underline": False,
                "code": False,
                "color": "default"
            },
            "plain_text": "@Anonymous",
            "href": None
        }
    ]
}

rich_text_objects = RichTextParser.parse_array(api_response["rich_text"])

# Create a text object
text = TextObject(
    content="Click here",
    link={"url": "https://example.com"},
    annotations=Annotations(underline=True, color=RichTextColor.BLUE),
    plain_text="Click here",
    href="https://example.com"
)

# Create an equation
equation = EquationObject(
    expression="E = mc^2",
    plain_text="E = mc^2"
)

# Create a user mention
user_mention = UserMention(
    user_id=UUID("b2e19928-b427-4aad-9a9d-fde65479b1d9"),
    plain_text="@John Doe"
)

# Convert to API format
api_format = text.to_dict()
```

## Request Limits

Refer to the Notion API request limits documentation for information about limits on the size of rich text objects.

## Related Documentation

- [Block Types](./block/block-types.md) - Blocks that use rich text
- [Rich Text Reference](./block/rich-text.md) - Implementation guide
- [Blocks Overview](./block/blocks-overview.md) - Block concepts

---

**Better Notion SDK** - This document provides the official API structure for rich text objects used throughout the Notion API.
