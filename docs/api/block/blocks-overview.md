# Blocks - Overview

## Introduction

Blocks are the fundamental content units in Notion. Every piece of content on a page - headings, paragraphs, lists, media, and more - is represented as a block object in the Notion API.

## Core Concepts

### Block Structure

Every block object follows this base structure:

```json
{
  "object": "block",
  "id": "uuid-v4",
  "parent": { /* parent object */ },
  "created_time": "ISO-8601",
  "last_edited_time": "ISO-8601",
  "created_by": { /* partial user object */ },
  "last_edited_by": { /* partial user object */ },
  "has_children": false,
  "archived": false,
  "in_trash": false,
  "type": "block_type",
  "block_type": { /* type-specific data */ }
}
```

### Base Fields

| Field | Type | Description | Capability Required |
|-------|------|-------------|---------------------|
| `object` | string | Always `"block"` | None |
| `id` | string (UUIDv4) | Unique identifier for the block | None |
| `parent` | object | Information about the block's parent | Read content |
| `type` | string (enum) | The block type identifier | None |
| `created_time` | string (ISO 8601) | Creation timestamp | Read content |
| `created_by` | PartialUser | User who created the block | Read content |
| `last_edited_time` | string (ISO 8601) | Last edit timestamp | Read content |
| `last_edited_by` | PartialUser | User who last edited the block | Read content |
| `archived` | boolean | Whether the block is archived | None |
| `in_trash` | boolean | Whether the block is deleted | Read content |
| `has_children` | boolean | Whether the block has nested child blocks | None |
| `{type}` | object | Type-specific block information | Varies |

**Important:** Fields not marked with an asterisk (*) require the "read content" capability to be returned by the API.

## Parent Object

Blocks can have different parent types:

```json
// Parent is a page
{
  "type": "page_id",
  "page_id": "59833787-2cf9-4fdf-8782-e53db20768a5"
}

// Parent is another block
{
  "type": "block_id",
  "block_id": "7d50a184-5bbe-4d90-8f29-6bec57ed817b"
}

// Parent is a workspace (for root blocks)
{
  "type": "workspace",
  "workspace": true
}
```

## Block Hierarchy

Blocks can be nested within other blocks, creating a tree structure:

```
Page (root)
├── Heading 1
├── Paragraph
│   └── Text
├── Bulleted List Item
│   ├── Nested Paragraph
│   └── Another List Item
└── Toggle
    └── Hidden Content
```

### Blocks Supporting Children

The following block types can contain nested blocks:

- **Bulleted list item** - Can contain nested blocks
- **Callout** - Can contain nested blocks
- **Child database** - Database within a page
- **Child page** - Page within a page
- **Column** - Column within a column list
- **Heading 1/2/3** - When `is_toggleable: true`
- **Numbered list item** - Can contain nested blocks
- **Paragraph** - Can contain nested blocks
- **Quote** - Can contain nested blocks
- **Synced block** - Can contain nested blocks
- **Table** - Contains table rows
- **Table row** - Contains cells
- **Template** - Can contain nested blocks
- **To do** - Can contain nested blocks
- **Toggle** - Can contain nested blocks

## Block Type Categories

### 1. Text Blocks
- Paragraph
- Heading 1, Heading 2, Heading 3
- Bulleted list item
- Numbered list item
- To do
- Toggle
- Quote
- Callout

### 2. Media Blocks
- Image
- Video
- Audio
- File
- PDF

### 3. Embed Blocks
- Bookmark
- Embed
- Link preview

### 4. Structure Blocks
- Column list
- Column
- Table
- Table row
- Table of contents
- Synced block
- Template
- Divider

### 5. Database Blocks
- Child database
- Child page

### 6. Special Blocks
- Breadcrumb
- Code
- Equation

### 7. Unsupported Blocks
- `unsupported` - Represents blocks not yet supported by the API

## Working with Blocks

### Retrieving Blocks

Use the **Retrieve block children** endpoint to list blocks:

```
GET /blocks/{block_id}/children
```

This returns a paginated list of child blocks for the given block ID.

**For pages:** Use the page ID as the block ID to get all top-level blocks on a page.

### Creating Blocks

Use the **Append block children** endpoint to add blocks:

```
POST /blocks/{block_id}/children
```

**Key limitations:**
- Some block types cannot be created via API (e.g., `link_preview`, `breadcrumb`)
- Some blocks require special endpoints (e.g., `child_database`, `child_page`)
- Block creation is append-only; blocks must be deleted and recreated to move them

### Updating Blocks

Use the **Update block** endpoint:

```
PATCH /blocks/{block_id}
```

**Important limitations:**
- `synced_block` content cannot be updated via API
- Table `table_width` cannot be changed after creation
- Some block types don't support updates

