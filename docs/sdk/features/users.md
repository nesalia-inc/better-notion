# Users Feature

Comprehensive documentation of user-related operations and features in the Better Notion SDK.

## Overview

Users in Notion represent people and bots in a workspace. They appear as:
- **Creators**: `created_by` field on pages, blocks, databases
- **Editors**: `last_edited_by` field
- **Assignees**: In people property types
- **Mentions**: In comments, discussions, and text

**User Types:**
- **Person**: Human user with email
- **Bot**: Integration with owner information

## Features

### Core Operations

#### Get Current Bot User

```python
# Get bot user info for current integration
me = await client.users.me()

print(me.name)           # Bot name
print(me.type)           # "bot"
print(me.id)             # Bot user ID

# Owner information
if me.bot and me.bot.owner:
    owner_type = me.bot.owner.type
    print(f"Owner type: {owner_type}")

    if owner_type == "workspace":
        print("Owned by workspace")
    elif owner_type == "user" and me.bot.owner.user:
        print(f"Owned by: {me.bot.owner.user.name}")
```

**API Equivalent:** `GET /users/me`

**Error Handling:**
- Raises `PermissionError` if integration lacks user information capability

#### Get User by ID

```python
# Get specific user
user = await client.users.get(user_id)

print(user.name)         # Display name
print(user.type)         # "person" or "bot"
print(user.email)        # Email (for persons)
print(user.avatar_url)   # Avatar image

# Check user type
if user.is_person:
    print(f"Email: {user.email}")
elif user.is_bot:
    print("This is a bot")
```

**API Equivalent:** `GET /users/{user_id}`

**Error Handling:**
- Raises `UserNotFound` if user doesn't exist

#### List All Users

```python
# Iterate over all users
async for user in client.users.list():
    print(f"{user.name} ({user.type})")

# Collect all users
all_users = await client.users.list().collect()

# With page size
async for user in client.users.list(page_size=50):
    process(user)
```

**API Equivalent:** `GET /users` + pagination

**Enhancements:**
- Async iterator handles pagination
- Memory-efficient streaming
- Excludes guests (API behavior)

### Find Operations

#### Find by Email

```python
# Find user by exact email
user = await client.users.find_by_email("john@example.com")

if user:
    print(f"Found: {user.name}")
else:
    print("User not found")

# Case-insensitive
user = await client.users.find_by_email(
    "JOHN@EXAMPLE.COM".lower()
)
```

**API Equivalent:** `GET /users` + client filtering

**Why SDK-Exclusive:**
- Common operation (lookup user by email)
- Requires listing all users + filtering
- SDK handles search + returns match

#### Find by Name

```python
# Find by exact name
user = await client.users.find_by_name("John Doe")

# Partial match
users = await client.users.find_by_name(
    "John",
    exact=False
)

# Returns list of matches
for user in users:
    print(f"{user.name} ({user.email})")
```

**Why SDK-Exclusive:**
- Common pattern (search by name)
- API doesn't support search by name
- SDK handles fuzzy matching

### Cache Operations

#### Populate Cache

```python
# Load all users into cache
await client.users.populate_cache()

# Subsequent lookups are instant
user = client.users.cache.get(user_id)

if user:
    print(f"Cached: {user.name}")
else:
    # Not in cache, fetch from API
    user = await client.users.get(user_id)
```

**Why SDK-Exclusive:**
- Preload user directory
- Subsequent lookups are instant (no API calls)
- Useful for applications that reference users frequently

#### Cache Lookup

```python
# Instant lookup (no API call)
user = client.users.cache.get(user_id)

if user:
    print(f"Name: {user.name}")
    print(f"Email: {user.email}")
else:
    print("User not in cache")

# Check cache size
print(f"Cached users: {len(client.users.cache)}")

# Get all cached users
all_cached = client.users.cache.get_all()
people = [u for u in all_cached if u.is_person]
bots = [u for u in all_cached if u.is_bot]
```

**Cache Population:**

The user cache is populated from multiple sources:
1. Explicit `populate_cache()` call
2. `users.list()` iteration
3. `users.get()` responses
4. `created_by` fields in pages/blocks/databases
5. `last_edited_by` fields
6. People properties in query results

#### Cache Management

```python
# Check if user is cached
if user_id in client.users.cache:
    user = client.users.cache[user_id]

# Invalidate specific user
client.users.cache.invalidate(user_id)

# Clear all cache
client.users.cache.clear()

# Refresh cache
await client.users.populate_cache()
```

### User Type Operations

