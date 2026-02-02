"""CLI commands for workflow entities.

This module provides CRUD commands for all workflow entities including
Organizations, Projects, Versions, Tasks, Ideas, Work Issues, and Incidents.
"""

from __future__ import annotations

import asyncio
from typing import Optional

import typer

from better_notion._cli.response import format_error, format_success
from better_notion._sdk.client import NotionClient
from better_notion.utils.agents import get_or_create_agent_id


def get_client() -> NotionClient:
    """Get authenticated Notion client."""
    from better_notion._cli.config import Config

    config = Config.load()
    return NotionClient(auth=config.token, timeout=config.timeout)


def get_workspace_config() -> dict:
    """Get workspace configuration."""
    import json
    from pathlib import Path

    config_path = Path.home() / ".notion" / "workspace.json"
    if not config_path.exists():
        return {}

    with open(config_path) as f:
        return json.load(f)


def register_agents_sdk_plugin(client: NotionClient) -> None:
    """Register the agents SDK plugin with a NotionClient instance.

    This helper function registers all models, caches, and managers
    for the agents workflow system.

    Args:
        client: NotionClient instance
    """
    from better_notion.plugins.official.agents_sdk.plugin import AgentsSDKPlugin

    plugin = AgentsSDKPlugin()
    plugin.initialize(client)

    # Register models, caches, and managers
    models = plugin.register_models()
    caches = plugin.register_caches(client)
    managers = plugin.register_managers(client)
    client.register_sdk_plugin(models=models, caches=caches, managers=managers)


# ===== ORGANIZATIONS =====

def orgs_list() -> str:
    """
    List all organizations.

    Example:
        $ notion orgs list
    """
    async def _list() -> str:
        try:
            client = get_client()

            # Register SDK plugin
            from better_notion.plugins.official.agents_sdk.plugin import AgentsSDKPlugin
            plugin = AgentsSDKPlugin()
            plugin.initialize(client)

            # Register models, caches, and managers
            models = plugin.register_models()
            caches = plugin.register_caches(client)
            managers = plugin.register_managers(client)
            client.register_sdk_plugin(models=models, caches=caches, managers=managers)

            # Get manager
            manager = client.plugin_manager("organizations")
            orgs = await manager.list()

            return format_success({
                "organizations": [
                    {
                        "id": org.id,
                        "name": org.name,
                        "slug": org.slug,
                        "status": org.status,
                    }
                    for org in orgs
                ],
                "total": len(orgs),
            })

        except Exception as e:
            return format_error("LIST_ORGS_ERROR", str(e), retry=False)

    return asyncio.run(_list())


def orgs_get(org_id: str) -> str:
    """
    Get an organization by ID.

    Args:
        org_id: Organization page ID

    Example:
        $ notion orgs get org_123
    """
    async def _get() -> str:
        try:
            client = get_client()

            # Register SDK plugin
            register_agents_sdk_plugin(client)

            # Get organization
            manager = client.plugin_manager("organizations")
            org = await manager.get(org_id)

            return format_success({
                "id": org.id,
                "name": org.name,
                "slug": org.slug,
                "description": org.description,
                "repository_url": org.repository_url,
                "status": org.status,
            })

        except Exception as e:
            return format_error("GET_ORG_ERROR", str(e), retry=False)

    return asyncio.run(_get())


def orgs_create(
    name: str,
    slug: Optional[str] = None,
    description: Optional[str] = None,
    repository_url: Optional[str] = None,
    status: str = "Active",
) -> str:
    """
    Create a new organization.

    Args:
        name: Organization name
        slug: URL-safe identifier (optional)
        description: Organization description (optional)
        repository_url: Code repository URL (optional)
        status: Organization status (default: Active)

    Example:
        $ notion orgs create "My Organization" --slug "my-org"
    """
    async def _create() -> str:
        try:
            client = get_client()

            # Register SDK plugin
            register_agents_sdk_plugin(client)

            # Create organization
            manager = client.plugin_manager("organizations")
            org = await manager.create(
                name=name,
                slug=slug,
                description=description,
                repository_url=repository_url,
                status=status,
            )

            return format_success({
                "message": "Organization created successfully",
                "id": org.id,
                "name": org.name,
                "slug": org.slug,
            })

        except Exception as e:
            return format_error("CREATE_ORG_ERROR", str(e), retry=False)

    return asyncio.run(_create())


# ===== PROJECTS =====

def projects_list(
    org_id: Optional[str] = typer.Option(None, "--org-id", "-o", help="Filter by organization ID"),
) -> str:
    """
    List all projects, optionally filtered by organization.

    Args:
        org_id: Filter by organization ID (optional)

    Example:
        $ notion projects list
        $ notion projects list --org-id org_123
    """
    async def _list() -> str:
        try:
            client = get_client()

            # Register SDK plugin
            register_agents_sdk_plugin(client)

            # Get manager
            manager = client.plugin_manager("projects")
            projects = await manager.list(organization_id=org_id)

            return format_success({
                "projects": [
                    {
                        "id": p.id,
                        "name": p.name,
                        "slug": p.slug,
                        "status": p.status,
                        "role": p.role,
                        "organization_id": p.organization_id,
                    }
                    for p in projects
                ],
                "total": len(projects),
            })

        except Exception as e:
            return format_error("LIST_PROJECTS_ERROR", str(e), retry=False)

    return asyncio.run(_list())


