# BlockManager

Ultra-thin wrapper to autonomous Block classes.

## Overview

`BlockManager` is a **zero-logic wrapper** that delegates all operations to autonomous block classes. Unlike other managers, it handles multiple specialized block types (Code, Todo, Paragraph, etc.).

**Key Principle**: Managers provide syntactic sugar. Entities contain all logic.

```python
# Via Manager (recommended - shorter)
block = await client.blocks.get(block_id)
code = await client.blocks.create_code(page, code="print('hi')")

# Via Entity directly (autonomous - same result)
block = await Block.get(block_id, client=client)
code = await Code.create(parent=page, code="print('hi')", client=client)
```

## Architecture

```
NotionClient
    └── blocks: BlockManager
              └── delegates to → Block subclasses (autonomous)
                  ├── Code
                  ├── Todo
                  ├── Paragraph
                  ├── Heading
                  └── ... (specialized types)
```

## Specialized Block Types

The SDK uses **specialized classes** instead of a generic `Block` class:

```python
# ✅ Specialized classes
code = await client.blocks.create_code(page, code="...")
todo = await client.blocks.create_todo(page, text="Task", checked=False)

# ❌ No generic create_block()
block = await client.blocks.create_block(type="code", ...)  # Doesn't exist
```

**Benefits**:
- Type-safe: Each class has specific methods
- IDE autocomplete: `code.language`, `todo.checked`
- Clear intent: `create_code()` vs `create_block(type="code")`

## Implementation

