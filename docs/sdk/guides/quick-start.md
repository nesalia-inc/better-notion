# Quick Start Guide

Get started with the Better Notion SDK in minutes.

## Installation

```bash
pip install better-notion
```

## Initialize Client

```python
import os
from better_notion import NotionClient

# Initialize with your integration token
client = NotionClient(auth=os.getenv("NOTION_KEY"))
```

**Get your token**:
1. Go to https://www.notion.so/my-integrations
2. Click "New integration"
3. Copy "Internal Integration Token"
4. Share integration with your workspace pages/databases

## Basic Operations

### Get a Page

```python
# Get page by ID
page = await client.pages.get(page_id)

# Access properties
print(f"Title: {page.title}")
print(f"URL: {page.url}")
print(f"Icon: {page.icon}")
print(f"Cover: {page.cover}")
```

### Get a Database

```python
# Get database by ID
database = await client.databases.get(database_id)

# Access database info
print(f"Database: {database.title}")
print(f"Description: {database.description}")

# List all properties
for prop_name, prop_def in database.schema.items():
    prop_type = prop_def["type"]
    print(f"  {prop_name}: {prop_type}")
```

### Query a Database

```python
# Get all pages with status "Done"
pages = await database.query(
    client=client,
    status="Done"
).collect()

for page in pages:
    print(f"{page.title}")
```

### Create a Page

```python
# Create a new page in a database
database = await client.databases.get(database_id)

new_page = await client.pages.create(
    parent=database,
    title="My New Task",
    status="Todo",
    priority=5
)

print(f"Created: {new_page.url}")
```

### Update a Page

```python
# Get page
page = await client.pages.get(page_id)

# Update properties
await page.update(
    client=client,
    status="In Progress",
    priority=7
)
```

### Add Content to a Page

```python
# Get page
page = await client.pages.get(page_id)

# Add a heading
await client.blocks.create_heading(
    parent=page,
    text="Introduction",
    level=1
)

# Add a paragraph
await client.blocks.create_paragraph(
    parent=page,
    text="This is the introduction."
)

# Add code
await client.blocks.create_code(
    parent=page,
    code="print('Hello, World!')",
    language="python"
)
```

## Working with Properties

### Smart Property Access

```python
page = await client.pages.get(page_id)

# Get typed values automatically
status = page.get_property("Status")  # → "In Progress"
priority = page.get_property("Priority")  # → 7
due_date = page.get_property("Due Date")  # → datetime object
tags = page.get_property("Tags")  # → ["urgent", "backend"]

# Safe defaults
status = page.get_property("Status", default="Unknown")
```

### Property Types

| Property Type | Example | Returns |
|--------------|---------|---------|
| Title | `page.title` | `str` |
| Select | `page.get_property("Status")` | `str` |
| Multi-select | `page.get_property("Tags")` | `list[str]` |
| Checkbox | `page.get_property("Done")` | `bool` |
| Number | `page.get_property("Count")` | `float` |
| Date | `page.get_property("Due")` | `datetime` |
| People | `page.get_property("Assignee")` | `list[str]` (user IDs) |

## Query Filters

### Simple Filters

```python
# Equality
pages = await database.query(client=client, status="Done").collect()

# Comparison operators
pages = await database.query(client=client, priority__gte=5).collect()

# Date filters
pages = await database.query(
    client=client,
    due_date__before="2025-01-31"
).collect()
```

### Multiple Filters (AND)

```python
pages = await database.query(
    client=client,
    status="In Progress",
    priority__gte=5,
    assignee__is_null=False
).collect()
```

### Text Search

```python
# Contains
pages = await database.query(
    client=client,
    title__contains="Project"
).collect()

# Starts with
pages = await database.query(
    client=client,
    title__starts_with="Q1"
).collect()
```

## Using Cache

### Populate User Cache (Recommended)

```python
# Pre-load all users (one-time)
await client.users.populate_cache()

# Now user lookups are instant
pages = await database.query(client=client).collect()

for page in pages:
    # Instant lookup from cache
    creator = client.users.cache.get(page.created_by_id)
    if creator:
        print(f"Created by: {creator.name}")
```

