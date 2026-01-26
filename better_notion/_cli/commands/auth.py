"""
Authentication commands for Better Notion CLI.

This module provides commands for managing authentication tokens.
"""
from __future__ import annotations

from better_notion._cli.async_typer import AsyncTyper
from better_notion._cli.config import Config
from better_notion._cli.response import format_success

app = AsyncTyper(help="Authentication commands")


@app.command()
def status() -> None:
    """
    Check authentication status.

    Verifies the stored authentication token and displays workspace information.
    """
    import typer

    try:
        config = Config.load()
        typer.echo(
            format_success(
                {
                    "status": "authenticated",
                    "token": config.token[:20] + "...",  # Show partial token
                    "timeout": config.timeout,
                    "retry_attempts": config.retry_attempts,
                }
            )
        )
    except typer.Exit:
        # Config.load() already showed error message
        pass


@app.command()
def logout() -> None:
    """
    Remove stored credentials.

    Deletes the authentication token from the configuration file.
    """
    import typer

    config_path = Config.get_config_path()

    if not config_path.exists():
        typer.echo("⚠️  No credentials found", err=True)
        raise typer.Exit(1)

    try:
        config_path.unlink()
        typer.echo(
            format_success(
                {
                    "status": "logged_out",
                    "message": f"Credentials removed from {config_path}",
                }
            )
        )
    except OSError as e:
        typer.echo(f"❌ Failed to remove credentials: {e}", err=True)
        raise typer.Exit(1)
