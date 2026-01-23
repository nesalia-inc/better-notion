# Databases Feature

Comprehensive documentation of database-related operations and features in the Better Notion SDK.

## Overview

Databases in Notion are structured containers for pages with a defined schema (properties). Each database:
- **Defines schema**: Property types and configurations
- **Contains pages**: Entries that follow the schema
- **Is queryable**: Filter, sort, and search pages
- **Can be nested**: Belongs to a page or workspace

## Features

### Core CRUD Operations

#### Retrieve a Database

```python
# Get database by ID
database = await client.databases.get(database_id)

# Access database properties
print(database.title)         # "Tasks"
print(database.description)   # Optional description
print(database.properties)    # Property schema

# Iterate over properties
for prop_name, prop_config in database.properties.items():
    print(f"{prop_name}: {prop_config.type}")
```

**API Equivalent:** `GET /databases/{database_id}`

**Error Handling:**
- Raises `DatabaseNotFound` if database doesn't exist
- Raises `PermissionError` if no access

#### Create a Database

```python
# Create in a page
database = await client.databases.create(
    parent=page,
    title="Tasks",
    properties={
        "Name": PropertyConfig.title(),
        "Status": PropertyConfig.select(
            options=["Todo", "In Progress", "Done"]
        ),
        "Priority": PropertyConfig.number(),
        "Due Date": PropertyConfig.date(),
        "Assignee": PropertyConfig.people()
    }
)

# With description
database = await client.databases.create(
    parent=page,
    title="Projects",
    description="Track all projects",
    properties={...}
)
```

**API Equivalent:** `POST /databases`

**Enhancements:**
- `PropertyConfig` builder for creating properties
- Simplified select/option creation
- Type-safe property configuration

#### Update a Database

```python
# Update title
await client.databases.update(
    database,
    title="New Title"
)

# Add/modify properties
await client.databases.update(
    database,
    properties={
        "Name": PropertyConfig.title(),
        "Status": PropertyConfig.select(...),
        "New Field": PropertyConfig.text()  # Add new property
    }
)

# Update description
await client.databases.update(
    database,
    description="Updated description"
)
```

**API Equivalent:** `PATCH /databases/{database_id}`

#### Delete a Database

```python
# Delete database (moves to trash)
await client.databases.delete(database)

# Note: This is a soft delete (archive)
# To permanently delete, use archive=True
await client.databases.delete(database, archive=True)
```

**API Equivalent:** `PATCH /databases/{database_id}` with archived=true

### List Operations

#### List All Databases

```python
# Iterate over all databases in workspace
async for database in client.databases.all():
    print(database.title)

# Collect all databases
all_databases = await client.databases.all().collect()

# With limit
async for database in client.databases.all().limit(50):
    process(database)
```

**API Equivalent:** `POST /search` with filter={"value": "database", "property": "object"}

**Why SDK-Exclusive:** User intent is "get all databases", not "search for database objects".

### Find Operations

#### Find by Title

```python
# Exact match
database = await client.databases.find_by_title("Tasks")

# Substring match
databases = await client.databases.find_by_title(
    "Project",
    exact=False
)

# Returns None if not found
database = await client.databases.find_by_title("Nonexistent")
if database:
    print(f"Found: {database.title}")
```

**API Equivalent:** `POST /search` + manual filtering

**Why SDK-Exclusive:**
- Common operation (find database by name)
- API returns all results, requires filtering
- SDK handles search + filtering + returns first match

### Query Operations

#### Basic Query

```python
# Get all pages in database
async for page in database.query():
    print(page.title)

# Collect all pages
pages = await database.query().collect()

# With limit
async for page in database.query().limit(100):
    process(page)
```

**API Equivalent:** `POST /databases/{database_id}/query` + pagination

**Enhancements:**
- Async iterator handles pagination
- No manual cursor management
- Memory-efficient streaming

#### Simple Filtering

```python
# Filter by property value
async for page in database.query(status="Done"):
    print(page.title)

# Multiple filters
async for page in database.query(
    status="In Progress",
    priority=5
):
    process(page)
```

