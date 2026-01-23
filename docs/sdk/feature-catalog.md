# Feature Catalog

This document catalogs all features provided by the Better Notion SDK, distinguishing between:
- Features that mirror the Notion API
- Features that enhance or go beyond the API

## High-Level Organization

```
client
├── pages
├── databases
├── blocks
├── users
├── search
├── comments
├── files
└── workspace
```

## Pages Manager

### API-Mirrored Features

#### Retrieve a Page
```python
page = await client.pages.get(page_id)
```

#### Create a Page
```python
page = await client.pages.create(
    parent=database,
    properties={...}
)
```

#### Update a Page
```python
await client.pages.update(page, properties={...})
```

#### Archive/Restore a Page
```python
await client.pages.archive(page)
await client.pages.restore(page)
```

#### Retrieve Page Property Item
```python
property_value = await client.pages.get_property(page_id, property_id)
```

#### Move a Page
```python
await client.pages.move(page, new_parent=database, position="after:...")
```

### SDK-Exclusive Features

#### List All Pages
Not in API - requires search without query.

```python
async for page in client.pages.all():
    print(page.title)

# Or collect all
all_pages = await client.pages.all().collect()
```

#### Find by Title
Not in API - requires search + filtering.

```python
page = await client.pages.find_by_title("Project Plan")
pages = await client.pages.find_by_title("Q1 Report", exact=False)
```

#### Filter Pages
Not in API - requires search with object filter.

```python
async for page in client.pages.filter(type="page"):
    process(page)

async for page in client.pages.filter(in_trash=False):
    process(page)
```

#### Cache Lookup
Instant memory access, no API call.

```python
page = client.pages.cache.get(page_id)
if page:
    print(page.title)
else:
    page = await client.pages.get(page_id)
```

#### Hierarchical Navigation
Not in API - requires chaining ID lookups.

```python
# Get parent
parent = await page.parent  # Auto-fetches

# Get cached parent if available
parent = page.parent_cached

# Get children iterator
async for block in page.children:
    print(block)

# Walk up the tree
for ancestor in await page.ancestors():
    print(ancestor.title)

# Walk down the tree
async for descendant in page.descendants():
    process(descendant)
```

#### Property Shortcuts
Not in API - requires navigating nested structure.

```python
# Direct access to common properties
title = page.title
url = page.url
icon = page.icon
cover = page.cover
created_time = page.created_time
last_edited_time = page.last_edited_time
archived = page.archived

# But also raw access
all_properties = page.properties
```

#### Duplicate Page
Not in API - requires recursive copy of all blocks.

```python
# Duplicate with all children
new_page = await page.duplicate(
    parent=target_database,
    title="Copy - " + page.title
)

# Duplicate without children
new_page = await page.duplicate(
    parent=target_database,
    include_children=False
)
```

#### Bulk Operations
Not in API - requires multiple API calls with rate limiting.

```python
# Bulk create
pages = await client.pages.create_bulk(
    parent=database,
    data=[
        {"title": "Task 1", "status": "Todo"},
        {"title": "Task 2", "status": "Todo"},
        {"title": "Task 3", "status": "Todo"},
    ]
)

# Bulk update
await client.pages.update_bulk(
    pages,
    properties={"Status": "Done"}
)

# Bulk archive
await client.pages.archive_bulk(pages)

# Bulk move
await client.pages.move_bulk(
    pages,
    new_parent=target_database
)
```

#### Smart Property Access
Not in API - fuzzy matching and case insensitivity.

```python
# Find property by name (case-insensitive)
prop = page.find_property("status")  # Finds "Status", "status", "STATUS"

# Get property value with type conversion
status = page.get_property("status")  # Returns typed value
status = page.get_property("status", default="Unknown")
```

## Databases Manager

### API-Mirrored Features

#### Create a Database
```python
database = await client.databases.create(
    parent=page,
    title={...},
    properties={...}
)
```

#### Retrieve a Database
```python
database = await client.databases.get(database_id)
```

#### Update a Database
```python
await client.databases.update(database, properties={...})
```

#### Query a Data Source
```python
results = await database.query(
    filter={...},
    sort={...}
)
```

### SDK-Exclusive Features

#### List All Databases
Not in API - requires search with filter.

```python
async for database in client.databases.all():
    print(database.title)

# Or collect all
all_databases = await client.databases.all().collect()
```

#### Find by Title
Not in API - requires search.

```python
database = await client.databases.find_by_title("Tasks")
databases = await client.databases.find_by_title("Project")
```

#### Cache Lookup
Instant memory access.

```python
database = client.databases.cache.get(database_id)
if database:
    print(database.title)
```

#### Enhanced Query
Builder pattern with shortcuts.

