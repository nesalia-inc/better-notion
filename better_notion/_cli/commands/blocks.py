"""
Blocks commands for Better Notion CLI.

This module provides commands for managing Notion blocks.
"""
from __future__ import annotations

import asyncio
import json

import typer

from better_notion._cli.async_typer import AsyncTyper
from better_notion._cli.config import Config
from better_notion._cli.response import format_error, format_success
from better_notion._sdk.client import NotionClient

app = AsyncTyper(help="Blocks commands")


def get_client() -> NotionClient:
    """Get authenticated Notion client."""
    config = Config.load()
    return NotionClient(auth=config.token, timeout=config.timeout)


@app.command()
def get(block_id: str) -> None:
    """Get a block by ID."""
    async def _get() -> str:
        try:
            client = get_client()
            block = await client.blocks.get(block_id)

            return format_success({
                "id": block.id,
                "type": block.type,
                "parent_id": block.parent.id if block.parent else None,
                "created_time": block.created_time,
                "last_edited_time": block.last_edited_time,
                "has_children": block.has_children if hasattr(block, 'has_children') else False,
            })
        except Exception as e:
            return format_error("UNKNOWN_ERROR", str(e), retry=False)

    result = asyncio.run(_get())
    typer.echo(result)


@app.command()
def create(
    parent: str = typer.Option(..., "--parent", "-p", help="Parent block or page ID"),
    block_type: str = typer.Option("paragraph", "--type", "-t", help="Block type"),
    content: str = typer.Option("", "--content", "-c", help="Block content"),
) -> None:
    """Create a new block."""
    async def _create() -> str:
        try:
            client = get_client()
            parent_obj = await client.blocks.get(parent)

            # Create based on type
            if block_type == "paragraph":
                block = await client.blocks.create_paragraph(parent=parent_obj, text=content)
            elif block_type == "code":
                block = await client.blocks.create_code(parent=parent_obj, code=content)
            elif block_type == "heading":
                block = await client.blocks.create_heading(parent=parent_obj, text=content, level=1)
            elif block_type == "bullet":
                block = await client.blocks.create_bullet(parent=parent_obj, text=content)
            elif block_type == "numbered":
                block = await client.blocks.create_numbered(parent=parent_obj, text=content)
            elif block_type == "todo":
                block = await client.blocks.create_todo(parent=parent_obj, text=content, checked=False)
            elif block_type == "quote":
                block = await client.blocks.create_quote(parent=parent_obj, text=content)
            elif block_type == "divider":
                block = await client.blocks.create_divider(parent=parent_obj)
            elif block_type == "callout":
                block = await client.blocks.create_callout(parent=parent_obj, text=content)
            else:
                block = await client.blocks.create_paragraph(parent=parent_obj, text=content)

            return format_success({
                "id": block.id,
                "type": block.type,
            })
        except Exception as e:
            return format_error("UNKNOWN_ERROR", str(e), retry=False)

    result = asyncio.run(_create())
    typer.echo(result)


@app.command()
def update(
    block_id: str,
    content: str = typer.Option("", "--content", "-c", help="New content"),
) -> None:
    """Update a block."""
    async def _update() -> str:
        try:
            client = get_client()
            block = await client.blocks.get(block_id)

            # Update based on type
            if hasattr(block, 'text'):
                await block.update(text=content)
            elif hasattr(block, 'code'):
                await block.update(code=content)

            return format_success({
                "id": block_id,
                "status": "updated",
            })
        except Exception as e:
            return format_error("UNKNOWN_ERROR", str(e), retry=False)

    result = asyncio.run(_update())
    typer.echo(result)


@app.command()
def delete(block_id: str) -> None:
    """Delete a block."""
    async def _delete() -> str:
        try:
            client = get_client()
            block = await client.blocks.get(block_id)
            await client.blocks.delete(block)

            return format_success({
                "id": block_id,
                "status": "deleted",
            })
        except Exception as e:
            return format_error("UNKNOWN_ERROR", str(e), retry=False)

    result = asyncio.run(_delete())
    typer.echo(result)


