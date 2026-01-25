"""Property parsers for extracting typed values from Notion API properties."""

from __future__ import annotations

from datetime import datetime
from typing import Any


class PropertyParser:
    """Utility class for parsing Notion properties.

    Provides static methods to extract typed values from Notion's
    nested property structures.

    Example:
        >>> properties = {"Name": {"type": "title", "title": [{"text": {"content": "My Page"}}]}}
        >>> title = PropertyParser.get_title(properties)
        >>> print(title)
        'My Page'
    """

    @staticmethod
    def get_title(properties: dict[str, Any]) -> str | None:
        """Extract title from properties.

        Args:
            properties: Properties dict from Notion API

        Returns:
            Title text or None if no title

        Note:
            Finds first property of type "title".

        Example:
            >>> title = PropertyParser.get_title(page.properties)
        """
        for prop_name, prop_data in properties.items():
            if prop_data.get("type") == "title":
                title_array = prop_data.get("title", [])
                if title_array and title_array[0].get("type") == "text":
                    return title_array[0]["text"].get("content")
        return None

    @staticmethod
    def get_select(properties: dict[str, Any], name: str) -> str | None:
        """Extract select property value.

        Args:
            properties: Properties dict
            name: Property name (case-insensitive)

        Returns:
            Select option name or None

        Example:
            >>> status = PropertyParser.get_select(page.properties, "Status")
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

        Example:
            >>> tags = PropertyParser.get_multi_select(page.properties, "Tags")
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

        Example:
            >>> done = PropertyParser.get_checkbox(page.properties, "Done")
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

        Example:
            >>> priority = PropertyParser.get_number(page.properties, "Priority")
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

        Example:
            >>> due_date = PropertyParser.get_date(page.properties, "Due Date")
        """
        prop = PropertyParser._find_property(properties, name)
        if prop and prop.get("type") == "date":
            date_data = prop.get("date")
            if date_data and date_data.get("start"):
                # Parse ISO 8601 date
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

        Example:
            >>> url = PropertyParser.get_url(page.properties)
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

        Example:
            >>> email = PropertyParser.get_email(page.properties)
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

        Example:
            >>> phone = PropertyParser.get_phone(page.properties)
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

        Example:
            >>> assignees = PropertyParser.get_people(page.properties, "Assignee")
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

        Example:
            >>> prop = PropertyParser._find_property(page.properties, "status")
        """
        name_lower = name.lower()

        for prop_name, prop_data in properties.items():
            if prop_name.lower() == name_lower:
                return prop_data

        return None
