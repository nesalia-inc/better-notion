"""Filter translator for converting Python expressions to Notion API format."""

from __future__ import annotations

from datetime import datetime
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
            ValueError: If operator is not supported or property not found

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
    def _find_property_schema(prop_name: str, schema: dict) -> dict | None:
        """Find property schema by name (case-insensitive).

        Args:
            prop_name: Property name to find
            schema: Database properties schema

        Returns:
            Property schema dict or None
        """
        prop_name_lower = prop_name.lower()

        for name, prop_def in schema.items():
            if name.lower() == prop_name_lower:
                return prop_def

        return None

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
        elif operator == "in":
            # Notion doesn't support "in" for select, but we can use equals
            return {
                "property": prop_name,
                "select": {"equals": value}
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
        elif operator == "in":
            # For multi_select, "in" means "contains"
            return {
                "property": prop_name,
                "multi_select": {"contains": value}
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
    def _translate_date(prop_name: str, operator: str, value: Any) -> dict:
        """Translate date property filter."""
        # Convert datetime to ISO format string if needed
        if isinstance(value, datetime):
            value = value.isoformat()

        if operator == "eq":
            return {
                "property": prop_name,
                "date": {"equals": value}
            }
        elif operator == "ne":
            return {
                "property": prop_name,
                "date": {"does_not_equal": value}
            }
        elif operator == "before" or operator == "lt":
            return {
                "property": prop_name,
                "date": {"before": value}
            }
        elif operator == "after" or operator == "gt":
            return {
                "property": prop_name,
                "date": {"after": value}
            }
        elif operator == "on_or_before" or operator == "lte":
            return {
                "property": prop_name,
                "date": {"on_or_before": value}
            }
        elif operator == "on_or_after" or operator == "gte":
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
        elif operator == "ne":
            return {
                "property": prop_name,
                "checkbox": {"does_not_equal": value}
            }
        else:
            raise ValueError(f"Operator '{operator}' not supported for checkbox")

    @staticmethod
    def _translate_people(prop_name: str, operator: str, value: Any) -> dict:
        """Translate people property filter."""
        if operator == "contains":
            # value should be a user ID
            return {
                "property": prop_name,
                "people": {"contains": value}
            }
        elif operator == "is_null":
            return {
                "property": prop_name,
                "people": {"is_empty": True}
            }
        elif operator == "is_not_null":
            return {
                "property": prop_name,
                "people": {"is_not_empty": True}
            }
        else:
            raise ValueError(f"Operator '{operator}' not supported for people")

    @staticmethod
    def _translate_files(prop_name: str, operator: str, value: Any) -> dict:
        """Translate files property filter."""
        if operator == "is_null":
            return {
                "property": prop_name,
                "files": {"is_empty": True}
            }
        elif operator == "is_not_null":
            return {
                "property": prop_name,
                "files": {"is_not_empty": True}
            }
        else:
            raise ValueError(f"Operator '{operator}' not supported for files")