**API Equivalent:** `POST /databases/{database_id}/query` with filter object

**Why SDK-Exclusive:**
- Transforms simple kwargs into complex filter structure
- Users don't need to know filter syntax
- More Pythonic

#### Advanced Filtering

```python
# Builder pattern for complex queries
results = await (database.query()
    .filter(status="In Progress")
    .filter(priority__gte=5)
    .sort("due_date", "ascending")
    .limit(10)
    .collect())

# Comparison operators
async for page in database.query(priority__gte=5):
    process(page)

async for page in database.query(due_date__before="2025-02-01"):
    process(page)

# Multiple conditions
async for page in (database.query()
    .filter(status="In Progress")
    .and_(priority__gte=5)
    .or_(priority__is_null=True)):
    process(page)
```

**Supported Operators:**
- `__eq`, `__ne`: equals, not equals
- `__gt`, `__gte`: greater than, greater than or equal
- `__lt`, `__lte`: less than, less than or equal
- `__contains`: contains (for text, multi-select)
- `__starts_with`, `__ends_with`: text matching
- `__is_null`, `__is_not_null`: null checks
- `__before`, `__after`: date comparisons
- `__in`: in list (for select)
- `__and__`, `__or__`: logical operators

#### Sorting

```python
# Sort by property
async for page in database.query().sort("priority", "descending"):
    print(page.title, page.get_property("priority"))

# Multi-field sort
async for page in (database.query()
    .sort("status", "ascending")
    .sort("priority", "descending")):
    process(page)

# Sort by timestamp
async for page in database.query().sort("last_edited_time", "ascending"):
    process(page)
```

### Query Helpers

#### Recent Pages

```python
# Get pages modified in last N days
recent = await database.recent(days=7)

# Get pages created today
today = await database.recent(days=0)

# Returns list of Page objects
for page in recent:
    print(f"{page.title} - {page.last_edited_time}")
```

**API Equivalent:** Query with last_edited_time filter + date calculation

**Why SDK-Exclusive:**
- Common operation ("show me recent changes")
- Abstracts date calculation and filter structure

#### Filter by Property

```python
# Filter by single property
pages = await database.filter_by("Status", "Done")

# Case-insensitive text search
pages = await database.filter_by("Name", "project", exact=False)

# Returns list of matching pages
for page in pages:
    print(page.title)
```

#### Filter by Multiple Properties

```python
# Filter by multiple properties
pages = await database.filter_multiple(
    status="In Progress",
    priority__gte=5,
    assignee=current_user
)

# All conditions must match (AND)
for page in pages:
    print(page.title)
```

### Database Pages

#### Iterate Over Pages

```python
# Get all pages (cached)
async for page in database.pages:
    print(page.title)

# More efficient than query for simple iteration
# Uses cached data if available
```

**Why SDK-Exclusive:**
- Semantic operation ("pages in this database")
- Uses cache when possible
- Simpler than full query

#### Find Page by Title

```python
# Find page by exact title
page = await database.get_page_by_title("Task 1")

# Substring match
pages = await database.get_page_by_title("Task", exact=False)

# Returns None if not found
page = await database.get_page_by_title("Nonexistent")
if page:
    print(f"Found: {page.title}")
```

**API Equivalent:** Query database + filter by title property

**Why SDK-Exclusive:**
- Common pattern (find page by name in database)
- Handles title property lookup automatically
- Returns Page object, not search results

### Property Schema

#### Get Property Configuration

```python
# Get property by name
prop = database.get_property("Status")

if prop:
    print(f"Type: {prop.type}")
    if prop.type == "select":
        print(f"Options: {prop.options}")
```

#### Check Property Existence

```python
# Check if property exists
has_status = database.has_property("Status")
has_due_date = database.has_property("Due Date")

if has_status:
    # Safe to use
    status = page.get_property("Status")
```

#### Get Property Type

