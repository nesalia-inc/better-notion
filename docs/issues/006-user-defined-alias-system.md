# User-Defined Alias System for CLI

## Summary
Add ability for users to create custom command aliases in the Better Notion CLI, allowing personalized shortcuts for frequently-used commands.

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
- **Not personalized**: One-size-fits-all CLI

### Proposed Solution
User-defined aliases stored in `~/.notion/aliases.json`:
```bash
# After setup, users can simply type:
notion orgs          # Lists organizations
notion my-tasks      # Shows my active tasks
notion quick-add     # Adds to inbox
```

### Use Cases
1. **Personal workflows** - Quick access to frequently-used databases
2. **Team standardization** - Share aliases across team members
3. **Custom shortcuts** - Create memorable names for specific databases
4. **Complex commands** - Simplify multi-step operations
5. **Role-based access** - Different aliases for different contexts

## Proposed CLI Interface

### Alias Management Commands
```bash
# List all user aliases
notion alias --list
# or
notion alias -l

# Edit aliases file (opens in editor)
notion alias --edit
# or
notion alias -e

# Show alias configuration
notion alias <name> --show
```

### Execute Alias
```bash
# Execute an alias directly
notion <alias-name>

# Example: after defining "orgs" alias
notion orgs
# Equivalent to: notion databases query --database-id org-db-abc123
```

## Configuration File

### Location
`~/.notion/aliases.json`

### Structure
```json
{
  "aliases": {
    "orgs": {
      "description": "List all organizations",
      "command": "databases query",
      "args": {
        "database_id": "org-db-abc123"
      }
    },
    "my-tasks": {
      "description": "Show my active tasks",
      "command": "databases rows",
      "args": {
        "database_id": "tasks-db-456",
        "filter": "{\"property\": \"Status\", \"value\": \"In Progress\"}"
      }
    },
    "quick-add": {
      "description": "Quick add item to inbox",
      "command": "pages create",
      "args": {
        "parent": "inbox-db-789",
        "title": "{title}"
      },
      "template": true
    },
    "list-users": {
      "description": "List all users from users DB",
      "command": "databases query",
      "args": {
        "database_id": "users-db-999"
      }
    }
  }
}
```

### Field Descriptions
- **description**: Human-readable description (shown in `--list`)
- **command**: Base command to execute (e.g., `databases query`)
- **args**: Default arguments to pass to the command
- **template**: (optional) If true, alias accepts parameters from command line

## Implementation Plan

### Phase 1: Core Alias System (MVP)
1. **Alias Manager Module**
   - `AliasManager` class to load/save/execute aliases
   - JSON file loading with validation
   - Default config creation if file doesn't exist

2. **CLI Integration**
   - `notion alias` command for management
   - Dynamic command registration for user aliases
   - Help text integration

3. **Execution Engine**
   - Resolve alias to underlying command
   - Merge default args with runtime args
   - Execute and return results

### Phase 2: Advanced Features
1. **Template Variables**
   - Support `{variable}` placeholders in alias definitions
   - Runtime substitution from command-line args

2. **Alias Composition**
   - Allow aliases to call other aliases
   - Build complex workflows from simple aliases

3. **Shared Aliases**
   - Team alias files (`.notion/team-aliases.json`)
   - Include mechanism for shared configs

### Phase 3: Alias Development Tools
1. **Alias Editor**
   - Interactive alias creation wizard
   - Command capture: `notion alias --record <name> <command>`

2. **Validation**
   - Test alias without execution
   - Show what command would be run

3. **Documentation**
   - Generate docs from alias file
   - Export/import alias sets

## Technical Specifications

### Alias Manager Class
```python
class AliasManager:
    """Manage user-defined CLI aliases."""

    DEFAULT_ALIASES_FILE = Path.home() / ".notion" / "aliases.json"

    def __init__(self, aliases_file: Path | None = None)
    def load(self) -> None
    def save(self) -> None
    def get(self, alias_name: str) -> dict | None
    def list_all(self) -> dict[str, dict]
    def execute(self, alias_name: str, extra_args: dict | None = None) -> str
    def validate(self, alias_config: dict) -> bool
    def _create_default_config(self) -> None
    def _execute_command(self, command: str, args: dict) -> str
```

### Command Registration
Dynamically register aliases as CLI commands:
```python
alias_manager = AliasManager()

for alias_name, alias_config in alias_manager.list_all().items():
    @app.command(alias_name)
    def alias_command(alias_name=alias_name, alias_config=alias_config, **kwargs):
        result = alias_manager.execute(alias_name, kwargs)
        typer.echo(result)
```

