# Query Builder

Transform Pythonic filter expressions into Notion API queries.

## Overview

The Notion API uses verbose, nested JSON for database queries. The Query Builder transforms simple Python expressions into complex Notion API filters.

### The Problem

Notion API requires complex filter structures:

```python
# Notion API - verbose and error-prone
filter_body = {
    "filter": {
        "and": [
            {
                "property": "Status",
                "select": {"equals": "In Progress"}
            },
            {
                "property": "Priority",
                "number": {"greater_than_or_equal_to": 5}
            }
        ]
    }
}
```

**Issues**:
- Verbose syntax
- Easy to make mistakes
- Hard to read
- Not "Pythonic"

### The Solution

Simple, readable queries:

```python
# Simple equality
pages = await database.query(status="Done")

# Multiple conditions
pages = await database.query(
    status="In Progress",
    priority__gte=5
)

# Builder pattern
pages = await (database.query()
    .filter(status="In Progress")
    .sort("due_date")
    .limit(10)
).collect()
```

## Architecture

```
User Interface (Database.query())
    ↓
QueryBuilder (builds query)
    ↓
FilterTranslator (translates to Notion format)
    ↓
API Execution (NotionAPI._request())
```

## Component 1: Database.query() Interface

### User-Facing API

```python
# better_notion/_sdk/models/database.py

class Database(BaseEntity):

    def query(self, **filters) -> DatabaseQuery:
        """Query database with Pythonic filters.

        Simple filtering:
            >>> pages = await database.query(client=client, status="Done")

        Multiple filters:
            >>> pages = await database.query(
            ...     client=client,
            ...     status="In Progress",
            ...     priority__gte=5
            ... )

        With operators:
            >>> pages = await database.query(
            ...     client=client,
            ...     due_date__before="2025-01-31",
            ...     title__contains="Q1"
            ... )

        Args:
            client: NotionClient instance
            **filters: Filter conditions
                - property_name: value (equality)
                - property_name__op: value (comparison)

        Returns:
            DatabaseQuery object (async iterable)

        Supported operators:
            __eq, __ne: equals, not equals
            __gt, __gte, __lt, __lte: comparisons
            __contains: contains (text, multi_select)
            __starts_with, __ends_with: text matching
            __is_null, __is_not_null: null checks
            __before, __after: date comparisons
            __in: in list (select)

        Example:
            >>> # Iterate
            >>> async for page in database.query(client=client, status="Done"):
            ...     print(page.title)
            >>>
            >>> # Collect all
            >>> pages = await database.query(client=client, status="Done").collect()
        """
        return DatabaseQuery(
            client=client,
            database_id=self.id,
            schema=self._data["properties"],
            filters=filters
        )
```

### Usage Examples

```python
# Simple equality
pages = await database.query(status="Done")

# Comparison operators
pages = await database.query(priority__gte=5)

# Date comparisons
pages = await database.query(due_date__before="2025-01-31")

# Text search
pages = await database.query(title__contains("Project"))

# Null checks
pages = await database.query(assignee__is_null=True)

# Multiple conditions (implicit AND)
pages = await database.query(
    status="In Progress",
    priority__gte=5,
    assignee__is_null=False
)
```

## Component 2: QueryBuilder Class

### QueryBuilder Implementation

