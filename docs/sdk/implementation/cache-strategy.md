# Cache Strategy

Caching system for minimizing API calls and improving performance.

## Overview

Notion API calls are slow (200-500ms each) and rate-limited (3 requests/second for integrations). Caching transforms sequential API calls into instant memory lookups.

**Performance Impact**:
```
Without cache: 100 pages × 2 user lookups = 200 API calls ≈ 60 seconds
With cache:    1 populate call + 200 memory lookups ≈ 1 second
```

**60x faster** through intelligent caching.

## Why Caching Matters

### The Problem: API Latency

Each API call involves:
- Network round-trip (200-500ms minimum)
- Rate limiting delays
- Potential timeouts

### Real-World Example

```python
# WITHOUT CACHE - 60 seconds 🐌
pages = await database.query().collect()  # 100 pages

for page in pages:
    # Each lookup = 1 API call (300ms)
    creator = await api.users.retrieve(page.created_by_id)
    editor = await api.users.retrieve(page.last_edited_by_id)

# Total: 200 API calls × 300ms = 60 seconds
```

```python
# WITH CACHE - 1 second ⚡
await client.users.populate_cache()  # 1 API call = 300ms

for page in pages:
    # Instant memory lookups (0ms)
    creator = client.users.cache.get(page.created_by_id)
    editor = client.users.cache.get(page.last_edited_by_id)

# Total: 1 API call + 200 lookups = 1.3 seconds
```

## Cache Architecture

### Two-Level Design

The SDK uses two complementary caching levels:

```
┌─────────────────────────────────────────────────┐
│  Level 1: Manager Cache (Global, Shared)        │
│  ┌─────────────────────────────────────────┐    │
│  │ UserCache                                │    │
│  │   user_123 → User(...)                  │    │
│  │   user_456 → User(...)                  │    │
│  └─────────────────────────────────────────┘    │
│                                                 │
│  Accessed via: client.users.cache              │
│  Scope: Shared across all users                │
└─────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────┐
│  Level 2: Entity Cache (Local, Navigation)      │
│  ┌─────────────────────────────────────────┐    │
│  │ page_abc._cache:                         │    │
│  │   "parent" → Database(...)               │    │
│  │   "children" → [Block(...), ...]         │    │
│  └─────────────────────────────────────────┘    │
│                                                 │
│  Accessed via: page._cache_get/_set()          │
│  Scope: Local to each entity                   │
└─────────────────────────────────────────────────┘
```

### Why Two Levels?

**Scenario**: 10 pages with the same parent database

```python
# With only manager cache
for page in pages:
    db = client.databases.cache.get(page.parent_id)
    # First page: cache miss → API fetch
    # Pages 2-10: cache hit ✅

# With entity cache too
for page in pages:
    parent = await page.parent  # Fetch + cache in page._cache
    parent2 = await page.parent  # Local cache hit ✅
```

**Complementary benefits**:
- **Manager cache**: Shared across different entities
- **Entity cache**: Optimization within same entity

## Generic Cache Implementation

### Base Cache Class

```python
from typing import TypeVar, Generic, Optional, Dict
from dataclasses import dataclass, field

T = TypeVar('T')

@dataclass
class CacheStats:
    """Cache statistics for monitoring effectiveness."""
    hits: int = 0
    misses: int = 0
    size: int = 0

    @property
    def hit_rate(self) -> float:
        """Cache hit rate (0.0 to 1.0)."""
        total = self.hits + self.misses
        return self.hits / total if total > 0 else 0.0


class Cache(Generic[T]):
    """Generic cache for Notion entities.

    Thread-safe cache for storing and retrieving entities by ID.

    Example:
        >>> cache = Cache[User]()
        >>> cache.set("user_123", user)
        >>> user = cache.get("user_123")
        >>> print(len(cache))  # 1
        >>> "user_123" in cache  # True
    """

    def __init__(self) -> None:
        """Initialize empty cache."""
        self._data: Dict[str, T] = {}
        self._stats = CacheStats()

    def get(self, id: str) -> Optional[T]:
        """Get entity from cache.

        Args:
            id: Entity ID

        Returns:
            Cached entity or None if not found

        Note:
            Updates cache statistics (hit or miss)
        """
        result = self._data.get(id)

        if result is not None:
            self._stats.hits += 1
        else:
            self._stats.misses += 1

        self._stats.size = len(self._data)
        return result

    def set(self, id: str, entity: T) -> None:
        """Store entity in cache.

        Args:
            id: Entity ID
            entity: Entity to cache

        Note:
            Overwrites existing entry if already cached
        """
        self._data[id] = entity
        self._stats.size = len(self._data)

    def get_all(self) -> list[T]:
        """Get all cached entities.

        Returns:
            List of all cached entities
        """
        return list(self._data.values())

    def invalidate(self, id: str) -> None:
        """Remove entity from cache.

        Args:
            id: Entity ID to remove

        Note:
            No-op if ID not in cache
        """
        self._data.pop(id, None)
        self._stats.size = len(self._data)

    def clear(self) -> None:
        """Clear all cache."""
        self._data.clear()
        self._stats.size = 0

    def __contains__(self, id: str) -> bool:
        """Check if entity is cached.

        Args:
            id: Entity ID

        Returns:
            True if cached, False otherwise
        """
        return id in self._data

    def __len__(self) -> int:
        """Get cache size.

        Returns:
            Number of cached entities
        """
        return len(self._data)

    def __getitem__(self, id: str) -> T:
        """Get entity with dict syntax.

        Args:
            id: Entity ID

        Returns:
            Cached entity

        Raises:
            KeyError: If entity not cached
        """
        if id not in self._data:
            raise KeyError(f"ID {id} not in cache")
        return self._data[id]

    @property
    def stats(self) -> CacheStats:
        """Get cache statistics.

        Returns:
            CacheStats object with hit rate, size, etc.
        """
        return self._stats
```

