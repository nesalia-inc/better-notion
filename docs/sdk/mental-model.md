# Mental Model and Abstractions

This document defines the conceptual model that developers will work with when using the Better Notion SDK.

## Core Concept: Notion as Objects

The mental model shifts from "API responses" to "Notion objects with behavior."

### API-Centric Model (What We Avoid)
- Responses are dictionaries
- Resources are identified by IDs
- Operations are endpoint-based
- Relationships are maintained manually

### SDK-Centric Model (Our Approach)
- Resources are objects with methods
- Objects know their relationships
- Operations are object-oriented
- State is cached and accessible

## Primary Abstractions

### 1. Workspace

The top-level container representing a Notion workspace.

```python
workspace = client.workspace

workspace.name        # "My Company"
workspace.id          # UUID
workspace.users       # User directory
workspace.statistics  # Usage stats
```

**Conceptual Role:**
- Entry point for workspace-wide operations
- Cache of workspace metadata
- Directory of users and resources

**Relationships:**
- Contains many Databases
- Contains many Pages
- Contains many Users
- Has one Bot User (for integrations)

### 2. Page

A page in Notion, representing a document with properties and content.

```python
page = await client.pages.get(page_id)

page.title           # "Project Plan"
page.properties      # All properties
page.url             # Public URL
page.icon            # Emoji or image
page.cover           # Cover image

page.parent          # Parent object
page.children        # Child blocks iterator
```

**Conceptual Role:**
- Primary content container in Notion
- Has structured data (properties)
- Has hierarchical content (blocks)
- Can be in databases or under other pages

**Relationships:**
- Belongs to one Parent (Database or Page)
- Contains many Blocks (children)
- Has one Creator (created_by)
- Has one Editor (last_edited_by)

**Key Behaviors:**
- Can be retrieved, created, updated, archived
- Can be moved to different parents
- Can be duplicated with children
- Can be searched within

### 3. Database

A structured collection of pages with a defined schema (properties).

```python
database = await client.databases.get(database_id)

database.title        # "Tasks"
database.properties   # Property schema
database.description  # Optional description

database.query()      # Query pages
database.pages        # Iterator over pages
```

**Conceptual Role:**
- Schema definition for pages
- Container for related pages
- Queryable by properties
- Template for new pages

**Relationships:**
- Belongs to one Parent (Page or Workspace)
- Contains many Pages (entries)
- Has Properties (schema)
- Has one Creator

**Key Behaviors:**
- Can be queried with filters
- Can be sorted
- Defines property types
- Validates page data

### 4. Block

A unit of content within a page (paragraph, heading, list, image, etc.).

```python
block = await client.blocks.get(block_id)

block.type           # "paragraph", "heading_1", etc.
block.content        # Type-specific content

block.parent         # Parent block or page
block.children       # Child blocks iterator
```

**Conceptual Role:**
- Atomic content unit
- Can contain other blocks (nested)
- Rich text formatting
- Media container

**Relationships:**
- Belongs to one Parent (Page or Block)
- Contains many Blocks (children, max 2 levels)
- Has one Creator
- Has one Editor

**Key Behaviors:**
- Can be created, updated, deleted
- Can be moved between parents
- Can have 0-2 levels of children
- Typed content (paragraph, heading, code, etc.)

### 5. User

A person or bot in the Notion workspace.

```python
user = await client.users.get(user_id)

user.name            # Display name
user.email           # Email (for persons)
user.type            # "person" or "bot"
user.avatar_url      # Avatar image
```

**Conceptual Role:**
- Actor in the workspace
- Creator/editor of resources
- Assignee in properties
- Mentionable in comments/text

**Relationships:**
- Belongs to one Workspace
- Creates many Pages
- Creates many Blocks
- Edits many resources

**Key Behaviors:**
- Can be retrieved by ID
- Can be found by email/name
- Cached for instant lookups

### 6. Property

A typed field on a Page or Database schema.

```python
property = page.properties["Status"]

property.name        # "Status"
property.type        # "select"
property.value       # "In Progress"
```

**Conceptual Role:**
- Structured data field
- Typed validation
- Queryable attribute
- Displayable metadata

**Types:**
- Text: title, rich_text, url, email, phone
- Number: number
- Selection: select, multi_select, status
- Date: date, created_time, last_edited_time
- Relations: people, relation
- Computed: formula, rollup, verification
- Media: files
- Metadata: checkbox, unique_id

## Hierarchical Model

### Parent-Child Relationships

Notion is fundamentally hierarchical. The SDK exposes this naturally.

```
Workspace
  ├─ Database (root level)
  │   └─ Page (entry)
  │       └─ Block
  │           └─ Block (child)
  │
  └─ Page (root level)
      ├─ Block
      │   ├─ Block (child)
      │   └─ Block (child)
      │
      └─ Block
```

### Navigation Patterns

```python
# Walk up (ancestors)
current = page
while current.parent:
    current = current.parent
    print(current.title)

# Walk down (descendants)
async for block in page.descendants():
    process(block)

# Get siblings
async for sibling in page.siblings():
    process(sibling)

# Get root
root = await page.root()
```

## Query Model

### Filtering as Mental Model, Not API Syntax

The SDK translates user intent to API filter structure.

```python
# User thinks: "Status equals Done"
# SDK translates to:
{
    "property": "Status",
    "select": {"equals": "Done"}
}
```

### Query Building

