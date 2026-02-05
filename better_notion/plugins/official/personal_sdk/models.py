"""Personal entity models for the personal SDK plugin.

This module provides SDK model classes for personal entities:
- Domain
- Tag
- Project
- Task
- Routine
- Agenda

These models inherit from BaseEntity and provide autonomous CRUD operations
with caching support through the plugin system.
"""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Any, AsyncIterator

from better_notion._sdk.base.entity import BaseEntity

if TYPE_CHECKING:
    from better_notion._sdk.client import NotionClient
    from better_notion._sdk.models.block import Block
    from better_notion._sdk.models.database import Database
    from better_notion._sdk.models.page import Page


class DatabasePageEntityMixin:
    """Mixin providing BaseEntity abstract method implementations for database pages.

    This mixin provides parent() and children() implementations for entities
    that are pages in databases (like Domain, Tag, Project, etc.).
    """

    async def parent(self) -> "Database | Page | None":
        """Get parent object (database for entity pages).

        Returns:
            Parent Database or Page or None
        """
        from better_notion._sdk.models.database import Database

        # Get parent from data
        parent_data = self._data.get("parent")
        if not parent_data:
            return None

        # Check cache
        cached = self._cache_get("parent")
        if cached:
            return cached

        # Database parent
        if parent_data.get("type") == "database_id":
            db_id = parent_data.get("database_id")
            parent = await Database.get(db_id, client=self._client)
            self._cache_set("parent", parent)
            return parent

        # Page parent
        if parent_data.get("type") == "page_id":
            from better_notion._sdk.models.page import Page
            page_id = parent_data.get("page_id")
            parent = await Page.get(page_id, client=self._client)
            self._cache_set("parent", parent)
            return parent

        return None

    async def children(self) -> AsyncIterator["Block"]:
        """Iterate over child blocks.

        Yields:
            Block objects that are direct children
        """
        from better_notion._api.utils.pagination import AsyncPaginatedIterator
        from better_notion._sdk.models.block import Block

        async def _get_blocks(offset: str | None = None) -> dict[str, Any]:
            return await self._client._api._request(
                "GET",
                f"/blocks/{self.id}/children",
                params={"start_cursor": offset} if offset else None
            )

        iterator = AsyncPaginatedIterator(_get_blocks, lambda data: data.get("results", []))

        async for block_data in iterator:
            yield Block(self._client, block_data)


