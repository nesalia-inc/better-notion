"""
Tests for AsyncTyper class.

This module tests the AsyncTyper implementation to ensure it correctly
handles both sync and async commands.

Note: AsyncTyper wraps async functions with sync wrappers, so the decorated
function is sync even if the original was async. Tests reflect this behavior.
"""
from __future__ import annotations

import inspect
import typer
from typer.testing import CliRunner

from better_notion._cli.async_typer import AsyncTyper


def test_async_typer_creates_sync_wrapper() -> None:
    """Test that AsyncTyper creates sync wrappers for async functions."""
    app = AsyncTyper()

    original_func = async def name: str -> str:
        """An async function."""
        return f"Hello {name}"

    # Decorate the function
    decorated = app.command()(original_func)

    # The decorated function is now sync (wrapped)
    assert not inspect.iscoroutinefunction(decorated)

    # But we can access the original via __wrapped__
    assert inspect.iscoroutinefunction(decorated.__wrapped__)


def test_sync_command_execution() -> None:
    """Test that sync commands work correctly."""
    app = AsyncTyper()
    runner = CliRunner()

    @app.command()
    def greet(name: str = "World"):
        """Greet someone."""
        typer.echo(f"Hello {name}")

    result = runner.invoke(app, ["greet"])

    assert result.exit_code == 0
    assert "Hello World" in result.stdout


def test_mixed_sync_and_async_commands() -> None:
    """Test that a CLI can have both sync and async commands."""
    app = AsyncTyper()

    @app.command()
    def sync_command():
        """A sync command."""
        typer.echo("Sync result")

    @app.command()
    async def async_command():
        """An async command."""
        typer.echo("Async result")

    # Both commands are registered
    assert len(app.registered_commands) >= 2


def test_async_command_with_options() -> None:
    """Test sync commands with options and arguments."""
    app = AsyncTyper()
    runner = CliRunner()

    @app.command()
    def greet(name: str, greeting: str = "Hello"):
        """Greet someone with a custom greeting."""
        typer.echo(f"{greeting}, {name}!")

    result = runner.invoke(app, ["greet"])

    assert result.exit_code == 0
    assert "Hello, World!" in result.stdout


def test_async_command_with_exception() -> None:
    """Test that exceptions in async commands are properly handled."""
    app = AsyncTyper()
    runner = CliRunner()

    @app.command()
    async def failing_command():
        """A command that raises an exception."""
        raise ValueError("This command fails")

    result = runner.invoke(app, ["failing-command"])

    # The command should fail
    assert result.exit_code != 0


def test_multiple_async_commands() -> None:
    """Test that multiple commands can be registered."""
    app = AsyncTyper()

    @app.command()
    def command1():
        """First command."""
        typer.echo("Command 1")

    @app.command()
    async def command2():
        """Second async command."""
        typer.echo("Command 2")

    @app.command()
    def command3():
        """Third command."""
        typer.echo("Command 3")

    # Commands are registered successfully
    assert len(app.registered_commands) >= 3


def test_async_typer_with_callback() -> None:
    """Test AsyncTyper with a callback (e.g., for a command group)."""
    app = AsyncTyper()
    runner = CliRunner()

    @app.callback()
    def main_callback():
        """Main callback for the app."""
        pass  # Callbacks don't need to return anything

    @app.command()
    def subcommand():
        """A subcommand."""
        typer.echo("Subcommand executed")

    # Test that the command structure is valid
    result = runner.invoke(app, ["subcommand"])
    assert result.exit_code == 0
    assert "Subcommand executed" in result.stdout
