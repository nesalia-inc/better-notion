"""
Configuration management for Better Notion CLI.

This module handles loading and saving CLI configuration, including
authentication tokens and user preferences.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import typer


@dataclass
class Config:
    """
    CLI configuration.

    Attributes:
        token: Notion API authentication token
        default_database: Default database ID for queries (optional)
        default_output: Default output format (always "json" for agents)
        timeout: Request timeout in seconds
        retry_attempts: Number of retry attempts for failed requests
    """

    token: str
    default_database: str | None = None
    default_output: str = "json"
    timeout: int = 30
    retry_attempts: int = 3

    @classmethod
    def get_config_path(cls) -> Path:
        """
        Get the path to the config file.

        Returns:
            Path to ~/.notion/config.json
        """
        config_dir = Path.home() / ".notion"
        config_dir.mkdir(parents=True, exist_ok=True)
        return config_dir / "config.json"

    @classmethod
    def load(cls) -> "Config":
        """
        Load configuration from ~/.notion/config.json.

        Returns:
            Loaded Config object

        Raises:
            typer.Exit: If config file doesn't exist
        """
        config_path = cls.get_config_path()

        if not config_path.exists():
            typer.echo(
                "⚠️  Not configured. Run 'notion auth login' first.",
                err=True,
            )
            raise typer.Exit(1)

        try:
            with open(config_path) as f:
                data = json.load(f)
            return cls(**data)
        except (json.JSONDecodeError, TypeError) as e:
            typer.echo(
                f"❌ Invalid config file: {e}",
                err=True,
            )
            raise typer.Exit(1)

    @classmethod
    def save(cls, **kwargs: Any) -> "Config":
        """
        Save configuration to ~/.notion/config.json.

        Args:
            **kwargs: Config fields as keyword arguments

        Returns:
            Saved Config object
        """
        config_path = cls.get_config_path()

        # Validate required fields
        if "token" not in kwargs:
            typer.echo("❌ Token is required", err=True)
            raise typer.Exit(1)

        with open(config_path, "w") as f:
            json.dump(kwargs, f, indent=2)

        typer.echo(f"✅ Configuration saved to {config_path}")
        return cls(**kwargs)

    def to_dict(self) -> dict[str, Any]:
        """
        Convert config to dictionary.

        Returns:
            Dictionary representation of config
        """
        return {
            "token": self.token,
            "default_database": self.default_database,
            "default_output": self.default_output,
            "timeout": self.timeout,
            "retry_attempts": self.retry_attempts,
        }
