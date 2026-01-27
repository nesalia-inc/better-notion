# Plugin System and Official Plugins Repository

## Summary
Implement a comprehensive plugin system for the Better Notion CLI, allowing users to extend functionality through both official plugins (maintained in the main repository) and community plugins. This replaces the simpler alias system approach with a more powerful, portable, and maintainable solution.

## Motivation

### Current Limitations
Users often need to repeat complex commands with specific database IDs:
```bash
# Every time I want to list organizations
notion databases query --database-id org-db-abc123

# Every time I want to see my tasks
notion databases rows --database-id tasks-db-456 --filter '{"Status": "In Progress"}'

# Every time I want to add to inbox
notion pages create --parent inbox-db-789 --title "New Item"
```

This is:
- **Repetitive**: Users type the same commands daily
- **Error-prone**: Manual entry of database IDs
- **Hard to remember**: Complex command structures
- **Not portable**: Aliases must be recreated on each machine
- **Not shareable**: Difficult to distribute across teams

### Problems with Simple Alias System

1. **Machine-Specific Configuration**
   - Each machine requires manual alias setup
   - Team members must recreate aliases on each new machine
   - No way to distribute aliases programmatically
   - CI/CD environments can't easily use custom aliases

2. **Limited Extensibility**
   - Aliases are simple command substitutions
   - Can't add complex logic or custom workflows
   - No way to package and share functionality
   - Limited to single-command mapping

3. **Maintenance Overhead**
   - Every new machine = manual alias configuration
   - No version control for aliases across team
   - Difficult to update aliases across organization
   - Onboarding friction for new team members

### Proposed Solution: Plugin System
Instead of simple aliases, implement a comprehensive plugin system with:

1. **Official Plugins** - Maintained in the Better Notion repository
2. **Plugin Management CLI** - Full lifecycle management commands
3. **Community Plugins** - Third-party plugin ecosystem

## Proposed CLI Interface

### Plugin Management Commands

```bash
notion plugin <command> [options]
```

#### Available Commands

1. **Add/Install Plugin**
   ```bash
   notion plugin add <source> [options]

   # Install official plugin
   notion plugin add organizations

   # Install from Git
   notion plugin add https://github.com/company/plugins.git

   # Install from PyPI
   notion plugin add company-notion-plugins --index pypi

   # Install all official plugins
   notion plugin add --all-official
   ```

2. **Remove/Uninstall Plugin**
   ```bash
   notion plugin remove <plugin-name> [options]
   notion plugin remove organizations --purge
   ```

3. **List Plugins**
   ```bash
   notion plugin list [options]
   notion plugin list --verbose
   notion plugin list --available-official
   notion plugin list --outdated
   ```

4. **Update Plugin**
   ```bash
   notion plugin update <plugin-name> [options]
   notion plugin update --all
   ```

5. **Show Plugin Info**
   ```bash
   notion plugin info <plugin-name> [options]
   notion plugin info organizations --show-commands
   ```

6. **Search Plugins**
   ```bash
   notion plugin search <query> [options]
   notion plugin search organizations
   ```

7. **Create New Plugin**
   ```bash
   notion plugin init <plugin-name> [options]
   notion plugin init my-plugin --template advanced
   ```

8. **Validate Plugin**
   ```bash
   notion plugin validate <plugin-name> [options]
   notion plugin validate organizations --strict
   ```

9. **Enable/Disable Plugin**
   ```bash
   notion plugin enable <plugin-name>
   notion plugin disable <plugin-name>
   ```

10. **Export/Import Configuration**
    ```bash
    notion plugin export [options]
    notion plugin import <file> [options]
    notion plugin export --output team-plugins.json
    ```

## Configuration Files

### Plugin Directory Structure
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

### Global Plugin Config
**`~/.notion/plugin-config.json`**:
```json
{
  "plugin_dir": "~/.notion/plugins",
  "auto_update": false,
  "update_interval": 86400,
  "install_location": "user",
  "enable_telemetry": false,
  "default_source": "pypi",
  "official_plugins": {
    "auto_install": ["productivity"],
    "enabled_by_default": ["organizations", "workflows"]
  }
}
```

