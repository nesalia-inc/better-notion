"""
Plugin management commands for Better Notion CLI.

Provides commands for managing the plugin system:
- add: Install a plugin
- remove: Uninstall a plugin
- list: List all plugins
- info: Show plugin details
- marketplace: Browse official plugin marketplace
- update: Update plugins
- init: Create a new plugin
- validate: Validate a plugin
- enable/disable: Enable or disable plugins
"""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

import typer
from typer.testing import CliRunner

from better_notion._cli.async_typer import AsyncTyper
from better_notion._cli.response import format_error, format_success
from better_notion.plugins.loader import PluginLoader
from better_notion.plugins.base import CommandPlugin

app = AsyncTyper(help="Plugin management commands")


def get_plugin_loader() -> PluginLoader:
    """Get a plugin loader instance."""
    return PluginLoader()


@app.command()
def add(
    source: str = typer.Argument(..., help="Plugin source (name, git URL, or local path)"),
    name: str = typer.Option(None, "--name", "-n", help="Custom name for the plugin"),
    global_install: bool = typer.Option(False, "--global", "-g", help="Install system-wide"),
) -> None:
    """
    Install a plugin from various sources.

    Examples:
        notion plugin add organizations          # Install official plugin
        notion plugin add https://github.com/user/plugin.git  # Install from git
        notion plugin add /path/to/plugin       # Install from local path
    """
    try:
        loader = get_plugin_loader()
        plugin_dir = Path.home() / ".notion" / "plugins"

        if global_install:
            plugin_dir = Path("/usr/local/lib/notion/plugins")

        plugin_dir.mkdir(parents=True, exist_ok=True)

        # Determine source type
        if source.startswith(("http://", "https://")):
            # Git repository
            typer.echo(f"Cloning plugin from {source}...")
            dest = plugin_dir / (name or Path(source).stem)
            subprocess.run(
                ["git", "clone", source, str(dest)],
                check=True,
                capture_output=True
            )
            return format_success({
                "plugin": name or Path(source).stem,
                "source": source,
                "location": str(dest),
                "status": "installed"
            })

        elif Path(source).exists():
            # Local path
            typer.echo(f"Installing plugin from {source}...")
            dest = plugin_dir / (name or Path(source).stem)
            if dest.exists():
                shutil.rmtree(dest) if dest.is_dir() else dest.unlink()
            shutil.copytree(source, dest) if (Path(source) / "__init__.py").exists() else shutil.copy2(source, dest)
            return format_success({
                "plugin": name or Path(source).stem,
                "source": source,
                "location": str(dest),
                "status": "installed"
            })

        else:
            # Try as official plugin or PyPI package
            # Check if it's an official plugin
            if loader.is_official_plugin(source):
                typer.echo(f"Plugin '{source}' is already bundled as an official plugin.")
                return format_success({
                    "plugin": source,
                    "type": "official",
                    "status": "already-installed"
                })

            # Try pip install
            typer.echo(f"Installing plugin from PyPI: {source}...")
            result = subprocess.run(
                [sys.executable, "-m", "pip", "install", source],
                capture_output=True,
                text=True
            )

            if result.returncode == 0:
                return format_success({
                    "plugin": source,
                    "source": "pypi",
                    "status": "installed"
                })
            else:
                return format_error(
                    "INSTALL_FAILED",
                    f"Failed to install plugin: {result.stderr}",
                    False
                )

    except subprocess.CalledProcessError as e:
        return format_error("INSTALL_ERROR",  str(e))
    except Exception as e:
        return format_error("UNKNOWN_ERROR",  str(e))


@app.command()
def remove(
    plugin_name: str = typer.Argument(..., help="Name of the plugin to remove"),
    purge: bool = typer.Option(False, "--purge", "-p", help="Remove plugin configuration and data"),
) -> None:
    """
    Remove an installed plugin.

    Examples:
        notion plugin remove organizations
        notion plugin remove my-plugin --purge
    """
    try:
        plugin_dir = Path.home() / ".notion" / "plugins"
        plugin_path = plugin_dir / plugin_name

        # Check if plugin exists
        if not plugin_path.exists():
            return format_error(
                "PLUGIN_NOT_FOUND",
                f"Plugin '{plugin_name}' not found in {plugin_dir}",
                False
            )

        # Remove plugin
        if plugin_path.is_dir():
            shutil.rmtree(plugin_path)
        else:
            plugin_path.unlink()

        # Remove config if purging
        if purge:
            config_file = Path.home() / ".notion" / "plugins" / f"{plugin_name}.json"
            if config_file.exists():
                config_file.unlink()

        return format_success({
            "plugin": plugin_name,
            "status": "removed",
            "purged": purge
        })

    except Exception as e:
        return format_error("REMOVE_ERROR",  str(e))