class Domain(DatabasePageEntityMixin, BaseEntity):
    """
    Domain entity representing a life area.

    A domain is a high-level category for organizing different areas of life
    like Work, Health, Finance, Learning, etc.

    Attributes:
        id: Domain page ID
        name: Domain name
        description: Domain description
        color: Visual color tag

    Example:
        >>> domain = await Domain.get("domain_id", client=client)
        >>> print(domain.name)
    """

    def __init__(self, client: "NotionClient", data: dict[str, Any]) -> None:
        """Initialize domain with client and API data.

        Args:
            client: NotionClient instance
            data: Raw API response data
        """
        super().__init__(client, data)
        self._domain_cache = client.plugin_cache("domains")

    # ===== PROPERTIES =====

    @property
    def name(self) -> str:
        """Get domain name from title property.

        Returns:
            Domain name as string
        """
        title_prop = self._data["properties"].get("Name")
        if title_prop and title_prop.get("type") == "title":
            title_data = title_prop.get("title", [])
            if title_data:
                return title_data[0].get("plain_text", "")
        return ""

    @property
    def description(self) -> str:
        """Get domain description.

        Returns:
            Description string
        """
        desc_prop = self._data["properties"].get("Description")
        if desc_prop and desc_prop.get("type") == "rich_text" or desc_prop.get("type") == "text":
            text_data = desc_prop.get("rich_text") or desc_prop.get("text", [])
            if text_data:
                return text_data[0].get("plain_text", "") if isinstance(text_data, list) else str(text_data)
        return ""

    @property
    def color(self) -> str:
        """Get domain color.

        Returns:
            Color string (Red, Orange, Yellow, Green, Blue, Purple, Gray)
        """
        color_prop = self._data["properties"].get("Color")
        if color_prop and color_prop.get("type") == "select":
            select_data = color_prop.get("select")
            if select_data:
                return select_data.get("name", "Gray")
        return "Gray"

    # ===== AUTONOMOUS METHODS =====

    @classmethod
    async def get(cls, domain_id: str, *, client: "NotionClient") -> "Domain":
        """
        Get a domain by ID.

        Args:
            domain_id: Domain page ID
            client: NotionClient instance

        Returns:
            Domain instance

        Raises:
            Exception: If API call fails

        Example:
            >>> domain = await Domain.get("domain_123", client=client)
        """
        # Check plugin cache
        cache = client.plugin_cache("domains")
        if cache and domain_id in cache:
            return cache[domain_id]

        # Fetch from API
        data = await client._api.pages.get(page_id=domain_id)
        domain = cls(client, data)

        # Cache it
        if cache:
            cache[domain_id] = domain

        return domain

    @classmethod
    async def create(
        cls,
        *,
        client: "NotionClient",
        database_id: str,
        name: str,
        description: str = "",
        color: str = "Blue",
    ) -> "Domain":
        """
        Create a new domain.

        Args:
            client: NotionClient instance
            database_id: Domains database ID
            name: Domain name
            description: Domain description
            color: Domain color (default: Blue)

        Returns:
            Created Domain instance

        Raises:
            Exception: If API call fails

        Example:
            >>> domain = await Domain.create(
            ...     client=client,
            ...     database_id="db_123",
            ...     name="Work",
            ...     description="Professional activities",
            ...     color="Blue"
            ... )
        """
        from better_notion._api.properties import Title, RichText, Select

        # Build properties
        properties: dict[str, Any] = {
            "Name": Title(content=name),
        }

        if description:
            properties["Description"] = RichText(name="Description", content=description)

        properties["Color"] = Select(name="Color", value=color)

        # Convert Property objects to dicts for API
        serialized_properties = {
            key: prop.to_dict() if hasattr(prop, 'to_dict') else prop
            for key, prop in properties.items()
        }

        # Create page
        data = await client._api.pages.create(
            parent={"database_id": database_id},
            properties=serialized_properties,
        )

        domain = cls(client, data)

        # Cache it
        cache = client.plugin_cache("domains")
        if cache:
            cache[domain.id] = domain

        return domain


class Tag(DatabasePageEntityMixin, BaseEntity):
    """
    Tag entity for flexible categorization.

    Tags provide flexible context labels like @computer, #high-energy,
    or ~morning to complement domain-based organization.

    Attributes:
        id: Tag page ID
        name: Tag name
        color: Visual color tag
        category: Tag category (Context, Energy, Location, Time, Custom)
        description: Tag description

    Example:
        >>> tag = await Tag.get("tag_id", client=client)
        >>> print(tag.name)
    """

    def __init__(self, client: "NotionClient", data: dict[str, Any]) -> None:
        """Initialize tag with client and API data.

        Args:
            client: NotionClient instance
            data: Raw API response data
        """
        super().__init__(client, data)
        self._tag_cache = client.plugin_cache("tags")

    # ===== PROPERTIES =====

    @property
    def name(self) -> str:
        """Get tag name from title property.

        Returns:
            Tag name as string
        """
        title_prop = self._data["properties"].get("Name")
        if title_prop and title_prop.get("type") == "title":
            title_data = title_prop.get("title", [])
            if title_data:
                return title_data[0].get("plain_text", "")
        return ""

    @property
    def color(self) -> str:
        """Get tag color.

        Returns:
            Color string
        """
        color_prop = self._data["properties"].get("Color")
        if color_prop and color_prop.get("type") == "select":
            select_data = color_prop.get("select")
            if select_data:
                return select_data.get("name", "Gray")
        return "Gray"

    @property
    def category(self) -> str:
        """Get tag category.

        Returns:
            Category string (Context, Energy, Location, Time, Custom)
        """
        category_prop = self._data["properties"].get("Category")
        if category_prop and category_prop.get("type") == "select":
            select_data = category_prop.get("select")
            if select_data:
                return select_data.get("name", "Custom")
        return "Custom"

    @property
    def description(self) -> str:
        """Get tag description.

        Returns:
            Description string
        """
        desc_prop = self._data["properties"].get("Description")
        if desc_prop and desc_prop.get("type") == "rich_text" or desc_prop.get("type") == "text":
            text_data = desc_prop.get("rich_text") or desc_prop.get("text", [])
            if text_data:
                return text_data[0].get("plain_text", "") if isinstance(text_data, list) else str(text_data)
        return ""

    # ===== AUTONOMOUS METHODS =====

    @classmethod
    async def get(cls, tag_id: str, *, client: "NotionClient") -> "Tag":
        """Get a tag by ID."""
        cache = client.plugin_cache("tags")
        if cache and tag_id in cache:
            return cache[tag_id]

        data = await client._api.pages.get(page_id=tag_id)
        tag = cls(client, data)

        if cache:
            cache[tag_id] = tag

        return tag

    @classmethod
    async def create(
        cls,
        *,
        client: "NotionClient",
        database_id: str,
        name: str,
        color: str = "Gray",
        category: str = "Custom",
        description: str = "",
    ) -> "Tag":
        """Create a new tag."""
        from better_notion._api.properties import Title, RichText, Select

        properties: dict[str, Any] = {
            "Name": Title(content=name),
            "Color": Select(name="Color", value=color),
            "Category": Select(name="Category", value=category),
        }

        if description:
            properties["Description"] = RichText(name="Description", content=description)

        serialized_properties = {
            key: prop.to_dict() if hasattr(prop, 'to_dict') else prop
            for key, prop in properties.items()
        }

        data = await client._api.pages.create(
            parent={"database_id": database_id},
            properties=serialized_properties,
        )

        tag = cls(client, data)

        cache = client.plugin_cache("tags")
        if cache:
            cache[tag.id] = tag

        return tag


