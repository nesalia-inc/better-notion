# Block Types Reference

Complete reference of all block types in the Notion API and their type-specific properties.

## Block Type Enumeration

```python
class BlockType(str, Enum):
    """All supported Notion block types."""

    # Text blocks
    PARAGRAPH = "paragraph"
    HEADING_1 = "heading_1"
    HEADING_2 = "heading_2"
    HEADING_3 = "heading_3"
    BULLETED_LIST_ITEM = "bulleted_list_item"
    NUMBERED_LIST_ITEM = "numbered_list_item"
    TO_DO = "to_do"
    TOGGLE = "toggle"
    QUOTE = "quote"
    CALLOUT = "callout"

    # Media blocks
    IMAGE = "image"
    VIDEO = "video"
    AUDIO = "audio"
    FILE = "file"
    PDF = "pdf"

    # Embed blocks
    BOOKMARK = "bookmark"
    EMBED = "embed"
    LINK_PREVIEW = "link_preview"

    # Structure blocks
    DIVIDER = "divider"
    COLUMN_LIST = "column_list"
    COLUMN = "column"
    TABLE = "table"
    TABLE_ROW = "table_row"
    TABLE_OF_CONTENTS = "table_of_contents"
    SYNCED_BLOCK = "synced_block"
    TEMPLATE = "template"

    # Database blocks
    CHILD_DATABASE = "child_database"
    CHILD_PAGE = "child_page"

    # Special blocks
    BREADCRUMB = "breadcrumb"
    CODE = "code"
    EQUATION = "equation"

    # Unsupported
    UNSUPPORTED = "unsupported"
```

## Quick Reference Table

| Block Type | Has Rich Text | Has Children | Color Supported | Create via API | Notes |
|------------|--------------|--------------|-----------------|----------------|-------|
| Paragraph | ✅ | ✅ | ✅ | ✅ | Most common block |
| Heading 1 | ✅ | Toggle only | ✅ | ✅ | `is_toggleable` enables children |
| Heading 2 | ✅ | Toggle only | ✅ | ✅ | `is_toggleable` enables children |
| Heading 3 | ✅ | Toggle only | ✅ | ✅ | `is_toggleable` enables children |
| Bulleted List | ✅ | ✅ | ✅ | ✅ | Nested lists supported |
| Numbered List | ✅ | ✅ | ✅ | ✅ | Nested lists supported |
| To Do | ✅ | ✅ | ✅ | ✅ | Checkbox `checked` property |
| Toggle | ✅ | ✅ | ✅ | ✅ | Collapsible content |
| Quote | ✅ | ✅ | ✅ | ✅ | Blockquotes |
| Callout | ✅ | ✅ | ✅ | ✅ | Emoji icon support |
| Image | ❌ | ❌ | ❌ | ✅ | External or hosted |
| Video | ❌ | ❌ | ❌ | ✅ | YouTube, Vimeo, external |
| Audio | ❌ | ❌ | ❌ | ✅ | MP3, WAV, etc. |
| File | ❌ | ❌ | ❌ | ✅ | Any file type |
| PDF | ❌ | ❌ | ❌ | ✅ | PDF documents |
| Bookmark | ❌ | ❌ | ❌ | ✅ | URL + caption |
| Embed | ❌ | ❌ | ❌ | ✅ | URL embed |
| Link Preview | ❌ | ❌ | ❌ | ❌ | Read-only, returned by API |
| Divider | ❌ | ❌ | ❌ | ✅ | Horizontal line |
| Column List | ❌ | ✅ | ❌ | ✅ | Parent for columns |
| Column | ❌ | ✅ | ❌ | ✅ | Width ratio customizable |
| Table | ❌ | ✅ | ❌ | ✅ | Fixed width after creation |
| Table Row | ❌ | ❌ | ❌ | ✅ | Array of cells |
| Table of Contents | ❌ | ❌ | ✅ | ✅ | Auto-generated |
| Synced Block | ❌ | ✅ | ❌ | ⚠️ | Cannot update content |
| Template | ✅ | ✅ | ❌ | ❌ | Deprecated for creation |
| Child Database | ❌ | ❌ | ❌ | ⚠️ | Use database endpoints |
| Child Page | ❌ | ❌ | ❌ | ⚠️ | Use page endpoints |
| Breadcrumb | ❌ | ❌ | ❌ | ❌ | Read-only |
| Code | ✅ | ❌ | ❌ | ✅ | Syntax highlighting |
| Equation | ❌ | ❌ | ❌ | ✅ | KaTeX expressions |
| Unsupported | ❌ | ❌ | ❌ | ❌ | Unknown block types |

