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

        Raises:
            ValueError: If project_id is provided but project doesn't exist
        """
        from better_notion.plugins.official.agents_sdk.models import Task, Project

        database_id = self._get_database_id("Tasks")
        if not database_id:
            return None

        # Validate project_id if provided
        if project_id:
            # First check if Projects database exists in workspace config
            projects_db = self._get_database_id("Projects")
            if not projects_db:
                # Workspace not initialized, can't validate project
                pass
            else:
                # Check if project exists by querying for it
                try:
                    project_response = await self._client._api.databases.query(
                        database_id=projects_db,
                        filter={"property": "id", "rich_text": {"equals": project_id}}
                    )
                    # If no results, project doesn't exist
                    if not project_response.get("results"):
                        raise ValueError(
                            f"Project '{project_id}' not found. "
                            f"Please verify the project ID or run 'notion agents projects list' to see available projects."
                        )
                except Exception as e:
                    if "not found" in str(e).lower():
                        raise
                    # If query fails for other reasons, continue without validation

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


class IdeaManager:
    """
    Manager for Idea entities.

    Provides convenience methods for working with Ideas,
    including filtering by project, category, and status.
    """

    def __init__(self, client: "NotionClient") -> None:
        """Initialize manager with NotionClient instance."""
        self._client = client

    async def list(
        self,
        project_id: str | None = None,
        category: str | None = None,
        status: str | None = None,
        effort_estimate: str | None = None,
    ) -> list:
        """
        List Ideas with optional filtering.

        Args:
            project_id: Filter by project ID
            category: Filter by category (enhancement, feature, bugfix, optimization, research)
            status: Filter by status
            effort_estimate: Filter by effort estimate

        Returns:
            List of Idea instances
        """
        from better_notion.plugins.official.agents_sdk.models import Idea

        database_id = self._get_database_id("Ideas")
        if not database_id:
            return []

        # Build filters
        filters = []

        if project_id:
            filters.append({
                "property": "project_id",
                "relation": {"contains": project_id}
            })

        if category:
            filters.append({
                "property": "category",
                "select": {"equals": category}
            })

        if status:
            filters.append({
                "property": "status",
                "select": {"equals": status}
            })

        if effort_estimate:
            filters.append({
                "property": "effort_estimate",
                "select": {"equals": effort_estimate}
            })

        # Query database
        query = {}
        if filters:
            if len(filters) == 1:
                query["filter"] = filters[0]
            else:
                query["filter"] = {
                    "and": filters
                }

        response = await self._client._api.request(
            method="POST",
            path=f"databases/{database_id}/query",
            json=query,
        )

        # Create Idea instances
        ideas = []
        for page_data in response.get("results", []):
            idea = Idea(data=page_data, client=self._client, cache=self._client._plugin_caches.get("ideas"))
            ideas.append(idea)

        return ideas

    async def review_batch(self, count: int = 10) -> list:
        """
        Get a batch of ideas for review, prioritized by effort.

        Args:
            count: Maximum number of ideas to return

        Returns:
            List of Idea instances ready for review
        """
        ideas = await self.list(status="Proposed")

        # Sort by effort (XS < S < M < L < XL)
        effort_order = {"XS": 0, "S": 1, "M": 2, "L": 3, "XL": 4}
        ideas.sort(key=lambda i: effort_order.get(i.effort_estimate or "M", 2))

        return ideas[:count]

    async def get_accepted_without_tasks(self) -> list:
        """
        Get all accepted ideas that don't have related tasks yet.

        Returns:
            List of Idea instances that should have tasks created
        """
        ideas = await self.list(status="Accepted")
        return [idea for idea in ideas if not idea.related_task_id]

    def _get_database_id(self, name: str) -> str | None:
        """Get database ID from workspace config."""
        return getattr(self._client, "_workspace_config", {}).get(name)


class WorkIssueManager:
    """
    Manager for Work Issue entities.

    Provides convenience methods for working with work issues,
    including finding blockers and creating from exceptions.
    """

    def __init__(self, client: "NotionClient") -> None:
        """Initialize manager with NotionClient instance."""
        self._client = client

    async def list(
        self,
        project_id: str | None = None,
        task_id: str | None = None,
        type_: str | None = None,
        severity: str | None = None,
        status: str | None = None,
    ) -> list:
        """
        List Work Issues with optional filtering.

        Args:
            project_id: Filter by project ID
            task_id: Filter by task ID
            type_: Filter by type
            severity: Filter by severity
            status: Filter by status

        Returns:
            List of WorkIssue instances
        """
        from better_notion.plugins.official.agents_sdk.models import WorkIssue

        database_id = self._get_database_id("Work Issues")
        if not database_id:
            return []

        # Build filters
        filters = []

        if project_id:
            filters.append({
                "property": "project_id",
                "relation": {"contains": project_id}
            })

        if task_id:
            filters.append({
                "property": "task_id",
                "relation": {"contains": task_id}
            })

        if type_:
            filters.append({
                "property": "type",
                "select": {"equals": type_}
            })

        if severity:
            filters.append({
                "property": "severity",
                "select": {"equals": severity}
            })

        if status:
            filters.append({
                "property": "status",
                "select": {"equals": status}
            })

        # Query database
        query = {}
        if filters:
            if len(filters) == 1:
                query["filter"] = filters[0]
            else:
                query["filter"] = {
                    "and": filters
                }

        response = await self._client._api.request(
            method="POST",
            path=f"databases/{database_id}/query",
            json=query,
        )

        # Create WorkIssue instances
        issues = []
        for page_data in response.get("results", []):
            issue = WorkIssue(data=page_data, client=self._client, cache=self._client._plugin_caches.get("work_issues"))
            issues.append(issue)

        return issues

    async def find_blockers(self, project_id: str) -> list:
        """
        Find all open work issues that are blocking development.

        Args:
            project_id: Project ID to search within

        Returns:
            List of WorkIssue instances with High/Critical severity
        """
        issues = await self.list(
            project_id=project_id,
            status="Open"
        )

        return [issue for issue in issues if issue.severity in ("High", "Critical")]

    async def create_from_exception(
        self,
        title: str,
        exception: Exception,
        project_id: str,
        task_id: str | None = None,
        context: str | None = None,
    ) -> "WorkIssue":
        """
        Create a work issue from an exception.

        Args:
            title: Issue title
            exception: Exception object
            project_id: Project ID
            task_id: Related task ID (optional)
            context: Additional context

        Returns:
            Created WorkIssue instance
        """
        from better_notion.plugins.official.agents_sdk.models import WorkIssue

        database_id = self._get_database_id("Work Issues")
        if not database_id:
            raise ValueError("Work Issues database not configured")

        # Create issue in Notion
        properties = {
            "title": {"title": [{"text": {"content": title}}]},
            "project_id": {"relation": [{"id": project_id}]},
            "type": {"select": {"name": "Technical"}},
            "severity": {"select": {"name": "Medium"}},
            "status": {"select": {"name": "Open"}},
            "description": {
                "rich_text": [{
                    "text": {
                        "content": f"Exception: {type(exception).__name__}: {str(exception)}"
                    }
                }]
            },
        }

        if task_id:
            properties["task_id"] = {"relation": [{"id": task_id}]}

        if context:
            properties["context"] = {
                "rich_text": [{"text": {"content": context}}]
            }

        response = await self._client._api.request(
            method="POST",
            path=f"databases/{database_id}",
            json={"properties": properties},
        )

        # Create WorkIssue instance
        issue = WorkIssue(
            data=response,
            client=self._client,
            cache=self._client._plugin_caches.get("work_issues"),
        )

        return issue

    def _get_database_id(self, name: str) -> str | None:
        """Get database ID from workspace config."""
        return getattr(self._client, "_workspace_config", {}).get(name)


class IncidentManager:
    """
    Manager for Incident entities.

    Provides convenience methods for working with incidents,
    including finding SLA violations and calculating MTTR.
    """

    def __init__(self, client: "NotionClient") -> None:
        """Initialize manager with NotionClient instance."""
        self._client = client

    async def list(
        self,
        project_id: str | None = None,
        version_id: str | None = None,
        severity: str | None = None,
        status: str | None = None,
    ) -> list:
        """
        List Incidents with optional filtering.

        Args:
            project_id: Filter by project ID
            version_id: Filter by affected version ID
            severity: Filter by severity
            status: Filter by status

        Returns:
            List of Incident instances
        """
        from better_notion.plugins.official.agents_sdk.models import Incident

        database_id = self._get_database_id("Incidents")
        if not database_id:
            return []

        # Build filters
        filters = []

        if project_id:
            filters.append({
                "property": "project_id",
                "relation": {"contains": project_id}
            })

        if version_id:
            filters.append({
                "property": "affected_version_id",
                "relation": {"contains": version_id}
            })

        if severity:
            filters.append({
                "property": "severity",
                "select": {"equals": severity}
            })

        if status:
            filters.append({
                "property": "status",
                "select": {"equals": status}
            })

        # Query database
        query = {}
        if filters:
            if len(filters) == 1:
                query["filter"] = filters[0]
            else:
                query["filter"] = {
                    "and": filters
                }

        response = await self._client._api.request(
            method="POST",
            path=f"databases/{database_id}/query",
            json=query,
        )

        # Create Incident instances
        incidents = []
        for page_data in response.get("results", []):
            incident = Incident(data=page_data, client=self._client, cache=self._client._plugin_caches.get("incidents"))
            incidents.append(incident)

        return incidents

    async def find_sla_violations(self) -> list:
        """
        Find all incidents that violated SLA.

        SLA: Critical incidents should be resolved within 4 hours.

        Returns:
            List of Incident instances with SLA violations
        """
        from datetime import timedelta

        incidents = await self.list()

        violations = []
        for incident in incidents:
            if incident.severity == "Critical" and incident.resolved_date:
                # SLA: 4 hours for Critical
                sla_hours = 4
                sla_duration = timedelta(hours=sla_hours)

                if incident.discovery_date:
                    resolution_time = incident.resolved_date - incident.discovery_date
                    if resolution_time > sla_duration:
                        violations.append(incident)

        return violations

    async def calculate_mttr(
        self, project_id: str | None = None, within_days: int = 30
    ) -> dict[str, float]:
        """
        Calculate Mean Time To Resolve (MTTR) for incidents.

        Args:
            project_id: Filter by project ID (optional)
            within_days: Only consider incidents from last N days

        Returns:
            Dictionary mapping severity to MTTR in hours
        """
        from datetime import datetime, timedelta, timezone

        cutoff_date = datetime.now(timezone.utc) - timedelta(days=within_days)
        incidents = await self.list(project_id=project_id)

        # Filter by date and resolved status
        resolved_incidents = [
            i for i in incidents
            if i.status == "Resolved"
            and i.discovery_date
            and i.resolved_date
            and i.discovery_date >= cutoff_date
        ]

        # Group by severity
        by_severity = {}
        for incident in resolved_incidents:
            severity = incident.severity or "Unknown"
            if severity not in by_severity:
                by_severity[severity] = []

            # Calculate resolution time in hours
            resolution_time = incident.resolved_date - incident.discovery_date
            hours = resolution_time.total_seconds() / 3600
            by_severity[severity].append(hours)

        # Calculate averages
        mttr = {}
        for severity, times in by_severity.items():
            mttr[severity] = sum(times) / len(times) if times else 0.0

        return mttr

    def _get_database_id(self, name: str) -> str | None:
        """Get database ID from workspace config."""
        return getattr(self._client, "_workspace_config", {}).get(name)
