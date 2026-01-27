# Plugin System

The Better Notion CLI supports a powerful plugin system that allows you to extend the CLI with custom commands and functionality.

## Overview

Plugins can add new commands to the CLI, provide custom data processing, and integrate seamlessly with the existing command structure. There are two types of plugins:

1. **Official Plugins** - Maintained in the Better Notion repository
2. **User Plugins** - Created by users for personal or team workflows

## Official Plugins

The following official plugins are included with Better Notion CLI but must be explicitly enabled to use:

### Productivity Plugin

The productivity plugin provides common productivity commands for daily workflows:

- `notion quick-capture` - Quick capture text to your inbox database
- `notion inbox-zero` - Process inbox items to achieve inbox zero
- `notion my-tasks` - Show your active tasks
- `notion daily-notes` - Create a daily notes page

**Note**: Official plugins are **not enabled by default** to keep the CLI lightweight. You must explicitly enable them:

```bash
# Enable the productivity plugin
notion plugin enable productivity

# Now the commands are available
notion quick-capture --text "Meeting notes"
```

### Enabling Official Plugins

Official plugins are bundled with the CLI but not activated by default. To enable an official plugin:

```bash
notion plugin enable <plugin-name>
```

For example:
```bash
notion plugin enable productivity
```

Once enabled, the plugin's commands become available in the CLI.

To disable an official plugin:
```bash
notion plugin disable <plugin-name>
```

To see which official plugins are available:
```bash
notion plugin list --available-official
```

## Installing Plugins

### Install an Official Plugin

Official plugins are automatically available - no installation needed!

### Install from Git

```bash
notion plugin add https://github.com/user/plugin.git
```

### Install from PyPI

```bash
notion plugin add plugin-name
```

### Install from Local Path

```bash
notion plugin add /path/to/plugin
```

## Managing Plugins

### List Installed Plugins

```bash
notion plugin list
```

### Show Plugin Information

```bash
notion plugin info <plugin-name>
```

### Remove a Plugin

```bash
notion plugin remove <plugin-name>
```

### Update a Plugin

```bash
notion plugin update <plugin-name>
```

### Validate a Plugin

```bash
notion plugin validate <plugin-name>
```

## Creating Plugins

### Create a New Plugin

Use the plugin scaffolding command to create a new plugin:

```bash
# Basic plugin
notion plugin init my-plugin --template basic

# Advanced plugin
notion plugin init my-plugin --template advanced
```

This creates a plugin scaffold in `~/.notion/plugins/my-plugin/` with:
- `__init__.py` - Package initialization
- `plugin.py` - Plugin implementation
- `README.md` - Documentation
- `config.json` - Configuration (advanced template)

### Basic Plugin Structure

A basic plugin consists of a Python file with a `register` function:

```python
# my_plugin.py
def register(app):
    """Register plugin commands with the CLI app."""
    @app.command("my-command")
    def my_command():
        typer.echo("Hello from my plugin!")

PLUGIN_INFO = {
    "name": "my-plugin",
    "version": "1.0.0",
    "description": "My custom plugin",
    "author": "Your Name"
}
```

### Advanced Plugin Structure

For more complex plugins, use the plugin interface:

```python
from better_notion.plugins.base import PluginInterface
from better_notion._cli.config import Config
from better_notion._sdk.client import NotionClient
import asyncio

class MyPlugin(PluginInterface):
    """My custom plugin."""

    def register_commands(self, app):
        """Register plugin commands."""
        @app.command("my-action")
        def my_action(param: str = typer.Option(..., "--param")):
            """My custom command."""
            async def _action():
                client = NotionClient(auth=Config.load().token)
                # Your logic here
                pass
            return asyncio.run(_action())

    def get_info(self):
        """Return plugin metadata."""
        return {
            "name": "my-plugin",
            "version": "1.0.0",
            "description": "My plugin description",
            "author": "Your Name",
            "official": False
        }
```

## Plugin Directory

Plugins are stored in `~/.notion/plugins/` by default. Each plugin can be:
- A single Python file
- A directory with `__init__.py` and `plugin.py`

## Configuration

Plugin configuration is stored in `~/.notion/plugin-config.json`:

```json
{
  "plugin_dir": "~/.notion/plugins",
  "auto_update": false,
  "install_location": "user",
  "official_plugins": {
    "auto_install": [],
    "enabled_by_default": []
  }
}
```

## Plugin Interface

### CommandPlugin Protocol

Command plugins must implement:
- `register_commands(app)` - Register commands with the Typer app
- `get_info()` - Return plugin metadata

### DataPlugin Protocol

Data plugins can optionally implement:
- `register_filters()` - Register custom data filters
- `register_formatters()` - Register custom output formatters

## Examples

### Example 1: Simple Command Plugin

```python
# hello.py
def register(app):
    @app.command("say-hello")
    def say_hello(name: str = typer.Option("World", "--name", "-n")):
        typer.echo(f"Hello, {name}!")

PLUGIN_INFO = {
    "name": "hello",
    "version": "1.0.0",
    "description": "Say hello",
    "author": "You"
}
```

Install:
```bash
notion plugin add hello.py
```

Use:
```bash
notion say-hello --name Alice
```

### Example 2: Database Query Plugin

```python
# my_db.py
from better_notion.plugins.base import PluginInterface
from better_notion._sdk.client import NotionClient
import asyncio

class MyDatabasePlugin(PluginInterface):
    """Plugin for querying my database."""

    def register_commands(self, app):
        @app.command("query-my-db")
        def query_db():
            """Query my database."""
            async def _query():
                client = NotionClient(auth=Config.load().token)
                db = await client.databases.get("db-id-123")
                results = await db.query().collect()
                # Process results
                pass
            return asyncio.run(_query())

    def get_info(self):
        return {
            "name": "my-db",
            "version": "1.0.0",
            "description": "Query my database",
            "author": "You",
            "official": False
        }
```

## Enabling/Disabling Plugins

Plugins can be enabled or disabled:

```bash
notion plugin enable <plugin-name>
notion plugin disable <plugin-name>
```

Enabled plugins are tracked in `~/.notion/plugins/enabled.json`.

## Troubleshooting

### Plugin Not Found

If a plugin is not being found:
1. Check it's in the correct directory: `~/.notion/plugins/`
2. Verify the plugin file has a `register` function or plugin class
3. Ensure the file is a valid Python module

### Commands Not Available

If plugin commands are not showing up:
1. Verify the plugin is properly loaded: `notion plugin list`
2. Check the plugin's `register` function is correct
3. Ensure commands are registered using `@app.command()`

### Import Errors

If you get import errors:
1. Check all dependencies are installed
2. Verify the plugin file has valid Python syntax
3. Run `notion plugin validate <plugin-name>` to check structure

## Best Practices

1. **Use Descriptive Names** - Plugin and command names should be clear and descriptive
2. **Provide Documentation** - Include a README.md with usage examples
3. **Handle Errors** - Use try-except blocks and return proper error responses
4. **Version Your Plugins** - Use semantic versioning
5. **Test Your Plugins** - Validate with `notion plugin validate` before sharing
6. **Use Configuration** - Store database IDs and settings in config files
7. **Be Idempotent** - Commands should be safe to run multiple times
8. **Provide Help** - Include docstrings for all commands

## Advanced Topics

### Plugin Dependencies

Plugins can declare dependencies in their `get_info()` method:

```python
def get_info(self):
    return {
        ...
        "dependencies": ["requests>=2.28.0", "another-package"]
    }
```

### Plugin Configuration

Plugins can load their own configuration files:

```python
import json
from pathlib import Path

class MyPlugin(PluginInterface):
    def __init__(self):
        config_file = Path(__file__).parent / "config.json"
        if config_file.exists():
            self.config = json.loads(config_file.read_text())
        else:
            self.config = {}
```

### Composition

Plugins can call other plugins or CLI commands:

```python
from better_notion._cli.commands.pages import app as pages_app

# Call pages commands
result = subprocess.run(["notion", "pages", "get", page_id])
```

## See Also

- [Plugin Development Guide](./plugin-development.md) - Detailed plugin development tutorial
- [API Reference](./api-reference.md) - Complete plugin API documentation
- [Official Plugins](./official-plugins.md) - Documentation for official plugins