#### Person Users

```python
# Get person-specific info
if user.is_person:
    name = user.name
    email = user.email
    avatar = user.avatar_url

    # Display name with fallback
    display_name = user.display_name  # name or email or ID
```

#### Bot Users

```python
# Get bot-specific info
if user.is_bot:
    name = user.name
    owner = user.bot.owner if user.bot else None

    if owner and owner.type == "workspace":
        print("Workspace-owned bot")
    elif owner and owner.type == "user":
        print(f"Owned by: {owner.user.name}")
```

### Display Helpers

#### Display Name

```python
# Get display name with intelligent fallback
name = user.display_name

# Fallback chain:
# 1. user.name (if not empty)
# 2. user.email (if person)
# 3. "User {id}"

# Examples
user1.name = "John Doe"
print(user1.display_name)  # "John Doe"

user2.name = None
user2.email = "jane@example.com"
print(user2.display_name)  # "jane@example.com"

user3.name = None
user3.email = None
print(user3.display_name)  # "User abc-123-def"
```

#### Avatar URL

```python
# Get avatar URL or default
avatar = user.avatar_url  # May be None

# Helper to get default
def get_avatar(user: User, default: str | None = None) -> str | None:
    if user.avatar_url:
        return user.avatar_url
    if default:
        return default
    # Generate initials avatar
    if user.name:
        initials = "".join([n[0] for n in user.name.split()])[:2]
        return f"https://ui-avatars.com/api/?name={initials}"
    return None
```

### User Resolution

#### Resolve Multiple User IDs

```python
# Resolve list of user IDs to user objects
user_ids = [
    "user-id-1",
    "user-id-2",
    "user-id-3"
]

users = await client.users.resolve(user_ids)

for user in users:
    print(f"{user.display_name}")
```

**Why SDK-Exclusive:**
- Common pattern (resolve user mentions)
- Batch operation is more efficient
- Uses cache when possible

#### Build User Directory

```python
# Build lookup dictionary
directory = await client.users.build_directory()

# Quick lookups
user = directory.get(user_id)
if user:
    print(user.name)

# Directory is just a dict
directory = {
    "id-1": user1,
    "id-2": user2,
    "id-3": user3
}
```

### Advanced Patterns

#### Find Users by Domain

```python
# Find all users from a company domain
async def find_users_by_domain(domain: str) -> list[User]:
    users = []
    async for user in client.users.list():
        if user.is_person and user.email:
            if user.email.endswith(f"@{domain}"):
                users.append(user)
    return users

# Use
company_users = await find_users_by_domain("example.com")
for user in company_users:
    print(user.name)
```

#### User Statistics

```python
# Get user statistics
async def user_statistics() -> dict:
    people_count = 0
    bots_count = 0

    async for user in client.users.list():
        if user.is_person:
            people_count += 1
        elif user.is_bot:
            bots_count += 1

    return {
        "total": people_count + bots_count,
        "people": people_count,
        "bots": bots_count
    }

# Use
stats = await user_statistics()
print(f"Total: {stats['total']}")
print(f"People: {stats['people']}")
print(f"Bots: {stats['bots']}")
```

#### Active Users

```python
# Find users who recently created/edited content
async def find_active_users(days: int = 7) -> list[User]:
    cutoff = datetime.now() - timedelta(days=days)
    active_user_ids = set()

    # Check recent pages
    async for page in client.pages.all():
        if page.last_edited_time > cutoff:
            active_user_ids.add(page.last_edited_by.id)

    # Resolve to user objects
    return await client.users.resolve(list(active_user_ids))

# Use
active = await find_active_users(days=30)
print(f"Active users (30 days): {len(active)}")
```

#### User Properties Aggregation

```python
# Aggregate pages created by each user
async def pages_by_user() -> dict[User, int]:
    page_counts = defaultdict(int)

    async for page in client.pages.all():
        if page.created_by:
            user = await client.users.get(page.created_by.id)
            page_counts[user] += 1

    return dict(page_counts)

# Use
counts = await pages_by_user()
for user, count in sorted(counts.items(), key=lambda x: x[1], reverse=True):
    print(f"{user.display_name}: {count} pages")
```

## Implementation Considerations

### User Object Model

```python
class User(BaseEntity):
    id: str
    type: str  # "person" or "bot"
    name: str | None
    avatar_url: str | None
    email: str | None  # For persons
    bot: BotInfo | None  # For bots

    # Type checking
    @property
    def is_person(self) -> bool
    @property
    def is_bot(self) -> bool

    # Display helpers
    @property
    def display_name(self) -> str
    @property
    def email(self) -> str | None

    # Bot-specific
    @property
    def owner(self) -> OwnerInfo | None
    @property
    def workspace_name(self) -> str | None
```