@app.command("list")
def list_plugins(
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Show detailed information"),
    json_output: bool = typer.Option(False, "--json", "-j", help="Output as JSON"),
) -> None:
    """
    List all installed and available plugins.

    Examples:
        notion plugin list
        notion plugin list --verbose
        notion plugin list --json
    """
    try:
        loader = get_plugin_loader()
        plugins = loader.list_plugins()

        if json_output:
            return typer.echo(json.dumps(plugins, indent=2))

        # Display as table
        if not plugins:
            typer.echo("No plugins installed.")
            typer.echo(f"\nPlugins directory: {Path.home() / '.notion' / 'plugins'}")
            return

        typer.echo("Installed Plugins:")
        typer.echo("┌" + "─" * 50 + "┐")

        for name, info in plugins.items():
            official_marker = "✓" if info.get("official") else " "
            typer.echo(f"│ {official_marker} {name:30} │ {info.get('description', 'No description'):40} │")

            if verbose:
                typer.echo(f"│   Version: {info.get('version', 'unknown'):20} │")
                typer.echo(f"│   Author:  {info.get('author', 'unknown'):20} │")
                typer.echo("│" + "─" * 50 + "│")

        typer.echo("└" + "─" * 50 + "┘")

    except Exception as e:
        return format_error("LIST_ERROR",  str(e))


@app.command()
def info(
    plugin_name: str = typer.Argument(..., help="Name of the plugin"),
    show_commands: bool = typer.Option(False, "--show-commands", "-c", help="List commands provided by plugin"),
) -> None:
    """
    Show detailed information about a plugin.

    Examples:
        notion plugin info organizations
        notion plugin info organizations --show-commands
    """
    try:
        loader = get_plugin_loader()
        plugin = loader.load_plugin(plugin_name)

        if not plugin:
            return format_error(
                "PLUGIN_NOT_FOUND",
                f"Plugin '{plugin_name}' not found"
            )

        info = plugin.get_info()

        typer.echo(f"Plugin: {info.get('name')}")
        typer.echo(f"Version: {info.get('version')}")
        typer.echo(f"Author: {info.get('author')}")
        typer.echo(f"Description: {info.get('description')}")
        typer.echo(f"Official: {'Yes' if info.get('official') else 'No'}")

        if info.get('dependencies'):
            typer.echo(f"\nDependencies:")
            for dep in info.get('dependencies', []):
                typer.echo(f"  - {dep}")

        if show_commands:
            typer.echo(f"\nCommands provided by plugin:")
            # This would require inspecting registered commands
            # For now, just show a message
            typer.echo("  (Command listing not yet implemented)")

    except Exception as e:
        return format_error("INFO_ERROR",  str(e))


