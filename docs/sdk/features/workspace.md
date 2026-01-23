# Workspace Feature

Comprehensive documentation of workspace-related operations and features in the Better Notion SDK.

## Overview

The Workspace represents the Notion workspace and provides:
- **Workspace metadata**: Name, ID, icon
- **User directory**: All users in the workspace
- **Resource inventory**: Pages, databases, blocks
- **Statistics**: Counts and aggregates

**Important:** This is an SDK-exclusive feature. The Notion API doesn't have a dedicated "workspace" endpoint. Workspace information is aggregated from various API responses.

## Features

### Workspace Information

#### Get Workspace Details

```python
# Access workspace through client
workspace = client.workspace

print(workspace.name)  # Workspace name
print(workspace.id)    # Workspace ID
print(workspace.icon)  # Workspace icon (emoji or image)
```

**API Equivalent:** Aggregated from `/users/me` response

**Why SDK-Exclusive:**
- API doesn't provide workspace endpoint
- SDK aggregates workspace information from various responses
- Convenient access to workspace-level data

#### Workspace Properties

```python
# Basic properties
name = workspace.name
id = workspace.id
icon = workspace.icon

# Bot user info (your integration)
bot_user = workspace.bot_user
print(bot_user.name)  # Integration name
```

### User Directory

#### Refresh User Cache

```python
# Populate user directory
await workspace.refresh_users()

# Fetches all users via /users endpoint
# Stores in cache for instant lookups

print(f"Loaded {len(workspace.users)} users")
```

**Why SDK-Exclusive:**
- One-time operation to load all users
- Subsequent user lookups are instant
- Useful for applications with frequent user references

#### Get All Users

```python
# Get all users (cached)
users = workspace.users

people = [u for u in users if u.is_person]
bots = [u for u in users if u.is_bot]

print(f"People: {len(people)}")
print(f"Bots: {len(bots)}")
```

#### Find User by Email

```python
# Find user in directory
user = workspace.find_user(email="john@example.com")

if user:
    print(f"Found: {user.name}")
else:
    print("User not found")
```

**Why SDK-Exclusive:**
- Common operation (lookup by email)
- Scans cached user directory
- No API call required if cache is populated

#### Find User by Name

```python
# Find user by name
user = workspace.find_user(name="John Doe")

# Partial match
users = workspace.find_user(name="John", exact=False)

# Returns list of matches
for user in users:
    print(user.name)
```

#### User Search

```python
# Search users by attribute
async def search_users(
    query: str
) -> list[User]:
    """Search users by name or email."""
    results = []

    for user in workspace.users:
        # Check name
        if user.name and query.lower() in user.name.lower():
            results.append(user)
            continue

        # Check email
        if user.email and query.lower() in user.email.lower():
            results.append(user)

    return results

# Use
matches = await search_users("john")
print(f"Found {len(matches)} users")
```

### Workspace Resources

#### List All Databases

```python
# Iterate over all databases
async for database in workspace.databases():
    print(database.title)

# Collect all
databases = await workspace.databases().collect()
```

**Why SDK-Exclusive:**
- Semantic operation ("workspace databases")
- Wraps search with filter
- More intuitive than API

#### List All Pages

```python
# Iterate over all pages
async for page in workspace.pages():
    print(page.title)

# Collect all
pages = await workspace.pages().collect()
```

#### Resource Statistics

```python
# Get workspace statistics
stats = workspace.statistics

print(f"Total pages: {stats.page_count}")
print(f"Total databases: {stats.database_count}")
print(f"Total users: {stats.user_count}")
print(f"Bot users: {stats.bot_count}")

# Breakdown by type
print(f"People: {stats.people_count}")
print(f"Bots: {stats.bot_count}")
```

**Why SDK-Exclusive:**
- API doesn't provide statistics
- SDK computes from cached data
- Useful for dashboard/overview

### Advanced Operations

#### Resource Aggregation

