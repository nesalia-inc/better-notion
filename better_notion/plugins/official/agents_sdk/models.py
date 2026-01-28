"""Workflow entity models for the agents SDK plugin.

This module provides SDK model classes for workflow entities:
- Organization
- Project
- Version
- Task

These models inherit from BaseEntity and provide autonomous CRUD operations
with caching support through the plugin system.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from better_notion._sdk.base.entity import BaseEntity

if TYPE_CHECKING:
    from better_notion._sdk.client import NotionClient


class Organization(BaseEntity):
    """
    Organization entity representing a company or team.

    An organization contains multiple projects and serves as the top-level
    grouping in the workflow hierarchy.

    Attributes:
        id: Organization page ID
        name: Organization name
        slug: URL-safe identifier
        description: Organization purpose
        repository_url: Code repository URL
        status: Organization status (Active, Archived, On Hold)

    Example:
        >>> org = await Organization.get("org_id", client=client)
        >>> print(org.name)
        >>> projects = await org.projects()
    """

    def __init__(self, client: "NotionClient", data: dict[str, Any]) -> None:
        """Initialize organization with client and API data.

        Args:
            client: NotionClient instance
            data: Raw API response data
        """
        super().__init__(client, data)
        self._organization_cache = client.plugin_cache("organizations")

    # ===== PROPERTIES =====

    @property
    def name(self) -> str:
        """Get organization name from title property.

        Returns:
            Organization name as string
        """
        title_prop = self._data["properties"].get("Name") or self._data["properties"].get("name")
        if title_prop and title_prop.get("type") == "title":
            title_data = title_prop.get("title", [])
            if title_data:
                return title_data[0].get("plain_text", "")
        return ""

    @property
    def slug(self) -> str:
        """Get organization slug (URL-safe identifier).

        Returns:
            Slug string or empty string if not set
        """
        slug_prop = self._data["properties"].get("Slug") or self._data["properties"].get("slug")
        if slug_prop and slug_prop.get("type") == "rich_text":
            text_data = slug_prop.get("rich_text", [])
            if text_data:
                return text_data[0].get("plain_text", "")
        return ""

    @property
    def description(self) -> str:
        """Get organization description.

        Returns:
            Description string
        """
        desc_prop = self._data["properties"].get("Description") or self._data["properties"].get("description")
        if desc_prop and desc_prop.get("type") == "rich_text":
            text_data = desc_prop.get("rich_text", [])
            if text_data:
                return text_data[0].get("plain_text", "")
        return ""

    @property
    def repository_url(self) -> str | None:
        """Get repository URL.

        Returns:
            Repository URL string or None
        """
        repo_prop = self._data["properties"].get("Repository URL") or self._data["properties"].get("repository_url")
        if repo_prop and repo_prop.get("type") == "url":
            return repo_prop.get("url")
        return None

    @property
    def status(self) -> str:
        """Get organization status.

        Returns:
            Status string (Active, Archived, On Hold)
        """
        status_prop = self._data["properties"].get("Status") or self._data["properties"].get("status")
        if status_prop and status_prop.get("type") == "select":
            select_data = status_prop.get("select")
            if select_data:
                return select_data.get("name", "Unknown")
        return "Unknown"

    # ===== AUTONOMOUS METHODS =====

    @classmethod
    async def get(cls, org_id: str, *, client: "NotionClient") -> "Organization":
        """
        Get an organization by ID.

        Args:
            org_id: Organization page ID
            client: NotionClient instance

        Returns:
            Organization instance

        Raises:
            Exception: If API call fails

        Example:
            >>> org = await Organization.get("org_123", client=client)
        """
        # Check plugin cache
        cache = client.plugin_cache("organizations")
        if cache and org_id in cache:
            return cache[org_id]

        # Fetch from API
        data = await client._api.pages.get(page_id=org_id)
        org = cls(client, data)

        # Cache it
        if cache:
            cache[org_id] = org

        return org

    @classmethod
    async def create(
        cls,
        *,
        client: "NotionClient",
        database_id: str,
        name: str,
        slug: str | None = None,
        description: str | None = None,
        repository_url: str | None = None,
        status: str = "Active",
    ) -> "Organization":
        """
        Create a new organization.

        Args:
            client: NotionClient instance
            database_id: Organizations database ID
            name: Organization name
            slug: URL-safe identifier (defaults to name if not provided)
            description: Organization description
            repository_url: Code repository URL
            status: Organization status (default: Active)

        Returns:
            Created Organization instance

        Raises:
            Exception: If API call fails

        Example:
            >>> org = await Organization.create(
            ...     client=client,
            ...     database_id="db_123",
            ...     name="My Organization",
            ...     slug="my-org",
            ...     description="A great organization"
            ... )
        """
        from better_notion._api.properties import Title, RichText, URL, Select

        # Build properties
        properties: dict[str, Any] = {
            "Name": Title(name),
        }

        if slug:
            properties["Slug"] = RichText(slug)
        if description:
            properties["Description"] = RichText(description)
        if repository_url:
            properties["Repository URL"] = URL(repository_url)
        if status:
            properties["Status"] = Select(status)

        # Create page
        data = await client._api.pages.create(
            parent={"database_id": database_id},
            properties=properties,
        )

        org = cls(client, data)

        # Cache it
        cache = client.plugin_cache("organizations")
        if cache:
            cache[org.id] = org

        return org

    async def update(
        self,
        *,
        name: str | None = None,
        slug: str | None = None,
        description: str | None = None,
        repository_url: str | None = None,
        status: str | None = None,
    ) -> "Organization":
        """
        Update organization properties.

        Args:
            name: New name
            slug: New slug
            description: New description
            repository_url: New repository URL
            status: New status

        Returns:
            Updated Organization instance

        Example:
            >>> org = await org.update(status="Archived")
        """
        from better_notion._api.properties import Title, RichText, URL, Select

        # Build properties to update
        properties: dict[str, Any] = {}

        if name is not None:
            properties["Name"] = Title(name)
        if slug is not None:
            properties["Slug"] = RichText(slug)
        if description is not None:
            properties["Description"] = RichText(description)
        if repository_url is not None:
            properties["Repository URL"] = URL(repository_url)
        if status is not None:
            properties["Status"] = Select(status)

        # Update page
        data = await self._client._api.pages.update(
            page_id=self.id,
            properties=properties,
        )

        # Update instance
        self._data = data

        # Invalidate cache
        cache = self._client.plugin_cache("organizations")
        if cache and self.id in cache:
            del cache[self.id]

        return self

    async def delete(self) -> None:
        """
        Delete the organization.

        Example:
            >>> await org.delete()
        """
        await self._client._api.pages.delete(page_id=self.id)

        # Invalidate cache
        cache = self._client.plugin_cache("organizations")
        if cache and self.id in cache:
            del cache[self.id]

    async def projects(self) -> list["Project"]:
        """
        Get all projects in this organization.

        Returns:
            List of Project instances

        Example:
            >>> projects = await org.projects()
        """
        # Get database ID from workspace config
        import json
        from pathlib import Path

        config_path = Path.home() / ".notion" / "workspace.json"
        if not config_path.exists():
            return []

        config = json.loads(config_path.read_text())
        projects_db_id = config.get("Projects")

        if not projects_db_id:
            return []

        # Query projects with relation filter
        from better_notion._api.properties import Relation

        response = await self._client._api.databases.query(
            database_id=projects_db_id,
            filter={
                "property": "Organization",
                "relation": {"contains": self.id},
            },
        )

        from better_notion.plugins.official.agents_sdk.models import Project
        return [Project(self._client, page_data) for page_data in response.get("results", [])]


class Project(BaseEntity):
    """
    Project entity representing a software project.

    A project belongs to an organization and contains multiple versions.

    Attributes:
        id: Project page ID
        name: Project name
        slug: URL-safe identifier
        description: Project description
        repository: Git repository URL
        status: Project status (Active, Archived, Planning, Completed)
        tech_stack: List of technologies used
        role: Project role (Developer, PM, QA, etc.)
        organization: Parent organization

    Example:
        >>> project = await Project.get("project_id", client=client)
        >>> print(project.name)
        >>> versions = await project.versions()
    """

    def __init__(self, client: "NotionClient", data: dict[str, Any]) -> None:
        """Initialize project with client and API data.

        Args:
            client: NotionClient instance
            data: Raw API response data
        """
        super().__init__(client, data)
        self._project_cache = client.plugin_cache("projects")

    # ===== PROPERTIES =====

    @property
    def name(self) -> str:
        """Get project name from title property."""
        title_prop = self._data["properties"].get("Name") or self._data["properties"].get("name")
        if title_prop and title_prop.get("type") == "title":
            title_data = title_prop.get("title", [])
            if title_data:
                return title_data[0].get("plain_text", "")
        return ""

    @property
    def slug(self) -> str:
        """Get project slug."""
        slug_prop = self._data["properties"].get("Slug") or self._data["properties"].get("slug")
        if slug_prop and slug_prop.get("type") == "rich_text":
            text_data = slug_prop.get("rich_text", [])
            if text_data:
                return text_data[0].get("plain_text", "")
        return ""

    @property
    def description(self) -> str:
        """Get project description."""
        desc_prop = self._data["properties"].get("Description") or self._data["properties"].get("description")
        if desc_prop and desc_prop.get("type") == "rich_text":
            text_data = desc_prop.get("rich_text", [])
            if text_data:
                return text_data[0].get("plain_text", "")
        return ""

    @property
    def repository(self) -> str | None:
        """Get repository URL."""
        repo_prop = self._data["properties"].get("Repository") or self._data["properties"].get("repository")
        if repo_prop and repo_prop.get("type") == "url":
            return repo_prop.get("url")
        return None

    @property
    def status(self) -> str:
        """Get project status."""
        status_prop = self._data["properties"].get("Status") or self._data["properties"].get("status")
        if status_prop and status_prop.get("type") == "select":
            select_data = status_prop.get("select")
            if select_data:
                return select_data.get("name", "Unknown")
        return "Unknown"

    @property
    def tech_stack(self) -> list[str]:
        """Get tech stack as list of strings."""
        tech_prop = self._data["properties"].get("Tech Stack") or self._data["properties"].get("tech_stack")
        if tech_prop and tech_prop.get("type") == "multi_select":
            multi_data = tech_prop.get("multi_select", [])
            return [item.get("name", "") for item in multi_data]
        return []

    @property
    def role(self) -> str:
        """Get project role."""
        role_prop = self._data["properties"].get("Role") or self._data["properties"].get("role")
        if role_prop and role_prop.get("type") == "select":
            select_data = role_prop.get("select")
            if select_data:
                return select_data.get("name", "Unknown")
        return "Unknown"

    @property
    def organization_id(self) -> str | None:
        """Get parent organization ID."""
        org_prop = self._data["properties"].get("Organization") or self._data["properties"].get("organization")
        if org_prop and org_prop.get("type") == "relation":
            relations = org_prop.get("relation", [])
            if relations:
                return relations[0].get("id")
        return None

    # ===== AUTONOMOUS METHODS =====

    @classmethod
    async def get(cls, project_id: str, *, client: "NotionClient") -> "Project":
        """Get a project by ID."""
        # Check plugin cache
        cache = client.plugin_cache("projects")
        if cache and project_id in cache:
            return cache[project_id]

        # Fetch from API
        data = await client._api.pages.get(page_id=project_id)
        project = cls(client, data)

        # Cache it
        if cache:
            cache[project_id] = project

        return project

    @classmethod
    async def create(
        cls,
        *,
        client: "NotionClient",
        database_id: str,
        name: str,
        organization_id: str,
        slug: str | None = None,
        description: str | None = None,
        repository: str | None = None,
        status: str = "Active",
        tech_stack: list[str] | None = None,
        role: str = "Developer",
    ) -> "Project":
        """Create a new project."""
        from better_notion._api.properties import Title, RichText, URL, Select, MultiSelect, Relation

        # Build properties
        properties: dict[str, Any] = {
            "Name": Title(name),
            "Organization": Relation([organization_id]),
            "Role": Select(role),
        }

        if slug:
            properties["Slug"] = RichText(slug)
        if description:
            properties["Description"] = RichText(description)
        if repository:
            properties["Repository"] = URL(repository)
        if status:
            properties["Status"] = Select(status)
        if tech_stack:
            properties["Tech Stack"] = MultiSelect(tech_stack)

        # Create page
        data = await client._api.pages.create(
            parent={"database_id": database_id},
            properties=properties,
        )

        project = cls(client, data)

        # Cache it
        cache = client.plugin_cache("projects")
        if cache:
            cache[project.id] = project

        return project

    async def update(
        self,
        *,
        name: str | None = None,
        slug: str | None = None,
        description: str | None = None,
        repository: str | None = None,
        status: str | None = None,
        tech_stack: list[str] | None = None,
        role: str | None = None,
    ) -> "Project":
        """Update project properties."""
        from better_notion._api.properties import Title, RichText, URL, Select, MultiSelect

        # Build properties to update
        properties: dict[str, Any] = {}

        if name is not None:
            properties["Name"] = Title(name)
        if slug is not None:
            properties["Slug"] = RichText(slug)
        if description is not None:
            properties["Description"] = RichText(description)
        if repository is not None:
            properties["Repository"] = URL(repository)
        if status is not None:
            properties["Status"] = Select(status)
        if tech_stack is not None:
            properties["Tech Stack"] = MultiSelect(tech_stack)
        if role is not None:
            properties["Role"] = Select(role)

        # Update page
        data = await self._client._api.pages.update(
            page_id=self.id,
            properties=properties,
        )

        # Update instance
        self._data = data

        # Invalidate cache
        cache = self._client.plugin_cache("projects")
        if cache and self.id in cache:
            del cache[self.id]

        return self

    async def delete(self) -> None:
        """Delete the project."""
        await self._client._api.pages.delete(page_id=self.id)

        # Invalidate cache
        cache = self._client.plugin_cache("projects")
        if cache and self.id in cache:
            del cache[self.id]

    async def organization(self) -> Organization | None:
        """Get parent organization."""
        if self.organization_id:
            return await Organization.get(self.organization_id, client=self._client)
        return None

    async def versions(self) -> list["Version"]:
        """Get all versions in this project."""
        # Get database ID from workspace config
        import json
        from pathlib import Path

        config_path = Path.home() / ".notion" / "workspace.json"
        if not config_path.exists():
            return []

        config = json.loads(config_path.read_text())
        versions_db_id = config.get("Versions")

        if not versions_db_id:
            return []

        # Query versions with relation filter
        response = await self._client._api.databases.query(
            database_id=versions_db_id,
            filter={
                "property": "Project",
                "relation": {"contains": self.id},
            },
        )

        return [Version(self._client, page_data) for page_data in response.get("results", [])]


class Version(BaseEntity):
    """
    Version entity representing a project version/release.

    A version belongs to a project and contains multiple tasks.

    Attributes:
        id: Version page ID
        name: Version name (e.g., "v1.0.0")
        project: Parent project
        status: Version status (Planning, Alpha, Beta, RC, In Progress, Released)
        type: Version type (Major, Minor, Patch, Hotfix)
        branch_name: Git branch name
        progress: Progress percentage (0-100)

    Example:
        >>> version = await Version.get("version_id", client=client)
        >>> print(version.name)
        >>> tasks = await version.tasks()
    """

    def __init__(self, client: "NotionClient", data: dict[str, Any]) -> None:
        """Initialize version with client and API data."""
        super().__init__(client, data)
        self._version_cache = client.plugin_cache("versions")

    # ===== PROPERTIES =====

    @property
    def name(self) -> str:
        """Get version name from title property."""
        title_prop = self._data["properties"].get("Version") or self._data["properties"].get("version")
        if title_prop and title_prop.get("type") == "title":
            title_data = title_prop.get("title", [])
            if title_data:
                return title_data[0].get("plain_text", "")
        return ""

    @property
    def status(self) -> str:
        """Get version status."""
        status_prop = self._data["properties"].get("Status") or self._data["properties"].get("status")
        if status_prop and status_prop.get("type") == "select":
            select_data = status_prop.get("select")
            if select_data:
                return select_data.get("name", "Unknown")
        return "Unknown"

    @property
    def version_type(self) -> str:
        """Get version type."""
        type_prop = self._data["properties"].get("Type") or self._data["properties"].get("type")
        if type_prop and type_prop.get("type") == "select":
            select_data = type_prop.get("select")
            if select_data:
                return select_data.get("name", "Unknown")
        return "Unknown"

    @property
    def branch_name(self) -> str:
        """Get git branch name."""
        branch_prop = self._data["properties"].get("Branch Name") or self._data["properties"].get("branch_name")
        if branch_prop and branch_prop.get("type") == "rich_text":
            text_data = branch_prop.get("rich_text", [])
            if text_data:
                return text_data[0].get("plain_text", "")
        return ""

    @property
    def progress(self) -> int:
        """Get progress percentage."""
        progress_prop = self._data["properties"].get("Progress") or self._data["properties"].get("progress")
        if progress_prop and progress_prop.get("type") == "number":
            return progress_prop.get("number", 0) or 0
        return 0

    @property
    def project_id(self) -> str | None:
        """Get parent project ID."""
        project_prop = self._data["properties"].get("Project") or self._data["properties"].get("project")
        if project_prop and project_prop.get("type") == "relation":
            relations = project_prop.get("relation", [])
            if relations:
                return relations[0].get("id")
        return None

    # ===== AUTONOMOUS METHODS =====

    @classmethod
    async def get(cls, version_id: str, *, client: "NotionClient") -> "Version":
        """Get a version by ID."""
        # Check plugin cache
        cache = client.plugin_cache("versions")
        if cache and version_id in cache:
            return cache[version_id]

        # Fetch from API
        data = await client._api.pages.get(page_id=version_id)
        version = cls(client, data)

        # Cache it
        if cache:
            cache[version_id] = version

        return version

    @classmethod
    async def create(
        cls,
        *,
        client: "NotionClient",
        database_id: str,
        name: str,
        project_id: str,
        status: str = "Planning",
        version_type: str = "Minor",
        branch_name: str | None = None,
        progress: int = 0,
    ) -> "Version":
        """Create a new version."""
        from better_notion._api.properties import Title, Select, RichText, Number, Relation

        # Build properties
        properties: dict[str, Any] = {
            "Version": Title(name),
            "Project": Relation([project_id]),
            "Status": Select(status),
            "Type": Select(version_type),
            "Progress": Number(progress),
        }

        if branch_name:
            properties["Branch Name"] = RichText(branch_name)

        # Create page
        data = await client._api.pages.create(
            parent={"database_id": database_id},
            properties=properties,
        )

        version = cls(client, data)

        # Cache it
        cache = client.plugin_cache("versions")
        if cache:
            cache[version.id] = version

        return version

    async def update(
        self,
        *,
        name: str | None = None,
        status: str | None = None,
        version_type: str | None = None,
        branch_name: str | None = None,
        progress: int | None = None,
    ) -> "Version":
        """Update version properties."""
        from better_notion._api.properties import Title, Select, RichText, Number

        # Build properties to update
        properties: dict[str, Any] = {}

        if name is not None:
            properties["Version"] = Title(name)
        if status is not None:
            properties["Status"] = Select(status)
        if version_type is not None:
            properties["Type"] = Select(version_type)
        if branch_name is not None:
            properties["Branch Name"] = RichText(branch_name)
        if progress is not None:
            properties["Progress"] = Number(progress)

        # Update page
        data = await self._client._api.pages.update(
            page_id=self.id,
            properties=properties,
        )

        # Update instance
        self._data = data

        # Invalidate cache
        cache = self._client.plugin_cache("versions")
        if cache and self.id in cache:
            del cache[self.id]

        return self

    async def delete(self) -> None:
        """Delete the version."""
        await self._client._api.pages.delete(page_id=self.id)

        # Invalidate cache
        cache = self._client.plugin_cache("versions")
        if cache and self.id in cache:
            del cache[self.id]

    async def project(self) -> Project | None:
        """Get parent project."""
        if self.project_id:
            return await Project.get(self.project_id, client=self._client)
        return None

    async def tasks(self) -> list["Task"]:
        """Get all tasks in this version."""
        # Get database ID from workspace config
        import json
        from pathlib import Path

        config_path = Path.home() / ".notion" / "workspace.json"
        if not config_path.exists():
            return []

        config = json.loads(config_path.read_text())
        tasks_db_id = config.get("Tasks")

        if not tasks_db_id:
            return []

        # Query tasks with relation filter
        response = await self._client._api.databases.query(
            database_id=tasks_db_id,
            filter={
                "property": "Version",
                "relation": {"contains": self.id},
            },
        )

        return [Task(self._client, page_data) for page_data in response.get("results", [])]


class Task(BaseEntity):
    """
    Task entity representing a work task.

    A task belongs to a version and can have dependencies on other tasks.

    Attributes:
        id: Task page ID
        title: Task title
        version: Parent version
        status: Task status (Backlog, Claimed, In Progress, In Review, Completed)
        type: Task type (New Feature, Refactor, Documentation, Test, Bug Fix)
        priority: Task priority (Critical, High, Medium, Low)
        dependencies: List of task IDs this task depends on
        estimated_hours: Estimated hours to complete
        actual_hours: Actual hours spent

    Example:
        >>> task = await Task.get("task_id", client=client)
        >>> await task.claim()
        >>> await task.start()
        >>> await task.complete()
    """

    def __init__(self, client: "NotionClient", data: dict[str, Any]) -> None:
        """Initialize task with client and API data."""
        super().__init__(client, data)
        self._task_cache = client.plugin_cache("tasks")

    # ===== PROPERTIES =====

    @property
    def title(self) -> str:
        """Get task title from title property."""
        title_prop = self._data["properties"].get("Title") or self._data["properties"].get("title")
        if title_prop and title_prop.get("type") == "title":
            title_data = title_prop.get("title", [])
            if title_data:
                return title_data[0].get("plain_text", "")
        return ""

    @property
    def status(self) -> str:
        """Get task status."""
        status_prop = self._data["properties"].get("Status") or self._data["properties"].get("status")
        if status_prop and status_prop.get("type") == "select":
            select_data = status_prop.get("select")
            if select_data:
                return select_data.get("name", "Unknown")
        return "Unknown"

    @property
    def task_type(self) -> str:
        """Get task type."""
        type_prop = self._data["properties"].get("Type") or self._data["properties"].get("type")
        if type_prop and type_prop.get("type") == "select":
            select_data = type_prop.get("select")
            if select_data:
                return select_data.get("name", "Unknown")
        return "Unknown"

    @property
    def priority(self) -> str:
        """Get task priority."""
        priority_prop = self._data["properties"].get("Priority") or self._data["properties"].get("priority")
        if priority_prop and priority_prop.get("type") == "select":
            select_data = priority_prop.get("select")
            if select_data:
                return select_data.get("name", "Unknown")
        return "Unknown"

    @property
    def version_id(self) -> str | None:
        """Get parent version ID."""
        version_prop = self._data["properties"].get("Version") or self._data["properties"].get("version")
        if version_prop and version_prop.get("type") == "relation":
            relations = version_prop.get("relation", [])
            if relations:
                return relations[0].get("id")
        return None

    @property
    def dependency_ids(self) -> list[str]:
        """Get list of task IDs this task depends on."""
        dep_prop = self._data["properties"].get("Dependencies") or self._data["properties"].get("dependencies")
        if dep_prop and dep_prop.get("type") == "relation":
            relations = dep_prop.get("relation", [])
            return [r.get("id", "") for r in relations if r.get("id")]
        return []

    @property
    def estimated_hours(self) -> int | None:
        """Get estimated hours."""
        hours_prop = self._data["properties"].get("Estimated Hours") or self._data["properties"].get("estimated_hours")
        if hours_prop and hours_prop.get("type") == "number":
            return hours_prop.get("number")
        return None

    @property
    def actual_hours(self) -> int | None:
        """Get actual hours spent."""
        hours_prop = self._data["properties"].get("Actual Hours") or self._data["properties"].get("actual_hours")
        if hours_prop and hours_prop.get("type") == "number":
            return hours_prop.get("number")
        return None

    # ===== AUTONOMOUS METHODS =====

    @classmethod
    async def get(cls, task_id: str, *, client: "NotionClient") -> "Task":
        """Get a task by ID."""
        # Check plugin cache
        cache = client.plugin_cache("tasks")
        if cache and task_id in cache:
            return cache[task_id]

        # Fetch from API
        data = await client._api.pages.get(page_id=task_id)
        task = cls(client, data)

        # Cache it
        if cache:
            cache[task_id] = task

        return task

    @classmethod
    async def create(
        cls,
        *,
        client: "NotionClient",
        database_id: str,
        title: str,
        version_id: str,
        status: str = "Backlog",
        task_type: str = "New Feature",
        priority: str = "Medium",
        dependency_ids: list[str] | None = None,
        estimated_hours: int | None = None,
    ) -> "Task":
        """Create a new task."""
        from better_notion._api.properties import Title, Select, Number, Relation

        # Build properties
        properties: dict[str, Any] = {
            "Title": Title(title),
            "Version": Relation([version_id]),
            "Status": Select(status),
            "Type": Select(task_type),
            "Priority": Select(priority),
        }

        if dependency_ids:
            properties["Dependencies"] = Relation(dependency_ids)
        if estimated_hours is not None:
            properties["Estimated Hours"] = Number(estimated_hours)

        # Create page
        data = await client._api.pages.create(
            parent={"database_id": database_id},
            properties=properties,
        )

        task = cls(client, data)

        # Cache it
        cache = client.plugin_cache("tasks")
        if cache:
            cache[task.id] = task

        return task

    async def update(
        self,
        *,
        title: str | None = None,
        status: str | None = None,
        task_type: str | None = None,
        priority: str | None = None,
        dependency_ids: list[str] | None = None,
        estimated_hours: int | None = None,
        actual_hours: int | None = None,
    ) -> "Task":
        """Update task properties."""
        from better_notion._api.properties import Title, Select, Number, Relation

        # Build properties to update
        properties: dict[str, Any] = {}

        if title is not None:
            properties["Title"] = Title(title)
        if status is not None:
            properties["Status"] = Select(status)
        if task_type is not None:
            properties["Type"] = Select(task_type)
        if priority is not None:
            properties["Priority"] = Select(priority)
        if dependency_ids is not None:
            properties["Dependencies"] = Relation(dependency_ids)
        if estimated_hours is not None:
            properties["Estimated Hours"] = Number(estimated_hours)
        if actual_hours is not None:
            properties["Actual Hours"] = Number(actual_hours)

        # Update page
        data = await self._client._api.pages.update(
            page_id=self.id,
            properties=properties,
        )

        # Update instance
        self._data = data

        # Invalidate cache
        cache = self._client.plugin_cache("tasks")
        if cache and self.id in cache:
            del cache[self.id]

        return self

    async def delete(self) -> None:
        """Delete the task."""
        await self._client._api.pages.delete(page_id=self.id)

        # Invalidate cache
        cache = self._client.plugin_cache("tasks")
        if cache and self.id in cache:
            del cache[self.id]

    async def version(self) -> Version | None:
        """Get parent version."""
        if self.version_id:
            return await Version.get(self.version_id, client=self._client)
        return None

    async def dependencies(self) -> list["Task"]:
        """Get all tasks this task depends on."""
        tasks = []
        for dep_id in self.dependency_ids:
            try:
                task = await Task.get(dep_id, client=self._client)
                tasks.append(task)
            except Exception:
                pass
        return tasks

    # ===== WORKFLOW METHODS =====

    async def claim(self) -> "Task":
        """
        Claim this task (transition to Claimed status).

        Returns:
            Updated Task instance

        Example:
            >>> await task.claim()
        """
        return await self.update(status="Claimed")

    async def start(self) -> "Task":
        """
        Start working on this task (transition to In Progress).

        Returns:
            Updated Task instance

        Example:
            >>> await task.start()
        """
        return await self.update(status="In Progress")

    async def complete(self, actual_hours: int | None = None) -> "Task":
        """
        Complete this task (transition to Completed).

        Args:
            actual_hours: Actual hours spent (optional)

        Returns:
            Updated Task instance

        Example:
            >>> await task.complete(actual_hours=3)
        """
        return await self.update(status="Completed", actual_hours=actual_hours)

    async def can_start(self) -> bool:
        """
        Check if this task can start (all dependencies completed).

        Returns:
            True if all dependencies are completed

        Example:
            >>> if await task.can_start():
            ...     await task.start()
        """
        for dep in await self.dependencies():
            if dep.status != "Completed":
                return False
        return True


class Idea(BaseEntity):
    """
    Idea entity representing an improvement opportunity discovered during work.

    Ideas enable continuous improvement by capturing innovations and
    problems discovered during development work.

    Attributes:
        id: Idea page ID
        title: Idea title
        category: Idea category (Feature, Improvement, Refactor, etc.)
        status: Idea status (New, Evaluated, Accepted, Rejected, Deferred)
        description: Detailed explanation
        proposed_solution: How to implement
        benefits: Why this is valuable
        effort_estimate: Implementation effort (Small, Medium, Large)
        context: What you were doing when you thought of this
        project_id: Related project ID (optional)
        related_task_id: Task created from this idea (optional)

    Example:
        >>> idea = await Idea.create(
        ...     client=client,
        ...     database_id=db_id,
        ...     title="Add caching layer",
        ...     category="Improvement",
        ...     description="Would improve performance"
        ... )
        >>> await idea.accept()
        >>> task = await idea.create_task(version_id=ver.id)
    """

    def __init__(self, client: "NotionClient", data: dict[str, Any]) -> None:
        """Initialize idea with client and API data."""
        super().__init__(client, data)
        self._idea_cache = client.plugin_cache("ideas")

    # ===== PROPERTIES =====

    @property
    def title(self) -> str:
        """Get idea title."""
        title_prop = self._data["properties"].get("Title") or self._data["properties"].get("title")
        if title_prop and title_prop.get("type") == "title":
            title_data = title_prop.get("title", [])
            if title_data:
                return title_data[0].get("plain_text", "")
        return ""

    @property
    def category(self) -> str:
        """Get idea category."""
        cat_prop = self._data["properties"].get("Category") or self._data["properties"].get("category")
        if cat_prop and cat_prop.get("type") == "select":
            select_data = cat_prop.get("select")
            if select_data:
                return select_data.get("name", "Unknown")
        return "Unknown"

    @property
    def status(self) -> str:
        """Get idea status."""
        status_prop = self._data["properties"].get("Status") or self._data["properties"].get("status")
        if status_prop and status_prop.get("type") == "select":
            select_data = status_prop.get("select")
            if select_data:
                return select_data.get("name", "Unknown")
        return "Unknown"

    @property
    def description(self) -> str:
        """Get idea description."""
        desc_prop = self._data["properties"].get("Description") or self._data["properties"].get("description")
        if desc_prop and desc_prop.get("type") == "rich_text":
            text_data = desc_prop.get("rich_text", [])
            if text_data:
                return text_data[0].get("plain_text", "")
        return ""

    @property
    def proposed_solution(self) -> str:
        """Get proposed solution."""
        sol_prop = self._data["properties"].get("Proposed Solution") or self._data["properties"].get("proposed_solution")
        if sol_prop and sol_prop.get("type") == "rich_text":
            text_data = sol_prop.get("rich_text", [])
            if text_data:
                return text_data[0].get("plain_text", "")
        return ""

    @property
    def benefits(self) -> str:
        """Get idea benefits."""
        ben_prop = self._data["properties"].get("Benefits") or self._data["properties"].get("benefits")
        if ben_prop and ben_prop.get("type") == "rich_text":
            text_data = ben_prop.get("rich_text", [])
            if text_data:
                return text_data[0].get("plain_text", "")
        return ""

    @property
    def effort_estimate(self) -> str:
        """Get effort estimate."""
        effort_prop = self._data["properties"].get("Effort Estimate") or self._data["properties"].get("effort_estimate")
        if effort_prop and effort_prop.get("type") == "select":
            select_data = effort_prop.get("select")
            if select_data:
                return select_data.get("name", "Unknown")
        return "Unknown"

    @property
    def context(self) -> str:
        """Get idea context."""
        ctx_prop = self._data["properties"].get("Context") or self._data["properties"].get("context")
        if ctx_prop and ctx_prop.get("type") == "rich_text":
            text_data = ctx_prop.get("rich_text", [])
            if text_data:
                return text_data[0].get("plain_text", "")
        return ""

    @property
    def project_id(self) -> str | None:
        """Get related project ID."""
        proj_prop = self._data["properties"].get("Project") or self._data["properties"].get("project")
        if proj_prop and proj_prop.get("type") == "relation":
            relations = proj_prop.get("relation", [])
            if relations:
                return relations[0].get("id")
        return None

    @property
    def related_task_id(self) -> str | None:
        """Get ID of task created from this idea."""
        task_prop = self._data["properties"].get("Related Task") or self._data["properties"].get("related_task")
        if task_prop and task_prop.get("type") == "relation":
            relations = task_prop.get("relation", [])
            if relations:
                return relations[0].get("id")
        return None

    # ===== AUTONOMOUS METHODS =====

    @classmethod
    async def get(cls, idea_id: str, *, client: "NotionClient") -> "Idea":
        """Get an idea by ID."""
        cache = client.plugin_cache("ideas")
        if cache and idea_id in cache:
            return cache[idea_id]

        data = await client._api.pages.get(page_id=idea_id)
        idea = cls(client, data)

        if cache:
            cache[idea_id] = idea

        return idea

    @classmethod
    async def create(
        cls,
        *,
        client: "NotionClient",
        database_id: str,
        title: str,
        category: str,
        status: str = "New",
        description: str | None = None,
        proposed_solution: str | None = None,
        benefits: str | None = None,
        effort_estimate: str = "Medium",
        context: str | None = None,
        project_id: str | None = None,
    ) -> "Idea":
        """Create a new idea."""
        from better_notion._api.properties import Title, RichText, Select, Relation

        properties: dict[str, Any] = {
            "Title": Title(title),
            "Category": Select(category),
            "Status": Select(status),
            "Effort Estimate": Select(effort_estimate),
        }

        if description:
            properties["Description"] = RichText(description)
        if proposed_solution:
            properties["Proposed Solution"] = RichText(proposed_solution)
        if benefits:
            properties["Benefits"] = RichText(benefits)
        if context:
            properties["Context"] = RichText(context)
        if project_id:
            properties["Project"] = Relation([project_id])

        data = await client._api.pages.create(
            parent={"database_id": database_id},
            properties=properties,
        )

        idea = cls(client, data)

        cache = client.plugin_cache("ideas")
        if cache:
            cache[idea.id] = idea

        return idea

    async def update(
        self,
        *,
        title: str | None = None,
        category: str | None = None,
        status: str | None = None,
        description: str | None = None,
        proposed_solution: str | None = None,
        benefits: str | None = None,
        effort_estimate: str | None = None,
        context: str | None = None,
    ) -> "Idea":
        """Update idea properties."""
        from better_notion._api.properties import Title, RichText, Select

        properties: dict[str, Any] = {}

        if title is not None:
            properties["Title"] = Title(title)
        if category is not None:
            properties["Category"] = Select(category)
        if status is not None:
            properties["Status"] = Select(status)
        if description is not None:
            properties["Description"] = RichText(description)
        if proposed_solution is not None:
            properties["Proposed Solution"] = RichText(proposed_solution)
        if benefits is not None:
            properties["Benefits"] = RichText(benefits)
        if effort_estimate is not None:
            properties["Effort Estimate"] = Select(effort_estimate)
        if context is not None:
            properties["Context"] = RichText(context)

        data = await self._client._api.pages.update(
            page_id=self.id,
            properties=properties,
        )

        self._data = data

        cache = self._client.plugin_cache("ideas")
        if cache and self.id in cache:
            del cache[self.id]

        return self

    async def delete(self) -> None:
        """Delete the idea."""
        await self._client._api.pages.delete(page_id=self.id)

        cache = self._client.plugin_cache("ideas")
        if cache and self.id in cache:
            del cache[self.id]

    # ===== WORKFLOW METHODS =====

    async def accept(self) -> "Idea":
        """
        Accept this idea (transition to Accepted status).

        Returns:
            Updated Idea instance

        Example:
            >>> await idea.accept()
        """
        return await self.update(status="Accepted")

    async def reject(self, reason: str) -> "Idea":
        """
        Reject this idea (transition to Rejected status).

        Args:
            reason: Rejection reason stored in context

        Returns:
            Updated Idea instance

        Example:
            >>> await idea.reject("Not technically feasible")
        """
        return await self.update(
            status="Rejected",
            context=f"Rejected: {reason}",
        )

    async def defer(self) -> "Idea":
        """
        Defer this idea (transition to Deferred status).

        Returns:
            Updated Idea instance

        Example:
            >>> await idea.defer()
        """
        return await self.update(status="Deferred")

    async def create_task(
        self,
        *,
        version_id: str,
        title: str | None = None,
        task_type: str = "New Feature",
        priority: str = "Medium",
    ) -> Task:
        """
        Create a task from this idea.

        Args:
            version_id: Version to create task in
            title: Task title (defaults to idea title)
            task_type: Type of task
            priority: Task priority

        Returns:
            Created Task instance

        Example:
            >>> task = await idea.create_task(version_id=ver.id, priority="High")
        """
        from better_notion.plugins.official.agents_sdk.models import Task

        # Get database ID
        import json
        from pathlib import Path

        config_path = Path.home() / ".notion" / "workspace.json"
        config = json.loads(config_path.read_text())
        tasks_db_id = config.get("Tasks")

        if not tasks_db_id:
            raise ValueError("Tasks database not found in workspace config")

        task = await Task.create(
            client=self._client,
            database_id=tasks_db_id,
            title=title or self.title,
            version_id=version_id,
            task_type=task_type,
            priority=priority,
        )

        # Link idea to task
        await self.link_to_task(task.id)

        return task

    async def link_to_task(self, task_id: str) -> None:
        """
        Link this idea to a task.

        Args:
            task_id: Task ID to link to

        Example:
            >>> await idea.link_to_task(task.id)
        """
        from better_notion._api.properties import Relation

        await self._client._api.pages.update(
            page_id=self.id,
            properties={
                "Related Task": Relation([task_id]),
            },
        )


class WorkIssue(BaseEntity):
    """
    Work Issue entity representing a development-time problem.

    Work Issues track blockers, confusions, documentation gaps,
    tooling limitations, and other problems encountered during development.

    Attributes:
        id: Work Issue page ID
        title: Issue title
        project_id: Affected project ID
        task_id: Task where issue occurred (optional)
        type: Issue type (Blocker, Confusion, Documentation, Tooling, etc.)
        severity: Issue severity (Critical, High, Medium, Low)
        status: Issue status (Open, Investigating, Resolved, Won't Fix, Deferred)
        description: What happened
        context: Environment details
        proposed_solution: How to fix
        related_idea_id: Idea this inspired (optional)

    Example:
        >>> issue = await WorkIssue.create(
        ...     client=client,
        ...     database_id=db_id,
        ...     title="API documentation unclear",
        ...     project_id=proj.id,
        ...     type="Documentation",
        ...     severity="Medium"
        ... )
        >>> await issue.resolve("Updated docs with examples")
        >>> idea = await issue.create_idea_from_solution()
    """

    def __init__(self, client: "NotionClient", data: dict[str, Any]) -> None:
        """Initialize work issue with client and API data."""
        super().__init__(client, data)
        self._work_issue_cache = client.plugin_cache("work_issues")

    # ===== PROPERTIES =====

    @property
    def title(self) -> str:
        """Get issue title."""
        title_prop = self._data["properties"].get("Title") or self._data["properties"].get("title")
        if title_prop and title_prop.get("type") == "title":
            title_data = title_prop.get("title", [])
            if title_data:
                return title_data[0].get("plain_text", "")
        return ""

    @property
    def project_id(self) -> str | None:
        """Get affected project ID."""
        proj_prop = self._data["properties"].get("Project") or self._data["properties"].get("project")
        if proj_prop and proj_prop.get("type") == "relation":
            relations = proj_prop.get("relation", [])
            if relations:
                return relations[0].get("id")
        return None

    @property
    def task_id(self) -> str | None:
        """Get related task ID."""
        task_prop = self._data["properties"].get("Task") or self._data["properties"].get("task")
        if task_prop and task_prop.get("type") == "relation":
            relations = task_prop.get("relation", [])
            if relations:
                return relations[0].get("id")
        return None

    @property
    def type(self) -> str:
        """Get issue type."""
        type_prop = self._data["properties"].get("Type") or self._data["properties"].get("type")
        if type_prop and type_prop.get("type") == "select":
            select_data = type_prop.get("select")
            if select_data:
                return select_data.get("name", "Unknown")
        return "Unknown"

    @property
    def severity(self) -> str:
        """Get issue severity."""
        sev_prop = self._data["properties"].get("Severity") or self._data["properties"].get("severity")
        if sev_prop and sev_prop.get("type") == "select":
            select_data = sev_prop.get("select")
            if select_data:
                return select_data.get("name", "Unknown")
        return "Unknown"

    @property
    def status(self) -> str:
        """Get issue status."""
        status_prop = self._data["properties"].get("Status") or self._data["properties"].get("status")
        if status_prop and status_prop.get("type") == "select":
            select_data = status_prop.get("select")
            if select_data:
                return select_data.get("name", "Unknown")
        return "Unknown"

    @property
    def description(self) -> str:
        """Get issue description."""
        desc_prop = self._data["properties"].get("Description") or self._data["properties"].get("description")
        if desc_prop and desc_prop.get("type") == "rich_text":
            text_data = desc_prop.get("rich_text", [])
            if text_data:
                return text_data[0].get("plain_text", "")
        return ""

    @property
    def context(self) -> str:
        """Get issue context."""
        ctx_prop = self._data["properties"].get("Context") or self._data["properties"].get("context")
        if ctx_prop and ctx_prop.get("type") == "rich_text":
            text_data = ctx_prop.get("rich_text", [])
            if text_data:
                return text_data[0].get("plain_text", "")
        return ""

    @property
    def proposed_solution(self) -> str:
        """Get proposed solution."""
        sol_prop = self._data["properties"].get("Proposed Solution") or self._data["properties"].get("proposed_solution")
        if sol_prop and sol_prop.get("type") == "rich_text":
            text_data = sol_prop.get("rich_text", [])
            if text_data:
                return text_data[0].get("plain_text", "")
        return ""

    @property
    def related_idea_id(self) -> str | None:
        """Get related idea ID."""
        idea_prop = self._data["properties"].get("Related Idea") or self._data["properties"].get("related_idea")
        if idea_prop and idea_prop.get("type") == "relation":
            relations = idea_prop.get("relation", [])
            if relations:
                return relations[0].get("id")
        return None

    # ===== AUTONOMOUS METHODS =====

    @classmethod
    async def get(cls, issue_id: str, *, client: "NotionClient") -> "WorkIssue":
        """Get a work issue by ID."""
        cache = client.plugin_cache("work_issues")
        if cache and issue_id in cache:
            return cache[issue_id]

        data = await client._api.pages.get(page_id=issue_id)
        issue = cls(client, data)

        if cache:
            cache[issue_id] = issue

        return issue

    @classmethod
    async def create(
        cls,
        *,
        client: "NotionClient",
        database_id: str,
        title: str,
        project_id: str,
        task_id: str | None = None,
        type: str = "Blocker",
        severity: str = "Medium",
        status: str = "Open",
        description: str | None = None,
        context: str | None = None,
        proposed_solution: str | None = None,
    ) -> "WorkIssue":
        """Create a new work issue."""
        from better_notion._api.properties import Title, RichText, Select, Relation

        properties: dict[str, Any] = {
            "Title": Title(title),
            "Project": Relation([project_id]),
            "Type": Select(type),
            "Severity": Select(severity),
            "Status": Select(status),
        }

        if task_id:
            properties["Task"] = Relation([task_id])
        if description:
            properties["Description"] = RichText(description)
        if context:
            properties["Context"] = RichText(context)
        if proposed_solution:
            properties["Proposed Solution"] = RichText(proposed_solution)

        data = await client._api.pages.create(
            parent={"database_id": database_id},
            properties=properties,
        )

        issue = cls(client, data)

        cache = client.plugin_cache("work_issues")
        if cache:
            cache[issue.id] = issue

        return issue

    async def update(
        self,
        *,
        title: str | None = None,
        type: str | None = None,
        severity: str | None = None,
        status: str | None = None,
        description: str | None = None,
        context: str | None = None,
        proposed_solution: str | None = None,
    ) -> "WorkIssue":
        """Update work issue properties."""
        from better_notion._api.properties import Title, RichText, Select

        properties: dict[str, Any] = {}

        if title is not None:
            properties["Title"] = Title(title)
        if type is not None:
            properties["Type"] = Select(type)
        if severity is not None:
            properties["Severity"] = Select(severity)
        if status is not None:
            properties["Status"] = Select(status)
        if description is not None:
            properties["Description"] = RichText(description)
        if context is not None:
            properties["Context"] = RichText(context)
        if proposed_solution is not None:
            properties["Proposed Solution"] = RichText(proposed_solution)

        data = await self._client._api.pages.update(
            page_id=self.id,
            properties=properties,
        )

        self._data = data

        cache = self._client.plugin_cache("work_issues")
        if cache and self.id in cache:
            del cache[self.id]

        return self

    async def delete(self) -> None:
        """Delete the work issue."""
        await self._client._api.pages.delete(page_id=self.id)

        cache = self._client.plugin_cache("work_issues")
        if cache and self.id in cache:
            del cache[self.id]

    # ===== WORKFLOW METHODS =====

    async def resolve(self, solution: str) -> "WorkIssue":
        """
        Resolve this issue.

        Args:
            solution: How the issue was resolved

        Returns:
            Updated WorkIssue instance

        Example:
            >>> await issue.resolve("Updated documentation")
        """
        return await self.update(
        status="Resolved",
        proposed_solution=solution,
    )

    async def investigate(self) -> "WorkIssue":
        """
        Mark issue as under investigation.

        Returns:
            Updated WorkIssue instance

        Example:
            >>> await issue.investigate()
        """
        return await self.update(status="Investigating")

    async def link_to_idea(self, idea_id: str) -> None:
        """
        Link this issue to an idea.

        Args:
            idea_id: Idea ID to link to

        Example:
            >>> await issue.link_to_idea(idea.id)
        """
        from better_notion._api.properties import Relation

        await self._client._api.pages.update(
            page_id=self.id,
            properties={
                "Related Idea": Relation([idea_id]),
            },
        )

    async def create_idea_from_solution(self) -> Idea:
        """
        Create an idea from this issue's solution.

        Returns:
            Created Idea instance

        Example:
            >>> idea = await issue.create_idea_from_solution()
        """
        from better_notion.plugins.official.agents_sdk.models import Idea

        import json
        from pathlib import Path

        config_path = Path.home() / ".notion" / "workspace.json"
        config = json.loads(config_path.read_text())
        ideas_db_id = config.get("Ideas")

        if not ideas_db_id:
            raise ValueError("Ideas database not found in workspace config")

        idea = await Idea.create(
            client=self._client,
            database_id=ideas_db_id,
            title=f"Prevent issue: {self.title}",
            category="Process",
            status="New",
            description=f"Issue {self.id} revealed process gap",
            proposed_solution=self.proposed_solution or "Implement prevention",
            context=self.context,
            project_id=self.project_id,
        )

        # Link issue to idea
        await self.link_to_idea(idea.id)

        return idea


class Incident(BaseEntity):
    """
    Incident entity representing a production incident.

    Incidents track production problems separate from development
    work issues. Critical for production reliability and MTTR tracking.

    Attributes:
        id: Incident page ID
        title: Incident title
        project_id: Affected project ID
        affected_version_id: Version where incident occurred
        severity: Incident severity (Critical, High, Medium, Low)
        type: Incident type (Bug, Crash, Performance, Security, etc.)
        status: Incident status (Open, Investigating, Fix in Progress, Resolved)
        fix_task_id: Task to fix this incident (optional)
        root_cause: Analysis of what went wrong
        discovery_date: When incident was discovered
        resolved_date: When incident was resolved (optional)

    Example:
        >>> incident = await Incident.create(
        ...     client=client,
        ...     database_id=db_id,
        ...     title="Production database down",
        ...     project_id=proj.id,
        ...     affected_version_id=ver.id,
        ...     severity="Critical",
        ...     type="Outage"
        ... )
        >>> task = await incident.create_fix_task(version_id=hotfix.id)
        >>> await incident.resolve("Config error in connection pool")
        >>> mttr = incident.calculate_mttr()
    """

    def __init__(self, client: "NotionClient", data: dict[str, Any]) -> None:
        """Initialize incident with client and API data."""
        super().__init__(client, data)
        self._incident_cache = client.plugin_cache("incidents")

    # ===== PROPERTIES =====

    @property
    def title(self) -> str:
        """Get incident title."""
        title_prop = self._data["properties"].get("Title") or self._data["properties"].get("title")
        if title_prop and title_prop.get("type") == "title":
            title_data = title_prop.get("title", [])
            if title_data:
                return title_data[0].get("plain_text", "")
        return ""

    @property
    def project_id(self) -> str | None:
        """Get affected project ID."""
        proj_prop = self._data["properties"].get("Project") or self._data["properties"].get("project")
        if proj_prop and proj_prop.get("type") == "relation":
            relations = proj_prop.get("relation", [])
            if relations:
                return relations[0].get("id")
        return None

    @property
    def affected_version_id(self) -> str | None:
        """Get affected version ID."""
        ver_prop = self._data["properties"].get("Affected Version") or self._data["properties"].get("affected_version")
        if ver_prop and ver_prop.get("type") == "relation":
            relations = ver_prop.get("relation", [])
            if relations:
                return relations[0].get("id")
        return None

    @property
    def severity(self) -> str:
        """Get incident severity."""
        sev_prop = self._data["properties"].get("Severity") or self._data["properties"].get("severity")
        if sev_prop and sev_prop.get("type") == "select":
            select_data = sev_prop.get("select")
            if select_data:
                return select_data.get("name", "Unknown")
        return "Unknown"

    @property
    def type(self) -> str:
        """Get incident type."""
        type_prop = self._data["properties"].get("Type") or self._data["properties"].get("type")
        if type_prop and type_prop.get("type") == "select":
            select_data = type_prop.get("select")
            if select_data:
                return select_data.get("name", "Unknown")
        return "Unknown"

    @property
    def status(self) -> str:
        """Get incident status."""
        status_prop = self._data["properties"].get("Status") or self._data["properties"].get("status")
        if status_prop and status_prop.get("type") == "select":
            select_data = status_prop.get("select")
            if select_data:
                return select_data.get("name", "Unknown")
        return "Unknown"

    @property
    def fix_task_id(self) -> str | None:
        """Get fix task ID."""
        task_prop = self._data["properties"].get("Fix Task") or self._data["properties"].get("fix_task")
        if task_prop and task_prop.get("type") == "relation":
            relations = task_prop.get("relation", [])
            if relations:
                return relations[0].get("id")
        return None

    @property
    def root_cause(self) -> str:
        """Get root cause analysis."""
        rc_prop = self._data["properties"].get("Root Cause") or self._data["properties"].get("root_cause")
        if rc_prop and rc_prop.get("type") == "rich_text":
            text_data = rc_prop.get("rich_text", [])
            if text_data:
                return text_data[0].get("plain_text", "")
        return ""

    @property
    def discovery_date(self) -> str | None:
        """Get discovery date."""
        date_prop = self._data["properties"].get("Discovery Date") or self._data["properties"].get("discovery_date")
        if date_prop and date_prop.get("type") == "date":
            date_data = date_prop.get("date")
            if date_data and date_data.get("start"):
                return date_data["start"]
        return None

    @property
    def resolved_date(self) -> str | None:
        """Get resolved date."""
        date_prop = self._data["properties"].get("Resolved Date") or self._data["properties"].get("resolved_date")
        if date_prop and date_prop.get("type") == "date":
            date_data = date_prop.get("date")
            if date_data and date_data.get("start"):
                return date_data["start"]
        return None

    # ===== AUTONOMOUS METHODS =====

    @classmethod
    async def get(cls, incident_id: str, *, client: "NotionClient") -> "Incident":
        """Get an incident by ID."""
        cache = client.plugin_cache("incidents")
        if cache and incident_id in cache:
            return cache[incident_id]

        data = await client._api.pages.get(page_id=incident_id)
        incident = cls(client, data)

        if cache:
            cache[incident_id] = incident

        return incident

    @classmethod
    async def create(
        cls,
        *,
        client: "NotionClient",
        database_id: str,
        title: str,
        project_id: str,
        affected_version_id: str,
        severity: str = "High",
        type: str = "Bug",
        status: str = "Open",
        discovery_date: str | None = None,
    ) -> "Incident":
        """Create a new incident."""
        from datetime import datetime
        from better_notion._api.properties import Title, Date, Select, Relation

        properties: dict[str, Any] = {
            "Title": Title(title),
            "Project": Relation([project_id]),
            "Affected Version": Relation([affected_version_id]),
            "Severity": Select(severity),
            "Type": Select(type),
            "Status": Select(status),
            "Discovery Date": Date(discovery_date or datetime.now().isoformat()),
        }

        data = await client._api.pages.create(
            parent={"database_id": database_id},
            properties=properties,
        )

        incident = cls(client, data)

        cache = client.plugin_cache("incidents")
        if cache:
            cache[incident.id] = incident

        return incident

    async def update(
        self,
        *,
        title: str | None = None,
        severity: str | None = None,
        status: str | None = None,
        root_cause: str | None = None,
        resolved_date: str | None = None,
    ) -> "Incident":
        """Update incident properties."""
        from better_notion._api.properties import Title, RichText, Select, Date

        properties: dict[str, Any] = {}

        if title is not None:
            properties["Title"] = Title(title)
        if severity is not None:
            properties["Severity"] = Select(severity)
        if status is not None:
            properties["Status"] = Select(status)
        if root_cause is not None:
            properties["Root Cause"] = RichText(root_cause)
        if resolved_date is not None:
            properties["Resolved Date"] = Date(resolved_date)

        data = await self._client._api.pages.update(
            page_id=self.id,
            properties=properties,
        )

        self._data = data

        cache = self._client.plugin_cache("incidents")
        if cache and self.id in cache:
            del cache[self.id]

        return self

    async def delete(self) -> None:
        """Delete the incident."""
        await self._client._api.pages.delete(page_id=self.id)

        cache = self._client.plugin_cache("incidents")
        if cache and self.id in cache:
            del cache[self.id]

    # ===== WORKFLOW METHODS =====

    async def investigate(self) -> "Incident":
        """
        Mark incident as under investigation.

        Returns:
            Updated Incident instance

        Example:
            >>> await incident.investigate()
        """
        return await self.update(status="Investigating")

    async def assign(self, task_id: str) -> "Incident":
        """
        Assign a fix task to this incident.

        Args:
            task_id: Task ID that will fix this incident

        Returns:
            Updated Incident instance

        Example:
            >>> await incident.assign(task.id)
        """
        from better_notion._api.properties import Relation

        await self._client._api.pages.update(
            page_id=self.id,
            properties={
                "Fix Task": Relation([task_id]),
                "Status": Select("Fix in Progress"),
            },
        )

        # Update local data
        self._data["properties"]["Fix Task"] = {"type": "relation", "relation": [{"id": task_id}]}
        self._data["properties"]["Status"] = {"type": "select", "select": {"name": "Fix in Progress"}}

        return self

    async def resolve(self, root_cause: str, resolved_date: str | None = None) -> "Incident":
        """
        Resolve this incident.

        Args:
            root_cause: Analysis of what went wrong
            resolved_date: When incident was resolved (defaults to now)

        Returns:
            Updated Incident instance

        Example:
            >>> await incident.resolve("Config error in connection pool")
        """
        from datetime import datetime

        return await self.update(
            status="Resolved",
        root_cause=root_cause,
        resolved_date=resolved_date or datetime.now().isoformat(),
        )

    def calculate_mttr(self) -> float | None:
        """
        Calculate Mean Time To Resolve in minutes.

        Returns:
            MTTR in minutes, or None if not resolved

        Example:
            >>> mttr_minutes = incident.calculate_mttr()
            >>> print(f"MTTR: {mttr_minutes:.1f} minutes")
        """
        if not self.resolved_date or not self.discovery_date:
            return None

        from datetime import datetime

        resolved = datetime.fromisoformat(self.resolved_date)
        discovered = datetime.fromisoformat(self.discovery_date)

        mttr_seconds = (resolved - discovered).total_seconds()
        return mttr_seconds / 60

    async def create_fix_task(
        self,
        *,
        version_id: str,
        title: str | None = None,
        priority: str = "Critical",
    ) -> Task:
        """
        Create a fix task for this incident.

        Args:
            version_id: Version to create fix in
            title: Task title (defaults to incident title)
            priority: Task priority

        Returns:
            Created Task instance

        Example:
            >>> task = await incident.create_fix_task(
            ...     version_id=hotfix.id,
            ...     priority="Critical"
            ... )
        """
        from better_notion.plugins.official.agents_sdk.models import Task

        import json
        from pathlib import Path

        config_path = Path.home() / ".notion" / "workspace.json"
        config = json.loads(config_path.read_text())
        tasks_db_id = config.get("Tasks")

        if not tasks_db_id:
            raise ValueError("Tasks database not found in workspace config")

        task = await Task.create(
            client=self._client,
            database_id=tasks_db_id,
            title=title or f"Fix incident: {self.title}",
            version_id=version_id,
            task_type="Bug Fix",
            priority=priority,
        )

        # Assign task to incident
        await self.assign(task.id)

        return task