```python
# better_notion/_sdk/implementation/query_builder.py

from typing import Any, AsyncIterator, TYPE_CHECKING
from dataclasses import dataclass, field

if TYPE_CHECKING:
    from better_notion._api import NotionAPI
    from better_notion._sdk.models.page import Page

@dataclass
class SortConfig:
    """Sort configuration."""
    property: str
    direction: str = "ascending"  # or "descending"


class DatabaseQuery:
    """Build and execute Notion database queries.

    Provides fluent interface for building complex queries:
        >>> query = database.query(client=client, status="Done")
        >>> query = query.sort("due_date").limit(10)
        >>> pages = await query.collect()
    """

    def __init__(
        self,
        client: NotionClient,
        database_id: str,
        schema: dict,
        filters: dict
    ) -> None:
        """Initialize query builder.

        Args:
            client: NotionClient instance
            database_id: Database to query
            schema: Database property schema (for type inference)
            filters: Initial filters from kwargs
        """
        self._client = client
        self._database_id = database_id
        self._schema = schema
        self._filters: list[dict] = []
        self._sorts: list[SortConfig] = []
        self._limit: int | None = None

        # Process initial filters
        for key, value in filters.items():
            self._add_filter(key, value)

    def _add_filter(self, key: str, value: Any) -> None:
        """Add filter from key-value pair.

        Parses operator from key (e.g., "priority__gte")
        and translates to Notion filter format.

        Args:
            key: Property name with optional operator suffix
            value: Filter value
        """
        # Parse key and operator
        if "__" in key:
            prop_name, operator = key.rsplit("__", 1)
        else:
            prop_name, operator = key, "eq"

        # Translate to Notion filter
        filter_dict = FilterTranslator.translate(
            prop_name=prop_name,
            operator=operator,
            value=value,
            schema=self._schema
        )

        self._filters.append(filter_dict)

    def filter(
        self,
        **kwargs: Any
    ) -> "DatabaseQuery":
        """Add filter conditions.

        Args:
            **kwargs: Filter conditions

        Returns:
            self (for chaining)

        Example:
            >>> query.filter(status="Done")
            >>> query.filter(priority__gte=5)
        """
        for key, value in kwargs.items():
            self._add_filter(key, value)
        return self

    def sort(
        self,
        property: str,
        direction: str = "ascending"
    ) -> "DatabaseQuery":
        """Add sort order.

        Args:
            property: Property name to sort by
            direction: "ascending" or "descending"

        Returns:
            self (for chaining)

        Example:
            >>> query.sort("due_date", "ascending")
            >>> query.sort("priority", "descending")

        Raises:
            ValueError: If direction is not "ascending" or "descending"
        """
        if direction not in ("ascending", "descending"):
            raise ValueError(
                f"Direction must be 'ascending' or 'descending', got '{direction}'"
            )

        self._sorts.append(SortConfig(property, direction))
        return self

    def limit(self, n: int) -> "DatabaseQuery":
        """Limit results to n items.

        Args:
            n: Maximum number of results

        Returns:
            self (for chaining)

        Note:
            This is client-side limit (fetches all then truncates)
            For large datasets, break iteration early instead

        Example:
            >>> async for page in query.limit(10):
            ...     process(page)
        """
        if n <= 0:
            raise ValueError(f"Limit must be positive, got {n}")

        self._limit = n
        return self

    def execute(self) -> AsyncIterator[Page]:
        """Execute query and return async iterator.

        Yields:
            Page objects matching query

        Note:
            Handles pagination automatically
        """
        # Build request body
        body = {}

        # Add filters (combine with AND if multiple)
        if self._filters:
            if len(self._filters) == 1:
                body["filter"] = self._filters[0]
            else:
                body["filter"] = {"and": self._filters}

        # Add sorts
        if self._sorts:
            body["sorts"] = [
                {
                    "property": s.property,
                    "direction": s.direction
                }
                for s in self._sorts
            ]

        # Execute query with pagination
        async def fetch_fn(cursor: str | None) -> dict:
            body_copy = body.copy()
            if cursor:
                body_copy["start_cursor"] = cursor
            return await self._client.api._request(
                "POST",
                f"/databases/{self._database_id}/query",
                json=body_copy
            )

        from better_notion._api.utils import AsyncPaginatedIterator
        from better_notion._sdk.models.page import Page

        iterator = AsyncPaginatedIterator(fetch_fn)

        # Apply limit if set
        count = 0
        async for page_data in iterator:
            if self._limit and count >= self._limit:
                break

            yield Page.from_data(self._client, page_data)
            count += 1

    # ===== ASYNC ITERATOR =====

    def __aiter__(self) -> AsyncIterator[Page]:
        """Make DatabaseQuery async iterable.

        Example:
            >>> async for page in database.query():
            ...     print(page.title)
        """
        return self.execute()

    # ===== CONVENIENCE METHODS =====

    async def collect(self) -> list[Page]:
        """Collect all results into list.

        Returns:
            List of Page objects

        Warning:
            For large result sets, this consumes significant memory

        Example:
            >>> pages = await database.query(status="Done").collect()
            >>> print(f"Found {len(pages)} pages")
        """
        pages = []
        async for page in self:
            pages.append(page)
        return pages

    async def first(self) -> Page | None:
        """Get first result only.

        Returns:
            First matching Page or None if no results

        Example:
            >>> page = await database.query(status="Done").first()
            >>> if page:
            ...     print(page.title)
        """
        async for page in self:
            return page
        return None

    async def count(self) -> int:
        """Count matching pages.

        Returns:
            Number of matching pages

        Example:
            >>> count = await database.query(status="Done").count()
            >>> print(f"Found {count} done tasks")
        """
        count = 0
        async for _ in self:
            count += 1
        return count

    async def exists(self) -> bool:
        """Check if any pages match query.

        Returns:
            True if at least one result exists

        Example:
            >>> if await database.query(status="Done").exists():
            ...     print("There are done tasks")
        """
        return await self.first() is not None
```

