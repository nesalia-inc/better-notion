# Incomplete Database Entity Implementation

## Summary

The `Database` entity class has `NotImplementedError` for core methods (`query()` and `reload()`), making it incomplete and unusable. This breaks the expected API consistency across entity types.

## Problem Statement

### Current State

```python
class Database:
    """Represents a Notion database."""

    async def query(self, **kwargs):
        """Query this database."""
        raise NotImplementedError("Database.query() not yet implemented")

    async def reload(self):
        """Reload database data from Notion."""
        raise NotImplementedError("Database.reload() not yet implemented")
```

### Inconsistency with Other Entities

```python
# Page entity - fully implemented
class Page:
    async def save(self): ...      # ✅ Implemented
    async def reload(self): ...    # ✅ Implemented
    async def delete(self): ...    # ✅ Implemented

# Database entity - incomplete
class Database:
    async def query(self): ...     # ❌ NotImplementedError
    async def reload(self): ...    # ❌ NotImplementedError
    async def save(self): ...      # ❌ Doesn't exist
    async def delete(self): ...    # ❌ Doesn't exist
```

### Impact

1. **Broken Polymorphism**: Can't use Database and Page interchangeably
2. **API Confusion**: Users expect entities to have consistent methods
3. **Blocking Issues**: Core database operations are unavailable
4. **Poor Developer Experience**: NotImplementedErrors at runtime
5. **Incomplete Type Safety**: Type hints suggest methods exist but they crash

## Proposed Solution

### 1. Implement Database.query()

```python
class Database:
    async def query(self, **kwargs) -> list[Page]:
        """Query this database.

        Args:
            **kwargs: Query parameters (filter, sorts, start_cursor, etc.)

        Returns:
            List of Page objects from the query results.

        Raises:
            ValidationError: If query parameters are invalid.
            NotFoundError: If the database no longer exists.
        """
        response = await self._api._request(
            "POST",
            f"/databases/{self.id}/query",
            json=kwargs,
        )

        from better_notion._api.entities import Page
        results = response.get("results", [])
        return [Page(self._api, page_data) for page_data in results]
```

**Implementation Notes:**
- Reuse existing DatabaseCollection.query() logic
- Return Page entities (consistent with Entity-first approach)
- Support all query parameters (filter, sorts, start_cursor, page_size)

### 2. Implement Database.reload()

```python
class Database:
    async def reload(self) -> None:
        """Reload database data from Notion.

        Fetches the latest database schema and data from Notion.

        Raises:
            NotFoundError: If the database no longer exists.
        """
        data = await self._api._request("GET", f"/databases/{self.id}")
        self._data = data
        self._modified = False  # Reset modification tracking
```

**Implementation Notes:**
- Similar to Page.reload()
- Updates internal `_data` with fresh data
- Resets modification tracking flags

### 3. Add Database.save() (Modification Tracking)

```python
class Database:
    def __init__(self, api: NotionAPI, data: dict[str, Any]) -> None:
        self._api = api
        self._data = data
        self._modified_properties: dict[str, Any] = {}  # Add this
        self._modified = False

    async def update_schema(self, **kwargs) -> None:
        """Update database schema properties.

        Args:
            **kwargs: Schema properties to update.
        """
        # Track schema modifications
        self._modified_properties.update(kwargs)
        self._modified = True

    async def save(self) -> None:
        """Save schema changes to Notion.

        Raises:
            ValidationError: If schema is invalid.
            NotFoundError: If database no longer exists.
        """
        if not self._modified:
            return

        # Notion API doesn't support partial schema updates
        # Need to send the full schema
        await self._api._request(
            "PATCH",
            f"/databases/{self.id}",
            json={"properties": self._data["properties"]}
        )

        self._modified_properties = {}
        self._modified = False
```

**Implementation Notes:**
- Add modification tracking (like Page entity)
- Note: Notion API has limitations on schema updates
- May need to recreate database for some schema changes

### 4. Add Database.delete()

```python
class Database:
    async def delete(self) -> None:
        """Delete (archive) this database.

        Raises:
            NotFoundError: If the database no longer exists.
        """
        await self._api._request("DELETE", f"/blocks/{self.id}")
        self._data["archived"] = True
```

**Implementation Notes:**
- Uses DELETE /blocks/{id} (databases are blocks)
- Sets archived flag in local data
- Consistent with Page.delete()

### 5. Add Database Properties

```python
class Database:
    @property
    def created_time(self) -> datetime:
        """Get the creation time."""
        from better_notion.utils.helpers import parse_datetime
        return parse_datetime(self._data["created_time"])

    @property
    def last_edited_time(self) -> datetime:
        """Get the last edited time."""
        from better_notion.utils.helpers import parse_datetime
        return parse_datetime(self._data["last_edited_time"])

    @property
    def archived(self) -> bool:
        """Check if database is archived."""
        return self._data.get("archived", False)

    @property
    def parent(self) -> dict[str, Any]:
        """Get the parent object."""
        return self._data["parent"]
```

**Implementation Notes:**
- Add common properties (consistent with Page entity)
- Use helper functions for datetime parsing
- Provide type hints for all properties

## Implementation Plan

### Phase 1: Core Methods (1 day)
1. Implement `Database.query()` - returns list of Page entities
2. Implement `Database.reload()` - fetches fresh data
3. Add basic tests

### Phase 2: Entity Consistency (1 day)
1. Add `Database.save()` with modification tracking
2. Add `Database.delete()`
3. Add common properties (created_time, last_edited_time, archived, parent)
4. Update type hints

### Phase 3: Testing & Documentation (1 day)
1. Write comprehensive tests
2. Add docstring examples
3. Update API documentation

## Breaking Changes

**None** - This is purely additive. No existing code will break.

## API Examples

### Before (Broken)

```python
database = await api.databases.get("db_id")
# What now? Can't query, can't reload

results = await database.query(filter=...)
# NotImplementedError: Database.query() not yet implemented
```

### After (Working)

```python
# Get database entity
database = await api.databases.get("db_id")

# Query database
pages = await database.query(
    filter={"property": "Status", "select": {"equals": "In Progress"}}
)

# Reload to get fresh schema
await database.reload()

# Update schema
database.update_schema(new_property_config)
await database.save()

# Delete database
await database.delete()
```

## Related Issues

- #050: Entity/Collection architecture consistency
- #054: Add property validation to entities

## Success Metrics

1. ✅ Database.query() returns Page entities
2. ✅ Database.reload() fetches fresh data
3. ✅ Database has save(), delete() methods
4. ✅ Database has same properties as Page (created_time, etc.)
5. ✅ All methods tested and documented

## Priority

**🔴 Critical** - Core functionality is completely broken:

1. **Runtime Errors**: Methods raise NotImplementedError at runtime
2. **Inconsistent API**: Database doesn't match other entity types
3. **Unusable**: Can't query databases from entity objects
4. **Type Safety**: Methods exist in type hints but crash

This prevents the Entity system from being used as designed and forces users to work with raw dictionaries, defeating the purpose of having Entity classes.

## Timeline

- **Implementation**: 2-3 days
- **Testing**: 1 day
- **Documentation**: 0.5 day
- **Total**: 3-4 days
