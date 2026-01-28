"""
Update command for Better Notion CLI.

Provides a simple wrapper around pip to upgrade the package.
"""
from __future__ import annotations

import subprocess
import sys

import typer

from better_notion._cli.async_typer import AsyncTyper
from better_notion._cli.response import format_error, format_success

app = AsyncTyper(help="Update Better Notion CLI", invoke_without_command=True)


@app.callback()
def main(
    ctx: typer.Context,
    check: bool = typer.Option(False, "--check", "-c", help="Only check if an update is available"),
) -> None:
    """
    Update Better Notion CLI to the latest version.

    If no subcommand is specified, performs an update by default.
    """
    # If no subcommand was provided, execute upgrade
    if ctx.invoked_subcommand is None:
        upgrade(check=check)


@app.command()
def upgrade(
    check: bool = typer.Option(False, "--check", "-c", help="Only check if an update is available"),
) -> None:
    """
    Update Better Notion CLI to the latest version.

    This is a simple wrapper around pip that checks for and installs updates.
    pip handles all version checking, downloading, and dependency management.

    Examples:
        notion update                 # Install latest version (default)
        notion update upgrade         # Same as above
        notion update --check         # Check for updates only
        notion update upgrade --check # Same as above
    """
    package_name = "better-notion"

    if check:
        # Check current version vs latest using pip index
        typer.echo(f"Checking for updates for {package_name}...")
        try:
            result = subprocess.run(
                [sys.executable, "-m", "pip", "index", "versions", package_name],
                capture_output=True,
                text=True,
                check=False
            )

            if result.returncode == 0:
                typer.echo(result.stdout)
                return format_success({
                    "status": "checked",
                    "package": package_name
                })
            else:
                # pip index command might not be available in older pip versions
                # Show a helpful message
                typer.echo(f"Currently installed: {package_name}")
                typer.echo("To check for updates manually:")
                typer.echo(f"  pip index versions {package_name}")
                typer.echo("")
                typer.echo("To update:")
                typer.echo(f"  notion update upgrade")
                return format_success({
                    "status": "check_attempted",
                    "package": package_name
                })

        except Exception as e:
            return format_error("CHECK_ERROR", str(e))
    else:
        # Perform the actual upgrade
        typer.echo(f"Updating {package_name} to the latest version...")
        typer.echo("")

        try:
            result = subprocess.run(
                [sys.executable, "-m", "pip", "install", "--upgrade", package_name],
                check=False,
                capture_output=False  # Show progress to user
            )

            if result.returncode == 0:
                typer.echo("")
                typer.echo(f"✓ Successfully updated {package_name}")
                return format_success({
                    "status": "updated",
                    "package": package_name
                })
            else:
                return format_error(
                    "UPDATE_FAILED",
                    f"Failed to update {package_name}. You can try manually:\n  pip install --upgrade {package_name}",
                    False
                )

        except Exception as e:
            return format_error("UPDATE_ERROR", str(e))


@app.command()
def check() -> None:
    """
    Check for available updates.

    This is an alias for 'upgrade --check'.

    Examples:
        notion update check
    """
    upgrade(check=True)


@app.command()
def self() -> None:
    """
    Update Better Notion CLI to the latest version.

    This is an alias for 'upgrade'.

    Examples:
        notion update self
    """
    upgrade(check=False)