### Cache Statistics

```python
# Get cache stats
stats = client.get_cache_stats()

print(f"User cache hit rate: {stats['user_cache']['hit_rate']:.1%}")
print(f"Page cache size: {stats['page_cache']['size']}")
```

## Working with Blocks

### Get Page Content

```python
page = await client.pages.get(page_id)

# Iterate over child blocks
async for block in page.children:
    print(f"{block.type}: {block}")
```

### Create Different Block Types

```python
page = await client.pages.get(page_id)

# Code block
code = await client.blocks.create_code(
    parent=page,
    code="def hello():\n    print('Hi!')",
    language="python"
)

# To-do
todo = await client.blocks.create_todo(
    parent=page,
    text="Review PR",
    checked=False
)

# Heading
h1 = await client.blocks.create_heading(
    parent=page,
    text="Introduction",
    level=1
)

# Quote
quote = await client.blocks.create_quote(
    parent=page,
    text="Code is poetry."
)

# Callout
callout = await client.blocks.create_callout(
    parent=page,
    text="Important note!",
    icon="💡"
)

# Divider
await client.blocks.create_divider(parent=page)
```

### Specialized Block Properties

```python
# Get code block
code = await client.blocks.get(block_id)

# Type-specific properties
if code.type == "code":
    print(code.code)  # The code content
    print(code.language)  # Programming language

# Get todo
todo = await client.blocks.get(block_id)

if todo.type == "to_do":
    print(todo.text)  # Todo text
    print(todo.checked)  # Boolean
```

## Common Patterns

### Iterate All Pages in Database

```python
database = await client.databases.get(database_id)

# Stream pages (memory efficient)
async for page in database.query(client=client):
    print(page.title)
```

### Find Specific Page

```python
database = await client.databases.get(database_id)

# Find first match
page = await database.query(
    client=client,
    title="My Task"
).first()

if page:
    print(f"Found: {page.title}")
```

### Count Pages

```python
database = await client.databases.get(database_id)

# Count all pages
count = await database.query(client=client).count()

# Count with filter
done_count = await database.query(
    client=client,
    status="Done"
).count()

print(f"Total: {count}, Done: {done_count}")
```

### Batch User Lookups

```python
# ❌ BAD - Makes API call for each page
for page in pages:
    user = await client.users.get(page.created_by_id)  # Slow!

# ✅ GOOD - One populate, instant lookups
await client.users.populate_cache()

for page in pages:
    user = client.users.cache.get(page.created_by_id)  # Fast!
```

## Context Manager (Auto Cleanup)

```python
# Client automatically clears caches on exit
async with NotionClient(auth="...") as client:
    page = await client.pages.get(page_id)
    await page.update(client=client, status="Done")

    # Caches auto-cleared on exit
```

## Next Steps

- **[Advanced Examples](./advanced-examples.md)** - Complex patterns and use cases
- **[NotionClient](../implementation/notion-client.md)** - Client architecture
- **[Managers](../managers/)** - Page, Database, Block, User managers
- **[Models](../models/)** - Page, Database, Block, User entities
- **[Implementation](../implementation/)** - Technical specifications

## Need Help?

- Check the [examples](../../../examples/) directory
- Read the [feature catalog](../feature-catalog.md)
- Review [implementation specs](../implementation/)

## Common Mistakes

### Don't Forget `client=` Parameter

```python
# ❌ WRONG - Missing client parameter
pages = await database.query(status="Done")

# ✅ CORRECT - Pass client
pages = await database.query(client=client, status="Done")
```

### Don't Ignore Cache in Loops

```python
# ❌ WRONG - API call in each iteration
for page in pages:
    user = await client.users.get(page.created_by_id)

# ✅ CORRECT - Use cache
await client.users.populate_cache()

for page in pages:
    user = client.users.cache.get(page.created_by_id)
```

### Don't Collect Without Limits

```python
# ❌ WRONG - Could be huge
all_pages = await database.query(client=client).collect()

# ✅ CORRECT - Stream instead
async for page in database.query(client=client):
    process(page)

# Or use limit
pages = await database.query(client=client).limit(10).collect()
```