@app.command()
def init(
    plugin_name: str = typer.Argument(..., help="Name of the plugin to create"),
    template: str = typer.Option("basic", "--template", "-t", help="Template to use (basic, advanced)"),
    description: str = typer.Option(None, "--description", "-d", help="Plugin description"),
    author: str = typer.Option(None, "--author", "-a", help="Plugin author"),
    output_dir: str = typer.Option(str(Path.home() / ".notion" / "plugins"), "--dir", help="Output directory"),
) -> None:
    """
    Create a new plugin with scaffolding.

    Examples:
        notion plugin init my-plugin
        notion plugin init my-plugin --template advanced
        notion plugin init workflows --description "My workflows" --author "John Doe"
    """
    try:
        output = Path(output_dir)
        output.mkdir(parents=True, exist_ok=True)

        plugin_dir = output / plugin_name
        plugin_dir.mkdir(exist_ok=True)

        # Create __init__.py
        (plugin_dir / "__init__.py").write_text(
            f'"""\"{plugin_name} plugin for Better Notion CLI.\"\""\n'
            f'from __future__ import annotations\n\n'
            f'from .plugin import {plugin_name.replace("-", "_").title()}Plugin\n\n'
            f'__all__ = ["{plugin_name.replace("-", "_").title()}Plugin"]\n'
        )

        # Create plugin.py
        if template == "basic":
            plugin_content = f'''"""
{plugin_name} plugin for Better Notion CLI.
"""
from __future__ import annotations

import typer
from better_notion.plugins.base import PluginInterface
from typing import Any


class {plugin_name.replace("-", "_").title()}Plugin(PluginInterface):
    """{description or plugin_name} plugin."""

    def register_commands(self, app: typer.Typer) -> None:
        """Register plugin commands with the CLI app."""
        @app.command("{plugin_name.replace("-", "_")}-command")
        def {plugin_name.replace("-", "_")}_command():
            """Your custom command."""
            typer.echo("Hello from {plugin_name} plugin!")

    def get_info(self) -> dict[str, Any]:
        """Return plugin metadata."""
        return {{
            "name": "{plugin_name}",
            "version": "1.0.0",
            "description": "{description or "A custom plugin"}",
            "author": "{author or "Unknown"}",
            "official": False
        }}
'''
        else:  # advanced template
            plugin_content = f'''"""
{plugin_name} plugin for Better Notion CLI (Advanced Template).
"""
from __future__ import annotations

import asyncio
from typing import Any

import typer
from better_notion._cli.config import Config
from better_notion._cli.response import format_success, format_error
from better_notion._sdk.client import NotionClient
from better_notion.plugins.base import PluginInterface


def get_client() -> NotionClient:
    """Get authenticated Notion client."""
    config = Config.load()
    return NotionClient(auth=config.token, timeout=config.timeout)


class {plugin_name.replace("-", "_").title()}Plugin(PluginInterface):
    """{description or plugin_name} plugin (advanced)."""

    def __init__(self):
        """Initialize the plugin."""
        self.config = self._load_config()

    def _load_config(self) -> dict:
        """Load plugin configuration."""
        import json
        from pathlib import Path

        config_file = Path(__file__).parent / "config.json"
        if config_file.exists():
            return json.loads(config_file.read_text())
        return {{}}

    def register_commands(self, app: typer.Typer) -> None:
        """Register plugin commands with the CLI app."""
        @app.command("{plugin_name.replace("-", "_")}-action")
        def {plugin_name.replace("-", "_")}_action(
            param: str = typer.Option(..., "--param", "-p", help="Parameter")
        ) -> None:
            """Your custom command action."""
            async def _action():
                try:
                    client = get_client()
                    # Your logic here
                    return format_success({{"message": "Action executed"}})

                except Exception as e:
                    return format_error("ACTION_ERROR",  str(e))

            result = asyncio.run(_action())
            typer.echo(result)

    def get_info(self) -> dict[str, Any]:
        """Return plugin metadata."""
        return {{
            "name": "{plugin_name}",
            "version": "1.0.0",
            "description": "{description or "A custom plugin"}",
            "author": "{author or "Unknown"}",
            "official": False,
            "dependencies": []
        }}
'''

        (plugin_dir / "plugin.py").write_text(plugin_content)

        # Create config.json for advanced template
        if template == "advanced":
            (plugin_dir / "config.json").write_text(json.dumps({
                "database_id": "",
                "settings": {}
            }, indent=2))

        # Create README.md
        (plugin_dir / "README.md").write_text(
            f"# {plugin_name} Plugin\n\n"
            f"{description or 'A custom plugin for Better Notion CLI.'}\n\n"
            f"## Installation\n\n"
            f"```bash\nnotion plugin add {plugin_name}\n```\n\n"
            f"## Usage\n\n"
            f"```bash\nnotion {plugin_name.replace('-', '-')}-command --param value\n```\n"
        )

        return format_success({
            "plugin": plugin_name,
            "location": str(plugin_dir),
            "template": template,
            "status": "created"
        })

    except Exception as e:
        return format_error("INIT_ERROR",  str(e))


@app.command()
def validate(
    plugin_name: str = typer.Argument(..., help="Name of the plugin to validate"),
    strict: bool = typer.Option(False, "--strict", "-s", help="Fail on warnings"),
) -> None:
    """
    Validate a plugin's structure and configuration.

    Examples:
        notion plugin validate organizations
        notion plugin validate my-plugin --strict
    """
    try:
        loader = get_plugin_loader()
        plugin = loader.load_plugin(plugin_name)

        if not plugin:
            return format_error(
                "PLUGIN_NOT_FOUND",
                f"Plugin '{plugin_name}' not found"
            )

        # Validate plugin
        is_valid, errors = plugin.validate()

        if is_valid:
            return format_success({
                "plugin": plugin_name,
                "valid": True,
                "errors": []
            })
        else:
            return format_error(
                "VALIDATION_FAILED",
                f"Plugin validation failed with {len(errors)} error(s)",
                details={"errors": errors}
            )

    except Exception as e:
        return format_error("VALIDATE_ERROR",  str(e))


@app.command()
def enable(
    plugin_name: str = typer.Argument(..., help="Name of the plugin to enable"),
) -> None:
    """
    Enable a plugin.

    Examples:
        notion plugin enable organizations
    """
    # Create enabled plugins list
    config_file = Path.home() / ".notion" / "plugins" / "enabled.json"
    config_file.parent.mkdir(parents=True, exist_ok=True)

    try:
        if config_file.exists():
            config = json.loads(config_file.read_text())
        else:
            config = {"enabled": []}

        if plugin_name not in config["enabled"]:
            config["enabled"].append(plugin_name)
            config_file.write_text(json.dumps(config, indent=2))

        return format_success({
            "plugin": plugin_name,
            "status": "enabled"
        })

    except Exception as e:
        return format_error("ENABLE_ERROR",  str(e))