```python
# Simple filter
results = await database.query(status="In Progress")

# Complex filter
results = await database.query().filter(
    status="In Progress",
    priority__gte=5
).sort("due_date", "ascending")

# Convert to list
pages = await results.collect()

# Async iteration
async for page in database.query():
    process(page)
```

#### Query Helpers
Not in API - semantic filters.

```python
# Recent items
recent = await database.recent(days=7)

# By property value
pages = await database.filter_by("status", "Done")

# Multi-condition
pages = await database.filter_multiple(
    status="In Progress",
    assignee=current_user
)
```

#### Database Pages
Not in API - direct access to pages in a database.

```python
# All pages in database (cached)
async for page in database.pages:
    print(page.title)

# Get page by title
page = await database.get_page_by_title("Task 1")
```

#### Property Schema Helpers
Not in API - easier property inspection.

```python
# Get property by name
prop = database.get_property("Status")

# Check property exists
has_status = database.has_property("Status")

# List all property names
names = database.property_names

# Get property type
prop_type = database.get_property_type("Status")
```

## Blocks Manager

### API-Mirrored Features

#### Retrieve a Block
```python
block = await client.blocks.get(block_id)
```

#### Retrieve Block Children
```python
children = await client.blocks.children.list(block_id)
```

#### Append Block Children
```python
await client.blocks.children.append(
    block_id,
    children=[...]
)
```

#### Update a Block
```python
await client.blocks.update(block, {...})
```

#### Delete a Block
```python
await client.blocks.delete(block)
```

### SDK-Exclusive Features

#### Hierarchical Navigation
Not in API - requires chaining API calls.

```python
# Get parent
parent = await block.parent

# Get children as iterator
async for child in block.children:
    print(child)

# Walk subtree
async for descendant in block.descendants():
    process(descendant)
```

#### Block Type Shortcuts
Not in API - requires checking "type" field.

```python
# Direct access to typed content
if block.is_paragraph:
    text = block.text
elif block.is_heading:
    text = block.text
    level = block.level
elif block.is_code:
    code = block.code
    language = block.language
```

#### Content Manipulation
Not in API - requires multiple API calls.

```python
# Insert at position
await block.insert_child(new_block, position=0)

# Replace all children
await block.replace_children(new_blocks)

# Delete all children
await block.clear_children()

# Move block
await block.move(new_parent=other_block, position="after:...")
```

#### Block Creation Helpers
Not in API - simplified block creation.

```python
# Create with simple API
paragraph = Block.paragraph("Hello world")
heading = Block.heading("Title", level=2)
code = Block.code("print('hello')", language="python")
list_item = Block.bullet_item("Item 1")
```

#### Batch Block Operations
Not in API - requires multiple calls with rate limiting.

```python
# Bulk append
await block.append_children(blocks)

# Bulk delete
await client.blocks.delete_bulk(blocks)
```

## Users Manager

### API-Mirrored Features

#### Retrieve Your Bot User
```python
me = await client.users.me()
```

#### Retrieve a User
```python
user = await client.users.get(user_id)
```

#### List All Users
```python
async for user in client.users.list():
    print(user.name)
```

### SDK-Exclusive Features

#### Persistent Cache
Not in API - cache populated from various sources.

```python
# Instant lookup (no API call)
user = client.users.cache.get(user_id)

# User cache is populated from:
# - /users/me response
# - /users responses
# - page.created_by fields
# - page.last_edited_by fields
# - people properties
```

#### Find by Email
Not in API - requires listing all users and filtering.

```python
user = await client.users.find_by_email("john@example.com")
```

#### Find by Name
Not in API - requires listing and filtering.

```python
user = await client.users.find_by_name("John Doe")
users = await client.users.find_by_name("John", exact=False)
```

#### Workspace Directory
Not in API - aggregated from various responses.

```python
# Get all users once
await client.users.populate_cache()

# Then instant lookups
all_users = client.users.cache.all()
people = [u for u in all_users if u.is_person]
bots = [u for u in all_users if u.is_bot]
```

## Search Manager

### API-Mirrored Features

#### Search by Title
```python
results = await client.search.query(query="project")
```

### SDK-Exclusive Features

#### Search with Local Cache
Not in API - hybrid cache/API search.

```python
# Search in cache first (instant)
results = await client.search.query(
    "project",
    use_cache_first=True
)

# Cache-only search (no API call)
results = client.search.search_cache("project")
```

#### Search by Type
Not in API - requires filter parameter.

```python
pages = await client.search.pages(query="project")
databases = await client.search.databases(query="tasks")
```

#### Search Shortcuts
Not in API - semantic search methods.

```python
# Find pages by title
pages = await client.search.find_pages_by_title("Project")

# Fuzzy matching
pages = await client.search.find_pages_fuzzy("proj")  # Finds "Project", "Projects", etc.
```

## Comments Manager

### API-Mirrored Features

#### Create a Comment
```python
comment = await client.comments.create(
    parent=page,
    rich_text=[...]
)
```

