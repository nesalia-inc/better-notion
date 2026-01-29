# Bug: `notion databases create` fails with "Bad request" - unclear schema format

## Summary

The database creation command requires a `--schema` parameter but the expected format is unclear, and all attempts result in generic "Bad request" errors.

## Steps to Reproduce

```bash
# Attempt 1: No schema
notion databases create --parent <page-id> --title "Test DB"

# Attempt 2: Empty schema
notion databases create --parent <page-id> --title "Test DB" --schema "{}"

# Attempt 3: Schema with properties
notion databases create --parent <page-id> --title "Test DB" \
  --schema '{"properties": {"Name": {"title": {}}}}'
```

All result in:
```json
{
  "error": {
    "code": "UNKNOWN_ERROR",
    "message": "Bad request",
    "retry": false
  }
}
```

## Expected Behavior

1. Clear documentation of schema format
2. Schema validation with helpful error messages
3. Default schema if none provided (just title)
4. Examples of valid schemas

## Actual Behavior

- Generic "Bad request" with no details
- No indication of what's wrong with the schema
- No examples in help documentation
- Schema format unclear (JSON? properties format?)

## Environment

- **OS**: Windows 11, Linux, Mac
- **Python**: 3.14
- **better-notion**: 1.4.0

## Root Cause

**File**: `better_notion/_cli/commands/databases.py`

Multiple issues:

1. **Schema format undocumented** - Users don't know what format to use
2. **No validation** - Invalid schemas sent directly to Notion API
3. **Error handling** - Notion API errors not propagated usefully
4. **Default behavior** - Should work with empty schema (title-only DB)

## Current Implementation Issues

```python
# databases.py (approximate)
@app.command()
def create(
    parent: str = typer.Option(..., "--parent", "-p"),
    title: str = typer.Option(..., "--title", "-t"),
    schema: str = typer.Option("{}", "--schema", "-s"),
):
    # ...
    database = await client.databases.create(
        parent=parent,
        title=title,
        **json.loads(schema)  # <-- Error prone, no validation
    )
```

## Proposed Solution

### 1. Define Schema Format

Based on Notion API documentation, schema should be:

```json
{
  "title": "Database Title",
  "icon": "📊",
  "properties": {
    "Name": {
      "title": {}
    },
    "Status": {
      "select": {
        "options": [
          {"name": "To Do", "color": "gray"},
          {"name": "Done", "color": "green"}
        ]
      }
    },
    "Tags": {
      "multi_select": {
        "options": [
          {"name": "Work", "color": "blue"},
          {"name": "Personal", "color": "orange"}
        ]
      }
    }
  }
}
```

### 2. Add Schema Validation

```python
def validate_database_schema(schema: dict) -> list[str]:
    """Validate database schema and return list of errors."""
    errors = []

    if not isinstance(schema, dict):
        errors.append("Schema must be a JSON object")
        return errors

    # Check properties
    properties = schema.get("properties", {})
    if not isinstance(properties, dict):
        errors.append("'properties' must be an object")

    for prop_name, prop_def in properties.items():
        if not isinstance(prop_def, dict):
            errors.append(f"Property '{prop_name}' definition must be an object")
            continue

        prop_type = prop_def.get("type")
        if not prop_type:
            errors.append(f"Property '{prop_name}' must have a 'type' field")

        # Validate specific property types
        if prop_type == "select":
            options = prop_def.get("select", {}).get("options", [])
            if not options or not isinstance(options, list):
                errors.append(f"Property '{prop_name}': select must have non-empty options array")

        elif prop_type == "multi_select":
            options = prop_def.get("multi_select", {}).get("options", [])
            if not options or not isinstance(options, list):
                errors.append(f"Property '{prop_name}': multi_select must have non-empty options array")

        elif prop_type == "relation":
            if "database_id" not in prop_def.get("relation", {}):
                errors.append(f"Property '{prop_name}': relation must have database_id")

    return errors
```

### 3. Improve Error Messages