```python
# Get property type
prop_type = database.get_property_type("Status")

if prop_type == "select":
    # Handle select property
    status = page.get_property("Status")
elif prop_type == "date":
    # Handle date property
    date = page.get_property("Due Date")
```

#### List Property Names

```python
# Get all property names
names = database.property_names
print(names)  # ["Name", "Status", "Priority", ...]

# Iterate over properties
for name in database.property_names:
    prop_type = database.get_property_type(name)
    print(f"{name}: {prop_type}")
```

### Cache Operations

#### Cache Lookup

```python
# Instant lookup (no API call)
database = client.databases.cache.get(database_id)

if database:
    print(f"Cached: {database.title}")
else:
    database = await client.databases.get(database_id)
```

**Populated From:**
- `databases.get()` responses
- `databases.all()` iteration
- `search.query()` results
- Parent page references

#### Cache Management

```python
# Check cache size
print(f"Cached databases: {len(client.databases.cache)}")

# Get all cached databases
all_cached = client.databases.cache.get_all()

# Invalidate specific database
client.databases.cache.invalidate(database_id)

# Clear all cache
client.databases.cache.clear()
```

## Property Configuration

### Property Types

#### Title

```python
PropertyConfig.title()
```

#### Text

```python
PropertyConfig.text()
```

#### Number

```python
PropertyConfig.number(
    format="number"  # or "dollar", "euro", "percentage", etc.
)
```

#### Select

```python
PropertyConfig.select(
    options=["Todo", "In Progress", "Done"],
    colors=["gray", "blue", "green"]  # Optional
)
```

#### Multi-Select

```python
PropertyConfig.multi_select(
    options=["Tag1", "Tag2", "Tag3"]
)
```

#### Date

```python
PropertyConfig.date()
```

#### People

```python
PropertyConfig.people()
```

#### Files

```python
PropertyConfig.files()
```

#### Checkbox

```python
PropertyConfig.checkbox()
```

#### URL

```python
PropertyConfig.url()
```

#### Email

```python
PropertyConfig.email()
```

#### Phone

```python
PropertyConfig.phone()
```

#### Formula

```python
PropertyConfig.formula(
    expression="prop(\"Status\") == \"Done\""
)
```

#### Relation

```python
PropertyConfig.relation(
    database_id=target_database.id
)
```

#### Rollup

```python
PropertyConfig.rollup(
    relation_property_name="Related Tasks",
    rollup_property_name="Status",
    function="show_original"  # or count, etc.
)
```

### Creating Properties

#### Simple Property

```python
properties = {
    "Name": PropertyConfig.title(),
    "Status": PropertyConfig.select(["Todo", "Done"])
}
```

#### With Options

```python
properties = {
    "Priority": PropertyConfig.select(
        options=["Low", "Medium", "High"],
        colors=["gray", "yellow", "red"]
    )
}
```

#### Advanced Configuration

```python
properties = {
    "Progress": PropertyConfig.formula(
        expression="prop(\"Completed\") / prop(\"Total\") * 100"
    ),
    "Related Tasks": PropertyConfig.relation(
        database_id=tasks_db.id,
        dual_property="Related Project"
    )
}
```

## Advanced Patterns

### Dynamic Query Building

```python
# Build query based on conditions
query = database.query()

if status_filter:
    query = query.filter(status=status_filter)

if priority_min:
    query = query.filter(priority__gte=priority_min)

if sort_by:
    query = query.sort(sort_by, sort_order)

# Execute
async for page in query:
    process(page)
```

### Aggregation

```python
# Count by status
from collections import Counter

status_counts = Counter()
async for page in database.query():
    status = page.get_property("Status", default="Unknown")
    status_counts[status] += 1

print(status_counts)
# Output: Counter({'Done': 45, 'In Progress': 12, 'Todo': 23})
```

### Grouping

```python
# Group by status
from collections import defaultdict

by_status = defaultdict(list)
async for page in database.query():
    status = page.get_property("Status", default="Unknown")
    by_status[status].append(page)

# Access groups
for status, pages in by_status.items():
    print(f"{status}: {len(pages)} pages")
```

