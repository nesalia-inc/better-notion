"""Tests for BaseEntity abstract class."""

from typing import Any
import pytest

from better_notion._sdk.base.entity import BaseEntity


class MockEntity(BaseEntity):
    """Mock entity for testing BaseEntity."""

    def __init__(self, client, data: dict[str, Any]) -> None:
        self.parent_value = None
        self.children_value = []
        super().__init__(client, data)

    async def parent(self):
        """Return mock parent."""
        return self.parent_value

    async def children(self):
        """Yield mock children."""
        for child in self.children_value:
            yield child


class TestBaseEntityInit:
    """Tests for BaseEntity initialization."""

    def test_init_with_client_and_data(self) -> None:
        """Test initialization with client and data."""
        from unittest.mock import Mock

        client = Mock()
        data = {"id": "test-id", "object": "page"}

        entity = MockEntity(client, data)

        assert entity._client is client
        assert entity._data is data
        assert entity._cache == {}

    def test_init_requires_id(self) -> None:
        """Test initialization raises ValueError without id."""
        from unittest.mock import Mock

        client = Mock()
        data = {"object": "page"}

        with pytest.raises(ValueError, match="must contain 'id' field"):
            MockEntity(client, data)

    def test_init_with_optional_object(self) -> None:
        """Test initialization works without object field."""
        from unittest.mock import Mock

        client = Mock()
        data = {"id": "test-id"}

        entity = MockEntity(client, data)

        assert entity.object == ""


class TestBaseEntityIdentity:
    """Tests for entity identity properties."""

    def test_id_property(self) -> None:
        """Test id property returns data id."""
        from unittest.mock import Mock

        client = Mock()
        data = {"id": "test-id-123", "object": "page"}

        entity = MockEntity(client, data)

        assert entity.id == "test-id-123"

    def test_object_property(self) -> None:
        """Test object property returns data object."""
        from unittest.mock import Mock

        client = Mock()
        data = {"id": "test-id", "object": "page"}

        entity = MockEntity(client, data)

        assert entity.object == "page"

    def test_object_property_default(self) -> None:
        """Test object property returns empty string if missing."""
        from unittest.mock import Mock

        client = Mock()
        data = {"id": "test-id"}

        entity = MockEntity(client, data)

        assert entity.object == ""


class TestBaseEntityEquality:
    """Tests for entity equality and hashing."""

    def test_eq_same_id(self) -> None:
        """Test entities with same ID are equal."""
        from unittest.mock import Mock

        client = Mock()
        data1 = {"id": "same-id", "object": "page"}
        data2 = {"id": "same-id", "object": "database"}

        entity1 = MockEntity(client, data1)
        entity2 = MockEntity(client, data2)

        assert entity1 == entity2

    def test_eq_different_id(self) -> None:
        """Test entities with different IDs are not equal."""
        from unittest.mock import Mock

        client = Mock()
        data1 = {"id": "id-1", "object": "page"}
        data2 = {"id": "id-2", "object": "page"}

        entity1 = MockEntity(client, data1)
        entity2 = MockEntity(client, data2)

        assert entity1 != entity2

    def test_eq_non_entity(self) -> None:
        """Test entity is not equal to non-entity."""
        from unittest.mock import Mock

        client = Mock()
        data = {"id": "test-id", "object": "page"}

        entity = MockEntity(client, data)

        assert entity != "test-id"
        assert entity != {"id": "test-id"}
        assert entity != None

    def test_hash_by_id(self) -> None:
        """Test entities with same ID have same hash."""
        from unittest.mock import Mock

        client = Mock()
        data1 = {"id": "same-id", "object": "page"}
        data2 = {"id": "same-id", "object": "database"}

        entity1 = MockEntity(client, data1)
        entity2 = MockEntity(client, data2)

        assert hash(entity1) == hash(entity2)

    def test_hash_different_id(self) -> None:
        """Test entities with different IDs have different hashes."""
        from unittest.mock import Mock

        client = Mock()
        data1 = {"id": "id-1", "object": "page"}
        data2 = {"id": "id-2", "object": "page"}

        entity1 = MockEntity(client, data1)
        entity2 = MockEntity(client, data2)

        assert hash(entity1) != hash(entity2)

    def test_hash_usable_in_set(self) -> None:
        """Test entities can be used in sets."""
        from unittest.mock import Mock

        client = Mock()
        data1 = {"id": "id-1", "object": "page"}
        data2 = {"id": "id-2", "object": "page"}
        data3 = {"id": "id-1", "object": "database"}  # Same ID as data1

        entity1 = MockEntity(client, data1)
        entity2 = MockEntity(client, data2)
        entity3 = MockEntity(client, data3)

        entity_set = {entity1, entity2, entity3}

        # entity1 and entity3 have same ID, so only one should be in set
        assert len(entity_set) == 2

    def test_repr(self) -> None:
        """Test string representation."""
        from unittest.mock import Mock

        client = Mock()
        data = {"id": "test-id", "object": "page"}

        entity = MockEntity(client, data)

        assert repr(entity) == "MockEntity(id='test-id')"


