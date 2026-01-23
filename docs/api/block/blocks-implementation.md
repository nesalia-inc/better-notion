# Blocks Implementation Guide

Technical implementation guide for building the Block system in Better Notion SDK.

## Architecture Overview

### Class Hierarchy

```
Block (base class)
├── TextBlock (base for text-containing blocks)
│   ├── Paragraph
│   ├── Heading (with level 1/2/3)
│   ├── BulletedListItem
│   ├── NumberedListItem
│   ├── ToDo
│   ├── Toggle
│   ├── Quote
│   ├── Callout
│   └── Code
├── MediaBlock (base for media blocks)
│   ├── Image
│   ├── Video
│   ├── Audio
│   ├── File
│   └── PDF
├── EmbedBlock (base for embeds)
│   ├── Bookmark
│   ├── Embed
│   └── LinkPreview
├── StructureBlock (base for structural blocks)
│   ├── ColumnList
│   ├── Column
│   ├── Table
│   ├── TableRow
│   ├── TableOfContents
│   ├── SyncedBlock
│   └── Template
└── SpecialBlock
    ├── ChildDatabase
    ├── ChildPage
    ├── Breadcrumb
    ├── Equation
    └── Divider
```

## Base Implementation

### Block Base Class

```python
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Any, List
from uuid import UUID
from enum import Enum

class BlockType(str, Enum):
    """All Notion block types."""
    PARAGRAPH = "paragraph"
    HEADING_1 = "heading_1"
    HEADING_2 = "heading_2"
    HEADING_3 = "heading_3"
    # ... all other types

@dataclass
class Parent:
    """Block parent information."""
    type: str  # "page_id", "block_id", "workspace"
    page_id: Optional[UUID] = None
    block_id: Optional[UUID] = None
    workspace: bool = False

    @classmethod
    def from_dict(cls, data: dict) -> "Parent":
        """Parse parent from API response."""
        parent_type = data.get("type")

        if parent_type == "page_id":
            return cls(type=parent_type, page_id=data.get("page_id"))
        elif parent_type == "block_id":
            return cls(type=parent_type, block_id=data.get("block_id"))
        elif parent_type == "workspace":
            return cls(type=parent_type, workspace=True)

        raise ValueError(f"Unknown parent type: {parent_type}")

    def to_dict(self) -> dict:
        """Convert to API-compatible dict."""
        if self.type == "page_id":
            return {"type": self.type, "page_id": str(self.page_id)}
        elif self.type == "block_id":
            return {"type": self.type, "block_id": str(self.block_id)}
        elif self.type == "workspace":
            return {"type": self.type, "workspace": True}

@dataclass
class PartialUser:
    """Partial user object (created_by, last_edited_by)."""
    object: str = "user"
    id: UUID = None

    @classmethod
    def from_dict(cls, data: dict) -> "PartialUser":
        return cls(
            object=data.get("object"),
            id=UUID(data.get("id"))
        )

@dataclass
class Block:
    """Base Notion block."""
    object: str = "block"
    id: UUID = None
    parent: Optional[Parent] = None
    created_time: Optional[datetime] = None
    last_edited_time: Optional[datetime] = None
    created_by: Optional[PartialUser] = None
    last_edited_by: Optional[PartialUser] = None
    has_children: bool = False
    archived: bool = False
    in_trash: bool = False
    type: BlockType = None

    # Type-specific data (set by subclasses)
    _type_data: dict = field(default_factory=dict, init=False, repr=False)

    # Reference to client for lazy loading
    _client: Any = field(default=None, init=False, repr=False)

    @classmethod
    def from_dict(cls, data: dict, client: Any = None) -> "Block":
        """Parse block from API response."""
        block_type = BlockType(data.get("type"))

        # Create appropriate subclass instance
        block_class = BLOCK_CLASS_MAP.get(block_type, Block)
        instance = block_class.__new__(block_class)

        # Set common fields
        instance.object = data.get("object")
        instance.id = UUID(data.get("id"))
        instance.parent = Parent.from_dict(data.get("parent", {}))
        instance.created_time = datetime.fromisoformat(data.get("created_time").replace("Z", "+00:00"))
        instance.last_edited_time = datetime.fromisoformat(data.get("last_edited_time").replace("Z", "+00:00"))
        instance.created_by = PartialUser.from_dict(data.get("created_by", {}))
        instance.last_edited_by = PartialUser.from_dict(data.get("last_edited_by", {}))
        instance.has_children = data.get("has_children", False)
        instance.archived = data.get("archived", False)
        instance.in_trash = data.get("in_trash", False)
        instance.type = block_type
        instance._client = client

        # Parse type-specific data
        type_key = BLOCK_TYPE_KEYS.get(block_type, block_type.value)
        instance._type_data = data.get(type_key, {})

        # Let subclass parse its specific data
        if hasattr(instance, "_parse_type_data"):
            instance._parse_type_data(instance._type_data)

        return instance

    def to_dict(self) -> dict:
        """Convert block to API-compatible dict."""
        data = {
            "object": self.object,
            "type": self.type.value,
        }

        # Add type-specific data
        if hasattr(self, "_get_type_data"):
            type_data = self._get_type_data()
            type_key = BLOCK_TYPE_KEYS.get(self.type, self.type.value)
            data[type_key] = type_data

        return data

    async def get_children(self, **kwargs) -> List["Block"]:
        """Get child blocks (if supported)."""
        if not self.has_children:
            return []

        if not self._client:
            raise RuntimeError("Block has no client reference")

        response = await self._client.blocks.children.list(
            block_id=str(self.id),
            **kwargs
        )

        return [
            Block.from_dict(block_data, self._client)
            for block_data in response.get("results", [])
        ]

    async def delete(self) -> None:
        """Delete this block."""
        if not self._client:
            raise RuntimeError("Block has no client reference")

        await self._client.blocks.delete(str(self.id))

    async def update(self, **changes) -> "Block":
        """Update block properties."""
        if not self._client:
            raise RuntimeError("Block has no client reference")

        # Apply changes to this instance
        for key, value in changes.items():
            setattr(self, key, value)

        # Send update to API
        response = await self._client.blocks.update(
            block_id=str(self.id),
            **self._get_update_data()
        )

        return Block.from_dict(response, self._client)

    def _get_update_data(self) -> dict:
        """Get data for update request. Override in subclasses."""
        return self._get_type_data()
```

