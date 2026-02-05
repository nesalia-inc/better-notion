"""CLI functions for personal organization plugin.

This module provides all the CLI command implementations for the personal
organization plugin, including tasks, projects, routines, agenda, domains,
tags, search, archive, and reviews.
"""

from __future__ import annotations

import asyncio
import json
from datetime import date, datetime, timedelta
from pathlib import Path

from better_notion._cli.config import Config
from better_notion._cli.response import format_error, format_success
from better_notion._sdk.client import NotionClient


def get_client() -> NotionClient:
    """Get authenticated Notion client."""
    config = Config.load()
    return NotionClient(auth=config.token, timeout=config.timeout)


def get_workspace_config() -> dict:
    """Get workspace configuration."""
    config_path = Path.home() / ".notion" / "personal.json"
    if config_path.exists():
        with open(config_path) as f:
            return json.load(f)
    return {}


# ===== DOMAINS =====

def domains_list() -> str:
    """List all domains."""
    async def _list() -> str:
        try:
            client = get_client()
            config = get_workspace_config()
            database_ids = config.get("database_ids", {})
            domains_db_id = database_ids.get("domains")

            if not domains_db_id:
                return format_error("NOT_INITIALIZED", "Personal workspace not initialized. Run 'notion personal init' first.", retry=False)

            from better_notion.plugins.official.personal_sdk.models import Domain

            response = await client._api.databases.query(database_id=domains_db_id)

            domains = [Domain(client, page_data) for page_data in response.get("results", [])]

            return format_success({
                "domains": [
                    {
                        "id": d.id,
                        "name": d.name,
                        "description": d.description,
                        "color": d.color,
                    }
                    for d in domains
                ],
                "count": len(domains),
            })

        except Exception as e:
            return format_error("DOMAINS_LIST_ERROR", str(e), retry=False)

    return asyncio.run(_list())


def domains_create(name: str, description: str, color: str) -> str:
    """Create a new domain."""
    async def _create() -> str:
        try:
            client = get_client()
            config = get_workspace_config()
            database_ids = config.get("database_ids", {})
            domains_db_id = database_ids.get("domains")

            if not domains_db_id:
                return format_error("NOT_INITIALIZED", "Personal workspace not initialized. Run 'notion personal init' first.", retry=False)

            from better_notion.plugins.official.personal_sdk.models import Domain

            domain = await Domain.create(
                client=client,
                database_id=domains_db_id,
                name=name,
                description=description,
                color=color,
            )

            return format_success({
                "message": "Domain created successfully",
                "domain": {
                    "id": domain.id,
                    "name": domain.name,
                    "description": domain.description,
                    "color": domain.color,
                },
            })

        except Exception as e:
            return format_error("DOMAIN_CREATE_ERROR", str(e), retry=False)

    return asyncio.run(_create())


# ===== TAGS =====

def tags_list() -> str:
    """List all tags."""
    async def _list() -> str:
        try:
            client = get_client()
            config = get_workspace_config()
            database_ids = config.get("database_ids", {})
            tags_db_id = database_ids.get("tags")

            if not tags_db_id:
                return format_error("NOT_INITIALIZED", "Personal workspace not initialized. Run 'notion personal init' first.", retry=False)

            from better_notion.plugins.official.personal_sdk.models import Tag

            response = await client._api.databases.query(database_id=tags_db_id)

            tags = [Tag(client, page_data) for page_data in response.get("results", [])]

            return format_success({
                "tags": [
                    {
                        "id": t.id,
                        "name": t.name,
                        "color": t.color,
                        "category": t.category,
                        "description": t.description,
                    }
                    for t in tags
                ],
                "count": len(tags),
            })

        except Exception as e:
            return format_error("TAGS_LIST_ERROR", str(e), retry=False)

    return asyncio.run(_list())


def tags_create(name: str, category: str, color: str) -> str:
    """Create a new tag."""
    async def _create() -> str:
        try:
            client = get_client()
            config = get_workspace_config()
            database_ids = config.get("database_ids", {})
            tags_db_id = database_ids.get("tags")

            if not tags_db_id:
                return format_error("NOT_INITIALIZED", "Personal workspace not initialized. Run 'notion personal init' first.", retry=False)

            from better_notion.plugins.official.personal_sdk.models import Tag

            tag = await Tag.create(
                client=client,
                database_id=tags_db_id,
                name=name,
                color=color,
                category=category,
            )

            return format_success({
                "message": "Tag created successfully",
                "tag": {
                    "id": tag.id,
                    "name": tag.name,
                    "color": tag.color,
                    "category": tag.category,
                },
            })

        except Exception as e:
            return format_error("TAG_CREATE_ERROR", str(e), retry=False)

    return asyncio.run(_create())


def tags_get(tag_name: str) -> str:
    """Get a tag by name."""
    async def _get() -> str:
        try:
            client = get_client()
            config = get_workspace_config()
            database_ids = config.get("database_ids", {})
            tags_db_id = database_ids.get("tags")

            if not tags_db_id:
                return format_error("NOT_INITIALIZED", "Personal workspace not initialized. Run 'notion personal init' first.", retry=False)

            from better_notion.plugins.official.personal_sdk.models import Tag

            response = await client._api.databases.query(
                database_id=tags_db_id,
                filter={
                    "property": "Name",
                    "title": {"equals": tag_name},
                },
            )

            results = response.get("results", [])
            if not results:
                return format_error("TAG_NOT_FOUND", f"Tag '{tag_name}' not found", retry=False)

            tag = Tag(client, results[0])

            return format_success({
                "tag": {
                    "id": tag.id,
                    "name": tag.name,
                    "color": tag.color,
                    "category": tag.category,
                    "description": tag.description,
                },
            })

        except Exception as e:
            return format_error("TAG_GET_ERROR", str(e), retry=False)

    return asyncio.run(_get())


