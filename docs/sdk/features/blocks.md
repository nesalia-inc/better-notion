# Blocks Feature

Comprehensive documentation of block-related operations and features in the Better Notion SDK.

## Overview

Blocks are the atomic content units in Notion. They form the content of pages and can be nested up to 2 levels deep.

**Block Types:**
- **Text blocks**: Paragraph, headings, lists, quotes, callouts, code
- **Media blocks**: Image, video, file, audio, PDF
- **Layout blocks**: Column, divider, table of contents
- **Database blocks**: Database view, linked database
- **Embed blocks**: Embed, bookmark, link preview
- **Other**: Toggle, sync block, template, breadcrumb

## Features

### Core CRUD Operations

#### Retrieve a Block

```python
# Get block by ID
block = await client.blocks.get(block_id)

# Access block properties
print(block.type)           # "paragraph", "heading_1", etc.
print(block.content)        # Type-specific content
print(block.has_children)   # Boolean

# Check block type
if block.is_paragraph:
    text = block.text
elif block.is_heading:
    text = block.text
    level = block.level
elif block.is_code:
    code = block.code
    language = block.language
```

**API Equivalent:** `GET /blocks/{block_id}`

**Enhancements:**
- Type checking properties (`.is_paragraph`, etc.)
- Type-specific content accessors
- Content extraction helpers

#### Update a Block

```python
# Update text content
await client.blocks.update(
    block,
    text="New text content"
)

# Update code block
await client.blocks.update(
    block,
    code="print('hello')",
    language="python"
)

# Update heading
await client.blocks.update(
    block,
    text="New Title",
    level=2
)
```

**API Equivalent:** `PATCH /blocks/{block_id}`

**Enhancements:**
- Direct content update (no rich text structure)
- Type-safe parameters
- Validation based on block type

#### Delete a Block

```python
# Delete a block
await client.blocks.delete(block)

# Delete returns immediately
# Block is moved to trash
```

**API Equivalent:** `DELETE /blocks/{block_id}`

### Children Operations

#### Retrieve Children

```python
# Get children of a block
async for child in client.blocks.children(block_id):
    print(child.type, child.content)

# From block object
async for child in block.children:
    process(child)

# Collect all children
children = await client.blocks.children(block_id).collect()
```

**API Equivalent:** `GET /blocks/{block_id}/children` + pagination

**Enhancements:**
- Async iterator for pagination
- Direct access from block object
- Memory-efficient streaming

#### Append Children

```python
# Append single block
await client.blocks.append(
    block_id,
    Block.paragraph("New paragraph")
)

# Append multiple blocks
await client.blocks.append(
    block_id,
    children=[
        Block.heading("Section 1", level=2),
        Block.paragraph("Content here"),
        Block.bullet_item("Point 1"),
        Block.bullet_item("Point 2")
    ]
)

# From block object
await block.append_children([
    Block.paragraph("Another paragraph")
])
```

**API Equivalent:** `PATCH /blocks/{block_id}/children`

**Enhancements:**
- Accepts single block or list
- Block factory methods for creation
- Automatic rich text structure generation

### Block Creation

#### Factory Methods

```python
# Text blocks
Block.paragraph("Plain text paragraph")

Block.heading("Main Title", level=1)
Block.heading("Subtitle", level=2)
Block.heading("Section", level=3)

Block.bullet_item("Bullet point")
Block.numbered_item("Numbered item")
Block.to_do("Task name", checked=False)

# Rich text
Block.paragraph("Text with **bold** and *italic*")

# Code
Block.code("print('hello')", language="python")
Block.code("SELECT * FROM table", language="sql")

# Quote
Block.quote("This is a quote")

# Callout
Block.callout("Important note", icon="⚠️")

# Divider
Block.divider()

# Toggle
Block.toggle("Click to expand", children=[...])
```

#### Rich Text Blocks

```python
# With formatting
Block.paragraph(
    RichText()
    .text("Normal ")
    .bold("bold text")
    .text(" ")
    .italic("italic text")
)

# With links
Block.paragraph(
    RichText()
    .text("Visit ")
    .link("Notion", "https://notion.so")
)

# With mentions
Block.paragraph(
    RichText()
    .text("Assigned to ")
    .user_mention(user_id)
)
```

#### Media Blocks

