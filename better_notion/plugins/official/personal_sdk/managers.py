"""Managers for personal entities.

These managers provide convenience methods for working with personal
entities through the client.plugin_manager() interface.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from better_notion._sdk.client import NotionClient


class DomainManager:
    """
    Manager for Domain entities.

    Provides convenience methods for working with domains.

    Example:
        >>> manager = client.plugin_manager("domains")
        >>> domains = await manager.list()
        >>> domain = await manager.get("domain_id")
    """

    def __init__(self, client: "NotionClient") -> None:
        """Initialize domain manager.

        Args:
            client: NotionClient instance
        """
        self._client = client

    async def list(self) -> list:
        """
        List all domains.

        Returns:
            List of Domain instances
        """
        from better_notion.plugins.official.personal_sdk.models import Domain

        database_id = self._get_database_id("domains")
        if not database_id:
            return []

        response = await self._client._api.databases.query(database_id=database_id)

        return [
            Domain(self._client, page_data)
            for page_data in response.get("results", [])
        ]

    async def get(self, domain_id: str) -> Any:
        """
        Get a domain by ID.

        Args:
            domain_id: Domain page ID

        Returns:
            Domain instance
        """
        from better_notion.plugins.official.personal_sdk.models import Domain

        return await Domain.get(domain_id, client=self._client)

    async def create(
        self,
        name: str,
        description: str = "",
        color: str = "Blue",
    ) -> Any:
        """
        Create a new domain.

        Args:
            name: Domain name
            description: Domain description
            color: Domain color

        Returns:
            Created Domain instance
        """
        from better_notion.plugins.official.personal_sdk.models import Domain

        database_id = self._get_database_id("domains")
        if not database_id:
            raise ValueError("Domains database ID not found in workspace config")

        return await Domain.create(
            client=self._client,
            database_id=database_id,
            name=name,
            description=description,
            color=color,
        )

    def _get_database_id(self, name: str) -> str | None:
        """Get database ID from workspace config."""
        return getattr(self._client, "_personal_workspace_config", {}).get("database_ids", {}).get(name)


class TagManager:
    """
    Manager for Tag entities.

    Example:
        >>> manager = client.plugin_manager("tags")
        >>> tags = await manager.list()
        >>> tag = await manager.get("tag_id")
    """

    def __init__(self, client: "NotionClient") -> None:
        """Initialize tag manager."""
        self._client = client

    async def list(self, category: str | None = None) -> list:
        """
        List all tags, optionally filtered by category.

        Args:
            category: Filter by category (optional)

        Returns:
            List of Tag instances
        """
        from better_notion.plugins.official.personal_sdk.models import Tag

        database_id = self._get_database_id("tags")
        if not database_id:
            return []

        # Build filter if category provided
        filter_dict = None
        if category:
            filter_dict = {
                "property": "Category",
                "select": {"equals": category},
            }

        response = await self._client._api.databases.query(
            database_id=database_id,
            filter=filter_dict,
        )

        return [
            Tag(self._client, page_data)
            for page_data in response.get("results", [])
        ]

    async def get(self, tag_id: str) -> Any:
        """Get a tag by ID."""
        from better_notion.plugins.official.personal_sdk.models import Tag

        return await Tag.get(tag_id, client=self._client)

    async def create(
        self,
        name: str,
        color: str = "Gray",
        category: str = "Custom",
        description: str = "",
    ) -> Any:
        """Create a new tag."""
        from better_notion.plugins.official.personal_sdk.models import Tag

        database_id = self._get_database_id("tags")
        if not database_id:
            raise ValueError("Tags database ID not found in workspace config")

        return await Tag.create(
            client=self._client,
            database_id=database_id,
            name=name,
            color=color,
            category=category,
            description=description,
        )

    async def find_by_name(self, name: str) -> Any | None:
        """Find a tag by name."""
        tags = await self.list()
        for tag in tags:
            if tag.name == name:
                return tag
        return None

    def _get_database_id(self, name: str) -> str | None:
        """Get database ID from workspace config."""
        return getattr(self._client, "_personal_workspace_config", {}).get("database_ids", {}).get(name)


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

    async def list(self, domain_id: str | None = None) -> list:
        """
        List all projects, optionally filtered by domain.

        Args:
            domain_id: Filter by domain ID (optional)

        Returns:
            List of Project instances
        """
        from better_notion.plugins.official.personal_sdk.models import Project

        database_id = self._get_database_id("projects")
        if not database_id:
            return []

        # Build filter if domain_id provided
        filter_dict = None
        if domain_id:
            filter_dict = {
                "property": "Domain",
                "relation": {"contains": domain_id},
            }

        response = await self._client._api.databases.query(
            database_id=database_id,
            filter=filter_dict,
        )

        return [
            Project(self._client, page_data)
            for page_data in response.get("results", [])
        ]

    async def get(self, project_id: str) -> Any:
        """Get a project by ID."""
        from better_notion.plugins.official.personal_sdk.models import Project

        return await Project.get(project_id, client=self._client)

    async def create(
        self,
        name: str,
        status: str = "Active",
        domain_id: str | None = None,
        deadline: str | None = None,
        priority: str = "Medium",
        progress: int = 0,
        goal: str = "",
        notes: str = "",
    ) -> Any:
        """Create a new project."""
        from better_notion.plugins.official.personal_sdk.models import Project

        database_id = self._get_database_id("projects")
        if not database_id:
            raise ValueError("Projects database ID not found in workspace config")

        return await Project.create(
            client=self._client,
            database_id=database_id,
            name=name,
            status=status,
            domain_id=domain_id,
            deadline=deadline,
            priority=priority,
            progress=progress,
            goal=goal,
            notes=notes,
        )

    def _get_database_id(self, name: str) -> str | None:
        """Get database ID from workspace config."""
        return getattr(self._client, "_personal_workspace_config", {}).get("database_ids", {}).get(name)


class TaskManager:
    """
    Manager for Task entities.

    Example:
        >>> manager = client.plugin_manager("tasks")
        >>> tasks = await manager.list()
        >>> task = await manager.get("task_id")
    """

    def __init__(self, client: "NotionClient") -> None:
        """Initialize task manager."""
        self._client = client

    async def list(
        self,
        status: str | None = None,
        domain_id: str | None = None,
        project_id: str | None = None,
        parent_task_id: str | None = None,
        tag_ids: list[str] | None = None,
    ) -> list:
        """
        List all tasks with optional filters.

        Args:
            status: Filter by status (optional)
            domain_id: Filter by domain ID (optional)
            project_id: Filter by project ID (optional)
            parent_task_id: Filter by parent task ID (optional)
            tag_ids: Filter by tag IDs (optional)

        Returns:
            List of Task instances
        """
        from better_notion.plugins.official.personal_sdk.models import Task

        database_id = self._get_database_id("tasks")
        if not database_id:
            return []

        # Build filters
        filters = []
        if status:
            filters.append({
                "property": "Status",
                "select": {"equals": status},
            })
        if domain_id:
            filters.append({
                "property": "Domain",
                "relation": {"contains": domain_id},
            })
        if project_id:
            filters.append({
                "property": "Project",
                "relation": {"contains": project_id},
            })
        if parent_task_id:
            filters.append({
                "property": "Parent Task",
                "relation": {"contains": parent_task_id},
            })
        if tag_ids:
            filters.append({
                "property": "Tags",
                "relation": {"contains": tag_ids[0]},  # Notion API limitation
            })

        filter_dict = {"and": filters} if len(filters) > 1 else (filters[0] if filters else None)

        response = await self._client._api.databases.query(
            database_id=database_id,
            filter=filter_dict,
        )

        return [
            Task(self._client, page_data)
            for page_data in response.get("results", [])
        ]

    async def get(self, task_id: str) -> Any:
        """Get a task by ID."""
        from better_notion.plugins.official.personal_sdk.models import Task

        return await Task.get(task_id, client=self._client)

    async def create(
        self,
        title: str,
        status: str = "Todo",
        priority: str = "Medium",
        due_date: str | None = None,
        domain_id: str | None = None,
        project_id: str | None = None,
        parent_task_id: str | None = None,
        tag_ids: list[str] | None = None,
        estimated_time: int | None = None,
        energy_required: str | None = None,
        context: str = "",
    ) -> Any:
        """Create a new task."""
        from better_notion.plugins.official.personal_sdk.models import Task

        database_id = self._get_database_id("tasks")
        if not database_id:
            raise ValueError("Tasks database ID not found in workspace config")

        return await Task.create(
            client=self._client,
            database_id=database_id,
            title=title,
            status=status,
            priority=priority,
            due_date=due_date,
            domain_id=domain_id,
            project_id=project_id,
            parent_task_id=parent_task_id,
            tag_ids=tag_ids,
            estimated_time=estimated_time,
            energy_required=energy_required,
            context=context,
        )

    def _get_database_id(self, name: str) -> str | None:
        """Get database ID from workspace config."""
        return getattr(self._client, "_personal_workspace_config", {}).get("database_ids", {}).get(name)


class RoutineManager:
    """
    Manager for Routine entities.

    Example:
        >>> manager = client.plugin_manager("routines")
        >>> routines = await manager.list()
        >>> routine = await manager.get("routine_id")
    """

    def __init__(self, client: "NotionClient") -> None:
        """Initialize routine manager."""
        self._client = client

    async def list(self, domain_id: str | None = None) -> list:
        """
        List all routines, optionally filtered by domain.

        Args:
            domain_id: Filter by domain ID (optional)

        Returns:
            List of Routine instances
        """
        from better_notion.plugins.official.personal_sdk.models import Routine

        database_id = self._get_database_id("routines")
        if not database_id:
            return []

        filter_dict = None
        if domain_id:
            filter_dict = {
                "property": "Domain",
                "relation": {"contains": domain_id},
            }

        response = await self._client._api.databases.query(
            database_id=database_id,
            filter=filter_dict,
        )

        return [
            Routine(self._client, page_data)
            for page_data in response.get("results", [])
        ]

    async def get(self, routine_id: str) -> Any:
        """Get a routine by ID."""
        from better_notion.plugins.official.personal_sdk.models import Routine

        return await Routine.get(routine_id, client=self._client)

    async def create(
        self,
        name: str,
        frequency: str = "Daily",
        domain_id: str | None = None,
        best_time: str = "Anytime",
        estimated_duration: int = 30,
    ) -> Any:
        """Create a new routine."""
        from better_notion.plugins.official.personal_sdk.models import Routine

        database_id = self._get_database_id("routines")
        if not database_id:
            raise ValueError("Routines database ID not found in workspace config")

        return await Routine.create(
            client=self._client,
            database_id=database_id,
            name=name,
            frequency=frequency,
            domain_id=domain_id,
            best_time=best_time,
            estimated_duration=estimated_duration,
        )

    def _get_database_id(self, name: str) -> str | None:
        """Get database ID from workspace config."""
        return getattr(self._client, "_personal_workspace_config", {}).get("database_ids", {}).get(name)