### Block Class Mapping

```python
# Mapping of block types to their classes
BLOCK_CLASS_MAP = {
    BlockType.PARAGRAPH: Paragraph,
    BlockType.HEADING_1: lambda data, client: Heading.from_dict(data, client, level=1),
    BlockType.HEADING_2: lambda data, client: Heading.from_dict(data, client, level=2),
    BlockType.HEADING_3: lambda data, client: Heading.from_dict(data, client, level=3),
    # ... etc
}

# Mapping of block types to their type keys in API responses
BLOCK_TYPE_KEYS = {
    BlockType.PARAGRAPH: "paragraph",
    BlockType.HEADING_1: "heading_1",
    BlockType.HEADING_2: "heading_2",
    BlockType.HEADING_3: "heading_3",
    # ... etc
}
```

## Text Block Implementation

### TextBlock Base Class

```python
@dataclass
class TextBlock(Block):
    """Base class for blocks containing rich text."""
    content: List[RichTextSegment] = field(default_factory=list)
    color: str = "default"

    def _parse_type_data(self, data: dict):
        """Parse type-specific data."""
        self.content = RichTextParser.parse_array(data.get("rich_text", []))
        self.color = data.get("color", "default")

    def _get_type_data(self) -> dict:
        """Get type-specific data for API requests."""
        return {
            "rich_text": [segment.to_dict() for segment in self.content],
            "color": self.color
        }

    @property
    def plain_text(self) -> str:
        """Get plain text representation."""
        return "".join(seg.plain_text for seg in self.content)

    def set_text(self, text: str, **formatting) -> None:
        """Set text content with optional formatting."""
        self.content = [TextSegment(
            content=text,
            annotations=Annotations(**formatting),
            plain_text=text
        )]
```

