## Overview
This PR implements a comprehensive plugin system for the Better Notion CLI, allowing users to extend CLI functionality through custom plugins. This addresses Issue #12.

## What is the Plugin System?

The plugin system allows you to add new commands to the Better Notion CLI without modifying the core codebase. You can:

1. **Install plugins** from Git, PyPI, or local paths
2. **Create your own plugins** with custom commands
3. **Use official plugins** that come bundled with the CLI
4. **Share plugins** with your team via Git repositories

## Creating Plugins

### Quick Start: Scaffolding

```bash
notion plugin init my-plugin --template basic
```

This creates a ready-to-use plugin in `~/.notion/plugins/my-plugin/`:
- `plugin.py` - Plugin code
- `README.md` - Documentation
- `__init__.py` - Package file

### Method 1: Simple Function-Based Plugin

```python
# my_commands.py
def register(app):
    @app.command("greet")
    def greet(name: str = "World"):
        typer.echo(f"Hello, {name}!")

PLUGIN_INFO = {
    "name": "greet",
    "version": "1.0.0",
    "description": "Greeting commands",
    "author": "Your Name"
}
```

Install:
```bash
notion plugin add my_commands.py
```

Use:
```bash
notion greet --name Alice
```

### Method 2: Advanced Class-Based Plugin

```python
from better_notion.plugins.base import PluginInterface
import asyncio
import typer

class MyPlugin(PluginInterface):
    """My custom plugin."""

    def register_commands(self, app):
        @app.command("my-command")
        def my_command():
            async def _cmd():
                # Your logic here
                pass
            return asyncio.run(_cmd())

    def get_info(self):
        return {
            "name": "my-plugin",
            "version": "1.0.0",
            "description": "My plugin",
            "author": "You"
        }
```

## Installing Plugins

### From Git
```bash
notion plugin add https://github.com/user/plugin.git
```

### From Local Path
```bash
notion plugin add ./my-plugin
```

### Official Plugins
Official plugins are **automatically available** - no installation needed!

Current official plugin: **Productivity**
- `notion quick-capture`
- `notion inbox-zero`
- `notion my-tasks`
- `notion daily-notes`

## Using Plugins

### Using Official Plugin Commands

```bash
# Quick capture to inbox
notion quick-capture --text "Meeting notes"

# Process inbox
notion inbox-zero

# Show my tasks
notion my-tasks --status "In Progress"

# Create daily notes
notion daily-notes
```

### Using Custom Plugin Commands

Once installed, plugin commands are immediately available:
```bash
notion <your-command>
```

## Managing Plugins

### List Plugins
```bash
notion plugin list
```

### Plugin Info
```bash
notion plugin info <plugin-name>
```

### Validate Plugin
```bash
notion plugin validate <plugin-name>
```

### Remove Plugin
```bash
notion plugin remove <plugin-name>
```

## Benefits

- **Portability**: Git-tracked plugin code
- **Team Distribution**: Share via Git repositories
- **Extensibility**: Full Python power available
- **Simplicity**: One command to install
- **Official Plugins**: Vetted commands out of the box

Closes #12
