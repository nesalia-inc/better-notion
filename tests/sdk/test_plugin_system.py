"""Unit tests for SDK Plugin System."""

from unittest.mock import Mock, MagicMock

import pytest

from better_notion._sdk.cache import Cache
from better_notion._sdk.client import NotionClient
from better_notion._sdk.base.entity import BaseEntity
from better_notion.plugins.base import PluginInterface
from better_notion.plugins.loader import PluginLoader


# ===== Mock Entities for Testing =====

class MockEntity(BaseEntity):
    """Mock entity for testing."""

    def __init__(self, client, data):
        super().__init__(client, data)
        self._title_property = "Name"

    @property
    def title(self) -> str:
        return "Mock Entity"


# ===== Mock Plugins for Testing =====

class MockSDKPlugin(PluginInterface):
    """Mock plugin with SDK extensions."""

    def register_commands(self, app):
        pass

    def register_sdk_models(self):
        return {
            "MockEntity": MockEntity,
        }

    def register_sdk_caches(self, client):
        return {
            "mock_entities": Cache(),
            "mock_cache": Cache(),
        }

    def register_sdk_managers(self, client):
        mock_mgr = Mock()
        mock_mgr.list = Mock(return_value=[])
        return {
            "mock_entities": mock_mgr,
        }

    def sdk_initialize(self, client):
        client._mock_initialized = True


class MinimalPlugin(PluginInterface):
    """Minimal plugin without SDK extensions."""

    def register_commands(self, app):
        pass


# ===== Tests for NotionClient Plugin Support =====


def test_client_has_plugin_attributes():
    """Test that NotionClient initializes plugin-related attributes."""
    client = NotionClient(auth="secret_test_token")

    assert hasattr(client, '_plugin_caches')
    assert hasattr(client, '_plugin_managers')
    assert hasattr(client, '_plugin_models')

    assert isinstance(client._plugin_caches, dict)
    assert isinstance(client._plugin_managers, dict)
    assert isinstance(client._plugin_models, dict)


def test_register_sdk_plugin_with_models():
    """Test registering SDK models."""
    client = NotionClient(auth="secret_test_token")

    client.register_sdk_plugin(models={"MockEntity": MockEntity})

    assert "MockEntity" in client._plugin_models
    assert client._plugin_models["MockEntity"] is MockEntity


def test_register_sdk_plugin_with_caches():
    """Test registering SDK caches."""
    client = NotionClient(auth="secret_test_token")

    cache1 = Cache()
    cache2 = Cache()

    client.register_sdk_plugin(caches={"cache1": cache1, "cache2": cache2})

    assert "cache1" in client._plugin_caches
    assert "cache2" in client._plugin_caches
    assert client._plugin_caches["cache1"] is cache1
    assert client._plugin_caches["cache2"] is cache2


def test_register_sdk_plugin_with_managers():
    """Test registering SDK managers."""
    client = NotionClient(auth="secret_test_token")

    manager1 = Mock()
    manager2 = Mock()

    client.register_sdk_plugin(managers={"mgr1": manager1, "mgr2": manager2})

    assert "mgr1" in client._plugin_managers
    assert "mgr2" in client._plugin_managers
    assert client._plugin_managers["mgr1"] is manager1
    assert client._plugin_managers["mgr2"] is manager2


def test_register_sdk_plugin_with_all():
    """Test registering models, caches, and managers together."""
    client = NotionClient(auth="secret_test_token")

    cache = Cache()
    manager = Mock()

    client.register_sdk_plugin(
        models={"MockEntity": MockEntity},
        caches={"entities": cache},
        managers={"entities": manager}
    )

    assert client._plugin_models["MockEntity"] is MockEntity
    assert client._plugin_caches["entities"] is cache
    assert client._plugin_managers["entities"] is manager


def test_plugin_cache_method():
    """Test accessing plugin caches via plugin_cache method."""
    client = NotionClient(auth="secret_test_token")
    cache = Cache()

    client._plugin_caches["test_cache"] = cache

    result = client.plugin_cache("test_cache")

    assert result is cache


def test_plugin_cache_returns_none_for_missing():
    """Test that plugin_cache returns None for non-existent cache."""
    client = NotionClient(auth="secret_test_token")

    result = client.plugin_cache("nonexistent")

    assert result is None


def test_plugin_manager_method():
    """Test accessing plugin managers via plugin_manager method."""
    client = NotionClient(auth="secret_test_token")
    manager = Mock()

    client._plugin_managers["test_mgr"] = manager

    result = client.plugin_manager("test_mgr")

    assert result is manager


def test_plugin_manager_returns_none_for_missing():
    """Test that plugin_manager returns None for non-existent manager."""
    client = NotionClient(auth="secret_test_token")

    result = client.plugin_manager("nonexistent")

    assert result is None