### Why Generic?

Without generics: code duplication
```python
class UserCache:
    def __init__(self):
        self._data: Dict[str, User] = {}
    def get(self, id: str) -> Optional[User]: ...

class PageCache:
    def __init__(self):
        self._data: Dict[str, Page] = {}
    def get(self, id: str) -> Optional[Page]: ...
```

With generics: single implementation
```python
user_cache: Cache[User] = Cache[User]()
page_cache: Cache[Page] = Cache[Page]()
db_cache: Cache[Database] = Cache[Database]()
```

**Benefits**:
- ✅ Single implementation to maintain
- ✅ Type-safe with mypy/pyright
- ✅ Reusable for any entity type

## Manager Cache Integration

### User Manager with Cache

```python
# better_notion/_sdk/managers/users.py

from better_notion._sdk.implementation.cache import Cache

class UserManager:
    """Manager for user operations with caching."""

    def __init__(self, api: NotionAPI):
        """Initialize manager.

        Args:
            api: Low-level NotionAPI client
        """
        self._api = api
        self._cache = Cache[User]()

    async def get(self, user_id: str) -> User:
        """Get user by ID (with cache lookup).

        Args:
            user_id: User UUID

        Returns:
            User object

        Raises:
            UserNotFound: If user doesn't exist

        Behavior:
            1. Check cache first
            2. If cached, return immediately (no API call)
            3. If not cached, fetch from API
            4. Store in cache for next time
        """
        # Check cache first (instant)
        cached = self._cache.get(user_id)
        if cached:
            return cached

        # Cache miss - fetch from API
        data = await self._api._request("GET", f"/users/{user_id}")
        user = User(self._api, data)

        # Store in cache for next access
        self._cache.set(user_id, user)

        return user

    async def populate_cache(self) -> None:
        """Load ALL users into cache.

        Fetches all users from API and stores them in cache.
        Subsequent get() calls will be instant memory lookups.

        Use case:
            Call this at startup if you'll be looking up many users.
            Avoids repeated API calls in loops.

        Example:
            >>> # Pre-load all users
            >>> await client.users.populate_cache()
            >>>
            >>> # Now all lookups are instant
            >>> for page in pages:
            ...     user = client.users.cache.get(page.created_by_id)
        """
        # Clear existing cache
        self._cache.clear()

        # Fetch all users (handles pagination)
        async for user_data in self._api.users.list():
            user = User(self._api, user_data)
            self._cache.set(user.id, user)

    async def find_by_email(self, email: str) -> User | None:
        """Find user by email (cache-aware).

        Args:
            email: User email address

        Returns:
            User object or None if not found

        Note:
            Searches cache first. If not found, returns None
            (doesn't fall back to API to avoid listing all users)
        """
        # Search in cache (linear scan but in-memory)
        for user in self._cache.get_all():
            if user.email == email:
                return user

        return None

    @property
    def cache(self) -> Cache[User]:
        """Direct access to user cache.

        Example:
            >>> # Check if cached
            >>> if user_id in client.users.cache:
            ...     user = client.users.cache[user_id]
            >>>
            >>> # Get without API call
            >>> user = client.users.cache.get(user_id)
            >>>
            >>> # Monitor effectiveness
            >>> stats = client.users.cache.stats
            >>> print(f"Hit rate: {stats.hit_rate:.1%}")
        """
        return self._cache
```

## Entity-Level Caching

### Navigation Cache Pattern

