"""Workspace metadata management for agents plugin.

This module provides functionality to manage workspace metadata,
including detecting duplicate workspaces and storing workspace information.
"""

import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional
from uuid import uuid4

from better_notion._sdk.client import NotionClient
from better_notion._sdk.models.page import Page

logger = logging.getLogger(__name__)


class WorkspaceMetadata:
    """Manage workspace metadata for duplicate detection."""

    # Property names used in Notion page
    PROP_WORKSPACE_ID = "agents_workspace_id"
    PROP_WORKSPACE_NAME = "agents_workspace_name"
    PROP_INITIALIZED_AT = "agents_workspace_created"
    PROP_VERSION = "agents_workspace_version"
    PROP_DATABASE_IDS = "agents_workspace_databases"

    @staticmethod
    def generate_workspace_id() -> str:
        """Generate a unique workspace ID.

        Returns:
            Unique workspace ID (UUID without hyphens for compactness)
        """
        return str(uuid4()).replace("-", "")

    @staticmethod
    def extract_metadata_from_page(page: Page) -> dict[str, Any]:
        """Extract workspace metadata from page properties.

        Args:
            page: Page object to extract metadata from

        Returns:
            Dict with workspace metadata (empty if not initialized)

        Example:
            >>> metadata = WorkspaceMetadata.extract_metadata_from_page(page)
            >>> if metadata.get("workspace_id"):
            ...     print(f"Workspace: {metadata['workspace_name']}")
        """
        metadata = {}

        # Try to get workspace ID from icon (stored as emoji)
        # Notion doesn't support custom properties, so we use creative approaches

        # Check if page icon contains our metadata marker
        icon = page.icon
        if icon and icon.startswith("🤖"):
            metadata["is_agents_workspace"] = True
            # Could encode data in icon, but keep it simple for now

        return metadata

    @staticmethod
    async def detect_workspace(
        page: Page,
        client: NotionClient
    ) -> dict[str, Any] | None:
        """Detect if page already has an agents workspace.

        Args:
            page: Parent page to check
            client: NotionClient instance

        Returns:
            Workspace metadata dict if found, None otherwise
        """
        # Primary detection: Scan for databases with expected names
        expected_databases = [
            "Organizations",
            "Tags",
            "Projects",
            "Versions",
            "Tasks",
            "Ideas",
            "Work Issues",
            "Incidents"
        ]

        try:
            # Search for databases in this page
            results = await client.search(
                query="",
                filter={"value": "database", "property": "object"}
            )

            databases_found = []
            database_ids = {}

            for result in results:
                if hasattr(result, 'title') and result.title in expected_databases:
                    databases_found.append(result.title)
                    # Extract the key name (lowercase with underscores)
                    key = result.title.lower().replace(" ", "_")
                    database_ids[key] = result.id

            # Check if we have at least 5 of the expected databases
            matches = len(databases_found)
            if matches >= 5:
                logger.info(f"Detected existing workspace with {matches}/{len(expected_databases)} databases in page {page.id}")

                # Try to load workspace metadata from local config to get workspace_id
                workspace_id = None
                workspace_name = None
                initialized_at = None

                try:
                    config_path = Path.home() / ".notion" / "workspace.json"
                    if config_path.exists():
                        with open(config_path, "r", encoding="utf-8") as f:
                            config = json.load(f)
                            # Only use config if it matches this page
                            if config.get("parent_page") == page.id:
                                workspace_id = config.get("workspace_id")
                                workspace_name = config.get("workspace_name")
                                initialized_at = config.get("initialized_at")
                                logger.info(f"Config file matches this page, workspace_id: {workspace_id}")
                except Exception as e:
                    logger.debug(f"Could not load local config: {e}")

                return {
                    "workspace_id": workspace_id,
                    "workspace_name": workspace_name,
                    "initialized_at": initialized_at,
                    "database_ids": database_ids,
                    "detection_method": "database_scan",
                    "databases_count": matches
                }
        except Exception as e:
            logger.debug(f"Could not scan for databases: {e}")

        return None

    @staticmethod
    def save_workspace_config(
        page_id: str,
        workspace_id: str,
        workspace_name: str,
        database_ids: dict[str, str],
        path: Optional[Path] = None
    ) -> Path:
        """Save workspace configuration to local file.

        Args:
            page_id: Parent page ID
            workspace_id: Unique workspace ID
            workspace_name: Workspace name
            database_ids: Dict of database name to ID
            path: Optional custom path for config file

        Returns:
            Path to saved config file
        """
        if path is None:
            path = Path.home() / ".notion" / "workspace.json"

        path.parent.mkdir(parents=True, exist_ok=True)

        config = {
            "workspace_id": workspace_id,
            "workspace_name": workspace_name,
            "parent_page": page_id,
            "initialized_at": datetime.now(timezone.utc).isoformat(),
            "version": "1.5.4",  # Track version for migrations
            "database_ids": database_ids
        }

        with open(path, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2)

        logger.info(f"Saved workspace config to {path}")
        return path
