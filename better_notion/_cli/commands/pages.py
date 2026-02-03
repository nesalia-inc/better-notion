"""
Pages commands for Better Notion CLI.

This module provides commands for managing Notion pages.
"""
from __future__ import annotations

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
async def get(page_id: str) -> None:
    """
    Get a page by ID.

    Retrieves detailed information about a specific Notion page.
    """
    try:
        client = get_client()
        page = await client.pages.get(page_id)

        # Get parent (async method - note the parentheses)
        parent_obj = await page.parent()

        result = format_success({
            "id": page.id,
            "title": page.title,
            "url": page.url,
            "parent_id": parent_obj.id if parent_obj else None,
            "parent_type": parent_obj.object if parent_obj else None,
            "created_time": page._data.get("created_time"),
            "last_edited_time": page._data.get("last_edited_time"),
            "archived": page.archived,
            "properties": {name: str(value) for name, value in page._data.get("properties", {}).items()},
        })
        typer.echo(result)
    except Exception as e:
        result = format_error("UNKNOWN_ERROR", str(e), retry=False)
        typer.echo(result)
        raise typer.Exit(code=1)


@app.command()
async def create(
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
    client = get_client()
    props = json.loads(properties) if properties else {}

    # Validate mutual exclusivity
    if root and parent:
        result = format_error(
            "INVALID_ARGUMENT",
            "Cannot specify both --root and --parent",
            retry=False
        )
        typer.echo(result)
        raise typer.Exit(code=1)

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
                result = format_error(
                    "PARENT_NOT_FOUND",
                    f"Could not find parent '{parent}' as database or page. "
                    f"Database error: {str(db_err)}. Page error: {str(page_err)}",
                    retry=False
                )
                typer.echo(result)
                raise typer.Exit(code=1)

    page = await client.pages.create(parent=parent_obj, title=title, **props)

    # Get parent info safely
    parent_id = None
    parent_type = None
    if root:
        parent_type = "workspace"
    elif page.parent:
        parent_id = getattr(page.parent, 'id', None)
        parent_type = getattr(page.parent, 'object', None)

    result = format_success({
        "id": page.id,
        "title": page.title,
        "url": page.url,
        "parent_id": parent_id,
        "parent_type": parent_type,
    })
    typer.echo(result)


@app.command()
async def update(
    page_id: str = typer.Argument(..., help="Page ID to update"),
    properties: str = typer.Option(..., "--properties", "-p", help="JSON string of properties to update"),
) -> None:
    """
    Update a page.

    Updates the specified properties of a page.
    """
    client = get_client()
    page = await client.pages.get(page_id)
    props = json.loads(properties)

    updated_page = await page.update(**props)

    result = format_success({
        "id": updated_page.id,
        "title": updated_page.title,
        "last_edited_time": updated_page.last_edited_time,
    })
    typer.echo(result)


@app.command()
async def delete(page_id: str) -> None:
    """
    Delete a page.

    Permanently deletes a page and all its children.
    """
    client = get_client()
    page = await client.pages.get(page_id)
    await page.delete()

    result = format_success({
        "id": page_id,
        "status": "deleted",
    })
    typer.echo(result)


@app.command()
async def list(
    database: str = typer.Option(..., "--database", "-d", help="Database ID to list pages from"),
    filter: str = typer.Option(None, "--filter", "-f", help="JSON filter for query"),
) -> None:
    """
    List pages in a database.

    Lists all pages in a database, optionally filtered.
    """
    client = get_client()
    db = await client.databases.get(database)

    filters = json.loads(filter) if filter else {}
    pages = await db.query(client=client, **filters)

    result = format_success({
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
    typer.echo(result)


@app.command()
async def search(
    query: str = typer.Argument(..., help="Search query"),
    filter: str = typer.Option(None, "--filter", "-f", help="JSON filter for object type"),
) -> None:
    """
    Search for pages.

    Searches for pages matching the query.
    """
    client = get_client()
    filters = json.loads(filter) if filter else {}

    results = await client.search(query=query, filter=filters)

    pages = [r for r in results if hasattr(r, 'title')]
    result = format_success({
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
    typer.echo(result)


@app.command()
async def blocks(page_id: str) -> None:
    """
    Get blocks in a page.

    Retrieves all blocks contained in a page.
    """
    client = get_client()
    page = await client.pages.get(page_id)

    block_list = []
    async for block in page.children():
        block_list.append({
            "id": block.id,
            "type": block.type,
        })

    result = format_success({
        "page_id": page_id,
        "count": len(block_list),
        "blocks": block_list,
    })
    typer.echo(result)


@app.command()
async def copy(
    page_id: str = typer.Argument(..., help="Page ID to copy"),
    destination: str = typer.Option(..., "--dest", "-d", help="Destination parent ID"),
) -> None:
    """
    Copy a page.

    Creates a copy of a page under a new parent.
    """
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

    result = format_success({
        "original_id": page_id,
        "new_id": new_page.id,
        "new_url": new_page.url,
    })
    typer.echo(result)


@app.command()
async def move(
    page_id: str = typer.Argument(..., help="Page ID to move"),
    destination: str = typer.Argument(..., help="Destination parent ID"),
) -> None:
    """
    Move a page.

    Moves a page to a new parent (database or page).
    """
    client = get_client()
    page = await client.pages.get(page_id)

    # Get destination parent
    try:
        dest_parent = await client.databases.get(destination)
    except Exception:
        dest_parent = await client.pages.get(destination)

    # Update parent
    await page.update(parent=dest_parent._data)

    result = format_success({
        "id": page_id,
        "new_parent_id": destination,
    })
    typer.echo(result)


@app.command()
async def archive(page_id: str) -> None:
    """
    Archive a page.

    Archives a page (moves to trash).
    """
    client = get_client()
    page = await client.pages.get(page_id)

    await page.update(archived=True)

    result = format_success({
        "id": page_id,
        "status": "archived",
    })
    typer.echo(result)


@app.command()
async def restore(page_id: str) -> None:
    """
    Restore an archived page.

    Restores a page from the trash/archive.
    """
    client = get_client()
    page = await client.pages.get(page_id)

    await page.update(archived=False)

    result = format_success({
        "id": page_id,
        "status": "restored",
    })
    typer.echo(result)


@app.command()
async def clear(page_id: str) -> None:
    """
    Clear all blocks from a page.

    Deletes all content blocks from a page while keeping the page itself.
    The page title and properties are preserved.
    """
    client = get_client()
    page = await client.pages.get(page_id)

    # Collect all block IDs using direct API call
    block_ids = []
    response = await client.api._request("GET", f"/blocks/{page_id}/children")
    for block_data in response.get("results", []):
        block_ids.append(block_data["id"])

    # Handle pagination if there are more blocks
    while response.get("next_cursor"):
        response = await client.api._request(
            "GET",
            f"/blocks/{page_id}/children",
            params={"start_cursor": response["next_cursor"]}
        )
        for block_data in response.get("results", []):
            block_ids.append(block_data["id"])

    # Delete all blocks
    deleted_count = 0
    for block_id in block_ids:
        try:
            await client.api._request("DELETE", f"/blocks/{block_id}")
            deleted_count += 1
        except Exception:
            # Continue even if deletion fails
            pass

    result = format_success({
        "id": page_id,
        "blocks_deleted": deleted_count,
        "status": "cleared",
    })
    typer.echo(result)


@app.command("create-from-md")
async def create_from_md(
    file: str = typer.Option(..., "--file", "-f", help="Path to markdown file"),
    parent: str = typer.Option(..., "--parent", "-p", help="Parent database or page ID"),
    title: str = typer.Option(None, "--title", "-t", help="Custom page title (default: first H1 or filename)"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Show what would be created without creating"),
) -> None:
    """
    Create a page from a markdown file.

    Parses the markdown file and creates a new Notion page with all blocks.
    """
    try:
        # Parse markdown file
        md_title, blocks = parse_markdown_file(file)

        # Use custom title if provided
        page_title = title or md_title

        if dry_run:
            # Show what would be created
            result = format_success({
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
            typer.echo(result)
            return

        client = get_client()

        # Resolve parent with clear error messages
        try:
            parent_obj = await client.databases.get(parent)
        except Exception as db_err:
            # If database fails, try as page
            try:
                parent_obj = await client.pages.get(parent)
            except Exception as page_err:
                # Both failed - return detailed error
                result = format_error(
                    "PARENT_NOT_FOUND",
                    f"Could not find parent '{parent}' as database or page. "
                    f"Database error: {str(db_err)}. Page error: {str(page_err)}",
                    retry=False
                )
                typer.echo(result)
                raise typer.Exit(code=1)

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

        result = format_success({
            "id": page.id,
            "title": page_title,
            "url": page.url,
            "blocks_created": len(blocks),
            "file": file,
        })
        typer.echo(result)

    except FileNotFoundError as e:
        result = format_error("FILE_NOT_FOUND", str(e), retry=False)
        typer.echo(result)
        raise typer.Exit(code=1)
    except ValueError as e:
        result = format_error("INVALID_FILE", str(e), retry=False)
        typer.echo(result)
        raise typer.Exit(code=1)
    except Exception as e:
        result = format_error("UNKNOWN_ERROR", str(e), retry=False)
        typer.echo(result)
        raise typer.Exit(code=1)