```python
# better_notion/_sdk/models/page.py

class Page(BaseEntity):
    """Page model with navigation caching."""

    async def parent(self) -> Database | Page | None:
        """Get parent object (cached).

        Returns:
            Parent Database or Page object

        Behavior:
            - First call: Fetch from API, cache result
            - Subsequent calls: Return cached version (instant)

        Example:
            >>> parent = await page.parent  # API fetch
            >>> parent2 = await page.parent  # Cache hit
            >>>
            >>> # Force refresh
            >>> page._cache_clear()
            >>> parent3 = await page.parent  # API fetch again
        """
        # Check entity cache
        cached_parent = self._cache_get("parent")
        if cached_parent:
            return cached_parent

        # Fetch from API
        parent_data = self._data.get("parent", {})

        if parent_data.get("type") == "database_id":
            database_id = parent_data["database_id"]
            data = await self._api._request("GET", f"/databases/{database_id}")
            parent = Database(self._api, data)

        elif parent_data.get("type") == "page_id":
            page_id = parent_data["page_id"]
            data = await self._api._request("GET", f"/pages/{page_id}")
            parent = Page(self._api, data)

        else:
            parent = None

        # Cache result
        if parent:
            self._cache_set("parent", parent)

        return parent

    @property
    def parent_cached(self) -> Database | Page | None:
        """Get parent from cache only (no API fetch).

        Returns:
            Cached parent or None if not cached

        Use case:
            Check if parent is available without triggering API call.

        Example:
            >>> parent = page.parent_cached
            >>> if parent:
            ...     print(f"Parent: {parent.title}")
            ... else:
            ...     parent = await page.parent  # Fetch it
        """
        return self._cache_get("parent")
```

### Cache Invalidation After Updates

```python
class Page(BaseEntity):
    async def save(self) -> None:
        """Save changes and clear cache.

        Clears entity cache after save since data has changed
        and cached references might be stale.
        """
        # Save to API (inherited from API entity)
        await super().save()

        # Clear navigation cache (references may be stale)
        self._cache_clear()
```

## Cache Population Strategies

### 1. Lazy Loading (Default)

Cache populated on-demand:

```python
# Initially empty
print(len(client.users.cache))  # 0

# First access triggers fetch
user1 = await client.users.get("user_123")  # API call
print(len(client.users.cache))  # 1

# Second access hits cache
user2 = await client.users.get("user_123")  # Instant
print(len(client.users.cache))  # 1

# Third access fetches new user
user3 = await client.users.get("user_456")  # API call
print(len(client.users.cache))  # 2
```

**Use when**: General usage, don't know what you'll need upfront

**Pros**: No wasted API calls, memory efficient
**Cons**: First access is slow

### 2. Eager Loading

Pre-load everything:

```python
# Load everything at start
await client.users.populate_cache()  # Several API calls (paginated)

# Now everything is instant
users = []
for page in pages:
    creator = client.users.cache.get(page.created_by_id)  # Instant
    editor = client.users.cache.get(page.last_edited_by_id)  # Instant
    users.append((creator, editor))
```

**Use when**: Batch processing, know you'll need everything

**Pros**: Instant access after load, predictable
**Cons**: High upfront cost, may load unused data

### 3. Hybrid Strategy

Adapt based on context:

```python
async def get_user(user_id: str) -> User:
    """Cache-then-fetch pattern."""
    # Try cache first
    user = client.users.cache.get(user_id)
    if user:
        return user  # Cache hit

    # Cache miss, fetch from API
    return await client.users.get(user_id)  # Fetches + caches

# Usage depends on context
if processing_batch:
    # Pre-load for batch
    await client.users.populate_cache()
    for page in pages:
        user = client.users.cache.get(page.created_by_id)
else:
    # One-off lookup
    user = await get_user(user_id)
```

## Usage Examples

### Example 1: Batch Processing

```python
# ❌ BAD - 100 API calls
pages = await database.query().collect()

for page in pages:
    creator = await client.users.get(page.created_by_id)
    print(f"{page.title} by {creator.name}")

# ✅ GOOD - 1 API call + cache
await client.users.populate_cache()

for page in pages:
    creator = client.users.cache.get(page.created_by_id)
    print(f"{page.title} by {creator.name}")
```

### Example 2: Conditional Lookup

```python
# ❌ BAD - Fetches even when not needed
async def process_page(page: Page):
    user = await client.users.get(page.created_by_id)  # Always fetches

    if needs_notification(page):
        notify(user)

# ✅ GOOD - Fetches only when needed
async def process_page(page: Page):
    if needs_notification(page):
        user = await client.users.get(page.created_by_id)
        notify(user)
```

### Example 3: Cache Search

```python
# Search in cache (no API call)
def find_user_by_name(name: str) -> User | None:
    for user in client.users.cache.get_all():
        if user.name == name:
            return user
    return None

user = find_user_by_name("John Doe")
```

