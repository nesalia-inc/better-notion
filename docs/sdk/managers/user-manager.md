# UserManager

Ultra-thin wrapper to autonomous User class.

## Overview

`UserManager` is a **zero-logic wrapper** that delegates all operations to the autonomous `User` class. It focuses on caching and user lookup optimization.

**Key Principle**: Managers provide syntactic sugar. Entities contain all logic.

```python
# Via Manager (recommended - shorter)
user = await client.users.get(user_id)

# Via Entity directly (autonomous - same result)
user = await User.get(user_id, client=client)
```

## Architecture

```
NotionClient
    └── users: UserManager
              └── delegates to → User (autonomous)
```

## Key Feature: Cache Population

Unlike other managers, `UserManager` emphasizes cache population:

```python
# Pre-load ALL users (one-time operation)
await client.users.populate_cache()

# Now all lookups are instant (no API calls)
for page in pages:
    creator = client.users.cache.get(page.created_by_id)
    print(f"Created by: {creator.name}")  # Instant!
```

**Why this matters**: User lookups are common in loops. Without caching, each lookup = 1 API call (300ms).

## Implementation

```python
# better_notion/_sdk/managers/user_manager.py

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from better_notion._sdk.client import NotionClient
    from better_notion._sdk.models.user import User

class UserManager:
    """Ultra-thin wrapper to autonomous User class.

    Focuses on cache population and fast user lookups.

    Example:
        >>> # Via manager (recommended)
        >>> user = await client.users.get(user_id)
        >>>
        >>> # Via entity directly (autonomous)
        >>> user = await User.get(user_id, client=client)
    """

    def __init__(self, client: "NotionClient") -> None:
        """Initialize user manager.

        Args:
            client: NotionClient instance
        """
        self._client = client

    # ===== CRUD OPERATIONS =====

    async def get(self, user_id: str) -> "User":
        """Get user by ID (with cache lookup).

        Args:
            user_id: User UUID

        Returns:
            User object

        Raises:
            UserNotFound: If user doesn't exist

        Behavior:
            1. Check cache first (instant)
            2. If cached, return immediately
            3. If not cached, fetch from API
            4. Store in cache for next time

        Example:
            >>> user = await client.users.get(user_id)
            >>> print(f"{user.name} ({user.email})")
        """
        from better_notion._sdk.models.user import User

        return await User.get(user_id, client=self._client)

    # ===== CACHE MANAGEMENT =====

    async def populate_cache(self) -> None:
        """Load ALL users into cache.

        Fetches all users from API and stores them in cache.
        Subsequent get() calls will be instant memory lookups.

        Use case:
            Call this at startup if you'll be looking up many users.
            Avoids repeated API calls in loops.

        Performance:
            - One-time: N API calls (paginated)
            - Afterwards: Instant lookups

        Example:
            >>> # Pre-load all users
            >>> await client.users.populate_cache()
            >>>
            >>> # Now all lookups are instant
            >>> for page in pages:
            ...     user = client.users.cache.get(page.created_by_id)
            ...     print(f"Created by: {user.name}")  # No API call!
        """
        from better_notion._sdk.models.user import User

        # Clear existing cache
        self._client._user_cache.clear()

        # Fetch all users (handles pagination)
        async for user_data in self._client.api.users.list():
            user = User.from_data(self._client, user_data)
            self._client._user_cache.set(user.id, user)

    # ===== FINDING =====

    async def find_by_email(
        self,
        email: str
    ) -> "User | None":
        """Find user by email address.

        Args:
            email: User email address

        Returns:
            User object or None if not found

        Note:
            Searches cache first. If not in cache, returns None
            (doesn't fall back to API to avoid listing all users).

        Example:
            >>> user = await client.users.find_by_email("user@example.com")
            >>> if user:
            ...     print(f"Found: {user.name}")
            >>> else:
            ...     print("User not found (try populate_cache first)")
        """
        # Search in cache (linear scan but in-memory)
        for user in self._client._user_cache.get_all():
            if user.email == email:
                return user

        return None

    async def find_by_name(
        self,
        name: str
    ) -> "User | None":
        """Find user by name (case-insensitive).

        Args:
            name: User name to search for

        Returns:
            User object or None if not found

        Note:
            Searches cache first. Requires populate_cache() for full results.

        Example:
            >>> user = await client.users.find_by_name("John Doe")
            >>> if user:
            ...     print(f"Found: {user.email}")
        """
        # Search in cache
        name_lower = name.lower()
        for user in self._client._user_cache.get_all():
            if user.name.lower() == name_lower:
                return user

        return None

    # ===== CACHE ACCESS =====

    @property
    def cache(self) -> "Cache[User]":
        """Access to user cache.

        Returns:
            Cache object for users

        Example:
            >>> # Check if cached
            >>> if user_id in client.users.cache:
            ...     user = client.users.cache[user_id]
            >>>
            >>> # Get without API call
            >>> user = client.users.cache.get(user_id)
            >>>
            >>> # Get all cached users
            >>> all_users = client.users.cache.get_all()
        """
        return self._client._user_cache

    # ===== BULK OPERATIONS =====

    async def get_multiple(
        self,
        user_ids: list[str]
    ) -> list["User"]:
        """Get multiple users by IDs.

        Args:
            user_ids: List of user IDs

        Returns:
            List of User objects (in same order)

        Example:
            >>> user_ids = ["id1", "id2", "id3"]
            >>> users = await client.users.get_multiple(user_ids)
        """
        from better_notion._sdk.models.user import User

        users = []
        for user_id in user_ids:
            user = await User.get(user_id, client=self._client)
            users.append(user)

        return users
```

