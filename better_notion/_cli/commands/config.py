"""
Config commands for Better Notion CLI.

This module provides commands for managing CLI configuration.
"""
from __future__ import annotations

import json

import typer

from better_notion._cli.async_typer import AsyncTyper
from better_notion._cli.config import Config
from better_notion._cli.display import is_human_mode, print_rich_error, print_rich_info, print_rich_success

app = AsyncTyper(help="Configuration commands")


@app.command("get")
def get(
    key: str = typer.Argument(..., help="Configuration key to get"),
    json_output: bool = typer.Option(False, "--json", "-j", help="Output as JSON"),
) -> None:
    """Get a configuration value."""
    use_json = json_output or not is_human_mode()

    try:
        config = Config.load()

        valid_keys = ["token", "default_database", "default_output", "timeout", "retry_attempts"]

        if key not in valid_keys:
            print_rich_error(
                f"Invalid key. Valid keys: {', '.join(valid_keys)}",
                code="INVALID_KEY",
                json_output=use_json
            )
            raise typer.Exit(1)

        value = getattr(config, key, None)

        # Mask token for security
        if key == "token" and value:
            value = value[:20] + "..."

        print_rich_info(
            {"key": key, "value": value},
            title="Configuration Value",
            json_output=use_json
        )

    except typer.Exit:
        raise
    except Exception as e:
        print_rich_error(
            f"Failed to get configuration: {e}",
            code="UNKNOWN_ERROR",
            json_output=use_json
        )
        raise typer.Exit(1)


@app.command("set")
def set(
    key: str = typer.Argument(..., help="Configuration key to set"),
    value: str = typer.Argument(..., help="Value to set"),
    json_output: bool = typer.Option(False, "--json", "-j", help="Output as JSON"),
) -> None:
    """Set a configuration value."""
    use_json = json_output or not is_human_mode()

    try:
        config_path = Config.get_config_path()

        # Load existing config
        if config_path.exists():
            with open(config_path) as f:
                config_data = json.load(f)
        else:
            config_data = {}

        # Parse value based on type
        parsed_value = value
        if key == "timeout" or key == "retry_attempts":
            parsed_value = int(value)
        elif key == "token" or key == "default_database" or key == "default_output":
            pass  # Keep as string

        config_data[key] = parsed_value

        # Save updated config
        with open(config_path, "w") as f:
            json.dump(config_data, f, indent=2)

        print_rich_success(
            f"Configuration '{key}' set to {parsed_value}",
            data={"key": key, "value": parsed_value},
            json_output=use_json
        )

    except ValueError:
        print_rich_error(
            f"Invalid value for '{key}'. Expected type: int for timeout/retry_attempts",
            code="INVALID_VALUE",
            json_output=use_json
        )
        raise typer.Exit(1)
    except Exception as e:
        print_rich_error(
            f"Failed to set configuration: {e}",
            code="UNKNOWN_ERROR",
            json_output=use_json
        )
        raise typer.Exit(1)


@app.command("list")
def list_all(
    json_output: bool = typer.Option(False, "--json", "-j", help="Output as JSON"),
) -> None:
    """List all configuration values."""
    use_json = json_output or not is_human_mode()

    try:
        from better_notion._cli.display import print_rich_table

        config = Config.load()

        config_data = [
            {"key": "token", "value": config.token[:20] + "..." if config.token else None},
            {"key": "default_database", "value": config.default_database},
            {"key": "default_output", "value": config.default_output},
            {"key": "timeout", "value": config.timeout},
            {"key": "retry_attempts", "value": config.retry_attempts},
        ]

        print_rich_table(
            config_data,
            title="Configuration",
            columns=["key", "value"],
            json_output=use_json
        )

    except Exception as e:
        print_rich_error(
            f"Failed to list configuration: {e}",
            code="UNKNOWN_ERROR",
            json_output=use_json
        )
        raise typer.Exit(1)


@app.command("reset")
def reset(
    json_output: bool = typer.Option(False, "--json", "-j", help="Output as JSON"),
) -> None:
    """Reset configuration to defaults."""
    use_json = json_output or not is_human_mode()

    try:
        config_path = Config.get_config_path()

        if config_path.exists():
            config_path.unlink()

        print_rich_success(
            "Configuration has been reset. Run 'notion auth login' to configure.",
            data={"status": "reset"},
            json_output=use_json
        )

    except Exception as e:
        print_rich_error(
            f"Failed to reset configuration: {e}",
            code="UNKNOWN_ERROR",
            json_output=use_json
        )
        raise typer.Exit(1)