## Official Plugins Strategy

### Why Official Plugins in Main Repo?

1. **Simplified Maintenance**
   - Single repository to manage
   - Same release cycle as main package
   - Consistent code review process
   - Easier updates and bug fixes

2. **Trust & Security**
   - Official plugins are vetted and secure
   - No external dependencies to audit
   - Users can trust official plugins
   - Reduced security surface

3. **Better Documentation**
   - Plugins documented alongside core features
   - Consistent documentation style
   - Examples in main README
   - Tutorials use official plugins

4. **Zero-Config Installation**
   ```bash
   # No need to specify URLs or package names
   notion plugin add organizations  # Auto-installs official plugin
   ```

5. **Quality Assurance**
   - Same test coverage as core
   - Version compatibility guaranteed
   - Follows project best practices
   - Integrated into CI/CD

### Proposed Repository Structure

```
better-notion/
├── better_notion/
│   ├── _cli/
│   │   └── commands/
│   ├── _sdk/
│   └── plugins/              # NEW: Official plugins directory
│       ├── __init__.py
│       ├── base.py           # Plugin interface/protocol
│       ├── loader.py         # Plugin loader
│       │
│       ├── official/         # Official plugins
│       │   ├── __init__.py
│       │   ├── organizations.py
│       │   ├── workflows.py
│       │   ├── reports.py
│       │   ├── productivity.py
│       │   └── templates.py
│       │
│       └── examples/         # Example plugins for community
│           ├── simple_plugin.py
│           └── advanced_plugin.py
│
├── tests/
│   └── plugins/              # Plugin tests
│       ├── test_organizations.py
│       ├── test_workflows.py
│       └── test_loader.py
│
└── docs/
    └── plugins/
        ├── index.md
        ├── official-plugins.md
        └── creating-plugins.md
```

### Official Plugins Catalog

#### 1. Organizations Plugin
**Purpose**: Common organization management operations

**Commands**:
- `notion list-organizations` - List all organizations
- `notion get-organization <id>` - Get org details
- `notion add-organization --name <name> --domain <domain>` - Add new org
- `notion update-organization <id> --property <value>` - Update org
- `notion org-stats` - Show organization statistics

#### 2. Workflows Plugin
**Purpose**: Daily workflow automation

**Commands**:
- `notion daily-standup` - Generate daily standup page
- `notion weekly-review` - Create weekly review page
- `notion sprint-planning --sprint <n>` - Sprint planning template
- `notion retro --sprint <n>` - Retrospective template
- `notion 1on1 --with <person>` - 1-on-1 meeting template

#### 3. Reports Plugin
**Purpose**: Generate reports from Notion databases

**Commands**:
- `notion report tasks --status <status>` - Task status report
- `notion report timeline --start <date> --end <date>` - Timeline report
- `notion report workload --user <user>` - Workload analysis
- `notion export-report --format (pdf|csv|md)` - Export report

#### 4. Productivity Plugin
**Purpose**: Personal productivity helpers

**Commands**:
- `notion quick-capture --text <text>` - Quick capture to inbox
- `notion inbox-zero` - Process inbox items
- `notion my-tasks --status active` - Show my active tasks
- `notion focus-timer --minutes <n>` - Pomodoro timer integration
- `notion daily-notes` - Create daily notes page

#### 5. Templates Plugin
**Purpose**: Page and database templates

**Commands**:
- `notion template list` - List available templates
- `notion template apply <name> --parent <db>` - Apply template
- `notion template create --name <name> --from <page>` - Create template

#### 6. Development Plugin
**Purpose**: Developer-specific workflows

**Commands**:
- `notion dev-task --ticket <jira-id>` - Create dev task from ticket
- `notion pr-summary --pr <number>` - Summarize PR in Notion
- `notion code-review --pr <number>` - Code review checklist
- `notion deployment-checklist` - Deployment checklist

## Implementation Plan

### Phase 1: Plugin Infrastructure (MVP)
1. **Plugin Interface & Loader**
   - `CommandPlugin` protocol/interface
   - `PluginLoader` class for discovery
   - Plugin configuration management
   - Default config creation