### Paragraph

```python
@dataclass
class Paragraph(TextBlock):
    """Paragraph block."""
    type: BlockType = BlockType.PARAGRAPH
    children: List[Block] = field(default_factory=list)

    def _parse_type_data(self, data: dict):
        """Parse type-specific data."""
        super()._parse_type_data(data)
        # Children loaded separately via get_children()
```

### Heading

```python
@dataclass
class Heading(TextBlock):
    """Heading block (H1, H2, H3)."""
    type: BlockType = None  # Set based on level
    level: int = 1
    is_toggleable: bool = False

    def __post_init__(self):
        """Set type based on level."""
        if self.level == 1:
            self.type = BlockType.HEADING_1
        elif self.level == 2:
            self.type = BlockType.HEADING_2
        elif self.level == 3:
            self.type = BlockType.HEADING_3
        else:
            raise ValueError(f"Invalid heading level: {self.level}")

    @classmethod
    def from_dict(cls, data: dict, client: Any = None, level: int = 1) -> "Heading":
        """Parse heading from API response."""
        instance = super().from_dict(data, client)
        instance.level = level
        instance.is_toggleable = data.get(f"heading_{level}", {}).get("is_toggleable", False)
        return instance

    def _parse_type_data(self, data: dict):
        """Parse type-specific data."""
        super()._parse_type_data(data)
        self.is_toggleable = data.get("is_toggleable", False)

    def _get_type_data(self) -> dict:
        """Get type-specific data."""
        base_data = super()._get_type_data()
        base_data["is_toggleable"] = self.is_toggleable
        return base_data
```

### ToDo

```python
@dataclass
class ToDo(TextBlock):
    """To-do block with checkbox."""
    type: BlockType = BlockType.TO_DO
    checked: bool = False
    children: List[Block] = field(default_factory=list)

    def _parse_type_data(self, data: dict):
        """Parse type-specific data."""
        super()._parse_type_data(data)
        self.checked = data.get("checked", False)

    def _get_type_data(self) -> dict:
        """Get type-specific data."""
        base_data = super()._get_type_data()
        base_data["checked"] = self.checked
        return base_data

    async def toggle(self) -> bool:
        """Toggle the checkbox."""
        self.checked = not self.checked
        await self.update()
        return self.checked
```

### Code Block

```python
@dataclass
class Code(TextBlock):
    """Code block with syntax highlighting."""
    type: BlockType = BlockType.CODE
    language: str = "plain text"
    caption: List[RichTextSegment] = field(default_factory=list)

    SUPPORTED_LANGUAGES = [
        "abap", "arduino", "bash", "basic", "c", "clojure", "coffeescript",
        "c++", "c#", "css", "dart", "diff", "docker", "elixir", "elm",
        "erlang", "flow", "fortran", "f#", "gherkin", "glsl", "go",
        "graphql", "groovy", "haskell", "html", "java", "javascript",
        "json", "julia", "kotlin", "latex", "less", "lisp", "livescript",
        "lua", "makefile", "markdown", "markup", "matlab", "mermaid",
        "nix", "objective-c", "ocaml", "pascal", "perl", "php",
        "plain text", "powershell", "prolog", "protobuf", "python", "r",
        "reason", "ruby", "rust", "sass", "scala", "scheme", "scss",
        "shell", "sql", "swift", "typescript", "vb.net", "verilog",
        "vhdl", "visual basic", "webassembly", "xml", "yaml"
    ]

    def _parse_type_data(self, data: dict):
        """Parse type-specific data."""
        self.content = RichTextParser.parse_array(data.get("rich_text", []))
        self.language = data.get("language", "plain text")
        self.caption = RichTextParser.parse_array(data.get("caption", []))

    def _get_type_data(self) -> dict:
        """Get type-specific data."""
        return {
            "rich_text": [seg.to_dict() for seg in self.content],
            "language": self.language,
            "caption": [seg.to_dict() for seg in self.caption]
        }
```