### Deleting Blocks

Use the **Delete block** endpoint:

```
DELETE /blocks/{block_id}
```

**Note:** Deleting a parent block also deletes all its children.

## Rich Text

Most blocks contain rich text content. The `rich_text` array is a common structure across block types.

See [Rich Text Reference](./rich-text.md) for detailed information about:
- Text formatting (bold, italic, underline, etc.)
- Colors
- Links
- Mentions (@users, @dates, @pages, @databases)
- Equations

## Color System

Many blocks support color customization. Colors come in two categories:

### Text Colors
- `blue`, `brown`, `gray`, `green`, `orange`, `pink`, `purple`, `red`, `yellow`, `default`

### Background Colors
- `blue_background`, `brown_background`, `gray_background`, `green_background`, `orange_background`, `pink_background`, `purple_background`, `red_background`, `yellow_background`, `default`

## Unsupported Block Types

The Notion API doesn't support all block types that exist in the Notion UI. Unsupported blocks appear in API responses with:

```json
{
  "type": "unsupported",
  "unsupported": {}
}
```

When your integration encounters an `unsupported` block:
- It can still be moved (position changed)
- It cannot be created or modified via API
- Content cannot be retrieved or modified

## Common Patterns

### Example: Creating a Simple Page

```python
# Better Notion SDK example
page = await client.pages.get(page_id)

# Add a heading
await page.blocks.append_heading(
    "Welcome to My Page",
    level=1,
    color="blue"
)

# Add a paragraph
await page.blocks.append_paragraph(
    "This is some text with **bold** and *italic* formatting."
)

# Add a to-do item
await page.blocks.append_to_do(
    "Complete the documentation",
    checked=False
)
```

### Example: Working with Nested Blocks

```python
# Create a bullet list with nested items
await page.blocks.append_bulleted_list_item(
    "Main item",
    children=[
        Block(type="paragraph", content="Nested item 1"),
        Block(type="paragraph", content="Nested item 2")
    ]
)
```

### Example: Fetching All Blocks

```python
# Get all blocks from a page (with automatic pagination)
blocks = await page.blocks.get_all()

# Or iterate page by page
async for block_batch in page.blocks.iter_batches():
    for block in block_batch:
        print(block.type)
```

## SDK Architecture Implications

### Class Hierarchy

```python
class Block:
    """Base block class."""
    id: UUID
    type: BlockType
    parent: Parent
    created_time: datetime
    last_edited_time: datetime
    has_children: bool
    archived: bool
    in_trash: bool

class TextBlock(Block):
    """Base class for blocks with rich text."""
    content: RichText
    color: str

class Paragraph(TextBlock):
    """Paragraph block."""
    pass

class Heading(TextBlock):
    """Heading block (H1, H2, H3)."""
    level: int
    is_toggleable: bool
```

### Block Factory Pattern

```python
class BlockFactory:
    @staticmethod
    def from_dict(data: dict) -> Block:
        block_type = data.get("type")

        if block_type == "paragraph":
            return Paragraph.from_dict(data)
        elif block_type == "heading_1":
            return Heading.from_dict(data, level=1)
        # ... etc
```

### Block Manager

```python
class BlockManager:
    """Manages blocks for a parent (page or block)."""

    async def append(self, block: Block) -> Block:
        """Append a block to the parent."""
        pass

    async def get_children(self, **kwargs) -> List[Block]:
        """Get child blocks."""
        pass

    async def delete(self, block_id: str) -> None:
        """Delete a block."""
        pass

    async def update(self, block: Block) -> Block:
        """Update a block."""
        pass
```

## Implementation Checklist

- [ ] Base `Block` class with all common fields
- [ ] Type-specific block classes (30+ types)
- [ ] `BlockFactory` for parsing API responses
- [ ] `BlockManager` for CRUD operations
- [ ] Rich text parsing and formatting
- [ ] Color enum with all color values
- [ ] Block hierarchy traversal utilities
- [ ] Pagination support for children
- [ ] Validation for block-specific constraints
- [ ] Helper methods for common operations

## Related Documentation

- [Blocks API Reference](./blocks-api.md) - Complete API endpoint documentation
- [Block Types Reference](./block-types.md) - Complete list of all block types
- [Text Blocks](./text-blocks.md) - Paragraphs, headings, lists
- [Media Blocks](./media-blocks.md) - Images, videos, files
- [Structure Blocks](./structure-blocks.md) - Tables, columns, synced blocks
- [Rich Text Reference](./rich-text.md) - Text formatting system
- [Block Implementation Guide](./blocks-implementation.md) - SDK implementation details

---

**Next:** See [Blocks API Reference](./blocks-api.md) for complete API endpoint documentation or [Block Types](./block-types.md) for a complete reference of all block types and their properties.