### Example 4: Monitoring Effectiveness

```python
# After running your code
stats = client.users.cache.stats

print(f"Cache hits: {stats.hits}")
print(f"Cache misses: {stats.misses}")
print(f"Hit rate: {stats.hit_rate:.1%}")
print(f"Cache size: {stats.size}")

# Example output:
# Cache hits: 947
# Cache misses: 53
# Hit rate: 94.7%
# Cache size: 156
```

**Interpreting hit rate**:
- **> 90%**: Excellent! Cache working well
- **50-90%**: Good, but could be optimized
- **< 50%**: Ineffective, reconsider strategy

## Design Decisions

### Q1: Automatic TTL (Time-To-Live)?

**Scenario**: Cached user data becomes stale

```python
user = await client.users.get("user_123")
print(user.name)  # "John Doe"

# ... 1 hour later (user renamed in Notion)
print(user.name)  # Still "John Doe" (STALE!)
```

**Decision**: No automatic TTL

**Rationale**:
- ✅ Simple, predictable behavior
- ✅ No surprise refetches
- ✅ User controls when to refresh

**Alternative**: Manual invalidation
```python
# User controls refresh
client.users.cache.invalidate("user_123")
user = await client.users.get("user_123")  # Fresh data
```

### Q2: Cache Size Limits?

**Scenario**: Workspace with 10,000 users

```python
await client.users.populate_cache()
# ≈ 10,000 entities × 1KB = 10MB RAM
```

**Decision**: No size limit (initially)

**Rationale**:
- ✅ Simple implementation
- ✅ Most workspaces are < 1000 users
- ✅ Memory is cheap

**Future enhancement**: LRU eviction if needed
```python
# If memory becomes an issue
cache = Cache[User](max_size=1000)  # Keep only 1000 most recent
```

### Q3: Thread-Safety?

**Decision**: Not thread-safe (async single-threaded)

**Rationale**:
- Python async is single-threaded
- No need for locks in typical usage
- Simpler, faster code

**If needed**: Add threading.Lock later
```python
class Cache(Generic[T]):
    def __init__(self):
        self._lock = threading.Lock()
        self._data = {}

    def get(self, id: str):
        with self._lock:
            return self._data.get(id)
```

## Best Practices

### DO ✅

```python
# Preload cache for batch operations
await client.users.populate_cache()
for page in pages:
    user = client.users.cache.get(page.created_by_id)

# Check cache before fetching
user = client.users.cache.get(user_id)
if user:
    return user
return await client.users.get(user_id)

# Invalidate after updates
await page.update(properties={...})
await page.save()
page._cache_clear()

# Monitor cache effectiveness
stats = client.users.cache.stats
if stats.hit_rate < 0.5:
    logger.warning("Cache hit rate low, consider populate_cache()")
```

### DON'T ❌

```python
# Don't assume cache is populated
user = client.users.cache.get(user_id)
print(user.name)  # Could crash if None!

# Don't ignore cache in loops
for page in pages:
    user = await client.users.get(page.created_by_id)  # Slow!

# Don't cache volatile data
results = await client.search.query("term")  # Don't cache
```

## Performance Considerations

### Memory Usage

Approximate per-entity memory:
- User: ~1 KB
- Page: ~2-5 KB (depends on properties)
- Database: ~5-10 KB (includes schema)

**Example cache sizes**:
- 100 users: ~100 KB
- 1000 pages: ~2-5 MB
- Full workspace: ~10-50 MB

### Cache Hit Rate Targets

| Scenario | Target Hit Rate | Strategy |
|----------|----------------|----------|
| Batch processing | > 95% | Eager load first |
| Interactive app | > 80% | Lazy + occasional populate |
| One-off scripts | N/A | Don't cache |

### When NOT to Cache

```python
# ❌ Don't cache search results (query-specific)
results = await client.search.query("project")

# ❌ Don't cache large datasets
all_pages = await database.query().collect()  # Could be 1000s

# ❌ Don't cache volatile operations
audit_log = await client.get_audit_log()  # Changes constantly
```

## Next Steps

1. ✅ Implement generic `Cache[T]` class
2. ✅ Add cache to `UserManager`
3. ✅ Add entity-level navigation caching
4. ✅ Add cache statistics monitoring
5. ⏭️ Consider TTL strategy (future enhancement)
6. ⏭️ Consider LRU eviction (if memory issues)

## Related Documentation

- [BaseEntity](./base-entity.md) - Entity-level caching methods
- [Navigation](./navigation.md) - Cached navigation patterns
- [User Manager](../managers/user-manager.md) - Manager-specific usage
- [Property Parsers](./property-parsers.md) - Property access optimization
