# Block Model

High-level Block SDK model with type-specific content access and navigation.

## Overview

The `Block` model represents a content block in Notion (paragraph, heading, code, image, etc.) with intelligent type detection and content access.

```python
# Access block
block = await client.blocks.get(block_id)

# Type checking
if block.is_heading:
    print(f"Heading: {block.text}")

if block.is_code:
    print(f"Code: {block.code}")
    print(f"Language: {block.language}")

# Navigation
async for child in block.children:
    print(f"Child: {child.type}")
```

## Architecture

### Block Class Structure

```python
# better_notion/_sdk/models/block.py

from better_notion._sdk.models.base import BaseEntity
from typing import Any, TYPE_CHECKING

if TYPE_CHECKING:
    from better_notion._sdk.client import NotionClient

class Block(BaseEntity):
    """Generic Block model - base for all specialized blocks.

    This is the base class for all block types. For type-specific
    functionality, use specialized classes like Code, Todo, Paragraph.

    Example:
        >>> # Get block (returns specialized instance)
        >>> block = await Block.get(block_id, client=client)
        >>>
        >>> # Type checking
        >>> if block.type == "code":
        ...     print(block.code)  # Code-specific property
    """

    def __init__(self, client: "NotionClient", data: dict[str, Any]) -> None:
        """Initialize block with client and API response data.

        Args:
            client: NotionClient instance
            data: Block object from Notion API
        """
        super().__init__(client, data)

        # Cache block type for frequent access
        self._block_type = self._data.get("type", "")

    @classmethod
    async def get(
        cls,
        block_id: str,
        client: "NotionClient"
    ) -> "Block":
        """Get block by ID.

        Args:
            block_id: Block UUID
            client: NotionClient instance

        Returns:
            Specialized block instance (Code, Todo, Paragraph, etc.)

        Raises:
            BlockNotFound: If block doesn't exist

        Example:
            >>> block = await Block.get(block_id, client=client)
        """
        # Fetch from API
        data = await client.api._request("GET", f"/blocks/{block_id}")

        # Return specialized instance based on type
        return cls.from_data(client, data)

    @classmethod
    def from_data(
        cls,
        client: "NotionClient",
        data: dict[str, Any]
    ) -> "Block":
        """Create specialized block instance from API data.

        Args:
            client: NotionClient instance
            data: Raw API response data

        Returns:
            Specialized block instance (Code, Todo, etc.)

        Example:
            >>> block = Block.from_data(client, api_data)
        """
        from better_notion._sdk.models.blocks.code import Code
        from better_notion._sdk.models.blocks.todo import Todo
        from better_notion._sdk.models.blocks.paragraph import Paragraph
        # Import other specialized blocks...

        block_type = data.get("type", "")

        # Map to specialized class
        block_classes = {
            "code": Code,
            "to_do": Todo,
            "paragraph": Paragraph,
            # Add more mappings...
        }

        block_class = block_classes.get(block_type, cls)
        return block_class(client, data)

    @property
    def object(self) -> str:
        """Object type (always "block")."""
        return "block"
```

## Properties

### Metadata

```python
@property
def type(self) -> str:
    """Get block type.

    Returns:
        Block type string

    Types:
        'paragraph', 'heading_1', 'heading_2', 'heading_3',
        'bulleted_list_item', 'numbered_list_item', 'to_do',
        'toggle', 'callout', 'quote', 'divider', 'thematic_break',
        'code', 'bookmark', 'image', 'video', 'file', 'pdf',
        'table', 'table_row', 'table_of_contents',
        'breadcrumb', 'column', 'column_list',
        'link_to_page', 'synced_block', 'template',
        'link_preview', 'embed', 'child_page', 'child_database'

    Example:
        >>> block.type
        'heading_1'
    """
    return self._block_type

@property
def has_children(self) -> bool:
    """Check if block has children.

    Returns:
        True if block has children blocks

    Example:
        >>> if block.has_children:
        ...     async for child in block.children:
        ...         print(child.type)
    """
    return self._data.get("has_children", False)

@property
def archived(self) -> bool:
    """Check if block is archived.

    Returns:
        True if block is archived
    """
    return self._data.get("archived", False)

@property
def created_by(self) -> str:
    """Get ID of user who created block.

    Returns:
        User ID

    Note:
        Use client.users.cache.get() to get User object
    """
    return self._data.get("created_by", "")

@property
def last_edited_by(self) -> str:
    """Get ID of user who last edited block.

    Returns:
        User ID
    """
    return self._data.get("last_edited_by", "")

@property
def created_time(self) -> datetime:
    """Get creation timestamp.

    Returns:
        Creation datetime
    """
    from datetime import datetime
    ts = self._data.get("created_time", "")
    return datetime.fromisoformat(ts.replace('Z', '+00:00'))

@property
def last_edited_time(self) -> datetime:
    """Get last edit timestamp.

    Returns:
        Last edit datetime
    """
    from datetime import datetime
    ts = self._data.get("last_edited_time", "")
    return datetime.fromisoformat(ts.replace('Z', '+00:00'))
```