def test_plugin_model_method():
    """Test accessing plugin models via plugin_model method."""
    client = NotionClient(auth="secret_test_token")

    client._plugin_models["MockEntity"] = MockEntity

    result = client.plugin_model("MockEntity")

    assert result is MockEntity


def test_plugin_model_returns_none_for_missing():
    """Test that plugin_model returns None for non-existent model."""
    client = NotionClient(auth="secret_test_token")

    result = client.plugin_model("NonExistent")

    assert result is None


def test_clear_all_caches_includes_plugin_caches():
    """Test that clear_all_caches also clears plugin caches."""
    client = NotionClient(auth="secret_test_token")

    # Add plugin caches
    cache1 = Cache()
    cache2 = Cache()
    cache1["key1"] = "value1"
    cache2["key2"] = "value2"

    client._plugin_caches["cache1"] = cache1
    client._plugin_caches["cache2"] = cache2

    # Clear all caches
    client.clear_all_caches()

    # Check all caches are cleared
    assert "key1" not in cache1
    assert "key2" not in cache2


def test_get_cache_stats_includes_plugin_caches():
    """Test that get_cache_stats includes plugin cache statistics."""
    client = NotionClient(auth="secret_test_token")

    # Add plugin cache
    cache = Cache()
    cache["key"] = "value"
    _ = cache["key"]  # Generate a hit

    client._plugin_caches["test_cache"] = cache

    # Get stats
    stats = client.get_cache_stats()

    # Check plugin cache stats are included
    assert "plugin:test_cache" in stats
    assert "hits" in stats["plugin:test_cache"]
    assert "misses" in stats["plugin:test_cache"]
    assert "size" in stats["plugin:test_cache"]
    assert "hit_rate" in stats["plugin:test_cache"]


# ===== Tests for PluginInterface SDK Methods =====


def test_plugin_interface_has_sdk_methods():
    """Test that PluginInterface has SDK extension methods."""
    plugin = MinimalPlugin()

    assert hasattr(plugin, 'register_sdk_models')
    assert hasattr(plugin, 'register_sdk_caches')
    assert hasattr(plugin, 'register_sdk_managers')
    assert hasattr(plugin, 'sdk_initialize')


def test_register_sdk_models_default_empty():
    """Test that default register_sdk_models returns empty dict."""
    plugin = MinimalPlugin()

    result = plugin.register_sdk_models()

    assert result == {}


def test_register_sdk_caches_default_empty():
    """Test that default register_sdk_caches returns empty dict."""
    plugin = MinimalPlugin()
    client = NotionClient(auth="secret_test_token")

    result = plugin.register_sdk_caches(client)

    assert result == {}


def test_register_sdk_managers_default_empty():
    """Test that default register_sdk_managers returns empty dict."""
    plugin = MinimalPlugin()
    client = NotionClient(auth="secret_test_token")

    result = plugin.register_sdk_managers(client)

    assert result == {}


def test_sdk_initialize_default_noop():
    """Test that default sdk_initialize does nothing (no-op)."""
    plugin = MinimalPlugin()
    client = NotionClient(auth="secret_test_token")

    # Should not raise any exception
    plugin.sdk_initialize(client)


def test_custom_sdk_plugin_registers_models():
    """Test that custom plugin can register models."""
    plugin = MockSDKPlugin()

    models = plugin.register_sdk_models()

    assert "MockEntity" in models
    assert models["MockEntity"] is MockEntity


def test_custom_sdk_plugin_registers_caches():
    """Test that custom plugin can register caches."""
    plugin = MockSDKPlugin()
    client = NotionClient(auth="secret_test_token")

    caches = plugin.register_sdk_caches(client)

    assert "mock_entities" in caches
    assert "mock_cache" in caches
    assert isinstance(caches["mock_entities"], Cache)
    assert isinstance(caches["mock_cache"], Cache)


def test_custom_sdk_plugin_registers_managers():
    """Test that custom plugin can register managers."""
    plugin = MockSDKPlugin()
    client = NotionClient(auth="secret_test_token")

    managers = plugin.register_sdk_managers(client)

    assert "mock_entities" in managers
    assert hasattr(managers["mock_entities"], 'list')


def test_custom_sdk_plugin_initializes():
    """Test that custom plugin can initialize client."""
    plugin = MockSDKPlugin()
    client = NotionClient(auth="secret_test_token")

    plugin.sdk_initialize(client)

    assert hasattr(client, '_mock_initialized')
    assert client._mock_initialized is True


# ===== Tests for PluginLoader SDK Extension Registration =====


def test_plugin_loader_has_register_sdk_extensions():
    """Test that PluginLoader has register_sdk_extensions method."""
    loader = PluginLoader()

    assert hasattr(loader, 'register_sdk_extensions')
    assert callable(loader.register_sdk_extensions)


