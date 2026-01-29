"""Official agents workflow management plugin for Better Notion CLI.

This plugin provides comprehensive workflow management capabilities for coordinating
AI agents working on software development projects through Notion.

Features:
    - Workspace initialization (creates all required databases)
    - Project context management (.notion files)
    - Role management (set and check current role)
    - Task discovery and execution (claim, start, complete tasks)
    - Idea capture and management
    - Work issue tracking
    - Dependency resolution
"""

from __future__ import annotations

import asyncio
from pathlib import Path
from typing import Optional

import typer

from better_notion._cli.config import Config
from better_notion._cli.response import format_error, format_success
from better_notion._sdk.cache import Cache
from better_notion._sdk.client import NotionClient
from better_notion._sdk.plugins import CombinedPluginInterface
from better_notion.plugins.base import PluginInterface
from better_notion.utils.agents import (
    DependencyResolver,
    ProjectContext,
    RoleManager,
    get_or_create_agent_id,
)
from better_notion.utils.agents.workspace import WorkspaceInitializer, initialize_workspace_command


def get_client() -> NotionClient:
    """Get authenticated Notion client."""
    config = Config.load()
    return NotionClient(auth=config.token, timeout=config.timeout)


class AgentsPlugin(CombinedPluginInterface):
    """
    Official agents workflow management plugin.

    This plugin provides tools for managing software development workflows
    through Notion databases, enabling AI agents to coordinate work on projects.

    CLI Commands:
        - agents init: Initialize a new workspace with all databases
        - agents init-project: Initialize a new project with .notion file
        - agents role: Manage project role
        - orgs: Organizations CRUD commands
        - projects: Projects CRUD commands
        - versions: Versions CRUD commands
        - tasks: Tasks CRUD and workflow commands

    SDK Extensions:
        - Organization, Project, Version, Task models
        - Dedicated caches for each entity type
        - Managers for convenient operations
    """

    def register_commands(self, app: typer.Typer) -> None:
        """Register plugin commands with the CLI app."""
        # Create agents command group
        agents_app = typer.Typer(
            name="agents",
            help="Agents workflow management commands",
        )

        # Register sub-commands
        @agents_app.command("init")
        def init_workspace(
            parent_page_id: str = typer.Option(
                ...,
                "--parent-page",
                "-p",
                help="ID of the parent page where databases will be created",
            ),
            workspace_name: str = typer.Option(
                "Agents Workspace",
                "--name",
                "-n",
                help="Name for the workspace",
            ),
        ) -> None:
            """
            Initialize a new workspace with all required databases.

            Creates 8 databases in Notion with proper relationships:
            - Organizations
            - Projects
            - Versions
            - Tasks
            - Ideas
            - Work Issues
            - Incidents
            - Tags

            Example:
                $ notion agents init --parent-page page123 --name "My Workspace"
            """
            async def _init() -> str:
                try:
                    client = get_client()
                    initializer = WorkspaceInitializer(client)

                    database_ids = await initializer.initialize_workspace(
                        parent_page_id=parent_page_id,
                        workspace_name=workspace_name,
                    )

                    # Save database IDs
                    initializer.save_database_ids()

                    return format_success(
                        {
                            "message": "Workspace initialized successfully",
                            "databases_created": len(database_ids),
                            "database_ids": database_ids,
                        }
                    )

                except Exception as e:
                    return format_error("INIT_ERROR", str(e), retry=False)

            result = asyncio.run(_init())
            typer.echo(result)

        @agents_app.command("init-project")
        def init_project(
            project_id: str = typer.Option(
                ...,
                "--project-id",
                "-i",
                help="Notion page ID for the project",
            ),
            project_name: str = typer.Option(
                ...,
                "--name",
                "-n",
                help="Project name",
            ),
            org_id: str = typer.Option(
                ...,
                "--org-id",
                "-o",
                help="Notion page ID for the organization",
            ),
            role: str = typer.Option(
                "Developer",
                "--role",
                "-r",
                help="Project role (default: Developer)",
            ),
        ) -> None:
            """
            Initialize a new project with a .notion file.

            Creates a .notion file in the current directory that identifies
            the project context for all CLI commands.

            Example:
                $ notion agents init-project \\
                    --project-id page123 \\
                    --name "My Project" \\
                    --org-id org456 \\
                    --role Developer
            """
            try:
                # Validate role
                if not RoleManager.is_valid_role(role):
                    return format_error(
                        "INVALID_ROLE",
                        f"Invalid role: {role}. Valid roles: {', '.join(RoleManager.get_all_roles())}",
                        retry=False,
                    )

                # Create .notion file
                context = ProjectContext.create(
                    project_id=project_id,
                    project_name=project_name,
                    org_id=org_id,
                    role=role,
                    path=Path.cwd(),
                )

                return format_success(
                    {
                        "message": "Project initialized successfully",
                        "project_id": context.project_id,
                        "project_name": context.project_name,
                        "org_id": context.org_id,
                        "role": context.role,
                        "notion_file": str(Path.cwd() / ".notion"),
                    }
                )

            except Exception as e:
                return format_error("INIT_PROJECT_ERROR", str(e), retry=False)

        # Role management commands
        role_app = typer.Typer(
            name="role",
            help="Role management commands",
        )
        agents_app.add_typer(role_app)

        @role_app.command("be")
        def role_be(
            new_role: str = typer.Argument(..., help="Role to set"),
            path: Optional[Path] = typer.Option(
                None, "--path", "-p", help="Path to project directory (default: cwd)"
            ),
        ) -> None:
            """
            Set the project role.

            Updates the role in the .notion file. The role determines what
            actions the agent can perform in this project.

            Example:
                $ notion agents role be PM
                $ notion agents role be Developer --path /path/to/project
            """
            try:
                # Validate role
                if not RoleManager.is_valid_role(new_role):
                    return format_error(
                        "INVALID_ROLE",
                        f"Invalid role: {new_role}. Valid roles: {', '.join(RoleManager.get_all_roles())}",
                        retry=False,
                    )

                # Load project context
                if path:
                    context = ProjectContext.from_path(path)
                else:
                    context = ProjectContext.from_current_directory()

                if not context:
                    return format_error(
                        "NO_PROJECT_CONTEXT",
                        "No .notion file found. Are you in a project directory?",
                        retry=False,
                    )

                # Update role
                context.update_role(new_role, path=path or None)

                return format_success(
                    {
                        "message": f"Role updated to {new_role}",
                        "previous_role": context.role,
                        "new_role": new_role,
                    }
                )

            except Exception as e:
                return format_error("ROLE_UPDATE_ERROR", str(e), retry=False)

        @role_app.command("whoami")
        def role_whoami(
            path: Optional[Path] = typer.Option(
                None, "--path", "-p", help="Path to project directory (default: cwd)"
            ),
        ) -> None:
            """
            Show the current project role.

            Displays the role from the .notion file in the current or
            specified project directory.

            Example:
                $ notion agents role whoami
                $ notion agents role whoami --path /path/to/project
            """
            try:
                # Load project context
                if path:
                    context = ProjectContext.from_path(path)
                else:
                    context = ProjectContext.from_current_directory()

                if not context:
                    return format_error(
                        "NO_PROJECT_CONTEXT",
                        "No .notion file found. Are you in a project directory?",
                        retry=False,
                    )

                # Get role description
                description = RoleManager.get_role_description(context.role)

                return format_success(
                    {
                        "role": context.role,
                        "description": description,
                        "project": context.project_name,
                        "permissions": RoleManager.get_permissions(context.role),
                    }
                )

            except Exception as e:
                return format_error("ROLE_ERROR", str(e), retry=False)

        @role_app.command("list")
        def role_list() -> None:
            """
            List all available roles.

            Shows all valid roles that can be used in the workflow system.

            Example:
                $ notion agents role list
            """
            try:
                roles = RoleManager.get_all_roles()

                role_info = []
                for role in roles:
                    description = RoleManager.get_role_description(role)
                    permissions = RoleManager.get_permissions(role)
                    role_info.append(
                        {
                            "role": role,
                            "description": description,
                            "permission_count": len(permissions),
                        }
                    )

                return format_success(
                    {
                        "roles": role_info,
                        "total": len(roles),
                    }
                )

            except Exception as e:
                return format_error("ROLE_LIST_ERROR", str(e), retry=False)

        # Register agents app to main CLI
        app.add_typer(agents_app)

        # Import and register CRUD commands
        from better_notion.plugins.official import agents_cli

        # Organizations commands
        orgs_app = typer.Typer(name="orgs", help="Organizations management commands")
        orgs_app.command("list")(agents_cli.orgs_list)
        orgs_app.command("get")(agents_cli.orgs_get)
        orgs_app.command("create")(agents_cli.orgs_create)
        app.add_typer(orgs_app)

        # Projects commands
        projects_app = typer.Typer(name="projects", help="Projects management commands")
        projects_app.command("list")(projects_list_with_cli := lambda **kwargs: agents_cli.projects_list(**kwargs))
        projects_app.command("get")(projects_get_with_cli := lambda project_id: agents_cli.projects_get(project_id))
        projects_app.command("create")(lambda **kwargs: agents_cli.projects_create(**kwargs))
        app.add_typer(projects_app)

        # Versions commands
        versions_app = typer.Typer(name="versions", help="Versions management commands")
        versions_app.command("list")(lambda **kwargs: agents_cli.versions_list(**kwargs))
        versions_app.command("get")(lambda version_id: agents_cli.versions_get(version_id))
        versions_app.command("create")(lambda **kwargs: agents_cli.versions_create(**kwargs))
        app.add_typer(versions_app)

        # Tasks commands
        tasks_app = typer.Typer(name="tasks", help="Tasks management commands")
        tasks_app.command("list")(lambda **kwargs: agents_cli.tasks_list(**kwargs))
        tasks_app.command("get")(lambda task_id: agents_cli.tasks_get(task_id))
        tasks_app.command("create")(lambda **kwargs: agents_cli.tasks_create(**kwargs))
        tasks_app.command("next")(lambda **kwargs: agents_cli.tasks_next(**kwargs))
        tasks_app.command("claim")(lambda task_id: agents_cli.tasks_claim(task_id))
        tasks_app.command("start")(lambda task_id: agents_cli.tasks_start(task_id))
        tasks_app.command("complete")(lambda **kwargs: agents_cli.tasks_complete(**kwargs))
        tasks_app.command("can-start")(lambda task_id: agents_cli.tasks_can_start(task_id))
        app.add_typer(tasks_app)

    def register_sdk_models(self) -> dict[str, type]:
        """Register workflow entity models."""
        from better_notion.plugins.official.agents_sdk.models import (
            Organization,
            Project,
            Task,
            Version,
        )

        return {
            "Organization": Organization,
            "Project": Project,
            "Version": Version,
            "Task": Task,
        }

    def register_sdk_caches(self, client: NotionClient) -> dict[str, Cache]:
        """Register dedicated caches for workflow entities."""
        return {
            "organizations": Cache(),
            "projects": Cache(),
            "versions": Cache(),
            "tasks": Cache(),
        }

    def register_sdk_managers(self, client: NotionClient) -> dict:
        """Register custom managers for workflow entities."""
        from better_notion.plugins.official.agents_sdk.managers import (
            OrganizationManager,
            ProjectManager,
            TaskManager,
            VersionManager,
        )

        return {
            "organizations": OrganizationManager(client),
            "projects": ProjectManager(client),
            "versions": VersionManager(client),
            "tasks": TaskManager(client),
        }

    def sdk_initialize(self, client: NotionClient) -> None:
        """Initialize plugin resources."""
        import json
        from pathlib import Path

        config_path = Path.home() / ".notion" / "workspace.json"

        if config_path.exists():
            with open(config_path) as f:
                client._workspace_config = json.load(f)
        else:
            client._workspace_config = {}

    def get_info(self) -> dict[str, str | bool | list]:
        """Return plugin metadata."""
        return {
            "name": "agents",
            "version": "1.0.0",
            "description": "Workflow management system for AI agents coordinating on software development projects",
            "author": "Better Notion Team",
            "official": True,
            "category": "workflow",
            "dependencies": [],
        }
