# Todo Command `--checked` Parameter Bug

## Description
The `notion blocks todo` command's `--checked` parameter is defined as a flag (boolean switch) rather than a value-accepting parameter, making it impossible to explicitly set a todo item as "checked" or "unchecked".

## Current Behavior
```bash
# This works (defaults to unchecked/False)
notion blocks todo --parent <id> --text "Task name"

# This fails with error: "Got unexpected extra argument (false)"
notion blocks todo --parent <id> --text "Task name" --checked false

# This sets checked to True (because it's a flag presence)
notion blocks todo --parent <id> --text "Task name" --checked
```

## Error Message
```
Usage: notion blocks todo [OPTIONS]
Try 'notion blocks todo --help' for help.

╭─ Error ──────────────────────────────────────────────────────────────────╮
│ Got unexpected extra argument (false)                                     │
╰───────────────────────────────────────────────────────────────────────────╯
```

## Expected Behavior
The `--checked` parameter should accept a boolean value:
```bash
# Explicit unchecked
notion blocks todo --parent <id> --text "Task name" --checked false

# Explicit checked
notion blocks todo --parent <id> --text "Task name" --checked true
```

OR use clearer flag names:
```bash
# Unchecked
notion blocks todo --parent <id> --text "Task name"

# Checked
notion blocks todo --parent <id> --text "Task name" --checked

# Explicit unchecked with flag
notion blocks todo --parent <id> --text "Task name" --unchecked
```

## Root Cause
In `better_notion/_cli/commands/blocks.py`, the parameter is defined as:
```python
checked: bool = typer.Option(False, "--checked", "-c", help="Initial checked state")
```

This defines `--checked` as a flag that, when present, sets `checked=True`. It doesn't accept a value argument.

## Impact
- **User Confusion**: Users expect to pass `true`/`false` to boolean parameters
- **Limited Functionality**: Cannot explicitly create unchecked todos when the default might be checked
- **Inconsistent UX**: Most CLI tools accept values for boolean flags

## Workarounds
1. Omit the `--checked` flag entirely to create unchecked todos (default)
2. Include `--checked` flag to create checked todos

## Proposed Fix
Option 1: Make it a value-accepting parameter
```python
checked: bool = typer.Option(None, "--checked", "-c", help="Initial checked state")
```

Option 2: Use explicit true/false flags (Typer pattern)
```python
checked: bool = typer.Option(False, "--checked/--unchecked", "-c/-u", help="Initial checked state")
```

Option 3: Use enum/choice parameter
```python
checked: str = typer.Option("false", "--checked", "-c", help="Initial checked state (true/false)")
```

## Related Files
- `better_notion/_cli/commands/blocks.py` - CLI command definitions
- `better_notion/_sdk/models/blocks/todo.py` - Todo block model

## Related
- Issue #001: Missing dedicated block commands
- Issue #003: notion blocks children command broken