#### Retrieve a Comment
```python
comment = await client.comments.get(comment_id)
```

#### List Comments
```python
comments = await client.comments.list(block_id=page_id)
```

### SDK-Exclusive Features

#### Thread Navigation
Not in API - requires multiple API calls.

```python
# Get all comments in thread
thread = await comment.thread()

# Get parent comment
parent = await comment.parent

# Get replies
async for reply in comment.replies():
    print(reply.text)
```

#### Rich Comment Creation
Not in API - simplified rich text building.

```python
# Simple text
comment = await client.comments.create(
    parent=page,
    text="This looks great!"
)

# With mentions
comment = await client.comments.create(
    parent=page,
    text="Hey @user, check this out!",
    mentions=[user]
)

# With attachments
comment = await client.comments.create(
    parent=page,
    text="See this file",
    attachments=[file]
)
```

## Files Manager

### API-Mirrored Features

#### Create File Upload
```python
upload = await client.files.create_upload(
    file_path="...",
    file_name="document.pdf"
)
```

#### Send File Upload
```python
await upload.send()
```

#### Complete File Upload
```python
await upload.complete()
```

### SDK-Exclusive Features

#### Simple Upload
Not in API - handles upload mode selection automatically.

```python
# Upload with automatic mode selection
file = await client.files.upload(
    file_path="document.pdf",
    parent=page
)

# Small files: single_part
# Large files: multi_part
```

#### Upload from URL
Not in API - requires external_url mode.

```python
file = await client.files.upload_from_url(
    url="https://example.com/image.png",
    parent=page
)
```

#### Upload Progress
Not in API - requires tracking uploaded bytes.

```python
async def progress_callback(uploaded, total):
    print(f"{uploaded}/{total} bytes")

file = await client.files.upload(
    file_path="large.zip",
    progress_callback=progress_callback
)
```

#### Bulk Upload
Not in API - requires parallel upload management.

```python
files = await client.files.upload_bulk(
    file_paths=["doc1.pdf", "doc2.pdf", "doc3.pdf"],
    parent=page
)
```

## Workspace Manager

### SDK-Exclusive Features

This entire manager doesn't exist in the Notion API.

#### Workspace Information
Aggregated from various API responses.

```python
workspace = client.workspace

print(workspace.name)
print(workspace.id)
print(workspace.icon)
```

#### Workspace Users
Cached user directory.

```python
# Pre-populate user cache
await workspace.refresh_users()

# Get all users
users = workspace.users

# Find user
user = workspace.find_user(email="john@example.com")
user = workspace.find_user(name="John Doe")
```

#### Workspace Statistics
Computed from cached data.

```python
stats = workspace.statistics

print(stats.page_count)
print(stats.database_count)
print(stats.user_count)
print(stats.bot_count)
```

## Cross-Cutting Features

### Async Iterators
All list/query operations support async iteration.

```python
# Automatic pagination
async for page in database.query():
    process(page)

# With limit
async for page in database.query().limit(10):
    process(page)

# Collect to list
pages = await database.query().collect()
```

### Error Handling
Semantic exceptions with helpful messages.

```python
try:
    page = await client.pages.get(page_id)
except PageNotFound:
    print("Page doesn't exist")
except PermissionError:
    print("No access to this page")
except RateLimited:
    print("Too many requests, retry later")
```

### Retry Logic
Automatic retry with exponential backoff.

```python
client = NotionClient(
    auth=token,
    max_retries=3,
    retry_backoff=True
)
```

### Rate Limiting
Respect rate limits automatically.

```python
# Configure behavior
client = NotionClient(
    auth=token,
    rate_limit_strategy="wait"  # or "fail"
)
```

### Logging
Structured logging for debugging.

```python
client = NotionClient(
    auth=token,
    log_level="DEBUG",
    log_handler=handler
)
```

### Type Safety
Comprehensive type hints throughout.

```python
page: Page = await client.pages.get(page_id)
database: Database = await client.databases.get(database_id)
blocks: AsyncIterator[Block] = await page.children
```

## Priority Classification

### Tier 1: Critical (Massive Impact)
- User cache with instant lookups
- Async iterators for pagination
- Property shortcuts (`.title`, `.status`, etc.)
- Hierarchical navigation (`.parent`, `.children`)

### Tier 2: High (Frequently Used)
- List operations (`.all()`, `.filter()`)
- Find operations (`.find_by_title()`, etc.)
- Bulk operations (create_bulk, update_bulk)
- Enhanced query builders

### Tier 3: Medium (Nice to Have)
- Content operations (duplicate, copy, move)
- Advanced search (fuzzy, cache-first)
- Workspace manager
- Progress callbacks

### Tier 4: Future (Advanced Features)
- Event system (on_created, on_updated)
- Real-time synchronization
- Offline mode
- Optimistic concurrency control
