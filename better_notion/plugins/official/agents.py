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
            reset: bool = typer.Option(
                False,
                "--reset",
                "-r",
                help="Reset workspace (delete existing databases and recreate)",
            ),
            skip: bool = typer.Option(
                False,
                "--skip",
                "-s",
                help="Skip if workspace already exists (return existing databases)",
            ),
            debug: bool = typer.Option(
                False,
                "--debug",
                "-d",
                help="Enable debug logging",
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

            If a workspace already exists in the page, use --reset to recreate
            or --skip to keep the existing one.

            Example:
                $ notion agents init --parent-page page123 --name "My Workspace"
                $ notion agents init --parent-page page123 --reset  # Recreate
                $ notion agents init --parent-page page123 --skip    # Keep existing
            """
            import asyncio
            import logging
            import sys

            # Enable debug logging if requested
            if debug:
                logging.basicConfig(
                    level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    stream=sys.stderr,
                )
                # Also enable httpx debug logging
                logging.getLogger("httpx").setLevel(logging.DEBUG)

            async def _init() -> str:
                try:
                    client = get_client()
                    initializer = WorkspaceInitializer(client)

                    # Handle --skip flag
                    if skip:
                        from better_notion._sdk.models.page import Page
                        from better_notion.utils.agents.metadata import WorkspaceMetadata

                        try:
                            page = await Page.get(parent_page_id, client=client)
                            existing = await WorkspaceMetadata.detect_workspace(page, client)

                            if existing:
                                database_ids = existing.get("database_ids", {})
                                return format_success(
                                    {
                                        "message": "Workspace already exists, skipping initialization",
                                        "workspace_id": existing.get("workspace_id"),
                                        "databases_found": len(database_ids),
                                        "database_ids": database_ids,
                                    }
                                )
                        except Exception:
                            # If detection fails, proceed with normal init
                            pass

                    # Initialize workspace (with skip_detection=True if --reset)
                    database_ids = await initializer.initialize_workspace(
                        parent_page_id=parent_page_id,
                        workspace_name=workspace_name,
                        skip_detection=reset,  # Skip detection if resetting
                    )

                    return format_success(
                        {
                            "message": "Workspace initialized successfully",
                            "workspace_id": initializer._workspace_id,
                            "databases_created": len(database_ids),
                            "database_ids": database_ids,
                        }
                    )

                except Exception as e:
                    result = format_error("INIT_ERROR", str(e), retry=False)
                    return result

            result = asyncio.run(_init())
            typer.echo(result)

        @agents_app.command("info")
        def workspace_info(
            parent_page_id: str = typer.Option(
                ...,
                "--parent-page",
                "-p",
                help="ID of the parent page to check",
            ),
        ) -> None:
            """
            Show workspace information for a page.

            Displays whether a workspace is initialized in the given page,
            along with workspace metadata and database information.

            Example:
                $ notion agents info --parent-page page123
            """
            import asyncio

            async def _info() -> str:
                try:
                    client = get_client()
                    from better_notion._sdk.models.page import Page
                    from better_notion.utils.agents.metadata import WorkspaceMetadata

                    page = await Page.get(parent_page_id, client=client)
                    existing = await WorkspaceMetadata.detect_workspace(page, client)

                    if existing:
                        database_ids = existing.get("database_ids", {})

                        return format_success(
                            {
                                "message": "Workspace found in this page",
                                "parent_page": parent_page_id,
                                "parent_title": page.title,
                                "workspace_id": existing.get("workspace_id"),
                                "workspace_name": existing.get("workspace_name"),
                                "initialized_at": existing.get("initialized_at"),
                                "databases_count": len(database_ids),
                                "database_ids": database_ids,
                                "detection_method": existing.get("detection_method", "config_file"),
                            }
                        )
                    else:
                        # Search for any databases in the page
                        results = await client.search(
                            query="",
                            filter={"value": "database", "property": "object"}
                        )

                        # Count databases in this page
                        databases_in_page = []
                        for result in results:
                            if hasattr(result, 'title'):
                                databases_in_page.append(result.title)

                        return format_success(
                            {
                                "message": "No agents workspace found in this page",
                                "parent_page": parent_page_id,
                                "parent_title": page.title,
                                "workspace_initialized": False,
                                "other_databases": len(databases_in_page),
                            }
                        )

                except Exception as e:
                    result = format_error("INFO_ERROR", str(e), retry=False)
                    return result

            result = asyncio.run(_info())
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

        # Register the agents app to main CLI FIRST
        app.add_typer(agents_app)

        # Import CLI functions for CRUD commands
        from better_notion.plugins.official import agents_cli

        # Organizations commands (under agents)
        orgs_app = typer.Typer(name="orgs", help="Organizations management commands")

        @orgs_app.command("list")
        def orgs_list_cmd():
            typer.echo(agents_cli.orgs_list())

        @orgs_app.command("get")
        def orgs_get_cmd(org_id: str):
            typer.echo(agents_cli.orgs_get(org_id))

        @orgs_app.command("create")
        def orgs_create_cmd(
            name: str = typer.Option(..., "--name", "-n"),
            slug: str = typer.Option(..., "--slug"),
            description: str = typer.Option("", "--description", "-d"),
            repository_url: str = typer.Option("", "--repository-url"),
            status: str = typer.Option("Active", "--status"),
        ):
            typer.echo(agents_cli.orgs_create(name, slug, description, repository_url, status))

        agents_app.add_typer(orgs_app)

        # Projects commands (under agents)
        projects_app = typer.Typer(name="projects", help="Projects management commands")

        @projects_app.command("list")
        def projects_list_cmd(org_id: str = typer.Option(None, "--org-id", "-o")):
            typer.echo(agents_cli.projects_list(org_id))

        @projects_app.command("get")
        def projects_get_cmd(project_id: str):
            typer.echo(agents_cli.projects_get(project_id))

        @projects_app.command("create")
        def projects_create_cmd(
            name: str = typer.Option(..., "--name", "-n"),
            org_id: str = typer.Option(..., "--org-id", "-o"),
            slug: str = typer.Option("", "--slug"),
            description: str = typer.Option("", "--description", "-d"),
            repository: str = typer.Option("", "--repository"),
            status: str = typer.Option("Active", "--status"),
            tech_stack: str = typer.Option("", "--tech-stack"),
        ):
            typer.echo(agents_cli.projects_create(name, org_id, slug, description, repository, status, tech_stack))

        agents_app.add_typer(projects_app)

        # Versions commands (under agents)
        versions_app = typer.Typer(name="versions", help="Versions management commands")

        @versions_app.command("list")
        def versions_list_cmd(project_id: str = typer.Option(None, "--project-id", "-p")):
            typer.echo(agents_cli.versions_list(project_id))

        @versions_app.command("get")
        def versions_get_cmd(version_id: str):
            typer.echo(agents_cli.versions_get(version_id))

        @versions_app.command("create")
        def versions_create_cmd(
            name: str = typer.Option(..., "--name", "-n"),
            project_id: str = typer.Option(..., "--project-id", "-p"),
            status: str = typer.Option("Planning", "--status"),
            type_: str = typer.Option("Minor", "--type", "-t"),
            branch_name: str = typer.Option("", "--branch-name"),
        ):
            typer.echo(agents_cli.versions_create(name, project_id, status, type_, branch_name))

        agents_app.add_typer(versions_app)

        # Tasks commands (under agents)
        tasks_app = typer.Typer(name="tasks", help="Tasks management commands")

        @tasks_app.command("list")
        def tasks_list_cmd(
            version_id: str = typer.Option(None, "--version-id", "-v"),
            status: str = typer.Option(None, "--status", "-s"),
        ):
            typer.echo(agents_cli.tasks_list(version_id, status))

        @tasks_app.command("get")
        def tasks_get_cmd(task_id: str):
            typer.echo(agents_cli.tasks_get(task_id))

        @tasks_app.command("create")
        def tasks_create_cmd(
            title: str = typer.Option(..., "--title", "-t"),
            version_id: str = typer.Option(..., "--version-id", "-v"),
            type_: str = typer.Option("New Feature", "--type"),
            priority: str = typer.Option("Medium", "--priority"),
            estimated_hours: float = typer.Option(0, "--estimated-hours"),
        ):
            typer.echo(agents_cli.tasks_create(title, version_id, type_, priority, estimated_hours))

        @tasks_app.command("next")
        def tasks_next_cmd(project_id: str = typer.Option(None, "--project-id", "-p")):
            typer.echo(agents_cli.tasks_next(project_id))

        @tasks_app.command("claim")
        def tasks_claim_cmd(task_id: str):
            typer.echo(agents_cli.tasks_claim(task_id))

        @tasks_app.command("start")
        def tasks_start_cmd(task_id: str):
            typer.echo(agents_cli.tasks_start(task_id))

        @tasks_app.command("complete")
        def tasks_complete_cmd(
            task_id: str,
            actual_hours: float = typer.Option(0, "--actual-hours"),
        ):
            typer.echo(agents_cli.tasks_complete(task_id, actual_hours))

        @tasks_app.command("can-start")
        def tasks_can_start_cmd(task_id: str):
            typer.echo(agents_cli.tasks_can_start(task_id))

        agents_app.add_typer(tasks_app)

        # Ideas commands (under agents)
        ideas_app = typer.Typer(name="ideas", help="Ideas management commands")

        @ideas_app.command("list")
        def ideas_list_cmd(
            project_id: str = typer.Option(None, "--project-id", "-p"),
            status: str = typer.Option(None, "--status", "-s"),
        ):
            typer.echo(agents_cli.ideas_list(project_id, status))

        @ideas_app.command("get")
        def ideas_get_cmd(idea_id: str):
            typer.echo(agents_cli.ideas_get(idea_id))

        @ideas_app.command("create")
        def ideas_create_cmd(
            title: str = typer.Option(..., "--title", "-t"),
            project_id: str = typer.Option(None, "--project-id", "-p"),
            category: str = typer.Option("Feature", "--category"),
            description: str = typer.Option("", "--description", "-d"),
            proposed_solution: str = typer.Option("", "--proposed-solution"),
            benefits: str = typer.Option("", "--benefits"),
            effort_estimate: str = typer.Option("Medium", "--effort-estimate"),
            context: str = typer.Option("", "--context"),
        ):
            typer.echo(agents_cli.ideas_create(title, project_id, category, description, proposed_solution, benefits, effort_estimate, context))

        @ideas_app.command("review")
        def ideas_review_cmd(count: int = typer.Option(10, "--count", "-c")):
            typer.echo(agents_cli.ideas_review(count))

        @ideas_app.command("accept")
        def ideas_accept_cmd(idea_id: str):
            typer.echo(agents_cli.ideas_accept(idea_id))

        @ideas_app.command("reject")
        def ideas_reject_cmd(
            idea_id: str,
            reason: str = typer.Option("", "--reason", "-r"),
        ):
            typer.echo(agents_cli.ideas_reject(idea_id, reason))

        agents_app.add_typer(ideas_app)

        # Work Issues commands (under agents)
        work_issues_app = typer.Typer(name="work-issues", help="Work Issues management commands")

        @work_issues_app.command("list")
        def work_issues_list_cmd(
            project_id: str = typer.Option(None, "--project-id", "-p"),
            status: str = typer.Option(None, "--status", "-s"),
        ):
            typer.echo(agents_cli.work_issues_list(project_id, status))

        @work_issues_app.command("get")
        def work_issues_get_cmd(issue_id: str):
            typer.echo(agents_cli.work_issues_get(issue_id))

        @work_issues_app.command("create")
        def work_issues_create_cmd(
            title: str = typer.Option(..., "--title", "-t"),
            project_id: str = typer.Option(None, "--project-id", "-p"),
            task_id: str = typer.Option(None, "--task-id"),
            type_: str = typer.Option("Blocker", "--type"),
            severity: str = typer.Option("Medium", "--severity"),
            description: str = typer.Option("", "--description", "-d"),
            context: str = typer.Option("", "--context"),
            proposed_solution: str = typer.Option("", "--proposed-solution"),
        ):
            typer.echo(agents_cli.work_issues_create(title, project_id, task_id, type_, severity, description, context, proposed_solution))

        @work_issues_app.command("resolve")
        def work_issues_resolve_cmd(
            issue_id: str,
            resolution: str = typer.Option("", "--resolution", "-r"),
        ):
            typer.echo(agents_cli.work_issues_resolve(issue_id, resolution))

        @work_issues_app.command("blockers")
        def work_issues_blockers_cmd(project_id: str):
            typer.echo(agents_cli.work_issues_blockers(project_id))

        agents_app.add_typer(work_issues_app)

        # Incidents commands (under agents)
        incidents_app = typer.Typer(name="incidents", help="Incidents management commands")

        @incidents_app.command("list")
        def incidents_list_cmd(
            project_id: str = typer.Option(None, "--project-id", "-p"),
            severity: str = typer.Option(None, "--severity", "-s"),
        ):
            typer.echo(agents_cli.incidents_list(project_id, severity))

        @incidents_app.command("get")
        def incidents_get_cmd(incident_id: str):
            typer.echo(agents_cli.incidents_get(incident_id))

        @incidents_app.command("create")
        def incidents_create_cmd(
            title: str = typer.Option(..., "--title", "-t"),
            project_id: str = typer.Option(None, "--project-id", "-p"),
            affected_version_id: str = typer.Option(None, "--affected-version-id"),
            severity: str = typer.Option("Medium", "--severity"),
            type_: str = typer.Option("Bug", "--type"),
        ):
            typer.echo(agents_cli.incidents_create(title, project_id, affected_version_id, severity, type_))

        @incidents_app.command("resolve")
        def incidents_resolve_cmd(
            incident_id: str,
            resolution: str = typer.Option("", "--resolution", "-r"),
        ):
            typer.echo(agents_cli.incidents_resolve(incident_id, resolution))

        @incidents_app.command("mttr")
        def incidents_mttr_cmd(
            project_id: str = typer.Option(None, "--project-id", "-p"),
            within_days: int = typer.Option(30, "--within-days", "-d"),
        ):
            typer.echo(agents_cli.incidents_mttr(project_id, within_days))

        @incidents_app.command("sla-violations")
        def incidents_sla_violations_cmd():
            typer.echo(agents_cli.incidents_sla_violations())

        agents_app.add_typer(incidents_app)

    def register_sdk_models(self) -> dict[str, type]:
        """Register workflow entity models."""
        from better_notion.plugins.official.agents_sdk.models import (
            Idea,
            Incident,
            Organization,
            Project,
            Task,
            Version,
            WorkIssue,
        )

        return {
            "Organization": Organization,
            "Project": Project,
            "Version": Version,
            "Task": Task,
            "Idea": Idea,
            "WorkIssue": WorkIssue,
            "Incident": Incident,
        }

    def register_sdk_caches(self, client: NotionClient) -> dict[str, Cache]:
        """Register dedicated caches for workflow entities."""
        return {
            "organizations": Cache(),
            "projects": Cache(),
            "versions": Cache(),
            "tasks": Cache(),
            "ideas": Cache(),
            "work_issues": Cache(),
            "incidents": Cache(),
        }

    def register_sdk_managers(self, client: NotionClient) -> dict:
        """Register custom managers for workflow entities."""
        from better_notion.plugins.official.agents_sdk.managers import (
            IdeaManager,
            IncidentManager,
            OrganizationManager,
            ProjectManager,
            TaskManager,
            VersionManager,
            WorkIssueManager,
        )

        return {
            "organizations": OrganizationManager(client),
            "projects": ProjectManager(client),
            "versions": VersionManager(client),
            "tasks": TaskManager(client),
            "ideas": IdeaManager(client),
            "work_issues": WorkIssueManager(client),
            "incidents": IncidentManager(client),
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
