## Plugin CLI Commands Specification

Building on the plugin system proposal, here's a detailed specification for the **plugin management CLI commands** that should be implemented:

### Proposed CLI Interface

```bash
notion plugin <command> [options]
```

### Available Commands

#### 1. Add/Install Plugin
```bash
notion plugin add <source> [options]

# Examples:
notion plugin add organizations
notion plugin add https://github.com/company/notion-plugins.git
notion plugin add company-notion-plugins --index pypi
notion plugin add /path/to/local/plugin --link
```

**Options:**
- `--source, -s`: Package source (pypi, git, local) [default: auto-detect]
- `--version, -v`: Specific version to install
- `--name, -n`: Custom name for the plugin
- `--link, -l`: Create symlink instead of copy (for local development)
- `--global, -g`: Install system-wide instead of user-local
- `--force, -f`: Overwrite if plugin already exists

**Features:**
- Auto-detect source from URL/pattern
- Install dependencies automatically
- Validate plugin before installation
- Show installation progress
- Verify plugin integrity

#### 2. Remove/Uninstall Plugin
```bash
notion plugin remove <plugin-name> [options]

# Examples:
notion plugin remove organizations
notion plugin remove organizations --purge
notion plugin remove organizations --force
```

**Options:**
- `--purge, -p`: Remove plugin configuration and data
- `--force, -f`: Remove even if other plugins depend on it
- `--keep-config, -k`: Keep plugin configuration file

**Features:**
- Check dependencies before removal
- Warn if other plugins use this one
- Backup plugin data before removal
- Cleanup cached files

#### 3. List Plugins
```bash
notion plugin list [options]

# Examples:
notion plugin list
notion plugin list --verbose
notion plugin list --installed-only
notion plugin list | grep organizations
```

**Options:**
- `--verbose, -v`: Show detailed information
- `--installed-only, -i`: Show only installed plugins
- `--available-only, -a`: Show available from configured sources
- `--outdated, -o`: Show plugins with updates available
- `--format, -f`: Output format (table, json, plain)

**Output Example:**
```
Installed Plugins:
┌────────────────────┬─────────┬────────────────────────┬────────────┐
│ Name               │ Version │ Description            │ Author     │
├────────────────────┼─────────┼────────────────────────┼────────────┤
│ organizations      │ 1.2.0   │ Manage organizations   │ Company    │
│ workflows          │ 2.1.3   │ Custom workflows       │ Team       │
│ daily-standup      │ 0.5.0   │ Daily standup reports   │ Community  │
└────────────────────┴─────────┴────────────────────────┴────────────┘
```

#### 4. Update Plugin
```bash
notion plugin update <plugin-name> [options]

# Examples:
notion plugin update organizations
notion plugin update --all
notion plugin update organizations --major
```

**Options:**
- `--all, -a`: Update all installed plugins
- `--major, -M`: Allow major version updates
- `--pre-release, -p`: Include pre-release versions
- `--dry-run, -d`: Show what would be updated without updating
- `--force, -f`: Update even if version check fails

**Features:**
- Check for updates before downloading
- Show changelog if available
- Backup current version before update
- Rollback on failure

#### 5. Show Plugin Info
```bash
notion plugin info <plugin-name> [options]

# Examples:
notion plugin info organizations
notion plugin info organizations --json
notion plugin info organizations --show-commands
```

**Options:**
- `--json, -j`: Output as JSON
- `--show-commands, -c`: List commands provided by plugin
- `--show-deps, -d`: Show plugin dependencies
- `--show-config, -s`: Show current configuration

**Output Example:**
```
Plugin: organizations
Version: 1.2.0
Author: Company <dev@company.com>
Description: Manage organizations database
Homepage: https://github.com/company/notion-plugins

Commands provided:
  - list-organizations: List all organizations
  - get-organization: Get organization by ID
  - add-organization: Add new organization

Dependencies:
  - better-notion >= 0.8.0
  - requests >= 2.28.0

Configuration:
  Database ID: org-db-abc123
  Cache TTL: 3600
```