## Component 3: Filter Translator

### FilterTranslator Implementation

```python
# better_notion/_sdk/implementation/filter_translator.py

from typing import Any

class FilterTranslator:
    """Translate Python filter expressions to Notion API format.

    Examples:
        >>> # Python: status="Done"
        >>> # Notion: {"property": "Status", "select": {"equals": "Done"}}
        >>>
        >>> # Python: priority__gte=5
        >>> # Notion: {"property": "Priority", "number": {"greater_than_or_equal_to": 5}}

    Note:
        Uses database schema to infer property types for correct formatting
    """

    @staticmethod
    def translate(
        prop_name: str,
        operator: str,
        value: Any,
        schema: dict
    ) -> dict[str, Any]:
        """Translate filter to Notion format.

        Args:
            prop_name: Property name
            operator: Comparison operator
            value: Filter value
            schema: Database properties schema

        Returns:
            Notion filter dict

        Raises:
            ValueError: If operator is not supported
            PropertyNotFound: If property doesn't exist in schema

        Example:
            >>> filter = FilterTranslator.translate(
            ...     "Status", "eq", "Done", schema
            ... )
            >>> print(filter)
            {'property': 'Status', 'select': {'equals': 'Done'}}
        """
        # Find property in schema (case-insensitive)
        prop_def = FilterTranslator._find_property_schema(prop_name, schema)

        if not prop_def:
            raise ValueError(f"Property not found: {prop_name}")

        prop_type = prop_def["type"]

        # Build filter based on property type
        if prop_type == "select":
            return FilterTranslator._translate_select(prop_name, operator, value)

        elif prop_type == "multi_select":
            return FilterTranslator._translate_multi_select(prop_name, operator, value)

        elif prop_type == "number":
            return FilterTranslator._translate_number(prop_name, operator, value)

        elif prop_type == "checkbox":
            return FilterTranslator._translate_checkbox(prop_name, operator, value)

        elif prop_type == "date":
            return FilterTranslator._translate_date(prop_name, operator, value)

        elif prop_type in ["title", "rich_text", "text", "url", "email", "phone"]:
            return FilterTranslator._translate_text(prop_name, operator, value)

        elif prop_type == "people":
            return FilterTranslator._translate_people(prop_name, operator, value)

        elif prop_type == "files":
            return FilterTranslator._translate_files(prop_name, operator, value)

        else:
            raise ValueError(f"Unsupported property type: {prop_type}")

    @staticmethod
    def _translate_select(prop_name: str, operator: str, value: str) -> dict:
        """Translate select property filter."""
        if operator == "eq":
            return {
                "property": prop_name,
                "select": {"equals": value}
            }
        elif operator == "ne":
            return {
                "property": prop_name,
                "select": {"does_not_equal": value}
            }
        elif operator == "is_null":
            return {
                "property": prop_name,
                "select": {"is_empty": True}
            }
        elif operator == "is_not_null":
            return {
                "property": prop_name,
                "select": {"is_not_empty": True}
            }
        else:
            raise ValueError(f"Operator '{operator}' not supported for select")

    @staticmethod
    def _translate_multi_select(prop_name: str, operator: str, value: Any) -> dict:
        """Translate multi-select property filter."""
        if operator == "contains":
            return {
                "property": prop_name,
                "multi_select": {"contains": value}
            }
        elif operator == "is_null":
            return {
                "property": prop_name,
                "multi_select": {"is_empty": True}
            }
        elif operator == "is_not_null":
            return {
                "property": prop_name,
                "multi_select": {"is_not_empty": True}
            }
        else:
            raise ValueError(f"Operator '{operator}' not supported for multi_select")

    @staticmethod
    def _translate_number(prop_name: str, operator: str, value: int | float) -> dict:
        """Translate number property filter."""
        op_map = {
            "eq": "equals",
            "ne": "does_not_equal",
            "gt": "greater_than",
            "gte": "greater_than_or_equal_to",
            "lt": "less_than",
            "lte": "less_than_or_equal_to"
        }

        if operator not in op_map:
            raise ValueError(f"Operator '{operator}' not supported for number")

        return {
            "property": prop_name,
            "number": {op_map[operator]: value}
        }

    @staticmethod
    def _translate_date(prop_name: str, operator: str, value: str) -> dict:
        """Translate date property filter."""
        if operator == "eq" or operator == "before":
            return {
                "property": prop_name,
                "date": {"on_or_before": value}
            }
        elif operator == "after":
            return {
                "property": prop_name,
                "date": {"on_or_after": value}
            }
        elif operator == "is_null":
            return {
                "property": prop_name,
                "date": {"is_empty": True}
            }
        elif operator == "is_not_null":
            return {
                "property": prop_name,
                "date": {"is_not_empty": True}
            }
        else:
            raise ValueError(f"Operator '{operator}' not supported for date")

    @staticmethod
    def _translate_text(prop_name: str, operator: str, value: str) -> dict:
        """Translate text property filter."""
        if operator == "eq":
            return {
                "property": prop_name,
                "rich_text": {"equals": value}
            }
        elif operator == "ne":
            return {
                "property": prop_name,
                "rich_text": {"does_not_equal": value}
            }
        elif operator == "contains":
            return {
                "property": prop_name,
                "rich_text": {"contains": value}
            }
        elif operator == "starts_with":
            return {
                "property": prop_name,
                "rich_text": {"starts_with": value}
            }
        elif operator == "ends_with":
            return {
                "property": prop_name,
                "rich_text": {"ends_with": value}
            }
        elif operator == "is_null":
            return {
                "property": prop_name,
                "rich_text": {"is_empty": True}
            }
        elif operator == "is_not_null":
            return {
                "property": prop_name,
                "rich_text": {"is_not_empty": True}
            }
        else:
            raise ValueError(f"Operator '{operator}' not supported for text")

    @staticmethod
    def _translate_checkbox(prop_name: str, operator: str, value: bool) -> dict:
        """Translate checkbox property filter."""
        if operator == "eq":
            return {
                "property": prop_name,
                "checkbox": {"equals": value}
            }
        else:
            raise ValueError(f"Operator '{operator}' not supported for checkbox")

    @staticmethod
    def _translate_people(prop_name: str, operator: str, value: Any) -> dict:
        """Translate people property filter."""
        if operator == "contains":
            # value can be user ID or User object
            user_id = value if isinstance(value, str) else value.id
            return {
                "property": prop_name,
                "people": {"contains": user_id}
            }
        elif operator == "is_null":
            return {
                "property": prop_name,
                "people": {"is_empty": True}
            }
        else:
            raise ValueError(f"Operator '{operator}' not supported for people")

    @staticmethod
    def _find_property_schema(
        name: str,
        schema: dict
    ) -> dict | None:
        """Find property definition in schema (case-insensitive).

        Args:
            name: Property name to find
            schema: Database properties schema

        Returns:
            Property definition dict or None if not found
        """
        name_lower = name.lower()

        for prop_name, prop_def in schema.items():
            if prop_name.lower() == name_lower:
                return prop_def

        return None
```