### Error Handling
- **File not found**: Create default config with example
- **Invalid JSON**: Show error with line number
- **Alias not found**: Clear error message
- **Command execution error**: Pass through original error

## Examples

### Example 1: Simple Database Shortcut
**Config**:
```json
{
  "aliases": {
    "orgs": {
      "description": "List organizations",
      "command": "databases query",
      "args": {
        "database_id": "org-db-abc123"
      }
    }
  }
}
```

**Usage**:
```bash
$ notion orgs
{
  "success": true,
  "data": {
    "count": 42,
    "databases": [...]
  }
}
```

### Example 2: Alias with Filter
**Config**:
```json
{
  "aliases": {
    "my-tasks": {
      "description": "My active tasks",
      "command": "databases rows",
      "args": {
        "database_id": "tasks-db-456",
        "filter": "{\"property\": \"Status\", \"value\": \"In Progress\"}"
      }
    }
  }
}
```

**Usage**:
```bash
$ notion my-tasks
{
  "success": true,
  "data": {
    "database_id": "tasks-db-456",
    "count": 7,
    "rows": [...]
  }
}
```

### Example 3: Template Alias (Phase 2)
**Config**:
```json
{
  "aliases": {
    "add-task": {
      "description": "Add task to inbox",
      "command": "blocks create",
      "args": {
        "parent": "inbox-page-123",
        "type": "to_do",
        "text": "{text}"
      },
      "template": true
    }
  }
}
```

**Usage**:
```bash
$ notion add-task --text "Buy groceries"
{
  "success": true,
  "data": {
    "id": "block-789",
    "type": "to_do"
  }
}
```

## Edge Cases to Handle

1. **Name Conflicts**
   - Alias name conflicts with built-in command
   - Solution: Built-in commands take priority, warn user

2. **Circular References**
   - Alias A calls alias B which calls alias A
   - Solution: Detect and prevent circular dependencies

3. **Invalid Commands**
   - Alias references non-existent command
   - Solution: Validate on load, show clear error

4. **Missing Arguments**
   - Alias requires args not provided
   - Solution: Use defaults or prompt user

5. **File Permissions**
   - Can't write to `~/.notion/aliases.json`
   - Solution: Clear error with fix suggestion

6. **Config Migration**
   - Alias config format changes
   - Solution: Version field, auto-migration

## Benefits

1. **Personalization** - Each user has their own shortcuts
2. **Productivity** - Reduce typing for common operations
3. **Memorability** - Use meaningful names instead of IDs
4. **Discoverability** - `notion alias --list` shows all shortcuts
5. **Shareability** - Team alias files for standard workflows
6. **Non-Breaking** - Optional feature, no changes to existing CLI
7. **Extensible** - Foundation for future enhancements

## Alternatives Considered

### 1. Shell Aliases
**Pros**: Simple, no code changes
**Cons**: Not discoverable, shell-specific, can't use in scripts

### 2. Environment Variables
**Pros**: Standard approach
**Cons**: Limited to simple values, no structure

### 3. Plugin System
**Pros**: Maximum flexibility
**Cons**: Overkill for simple use case, security concerns

### 4. Hardcoded Shortcuts
**Pros**: Simple to implement
**Cons**: Not customizable, one-size-fits-all

**Chosen Approach**: User-defined aliases in JSON file
- Best balance of flexibility and simplicity
- Discoverable via CLI
- Easy to share and version control
- No security concerns (user-space only)

## Success Metrics
- **Usage**: Number of users who create aliases
- **Adoption**: Average aliases per user
- **Satisfaction**: Feedback on usefulness
- **Reduction**: Decrease in command length (avg chars saved)

## Related Features
- Command history with favorites
- Macro recording (series of commands)
- Interactive mode with shortcuts
- Team/shared alias management

## Open Questions

1. **Alias scope**: Should aliases be per-project or global? (Recommendation: Start with global)
2. **Command capture**: Should we offer `notion alias --record`? (Recommendation: Phase 2)
3. **Validation**: Validate aliases on load or on execution? (Recommendation: On load with warning)
4. **Conflicts**: How to handle alias/command name conflicts? (Recommendation: Built-ins take priority)
5. **Sharing**: Format for sharing aliases? (Recommendation: Simple JSON files)