# ===== TASKS =====

def tasks_add(
    title: str,
    priority: str,
    domain: str | None,
    project: str | None,
    due: str | None,
    parent: str | None,
    tags: str | None,
    energy: str | None,
) -> str:
    """Add a new task."""
    async def _add() -> str:
        try:
            client = get_client()
            config = get_workspace_config()
            database_ids = config.get("database_ids", {})
            tasks_db_id = database_ids.get("tasks")

            if not tasks_db_id:
                return format_error("NOT_INITIALIZED", "Personal workspace not initialized. Run 'notion personal init' first.", retry=False)

            # Resolve domain ID if provided
            domain_id = None
            if domain:
                domain_id = await _resolve_domain_id(client, domain)
                if not domain_id:
                    return format_error("DOMAIN_NOT_FOUND", f"Domain '{domain}' not found", retry=False)

            # Resolve project ID if provided
            project_id = None
            if project:
                project_id = await _resolve_project_id(client, project)
                if not project_id:
                    return format_error("PROJECT_NOT_FOUND", f"Project '{project}' not found", retry=False)

            # Resolve parent task ID if provided
            parent_task_id = None
            if parent:
                parent_task_id = await _resolve_task_id(client, parent)
                if not parent_task_id:
                    return format_error("PARENT_TASK_NOT_FOUND", f"Parent task '{parent}' not found", retry=False)

            # Resolve tag IDs if provided
            tag_ids = None
            if tags:
                tag_names = [t.strip() for t in tags.split(",")]
                tag_ids = await _resolve_tag_ids(client, tag_names)

            from better_notion.plugins.official.personal_sdk.models import Task

            task = await Task.create(
                client=client,
                database_id=tasks_db_id,
                title=title,
                priority=priority,
                due_date=due,
                domain_id=domain_id,
                project_id=project_id,
                parent_task_id=parent_task_id,
                tag_ids=tag_ids,
                energy_required=energy,
            )

            return format_success({
                "message": "Task created successfully",
                "task": {
                    "id": task.id,
                    "title": task.title,
                    "status": task.status,
                    "priority": task.priority,
                },
            })

        except Exception as e:
            return format_error("TASK_CREATE_ERROR", str(e), retry=False)

    return asyncio.run(_add())


def tasks_list(
    today: bool,
    week: bool,
    domain: str | None,
    project: str | None,
    status: str | None,
    tag: str | None,
) -> str:
    """List tasks with filters."""
    async def _list() -> str:
        try:
            client = get_client()
            config = get_workspace_config()
            database_ids = config.get("database_ids", {})
            tasks_db_id = database_ids.get("tasks")

            if not tasks_db_id:
                return format_error("NOT_INITIALIZED", "Personal workspace not initialized. Run 'notion personal init' first.", retry=False)

            from better_notion.plugins.official.personal_sdk.models import Task

            # Build filters
            filters = []

            # Filter out archived tasks by default
            filters.append({
                "property": "Status",
                "select": {"does_not_equal": "Archived"},
            })

            if today:
                today_str = date.today().isoformat()
                filters.append({
                    "property": "Due Date",
                    "date": {"equals": today_str},
                })

            if week:
                today_date = date.today()
                week_end = today_date + timedelta(days=7)
                filters.append({
                    "property": "Due Date",
                    "date": {
                        "on_or_before": week_end.isoformat(),
                    },
                })

            if status:
                filters.append({
                    "property": "Status",
                    "select": {"equals": status},
                })

            if domain:
                domain_id = await _resolve_domain_id(client, domain)
                if domain_id:
                    filters.append({
                        "property": "Domain",
                        "relation": {"contains": domain_id},
                    })

            if project:
                project_id = await _resolve_project_id(client, project)
                if project_id:
                    filters.append({
                        "property": "Project",
                        "relation": {"contains": project_id},
                    })

            if tag:
                tag_id = await _resolve_tag_id(client, tag)
                if tag_id:
                    filters.append({
                        "property": "Tags",
                        "relation": {"contains": tag_id},
                    })

            filter_dict = {"and": filters} if len(filters) > 1 else (filters[0] if filters else None)

            # Build query params dynamically (filter is optional)
            query_params = {"database_id": tasks_db_id}
            if filter_dict:
                query_params["filter"] = filter_dict

            response = await client._api.databases.query(**query_params)

            tasks = [Task(client, page_data) for page_data in response.get("results", [])]

            return format_success({
                "tasks": [
                    {
                        "id": t.id,
                        "title": t.title,
                        "status": t.status,
                        "priority": t.priority,
                        "due_date": t.due_date.isoformat() if t.due_date else None,
                    }
                    for t in tasks
                ],
                "count": len(tasks),
            })

        except Exception as e:
            return format_error("TASKS_LIST_ERROR", str(e), retry=False)

    return asyncio.run(_list())