## Detailed Block Type Reference

### 1. Paragraph

**Type:** `paragraph`

**Properties:**
```json
{
  "rich_text": [/* Rich text array */],
  "color": "default",
  "children": [/* Nested blocks */]
}
```

**Features:**
- Rich text with formatting
- Customizable color
- Supports nested blocks
- Most common block type

**SDK Class:**
```python
class Paragraph(TextBlock):
    type: BlockType = BlockType.PARAGRAPH
    content: RichText
    color: str = "default"
    children: List[Block] = field(default_factory=list)
```

---

### 2. Heading 1 / 2 / 3

**Types:** `heading_1`, `heading_2`, `heading_3`

**Properties:**
```json
{
  "rich_text": [/* Rich text array */],
  "color": "default",
  "is_toggleable": false
}
```

**Features:**
- Rich text with formatting
- Customizable color
- Toggleable when `is_toggleable: true` (supports children)
- Three heading levels

**SDK Classes:**
```python
class Heading1(TextBlock):
    type: BlockType = BlockType.HEADING_1
    level: int = 1
    is_toggleable: bool = False

class Heading2(TextBlock):
    type: BlockType = BlockType.HEADING_2
    level: int = 2
    is_toggleable: bool = False

class Heading3(TextBlock):
    type: BlockType = BlockType.HEADING_3
    level: int = 3
    is_toggleable: bool = False
```

---

### 3. Bulleted List Item

**Type:** `bulleted_list_item`

**Properties:**
```json
{
  "rich_text": [/* Rich text array */],
  "color": "default",
  "children": [/* Nested blocks */]
}
```

**Features:**
- Rich text with formatting
- Customizable color
- Supports nested blocks (for sub-items)
- Auto-numbered at parent level

**SDK Class:**
```python
class BulletedListItem(TextBlock):
    type: BlockType = BlockType.BULLETED_LIST_ITEM
    content: RichText
    color: str = "default"
    children: List[Block] = field(default_factory=list)
```

---

### 4. Numbered List Item

**Type:** `numbered_list_item`

**Properties:**
```json
{
  "rich_text": [/* Rich text array */],
  "color": "default",
  "children": [/* Nested blocks */]
}
```

**Features:**
- Rich text with formatting
- Customizable color
- Supports nested blocks
- Auto-numbered sequentially

**SDK Class:**
```python
class NumberedListItem(TextBlock):
    type: BlockType = BlockType.NUMBERED_LIST_ITEM
    content: RichText
    color: str = "default"
    children: List[Block] = field(default_factory=list)
```

---

### 5. To Do

**Type:** `to_do`

**Properties:**
```json
{
  "rich_text": [/* Rich text array */],
  "checked": false,
  "color": "default",
  "children": [/* Nested blocks */]
}
```

**Features:**
- Rich text with formatting
- Checkbox state (`checked` boolean)
- Customizable color
- Supports nested blocks

**SDK Class:**
```python
class ToDo(TextBlock):
    type: BlockType = BlockType.TO_DO
    content: RichText
    checked: bool = False
    color: str = "default"
    children: List[Block] = field(default_factory=list)
```

---

### 6. Toggle

**Type:** `toggle`

**Properties:**
```json
{
  "rich_text": [/* Rich text array */],
  "color": "default",
  "children": [/* Hidden content blocks */]
}
```

**Features:**
- Rich text with formatting (the toggle header)
- Customizable color
- Supports nested blocks (the hidden content)
- Collapsible in UI

**SDK Class:**
```python
class Toggle(TextBlock):
    type: BlockType = BlockType.TOGGLE
    content: RichText
    color: str = "default"
    children: List[Block] = field(default_factory=list)
```

---

### 7. Quote

**Type:** `quote`

**Properties:**
```json
{
  "rich_text": [/* Rich text array */],
  "color": "default",
  "children": [/* Nested blocks */]
}
```

**Features:**
- Rich text with formatting
- Customizable color
- Supports nested blocks
- Styled as blockquote in UI

**SDK Class:**
```python
class Quote(TextBlock):
    type: BlockType = BlockType.QUOTE
    content: RichText
    color: str = "default"
    children: List[Block] = field(default_factory=list)
```

---

### 8. Callout

**Type:** `callout`