def projects_get(project_id: str) -> str:
    """
    Get a project by ID.

    Args:
        project_id: Project page ID

    Example:
        $ notion projects get proj_123
    """
    async def _get() -> str:
        try:
            client = get_client()

            # Register SDK plugin
            register_agents_sdk_plugin(client)

            # Get project
            manager = client.plugin_manager("projects")
            project = await manager.get(project_id)

            return format_success({
                "id": project.id,
                "name": project.name,
                "slug": project.slug,
                "description": project.description,
                "repository": project.repository,
                "status": project.status,
                "tech_stack": project.tech_stack,
                "role": project.role,
                "organization_id": project.organization_id,
            })

        except Exception as e:
            return format_error("GET_PROJECT_ERROR", str(e), retry=False)

    return asyncio.run(_get())


def projects_create(
    name: str,
    organization_id: str,
    slug: Optional[str] = None,
    description: Optional[str] = None,
    repository: Optional[str] = None,
    status: str = "Active",
    tech_stack: Optional[str] = None,
    role: str = "Developer",
) -> str:
    """
    Create a new project.

    Args:
        name: Project name
        organization_id: Parent organization ID
        slug: URL-safe identifier (optional)
        description: Project description (optional)
        repository: Git repository URL (optional)
        status: Project status (default: Active)
        tech_stack: Comma-separated technologies (optional)
        role: Project role (default: Developer)

    Example:
        $ notion projects create "My Project" org_123 --tech-stack "Python,React"
    """
    async def _create() -> str:
        try:
            client = get_client()

            # Register SDK plugin
            register_agents_sdk_plugin(client)

            # Parse tech stack
            tech_stack_list = tech_stack.split(",") if tech_stack else None

            # Create project
            manager = client.plugin_manager("projects")
            project = await manager.create(
                name=name,
                organization_id=organization_id,
                slug=slug,
                description=description,
                repository=repository,
                status=status,
                tech_stack=tech_stack_list,
                role=role,
            )

            return format_success({
                "message": "Project created successfully",
                "id": project.id,
                "name": project.name,
                "slug": project.slug,
            })

        except Exception as e:
            return format_error("CREATE_PROJECT_ERROR", str(e), retry=False)

    return asyncio.run(_create())


# ===== VERSIONS =====

def versions_list(
    project_id: Optional[str] = typer.Option(None, "--project-id", "-p", help="Filter by project ID"),
) -> str:
    """
    List all versions, optionally filtered by project.

    Args:
        project_id: Filter by project ID (optional)

    Example:
        $ notion versions list
        $ notion versions list --project-id proj_123
    """
    async def _list() -> str:
        try:
            client = get_client()

            # Register SDK plugin
            register_agents_sdk_plugin(client)

            # Get manager
            manager = client.plugin_manager("versions")
            versions = await manager.list(project_id=project_id)

            return format_success({
                "versions": [
                    {
                        "id": v.id,
                        "name": v.name,
                        "status": v.status,
                        "type": v.version_type,
                        "branch_name": v.branch_name,
                        "progress": v.progress,
                        "project_id": v.project_id,
                    }
                    for v in versions
                ],
                "total": len(versions),
            })

        except Exception as e:
            return format_error("LIST_VERSIONS_ERROR", str(e), retry=False)

    return asyncio.run(_list())


def versions_get(version_id: str) -> str:
    """
    Get a version by ID.

    Args:
        version_id: Version page ID

    Example:
        $ notion versions get ver_123
    """
    async def _get() -> str:
        try:
            client = get_client()

            # Register SDK plugin
            register_agents_sdk_plugin(client)

            # Get version
            manager = client.plugin_manager("versions")
            version = await manager.get(version_id)

            return format_success({
                "id": version.id,
                "name": version.name,
                "status": version.status,
                "type": version.version_type,
                "branch_name": version.branch_name,
                "progress": version.progress,
                "project_id": version.project_id,
            })

        except Exception as e:
            return format_error("GET_VERSION_ERROR", str(e), retry=False)

    return asyncio.run(_get())


def versions_create(
    name: str,
    project_id: str,
    status: str = "Planning",
    version_type: str = "Minor",
    branch_name: Optional[str] = None,
    progress: int = 0,
) -> str:
    """
    Create a new version.

    Args:
        name: Version name (e.g., v1.0.0)
        project_id: Parent project ID
        status: Version status (default: Planning)
        version_type: Version type (default: Minor)
        branch_name: Git branch name (optional)
        progress: Progress percentage 0-100 (default: 0)

    Example:
        $ notion versions create "v1.0.0" proj_123 --type Major
    """
    async def _create() -> str:
        try:
            client = get_client()

            # Register SDK plugin
            register_agents_sdk_plugin(client)

            # Create version
            manager = client.plugin_manager("versions")
            version = await manager.create(
                name=name,
                project_id=project_id,
                status=status,
                version_type=version_type,
                branch_name=branch_name,
                progress=progress,
            )

            return format_success({
                "message": "Version created successfully",
                "id": version.id,
                "name": version.name,
            })

        except Exception as e:
            return format_error("CREATE_VERSION_ERROR", str(e), retry=False)

    return asyncio.run(_create())


