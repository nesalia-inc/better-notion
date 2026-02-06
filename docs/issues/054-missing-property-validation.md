# Missing Property Validation in Entities

## Summary

Entity classes allow arbitrary properties to be set without validation. The `update()` method accepts any keyword arguments and blindly adds them to `_modified_properties`, which can cause API errors that are only discovered at runtime when calling Notion's API.

## Problem Statement

### Current State

```python
# Page entity (page.py:115-135)
async def update(self, **kwargs: Any) -> None:
    """Update page properties.

    Args:
        **kwargs: Properties to update.
    """
    # Special handling for 'properties' kwarg - unpack it
    if "properties" in kwargs:
        self._modified_properties.update(kwargs["properties"])

    # Handle other kwargs normally (e.g., 'archived')
    for key, value in kwargs.items():
        if key != "properties":
            self._modified_properties[key] = value

    self._modified = True  # ❌ Modified even if empty or invalid
```

### Issues

**1. No Property Name Validation**

```python
page = await api.pages.get("page_id")

# Typos won't be caught until API call
await page.update(tille="New Title")  # ❌ Typo: tilde instead of title
await page.save()  # API error: "Invalid property name"
```

**2. No Property Value Validation**

```python
# Can set invalid values
await page.update(Status="InvalidStatus")  # ❌ Not a valid select option
await page.save()  # API error at runtime
```

**3. No Type Checking**

```python
# Wrong types accepted silently
await page.update(title=123)  # ❌ Should be string/Title object
await page.save()  # API error at runtime
```

**4. Accepts Arbitrary Keywords**

```python
# Completely made-up property
await page.update(fake_property="some value")
await page.save()  # Only fails when calling Notion API
```

**5. No Schema Awareness**

```python
# Entity has no knowledge of database schema
# Doesn't know which properties are valid for this page
# Can't validate against database schema
```

### Impact

1. **Late Error Detection**: Errors only discovered when calling Notion API
2. **Poor Developer Experience**: No feedback until runtime
3. **Type Safety**: Type hints suggest safety but don't exist
4. **Debugging Difficulty**: Hard to find which property is invalid
5. **API Wastage**: Unnecessary API calls to discover validation errors

## Proposed Solution

### 1. Add Property Name Validation

```python
class Page:
    # Define valid top-level properties
    VALID_PROPERTIES = {
        "properties",     # Page properties (title, etc.)
        "archived",       # Archive status
        "icon",           # Page icon
        "cover",          # Page cover
        # "parent" is not allowed (immutable)
    }

    async def update(self, **kwargs: Any) -> None:
        """Update page properties.

        Args:
            **kwargs: Properties to update.

        Raises:
            ValueError: If an invalid property name is provided.
            ValidationError: If property validation fails.
        """
        # Validate property names
        for key in kwargs:
            if key not in self.VALID_PROPERTIES:
                raise ValueError(
                    f"Invalid page property: {key!r}. "
                    f"Valid properties are: {', '.join(sorted(self.VALID_PROPERTIES))}"
                )

        # Special handling for 'properties' kwarg
        if "properties" in kwargs:
            self._modified_properties.update(kwargs["properties"])

        # Handle other kwargs
        for key, value in kwargs.items():
            if key != "properties":
                self._modified_properties[key] = value

        # Only mark as modified if we actually added something
        if kwargs:
            self._modified = True
```

### 2. Add Property Value Validation