**Properties:**
```json
{
  "rich_text": [/* Rich text array */],
  "icon": {
    "emoji": "⭐",
    // OR
    "type": "external",
    "external": { "url": "..." }
  },
  "color": "default"
}
```

**Features:**
- Rich text with formatting
- Emoji or file icon
- Customizable background color
- Highlighted box in UI

**SDK Class:**
```python
class Callout(TextBlock):
    type: BlockType = BlockType.CALLOUT
    content: RichText
    icon: Optional[Icon] = None
    color: str = "default"

    class Icon:
        emoji: Optional[str] = None
        external: Optional[dict] = None  # File URL
```

---

### 9. Image

**Type:** `image`

**Properties:**
```json
{
  "type": "external",  // or "file", "file_upload"
  "external": {
    "url": "https://..."
  }
  // OR
  "file": {
    "url": "https://...",
    "expiry_time": "2023-01-01T00:00:00.000Z"
  }
}
```

**Features:**
- External URLs (hosted images)
- Notion-hosted files (with expiry)
- File uploads (via File Upload API)
- Supported formats: BMP, GIF, HEIC, JPEG, JPG, PNG, SVG, TIF, TIFF

**SDK Class:**
```python
class Image(Block):
    type: BlockType = BlockType.IMAGE
    image_type: str  # "external", "file", "file_upload"
    url: str
    expiry_time: Optional[datetime] = None
    caption: RichText = field(default_factory=RichText)
```

---

### 10. Video

**Type:** `video`

**Properties:**
```json
{
  "type": "external",
  "external": {
    "url": "https://..."
  }
}
```

**Features:**
- External URLs
- Notion-hosted files
- File uploads
- YouTube embed support
- Supported formats: AMV, ASF, AVI, F4V, FLV, GIFV, MKV, MOV, MP4, etc.
- Note: Use `embed` block for Vimeo

**SDK Class:**
```python
class Video(Block):
    type: BlockType = BlockType.VIDEO
    video_type: str
    url: str
    expiry_time: Optional[datetime] = None
    caption: RichText = field(default_factory=RichText)
```

---

### 11. Audio

**Type:** `audio`

**Properties:**
```json
{
  "type": "external",
  "external": {
    "url": "https://..."
  }
}
```

**Features:**
- External URLs
- Notion-hosted files
- File uploads
- Supported formats: M4A, MP3, OGA, OGG, WAV

**SDK Class:**
```python
class Audio(Block):
    type: BlockType = BlockType.AUDIO
    audio_type: str
    url: str
    expiry_time: Optional[datetime] = None
    caption: RichText = field(default_factory=RichText)
```

---

### 12. File

**Type:** `file`

**Properties:**
```json
{
  "caption": [/* Rich text array */],
  "type": "external",  // or "file", "file_upload"
  "name": "document.pdf",
  "external": {
    "url": "https://..."
  }
}
```

**Features:**
- Any file type
- Caption support
- External URLs or Notion-hosted
- File uploads

**SDK Class:**
```python
class File(Block):
    type: BlockType = BlockType.FILE
    file_type: str
    url: str
    name: Optional[str] = None
    expiry_time: Optional[datetime] = None
    caption: RichText = field(default_factory=RichText)
```

---

### 13. PDF

**Type:** `pdf`

**Properties:**
```json
{
  "caption": [/* Rich text array */],
  "type": "external",
  "external": {
    "url": "https://..."
  }
}
```

**Features:**
- PDF documents only
- Caption support
- External URLs or Notion-hosted
- File uploads

**SDK Class:**
```python
class PDF(Block):
    type: BlockType = BlockType.PDF
    pdf_type: str
    url: str
    expiry_time: Optional[datetime] = None
    caption: RichText = field(default_factory=RichText)
```

---

### 14. Bookmark

**Type:** `bookmark`

**Properties:**
```json
{
  "caption": [/* Rich text array */],
  "url": "https://..."
}
```

**Features:**
- URL bookmark
- Optional caption (rich text)
- Auto-fetched metadata (in UI)

**SDK Class:**
```python
class Bookmark(Block):
    type: BlockType = BlockType.BOOKMARK
    url: str
    caption: RichText = field(default_factory=RichText)
```

---

### 15. Embed

**Type:** `embed`

**Properties:**
```json
{
  "url": "https://..."
}
```

**Features:**
- Embed external content
- Note: API doesn't use iFramely (unlike UI)
- Vimeo links via embed block
- YouTube links via video block

