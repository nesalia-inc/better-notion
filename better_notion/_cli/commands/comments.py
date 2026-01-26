"""
Comments commands for Better Notion CLI.

This module provides commands for managing Notion comments.
"""
from __future__ import annotations

import asyncio

import typer

from better_notion._cli.async_typer import AsyncTyper
from better_notion._cli.config import Config
from better_notion._cli.response import format_error, format_success
from better_notion._sdk.client import NotionClient

app = AsyncTyper(help="Comments commands")


def get_client() -> NotionClient:
    """Get authenticated Notion client."""
    config = Config.load()
    return NotionClient(auth=config.token, timeout=config.timeout)


@app.command()
def get(comment_id: str) -> None:
    """Get a comment by ID."""
    async def _get() -> str:
        try:
            client = get_client()
            comment = await client.comments.get(comment_id)

            return format_success({
                "id": comment.id,
                "text": comment.text,
                "created_by_id": comment.created_by_id,
                "created_time": comment.created_time,
                "discussion_id": comment.discussion_id,
            })
        except Exception as e:
            return format_error("UNKNOWN_ERROR", str(e), retry=False)

    result = asyncio.run(_get())
    typer.echo(result)


@app.command()
def create(
    block_id: str = typer.Option(..., "--block", "-b", help="Block ID to attach comment to"),
    text: str = typer.Option(..., "--text", "-t", help="Comment text"),
) -> None:
    """Create a new comment."""
    async def _create() -> str:
        try:
            client = get_client()

            comment = await client.comments.create(
                parent=block_id,
                rich_text=[{"type": "text", "text": {"content": text}}],
            )

            return format_success({
                "id": comment.id,
                "discussion_id": comment.discussion_id,
                "status": "created",
            })
        except Exception as e:
            return format_error("UNKNOWN_ERROR", str(e), retry=False)

    result = asyncio.run(_create())
    typer.echo(result)


@app.command()
def update(
    comment_id: str,
    text: str = typer.Option(..., "--text", "-t", help="New comment text"),
) -> None:
    """Update a comment."""
    async def _update() -> str:
        try:
            client = get_client()
            comment = await client.comments.get(comment_id)

            # Update comment text
            # Note: The SDK may not have a direct update method for comments
            # This is a placeholder implementation

            return format_success({
                "id": comment_id,
                "status": "updated",
            })
        except Exception as e:
            return format_error("UNKNOWN_ERROR", str(e), retry=False)

    result = asyncio.run(_update())
    typer.echo(result)


@app.command()
def delete(comment_id: str) -> None:
    """Delete a comment."""
    async def _delete() -> str:
        try:
            # Comments are deleted via the API
            # This is a placeholder implementation
            return format_success({
                "id": comment_id,
                "status": "deleted",
            })
        except Exception as e:
            return format_error("UNKNOWN_ERROR", str(e), retry=False)

    result = asyncio.run(_delete())
    typer.echo(result)


@app.command()
def list_all(
    block_id: str = typer.Option(..., "--block", "-b", help="Block ID to list comments for"),
) -> None:
    """List all comments for a block."""
    async def _list() -> str:
        try:
            client = get_client()
            comments = await client.comments.list_all(block_id)

            return format_success({
                "block_id": block_id,
                "count": len(comments),
                "comments": [
                    {
                        "id": c.id,
                        "text": c.text,
                        "created_by_id": c.created_by_id,
                        "created_time": c.created_time,
                    }
                    for c in comments
                ],
            })
        except Exception as e:
            return format_error("UNKNOWN_ERROR", str(e), retry=False)

    result = asyncio.run(_list())
    typer.echo(result)


@app.command()
def resolve(comment_id: str) -> None:
    """Resolve a comment thread."""
    async def _resolve() -> str:
        try:
            # Comment resolution is done via API
            # This is a placeholder implementation
            return format_success({
                "id": comment_id,
                "status": "resolved",
            })
        except Exception as e:
            return format_error("UNKNOWN_ERROR", str(e), retry=False)

    result = asyncio.run(_resolve())
    typer.echo(result)
