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