def tasks_get(task_id: str) -> str:
    """Get a task by ID."""
    async def _get() -> str:
        try:
            client = get_client()
            from better_notion.plugins.official.personal_sdk.models import Task

            task = await Task.get(task_id, client=client)

            # Get related data
            domain_name = None
            if task.domain_id:
                domain = await Task.get(task.domain_id, client=client)
                domain_name = domain.title if hasattr(domain, 'title') else None

            return format_success({
                "task": {
                    "id": task.id,
                    "title": task.title,
                    "status": task.status,
                    "priority": task.priority,
                    "due_date": task.due_date.isoformat() if task.due_date else None,
                    "domain_id": task.domain_id,
                    "project_id": task.project_id,
                    "parent_task_id": task.parent_task_id,
                    "subtasks_count": task.subtasks_count,
                    "tag_ids": task.tag_ids,
                    "estimated_time": task.estimated_time,
                    "energy_required": task.energy_required,
                    "context": task.context,
                },
            })

        except Exception as e:
            return format_error("TASK_GET_ERROR", str(e), retry=False)

    return asyncio.run(_get())


def tasks_update(task_id: str, status: str | None, priority: str | None) -> str:
    """Update a task."""
    async def _update() -> str:
        try:
            client = get_client()
            from better_notion._api.properties import Select
            from better_notion.plugins.official.personal_sdk.models import Task

            task = await Task.get(task_id, client=client)

            properties = {}

            if status:
                properties["Status"] = Select(name="Status", value=status)
                # Set completed date if marking as done
                if status == "Done":
                    from better_notion._api.properties import Date
                    from datetime import datetime
                    properties["Completed Date"] = Date(name="Completed Date", start=datetime.now().isoformat())

            if priority:
                properties["Priority"] = Select(name="Priority", value=priority)

            if properties:
                serialized_properties = {
                    key: prop.to_dict() if hasattr(prop, 'to_dict') else prop
                    for key, prop in properties.items()
                }

                data = await client._api.pages.update(
                    page_id=task_id,
                    properties=serialized_properties,
                )

                # Update task data
                task._data = data

            return format_success({
                "message": "Task updated successfully",
                "task": {
                    "id": task.id,
                    "title": task.title,
                    "status": task.status,
                    "priority": task.priority,
                },
            })

        except Exception as e:
            return format_error("TASK_UPDATE_ERROR", str(e), retry=False)

    return asyncio.run(_update())


def tasks_done(task_id: str) -> str:
    """Mark a task as done."""
    return tasks_update(task_id, status="Done", priority=None)


def tasks_delete(task_id: str) -> str:
    """Delete a task."""
    async def _delete() -> str:
        try:
            client = get_client()

            await client._api.pages.delete(page_id=task_id)

            return format_success({
                "message": "Task deleted successfully",
                "task_id": task_id,
            })

        except Exception as e:
            return format_error("TASK_DELETE_ERROR", str(e), retry=False)

    return asyncio.run(_delete())


def tasks_subtasks(task_id: str) -> str:
    """Get subtasks of a task."""
    async def _subtasks() -> str:
        try:
            client = get_client()
            config = get_workspace_config()
            database_ids = config.get("database_ids", {})
            tasks_db_id = database_ids.get("tasks")

            if not tasks_db_id:
                return format_error("NOT_INITIALIZED", "Personal workspace not initialized. Run 'notion personal init' first.", retry=False)

            from better_notion.plugins.official.personal_sdk.models import Task

            response = await client._api.databases.query(
                database_id=tasks_db_id,
                filter={
                    "property": "Parent Task",
                    "relation": {"contains": task_id},
                },
            )

            subtasks = [Task(client, page_data) for page_data in response.get("results", [])]

            return format_success({
                "subtasks": [
                    {
                        "id": t.id,
                        "title": t.title,
                        "status": t.status,
                        "priority": t.priority,
                    }
                    for t in subtasks
                ],
                "count": len(subtasks),
            })

        except Exception as e:
            return format_error("SUBTASKS_GET_ERROR", str(e), retry=False)

    return asyncio.run(_subtasks())


def tasks_archive(task_id: str) -> str:
    """Archive a task."""
    async def _archive() -> str:
        try:
            client = get_client()
            from better_notion._api.properties import Select, Date
            from better_notion.plugins.official.personal_sdk.models import Task

            # First check if task exists
            task = await Task.get(task_id, client=client)

            properties = {
                "Status": Select(name="Status", value="Archived"),
                "Archived Date": Date(name="Archived Date", start=datetime.now().isoformat()),
            }

            serialized_properties = {
                key: prop.to_dict() if hasattr(prop, 'to_dict') else prop
                for key, prop in properties.items()
            }

            await client._api.pages.update(
                page_id=task_id,
                properties=serialized_properties,
            )

            return format_success({
                "message": "Task archived successfully",
                "task_id": task_id,
            })

        except Exception as e:
            return format_error("TASK_ARCHIVE_ERROR", str(e), retry=False)

    return asyncio.run(_archive())


# ===== PROJECTS =====

def projects_list(domain: str | None) -> str:
    """List all projects."""
    async def _list() -> str:
        try:
            client = get_client()
            config = get_workspace_config()
            database_ids = config.get("database_ids", {})
            projects_db_id = database_ids.get("projects")

            if not projects_db_id:
                return format_error("NOT_INITIALIZED", "Personal workspace not initialized. Run 'notion personal init' first.", retry=False)

            from better_notion.plugins.official.personal_sdk.models import Project

            filter_dict = None
            if domain:
                domain_id = await _resolve_domain_id(client, domain)
                if domain_id:
                    filter_dict = {
                        "property": "Domain",
                        "relation": {"contains": domain_id},
                    }

            # Build query params dynamically (filter is optional)
            query_params = {"database_id": projects_db_id}
            if filter_dict:
                query_params["filter"] = filter_dict

            response = await client._api.databases.query(**query_params)

            projects = [Project(client, page_data) for page_data in response.get("results", [])]

            return format_success({
                "projects": [
                    {
                        "id": p.id,
                        "name": p.name,
                        "status": p.status,
                        "priority": p.priority,
                        "deadline": p.deadline.isoformat() if p.deadline else None,
                        "progress": p.progress,
                    }
                    for p in projects
                ],
                "count": len(projects),
            })

        except Exception as e:
            return format_error("PROJECTS_LIST_ERROR", str(e), retry=False)

    return asyncio.run(_list())


