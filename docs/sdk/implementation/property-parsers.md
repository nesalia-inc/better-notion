# Property Parsers

Utilities for extracting typed values from Notion API property structures.

## Overview

Notion API returns nested dictionaries for properties. For example, a title looks like:

```json
{
  "properties": {
    "Name": {
      "type": "title",
      "title": [
        {
          "type": "text",
          "text": {"content": "My Page Title"}
        }
      ]
    }
  }
}
```

**Problem**: Accessing this requires deep dictionary navigation:
```python
title = page["properties"]["Name"]["title"][0]["text"]["content"]
```

**Solution**: Property parsers provide simple, typed access:
```python
title = page.title  # → "My Page Title"
```

## Property Parser Architecture

### Base Property Parser

```python
from typing import Any

class PropertyParser:
    """Utility class for parsing Notion properties."""

    @staticmethod
    def get_title(properties: dict[str, Any]) -> str | None:
        """Extract title from properties.

        Args:
            properties: Properties dict from Notion API

        Returns:
            Title text or None if no title

        Note:
            Finds first property of type "title".
        """
        for prop_name, prop_data in properties.items():
            if prop_data.get("type") == "title":
                title_array = prop_data.get("title", [])
                if title_array and title_array[0].get("type") == "text":
                    return title_array[0]["text"]["content"]
        return None

    @staticmethod
    def get_select(properties: dict[str, Any], name: str) -> str | None:
        """Extract select property value.

        Args:
            properties: Properties dict
            name: Property name (case-insensitive)

        Returns:
            Select option name or None
        """
        prop = PropertyParser._find_property(properties, name)
        if prop and prop.get("type") == "select":
            select_data = prop.get("select")
            return select_data["name"] if select_data else None
        return None

    @staticmethod
    def get_multi_select(properties: dict[str, Any], name: str) -> list[str]:
        """Extract multi-select property values.

        Args:
            properties: Properties dict
            name: Property name (case-insensitive)

        Returns:
            List of select option names
        """
        prop = PropertyParser._find_property(properties, name)
        if prop and prop.get("type") == "multi_select":
            options = prop.get("multi_select", [])
            return [opt["name"] for opt in options]
        return []

    @staticmethod
    def get_checkbox(properties: dict[str, Any], name: str) -> bool:
        """Extract checkbox property value.

        Args:
            properties: Properties dict
            name: Property name (case-insensitive)

        Returns:
            Checkbox value (default False)
        """
        prop = PropertyParser._find_property(properties, name)
        if prop and prop.get("type") == "checkbox":
            return prop.get("checkbox", False)
        return False

    @staticmethod
    def get_number(properties: dict[str, Any], name: str) -> float | None:
        """Extract number property value.

        Args:
            properties: Properties dict
            name: Property name (case-insensitive)

        Returns:
            Number value or None
        """
        prop = PropertyParser._find_property(properties, name)
        if prop and prop.get("type") == "number":
            return prop.get("number")
        return None

    @staticmethod
    def get_date(properties: dict[str, Any], name: str) -> datetime | None:
        """Extract date property value.

        Args:
            properties: Properties dict
            name: Property name (case-insensitive)

        Returns:
            Datetime object or None
        """
        from datetime import datetime

        prop = PropertyParser._find_property(properties, name)
        if prop and prop.get("type") == "date":
            date_data = prop.get("date")
            if date_data and date_data.get("start"):
                # Parse ISO 8601 date
                # Simple version (use proper ISO parsing in production)
                return datetime.fromisoformat(date_data["start"].replace('Z', '+00:00'))
        return None

    @staticmethod
    def get_url(properties: dict[str, Any], name: str = "URL") -> str | None:
        """Extract URL property value.

        Args:
            properties: Properties dict
            name: Property name (case-insensitive, default "URL")

        Returns:
            URL string or None
        """
        prop = PropertyParser._find_property(properties, name)
        if prop and prop.get("type") == "url":
            return prop.get("url")
        return None

    @staticmethod
    def get_email(properties: dict[str, Any], name: str = "Email") -> str | None:
        """Extract email property value.

        Args:
            properties: Properties dict
            name: Property name (case-insensitive, default "Email")

        Returns:
            Email string or None
        """
        prop = PropertyParser._find_property(properties, name)
        if prop and prop.get("type") == "email":
            return prop.get("email")
        return None

    @staticmethod
    def get_phone(properties: dict[str, Any], name: str = "Phone") -> str | None:
        """Extract phone property value.

        Args:
            properties: Properties dict
            name: Property name (case-insensitive, default "Phone")

        Returns:
            Phone string or None
        """
        prop = PropertyParser._find_property(properties, name)
        if prop and prop.get("type") == "phone":
            return prop.get("phone")
        return None

    @staticmethod
    def get_people(properties: dict[str, Any], name: str) -> list[str]:
        """Extract people property user IDs.

        Args:
            properties: Properties dict
            name: Property name (case-insensitive)

        Returns:
            List of user IDs
        """
        prop = PropertyParser._find_property(properties, name)
        if prop and prop.get("type") == "people":
            people = prop.get("people", [])
            return [p["id"] for p in people]
        return []

    @staticmethod
    def _find_property(properties: dict[str, Any], name: str) -> dict[str, Any] | None:
        """Find property by name (case-insensitive).

        Args:
            properties: Properties dict
            name: Property name to find

        Returns:
            Property data or None
        """
        name_lower = name.lower()

        for prop_name, prop_data in properties.items():
            if prop_name.lower() == name_lower:
                return prop_data

        return None
```