**SDK Class:**
```python
class Embed(Block):
    type: BlockType = BlockType.EMBED
    url: str
```

---

### 16. Link Preview

**Type:** `link_preview`

**Properties:**
```json
{
  "url": "https://..."
}
```

**Features:**
- Read-only (returned by API only)
- Cannot create via API
- Auto-generated from pasted URLs

**SDK Class:**
```python
class LinkPreview(Block):
    type: BlockType = BlockType.LINK_PREVIEW
    url: str
    read_only: bool = True
```

---

### 17. Divider

**Type:** `divider`

**Properties:**
```json
{}
```

**Features:**
- Horizontal line
- No additional properties
- Visual separator

**SDK Class:**
```python
class Divider(Block):
    type: BlockType = BlockType.DIVIDER
```

---

### 18. Column List

**Type:** `column_list`

**Properties:**
```json
{}
```

**Features:**
- Parent block for columns
- No additional properties
- Must have at least 2 columns

**SDK Class:**
```python
class ColumnList(Block):
    type: BlockType = BlockType.COLUMN_LIST
    children: List[Column]  # Only Column blocks allowed
```

---

### 19. Column

**Type:** `column`

**Properties:**
```json
{
  "width_ratio": 0.5
}
```

**Features:**
- Child of column_list
- Customizable width ratio (0-1)
- Can contain any block type except columns
- Width ratios in same list should sum to 1

**SDK Class:**
```python
class Column(Block):
    type: BlockType = BlockType.COLUMN
    width_ratio: float = 0.5
    children: List[Block] = field(default_factory=list)
```

---

### 20. Table

**Type:** `table`

**Properties:**
```json
{
  "table_width": 3,
  "has_column_header": false,
  "has_row_header": false
}
```

**Features:**
- Fixed width after creation
- Optional column header
- Optional row header
- Parent block for table rows
- Must have at least 1 row on creation

**SDK Class:**
```python
class Table(Block):
    type: BlockType = BlockType.TABLE
    table_width: int
    has_column_header: bool = False
    has_row_header: bool = False
    children: List[TableRow]  # Only TableRow blocks allowed
```

---

### 21. Table Row

**Type:** `table_row`

**Properties:**
```json
{
  "cells": [
    [/* Rich text for cell 1 */],
    [/* Rich text for cell 2 */],
    [/* Rich text for cell 3 */]
  ]
}
```

**Features:**
- Array of cells (horizontal order)
- Each cell is a rich text array
- Length must match table width
- Child of table blocks

**SDK Class:**
```python
class TableRow(Block):
    type: BlockType = BlockType.TABLE_ROW
    cells: List[RichText]
```

---

### 22. Table of Contents

**Type:** `table_of_contents`

**Properties:**
```json
{
  "color": "default"
}
```

**Features:**
- Auto-generated from headings
- Customizable color
- No manual content control

**SDK Class:**
```python
class TableOfContents(Block):
    type: BlockType = BlockType.TABLE_OF_CONTENTS
    color: str = "default"
```

---

### 23. Synced Block

**Type:** `synced_block`

**Properties:**

**Original:**
```json
{
  "synced_from": null,
  "children": [/* Shared blocks */]
}
```

**Duplicate:**
```json
{
  "synced_from": {
    "type": "block_id",
    "block_id": "original-block-id"
  }
}
```

**Features:**
- Original block has `synced_from: null`
- Duplicate blocks reference original
- Content cannot be updated via API
- Changes sync between all copies

**SDK Class:**
```python
class SyncedBlock(Block):
    type: BlockType = BlockType.SYNCED_BLOCK
    synced_from: Optional[str] = None  # Block ID or None
    children: List[Block] = field(default_factory=list)
    read_only_content: bool = synced_from is not None
```

---

### 24. Template

**Type:** `template`

**Properties:**
```json
{
  "rich_text": [/* Rich text array */],
  "children": [/* Template blocks */]
}
```

**Features:**
- ⚠️ **Deprecated for creation** (as of March 27, 2023)
- Can still be retrieved
- Represents template buttons in UI
- Rich text title + nested blocks

**SDK Class:**
```python
class Template(TextBlock):
    type: BlockType = BlockType.TEMPLATE
    content: RichText
    children: List[Block] = field(default_factory=list)
    deprecated_for_creation: bool = True
```

---

### 25. Child Database

**Type:** `child_database`

