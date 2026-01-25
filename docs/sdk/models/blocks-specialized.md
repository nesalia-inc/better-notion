# Block Specialized Classes

Type-safe block classes with specific methods for each Notion block type.

## Overview

Instead of a generic `Block` class with type flags, we use specialized classes: `Paragraph`, `Code`, `Todo`, `Heading`, etc. Each class has:
- Type-specific properties
- Type-specific methods
- Its own `create()` method

## Architecture

### Class Hierarchy

```
BaseEntity
└── Block (ABC)
    ├── Paragraph
    ├── Heading
    │   ├── (level 1, 2, 3)
    ├── Code
    ├── Todo
    ├── BulletedListItem
    ├── NumberedListItem
    ├── Image
    ├── Callout
    ├── Quote
    ├── Toggle
    ├── Divider
    └── GenericBlock (fallback)
```

### Base Block Class

```python
from abc import ABC, abstractmethod
from typing import AsyncIterator

class Block(BaseEntity, ABC):
    """Base class for all specialized block types."""

    @classmethod
    def from_data(cls, client: NotionClient, data: dict) -> Block:
        """Factory to create correct block type from API data.

        Used internally when loading blocks from Notion.

        Example:
            >>> block = Block.from_data(client, api_response)
            >>> # Returns Paragraph, Code, Todo, etc.
        """
        block_type = data.get("type")

        dispatch = {
            "paragraph": Paragraph,
            "code": Code,
            "heading_1": Heading,
            "heading_2": Heading,
            "heading_3": Heading,
            "image": Image,
            "to_do": Todo,
            "bulleted_list_item": BulletedListItem,
            "numbered_list_item": NumberedListItem,
            "callout": Callout,
            "quote": Quote,
            "toggle": Toggle,
            "divider": Divider,
        }

        block_class = dispatch.get(block_type, GenericBlock)
        return block_class(client, data)

    @classmethod
    async def get(cls, id: str, client: NotionClient) -> Block:
        """Load block from Notion.

        Example:
            >>> block = await Block.get(block_id, client=client)
            >>> if isinstance(block, Code):
            ...     print(block.code)
        """
        data = await client._api._request("GET", f"/blocks/{id}")
        return cls.from_data(client, data)

    @property
    def type(self) -> str:
        """Block type string."""
        return self._data.get("type", "")

    @property
    def has_children(self) -> bool:
        """Does this block have children?"""
        return self._data.get("has_children", False)

    @property
    def archived(self) -> bool:
        """Is block archived?"""
        return self._data.get("archived", False)

    async def parent(self) -> Page | Block | None:
        """Get parent block or page."""
        cached = self._cache_get("parent")
        if cached:
            return cached

        parent_data = self._data.get("parent", {})

        if parent_data.get("type") == "page_id":
            page_id = parent_data["page_id"]
            data = await self._client._api._request("GET", f"/pages/{page_id}")
            parent = Page(self._client, data)
        elif parent_data.get("type") == "block_id":
            block_id = parent_data["block_id"]
            data = await self._client._api._request("GET", f"/blocks/{block_id}")
            parent = Block.from_data(self._client, data)
        else:
            parent = None

        if parent:
            self._cache_set("parent", parent)

        return parent

    async def children(self) -> AsyncIterator[Block]:
        """Iterate child blocks.

        Example:
            >>> async for child in block.children:
            ...     print(child.type)
        """
        from better_notion._api.utils import AsyncPaginatedIterator

        async def fetch_fn(cursor: str | None) -> dict:
            params = {}
            if cursor:
                params["start_cursor"] = cursor
            return await self._client._api._request(
                "GET",
                f"/blocks/{self.id}/children",
                params=params
            )

        iterator = AsyncPaginatedIterator(fetch_fn)
        async for block_data in iterator:
            yield Block.from_data(self._client, block_data)

    async def delete(self, client: NotionClient) -> None:
        """Delete this block.

        Example:
            >>> await block.delete(client=client)
        """
        await client._api._request("DELETE", f"/blocks/{self.id}")
        self._data["archived"] = True
        self._cache_clear()

    def _extract_plain_text(self, rich_text_array: list[dict]) -> str:
        """Extract plain text from rich text array."""
        parts = []
        for text_obj in rich_text_array:
            if text_obj.get("type") == "text":
                parts.append(text_obj["text"].get("content", ""))
        return "".join(parts)
```

