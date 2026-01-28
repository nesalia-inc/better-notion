"""CLI commands for workflow entities (Organizations, Projects, Versions, Tasks).

This module provides CRUD commands for all Phase 1 workflow entities.
"""

from __future__ import annotations

import asyncio
from typing import Optional

import typer

from better_notion._cli.response import format_error, format_success
from better_notion._sdk.client import NotionClient
from better_notion.utils.agents import ProjectContext, get_or_create_agent_id


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
            client.register_sdk_plugin(plugin)

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
            from better_notion.plugins.official.agents_sdk.plugin import AgentsSDKPlugin
            plugin = AgentsSDKPlugin()
            plugin.initialize(client)
            client.register_sdk_plugin(plugin)

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
            from better_notion.plugins.official.agents_sdk.plugin import AgentsSDKPlugin
            plugin = AgentsSDKPlugin()
            plugin.initialize(client)
            client.register_sdk_plugin(plugin)

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
            from better_notion.plugins.official.agents_sdk.plugin import AgentsSDKPlugin
            plugin = AgentsSDKPlugin()
            plugin.initialize(client)
            client.register_sdk_plugin(plugin)

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
            from better_notion.plugins.official.agents_sdk.plugin import AgentsSDKPlugin
            plugin = AgentsSDKPlugin()
            plugin.initialize(client)
            client.register_sdk_plugin(plugin)

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
    slug: Optional[str] = typer.Option(None, "--slug", "-s", help="URL-safe identifier"),
    description: Optional[str] = typer.Option(None, "--description", "-d", help="Project description"),
    repository: Optional[str] = typer.Option(None, "--repository", "-r", help="Git repository URL"),
    status: str = typer.Option("Active", "--status", help="Project status"),
    tech_stack: Optional[str] = typer.Option(None, "--tech-stack", "-t", help="Comma-separated tech stack"),
    role: str = typer.Option("Developer", "--role", help="Project role"),
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
            from better_notion.plugins.official.agents_sdk.plugin import AgentsSDKPlugin
            plugin = AgentsSDKPlugin()
            plugin.initialize(client)
            client.register_sdk_plugin(plugin)

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
            from better_notion.plugins.official.agents_sdk.plugin import AgentsSDKPlugin
            plugin = AgentsSDKPlugin()
            plugin.initialize(client)
            client.register_sdk_plugin(plugin)

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
            from better_notion.plugins.official.agents_sdk.plugin import AgentsSDKPlugin
            plugin = AgentsSDKPlugin()
            plugin.initialize(client)
            client.register_sdk_plugin(plugin)

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
    status: str = typer.Option("Planning", "--status", help="Version status"),
    version_type: str = typer.Option("Minor", "--type", help="Version type"),
    branch_name: Optional[str] = typer.Option(None, "--branch", "-b", help="Git branch name"),
    progress: int = typer.Option(0, "--progress", "-p", help="Progress percentage (0-100)"),
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
            from better_notion.plugins.official.agents_sdk.plugin import AgentsSDKPlugin
            plugin = AgentsSDKPlugin()
            plugin.initialize(client)
            client.register_sdk_plugin(plugin)

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
            from better_notion.plugins.official.agents_sdk.plugin import AgentsSDKPlugin
            plugin = AgentsSDKPlugin()
            plugin.initialize(client)
            client.register_sdk_plugin(plugin)

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
            from better_notion.plugins.official.agents_sdk.plugin import AgentsSDKPlugin
            plugin = AgentsSDKPlugin()
            plugin.initialize(client)
            client.register_sdk_plugin(plugin)

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
    status: str = typer.Option("Backlog", "--status", help="Task status"),
    task_type: str = typer.Option("New Feature", "--type", help="Task type"),
    priority: str = typer.Option("Medium", "--priority", "-p", help="Task priority"),
    dependencies: Optional[str] = typer.Option(None, "--dependencies", "-d", help="Comma-separated dependency task IDs"),
    estimated_hours: Optional[int] = typer.Option(None, "--estimate", "-e", help="Estimated hours"),
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
            from better_notion.plugins.official.agents_sdk.plugin import AgentsSDKPlugin
            plugin = AgentsSDKPlugin()
            plugin.initialize(client)
            client.register_sdk_plugin(plugin)

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
            from better_notion.plugins.official.agents_sdk.plugin import AgentsSDKPlugin
            plugin = AgentsSDKPlugin()
            plugin.initialize(client)
            client.register_sdk_plugin(plugin)

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
            from better_notion.plugins.official.agents_sdk.plugin import AgentsSDKPlugin
            plugin = AgentsSDKPlugin()
            plugin.initialize(client)
            client.register_sdk_plugin(plugin)

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
            from better_notion.plugins.official.agents_sdk.plugin import AgentsSDKPlugin
            plugin = AgentsSDKPlugin()
            plugin.initialize(client)
            client.register_sdk_plugin(plugin)

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
    actual_hours: Optional[int] = typer.Option(None, "--actual-hours", "-a", help="Actual hours spent"),
) -> str:
    """
    Complete a task (transition to Completed).

    Args:
        task_id: Task page ID
        actual_hours: Actual hours spent (optional)

    Example:
        $ notion tasks complete task_123 --actual-hours 3
    """
    async def _complete() -> str:
        try:
            client = get_client()

            # Register SDK plugin
            from better_notion.plugins.official.agents_sdk.plugin import AgentsSDKPlugin
            plugin = AgentsSDKPlugin()
            plugin.initialize(client)
            client.register_sdk_plugin(plugin)

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
            from better_notion.plugins.official.agents_sdk.plugin import AgentsSDKPlugin
            plugin = AgentsSDKPlugin()
            plugin.initialize(client)
            client.register_sdk_plugin(plugin)

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