### Type Checkers

```python
# Text blocks
@property
def is_paragraph(self) -> bool:
    """Check if block is a paragraph."""
    return self._block_type == "paragraph"

@property
def is_heading(self) -> bool:
    """Check if block is any heading (1, 2, or 3)."""
    return self._block_type in ("heading_1", "heading_2", "heading_3")

@property
def is_heading_1(self) -> bool:
    """Check if block is heading level 1."""
    return self._block_type == "heading_1"

@property
def is_heading_2(self) -> bool:
    """Check if block is heading level 2."""
    return self._block_type == "heading_2"

@property
def is_heading_3(self) -> bool:
    """Check if block is heading level 3."""
    return self._block_type == "heading_3"

@property
def is_quote(self) -> bool:
    """Check if block is a quote."""
    return self._block_type == "quote"

@property
def is_callout(self) -> bool:
    """Check if block is a callout."""
    return self._block_type == "callout"

# List blocks
@property
def is_bulleted_list_item(self) -> bool:
    """Check if block is a bulleted list item."""
    return self._block_type == "bulleted_list_item"

@property
def is_numbered_list_item(self) -> bool:
    """Check if block is a numbered list item."""
    return self._block_type == "numbered_list_item"

@property
def is_to_do(self) -> bool:
    """Check if block is a to-do item."""
    return self._block_type == "to_do"

# Structure blocks
@property
def is_toggle(self) -> bool:
    """Check if block is a toggle."""
    return self._block_type == "toggle"

@property
def is_divider(self) -> bool:
    """Check if block is a divider."""
    return self._block_type in ("divider", "thematic_break")

@property
def is_table(self) -> bool:
    """Check if block is a table."""
    return self._block_type == "table"

@property
def is_column_list(self) -> bool:
    """Check if block is a column list."""
    return self._block_type == "column_list"

@property
def is_column(self) -> bool:
    """Check if block is a column."""
    return self._block_type == "column"

# Code blocks
@property
def is_code(self) -> bool:
    """Check if block is a code block."""
    return self._block_type == "code"

# Media blocks
@property
def is_image(self) -> bool:
    """Check if block is an image."""
    return self._block_type == "image"

@property
def is_video(self) -> bool:
    """Check if block is a video."""
    return self._block_type == "video"

@property
def is_file(self) -> bool:
    """Check if block is a file."""
    return self._block_type == "file"

@property
def is_pdf(self) -> bool:
    """Check if block is a PDF."""
    return self._block_type == "pdf"

@property
def is_bookmark(self) -> bool:
    """Check if block is a bookmark."""
    return self._block_type == "bookmark"

# Special blocks
@property
def is_child_page(self) -> bool:
    """Check if block contains a child page."""
    return self._block_type == "child_page"

@property
def is_child_database(self) -> bool:
    """Check if block contains a child database."""
    return self._block_type == "child_database"

@property
def is_embed(self) -> bool:
    """Check if block is an embed."""
    return self._block_type == "embed"

@property
def is_link_preview(self) -> bool:
    """Check if block is a link preview."""
    return self._block_type == "link_preview"
```

### Content Access

#### Text Content

