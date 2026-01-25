# BaseEntity

Foundation class for all Notion SDK entities (Page, Database, Block, User).

## Overview

`BaseEntity` is the abstract base class that all Notion entities inherit from. It provides:

1. **Common properties**: `id`, `object`
2. **Local cache**: For navigation results
3. **Navigation methods**: `parent()`, `children()`, `ancestors()`, `descendants()`
4. **Equality & hashing**: For comparing entities

## Architecture

```
BaseEntity (ABC)
├── id                 # Entity UUID
├── object            # Entity type
├── _client           # NotionClient reference
├── _data             # Raw API data
├── _cache            # Local navigation cache
├── _cache_set/get/clear  # Cache methods
├── parent()          # Abstract (implemented by subclasses)
├── children()        # Abstract (implemented by subclasses)
├── ancestors()       # Walk up hierarchy (implemented)
└── descendants()     # Walk down recursively (implemented)
```

## Implementation

```python
from abc import ABC, abstractmethod
from typing import Any, AsyncIterator

class BaseEntity(ABC):
    """Base class for all Notion entities.

    All entities (Page, Database, Block, User) inherit from this class.
    """

    def __init__(self, client: NotionClient, data: dict[str, Any]) -> None:
        """Initialize entity with API data.

        Args:
            client: NotionClient instance
            data: Raw API response data
        """
        self._client = client
        self._data = data
        self._cache: dict[str, Any] = {}

    # ===== IDENTITY =====

    @property
    def id(self) -> str:
        """Entity UUID.

        Example:
            >>> print(page.id)
            '123e4567-e89b-12d3-a456-426614174000'
        """
        return self._data["id"]

    @property
    def object(self) -> str:
        """Entity type ('page', 'database', 'block', 'user').

        Example:
            >>> print(page.object)
            'page'
        """
        return self._data["object"]

    def __eq__(self, other: object) -> bool:
        """Equality by ID.

        Example:
            >>> page1 == page2  # True if same ID
        """
        if not isinstance(other, BaseEntity):
            return NotImplemented
        return self.id == other.id

    def __hash__(self) -> int:
        """Hash by ID for use in sets/dicts.

        Example:
            >>> pages_set = {page1, page2}
        """
        return hash(self.id)

    # ===== LOCAL CACHE =====

    def _cache_set(self, key: str, value: Any) -> None:
        """Store value in local cache.

        Used internally to cache navigation results.
        """
        self._cache[key] = value

    def _cache_get(self, key: str) -> Any | None:
        """Get value from local cache.

        Returns None if not cached.
        """
        return self._cache.get(key)

    def _cache_clear(self) -> None:
        """Clear local cache.

        Called after updates to invalidate stale data.
        """
        self._cache.clear()

    # ===== NAVIGATION - ABSTRACT =====

    @abstractmethod
    async def parent(self) -> "Database | Page | Block | None":
        """Get parent object.

        Each subclass implements its own logic:
        - Page: parent can be Database or Page
        - Database: parent can be Page
        - Block: parent can be Page or Block
        - User: no parent (returns None)

        Returns:
            Parent object or None if workspace root
        """
        raise NotImplementedError

    @abstractmethod
    async def children(self) -> AsyncIterator["Block | Page"]:
        """Iterate over direct children.

        Each subclass implements its own logic:
        - Page: children are Block
        - Database: children are Page
        - Block: children are Block
        - User: no children (empty iterator)

        Yields:
            Child entities
        """
        raise NotImplementedError

    # ===== NAVIGATION - IMPLEMENTED =====

    async def ancestors(self) -> AsyncIterator["Database | Page | Block"]:
        """Walk up hierarchy to root.

        Starts from current entity and walks up to workspace root.

        Example:
            >>> # Build breadcrumb
            >>> parts = []
            >>> async for ancestor in page.ancestors():
            ...     title = ancestor.title if hasattr(ancestor, 'title') else 'Workspace'
            ...     parts.append(title)
            >>> parts.reverse()
            >>> print(" / ".join(parts))
            # Output: "Workspace / DB / Section / Page"

        Note:
            - First yield: immediate parent
            - Last yield: root (workspace level)
            - Does NOT include self
            - Stops when parent is None
        """
        current = self

        while True:
            parent = await current.parent()

            if parent is None:
                break

            yield parent

            current = parent

    async def descendants(
        self,
        max_depth: int | None = None
    ) -> AsyncIterator["Block"]:
        """Walk down hierarchy recursively.

        Args:
            max_depth: Maximum depth to traverse (None = unlimited)

        Example:
            >>> # Count all blocks
            >>> count = 0
            >>> async for block in page.descendants():
            ...     count += 1
            >>> print(f"Total blocks: {count}")

            >>> # Limit depth
            >>> async for block in page.descendants(max_depth=2):
            ...     print(block.type)

        Note:
            - Depth-first traversal
            - Includes self in iteration
            - Cycle detection (visited tracking)
        """
        visited = set()

        async def traverse(entity: BaseEntity, depth: int):
            if max_depth is not None and depth > max_depth:
                return

            if entity.id in visited:
                return

            visited.add(entity.id)

            if entity.object == "block":
                yield entity

            try:
                async for child in entity.children():
                    async for descendant in traverse(child, depth + 1):
                        yield descendant
            except NotImplementedError:
                pass

        async for descendant in traverse(self, 0):
            yield descendant
```

## Usage in Subclasses

Subclasses only need to implement `parent()` and `children()`:

```python
class Page(BaseEntity):
    """Page inherits all navigation from BaseEntity."""

    async def parent(self) -> Database | Page | None:
        """Implemented by Page."""
        cached = self._cache_get("parent")
        if cached:
            return cached

        parent_data = self._data.get("parent", {})

        if parent_data.get("type") == "database_id":
            parent = await Database.get(
                parent_data["database_id"],
                client=self._client
            )
        elif parent_data.get("type") == "page_id":
            parent = await Page.get(
                parent_data["page_id"],
                client=self._client
            )
        else:
            parent = None

        if parent:
            self._cache_set("parent", parent)

        return parent

    async def children(self) -> AsyncIterator[Block]:
        """Implemented by Page."""
        async for block_data in self._fetch_children():
            yield Block.from_data(self._client, block_data)

    # Inherits ancestors() and descendants() for free!
```

## Benefits

1. **DRY**: Common logic in one place
2. **Polymorphism**: Work with any entity
3. **Type safety**: BaseEntity as base type
4. **Navigation**: All entities have `ancestors()`, `descendants()`

## Design Decisions

### Q1: Why store client reference?

**Decision**: Store `self._client` in `__init__`

**Rationale**:
- Simpler: no need to pass `client` everywhere
- Entity knows its context

### Q2: Generic cache or specific attributes?

**Decision**: Generic `_cache` dict

**Rationale**:
- Flexible: cache any data
- No pre-declaration needed

### Q3: ancestors() include self?

**Decision**: No, only parents

**Rationale**:
- "Ancestors" = those before, not self
- More intuitive for breadcrumbs

## Related Documentation

- [Cache Strategy](./cache-strategy.md) - Cache levels
- [Navigation](./navigation.md) - Navigation patterns
- [Entity-Oriented Architecture](./entity-oriented-architecture.md) - Overall architecture
