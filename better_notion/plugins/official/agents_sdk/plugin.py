"""Agents SDK Plugin - Registers workflow models and caches.

This plugin implements the SDKPluginInterface to register workflow
entity models (Organization, Project, Version, Task) and their
dedicated caches with NotionClient.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from better_notion._sdk.cache import Cache
from better_notion._sdk.plugins import SDKPluginInterface

if TYPE_CHECKING:
    from better_notion._sdk.base.entity import BaseEntity
    from better_notion._sdk.client import NotionClient


class AgentsSDKPlugin:
    """
    SDK Plugin for agents workflow management system.

    This plugin registers workflow entity models and dedicated caches
    with NotionClient, enabling agents to work with Organizations,
    Projects, Versions, and Tasks through the SDK.

    Example:
        >>> from better_notion import NotionClient
        >>> from better_notion.plugins.official.agents_sdk import AgentsSDKPlugin
        >>>
        >>> client = NotionClient(auth="...")
        >>> plugin = AgentsSDKPlugin()
        >>>
        >>> # Register models and caches
        >>> client.register_sdk_plugin(plugin)
        >>>
        >>> # Now use models
        >>> org = await Organization.get("org_id", client=client)
    """

    def register_models(self) -> dict[str, type]:
        """Register workflow entity models.

        Returns:
            Dictionary mapping model names to model classes
        """
        from better_notion.plugins.official.agents_sdk.models import (
            Organization,
            Project,
            Task,
            Version,
        )

        return {
            "Organization": Organization,
            "Project": Project,
            "Version": Version,
            "Task": Task,
        }

    def register_caches(self, client: "NotionClient") -> dict[str, Cache]:
        """Register dedicated caches for workflow entities.

        Args:
            client: NotionClient instance

        Returns:
            Dictionary mapping cache names to Cache instances
        """
        return {
            "organizations": Cache(),
            "projects": Cache(),
            "versions": Cache(),
            "tasks": Cache(),
        }

    def register_managers(self, client: "NotionClient") -> dict[str, Any]:
        """Register custom managers for workflow entities.

        Args:
            client: NotionClient instance

        Returns:
            Dictionary mapping manager names to manager instances
        """
        from better_notion.plugins.official.agents_sdk.managers import (
            OrganizationManager,
            ProjectManager,
            TaskManager,
            VersionManager,
        )

        return {
            "organizations": OrganizationManager(client),
            "projects": ProjectManager(client),
            "versions": VersionManager(client),
            "tasks": TaskManager(client),
        }

    def initialize(self, client: "NotionClient") -> None:
        """Initialize plugin resources.

        Loads workspace configuration to get database IDs.

        Args:
            client: NotionClient instance
        """
        import json
        from pathlib import Path

        config_path = Path.home() / ".notion" / "workspace.json"

        if config_path.exists():
            with open(config_path) as f:
                client._workspace_config = json.load(f)
        else:
            client._workspace_config = {}

    def get_info(self) -> dict[str, Any]:
        """Return plugin metadata.

        Returns:
            Dictionary with plugin information
        """
        return {
            "name": "agents-sdk",
            "version": "1.0.0",
            "description": "SDK extensions for agents workflow management",
            "author": "Better Notion Team",
        }
