"""Workspace initializer for the agents workflow system.

This module provides functionality to initialize a new workspace with all
required databases for the workflow management system.
"""

import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional

from better_notion._cli.config import Config
from better_notion._sdk.client import NotionClient
from better_notion._sdk.models.page import Page
from better_notion.utils.agents.metadata import WorkspaceMetadata
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

logger = logging.getLogger(__name__)


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
        self._workspace_id: Optional[str] = None
        self._parent_page_id: Optional[str] = None
        self._workspace_name: Optional[str] = None

    async def initialize_workspace(
        self,
        parent_page_id: str,
        workspace_name: str = "Agents Workspace",
        skip_detection: bool = False,
    ) -> Dict[str, str]:
        """Initialize a complete workspace with all databases.

        Creates all 8 databases in the correct order, establishing
        relationships between them.

        Args:
            parent_page_id: ID of the parent page where databases will be created
            workspace_name: Name for the workspace (used for database titles)
            skip_detection: If True, skip duplicate detection (for reset operation)

        Returns:
            Dict mapping database names to their IDs

        Raises:
            Exception: If database creation fails with detailed error message
            Exception: If workspace already exists (and skip_detection is False)
        """
        logger.info(f"Initializing workspace '{workspace_name}' in page {parent_page_id}")

        # Store workspace info
        self._parent_page_id = parent_page_id
        self._workspace_name = workspace_name
        self._workspace_id = WorkspaceMetadata.generate_workspace_id()

        # Get parent page
        try:
            parent = await Page.get(parent_page_id, client=self._client)
            logger.info(f"Parent page found: {parent.id}")
        except Exception as e:
            error_msg = f"Failed to get parent page '{parent_page_id}': {str(e)}"
            logger.error(error_msg)
            raise Exception(error_msg) from e

        # Check for existing workspace
        existing = await WorkspaceMetadata.detect_workspace(parent, self._client)

        if existing:
            if skip_detection:
                # --reset flag: Delete all existing databases first
                logger.warning(f"Reset mode: Deleting {len(existing.get('database_ids', {}))} existing databases...")
                await self._delete_existing_databases(parent, existing.get("database_ids", {}))
                logger.info("All existing databases deleted")
            else:
                # Normal mode: Raise error if workspace exists
                workspace_info = {
                    "workspace_id": existing.get("workspace_id", "unknown"),
                    "workspace_name": existing.get("workspace_name", workspace_name),
                    "initialized_at": existing.get("initialized_at", "unknown"),
                    "databases": existing.get("database_ids", {})
                }
                error_msg = (
                    f"Workspace already initialized in this page\n"
                    f"Workspace ID: {workspace_info['workspace_id']}\n"
                    f"Initialized: {workspace_info['initialized_at']}\n"
                    f"Databases: {len(workspace_info.get('databases', {}))} created\n"
                    f"Use --reset to reinitialize or --skip to keep existing"
                )
                logger.error(error_msg)
                raise Exception(error_msg) from None

        # Create databases in order (independent first, then dependent)
        self._database_ids = {}
        databases_order = [
            ("Organizations", "organizations", self._create_organizations_db),
            ("Tags", "tags", self._create_tags_db),
            ("Projects", "projects", self._create_projects_db),
            ("Versions", "versions", self._create_versions_db),
            ("Tasks", "tasks", self._create_tasks_db),
            ("Ideas", "ideas", self._create_ideas_db),
            ("Work Issues", "work_issues", self._create_work_issues_db),
            ("Incidents", "incidents", self._create_incidents_db),
        ]

        try:
            for display_name, key, create_func in databases_order:
                try:
                    logger.info(f"Creating {display_name} database...")
                    await create_func(parent)
                    logger.info(f"✓ {display_name} database created: {self._database_ids[key]}")
                except Exception as e:
                    # Clean up databases created so far
                    import traceback
                    logger.error(f"Failed to create {display_name} database: {str(e)}")
                    logger.error(f"Full traceback:\n{traceback.format_exc()}")

                    # Try to get more error details if available
                    error_details = str(e)
                    if hasattr(e, 'response') and hasattr(e.response, 'text'):
                        logger.error(f"Notion API response: {e.response.text}")
                        error_details += f"\nNotion API response: {e.response.text}"

                    logger.warning(f"Cleaning up {len(self._database_ids)} databases that were created...")
                    await self._delete_existing_databases(parent, self._database_ids)

                    error_msg = (
                        f"Failed to create {display_name} database: {error_details}\n"
                        f"All partially created databases have been deleted.\n"
                        f"Parent page: {parent_page_id}\n"
                        f"Workspace name: {workspace_name}"
                    )
                    logger.error(error_msg)
                    raise Exception(error_msg) from e
        except Exception as e:
            # Re-raise the exception
            raise e

        # Update cross-database relations that require both databases to exist
        await self._update_cross_database_relations()

        # Save workspace metadata
        self.save_database_ids()

        logger.info(f"Workspace initialization complete. Created {len(self._database_ids)} databases")
        logger.info(f"Workspace ID: {self._workspace_id}")
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
        if "tasks" in self._database_ids:
            schema["Related Task"]["relation"]["database_id"] = self._database_ids["tasks"]
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
            schema["Fix Tasks"]["relation"]["database_id"] = self._database_ids["tasks"]
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

    async def _delete_existing_databases(self, parent: Page, database_ids: dict) -> None:
        """Delete all existing databases in the parent page.

        Args:
            parent: Parent page
            database_ids: Dict of database IDs to delete
        """
        import asyncio

        deletion_tasks = []
        for db_name, db_id in database_ids.items():
            if db_id:
                logger.info(f"Deleting {db_name} database ({db_id})...")
                deletion_tasks.append(self._delete_database(db_id))

        # Delete all databases concurrently
        if deletion_tasks:
            await asyncio.gather(*deletion_tasks, return_exceptions=True)

    async def _delete_database(self, database_id: str) -> None:
        """Delete a single database.

        Args:
            database_id: ID of the database to delete
        """
        try:
            await self._client._api._request(
                "DELETE",
                f"/blocks/{database_id}"
            )
            logger.info(f"Deleted database {database_id}")
        except Exception as e:
            logger.warning(f"Failed to delete database {database_id}: {str(e)}")
            # Continue with other deletions even if this one fails

    async def _update_self_relations(self, database_id: str) -> None:
        """Add self-referential Dependencies relation to Tasks database.

        The Dependencies property cannot be included in the initial schema
        because it requires the database's own ID. This method adds it
        after the database is created.

        Args:
            database_id: ID of the Tasks database
        """
        # Get the current database schema
        db = await self._client.databases.get(database_id)
        schema = db.schema

        # Add the Dependencies self-referential relation
        # This creates a relation from Tasks to Tasks itself
        schema["Dependencies"] = {
            "relation": {
                "database_id": database_id,  # Self-reference
                "type": "dual_property",
                "dual_property": {
                    "synced_property_name": "Dependent Tasks",
                    "synced_property_type": "relation"
                }
            }
        }

        # Update the database schema via API
        await self._client._api._request(
            "PATCH",
            f"/databases/{database_id}",
            json={"properties": schema}
        )

        logger.info(f"Added Dependencies self-referential relation to Tasks database {database_id}")

    async def _update_cross_database_relations(self) -> None:
        """Update cross-database relations after all databases are created.

        This updates:
        - Tasks: Related Work Issue -> Work Issues
        - Work Issues: Blocking Tasks -> Tasks
        - Work Issues: Caused Incidents -> Incidents
        - Incidents: Root Cause Work Issue -> Work Issues
        """
        if "tasks" in self._database_ids:
            await self._update_relation(
                self._database_ids["tasks"],
                "Related Work Issue",
                self._database_ids.get("work_issues")
            )

        if "work_issues" in self._database_ids:
            await self._update_relation(
                self._database_ids["work_issues"],
                "Blocking Tasks",
                self._database_ids.get("tasks")
            )
            await self._update_relation(
                self._database_ids["work_issues"],
                "Caused Incidents",
                self._database_ids.get("incidents")
            )

        if "incidents" in self._database_ids:
            await self._update_relation(
                self._database_ids["incidents"],
                "Root Cause Work Issue",
                self._database_ids.get("work_issues")
            )

        logger.info("Updated all cross-database relations")

    async def _update_relation(
        self,
        database_id: str,
        property_name: str,
        target_database_id: Optional[str],
    ) -> None:
        """Update a relation property to point to the target database.

        Args:
            database_id: Database to update
            property_name: Name of the relation property
            target_database_id: Target database ID (if None, skip update)
        """
        if not target_database_id:
            logger.warning(f"Skipping {property_name} update: target database not found")
            return

        # Get the current database schema
        db = await self._client.databases.get(database_id)
        schema = db.schema

        # Update the relation property
        if property_name in schema:
            schema[property_name]["relation"]["database_id"] = target_database_id

            # Update the database schema via API
            await self._client._api._request(
                "PATCH",
                f"/databases/{database_id}",
                json={"properties": schema}
            )

            logger.info(f"Updated {property_name} relation to {target_database_id}")
        else:
            logger.warning(f"Property {property_name} not found in database {database_id}")

    def save_database_ids(self, path: Optional[Path] = None) -> None:
        """Save workspace metadata (database IDs and workspace info) to config file.

        Saves database IDs at top level with capitalized keys (e.g., "Organizations", "Projects")
        to match what SDK managers expect. Also saves under "database_ids" for compatibility.

        Args:
            path: Path to save config file (default: ~/.notion/workspace.json)
        """
        if path is None:
            path = Path.home() / ".notion" / "workspace.json"

        path.parent.mkdir(parents=True, exist_ok=True)

        # Map lowercase keys to capitalized keys for SDK manager compatibility
        database_ids_capitalized = {
            key.capitalize(): value for key, value in self._database_ids.items()
        }

        # Save full workspace metadata
        # Database IDs are saved at top level with capitalized keys for SDK managers
        config = {
            "workspace_id": self._workspace_id,
            "workspace_name": self._workspace_name,
            "parent_page": self._parent_page_id,
            "initialized_at": datetime.now(timezone.utc).isoformat(),
            "version": "1.5.4",
            **database_ids_capitalized,  # Save at top level: "Organizations", "Projects", etc.
            "database_ids": self._database_ids,  # Also save under database_ids for compatibility
        }

        with open(path, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2)

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
