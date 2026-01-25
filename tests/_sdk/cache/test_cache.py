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