```python
# Simple
pages = await database.query(status="Done")

# Compound
pages = await database.query().filter(
    status="In Progress",
    priority__gte=5
)

# Fluent
pages = await (database.query()
    .filter(status="In Progress")
    .sort("due_date")
    .limit(10))
```

## Cache Model

### What Gets Cached

**Implicit Caching (happens automatically):**
- Users (from created_by, last_edited_by, people properties)
- Workspace metadata (from /users/me)
- Recently accessed pages/databases/blocks

**Explicit Caching (user-controlled):**
- Preloading all users
- Preloading all databases
- Preloading specific resources

### Cache Behavior

```python
# First access: API call + cache
page = await client.pages.get(page_id)

# Subsequent access: cache only
page = client.pages.cache.get(page_id)

# Cache invalidation
client.pages.cache.invalidate(page_id)
client.pages.cache.clear()
```

### Cache-First Operations

```python
# Find in cache first, fallback to API
user = await client.users.find_by_email(
    "john@example.com",
    use_cache_first=True
)
```

## Type Model

### Type Hierarchy

```
BaseEntity
  ├─ Page
  ├─ Database
  ├─ Block
  └─ User

BaseProperty
  ├─ TextProperty
  ├─ NumberProperty
  ├─ SelectProperty
  ├─ DateProperty
  └─ ...
```

### Type Safety

```python
# Type-checked at compile time
page: Page = await client.pages.get(page_id)

# Iterator types
blocks: AsyncIterator[Block] = page.children

# Optional types
parent: Optional[Page] = page.parent
```

### Generic Operations

```python
# Operations work on all entities
async def get_id(entity: BaseEntity) -> str:
    return entity.id

async def archive(entity: Page | Database):
    await entity.archive()
```

## Async Model

### All I/O is Async

Every operation that involves network access is async.

```python
# All these are async
page = await client.pages.get(id)
pages = await database.query()
user = await client.users.find(email)

# Iteration is async
async for block in page.children:
    process(block)
```

### Rationale

- Non-blocking operations
- Efficient concurrent requests
- Modern Python standard
- Compatible with async frameworks

## Error Model

### Semantic Exceptions

Errors map to domain concepts, not HTTP codes.

```python
# Not: HTTPError(404, "Not found")
# But: PageNotFound(page_id)

try:
    page = await client.pages.get(page_id)
except PageNotFound:
    logger.error(f"Page {page_id} doesn't exist")
except PermissionError:
    logger.error(f"No access to page {page_id}")
except RateLimited:
    logger.warning("Rate limited, retrying...")
```

### Exception Hierarchy

```
NotionError
  ├─ NotFoundError
  │   ├─ PageNotFound
  │   ├─ DatabaseNotFound
  │   └─ UserNotFound
  ├─ PermissionError
  ├─ ValidationError
  ├─ RateLimited
  └─ APIError
```

## Comparison: API vs SDK Mental Model

### Retrieving a Page

**API Model:**
```python
# Make HTTP request
response = requests.get(
    f"https://api.notion.com/v1/pages/{page_id}",
    headers={"Authorization": f"Bearer {token}"}
)

# Parse JSON
data = response.json()

# Access nested structure
title = data["properties"]["Name"]["title"][0]["plain_text"]
```

**SDK Model:**
```python
# Get page object
page = await client.pages.get(page_id)

# Access property
title = page.title
```

### Querying a Database

**API Model:**
```python
# Build filter structure
filter_body = {
    "filter": {
        "property": "Status",
        "select": {"equals": "In Progress"}
    }
}

# Make request
response = requests.post(
    f"https://api.notion.com/v1/databases/{database_id}/query",
    json=filter_body
)

# Handle pagination
results = response.json()["results"]
while response.json()["has_more"]:
    # Make another request...
```

**SDK Model:**
```python
# Query with semantic filter
async for page in database.query(status="In Progress"):
    process(page)
```

### Getting User Information

**API Model:**
```python
# Multiple API calls
user1 = requests.get(f"https://api.notion.com/v1/users/{user1_id}")
user2 = requests.get(f"https://api.notion.com/v1/users/{user2_id}")
user3 = requests.get(f"https://api.notion.com/v1/users/{user3_id}")
```

**SDK Model:**
```python
# One API call, then cache
await client.users.populate_cache()

# Instant lookups
user1 = client.users.cache.get(user1_id)
user2 = client.users.cache.get(user2_id)
user3 = client.users.cache.get(user3_id)
```

## Key Mental Shifts

### 1. From Endpoints to Objects

**Before:** "I need to call the retrieve page endpoint"
**After:** "I need to get a Page object"

### 2. From IDs to Navigation

**Before:** "I have the parent ID, let me retrieve it"
**After:** "Let me get page.parent"

### 3. From Manual Caching to Automatic

**Before:** "I should store this user data to avoid API calls"
**After:** "The SDK caches users automatically"

### 4. From Pagination to Iteration

**Before:** "I need to manage cursors and has_more"
**After:** "I iterate with async for"

### 5. From HTTP Errors to Semantic Exceptions

**Before:** "If status code is 404..."
**After:** "except PageNotFound"

### 6. From Raw Data to Typed Objects

**Before:** "Access this nested dictionary structure"
**After:** "Use this typed object with methods"

## Success Criteria

The mental model is successful when:

1. Developers think in Notion concepts, not API details
2. Common operations feel like one step, not five
3. The SDK does what the user expects
4. Type hints guide the user to correct usage
5. Errors explain what went wrong
6. Documentation focuses on concepts, not endpoints
7. Users rarely need to reference Notion API docs
