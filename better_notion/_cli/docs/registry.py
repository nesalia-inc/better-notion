"""Schema registry for plugin documentation.

This module provides a central registry where plugins can register
their documentation schemas for AI agent consumption.
"""

import logging
from typing import Any

from better_notion._cli.docs.base import Schema

logger = logging.getLogger(__name__)


class SchemaRegistry:
    """Registry for plugin documentation schemas.

    This class maintains a collection of plugin schemas that
    AI agents can query to understand the system.

    Example:
        >>> # Register a plugin schema
        >>> SchemaRegistry.register("agents", AGENTS_SCHEMA)
        >>>
        >>> # Query for a plugin schema
        >>> schema = SchemaRegistry.get("agents")
        >>>
        >>> # List all available schemas
        >>> all_schemas = SchemaRegistry.list_all()
    """

    _schemas: dict[str, Schema] = {}

    @classmethod
    def register(cls, plugin_name: str, schema: Schema) -> None:
        """Register a plugin schema.

        Args:
            plugin_name: Name of the plugin (e.g., "agents")
            schema: Schema object containing plugin documentation
        """
        cls._schemas[plugin_name] = schema
        logger.info(f"Registered schema for plugin: {plugin_name}")

    @classmethod
    def get(cls, plugin_name: str) -> Schema | None:
        """Get a plugin schema by name.

        Args:
            plugin_name: Name of the plugin

        Returns:
            Schema object if found, None otherwise
        """
        return cls._schemas.get(plugin_name)

    @classmethod
    def list_all(cls) -> dict[str, Schema]:
        """List all registered plugin schemas.

        Returns:
            Dict mapping plugin names to Schema objects
        """
        return cls._schemas.copy()

    @classmethod
    def get_all_names(cls) -> list[str]:
        """Get list of all registered plugin names.

        Returns:
            List of plugin names
        """
        return list(cls._schemas.keys())

    @classmethod
    def clear(cls) -> None:
        """Clear all registered schemas.

        This is primarily useful for testing.
        """
        cls._schemas.clear()
        logger.debug("Cleared schema registry")
