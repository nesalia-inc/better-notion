"""
Search commands for Better Notion CLI.

This module provides commands for searching Notion content.
"""
from __future__ import annotations

import asyncio
import json

import typer

from better_notion._cli.async_typer import AsyncTyper
from better_notion._cli.config import Config
from better_notion._cli.response import format_error, format_success
from better_notion._sdk.client import NotionClient

app = AsyncTyper(help="Search commands")


def get_client() -> NotionClient:
    """Get authenticated Notion client."""
    config = Config.load()
    return NotionClient(auth=config.token, timeout=config.timeout)


@app.command()
def search(
    query: str = typer.Argument(..., help="Search query"),
    filter: str = typer.Option(None, "--filter", "-f", help="JSON filter for object type"),
) -> None:
    """Search for pages and databases."""
    async def _search() -> str:
        try:
            client = get_client()
            filters = json.loads(filter) if filter else {}

            results = await client.search.search(query=query, filter=filters)

            items = []
            for result in results:
                item = {
                    "id": result.id,
                    "object_type": type(result).__name__.lower(),
                }
                if hasattr(result, 'title'):
                    item["title"] = result.title
                items.append(item)

            return format_success({
                "query": query,
                "count": len(items),
                "results": items,
            })
        except Exception as e:
            return format_error("UNKNOWN_ERROR", str(e), retry=False)

    result = asyncio.run(_search())
    typer.echo(result)


@app.command("pages")
def search_pages(
    query: str = typer.Argument(..., help="Search query"),
) -> None:
    """Search for pages only."""
    async def _search() -> str:
        try:
            client = get_client()
            filter_obj = {"value": "page", "property": "object"}

            results = await client.search.search(query=query, filter=filter_obj)

            pages = [
                {
                    "id": p.id,
                    "title": p.title,
                    "url": p.url,
                }
                for p in results
            ]

            return format_success({
                "query": query,
                "count": len(pages),
                "pages": pages,
            })
        except Exception as e:
            return format_error("UNKNOWN_ERROR", str(e), retry=False)

    result = asyncio.run(_search())
    typer.echo(result)


@app.command("databases")
def search_databases(
    query: str = typer.Argument(..., help="Search query"),
) -> None:
    """Search for databases only."""
    async def _search() -> str:
        try:
            client = get_client()
            filter_obj = {"value": "database", "property": "object"}

            results = await client.search.search(query=query, filter=filter_obj)

            databases = [
                {
                    "id": db.id,
                    "title": db.title,
                }
                for db in results
            ]

            return format_success({
                "query": query,
                "count": len(databases),
                "databases": databases,
            })
        except Exception as e:
            return format_error("UNKNOWN_ERROR", str(e), retry=False)

    result = asyncio.run(_search())
    typer.echo(result)


@app.command("all")
def search_all(
    query: str = typer.Argument(..., help="Search query"),
) -> None:
    """Search all content types."""
    async def _search() -> str:
        try:
            client = get_client()

            results = await client.search.search(query=query)

            items = []
            for result in results:
                item = {
                    "id": result.id,
                    "object_type": type(result).__name__.lower(),
                }
                if hasattr(result, 'title'):
                    item["title"] = result.title
                elif hasattr(result, 'name'):
                    item["name"] = result.name
                items.append(item)

            return format_success({
                "query": query,
                "count": len(items),
                "results": items,
            })
        except Exception as e:
            return format_error("UNKNOWN_ERROR", str(e), retry=False)

    result = asyncio.run(_search())
    typer.echo(result)
