"""
Authentication commands for Better Notion CLI.

This module provides commands for managing authentication tokens.
"""
from __future__ import annotations

import typer

from better_notion._cli.async_typer import AsyncTyper
from better_notion._cli.config import Config
from better_notion._cli.display import is_human_mode, print_rich_error, print_rich_success

app = AsyncTyper(help="Authentication commands")


@app.command()
def login(
    ctx: typer.Context,
    token: str = typer.Option(
        ...,
        "--token",
        "-t",
        help="Notion API integration token",
        prompt=True,
        hide_input=True,
    ),
    json_output: bool = typer.Option(
        False,
        "--json",
        "-j",
        help="Output in JSON format (for AI agents)",
    ),
) -> None:
    """
    Authenticate with Notion API.

    Stores the authentication token for subsequent CLI commands.
    The token can be obtained from https://www.notion.so/my-integrations.
    """
    config_path = Config.get_config_path()

    # Check if already logged in
    if config_path.exists():
        typer.confirm(
            "You are already authenticated. Overwrite existing credentials?",
            abort=True,
        )

    # Save the token
    try:
        Config.save(token=token)
        print_rich_success(
            "Successfully authenticated with Notion API",
            data={"config_path": str(config_path)},
            json_output=json_output and not is_human_mode()
        )
    except OSError as e:
        print_rich_error(
            f"Failed to save credentials: {e}",
            details={"config_path": str(config_path)},
            json_output=json_output and not is_human_mode()
        )
        raise typer.Exit(1)


@app.command()
def status(
    json_output: bool = typer.Option(
        False,
        "--json",
        "-j",
        help="Output in JSON format (for AI agents)",
    ),
) -> None:
    """
    Check authentication status.

    Verifies the stored authentication token and displays workspace information.
    """
    from better_notion._cli.display import print_rich_info

    config = Config.load()

    info = {
        "status": "authenticated",
        "token_preview": config.token[:20] + "...",
        "timeout": config.timeout,
        "retry_attempts": config.retry_attempts,
    }

    print_rich_info(
        info,
        title="Authentication Status",
        json_output=json_output and not is_human_mode()
    )


@app.command()
def logout(
    json_output: bool = typer.Option(
        False,
        "--json",
        "-j",
        help="Output in JSON format (for AI agents)",
    ),
) -> None:
    """
    Remove stored credentials.

    Deletes the authentication token from the configuration file.
    """
    from better_notion._cli.display import print_rich_error

    config_path = Config.get_config_path()

    if not config_path.exists():
        print_rich_error(
            "No credentials found",
            details={"config_path": str(config_path)},
            json_output=json_output and not is_human_mode()
        )
        raise typer.Exit(1)

    try:
        config_path.unlink()
        print_rich_success(
            f"Credentials removed from {config_path}",
            json_output=json_output and not is_human_mode()
        )
    except OSError as e:
        print_rich_error(
            f"Failed to remove credentials: {e}",
            json_output=json_output and not is_human_mode()
        )
        raise typer.Exit(1)