```python
# Image
Block.image("https://example.com/image.png")
Block.image(file_upload)  # From file upload

# Video
Block.video("https://example.com/video.mp4")

# File
Block.file("https://example.com/document.pdf")

# Audio
Block.audio("https://example.com/audio.mp3")

# PDF
Block.pdf("https://example.com/doc.pdf")
```

#### Layout Blocks

```python
# Columns
Block.column_list([
    Block.column([Block.paragraph("Column 1")]),
    Block.column([Block.paragraph("Column 2")])
])

# Divider
Block.divider()

# Table of Contents
Block.table_of_contents()
```

### Hierarchical Navigation

#### Get Parent

```python
# Get parent object
parent = await block.parent

# Parent can be Page or Block
if isinstance(parent, Page):
    print(f"In page: {parent.title}")
elif isinstance(parent, Block):
    print(f"In block: {parent.type}")

# From cache
parent = block.parent_cached
```

**API Equivalent:** Get block + access parent field + fetch parent

**Why SDK-Exclusive:**
- User thinks "get parent", not "get parent ID then fetch"
- Returns typed object (Page or Block)
- Uses cache when available

#### Get Children

```python
# Iterate over children
async for child in block.children:
    print(f"{child.type}: {child.content}")

# Collect all children
children = await block.children.collect()

# Check if has children
if block.has_children:
    async for child in block.children:
        process(child)
```

**Why SDK-Exclusive:**
- `block.children` more intuitive than `api.blocks.children.list(block_id)`
- Async iterator handles pagination
- No manual cursor management

#### Walk Tree

```python
# Walk all descendants recursively
async for descendant in block.descendants():
    process(descendant)

# With depth limit
async for descendant in block.descendants(max_depth=2):
    process(descendant)

# Walk with level info
async for level, descendant in block.descendants.with_level():
    print(f"Level {level}: {descendant.type}")
```

**API Equivalent:** Recursive traversal with multiple API calls

**Why SDK-Exclusive:**
- Common pattern (traverse block tree)
- Handles 2-level nesting limitation
- Automatic pagination at each level

### Content Manipulation

#### Insert Child at Position

```python
# Insert at beginning
await block.insert_child(
    new_block,
    position=0
)

# Insert at specific position
await block.insert_child(
    new_block,
    position=5
)

# Insert before another block
await block.insert_child(
    new_block,
    before=other_block.id
)
```

**API Equivalent:** `PATCH /blocks/{block_id}/children` with children array

**Why SDK-Exclusive:**
- Semantic operation ("insert at position")
- API requires rebuilding entire children array
- SDK handles array manipulation

#### Replace All Children

```python
# Replace all children
await block.replace_children(new_blocks)

# Clear and add new
await block.replace_children([
    Block.heading("New Content"),
    Block.paragraph("All new content")
])
```

**Why SDK-Exclusive:**
- Common operation (replace content)
- Simpler than delete + append

#### Clear Children

```python
# Delete all children
await block.clear_children()

# Faster than deleting individually
# Single API call
```

**Why SDK-Exclusive:**
- Common pattern (clear before adding new content)
- More efficient than individual deletes

#### Move Block

```python
# Move to new parent
await block.move(new_parent=other_block)

# Move with position
await block.move(
    new_parent=page,
    position="after:block_id"
)

# Move to beginning
await block.move(
    new_parent=other_block,
    position="first"
)
```

**API Equivalent:** `PATCH /blocks/{block_id}` with parent

**Why SDK-Exclusive:**
- Semantic operation ("move")
- Handles position parameter formatting
- Updates cache automatically

### Type-Specific Operations

#### Text Operations

```python
if block.is_text_block:  # paragraph, heading, etc.
    # Get plain text
    text = block.text

    # Get rich text
    rich_text = block.rich_text

    # Append text
    await block.append_text(" more text")

    # Replace text
    await block.replace_text("old", "new")
```

#### Code Operations

```python
if block.is_code:
    # Get code
    code = block.code

    # Get language
    language = block.language

    # Update code
    await block.update_code(
        "new code",
        language="javascript"
    )
```

#### Toggle Operations

```python
if block.is_toggle:
    # Expand toggle
    await block.expand()

    # Collapse toggle
    await block.collapse()

    # Toggle state
    if block.is_expanded:
        await block.collapse()
```

#### To-Do Operations