@app.command()
def disable(
    plugin_name: str = typer.Argument(..., help="Name of the plugin to disable"),
) -> None:
    """
    Disable a plugin.

    Examples:
        notion plugin disable organizations
    """
    config_file = Path.home() / ".notion" / "plugins" / "enabled.json"

    try:
        if config_file.exists():
            config = json.loads(config_file.read_text())
            if plugin_name in config.get("enabled", []):
                config["enabled"].remove(plugin_name)
                config_file.write_text(json.dumps(config, indent=2))

        return format_success({
            "plugin": plugin_name,
            "status": "disabled"
        })

    except Exception as e:
        return format_error("DISABLE_ERROR",  str(e))


@app.command()
def update(
    plugin_name: str = typer.Argument(..., help="Name of the plugin to update"),
) -> None:
    """
    Update a plugin to the latest version.

    Examples:
        notion plugin update organizations
    """
    try:
        # For git-based plugins, pull latest changes
        plugin_dir = Path.home() / ".notion" / "plugins" / plugin_name

        if (plugin_dir / ".git").exists():
            subprocess.run(
                ["git", "pull"],
                cwd=plugin_dir,
                check=True,
                capture_output=True
            )
            return format_success({
                "plugin": plugin_name,
                "status": "updated"
            })
        else:
            return format_error(
                "UPDATE_NOT_SUPPORTED",
                f"Plugin '{plugin_name}' does not support automatic updates",
                False
            )

    except subprocess.CalledProcessError as e:
        return format_error("UPDATE_ERROR",  str(e))
    except Exception as e:
        return format_error("UNKNOWN_ERROR",  str(e))


@app.command()
def marketplace(
    category: str = typer.Option(None, "--category", "-c", help="Filter by category"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Show detailed information"),
    json_output: bool = typer.Option(False, "--json", "-j", help="Output as JSON"),
) -> None:
    """
    List available official plugins in the marketplace.

    Shows all official plugins that are bundled with the CLI package,
    including their descriptions, versions, and other metadata.

    Examples:
        notion plugin marketplace
        notion plugin marketplace --category productivity
        notion plugin marketplace --verbose
        notion plugin marketplace --json
    """
    try:
        # Import official plugins registry
        from better_notion.plugins.official import OFFICIAL_PLUGINS

        if not OFFICIAL_PLUGINS:
            typer.echo("No official plugins available in the marketplace.")
            return

        # Collect plugin information
        plugins_data = []
        for plugin_class in OFFICIAL_PLUGINS:
            try:
                plugin = plugin_class()
                info = plugin.get_info()
                plugins_data.append(info)
            except Exception:
                # Skip plugins that fail to instantiate
                continue

        # Filter by category if specified
        if category:
            plugins_data = [p for p in plugins_data if p.get("category") == category]

        # Output as JSON if requested
        if json_output:
            return typer.echo(json.dumps({"plugins": plugins_data}, indent=2))

        # Display in formatted table
        if not plugins_data:
            if category:
                typer.echo(f"No plugins found in category '{category}'.")
            else:
                typer.echo("No official plugins available.")
            return

        typer.echo("Official Plugins Marketplace")
        typer.echo("=" * 70)
        typer.echo(f"Found {len(plugins_data)} official plugin(s)")
        typer.echo()

        for idx, info in enumerate(plugins_data, 1):
            typer.echo(f"{idx}. {info.get('name', 'unknown')}")
            typer.echo(f"   {info.get('description', 'No description')}")

            # Always show basic info
            typer.echo(f"   Version: {info.get('version', 'unknown'):8} │ "
                      f"Author: {info.get('author', 'unknown')}")

            if verbose:
                # Show additional details in verbose mode
                if info.get("category"):
                    typer.echo(f"   Category: {info.get('category')}")
                if info.get("dependencies"):
                    deps = info.get("dependencies", [])
                    if deps:
                        typer.echo(f"   Dependencies: {', '.join(deps)}")
                    else:
                        typer.echo(f"   Dependencies: None")
                if info.get("official"):
                    typer.echo(f"   Official: ✓ Yes")

                # Show any additional metadata
                for key in ["license", "homepage", "repository"]:
                    if info.get(key):
                        typer.echo(f"   {key.capitalize()}: {info.get(key)}")

            typer.echo()

        if category:
            typer.echo(f"Showing plugins in category: {category}")
        typer.echo("\nTip: Use --verbose to see more details")

    except Exception as e:
        return format_error("MARKETPLACE_ERROR", str(e))