# ===== TASKS =====

def tasks_list(
    version_id: Optional[str] = typer.Option(None, "--version-id", "-v", help="Filter by version ID"),
    status: Optional[str] = typer.Option(None, "--status", "-s", help="Filter by status"),
) -> str:
    """
    List all tasks, optionally filtered.

    Args:
        version_id: Filter by version ID (optional)
        status: Filter by status (optional)

    Example:
        $ notion tasks list
        $ notion tasks list --version-id ver_123 --status Backlog
    """
    async def _list() -> str:
        try:
            client = get_client()

            # Register SDK plugin
            register_agents_sdk_plugin(client)

            # Get manager
            manager = client.plugin_manager("tasks")
            tasks = await manager.list(version_id=version_id, status=status)

            return format_success({
                "tasks": [
                    {
                        "id": t.id,
                        "title": t.title,
                        "status": t.status,
                        "type": t.task_type,
                        "priority": t.priority,
                        "version_id": t.version_id,
                        "estimated_hours": t.estimated_hours,
                    }
                    for t in tasks
                ],
                "total": len(tasks),
            })

        except Exception as e:
            return format_error("LIST_TASKS_ERROR", str(e), retry=False)

    return asyncio.run(_list())


def tasks_get(task_id: str) -> str:
    """
    Get a task by ID.

    Args:
        task_id: Task page ID

    Example:
        $ notion tasks get task_123
    """
    async def _get() -> str:
        try:
            client = get_client()

            # Register SDK plugin
            register_agents_sdk_plugin(client)

            # Get task
            manager = client.plugin_manager("tasks")
            task = await manager.get(task_id)

            return format_success({
                "id": task.id,
                "title": task.title,
                "status": task.status,
                "type": task.task_type,
                "priority": task.priority,
                "version_id": task.version_id,
                "dependency_ids": task.dependency_ids,
                "estimated_hours": task.estimated_hours,
                "actual_hours": task.actual_hours,
            })

        except Exception as e:
            return format_error("GET_TASK_ERROR", str(e), retry=False)

    return asyncio.run(_get())


def tasks_create(
    title: str,
    version_id: str,
    status: str = "Backlog",
    task_type: str = "New Feature",
    priority: str = "Medium",
    dependencies: Optional[str] = None,
    estimated_hours: Optional[int] = None,
) -> str:
    """
    Create a new task.

    Args:
        title: Task title
        version_id: Parent version ID
        status: Task status (default: Backlog)
        task_type: Task type (default: New Feature)
        priority: Task priority (default: Medium)
        dependencies: Comma-separated dependency task IDs (optional)
        estimated_hours: Estimated hours (optional)

    Example:
        $ notion tasks create "Fix authentication bug" ver_123 --priority High --type "Bug Fix"
    """
    async def _create() -> str:
        try:
            client = get_client()

            # Register SDK plugin
            register_agents_sdk_plugin(client)

            # Parse dependencies
            dependency_ids = dependencies.split(",") if dependencies else None

            # Create task
            manager = client.plugin_manager("tasks")
            task = await manager.create(
                title=title,
                version_id=version_id,
                status=status,
                task_type=task_type,
                priority=priority,
                dependency_ids=dependency_ids,
                estimated_hours=estimated_hours,
            )

            return format_success({
                "message": "Task created successfully",
                "id": task.id,
                "title": task.title,
                "status": task.status,
            })

        except Exception as e:
            return format_error("CREATE_TASK_ERROR", str(e), retry=False)

    return asyncio.run(_create())


# ===== TASK WORKFLOW COMMANDS =====

def tasks_next(
    project_id: Optional[str] = typer.Option(None, "--project-id", "-p", help="Filter by project ID"),
) -> str:
    """
    Find the next available task to work on.

    Finds a task that is:
    - In Backlog or Claimed status
    - Has all dependencies completed

    Args:
        project_id: Filter by project ID (optional)

    Example:
        $ notion tasks next
        $ notion tasks next --project-id proj_123
    """
    async def _next() -> str:
        try:
            client = get_client()

            # Register SDK plugin
            register_agents_sdk_plugin(client)

            # Get manager
            manager = client.plugin_manager("tasks")
            task = await manager.next(project_id=project_id)

            if not task:
                return format_success({
                    "message": "No available tasks found",
                    "task": None,
                })

            return format_success({
                "message": "Found available task",
                "task": {
                    "id": task.id,
                    "title": task.title,
                    "status": task.status,
                    "priority": task.priority,
                    "version_id": task.version_id,
                    "can_start": True,
                },
            })

        except ValueError as e:
            # Specific validation error (e.g., project not found)
            return format_error("VALIDATION_ERROR", str(e), retry=False)
        except Exception as e:
            return format_error("FIND_NEXT_TASK_ERROR", str(e), retry=False)

    return asyncio.run(_next())