## Text Blocks

### Paragraph

```python
class Paragraph(Block):
    """A paragraph block."""

    @classmethod
    async def create(
        cls,
        parent: Page | Block,
        text: str,
        client: NotionClient
    ) -> "Paragraph":
        """Create a new paragraph.

        Example:
            >>> para = await Paragraph.create(
            ...     parent=page,
            ...     text="Hello world",
            ...     client=client
            ... )
        """
        from better_notion._api.blocks import ParagraphBlock as APIParagraph

        api_block = APIParagraph(text=text)
        data = await client._api.blocks.children.append(
            parent.id,
            children=[api_block]
        )
        return cls(client, data)

    @property
    def text(self) -> str:
        """Plain text content.

        Example:
            >>> print(paragraph.text)
        """
        rich_text = self._data.get("paragraph", {}).get("rich_text", [])
        return self._extract_plain_text(rich_text)

    @property
    def rich_text(self) -> list[dict]:
        """Rich text array with annotations.

        Example:
            >>> for text_obj in paragraph.rich_text:
            ...     if text_obj.get("annotations", {}).get("bold"):
            ...         print(f"Bold: {text_obj['text']['content']}")
        """
        return self._data.get("paragraph", {}).get("rich_text", [])

    async def set_text(self, new_text: str, client: NotionClient) -> None:
        """Change the text.

        Example:
            >>> await paragraph.set_text("New text", client=client)
        """
        await self.update(
            client=client,
            paragraph={"rich_text": [{"type": "text", "text": {"content": new_text}}]}
        )

    async def update(self, client: NotionClient, **kwargs) -> None:
        """Update the block."""
        data = await client._api._request(
            "PATCH",
            f"/blocks/{self.id}",
            json=kwargs
        )
        self._data.update(data)
        self._cache_clear()
```

### Heading

```python
class Heading(Block):
    """A heading block (H1, H2, or H3)."""

    def __init__(self, client: NotionClient, data: dict):
        super().__init__(client, data)
        # Extract level from type: "heading_1" -> 1
        self._level = int(data.get("type", "heading_1").split("_")[1])

    @classmethod
    async def create(
        cls,
        parent: Page | Block,
        text: str,
        level: int = 1,
        client: NotionClient
    ) -> "Heading":
        """Create a new heading.

        Args:
            parent: Parent page or block
            text: Heading text
            level: Heading level (1, 2, or 3)
            client: Notion client

        Example:
            >>> h1 = await Heading.create(
            ...     parent=page,
            ...     text="Chapter 1",
            ...     level=1,
            ...     client=client
            ... )
            >>> h2 = await Heading.create(
            ...     parent=page,
            ...     text="Section 1.1",
            ...     level=2,
            ...     client=client
            ... )
        """
        from better_notion._api.blocks import HeadingBlock as APIHeading

        api_block = APIHeading(text=text, level=level)
        data = await client._api.blocks.children.append(
            parent.id,
            children=[api_block]
        )
        return cls(client, data)

    @property
    def level(self) -> int:
        """Heading level (1, 2, or 3).

        Example:
            >>> if heading.level == 1:
            ...     print(f"# {heading.text}")
        """
        return self._level

    @property
    def is_h1(self) -> bool:
        """Is this an H1?"""
        return self._level == 1

    @property
    def is_h2(self) -> bool:
        """Is this an H2?"""
        return self._level == 2

    @property
    def is_h3(self) -> bool:
        """Is this an H3?"""
        return self._level == 3

    @property
    def text(self) -> str:
        """Heading text.

        Example:
            >>> print(heading.text)
        """
        rich_text = self._data.get(f"heading_{self._level}", {}).get("rich_text", [])
        return self._extract_plain_text(rich_text)

    async def set_text(self, new_text: str, client: NotionClient) -> None:
        """Change the heading text."""
        await self.update(
            client=client,
            **{f"heading_{self._level}": {"rich_text": [{"type": "text", "text": {"content": new_text}}]}}
        )

    async def update(self, client: NotionClient, **kwargs) -> None:
        """Update the block."""
        data = await client._api._request(
            "PATCH",
            f"/blocks/{self.id}",
            json=kwargs
        )
        self._data.update(data)
        self._cache_clear()
```