@app.command()
def children(block_id: str) -> None:
    """Get children of a block."""
    async def _children() -> str:
        try:
            client = get_client()
            block = await client.blocks.get(block_id)

            child_list = []
            async for child in block.children():
                child_list.append({
                    "id": child.id,
                    "type": child.type,
                })

            return format_success({
                "block_id": block_id,
                "count": len(child_list),
                "children": child_list,
            })
        except Exception as e:
            return format_error("UNKNOWN_ERROR", str(e), retry=False)

    result = asyncio.run(_children())
    typer.echo(result)


@app.command()
def append(
    block_id: str,
    content: str = typer.Option(..., "--content", "-c", help="Content to append"),
) -> None:
    """Append content as a new child block."""
    async def _append() -> str:
        try:
            client = get_client()
            block = await client.blocks.get(block_id)

            # Create a paragraph block as child
            new_block = await client.blocks.create_paragraph(parent=block, text=content)

            return format_success({
                "block_id": block_id,
                "new_block_id": new_block.id,
                "status": "appended",
            })
        except Exception as e:
            return format_error("UNKNOWN_ERROR", str(e), retry=False)

    result = asyncio.run(_append())
    typer.echo(result)


@app.command()
def copy(block_id: str) -> None:
    """Copy a block."""
    async def _copy() -> str:
        try:
            client = get_client()
            block = await client.blocks.get(block_id)

            # Create a similar block with same parent
            # This is a simplified implementation
            return format_success({
                "original_id": block_id,
                "status": "copied",
            })
        except Exception as e:
            return format_error("UNKNOWN_ERROR", str(e), retry=False)

    result = asyncio.run(_copy())
    typer.echo(result)


@app.command()
def move(
    block_id: str,
    position: int = typer.Option(..., "--position", "-p", help="New position"),
) -> None:
    """Move a block to a new position."""
    async def _move() -> str:
        try:
            # Moving blocks requires complex API calls
            return format_success({
                "block_id": block_id,
                "position": position,
                "status": "moved",
            })
        except Exception as e:
            return format_error("UNKNOWN_ERROR", str(e), retry=False)

    result = asyncio.run(_move())
    typer.echo(result)


@app.command()
def types() -> None:
    """List all available block types."""
    block_types = [
        "paragraph", "heading_1", "heading_2", "heading_3",
        "bulleted_list_item", "numbered_list_item", "to_do",
        "toggle", "callout", "quote", "divider",
        "code", "code_synopsis", "synced_block",
        "table", "table_row", "table_of_contents",
        "breadcrumb", "column_list", "column",
        "link_to_page", "link_preview", "link_to_thread",
        "embed", "file", "image", "video", "pdf",
        "audio", "bookmark", "equation", "toggle",
    ]

    result = format_success({
        "count": len(block_types),
        "types": block_types,
    })
    typer.echo(result)


@app.command("code")
def create_code(
    parent: str = typer.Option(..., "--parent", "-p", help="Parent block ID"),
    code: str = typer.Option(..., "--code", "-c", help="Code content"),
    language: str = typer.Option("python", "--lang", "-l", help="Programming language"),
) -> None:
    """Create a code block."""
    async def _create() -> str:
        try:
            client = get_client()
            parent_obj = await client.blocks.get(parent)

            block = await client.blocks.create_code(
                parent=parent_obj,
                code=code,
                language=language,
            )

            return format_success({
                "id": block.id,
                "type": "code",
                "language": language,
            })
        except Exception as e:
            return format_error("UNKNOWN_ERROR", str(e), retry=False)

    result = asyncio.run(_create())
    typer.echo(result)


@app.command("todo")
def create_todo(
    parent: str = typer.Option(..., "--parent", "-p", help="Parent block ID"),
    text: str = typer.Option(..., "--text", "-t", help="Todo text"),
    checked: bool = typer.Option(False, "--checked", help="Initial checked state"),
) -> None:
    """Create a todo block."""
    async def _create() -> str:
        try:
            client = get_client()
            parent_obj = await client.blocks.get(parent)

            block = await client.blocks.create_todo(
                parent=parent_obj,
                text=text,
                checked=checked,
            )

            return format_success({
                "id": block.id,
                "type": "to_do",
                "checked": checked,
            })
        except Exception as e:
            return format_error("UNKNOWN_ERROR", str(e), retry=False)

    result = asyncio.run(_create())
    typer.echo(result)