def projects_get(project_id: str) -> str:
    """Get a project by ID."""
    async def _get() -> str:
        try:
            client = get_client()
            from better_notion.plugins.official.personal_sdk.models import Project

            project = await Project.get(project_id, client=client)

            return format_success({
                "project": {
                    "id": project.id,
                    "name": project.name,
                    "status": project.status,
                    "priority": project.priority,
                    "deadline": project.deadline.isoformat() if project.deadline else None,
                    "progress": project.progress,
                    "goal": project.goal,
                    "notes": project.notes,
                },
            })

        except Exception as e:
            return format_error("PROJECT_GET_ERROR", str(e), retry=False)

    return asyncio.run(_get())


def projects_create(name: str, domain: str, priority: str, deadline: str | None) -> str:
    """Create a new project."""
    async def _create() -> str:
        try:
            client = get_client()
            config = get_workspace_config()
            database_ids = config.get("database_ids", {})
            projects_db_id = database_ids.get("projects")

            if not projects_db_id:
                return format_error("NOT_INITIALIZED", "Personal workspace not initialized. Run 'notion personal init' first.", retry=False)

            # Resolve domain ID
            domain_id = await _resolve_domain_id(client, domain)
            if not domain_id:
                return format_error("DOMAIN_NOT_FOUND", f"Domain '{domain}' not found", retry=False)

            from better_notion.plugins.official.personal_sdk.models import Project

            project = await Project.create(
                client=client,
                database_id=projects_db_id,
                name=name,
                domain_id=domain_id,
                priority=priority,
                deadline=deadline,
            )

            return format_success({
                "message": "Project created successfully",
                "project": {
                    "id": project.id,
                    "name": project.name,
                    "status": project.status,
                    "priority": project.priority,
                },
            })

        except Exception as e:
            return format_error("PROJECT_CREATE_ERROR", str(e), retry=False)

    return asyncio.run(_create())


def projects_delete(project_id: str) -> str:
    """Delete a project."""
    async def _delete() -> str:
        try:
            client = get_client()

            await client._api.pages.delete(page_id=project_id)

            return format_success({
                "message": "Project deleted successfully",
                "project_id": project_id,
            })

        except Exception as e:
            return format_error("PROJECT_DELETE_ERROR", str(e), retry=False)

    return asyncio.run(_delete())


# ===== ROUTINES =====

def routines_list(domain: str | None) -> str:
    """List all routines."""
    async def _list() -> str:
        try:
            client = get_client()
            config = get_workspace_config()
            database_ids = config.get("database_ids", {})
            routines_db_id = database_ids.get("routines")

            if not routines_db_id:
                return format_error("NOT_INITIALIZED", "Personal workspace not initialized. Run 'notion personal init' first.", retry=False)

            from better_notion.plugins.official.personal_sdk.models import Routine

            filter_dict = None
            if domain:
                domain_id = await _resolve_domain_id(client, domain)
                if domain_id:
                    filter_dict = {
                        "property": "Domain",
                        "relation": {"contains": domain_id},
                    }

            # Build query params dynamically (filter is optional)
            query_params = {"database_id": routines_db_id}
            if filter_dict:
                query_params["filter"] = filter_dict

            response = await client._api.databases.query(**query_params)

            routines = [Routine(client, page_data) for page_data in response.get("results", [])]

            return format_success({
                "routines": [
                    {
                        "id": r.id,
                        "name": r.name,
                        "frequency": r.frequency,
                        "streak": r.streak,
                        "best_time": r.best_time,
                        "last_completed": r.last_completed.isoformat() if r.last_completed else None,
                    }
                    for r in routines
                ],
                "count": len(routines),
            })

        except Exception as e:
            return format_error("ROUTINES_LIST_ERROR", str(e), retry=False)

    return asyncio.run(_list())


def routines_create(name: str, frequency: str, domain: str, best_time: str, duration: int) -> str:
    """Create a new routine."""
    async def _create() -> str:
        try:
            client = get_client()
            config = get_workspace_config()
            database_ids = config.get("database_ids", {})
            routines_db_id = database_ids.get("routines")

            if not routines_db_id:
                return format_error("NOT_INITIALIZED", "Personal workspace not initialized. Run 'notion personal init' first.", retry=False)

            # Resolve domain ID
            domain_id = await _resolve_domain_id(client, domain)
            if not domain_id:
                return format_error("DOMAIN_NOT_FOUND", f"Domain '{domain}' not found", retry=False)

            from better_notion.plugins.official.personal_sdk.models import Routine

            routine = await Routine.create(
                client=client,
                database_id=routines_db_id,
                name=name,
                frequency=frequency,
                domain_id=domain_id,
                best_time=best_time,
                estimated_duration=duration,
            )

            return format_success({
                "message": "Routine created successfully",
                "routine": {
                    "id": routine.id,
                    "name": routine.name,
                    "frequency": routine.frequency,
                },
            })

        except Exception as e:
            return format_error("ROUTINE_CREATE_ERROR", str(e), retry=False)

    return asyncio.run(_create())