## Media Block Implementation

### MediaBlock Base Class

```python
@dataclass
class MediaBlock(Block):
    """Base class for media blocks."""
    media_type: str = "external"  # "external", "file", "file_upload"
    url: str = ""
    expiry_time: Optional[datetime] = None
    caption: List[RichTextSegment] = field(default_factory=list)

    def _parse_type_data(self, data: dict):
        """Parse type-specific data."""
        self.media_type = data.get("type", "external")
        self.caption = RichTextParser.parse_array(data.get("caption", []))

        if self.media_type == "external":
            self.url = data.get("external", {}).get("url", "")
        elif self.media_type == "file":
            file_data = data.get("file", {})
            self.url = file_data.get("url", "")
            expiry_str = file_data.get("expiry_time")
            if expiry_str:
                self.expiry_time = datetime.fromisoformat(expiry_str.replace("Z", "+00:00"))
        elif self.media_type == "file_upload":
            # File upload IDs are converted to files on response
            file_data = data.get("file_upload", {})
            self.url = file_data.get("url", "")

    def _get_type_data(self) -> dict:
        """Get type-specific data."""
        data = {
            "caption": [seg.to_dict() for seg in self.caption]
        }

        if self.media_type == "external":
            data["type"] = "external"
            data["external"] = {"url": self.url}
        elif self.media_type == "file":
            data["type"] = "file"
            data["file"] = {"url": self.url}
        elif self.media_type == "file_upload":
            data["type"] = "file_upload"
            data["file_upload"] = {"id": self.url}  # URL is actually upload ID

        return data

    async def refresh_url(self) -> None:
        """Refresh expired URL for hosted files."""
        if self.media_type == "file" and not self._client:
            raise RuntimeError("Cannot refresh URL without client reference")

        # Fetch updated block
        updated = await self._client.blocks.get(str(self.id))
        if isinstance(updated, MediaBlock):
            self.url = updated.url
            self.expiry_time = updated.expiry_time
```

### Image

```python
@dataclass
class Image(MediaBlock):
    """Image block."""
    type: BlockType = BlockType.IMAGE

    SUPPORTED_FORMATS = [
        "bmp", "gif", "heic", "jpeg", "jpg",
        "png", "svg", "tif", "tiff"
    ]
```

### Video

```python
@dataclass
class Video(MediaBlock):
    """Video block."""
    type: BlockType = BlockType.VIDEO

    SUPPORTED_FORMATS = [
        "amv", "asf", "avi", "f4v", "flv", "gifv",
        "mkv", "mov", "mpg", "mpeg", "mpv", "mp4",
        "m4v", "qt", "wmv"
    ]
```

## Structure Block Implementation

### Table

```python
@dataclass
class Table(StructureBlock):
    """Table block."""
    type: BlockType = BlockType.TABLE
    table_width: int = 1
    has_column_header: bool = False
    has_row_header: bool = False

    def _parse_type_data(self, data: dict):
        """Parse type-specific data."""
        self.table_width = data.get("table_width", 1)
        self.has_column_header = data.get("has_column_header", False)
        self.has_row_header = data.get("has_row_header", False)

    def _get_type_data(self) -> dict:
        """Get type-specific data."""
        return {
            "table_width": self.table_width,
            "has_column_header": self.has_column_header,
            "has_row_header": self.has_row_header
        }

    async def get_rows(self) -> List["TableRow"]:
        """Get all table rows."""
        children = await self.get_children()
        return [child for child in children if isinstance(child, TableRow)]

    async def add_row(self, cells: List[List[RichTextSegment]]) -> "TableRow":
        """Add a new row to the table."""
        if not self._client:
            raise RuntimeError("Cannot add row without client reference")

        if len(cells) != self.table_width:
            raise ValueError(f"Row must have {self.table_width} cells")

        row_data = {
            "type": "table_row",
            "table_row": {
                "cells": [[seg.to_dict() for seg in cell] for cell in cells]
            }
        }

        response = await self._client.blocks.children.append(
            block_id=str(self.id),
            children=[row_data]
        )

        return TableRow.from_dict(response.get("results", [])[0], self._client)
```

