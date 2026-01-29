# SDK Plugin System

## Summary

Design and implement a plugin system for the Better Notion SDK that allows plugins to register custom models, managers, and caches without polluting the core SDK.

## Problem Statement

### Current Limitations

The Better Notion CLI has a robust plugin system for extending commands and data processing, but the SDK lacks equivalent extensibility. This creates architectural problems:

**1. Core SDK Pollution**
Plugins that need SDK models must modify core files:
```python
# Current bad practice - modifying core SDK
class NotionClient:
    def __init__(self):
        self._organization_cache = Cache()  # Plugin-specific!
        self._project_cache = Cache()        # Plugin-specific!
```

**2. Tight Coupling**
Official plugins like `agents` cannot add domain-specific models without:
- Embedding them in the core SDK (violates separation of concerns)
- Living outside the SDK ecosystem (loses caching, manager benefits)
- Duplicating infrastructure code (reinvent caching for each plugin)

**3. Scalability Issues**
As more official plugins are added:
- Templates plugin → needs `Template` model
- Workflows plugin → needs `Workflow` model
- Analytics plugin → needs `Metric` model
- Each would require core SDK modifications

**4. Inconsistent Developer Experience**
CLI plugins can extend functionality seamlessly:
```python
class MyPlugin(PluginInterface):
    def register_commands(self, app: typer.Typer) -> None:
        # Easy CLI extension
        app.command("my-command")(my_command)
```

But SDK extensions require core modifications.

### What's Missing

1. **No Model Registration**: Plugins can't register custom SDK models
2. **No Cache Registration**: Plugins can't add dedicated caches to NotionClient
3. **No Manager Registration**: Plugins can't add managers to client
4. **No Lifecycle Hooks**: Plugins can't hook into client initialization

## Proposed Solution

Implement an SDK plugin system that allows plugins to register extensions with NotionClient.

### Architecture

```python
# 1. SDK Plugin Interface
class SDKPluginInterface(Protocol):
    """Interface for SDK-level plugins."""

    def register_models(self) -> dict[str, type[BaseEntity]]:
        """Register custom model classes.

        Returns:
            Dict mapping model names to model classes
        """
        ...

    def register_caches(self, client: NotionClient) -> dict[str, Cache]:
        """Register custom caches with the client.

        Args:
            client: NotionClient instance to register caches with

        Returns:
            Dict mapping cache names to Cache instances
        """
        ...

    def register_managers(self, client: NotionClient) -> dict[str, Any]:
        """Register custom managers with the client.

        Args:
            client: NotionClient instance

        Returns:
            Dict mapping manager names to manager instances
        """
        ...

    def initialize(self, client: NotionClient) -> None:
        """Initialize plugin-specific resources.

        Called after all registrations are complete.
        """
        ...

# 2. Extended NotionClient
class NotionClient:
    def __init__(self, auth: str, sdk_plugins: list[SDKPluginInterface] | None = None):
        # ... existing initialization ...

        # Plugin-managed resources
        self._plugin_caches: dict[str, Cache] = {}
        self._plugin_managers: dict[str, Any] = {}
        self._plugin_models: dict[str, type[BaseEntity]] = {}

        # Register plugins
        if sdk_plugins:
            for plugin in sdk_plugins:
                self._register_sdk_plugin(plugin)

    def _register_sdk_plugin(self, plugin: SDKPluginInterface) -> None:
        """Register an SDK plugin with this client."""
        # Register models
        for name, model_class in plugin.register_models().items():
            self._plugin_models[name] = model_class

        # Register caches
        for name, cache in plugin.register_caches(self).items():
            self._plugin_caches[name] = cache

        # Register managers
        for name, manager in plugin.register_managers(self).items():
            self._plugin_managers[name] = manager

        # Initialize plugin
        plugin.initialize(self)

    @property
    def plugin_cache(self, name: str) -> Cache | None:
        """Access a plugin-registered cache."""
        return self._plugin_caches.get(name)

    @property
    def plugin_manager(self, name: str) -> Any | None:
        """Access a plugin-registered manager."""
        return self._plugin_managers.get(name)
```