def routines_check(routine_id: str) -> str:
    """Check off a routine (increment completions)."""
    async def _check() -> str:
        try:
            client = get_client()
            from better_notion._api.properties import Number, Date
            from better_notion.plugins.official.personal_sdk.models import Routine

            routine = await Routine.get(routine_id, client=client)

            # Increment streak and total completions
            new_streak = routine.streak + 1
            new_total = routine.total_completions + 1

            properties = {
                "Streak": Number(name="Streak", number=new_streak),
                "Total Completions": Number(name="Total Completions", number=new_total),
                "Last Completed": Date(name="Last Completed", start=datetime.now().isoformat()),
            }

            serialized_properties = {
                key: prop.to_dict() if hasattr(prop, 'to_dict') else prop
                for key, prop in properties.items()
            }

            await client._api.pages.update(
                page_id=routine_id,
                properties=serialized_properties,
            )

            return format_success({
                "message": "Routine checked successfully",
                "routine_id": routine_id,
                "streak": new_streak,
                "total_completions": new_total,
            })

        except Exception as e:
            return format_error("ROUTINE_CHECK_ERROR", str(e), retry=False)

    return asyncio.run(_check())


def routines_stats(period: str) -> str:
    """Get routine statistics."""
    async def _stats() -> str:
        try:
            client = get_client()
            config = get_workspace_config()
            database_ids = config.get("database_ids", {})
            routines_db_id = database_ids.get("routines")

            if not routines_db_id:
                return format_error("NOT_INITIALIZED", "Personal workspace not initialized. Run 'notion personal init' first.", retry=False)

            from better_notion.plugins.official.personal_sdk.models import Routine

            response = await client._api.databases.query(database_id=routines_db_id)

            routines = [Routine(client, page_data) for page_data in response.get("results", [])]

            total_completions = sum(r.total_completions for r in routines)
            active_streaks = sum(1 for r in routines if r.streak > 0)

            return format_success({
                "period": period,
                "total_routines": len(routines),
                "total_completions": total_completions,
                "active_streaks": active_streaks,
                "routines": [
                    {
                        "name": r.name,
                        "streak": r.streak,
                        "total_completions": r.total_completions,
                    }
                    for r in routines
                ],
            })

        except Exception as e:
            return format_error("ROUTINES_STATS_ERROR", str(e), retry=False)

    return asyncio.run(_stats())


# ===== AGENDA =====

def agenda_show(week: bool) -> str:
    """Show agenda items."""
    async def _show() -> str:
        try:
            client = get_client()
            config = get_workspace_config()
            database_ids = config.get("database_ids", {})
            agenda_db_id = database_ids.get("agenda")

            if not agenda_db_id:
                return format_error("NOT_INITIALIZED", "Personal workspace not initialized. Run 'notion personal init' first.", retry=False)

            from better_notion.plugins.official.personal_sdk.models import Agenda

            # Build date filter
            today_date = date.today()
            if week:
                end_date = today_date + timedelta(days=7)
                filter_dict = {
                    "property": "Date & Time",
                    "date": {
                        "on_or_before": end_date.isoformat(),
                    },
                }
            else:
                filter_dict = {
                    "property": "Date & Time",
                    "date": {
                        "on_or_before": today_date.isoformat(),
                    },
                }

            response = await client._api.databases.query(
                database_id=agenda_db_id,
                filter=filter_dict,
                sorts=[{
                    "property": "Date & Time",
                    "direction": "ascending",
                }],
            )

            agenda_items = [Agenda(client, page_data) for page_data in response.get("results", [])]

            return format_success({
                "agenda": [
                    {
                        "id": a.id,
                        "name": a.name,
                        "date_time": a.date_time.isoformat() if a.date_time else None,
                        "duration": a.duration,
                        "type": a.type,
                    }
                    for a in agenda_items
                ],
                "count": len(agenda_items),
            })

        except Exception as e:
            return format_error("AGENDA_SHOW_ERROR", str(e), retry=False)

    return asyncio.run(_show())


def agenda_add(name: str, when: str, duration: int, location: str) -> str:
    """Add an agenda item."""
    async def _add() -> str:
        try:
            client = get_client()
            config = get_workspace_config()
            database_ids = config.get("database_ids", {})
            agenda_db_id = database_ids.get("agenda")

            if not agenda_db_id:
                return format_error("NOT_INITIALIZED", "Personal workspace not initialized. Run 'notion personal init' first.", retry=False)

            from better_notion.plugins.official.personal_sdk.models import Agenda

            item = await Agenda.create(
                client=client,
                database_id=agenda_db_id,
                name=name,
                date_time=when,
                duration=duration,
                type_="Event",
                location=location,
            )

            return format_success({
                "message": "Agenda item created successfully",
                "item": {
                    "id": item.id,
                    "name": item.name,
                    "date_time": item.date_time.isoformat() if item.date_time else None,
                },
            })

        except Exception as e:
            return format_error("AGENDA_CREATE_ERROR", str(e), retry=False)

    return asyncio.run(_add())


