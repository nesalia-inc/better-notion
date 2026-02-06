# Entity/Collection Architecture Inconsistency

## Summary

The low-level API has a fundamental architectural inconsistency between Collections and Entities. Collections return raw dictionaries while Entity classes exist but are not consistently used, creating confusion about which API level to use.

## Problem Statement

### Current Issues

**1. Collections Return Raw Dicts**

```python
# Collection methods return raw Notion API data
async def get(self, page_id: str) -> dict[str, Any]:
    return await self._api._request("GET", f"/pages/{page_id}")
```

**2. Entity Classes Exist But Are Not Used**

```python
# Entity class is defined but not returned by collections
class Page:
    def __init__(self, api: NotionAPI, data: dict[str, Any]):
        self._api = api
        self._data = data
        self._modified_properties = {}  # Rich functionality
```

**3. Inconsistent Developer Experience**

```python
# User doesn't know when to use dict vs Entity
page_dict = await api.pages.get("page_id")  # Returns dict
# But there's a Page class with methods!
# How to get Page instance from collection?
```

**4. Two API Levels Without Clear Separation**

- Low-level: Raw dict access (what collections return)
- High-level: Entity objects with methods (exists but not exposed)
- No guidance on when to use which

### Impact

- **Confusion**: Users don't know whether to work with dicts or Entities
- **Broken Abstraction**: Entity classes exist but aren't the primary interface
- **Type Safety**: Dicts don't provide compile-time type checking
- **Discoverability**: Methods like `page.save()` exist but aren't easily accessible
- **Inconsistent Patterns**: Some code uses dicts, some uses Entities

## Proposed Solution

### Option A: Collections Return Entities (Recommended)

```python
class PageCollection:
    async def get(self, page_id: str) -> Page:  # Return Entity
        data = await self._api._request("GET", f"/pages/{page_id}")
        return Page(self._api, data)

    async def create(self, **kwargs) -> Page:
        data = await self._api._request("POST", "/pages", json=kwargs)
        return Page(self._api, data)

    async def list(self, database_id: str, **kwargs) -> list[Page]:
        data = await self._api._request("POST", f"/databases/{database_id}/query", json=kwargs)
        return [Page(self._api, page_data) for page_data in data.get("results", [])]
```

**Benefits:**
- Consistent API - collections always return Entities
- Users get rich methods (save, delete, reload) automatically
- Better type safety with Entity classes
- Clear separation: low-level `_request()` for advanced use, Collections for normal use

**Migration Path:**
1. Change all Collection method return types to Entities
2. Keep `._data` attribute access for raw data if needed
3. Add entity methods for all database operations
4. Document the migration guide

### Option B: Add Dedicated EntityFactory

```python
class EntityFactory:
    """Create Entity instances from raw data."""

    def page(self, data: dict) -> Page:
        return Page(self._api, data)

    def database(self, data: dict) -> Database:
        return Database(self._api, data)

# Usage
factory = EntityFactory(api)
raw_data = await api.pages.get("page_id")
page = factory.page(raw_data)
```

**Benefits:**
- Clear distinction between raw data and entities
- Backward compatible with existing code
- Explicit conversion

**Drawbacks:**
- More boilerplate for users
- Still confusing - when to use factory vs collections?

### Option C: Dual API (Both Raw and Entity)

```python
class PageCollection:
    # Raw methods (backward compatible)
    async def get_raw(self, page_id: str) -> dict:
        ...

    # Entity methods (new recommended way)
    async def get(self, page_id: str) -> Page:
        ...

# Or via separate namespaces
api.pages.get("id")      # Returns Entity (new default)
api.pages_raw.get("id")  # Returns dict (for advanced use)
```

**Benefits:**
- Backward compatible
- Gradual migration path

**Drawbacks:**
- API surface area doubles
- Still confusing - which one to use?

## Recommendation

**Implement Option A** - Collections should return Entity objects by default.

### Rationale

1. **Primary Use Case**: Most users want Entity objects with methods
2. **Type Safety**: Entities provide better compile-time guarantees
3. **Rich Functionality**: save(), delete(), reload() are useful
4. **Object-Oriented**: Matches the advertised "object-oriented interface"
5. **Discovery**: Methods are discoverable via IDE autocomplete

### For Advanced Users

Keep low-level access available:

```python
# For users who need raw dict access
page = await api.pages.get("page_id")
raw_data = page._data  # Access raw Notion API data

# Or use _request() directly
raw = await api._request("GET", f"/pages/{page_id}")
```

### Implementation Steps

1. **Update all Collection method signatures**
   - Return types: `dict` → `Entity`
   - Update type hints

2. **Complete Entity implementations**
   - Database.query() and reload()
   - Ensure all entities have save(), delete(), reload()

3. **Update type hints throughout**
   - Collections return Entity types
   - Generics for specific entity types

4. **Add migration guide**
   - Document breaking changes
   - Show before/after examples
   - Explain how to access raw data if needed

5. **Update tests**
   - Test Entity methods
   - Test Collection → Entity conversion

6. **Update documentation**
   - All examples use Entities
   - Document raw data access via `._data`

## Breaking Changes

This is a **breaking change** that requires a major version bump (3.0.0).

### Migration Guide

```python
# Old way (2.x)
page_dict = await api.pages.get("page_id")
title = page_dict["properties"]["title"]

# New way (3.x)
page = await api.pages.get("page_id")
title = page.title  # Or page.properties if needed

# For raw data access:
page = await api.pages.get("page_id")
raw = page._data  # Still available
```

## Related Issues

- #051: Complete Database entity implementation
- #054: Add property validation to entities
- #055: Standardize property builder API

## Success Metrics

1. ✅ All Collection methods return Entity objects
2. ✅ All Entities have complete method implementations
3. ✅ Type hints are accurate and useful
4. ✅ Documentation shows Entity-first approach
5. ✅ Raw data still accessible via `._data` attribute

## Timeline

- **Design review**: 1 day
- **Implementation**: 3-5 days
- **Testing**: 2 days
- **Documentation**: 1 day
- **Total**: 1-2 weeks

## Priority

**🔴 Critical** - This is a foundational architectural issue that affects:
- API consistency
- Type safety
- Developer experience
- Future maintainability

Every new feature builds on this architecture, so fixing it sooner prevents accumulating more technical debt.
