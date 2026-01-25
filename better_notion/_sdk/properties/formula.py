"""Formula property parser for Notion formula properties."""

from __future__ import annotations

from datetime import datetime
from typing import Any


class FormulaParser:
    """Parse Notion formula properties.

    Formula properties can return different types:
    - string: Text result
    - number: Numeric result
    - boolean: Boolean result
    - date: Date result
    - empty: No result

    Example:
        >>> value = FormulaParser.parse(formula_data)
        >>> print(value)  # Parsed value based on result type
    """

    @staticmethod
    def parse(data: dict[str, Any]) -> Any:
        """Parse formula property value.

        Args:
            data: Raw formula property data from Notion API

        Returns:
            Parsed value (str, int, float, bool, datetime, or None)

        Raises:
            ValueError: If formula type is unsupported

        Example:
            >>> formula = {
            ...     \"type\": \"formula\",
            ...     \"formula\": {
            ...         \"type\": \"string\",
            ...         \"string\": \"Hello\"
            ...     }
            ... }
            >>> value = FormulaParser.parse(formula)
            >>> assert value == \"Hello\"
        """
        formula_data = data.get("formula", {})
        result_type = formula_data.get("type", "")

        if result_type == "string":
            return formula_data.get("string", "")

        elif result_type == "number":
            # Can be int or float
            number = formula_data.get("number")
            if number is None:
                return None
            if isinstance(number, float) and number.is_integer():
                return int(number)
            return number

        elif result_type == "boolean":
            return formula_data.get("boolean", False)

        elif result_type == "date":
            date_data = formula_data.get("date", {})
            if not date_data:
                return None
            # Parse ISO 8601 date
            date_str = date_data.get("start", "")
            if not date_str:
                return None
            return datetime.fromisoformat(date_str.replace('Z', '+00:00'))

        elif result_type == "empty":
            return None

        else:
            raise ValueError(f"Unsupported formula result type: {result_type}")

    @staticmethod
    def get_expression(data: dict[str, Any]) -> str:
        """Get formula expression string.

        Args:
            data: Raw formula property data from Notion API

        Returns:
            Formula expression string

        Example:
            >>> formula = {
            ...     \"type\": \"formula\",
            ...     \"formula\": {
            ...         \"expression\": \"prop(\"Status\") == \"Done\"\"
            ...     }
            ... }
            >>> expr = FormulaParser.get_expression(formula)
            >>> assert expr == \"prop(\\\"Status\\\") == \\\"Done\\\"\"
        """
        # Note: The schema has expression, not the instance data
        # This would typically come from database schema, not page data
        formula_data = data.get("formula", {})
        return formula_data.get("expression", "")

    @staticmethod
    def get_type(data: dict[str, Any]) -> str:
        """Get formula result type.

        Args:
            data: Raw formula property data from Notion API

        Returns:
            Formula result type (string, number, boolean, date, empty)

        Example:
            >>> formula = {
            ...     \"type\": \"formula\",
            ...     \"formula\": {
            ...         \"type\": \"number\",
            ...         \"number\": 42
            ...     }
            ... }
            >>> result_type = FormulaParser.get_type(formula)
            >>> assert result_type == \"number\"
        """
        formula_data = data.get("formula", {})
        return formula_data.get("type", "empty")
