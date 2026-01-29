"""SDK Plugin System for extending NotionClient functionality.

This module provides the protocol interface for SDK-level plugins that need to:
- Register custom model classes
- Add dedicated caches to NotionClient
- Create custom managers
- Initialize plugin-specific resources
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Protocol

if TYPE_CHECKING:
    from better_notion._sdk.cache import Cache
    from better_notion._sdk.client import NotionClient
    from better_notion._sdk.base.entity import BaseEntity


class SDKPluginInterface(Protocol):
    """
    Protocol for SDK-level plugins that extend NotionClient functionality.

    SDK plugins can register custom models, caches, and managers with the
    NotionClient, enabling domain-specific extensions without modifying
    the core SDK.

    Example:
        >>> class AgentsSDKPlugin:
        ...     def register_models(self) -> dict[str, type[BaseEntity]]:
        ...         return {"Organization": Organization}
        ...
        ...     def register_caches(self, client: NotionClient) -> dict[str, Cache]:
        ...         return {"organizations": Cache()}
        ...
        ...     def register_managers(self, client: NotionClient) -> dict[str, Any]:
        ...         return {"organizations": OrganizationManager(client)}
    """

    def register_models(self) -> dict[str, type[BaseEntity]]:
        """Register custom model classes.

        Model classes should inherit from BaseEntity and follow the
        autonomous entity pattern (get, create, update methods).

        Returns:
            Dictionary mapping model names to model classes

        Example:
            >>> def register_models(self) -> dict[str, type[BaseEntity]]:
            ...     return {
            ...         "Organization": Organization,
            ...         "Project": Project,
            ...         "Task": Task,
            ...     }
        """
        ...

    def register_caches(self, client: "NotionClient") -> dict[str, "Cache"]:
        """Register custom caches with the client.

        Caches are stored in the client and accessible via
        client.plugin_cache(name). Each cache should have a unique name
        to avoid collisions with other plugins.

        Args:
            client: NotionClient instance to register caches with

        Returns:
            Dictionary mapping cache names to Cache instances

        Example:
            >>> def register_caches(self, client) -> dict[str, Cache]:
            ...     return {
            ...         "organizations": Cache(),
            ...         "projects": Cache(),
            ...         "tasks": Cache(),
            ...     }
        """
        ...

    def register_managers(self, client: "NotionClient") -> dict[str, Any]:
        """Register custom managers with the client.

        Managers are accessible via client.plugin_manager(name).
        They typically provide convenience methods for working with
        the plugin's models.

        Args:
            client: NotionClient instance

        Returns:
            Dictionary mapping manager names to manager instances

        Example:
            >>> def register_managers(self, client) -> dict[str, Any]:
            ...     return {
            ...         "organizations": OrganizationManager(client),
            ...         "projects": ProjectManager(client),
            ...     }
        """
        ...

    def initialize(self, client: "NotionClient") -> None:
        """Initialize plugin-specific resources.

        Called after all registrations (models, caches, managers) are
        complete. Use this for setup tasks like loading configuration,
        validating resources, or establishing connections.

        Args:
            client: NotionClient instance

        Example:
            >>> def initialize(self, client) -> None:
            ...     # Load database IDs from config
            ...     db_ids = load_workspace_config()
            ...     client._workspace_config = db_ids
        """
        ...

    def get_info(self) -> dict[str, Any]:
        """Return plugin metadata.

        Returns:
            Dictionary with plugin information

        Example:
            >>> def get_info(self) -> dict[str, Any]:
            ...     return {
            ...         "name": "agents-sdk",
            ...         "version": "1.0.0",
            ...         "description": "SDK extensions for agents workflow",
            ...     }
        """
        ...


class CombinedPluginInterface(Protocol):
    """
    Protocol for plugins that extend both CLI and SDK.

    This allows a single plugin class to provide:
    - CLI commands (via register_commands)
    - SDK extensions (via register_models, register_caches, etc.)

    Example:
        >>> class AgentsPlugin(CombinedPluginInterface):
        ...     def register_commands(self, app: typer.Typer) -> None:
        ...         # Register CLI commands
        ...         pass
        ...
        ...     def register_models(self) -> dict[str, type[BaseEntity]]:
        ...         # Register SDK models
        ...         return {"Organization": Organization}
    """

    def register_commands(self, app: Any) -> None:
        """Register CLI commands with Typer app."""
        ...

    def register_models(self) -> dict[str, type[BaseEntity]]:
        """Register custom model classes."""
        ...

    def register_caches(self, client: "NotionClient") -> dict[str, "Cache"]:
        """Register custom caches."""
        ...

    def register_managers(self, client: "NotionClient") -> dict[str, Any]:
        """Register custom managers."""
        ...

    def initialize(self, client: "NotionClient") -> None:
        """Initialize plugin resources."""
        ...

    def get_info(self) -> dict[str, Any]:
        """Return plugin metadata."""
        ...