```python
# better_notion/_sdk/managers/block_manager.py

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from better_notion._sdk.client import NotionClient
    from better_notion._sdk.models.block import Block

class BlockManager:
    """Ultra-thin wrapper to autonomous block classes.

    All methods delegate to specialized block classes.
    The manager only stores and passes the client reference.

    Example:
        >>> # Via manager (recommended)
        >>> block = await client.blocks.get(block_id)
        >>> code = await client.blocks.create_code(page, code="print('hi')")
        >>>
        >>> # Via entity directly (autonomous)
        >>> block = await Block.get(block_id, client=client)
        >>> code = await Code.create(parent=page, code="...", client=client)
    """

    def __init__(self, client: "NotionClient") -> None:
        """Initialize block manager.

        Args:
            client: NotionClient instance
        """
        self._client = client

    # ===== GENERIC OPERATIONS =====

    async def get(self, block_id: str) -> "Block":
        """Get block by ID (returns specialized instance).

        Args:
            block_id: Block UUID

        Returns:
            Specialized block object (Code, Todo, Paragraph, etc.)

        Raises:
            BlockNotFound: If block doesn't exist

        Example:
            >>> block = await client.blocks.get(block_id)
            >>> if block.type == "code":
            ...     print(block.code)  # Type-specific access
        """
        from better_notion._sdk.models.block import Block

        return await Block.get(block_id, client=self._client)

    async def delete(self, block: "Block") -> None:
        """Delete a block.

        Args:
            block: Block object to delete

        Example:
            >>> block = await client.blocks.get(block_id)
            >>> await client.blocks.delete(block)
        """
        await block.delete(client=self._client)

    # ===== CODE BLOCKS =====

    async def create_code(
        self,
        parent: "Page | Block",
        code: str,
        language: str = "python",
        **kwargs
    ) -> "Code":
        """Create a code block.

        Args:
            parent: Parent page or block
            code: Code content
            language: Programming language (python, javascript, etc.)
            **kwargs: Additional properties

        Returns:
            Code block object

        Example:
            >>> code = await client.blocks.create_code(
            ...     parent=page,
            ...     code="print('Hello, World!')",
            ...     language="python"
            ... )
            >>> print(code.code)
        """
        from better_notion._sdk.models.blocks.code import Code

        return await Code.create(
            parent=parent,
            code=code,
            language=language,
            client=self._client,
            **kwargs
        )

    # ===== TODO BLOCKS =====

    async def create_todo(
        self,
        parent: "Page | Block",
        text: str,
        checked: bool = False,
        **kwargs
    ) -> "Todo":
        """Create a to-do block.

        Args:
            parent: Parent page or block
            text: Todo text
            checked: Whether todo is checked
            **kwargs: Additional properties

        Returns:
            Todo block object

        Example:
            >>> todo = await client.blocks.create_todo(
            ...     parent=page,
            ...     text="Review PR",
            ...     checked=False
            ... )
            >>> print(f"Todo: {todo.text} (checked: {todo.checked})")
        """
        from better_notion._sdk.models.blocks.todo import Todo

        return await Todo.create(
            parent=parent,
            text=text,
            checked=checked,
            client=self._client,
            **kwargs
        )

    # ===== PARAGRAPH BLOCKS =====

    async def create_paragraph(
        self,
        parent: "Page | Block",
        text: str,
        **kwargs
    ) -> "Paragraph":
        """Create a paragraph block.

        Args:
            parent: Parent page or block
            text: Paragraph text
            **kwargs: Additional properties

        Returns:
            Paragraph block object

        Example:
            >>> para = await client.blocks.create_paragraph(
            ...     parent=page,
            ...     text="This is a paragraph."
            ... )
        """
        from better_notion._sdk.models.blocks.paragraph import Paragraph

        return await Paragraph.create(
            parent=parent,
            text=text,
            client=self._client,
            **kwargs
        )

    # ===== HEADING BLOCKS =====

    async def create_heading(
        self,
        parent: "Page | Block",
        text: str,
        level: int = 1,
        **kwargs
    ) -> "Heading":
        """Create a heading block.

        Args:
            parent: Parent page or block
            text: Heading text
            level: Heading level (1, 2, or 3)
            **kwargs: Additional properties

        Returns:
            Heading block object

        Example:
            >>> h1 = await client.blocks.create_heading(
            ...     parent=page,
            ...     text="Introduction",
            ...     level=1
            ... )
        """
        from better_notion._sdk.models.blocks.heading import Heading

        return await Heading.create(
            parent=parent,
            text=text,
            level=level,
            client=self._client,
            **kwargs
        )

    # ===== BULLET LIST BLOCKS =====

    async def create_bullet(
        self,
        parent: "Page | Block",
        text: str,
        **kwargs
    ) -> "Bullet":
        """Create a bulleted list item block.

        Args:
            parent: Parent page or block
            text: List item text
            **kwargs: Additional properties

        Returns:
            Bullet block object

        Example:
            >>> item = await client.blocks.create_bullet(
            ...     parent=page,
            ...     text="First item"
            ... )
        """
        from better_notion._sdk.models.blocks.bullet import Bullet

        return await Bullet.create(
            parent=parent,
            text=text,
            client=self._client,
            **kwargs
        )

    # ===== NUMBERED LIST BLOCKS =====

    async def create_numbered(
        self,
        parent: "Page | Block",
        text: str,
        **kwargs
    ) -> "Numbered":
        """Create a numbered list item block.

        Args:
            parent: Parent page or block
            text: List item text
            **kwargs: Additional properties

        Returns:
            Numbered block object

        Example:
            >>> item = await client.blocks.create_numbered(
            ...     parent=page,
            ...     text="First item"
            ... )
        """
        from better_notion._sdk.models.blocks.numbered import Numbered

        return await Numbered.create(
            parent=parent,
            text=text,
            client=self._client,
            **kwargs
        )

    # ===== QUOTE BLOCKS =====

    async def create_quote(
        self,
        parent: "Page | Block",
        text: str,
        **kwargs
    ) -> "Quote":
        """Create a quote block.

        Args:
            parent: Parent page or block
            text: Quote text
            **kwargs: Additional properties

        Returns:
            Quote block object

        Example:
            >>> quote = await client.blocks.create_quote(
            ...     parent=page,
            ...     text="Code is poetry."
            ... )
        """
        from better_notion._sdk.models.blocks.quote import Quote

        return await Quote.create(
            parent=parent,
            text=text,
            client=self._client,
            **kwargs
        )

    # ===== DIVIDER BLOCKS =====

    async def create_divider(
        self,
        parent: "Page | Block",
        **kwargs
    ) -> "Divider":
        """Create a divider block.

        Args:
            parent: Parent page or block
            **kwargs: Additional properties

        Returns:
            Divider block object

        Example:
            >>> divider = await client.blocks.create_divider(parent=page)
        """
        from better_notion._sdk.models.blocks.divider import Divider

        return await Divider.create(
            parent=parent,
            client=self._client,
            **kwargs
        )

    # ===== CALLOUT BLOCKS =====

    async def create_callout(
        self,
        parent: "Page | Block",
        text: str,
        icon: str | None = None,
        **kwargs
    ) -> "Callout":
        """Create a callout block.

        Args:
            parent: Parent page or block
            text: Callout text
            icon: Emoji icon (optional)
            **kwargs: Additional properties

        Returns:
            Callout block object

        Example:
            >>> callout = await client.blocks.create_callout(
            ...     parent=page,
            ...     text="Important note!",
            ...     icon="💡"
            ... )
        """
        from better_notion._sdk.models.blocks.callout import Callout

        return await Callout.create(
            parent=parent,
            text=text,
            icon=icon,
            client=self._client,
            **kwargs
        )
```

## Usage Examples

### Example 1: Creating Various Blocks

```python
page = await client.pages.get(page_id)

# Code block
code = await client.blocks.create_code(
    parent=page,
    code="def hello():\n    print('Hi!')",
    language="python"
)

# Todo
todo = await client.blocks.create_todo(
    parent=page,
    text="Fix bug",
    checked=False
)

# Heading
h1 = await client.blocks.create_heading(
    parent=page,
    text="Introduction",
    level=1
)

# Paragraph
para = await client.blocks.create_paragraph(
    parent=page,
    text="This is the introduction."
)
```