```python
@property
def text(self) -> str:
    """Get text content for text-based blocks.

    Returns:
        Plain text content

    Supports:
        paragraph, heading_1/2/3, quote, callout,
        bulleted_list_item, numbered_list_item, to_do, toggle

    Example:
        >>> block.text
        'This is a paragraph with **bold** text'

    Note:
        Returns empty string for non-text blocks
    """
    if self._block_type in ("paragraph", "heading_1", "heading_2", "heading_3",
                            "quote", "callout", "bulleted_list_item",
                            "numbered_list_item", "to_do", "toggle"):
        rich_text_array = self._data.get(self._block_type, {}).get("rich_text", [])
        return self._extract_plain_text(rich_text_array)

    return ""

def _extract_plain_text(self, rich_text_array: list[dict]) -> str:
    """Extract plain text from rich text array.

    Args:
        rich_text_array: Rich text array from Notion API

    Returns:
        Plain text string
    """
    parts = []

    for text_obj in rich_text_array:
        if text_obj.get("type") == "text":
            content = text_obj["text"].get("content", "")

            # Add annotations
            annotations = text_obj.get("annotations", {})
            if annotations.get("code"):
                content = f"`{content}`"
            if annotations.get("bold"):
                content = f"**{content}**"
            if annotations.get("italic"):
                content = f"*{content}*"
            if annotations.get("strikethrough"):
                content = f"~~{content}~~"
            if annotations.get("underline"):
                content = f"__{content}__"

            parts.append(content)

    return "".join(parts)

@property
def rich_text(self) -> list[dict[str, Any]]:
    """Get rich text array for advanced processing.

    Returns:
        Rich text array with annotations

    Example:
        >>> for text_obj in block.rich_text:
        ...     if text_obj.get("annotations", {}).get("bold"):
        ...         print(f"Bold: {text_obj['text']['content']}")
    """
    if self._block_type in ("paragraph", "heading_1", "heading_2", "heading_3",
                            "quote", "callout", "bulleted_list_item",
                            "numbered_list_item", "to_do", "toggle"):
        return self._data.get(self._block_type, {}).get("rich_text", [])

    return []
```

#### Code Content

```python
@property
def code(self) -> str:
    """Get code from code block.

    Returns:
        Code content

    Example:
        >>> if block.is_code:
        ...     print(block.code)
    """
    if self._block_type == "code":
        rich_text_array = self._data.get("code", {}).get("rich_text", [])
        return self._extract_plain_text(rich_text_array)
    return ""

@property
def language(self) -> str:
    """Get programming language for code block.

    Returns:
        Language name (e.g., 'python', 'javascript')

    Example:
        >>> if block.is_code:
        ...     print(f"Language: {block.language}")
    """
    if self._block_type == "code":
        return self._data.get("code", {}).get("language", "")
    return ""
```

#### To-Do Items

```python
@property
def checked(self) -> bool:
    """Get checked state for to-do block.

    Returns:
        True if to-do is checked

    Example:
        >>> if block.is_to_do:
        ...     print(f"Done: {block.checked}")
    """
    if self._block_type == "to_do":
        return self._data.get("to_do", {}).get("checked", False)
    return False

async def set_checked(self, checked: bool = True) -> None:
    """Set checked state for to-do block.

    Args:
        checked: New checked state

    Example:
        >>> await block.set_checked(True)
    """
    if self._block_type == "to_do":
        await self.update(to_do={"checked": checked})
```

#### Callout Blocks

```python
@property
def icon(self) -> str | None:
    """Get icon for callout or other blocks with icons.

    Returns:
        Icon emoji or URL

    Example:
        >>> if block.is_callout:
        ...     print(f"Icon: {block.icon}")
    """
    # Callouts have icons
    if self._block_type == "callout":
        icon_data = self._data.get("callout", {}).get("icon")
        if icon_data and icon_data.get("type") == "emoji":
            return icon_data.get("emoji")

    return None

@property
def callout_color(self) -> str | None:
    """Get background color for callout.

    Returns:
        Color name (e.g., 'blue_background')

    Example:
        >>> if block.is_callout:
        ...     print(f"Color: {block.callout_color}")
    """
    if self._block_type == "callout":
        return self._data.get("callout", {}).get("color")
    return None
```