def tasks_claim(task_id: str) -> str:
    """
    Claim a task (transition to Claimed status).

    Args:
        task_id: Task page ID

    Example:
        $ notion tasks claim task_123
    """
    async def _claim() -> str:
        try:
            client = get_client()

            # Register SDK plugin
            register_agents_sdk_plugin(client)

            # Get and claim task
            manager = client.plugin_manager("tasks")
            task = await manager.get(task_id)
            await task.claim()

            # Get agent ID for tracking
            agent_id = get_or_create_agent_id()

            return format_success({
                "message": f"Task claimed by agent {agent_id}",
                "task_id": task.id,
                "title": task.title,
                "status": task.status,
                "agent_id": agent_id,
            })

        except Exception as e:
            return format_error("CLAIM_TASK_ERROR", str(e), retry=False)

    return asyncio.run(_claim())


def tasks_start(task_id: str) -> str:
    """
    Start working on a task (transition to In Progress).

    Args:
        task_id: Task page ID

    Example:
        $ notion tasks start task_123
    """
    async def _start() -> str:
        try:
            client = get_client()

            # Register SDK plugin
            register_agents_sdk_plugin(client)

            # Get and start task
            manager = client.plugin_manager("tasks")
            task = await manager.get(task_id)

            # Check if can start
            if not await task.can_start():
                return format_error(
                    "TASK_BLOCKED",
                    "Task has incomplete dependencies",
                    retry=False,
                )

            await task.start()

            # Get agent ID for tracking
            agent_id = get_or_create_agent_id()

            return format_success({
                "message": f"Task started by agent {agent_id}",
                "task_id": task.id,
                "title": task.title,
                "status": task.status,
                "agent_id": agent_id,
            })

        except Exception as e:
            return format_error("START_TASK_ERROR", str(e), retry=False)

    return asyncio.run(_start())


def tasks_complete(
    task_id: str,
    actual_hours: Optional[int] = typer.Option(None, "--actual-hours", "-a", help="Actual hours spent (must be non-negative)"),
) -> str:
    """
    Complete a task (transition to Completed).

    Args:
        task_id: Task page ID
        actual_hours: Actual hours spent (optional, must be non-negative)

    Example:
        $ notion tasks complete task_123 --actual-hours 3
    """
    async def _complete() -> str:
        try:
            # Validate actual_hours parameter if provided
            if actual_hours is not None:
                from better_notion.utils.validators import Validators, ValidationError
                try:
                    Validators.non_negative_float(actual_hours, "actual_hours")
                except ValidationError as e:
                    return format_error("INVALID_PARAMETER", str(e), retry=False)

            client = get_client()

            # Register SDK plugin
            register_agents_sdk_plugin(client)

            # Get and complete task
            manager = client.plugin_manager("tasks")
            task = await manager.get(task_id)
            await task.complete(actual_hours=actual_hours)

            # Get agent ID for tracking
            agent_id = get_or_create_agent_id()

            return format_success({
                "message": f"Task completed by agent {agent_id}",
                "task_id": task.id,
                "title": task.title,
                "status": task.status,
                "actual_hours": task.actual_hours,
                "agent_id": agent_id,
            })

        except Exception as e:
            return format_error("COMPLETE_TASK_ERROR", str(e), retry=False)

    return asyncio.run(_complete())


def tasks_can_start(task_id: str) -> str:
    """
    Check if a task can start (all dependencies completed).

    Args:
        task_id: Task page ID

    Example:
        $ notion tasks can-start task_123
    """
    async def _can_start() -> str:
        try:
            client = get_client()

            # Register SDK plugin
            register_agents_sdk_plugin(client)

            # Get task and check
            manager = client.plugin_manager("tasks")
            task = await manager.get(task_id)
            can_start = await task.can_start()

            if not can_start:
                # Get incomplete dependencies
                incomplete = []
                for dep in await task.dependencies():
                    if dep.status != "Completed":
                        incomplete.append({
                            "id": dep.id,
                            "title": dep.title,
                            "status": dep.status,
                        })

                return format_success({
                    "task_id": task.id,
                    "can_start": False,
                    "incomplete_dependencies": incomplete,
                })

            return format_success({
                "task_id": task.id,
                "can_start": True,
                "message": "All dependencies are completed",
            })

        except Exception as e:
            return format_error("CAN_START_ERROR", str(e), retry=False)

    return asyncio.run(_can_start())


# ===== IDEAS =====

