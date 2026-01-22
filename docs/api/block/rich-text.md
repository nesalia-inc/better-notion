# Rich Text Reference

Rich text is the content format used in most Notion blocks. It provides text formatting capabilities including styles, colors, links, mentions, and equations.

## Overview

Rich text in Notion is represented as an **array of text segments**, where each segment can have different formatting. This allows for mixed formatting within a single block (e.g., "**bold** and *italic* text").

```json
{
  "rich_text": [
    {
      "type": "text",
      "text": {
        "content": "Hello ",
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
      "plain_text": "Hello ",
      "href": null
    },
    {
      "type": "text",
      "text": {
        "content": "world",
        "link": null
      },
      "annotations": {
        "bold": false,
        "italic": true,
        "strikethrough": false,
        "underline": false,
        "code": false,
        "color": "blue"
      },
      "plain_text": "world",
      "href": null
    }
  ]
}
```

## Rich Text Segment Types

Each segment in the `rich_text` array has a `type` field that determines its structure.

### 1. Text

**Type:** `text`

The most common segment type for plain text with optional formatting.

**Structure:**
```json
{
  "type": "text",
  "text": {
    "content": "The text content",
    "link": null
  },
  "annotations": { /* ... */ },
  "plain_text": "The text content",
  "href": null
}
```

**Properties:**

| Field | Type | Description |
|-------|------|-------------|
| `type` | string | Always `"text"` |
| `text.content` | string | The actual text content |
| `text.link` | object \| null | Link object if text is a hyperlink |
| `annotations` | object | Formatting annotations (see below) |
| `plain_text` | string | Unformatted text for quick access |
| `href` | string \| null | URL if text has a link |

**Link Object:**
```json
{
  "type": "url",
  "url": "https://example.com"
}
```

---

### 2. Mention

**Type:** `mention`

Represents @mentions in Notion - users, dates, pages, databases, or link previews.

**Structure:**
```json
{
  "type": "mention",
  "mention": {
    "type": "user",  // or "date", "page", "database", "link_preview"
    "user": {
      "object": "user",
      "id": "user-uuid"
    }
    // OR for dates:
    // "date": { "start": "2023-03-01", "end": null, "time_zone": null }
    // OR for pages:
    // "page": { "id": "page-uuid" }
    // OR for databases:
    // "database": { "id": "database-uuid" }
  },
  "annotations": { /* ... */ },
  "plain_text": "@User Name",
  "href": null
}
```

**Mention Types:**

| Type | Description | Structure |
|------|-------------|-----------|
| `user` | @mention a user | `{ "id": "uuid" }` |
| `date` | @mention a date | `{ "start": "2023-01-01", "end": null, "time_zone": null }` |
| `page` | @mention a page | `{ "id": "uuid" }` |
| `database` | @mention a database | `{ "id": "uuid" }` |
| `link_preview` | Miniaturized link preview | `{ "url": "https://..." }` |

---

### 3. Equation

**Type:** `equation`

Represents a mathematical equation using KaTeX syntax.

**Structure:**
```json
{
  "type": "equation",
  "equation": {
    "expression": "e = mc^2"
  },
  "annotations": {
    "code": true,  // Always true for equations
    "bold": false,
    "italic": false,
    "strikethrough": false,
    "underline": false,
    "color": "default"
  },
  "plain_text": "e = mc^2",
  "href": null
}
```

---

## Annotations

Annotations control text formatting and are present in all rich text segment types.

**Annotation Structure:**
```json
{
  "bold": false,
  "italic": false,
  "strikethrough": false,
  "underline": false,
  "code": false,
  "color": "default"
}
```

### Annotation Properties

| Property | Type | Description |
|----------|------|-------------|
| `bold` | boolean | **bold text** |
| `italic` | boolean | *italic text* |
| `strikethrough` | boolean | ~~strikethrough~~ |
| `underline` | boolean | <u>underlined</u> text |
| `code` | boolean | `monospace code` |
| `color` | string | Text/background color (see colors below) |

### Color Values

**Text Colors:**
- `blue`, `brown`, `gray`, `green`, `orange`, `pink`, `purple`, `red`, `yellow`, `default`

**Background Colors:**
- `blue_background`, `brown_background`, `gray_background`, `green_background`, `orange_background`, `pink_background`, `purple_background`, `red_background`, `yellow_background`, `default`

