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
    update,
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
app.add_typer(update.app, name="update")

# Load and register official plugins
def _load_official_plugins():
    """Load and register official plugins, respecting their enabled/disabled state."""
    try:
        from better_notion.plugins.official import OFFICIAL_PLUGINS
        from better_notion.plugins.loader import PluginLoader
        from better_notion.plugins.state import PluginStateManager

        loader = PluginLoader()
        state_manager = PluginStateManager()

        for plugin_class in OFFICIAL_PLUGINS:
            try:
                plugin = plugin_class()
                info = plugin.get_info()
                plugin_name = info.get('name')

                # Check if plugin is disabled
                if not state_manager.is_enabled(plugin_name):
                    # Skip loading this plugin
                    continue

                # Register the plugin's commands
                plugin.register_commands(app)

                # Store plugin for later reference
                if not hasattr(app, '_loaded_plugins'):
                    app._loaded_plugins = {}
                app._loaded_plugins[plugin_name] = plugin
            except Exception as e:
                # Log but don't fail if a plugin fails to load
                pass
    except ImportError:
        # No official plugins available
        pass


# Load official plugins at startup
_load_official_plugins()


@app.command()
def version(
    json_output: bool = typer.Option(False, "--json", "-j", help="Output as JSON"),
) -> None:
    """
    Show the CLI version.

    Displays the version information for the Better Notion CLI.
    """
    from better_notion._cli.display import is_human_mode, print_rich_info

    use_json = json_output or not is_human_mode()

    version_info = {
        "name": "Better Notion CLI",
        "version": __version__
    }

    if use_json:
        import json
        typer.echo(json.dumps({
            "success": True,
            "meta": {
                "version": __version__,
                "timestamp": None,
                "rate_limit": {
                    "remaining": None,
                    "reset_at": None
                }
            },
            "data": version_info
        }, indent=2))
    else:
        from rich.console import Console
        console = Console()
        console.print(f"[bold blue]Better Notion CLI[/bold blue] version [bold green]{__version__}[/bold green]")


@app.command()
def docs(
    topic: str = typer.Argument(None, help="Documentation topic to retrieve"),
    format: str = typer.Option("json", "--format", "-f", help="Output format (json, yaml, pretty)"),
) -> None:
    """
    Get system documentation for AI agents.

    This command provides comprehensive documentation about the Better Notion CLI
    that AI agents can consume to understand the system at a high level.

    Without arguments: List all available topics
    With topic: Show detailed documentation for that topic

    Available topics:
    - overview: System architecture and core concepts
    - plugins: Available plugins and their capabilities
    - commands: All available commands and their purposes

    Examples:
        $ notion docs                  # List all topics
        $ notion docs overview         # Get system overview
        $ notion docs overview --format json
    """
    import json

    # Define available topics
    topics = {
        "overview": {
            "name": "overview",
            "title": "System Overview",
            "description": "Better Notion CLI - Command-line interface for Notion API",
            "version": __version__,
            "architecture": {
                "description": "A CLI for interacting with Notion, designed for AI agents",
                "features": [
                    "JSON-only output for programmatic parsing",
                    "Structured error codes for reliable error handling",
                    "Async command support for better performance",
                    "Plugin system for extensibility",
                ]
            },
            "core_concepts": [
                {
                    "name": "Pages",
                    "description": "Notion pages with content blocks",
                    "commands": ["notion pages get", "notion pages create", "notion pages update"]
                },
                {
                    "name": "Databases",
                    "description": "Notion databases with structured properties",
                    "commands": ["notion databases get", "notion databases query", "notion databases create"]
                },
                {
                    "name": "Blocks",
                    "description": "Content blocks (paragraphs, headings, lists, etc.)",
                    "commands": ["notion blocks get", "notion blocks create"]
                },
                {
                    "name": "Plugins",
                    "description": "Extensible command groups for specialized workflows",
                    "commands": ["notion agents", "notion plugin list"]
                }
            ],
            "getting_started": [
                "1. Configure authentication: notion auth login",
                "2. Check status: notion auth status",
                "3. Get a page: notion pages get <page_id>"
            ]
        },
        "plugins": {
            "name": "plugins",
            "title": "Available Plugins",
            "description": "Official plugins that extend CLI functionality",
            "plugins": [
                {
                    "name": "agents",
                    "description": "Workflow management system for software development",
                    "commands": ["agents init", "agents info", "agents schema"],
                    "documentation": "Run 'notion agents schema' for complete documentation"
                }
            ]
        },
        "commands": {
            "name": "commands",
            "title": "Available Commands",
            "description": "Core CLI commands organized by category",
            "categories": [
                {
                    "name": "Authentication",
                    "commands": [
                        {"command": "notion auth login", "purpose": "Authenticate with Notion"},
                        {"command": "notion auth status", "purpose": "Check authentication status"},
                        {"command": "notion auth logout", "purpose": "Logout and clear credentials"}
                    ]
                },
                {
                    "name": "Pages",
                    "commands": [
                        {"command": "notion pages get <id>", "purpose": "Get page details"},
                        {"command": "notion pages create", "purpose": "Create a new page"},
                        {"command": "notion pages update <id>", "purpose": "Update page properties"},
                        {"command": "notion pages search <query>", "purpose": "Search for pages"}
                    ]
                },
                {
                    "name": "Databases",
                    "commands": [
                        {"command": "notion databases get <id>", "purpose": "Get database details"},
                        {"command": "notion databases query <id>", "purpose": "Query database with filters"},
                        {"command": "notion databases create", "purpose": "Create a new database"}
                    ]
                },
                {
                    "name": "Blocks",
                    "commands": [
                        {"command": "notion blocks get <id>", "purpose": "Get block details"},
                        {"command": "notion blocks children <id>", "purpose": "Get block children"}
                    ]
                }
            ]
        }
    }

    # If no topic specified, list available topics
    if topic is None:
        topics_list = {
            "available_topics": [
                {
                    "name": name,
                    "title": info["title"],
                    "description": info["description"],
                }
                for name, info in topics.items()
            ],
            "usage": "notion docs <topic> for detailed information",
            "examples": [
                "notion docs overview",
                "notion docs plugins",
                "notion docs commands"
            ]
        }
        typer.echo(json.dumps(topics_list, indent=2))
        return

    # Get the requested topic
    topic_lower = topic.lower()
    if topic_lower not in topics:
        result = {
            "success": False,
            "error": {
                "code": "UNKNOWN_TOPIC",
                "message": f"Unknown topic: {topic}",
                "retry": False,
                "details": {
                    "available_topics": list(topics.keys())
                }
            }
        }
        typer.echo(json.dumps(result, indent=2))
        raise typer.Exit(code=1)

    # Return the topic documentation
    topic_info = topics[topic_lower]
    typer.echo(json.dumps(topic_info, indent=2))


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
