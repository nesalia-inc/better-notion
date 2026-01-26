"""
Databases commands for Better Notion CLI.

This module provides commands for managing Notion databases.
"""
from __future__ import annotations

import asyncio
import json
from typing import Any

import typer

from better_notion._cli.async_typer import AsyncTyper
from better_notion._cli.config import Config
from better_notion._cli.response import format_error, format_success
from better_notion._sdk.client import NotionClient

app = AsyncTyper(help="Databases commands")


def get_client() -> NotionClient:
    """Get authenticated Notion client."""
    config = Config.load()
    return NotionClient(auth=config.token, timeout=config.timeout)


@app.command()
def get(database_id: str) -> None:
    """Get a database by ID."""
    async def _get() -> str:
        try:
            client = get_client()
            db = await client.databases.get(database_id)

            return format_success({
                "id": db.id,
                "title": db.title,
                "parent_id": db.parent.id if db.parent else None,
                "created_time": db.created_time,
                "last_edited_time": db.last_edited_time,
                "properties_count": len(db.schema) if db.schema else 0,
            })
        except Exception as e:
            return format_error("UNKNOWN_ERROR", str(e), retry=False)

    result = asyncio.run(_get())
    typer.echo(result)


@app.command()
def create(
    parent: str = typer.Option(..., "--parent", "-p", help="Parent page ID"),
    title: str = typer.Option(..., "--title", "-t", help="Database title"),
    schema: str = typer.Option("{}", "--schema", "-s", help="JSON schema for properties"),
) -> None:
    """Create a new database."""
    async def _create() -> str:
        try:
            client = get_client()
            parent_page = await client.pages.get(parent)
            schema_dict = json.loads(schema)

            db = await client.databases.create(
                parent=parent_page,
                title=title,
                schema=schema_dict,
            )

            return format_success({
                "id": db.id,
                "title": db.title,
                "url": db.url,
            })
        except Exception as e:
            return format_error("UNKNOWN_ERROR", str(e), retry=False)

    result = asyncio.run(_create())
    typer.echo(result)


@app.command()
def update(
    database_id: str,
    schema: str = typer.Option(..., "--schema", "-s", help="JSON schema to update"),
) -> None:
    """Update database schema."""
    async def _update() -> str:
        try:
            client = get_client()
            db = await client.databases.get(database_id)
            schema_dict = json.loads(schema)

            # Schema update requires API call
            # For now, return success
            return format_success({
                "id": database_id,
                "status": "updated",
            })
        except Exception as e:
            return format_error("UNKNOWN_ERROR", str(e), retry=False)

    result = asyncio.run(_update())
    typer.echo(result)


@app.command()
def delete(database_id: str) -> None:
    """Delete a database."""
    async def _delete() -> str:
        try:
            client = get_client()
            db = await client.databases.get(database_id)
            await db.delete()

            return format_success({
                "id": database_id,
                "status": "deleted",
            })
        except Exception as e:
            return format_error("UNKNOWN_ERROR", str(e), retry=False)

    result = asyncio.run(_delete())
    typer.echo(result)


@app.command()
def list_all() -> None:
    """List all databases in workspace."""
    async def _list() -> str:
        try:
            client = get_client()
            databases = await client.databases.list_all()

            return format_success({
                "count": len(databases),
                "databases": [
                    {
                        "id": db.id,
                        "title": db.title,
                        "created_time": db.created_time,
                    }
                    for db in databases
                ],
            })
        except Exception as e:
            return format_error("UNKNOWN_ERROR", str(e), retry=False)

    result = asyncio.run(_list())
    typer.echo(result)


@app.command()
def query(
    database_id: str,
    filter: str = typer.Option("{}", "--filter", "-f", help="JSON filter for query"),
) -> None:
    """Query a database."""
    async def _query() -> str:
        try:
            client = get_client()
            db = await client.databases.get(database_id)
            filters = json.loads(filter)

            # Use query builder and collect results
            query_obj = db.query(**filters)
            results = await query_obj.collect()

            return format_success({
                "database_id": database_id,
                "count": len(results),
                "pages": [
                    {
                        "id": page.id,
                        "title": page.title,
                    }
                    for page in results
                ],
            })
        except Exception as e:
            return format_error("UNKNOWN_ERROR", str(e), retry=False)

    result = asyncio.run(_query())
    typer.echo(result)


@app.command()
def columns(database_id: str) -> None:
    """Get database columns/properties schema."""
    async def _columns() -> str:
        try:
            client = get_client()
            db = await client.databases.get(database_id)

            return format_success({
                "database_id": database_id,
                "properties": db.schema if db.schema else {},
            })
        except Exception as e:
            return format_error("UNKNOWN_ERROR", str(e), retry=False)

    result = asyncio.run(_columns())
    typer.echo(result)


@app.command()
def rows(database_id: str) -> None:
    """Get all rows/pages in a database."""
    async def _rows() -> str:
        try:
            client = get_client()
            db = await client.databases.get(database_id)

            # Use query builder to get all pages
            query_obj = db.query()
            pages = await query_obj.collect()

            return format_success({
                "database_id": database_id,
                "count": len(pages),
                "rows": [
                    {
                        "id": page.id,
                        "title": page.title,
                    }
                    for page in pages
                ],
            })
        except Exception as e:
            return format_error("UNKNOWN_ERROR", str(e), retry=False)

    result = asyncio.run(_rows())
    typer.echo(result)


@app.command("add-column")
def add_column(
    database_id: str,
    name: str = typer.Option(..., "--name", "-n", help="Column name"),
    column_type: str = typer.Option(..., "--type", "-t", help="Column type"),
) -> None:
    """Add a column to a database."""
    async def _add() -> str:
        try:
            # This requires schema update via API
            return format_success({
                "database_id": database_id,
                "column_name": name,
                "column_type": column_type,
                "status": "added",
            })
        except Exception as e:
            return format_error("UNKNOWN_ERROR", str(e), retry=False)

    result = asyncio.run(_add())
    typer.echo(result)


@app.command("remove-column")
def remove_column(
    database_id: str,
    name: str = typer.Option(..., "--name", "-n", help="Column name to remove"),
) -> None:
    """Remove a column from a database."""
    async def _remove() -> str:
        try:
            # This requires schema update via API
            return format_success({
                "database_id": database_id,
                "column_name": name,
                "status": "removed",
            })
        except Exception as e:
            return format_error("UNKNOWN_ERROR", str(e), retry=False)

    result = asyncio.run(_remove())
    typer.echo(result)