### Code

```python
class Code(Block):
    """A code block."""

    @classmethod
    async def create(
        cls,
        parent: Page | Block,
        code: str,
        language: str = "python",
        caption: str = "",
        client: NotionClient
    ) -> "Code":
        """Create a new code block.

        Args:
            parent: Parent page or block
            code: Source code
            language: Programming language (python, javascript, etc.)
            caption: Optional caption
            client: Notion client

        Example:
            >>> code = await Code.create(
            ...     parent=page,
            ...     code="print('Hello')",
            ...     language="python",
            ...     client=client
            ... )
        """
        from better_notion._api.blocks import CodeBlock as APICode

        api_block = APICode(code=code, language=language, caption=caption)
        data = await client._api.blocks.children.append(
            parent.id,
            children=[api_block]
        )
        return cls(client, data)

    @property
    def code(self) -> str:
        """Source code content.

        Example:
            >>> print(code_block.code)
        """
        rich_text = self._data.get("code", {}).get("rich_text", [])
        return self._extract_plain_text(rich_text)

    @property
    def language(self) -> str:
        """Programming language.

        Example:
            >>> print(f"Language: {code_block.language}")
        """
        return self._data.get("code", {}).get("language", "")

    @property
    def caption(self) -> str:
        """Code caption.

        Example:
            >>> if code.caption:
            ...     print(f"Caption: {code.caption}")
        """
        caption_array = self._data.get("code", {}).get("caption", [])
        return self._extract_plain_text(caption_array)

    async def set_code(self, new_code: str, client: NotionClient) -> None:
        """Change the code content.

        Example:
            >>> await code.set_code("new code", client=client)
        """
        await self.update(
            client=client,
            code={
                "rich_text": [{"type": "text", "text": {"content": new_code}}],
                "language": self.language,
                "caption": self._data.get("code", {}).get("caption", [])
            }
        )

    async def set_language(self, new_language: str, client: NotionClient) -> None:
        """Change the programming language.

        Example:
            >>> await code.set_language("javascript", client=client)
        """
        await self.update(
            client=client,
            code={
                "rich_text": self._data.get("code", {}).get("rich_text", []),
                "language": new_language,
                "caption": self._data.get("code", {}).get("caption", [])
            }
        )

    async def update(self, client: NotionClient, **kwargs) -> None:
        """Update the block."""
        data = await client._api._request(
            "PATCH",
            f"/blocks/{self.id}",
            json=kwargs
        )
        self._data.update(data)
        self._cache_clear()
```

## List Blocks

### Todo