def ideas_list(
    project_id: Optional[str] = None,
    category: Optional[str] = None,
    status: Optional[str] = None,
    effort_estimate: Optional[str] = None,
) -> str:
    """
    List ideas with optional filtering.

    Args:
        project_id: Filter by project ID
        category: Filter by category
        status: Filter by status
        effort_estimate: Filter by effort estimate

    Example:
        $ notion ideas list --project-id proj_123 --status Proposed
    """
    async def _list() -> str:
        try:
            client = get_client()

            # Register SDK plugin
            register_agents_sdk_plugin(client)

            # Get manager and list
            manager = client.plugin_manager("ideas")
            ideas = await manager.list(
                project_id=project_id,
                category=category,
                status=status,
                effort_estimate=effort_estimate,
            )

            return format_success({
                "ideas": [
                    {
                        "id": idea.id,
                        "title": idea.title,
                        "category": idea.category,
                        "status": idea.status,
                        "effort_estimate": idea.effort_estimate,
                    }
                    for idea in ideas
                ],
                "total": len(ideas),
            })

        except Exception as e:
            return format_error("LIST_IDEAS_ERROR", str(e), retry=False)

    return asyncio.run(_list())


def ideas_get(idea_id: str) -> str:
    """
    Get an idea by ID.

    Args:
        idea_id: Idea page ID

    Example:
        $ notion ideas get idea_123
    """
    async def _get() -> str:
        try:
            client = get_client()

            # Register SDK plugin
            register_agents_sdk_plugin(client)

            # Get idea
            from better_notion.plugins.official.agents_sdk.models import Idea
            idea = await Idea.get(idea_id, client=client)

            return format_success({
                "id": idea.id,
                "title": idea.title,
                "category": idea.category,
                "status": idea.status,
                "description": idea.description,
                "effort_estimate": idea.effort_estimate,
                "project_id": idea.project_id,
            })

        except Exception as e:
            return format_error("GET_IDEA_ERROR", str(e), retry=False)

    return asyncio.run(_get())


def ideas_create(
    title: str,
    project_id: str,
    category: str = "enhancement",
    description: str = "",
    proposed_solution: str = "",
    benefits: str = "",
    effort_estimate: str = "M",
    context: str = "",
) -> str:
    """
    Create a new idea.

    Args:
        title: Idea title
        project_id: Project ID
        category: Idea category (enhancement, feature, bugfix, optimization, research)
        description: Detailed description
        proposed_solution: Proposed solution
        benefits: Expected benefits
        effort_estimate: Effort estimate (XS, S, M, L, XL)
        context: Additional context

    Example:
        $ notion ideas create "Add caching" --project-id proj_123 \\
            --category enhancement --effort-estimate M
    """
    async def _create() -> str:
        try:
            client = get_client()

            # Register SDK plugin
            register_agents_sdk_plugin(client)

            # Get workspace config
            workspace_config = get_workspace_config()
            database_id = workspace_config.get("Ideas")

            if not database_id:
                return format_error("NO_DATABASE", "Ideas database not configured", retry=False)

            # Create idea in Notion
            properties = {
                "Title": {"title": [{"text": {"content": title}}]},
                "Project": {"relation": [{"id": project_id}]},
                "Category": {"select": {"name": category}},
                "Status": {"select": {"name": "Proposed"}},
                "Effort Estimate": {"select": {"name": effort_estimate}},
            }

            if description:
                properties["Description"] = {
                    "rich_text": [{"text": {"content": description}}]
                }

            if proposed_solution:
                properties["Proposed Solution"] = {
                    "rich_text": [{"text": {"content": proposed_solution}}]
                }

            if benefits:
                properties["Benefits"] = {
                    "rich_text": [{"text": {"content": benefits}}]
                }

            if context:
                properties["Context"] = {
                    "rich_text": [{"text": {"content": context}}]
                }

            response = await client._api._request(
                "POST",
                "/pages",
                json={
                    "parent": {"database_id": database_id},
                    "properties": properties
                },
            )

            return format_success({
                "message": "Idea created successfully",
                "idea_id": response["id"],
                "title": title,
                "category": category,
            })

        except Exception as e:
            return format_error("CREATE_IDEA_ERROR", str(e), retry=False)

    return asyncio.run(_create())


def ideas_review(count: int = 10) -> str:
    """
    Get a batch of ideas for review, prioritized by effort.

    Args:
        count: Maximum number of ideas to return (must be positive)

    Example:
        $ notion ideas review --count 5
    """
    async def _review() -> str:
        try:
            # Validate count parameter
            from better_notion.utils.validators import Validators, ValidationError
            try:
                Validators.positive_int(count, "count")
            except ValidationError as e:
                return format_error("INVALID_PARAMETER", str(e), retry=False)

            client = get_client()

            # Register SDK plugin
            register_agents_sdk_plugin(client)

            # Get manager and review batch
            manager = client.plugin_manager("ideas")
            ideas = await manager.review_batch(count=count)

            return format_success({
                "ideas_for_review": [
                    {
                        "id": idea.id,
                        "title": idea.title,
                        "category": idea.category,
                        "effort_estimate": idea.effort_estimate,
                        "status": idea.status,
                    }
                    for idea in ideas
                ],
                "total": len(ideas),
            })

        except Exception as e:
            return format_error("REVIEW_IDEAS_ERROR", str(e), retry=False)

    return asyncio.run(_review())