### Cache Implementation

```python
class UserCache:
    def get(self, user_id: str) -> User | None
    def get_all(self) -> list[User]
    def set(self, user_id: str, user: User) -> None
    def invalidate(self, user_id: str) -> None
    def clear(self) -> None
    def __contains__(self, user_id: str) -> bool
    def __len__(self) -> int
    def __getitem__(self, user_id: str) -> User
```

### Cache Population Strategy

**Implicit Population:**
```python
# When processing pages, users are cached automatically
async for page in database.query():
    # These populate the cache
    creator = page.created_by
    editor = page.last_edited_by

    # Subsequent lookups are instant
    creator = client.users.cache.get(page.created_by.id)
```

**Explicit Population:**
```python
# Load all users upfront
await client.users.populate_cache()

# Useful for:
# - Applications with frequent user lookups
# - User selection dropdowns
# - User attribution features
```

### Email Handling

**Privacy Considerations:**
```python
# Email requires user information capability
if user.email:
    # Email is available
    send_email(user.email)
else:
    # Integration lacks capability
    print("Email not available")

# Always check before using
email = user.email if user.email else None
```

**Case Sensitivity:**
```python
# Email lookups are case-insensitive
user1 = await client.users.find_by_email("john@example.com")
user2 = await client.users.find_by_email("JOHN@EXAMPLE.COM")
# Both return the same user
```

## Error Scenarios

| Scenario | Error | Solution |
|----------|-------|----------|
| User doesn't exist | `UserNotFound` | Verify ID |
| No user capability | `PermissionError` | Enable user information |
| Email not accessible | `None` returned | Check capabilities |
| Rate limit | `RateLimited` | SDK retries |

## Performance Considerations

### Optimal Patterns

```python
# GOOD: Use cache for repeated lookups
await client.users.populate_cache()
for page_id in page_ids:
    page = await client.pages.get(page_id)
    creator = client.users.cache.get(page.created_by.id)  # Instant

# AVOID: Repeated API calls
for page_id in page_ids:
    page = await client.pages.get(page_id)
    creator = await client.users.get(page.created_by.id)  # API call each time

# GOOD: Batch resolve
users = await client.users.resolve(user_ids)  # Efficient

# AVOID: Individual lookups
for user_id in user_ids:
    user = await client.users.get(user_id)  # Many API calls
```

### Cache Warming Strategies

**Strategy 1: Populate on startup**
```python
# App initialization
async def startup():
    await client.users.populate_cache()
    logger.info(f"Loaded {len(client.users.cache)} users")
```

**Strategy 2: Lazy load**
```python
# Load users as needed
async def get_user(user_id: str) -> User:
    # Check cache first
    user = client.users.cache.get(user_id)
    if user:
        return user

    # Fetch from API
    return await client.users.get(user_id)
```

**Strategy 3: Background refresh**
```python
# Periodic cache refresh
async def refresh_user_cache():
    while True:
        await asyncio.sleep(3600)  # Every hour
        await client.users.populate_cache()
```

## Integration with Other Features

### Pages

```python
# Page creators/editors
page = await client.pages.get(page_id)

creator = page.created_by  # User object (cached)
editor = page.last_edited_by  # User object (cached)
```

### Databases

```python
# Database creators/editors
database = await client.databases.get(db_id)

creator = database.created_by
editor = database.last_edited_by
```

### Blocks

```python
# Block creators/editors
block = await client.blocks.get(block_id)

creator = block.created_by
editor = block.last_edited_by
```

### Comments

```python
# Comment authors
comment = await client.comments.get(comment_id)

author = comment.author  # User object
```

### People Properties

```python
# People properties in pages
assignees = page.get_property("Assignee")  # list[User]

for user in assignees:
    print(user.display_name)

# Set people property
await client.pages.update(
    page,
    properties={
        "Assignee": [current_user]
    }
)
```

## Future Enhancements

### Tier 2 (High Priority)
- [ ] User groups/teams (if API adds support)
- [ ] User preferences (if API adds support)

### Tier 3 (Medium Priority)
- [ ] User activity tracking
- [ ] User relationship graphs
- [ ] Advanced user search

### Tier 4 (Future)
- [ ] Real-time user presence
- [ ] User collaboration features
- [ ] User analytics
