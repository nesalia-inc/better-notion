# Inconsistent Property Builder API

## Summary

Property builders have inconsistent constructor signatures. The `Relation` property builder hardcodes its name and doesn't accept a `name` parameter like other property builders, creating API inconsistency and preventing multiple relations on the same entity.

## Problem Statement

### Current State

**Most Property Builders Follow This Pattern:**

```python
# number.py
class Number(Property):
    def __init__(self, name: str, value: int | float | None = None):
        super().__init__(name)  # ✅ Name parameter
        self._value = value

# date.py
class Date(Property):
    def __init__(self, name: str, value: datetime | str | None = None, end: datetime | str | None = None):
        super().__init__(name)  # ✅ Name parameter
        self._value = value
        self._end = end

# title.py
class Title(Property):
    def __init__(self, content: str):
        super().__init__("Title")  # ⚠️ Fixed name
```

**But Relation is Different:**

```python
# relation.py
class Relation(Property):
    def __init__(self, page_ids: list[str]):  # ❌ No name parameter
        super().__init__("Relation")  # ❌ Name hardcoded
        self._page_ids = page_ids
```

### Issues

**1. Name Hardcoded**

```python
# Relation always has name "Relation"
relation = Relation(page_ids=["page_123", "page_456"])
# to_dict() returns {"Relation": {...}}  # ❌ Always "Relation"

# Cannot create a relation with a custom name
# This breaks if a database has multiple relation properties
```

**2. Inconsistent Constructor Signature**

```python
# Most properties
Number(name="Price", value=100)
Date(name="Start Date", value="2025-02-10")
Select(name="Status", value="In Progress")

# Relation (different!)
Relation(page_ids=["page_123"])  # ❌ No name parameter
```

**3. Breaking the Pattern**

```python
# Base Property class expects a name
class Property(ABC):
    def __init__(self, name: str):  # Takes name parameter
        self._name = name
```

All subclasses except `Relation` follow this pattern, but `Relation` hardcodes `"Relation"`.

**4. Real-World Limitation**

```python
# Database schema with TWO relation properties:
# - "Assigned To" → relation to Users
# - "Depends On" → relation to Tasks

# Cannot create both properties with current API
assigned_to = Relation(page_ids=["user_123"])  # Creates "Relation" property
depends_on = Relation(page_ids=["task_456"])   # Also creates "Relation" property
# ❌ Both have the same name! Second one overwrites first!
```

### Impact

1. **API Inconsistency**: Relation doesn't match other properties
2. **Limited Functionality**: Cannot have multiple relation properties
3. **Confusion**: Different constructor signatures for similar classes
4. **Breaking Use Cases**: Cannot work with databases that have multiple relations
5. **Poor Design**: Violates the established pattern

## Root Cause Analysis

### Why Was This Done?

Looking at the code, `Relation` was designed to be used **inside entity property dictionaries**, where the property name is the dictionary key:

```python
properties = {
    "Assigned To": Relation(page_ids=["user_123"]),  # Name is dict key
    "Depends On": Relation(page_ids=["task_456"]),   # Name is dict key
}
```

But this breaks the pattern because:
1. Other property builders also go into dicts but still take a `name` parameter
2. The `name` parameter is ignored in `to_dict()` output
3. It's inconsistent with the base class design

### The Pattern

```python
# Base Property
class Property(ABC):
    def __init__(self, name: str):
        self._name = name

    def build(self) -> dict[str, Any]:
        """Build the complete property for Notion API."""
        return {self._name: self.to_dict()}

# Most properties follow this
Number(name="Price", value=100)
# .build() returns {"Price": {"type": "number", "number": 100}}

# Relation breaks this
Relation(page_ids=["page_123"])
# .build() returns {"Relation": {"type": "relation", ...}}
# The name is ALWAYS "Relation", not customizable
```

## Proposed Solution

### Option A: Make Relation Consistent (Recommended)

```python
class Relation(Property):
    """Builder for relation properties."""

    def __init__(self, name: str, page_ids: list[str]):  # ✅ Add name parameter
        """Initialize a relation property.

        Args:
            name: The property name (e.g., "Assigned To", "Depends On")
            page_ids: List of related page IDs
        """
        super().__init__(name)  # ✅ Use name parameter
        self._page_ids = page_ids

    def to_dict(self) -> dict[str, Any]:
        """Convert to Notion API format."""
        return {
            "type": "relation",
            "relation": [{"id": page_id} for page_id in self._page_ids]
        }
```

**Usage:**

```python
# Now consistent with other properties
assigned_to = Relation(name="Assigned To", page_ids=["user_123"])
depends_on = Relation(name="Depends On", page_ids=["task_456"])

# Works in property dictionaries
properties = {
    "Assigned To": assigned_to,
    "Depends On": depends_on,
}
```

**Benefits:**
- Consistent API with other property builders
- Can create multiple relation properties
- Follows the established pattern
- More intuitive

**Migration:**
```python
# Old way (breaks with multiple relations)
Relation(page_ids=["page_123"])

# New way (consistent with other properties)
Relation(name="Related Task", page_ids=["page_123"])
```

### Option B: Add Separate RelationProperty Class

Keep `Relation` as-is for backwards compatibility, add a new `RelationProperty`:

```python
class Relation(Property):
    """Deprecated: Use RelationProperty instead."""

    def __init__(self, page_ids: list[str]):
        super().__init__("Relation")
        self._page_ids = page_ids
        import warnings
        warnings.warn(
            "Relation() is deprecated, use RelationProperty(name, page_ids) instead",
            DeprecationWarning,
            stacklevel=2
        )

class RelationProperty(Property):
    """Builder for relation properties."""

    def __init__(self, name: str, page_ids: list[str]):
        super().__init__(name)
        self._page_ids = page_ids

    def to_dict(self) -> dict[str, Any]:
        return {
            "type": "relation",
            "relation": [{"id": page_id} for page_id in self._page_ids]
        }
```

**Benefits:**
- Backward compatible
- Clear migration path

**Drawbacks:**
- Two classes doing the same thing
- Confusing to have both

### Option C: Factory Method on Base Property

```python
class Property(ABC):
    @classmethod
    def relation(cls, name: str, page_ids: list[str]) -> "Relation":
        """Create a Relation property."""
        return Relation(name, page_ids)

# Usage
rel = Property.relation("Assigned To", ["user_123"])
```

**Drawbacks:**
- Still inconsistent - other properties have direct constructors
- More verbose

## Recommendation

**Implement Option A** - Make `Relation` consistent with other property builders.

This is a breaking change but fixes a fundamental design inconsistency. The current design prevents valid use cases (multiple relations) and breaks the established pattern.

### Breaking Change Strategy

Since this changes the constructor signature, it requires a major version bump (3.0.0):

```python
# 2.x (current)
Relation(page_ids=["page_123"])

# 3.x (proposed)
Relation(name="Related Task", page_ids=["page_123"])
```

### Migration Path

1. Keep the old behavior in 2.x as deprecated
2. In 3.0, change the signature
3. Provide migration script/guide
4. Document the breaking change clearly

## Implementation Plan

### Phase 1: Add Deprecation Warning (2.x)

```python
# relation.py
class Relation(Property):
    def __init__(self, name_or_ids: str | list[str], page_ids: list[str] | None = None):
        # Support both old and new API during deprecation
        if isinstance(name_or_ids, list) and page_ids is None:
            # Old API: Relation(page_ids=[...])
            import warnings
            warnings.warn(
                "Relation(page_ids=[...]) is deprecated, "
                "use Relation(name='...', page_ids=[...]) instead",
                DeprecationWarning,
                stacklevel=2
            )
            self._name = "Relation"
            self._page_ids = name_or_ids
        else:
            # New API: Relation(name="...", page_ids=[...])
            self._name = name_or_ids
            self._page_ids = page_ids or []
```

### Phase 2: Change Signature (3.0.0)

```python
# relation.py
class Relation(Property):
    def __init__(self, name: str, page_ids: list[str]):
        super().__init__(name)
        self._page_ids = page_ids
```

### Phase 3: Update All Usage

```python
# Find all Relation() usage and update
# Old:
Relation(page_ids=["page_123"])

# New:
Relation(name="Related Task", page_ids=["page_123"])
```

### Phase 4: Update Documentation

1. Update examples in README
2. Update docstrings
3. Add migration guide
4. Update type hints

## Code Examples

### Before (Current - Inconsistent)

```python
# Most properties - take name parameter
number = Number(name="Price", value=100)
date = Date(name="Due Date", value="2025-02-10")
select = Select(name="Status", value="In Progress")

# Relation - different!
relation = Relation(page_ids=["page_123"])  # ❌ No name parameter

# Problem: Can't create two relations
properties = {
    "Assigned To": Relation(page_ids=["user_123"]),
    "Depends On": Relation(page_ids=["task_456"]),  # ❌ Both named "Relation"!
}
```

### After (Consistent)

```python
# All properties follow the same pattern
number = Number(name="Price", value=100)
date = Date(name="Due Date", value="2025-02-10")
select = Select(name="Status", value="In Progress")
relation = Relation(name="Related Task", page_ids=["page_123"])  # ✅ Consistent!

# Now can create multiple relations
properties = {
    "Assigned To": Relation(name="Assigned To", page_ids=["user_123"]),
    "Depends On": Relation(name="Depends On", page_ids=["task_456"]),  # ✅ Works!
}
```

## Benefits

1. **Consistency**: All properties follow the same pattern
2. **Functionality**: Can create multiple relation properties
3. **Clarity**: API is more intuitive
4. **Type Safety**: Consistent constructor signatures
5. **Maintainability**: Easier to understand and extend

## Related Issues

- #050: Entity/Collection architecture consistency
- #054: Missing property validation in entities

## Success Metrics

1. ✅ Relation takes `name` parameter like other properties
2. ✅ Can create multiple relation properties on same entity
3. ✅ All property builders have consistent signatures
4. ✅ No hardcoded property names in constructors
5. ✅ Documentation updated with examples
6. ✅ Migration guide provided

## Priority

**🟡 Medium** - API inconsistency issue:

1. **Breaking Use Case**: Cannot have multiple relations
2. **Inconsistent API**: Doesn't match other property builders
3. **Confusing**: Different constructor signatures
4. **Design Violation**: Breaks established pattern

This is not blocking (the current code works for single relations), but it's a design flaw that should be fixed for API consistency and to enable valid use cases.

## Timeline

- **Deprecation warning (2.x)**: 0.5 day
- **Change signature (3.0.0)**: 0.5 day
- **Update all usage**: 1 day
- **Testing**: 1 day
- **Documentation**: 0.5 day
- **Total**: 3-4 days (can be done with other breaking changes for 3.0.0)