class Project(DatabasePageEntityMixin, BaseEntity):
    """
    Project entity for tracking medium-term goals.

    Projects group related tasks and represent medium-term objectives
    with clear goals and deadlines.

    Attributes:
        id: Project page ID
        name: Project name
        status: Project status (Active, On Hold, Completed, Archived)
        domain_id: Related domain ID
        deadline: Project deadline
        priority: Project priority (Critical, High, Medium, Low)
        progress: Progress percentage (0-100)
        goal: Project goal description
        notes: Additional notes

    Example:
        >>> project = await Project.get("project_id", client=client)
        >>> print(project.name, project.status)
    """

    def __init__(self, client: "NotionClient", data: dict[str, Any]) -> None:
        """Initialize project with client and API data."""
        super().__init__(client, data)
        self._project_cache = client.plugin_cache("projects")

    # ===== PROPERTIES =====

    @property
    def name(self) -> str:
        """Get project name from title property."""
        title_prop = self._data["properties"].get("Name")
        if title_prop and title_prop.get("type") == "title":
            title_data = title_prop.get("title", [])
            if title_data:
                return title_data[0].get("plain_text", "")
        return ""

    @property
    def status(self) -> str:
        """Get project status."""
        status_prop = self._data["properties"].get("Status")
        if status_prop and status_prop.get("type") == "select":
            select_data = status_prop.get("select")
            if select_data:
                return select_data.get("name", "Active")
        return "Active"

    @property
    def domain_id(self) -> str | None:
        """Get related domain ID."""
        domain_prop = self._data["properties"].get("Domain")
        if domain_prop and domain_prop.get("type") == "relation":
            relation_data = domain_prop.get("relation", [])
            if relation_data:
                return relation_data[0].get("id")
        return None

    @property
    def deadline(self) -> datetime | None:
        """Get project deadline."""
        deadline_prop = self._data["properties"].get("Deadline")
        if deadline_prop and deadline_prop.get("type") == "date":
            date_data = deadline_prop.get("date")
            if date_data and date_data.get("start"):
                from datetime import datetime
                return datetime.fromisoformat(date_data["start"])
        return None

    @property
    def priority(self) -> str:
        """Get project priority."""
        priority_prop = self._data["properties"].get("Priority")
        if priority_prop and priority_prop.get("type") == "select":
            select_data = priority_prop.get("select")
            if select_data:
                return select_data.get("name", "Medium")
        return "Medium"

    @property
    def progress(self) -> int:
        """Get project progress percentage."""
        progress_prop = self._data["properties"].get("Progress")
        if progress_prop and progress_prop.get("type") == "number":
            return progress_prop.get("number", 0) or 0
        return 0

    @property
    def goal(self) -> str:
        """Get project goal."""
        goal_prop = self._data["properties"].get("Goal")
        if goal_prop and goal_prop.get("type") == "rich_text" or goal_prop.get("type") == "text":
            text_data = goal_prop.get("rich_text") or goal_prop.get("text", [])
            if text_data:
                return text_data[0].get("plain_text", "") if isinstance(text_data, list) else str(text_data)
        return ""

    @property
    def notes(self) -> str:
        """Get project notes."""
        notes_prop = self._data["properties"].get("Notes")
        if notes_prop and notes_prop.get("type") == "rich_text" or notes_prop.get("type") == "text":
            text_data = notes_prop.get("rich_text") or notes_prop.get("text", [])
            if text_data:
                return text_data[0].get("plain_text", "") if isinstance(text_data, list) else str(text_data)
        return ""

    # ===== AUTONOMOUS METHODS =====

    @classmethod
    async def get(cls, project_id: str, *, client: "NotionClient") -> "Project":
        """Get a project by ID."""
        cache = client.plugin_cache("projects")
        if cache and project_id in cache:
            return cache[project_id]

        data = await client._api.pages.get(page_id=project_id)
        project = cls(client, data)

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
        status: str = "Active",
        domain_id: str | None = None,
        deadline: str | None = None,
        priority: str = "Medium",
        progress: int = 0,
        goal: str = "",
        notes: str = "",
    ) -> "Project":
        """Create a new project."""
        from better_notion._api.properties import Title, RichText, Select, Number, Date, Relation

        properties: dict[str, Any] = {
            "Name": Title(content=name),
            "Status": Select(name="Status", value=status),
            "Priority": Select(name="Priority", value=priority),
            "Progress": Number(name="Progress", value=progress),
        }

        if domain_id:
            properties["Domain"] = Relation("Domain", [domain_id])

        if deadline:
            properties["Deadline"] = Date(name="Deadline", start=deadline)

        if goal:
            properties["Goal"] = RichText(name="Goal", content=goal)

        if notes:
            properties["Notes"] = RichText(name="Notes", content=notes)

        serialized_properties = {
            key: prop.to_dict() if hasattr(prop, 'to_dict') else prop
            for key, prop in properties.items()
        }

        data = await client._api.pages.create(
            parent={"database_id": database_id},
            properties=serialized_properties,
        )

        project = cls(client, data)

        cache = client.plugin_cache("projects")
        if cache:
            cache[project.id] = project

        return project