def ideas_accept(idea_id: str) -> str:
    """
    Accept an idea (moves to Accepted status).

    Args:
        idea_id: Idea page ID

    Example:
        $ notion ideas accept idea_123
    """
    async def _accept() -> str:
        try:
            client = get_client()

            # Register SDK plugin
            register_agents_sdk_plugin(client)

            # Get idea and accept
            from better_notion.plugins.official.agents_sdk.models import Idea
            idea = await Idea.get(idea_id, client=client)
            await idea.accept()

            return format_success({
                "message": "Idea accepted successfully",
                "idea_id": idea.id,
                "status": idea.status,
            })

        except Exception as e:
            return format_error("ACCEPT_IDEA_ERROR", str(e), retry=False)

    return asyncio.run(_accept())


def ideas_reject(idea_id: str, reason: str = "") -> str:
    """
    Reject an idea (moves to Rejected status).

    Args:
        idea_id: Idea page ID
        reason: Reason for rejection

    Example:
        $ notion ideas reject idea_123 --reason "Out of scope"
    """
    async def _reject() -> str:
        try:
            client = get_client()

            # Register SDK plugin
            register_agents_sdk_plugin(client)

            # Get idea and reject
            from better_notion.plugins.official.agents_sdk.models import Idea
            idea = await Idea.get(idea_id, client=client)
            await idea.reject(reason)

            return format_success({
                "message": "Idea rejected successfully",
                "idea_id": idea.id,
                "status": idea.status,
                "reason": reason,
            })

        except Exception as e:
            return format_error("REJECT_IDEA_ERROR", str(e), retry=False)

    return asyncio.run(_reject())


# ===== WORK ISSUES =====

def work_issues_list(
    project_id: Optional[str] = None,
    task_id: Optional[str] = None,
    type: Optional[str] = None,
    severity: Optional[str] = None,
    status: Optional[str] = None,
) -> str:
    """
    List work issues with optional filtering.

    Args:
        project_id: Filter by project ID
        task_id: Filter by task ID
        type: Filter by type
        severity: Filter by severity
        status: Filter by status

    Example:
        $ notion work-issues list --project-id proj_123 --severity High
    """
    async def _list() -> str:
        try:
            client = get_client()

            # Register SDK plugin
            register_agents_sdk_plugin(client)

            # Get manager and list
            manager = client.plugin_manager("work_issues")
            issues = await manager.list(
                project_id=project_id,
                task_id=task_id,
                type_=type,
                severity=severity,
                status=status,
            )

            return format_success({
                "work_issues": [
                    {
                        "id": issue.id,
                        "title": issue.title,
                        "type": issue.type,
                        "severity": issue.severity,
                        "status": issue.status,
                    }
                    for issue in issues
                ],
                "total": len(issues),
            })

        except Exception as e:
            return format_error("LIST_WORK_ISSUES_ERROR", str(e), retry=False)

    return asyncio.run(_list())


def work_issues_get(issue_id: str) -> str:
    """
    Get a work issue by ID.

    Args:
        issue_id: Work issue page ID

    Example:
        $ notion work-issues get issue_123
    """
    async def _get() -> str:
        try:
            client = get_client()

            # Register SDK plugin
            register_agents_sdk_plugin(client)

            # Get issue
            from better_notion.plugins.official.agents_sdk.models import WorkIssue
            issue = await WorkIssue.get(issue_id, client=client)

            return format_success({
                "id": issue.id,
                "title": issue.title,
                "type": issue.type,
                "severity": issue.severity,
                "status": issue.status,
                "description": issue.description,
                "project_id": issue.project_id,
                "task_id": issue.task_id,
            })

        except Exception as e:
            return format_error("GET_WORK_ISSUE_ERROR", str(e), retry=False)

    return asyncio.run(_get())


def work_issues_create(
    title: str,
    project_id: str,
    type: str = "Technical",
    severity: str = "Medium",
    description: str = "",
    context: str = "",
    task_id: Optional[str] = None,
) -> str:
    """
    Create a new work issue.

    Args:
        title: Issue title
        project_id: Project ID
        type: Issue type (Technical, Process, Resource, Other)
        severity: Issue severity (Low, Medium, High, Critical)
        description: Detailed description
        context: Additional context
        task_id: Related task ID (optional)

    Example:
        $ notion work-issues create "API error" --project-id proj_123 \\
            --type Technical --severity High
    """
    async def _create() -> str:
        try:
            client = get_client()

            # Register SDK plugin
            register_agents_sdk_plugin(client)

            # Get workspace config
            workspace_config = get_workspace_config()
            database_id = workspace_config.get("Work_issues")

            if not database_id:
                return format_error("NO_DATABASE", "Work Issues database not configured", retry=False)

            # Create issue in Notion
            properties = {
                "Title": {"title": [{"text": {"content": title}}]},
                "Project": {"relation": [{"id": project_id}]},
                "Type": {"select": {"name": type}},
                "Severity": {"select": {"name": severity}},
                "Status": {"select": {"name": "Open"}},
            }

            if description:
                properties["Description"] = {
                    "rich_text": [{"text": {"content": description}}]
                }

            if context:
                properties["Context"] = {
                    "rich_text": [{"text": {"content": context}}]
                }

            if task_id:
                properties["Task"] = {"relation": [{"id": task_id}]}

            response = await client._api._request(
                "POST",
                "/pages",
                json={
                    "parent": {"database_id": database_id},
                    "properties": properties
                },
            )

            return format_success({
                "message": "Work issue created successfully",
                "issue_id": response["id"],
                "title": title,
                "type": type,
                "severity": severity,
            })

        except Exception as e:
            return format_error("CREATE_WORK_ISSUE_ERROR", str(e), retry=False)

    return asyncio.run(_create())