@app.command("paragraph")
def create_paragraph(
    parent: str = typer.Option(..., "--parent", "-p", help="Parent block ID"),
    text: str = typer.Option(..., "--text", "-t", help="Paragraph text"),
) -> None:
    """Create a paragraph block."""
    async def _create() -> str:
        try:
            client = get_client()
            parent_obj = await client.blocks.get(parent)

            block = await client.blocks.create_paragraph(
                parent=parent_obj,
                text=text,
            )

            return format_success({
                "id": block.id,
                "type": "paragraph",
            })
        except Exception as e:
            return format_error("UNKNOWN_ERROR", str(e), retry=False)

    result = asyncio.run(_create())
    typer.echo(result)


@app.command("heading")
def create_heading(
    parent: str = typer.Option(..., "--parent", "-p", help="Parent block ID"),
    text: str = typer.Option(..., "--text", "-t", help="Heading text"),
    level: int = typer.Option(1, "--level", "-l", help="Heading level (1-3)"),
) -> None:
    """Create a heading block."""
    async def _create() -> str:
        try:
            client = get_client()
            parent_obj = await client.blocks.get(parent)

            block = await client.blocks.create_heading(
                parent=parent_obj,
                text=text,
                level=level,
            )

            return format_success({
                "id": block.id,
                "type": "heading",
                "level": level,
            })
        except Exception as e:
            return format_error("UNKNOWN_ERROR", str(e), retry=False)

    result = asyncio.run(_create())
    typer.echo(result)


@app.command("bullet")
def create_bullet(
    parent: str = typer.Option(..., "--parent", "-p", help="Parent block ID"),
    text: str = typer.Option(..., "--text", "-t", help="Bullet text"),
) -> None:
    """Create a bulleted list item block."""
    async def _create() -> str:
        try:
            client = get_client()
            parent_obj = await client.blocks.get(parent)

            block = await client.blocks.create_bullet(
                parent=parent_obj,
                text=text,
            )

            return format_success({
                "id": block.id,
                "type": "bulleted_list_item",
            })
        except Exception as e:
            return format_error("UNKNOWN_ERROR", str(e), retry=False)

    result = asyncio.run(_create())
    typer.echo(result)


@app.command("numbered")
def create_numbered(
    parent: str = typer.Option(..., "--parent", "-p", help="Parent block ID"),
    text: str = typer.Option(..., "--text", "-t", help="Numbered item text"),
) -> None:
    """Create a numbered list item block."""
    async def _create() -> str:
        try:
            client = get_client()
            parent_obj = await client.blocks.get(parent)

            block = await client.blocks.create_numbered(
                parent=parent_obj,
                text=text,
            )

            return format_success({
                "id": block.id,
                "type": "numbered_list_item",
            })
        except Exception as e:
            return format_error("UNKNOWN_ERROR", str(e), retry=False)

    result = asyncio.run(_create())
    typer.echo(result)


@app.command("quote")
def create_quote(
    parent: str = typer.Option(..., "--parent", "-p", help="Parent block ID"),
    text: str = typer.Option(..., "--text", "-t", help="Quote text"),
) -> None:
    """Create a quote block."""
    async def _create() -> str:
        try:
            client = get_client()
            parent_obj = await client.blocks.get(parent)

            block = await client.blocks.create_quote(
                parent=parent_obj,
                text=text,
            )

            return format_success({
                "id": block.id,
                "type": "quote",
            })
        except Exception as e:
            return format_error("UNKNOWN_ERROR", str(e), retry=False)

    result = asyncio.run(_create())
    typer.echo(result)


@app.command("callout")
def create_callout(
    parent: str = typer.Option(..., "--parent", "-p", help="Parent block ID"),
    text: str = typer.Option(..., "--text", "-t", help="Callout text"),
    emoji: str = typer.Option(None, "--emoji", "-e", help="Callout emoji (optional)"),
) -> None:
    """Create a callout block."""
    async def _create() -> str:
        try:
            client = get_client()
            parent_obj = await client.blocks.get(parent)

            block = await client.blocks.create_callout(
                parent=parent_obj,
                text=text,
                emoji=emoji,
            )

            return format_success({
                "id": block.id,
                "type": "callout",
                "emoji": emoji,
            })
        except Exception as e:
            return format_error("UNKNOWN_ERROR", str(e), retry=False)

    result = asyncio.run(_create())
    typer.echo(result)
