"""
Pages commands for Better Notion CLI.

This module provides commands for managing Notion pages.
"""
from __future__ import annotations

import asyncio
import json
from typing import Any

import typer
from typer.testing import CliRunner

from better_notion._cli.async_typer import AsyncTyper
from better_notion._cli.config import Config
from better_notion._cli.response import format_error, format_success
from better_notion._sdk.client import NotionClient

app = AsyncTyper(help="Pages commands")


def get_client() -> NotionClient:
    """Get authenticated Notion client."""
    config = Config.load()
    return NotionClient(auth=config.token, timeout=config.timeout)


@app.command()
def get(page_id: str) -> None:
    """
    Get a page by ID.

    Retrieves detailed information about a specific Notion page.
    """
    async def _get() -> str:
        try:
            client = get_client()
            page = await client.pages.get(page_id)

            return format_success({
                "id": page.id,
                "title": page.title,
                "url": page.url,
                "parent_id": page.parent.id if page.parent else None,
                "parent_type": page.parent.type if page.parent else None,
                "created_time": page.created_time,
                "last_edited_time": page.last_edited_time,
                "archived": page.archived,
                "properties": {name: str(value) for name, value in page._data.get("properties", {}).items()},
            })
        except Exception as e:
            return format_error("UNKNOWN_ERROR", str(e), retry=False)

    result = asyncio.run(_get())
    typer.echo(result)


@app.command()
def create(
    parent: str = typer.Option(..., "--parent", "-p", help="Parent database or page ID"),
    title: str = typer.Option(..., "--title", "-t", help="Page title"),
    properties: str = typer.Option(None, "--properties", "-p", help="JSON string of additional properties"),
) -> None:
    """
    Create a new page.

    Creates a new page under a parent database or page with the specified title.
    """
    async def _create() -> str:
        client = get_client()
        props = json.loads(properties) if properties else {}

        # Get parent
        try:
            parent_obj = await client.databases.get(parent)
        except Exception:
            parent_obj = await client.pages.get(parent)

        page = await client.pages.create(parent=parent_obj, title=title, **props)

        return format_success({
            "id": page.id,
            "title": page.title,
            "url": page.url,
            "parent_id": page.parent.id if page.parent else None,
        })

    result = asyncio.run(_create())
    typer.echo(result)


@app.command()
def update(
    page_id: str = typer.Argument(..., help="Page ID to update"),
    properties: str = typer.Option(..., "--properties", "-p", help="JSON string of properties to update"),
) -> None:
    """
    Update a page.

    Updates the specified properties of a page.
    """
    async def _update() -> str:
        client = get_client()
        page = await client.pages.get(page_id)
        props = json.loads(properties)

        updated_page = await page.update(**props)

        return format_success({
            "id": updated_page.id,
            "title": updated_page.title,
            "last_edited_time": updated_page.last_edited_time,
        })

    result = asyncio.run(_update())
    typer.echo(result)


@app.command()
def delete(page_id: str) -> None:
    """
    Delete a page.

    Permanently deletes a page and all its children.
    """
    async def _delete() -> str:
        client = get_client()
        page = await client.pages.get(page_id)
        await page.delete()

        return format_success({
            "id": page_id,
            "status": "deleted",
        })

    result = asyncio.run(_delete())
    typer.echo(result)


@app.command()
def list(
    database: str = typer.Option(..., "--database", "-d", help="Database ID to list pages from"),
    filter: str = typer.Option(None, "--filter", "-f", help="JSON filter for query"),
) -> None:
    """
    List pages in a database.

    Lists all pages in a database, optionally filtered.
    """
    async def _list() -> str:
        client = get_client()
        db = await client.databases.get(database)

        filters = json.loads(filter) if filter else {}
        pages = await db.query(client=client, **filters)

        return format_success({
            "database_id": database,
            "count": len(pages),
            "pages": [
                {
                    "id": page.id,
                    "title": page.title,
                    "url": page.url,
                }
                for page in pages
            ],
        })

    result = asyncio.run(_list())
    typer.echo(result)


@app.command()
def search(
    query: str = typer.Argument(..., help="Search query"),
    filter: str = typer.Option(None, "--filter", "-f", help="JSON filter for object type"),
) -> None:
    """
    Search for pages.

    Searches for pages matching the query.
    """
    async def _search() -> str:
        client = get_client()
        filters = json.loads(filter) if filter else {}

        results = await client.search.search(query=query, filter=filters)

        pages = [r for r in results if hasattr(r, 'title')]
        return format_success({
            "query": query,
            "count": len(pages),
            "pages": [
                {
                    "id": page.id,
                    "title": page.title,
                    "url": page.url,
                }
                for page in pages
            ],
        })

    result = asyncio.run(_search())
    typer.echo(result)


@app.command()
def blocks(page_id: str) -> None:
    """
    Get blocks in a page.

    Retrieves all blocks contained in a page.
    """
    async def _blocks() -> str:
        client = get_client()
        page = await client.pages.get(page_id)

        block_list = []
        async for block in page.children():
            block_list.append({
                "id": block.id,
                "type": block.type,
            })

        return format_success({
            "page_id": page_id,
            "count": len(block_list),
            "blocks": block_list,
        })

    result = asyncio.run(_blocks())
    typer.echo(result)


@app.command()
def copy(
    page_id: str = typer.Argument(..., help="Page ID to copy"),
    destination: str = typer.Option(..., "--dest", "-d", help="Destination parent ID"),
) -> None:
    """
    Copy a page.

    Creates a copy of a page under a new parent.
    """
    async def _copy() -> str:
        client = get_client()
        page = await client.pages.get(page_id)

        # Get destination parent
        try:
            dest_parent = await client.databases.get(destination)
        except Exception:
            dest_parent = await client.pages.get(destination)

        # Create new page with same title
        new_page = await client.pages.create(
            parent=dest_parent,
            title=page.title,
        )

        return format_success({
            "original_id": page_id,
            "new_id": new_page.id,
            "new_url": new_page.url,
        })

    result = asyncio.run(_copy())
    typer.echo(result)


@app.command()
def move(
    page_id: str = typer.Argument(..., help="Page ID to move"),
    destination: str = typer.Argument(..., help="Destination parent ID"),
) -> None:
    """
    Move a page.

    Moves a page to a new parent (database or page).
    """
    async def _move() -> str:
        client = get_client()
        page = await client.pages.get(page_id)

        # Get destination parent
        try:
            dest_parent = await client.databases.get(destination)
        except Exception:
            dest_parent = await client.pages.get(destination)

        # Update parent
        await page.update(parent=dest_parent._data)

        return format_success({
            "id": page_id,
            "new_parent_id": destination,
        })

    result = asyncio.run(_move())
    typer.echo(result)


@app.command()
def archive(page_id: str) -> None:
    """
    Archive a page.

    Archives a page (moves to trash).
    """
    async def _archive() -> str:
        client = get_client()
        page = await client.pages.get(page_id)

        await page.update(archived=True)

        return format_success({
            "id": page_id,
            "status": "archived",
        })

    result = asyncio.run(_archive())
    typer.echo(result)


@app.command()
def restore(page_id: str) -> None:
    """
    Restore an archived page.

    Restores a page from the trash/archive.
    """
    async def _restore() -> str:
        client = get_client()
        page = await client.pages.get(page_id)

        await page.update(archived=False)

        return format_success({
            "id": page_id,
            "status": "restored",
        })

    result = asyncio.run(_restore())
    typer.echo(result)
