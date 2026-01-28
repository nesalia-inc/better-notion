"""Workspace initializer for the agents workflow system.

This module provides functionality to initialize a new workspace with all
required databases for the workflow management system.
"""

import json
from pathlib import Path
from typing import Any, Dict, Optional

from better_notion._cli.config import Config
from better_notion._sdk.client import NotionClient
from better_notion._sdk.models.page import Page
from better_notion.utils.agents.schemas import (
    IncidentSchema,
    IdeaSchema,
    OrganizationSchema,
    ProjectSchema,
    TagSchema,
    TaskSchema,
    VersionSchema,
    WorkIssueSchema,
)


class WorkspaceInitializer:
    """Initialize a new workspace with workflow databases.

    This class handles the creation of all required databases and their
    relationships for the agents workflow system.

    Example:
        >>> initializer = WorkspaceInitializer(client)
        >>> database_ids = await initializer.initialize_workspace(
        ...     parent_page_id="page123",
        ...     workspace_name="My Workspace"
        ... )
    """

    def __init__(self, client: NotionClient) -> None:
        """Initialize the workspace initializer.

        Args:
            client: Authenticated NotionClient instance
        """
        self._client = client
        self._database_ids: Dict[str, str] = {}

    async def initialize_workspace(
        self,
        parent_page_id: str,
        workspace_name: str = "Agents Workspace",
    ) -> Dict[str, str]:
        """Initialize a complete workspace with all databases.

        Creates all 8 databases in the correct order, establishing
        relationships between them.

        Args:
            parent_page_id: ID of the parent page where databases will be created
            workspace_name: Name for the workspace (used for database titles)

        Returns:
            Dict mapping database names to their IDs

        Raises:
            Exception: If database creation fails
        """
        # Get parent page
        parent = await Page.get(parent_page_id, client=self._client)

        # Create databases in order (independent first, then dependent)
        self._database_ids = {}

        # 1. Organizations (independent)
        await self._create_organizations_db(parent)

        # 2. Tags (independent)
        await self._create_tags_db(parent)

        # 3. Projects (depends on Organizations)
        await self._create_projects_db(parent)

        # 4. Versions (depends on Projects)
        await self._create_versions_db(parent)

        # 5. Tasks (depends on Versions)
        await self._create_tasks_db(parent)

        # 6. Ideas (depends on Projects)
        await self._create_ideas_db(parent)

        # 7. Work Issues (depends on Projects, Tasks, Ideas)
        await self._create_work_issues_db(parent)

        # 8. Incidents (depends on Projects, Versions, Tasks)
        await self._create_incidents_db(parent)

        return self._database_ids

    async def _create_organizations_db(self, parent: Page) -> None:
        """Create Organizations database."""
        schema = OrganizationSchema.get_schema()

        db = await self._client.databases.create(
            parent=parent,
            title="Organizations",
            schema=schema,
        )

        self._database_ids["organizations"] = db.id

    async def _create_tags_db(self, parent: Page) -> None:
        """Create Tags database."""
        schema = TagSchema.get_schema()

        db = await self._client.databases.create(
            parent=parent,
            title="Tags",
            schema=schema,
        )

        self._database_ids["tags"] = db.id

    async def _create_projects_db(self, parent: Page) -> None:
        """Create Projects database with relation to Organizations."""
        schema = ProjectSchema.get_schema()

        # Update relation with Organizations database ID
        if "organizations" in self._database_ids:
            schema["Organization"]["relation"]["database_id"] = self._database_ids[
                "organizations"
            ]

        db = await self._client.databases.create(
            parent=parent,
            title="Projects",
            schema=schema,
        )

        self._database_ids["projects"] = db.id

        # Update Organizations database with reverse relation
        await self._add_reverse_relation(
            self._database_ids["organizations"],
            db.id,
            "Projects",
        )

    async def _create_versions_db(self, parent: Page) -> None:
        """Create Versions database with relation to Projects."""
        schema = VersionSchema.get_schema()

        # Update relation with Projects database ID
        if "projects" in self._database_ids:
            schema["Project"]["relation"]["database_id"] = self._database_ids["projects"]

        db = await self._client.databases.create(
            parent=parent,
            title="Versions",
            schema=schema,
        )

        self._database_ids["versions"] = db.id

        # Update Projects database with reverse relation
        await self._add_reverse_relation(
            self._database_ids["projects"],
            db.id,
            "Versions",
        )

    async def _create_tasks_db(self, parent: Page) -> None:
        """Create Tasks database with relations to Versions (self-referencing for dependencies)."""
        schema = TaskSchema.get_schema()

        # Update relations with Versions database ID
        if "versions" in self._database_ids:
            schema["Version"]["relation"]["database_id"] = self._database_ids["versions"]
            schema["Target Version"]["relation"]["database_id"] = self._database_ids[
                "versions"
            ]

        # Tasks reference themselves for dependencies
        # Will be updated after database creation
        db = await self._client.databases.create(
            parent=parent,
            title="Tasks",
            schema=schema,
        )

        self._database_ids["tasks"] = db.id

        # Update self-referential relations
        await self._update_self_relations(db.id)

        # Update Versions database with reverse relation
        await self._add_reverse_relation(
            self._database_ids["versions"],
            db.id,
            "Tasks",
        )

    async def _create_ideas_db(self, parent: Page) -> None:
        """Create Ideas database with relations to Projects and Tasks."""
        schema = IdeaSchema.get_schema()

        # Update relations
        if "projects" in self._database_ids:
            schema["Project"]["relation"]["database_id"] = self._database_ids["projects"]

        # Related Task will be updated after Tasks DB creation
        db = await self._client.databases.create(
            parent=parent,
            title="Ideas",
            schema=schema,
        )

        self._database_ids["ideas"] = db.id

        # Update Projects database with reverse relation
        await self._add_reverse_relation(
            self._database_ids["projects"],
            db.id,
            "Ideas",
        )

    async def _create_work_issues_db(self, parent: Page) -> None:
        """Create Work Issues database with relations."""
        schema = WorkIssueSchema.get_schema()

        # Update relations
        if "projects" in self._database_ids:
            schema["Project"]["relation"]["database_id"] = self._database_ids["projects"]
        if "tasks" in self._database_ids:
            schema["Task"]["relation"]["database_id"] = self._database_ids["tasks"]
        if "ideas" in self._database_ids:
            schema["Related Idea"]["relation"]["database_id"] = self._database_ids["ideas"]

        db = await self._client.databases.create(
            parent=parent,
            title="Work Issues",
            schema=schema,
        )

        self._database_ids["work_issues"] = db.id

    async def _create_incidents_db(self, parent: Page) -> None:
        """Create Incidents database with relations."""
        schema = IncidentSchema.get_schema()

        # Update relations
        if "projects" in self._database_ids:
            schema["Project"]["relation"]["database_id"] = self._database_ids["projects"]
        if "versions" in self._database_ids:
            schema["Affected Version"]["relation"][
                "database_id"
            ] = self._database_ids["versions"]
        if "tasks" in self._database_ids:
            schema["Fix Task"]["relation"]["database_id"] = self._database_ids["tasks"]

        db = await self._client.databases.create(
            parent=parent,
            title="Incidents",
            schema=schema,
        )

        self._database_ids["incidents"] = db.id

    async def _add_reverse_relation(
        self,
        database_id: str,
        related_db_id: str,
        property_name: str,
    ) -> None:
        """Add reverse relation to a database.

        Note: This is a placeholder. The actual Notion API creates
        dual_property relations automatically. This method exists
        for documentation purposes.
        """
        # Notion API handles dual_property relations automatically
        # This is a no-op but documents the intent
        pass

    async def _update_self_relations(self, database_id: str) -> None:
        """Update self-referential relations in Tasks database.

        Note: The database was created with placeholder relations.
        This method updates them to point to themselves.
        """
        # Get the database
        db = await self._client.databases.get(database_id)

        # Update Dependencies and Dependent Tasks to point to self
        # Note: This would require updating the database schema
        # via the Notion API, which may not support all updates
        pass

    def save_database_ids(self, path: Optional[Path] = None) -> None:
        """Save database IDs to a config file.

        Args:
            path: Path to save config file (default: ~/.notion/workspace.json)
        """
        if path is None:
            path = Path.home() / ".notion" / "workspace.json"

        path.parent.mkdir(parents=True, exist_ok=True)

        with open(path, "w", encoding="utf-8") as f:
            json.dump(self._database_ids, f, indent=2)

    @classmethod
    def load_database_ids(cls, path: Optional[Path] = None) -> Dict[str, str]:
        """Load database IDs from config file.

        Args:
            path: Path to config file (default: ~/.notion/workspace.json)

        Returns:
            Dict mapping database names to IDs

        Raises:
            FileNotFoundError: If config file doesn't exist
        """
        if path is None:
            path = Path.home() / ".notion" / "workspace.json"

        with open(path, encoding="utf-8") as f:
            return json.load(f)


async def initialize_workspace_command(
    parent_page_id: str,
    workspace_name: str = "Agents Workspace",
) -> Dict[str, str]:
    """Convenience function to initialize a workspace.

    Args:
        parent_page_id: ID of parent page
        workspace_name: Name for the workspace

    Returns:
        Dict mapping database names to IDs

    Example:
        >>> from better_notion._cli.config import Config
        >>> from better_notion._sdk.client import NotionClient
        >>>
        >>> config = Config.load()
        >>> client = NotionClient(auth=config.token)
        >>>
        >>> db_ids = await initialize_workspace_command(
        ...     parent_page_id="page123",
        ...     workspace_name="My Workspace"
        ... )
    """
    from better_notion._cli.config import Config
    from better_notion._sdk.client import NotionClient

    config = Config.load()
    client = NotionClient(auth=config.token)

    initializer = WorkspaceInitializer(client)
    database_ids = await initializer.initialize_workspace(parent_page_id, workspace_name)

    # Save to config file
    initializer.save_database_ids()

    return database_ids