def agenda_timeblock(name: str, start: str, duration: int, type_: str) -> str:
    """Add a time block to agenda."""
    async def _timeblock() -> str:
        try:
            client = get_client()
            config = get_workspace_config()
            database_ids = config.get("database_ids", {})
            agenda_db_id = database_ids.get("agenda")

            if not agenda_db_id:
                return format_error("NOT_INITIALIZED", "Personal workspace not initialized. Run 'notion personal init' first.", retry=False)

            from better_notion.plugins.official.personal_sdk.models import Agenda

            item = await Agenda.create(
                client=client,
                database_id=agenda_db_id,
                name=name,
                date_time=start,
                duration=duration,
                type_=type_,
            )

            return format_success({
                "message": "Time block created successfully",
                "item": {
                    "id": item.id,
                    "name": item.name,
                    "date_time": item.date_time.isoformat() if item.date_time else None,
                    "type": item.type,
                },
            })

        except Exception as e:
            return format_error("TIMEBLOCK_CREATE_ERROR", str(e), retry=False)

    return asyncio.run(_timeblock())


# ===== SEARCH =====

def search(query: str, domain: str | None, tag: str | None, status: str | None, priority: str | None, limit: int) -> str:
    """Search across tasks, projects, and routines."""
    async def _search() -> str:
        try:
            client = get_client()
            config = get_workspace_config()
            database_ids = config.get("database_ids", {})

            results = {
                "tasks": [],
                "projects": [],
                "routines": [],
            }

            # Search tasks
            tasks_db_id = database_ids.get("tasks")
            if tasks_db_id:
                from better_notion.plugins.official.personal_sdk.models import Task

                response = await client._api.databases.query(
                    database_id=tasks_db_id,
                    filter={
                        "property": "Title",
                        "title": {"contains": query},
                    },
                )

                tasks = [Task(client, page_data) for page_data in response.get("results", [])]
                results["tasks"] = [
                    {
                        "id": t.id,
                        "title": t.title,
                        "status": t.status,
                        "priority": t.priority,
                    }
                    for t in tasks[:limit]
                ]

            # Search projects
            projects_db_id = database_ids.get("projects")
            if projects_db_id:
                from better_notion.plugins.official.personal_sdk.models import Project

                response = await client._api.databases.query(
                    database_id=projects_db_id,
                    filter={
                        "property": "Name",
                        "title": {"contains": query},
                    },
                )

                projects = [Project(client, page_data) for page_data in response.get("results", [])]
                results["projects"] = [
                    {
                        "id": p.id,
                        "name": p.name,
                        "status": p.status,
                    }
                    for p in projects[:limit]
                ]

            # Search routines
            routines_db_id = database_ids.get("routines")
            if routines_db_id:
                from better_notion.plugins.official.personal_sdk.models import Routine

                response = await client._api.databases.query(
                    database_id=routines_db_id,
                    filter={
                        "property": "Name",
                        "title": {"contains": query},
                    },
                )

                routines = [Routine(client, page_data) for page_data in response.get("results", [])]
                results["routines"] = [
                    {
                        "id": r.id,
                        "name": r.name,
                        "frequency": r.frequency,
                    }
                    for r in routines[:limit]
                ]

            total_results = len(results["tasks"]) + len(results["projects"]) + len(results["routines"])

            return format_success({
                "query": query,
                "total_results": total_results,
                "results": results,
            })

        except Exception as e:
            return format_error("SEARCH_ERROR", str(e), retry=False)

    return asyncio.run(_search())


# ===== ARCHIVE =====

def archive_tasks(older_than: int | None, completed_before: str | None) -> str:
    """Archive old completed tasks."""
    async def _archive() -> str:
        try:
            client = get_client()
            config = get_workspace_config()
            database_ids = config.get("database_ids", {})
            tasks_db_id = database_ids.get("tasks")

            if not tasks_db_id:
                return format_error("NOT_INITIALIZED", "Personal workspace not initialized. Run 'notion personal init' first.", retry=False)

            from better_notion._api.properties import Select, Date
            from better_notion.plugins.official.personal_sdk.models import Task

            # Build filter for completed tasks
            filters = [
                {
                    "property": "Status",
                    "select": {"equals": "Done"},
                },
            ]

            if completed_before:
                filters.append({
                    "property": "Completed Date",
                    "date": {"on_or_before": completed_before},
                })

            filter_dict = {"and": filters} if len(filters) > 1 else filters[0]

            response = await client._api.databases.query(
                database_id=tasks_db_id,
                filter=filter_dict,
            )

            tasks = [Task(client, page_data) for page_data in response.get("results", [])]

            archived_count = 0
            for task in tasks:
                # Check if task is old enough
                if older_than and task.completed_date:
                    days_old = (date.today() - task.completed_date.date()).days
                    if days_old < older_than:
                        continue

                # Archive the task
                properties = {
                    "Status": Select(name="Status", value="Archived"),
                    "Archived Date": Date(name="Archived Date", start=datetime.now().isoformat()),
                }

                serialized_properties = {
                    key: prop.to_dict() if hasattr(prop, 'to_dict') else prop
                    for key, prop in properties.items()
                }

                await client._api.pages.update(
                    page_id=task.id,
                    properties=serialized_properties,
                )
                archived_count += 1

            return format_success({
                "message": f"Archived {archived_count} tasks",
                "archived_count": archived_count,
            })

        except Exception as e:
            return format_error("ARCHIVE_TASKS_ERROR", str(e), retry=False)

    return asyncio.run(_archive())