### TableRow

```python
@dataclass
class TableRow(StructureBlock):
    """Table row block."""
    type: BlockType = BlockType.TABLE_ROW
    cells: List[List[RichTextSegment]] = field(default_factory=list)

    def _parse_type_data(self, data: dict):
        """Parse type-specific data."""
        raw_cells = data.get("cells", [])
        self.cells = []
        for raw_cell in raw_cells:
            self.cells.append(RichTextParser.parse_array(raw_cell))

    def _get_type_data(self) -> dict:
        """Get type-specific data."""
        return {
            "cells": [[seg.to_dict() for seg in cell] for cell in self.cells]
        }

    def get_cell(self, index: int) -> List[RichTextSegment]:
        """Get cell at column index."""
        if 0 <= index < len(self.cells):
            return self.cells[index]
        raise IndexError(f"Cell index {index} out of range")

    def set_cell(self, index: int, content: List[RichTextSegment]) -> None:
        """Set cell at column index."""
        if 0 <= index < len(self.cells):
            self.cells[index] = content
        else:
            raise IndexError(f"Cell index {index} out of range")
```

### Column and ColumnList

```python
@dataclass
class ColumnList(StructureBlock):
    """Column list block (parent for columns)."""
    type: BlockType = BlockType.COLUMN_LIST

    async def get_columns(self) -> List["Column"]:
        """Get all columns."""
        children = await self.get_children()
        return [child for child in children if isinstance(child, Column)]

@dataclass
class Column(StructureBlock):
    """Column block."""
    type: BlockType = BlockType.COLUMN
    width_ratio: float = 0.5

    def _parse_type_data(self, data: dict):
        """Parse type-specific data."""
        self.width_ratio = data.get("width_ratio", 0.5)

    def _get_type_data(self) -> dict:
        """Get type-specific data."""
        return {"width_ratio": self.width_ratio}
```

## Block Manager

### BlockManager Class

```python
@dataclass
class BlockManager:
    """Manages blocks for a parent (page or block)."""
    parent_id: UUID
    client: Any

    async def get_children(
        self,
        page_size: int = 100,
        start_cursor: Optional[str] = None
    ) -> PaginatedResponse[Block]:
        """Get child blocks."""
        response = await self.client.blocks.children.list(
            block_id=str(self.parent_id),
            page_size=page_size,
            start_cursor=start_cursor
        )

        return PaginatedResponse(
            results=[
                Block.from_dict(block_data, self.client)
                for block_data in response.get("results", [])
            ],
            has_more=response.get("has_more", False),
            next_cursor=response.get("next_cursor")
        )

    async def get_all_children(self) -> List[Block]:
        """Get all children with automatic pagination."""
        all_blocks = []
        has_more = True
        cursor = None

        while has_more:
            response = await self.get_children(start_cursor=cursor)
            all_blocks.extend(response.results)
            has_more = response.has_more
            cursor = response.next_cursor

        return all_blocks

    async def append(self, *blocks: Block) -> List[Block]:
        """Append blocks to parent."""
        block_data = [block.to_dict() for block in blocks]

        response = await self.client.blocks.children.append(
            block_id=str(self.parent_id),
            children=block_data
        )

        return [
            Block.from_dict(block_data, self.client)
            for block_data in response.get("results", [])
        ]

    async def append_paragraph(self, text: str, **kwargs) -> Paragraph:
        """Append a paragraph block."""
        paragraph = Paragraph()
        paragraph.set_text(text, **kwargs)

        result = await self.append(paragraph)
        return result[0] if result else None

    async def append_heading(
        self,
        text: str,
        level: int = 1,
        **kwargs
    ) -> Heading:
        """Append a heading block."""
        heading = Heading(level=level)
        heading.set_text(text, **kwargs)

        result = await self.append(heading)
        return result[0] if result else None

    async def append_to_do(
        self,
        text: str,
        checked: bool = False,
        **kwargs
    ) -> ToDo:
        """Append a to-do block."""
        todo = ToDo(checked=checked)
        todo.set_text(text, **kwargs)

        result = await self.append(todo)
        return result[0] if result else None

    async def delete_children(self) -> None:
        """Delete all children blocks."""
        # Get all children
        children = await self.get_all_children()

        # Delete each child
        for child in children:
            await child.delete()
```