### Usage Example

```python
# agents/plugin_sdk.py
class AgentsSDKPlugin:
    """SDK extension for agents workflow system."""

    def register_models(self) -> dict[str, type[BaseEntity]]:
        """Register workflow models."""
        return {
            "Organization": Organization,
            "Project": Project,
            "Version": Version,
            "Task": Task,
        }

    def register_caches(self, client: NotionClient) -> dict[str, Cache]:
        """Register workflow caches."""
        return {
            "organizations": Cache(),
            "projects": Cache(),
            "versions": Cache(),
            "tasks": Cache(),
        }

    def register_managers(self, client: NotionClient) -> dict[str, Any]:
        """Register workflow managers."""
        return {
            "organizations": OrganizationManager(client),
            "projects": ProjectManager(client),
            "versions": VersionManager(client),
            "tasks": TaskManager(client),
        }

    def initialize(self, client: NotionClient) -> None:
        """Initialize workflow resources."""
        # Load database IDs from config
        # Validate workspace setup
        # etc.

# Usage in client initialization
client = NotionClient(
    auth=token,
    sdk_plugins=[AgentsSDKPlugin()]
)

# Use plugin models
org = await Organization.get(org_id, client=client)

# Use plugin managers
projects = await client.plugin_manager("projects").list()

# Access plugin caches
if org_id in client.plugin_cache("organizations"):
    org = client.plugin_cache("organizations")[org_id]
```

### Unified Plugin Interface

Extend the existing `PluginInterface` to support both CLI and SDK extensions:

```python
# plugins/base.py
class PluginInterface(ABC):
    """Enhanced plugin interface supporting both CLI and SDK extensions."""

    @abstractmethod
    def register_commands(self, app: typer.Typer) -> None:
        """Register CLI commands."""
        pass

    # New SDK extension methods (optional)

    def register_sdk_models(self) -> dict[str, type[BaseEntity]]:
        """Register SDK models. Optional - default empty."""
        return {}

    def register_sdk_caches(self, client: NotionClient) -> dict[str, Cache]:
        """Register SDK caches. Optional - default empty."""
        return {}

    def register_sdk_managers(self, client: NotionClient) -> dict[str, Any]:
        """Register SDK managers. Optional - default empty."""
        return {}

    def sdk_initialize(self, client: NotionClient) -> None:
        """Initialize SDK resources. Optional - default no-op."""
        pass
```

### Plugin Auto-Discovery

The CLI plugin loader can automatically register SDK extensions:

```python
# plugins/loader.py
async def load_plugins(
    app: typer.Typer,
    client: NotionClient
) -> list[PluginInterface]:
    """Load all plugins and register both CLI and SDK extensions."""

    plugins = []

    for plugin_class in OFFICIAL_PLUGINS:
        plugin = plugin_class()

        # Register CLI commands
        plugin.register_commands(app)

        # Register SDK extensions
        if hasattr(plugin, 'register_sdk_models'):
            for name, model in plugin.register_sdk_models().items():
                client._plugin_models[name] = model

        if hasattr(plugin, 'register_sdk_caches'):
            for name, cache in plugin.register_sdk_caches(client).items():
                client._plugin_caches[name] = cache

        if hasattr(plugin, 'register_sdk_managers'):
            for name, manager in plugin.register_sdk_managers(client).items():
                client._plugin_managers[name] = manager

        # Initialize SDK resources
        if hasattr(plugin, 'sdk_initialize'):
            plugin.sdk_initialize(client)

        plugins.append(plugin)

    return plugins
```

## Benefits

1. **Separation of Concerns**: Plugins maintain their own models/caches without polluting core SDK
2. **Scalability**: Unlimited plugins can be added without core modifications
3. **Consistency**: Unified plugin system for both CLI and SDK
4. **Backward Compatibility**: Existing code continues to work (all methods optional)
5. **Developer Experience**: Clean API for plugin authors
6. **Performance**: Dedicated caches prevent API rate limits
7. **Type Safety**: Model classes maintain type hints and IDE support

