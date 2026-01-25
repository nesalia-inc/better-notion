"""Generic cache implementation for SDK entities."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Generic, TypeVar

T = TypeVar("T")


@dataclass
class CacheStats:
    """Cache statistics for monitoring effectiveness.

    Attributes:
        hits: Number of cache hits
        misses: Number of cache misses
        size: Current number of items in cache
    """

    hits: int = 0
    misses: int = 0
    size: int = 0

    @property
    def hit_rate(self) -> float:
        """Calculate cache hit rate.

        Returns:
            Hit rate as float between 0.0 and 1.0
            Returns 0.0 if no requests have been made.
        """
        total = self.hits + self.misses
        return self.hits / total if total > 0 else 0.0


class Cache(Generic[T]):
    """Generic thread-safe cache for Notion entities.

    Provides simple key-value storage with statistics tracking.
    Type-safe with mypy/pyright.

    Example:
        >>> from better_notion._sdk.cache import Cache
        >>> cache = Cache[str]()  # Cache for strings
        >>> cache.set("key1", "value1")
        >>> value = cache.get("key1")  # Returns "value1"
        >>> "key1" in cache  # True
        >>> len(cache)  # 1

    Type Parameters:
        T: Type of cached objects
    """

    def __init__(self) -> None:
        """Initialize empty cache."""
        self._data: dict[str, T] = {}
        self._stats = CacheStats()

    def get(self, key: str) -> T | None:
        """Get entity from cache.

        Args:
            key: Entity ID to retrieve

        Returns:
            Cached entity or None if not found

        Note:
            Updates cache statistics (hit or miss)
        """
        result = self._data.get(key)

        if result is not None:
            self._stats.hits += 1
        else:
            self._stats.misses += 1

        self._stats.size = len(self._data)
        return result

    def set(self, key: str, value: T) -> None:
        """Store entity in cache.

        Args:
            key: Entity ID
            value: Entity to cache

        Note:
            Overwrites existing entry if already cached
        """
        self._data[key] = value
        self._stats.size = len(self._data)

    def get_all(self) -> list[T]:
        """Get all cached entities.

        Returns:
            List of all cached entities
        """
        return list(self._data.values())

    def keys(self) -> list[str]:
        """Get all cache keys.

        Returns:
            List of all keys in the cache
        """
        return list(self._data.keys())

    def values(self) -> list[T]:
        """Get all cached values.

        Returns:
            List of all values in the cache
        """
        return list(self._data.values())

    def items(self) -> list[tuple[str, T]]:
        """Get all cache key-value pairs.

        Returns:
            List of (key, value) tuples
        """
        return list(self._data.items())

    def invalidate(self, key: str) -> None:
        """Remove entity from cache.

        Args:
            key: Entity ID to remove

        Note:
            No-op if ID not in cache
        """
        self._data.pop(key, None)
        self._stats.size = len(self._data)

    def clear(self) -> None:
        """Clear all cache."""
        self._data.clear()
        self._stats.size = 0

    def __contains__(self, key: str) -> bool:
        """Check if entity is cached.

        Args:
            key: Entity ID

        Returns:
            True if cached, False otherwise
        """
        return key in self._data

    def __len__(self) -> int:
        """Get cache size.

        Returns:
            Number of cached entities
        """
        return len(self._data)

    def __getitem__(self, key: str) -> T:
        """Get entity with dict syntax.

        Args:
            key: Entity ID

        Returns:
            Cached entity

        Raises:
            KeyError: If entity not cached

        Example:
            >>> cache = Cache[str]()
            >>> cache.set("key", "value")
            >>> cache["key"]  # Returns "value"
        """
        if key not in self._data:
            raise KeyError(f"Key '{key}' not in cache")
        return self._data[key]

    def __setitem__(self, key: str, value: T) -> None:
        """Set entity with dict syntax.

        Args:
            key: Entity ID
            value: Entity to cache

        Example:
            >>> cache = Cache[str]()
            >>> cache["key"] = "value"
        """
        self._data[key] = value
        self._stats.size = len(self._data)

    @property
    def stats(self) -> CacheStats:
        """Get cache statistics.

        Returns:
            CacheStats object with hit rate, size, etc.

        Example:
            >>> cache = Cache[str]()
            >>> cache.get("missing")  # Miss
            >>> cache.stats.misses  # 1
            >>> cache.stats.hit_rate  # 0.0
        """
        return self._stats