#### Media Blocks

```python
@property
def url(self) -> str | None:
    """Get URL for media/embed blocks.

    Returns:
        Media URL or embed URL

    Supports:
        image, video, file, pdf, bookmark, embed, link_preview

    Example:
        >>> if block.is_image:
        ...     print(f"Image URL: {block.url}")
    """
    block_data = self._data.get(self._block_type, {})

    # External URL
    if block_data.get("type") == "external":
        return block_data.get("external", {}).get("url")

    # File URL (expires)
    if block_data.get("type") == "file":
        return block_data.get("file", {}).get("url")

    # Bookmark/embed
    if "url" in block_data:
        return block_data.get("url")

    return None

@property
def caption(self) -> str:
    """Get caption for media blocks.

    Returns:
        Caption text

    Example:
        >>> if block.is_image:
        ...     print(f"Caption: {block.caption}")
    """
    if self._block_type in ("image", "video", "file", "pdf"):
        caption_array = self._data.get(self._block_type, {}).get("caption", [])
        return self._extract_plain_text(caption_array)
    return ""
```

#### Child Pages/Databases

```python
@property
def child_page_id(self) -> str | None:
    """Get child page ID for child_page blocks.

    Returns:
        Page ID or None

    Example:
        >>> if block.is_child_page:
        ...     page = await client.pages.get(block.child_page_id)
    """
    if self._block_type == "child_page":
        return self._data.get("child_page", "").get("id")
    return None

@property
def child_database_id(self) -> str | None:
    """Get child database ID for child_database blocks.

    Returns:
        Database ID or None

    Example:
        >>> if block.is_child_database:
        ...     db = await client.databases.get(block.child_database_id)
    """
    if self._block_type == "child_database":
        return self._data.get("child_database", "").get("id")
    return None
```

## Navigation

### Parent

```python
async def parent(self) -> Page | Block | None:
    """Get parent block or page.

    Returns:
        Parent Page or Block object, or None

    Example:
        >>> parent = await block.parent
        >>> if isinstance(parent, Page):
        ...     print(f"In page: {parent.title}")
    """
    # Check cache first
    cached_parent = self._cache_get("parent")
    if cached_parent:
        return cached_parent

    # Fetch from API
    parent_data = self._data.get("parent", {})

    if parent_data.get("type") == "page_id":
        page_id = parent_data["page_id"]
        data = await self._api._request("GET", f"/pages/{page_id}")
        from better_notion._sdk.models.page import Page
        parent = Page(self._api, data)

    elif parent_data.get("type") == "block_id":
        block_id = parent_data["block_id"]
        data = await self._api._request("GET", f"/blocks/{block_id}")
        parent = Block(self._api, data)

    elif parent_data.get("type") == "workspace":
        parent = None

    else:
        parent = None

    # Cache result
    if parent:
        self._cache_set("parent", parent)

    return parent

@property
def parent_cached(self) -> Page | Block | None:
    """Get parent from cache only (no fetch)."""
    return self._cache_get("parent")
```

### Children

```python
async def children(self) -> AsyncIterator[Block]:
    """Iterate over child blocks.

    Yields:
        Child Block objects

    Example:
        >>> async for child in block.children:
        ...     print(f"{child.type}: {child.text[:50]}")
    """
    from better_notion._api.utils import AsyncPaginatedIterator

    async def fetch_fn(cursor: str | None) -> dict:
        params = {}
        if cursor:
            params["start_cursor"] = cursor

        return await self._api._request(
            "GET",
            f"/blocks/{self.id}/children",
            params=params
        )

    iterator = AsyncPaginatedIterator(fetch_fn)

    async for block_data in iterator:
        yield Block(self._api, block_data)

async def get_children(self) -> list[Block]:
    """Get all children as list.

    Returns:
        List of child blocks

    Example:
        >>> children = await block.get_children()
        >>> print(f"Has {len(children)} children")
    """
    children = []
    async for child in self.children():
        children.append(child)
    return children
```