```python
class Todo(Block):
    """A to-do item (checkbox)."""

    @classmethod
    async def create(
        cls,
        parent: Page | Block,
        text: str,
        checked: bool = False,
        client: NotionClient
    ) -> "Todo":
        """Create a new to-do item.

        Args:
            parent: Parent page or block
            text: Todo text
            checked: Initial checked state
            client: Notion client

        Example:
            >>> todo = await Todo.create(
            ...     parent=page,
            ...     text="Review PR",
            ...     checked=False,
            ...     client=client
            ... )
            >>> await todo.check(client=client)
        """
        from better_notion._api.blocks import TodoBlock as APITodo

        api_block = APITodo(text=text, checked=checked)
        data = await client._api.blocks.children.append(
            parent.id,
            children=[api_block]
        )
        return cls(client, data)

    @property
    def text(self) -> str:
        """Todo text.

        Example:
            >>> print(todo.text)
        """
        rich_text = self._data.get("to_do", {}).get("rich_text", [])
        return self._extract_plain_text(rich_text)

    @property
    def checked(self) -> bool:
        """Is the todo checked?

        Example:
            >>> if not todo.checked:
            ...     print(f"Need to do: {todo.text}")
        """
        return self._data.get("to_do", {}).get("checked", False)

    @property
    def is_done(self) -> bool:
        """Alias for checked."""
        return self.checked

    async def check(self, client: NotionClient) -> None:
        """Check the todo.

        Example:
            >>> await todo.check(client=client)
            >>> assert todo.checked == True
        """
        await self.update(
            client=client,
            to_do={
                "checked": True,
                "rich_text": self._data.get("to_do", {}).get("rich_text", [])
            }
        )

    async def uncheck(self, client: NotionClient) -> None:
        """Uncheck the todo.

        Example:
            >>> await todo.uncheck(client=client)
            >>> assert todo.checked == False
        """
        await self.update(
            client=client,
            to_do={
                "checked": False,
                "rich_text": self._data.get("to_do", {}).get("rich_text", [])
            }
        )

    async def toggle(self, client: NotionClient) -> None:
        """Toggle the checked state.

        Example:
            >>> await todo.toggle(client=client)
        """
        await self.update(
            client=client,
            to_do={
                "checked": not self.checked,
                "rich_text": self._data.get("to_do", {}).get("rich_text", [])
            }
        )

    async def update(self, client: NotionClient, **kwargs) -> None:
        """Update the block."""
        data = await client._api._request(
            "PATCH",
            f"/blocks/{self.id}",
            json=kwargs
        )
        self._data.update(data)
        self._cache_clear()
```

### BulletedListItem

```python
class BulletedListItem(Block):
    """A bulleted list item."""

    @classmethod
    async def create(
        cls,
        parent: Page | Block,
        text: str,
        client: NotionClient
    ) -> "BulletedListItem":
        """Create a new bulleted list item.

        Example:
            >>> item = await BulletedListItem.create(
            ...     parent=page,
            ...     text="First item",
            ...     client=client
            ... )
        """
        from better_notion._api.blocks import BulletedListItemBlock as APIBlock

        api_block = APIBlock(text=text)
        data = await client._api.blocks.children.append(
            parent.id,
            children=[api_block]
        )
        return cls(client, data)

    @property
    def text(self) -> str:
        """Item text."""
        rich_text = self._data.get("bulleted_list_item", {}).get("rich_text", [])
        return self._extract_plain_text(rich_text)
```

### NumberedListItem

```python
class NumberedListItem(Block):
    """A numbered list item."""

    @classmethod
    async def create(
        cls,
        parent: Page | Block,
        text: str,
        client: NotionClient
    ) -> "NumberedListItem":
        """Create a new numbered list item.

        Example:
            >>> item = await NumberedListItem.create(
            ...     parent=page,
            ...     text="First item",
            ...     client=client
            ... )
        """
        from better_notion._api.blocks import NumberedListItemBlock as APIBlock

        api_block = APIBlock(text=text)
        data = await client._api.blocks.children.append(
            parent.id,
            children=[api_block]
        )
        return cls(client, data)

    @property
    def text(self) -> str:
        """Item text."""
        rich_text = self._data.get("numbered_list_item", {}).get("rich_text", [])
        return self._extract_plain_text(rich_text)

    @property
    def number(self) -> int | None:
        """Item number (if available).

        Example:
            >>> if item.number:
            ...     print(f"{item.number}. {item.text}")
        """
        return self._data.get("numbered_list_item", {}).get("number")
```