## Integration with Models

### Page Model Example

```python
# better_notion/_sdk/models/page.py

from better_notion._sdk.models.base import BaseEntity
from better_notion._sdk.implementation.property_parsers import PropertyParser

class Page(BaseEntity):
    """SDK Page model with property shortcuts."""

    def __init__(self, client: NotionClient, data: dict[str, Any]) -> None:
        """Initialize page with client and API data.

        Args:
            client: NotionClient instance
            data: Raw API response data
        """
        super().__init__(client, data)

    # Property shortcuts
    @property
    def title(self) -> str | None:
        """Get page title from title property."""
        return PropertyParser.get_title(self._data["properties"])

    @property
    def url(self) -> str:
        """Get public Notion URL."""
        return f"https://notion.so/{self.id.replace('-', '')}"

    @property
    def icon(self) -> str | None:
        """Get page icon (emoji or URL)."""
        icon_data = self._data.get("icon")
        if not icon_data or icon_data.get("type") is None:
            return None

        if icon_data.get("type") == "emoji":
            return icon_data.get("emoji")
        elif icon_data.get("type") == "external":
            return icon_data.get("external", {}).get("url")
        elif icon_data.get("type") == "file":
            return icon_data.get("file", {}).get("url")

        return None

    @property
    def cover(self) -> str | None:
        """Get page cover image URL."""
        cover_data = self._data.get("cover")
        if not cover_data:
            return None

        if cover_data.get("type") == "external":
            return cover_data.get("external", {}).get("url")
        elif cover_data.get("type") == "file":
            return cover_data.get("file", {}).get("url")

        return None

    @property
    def archived(self) -> bool:
        """Check if page is archived."""
        return self._data.get("archived", False)

    # Smart property access
    def get_property(
        self,
        name: str,
        default: Any = None
    ) -> Any:
        """Get property value with type conversion.

        Args:
            name: Property name (case-insensitive)
            default: Default value if not found

        Returns:
            Typed property value or default
        """
        prop = PropertyParser._find_property(
            self._data["properties"],
            name
        )

        if not prop:
            return default

        prop_type = prop.get("type")

        if prop_type == "select":
            return PropertyParser.get_select(self._data["properties"], name)
        elif prop_type == "multi_select":
            return PropertyParser.get_multi_select(self._data["properties"], name)
        elif prop_type == "checkbox":
            return PropertyParser.get_checkbox(self._data["properties"], name)
        elif prop_type == "number":
            return PropertyParser.get_number(self._data["properties"], name)
        elif prop_type == "date":
            return PropertyParser.get_date(self._data["properties"], name)
        elif prop_type == "url":
            return PropertyParser.get_url(self._data["properties"], name)
        elif prop_type == "email":
            return PropertyParser.get_email(self._data["properties"], name)
        elif prop_type == "phone":
            return PropertyParser.get_phone(self._data["properties"], name)
        elif prop_type == "people":
            return PropertyParser.get_people(self._data["properties"], name)
        else:
            return default

    def find_property(
        self,
        name: str,
        fuzzy: bool = False
    ) -> dict[str, Any] | None:
        """Find property by name.

        Args:
            name: Property name
            fuzzy: Enable fuzzy matching

        Returns:
            Property dict or None
        """
        if not fuzzy:
            return PropertyParser._find_property(
                self._data["properties"],
                name
            )

        # Fuzzy matching (case-insensitive + substring)
        name_lower = name.lower()

        for prop_name, prop_data in self._data["properties"].items():
            if name_lower in prop_name.lower():
                return prop_data

        return None
```