```python
if block.is_to_do:
    # Check if checked
    if block.checked:
        print("Task is done")

    # Mark as done
    await block.check()

    # Uncheck
    await block.uncheck()

    # Toggle
    await block.toggle_check()
```

### Bulk Operations

#### Bulk Append

```python
# Append multiple blocks efficiently
await block.append_children([
    Block.paragraph("Paragraph 1"),
    Block.paragraph("Paragraph 2"),
    Block.paragraph("Paragraph 3"),
    # ... hundreds more
])
```

**Why SDK-Exclusive:**
- Single API call for all blocks
- Handles rate limiting
- More efficient than individual appends

#### Bulk Delete

```python
# Delete multiple blocks
await client.blocks.delete_bulk([
    block1, block2, block3, block4
])

# Delete all children
children = await block.children.collect()
await client.blocks.delete_bulk(children)
```

**Why SDK-Exclusive:**
- Common pattern (clear section)
- Handles batching and rate limiting
- Parallel deletion where possible

### Block Type Helpers

#### Type Checking

```python
# Text blocks
block.is_paragraph
block.is_heading_1
block.is_heading_2
block.is_heading_3
block.is_text_block  # Any text block

# List blocks
block.is_bullet_list
block.is_numbered_list
block.is_to_do

# Media blocks
block.is_image
block.is_video
block.is_file
block.is_audio
block.is_pdf

# Other
block.is_code
block.is_quote
block.is_callout
block.is_divider
block.is_toggle
block.is_table
block.is_column_list
```

#### Content Access

```python
# Type-safe content access
if block.is_heading:
    level = block.level  # 1, 2, or 3
    text = block.text

if block.is_code:
    code = block.code
    language = block.language
    caption = block.caption

if block.is_to_do:
    text = block.text
    checked = block.checked

if block.is_image:
    url = block.url
    caption = block.caption
```

## Advanced Patterns

### Build Document Structure

```python
# Create structured document
page = await client.pages.create(
    parent=database,
    title="Project Plan",
    content=[
        Block.heading("Introduction", level=1),
        Block.paragraph("This document outlines..."),

        Block.heading("Objectives", level=2),
        Block.bullet_item("Objective 1"),
        Block.bullet_item("Objective 2"),
        Block.bullet_item("Objective 3"),

        Block.heading("Timeline", level=2),
        Block.numbered_item("Phase 1: Planning"),
        Block.numbered_item("Phase 2: Execution"),
        Block.numbered_item("Phase 3: Review"),

        Block.divider(),

        Block.callout("Important: Review weekly", icon="⚠️")
    ]
)
```

### Dynamic Content Generation

```python
# Generate blocks from data
tasks = ["Task 1", "Task 2", "Task 3"]

blocks = [
    Block.heading("Task List", level=2)
]

for task in tasks:
    blocks.append(Block.to_do(task, checked=False))
    blocks.append(Block.paragraph(f"Details for {task}"))

await page.append_children(blocks)
```

### Convert Markdown to Blocks

```python
# Markdown-like parsing
def markdown_to_blocks(text: str) -> list[Block]:
    blocks = []
    for line in text.split("\n"):
        if line.startswith("# "):
            blocks.append(Block.heading(line[2:], level=1))
        elif line.startswith("## "):
            blocks.append(Block.heading(line[3:], level=2))
        elif line.startswith("### "):
            blocks.append(Block.heading(line[4:], level=3))
        elif line.startswith("- "):
            blocks.append(Block.bullet_item(line[2:]))
        elif line.startswith("1. "):
            blocks.append(Block.numbered_item(line[3:]))
        elif line.strip() == "---":
            blocks.append(Block.divider())
        else:
            blocks.append(Block.paragraph(line))
    return blocks

# Use
blocks = markdown_to_blocks(markdown_content)
await page.append_children(blocks)
```

### Find Blocks by Type

```python
# Find all code blocks in page
async def find_code_blocks(page: Page) -> list[Block]:
    code_blocks = []
    async for block in page.descendants():
        if block.is_code:
            code_blocks.append(block)
    return code_blocks

# Find all images
async def find_images(page: Page) -> list[Block]:
    images = []
    async for block in page.descendants():
        if block.is_image:
            images.append(block)
    return images
```

### Extract Text Content