## Media Blocks

### Image

```python
class Image(Block):
    """An image block."""

    @classmethod
    async def create(
        cls,
        parent: Page | Block,
        url: str,
        caption: str = "",
        client: NotionClient
    ) -> "Image":
        """Create a new image block.

        Args:
            parent: Parent page or block
            url: Image URL
            caption: Optional caption
            client: Notion client

        Example:
            >>> img = await Image.create(
            ...     parent=page,
            ...     url="https://example.com/image.png",
            ...     caption="Figure 1",
            ...     client=client
            ... )
        """
        from better_notion._api.blocks import ImageBlock as APIImage

        api_block = APIImage(url=url, caption=caption)
        data = await client._api.blocks.children.append(
            parent.id,
            children=[api_block]
        )
        return cls(client, data)

    @property
    def url(self) -> str | None:
        """Image URL.

        Example:
            >>> if image.url:
            ...     print(f"Image: {image.url}")
        """
        image_data = self._data.get("image", {})
        if image_data.get("type") == "external":
            return image_data.get("external", {}).get("url")
        elif image_data.get("type") == "file":
            return image_data.get("file", {}).get("url")
        return None

    @property
    def caption(self) -> str:
        """Image caption.

        Example:
            >>> print(image.caption)
        """
        caption_array = self._data.get("image", {}).get("caption", [])
        return self._extract_plain_text(caption_array)

    async def set_url(self, new_url: str, client: NotionClient) -> None:
        """Change the image URL.

        Example:
            >>> await image.set_url("https://example.com/new.png", client=client)
        """
        await self.update(
            client=client,
            image={"type": "external", "external": {"url": new_url}}
        )

    async def update(self, client: NotionClient, **kwargs) -> None:
        """Update the block."""
        data = await client._api._request(
            "PATCH",
            f"/blocks/{self.id}",
            json=kwargs
        )
        self._data.update(data)
        self._cache_clear()
```

## Other Block Types

### Callout

```python
class Callout(Block):
    """A callout block (highlighted box)."""

    @classmethod
    async def create(
        cls,
        parent: Page | Block,
        text: str,
        icon: str | None = None,
        client: NotionClient
    ) -> "Callout":
        """Create a new callout.

        Args:
            parent: Parent page or block
            text: Callout text
            icon: Optional emoji icon
            client: Notion client

        Example:
            >>> callout = await Callout.create(
            ...     parent=page,
            ...     text="Important note!",
            ...     icon="⚠️",
            ...     client=client
            ... )
        """
        from better_notion._api.blocks import CalloutBlock as APICallout

        api_block = APICallout(text=text, icon=icon)
        data = await client._api.blocks.children.append(
            parent.id,
            children=[api_block]
        )
        return cls(client, data)

    @property
    def text(self) -> str:
        """Callout text."""
        rich_text = self._data.get("callout", {}).get("rich_text", [])
        return self._extract_plain_text(rich_text)

    @property
    def icon(self) -> str | None:
        """Emoji icon.

        Example:
            >>> if callout.icon:
            ...     print(f"{callout.icon} {callout.text}")
        """
        icon_data = self._data.get("callout", {}).get("icon")
        if icon_data and icon_data.get("type") == "emoji":
            return icon_data.get("emoji")
        return None

    @property
    def color(self) -> str | None:
        """Background color.

        Example:
            >>> print(f"Color: {callout.color}")
        """
        return self._data.get("callout", {}).get("color")
```

### Quote