## CRUD Operations

### Update Block

```python
async def update(self, **kwargs) -> None:
    """Update block content.

    Args:
        **kwargs: Block-specific fields to update

    Example:
        >>> # Update paragraph text
        >>> await block.update(paragraph={"rich_text": [...]})

        >>> # Update to-do checked state
        >>> await block.update(to_do={"checked": True})

        >>> # Update code
        >>> await block.update(code={
        ...     "rich_text": [...],
        ...     "language": "python"
        ... })

    Note:
        Use builders from better_notion._sdk.builders for rich_text
    """
    # Call API
    data = await self._api._request(
        "PATCH",
        f"/blocks/{self.id}",
        json=kwargs
    )

    # Update internal data
    self._data.update(data)

    # Clear cache
    self._cache_clear()
```

### Delete Block

```python
async def delete(self) -> None:
    """Delete block (moves to trash).

    Example:
        >>> await block.delete()
    """
    await self._api._request("DELETE", f"/blocks/{self.id}")

    # Mark as archived
    self._data["archived"] = True
    self._cache_clear()
```

## SDK-Exclusive Methods

### Content Search

```python
def contains_text(self, search_term: str) -> bool:
    """Check if block text contains search term.

    Args:
        search_term: Text to search for

    Returns:
        True if search term found in block text

    Example:
        >>> if block.contains_text("important"):
        ...     print("Found important text")
    """
    return search_term.lower() in self.text.lower()

def get_links(self) -> list[str]:
    """Extract all URLs from block.

    Returns:
        List of URLs found in block

    Example:
        >>> urls = block.get_links()
        >>> for url in urls:
        ...     print(f"Link: {url}")
    """
    urls = []

    for text_obj in self.rich_text:
        if text_obj.get("type") == "text":
            link = text_obj["text"].get("link")
            if link and "url" in link:
                urls.append(link["url"])

    return urls
```

### Table Helpers

```python
async def get_table_rows(self) -> list[Block]:
    """Get all rows from a table block.

    Returns:
        List of table_row blocks

    Raises:
        ValueError: If block is not a table

    Example:
        >>> if block.is_table:
        ...     rows = await block.get_table_rows()
        ...     print(f"Table has {len(rows)} rows")
    """
    if not self.is_table:
        raise ValueError("Block is not a table")

    rows = []
    async for child in self.children():
        if child.type == "table_row":
            rows.append(child)

    return rows
```

### Transformations

```python
def to_markdown(self) -> str:
    """Convert block to Markdown.

    Returns:
        Markdown representation

    Example:
        >>> markdown = block.to_markdown()
        >>> print(markdown)
    """
    if self.is_paragraph:
        return self.text + "\n"

    elif self.is_heading_1:
        return f"# {self.text}\n"
    elif self.is_heading_2:
        return f"## {self.text}\n"
    elif self.is_heading_3:
        return f"### {self.text}\n"

    elif self.is_bulleted_list_item:
        return f"- {self.text}\n"
    elif self.is_numbered_list_item:
        return f"1. {self.text}\n"

    elif self.is_to_do:
        checkbox = "[x]" if self.checked else "[ ]"
        return f"{checkbox} {self.text}\n"

    elif self.is_quote:
        return f"> {self.text}\n"

    elif self.is_code:
        return f"```{self.language}\n{self.code}\n```\n"

    elif self.is_divider:
        return "---\n"

    elif self.is_image:
        return f"![Image]({self.url})\n"

    else:
        # Fallback
        return self.text + "\n"

async def descendants_to_markdown(self) -> str:
    """Convert block and all descendants to Markdown.

    Returns:
        Full Markdown document

    Example:
        >>> markdown = await block.descendants_to_markdown()
        >>> with open("output.md", "w") as f:
        ...     f.write(markdown)
    """
    lines = []

    async for descendant in self.descendants():
        lines.append(descendant.to_markdown())

    return "".join(lines)
```

## Usage Examples

### Example 1: Extract All Code Blocks