def test_plugin_loader_registers_sdk_extensions():
    """Test that PluginLoader can register SDK extensions from loaded plugins."""
    loader = PluginLoader()
    plugin = MockSDKPlugin()

    # Load plugin
    loader.loaded_plugins["mock"] = plugin

    # Create client
    client = NotionClient(auth="secret_test_token")

    # Register SDK extensions
    loader.register_sdk_extensions(client)

    # Verify registrations
    assert "MockEntity" in client._plugin_models
    assert "mock_entities" in client._plugin_caches
    assert "mock_entities" in client._plugin_managers
    assert hasattr(client, '_mock_initialized')


def test_plugin_loader_handles_plugins_without_sdk_extensions():
    """Test that PluginLoader handles plugins without SDK extensions gracefully."""
    loader = PluginLoader()
    plugin = MinimalPlugin()

    # Load plugin
    loader.loaded_plugins["minimal"] = plugin

    # Create client
    client = NotionClient(auth="secret_test_token")

    # Should not raise any exception
    loader.register_sdk_extensions(client)


def test_plugin_loader_discovers_and_registers():
    """Test that PluginLoader can discover and register plugins."""
    loader = PluginLoader()

    # Note: This test assumes no actual plugins are in the test environment
    # In a real scenario, you'd mock the discover() method

    # Create client
    client = NotionClient(auth="secret_test_token")

    # Register SDK extensions (will be empty in test env)
    loader.register_sdk_extensions(client)

    # Should not raise any exception
    assert isinstance(client._plugin_caches, dict)


# ===== Integration Tests =====


def test_full_sdk_plugin_workflow():
    """Test complete SDK plugin workflow from registration to usage."""
    # Create client
    client = NotionClient(auth="secret_test_token")

    # Create plugin
    plugin = MockSDKPlugin()

    # Register plugin's SDK extensions
    models = plugin.register_sdk_models()
    caches = plugin.register_sdk_caches(client)
    managers = plugin.register_sdk_managers(client)

    client.register_sdk_plugin(
        models=models,
        caches=caches,
        managers=managers
    )

    # Initialize plugin
    plugin.sdk_initialize(client)

    # Verify everything is registered
    assert client.plugin_model("MockEntity") is MockEntity
    assert client.plugin_cache("mock_entities") is not None
    assert client.plugin_manager("mock_entities") is not None
    assert client._mock_initialized is True

    # Test cache usage
    cache = client.plugin_cache("mock_entities")
    cache["test_key"] = "test_value"
    assert cache["test_key"] == "test_value"

    # Test manager usage
    mgr = client.plugin_manager("mock_entities")
    mgr.list.assert_not_called()  # Just verify it's the mock


def test_multiple_plugins_can_coexist():
    """Test that multiple plugins can register without conflicts."""
    client = NotionClient(auth="secret_test_token")

    # Create two plugins
    plugin1 = MockSDKPlugin()
    plugin2 = MockSDKPlugin()

    # Register first plugin
    client.register_sdk_plugin(
        models=plugin1.register_sdk_models(),
        caches=plugin1.register_sdk_caches(client),
        managers=plugin1.register_sdk_managers(client)
    )

    # Register second plugin (should not conflict)
    client.register_sdk_plugin(
        models={"AnotherEntity": MockEntity},
        caches={"another_cache": Cache()},
        managers={"another_mgr": Mock()}
    )

    # Verify both plugins' resources are available
    assert "MockEntity" in client._plugin_models
    assert "AnotherEntity" in client._plugin_models
    assert "mock_entities" in client._plugin_caches
    assert "another_cache" in client._plugin_caches
    assert "mock_entities" in client._plugin_managers
    assert "another_mgr" in client._plugin_managers


def test_plugin_caches_are_isolated():
    """Test that different plugin caches don't interfere with each other."""
    client = NotionClient(auth="secret_test_token")

    # Create two separate caches
    cache1 = Cache()
    cache2 = Cache()

    client.register_sdk_plugin(caches={"cache1": cache1, "cache2": cache2})

    # Add data to cache1
    cache1["key"] = "value1"

    # Add data to cache2
    cache2["key"] = "value2"

    # Verify they're independent
    assert cache1["key"] == "value1"
    assert cache2["key"] == "value2"


def test_plugin_cache_stats_are_correct():
    """Test that plugin cache statistics are calculated correctly."""
    client = NotionClient(auth="secret_test_token")

    # Create cache and add some data
    cache = Cache()
    cache["key1"] = "value1"
    cache["key2"] = "value2"

    # Generate some hits using get() method
    _ = cache.get("key1")  # hit
    _ = cache.get("key2")  # hit
    _ = cache.get("key3")  # miss

    client._plugin_caches["test_cache"] = cache

    # Get stats
    stats = client.get_cache_stats()

    # Verify stats
    test_stats = stats["plugin:test_cache"]
    assert test_stats["size"] == 2
    assert test_stats["hits"] == 2
    assert test_stats["misses"] == 1
    assert test_stats["hit_rate"] == 2/3