```python
class Quote(Block):
    """A quote block."""

    @classmethod
    async def create(
        cls,
        parent: Page | Block,
        text: str,
        client: NotionClient
    ) -> "Quote":
        """Create a new quote.

        Example:
            >>> quote = await Quote.create(
            ...     parent=page,
            ...     text="To be or not to be",
            ...     client=client
            ... )
        """
        from better_notion._api.blocks import QuoteBlock as APIQuote

        api_block = APIQuote(text=text)
        data = await client._api.blocks.children.append(
            parent.id,
            children=[api_block]
        )
        return cls(client, data)

    @property
    def text(self) -> str:
        """Quote text."""
        rich_text = self._data.get("quote", {}).get("rich_text", [])
        return self._extract_plain_text(rich_text)
```

### Toggle

```python
class Toggle(Block):
    """A toggle block (collapsible)."""

    @classmethod
    async def create(
        cls,
        parent: Page | Block,
        text: str,
        client: NotionClient
    ) -> "Toggle":
        """Create a new toggle.

        Example:
            >>> toggle = await Toggle.create(
            ...     parent=page,
            ...     text="Click to expand",
            ...     client=client
            ... )
        """
        from better_notion._api.blocks import ToggleBlock as APIToggle

        api_block = APIToggle(text=text)
        data = await client._api.blocks.children.append(
            parent.id,
            children=[api_block]
        )
        return cls(client, data)

    @property
    def text(self) -> str:
        """Toggle text."""
        rich_text = self._data.get("toggle", {}).get("rich_text", [])
        return self._extract_plain_text(rich_text)
```

### Divider

```python
class Divider(Block):
    """A divider (horizontal rule)."""

    @classmethod
    async def create(
        cls,
        parent: Page | Block,
        client: NotionClient
    ) -> "Divider":
        """Create a new divider.

        Example:
            >>> divider = await Divider.create(parent=page, client=client)
        """
        from better_notion._api.blocks import DividerBlock as APIDivider

        api_block = APIDivider()
        data = await client._api.blocks.children.append(
            parent.id,
            children=[api_block]
        )
        return cls(client, data)
```

## Fallback Block

### GenericBlock

```python
class GenericBlock(Block):
    """Fallback for unknown block types."""

    @property
    def text(self) -> str:
        """Try to extract text (may return empty string)."""
        return ""

    @property
    def raw_data(self) -> dict:
        """Access raw block data.

        Example:
            >>> data = generic_block.raw_data
            >>> print(f"Unknown type: {data.get('type')}")
        """
        return self._data
```

## Usage Examples

### Creating Different Block Types

```python
page = await Page.get(page_id, client=client)

# Text blocks
para = await Paragraph.create(parent=page, text="Introduction", client=client)
h1 = await Heading.create(parent=page, text="Chapter 1", level=1, client=client)
h2 = await Heading.create(parent=page, text="Section 1", level=2, client=client)

# Code
code = await Code.create(
    parent=page,
    code="def hello():\n    print('Hello')",
    language="python",
    client=client
)

# Lists
todo = await Todo.create(parent=page, text="Fix bug", checked=False, client=client)
bullet = await BulletedListItem.create(parent=page, text="Item 1", client=client)
numbered = await NumberedListItem.create(parent=page, text="Step 1", client=client)

# Media
img = await Image.create(
    parent=page,
    url="https://example.com/diagram.png",
    caption="Architecture",
    client=client
)

# Other
callout = await Callout.create(
    parent=page,
    text="Important!",
    icon="⚠️",
    client=client
)
quote = await Quote.create(parent=page, text="Quote here", client=client)
divider = await Divider.create(parent=page, client=client)
```

### Type-Safe Operations

```python
page = await Page.get(page_id, client=client)

async for block in page.children:
    if isinstance(block, Todo):
        # Type-safe: block is Todo here
        if not block.checked:
            print(f"Todo: {block.text}")
            await block.check(client=client)

    elif isinstance(block, Code):
        # Type-safe: block is Code here
        print(f"Code ({block.language}):")
        print(f"  {block.code[:50]}...")

    elif isinstance(block, Heading):
        # Type-safe: block is Heading here
        indent = "#" * block.level
        print(f"{indent} {block.text}")

    elif isinstance(block, Paragraph):
        # Type-safe: block is Paragraph here
        print(block.text)

    elif isinstance(block, Image):
        # Type-safe: block is Image here
        print(f"[Image: {block.url}]")
        if block.caption:
            print(f"  {block.caption}")
```