```python
# Aggregate resources by type
async def get_resources_by_type() -> dict:
    """Group all resources by type."""
    resources = {
        "databases": [],
        "pages": [],
        "users": []
    }

    # Databases
    async for db in workspace.databases():
        resources["databases"].append(db)

    # Pages
    async for page in workspace.pages():
        resources["pages"].append(page)

    # Users
    resources["users"] = workspace.users

    return resources

# Use
resources = await get_resources_by_type()
print(f"Databases: {len(resources['databases'])}")
print(f"Pages: {len(resources['pages'])}")
print(f"Users: {len(resources['users'])}")
```

#### User Activity

```python
# Find active users (who created/edited recently)
async def active_users(days: int = 30) -> list[User]:
    """Find users active in last N days."""
    cutoff = datetime.now() - timedelta(days=days)
    active_ids = set()

    # Check pages
    async for page in workspace.pages():
        if page.last_edited_time > cutoff:
            active_ids.add(page.last_edited_by.id)

    # Resolve to users
    return [
        workspace.find_user_by_id(user_id)
        for user_id in active_ids
    ]

# Use
active = await active_users(days=7)
print(f"Active users (7 days): {len(active)}")
for user in active:
    print(f"  {user.display_name}")
```

#### Content Statistics

```python
# Analyze workspace content
async def content_statistics() -> dict:
    """Get detailed content statistics."""
    stats = {
        "total_blocks": 0,
        "blocks_by_type": defaultdict(int),
        "pages_with_children": 0,
        "databases_with_entries": 0
    }

    # Analyze pages
    async for page in workspace.pages():
        async for block in page.descendants():
            stats["total_blocks"] += 1
            stats["blocks_by_type"][block.type] += 1

        if page.has_children:
            stats["pages_with_children"] += 1

    # Analyze databases
    async for database in workspace.databases():
        entry_count = 0
        async for page in database.pages():
            entry_count += 1

        if entry_count > 0:
            stats["databases_with_entries"] += 1

    return stats

# Use
stats = await content_statistics()
print(f"Total blocks: {stats['total_blocks']}")
print(f"Block types: {dict(stats['blocks_by_type'])}")
```

#### Workspace Overview

```python
# Generate workspace overview
async def workspace_overview() -> dict:
    """Generate comprehensive workspace overview."""
    return {
        "workspace": {
            "name": workspace.name,
            "id": workspace.id
        },
        "users": {
            "total": len(workspace.users),
            "people": len([u for u in workspace.users if u.is_person]),
            "bots": len([u for u in workspace.users if u.is_bot])
        },
        "resources": {
            "databases": await workspace.databases().count(),
            "pages": await workspace.pages().count()
        },
        "statistics": workspace.statistics
    }

# Use
overview = await workspace_overview()
print(json.dumps(overview, indent=2))
```

### User Management

#### User Directory Refresh Strategy

```python
# Periodic refresh
async def maintain_user_cache():
    """Keep user cache fresh."""
    while True:
        await workspace.refresh_users()
        await asyncio.sleep(3600)  # Every hour

# Or refresh on demand
async def get_user_fresh(user_id: str) -> User:
    """Get user, refreshing cache if needed."""
    user = workspace.find_user_by_id(user_id)

    if not user:
        # Cache not populated or user not found
        await workspace.refresh_users()
        user = workspace.find_user_by_id(user_id)

    return user
```

#### User Groups (Future)

```python
# If Notion adds user groups/teams
async def get_users_by_group(group_name: str) -> list[User]:
    """Get all users in a group."""
    users = []

    async for user in workspace.users:
        if hasattr(user, 'groups') and group_name in user.groups:
            users.append(user)

    return users

# Use
engineering = await get_users_by_group("Engineering")
for user in engineering:
    print(user.name)
```

### Workspace Monitoring

#### Recent Activity

```python
# Get recent activity across workspace
async def recent_activity(hours: int = 24) -> list[dict]:
    """Get recent activity in workspace."""
    cutoff = datetime.now() - timedelta(hours=hours)
    activity = []

    async for page in workspace.pages():
        if page.last_edited_time > cutoff:
            activity.append({
                "type": "page_edit",
                "resource": page,
                "user": page.last_edited_by,
                "time": page.last_edited_time
            })

    return sorted(activity, key=lambda x: x['time'], reverse=True)

# Use
activity = await recent_activity(hours=1)
print(f"Activity in last hour: {len(activity)}")
for item in activity[:10]:
    print(f"  {item['user'].name} edited {item['resource'].title}")
```

