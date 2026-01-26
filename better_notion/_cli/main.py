"""
Main entry point for Better Notion CLI.

This module defines the main CLI application using AsyncTyper.
"""
from __future__ import annotations

import typer

from better_notion._cli.async_typer import AsyncTyper
from better_notion._cli.commands import (
    auth,
    blocks,
    comments,
    config,
    databases,
    pages,
    search,
    users,
    workspace,
)
from better_notion._cli.response import format_success

# Create the main CLI app
app = AsyncTyper()

# Register command groups
app.add_typer(auth.app, name="auth")
app.add_typer(pages.app, name="pages")
app.add_typer(databases.app, name="databases")
app.add_typer(blocks.app, name="blocks")
app.add_typer(search.app, name="search")
app.add_typer(users.app, name="users")
app.add_typer(comments.app, name="comments")
app.add_typer(workspace.app, name="workspace")
app.add_typer(config.app, name="config")


@app.command()
def version() -> None:
    """
    Show the CLI version.

    Displays the version information for the Better Notion CLI.
    """
    typer.echo(format_success({"name": "Better Notion CLI", "version": "0.4.1"}))


@app.callback()
def main(
    ctx: typer.Context,
) -> None:
    """
    Better Notion CLI - Command-line interface for Notion API.

    A CLI for interacting with Notion, designed for AI agents.

    \b
    Features:
    - JSON-only output for programmatic parsing
    - Structured error codes for reliable error handling
    - Async command support for better performance
    - Idempotency support for safe retries

    \b
    Getting Started:
    1. Configure authentication: notion auth login
    2. Check status: notion auth status
    3. Get a page: notion pages get <page_id>

    For more help on a specific command, run: notion <command> --help
    """
    ctx.ensure_object(dict)


if __name__ == "__main__":
    app()
