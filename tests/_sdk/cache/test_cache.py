"""Tests for Cache implementation."""

import pytest

from better_notion._sdk.cache import Cache, CacheStats


class TestCacheStats:
    """Tests for CacheStats dataclass."""

    def test_default_values(self) -> None:
        """Test CacheStats initializes with zeros."""
        stats = CacheStats()
        assert stats.hits == 0
        assert stats.misses == 0
        assert stats.size == 0
        assert stats.hit_rate == 0.0

    def test_hit_rate_calculation(self) -> None:
        """Test hit rate calculation."""
        stats = CacheStats(hits=80, misses=20)
        assert stats.hit_rate == 0.8

    def test_hit_rate_no_requests(self) -> None:
        """Test hit rate returns 0.0 when no requests made."""
        stats = CacheStats()
        assert stats.hit_rate == 0.0

    def test_hit_rate_all_hits(self) -> None:
        """Test hit rate when all requests hit."""
        stats = CacheStats(hits=100, misses=0)
        assert stats.hit_rate == 1.0

    def test_hit_rate_all_misses(self) -> None:
        """Test hit rate when all requests miss."""
        stats = CacheStats(hits=0, misses=100)
        assert stats.hit_rate == 0.0


class TestCache:
    """Tests for Cache generic class."""

    def test_init_empty(self) -> None:
        """Test Cache initializes empty."""
        cache = Cache[str]()
        assert len(cache) == 0
        assert cache.stats.size == 0

    def test_set_and_get(self) -> None:
        """Test basic set and get operations."""
        cache = Cache[str]()
        cache.set("key1", "value1")

        value = cache.get("key1")
        assert value == "value1"

    def test_get_returns_none_for_missing(self) -> None:
        """Test get returns None for missing key."""
        cache = Cache[str]()
        assert cache.get("missing") is None

    def test_get_updates_stats_hit(self) -> None:
        """Test get increments hits on cache hit."""
        cache = Cache[str]()
        cache.set("key1", "value1")

        cache.get("key1")
        assert cache.stats.hits == 1
        assert cache.stats.misses == 0

    def test_get_updates_stats_miss(self) -> None:
        """Test get increments misses on cache miss."""
        cache = Cache[str]()
        cache.get("missing")

        assert cache.stats.hits == 0
        assert cache.stats.misses == 1

    def test_set_overwrites_existing(self) -> None:
        """Test set overwrites existing value."""
        cache = Cache[str]()
        cache.set("key1", "value1")
        cache.set("key1", "value2")

        assert cache.get("key1") == "value2"

    def test_get_all_returns_all_values(self) -> None:
        """Test get_all returns all cached values."""
        cache = Cache[str]()
        cache.set("key1", "value1")
        cache.set("key2", "value2")
        cache.set("key3", "value3")

        values = cache.get_all()
        assert len(values) == 3
        assert "value1" in values
        assert "value2" in values
        assert "value3" in values

    def test_invalidate_removes_key(self) -> None:
        """Test invalidate removes key from cache."""
        cache = Cache[str]()
        cache.set("key1", "value1")
        cache.invalidate("key1")

        assert cache.get("key1") is None
        assert "key1" not in cache

    def test_invalidate_missing_key_no_error(self) -> None:
        """Test invalidate doesn't error on missing key."""
        cache = Cache[str]()
        cache.invalidate("missing")  # Should not raise

    def test_clear_removes_all(self) -> None:
        """Test clear removes all entries."""
        cache = Cache[str]()
        cache.set("key1", "value1")
        cache.set("key2", "value2")

        cache.clear()

        assert len(cache) == 0
        assert cache.get("key1") is None
        assert cache.get("key2") is None

    def test_contains_operator(self) -> None:
        """Test 'in' operator works."""
        cache = Cache[str]()
        cache.set("key1", "value1")

        assert "key1" in cache
        assert "key2" not in cache

    def test_len_operator(self) -> None:
        """Test len() returns correct size."""
        cache = Cache[str]()
        assert len(cache) == 0

        cache.set("key1", "value1")
        assert len(cache) == 1

        cache.set("key2", "value2")
        assert len(cache) == 2

    def test_dict_syntax_getitem(self) -> None:
        """Test dict-style get with [] operator."""
        cache = Cache[str]()
        cache.set("key1", "value1")

        assert cache["key1"] == "value1"

    def test_dict_syntax_getitem_raises(self) -> None:
        """Test dict-style get raises KeyError for missing key."""
        cache = Cache[str]()

        with pytest.raises(KeyError, match="Key 'missing' not in cache"):
            _ = cache["missing"]

    def test_dict_syntax_setitem(self) -> None:
        """Test dict-style set with [] operator."""
        cache = Cache[str]()
        cache["key1"] = "value1"

        assert cache["key1"] == "value1"

    def test_stats_property(self) -> None:
        """Test stats property returns CacheStats."""
        cache = Cache[str]()
        stats = cache.stats

        assert isinstance(stats, CacheStats)
        assert stats.size == 0

    def test_stats_size_updates(self) -> None:
        """Test stats size updates with operations."""
        cache = Cache[str]()

        cache.set("key1", "value1")
        assert cache.stats.size == 1

        cache.set("key2", "value2")
        assert cache.stats.size == 2

        cache.invalidate("key1")
        assert cache.stats.size == 1

        cache.clear()
        assert cache.stats.size == 0

    def test_generic_type_different_objects(self) -> None:
        """Test cache works with different types."""
        # String cache
        str_cache = Cache[str]()
        str_cache.set("key", "value")
        assert str_cache.get("key") == "value"

        # Int cache
        int_cache = Cache[int]()
        int_cache.set("key", 42)
        assert int_cache.get("key") == 42

        # List cache
        list_cache = Cache[list[str]]()
        list_cache.set("key", ["a", "b", "c"])
        assert list_cache.get("key") == ["a", "b", "c"]

    def test_multiple_gets_track_stats(self) -> None:
        """Test multiple gets track statistics correctly."""
        cache = Cache[str]()
        cache.set("key1", "value1")

        # 3 hits, 2 misses
        cache.get("key1")
        cache.get("key1")
        cache.get("key1")
        cache.get("missing1")
        cache.get("missing2")

        assert cache.stats.hits == 3
        assert cache.stats.misses == 2
        assert cache.stats.hit_rate == 0.6

    def test_complex_object_storage(self) -> None:
        """Test cache can store complex objects."""

        class TestObject:
            def __init__(self, name: str, value: int):
                self.name = name
                self.value = value

        cache = Cache[TestObject]()
        obj = TestObject("test", 42)

        cache.set("obj1", obj)
        retrieved = cache.get("obj1")

        assert retrieved is obj
        assert retrieved.name == "test"
        assert retrieved.value == 42

    def test_iteration_over_cache(self) -> None:
        """Test iterating over cache keys and values."""
        cache = Cache[str]()
        cache.set("key1", "value1")
        cache.set("key2", "value2")
        cache.set("key3", "value3")

        keys = list(cache.keys())
        values = list(cache.values())

        assert len(keys) == 3
        assert len(values) == 3
        assert set(keys) == {"key1", "key2", "key3"}
        assert set(values) == {"value1", "value2", "value3"}

    def test_items_iteration(self) -> None:
        """Test iterating over cache items."""
        cache = Cache[str]()
        cache.set("key1", "value1")
        cache.set("key2", "value2")

        items = dict(cache.items())
        assert items == {"key1": "value1", "key2": "value2"}

    def test_cache_with_multiple_types(self) -> None:
        """Test cache handles None values."""
        cache = Cache[str | None]()
        cache.set("key1", None)
        cache.set("key2", "value2")

        assert cache.get("key1") is None
        assert cache.get("key2") == "value2"
        assert cache.stats.size == 2

    def test_stats_reset(self) -> None:
        """Test that stats persist correctly across operations."""
        cache = Cache[str]()

        # Initial state
        assert cache.stats.hits == 0
        assert cache.stats.misses == 0

        # Add items
        cache.set("key1", "value1")
        cache.set("key2", "value2")

        # Generate some hits and misses
        cache.get("key1")  # hit
        cache.get("key2")  # hit
        cache.get("missing")  # miss

        assert cache.stats.hits == 2
        assert cache.stats.misses == 1

        # Clear should reset size but not hits/misses
        cache.clear()
        assert cache.stats.size == 0
        assert cache.stats.hits == 2  # Stats persist
        assert cache.stats.misses == 1

    def test_performance_hit_rate_edge_cases(self) -> None:
        """Test hit rate calculation with edge cases."""
        cache = Cache[str]()

        # No requests
        assert cache.stats.hit_rate == 0.0

        # Only misses
        cache.get("missing1")
        cache.get("missing2")
        assert cache.stats.hit_rate == 0.0

        # Only hits
        cache.set("key1", "value1")
        cache.get("key1")
        cache.get("key1")
        # Total: 2 hits, 2 misses
        expected_rate = 2 / 4  # 0.5
        assert abs(cache.stats.hit_rate - expected_rate) < 0.001

    def test_cache_key_reuse(self) -> None:
        """Test reusing the same key updates stats correctly."""
        cache = Cache[str]()

        cache.set("key1", "value1")
        cache.get("key1")  # First hit

        cache.set("key1", "value2")  # Overwrite
        cache.get("key1")  # Second hit

        assert cache.stats.hits == 2
        assert cache.get("key1") == "value2"
        assert cache.stats.size == 1

    def test_get_or_else_default(self) -> None:
        """Test get returns None for missing keys (default behavior)."""
        cache = Cache[str]()
        cache.set("key1", "value1")

        assert cache.get("key1") == "value1"
        assert cache.get("missing") is None
        assert cache.stats.misses == 1

    def test_concurrent_like_operations(self) -> None:
        """Test cache handles rapid set/get operations."""
        cache = Cache[int]()

        # Simulate rapid operations
        for i in range(100):
            cache.set(f"key{i}", i)

        for i in range(100):
            value = cache.get(f"key{i}")
            assert value == i

        # Check some misses
        assert cache.get("key100") is None
        assert cache.get("key101") is None

        assert cache.stats.size == 100
        assert cache.stats.hits == 100
        assert cache.stats.misses == 2

    def test_cache_with_dict_like_operations(self) -> None:
        """Test cache behaves like a dict in common operations."""
        cache = Cache[str]()

        # __setitem__
        cache["key1"] = "value1"
        cache["key2"] = "value2"

        # __contains__
        assert "key1" in cache
        assert "key3" not in cache

        # __getitem__
        assert cache["key1"] == "value1"

        # __len__
        assert len(cache) == 2

        # get with default
        assert cache.get("key1") == "value1"
        assert cache.get("key3") is None

        # del via invalidate
        cache.invalidate("key1")
        assert "key1" not in cache
        assert len(cache) == 1  # Size decreased after invalidation

    def test_stats_accuracy_after_complex_operations(self) -> None:
        """Test stats remain accurate after complex operation sequences."""
        cache = Cache[str]()

        # Sequence: add, hit, add, miss, invalidate, hit
        cache.set("a", "1")      # size=1
        cache.get("a")           # hit=1
        cache.set("b", "2")      # size=2
        cache.get("c")           # miss=1
        cache.invalidate("a")    # size=1
        cache.get("b")           # hit=2
        cache.clear()            # size=0

        assert cache.stats.size == 0
        assert cache.stats.hits == 2
        assert cache.stats.misses == 1
        assert cache.stats.hit_rate == 2/3

    def test_type_safety_with_generic_types(self) -> None:
        """Test that cache preserves type information."""
        from typing import Union

        # Union type cache
        cache = Cache[Union[str, int]]()
        cache.set("str_key", "string")
        cache.set("int_key", 42)

        assert cache.get("str_key") == "string"
        assert cache.get("int_key") == 42

        # Type checker should be happy with this
        value: Union[str, int] | None = cache.get("str_key")
        assert value == "string"