#### Growth Tracking

```python
# Track workspace growth over time
async def track_growth() -> dict:
    """Track resource creation over time."""
    by_date = defaultdict(lambda: {"pages": 0, "databases": 0})

    async for page in workspace.pages():
        date = page.created_time.date()
        by_date[date]["pages"] += 1

    async for database in workspace.databases():
        date = database.created_time.date()
        by_date[date]["databases"] += 1

    return dict(by_date)

# Use
growth = await track_growth()
for date, counts in sorted(growth.items()):
    print(f"{date}: {counts['pages']} pages, {counts['databases']} databases")
```

## Implementation Considerations

### Workspace Object Model

```python
class Workspace:
    name: str
    id: str
    icon: str | None
    bot_user: User

    # User directory
    @property
    def users(self) -> list[User]

    # Resource access
    async def databases() -> AsyncIterator[Database]
    async def pages() -> AsyncIterator[Page]

    # Statistics
    @property
    def statistics(self) -> WorkspaceStatistics

    # User operations
    async def refresh_users() -> None
    def find_user(*, email: str | None, name: str | None) -> User | None
    def find_user_by_id(user_id: str) -> User | None
```

### Statistics Model

```python
class WorkspaceStatistics:
    page_count: int
    database_count: int
    user_count: int
    people_count: int
    bot_count: int
    block_count: int  # If computed
```

### Cache Strategy

**Populated from:**
- `/users/me` response (workspace info, bot user)
- `/users` response (user directory)
- Search results (resources)
- Individual resource lookups

**Refresh strategy:**
```python
# Manual refresh
await workspace.refresh_users()

# Auto-refresh (optional)
workspace = client.workspace(auto_refresh=True, refresh_interval=3600)
```

## Error Scenarios

| Scenario | Error | Solution |
|----------|-------|----------|
| Workspace not accessible | `PermissionError` | Check integration access |
| User not found in cache | `None` returned | Refresh cache |
| Rate limit during refresh | `RateLimited` | SDK retries |

## Performance Considerations

### Optimal Patterns

```python
# GOOD: Populate cache once
await workspace.refresh_users()
# Subsequent lookups are instant
user = workspace.find_user(email="john@example.com")

# AVOID: Repeated API calls
user = await client.users.find_by_email("john@example.com")  # API call each time

# GOOD: Use statistics property (cached)
stats = workspace.statistics
print(f"Pages: {stats.page_count}")

# AVOID: Re-count resources
pages = await workspace.pages().collect()  # Expensive
print(f"Pages: {len(pages)}")
```

### Cache Warming

```python
# App initialization
async def init_workspace():
    # Warm user cache
    await workspace.refresh_users()

    # Warm resource cache (optional, expensive)
    # await workspace.databases().collect()
    # await workspace.pages().collect()

    logger.info("Workspace cache ready")
```

## Integration with Other Features

### Users

```python
# Workspace user directory
users = workspace.users

# Same as client.users but:
# - Pre-populated if refresh_users() called
# - Instant access (no API calls)
```

### Pages

```python
# Workspace pages
async for page in workspace.pages():
    print(page.title)

# Includes all pages in workspace
# regardless of parent
```

### Databases

```python
# Workspace databases
async for database in workspace.databases():
    print(database.title)

# Includes all databases
# regardless of location
```

### Search

```python
# Search within workspace
async for result in client.search.query("project"):
    # Searches entire workspace
    process(result)
```

## Future Enhancements

### Tier 2 (High Priority)
- [ ] Workspace settings (if API adds support)
- [ ] Workspace permissions
- [ ] Workspace members management

### Tier 3 (Medium Priority)
- [ ] Workspace templates
- [ ] Workspace analytics dashboard
- [ ] Resource usage metrics

### Tier 4 (Future)
- [ ] Workspace-level search
- [ ] Workspace export
- [ ] Workspace backup/restore
- [ ] Multi-workspace support