class TestBaseEntityCache:
    """Tests for local cache methods."""

    def test_cache_set_and_get(self) -> None:
        """Test cache set and get operations."""
        from unittest.mock import Mock

        client = Mock()
        entity = MockEntity(client, {"id": "test", "object": "page"})

        entity._cache_set("key", "value")
        assert entity._cache_get("key") == "value"

    def test_cache_get_missing(self) -> None:
        """Test cache get returns None for missing key."""
        from unittest.mock import Mock

        client = Mock()
        entity = MockEntity(client, {"id": "test", "object": "page"})

        assert entity._cache_get("missing") is None

    def test_cache_clear(self) -> None:
        """Test cache clear removes all entries."""
        from unittest.mock import Mock

        client = Mock()
        entity = MockEntity(client, {"id": "test", "object": "page"})

        entity._cache_set("key1", "value1")
        entity._cache_set("key2", "value2")

        entity._cache_clear()

        assert entity._cache_get("key1") is None
        assert entity._cache_get("key2") is None
        assert entity._cache == {}

    def test_cache_multiple_values(self) -> None:
        """Test cache can store multiple values."""
        from unittest.mock import Mock

        client = Mock()
        entity = MockEntity(client, {"id": "test", "object": "page"})

        entity._cache_set("key1", "value1")
        entity._cache_set("key2", "value2")
        entity._cache_set("key3", {"complex": "object"})

        assert entity._cache_get("key1") == "value1"
        assert entity._cache_get("key2") == "value2"
        assert entity._cache_get("key3") == {"complex": "object"}


