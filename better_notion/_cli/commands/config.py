"""
Config commands for Better Notion CLI.

This module provides commands for managing CLI configuration.
"""
from __future__ import annotations

import json

import typer

from better_notion._cli.async_typer import AsyncTyper
from better_notion._cli.config import Config
from better_notion._cli.response import format_error, format_success

app = AsyncTyper(help="Configuration commands")


@app.command("get")
def get(key: str = typer.Argument(..., help="Configuration key to get")) -> None:
    """Get a configuration value."""
    try:
        config = Config.load()

        valid_keys = ["token", "default_database", "default_output", "timeout", "retry_attempts"]

        if key not in valid_keys:
            result = format_error(
                "INVALID_KEY",
                f"Invalid key. Valid keys: {', '.join(valid_keys)}",
                retry=False,
            )
            typer.echo(result)
            raise typer.Exit(1)

        value = getattr(config, key, None)
        result = format_success({
            "key": key,
            "value": value,
        })
        typer.echo(result)

    except typer.Exit:
        raise
    except Exception as e:
        result = format_error("UNKNOWN_ERROR", str(e), retry=False)
        typer.echo(result)
        raise typer.Exit(1)


@app.command("set")
def set(
    key: str = typer.Argument(..., help="Configuration key to set"),
    value: str = typer.Argument(..., help="Value to set"),
) -> None:
    """Set a configuration value."""
    try:
        config_path = Config.get_config_path()

        # Load existing config
        if config_path.exists():
            with open(config_path) as f:
                config_data = json.load(f)
        else:
            config_data = {}

        # Parse value based on type
        if key == "timeout" or key == "retry_attempts":
            value = int(value)
        elif key == "token" or key == "default_database" or key == "default_output":
            pass  # Keep as string

        config_data[key] = value

        # Save updated config
        with open(config_path, "w") as f:
            json.dump(config_data, f, indent=2)

        result = format_success({
            "key": key,
            "value": value,
            "status": "set",
        })
        typer.echo(result)

    except Exception as e:
        result = format_error("UNKNOWN_ERROR", str(e), retry=False)
        typer.echo(result)
        raise typer.Exit(1)


@app.command("list")
def list_all() -> None:
    """List all configuration values."""
    try:
        config = Config.load()

        result = format_success({
            "token": config.token[:20] + "..." if config.token else None,
            "default_database": config.default_database,
            "default_output": config.default_output,
            "timeout": config.timeout,
            "retry_attempts": config.retry_attempts,
        })
        typer.echo(result)

    except Exception as e:
        result = format_error("UNKNOWN_ERROR", str(e), retry=False)
        typer.echo(result)
        raise typer.Exit(1)


@app.command("reset")
def reset() -> None:
    """Reset configuration to defaults."""
    try:
        config_path = Config.get_config_path()

        if config_path.exists():
            config_path.unlink()

        result = format_success({
            "status": "reset",
            "message": "Configuration has been reset. Run 'notion auth login' to configure.",
        })
        typer.echo(result)

    except Exception as e:
        result = format_error("UNKNOWN_ERROR", str(e), retry=False)
        typer.echo(result)
        raise typer.Exit(1)