### Pagination with Processing

```python
# Process in batches
batch_size = 50

async for batch in database.query().batch(batch_size):
    # batch is list of Page objects
    await export_batch(batch)
```

### Cross-Database Query

```python
# Query across multiple databases
databases = [
    await client.databases.get(db_id)
    for db_id in database_ids
]

# Collect all pages
all_pages = []
for database in databases:
    async for page in database.query():
        all_pages.append(page)

# Process
for page in all_pages:
    process(page)
```

## Implementation Considerations

### Database Object Model

```python
class Database(BaseEntity):
    id: str
    title: str
    description: str | None
    properties: dict[str, PropertyConfig]

    # Query methods
    async def query(**filters) -> AsyncIterator[Page]
    async def recent(days: int) -> list[Page]
    async def filter_by(name: str, value: Any) -> list[Page]

    # Pages
    async def pages() -> AsyncIterator[Page]
    async def get_page_by_title(title: str) -> Page | None

    # Schema
    def get_property(name: str) -> PropertyConfig | None
    def has_property(name: str) -> bool
    def get_property_type(name: str) -> str | None
    @property
    def property_names(self) -> list[str]
```

### Query Builder

```python
class QueryBuilder:
    def filter(self, **conditions) -> QueryBuilder
    def and_(*conditions) -> QueryBuilder
    def or_(*conditions) -> QueryBuilder
    def sort(property: str, direction: str) -> QueryBuilder
    def limit(n: int) -> QueryBuilder
    def batch(size: int) -> AsyncIterator[list[Page]]

    async def collect() -> list[Page]
    async def first() -> Page | None
    def __aiter__() -> AsyncIterator[Page]
```

### Filter Translation

SDK translates Python expressions to Notion filter structure:

```python
# User provides:
database.query(status="Done", priority__gte=5)

# SDK generates:
{
    "filter": {
        "and": [
            {"property": "Status", "select": {"equals": "Done"}},
            {"property": "Priority", "number": {"greater_than_or_equal_to": 5}}
        ]
    }
}
```

## Error Scenarios

| Scenario | Error | Solution |
|----------|-------|----------|
| Database doesn't exist | `DatabaseNotFound` | Verify ID, check permissions |
| Invalid property | `ValidationError` | Check property exists in schema |
| Invalid filter | `QueryError` | Check property type matches filter |
| No access | `PermissionError` | Verify integration capabilities |
| Rate limit | `RateLimited` | SDK retries automatically |

## Performance Considerations

### Optimal Patterns

```python
# GOOD: Stream results
async for page in database.query():
    process(page)  # Process one at a time

# AVOID: Load all into memory
pages = await database.query().collect()  # Memory intensive

# GOOD: Use cache for repeated access
database = client.databases.cache.get(database_id)
if database:
    async for page in database.pages:
        process(page)

# AVOID: Re-fetch database
database = await client.databases.get(database_id)  # API call
async for page in database.pages:
    process(page)
```

### Query Optimization

```python
# GOOD: Specific filters
async for page in database.query(status="Done"):
    process(page)  # Fewer results

# AVOID: Fetch all then filter
async for page in database.query():
    if page.get_property("Status") == "Done":
        process(page)  # Wasteful
```

### Caching Strategy

**Populate cache:**
```python
# Warm cache with databases
async for database in client.databases.all():
    # Access populates cache
    print(database.title)

# Now instant lookups
database = client.databases.cache.get(database_id)
```

## Future Enhancements

### Tier 2 (High Priority)
- [ ] Database templates
- [ ] Property validation helpers
- [ ] Query result caching

### Tier 3 (Medium Priority)
- [ ] Cross-database queries
- [ ] Aggregation helpers (count, sum, avg)
- [ ] Query visualization (explain)

### Tier 4 (Future)
- [ ] Real-time query updates
- [ ] Query sharing/saving
- [ ] Advanced analytics