#### 6. Search Plugins
```bash
notion plugin search <query> [options]

# Examples:
notion plugin search organizations
notion plugin search workflow --source pypi
notion plugin search --list-all
```

**Options:**
- `--source, -s`: Search in specific source (pypi, github, local)
- `--limit, -n`: Maximum results to show [default: 20]
- `--verbose, -v`: Show detailed results
- `--installed, -i`: Show only installed plugins matching query

**Sources Configuration:**
Sources can be configured in `~/.notion/plugins/sources.json`:
```json
{
  "sources": [
    {
      "name": "pypi",
      "type": "pypi",
      "url": "https://pypi.org/pypi"
    },
    {
      "name": "company-plugins",
      "type": "git",
      "url": "https://github.com/company/notion-plugins"
    },
    {
      "name": "community",
      "type": "registry",
      "url": "https://notion-plugins.org/api"
    }
  ]
}
```

#### 7. Init/New Plugin (Scaffolding)
```bash
notion plugin init <plugin-name> [options]

# Examples:
notion plugin init my-custom-plugin
notion plugin init workflows --template advanced
notion plugin init daily-report --from existing-orgs
```

**Options:**
- `--template, -t`: Template to use (basic, advanced, with-config)
- `--from, -f`: Create based on existing plugin
- `--description, -d`: Plugin description
- `--author, -a`: Plugin author
- `--dir`: Output directory [default: ~/.notion/plugins/]

**Generated Structure:**
```
~/.notion/plugins/my-custom-plugin/
├── __init__.py
├── plugin.py          # Main plugin code
├── config.json        # Plugin configuration
├── README.md          # Documentation
├── pyproject.toml     # Package metadata
└── tests/
    └── test_plugin.py
```

**Template Examples:**

**Basic Template:**
```python
# plugin.py
from better_notion.plugins import CommandPlugin

class MyCustomPlugin(CommandPlugin):
    """My custom plugin."""

    def register_commands(self, app):
        @app.command("my-command")
        def my_command():
            """My custom command."""
            pass
```

**Advanced Template:**
```python
# plugin.py
from better_notion.plugins import CommandPlugin, DataPlugin
import typer

class MyCustomPlugin(CommandPlugin, DataPlugin):
    """My custom plugin with commands and data processing."""

    def __init__(self):
        self.config = self.load_config()

    def register_commands(self, app):
        @app.command("my-command")
        @app.option("--option", help="Command option")
        def my_command(option: str = None):
            """My custom command."""
            # Use self.config here
            pass

    def register_filters(self):
        return {
            "my_filter": self.my_filter_function
        }

    def load_config(self):
        """Load plugin configuration."""
        import json
        from pathlib import Path
        config_file = Path(__file__).parent / "config.json"
        if config_file.exists():
            return json.loads(config_file.read_text())
        return {}
```

#### 8. Enable/Disable Plugin
```bash
notion plugin enable <plugin-name>
notion plugin disable <plugin-name>

# Examples:
notion plugin enable organizations
notion plugin disable daily-standup
```

**Use Cases:**
- Temporarily disable plugin without removing
- Debug by disabling plugins one by one
- Keep plugin installed but not active

#### 9. Validate Plugin
```bash
notion plugin validate <plugin-name> [options]

# Examples:
notion plugin validate organizations
notion plugin validate organizations --strict
notion plugin validate /path/to/plugin
```

**Options:**
- `--strict, -s`: Fail on warnings
- `--detailed, -d`: Show detailed validation report
- `--fix, -f`: Automatically fix issues if possible

**Validation Checks:**
- Plugin structure is correct
- Required files exist
- Configuration is valid
- Dependencies are satisfied
- Commands are properly registered
- No naming conflicts with other plugins