def work_issues_resolve(issue_id: str, resolution: str = "") -> str:
    """
    Resolve a work issue.

    Args:
        issue_id: Work issue page ID
        resolution: Resolution description

    Example:
        $ notion work-issues resolve issue_123 --resolution "Fixed dependency version"
    """
    async def _resolve() -> str:
        try:
            client = get_client()

            # Register SDK plugin
            register_agents_sdk_plugin(client)

            # Get issue and resolve
            from better_notion.plugins.official.agents_sdk.models import WorkIssue
            issue = await WorkIssue.get(issue_id, client=client)
            await issue.resolve()

            return format_success({
                "message": "Work issue resolved successfully",
                "issue_id": issue.id,
                "status": issue.status,
                "resolution": resolution,
            })

        except Exception as e:
            return format_error("RESOLVE_WORK_ISSUE_ERROR", str(e), retry=False)

    return asyncio.run(_resolve())


def work_issues_blockers(project_id: str) -> str:
    """
    Find all blocking work issues for a project.

    Args:
        project_id: Project ID

    Example:
        $ notion work-issues blockers proj_123
    """
    async def _blockers() -> str:
        try:
            client = get_client()

            # Register SDK plugin
            register_agents_sdk_plugin(client)

            # Get manager and find blockers
            manager = client.plugin_manager("work_issues")
            blockers = await manager.find_blockers(project_id)

            return format_success({
                "blocking_issues": [
                    {
                        "id": issue.id,
                        "title": issue.title,
                        "type": issue.type,
                        "severity": issue.severity,
                        "status": issue.status,
                    }
                    for issue in blockers
                ],
                "total": len(blockers),
            })

        except Exception as e:
            return format_error("FIND_BLOCKERS_ERROR", str(e), retry=False)

    return asyncio.run(_blockers())


# ===== INCIDENTS =====

def incidents_list(
    project_id: Optional[str] = None,
    version_id: Optional[str] = None,
    severity: Optional[str] = None,
    status: Optional[str] = None,
) -> str:
    """
    List incidents with optional filtering.

    Args:
        project_id: Filter by project ID
        version_id: Filter by affected version ID
        severity: Filter by severity
        status: Filter by status

    Example:
        $ notion incidents list --project-id proj_123 --severity Critical
    """
    async def _list() -> str:
        try:
            client = get_client()

            # Register SDK plugin
            register_agents_sdk_plugin(client)

            # Get manager and list
            manager = client.plugin_manager("incidents")
            incidents = await manager.list(
                project_id=project_id,
                version_id=version_id,
                severity=severity,
                status=status,
            )

            return format_success({
                "incidents": [
                    {
                        "id": incident.id,
                        "title": incident.title,
                        "severity": incident.severity,
                        "status": incident.status,
                        "type": incident.type,
                    }
                    for incident in incidents
                ],
                "total": len(incidents),
            })

        except Exception as e:
            return format_error("LIST_INCIDENTS_ERROR", str(e), retry=False)

    return asyncio.run(_list())


def incidents_get(incident_id: str) -> str:
    """
    Get an incident by ID.

    Args:
        incident_id: Incident page ID

    Example:
        $ notion incidents get incident_123
    """
    async def _get() -> str:
        try:
            client = get_client()

            # Register SDK plugin
            register_agents_sdk_plugin(client)

            # Get incident
            from better_notion.plugins.official.agents_sdk.models import Incident
            incident = await Incident.get(incident_id, client=client)

            return format_success({
                "id": incident.id,
                "title": incident.title,
                "severity": incident.severity,
                "status": incident.status,
                "type": incident.type,
                "project_id": incident.project_id,
                "affected_version_id": incident.affected_version_id,
                "discovery_date": str(incident.discovery_date) if incident.discovery_date else None,
                "resolved_date": str(incident.resolved_date) if incident.resolved_date else None,
            })

        except Exception as e:
            return format_error("GET_INCIDENT_ERROR", str(e), retry=False)

    return asyncio.run(_get())


