"""
Users commands for Better Notion CLI.

This module provides commands for managing Notion users.
"""
from __future__ import annotations

import asyncio

import typer

from better_notion._cli.async_typer import AsyncTyper
from better_notion._cli.config import Config
from better_notion._cli.response import format_error, format_success
from better_notion._sdk.client import NotionClient

app = AsyncTyper(help="Users commands")


def get_client() -> NotionClient:
    """Get authenticated Notion client."""
    config = Config.load()
    return NotionClient(auth=config.token, timeout=config.timeout)


@app.command()
def get(user_id: str) -> None:
    """Get a user by ID."""
    async def _get() -> str:
        try:
            client = get_client()
            user = await client.users.get(user_id)

            return format_success({
                "id": user.id,
                "name": user.name,
                "email": user.email if hasattr(user, 'email') else None,
                "type": user.type,
                "is_bot": user.is_bot,
                "is_person": user.is_person,
            })
        except Exception as e:
            return format_error("UNKNOWN_ERROR", str(e), retry=False)

    result = asyncio.run(_get())
    typer.echo(result)


@app.command("me")
def get_me() -> None:
    """Get the current bot user info."""
    async def _me() -> str:
        try:
            client = get_client()
            me = await client.users.me()

            return format_success({
                "id": me.id,
                "name": me.name,
                "type": me.type,
                "is_bot": me.is_bot,
            })
        except Exception as e:
            return format_error("UNKNOWN_ERROR", str(e), retry=False)

    result = asyncio.run(_me())
    typer.echo(result)


@app.command()
def list_all() -> None:
    """List all users in workspace."""
    async def _list() -> str:
        try:
            client = get_client()
            # Populate cache first
            await client.users.populate_cache()

            # Get all users from cache
            users = client.users.list_all()

            return format_success({
                "count": len(users),
                "users": [
                    {
                        "id": user.id,
                        "name": user.name,
                        "email": user.email if hasattr(user, 'email') else None,
                        "type": user.type,
                    }
                    for user in users
                ],
            })
        except Exception as e:
            return format_error("UNKNOWN_ERROR", str(e), retry=False)

    result = asyncio.run(_list())
    typer.echo(result)


@app.command()
def search(query: str = typer.Argument(..., help="Search query (name or email)")) -> None:
    """Search for users by name or email."""
    async def _search() -> str:
        try:
            client = get_client()

            # Try to find by email first
            try:
                user = await client.users.find_by_email(query)
                users = [user]
            except Exception:
                # Fall back to name search
                try:
                    user = await client.users.find_by_name(query)
                    users = [user]
                except Exception:
                    users = []

            return format_success({
                "query": query,
                "count": len(users),
                "users": [
                    {
                        "id": u.id,
                        "name": u.name,
                        "email": u.email if hasattr(u, 'email') else None,
                    }
                    for u in users
                ],
            })
        except Exception as e:
            return format_error("UNKNOWN_ERROR", str(e), retry=False)

    result = asyncio.run(_search())
    typer.echo(result)


@app.command()
def avatar(user_id: str) -> None:
    """Get user avatar URL."""
    async def _avatar() -> str:
        try:
            client = get_client()
            user = await client.users.get(user_id)

            avatar_url = user.avatar_url if hasattr(user, 'avatar_url') else None

            return format_success({
                "user_id": user_id,
                "avatar_url": avatar_url,
            })
        except Exception as e:
            return format_error("UNKNOWN_ERROR", str(e), retry=False)

    result = asyncio.run(_avatar())
    typer.echo(result)