### Specialized Iterators on Page

```python
class Page(BaseEntity):
    """..."""

    async def todos(self) -> AsyncIterator[Todo]:
        """Iterate only todo items.

        Example:
            >>> async for todo in page.todos():
            ...     if not todo.checked:
            ...         print(todo.text)
        """
        async for block in self.children:
            if isinstance(block, Todo):
                yield block

    async def code_blocks(self) -> AsyncIterator[Code]:
        """Iterate only code blocks.

        Example:
            >>> async for code in page.code_blocks():
            ...     print(f"{code.language}: {code.code[:30]}")
        """
        async for block in self.children:
            if isinstance(block, Code):
                yield block

    async def headings(self, level: int | None = None) -> AsyncIterator[Heading]:
        """Iterate only headings.

        Args:
            level: Optional level filter (1, 2, or 3)

        Example:
            >>> async for h1 in page.headings(level=1):
            ...     print(f"# {h1.text}")
        """
        async for block in self.children:
            if isinstance(block, Heading):
                if level is None or block.level == level:
                    yield block
```

### Working with Todo Checkboxes

```python
page = await Page.get(page_id, client=client)

# Check all unchecked todos
async for todo in page.todos():
    if not todo.checked:
        print(f"Checking: {todo.text}")
        await todo.check(client=client)

# Toggle a specific todo
todo = await Todo.create(
    parent=page,
    text="Review changes",
    checked=False,
    client=client
)
print(f"Initial: {todo.checked}")  # False

await todo.toggle(client=client)
print(f"After toggle: {todo.checked}")  # True

await todo.toggle(client=client)
print(f"After toggle: {todo.checked}")  # False
```

### Code Block Manipulation

```python
# Create code block
code = await Code.create(
    parent=page,
    code="x = 1",
    language="python",
    client=client
)

# Change code content
await code.set_code("x = 2", client=client)

# Change language
await code.set_language("javascript", client=client)

# Read back
print(f"{code.language}: {code.code}")
# Output: javascript: x = 2
```

## Type Safety Benefits

### Before (Generic Block)

```python
# Type checker doesn't know block type
async for block in page.children:
    if block.type == "code":
        print(block.code)  # ❌ Type error: Block has no attribute 'code'
        print(block.language)  # ❌ Type error
```

### After (Specialized Classes)

```python
# Type checker knows block type
async for block in page.children:
    if isinstance(block, Code):
        print(block.code)  # ✅ Type-safe
        print(block.language)  # ✅ Type-safe
```

## Design Decisions

### Q1: Should update methods take `client` parameter?

**Decision**: Yes, explicit `client` parameter

**Rationale**:
- Clear that this requires API call
- Could use stored `self._client` in future
- Explicit is better than implicit

```python
# Current (chosen)
await todo.check(client=client)

# Alternative (use stored client)
async def check(self) -> None:
    await self._client._api._request(...)
```

### Q2: Should specialized blocks inherit from Block?

**Decision**: Yes, all inherit from Block

**Rationale**:
- Shared navigation methods (parent, children, ancestors, descendants)
- Polymorphism via `isinstance()`
- Can still add type-specific methods

### Q3: Should create() be classmethod or staticmethod?

**Decision**: classmethod

**Rationale**:
- Returns instance of cls
- Supports inheritance
- Can be overridden if needed

## Related Documentation

- [Entity-Oriented Architecture](../implementation/entity-oriented-architecture.md) - Overall architecture
- [BaseEntity](../implementation/base-entity.md) - Foundation class
- [Page Model](./page-model.md) - Page entity
- [Navigation](../implementation/navigation.md) - Hierarchical traversal
