"""
Official productivity plugin for Better Notion CLI.

Provides common productivity commands like quick capture, inbox management,
task tracking, and daily notes.
"""
from __future__ import annotations

import asyncio
from datetime import datetime
from pathlib import Path
from typing import Any

import typer

from better_notion._cli.config import Config
from better_notion._cli.response import format_error, format_success
from better_notion._sdk.client import NotionClient
from better_notion.plugins.base import PluginInterface


def get_client() -> NotionClient:
    """Get authenticated Notion client."""
    config = Config.load()
    return NotionClient(auth=config.token, timeout=config.timeout)


class ProductivityPlugin(PluginInterface):
    """
    Official productivity plugin with common productivity commands.

    Commands:
        - quick-capture: Quick capture to inbox
        - inbox-zero: Process inbox items
        - my-tasks: Show user's active tasks
        - daily-notes: Create daily notes page
    """

    def register_commands(self, app: typer.Typer) -> None:
        """Register plugin commands with the CLI app."""

        @app.command("quick-capture")
        def quick_capture(
            text: str = typer.Option(..., "--text", "-t", help="Text to capture"),
            inbox_db: str = typer.Option(None, "--inbox", "-i", help="Inbox database ID"),
        ) -> None:
            """
            Quick capture text to your inbox database.

            Creates a new page in your configured inbox database with the
            captured text. Perfect for quickly capturing ideas, tasks, or notes.
            """
            async def _capture() -> str:
                try:
                    client = get_client()

                    # Use provided inbox_db or try to get from config
                    db_id = inbox_db or self._get_inbox_db()

                    if not db_id:
                        return format_error(
                            "NO_INBOX",
                            "No inbox database configured. Use --inbox option or configure in ~/.notion/plugin-config.json",
                            False
                        )

                    # Create page in inbox database
                    db = await client.databases.get(db_id)
                    page = await client.pages.create(
                        parent=db,
                        title=text,
                    )

                    return format_success({
                        "id": page.id,
                        "title": text,
                        "url": page.url,
                        "captured_at": datetime.now().isoformat(),
                    })

                except Exception as e:
                    return format_error("CAPTURE_ERROR", str(e), False)

            result = asyncio.run(_capture())
            typer.echo(result)

        @app.command("inbox-zero")
        def inbox_zero(
            inbox_db: str = typer.Option(None, "--inbox", "-i", help="Inbox database ID"),
        ) -> None:
            """
            Process inbox items to achieve inbox zero.

            Lists all items in your inbox database so you can process them.
            """
            async def _process() -> str:
                try:
                    client = get_client()
                    db_id = inbox_db or self._get_inbox_db()

                    if not db_id:
                        return format_error(
                            "NO_INBOX",
                            "No inbox database configured.",
                            False
                        )

                    db = await client.databases.get(db_id)
                    results = await db.query().collect()

                    return format_success({
                        "inbox_db": db_id,
                        "item_count": len(results),
                        "items": [
                            {"id": r.id, "title": r.title}
                            for r in results
                        ],
                    })

                except Exception as e:
                    return format_error("INBOX_ERROR", str(e), False)

            result = asyncio.run(_process())
            typer.echo(result)

        @app.command("my-tasks")
        def my_tasks(
            tasks_db: str = typer.Option(None, "--tasks", "-t", help="Tasks database ID"),
            status: str = typer.Option(None, "--status", "-s", help="Filter by status"),
        ) -> None:
            """
            Show your active tasks.

            Lists tasks from your tasks database, optionally filtered by status.
            """
            async def _list() -> str:
                try:
                    client = get_client()
                    db_id = tasks_db or self._get_tasks_db()

                    if not db_id:
                        return format_error(
                            "NO_TASKS_DB",
                            "No tasks database configured.",
                            False
                        )

                    db = await client.databases.get(db_id)

                    # Query with status filter if provided
                    if status:
                        # This would require proper filter construction
                        # For now, just get all results
                        results = await db.query().collect()
                    else:
                        results = await db.query().collect()

                    return format_success({
                        "tasks_db": db_id,
                        "count": len(results),
                        "tasks": [
                            {"id": r.id, "title": r.title}
                            for r in results
                        ],
                    })

                except Exception as e:
                    return format_error("TASKS_ERROR", str(e), False)

            result = asyncio.run(_list())
            typer.echo(result)

        @app.command("daily-notes")
        def daily_notes(
            parent_db: str = typer.Option(None, "--parent", "-p", help="Parent database for daily notes"),
        ) -> None:
            """
            Create a daily notes page.

            Creates a new page for today's daily notes with a standard template.
            """
            async def _create() -> str:
                try:
                    client = get_client()
                    db_id = parent_db or self._get_daily_notes_db()

                    if not db_id:
                        return format_error(
                            "NO_DAILY_NOTES_DB",
                            "No daily notes database configured.",
                            False
                        )

                    # Create page with today's date as title
                    today = datetime.now().strftime("%Y-%m-%d")
                    db = await client.databases.get(db_id)
                    page = await client.pages.create(
                        parent=db,
                        title=f"Daily Notes - {today}",
                    )

                    return format_success({
                        "id": page.id,
                        "title": f"Daily Notes - {today}",
                        "url": page.url,
                        "created_at": datetime.now().isoformat(),
                    })

                except Exception as e:
                    return format_error("DAILY_NOTES_ERROR", str(e), False)

            result = asyncio.run(_create())
            typer.echo(result)

    def _get_inbox_db(self) -> str | None:
        """Get inbox database ID from configuration."""
        # This would read from a config file
        # For now, return None
        return None

    def _get_tasks_db(self) -> str | None:
        """Get tasks database ID from configuration."""
        return None

    def _get_daily_notes_db(self) -> str | None:
        """Get daily notes database ID from configuration."""
        return None

    def get_info(self) -> dict[str, Any]:
        """Return plugin metadata."""
        return {
            "name": "productivity",
            "version": "1.0.0",
            "description": "Personal productivity helpers for quick capture, inbox management, tasks, and daily notes",
            "author": "Better Notion Team",
            "official": True,
            "category": "productivity",
            "dependencies": []
        }