```python
class Page:
    def _validate_property_value(self, name: str, value: Any) -> Any:
        """Validate a property value.

        Args:
            name: Property name
            value: Property value to validate

        Returns:
            Validated/converted value

        Raises:
            ValueError: If value is invalid
        """
        if name == "archived":
            if not isinstance(value, bool):
                raise ValueError(f"archived must be a boolean, got {type(value).__name__}")
            return value

        elif name == "icon":
            # Icon can be None, dict, or str (emoji)
            if value is None:
                return None
            if isinstance(value, str):
                return {"type": "emoji", "emoji": value}
            if isinstance(value, dict):
                return value
            raise ValueError(f"icon must be None, str, or dict, got {type(value).__name__}")

        elif name == "cover":
            # Cover can be None, str (URL), or dict
            if value is None:
                return None
            if isinstance(value, str):
                return {"type": "external", "external": {"url": value}}
            if isinstance(value, dict):
                return value
            raise ValueError(f"cover must be None, str, or dict, got {type(value).__name__}")

        elif name == "properties":
            if not isinstance(value, dict):
                raise ValueError(f"properties must be a dict, got {type(value).__name__}")

            # Validate individual property values
            validated = {}
            for prop_name, prop_value in value.items():
                validated[prop_name] = self._validate_property(prop_name, prop_value)
            return validated

        return value
```

### 3. Add Schema-Based Validation (Advanced)

```python
class Page:
    def __init__(self, api: NotionAPI, data: dict[str, Any]) -> None:
        self._api = api
        self._data = data
        self._modified_properties: dict[str, Any] = {}
        self._modified = False
        self._schema: dict[str, Any] | None = None  # Cached schema

    async def _get_schema(self) -> dict[str, Any]:
        """Fetch and cache the database schema for this page.

        Returns:
            Database schema property definitions

        Raises:
            RuntimeError: If page is not in a database
        """
        if self._schema is not None:
            return self._schema

        # Fetch parent database schema
        parent_id = self._data.get("parent", {}).get("database_id")
        if not parent_id:
            raise RuntimeError("Page is not in a database, no schema available")

        db_data = await self._api._request("GET", f"/databases/{parent_id}")
        self._schema = db_data.get("properties", {})
        return self._schema

    def _validate_against_schema(self, name: str, value: Any) -> None:
        """Validate property against database schema.

        Args:
            name: Property name
            value: Property value

        Raises:
            ValueError: If property doesn't exist in schema
            ValidationError: If value doesn't match schema type
        """
        import asyncio

        # Schema fetch is async, but validation is sync
        # This is a limitation - we'll do best-effort validation
        schema = getattr(self, "_schema", None)
        if not schema:
            # Schema not loaded, skip validation
            return

        if name not in schema:
            raise ValueError(
                f"Property {name!r} does not exist in database schema. "
                f"Valid properties: {', '.join(schema.keys())}"
            )

        prop_schema = schema[name]
        prop_type = prop_schema.get("type")

        # Validate based on type
        if prop_type == "title":
            if not isinstance(value, str) and not hasattr(value, "to_dict"):
                raise ValueError(f"Title property must be a string or Title object")

        elif prop_type == "rich_text":
            if not isinstance(value, str) and not hasattr(value, "to_dict"):
                raise ValueError(f"Rich text property must be a string or RichText object")

        elif prop_type == "number":
            if not isinstance(value, (int, float)) and not hasattr(value, "to_dict"):
                raise ValueError(f"Number property must be numeric")

        elif prop_type == "select":
            if not isinstance(value, str) and not hasattr(value, "to_dict"):
                raise ValueError(f"Select property must be a string or Select object")

        # ... other property types
```

### 4. Provide Property Builder Helpers

```python
class Page:
    @property
    def properties(self) -> "PageProperties":
        """Get a properties helper object."""
        return PageProperties(self)

class PageProperties:
    """Helper for setting page properties with validation."""

    def __init__(self, page: Page):
        self._page = page

    def set_title(self, title: str) -> None:
        """Set the page title."""
        from better_notion._api.properties import Title
        self._page._modified_properties["title"] = Title(content=title).to_dict()
        self._page._modified = True

    def set_text(self, property_name: str, text: str) -> None:
        """Set a rich text property."""
        from better_notion._api.properties import RichText
        self._page._modified_properties[property_name] = RichText(
            name=property_name,
            content=text
        ).to_dict()
        self._page._modified = True

    def set_select(self, property_name: str, option: str) -> None:
        """Set a select property."""
        from better_notion._api.properties import Select
        self._page._modified_properties[property_name] = Select(
            name=property_name,
            value=option
        ).to_dict()
        self._page._modified = True

    def set_date(self, property_name: str, date: str | datetime) -> None:
        """Set a date property."""
        from better_notion._api.properties import Date
        self._page._modified_properties[property_name] = Date(
            name=property_name,
            value=date
        ).to_dict()
        self._page._modified = True

# Usage
page = await api.pages.get("page_id")
page.properties.set_title("New Title")
page.properties.set_select("Status", "In Progress")
page.properties.set_date("Due Date", "2025-02-10")
await page.save()
```