```python
@app.command()
def create(
    parent: str = typer.Option(..., "--parent", "-p"),
    title: str = typer.Option(..., "--title", "-t"),
    schema: str = typer.Option("{}", "--schema", "-s"),
):
    try:
        schema_dict = json.loads(schema)
    except json.JSONDecodeError as e:
        return format_error("INVALID_JSON", f"Invalid JSON in schema: {e}")

    # Validate schema
    errors = validate_database_schema(schema_dict)
    if errors:
        return format_error(
            "INVALID_SCHEMA",
            f"Schema validation failed:\n" + "\n".join(f"  - {e}" for e in errors)
        )

    # Use default schema if empty
    if not schema_dict:
        schema_dict = {"properties": {"Name": {"title": {}}}}

    try:
        database = await client.databases.create(
            parent=parent,
            title=title,
            **schema_dict
        )
        return format_success({"database": database})
    except Exception as e:
        # Enhance API error
        error_msg = str(e)
        if "Bad request" in error_msg:
            # Try to extract more info from the error
            return format_error(
                "SCHEMA_ERROR",
                f"Database creation failed. Check schema format. Details: {error_msg}"
            )
        raise
```

### 4. Add Examples to Help

```bash
notion databases create --help

# Should show:

Examples:
  # Create with title only (minimal schema)
  notion databases create --parent <page-id> --title "Tasks"

  # Create with select property
  notion databases create --parent <page-id> --title "Tasks" \
    --schema '{"properties": {"Status": {"type": "select", "select": {"options": [{"name": "To Do", "color": "gray"}]}}}'

  # Create from JSON file
  notion databases create --parent <page-id> --title "Tasks" \
    --schema "$(cat schema.json)"

Schema format:
  {
    "properties": {
      "Property Name": {
        "type": "title|text|number|select|multi_select|date|person|files|checkbox|url|email|phone"
      }
    }
  }

Property types:
  - title: Just {}
  - text: {}
  - number: {"format": "number"}
  - select: {"options": [{"name": "Option", "color": "gray"}]}
  - multi_select: {"options": [{"name": "Tag", "color": "blue"}]}
  - date: {}
  - person: {}
  - files: {}
  - checkbox: {}
  - url: {}
  - email: {}
  - phone: {}
  - relation: {"database_id": "...", "dual_property": "..."}
  - formula: {"expression": "..."}
  - rollup: {...}
```

## Priority

**CRITICAL** - Blocks core database functionality

## Related Issues

- #034 - agents init also has schema validation issues

## Acceptance Criteria

- [ ] Clear schema format documentation in help
- [ ] Schema validation with helpful error messages
- [ ] Default schema (title-only) when `--schema` not provided
- [ ] At least 3 working examples in help
- [ ] Unit tests for schema validation
- [ ] Schema examples for all property types

## Additional Notes

Consider adding a `--schema-template` flag to generate a schema template:

```bash
notion databases create --schema-template > my-schema.json
# Edit my-schema.json
notion databases create --parent <id> --title "DB" --schema "$(cat my-schema.json)"
```

Or even better:

```bash
# Interactive schema builder
notion databases create --parent <id> --title "Tasks" --interactive
# Add property 'Status' (select/multi_select/etc): select
# Add option 'To Do' with color (default: gray):
# Add option 'Done' with color: green
# Add another property? n
# Creating database...
```

This would be much more user-friendly than hand-coding JSON.

## Test Cases

```python
# Test 1: Minimal schema (should work)
schema = {"properties": {"Name": {"title": {}}}}

# Test 2: With select
schema = {
    "properties": {
        "Name": {"title": {}},
        "Status": {
            "type": "select",
            "select": {
                "options": [
                    {"name": "To Do", "color": "gray"}
                ]
            }
        }
    }
}

# Test 3: Invalid type (should fail validation)
schema = {
    "properties": {
        "InvalidType": {"type": "not_a_real_type"}
    }
}

# Test 4: Empty options (should fail validation)
schema = {
    "properties": {
        "Status": {
            "type": "select",
            "select": {"options": []}  # <-- Empty!
        }
    }
}
```

## References

- Notion API Database docs: https://developers.notion.com/reference/create-a-database
- Property type documentation: https://developers.notion.com/reference/property-object

Estimated effort: 3-4 hours