def incidents_create(
    title: str,
    project_id: str,
    severity: str = "Medium",
    type: str = "Bug",
    affected_version_id: Optional[str] = None,
    root_cause: str = "",
) -> str:
    """
    Create a new incident.

    Args:
        title: Incident title
        project_id: Project ID
        severity: Incident severity (Low, Medium, High, Critical)
        type: Incident type (Bug, Performance, Security, Data, Other)
        affected_version_id: Affected version ID
        root_cause: Root cause analysis

    Example:
        $ notion incidents create "Production outage" --project-id proj_123 \\
            --severity Critical --type Bug
    """
    async def _create() -> str:
        try:
            client = get_client()

            # Register SDK plugin
            register_agents_sdk_plugin(client)

            # Get workspace config
            workspace_config = get_workspace_config()
            database_id = workspace_config.get("Incidents")

            if not database_id:
                return format_error("NO_DATABASE", "Incidents database not configured", retry=False)

            # Create incident in Notion
            from datetime import datetime, timezone

            properties = {
                "Title": {"title": [{"text": {"content": title}}]},
                "Project": {"relation": [{"id": project_id}]},
                "Severity": {"select": {"name": severity}},
                "Type": {"select": {"name": type}},
                "Status": {"select": {"name": "Active"}},
                "Discovery Date": {
                    "date": {"start": datetime.now(timezone.utc).isoformat()}
                },
            }

            if affected_version_id:
                properties["Affected Version"] = {"relation": [{"id": affected_version_id}]}

            if root_cause:
                properties["Root Cause"] = {
                    "rich_text": [{"text": {"content": root_cause}}]
                }

            response = await client._api._request(
                "POST",
                "/pages",
                json={
                    "parent": {"database_id": database_id},
                    "properties": properties
                },
            )

            return format_success({
                "message": "Incident created successfully",
                "incident_id": response["id"],
                "title": title,
                "severity": severity,
            })

        except Exception as e:
            return format_error("CREATE_INCIDENT_ERROR", str(e), retry=False)

    return asyncio.run(_create())


def incidents_resolve(incident_id: str, resolution: str = "") -> str:
    """
    Resolve an incident.

    Args:
        incident_id: Incident page ID
        resolution: Resolution description

    Example:
        $ notion incidents resolve incident_123 --resolution "Hotfix deployed"
    """
    async def _resolve() -> str:
        try:
            client = get_client()

            # Register SDK plugin
            register_agents_sdk_plugin(client)

            # Get incident and resolve
            from better_notion.plugins.official.agents_sdk.models import Incident
            incident = await Incident.get(incident_id, client=client)
            await incident.resolve()

            return format_success({
                "message": "Incident resolved successfully",
                "incident_id": incident.id,
                "status": incident.status,
                "resolution": resolution,
            })

        except Exception as e:
            return format_error("RESOLVE_INCIDENT_ERROR", str(e), retry=False)

    return asyncio.run(_resolve())


def incidents_mttr(project_id: Optional[str] = None, within_days: int = 30) -> str:
    """
    Calculate Mean Time To Resolve (MTTR) for incidents.

    Args:
        project_id: Filter by project ID (optional)
        within_days: Only consider incidents from last N days (must be positive)

    Example:
        $ notion incidents mttr --project-id proj_123 --within-days 30
    """
    async def _mttr() -> str:
        try:
            # Validate within_days parameter
            from better_notion.utils.validators import Validators, ValidationError
            try:
                Validators.positive_int(within_days, "within_days")
            except ValidationError as e:
                return format_error("INVALID_PARAMETER", str(e), retry=False)

            client = get_client()

            # Register SDK plugin
            register_agents_sdk_plugin(client)

            # Get manager and calculate MTTR
            manager = client.plugin_manager("incidents")
            mttr = await manager.calculate_mttr(
                project_id=project_id,
                within_days=within_days,
            )

            return format_success({
                "mttr_hours": mttr,
                "within_days": within_days,
                "project_id": project_id,
            })

        except Exception as e:
            return format_error("CALCULATE_MTTR_ERROR", str(e), retry=False)

    return asyncio.run(_mttr())


def incidents_sla_violations() -> str:
    """
    Find all incidents that violated SLA.

    SLA: Critical incidents should be resolved within 4 hours.

    Example:
        $ notion incidents sla-violations
    """
    async def _sla_violations() -> str:
        try:
            client = get_client()

            # Register SDK plugin
            register_agents_sdk_plugin(client)

            # Get manager and find violations
            manager = client.plugin_manager("incidents")
            violations = await manager.find_sla_violations()

            return format_success({
                "sla_violations": [
                    {
                        "id": incident.id,
                        "title": incident.title,
                        "severity": incident.severity,
                        "discovery_date": str(incident.discovery_date) if incident.discovery_date else None,
                        "resolved_date": str(incident.resolved_date) if incident.resolved_date else None,
                    }
                    for incident in violations
                ],
                "total": len(violations),
            })

        except Exception as e:
            return format_error("SLA_VIOLATIONS_ERROR", str(e), retry=False)

    return asyncio.run(_sla_violations())
