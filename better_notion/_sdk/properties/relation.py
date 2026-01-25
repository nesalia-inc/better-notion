"""Relation property parser for Notion relation properties."""

from __future__ import annotations

from typing import Any


class RelationParser:
    """Parse Notion relation properties.

    Relation properties link pages between databases.
    A relation can have 0 or more related page IDs.

    Example:
        >>> page_ids = RelationParser.parse(relation_data)
        >>> print(page_ids)  # ['page-1', 'page-2']
    """

    @staticmethod
    def parse(data: dict[str, Any]) -> list[str]:
        """Parse relation property value.

        Args:
            data: Raw relation property data from Notion API

        Returns:
            List of related page IDs

        Example:
            >>> relation = {
            ...     \"type\": \"relation\",
            ...     \"relation\": [
            ...         {\"id\": \"page-123\"},
            ...         {\"id\": \"page-456\"}
            ...     ]
            ... }
            >>> page_ids = RelationParser.parse(relation)
            >>> assert page_ids == [\"page-123\", \"page-456\"]
        """
        relation_data = data.get("relation", [])
        return [item["id"] for item in relation_data]

    @staticmethod
    def get_database_id(data: dict[str, Any]) -> str | None:
        """Get the database ID this relation points to.

        Note: This is typically available in the database schema,
        not in the page property data.

        Args:
            data: Raw relation property data from Notion API

        Returns:
            Database ID or None

        Example:
            >>> relation_schema = {
            ...     \"type\": \"relation\",
            ...     \"relation\": {
            ...         \"database_id\": \"db-123\",
            ...         \"type\": \"dual_property\"
            ...     }
            ... }
            >>> db_id = RelationParser.get_database_id(relation_schema)
            >>> assert db_id == \"db-123\"
        """
        relation_data = data.get("relation", {})
        return relation_data.get("database_id")

    @staticmethod
    def get_type(data: dict[str, Any]) -> str | None:
        """Get relation type (dual_property or single_property).

        Note: This is typically available in the database schema.

        Args:
            data: Raw relation property data from Notion API

        Returns:
            Relation type or None

        Example:
            >>> relation_schema = {
            ...     \"type\": \"relation\",
            ...     \"relation\": {
            ...         \"database_id\": \"db-123\",
            ...         \"type\": \"dual_property\"
            ...     }
            ... }
            >>> rel_type = RelationParser.get_type(relation_schema)
            >>> assert rel_type == \"dual_property\"
        """
        relation_data = data.get("relation", {})
        return relation_data.get("type")

    @staticmethod
    def count(data: dict[str, Any]) -> int:
        """Count number of related pages.

        Args:
            data: Raw relation property data from Notion API

        Returns:
            Number of related pages

        Example:
            >>> relation = {
            ...     \"type\": \"relation\",
            ...     \"relation\": [
            ...         {\"id\": \"page-123\"},
            ...         {\"id\": \"page-456\"}
            ...     ]
            ... }
            >>> count = RelationParser.count(relation)
            >>> assert count == 2
        """
        relation_data = data.get("relation", [])
        return len(relation_data)

    @staticmethod
    def has_related_page(data: dict[str, Any], page_id: str) -> bool:
        """Check if a specific page is related.

        Args:
            data: Raw relation property data from Notion API
            page_id: Page ID to check

        Returns:
            True if page is in relation

        Example:
            >>> relation = {
            ...     \"type\": \"relation\",
            ...     \"relation\": [
            ...         {\"id\": \"page-123\"}
            ...     ]
            ... }
            >>> has_page = RelationParser.has_related_page(relation, \"page-123\")
            >>> assert has_page is True
        """
        relation_data = data.get("relation", [])
        return any(item["id"] == page_id for item in relation_data)