## Supported Operators

### Comparison Operators

| Operator | Types | Description |
|----------|-------|-------------|
| `__eq` (or no suffix) | All | Equality (default) |
| `__ne` | All | Not equals |
| `__gt` | Number | Greater than |
| `__gte` | Number | Greater than or equal |
| `__lt` | Number | Less than |
| `__lte` | Number | Less than or equal |

### Text Operators

| Operator | Types | Description |
|----------|-------|-------------|
| `__contains` | Text, Multi-select | Contains value |
| `__starts_with` | Text | Starts with value |
| `__ends_with` | Text | Ends with value |

### Date Operators

| Operator | Types | Description |
|----------|-------|-------------|
| `__before` | Date | On or before date |
| `__after` | Date | On or after date |

### Null Operators

| Operator | Types | Description |
|----------|-------|-------------|
| `__is_null` | All | Is empty/null |
| `__is_not_null` | All | Is not empty/null |

## Usage Examples

### Example 1: Simple Query

```python
# Python
database = await client.databases.get(db_id)
pages = await database.query(status="Done")

# What it generates (Notion API)
{
  "filter": {
    "property": "Status",
    "select": {"equals": "Done"}
  }
}
```

### Example 2: Multiple Filters

```python
# Python
pages = await database.query(
    status="In Progress",
    priority__gte=5
)

# Notion API
{
  "filter": {
    "and": [
      {
        "property": "Status",
        "select": {"equals": "In Progress"}
      },
      {
        "property": "Priority",
        "number": {"greater_than_or_equal_to": 5}
      }
    ]
  }
}
```

### Example 3: Builder Pattern

```python
# Python - Fluent interface
query = (database.query()
    .filter(status="In Progress")
    .sort("priority", "descending")
    .limit(10))

pages = await query.collect()

# Notion API
{
  "filter": {
    "property": "Status",
    "select": {"equals": "In Progress"}
  },
  "sorts": [
    {"property": "Priority", "direction": "descending"}
  ]
}
```