```python
async def extract_code(page: Page) -> list[tuple[str, str, str]]:
    """Extract all code blocks from a page.

    Args:
        page: Page to extract from

    Returns:
        List of (language, code, url) tuples
    """
    code_blocks = []

    async for block in page.descendants():
        if block.is_code:
            code_blocks.append((
                block.language,
                block.code,
                f"https://notion.so/{block.id.replace('-', '')}"
            ))

    return code_blocks
```

### Example 2: Convert Page to Markdown

```python
async def page_to_markdown(page: Page) -> str:
    """Convert entire page to Markdown.

    Args:
        page: Page to convert

    Returns:
        Markdown string
    """
    lines = [f"# {page.title}\n\n"]

    async for block in page.children:
        lines.append(await block.descendants_to_markdown())

    return "".join(lines)
```

### Example 3: Find All Images

```python
async def find_images(page: Page) -> list[str]:
    """Find all image URLs in page.

    Args:
        page: Page to search

    Returns:
        List of image URLs
    """
    images = []

    async for block in page.descendants():
        if block.is_image:
            url = block.url
            if url:
                images.append(url)

    return images
```

### Example 4: Table Processing

```python
async def process_table(block: Block) -> list[dict[str, str]]:
    """Extract table data.

    Args:
        block: Table block

    Returns:
        List of row dicts
    """
    if not block.is_table:
        raise ValueError("Not a table block")

    rows = []
    async for row_block in block.children:
        if row_block.type == "table_row":
            # Extract cells from table_row
            cells = row_block._data.get("table_row", {}).get("cells", [])
            rows.append({"cells": cells})

    return rows
```

## Design Decisions

### Q1: Should text return str or list[dict]?

**Decision**: `text` returns plain `str`, `rich_text` returns list[dict]

**Rationale**:
- Most use cases just need plain text
- Rich text array is available for advanced use cases
- Consistent with Notion's conceptual model

```python
# Simple
print(block.text)  # "Hello **world**"

# Advanced
for text_obj in block.rich_text:
    if text_obj["annotations"]["bold"]:
        print(f"Bold: {text_obj['text']['content']}")
```

### Q2: Separate is_* for each heading level?

**Decision**: Yes, specific is_heading_1/2/3 + generic is_heading

**Rationale**:
- Generic `is_heading` covers "any heading"
- Specific `is_heading_1/2/3` for level-specific logic
- Matches Notion's type system

```python
if block.is_heading:
    print(f"Heading: {block.text}")

if block.is_heading_1:
    # Top-level heading
    pass
```

### Q3: Include to_markdown() in SDK?

**Decision**: Yes, basic Markdown export

**Rationale**:
- Common use case (export, conversion)
- Simple implementation
- Not full fidelity (Notion → Markdown loses some features)
- Users can extend for custom formats

### Q4: URL property for all blocks?

**Decision**: Yes, but returns None for non-media blocks

**Rationale**:
- Cleaner API than separate methods
- Consistent interface
- None is clear signal

```python
# Works for media
url = block.url  # Returns URL for image, video, etc.

# Returns None for others
url = paragraph.url  # None
```

## Type Safety

### Type Guards

```python
# Use type guards for narrowed types
if block.is_code:
    # Type checker knows block is code block
    lang = block.language
    code = block.code
```

### Content Type Inference

```python
# Type checker can infer
if block.is_heading_1:
    text: str = block.text  # str
else:
    text: str = block.text  # still str
```

## Error Handling

### Wrong Block Type

```python
# Graceful degradation
code = block.code  # Returns "" for non-code blocks

# Explicit check
if block.is_code:
    print(f"Language: {block.language}")
else:
    print("Not a code block")
```

### Missing Children

```python
# Safe iteration
async for child in block.children:
    print(child.type)

# If has_children is False, children() yields nothing
```

## Next Steps

After Block model:

1. **User Model** - User with profile information
2. **Managers** - High-level managers that use these models

## Related Documentation

- [BaseEntity](../implementation/base-entity.md) - Foundation class
- [Navigation](../implementation/navigation.md) - Hierarchical traversal
- [Page Model](./page-model.md) - Pages contain blocks
- [Property Parsers](../implementation/property-parsers.md) - Text extraction
