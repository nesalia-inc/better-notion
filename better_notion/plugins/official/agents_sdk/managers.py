"""Managers for workflow entities.

These managers provide convenience methods for working with workflow
entities through the client.plugin_manager() interface.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from better_notion._sdk.client import NotionClient


class OrganizationManager:
    """
    Manager for Organization entities.

    Provides convenience methods for working with organizations.

    Example:
        >>> manager = client.plugin_manager("organizations")
        >>> orgs = await manager.list()
        >>> org = await manager.get("org_id")
    """

    def __init__(self, client: "NotionClient") -> None:
        """Initialize organization manager.

        Args:
            client: NotionClient instance
        """
        self._client = client

    async def list(self) -> list:
        """
        List all organizations.

        Returns:
            List of Organization instances
        """
        from better_notion.plugins.official.agents_sdk.models import Organization

        # Get database ID from workspace config
        database_id = self._get_database_id("Organizations")
        if not database_id:
            return []

        # Query all pages
        response = await self._client._api.databases.query(database_id=database_id)

        return [
            Organization(self._client, page_data)
            for page_data in response.get("results", [])
        ]

    async def get(self, org_id: str) -> Any:
        """
        Get an organization by ID.

        Args:
            org_id: Organization page ID

        Returns:
            Organization instance
        """
        from better_notion.plugins.official.agents_sdk.models import Organization

        return await Organization.get(org_id, client=self._client)

    async def create(
        self,
        name: str,
        slug: str | None = None,
        description: str | None = None,
        repository_url: str | None = None,
        status: str = "Active",
    ) -> Any:
        """
        Create a new organization.

        Args:
            name: Organization name
            slug: URL-safe identifier
            description: Organization description
            repository_url: Code repository URL
            status: Organization status

        Returns:
            Created Organization instance
        """
        from better_notion.plugins.official.agents_sdk.models import Organization

        database_id = self._get_database_id("Organizations")
        if not database_id:
            raise ValueError("Organizations database ID not found in workspace config")

        return await Organization.create(
            client=self._client,
            database_id=database_id,
            name=name,
            slug=slug,
            description=description,
            repository_url=repository_url,
            status=status,
        )

    def _get_database_id(self, name: str) -> str | None:
        """Get database ID from workspace config."""
        return getattr(self._client, "_workspace_config", {}).get(name)


class ProjectManager:
    """
    Manager for Project entities.

    Example:
        >>> manager = client.plugin_manager("projects")
        >>> projects = await manager.list()
        >>> project = await manager.get("project_id")
    """

    def __init__(self, client: "NotionClient") -> None:
        """Initialize project manager."""
        self._client = client

    async def list(self, organization_id: str | None = None) -> list:
        """
        List all projects, optionally filtered by organization.

        Args:
            organization_id: Filter by organization ID (optional)

        Returns:
            List of Project instances
        """
        from better_notion.plugins.official.agents_sdk.models import Project

        database_id = self._get_database_id("Projects")
        if not database_id:
            return []

        # Build filter
        filter_dict: dict[str, Any] = {}
        if organization_id:
            filter_dict = {
                "property": "Organization",
                "relation": {"contains": organization_id},
            }

        # Query pages
        response = await self._client._api.databases.query(
            database_id=database_id,
            filter=filter_dict if filter_dict else None,
        )

        return [
            Project(self._client, page_data)
            for page_data in response.get("results", [])
        ]

    async def get(self, project_id: str) -> Any:
        """Get a project by ID."""
        from better_notion.plugins.official.agents_sdk.models import Project

        return await Project.get(project_id, client=self._client)

    async def create(
        self,
        name: str,
        organization_id: str,
        slug: str | None = None,
        description: str | None = None,
        repository: str | None = None,
        status: str = "Active",
        tech_stack: list[str] | None = None,
        role: str = "Developer",
    ) -> Any:
        """Create a new project."""
        from better_notion.plugins.official.agents_sdk.models import Project

        database_id = self._get_database_id("Projects")
        if not database_id:
            raise ValueError("Projects database ID not found in workspace config")

        return await Project.create(
            client=self._client,
            database_id=database_id,
            name=name,
            organization_id=organization_id,
            slug=slug,
            description=description,
            repository=repository,
            status=status,
            tech_stack=tech_stack,
            role=role,
        )

    def _get_database_id(self, name: str) -> str | None:
        """Get database ID from workspace config."""
        return getattr(self._client, "_workspace_config", {}).get(name)


class VersionManager:
    """
    Manager for Version entities.

    Example:
        >>> manager = client.plugin_manager("versions")
        >>> versions = await manager.list()
        >>> version = await manager.get("version_id")
    """

    def __init__(self, client: "NotionClient") -> None:
        """Initialize version manager."""
        self._client = client

    async def list(self, project_id: str | None = None) -> list:
        """
        List all versions, optionally filtered by project.

        Args:
            project_id: Filter by project ID (optional)

        Returns:
            List of Version instances
        """
        from better_notion.plugins.official.agents_sdk.models import Version

        database_id = self._get_database_id("Versions")
        if not database_id:
            return []

        # Build filter
        filter_dict: dict[str, Any] = {}
        if project_id:
            filter_dict = {
                "property": "Project",
                "relation": {"contains": project_id},
            }

        # Query pages
        response = await self._client._api.databases.query(
            database_id=database_id,
            filter=filter_dict if filter_dict else None,
        )

        return [
            Version(self._client, page_data)
            for page_data in response.get("results", [])
        ]

    async def get(self, version_id: str) -> Any:
        """Get a version by ID."""
        from better_notion.plugins.official.agents_sdk.models import Version

        return await Version.get(version_id, client=self._client)

    async def create(
        self,
        name: str,
        project_id: str,
        status: str = "Planning",
        version_type: str = "Minor",
        branch_name: str | None = None,
        progress: int = 0,
    ) -> Any:
        """Create a new version."""
        from better_notion.plugins.official.agents_sdk.models import Version

        database_id = self._get_database_id("Versions")
        if not database_id:
            raise ValueError("Versions database ID not found in workspace config")

        return await Version.create(
            client=self._client,
            database_id=database_id,
            name=name,
            project_id=project_id,
            status=status,
            version_type=version_type,
            branch_name=branch_name,
            progress=progress,
        )

    def _get_database_id(self, name: str) -> str | None:
        """Get database ID from workspace config."""
        return getattr(self._client, "_workspace_config", {}).get(name)


class TaskManager:
    """
    Manager for Task entities.

    Provides task discovery and workflow management methods.

    Example:
        >>> manager = client.plugin_manager("tasks")
        >>> tasks = await manager.list()
        >>> task = await manager.next()
        >>> await task.claim()
    """

    def __init__(self, client: "NotionClient") -> None:
        """Initialize task manager."""
        self._client = client

    async def list(
        self,
        version_id: str | None = None,
        status: str | None = None,
    ) -> list:
        """
        List all tasks, optionally filtered.

        Args:
            version_id: Filter by version ID (optional)
            status: Filter by status (optional)

        Returns:
            List of Task instances
        """
        from better_notion.plugins.official.agents_sdk.models import Task

        database_id = self._get_database_id("Tasks")
        if not database_id:
            return []

        # Build filter
        filters: list[dict[str, Any]] = []

        if version_id:
            filters.append({
                "property": "Version",
                "relation": {"contains": version_id},
            })

        if status:
            filters.append({
                "property": "Status",
                "select": {"equals": status},
            })

        # Query pages
        response = await self._client._api.databases.query(
            database_id=database_id,
            filter={"and": filters} if len(filters) > 1 else (filters[0] if filters else None),
        )

        return [
            Task(self._client, page_data)
            for page_data in response.get("results", [])
        ]

    async def get(self, task_id: str) -> Any:
        """Get a task by ID."""
        from better_notion.plugins.official.agents_sdk.models import Task

        return await Task.get(task_id, client=self._client)

    async def create(
        self,
        title: str,
        version_id: str,
        status: str = "Backlog",
        task_type: str = "New Feature",
        priority: str = "Medium",
        dependency_ids: list[str] | None = None,
        estimated_hours: int | None = None,
    ) -> Any:
        """Create a new task."""
        from better_notion.plugins.official.agents_sdk.models import Task

        database_id = self._get_database_id("Tasks")
        if not database_id:
            raise ValueError("Tasks database ID not found in workspace config")

        return await Task.create(
            client=self._client,
            database_id=database_id,
            title=title,
            version_id=version_id,
            status=status,
            task_type=task_type,
            priority=priority,
            dependency_ids=dependency_ids,
            estimated_hours=estimated_hours,
        )

    async def next(self, project_id: str | None = None) -> Any | None:
        """
        Find the next available task to work on.

        Tasks are considered available if:
        - Status is Backlog or Claimed
        - All dependencies are completed

        Args:
            project_id: Filter by project ID (optional)

        Returns:
            Task instance or None if no tasks available
        """
        from better_notion.plugins.official.agents_sdk.models import Task

        database_id = self._get_database_id("Tasks")
        if not database_id:
            return None

        # Filter for backlog/claimed tasks
        response = await self._client._api.databases.query(
            database_id=database_id,
            filter={
                "or": [
                    {"property": "Status", "select": {"equals": "Backlog"}},
                    {"property": "Status", "select": {"equals": "Claimed"}},
                ]
            },
        )

        # Check each task for completed dependencies
        for page_data in response.get("results", []):
            task = Task(self._client, page_data)

            # Filter by project if specified
            if project_id:
                version = await task.version()
                if version:
                    project = await version.project()
                    if project and project.id != project_id:
                        continue

            # Check if can start
            if await task.can_start():
                return task

        return None

    async def find_ready(self, version_id: str | None = None) -> list:
        """
        Find all tasks that are ready to start (dependencies completed).

        Args:
            version_id: Filter by version ID (optional)

        Returns:
            List of Task instances ready to start
        """
        ready_tasks = []

        database_id = self._get_database_id("Tasks")
        if not database_id:
            return ready_tasks

        # Get all backlog/claimed tasks
        tasks = await self.list(status=None)

        for task in tasks:
            # Filter by version if specified
            if version_id and task.version_id != version_id:
                continue

            # Check status and dependencies
            if task.status in ("Backlog", "Claimed") and await task.can_start():
                ready_tasks.append(task)

        return ready_tasks

    async def find_blocked(self, version_id: str | None = None) -> list:
        """
        Find all tasks that are blocked by incomplete dependencies.

        Args:
            version_id: Filter by version ID (optional)

        Returns:
            List of Task instances that are blocked
        """
        blocked_tasks = []

        database_id = self._get_database_id("Tasks")
        if not database_id:
            return blocked_tasks

        # Get all backlog/claimed/in-progress tasks
        tasks = await self.list(status=None)

        for task in tasks:
            # Filter by version if specified
            if version_id and task.version_id != version_id:
                continue

            # Check status and dependencies
            if task.status in ("Backlog", "Claimed", "In Progress"):
                if not await task.can_start():
                    blocked_tasks.append(task)

        return blocked_tasks

    def _get_database_id(self, name: str) -> str | None:
        """Get database ID from workspace config."""
        return getattr(self._client, "_workspace_config", {}).get(name)
