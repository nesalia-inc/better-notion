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
    plugins,
    search,
    users,
    workspace,
)
from better_notion._cli.response import __version__, format_success

# Create the main CLI app
app = AsyncTyper()

# Register command groups
app.add_typer(auth.app, name="auth")
app.add_typer(pages.app, name="pages")
app.add_typer(databases.app, name="databases")
app.add_typer(blocks.app, name="blocks")
app.add_typer(plugins.app, name="plugin")
app.add_typer(search.app, name="search")
app.add_typer(users.app, name="users")
app.add_typer(comments.app, name="comments")
app.add_typer(workspace.app, name="workspace")
app.add_typer(config.app, name="config")

# Load and register official plugins
def _load_official_plugins():
    """Load and register official plugins."""
    try:
        from better_notion.plugins.official import OFFICIAL_PLUGINS
        from better_notion.plugins.loader import PluginLoader

        loader = PluginLoader()

        for plugin_class in OFFICIAL_PLUGINS:
            try:
                plugin = plugin_class()
                plugin.register_commands(app)
                info = plugin.get_info()
                # Store plugin for later reference
                if not hasattr(app, '_loaded_plugins'):
                    app._loaded_plugins = {}
                app._loaded_plugins[info['name']] = plugin
            except Exception as e:
                # Log but don't fail if a plugin fails to load
                pass
    except ImportError:
        # No official plugins available
        pass


# Load official plugins at startup
_load_official_plugins()


@app.command()
def version() -> None:
    """
    Show the CLI version.

    Displays the version information for the Better Notion CLI.
    """
    typer.echo(format_success({"name": "Better Notion CLI", "version": __version__}))


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