#### 10. Export/Import Plugin Configuration
```bash
notion plugin export [options]
notion plugin import <file> [options]

# Examples:
notion plugin export --output my-plugins.json
notion plugin import my-plugins.json --merge
notion plugin export --include-config
```

**Use Cases:**
- Backup plugin configuration
- Share plugins with team
- Migrate to new machine
- Replicate setup across environments

### Configuration Files

#### Plugin Directory Structure
```
~/.notion/
├── plugins/
│   ├── sources.json          # Available plugin sources
│   ├── installed.json        # Installed plugins registry
│   ├── cache/                # Downloaded plugin archives
│   └── */
│       ├── plugin.py         # Main plugin code
│       ├── config.json       # Plugin configuration
│       └── README.md         # Documentation
└── plugin-config.json        # Global plugin settings
```

#### Global Plugin Config
**`~/.notion/plugin-config.json`**:
```json
{
  "plugin_dir": "~/.notion/plugins",
  "auto_update": false,
  "update_interval": 86400,
  "install_location": "user",
  "enable_telemetry": false,
  "default_source": "pypi",
  "sources": [
    "pypi",
    "https://github.com/company/notion-plugins"
  ]
}
```

### Implementation Priority

**Phase 1 (MVP):**
1. `plugin add` - Install from git/pypi/local
2. `plugin remove` - Uninstall plugin
3. `plugin list` - List installed plugins
4. Basic plugin discovery and loading

**Phase 2:**
5. `plugin update` - Update plugins
6. `plugin info` - Show plugin details
7. `plugin validate` - Validate plugin structure
8. Plugin enable/disable

**Phase 3:**
9. `plugin init` - Scaffolding for new plugins
10. `plugin search` - Search available plugins
11. `plugin export/import` - Configuration management
12. Advanced dependency resolution

### Example Workflow

**First-time setup for a team:**

```bash
# 1. Developer creates plugin
cd company-notion-plugins
notion plugin init organizations --template advanced

# 2. Publish plugin
git push origin main
git tag v1.0.0
git push --tags

# 3. Team member installs plugin
notion plugin add https://github.com/company/notion-plugins.git

# 4. Verify installation
notion plugin list
notion plugin info organizations

# 5. Use the plugin commands
notion list-organizations
notion get-organization abc123

# 6. Update when needed
notion plugin update organizations

# 7. Share plugin config with team
notion plugin export --output team-plugins.json
# Send to team via slack/email

# 8. New team member imports all plugins
notion plugin import team-plugins.json
```

### Error Handling

```bash
# Dependency conflict
$ notion plugin add organizations
Error: Plugin 'organizations' requires better-notion >= 0.9.0
You have better-notion 0.8.1 installed.
Run 'pip install --upgrade better-notion' first.

# Name conflict
$ notion plugin add organizations
Warning: Command 'list-organizations' already exists in plugin 'old-orgs'.
Overwrite? [y/N]: n
Error: Installation cancelled.

# Invalid plugin
$ notion plugin add broken-plugin
Error: Plugin validation failed:
  - Missing required file: plugin.py
  - Invalid configuration in config.json
Use --force to install anyway.
```

### Summary

These CLI commands provide a complete plugin management experience:

✅ **Installation**: `notion plugin add <source>`
✅ **Removal**: `notion plugin remove <name>`
✅ **Listing**: `notion plugin list`
✅ **Updates**: `notion plugin update <name>`
✅ **Info**: `notion plugin info <name>`
✅ **Search**: `notion plugin search <query>`
✅ **Creation**: `notion plugin init <name>`
✅ **Validation**: `notion plugin validate <name>`
✅ **Enable/Disable**: `notion plugin enable/disable <name>`
✅ **Export/Import**: `notion plugin export/import`

This makes the plugin system:
- **Easy to use** - Simple commands for all operations
- **Discoverable** - `--help` on every command
- **Team-friendly** - Easy sharing via export/import
- **Professional** - Similar to npm, pip, cargo

Should we implement these commands as specified?
