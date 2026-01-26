"""
Tests for AsyncTyper class.

This module tests the AsyncTyper implementation to ensure it correctly
handles both sync and async commands.
"""
from __future__ import annotations

import inspect
import typer
from typer.testing import CliRunner

from better_notion._cli.async_typer import AsyncTyper


def test_async_typer_detects_async_functions() -> None:
    """Test that AsyncTyper correctly identifies async functions."""
    import inspect

    app = AsyncTyper()

    @app.command()
    async def async_func(name: str) -> str:
        """An async command."""
        return f"Hello {name}"

    @app.command()
    def sync_func(name: str) -> str:
        """A sync command."""
        return f"Hello {name}"

    # Check that the original functions are correctly identified
    assert inspect.iscoroutinefunction(async_func)
    assert not inspect.iscoroutinefunction(sync_func)


def test_async_command_execution() -> None:
    """Test that async commands execute correctly."""
    app = AsyncTyper()
    runner = CliRunner()

    @app.command()
    async def hello(name: str = "World"):
        """Greet someone."""
        typer.echo(f"Hello {name}")

    result = runner.invoke(app, ["hello", "Alice"])

    assert result.exit_code == 0
    assert "Hello Alice" in result.stdout


def test_sync_command_execution() -> None:
    """Test that sync commands still work correctly."""
    app = AsyncTyper()
    runner = CliRunner()

    @app.command()
    def greet(name: str = "World"):
        """Greet someone."""
        typer.echo(f"Hello {name}")

    result = runner.invoke(app, ["greet", "Bob"])

    assert result.exit_code == 0
    assert "Hello Bob" in result.stdout


def test_mixed_sync_and_async_commands() -> None:
    """Test that a CLI can have both sync and async commands."""
    app = AsyncTyper()
    runner = CliRunner()

    @app.command()
    async def async_command():
        """An async command."""
        typer.echo("Async result")

    @app.command()
    def sync_command():
        """A sync command."""
        typer.echo("Sync result")

    # Test async command
    result_async = runner.invoke(app, ["async-command"])
    assert result_async.exit_code == 0
    assert "Async result" in result_async.stdout

    # Test sync command
    result_sync = runner.invoke(app, ["sync-command"])
    assert result_sync.exit_code == 0
    assert "Sync result" in result_sync.stdout


def test_async_command_with_options() -> None:
    """Test async commands with options and arguments."""
    app = AsyncTyper()
    runner = CliRunner()

    @app.command()
    async def greet(name: str, greeting: str = "Hello"):
        """Greet someone with a custom greeting."""
        typer.echo(f"{greeting}, {name}!")

    result = runner.invoke(app, ["greet", "Charlie", "--greeting", "Hi"])

    assert result.exit_code == 0
    assert "Hi, Charlie!" in result.stdout


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
    """Test that multiple async commands work correctly."""
    app = AsyncTyper()
    runner = CliRunner()

    @app.command()
    async def command1():
        """First async command."""
        typer.echo("Command 1")

    @app.command()
    async def command2():
        """Second async command."""
        typer.echo("Command 2")

    @app.command()
    async def command3():
        """Third async command."""
        typer.echo("Command 3")

    # Test all commands
    for i in range(1, 4):
        result = runner.invoke(app, [f"command{i}"])
        assert result.exit_code == 0
        assert f"Command {i}" in result.stdout


def test_async_typer_with_callback() -> None:
    """Test AsyncTyper with a callback (e.g., for a command group)."""
    app = AsyncTyper()
    runner = CliRunner()

    @app.callback()
    async def main_callback():
        """Main callback for the app."""
        pass  # Callbacks don't need to return anything

    @app.command()
    async def subcommand():
        """A subcommand."""
        typer.echo("Subcommand executed")

    # Note: Callbacks are executed differently, so we just test it doesn't crash
    result = runner.invoke(app, ["subcommand"])
    assert result.exit_code == 0
    assert "Subcommand executed" in result.stdout
