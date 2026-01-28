"""
Display utilities for Better Notion CLI.

This module provides utilities for determining the output mode (AI vs human)
and displaying content appropriately using Rich for human-friendly output.
"""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text


class DisplayMode:
    """Display mode enumeration."""
    AI = "ai"           # JSON output for AI agents
    HUMAN = "human"     # Rich output for humans
    AUTO = "auto"       # Auto-detect based on context


def get_display_mode(force_json: bool = False) -> str:
    """
    Detect the appropriate display mode.

    Args:
        force_json: If True, force AI mode

    Returns:
        Display mode: "ai" or "human"
    """
    if force_json:
        return DisplayMode.AI

    # Auto-detect: if stdin is not a TTY (piping), use AI mode
    # This is perfect for CI/CD and agent usage
    if not sys.stdin.isatty():
        return DisplayMode.AI

    # If output is being piped, use AI mode
    # Check if we're in a terminal
    try:
        # Test if we can write to terminal
        import rich.console
        console = Console()
        # If we can create a console, we're in human mode
        return DisplayMode.HUMAN
    except Exception:
        # Fallback to AI mode
        return DisplayMode.AI


def is_human_mode(force_json: bool = False, rich_mode: bool = False) -> bool:
    """
    Check if we should use human-friendly Rich output.

    Args:
        force_json: If True, disable human mode
        rich_mode: If True, force human mode

    Returns:
        True if human mode should be used
    """
    if force_json:
        return False

    if rich_mode:
        return True

    return get_display_mode() == DisplayMode.HUMAN


def print_rich(
    content: Any,
    title: str | None = None,
    console: Console | None = None,
    json_output: bool = False
) -> None:
    """
    Print content using Rich formatting in human mode.

    Args:
        content: The content to display
        title: Optional title for the content
        console: Optional Rich console instance
        json_output: If True, skip Rich display and use JSON
    """
    if json_output or not is_human_mode():
        # In AI mode, don't use Rich
        # The calling function will handle JSON output
        return

    if console is None:
        console = Console()

    if title:
        console.print(Panel(content, title=title, border_style="blue"))
    else:
        console.print(content)


def print_rich_table(
    data: list[dict[str, Any]] | dict[str, list[Any]],
    title: str | None = None,
    columns: list[str] | None = None,
    console: Console | None = None,
    json_output: bool = False
) -> None:
    """
    Print a table using Rich formatting in human mode.

    Args:
        data: Table data (list of dicts or dict with column headers)
        title: Optional table title
        columns: List of column names to display
        console: Optional Rich console instance
        json_output: If True, skip Rich display and use JSON
    """
    if json_output or not is_human_mode():
        # In AI mode, output as JSON
        import json
        typer.echo(json.dumps(data, indent=2))
        return

    if console is None:
        console = Console()

    # Convert dict with list headers to list of dicts
    if isinstance(data, dict) and all(isinstance(v, list) for v in data.values()):
        # data format: {"col1": [val1, val2], "col2": [val3, val4]}
        if columns is None:
            columns = list(data.keys())
        table = Table(show_header=True, title=title, header_style="bold blue")
        for col in columns:
            table.add_column(col, style="cyan")
        for col in columns:
            table.add_row(*data[col])
        console.print(table)
    elif isinstance(data, list):
        # data format: [{"col1": val1, "col2": val2}, ...]
        if not data:
            console.print("[dim]No data to display[/dim]")
            return
        if columns is None:
            columns = list(data[0].keys())
        table = Table(show_header=True, title=title, header_style="bold blue")
        for col in columns:
            table.add_column(col, style="cyan")
        for row in data:
            table.add_row(*[str(row.get(col, "")) for col in columns])
        console.print(table)
    else:
        console.print(str(data))


def print_rich_info(
    info: dict[str, Any],
    title: str | None = None,
    console: Console | None = None,
    json_output: bool = False
) -> None:
    """
    Print information using Rich panels in human mode.

    Args:
        info: Dictionary with information to display
        title: Optional title for the panel
        console: Optional Rich console instance
        json_output: If True, skip Rich display and use JSON
    """
    if json_output or not is_human_mode():
        # In AI mode, output as JSON
        import json
        typer.echo(json.dumps(info, indent=2))
        return

    if console is None:
        console = Console()

    # Build formatted content
    lines = []
    for key, value in info.items():
        if key == "success" and value is True:
            lines.append(f"[bold green]✓ {key}[/bold green]")
        elif key == "success" and value is False:
            lines.append(f"[bold red]✗ {key}[/bold red]")
        elif key == "message":
            lines.append(f"[yellow]{value}[/yellow]")
        elif key == "error" or key == "code":
            lines.append(f"[bold red]{key}[/bold red]: {value}")
        else:
            lines.append(f"[cyan]{key}[/cyan]: {value}")

    content = "\n".join(lines)

    if title:
        console.print(Panel(content, title=title, border_style="blue"))
    else:
        console.print(content)


def print_rich_success(
    message: str,
    data: dict[str, Any] | None = None,
    console: Console | None = None,
    json_output: bool = False
) -> None:
    """
    Print success message using Rich formatting in human mode.

    Args:
        message: Success message to display
        data: Optional data dictionary
        console: Optional Rich console instance
        json_output: If True, skip Rich display and use JSON
    """
    if json_output or not is_human_mode():
        # In AI mode, output as JSON
        import json
        output = {"success": True, "message": message}
        if data:
            output["data"] = data
        typer.echo(json.dumps(output, indent=2))
        return

    if console is None:
        console = Console()

    console.print(f"[bold green]✓ {message}[/bold green]")

    if data:
        console.print(f"  [dim]{data}[/dim]")


def print_rich_error(
    message: str,
    code: str | None = None,
    details: dict[str, Any] | None = None,
    console: Console | None = None,
    json_output: bool = False
) -> None:
    """
    Print error message using Rich formatting in human mode.

    Args:
        message: Error message to display
        code: Optional error code
        details: Optional details dictionary
        console: Optional Rich console instance
        json_output: If True, skip Rich display and use JSON
    """
    if json_output or not is_human_mode():
        # In AI mode, output as JSON
        import json
        output = {"success": False, "error": {"message": message}}
        if code:
            output["error"]["code"] = code
        if details:
            output["error"]["details"] = details
        typer.echo(json.dumps(output, indent=2))
        return

    if console is None:
        console = Console()

    console.print(f"[bold red]✗ Error[/bold red]: {message}")

    if code:
        console.print(f"  Code: [yellow]{code}[/yellow]")

    if details:
        console.print(f"  [dim]{details}[/dim]")


# Export display mode check function for use in other modules
__all__ = [
    "DisplayMode",
    "get_display_mode",
    "is_human_mode",
    "print_rich",
    "print_rich_table",
    "print_rich_info",
    "print_rich_success",
    "print_rich_error",
]
