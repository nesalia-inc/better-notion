# Design Philosophy

## Core Principle: Developer Experience First

Better Notion SDK is not merely an API wrapper. It is a productivity framework that transforms how developers interact with Notion.

Inspired by discord.py, we believe the SDK should provide more features than the underlying API, making developers significantly more productive than they would be with raw API access.

## Mental Model Shift

### API-First Thinking (What We Avoid)
- "The API has a search endpoint"
- "The API uses pagination"
- "The API returns nested dictionaries"
- "Each operation = one API call"
- "Users must know resource IDs"
- "Handle HTTP errors"

### Developer-First Thinking (Our Approach)
- "The user wants to find pages"
- "The user wants to iterate through results"
- "The user wants `page.title`"
- "How can we avoid this API call?"
- "How can we find by attribute?"
- "Raise semantic exceptions"

## Discord.py as Inspiration

discord.py doesn't describe itself as an "API wrapper" but as a "modern, easy to use, feature-rich, and async ready API wrapper." The key word is **feature-rich** - it provides features that Discord API doesn't have.

### Examples from discord.py

#### Cache-First Operations
```python
# Discord API: No direct member lookup
# discord.py: Instant cache lookup
member = guild.get_member(user_id)  # No API call
member = guild.get_member_named("John#1234")  # Search cache
```

#### Semantic Iterators
```python
# Discord API: Manual pagination
# discord.py: Automatic async iteration
async for message in channel.history(limit=100):
    process(message)
```

#### Object-Oriented Methods
```python
# Discord API: DELETE /channels/{id}/messages/{id}
# discord.py: Semantically meaningful
await message.delete()
```

#### Non-API Methods
```python
# Discord API doesn't have "ban user by name"
# discord.py adds it:
member = guild.get_member_named("John")
await member.ban(reason="Spamming")
```

## Applied to Notion

We apply the same philosophy: identify what developers naturally want to do and make those operations effortless, even if the Notion API doesn't directly support them.

## Key Design Principles

### 1. Eliminate Friction

Every interaction should feel natural to a Python developer.

#### Before (API-like)
```python
title = page["properties"]["Name"]["title"][0]["plain_text"]
```

#### After (Pythonic)
```python
title = page.title
```

**Rationale:** Nested dictionary access is implementation detail. Users shouldn't need to understand Notion's internal structure.

### 2. Cache Aggressively

If information can be stored locally, avoid repeated API calls.

#### Problem
```python
# Every lookup = one API call
for page in pages:
    created_by = await api.users.retrieve(page["created_by"]["id"])
    last_edited_by = await api.users.retrieve(page["last_edited_by"]["id"])
```

#### Solution
```python
# First call populates cache, rest are instant
for page in pages:
    created_by = client.users.cache.get(page.created_by_id)
    last_edited_by = client.users.cache.get(page.last_edited_by_id)
```

**Rationale:** User information appears everywhere. Caching transforms 100 API calls into 1 call + 99 memory lookups.

### 3. Hide Pagination

Pagination is an implementation detail, not a user concern.

#### Before
```python
cursor = None
while True:
    response = await api.databases.query(database_id, start_cursor=cursor)
    process(response["results"])
    if not response["has_more"]:
        break
    cursor = response["next_cursor"]
```

#### After
```python
async for page in database.query():
    process(page)
```

**Rationale:** Users want to process results, not manage cursors. Async iteration is the Pythonic way.

### 4. Provide Semantic Operations

Users think in terms of operations, not API endpoints.

#### What Users Want
- "Get all pages in this workspace"
- "Find pages by title"
- "Copy this page with its content"
- "Move these pages to another database"

#### What We Provide
```python
# API doesn't have "list all"
async for page in client.pages.all():
    ...

# API doesn't have search by title
page = await client.pages.find_by_title("Project Plan")

# API doesn't have duplicate
new_page = await page.duplicate(parent=target_db)

# API doesn't have bulk move
await client.pages.move_bulk(pages, new_parent=target_db)
```

**Rationale:** Common operations should be one method call, not ten.

### 5. Enable Hierarchical Thinking

Notion is inherently hierarchical. The SDK should reflect that.