def archive_list(domain: str | None, tag: str | None) -> str:
    """List archived tasks."""
    async def _list() -> str:
        try:
            client = get_client()
            config = get_workspace_config()
            database_ids = config.get("database_ids", {})
            tasks_db_id = database_ids.get("tasks")

            if not tasks_db_id:
                return format_error("NOT_INITIALIZED", "Personal workspace not initialized. Run 'notion personal init' first.", retry=False)

            from better_notion.plugins.official.personal_sdk.models import Task

            # Filter for archived tasks
            filters = [
                {
                    "property": "Status",
                    "select": {"equals": "Archived"},
                },
            ]

            if domain:
                domain_id = await _resolve_domain_id(client, domain)
                if domain_id:
                    filters.append({
                        "property": "Domain",
                        "relation": {"contains": domain_id},
                    })

            if tag:
                tag_id = await _resolve_tag_id(client, tag)
                if tag_id:
                    filters.append({
                        "property": "Tags",
                        "relation": {"contains": tag_id},
                    })

            filter_dict = {"and": filters} if len(filters) > 1 else filters[0]

            response = await client._api.databases.query(
                database_id=tasks_db_id,
                filter=filter_dict,
            )

            tasks = [Task(client, page_data) for page_data in response.get("results", [])]

            return format_success({
                "archived_tasks": [
                    {
                        "id": t.id,
                        "title": t.title,
                        "archived_date": t.archived_date.isoformat() if t.archived_date else None,
                    }
                    for t in tasks
                ],
                "count": len(tasks),
            })

        except Exception as e:
            return format_error("ARCHIVE_LIST_ERROR", str(e), retry=False)

    return asyncio.run(_list())


def archive_restore(task_id: str) -> str:
    """Restore an archived task."""
    async def _restore() -> str:
        try:
            client = get_client()
            from better_notion._api.properties import Select
            from better_notion.plugins.official.personal_sdk.models import Task

            # Verify task is archived
            task = await Task.get(task_id, client=client)
            if task.status != "Archived":
                return format_error("NOT_ARCHIVED", "Task is not archived", retry=False)

            # Restore task
            properties = {
                "Status": Select(name="Status", value="Done"),
            }

            serialized_properties = {
                key: prop.to_dict() if hasattr(prop, 'to_dict') else prop
                for key, prop in properties.items()
            }

            await client._api.pages.update(
                page_id=task_id,
                properties=serialized_properties,
            )

            return format_success({
                "message": "Task restored successfully",
                "task_id": task_id,
            })

        except Exception as e:
            return format_error("ARCHIVE_RESTORE_ERROR", str(e), retry=False)

    return asyncio.run(_restore())


def archive_purge(older_than: int) -> str:
    """Permanently delete old archived tasks."""
    async def _purge() -> str:
        try:
            client = get_client()
            config = get_workspace_config()
            database_ids = config.get("database_ids", {})
            tasks_db_id = database_ids.get("tasks")

            if not tasks_db_id:
                return format_error("NOT_INITIALIZED", "Personal workspace not initialized. Run 'notion personal init' first.", retry=False)

            from better_notion.plugins.official.personal_sdk.models import Task

            # Filter for archived tasks
            filter_dict = {
                "property": "Status",
                "select": {"equals": "Archived"},
            }

            response = await client._api.databases.query(
                database_id=tasks_db_id,
                filter=filter_dict,
            )

            tasks = [Task(client, page_data) for page_data in response.get("results", [])]

            purged_count = 0
            for task in tasks:
                # Check if task is old enough
                if task.archived_date:
                    days_old = (date.today() - task.archived_date.date()).days
                    if days_old >= older_than:
                        await client._api.pages.delete(page_id=task.id)
                        purged_count += 1

            return format_success({
                "message": f"Purged {purged_count} archived tasks",
                "purged_count": purged_count,
            })

        except Exception as e:
            return format_error("ARCHIVE_PURGE_ERROR", str(e), retry=False)

    return asyncio.run(_purge())


# ===== REVIEWS =====

def review_daily() -> str:
    """Generate daily review."""
    async def _review() -> str:
        try:
            client = get_client()
            config = get_workspace_config()
            database_ids = config.get("database_ids", {})

            today_str = date.today().isoformat()

            # Get today's tasks
            tasks_db_id = database_ids.get("tasks")
            today_tasks = []
            completed_today = []
            overdue_tasks = []

            if tasks_db_id:
                from better_notion.plugins.official.personal_sdk.models import Task

                # Today's tasks
                response = await client._api.databases.query(
                    database_id=tasks_db_id,
                    filter={
                        "property": "Due Date",
                        "date": {"equals": today_str},
                    },
                )
                today_tasks = [Task(client, page_data) for page_data in response.get("results", [])]

                # Completed today
                response = await client._api.databases.query(
                    database_id=tasks_db_id,
                    filter={
                        "and": [
                            {"property": "Status", "select": {"equals": "Done"}},
                            {"property": "Completed Date", "date": {"equals": today_str}},
                        ],
                    },
                )
                completed_today = [Task(client, page_data) for page_data in response.get("results", [])]

                # Overdue
                response = await client._api.databases.query(
                    database_id=tasks_db_id,
                    filter={
                        "and": [
                            {"property": "Status", "select": {"does_not_equal": "Done"}},
                            {"property": "Due Date", "date": {"on_or_before": today_str}},
                        ],
                    },
                )
                overdue_tasks = [Task(client, page_data) for page_data in response.get("results", [])]

            return format_success({
                "message": "Daily review",
                "date": today_str,
                "summary": {
                    "tasks_due_today": len(today_tasks),
                    "completed_today": len(completed_today),
                    "overdue": len(overdue_tasks),
                },
                "tasks_due": [t.title for t in today_tasks],
                "completed": [t.title for t in completed_today],
                "overdue": [t.title for t in overdue_tasks],
            })

        except Exception as e:
            return format_error("DAILY_REVIEW_ERROR", str(e), retry=False)

    return asyncio.run(_review())