class Task(DatabasePageEntityMixin, BaseEntity):
    """
    Task entity for actionable items.

    Tasks represent individual actionable items with support for:
    - Hierarchical subtasks (parent-child relationships)
    - Project and domain association
    - Tag-based categorization
    - Priority and due date tracking
    - Energy and context metadata

    Attributes:
        id: Task page ID
        title: Task title
        status: Task status (Todo, In Progress, Done, Cancelled, Archived)
        priority: Task priority (Critical, High, Medium, Low)
        due_date: Task due date
        domain_id: Related domain ID
        project_id: Related project ID
        parent_task_id: Parent task ID (for subtasks)
        subtasks_count: Number of subtasks
        tag_ids: List of associated tag IDs
        estimated_time: Estimated time in minutes
        energy_required: Required energy level (High, Medium, Low)
        context: Additional context
        created_date: Task creation date
        completed_date: Task completion date
        archived_date: Task archival date

    Example:
        >>> task = await Task.get("task_id", client=client)
        >>> print(task.title, task.status)
    """

    def __init__(self, client: "NotionClient", data: dict[str, Any]) -> None:
        """Initialize task with client and API data."""
        super().__init__(client, data)
        self._task_cache = client.plugin_cache("tasks")

    # ===== PROPERTIES =====

    @property
    def title(self) -> str:
        """Get task title from title property."""
        title_prop = self._data["properties"].get("Title")
        if title_prop and title_prop.get("type") == "title":
            title_data = title_prop.get("title", [])
            if title_data:
                return title_data[0].get("plain_text", "")
        return ""

    @property
    def status(self) -> str:
        """Get task status."""
        status_prop = self._data["properties"].get("Status")
        if status_prop and status_prop.get("type") == "select":
            select_data = status_prop.get("select")
            if select_data:
                return select_data.get("name", "Todo")
        return "Todo"

    @property
    def priority(self) -> str:
        """Get task priority."""
        priority_prop = self._data["properties"].get("Priority")
        if priority_prop and priority_prop.get("type") == "select":
            select_data = priority_prop.get("select")
            if select_data:
                return select_data.get("name", "Medium")
        return "Medium"

    @property
    def due_date(self) -> datetime | None:
        """Get task due date."""
        due_date_prop = self._data["properties"].get("Due Date")
        if due_date_prop and due_date_prop.get("type") == "date":
            date_data = due_date_prop.get("date")
            if date_data and date_data.get("start"):
                return datetime.fromisoformat(date_data["start"])
        return None

    @property
    def domain_id(self) -> str | None:
        """Get related domain ID."""
        domain_prop = self._data["properties"].get("Domain")
        if domain_prop and domain_prop.get("type") == "relation":
            relation_data = domain_prop.get("relation", [])
            if relation_data:
                return relation_data[0].get("id")
        return None

    @property
    def project_id(self) -> str | None:
        """Get related project ID."""
        project_prop = self._data["properties"].get("Project")
        if project_prop and project_prop.get("type") == "relation":
            relation_data = project_prop.get("relation", [])
            if relation_data:
                return relation_data[0].get("id")
        return None

    @property
    def parent_task_id(self) -> str | None:
        """Get parent task ID."""
        parent_prop = self._data["properties"].get("Parent Task")
        if parent_prop and parent_prop.get("type") == "relation":
            relation_data = parent_prop.get("relation", [])
            if relation_data:
                return relation_data[0].get("id")
        return None

    @property
    def subtasks_count(self) -> int:
        """Get number of subtasks."""
        subtasks_prop = self._data["properties"].get("Subtasks")
        if subtasks_prop and subtasks_prop.get("type") == "rollup":
            rollup_data = subtasks_prop.get("rollup", {})
            if rollup_data.get("type") == "array":
                array_data = rollup_data.get("array", [])
                # Count non-null numbers
                return sum(1 for item in array_data if item.get("type") == "number" and item.get("number") is not None)
        return 0

    @property
    def tag_ids(self) -> list[str]:
        """Get associated tag IDs."""
        tags_prop = self._data["properties"].get("Tags")
        if tags_prop and tags_prop.get("type") == "relation":
            relation_data = tags_prop.get("relation", [])
            return [r.get("id") for r in relation_data if r.get("id")]
        return []

    @property
    def estimated_time(self) -> int | None:
        """Get estimated time in minutes."""
        time_prop = self._data["properties"].get("Estimated Time")
        if time_prop and time_prop.get("type") == "number":
            return time_prop.get("number")
        return None

    @property
    def energy_required(self) -> str | None:
        """Get required energy level."""
        energy_prop = self._data["properties"].get("Energy Required")
        if energy_prop and energy_prop.get("type") == "select":
            select_data = energy_prop.get("select")
            if select_data:
                return select_data.get("name")
        return None

    @property
    def context(self) -> str:
        """Get additional context."""
        context_prop = self._data["properties"].get("Context")
        if context_prop and context_prop.get("type") == "rich_text" or context_prop.get("type") == "text":
            text_data = context_prop.get("rich_text") or context_prop.get("text", [])
            if text_data:
                return text_data[0].get("plain_text", "") if isinstance(text_data, list) else str(text_data)
        return ""

    @property
    def created_date(self) -> datetime | None:
        """Get task creation date."""
        created_prop = self._data["properties"].get("Created Date")
        if created_prop and created_prop.get("type") == "date":
            date_data = created_prop.get("date")
            if date_data and date_data.get("start"):
                return datetime.fromisoformat(date_data["start"])
        return None

    @property
    def completed_date(self) -> datetime | None:
        """Get task completion date."""
        completed_prop = self._data["properties"].get("Completed Date")
        if completed_prop and completed_prop.get("type") == "date":
            date_data = completed_prop.get("date")
            if date_data and date_data.get("start"):
                return datetime.fromisoformat(date_data["start"])
        return None

    @property
    def archived_date(self) -> datetime | None:
        """Get task archival date."""
        archived_prop = self._data["properties"].get("Archived Date")
        if archived_prop and archived_prop.get("type") == "date":
            date_data = archived_prop.get("date")
            if date_data and date_data.get("start"):
                return datetime.fromisoformat(date_data["start"])
        return None

    # ===== AUTONOMOUS METHODS =====

    @classmethod
    async def get(cls, task_id: str, *, client: "NotionClient") -> "Task":
        """Get a task by ID."""
        cache = client.plugin_cache("tasks")
        if cache and task_id in cache:
            return cache[task_id]

        data = await client._api.pages.get(page_id=task_id)
        task = cls(client, data)

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
    ) -> "Task":
        """Create a new task."""
        from better_notion._api.properties import Title, Select, Date, Relation, Number, RichText

        properties: dict[str, Any] = {
            "Title": Title(content=title),
            "Status": Select(name="Status", value=status),
            "Priority": Select(name="Priority", value=priority),
        }

        if due_date:
            properties["Due Date"] = Date(name="Due Date", start=due_date)

        if domain_id:
            properties["Domain"] = Relation("Domain", [domain_id])

        if project_id:
            properties["Project"] = Relation("Project", [project_id])

        if parent_task_id:
            properties["Parent Task"] = Relation("Parent Task", [parent_task_id])

        if tag_ids:
            # Get Tags database ID from config
            config = getattr(client, '_personal_workspace_config', {})
            database_ids = config.get('database_ids', {})
            tags_db_id = database_ids.get('tags')
            if tags_db_id:
                properties["Tags"] = Relation("Tags", tag_ids)

        if estimated_time is not None:
            properties["Estimated Time"] = Number(name="Estimated Time", value=estimated_time)

        if energy_required:
            properties["Energy Required"] = Select(name="Energy Required", value=energy_required)

        if context:
            properties["Context"] = RichText(name="Context", content=context)

        serialized_properties = {
            key: prop.to_dict() if hasattr(prop, 'to_dict') else prop
            for key, prop in properties.items()
        }

        data = await client._api.pages.create(
            parent={"database_id": database_id},
            properties=serialized_properties,
        )

        task = cls(client, data)

        cache = client.plugin_cache("tasks")
        if cache:
            cache[task.id] = task

        return task