2. **CLI Integration**
   - `notion plugin` command group
   - Core commands: add, remove, list, info
   - Help text integration
   - Error handling

3. **Official Plugins Directory**
   - Create `better_notion/plugins/` structure
   - Implement first official plugin (productivity)
   - Add tests and documentation

### Phase 2: Plugin Management
1. **Advanced Commands**
   - `plugin update` with dependency resolution
   - `plugin search` across sources
   - `plugin init` for scaffolding
   - `plugin validate` for verification

2. **Plugin Sources**
   - Support multiple plugin sources
   - Source configuration in `sources.json`
   - Auto-discovery of official plugins

3. **Enable/Disable System**
   - Per-plugin enable/disable
   - Dependency checking
   - Conflict resolution

### Phase 3: Official Plugins Expansion
1. **Create Additional Plugins**
   - Organizations plugin
   - Workflows plugin
   - Reports plugin
   - Templates plugin
   - Development plugin

2. **Plugin Templates**
   - Basic template
   - Advanced template
   - With-config template
   - Example plugins

### Phase 4: Community Ecosystem
1. **Third-Party Plugin Support**
   - Plugin marketplace/registry
   - Submission guidelines
   - Security scanning
   - Rating system

2. **Distribution**
   - PyPI package format
   - Git repository support
   - Local plugin loading
   - Auto-updates

## Technical Specifications

### Plugin Interface
```python
# better_notion/plugins/base.py
from abc import ABC, abstractmethod
from typing import Protocol
import typer

class CommandPlugin(Protocol):
    """Interface for command plugins."""

    def register_commands(self, app: typer.Typer) -> None:
        """Register plugin commands with the CLI app."""
        ...

    def get_info(self) -> dict:
        """Return plugin metadata."""
        return {
            "name": "plugin-name",
            "version": "1.0.0",
            "description": "Plugin description",
            "author": "Author name",
            "official": False,
            "dependencies": []
        }

class DataPlugin(Protocol):
    """Interface for data/plugins (filters, formatters, etc.)."""

    def register_filters(self) -> dict:
        """Register custom data filters."""
        ...

    def register_formatters(self) -> dict:
        """Register custom output formatters."""
        ...
```

### Plugin Loader
```python
# better_notion/plugins/loader.py
class PluginLoader:
    """Discover and load plugins from multiple sources."""

    def __init__(self):
        self.plugin_dirs = [
            Path.home() / ".notion" / "plugins",
            Path("/usr/local/lib/notion/plugins"),
            Path.cwd() / ".notion-plugins",
        ]

    def discover(self) -> list[CommandPlugin]:
        """Discover all plugins from configured directories."""
        ...

    def load_from_dir(self, directory: Path) -> list[CommandPlugin]:
        """Load plugins from a directory."""
        ...

    def get_plugin(self, name: str) -> CommandPlugin | None:
        """Get specific plugin by name."""
        ...
```

### Example Plugin Implementation
```python
# better_notion/plugins/official/organizations.py
from better_notion.plugins.base import CommandPlugin
from better_notion._cli.response import format_success
import asyncio
import typer

class OrganizationsPlugin(CommandPlugin):
    """Plugin for managing organizations in Notion."""

    DATABASE_ID = "org-db-abc123"  # Could be in config

    def register_commands(self, app):
        @app.command("list-organizations")
        def list_orgs():
            """List all organizations."""
            async def _list():
                client = get_client()
                db = await client.databases.get(self.DATABASE_ID)
                results = await db.query().collect()
                return format_success({
                    "count": len(results),
                    "organizations": [
                        {"id": r.id, "title": r.title}
                        for r in results
                    ]
                })
            return asyncio.run(_list())

        @app.command("get-organization")
        def get_org(org_id: str):
            """Get organization by ID."""
            # Implementation
            pass

        @app.command("add-organization")
        def add_org(
            name: str = typer.Option(..., "--name", "-n"),
            domain: str = typer.Option(..., "--domain", "-d")
        ):
            """Add a new organization."""
            # Implementation
            pass

    def get_info(self):
        return {
            "name": "organizations",
            "version": "1.0.0",
            "description": "Manage organizations database",
            "author": "Better Notion Team",
            "official": True,
            "category": "database"
        }
```