def review_weekly() -> str:
    """Generate weekly review."""
    async def _review() -> str:
        try:
            client = get_client()
            config = get_workspace_config()
            database_ids = config.get("database_ids", {})

            today_date = date.today()
            week_start = today_date - timedelta(days=today_date.weekday())
            week_end = week_start + timedelta(days=6)

            tasks_db_id = database_ids.get("tasks")
            completed_this_week = []

            if tasks_db_id:
                from better_notion.plugins.official.personal_sdk.models import Task

                response = await client._api.databases.query(
                    database_id=tasks_db_id,
                    filter={
                        "and": [
                            {"property": "Status", "select": {"equals": "Done"}},
                            {"property": "Completed Date", "date": {
                                "on_or_after": week_start.isoformat(),
                                "on_or_before": week_end.isoformat(),
                            }},
                        ],
                    },
                )
                completed_this_week = [Task(client, page_data) for page_data in response.get("results", [])]

            return format_success({
                "message": "Weekly review",
                "week_start": week_start.isoformat(),
                "week_end": week_end.isoformat(),
                "completed_count": len(completed_this_week),
                "completed_tasks": [t.title for t in completed_this_week],
            })

        except Exception as e:
            return format_error("WEEKLY_REVIEW_ERROR", str(e), retry=False)

    return asyncio.run(_review())


def review_monthly() -> str:
    """Generate monthly review."""
    async def _review() -> str:
        try:
            client = get_client()
            config = get_workspace_config()
            database_ids = config.get("database_ids", {})

            today_date = date.today()
            month_start = today_date.replace(day=1)

            tasks_db_id = database_ids.get("tasks")
            completed_this_month = []

            if tasks_db_id:
                from better_notion.plugins.official.personal_sdk.models import Task

                response = await client._api.databases.query(
                    database_id=tasks_db_id,
                    filter={
                        "and": [
                            {"property": "Status", "select": {"equals": "Done"}},
                            {"property": "Completed Date", "date": {
                                "on_or_after": month_start.isoformat(),
                            }},
                        ],
                    },
                )
                completed_this_month = [Task(client, page_data) for page_data in response.get("results", [])]

            return format_success({
                "message": "Monthly review",
                "month": month_start.isoformat(),
                "completed_count": len(completed_this_month),
                "completed_tasks": [t.title for t in completed_this_month],
            })

        except Exception as e:
            return format_error("MONTHLY_REVIEW_ERROR", str(e), retry=False)

    return asyncio.run(_review())


# ===== HELPER FUNCTIONS =====

async def _resolve_domain_id(client: NotionClient, domain_name: str) -> str | None:
    """Resolve domain name to ID."""
    config = get_workspace_config()
    database_ids = config.get("database_ids", {})
    domains_db_id = database_ids.get("domains")

    if not domains_db_id:
        return None

    response = await client._api.databases.query(
        database_id=domains_db_id,
        filter={
            "property": "Name",
            "title": {"equals": domain_name},
        },
    )

    results = response.get("results", [])
    if results:
        return results[0]["id"]
    return None


async def _resolve_project_id(client: NotionClient, project_name: str) -> str | None:
    """Resolve project name to ID."""
    config = get_workspace_config()
    database_ids = config.get("database_ids", {})
    projects_db_id = database_ids.get("projects")

    if not projects_db_id:
        return None

    response = await client._api.databases.query(
        database_id=projects_db_id,
        filter={
            "property": "Name",
            "title": {"equals": project_name},
        },
    )

    results = response.get("results", [])
    if results:
        return results[0]["id"]
    return None


async def _resolve_task_id(client: NotionClient, task_title: str) -> str | None:
    """Resolve task title to ID."""
    config = get_workspace_config()
    database_ids = config.get("database_ids", {})
    tasks_db_id = database_ids.get("tasks")

    if not tasks_db_id:
        return None

    response = await client._api.databases.query(
        database_id=tasks_db_id,
        filter={
            "property": "Title",
            "title": {"equals": task_title},
        },
    )

    results = response.get("results", [])
    if results:
        return results[0]["id"]
    return None


async def _resolve_tag_id(client: NotionClient, tag_name: str) -> str | None:
    """Resolve tag name to ID."""
    config = get_workspace_config()
    database_ids = config.get("database_ids", {})
    tags_db_id = database_ids.get("tags")

    if not tags_db_id:
        return None

    response = await client._api.databases.query(
        database_id=tags_db_id,
        filter={
            "property": "Name",
            "title": {"equals": tag_name},
        },
    )

    results = response.get("results", [])
    if results:
        return results[0]["id"]
    return None


async def _resolve_tag_ids(client: NotionClient, tag_names: list[str]) -> list[str]:
    """Resolve multiple tag names to IDs."""
    config = get_workspace_config()
    database_ids = config.get("database_ids", {})
    tags_db_id = database_ids.get("tags")

    if not tags_db_id:
        return []

    tag_ids = []
    for tag_name in tag_names:
        tag_id = await _resolve_tag_id(client, tag_name)
        if tag_id:
            tag_ids.append(tag_id)

    return tag_ids