## Implementation Plan

### Phase 1: Core Infrastructure (1 week)

**Deliverables:**
1. `SDKPluginInterface` protocol class
2. Extend `NotionClient` with plugin support:
   - `_plugin_caches`, `_plugin_managers`, `_plugin_models` attributes
   - `_register_sdk_plugin()` method
   - `plugin_cache()`, `plugin_manager()` properties
3. Update `PluginInterface` with optional SDK methods
4. Update plugin loader to register SDK extensions

**Files:**
- `better_notion/_sdk/plugins.py` (new)
- `better_notion/_sdk/client.py` (modify)
- `better_notion/plugins/base.py` (extend)
- `better_notion/plugins/loader.py` (update)

### Phase 2: Agents Plugin Migration (1 week)

**Deliverables:**
1. Create `AgentsSDKPlugin` class
2. Move model definitions from core to plugin
3. Update agents plugin to implement SDK interface
4. Test that agents plugin works with new system

**Files:**
- `better_notion/plugins/official/agents_sdk.py` (new)
- `better_notion/plugins/official/agents.py` (update)
- `tests/workflow/test_sdk_plugin.py` (new)

### Phase 3: Documentation & Examples (3 days)

**Deliverables:**
1. SDK plugin development guide
2. Example plugin with SDK extensions
3. Migration guide for existing plugins
4. Update main documentation

### Phase 4: Testing & Validation (2 days)

**Deliverables:**
1. Unit tests for SDK plugin system
2. Integration tests with agents plugin
3. Performance benchmarks (cache effectiveness)
4. Backward compatibility tests

## Alternatives Considered

### Alternative A: Use page_cache for Everything

**Approach:** Use existing `page_cache` for all custom models.

**Pros:**
- Simple, no new infrastructure
- Works immediately

**Cons:**
- Potential cache key collisions
- No namespace isolation
- Can't set cache policies per model type
- Mixing concerns in single cache

**Verdict:** Workable short-term, not ideal long-term

### Alternative B: Standalone Cache in Plugin

**Approach:** Each plugin manages its own cache independently.

**Pros:**
- Complete isolation
- No core SDK modifications

**Cons:**
- Duplicates cache logic
- Inconsistent API (different from core models)
- More boilerplate for plugin authors
- Harder to test (no unified interface)

**Verdict:** Too much duplication, breaks consistency

### Alternative C: Decorator-Based Registration

**Approach:** Use decorators to register models/caches:

```python
@sdk_model
class Organization(BaseEntity):
    pass

@sdk_cache("organizations")
def get_org_cache():
    return Cache()
```

**Pros:**
- Declarative syntax
- Familiar pattern (similar to Flask/Django)

**Cons:**
- Less explicit
- Harder to debug
- Decorators can confuse IDEs
- Still needs core infrastructure

**Verdict:** Nice sugar, but doesn't solve core problem

## Migration Strategy

### For Existing Code

**Zero Breaking Changes:**
- All SDK plugin methods are optional
- Existing code continues to work unchanged
- New behavior is opt-in via plugin registration

### For Plugin Authors

**Step 1: Implement SDK Interface**
```python
# Before
class MyPlugin(PluginInterface):
    def register_commands(self, app) -> None:
        pass

# After
class MyPlugin(PluginInterface):
    def register_commands(self, app) -> None:
        pass  # Still required

    def register_sdk_models(self) -> dict[str, type]:
        return {"MyModel": MyModel}  # New, optional
```

**Step 2: Create Model Classes**
```python
class MyModel(BaseEntity):
    def __init__(self, client, data):
        super().__init__(client, data)

    @classmethod
    async def get(cls, model_id, *, client):
        # Check plugin cache
        if model_id in client.plugin_cache("mymodel"):
            return client.plugin_cache("mymodel")[model_id]

        # Fetch from API
        data = await client.api.pages.get(page_id=model_id)
        model = cls(client, data)

        # Cache it
        client.plugin_cache("mymodel")[model_id] = model
        return model
```