### Example 2: Working with Code Blocks

```python
# Create code block
code = await client.blocks.create_code(
    parent=page,
    code="print('Hello')",
    language="python"
)

# Access type-specific properties
print(code.code)  # "print('Hello')"
print(code.language)  # "python"

# Update
await code.update(
    client=client,
    code="print('Hello, World!')",
    language="python"
)
```

### Example 3: Working with Todos

```python
# Create todo
todo = await client.blocks.create_todo(
    parent=page,
    text="Review documentation",
    checked=False
)

# Check status
if not todo.checked:
    print(f"Todo: {todo.text}")

# Mark as done
await todo.update(client=client, checked=True)
```

### Example 4: Building Document Structure

```python
page = await client.pages.get(page_id)

# Title
h1 = await client.blocks.create_heading(
    parent=page,
    text="API Documentation",
    level=1
)

# Introduction
await client.blocks.create_paragraph(
    parent=page,
    text="This API allows you to..."
)

# Code example
await client.blocks.create_code(
    parent=page,
    code="import requests\nresponse = requests.get('https://api.example.com')",
    language="python"
)

# Warning callout
await client.blocks.create_callout(
    parent=page,
    text="Rate limit: 100 requests/minute",
    icon="⚠️"
)

# Divider
await client.blocks.create_divider(parent=page)
```

## Design Decisions

### Q1: Specialized classes or generic block?

**Decision**: Specialized classes (Code, Todo, etc.)

**Rationale**:
- **Type-safe**: Each class has specific methods
- **IDE support**: Autocomplete for type-specific properties
- **Clear intent**: `create_code()` vs `create_block(type="code")`

```python
# ✅ Specialized (our approach)
code = await client.blocks.create_code(page, code="...")
print(code.language)  # Type-specific

# ❌ Generic (alternative)
block = await client.blocks.create(page, type="code", code="...")
print(block.data["code"]["language"])  # Verbose, error-prone
```

### Q2: Why no generic create_block()?

**Decision**: No generic create, only specific create methods

**Rationale**:
- Forces explicit block type
- Prevents runtime type errors
- Better IDE autocomplete

```python
# ✅ Explicit - compiler can verify
code = await client.blocks.create_code(page, code="...")

# ❌ Generic - runtime errors possible
block = await client.blocks.create_block(page, type="codee")  # Typo!
```

### Q3: Block manager vs page.blocks?

**Decision**: Use `client.blocks` for creating, `page.children` for iterating

**Rationale**:
- **Manager**: For creating (factory pattern)
- **Page.children**: For navigation (entity-oriented)

```python
# ✅ Create via manager
code = await client.blocks.create_code(page, code="...")

# ✅ Iterate via page
async for block in page.children:
    print(block.type)
```

## Comparison: Manager vs Entity

### Via Manager (Recommended)

```python
# ✅ Shorter, discoverable
code = await client.blocks.create_code(page, code="...")
todo = await client.blocks.create_todo(page, text="Task")

# ✅ Easy to find methods
client.blocks.create_<TAB>
# .create_code(), .create_todo(), .create_paragraph(), etc.
```

### Via Entity (Advanced)

```python
# ✅ Autonomous - can be tested without client
code = await Code.create(parent=page, code="...", client=client)

# ✅ More control for special cases
block = Block.from_data(client, data)
```

## Supported Block Types

| Block Type | Create Method | Specialized Class |
|------------|---------------|-------------------|
| Paragraph | `create_paragraph()` | Paragraph |
| Heading 1-3 | `create_heading()` | Heading |
| Code | `create_code()` | Code |
| Todo | `create_todo()` | Todo |
| Bullet List | `create_bullet()` | Bullet |
| Numbered List | `create_numbered()` | Numbered |
| Quote | `create_quote()` | Quote |
| Divider | `create_divider()` | Divider |
| Callout | `create_callout()` | Callout |
| Toggle | `create_toggle()` | Toggle |

## Best Practices

### DO ✅

```python
# Use specialized create methods
code = await client.blocks.create_code(page, code="...")

# Use type-specific properties
print(code.language)  # Type-aware

# Use page.children for iteration
async for block in page.children:
    if block.type == "code":
        print(block.code)
```

### DON'T ❌

```python
# Don't try to create blocks generically
# This doesn't exist
block = await client.blocks.create_block(type="code", ...)

# Don't forget to pass client when needed
# Wrong
code = await Code.create(page, code="...")  # Missing client

# Right
code = await Code.create(page, code="...", client=client)
```

## Related Documentation

- [NotionClient](../implementation/notion-client.md) - Client with managers
- [Block Model](../models/block-model.md) - Generic Block base class
- [Specialized Blocks](../models/blocks-specialized.md) - Code, Todo, etc.
- [Navigation](../implementation/navigation.md) - Block navigation
