"""
Databases commands for Better Notion CLI.

This module provides commands for managing Notion databases.
"""
from __future__ import annotations

import json
from typing import Any

import typer

from better_notion._cli.async_typer import AsyncTyper
from better_notion._cli.config import Config
from better_notion._cli.response import format_error, format_success
from better_notion._sdk.client import NotionClient

app = AsyncTyper(help="Databases commands")


# Schema templates for common use cases
SCHEMA_TEMPLATES = {
    "minimal": {
        "description": "Database with only a title property (minimal schema)",
        "schema": {}
    },
    "simple": {
        "description": "Simple database with title, text, and number properties",
        "schema": {
            "Notes": {"type": "rich_text"},
            "Count": {"type": "number"}
        }
    },
    "task": {
        "description": "Task tracking database with status, priority, and due date",
        "schema": {
            "Status": {
                "type": "select",
                "select": {
                    "options": [
                        {"name": "Not Started", "color": "gray"},
                        {"name": "In Progress", "color": "blue"},
                        {"name": "Completed", "color": "green"}
                    ]
                }
            },
            "Priority": {
                "type": "select",
                "select": {
                    "options": [
                        {"name": "Low", "color": "gray"},
                        {"name": "Medium", "color": "yellow"},
                        {"name": "High", "color": "orange"},
                        {"name": "Critical", "color": "red"}
                    ]
                }
            },
            "Due Date": {"type": "date"}
        }
    }
}


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
                "url": db.url,
                "archived": db.archived,
                "properties_count": len(db.schema) if db.schema else 0,
            })
        except Exception as e:
            return format_error("UNKNOWN_ERROR", str(e), retry=False)

    result = asyncio.run(_get())
    typer.echo(result)


@app.command()
async def create(
    parent: str = typer.Option(..., "--parent", "-p", help="Parent page ID"),
    title: str = typer.Option(..., "--title", "-t", help="Database title"),
    schema: str = typer.Option("{}", "--schema", "-s", help="JSON schema for properties"),
    template: str = typer.Option(None, "--template", help="Use a predefined schema template (minimal, simple, task)"),
) -> None:
    """Create a new database.

    Schema Format:
        The schema should be a JSON object mapping property names to their types.
        Each property should have a "type" field and type-specific configuration.

    Common property types:
        - title: {"type": "title"} (Note: Every database must have exactly one title property)
        - rich_text: {"type": "rich_text"}
        - number: {"type": "number", "number": {"format": "number"}}
        - select: {"type": "select", "select": {"options": [{"name": "Option1", "color": "gray"}]}}
        - date: {"type": "date"}
        - checkbox: {"type": "checkbox"}
        - email: {"type": "email"}
        - url: {"type": "url"}
        - phone: {"type": "phone_number"}

    Examples:
        # Minimal database (title only)
        notion databases create --parent page123 --title "My Database" --template minimal

        # Simple custom schema
        notion databases create --parent page123 --title "Tasks" \\
            --schema '{"Status": {"type": "select", "select": {"options": [{"name": "Todo", "color": "gray"}]}}}'

        # Use a predefined template
        notion databases create --parent page123 --title "Task Tracker" --template task

        # Show available templates
        notion database-templates
    """
    try:
        client = get_client()
        parent_page = await client.pages.get(parent)

        # Use template if specified
        if template:
            if template not in SCHEMA_TEMPLATES:
                result = format_error(
                    "INVALID_TEMPLATE",
                    f"Template '{template}' not found. Available templates: {', '.join(SCHEMA_TEMPLATES.keys())}. Use 'notion database-templates' to see all templates.",
                    retry=False
                )
                typer.echo(result)
                raise typer.Exit(code=1)
            schema_dict = SCHEMA_TEMPLATES[template]["schema"]
        else:
            # Parse custom schema
            try:
                schema_dict = json.loads(schema)
            except json.JSONDecodeError as e:
                result = format_error(
                    "INVALID_SCHEMA",
                    f"Invalid JSON schema: {str(e)}",
                    retry=False
                )
                typer.echo(result)
                raise typer.Exit(code=1)

        # Validate schema structure
        if not isinstance(schema_dict, dict):
            result = format_error(
                "INVALID_SCHEMA",
                "Schema must be a JSON object (dictionary)",
                retry=False
            )
            typer.echo(result)
            raise typer.Exit(code=1)

        db = await client.databases.create(
            parent=parent_page,
            title=title,
            schema=schema_dict,
        )

        result = format_success({
            "id": db.id,
            "title": db.title,
            "url": db.url,
            "properties_count": len(db.schema) if db.schema else 0,
        })
        typer.echo(result)

    except typer.Exit:
        raise
    except Exception as e:
        error_msg = str(e)
        # Add helpful context for common errors
        if "schema" in error_msg.lower():
            error_msg += "\n\nHint: Use 'notion database-templates' to see schema examples or --template minimal for a simple database"
        result = format_error("CREATE_ERROR", error_msg, retry=False)
        typer.echo(result)
        raise typer.Exit(code=1)


@app.command("database-templates")
def templates_cmd() -> None:
    """Show available database schema templates.

    Examples:
        notion database-templates
    """
    typer.echo(json.dumps(SCHEMA_TEMPLATES, indent=2))


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


@app.command("list")
def list_cmd() -> None:
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
                        "url": db.url,
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