## Implementation Plan

### Phase 1: Basic Validation (1 day)

1. Add `VALID_PROPERTIES` constant to all entities
2. Validate property names in `update()` method
3. Add proper error messages
4. Add unit tests

### Phase 2: Value Validation (2 days)

1. Implement `_validate_property_value()` for each entity
2. Add type checking for top-level properties
3. Add validation for common property types
4. Add unit tests for validation

### Phase 3: Schema-Based Validation (2 days, optional)

1. Add schema fetching to entities
2. Implement `_validate_against_schema()`
3. Cache schemas for performance
4. Add tests

### Phase 4: Property Helpers (1 day, optional)

1. Create property helper classes
2. Add fluent setters
3. Document usage
4. Add examples

## Code Examples

### Before (Current - No Validation)

```python
page = await api.pages.get("page_id")

# Typos not caught
await page.update(tille="New Title")  # ❌ Typo
await page.save()  # API error: validation_error

# Invalid values not caught
await page.update(archived="not a bool")  # ❌ Wrong type
await page.save()  # API error at runtime

# Arbitrary properties accepted
await page.update(fake_property="value")  # ❌ Doesn't exist
await page.save()  # API error at runtime
```

### After (With Validation)

```python
page = await api.pages.get("page_id")

# Typos caught immediately
await page.update(tille="New Title")
# ValueError: Invalid page property: 'tilde'. Valid properties are: archived, cover, icon, properties

# Invalid values caught immediately
await page.update(archived="not a bool")
# ValueError: archived must be a boolean, got str

# Arbitrary properties rejected
await page.update(fake_property="value")
# ValueError: Invalid page property: 'fake_property'. Valid properties are: archived, cover, icon, properties

# Using property helpers (type-safe)
page.properties.set_title("New Title")
page.properties.set_select("Status", "In Progress")
page.properties.set_date("Due Date", "2025-02-10")
await page.save()
# ✅ All validation done before API call
```

## Breaking Changes

**Minor** - Code that previously relied on invalid property names will now raise `ValueError` instead of failing later in the API call.

This is a **good breaking change** as it catches bugs earlier.

## Benefits

1. **Early Error Detection**: Validation errors caught immediately
2. **Better Error Messages**: Clear guidance on what went wrong
3. **Type Safety**: Type checking at Python level
4. **Better DX**: IDE autocomplete for valid properties
5. **Reduced API Calls**: No wasted calls with invalid data
6. **Documentation**: VALID_PROPERTIES serves as documentation

## Related Issues

- #050: Entity/Collection architecture consistency
- #055: Inconsistent property builder API

## Success Metrics

1. ✅ All entities have VALID_PROPERTIES defined
2. ✅ Property names validated in update() methods
3. ✅ Property values validated for type and format
4. ✅ Clear error messages for invalid inputs
5. ✅ Validation happens before API calls
6. ✅ Comprehensive test coverage for validation

## Priority

**🟠 High** - Developer experience issue:

1. **Poor DX**: Errors only discovered at runtime
2. **Wasteful**: Unnecessary API calls for invalid data
3. **Confusing**: No guidance on valid properties
4. **Type Safety**: Type hints suggest safety that doesn't exist
5. **Maintainability**: Hard to debug validation errors

This should be fixed to provide the professional development experience expected from a production-quality library.

## Timeline

- **Basic validation**: 1 day
- **Value validation**: 2 days
- **Testing**: 1 day
- **Documentation**: 0.5 day
- **Total**: 4-5 days (without schema-based validation)
- **With schema validation**: +2 days
