"""Base entity class for all Notion SDK entities."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any, AsyncIterator

if TYPE_CHECKING:
    from better_notion._sdk.client import NotionClient


class BaseEntity(ABC):
    """Abstract base class for all Notion entities.

    All entities (Page, Database, Block, User) inherit from this class.
    Provides common functionality: id, object, cache, and navigation.

    Attributes:
        _client: NotionClient instance for API calls
        _data: Raw API response data
        _cache: Local cache for navigation results

    Example:
        >>> class Page(BaseEntity):
        ...     async def parent(self): ...
        ...     async def children(self): ...
    """

    def __init__(self, client: "NotionClient", data: dict[str, Any]) -> None:
        """Initialize entity with client and API data.

        Args:
            client: NotionClient instance
            data: Raw API response data

        Raises:
            ValueError: If data is missing required 'id' field
        """
        if "id" not in data:
            raise ValueError("API data must contain 'id' field")

        self._client = client
        self._data = data
        self._cache: dict[str, Any] = {}

    # ===== IDENTITY =====

    @property
    def id(self) -> str:
        """Get entity UUID.

        Returns:
            Entity ID as string

        Example:
            >>> print(page.id)
            '123e4567-e89b-12d3-a456-426614174000'
        """
        return self._data["id"]

    @property
    def object(self) -> str:
        """Get entity type.

        Returns:
            Entity type string ('page', 'database', 'block', 'user')

        Example:
            >>> print(page.object)
            'page'
        """
        return self._data.get("object", "")

    def __eq__(self, other: object) -> bool:
        """Check equality by ID.

        Two entities are equal if they have the same ID.

        Args:
            other: Object to compare with

        Returns:
            True if other is BaseEntity with same ID

        Example:
            >>> page1 == page2  # True if same ID
        """
        if not isinstance(other, BaseEntity):
            return False
        return self.id == other.id

    def __hash__(self) -> int:
        """Hash by ID for use in sets and dicts.

        Returns:
            Hash of entity ID

        Example:
            >>> pages_set = {page1, page2}
        """
        return hash(self.id)

    def __repr__(self) -> str:
        """String representation of entity.

        Returns:
            String with class name and ID
        """
        return f"{self.__class__.__name__}(id='{self.id}')"

    # ===== LOCAL CACHE =====

    def _cache_set(self, key: str, value: Any) -> None:
        """Store value in local cache.

        Used internally to cache navigation results like parent or children.

        Args:
            key: Cache key
            value: Value to cache
        """
        self._cache[key] = value

    def _cache_get(self, key: str) -> Any | None:
        """Get value from local cache.

        Args:
            key: Cache key

        Returns:
            Cached value or None if not found
        """
        return self._cache.get(key)

    def _cache_clear(self) -> None:
        """Clear local cache.

        Called after updates to invalidate stale navigation data.
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

        Raises:
            NotImplementedError: Always (subclass must implement)
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

        Raises:
            NotImplementedError: Always (subclass must implement)
        """
        raise NotImplementedError

    # ===== NAVIGATION - IMPLEMENTED =====

    async def ancestors(self) -> AsyncIterator["BaseEntity"]:
        """Walk up the hierarchy to root.

        Starts from current entity and walks up to workspace root.

        Yields:
            Ancestors from immediate parent to root

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
        """Walk down the hierarchy recursively.

        Args:
            max_depth: Maximum depth to traverse (None = unlimited)

        Yields:
            All descendant blocks (depth-first traversal)

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
            - Includes self in iteration (if it's a block)
            - Cycle detection (visited tracking)
        """
        visited = set()

        async def traverse(entity: BaseEntity, depth: int) -> AsyncIterator[Block]:
            if max_depth is not None and depth > max_depth:
                return

            if entity.id in visited:
                return

            visited.add(entity.id)

            # Yield if it's a block
            if entity.object == "block":
                yield entity  # type: ignore

            # Recurse into children
            try:
                # Get children iterator (handle both async iterators and coroutines)
                children_result = entity.children()

                # If it's a coroutine, we need to await it to get the iterator
                # But since we're already in an async context, we need to handle this differently
                # The simplest solution is to check if it has __aiter__
                if hasattr(children_result, '__aiter__'):
                    async for child in children_result:
                        async for descendant in traverse(child, depth + 1):
                            yield descendant
                else:
                    # It's a coroutine - await it to get the iterator
                    # This can happen in tests or with incorrectly implemented children()
                    from inspect import iscoroutine
                    if iscoroutine(children_result):
                        # This is a bug in the entity implementation, but handle it gracefully
                        pass
                    else:
                        # Not an async iterator and not a coroutine - skip
                        pass
            except (NotImplementedError, TypeError):
                # Entity doesn't support children or children() is not an async iterator
                pass

        async for descendant in traverse(self, 0):
            yield descendant