## Block Factory

```python
class BlockFactory:
    """Factory for creating blocks."""

    @staticmethod
    def create_paragraph(text: str, **kwargs) -> Paragraph:
        """Create a paragraph block."""
        paragraph = Paragraph(**kwargs)
        paragraph.set_text(text)
        return paragraph

    @staticmethod
    def create_heading(text: str, level: int = 1, **kwargs) -> Heading:
        """Create a heading block."""
        heading = Heading(level=level, **kwargs)
        heading.set_text(text)
        return heading

    @staticmethod
    def create_to_do(text: str, checked: bool = False, **kwargs) -> ToDo:
        """Create a to-do block."""
        todo = ToDo(checked=checked, **kwargs)
        todo.set_text(text)
        return todo

    @staticmethod
    def create_code(code: str, language: str = "python") -> Code:
        """Create a code block."""
        return Code(
            content=[TextSegment(content=code, annotations=Annotations(code=True))],
            language=language
        )

    @staticmethod
    def create_image(url: str, **kwargs) -> Image:
        """Create an image block."""
        return Image(url=url, **kwargs)

    @staticmethod
    def create_table(
        width: int,
        has_column_header: bool = False,
        has_row_header: bool = False
    ) -> Table:
        """Create a table block."""
        return Table(
            table_width=width,
            has_column_header=has_column_header,
            has_row_header=has_row_header
        )

    @staticmethod
    def create_table_row(cells: List[List[RichTextSegment]]) -> TableRow:
        """Create a table row."""
        return TableRow(cells=cells)
```

## Usage Examples

### Creating Blocks

```python
# Create a page with content
page = await client.pages.create(parent_id, title="My Page")

# Add blocks
await page.blocks.append_paragraph("Welcome to my page!")
await page.blocks.append_heading("Section 1", level=1)
await page.blocks.append_to_do("Task 1", checked=False)

# Or use factory
paragraph = BlockFactory.create_paragraph("Hello, world!")
await page.blocks.append(paragraph)
```

### Working with Tables

```python
# Create a table
table = BlockFactory.create_table(
    width=3,
    has_column_header=True
)
table_block = await page.blocks.append(table)[0]

# Add header row
header_row = BlockFactory.create_table_row([
    [TextSegment(content="Name")],
    [TextSegment(content="Email")],
    [TextSegment(content="Phone")]
])
await table_block.add_row(header_row.cells)

# Add data row
data_row = BlockFactory.create_table_row([
    [TextSegment(content="John Doe")],
    [TextSegment(content="john@example.com")],
    [TextSegment(content="555-1234")]
])
await table_block.add_row(data_row.cells)
```

### Querying and Modifying Blocks

