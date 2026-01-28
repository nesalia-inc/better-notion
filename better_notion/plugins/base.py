"""
Base plugin interfaces and protocols for the Better Notion CLI plugin system.

Plugins can extend the CLI by:
1. Adding new commands (CommandPlugin)
2. Providing data filters/formatters (DataPlugin)
3. Combining both capabilities
4. Extending the SDK with models, caches, and managers (SDKPlugin)
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any, Protocol

import typer

if TYPE_CHECKING:
    from better_notion._sdk.cache import Cache
    from better_notion._sdk.client import NotionClient
    from better_notion._sdk.base.entity import BaseEntity


class CommandPlugin(Protocol):
    """
    Protocol for command plugins that add custom CLI commands.

    A command plugin can register new commands with the Typer application,
    extending the CLI with custom functionality.

    Example:
        class MyPlugin(CommandPlugin):
            def register_commands(self, app: typer.Typer) -> None:
                @app.command("my-command")
                def my_command():
                    typer.echo("Hello from my plugin!")

            def get_info(self) -> dict[str, Any]:
                return {
                    "name": "my-plugin",
                    "version": "1.0.0",
                    "description": "My custom plugin",
                    "author": "Author Name",
                    "official": False
                }
    """

    def register_commands(self, app: typer.Typer) -> None:
        """
        Register plugin commands with the CLI application.

        Args:
            app: The Typer application instance to register commands with
        """
        ...

    def get_info(self) -> dict[str, Any]:
        """
        Return plugin metadata.

        Returns:
            Dictionary with keys:
                - name: Plugin name (str)
                - version: Plugin version (str)
                - description: Plugin description (str)
                - author: Plugin author (str)
                - official: Whether this is an official plugin (bool)
                - dependencies: List of required dependencies (list[str])
                - category: Plugin category (str | None)
        """
        ...


class DataPlugin(Protocol):
    """
    Protocol for data plugins that provide custom data processing capabilities.

    A data plugin can register custom filters and formatters for processing
    Notion data.

    Example:
        class MyDataPlugin(DataPlugin):
            def register_filters(self) -> dict[str, callable]:
                return {
                    "uppercase": lambda x: x.upper()
                }

            def register_formatters(self) -> dict[str, callable]:
                return {
                    "markdown": format_as_markdown
                }
    """

    def register_filters(self) -> dict[str, Any]:
        """
        Register custom data filters.

        Returns:
            Dictionary mapping filter names to filter functions
        """
        ...

    def register_formatters(self) -> dict[str, Any]:
        """
        Register custom output formatters.

        Returns:
            Dictionary mapping formatter names to formatter functions
        """
        ...


class PluginInterface(ABC):
    """
    Abstract base class for plugins combining command and data capabilities.

    This class provides a common interface that plugins can implement
    to provide both commands and data processing capabilities.
    """

    @abstractmethod
    def register_commands(self, app: typer.Typer) -> None:
        """Register plugin commands with the CLI application."""
        pass

    def get_info(self) -> dict[str, Any]:
        """
        Return plugin metadata.

        Default implementation that subclasses can override.
        """
        return {
            "name": self.__class__.__name__,
            "version": "1.0.0",
            "description": "A plugin for Better Notion CLI",
            "author": "Unknown",
            "official": False,
            "dependencies": [],
            "category": None
        }

    def register_filters(self) -> dict[str, Any]:
        """
        Register custom data filters.

        Default implementation returns empty dict.
        """
        return {}

    def register_formatters(self) -> dict[str, Any]:
        """
        Register custom output formatters.

        Default implementation returns empty dict.
        """
        return {}

    # ===== SDK EXTENSION METHODS (OPTIONAL) =====

    def register_sdk_models(self) -> dict[str, type[BaseEntity]]:
        """
        Register custom SDK model classes.

        Plugins can register domain-specific models that extend BaseEntity.
        These models are accessible via client.plugin_model(name).

        Default implementation returns empty dict.

        Returns:
            Dictionary mapping model names to model classes

        Example:
            >>> def register_sdk_models(self) -> dict[str, type[BaseEntity]]:
            ...     return {
            ...         "Organization": Organization,
            ...         "Project": Project,
            ...     }
        """
        return {}

    def register_sdk_caches(self, client: "NotionClient") -> dict[str, "Cache"]:
        """
        Register custom SDK caches.

        Plugins can register dedicated caches for their models.
        These caches are accessible via client.plugin_cache(name).

        Default implementation returns empty dict.

        Args:
            client: NotionClient instance

        Returns:
            Dictionary mapping cache names to Cache instances

        Example:
            >>> def register_sdk_caches(self, client) -> dict[str, Cache]:
            ...     return {
            ...         "organizations": Cache(),
            ...         "projects": Cache(),
            ...     }
        """
        return {}

    def register_sdk_managers(self, client: "NotionClient") -> dict[str, Any]:
        """
        Register custom SDK managers.

        Plugins can register managers that provide convenience methods
        for working with their models. Managers are accessible via
        client.plugin_manager(name).

        Default implementation returns empty dict.

        Args:
            client: NotionClient instance

        Returns:
            Dictionary mapping manager names to manager instances

        Example:
            >>> def register_sdk_managers(self, client) -> dict[str, Any]:
            ...     return {
            ...         "organizations": OrganizationManager(client),
            ...     }
        """
        return {}

    def sdk_initialize(self, client: "NotionClient") -> None:
        """
        Initialize SDK plugin resources.

        Called after all registrations are complete. Use this for
        setup tasks like loading configuration, validating resources,
        or establishing connections.

        Default implementation does nothing.

        Args:
            client: NotionClient instance

        Example:
            >>> def sdk_initialize(self, client) -> None:
            ...     # Load workspace configuration
            ...     config = load_workspace_config()
            ...     client._workspace_config = config
        """
        pass

    def validate(self) -> tuple[bool, list[str]]:
        """
        Validate the plugin structure and configuration.

        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []

        # Check if get_info returns required fields
        try:
            info = self.get_info()
            required_fields = ["name", "version", "description", "author"]
            for field in required_fields:
                if field not in info:
                    errors.append(f"Missing required field: {field}")
        except Exception as e:
            errors.append(f"Failed to get plugin info: {e}")

        # Check if register_commands is implemented
        if not hasattr(self, 'register_commands'):
            errors.append("Plugin must implement register_commands method")

        return (len(errors) == 0, errors)