#### Before (ID-based)
```python
parent_id = page["parent"]["page_id"]
parent = await api.pages.retrieve(parent_id)

children_data = await api.blocks.children.list(block_id=page["id"])
```

#### After (Hierarchical)
```python
parent = await page.parent
children = await page.children
```

**Rationale:** Users think in terms of parent/child relationships, not IDs.

### 6. Fail Clearly

Errors should guide users to solutions.

#### Before (HTTP errors)
```python
raise HTTPError(404, "Not found")
```

#### After (Semantic)
```python
raise PageNotFound(
    f"Page {page_id} does not exist or you don't have access"
)
```

**Rationale:** Error messages should explain what went wrong and suggest what to do.

### 7. Type Everything

Comprehensive type hints enable better IDE support and catch errors early.

```python
async def get_page(page_id: str) -> Page:
    ...

async def query_database(
    database_id: str,
    filter: QueryFilter | None = None
) -> AsyncIterator[Page]:
    ...
```

**Rationale:** Modern Python development relies on type hints for productivity.

### 8. Async-Native

All I/O operations should be async by default.

```python
# All these are async
page = await client.pages.get(page_id)
pages = await database.query()
async for block in page.children:
    ...
```

**Rationale:** Async is the modern standard for I/O-bound applications in Python.

### 9. Provide Escape Hatches

Opinionated defaults with escape routes for power users.

```python
# High-level abstraction
title = page.title

# Escape to raw when needed
raw_properties = page._raw["properties"]

# Access low-level API
raw_response = await client._api.pages.retrieve(page_id)
```

**Rationale:** Abstractions should hide complexity but not prevent access to power.

### 10. Batch Operations

Recognize patterns and optimize them.

#### Before
```python
for page in pages:
    await api.pages.update(
        page_id=page.id,
        properties={"Status": "Done"}
    )
```

#### After
```python
await client.pages.update_bulk(
    pages,
    properties={"Status": "Done"}
)
# Handles batching, rate limiting, parallelization
```

**Rationale:** Bulk operations are common. The SDK should handle the complexity.

## Features Beyond the API

These are capabilities that don't exist in the Notion API but should exist in the SDK:

### Cache Management
- Instant user lookups by ID
- Instant database/page lookups
- Cache invalidation strategies
- Local search within cached data

### Semantic List Operations
- `client.pages.all()` - List all pages
- `client.databases.all()` - List all databases
- `client.users.all()` - List all users
- Filter by type, attributes

### Hierarchical Navigation
- `page.parent` - Get parent object
- `page.children` - Get children iterator
- `page.ancestors` - Walk up the tree
- `page.descendants` - Walk down the tree

### Bulk Operations
- Create multiple pages at once
- Update multiple items
- Move multiple items
- Batch with automatic rate limiting

### Smart Search
- Search by title in cache
- Fuzzy matching for property names
- Search across multiple attributes
- Hybrid cache/API search

### Content Operations
- Duplicate page with children
- Copy blocks between pages
- Transform content structures
- Merge blocks

### Workspace Awareness
- `client.workspace` - Workspace info
- `client.workspace.users` - User directory
- `client.workspace.find_user_by_email()`

### Events (Optional Future)
- `@client.pages.on_created`
- `@client.pages.on_updated`
- `@page.on_changed`

## Decision Framework

When deciding how to implement a feature, ask:

1. **What does the user want to achieve?** (Not what API exists)
2. What is the most intuitive way to express this in Python?
3. Can we cache this to avoid API calls?
4. Can we combine multiple API calls into one operation?
5. What would a developer naturally expect this to be called?
6. How can we make this impossible to use incorrectly?
7. What type hints make this clear and safe?

## Success Metrics

The SDK is successful when:

1. Developers are productive in minutes, not hours
2. Common tasks require minimal code
3. API calls are minimized through caching
4. Errors provide clear guidance
5. IDE autocomplete suggests the right methods
6. Users rarely need to read API documentation
7. Complex operations feel simple

## Conclusion

We are not building a wrapper. We are building a transformation layer that turns a REST API into a delightful Python development experience. Every decision should prioritize developer productivity over API fidelity.
