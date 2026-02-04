"""Official personal organization plugin for Better Notion CLI.

This plugin provides comprehensive personal productivity features for managing
tasks, projects, routines, and schedule through Notion with flexible tagging,
powerful search, and archive management.

Features:
    - Workspace initialization (creates all required databases)
    - Task management with multi-level subtasks
    - Project tracking
    - Routine/habit tracking with streaks
    - Agenda and time blocking
    - Flexible tagging system
    - Full-text search with filters
    - Archive management
    - Guided daily/weekly/monthly reviews
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


def get_client() -> NotionClient:
    """Get authenticated Notion client."""
    config = Config.load()
    return NotionClient(auth=config.token, timeout=config.timeout)


class PersonalPlugin(CombinedPluginInterface):
    """
    Official personal organization plugin.

    This plugin provides tools for managing personal productivity through
    Notion databases, enabling task management, project tracking,
    routine habits, and schedule organization.

    CLI Commands:
        - personal init: Initialize a new workspace with all databases
        - personal info: Show workspace information
        - personal tasks: Task management commands
        - personal projects: Project management commands
        - personal routines: Routine/habit tracking
        - personal agenda: Agenda and time blocking
        - personal domains: Domain management
        - personal tags: Tag management
        - personal search: Full-text search
        - personal archive: Archive management
        - personal review: Guided reviews

    SDK Extensions:
        - Domain, Tag, Project, Task, Routine, Agenda models
        - Dedicated caches for each entity type
        - Managers for convenient operations
    """

    def register_commands(self, app: typer.Typer) -> None:
        """Register plugin commands with the CLI app."""
        # Create personal command group
        personal_app = typer.Typer(
            name="personal",
            help="Personal organization commands",
        )

        # Register sub-commands
        @personal_app.command("init")
        def init_workspace(
            parent_page_id: str | None = typer.Option(
                None,
                "--parent-page",
                "-p",
                help="ID of the parent page where databases will be created (auto-detected from existing config if not provided)",
            ),
            workspace_name: str = typer.Option(
                "Personal Workspace",
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
            debug: bool = typer.Option(
                False,
                "--debug",
                "-d",
                help="Enable debug logging",
            ),
        ) -> None:
            """
            Initialize a new workspace with all required databases.

            Creates 6 databases in Notion with proper relationships:
            - Domains
            - Tags
            - Projects
            - Tasks
            - Routines
            - Agenda

            If a workspace already exists in the page, it will be automatically detected and reused.
            Use --reset to recreate the workspace.

            Example:
                $ notion personal init --parent-page page123 --name "My Workspace"
                $ notion personal init --parent-page page123  # Reuse existing workspace
                $ notion personal init                        # Auto-detect from existing config
                $ notion personal init --reset                # Delete and recreate
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
                logging.getLogger("httpx").setLevel(logging.DEBUG)

            async def _init() -> str:
                try:
                    client = get_client()
                    from better_notion.utils.personal.workspace import PersonalWorkspaceInitializer

                    initializer = PersonalWorkspaceInitializer(client)

                    # Determine parent_page to use
                    effective_parent_page: str | None = parent_page_id

                    # Auto-detect parent_page from config if not provided
                    if not effective_parent_page:
                        try:
                            detected_parent_page = PersonalWorkspaceInitializer.load_parent_page()
                            if detected_parent_page:
                                effective_parent_page = detected_parent_page
                        except FileNotFoundError:
                            pass

                    # If we still don't have a parent_page, it's required for first initialization
                    if not effective_parent_page:
                        return format_error(
                            "MISSING_PARENT_PAGE",
                            "No existing workspace found. Please provide --parent-page for first initialization.",
                            retry=False,
                        )

                    # Auto-detect existing workspace
                    from better_notion._sdk.models.page import Page
                    from better_notion.utils.personal.metadata import PersonalWorkspaceMetadata

                    # Only detect if not in reset mode
                    if not reset:
                        try:
                            page = await Page.get(effective_parent_page, client=client)
                            existing = await PersonalWorkspaceMetadata.detect_workspace(page, client)

                            if existing:
                                database_ids = existing.get("database_ids", {})

                                # Save workspace config for subsequent commands
                                initializer._database_ids = database_ids
                                initializer._parent_page_id = effective_parent_page
                                initializer._workspace_id = existing.get("workspace_id")
                                initializer._workspace_name = existing.get("workspace_name", workspace_name)
                                initializer.save_database_ids()

                                return format_success(
                                    {
                                        "message": "Workspace already exists, using existing configuration",
                                        "workspace_id": existing.get("workspace_id"),
                                        "databases_found": len(database_ids),
                                        "database_ids": database_ids,
                                        "config_saved": True,
                                        "parent_page": effective_parent_page,
                                    },
                                )
                        except Exception:
                            # If detection fails, proceed with normal init
                            pass

                    # Initialize workspace (with skip_detection=True if --reset)
                    database_ids = await initializer.initialize_workspace(
                        parent_page_id=effective_parent_page,
                        workspace_name=workspace_name,
                        skip_detection=reset,
                    )

                    return format_success(
                        {
                            "message": "Workspace initialized successfully",
                            "workspace_id": initializer._workspace_id,
                            "databases_created": len(database_ids),
                            "database_ids": database_ids,
                        },
                    )

                except Exception as e:
                    # Get detailed error information
                    error_details = str(e)

                    # Try to extract API response details if available
                    if hasattr(e, 'response'):
                        try:
                            import json
                            response_data = e.response.json()
                            error_details = f"{error_details}\nAPI Response: {json.dumps(response_data, indent=2)}"
                        except:
                            if hasattr(e.response, 'text'):
                                error_details = f"{error_details}\nAPI Response: {e.response.text}"

                    if debug:
                        import traceback
                        error_details = f"{error_details}\nTraceback:\n{traceback.format_exc()}"

                    return format_error("INIT_ERROR", error_details, retry=False)

            result = asyncio.run(_init())
            typer.echo(result)

        @personal_app.command("info")
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
                $ notion personal info --parent-page page123
            """
            import asyncio

            async def _info() -> str:
                try:
                    client = get_client()
                    from better_notion._sdk.models.page import Page
                    from better_notion.utils.personal.metadata import PersonalWorkspaceMetadata

                    page = await Page.get(parent_page_id, client=client)
                    existing = await PersonalWorkspaceMetadata.detect_workspace(page, client)

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
                            }
                        )
                    else:
                        return format_success(
                            {
                                "message": "No personal workspace found in this page",
                                "parent_page": parent_page_id,
                                "parent_title": page.title,
                                "workspace_initialized": False,
                            }
                        )

                except Exception as e:
                    return format_error("INFO_ERROR", str(e), retry=False)

            result = asyncio.run(_info())
            typer.echo(result)

        @personal_app.command("schema")
        def personal_schema(
            format: str = typer.Option(
                "json",
                "--format",
                "-f",
                help="Output format (json, yaml, pretty)",
            ),
        ) -> None:
            """
            Get personal plugin schema for AI agents.

            Returns comprehensive documentation about the personal system including:
            - Concepts (workspace, task, project, routine)
            - Workflows (initialize, create_task, search)
            - Commands documentation (init, info)
            - Best practices and usage examples

            Example:
                $ notion personal schema
                $ notion personal schema --format json
                $ notion personal schema --format yaml
                $ notion personal schema --format pretty
            """
            from better_notion.plugins.official.personal_schema import PERSONAL_SCHEMA
            from better_notion._cli.docs.formatters import (
                format_schema_json,
                format_schema_yaml,
                format_schema_pretty,
            )

            if format == "json":
                typer.echo(format_schema_json(PERSONAL_SCHEMA))
            elif format == "yaml":
                typer.echo(format_schema_yaml(PERSONAL_SCHEMA))
            elif format == "pretty":
                typer.echo(format_schema_pretty(PERSONAL_SCHEMA))
            else:
                result = format_error(
                    "INVALID_FORMAT",
                    f"Unknown format: {format}. Supported formats: json, yaml, pretty",
                    retry=False,
                )
                typer.echo(result)
                raise typer.Exit(code=1)

        # Import CLI functions for CRUD commands
        from better_notion.plugins.official import personal_cli

        # Domains commands (under personal)
        domains_app = typer.Typer(name="domains", help="Domain management commands")

        @domains_app.command("list")
        def domains_list_cmd():
            typer.echo(personal_cli.domains_list())

        @domains_app.command("create")
        def domains_create_cmd(
            name: str = typer.Option(..., "--name", "-n"),
            description: str = typer.Option("", "--description", "-d"),
            color: str = typer.Option("Blue", "--color", "-c"),
        ):
            typer.echo(personal_cli.domains_create(name, description, color))

        personal_app.add_typer(domains_app)

        # Tags commands (under personal)
        tags_app = typer.Typer(name="tags", help="Tag management commands")

        @tags_app.command("list")
        def tags_list_cmd():
            typer.echo(personal_cli.tags_list())

        @tags_app.command("create")
        def tags_create_cmd(
            name: str = typer.Argument(...),
            category: str = typer.Option("Custom", "--category"),
            color: str = typer.Option("Gray", "--color"),
        ):
            typer.echo(personal_cli.tags_create(name, category, color))

        @tags_app.command("get")
        def tags_get_cmd(tag_name: str):
            typer.echo(personal_cli.tags_get(tag_name))

        personal_app.add_typer(tags_app)

        # Tasks sub-commands
        tasks_app = typer.Typer(name="tasks", help="Task management commands")

        @tasks_app.command("add")
        def tasks_add_cmd(
            title: str = typer.Argument(...),
            priority: str = typer.Option("Medium", "--priority", "-p"),
            domain: str = typer.Option(None, "--domain", "-d"),
            project: str = typer.Option(None, "--project"),
            due: str = typer.Option(None, "--due"),
            parent: str = typer.Option(None, "--parent"),
            tags: str = typer.Option(None, "--tags"),
            energy: str = typer.Option(None, "--energy"),
        ):
            typer.echo(personal_cli.tasks_add(title, priority, domain, project, due, parent, tags, energy))

        @tasks_app.command("list")
        def tasks_list_cmd(
            today: bool = typer.Option(False, "--today", "-t"),
            week: bool = typer.Option(False, "--week", "-w"),
            domain: str = typer.Option(None, "--domain", "-d"),
            project: str = typer.Option(None, "--project"),
            status: str = typer.Option(None, "--status", "-s"),
            tag: str = typer.Option(None, "--tag"),
        ):
            typer.echo(personal_cli.tasks_list(today, week, domain, project, status, tag))

        @tasks_app.command("get")
        def tasks_get_cmd(task_id: str):
            typer.echo(personal_cli.tasks_get(task_id))

        @tasks_app.command("update")
        def tasks_update_cmd(
            task_id: str,
            status: str = typer.Option(None, "--status"),
            priority: str = typer.Option(None, "--priority"),
        ):
            typer.echo(personal_cli.tasks_update(task_id, status, priority))

        @tasks_app.command("done")
        def tasks_done_cmd(task_id: str):
            typer.echo(personal_cli.tasks_done(task_id))

        @tasks_app.command("delete")
        def tasks_delete_cmd(task_id: str):
            typer.echo(personal_cli.tasks_delete(task_id))

        @tasks_app.command("subtasks")
        def tasks_subtasks_cmd(task_id: str):
            typer.echo(personal_cli.tasks_subtasks(task_id))

        @tasks_app.command("archive")
        def tasks_archive_cmd(task_id: str):
            typer.echo(personal_cli.tasks_archive(task_id))

        personal_app.add_typer(tasks_app)

        # Projects commands (under personal)
        projects_app = typer.Typer(name="projects", help="Project management commands")

        @projects_app.command("list")
        def projects_list_cmd(domain: str = typer.Option(None, "--domain", "-d")):
            typer.echo(personal_cli.projects_list(domain))

        @projects_app.command("get")
        def projects_get_cmd(project_id: str):
            typer.echo(personal_cli.projects_get(project_id))

        @projects_app.command("create")
        def projects_create_cmd(
            name: str = typer.Option(..., "--name", "-n"),
            domain: str = typer.Option(..., "--domain", "-d"),
            priority: str = typer.Option("Medium", "--priority", "-p"),
            deadline: str = typer.Option(None, "--deadline"),
        ):
            typer.echo(personal_cli.projects_create(name, domain, priority, deadline))

        @projects_app.command("delete")
        def projects_delete_cmd(project_id: str):
            typer.echo(personal_cli.projects_delete(project_id))

        personal_app.add_typer(projects_app)

        # Routines commands (under personal)
        routines_app = typer.Typer(name="routines", help="Routine management commands")

        @routines_app.command("list")
        def routines_list_cmd(domain: str = typer.Option(None, "--domain", "-d")):
            typer.echo(personal_cli.routines_list(domain))

        @routines_app.command("create")
        def routines_create_cmd(
            name: str = typer.Option(..., "--name", "-n"),
            frequency: str = typer.Option("Daily", "--frequency", "-f"),
            domain: str = typer.Option(..., "--domain", "-d"),
            best_time: str = typer.Option("Anytime", "--best-time"),
            duration: int = typer.Option(30, "--duration"),
        ):
            typer.echo(personal_cli.routines_create(name, frequency, domain, best_time, duration))

        @routines_app.command("check")
        def routines_check_cmd(routine_id: str):
            typer.echo(personal_cli.routines_check(routine_id))

        @routines_app.command("stats")
        def routines_stats_cmd(period: str = typer.Option("all", "--period")):
            typer.echo(personal_cli.routines_stats(period))

        personal_app.add_typer(routines_app)

        # Agenda commands (under personal)
        agenda_app = typer.Typer(name="agenda", help="Agenda management commands")

        @agenda_app.command("show")
        def agenda_show_cmd(
            week: bool = typer.Option(False, "--week", "-w"),
        ):
            typer.echo(personal_cli.agenda_show(week))

        @agenda_app.command("add")
        def agenda_add_cmd(
            name: str = typer.Option(..., "--name", "-n"),
            when: str = typer.Option(..., "--when", "-w"),
            duration: int = typer.Option(30, "--duration"),
            location: str = typer.Option("", "--location"),
        ):
            typer.echo(personal_cli.agenda_add(name, when, duration, location))

        @agenda_app.command("timeblock")
        def agenda_timeblock_cmd(
            name: str = typer.Option(..., "--name", "-n"),
            start: str = typer.Option(..., "--start", "-s"),
            duration: int = typer.Option(60, "--duration"),
            type_: str = typer.Option("Time Block", "--type", "-t"),
        ):
            typer.echo(personal_cli.agenda_timeblock(name, start, duration, type_))

        personal_app.add_typer(agenda_app)

        # Search command
        @personal_app.command("search")
        def search_cmd(
            query: str = typer.Argument(...),
            domain: str = typer.Option(None, "--domain", "-d"),
            tag: str = typer.Option(None, "--tag", "-t"),
            status: str = typer.Option(None, "--status", "-s"),
            priority: str = typer.Option(None, "--priority", "-p"),
            limit: int = typer.Option(20, "--limit", "-n"),
        ):
            typer.echo(personal_cli.search(query, domain, tag, status, priority, limit))

        # Archive sub-commands
        archive_app = typer.Typer(name="archive", help="Archive management commands")

        @archive_app.command("tasks")
        def archive_tasks_cmd(
            older_than: int = typer.Option(None, "--older-than"),
            completed_before: str = typer.Option(None, "--completed-before"),
        ):
            typer.echo(personal_cli.archive_tasks(older_than, completed_before))

        @archive_app.command("list")
        def archive_list_cmd(
            domain: str = typer.Option(None, "--domain", "-d"),
            tag: str = typer.Option(None, "--tag", "-t"),
        ):
            typer.echo(personal_cli.archive_list(domain, tag))

        @archive_app.command("restore")
        def archive_restore_cmd(
            task_id: str = typer.Argument(...),
        ):
            typer.echo(personal_cli.archive_restore(task_id))

        @archive_app.command("purge")
        def archive_purge_cmd(
            older_than: int = typer.Option(365, "--older-than"),
        ):
            typer.echo(personal_cli.archive_purge(older_than))

        personal_app.add_typer(archive_app)

        # Review sub-commands
        review_app = typer.Typer(name="review", help="Review commands")

        @review_app.command("daily")
        def review_daily_cmd():
            typer.echo(personal_cli.review_daily())

        @review_app.command("weekly")
        def review_weekly_cmd():
            typer.echo(personal_cli.review_weekly())

        @review_app.command("monthly")
        def review_monthly_cmd():
            typer.echo(personal_cli.review_monthly())

        personal_app.add_typer(review_app)

        # Register the personal app to main CLI
        app.add_typer(personal_app)

    def register_sdk_models(self) -> dict[str, type]:
        """Register personal models."""
        from better_notion.plugins.official.personal_sdk.models import (
            Domain, Tag, Project, Task, Routine, Agenda,
        )
        return {
            "Domain": Domain,
            "Tag": Tag,
            "Project": Project,
            "Task": Task,
            "Routine": Routine,
            "Agenda": Agenda,
        }

    def register_sdk_caches(self, client: NotionClient) -> dict[str, Cache]:
        """Register personal caches."""
        return {
            "domains": Cache(),
            "tags": Cache(),
            "projects": Cache(),
            "tasks": Cache(),
            "routines": Cache(),
            "agenda": Cache(),
        }

    def register_sdk_managers(self, client: NotionClient) -> dict:
        """Register custom managers for personal entities."""
        from better_notion.plugins.official.personal_sdk.managers import (
            DomainManager, TagManager, ProjectManager, TaskManager,
            RoutineManager,
        )
        return {
            "domains": DomainManager(client),
            "tags": TagManager(client),
            "projects": ProjectManager(client),
            "tasks": TaskManager(client),
            "routines": RoutineManager(client),
        }

    def sdk_initialize(self, client: NotionClient) -> None:
        """Initialize plugin resources."""
        import json
        from pathlib import Path

        config_path = Path.home() / ".notion" / "personal.json"

        if config_path.exists():
            with open(config_path) as f:
                client._personal_workspace_config = json.load(f)
        else:
            client._personal_workspace_config = {}

    def get_info(self) -> dict[str, str | bool | list]:
        """Return plugin metadata."""
        return {
            "name": "personal",
            "version": "1.0.0",
            "description": "Personal organization and productivity system",
            "author": "Better Notion Team",
            "official": True,
            "category": "productivity",
        }