class TestBaseEntityNavigation:
    """Tests for navigation methods."""

    @pytest.mark.asyncio
    async def test_parent_is_abstract(self) -> None:
        """Test parent method raises NotImplementedError."""
        from unittest.mock import Mock

        client = Mock()
        entity = MockEntity(client, {"id": "test", "object": "page"})

        # MockEntity implements parent, but BaseEntity doesn't
        # Test that abstract method is enforced
        from better_notion._sdk.base.entity import BaseEntity

        with pytest.raises(TypeError):
            # Can't instantiate abstract class
            BaseEntity(client, {"id": "test", "object": "page"})

    @pytest.mark.asyncio
    async def test_ancestors_single_parent(self) -> None:
        """Test ancestors yields single parent."""
        from unittest.mock import Mock, AsyncMock

        client = Mock()

        parent = MockEntity(client, {"id": "parent-id", "object": "page"})
        child = MockEntity(client, {"id": "child-id", "object": "page"})

        child.parent_value = parent

        ancestors = []
        async for ancestor in child.ancestors():
            ancestors.append(ancestor)

        assert len(ancestors) == 1
        assert ancestors[0] is parent

    @pytest.mark.asyncio
    async def test_ancestors_chain(self) -> None:
        """Test ancestors yields full chain to root."""
        from unittest.mock import Mock

        client = Mock()

        root = MockEntity(client, {"id": "root-id", "object": "page"})
        middle = MockEntity(client, {"id": "middle-id", "object": "page"})
        leaf = MockEntity(client, {"id": "leaf-id", "object": "page"})

        middle.parent_value = root
        leaf.parent_value = middle

        ancestors = []
        async for ancestor in leaf.ancestors():
            ancestors.append(ancestor)

        assert len(ancestors) == 2
        assert ancestors[0] is middle
        assert ancestors[1] is root

    @pytest.mark.asyncio
    async def test_ancestors_stops_at_none(self) -> None:
        """Test ancestors stops when parent is None."""
        from unittest.mock import Mock

        client = Mock()
        entity = MockEntity(client, {"id": "test-id", "object": "page"})
        entity.parent_value = None

        ancestors = []
        async for ancestor in entity.ancestors():
            ancestors.append(ancestor)

        assert len(ancestors) == 0

    @pytest.mark.asyncio
    async def test_descendants_includes_self_if_block(self) -> None:
        """Test descendants includes self if it's a block."""
        from unittest.mock import Mock

        client = Mock()
        block = MockEntity(client, {"id": "block-id", "object": "block"})
        block.children_value = []

        descendants = []
        async for descendant in block.descendants():
            descendants.append(descendant)

        assert len(descendants) == 1
        assert descendants[0] is block

    @pytest.mark.asyncio
    async def test_descendants_with_children(self) -> None:
        """Test descendants includes children blocks."""
        from unittest.mock import Mock

        client = Mock()

        parent_block = MockEntity(client, {"id": "parent-id", "object": "block"})

        child1 = MockEntity(client, {"id": "child1-id", "object": "block"})
        child2 = MockEntity(client, {"id": "child2-id", "object": "block"})

        parent_block.children_value = [child1, child2]
        child1.children_value = []
        child2.children_value = []

        descendants = []
        async for descendant in parent_block.descendants():
            descendants.append(descendant)

        assert len(descendants) == 3  # parent + 2 children
        assert parent_block in descendants
        assert child1 in descendants
        assert child2 in descendants

    @pytest.mark.asyncio
    async def test_descendants_max_depth(self) -> None:
        """Test descendants respects max_depth."""
        from unittest.mock import Mock

        client = Mock()

        root = MockEntity(client, {"id": "root-id", "object": "block"})
        child1 = MockEntity(client, {"id": "child1-id", "object": "block"})
        child2 = MockEntity(client, {"id": "child2-id", "object": "block"})

        root.children_value = [child1]
        child1.children_value = [child2]
        child2.children_value = []

        descendants = []
        async for descendant in root.descendants(max_depth=1):
            descendants.append(descendant)

        assert len(descendants) == 2  # root + child1 only (depth 0 and 1)

    @pytest.mark.asyncio
    async def test_descendants_cycle_detection(self) -> None:
        """Test descendants handles cycles gracefully."""
        from unittest.mock import Mock

        client = Mock()

        # Create cycle: parent -> child1 -> child2 -> child1
        parent = MockEntity(client, {"id": "parent-id", "object": "block"})
        child1 = MockEntity(client, {"id": "child1-id", "object": "block"})
        child2 = MockEntity(client, {"id": "child2-id", "object": "block"})

        parent.children_value = [child1]
        child1.children_value = [child2]
        child2.children_value = [child1]  # Cycle!

        descendants = []
        async for descendant in parent.descendants():
            descendants.append(descendant)

        # Should detect cycle and not infinite loop
        # parent + child1 + child2 (child1 already visited)
        assert len(descendants) == 3

    @pytest.mark.asyncio
    async def test_descendants_non_block_entity(self) -> None:
        """Test descendants doesn't yield non-block entities."""
        from unittest.mock import Mock

        client = Mock()

        page = MockEntity(client, {"id": "page-id", "object": "page"})
        block = MockEntity(client, {"id": "block-id", "object": "block"})

        page.children_value = [block]
        block.children_value = []

        descendants = []
        async for descendant in page.descendants():
            descendants.append(descendant)

        # Page is not a block, so only block should be yielded
        assert len(descendants) == 1
        assert descendants[0] is block

    @pytest.mark.asyncio
    async def test_descendants_handles_not_implemented(self) -> None:
        """Test descendants handles NotImplementedError from children()."""
        from unittest.mock import Mock

        client = Mock()

        class BadEntity(BaseEntity):
            def __init__(self):
                # Skip normal init
                self._client = client
                self._data = {"id": "bad", "object": "block"}
                self._cache = {}

            async def parent(self):
                return None

            def children(self):
                # Return a coroutine that raises NotImplementedError
                async def gen():
                    raise NotImplementedError("No children")
                return gen()

        entity = BadEntity()

        descendants = []
        async for descendant in entity.descendants():
            descendants.append(descendant)

        # Should yield self (the block) and handle the NotImplementedError
        assert len(descendants) == 1
        assert descendants[0] is entity