## Usage Examples

### Example 1: Basic Usage

```python
# Get user
user = await client.users.get(user_id)
print(f"Name: {user.name}")
print(f"Email: {user.email}")
print(f"Type: {user.type}")  # "person" or "bot"
```

### Example 2: Cache Population (Recommended)

```python
# ❌ WITHOUT CACHE - 60 seconds 🐌
pages = await database.query(client=client).collect()

for page in pages:
    creator = await client.users.get(page.created_by_id)  # API call each time
    print(f"{page.title} by {creator.name}")

# ✅ WITH CACHE - 1 second ⚡
await client.users.populate_cache()  # One-time: 300ms

for page in pages:
    creator = client.users.cache.get(page.created_by_id)  # Instant!
    print(f"{page.title} by {creator.name}")
```

### Example 3: Finding Users

```python
# Populate cache first
await client.users.populate_cache()

# Find by email
user = await client.users.find_by_email("user@example.com")
if user:
    print(f"Found: {user.name}")

# Find by name
user = await client.users.find_by_name("John Doe")
if user:
    print(f"Email: {user.email}")
```

### Example 4: Cache Statistics

```python
# Populate cache
await client.users.populate_cache()

# Check stats
stats = client.get_cache_stats()
user_stats = stats['user_cache']

print(f"Users cached: {user_stats['size']}")
print(f"Cache hit rate: {user_stats['hit_rate']:.1%}")
print(f"Cache hits: {user_stats['hits']}")
print(f"Cache misses: {user_stats['misses']}")
```

### Example 5: Direct Cache Access

```python
# Populate cache
await client.users.populate_cache()

# Check if user is cached
if user_id in client.users.cache:
    user = client.users.cache[user_id]  # Instant, no API call
else:
    user = await client.users.get(user_id)  # Fetch from API

# Get all cached users
all_users = client.users.cache.get_all()
print(f"Total users: {len(all_users)}")

# Get cache stats
stats = client.users.cache.stats
print(f"Hit rate: {stats.hit_rate:.1%}")
```

## Performance Impact

### Without Cache

```python
# 100 pages × 2 user lookups = 200 API calls
pages = await database.query(client=client).collect()

for page in pages:
    creator = await client.users.get(page.created_by_id)  # 300ms
    editor = await client.users.get(page.last_edited_by_id)  # 300ms

# Total: 200 × 300ms = 60 seconds
```

### With Cache

```python
# 1 populate call + 200 memory lookups
await client.users.populate_cache()  # 300ms (one-time)

for page in pages:
    creator = client.users.cache.get(page.created_by_id)  # ~0ms
    editor = client.users.cache.get(page.last_edited_by_id)  # ~0ms

# Total: 300ms + 200 × ~0ms = 0.3 seconds
```

**Result**: **200x faster** with caching!

## Design Decisions

### Q1: Why emphasize cache population?

**Decision**: `populate_cache()` as primary feature

**Rationale**:
- User lookups are extremely common in loops
- Workspace has limited users (typically < 100)
- Massive performance gain (200x faster)
- Simple API with clear benefits

```python
# ✅ Recommended pattern
await client.users.populate_cache()  # One-time setup

for page in pages:
    user = client.users.cache.get(page.created_by_id)  # Instant
```

### Q2: find_by_email() falls back to API?

**Decision**: No, only searches cache

**Rationale**:
- Avoids expensive `list()` call if not needed
- Explicit: user must call `populate_cache()` first
- Predictable performance (no surprise API calls)

```python
# ✅ Explicit: populate first
await client.users.populate_cache()
user = await client.users.find_by_email("user@example.com")

# ❌ Alternative (implicit): might trigger slow list() call
user = await client.users.find_by_email("user@example.com")
# Would need to fetch all users from API - slow!
```

### Q3: Cache auto-populate on first get?

**Decision**: No, manual populate only

**Rationale**:
- Predictable: no surprise API calls
- Explicit control: user decides when to populate
- Performance: user can batch lookups

```python
# ✅ Manual populate (our approach)
await client.users.populate_cache()  # Explicit

# ❌ Auto-populate (alternative)
user = await client.users.get(user_id)  # Might populate all users silently
```

## Best Practices

### DO ✅

```python
# Populate cache at startup
await client.users.populate_cache()

# Use cache for lookups in loops
for page in pages:
    user = client.users.cache.get(page.created_by_id)  # Instant

# Check cache before fetching
if user_id in client.users.cache:
    user = client.users.cache[user_id]
else:
    user = await client.users.get(user_id)
```

### DON'T ❌

```python
# Don't fetch users in loops without cache
for page in pages:
    user = await client.users.get(page.created_by_id)  # Slow!

# Don't use find_by_email() without populating first
user = await client.users.find_by_email("user@example.com")  # Returns None!

# Don't forget to populate cache
# Always call this if you'll be looking up users
await client.users.populate_cache()
```

## Related Documentation

- [NotionClient](../implementation/notion-client.md) - Client with managers
- [User Model](../models/user-model.md) - Autonomous User entity
- [Cache Strategy](../implementation/cache-strategy.md) - Detailed caching strategy