class Routine(DatabasePageEntityMixin, BaseEntity):
    """
    Routine entity for habit tracking.

    Routines represent recurring activities with frequency tracking
    and streak management for building consistent habits.

    Attributes:
        id: Routine page ID
        name: Routine name
        frequency: Routine frequency (Daily, Weekly, Weekdays, Weekends)
        domain_id: Related domain ID
        best_time: Best time for routine
        estimated_duration: Estimated duration in minutes
        streak: Current streak count
        last_completed: Last completion date
        total_completions: Total completion count

    Example:
        >>> routine = await Routine.get("routine_id", client=client)
        >>> print(routine.name, routine.streak)
    """

    def __init__(self, client: "NotionClient", data: dict[str, Any]) -> None:
        """Initialize routine with client and API data."""
        super().__init__(client, data)
        self._routine_cache = client.plugin_cache("routines")

    # ===== PROPERTIES =====

    @property
    def name(self) -> str:
        """Get routine name from title property."""
        title_prop = self._data["properties"].get("Name")
        if title_prop and title_prop.get("type") == "title":
            title_data = title_prop.get("title", [])
            if title_data:
                return title_data[0].get("plain_text", "")
        return ""

    @property
    def frequency(self) -> str:
        """Get routine frequency."""
        frequency_prop = self._data["properties"].get("Frequency")
        if frequency_prop and frequency_prop.get("type") == "select":
            select_data = frequency_prop.get("select")
            if select_data:
                return select_data.get("name", "Daily")
        return "Daily"

    @property
    def domain_id(self) -> str | None:
        """Get related domain ID."""
        domain_prop = self._data["properties"].get("Domain")
        if domain_prop and domain_prop.get("type") == "relation":
            relation_data = domain_prop.get("relation", [])
            if relation_data:
                return relation_data[0].get("id")
        return None

    @property
    def best_time(self) -> str:
        """Get best time for routine."""
        time_prop = self._data["properties"].get("Best Time")
        if time_prop and time_prop.get("type") == "rich_text" or time_prop.get("type") == "text":
            text_data = time_prop.get("rich_text") or time_prop.get("text", [])
            if text_data:
                return text_data[0].get("plain_text", "") if isinstance(text_data, list) else str(text_data)
        return ""

    @property
    def estimated_duration(self) -> int | None:
        """Get estimated duration in minutes."""
        duration_prop = self._data["properties"].get("Estimated Duration")
        if duration_prop and duration_prop.get("type") == "number":
            return duration_prop.get("number")
        return None

    @property
    def streak(self) -> int:
        """Get current streak count."""
        streak_prop = self._data["properties"].get("Streak")
        if streak_prop and streak_prop.get("type") == "number":
            return streak_prop.get("number", 0) or 0
        return 0

    @property
    def last_completed(self) -> datetime | None:
        """Get last completion date."""
        last_prop = self._data["properties"].get("Last Completed")
        if last_prop and last_prop.get("type") == "date":
            date_data = last_prop.get("date")
            if date_data and date_data.get("start"):
                return datetime.fromisoformat(date_data["start"])
        return None

    @property
    def total_completions(self) -> int:
        """Get total completion count."""
        total_prop = self._data["properties"].get("Total Completions")
        if total_prop and total_prop.get("type") == "number":
            return total_prop.get("number", 0) or 0
        return 0

    # ===== AUTONOMOUS METHODS =====

    @classmethod
    async def get(cls, routine_id: str, *, client: "NotionClient") -> "Routine":
        """Get a routine by ID."""
        cache = client.plugin_cache("routines")
        if cache and routine_id in cache:
            return cache[routine_id]

        data = await client._api.pages.get(page_id=routine_id)
        routine = cls(client, data)

        if cache:
            cache[routine_id] = routine

        return routine

    @classmethod
    async def create(
        cls,
        *,
        client: "NotionClient",
        database_id: str,
        name: str,
        frequency: str = "Daily",
        domain_id: str | None = None,
        best_time: str = "Anytime",
        estimated_duration: int = 30,
    ) -> "Routine":
        """Create a new routine."""
        from better_notion._api.properties import Title, Select, Relation, Number, RichText

        properties: dict[str, Any] = {
            "Name": Title(content=name),
            "Frequency": Select(name="Frequency", value=frequency),
            "Streak": Number(name="Streak", value=0),
            "Total Completions": Number(name="Total Completions", value=0),
        }

        if domain_id:
            properties["Domain"] = Relation("Domain", [domain_id])

        if best_time:
            properties["Best Time"] = RichText(name="Best Time", content=best_time)

        if estimated_duration:
            properties["Estimated Duration"] = Number(name="Estimated Duration", value=estimated_duration)

        serialized_properties = {
            key: prop.to_dict() if hasattr(prop, 'to_dict') else prop
            for key, prop in properties.items()
        }

        data = await client._api.pages.create(
            parent={"database_id": database_id},
            properties=serialized_properties,
        )

        routine = cls(client, data)

        cache = client.plugin_cache("routines")
        if cache:
            cache[routine.id] = routine

        return routine