**Step 3: Register with Client**
```python
client = NotionClient(
    auth=token,
    sdk_plugins=[MySDKPlugin()]
)
```

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| **Increased complexity** | Medium | Comprehensive documentation, examples |
| **Performance overhead** | Low | Minimal - just dictionary lookups |
| **Breaking changes** | Low | All optional, backward compatible |
| **Cache key collisions** | Low | Namespaced caches per plugin |
| **Plugin conflicts** | Medium | Validation in plugin loader, clear errors |

## Success Metrics

1. ✅ Agents plugin can register models without modifying core SDK
2. ✅ Plugin caches work as efficiently as core caches
3. ✅ Zero breaking changes to existing code
4. ✅ Plugin development time reduced by 50%
5. ✅ Documentation clear enough for 3rd party plugins

## Related Issues

This enhancement enables:
- #031: Workflow Management System (agents plugin SDK models)
- #016: Templates System (template model SDK extension)
- Future plugins that need SDK-level integration

## Next Steps

1. **Get approval** for this architectural enhancement
2. **Create proof-of-concept** with agents plugin
3. **Implement Phase 1** (core infrastructure)
4. **Migrate agents plugin** to validate approach
5. **Document and refine** based on real usage
6. **Release as minor version bump** (1.1.0)

---

## Appendix: Example Full Implementation

```python
# ===== SDK PLUGIN =====
from typing import Any
from better_notion._sdk.base.entity import BaseEntity
from better_notion._sdk.cache import Cache
from better_notion.plugins.base import PluginInterface

class AgentsSDKPlugin:
    """SDK plugin for agents workflow system."""

    def register_commands(self, app: typer.Typer) -> None:
        """Register CLI commands."""
        # Existing agents commands...
        pass

    def register_sdk_models(self) -> dict[str, type[BaseEntity]]:
        """Register workflow models."""
        from better_notion._sdk.models.workflow import (
            Organization, Project, Version, Task
        )
        return {
            "Organization": Organization,
            "Project": Project,
            "Version": Version,
            "Task": Task,
        }

    def register_sdk_caches(self, client: NotionClient) -> dict[str, Cache]:
        """Register workflow caches."""
        return {
            "organizations": Cache(),
            "projects": Cache(),
            "versions": Cache(),
            "tasks": Cache(),
        }

    def register_sdk_managers(self, client: NotionClient) -> dict[str, Any]:
        """Register workflow managers."""
        from better_notion._sdk.managers.workflow import (
            OrganizationManager, ProjectManager
        )
        return {
            "organizations": OrganizationManager(client),
            "projects": ProjectManager(client),
        }

    def sdk_initialize(self, client: NotionClient) -> None:
        """Initialize workflow resources."""
        # Load workspace config
        # Validate database IDs
        # etc.
        pass

# ===== MODEL USING PLUGIN CACHE =====
class Organization(BaseEntity):
    @classmethod
    async def get(cls, org_id: str, *, client: NotionClient) -> "Organization":
        """Get organization by ID."""
        # Check plugin cache
        cache = client.plugin_cache("organizations")
        if cache and org_id in cache:
            return cache[org_id]

        # Fetch from API
        data = await client.api.pages.get(page_id=org_id)
        org = cls(client, data)

        # Cache it
        if cache:
            cache[org_id] = org

        return org

# ===== USAGE =====
# Plugin is auto-loaded by CLI
client = get_client()  # Already has agents plugin registered

# Use models
org = await Organization.get(org_id, client=client)

# Use managers
projects = await client.plugin_manager("projects").list()

# Access caches
if org_id in client.plugin_cache("organizations"):
    org = client.plugin_cache("organizations")[org_id]
```

This approach provides clean separation, extensibility, and maintains consistency with the existing plugin architecture.