### Example 4: Date Filtering

```python
# Python
from datetime import datetime, timedelta

week_ago = (datetime.now() - timedelta(days=7)).isoformat()
pages = await database.query(created_date__after=week_ago)

# Notion API
{
  "filter": {
    "property": "Created Date",
    "date": {"on_or_after": "2025-01-17"}
  }
}
```

### Example 5: Text Search

```python
# Python
pages = await database.query(title__contains("Q1"))

# Notion API
{
  "filter": {
    "property": "Name",
    "rich_text": {"contains": "Q1"}
  }
}
```

### Example 6: Null Checks

```python
# Python - Find unassigned tasks
pages = await database.query(assignee__is_null=True)

# Notion API
{
  "filter": {
    "property": "Assignee",
    "people": {"is_empty": True}
  }
}
```

## Performance Considerations

### Query Execution

**Streaming (efficient)**:
```python
# ✅ GOOD: Process one at a time
async for page in database.query(status="Done"):
    process(page)  # Low memory usage
```

**Collection (memory intensive)**:
```python
# ⚠️ WARNING: Loads all into memory
pages = await database.query(status="Done").collect()
for page in pages:
    process(page)  # High memory for large results
```

### Limit vs Iteration

**Using limit()**:
```python
# Fetches ALL then truncates
pages = await database.query().limit(10).collect()
# Still makes multiple API calls if > 10 pages exist
```

**Breaking iteration early**:
```python
# Only fetches what you need
count = 0
async for page in database.query():
    process(page)
    count += 1
    if count >= 10:
        break  # No more API calls
```

## Design Decisions

### Q1: Implicit AND vs Explicit

**Decision**: Implicit AND (multiple kwargs = AND)

```python
# Implicit AND (our choice)
pages = await database.query(
    status="Done",
    priority__gte=5
)

# Explicit AND (alternative)
pages = await database.query().and_(
    status="Done",
    priority__gte=5
)
```

**Rationale**: More Pythonic, simpler for common cases

### Q2: Operator Suffix Syntax

**Decision**: Django-style `__` suffix

```python
# Our choice (Django-style)
priority__gte=5
title__contains="Project"

# Alternative (function-based)
query.filter(gte("priority", 5))
query.filter(contains("title", "Project"))
```

**Rationale**: Familiar to Django users, compact, IDE-friendly

### Q3: Schema Inference

**Decision**: Use database schema to infer types

```python
# Read schema to determine property type
prop_def = schema["Priority"]  # {"type": "number"}
prop_type = prop_def["type"]

# Build appropriate filter
if prop_type == "number":
    return {"number": {"greater_than_or_equal_to": value}}
```

**Rationale**: Correct filter formatting, validation support

## Error Handling

### Property Not Found

```python
try:
    pages = await database.query(nonexistent="value")
except ValueError as e:
    print(f"Error: {e}")
    # "Property not found: nonexistent"
```

### Invalid Operator

```python
try:
    pages = await database.query(status__invalid_op="value")
except ValueError as e:
    print(f"Error: {e}")
    # "Operator 'invalid_op' not supported for select"
```

### Type Mismatch

```python
# If value doesn't match property type
try:
    pages = await database.query(priority="not_a_number")
except ValueError as e:
    print(f"Error: {e}")
    # "Invalid value for number property"
```

## Best Practices

### DO ✅

```python
# Use meaningful filters
pages = await database.query(status="Done")

# Combine filters efficiently
pages = await database.query(
    status="In Progress",
    priority__gte=5,
    assignee__is_null=False
)

# Stream for large results
async for page in database.query():
    process(page)

# Use limit sparingly
pages = await database.query().limit(10).collect()
```

### DON'T ❌

```python
# Don't query without filters (might be huge)
pages = await database.query().collect()

# Don't use limit() to avoid fetching (still fetches all)
# Use iteration break instead
count = 0
async for page in database.query():
    if count >= 10:
        break

# Don't forget: operators are property-type specific
# This fails: status__gte=5  (select doesn't support gte)
```

## Next Steps

After implementing query builder:

1. ✅ Implement DatabaseQuery class
2. ✅ Implement FilterTranslator
3. ✅ Add operator translations for all types
4. ✅ Add comprehensive error handling
5. ⏭️ Add unit tests for each operator
6. ⏭️ Add integration tests with real Notion API

## Related Documentation

- [Database Model](../models/database-model.md) - Database query interface
- [Property Parsers](./property-parsers.md) - Property value extraction
- [Cache Strategy](./cache-strategy.md) - Caching query results
