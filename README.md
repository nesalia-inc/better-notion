# Better Notion

**A pythonic, object-oriented SDK for the Notion API.**

[![PyPI](https://img.shields.io/pypi/v/better-notion)](https://pypi.org/project/better-notion/)
[![Python](https://img.shields.io/pypi/pyversions/better-notion)](https://pypi.org/project/better-notion/)
[![Tests](https://img.shields.io/github/actions/nesalia-inc/better-notion/workflows/tests/badge.svg)](https://github.com/nesalia-inc/better-notion/actions)
[![Coverage](https://img.shields.io/codecov/c/gh/nesalia-inc/better-notion)](https://codecov.io/gh/nesalia-inc/better-notion)

---

## 🚀 Quick Start

```bash
pip install better-notion
```

```python
import asyncio
from better_notion import NotionAPI

async def main():
    async with NotionAPI(auth="secret_...") as api:
        # Get a page
        page = await api.pages.get("page_id")
        print(page.properties)

        # List pages in a database
        async for page in api.pages.iterate("database_id"):
            print(page.title)

asyncio.run(main())
```

---

## ✨ Why Better Notion?

- **🎯 Object-Oriented**: Work with entities, not JSON dicts
- **🔋 Type-Safe**: Property builders for compile-time safety
- **📄 Paginated**: Automatic cursor-based pagination
- **🔍 Powerful Search**: Search across your entire workspace
- **⚡ Async-First**: Built with `asyncio` and `httpx` for performance

---

## 📦 Installation

### SDK Installation

```bash
# With pip
pip install better-notion

# With uv
uv pip install better-notion
```

### CLI Installation

```bash
# Install with CLI support
pip install better-notion[cli]

# Or install everything
pip install better-notion[all]
```

The CLI provides a `notion` command for interacting with Notion from the terminal, designed primarily for AI agents.

**CLI Status**: ⚠️ Experimental - Under active development

---

## 💻 CLI Usage

The Better Notion CLI provides a command-line interface for interacting with Notion.

### Installation

```bash
pip install better-notion[cli]
```

### Basic Commands

```bash
# Show version
notion --version

# Check authentication status
notion auth status

# Show help
notion --help
```

### Response Format

All CLI commands return JSON for programmatic parsing:

```json
{
  "success": true,
  "data": {
    "id": "page_123",
    "title": "My Page"
  },
  "meta": {
    "version": "0.4.0",
    "timestamp": "2025-01-26T10:00:00Z",
    "rate_limit": {
      "remaining": 48,
      "reset_at": "2025-01-26T10:01:00Z"
    }
  }
}
```

### Error Handling

Errors are returned with structured codes:

```json
{
  "success": false,
  "error": {
    "code": "NOT_FOUND",
    "message": "Page not found",
    "retry": false
  },
  "meta": {...}
}
```

### Exit Codes

- `0` - Success
- `1` - Generic error
- `2` - Invalid input
- `3` - Authentication error
- `4` - Rate limit exceeded
- `5` - Not found
- `6` - Conflict

**Note**: The CLI is currently in experimental stage. See [CLI Documentation](docs/cli/) for more details.

---

## 🔑 Authentication

Create an integration at [notion.so/my-integrations](https://notion.so/my-integrations) to get your API token.

```python
from better_notion import NotionAPI

api = NotionAPI(auth="secret_...")
```

---

## 📚 Features

### Entities

All Notion objects are represented as Python entities:

- **Pages** - Create, read, update, delete, archive
- **Blocks** - Manipulate content blocks
- **Databases** - Query and manage databases
- **Users** - Retrieve user information

### Property Builders

Type-safe builders for all Notion property types:

```python
from better_notion._api.properties import Title, Select, Date, Checkbox

properties = {
    **Title("My Page").build(),
    **Select("Status", "In Progress").build(),
    **Date("Due Date", "2025-01-15").build(),
    **Checkbox("Done", False).build(),
}
```

### Automatic Pagination

Memory-efficient iteration over large datasets:

```python
async for page in api.pages.iterate("database_id"):
    # Processes pages lazily, not all at once
    process(page)
```

---

## 💡 Usage Examples

### Creating a Page

```python
from better_notion import NotionAPI
from better_notion._api.properties import Title, Text

async def create_page():
    async with NotionAPI(auth="secret_...") as api:
        page = await api.pages.create(
            parent={"database_id": "database_id"},
            properties={
                **Title("My New Page").build(),
                **Text("Notes", "Some notes").build(),
            }
        )
        print(f"Created page: {page.id}")
```

### Updating a Page

```python
from better_notion._api.properties import Select

async def update_page():
    async with NotionAPI(auth="secret_...") as api:
        page = await api.pages.get("page_id")

        # Update properties locally
        await page.update(
            **Select("Status", "Done").build()
        )

        # Save changes to Notion
        await page.save()
```

### Working with Blocks

```python
async def manipulate_blocks():
    async with NotionAPI(auth="secret_...") as api:
        page = await api.pages.get("page_id")

        # Get children blocks
        children = await page.blocks.children()

        # Append a new block
        await page.blocks.append(children=[
            {
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [{"type": "text", "text": {"content": "New paragraph"}}]
                }
            }
        ])
```

### Searching

```python
async def search_pages():
    async with NotionAPI(auth="secret_...") as api:
        # Search for pages matching query
        async for result in api.search_iterate("my query"):
            if result["object"] == "page":
                print(result["properties"]["title"])
```

---

## 📖 API Reference

### NotionAPI

The main client for interacting with Notion.

**Methods:**
- `search(query, *, filter, sort)` - Search pages and blocks
- `search_iterate(query, *, filter, sort)` - Iterate over search results

**Collections:**
- `api.pages` - PageCollection
- `api.blocks` - BlockCollection
- `api.databases` - DatabaseCollection
- `api.users` - UserCollection

### Page

**Properties:**
- `id` - Page ID
- `created_time` - Creation datetime
- `last_edited_time` - Last edited datetime
- `archived` - Whether page is archived
- `properties` - Page properties dict
- `blocks` - BlockCollection for children

**Methods:**
- `await save()` - Save changes to Notion
- `await delete()` - Archive page
- `await reload()` - Reload from Notion
- `await update(**kwargs)` - Update properties locally

### Block

**Properties:**
- `id` - Block ID
- `type` - Block type (paragraph, heading, etc.)
- `content` - Block content

**Methods:**
- `await save()` - Save changes to Notion
- `await delete()` - Delete block
- `await reload()` - Reload from Notion

### Collections

#### PageCollection
- `await get(page_id)` - Retrieve a page
- `await create(**kwargs)` - Create a new page
- `await list(database_id, **kwargs)` - List pages (first page)
- `iterate(database_id, **kwargs)` - Iterate over all pages

#### BlockCollection
- `await get(block_id)` - Retrieve a block
- `await children()` - Get children blocks
- `await append(**kwargs)` - Append new blocks

#### DatabaseCollection
- `await get(database_id)` - Retrieve a database
- `await query(database_id, **kwargs)` - Query a database
- `await create_page(database_id, **kwargs)` - Create a page in database

#### UserCollection
- `await get(user_id)` - Retrieve a user
- `await list()` - List all users
- `await me()` - Get current bot user

---

## 🤝 Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for details.

### Development

```bash
# Clone the repository
git clone https://github.com/nesalia-inc/better-notion.git

# Install with dev dependencies
uv sync

# Run tests
uv run pytest

# Run with coverage
uv run pytest --cov=better_notion
```

---

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🔗 Links

- [Notion API Documentation](https://developers.notion.com/reference)
- [Issue Tracker](https://github.com/nesalia-inc/better-notion/issues)
- [Discussions](https://github.com/nesalia-inc/better-notion/discussions)

---

## 🙏 Acknowledgments

Built with ❤️ using:
- [httpx](https://www.python-httpx.org/) - Async HTTP client
- [pytest](https://pytest.org/) - Testing framework