**Properties:**
```json
{
  "title": "Database Name"
}
```

**Features:**
- ⚠️ Use database endpoints to create/update
- Inline database on a page
- Title is plain text

**SDK Class:**
```python
class ChildDatabase(Block):
    type: BlockType = BlockType.CHILD_DATABASE
    title: str
    # Use database.client.databases.create() to create
```

---

### 26. Child Page

**Type:** `child_page`

**Properties:**
```json
{
  "title": "Page Title"
}
```

**Features:**
- ⚠️ Use page endpoints to create/update
- Nested page within another page
- Title is plain text

**SDK Class:**
```python
class ChildPage(Block):
    type: BlockType = BlockType.CHILD_PAGE
    title: str
    # Use client.pages.create() to create
```

---

### 27. Breadcrumb

**Type:** `breadcrumb`

**Properties:**
```json
{}
```

**Features:**
- Read-only (returned by API only)
- Cannot create via API
- Auto-generated navigation

**SDK Class:**
```python
class Breadcrumb(Block):
    type: BlockType = BlockType.BREADCRUMB
    read_only: bool = True
```

---

### 28. Code

**Type:** `code`

**Properties:**
```json
{
  "rich_text": [/* Rich text array */],
  "language": "python",
  "caption": [/* Rich text array */]
}
```

**Features:**
- Rich text code content
- Syntax highlighting (70+ languages)
- Optional caption
- Monospace font in UI

**Supported Languages:** `abap`, `arduino`, `bash`, `basic`, `c`, `clojure`, `coffeescript`, `c++`, `c#`, `css`, `dart`, `diff`, `docker`, `elixir`, `elm`, `erlang`, `flow`, `fortran`, `f#`, `gherkin`, `glsl`, `go`, `graphql`, `groovy`, `haskell`, `html`, `java`, `javascript`, `json`, `julia`, `kotlin`, `latex`, `less`, `lisp`, `livescript`, `lua`, `makefile`, `markdown`, `markup`, `matlab`, `mermaid`, `nix`, `objective-c`, `ocaml`, `pascal`, `perl`, `php`, `plain text`, `powershell`, `prolog`, `protobuf`, `python`, `r`, `reason`, `ruby`, `rust`, `sass`, `scala`, `scheme`, `scss`, `shell`, `sql`, `swift`, `typescript`, `vb.net`, `verilog`, `vhdl`, `visual basic`, `webassembly`, `xml`, `yaml`, `java/c/c++/c#`

**SDK Class:**
```python
class Code(TextBlock):
    type: BlockType = BlockType.CODE
    content: RichText
    language: str = "plain text"
    caption: RichText = field(default_factory=RichText)
```

---

### 29. Equation

**Type:** `equation`

**Properties:**
```json
{
  "expression": "e=mc^2"
}
```

**Features:**
- KaTeX-compatible expressions
- Mathematical notation
- Nested within rich text in paragraphs

**SDK Class:**
```python
class Equation(Block):
    type: BlockType = BlockType.EQUATION
    expression: str  # KaTeX syntax
```

---

### 30. Unsupported

**Type:** `unsupported`

**Properties:**
```json
{}
```

**Features:**
- Placeholder for unknown block types
- Can be moved but not created/modified
- Indicates unsupported Notion feature

**SDK Class:**
```python
class Unsupported(Block):
    type: BlockType = BlockType.UNSUPPORTED
    read_only: bool = True
```

---

## Implementation Notes

### Type-Specific Property Mapping

Each block type has a corresponding property key in the API response:

```python
BLOCK_TYPE_MAPPING = {
    BlockType.PARAGRAPH: "paragraph",
    BlockType.HEADING_1: "heading_1",
    BlockType.HEADING_2: "heading_2",
    BlockType.HEADING_3: "heading_3",
    # ... etc
}

def get_block_data(block_dict: dict) -> dict:
    """Extract type-specific data from block dict."""
    block_type = block_dict["type"]
    type_key = BLOCK_TYPE_MAPPING[block_type]
    return block_dict[type_key]
```

### Color Enum

```python
class BlockColor(str, Enum):
    """Supported block colors."""

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

**Related Documentation:**
- [Blocks Overview](./blocks-overview.md) - General block concepts
- [Text Blocks](./text-blocks.md) - Detailed text block implementations
- [Media Blocks](./media-blocks.md) - Media block implementations
- [Rich Text Reference](./rich-text.md) - Rich text formatting system
