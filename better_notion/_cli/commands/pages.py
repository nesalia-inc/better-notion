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
from better_notion._cli.markdown import parse_markdown_file
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
    root: bool = typer.Option(False, "--root", "-r", help="Create page at workspace root"),
    parent: str = typer.Option(None, "--parent", "-p", help="Parent database or page ID"),
    title: str = typer.Option(..., "--title", "-t", help="Page title"),
    properties: str = typer.Option(None, "--properties", help="JSON string of additional properties"),
) -> None:
    """
    Create a new page.

    Creates a new page under a parent database/page or at workspace root.

    Note: Workspace parent (--root) may require specific integration permissions.
    """
    async def _create() -> str:
        client = get_client()
        props = json.loads(properties) if properties else {}

        # Validate mutual exclusivity
        if root and parent:
            return format_error(
                "INVALID_ARGUMENT",
                "Cannot specify both --root and --parent",
                retry=False
            )

        # Handle workspace parent
        if root:
            from better_notion._sdk.parents import WorkspaceParent
            parent_obj = WorkspaceParent()
        else:
            # Existing parent resolution logic
            # Try database first
            try:
                parent_obj = await client.databases.get(parent)
            except Exception as db_err:
                # If database fails, try as page
                try:
                    parent_obj = await client.pages.get(parent)
                except Exception as page_err:
                    # Both failed - return detailed error
                    return format_error(
                        "PARENT_NOT_FOUND",
                        f"Could not find parent '{parent}' as database or page. "
                        f"Database error: {str(db_err)}. Page error: {str(page_err)}",
                        retry=False
                    )

        page = await client.pages.create(parent=parent_obj, title=title, **props)

        # Get parent info safely
        parent_id = None
        parent_type = None
        if root:
            parent_type = "workspace"
        elif page.parent:
            parent_id = getattr(page.parent, 'id', None)
            parent_type = getattr(page.parent, 'object', None)

        return format_success({
            "id": page.id,
            "title": page.title,
            "url": page.url,
            "parent_id": parent_id,
            "parent_type": parent_type,
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


@app.command("create-from-md")
def create_from_md(
    file: str = typer.Option(..., "--file", "-f", help="Path to markdown file"),
    parent: str = typer.Option(..., "--parent", "-p", help="Parent database or page ID"),
    title: str = typer.Option(None, "--title", "-t", help="Custom page title (default: first H1 or filename)"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Show what would be created without creating"),
) -> None:
    """
    Create a page from a markdown file.

    Parses the markdown file and creates a new Notion page with all blocks.
    """
    async def _create() -> str:
        try:
            # Parse markdown file
            md_title, blocks = parse_markdown_file(file)

            # Use custom title if provided
            page_title = title or md_title

            if dry_run:
                # Show what would be created
                return format_success({
                    "dry_run": True,
                    "file": file,
                    "title": page_title,
                    "parent": parent,
                    "blocks_count": len(blocks),
                    "blocks_preview": [
                        {
                            "type": block.get("type"),
                            "preview": str(block.get(block.get("type", {}), {}))[:100]
                        }
                        for block in blocks[:5]  # Show first 5 blocks
                    ]
                })

            client = get_client()

            # Resolve parent
            try:
                parent_obj = await client.databases.get(parent)
            except Exception:
                parent_obj = await client.pages.get(parent)

            # Create page
            page = await client.pages.create(
                parent=parent_obj,
                title=page_title,
            )

            # Add blocks to page
            if blocks:
                # Use BlockCollection to append blocks
                from better_notion._api.collections import BlockCollection

                blocks_collection = BlockCollection(client.api, parent_id=page.id)

                # Add blocks one by one (Notion API limitation)
                for block_data in blocks:
                    try:
                        await blocks_collection.append(block_data)
                    except Exception as e:
                        # Continue with other blocks even if one fails
                        pass

            return format_success({
                "id": page.id,
                "title": page_title,
                "url": page.url,
                "blocks_created": len(blocks),
                "file": file,
            })

        except FileNotFoundError as e:
            return format_error("FILE_NOT_FOUND", str(e), retry=False)
        except ValueError as e:
            return format_error("INVALID_FILE", str(e), retry=False)
        except Exception as e:
            return format_error("UNKNOWN_ERROR", str(e), retry=False)

    result = asyncio.run(_create())
    typer.echo(result)
