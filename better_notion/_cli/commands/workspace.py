"""
Workspace commands for Better Notion CLI.

This module provides commands for workspace operations.
"""
from __future__ import annotations

import asyncio

import typer

from better_notion._cli.async_typer import AsyncTyper
from better_notion._cli.config import Config
from better_notion._cli.response import format_error, format_success
from better_notion._sdk.client import NotionClient

app = AsyncTyper(help="Workspace commands")


def get_client() -> NotionClient:
    """Get authenticated Notion client."""
    config = Config.load()
    return NotionClient(auth=config.token, timeout=config.timeout)


@app.command("info")
def info() -> None:
    """Get workspace information."""
    async def _info() -> str:
        try:
            client = get_client()
            me = await client.users.me()

            # Get cache stats
            stats = client.get_cache_stats()

            return format_success({
                "bot_id": me.id,
                "bot_name": me.name,
                "workspace_name": me.name,
                "cache_stats": stats,
            })
        except Exception as e:
            return format_error("UNKNOWN_ERROR", str(e), retry=False)

    result = asyncio.run(_info())
    typer.echo(result)


@app.command()
def users() -> None:
    """List all users in workspace."""
    async def _users() -> str:
        try:
            client = get_client()
            await client.users.populate_cache()

            all_users = client.users.list_all()

            return format_success({
                "count": len(all_users),
                "users": [
                    {
                        "id": u.id,
                        "name": u.name,
                        "email": u.email if hasattr(u, 'email') else None,
                        "type": u.type,
                    }
                    for u in all_users
                ],
            })
        except Exception as e:
            return format_error("UNKNOWN_ERROR", str(e), retry=False)

    result = asyncio.run(_users())
    typer.echo(result)


@app.command("export")
def export() -> None:
    """Export workspace data (placeholder)."""
    # Export is a complex operation
    # This is a placeholder for future implementation
    result = format_success({
        "status": "not_implemented",
        "message": "Export functionality requires additional implementation",
    })
    typer.echo(result)


@app.command("stats")
def stats() -> None:
    """Get workspace statistics."""
    async def _stats() -> str:
        try:
            client = get_client()

            # Get cache stats
            cache_stats = client.get_cache_stats()

            # Count databases
            databases = await client.databases.list_all()

            # Get bot user info
            me = await client.users.me()

            return format_success({
                "bot_name": me.name,
                "database_count": len(databases),
                "cache_stats": cache_stats,
            })
        except Exception as e:
            return format_error("UNKNOWN_ERROR", str(e), retry=False)

    result = asyncio.run(_stats())
    typer.echo(result)


@app.command("settings")
def settings() -> None:
    """Get workspace settings (placeholder)."""
    # Workspace settings
    # This is a placeholder for future implementation
    result = format_success({
        "status": "not_implemented",
        "message": "Settings functionality requires additional implementation",
    })
    typer.echo(result)