## Usage Examples

### Direct Property Access

```python
page = await client.pages.get(page_id)

# Title shortcut
title = page.title  # → "My Page"

# Smart access with type conversion
status = page.get_property("Status")  # → "In Progress" (string)
priority = page.get_property("Priority")  # → 5 (int)
due_date = page.get_property("Due Date")  # → datetime(2025, 1, 15)
tags = page.get_property("Tags")  # → ["urgent", "backend"] (list[str])

# Safe defaults
status = page.get_property("Status", default="Unknown")
```

### Property Discovery

```python
# Find property by exact name (case-insensitive)
prop = page.find_property("status")

# Fuzzy matching
prop = page.find_property("stat", fuzzy=True)  # Finds "Status"

# Check property existence
has_status = "Status" in page.properties
has_due_date = page.has_property("Due Date")
```

## Testing Property Parsers

### Unit Test Example

```python
import pytest
from better_notion._sdk.implementation.property_parsers import PropertyParser

def test_get_title():
    properties = {
        "Name": {
            "type": "title",
            "title": [
                {
                    "type": "text",
                    "text": {"content": "Test Page"}
                }
            ]
        }
    }

    assert PropertyParser.get_title(properties) == "Test Page"

def test_get_empty_title():
    properties = {
        "Name": {
            "type": "title",
            "title": []
        }
    }

    assert PropertyParser.get_title(properties) is None

def test_case_insensitive_lookup():
    properties = {
        "Status": {
            "type": "select",
            "select": {"name": "Done"}
        }
    }

    # All these should work
    assert PropertyParser.get_select(properties, "Status") == "Done"
    assert PropertyParser.get_select(properties, "status") == "Done"
    assert PropertyParser.get_select(properties, "STATUS") == "Done"
```

## Performance Considerations

### Property Name Caching

Finding properties requires iterating through all properties:

```python
# Without cache - O(n) each time
title = page.title  # Iterates all props
status = page.get_property("Status")  # Iterates all props again
```

**Optimization**: Cache property name → type mapping:

```python
class Page(BaseEntity):
    def __init__(self, client: NotionClient, data: dict[str, Any]) -> None:
        super().__init__(client, data)
        # Build property name cache
        self._property_cache = {
            name.lower(): prop_data["type"]
            for name, prop_data in data["properties"].items()
        }
```

Now lookups are O(1).

## Error Handling

### Missing Properties

```python
# Returns None (not exception)
title = page.title  # None if no title property

# Returns default
status = page.get_property("NonExistent", default="Unknown")
```

### Type Mismatches

```python
# If property is number but you call get_date()
date = page.get_property("Count")  # → None (wrong type)

# Explicit type checking
prop = page.find_property("DueDate")
if prop and prop["type"] == "date":
    date = PropertyParser.get_date(page.properties, "DueDate")
```

## Next Steps

1. Implement base `PropertyParser` class
2. Add parser methods for all property types
3. Integrate into `Page` model
4. Add unit tests for each parser
5. Benchmark and optimize property lookups

## Related Documentation

- [BaseEntity](./base-entity.md) - Foundation class
- [Page Model](../models/page-model.md) - Page-specific usage
- [Property Builders](../../_api/properties/README.md) - Creating properties (different from parsing)