```python
# Extract all text from page
async def extract_text(page: Page) -> str:
    parts = []
    async for block in page.descendants():
        if block.is_text_block:
            parts.append(block.text)
    return "\n".join(parts)

# Use
text = await extract_text(page)
print(text)
```

### Transform Blocks

```python
# Transform all headings
async def transform_headings(page: Page):
    async for block in page.descendants():
        if block.is_heading:
            # Increase level by 1
            new_level = min(block.level + 1, 3)
            await client.blocks.update(
                block,
                text=block.text,
                level=new_level
            )

# Use
await transform_headings(page)
```

## Implementation Considerations

### Block Object Model

```python
class Block(BaseEntity):
    id: str
    type: str
    content: Any  # Type-specific
    has_children: bool

    # Type checking
    @property
    def is_paragraph(self) -> bool
    @property
    def is_heading(self) -> bool
    @property
    def is_code(self) -> bool
    # ... other type checks

    # Type-specific accessors
    @property
    def text(self) -> str | None
    @property
    def level(self) -> int | None
    @property
    def code(self) -> str | None
    @property
    def language(self) -> str | None

    # Hierarchical
    async def parent(self) -> Page | Block | None
    @property
    def parent_cached(self) -> Page | Block | None
    async def children(self) -> AsyncIterator[Block]
    async def descendants(self) -> AsyncIterator[Block]

    # Operations
    async def append_children(blocks: list[Block]) -> None
    async def insert_child(block: Block, position: int) -> None
    async def replace_children(blocks: list[Block]) -> None
    async def clear_children(self) -> None
    async def move(new_parent, position: str | None) -> Block

    # Static factory
    @staticmethod
    def paragraph(text: str) -> Block
    @staticmethod
    def heading(text: str, level: int) -> Block
    @staticmethod
    def code(code: str, language: str) -> Block
    # ... other factory methods
```

### Rich Text Builder

```python
class RichText:
    def text(self, content: str) -> RichText
    def bold(self, content: str) -> RichText
    def italic(self, content: str) -> RichText
    def underline(self, content: str) -> RichText
    def strike(self, content: str) -> RichText
    def code(self, content: str) -> RichText
    def link(self, text: str, url: str) -> RichText
    def user_mention(self, user_id: str) -> RichText
    def page_mention(self, page_id: str) -> RichText
    def database_mention(self, db_id: str) -> RichText
    def equation(self, expression: str) -> RichText

    def build(self) -> list[dict]
```

### Nesting Constraints

Notion enforces maximum 2 levels of block nesting:

```
Page (level 0)
  └─ Block (level 1)
      ├─ Block (level 2) ✓ OK
      │   └─ Block (level 3) ✗ NOT ALLOWED
      └─ Block (level 2) ✓ OK
```

SDK enforces this constraint:
```python
# Raises error if trying to nest too deep
try:
    deep_block = Block.paragraph("Too deep")
    parent.append_children([deep_block])  # Error!
except NestingError:
    print("Cannot nest more than 2 levels")
```

## Error Scenarios

| Scenario | Error | Solution |
|----------|-------|----------|
| Block doesn't exist | `BlockNotFound` | Verify ID |
| Too much nesting | `NestingError` | Restructure blocks |
| Invalid content type | `ValidationError` | Check block type |
| No children access | `NoChildrenError` | Check has_children |
| Parent is full | `CapacityError` | Maximum children reached |

## Performance Considerations

### Optimal Patterns

```python
# GOOD: Stream descendants
async for block in page.descendants():
    process(block)

# AVOID: Load all descendants
all_blocks = await page.descendants().collect()  # Memory intensive

# GOOD: Batch append
await block.append_children(many_blocks)  # Single API call

# AVOID: Individual appends
for b in many_blocks:
    await block.append_children([b])  # Many API calls
```

### Caching Strategy

**Populate cache:**
```python
# Traverse to cache blocks
async for block in page.descendants():
    # Access populates cache
    print(block.type)

# Now instant lookups
block = client.blocks.cache.get(block_id)
```

## Future Enhancements

### Tier 2 (High Priority)
- [ ] Block templates
- [ ] Block transformation helpers
- [ ] Rich text HTML import/export

### Tier 3 (Medium Priority)
- [ ] Table block helpers
- [ ] Column layout builders
- [ ] Sync block operations

### Tier 4 (Future)
- [ ] Block versioning
- [ ] Collaborative editing
- [ ] Real-time block updates