**SDK Implementation:**
```python
class TextColor(str, Enum):
    """Text and background colors for rich text."""

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

---

## Complete Examples

### Example 1: Simple Paragraph with Formatting

**Text:** "This is **bold** and *italic*."

```json
{
  "rich_text": [
    {
      "type": "text",
      "text": {
        "content": "This is ",
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
      "plain_text": "This is ",
      "href": null
    },
    {
      "type": "text",
      "text": {
        "content": "bold",
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
      "plain_text": "bold",
      "href": null
    },
    {
      "type": "text",
      "text": {
        "content": " and ",
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
      "plain_text": " and ",
      "href": null
    },
    {
      "type": "text",
      "text": {
        "content": "italic",
        "link": null
      },
      "annotations": {
        "bold": false,
        "italic": true,
        "strikethrough": false,
        "underline": false,
        "code": false,
        "color": "default"
      },
      "plain_text": "italic",
      "href": null
    },
    {
      "type": "text",
      "text": {
        "content": ".",
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
      "plain_text": ".",
      "href": null
    }
  ]
}
```

### Example 2: Text with Hyperlink

**Text:** "Visit [our website](https://example.com) for more."

```json
{
  "rich_text": [
    {
      "type": "text",
      "text": {
        "content": "Visit ",
        "link": null
      },
      "annotations": { /* default */ },
      "plain_text": "Visit ",
      "href": null
    },
    {
      "type": "text",
      "text": {
        "content": "our website",
        "link": {
          "type": "url",
          "url": "https://example.com"
        }
      },
      "annotations": {
        "bold": false,
        "italic": false,
        "strikethrough": false,
        "underline": true,  // Links are typically underlined
        "code": false,
        "color": "blue"
      },
      "plain_text": "our website",
      "href": "https://example.com"
    },
    {
      "type": "text",
      "text": {
        "content": " for more.",
        "link": null
      },
      "annotations": { /* default */ },
      "plain_text": " for more.",
      "href": null
    }
  ]
}
```

### Example 3: Multiple Mentions

**Text:** "Meeting with @John on @2023-03-15 about @Project Database."

```json
{
  "rich_text": [
    {
      "type": "text",
      "text": {
        "content": "Meeting with ",
        "link": null
      },
      "annotations": { /* default */ },
      "plain_text": "Meeting with ",
      "href": null
    },
    {
      "type": "mention",
      "mention": {
        "type": "user",
        "user": {
          "object": "user",
          "id": "user-uuid-here"
        }
      },
      "annotations": { /* default */ },
      "plain_text": "@John",
      "href": null
    },
    {
      "type": "text",
      "text": {
        "content": " on ",
        "link": null
      },
      "annotations": { /* default */ },
      "plain_text": " on ",
      "href": null
    },
    {
      "type": "mention",
      "mention": {
        "type": "date",
        "date": {
          "start": "2023-03-15",
          "end": null,
          "time_zone": null
        }
      },
      "annotations": { /* default */ },
      "plain_text": "2023-03-15",
      "href": null
    },
    {
      "type": "text",
      "text": {
        "content": " about ",
        "link": null
      },
      "annotations": { /* default */ },
      "plain_text": " about ",
      "href": null
    },
    {
      "type": "mention",
      "mention": {
        "type": "database",
        "database": {
          "id": "database-uuid-here"
        }
      },
      "annotations": { /* default */ },
      "plain_text": "Project Database",
      "href": null
    },
    {
      "type": "text",
      "text": {
        "content": ".",
        "link": null
      },
      "annotations": { /* default */ },
      "plain_text": ".",
      "href": null
    }
  ]
}
```

### Example 4: Code and Equation

**Text:** "The formula `E = mc^2` is famous."

```json
{
  "rich_text": [
    {
      "type": "text",
      "text": {
        "content": "The formula ",
        "link": null
      },
      "annotations": { /* default */ },
      "plain_text": "The formula ",
      "href": null
    },
    {
      "type": "equation",
      "equation": {
        "expression": "E = mc^2"
      },
      "annotations": {
        "code": true,
        "bold": false,
        "italic": false,
        "strikethrough": false,
        "underline": false,
        "color": "default"
      },
      "plain_text": "E = mc^2",
      "href": null
    },
    {
      "type": "text",
      "text": {
        "content": " is famous.",
        "link": null
      },
      "annotations": { /* default */ },
      "plain_text": " is famous.",
      "href": null
    }
  ]
}
```

### Example 5: Colored and Styled Text

**Text:** "This has **red**, <u>blue underline</u>, and ~~strikethrough~~."

```json
{
  "rich_text": [
    {
      "type": "text",
      "text": {
        "content": "This has ",
        "link": null
      },
      "annotations": { /* default */ },
      "plain_text": "This has ",
      "href": null
    },
    {
      "type": "text",
      "text": {
        "content": "red",
        "link": null
      },
      "annotations": {
        "bold": true,
        "italic": false,
        "strikethrough": false,
        "underline": false,
        "code": false,
        "color": "red"
      },
      "plain_text": "red",
      "href": null
    },
    {
      "type": "text",
      "text": {
        "content": ", ",
        "link": null
      },
      "annotations": { /* default */ },
      "plain_text": ", ",
      "href": null
    },
    {
      "type": "text",
      "text": {
        "content": "blue underline",
        "link": null
      },
      "annotations": {
        "bold": false,
        "italic": false,
        "strikethrough": false,
        "underline": true,
        "code": false,
        "color": "blue"
      },
      "plain_text": "blue underline",
      "href": null
    },
    {
      "type": "text",
      "text": {
        "content": ", and ",
        "link": null
      },
      "annotations": { /* default */ },
      "plain_text": ", and ",
      "href": null
    },
    {
      "type": "text",
      "text": {
        "content": "strikethrough",
        "link": null
      },
      "annotations": {
        "bold": false,
        "italic": false,
        "strikethrough": true,
        "underline": false,
        "code": false,
        "color": "default"
      },
      "plain_text": "strikethrough",
      "href": null
    },
    {
      "type": "text",
      "text": {
        "content": ".",
        "link": null
      },
      "annotations": { /* default */ },
      "plain_text": ".",
      "href": null
    }
  ]
}
```

---

## SDK Implementation

### Rich Text Classes

```python
from dataclasses import dataclass, field
from typing import Optional, List
from enum import Enum

class RichTextType(str, Enum):
    TEXT = "text"
    MENTION = "mention"
    EQUATION = "equation"

class MentionType(str, Enum):
    USER = "user"
    DATE = "date"
    PAGE = "page"
    DATABASE = "database"
    LINK_PREVIEW = "link_preview"

@dataclass
class Annotations:
    """Text formatting annotations."""
    bold: bool = False
    italic: bool = False
    strikethrough: bool = False
    underline: bool = False
    code: bool = False
    color: str = "default"

@dataclass
class RichTextSegment:
    """Base class for rich text segments."""
    type: RichTextType
    annotations: Annotations = field(default_factory=Annotations)
    plain_text: str = ""
    href: Optional[str] = None

@dataclass
class TextSegment(RichTextSegment):
    """Plain text segment."""
    type: RichTextType = RichTextType.TEXT
    content: str = ""
    link: Optional[dict] = None  # {"url": "..."}

@dataclass
class UserMention(RichTextSegment):
    """User mention segment."""
    type: RichTextType = RichTextType.MENTION
    mention_type: MentionType = MentionType.USER
    user_id: str = ""

@dataclass
class DateMention(RichTextSegment):
    """Date mention segment."""
    type: RichTextType = RichTextType.MENTION
    mention_type: MentionType = MentionType.DATE
    start: str = ""  # ISO 8601 date
    end: Optional[str] = None

@dataclass
class PageMention(RichTextSegment):
    """Page mention segment."""
    type: RichTextType = RichTextType.MENTION
    mention_type: MentionType = MentionType.PAGE
    page_id: str = ""

@dataclass
class DatabaseMention(RichTextSegment):
    """Database mention segment."""
    type: RichTextType = RichTextType.MENTION
    mention_type: MentionType = MentionType.DATABASE
    database_id: str = ""

@dataclass
class EquationSegment(RichTextSegment):
    """Equation segment."""
    type: RichTextType = RichTextType.EQUATION
    expression: str = ""
```

### Rich Text Builder

```python
class RichTextBuilder:
    """Helper class to build rich text arrays."""

    def __init__(self):
        self.segments: List[RichTextSegment] = []

    def text(self,
             content: str,
             bold: bool = False,
             italic: bool = False,
             strikethrough: bool = False,
             underline: bool = False,
             code: bool = False,
             color: str = "default",
             link: Optional[str] = None) -> "RichTextBuilder":
        """Add a text segment."""
        annotations = Annotations(
            bold=bold,
            italic=italic,
            strikethrough=strikethrough,
            underline=underline,
            code=code,
            color=color
        )

        link_obj = {"url": link} if link else None

        segment = TextSegment(
            content=content,
            annotations=annotations,
            plain_text=content,
            href=link,
            link=link_obj
        )

        self.segments.append(segment)
        return self

    def mention_user(self, user_id: str) -> "RichTextBuilder":
        """Add a user mention."""
        segment = UserMention(
            user_id=user_id,
            plain_text=f"@{user_id}"
        )
        self.segments.append(segment)
        return self

    def mention_date(self, date: str) -> "RichTextBuilder":
        """Add a date mention."""
        segment = DateMention(
            start=date,
            plain_text=date
        )
        self.segments.append(segment)
        return self

    def mention_page(self, page_id: str, title: str = "") -> "RichTextBuilder":
        """Add a page mention."""
        segment = PageMention(
            page_id=page_id,
            plain_text=title or f"@{page_id}"
        )
        self.segments.append(segment)
        return self

    def equation(self, expression: str) -> "RichTextBuilder":
        """Add an equation."""
        segment = EquationSegment(
            expression=expression,
            plain_text=expression
        )
        self.segments.append(segment)
        return self

    def build(self) -> List[dict]:
        """Build the rich text array for API requests."""
        return [segment.to_dict() for segment in self.segments]

    @classmethod
    def from_string(cls, text: str) -> List[dict]:
        """Create a simple rich text array from a plain string."""
        return cls().text(text).build()
```

### Usage Examples

```python
# Simple text
rich_text = RichTextBuilder.from_string("Hello, World!")

# Formatted text
rich_text = (RichTextBuilder()
    .text("This is ")
    .text("bold", bold=True)
    .text(" and ")
    .text("italic", italic=True)
    .text(" text.")
    .build())

# With mentions
rich_text = (RichTextBuilder()
    .text("Meeting with ")
    .mention_user("user-uuid")
    .text(" on ")
    .mention_date("2023-03-15")
    .build())

# With equations
rich_text = (RichTextBuilder()
    .text("The formula ")
    .equation("E = mc^2")
    .text(" is famous.")
    .build())

# With links
rich_text = (RichTextBuilder()
    .text("Visit ")
    .text("our website", link="https://example.com", color="blue", underline=True)
    .text(" for more.")
    .build())
```

### Parsing Rich Text

```python
class RichTextParser:
    """Parse rich text from API responses."""

    @staticmethod
    def from_dict(data: dict) -> RichTextSegment:
        """Parse a single rich text segment."""
        segment_type = data.get("type")
        annotations = Annotations(**data.get("annotations", {}))

        if segment_type == RichTextType.TEXT:
            text_data = data.get("text", {})
            return TextSegment(
                content=text_data.get("content", ""),
                link=text_data.get("link"),
                annotations=annotations,
                plain_text=data.get("plain_text", ""),
                href=data.get("href")
            )

        elif segment_type == RichTextType.MENTION:
            mention_data = data.get("mention", {})
            mention_type = mention_data.get("type")

            if mention_type == MentionType.USER:
                return UserMention(
                    user_id=mention_data.get("user", {}).get("id", ""),
                    annotations=annotations,
                    plain_text=data.get("plain_text", ""),
                    href=data.get("href")
                )
            # ... other mention types

        elif segment_type == RichTextType.EQUATION:
            equation_data = data.get("equation", {})
            return EquationSegment(
                expression=equation_data.get("expression", ""),
                annotations=annotations,
                plain_text=data.get("plain_text", ""),
                href=data.get("href")
            )

        raise ValueError(f"Unknown segment type: {segment_type}")

    @staticmethod
    def parse_array(data: List[dict]) -> List[RichTextSegment]:
        """Parse an array of rich text segments."""
        return [RichTextParser.from_dict(segment) for segment in data]
```

---

## Best Practices

### 1. Minimize Segments

**Good:** Fewer segments when possible
```python
# One segment with all formatting
builder.text("Bold and italic", bold=True, italic=True)
```

**Avoid:** Unnecessary splitting
```python
# Multiple segments for same formatting
builder.text("Bold ", bold=True).text("and ", bold=True).text("italic", bold=True, italic=True)
```

### 2. Use `plain_text` for Display

The `plain_text` field provides unformatted text for quick display without parsing formatting.

```python
def get_plain_text(rich_text: List[dict]) -> str:
    """Extract plain text from rich text array."""
    return "".join(segment.get("plain_text", "") for segment in rich_text)
```

### 3. Handle Empty Rich Text

Empty or null rich text arrays are common:

```python
def is_empty(rich_text: Optional[List[dict]]) -> bool:
    """Check if rich text is empty."""
    if not rich_text:
        return True
    return all(not seg.get("plain_text") for seg in rich_text)
```

### 4. Validate Mentions

Ensure mentioned resources exist and are accessible:

```python
async def validate_mention(client: NotionClient, mention: dict) -> bool:
    """Validate that a mention references an accessible resource."""
    mention_type = mention.get("type")

    if mention_type == "user":
        user_id = mention.get("user", {}).get("id")
        try:
            await client.users.get(user_id)
            return True
        except NotFoundError:
            return False

    # ... other types
```

---

## Implementation Checklist

- [ ] `RichTextSegment` base class
- [ ] `TextSegment`, `UserMention`, `DateMention`, `PageMention`, `DatabaseMention`, `EquationSegment` classes
- [ ] `Annotations` dataclass
- [ ] `RichTextBuilder` for constructing rich text
- [ ] `RichTextParser` for parsing API responses
- [ ] Color enum for text/background colors
- [ ] Helper methods for common operations
- [ ] Validation for mention references
- [ ] Plain text extraction utilities
- [ ] Unit tests for all segment types

---

**Related Documentation:**
- [Blocks Overview](./blocks-overview.md) - How rich text fits into blocks
- [Block Types](./block-types.md) - Which blocks use rich text
- [Text Blocks](./text-blocks.md) - Text block implementations