```python
# Get all blocks from a page
blocks = await page.blocks.get_all_children()

# Filter specific types
paragraphs = [b for b in blocks if isinstance(b, Paragraph)]
todos = [b for b in blocks if isinstance(b, ToDo)]

# Modify a block
for todo in todos:
    if not todo.checked:
        await todo.toggle()
```

## Testing Strategy

### Unit Tests

```python
import pytest

def test_paragraph_creation():
    """Test creating a paragraph block."""
    paragraph = BlockFactory.create_paragraph("Test text")
    assert paragraph.type == BlockType.PARAGRAPH
    assert paragraph.plain_text == "Test text"

def test_paragraph_to_dict():
    """Test converting paragraph to API format."""
    paragraph = BlockFactory.create_paragraph("Bold text", bold=True)
    data = paragraph.to_dict()

    assert data["type"] == "paragraph"
    assert "paragraph" in data
    assert len(data["paragraph"]["rich_text"]) == 1

def test_heading_levels():
    """Test heading level validation."""
    h1 = Heading(level=1)
    assert h1.type == BlockType.HEADING_1

    h2 = Heading(level=2)
    assert h2.type == BlockType.HEADING_2

    with pytest.raises(ValueError):
        Heading(level=5)  # Invalid

@pytest.mark.asyncio
async def test_block_manager_append():
    """Test appending blocks via BlockManager."""
    # Mock client
    client = MockNotionClient()
    manager = BlockManager(parent_id=UUID("..."), client=client)

    paragraph = BlockFactory.create_paragraph("Test")
    result = await manager.append(paragraph)

    assert len(result) == 1
    assert isinstance(result[0], Paragraph)
```

## Implementation Checklist

### Core Classes
- [ ] `Block` base class
- [ ] `Parent` class
- [ ] `PartialUser` class
- [ ] `BlockType` enum
- [ ] `BlockFactory` class
- [ ] `BlockManager` class

### Text Blocks
- [ ] `TextBlock` base class
- [ ] `Paragraph` class
- [ ] `Heading` class (with levels)
- [ ] `BulletedListItem` class
- [ ] `NumberedListItem` class
- [ ] `ToDo` class
- [ ] `Toggle` class
- [ ] `Quote` class
- [ ] `Callout` class
- [ ] `Code` class

### Media Blocks
- [ ] `MediaBlock` base class
- [ ] `Image` class
- [ ] `Video` class
- [ ] `Audio` class
- [ ] `File` class
- [ ] `PDF` class

### Structure Blocks
- [ ] `StructureBlock` base class
- [ ] `ColumnList` class
- [ ] `Column` class
- [ ] `Table` class
- [ ] `TableRow` class
- [ ] `TableOfContents` class
- [ ] `SyncedBlock` class
- [ ] `Template` class

### Special Blocks
- [ ] `ChildDatabase` class
- [ ] `ChildPage` class
- [ ] `Breadcrumb` class
- [ ] `Equation` class
- [ ] `Divider` class

### Rich Text Support
- [ ] `RichTextSegment` base class
- [ ] `TextSegment` class
- [ ] Mention classes (`UserMention`, `DateMention`, etc.)
- [ ] `EquationSegment` class
- [ ] `Annotations` class
- [ ] `RichTextBuilder` class
- [ ] `RichTextParser` class

### Utilities
- [ ] Block type mapping
- [ ] Color enums
- [ ] Validation helpers
- [ ] Pagination support

### Testing
- [ ] Unit tests for each block class
- [ ] Integration tests with Notion API
- [ ] Tests for BlockManager
- [ ] Tests for BlockFactory
- [ ] Tests for RichTextBuilder
- [ ] Mock client for testing

---

**Related Documentation:**
- [Blocks API Reference](./blocks-api.md) - Complete API endpoint documentation
- [Blocks Overview](./blocks-overview.md) - Block concepts
- [Block Types](./block-types.md) - Complete block type reference
- [Rich Text Reference](./rich-text.md) - Rich text implementation