## Benefits

### For Users
- **Portability** - Git-tracked plugin code works across machines
- **Simplicity** - One command to install: `notion plugin add organizations`
- **Discoverability** - `notion plugin list --available-official`
- **Trust** - Official plugins are vetted and secure
- **Flexibility** - Can create custom plugins for specific needs

### For Maintainers
- **Single Repository** - Official plugins in main repo
- **Unified CI/CD** - Same release cycle
- **Consistent Quality** - Same test coverage
- **Easy Updates** - Update all plugins with main package
- **Version Compatibility** - Guaranteed to work

### For Teams
- **Sharing** - Git repositories for team plugins
- **Standardization** - Shared workflows across organization
- **Onboarding** - Quick setup with plugin configs
- **Customization** - Team-specific plugins
- **Version Control** - Plugin code in git

## Migration from Aliases

While the plugin system is more powerful, we can still support simple aliases as a built-in plugin:

```python
# better_notion/plugins/official/aliases.py
class AliasPlugin(CommandPlugin):
    """Built-in plugin for user-defined aliases."""

    def register_commands(self, app):
        @app.command("alias")
        def alias_cmd(...):
            """Manage aliases (same as originally proposed)."""
            pass
```

This provides:
- Backward compatibility with alias workflow
- Gradual migration path to plugins
- Both systems coexist
- Users can choose their approach

## Examples

### Example 1: Install and Use Official Plugin
```bash
# Install official plugin
$ notion plugin add organizations
Installing official plugin: organizations... ✓

# List installed plugins
$ notion plugin list
Installed Plugins:
┌─────────────────┬─────────┬────────────────────────┬────────────┐
│ Name            │ Version │ Description            │ Author     │
├─────────────────┼─────────┼────────────────────────┼────────────┤
│ organizations   │ 1.0.0   │ Manage organizations   │ Official    │
└─────────────────┴─────────┴────────────────────────┴────────────┘

# Use plugin commands
$ notion list-organizations
{
  "success": true,
  "data": {
    "count": 42,
    "organizations": [...]
  }
}
```

### Example 2: Create Custom Plugin
```bash
# Scaffold new plugin
$ notion plugin init my-workflows --template advanced
Created plugin: my-workflows
Location: ~/.notion/plugins/my-workflows/

# Edit plugin
$ vim ~/.notion/plugins/my-workflows/plugin.py

# Install plugin
$ notion plugin add ~/.notion/plugins/my-workflows
Installing plugin: my-workflows... ✓

# Use plugin commands
$ notion my-custom-command
```

### Example 3: Team Plugin Distribution
```bash
# Create team plugin repo
$ mkdir company-notion-plugins
$ cd company-notion-plugins
$ notion plugin init organizations --template advanced

# Publish to GitHub
$ git init
$ git add .
$ git commit -m "Initial plugin"
$ git push origin main

# Team member installs
$ notion plugin add https://github.com/company/notion-plugins.git

# Export all plugins for sharing
$ notion plugin export --output team-plugins.json

# New team member imports all
$ notion plugin import team-plugins.json
```

## Success Metrics
- **Usage**: Number of users who install plugins
- **Adoption**: Average plugins per user
- **Official vs Community**: Ratio of official to community plugins
- **Satisfaction**: Feedback on plugin system
- **Contributions**: Number of community plugins submitted

## Related Features
- Command history with favorites
- Macro recording (series of commands)
- Interactive mode with shortcuts
- Team/shared plugin repositories

## Open Questions

1. **Plugin scope**: Should plugins be per-project or global? (Recommendation: Start with global, add project-local later)
2. **Official plugins**: Which plugins should we prioritize? (Recommendation: Start with productivity, organizations)
3. **Distribution**: Primary distribution method? (Recommendation: Official in repo, community via PyPI/Git)
4. **Sandboxing**: Should plugins run in sandboxed environment? (Recommendation: Phase 2, security consideration)
5. **API stability**: How to handle breaking changes? (Recommendation: Semantic versioning, deprecation warnings)

See full discussion in comments for:
- Plugin system vs alias system comparison
- Detailed CLI commands specification
- Official plugins strategy
