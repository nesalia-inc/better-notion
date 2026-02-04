"""Personal workspace metadata management."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from better_notion._sdk.models.page import Page
from better_notion._sdk.client import NotionClient


CONFIG_PATH = Path.home() / ".notion" / "personal.json"


class PersonalWorkspaceMetadata:
    """Manages personal workspace metadata."""

    @staticmethod
    def load_config() -> dict[str, Any]:
        """Load workspace configuration from disk.

        Returns:
            Configuration dictionary with workspace_id, database_ids, etc.
        """
        if CONFIG_PATH.exists():
            with open(CONFIG_PATH, encoding="utf-8") as f:
                return json.load(f)
        return {}

    @staticmethod
    def save_config(config: dict[str, Any]) -> None:
        """Save workspace configuration to disk.

        Args:
            config: Configuration dictionary to save
        """
        CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2)

    @staticmethod
    async def detect_workspace(page: Page, client: NotionClient) -> dict[str, Any] | None:
        """Detect if a personal workspace exists in the given page.

        Args:
            page: The parent page to check
            client: Notion client for API calls

        Returns:
            Workspace metadata if found, None otherwise
        """
        # Load saved config to check if we know about this workspace
        config = PersonalWorkspaceMetadata.load_config()

        # Check if we have a workspace_id in config
        workspace_id = config.get("workspace_id")
        if not workspace_id:
            return None

        # Check if databases exist in this page
        expected_db_names = {
            "Domains",
            "Tags",
            "Projects",
            "Tasks",
            "Routines",
            "Agenda",
        }

        # Get all children databases from the page
        try:
            children = await page.children()
            databases = [c for c in children if c.object == "database"]

            if len(databases) < 5:  # Need at least 5 databases to consider it a workspace
                return None

            found_db_names = {db.title for db in databases}

            # Check if we have most expected databases
            matches = sum(1 for name in expected_db_names if name in found_db_names)

            if matches >= 5:
                # Load database IDs from config
                database_ids = config.get("database_ids", {})

                return {
                    "workspace_id": workspace_id,
                    "workspace_name": config.get("workspace_name"),
                    "initialized_at": config.get("initialized_at"),
                    "database_ids": database_ids,
                    "detection_method": "config_file",
                }
        except Exception:
            pass

        return None
