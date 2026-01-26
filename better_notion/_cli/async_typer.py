"""
AsyncTyper - Typer with async command support.

Based on community solutions from:
https://github.com/fastapi/typer/discussions/1309

This module extends typer.Typer to automatically detect and run async functions
using asyncer.runnify(), while passing sync functions through unchanged.
"""
from __future__ import annotations

import inspect
from typing import Any, Callable

import asyncer
from typer import Typer
from typer.core import TyperCommand
from typer.models import CommandFunctionType


class AsyncTyper(Typer):
    """
    Typer subclass with automatic async command support.

    Features:
    - Detects async functions automatically via inspect.iscoroutinefunction()
    - Runs async commands with asyncer.runnify()
    - Passes sync commands through unchanged
    - Compatible with all Typer features (options, arguments, callbacks, etc.)

    Example:
        >>> app = AsyncTyper()
        >>> @app.command()
        >>> async def async_command(name: str):
        ...     await do_something_async(name)
        >>> @app.command()
        >>> def sync_command(name: str):
        ...     do_something_sync(name)
    """

    def command(
        self,
        name: str | None = None,
        *,
        cls: type[TyperCommand] | None = None,
        context_settings: dict | None = None,
        help: str | None = None,
        epilog: str | None = None,
        short_help: str | None = None,
        options_metavar: str = "[OPTIONS]",
        add_help_option: bool = True,
        no_args_is_help: bool = False,
        hidden: bool = False,
        deprecated: bool = False,
        rich_help_panel: str | None = None,
    ) -> Callable[[CommandFunctionType], CommandFunctionType]:
        """
        Override command decorator to support async functions.

        This method wraps async functions with a sync wrapper before
        passing them to Typer, allowing async commands to work seamlessly.

        All parameters are passed through to Typer.command() unchanged.

        Args:
            name: Command name (defaults to function name)
            cls: Command class to use
            context_settings: Click context settings
            help: Command help text
            epilog: Text to display after help
            short_help: Short help text
            options_metavar: Placeholder for options in help text
            add_help_option: Whether to add --help option
            no_args_is_help: Whether to show help if no args provided
            hidden: Whether to hide command from help
            deprecated: Whether to mark command as deprecated
            rich_help_panel: Rich help panel name

        Returns:
            Decorator function that handles both sync and async commands
        """

        def decorator(f: CommandFunctionType) -> CommandFunctionType:
            # Wrap async functions with sync wrapper
            if inspect.iscoroutinefunction(f):
                # Create sync wrapper for async function
                def runner(*args: Any, **kwargs: Any) -> Any:
                    return asyncer.runnify(f)(*args, **kwargs)

                # Copy function metadata
                runner.__name__ = f.__name__
                runner.__doc__ = f.__doc__
                runner.__wrapped__ = f

                # Use wrapper for registration
                func_to_decorate = runner
            else:
                func_to_decorate = f

            # Get parent's command decorator and apply it
            parent_decorator = Typer.command(
                self,
                name=name,
                cls=cls,
                context_settings=context_settings,
                help=help,
                epilog=epilog,
                short_help=short_help,
                options_metavar=options_metavar,
                add_help_option=add_help_option,
                no_args_is_help=no_args_is_help,
                hidden=hidden,
                deprecated=deprecated,
                rich_help_panel=rich_help_panel,
            )

            # Apply parent decorator and return result
            return parent_decorator(func_to_decorate)

        return decorator