class Agenda(DatabasePageEntityMixin, BaseEntity):
    """
    Agenda entity for time-based scheduling.

    Agenda items represent scheduled events, time blocks, and reminders
    for daily planning and time management.

    Attributes:
        id: Agenda page ID
        name: Agenda item name
        date_time: Scheduled date and time
        duration: Duration in minutes
        type: Item type (Event, Time Block, Reminder)
        linked_task_id: Related task ID
        linked_project_id: Related project ID
        location: Location
        notes: Additional notes

    Example:
        >>> agenda = await Agenda.get("agenda_id", client=client)
        >>> print(agenda.name, agenda.date_time)
    """

    def __init__(self, client: "NotionClient", data: dict[str, Any]) -> None:
        """Initialize agenda with client and API data."""
        super().__init__(client, data)
        self._agenda_cache = client.plugin_cache("agenda")

    # ===== PROPERTIES =====

    @property
    def name(self) -> str:
        """Get agenda name from title property."""
        title_prop = self._data["properties"].get("Name")
        if title_prop and title_prop.get("type") == "title":
            title_data = title_prop.get("title", [])
            if title_data:
                return title_data[0].get("plain_text", "")
        return ""

    @property
    def start(self) -> datetime | None:
        """Get start date and time."""
        start_prop = self._data["properties"].get("Start")
        if start_prop and start_prop.get("type") == "date":
            date_data = start_prop.get("date")
            if date_data and date_data.get("start"):
                return datetime.fromisoformat(date_data["start"])
        return None

    @property
    def end(self) -> datetime | None:
        """Get end date and time."""
        end_prop = self._data["properties"].get("End")
        if end_prop and end_prop.get("type") == "date":
            date_data = end_prop.get("date")
            if date_data and date_data.get("start"):
                return datetime.fromisoformat(date_data["start"])
        return None

    @property
    def type(self) -> str:
        """Get agenda item type."""
        type_prop = self._data["properties"].get("Type")
        if type_prop and type_prop.get("type") == "select":
            select_data = type_prop.get("select")
            if select_data:
                return select_data.get("name", "Event")
        return "Event"

    @property
    def linked_task_id(self) -> str | None:
        """Get linked task ID."""
        task_prop = self._data["properties"].get("Linked Task")
        if task_prop and task_prop.get("type") == "relation":
            relation_data = task_prop.get("relation", [])
            if relation_data:
                return relation_data[0].get("id")
        return None

    @property
    def linked_project_id(self) -> str | None:
        """Get linked project ID."""
        project_prop = self._data["properties"].get("Linked Project")
        if project_prop and project_prop.get("type") == "relation":
            relation_data = project_prop.get("relation", [])
            if relation_data:
                return relation_data[0].get("id")
        return None

    @property
    def location(self) -> str:
        """Get location."""
        location_prop = self._data["properties"].get("Location")
        if location_prop and location_prop.get("type") == "rich_text" or location_prop.get("type") == "text":
            text_data = location_prop.get("rich_text") or location_prop.get("text", [])
            if text_data:
                return text_data[0].get("plain_text", "") if isinstance(text_data, list) else str(text_data)
        return ""

    @property
    def notes(self) -> str:
        """Get additional notes."""
        notes_prop = self._data["properties"].get("Notes")
        if notes_prop and notes_prop.get("type") == "rich_text" or notes_prop.get("type") == "text":
            text_data = notes_prop.get("rich_text") or notes_prop.get("text", [])
            if text_data:
                return text_data[0].get("plain_text", "") if isinstance(text_data, list) else str(text_data)
        return ""

    # ===== AUTONOMOUS METHODS =====

    @classmethod
    async def get(cls, agenda_id: str, *, client: "NotionClient") -> "Agenda":
        """Get an agenda item by ID."""
        cache = client.plugin_cache("agenda")
        if cache and agenda_id in cache:
            return cache[agenda_id]

        data = await client._api.pages.get(page_id=agenda_id)
        agenda = cls(client, data)

        if cache:
            cache[agenda.id] = agenda

        return agenda

    @classmethod
    async def create(
        cls,
        *,
        client: "NotionClient",
        database_id: str,
        name: str,
        start: str,
        end: str,
        type_: str = "Event",
        linked_task_id: str | None = None,
        linked_project_id: str | None = None,
        location: str = "",
        notes: str = "",
    ) -> "Agenda":
        """Create a new agenda item."""
        from better_notion._api.properties import Title, Date, Select, Relation, RichText

        properties: dict[str, Any] = {
            "Name": Title(content=name),
            "Start": Date(name="Start", value=start),
            "End": Date(name="End", value=end),
            "Type": Select(name="Type", value=type_),
        }

        if linked_task_id:
            properties["Linked Task"] = Relation("Linked Task", [linked_task_id])

        if linked_project_id:
            properties["Linked Project"] = Relation("Linked Project", [linked_project_id])

        if location:
            properties["Location"] = RichText(name="Location", content=location)

        if notes:
            properties["Notes"] = RichText(name="Notes", content=notes)

        serialized_properties = {
            key: prop.to_dict() if hasattr(prop, 'to_dict') else prop
            for key, prop in properties.items()
        }

        data = await client._api.pages.create(
            parent={"database_id": database_id},
            properties=serialized_properties,
        )

        agenda = cls(client, data)

        cache = client.plugin_cache("agenda")
        if cache:
            cache[agenda.id] = agenda

        return agenda
