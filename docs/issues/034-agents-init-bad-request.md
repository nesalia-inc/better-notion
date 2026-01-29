# Bug: `notion agents init` fails with generic "Bad request" error

## Summary

The workspace initialization command fails with a generic "Bad request" error without any details about which database creation failed or why.

## Steps to Reproduce

```bash
# Get a valid parent page ID
notion databases list

# Initialize agents workspace
notion agents init --parent-page <parent-page-id> --name "Test Workspace"
```

## Expected Behavior

Should create 8 databases (Organizations, Projects, Versions, Tasks, Ideas, Work Issues, Incidents, Tags) with proper relationships and return success with database IDs.

## Actual Behavior

```json
{
  "success": false,
  "meta": {
    "version": "1.3.0",
    "timestamp": "2026-01-29T10:32:18.304208+00:00"
  },
  "error": {
    "code": "INIT_ERROR",
    "message": "Bad request",
    "retry": false
  }
}
```

No indication of:
- Which database creation failed
- What property/schema caused the issue
- What the Notion API error actually was

## Environment

- **OS**: Windows 11
- **Python**: 3.14
- **better-notion**: 1.4.0
- **Notion API**: Latest

## Root Cause Analysis

The error is swallowed somewhere in the workspace initialization chain. Possible causes:

1. **Invalid schema properties** - One of the database schemas may have invalid property types/formats
2. **Relation setup** - Attempting to create relations to databases that don't exist yet
3. **Property name conflicts** - Reserved Notion property names used incorrectly
4. **API error handling** - Actual Notion API error not propagated correctly

**File**: `better_notion/utils/agents/workspace.py`

```python
async def initialize_workspace(self, parent_page_id, workspace_name):
    # ...
    for database_creation in [
        self._create_organizations_db(parent),
        self._create_tags_db(parent),
        # ... etc
    ]:
        await database_creation  # <-- Error swallowed here
```

## Investigation Steps Needed

1. Add try-catch around each database creation with logging
2. Log the exact API request/response for each creation
3. Validate schemas against Notion API documentation
4. Test with minimal database (1 property) to isolate issue

## Proposed Solution

### Step 1: Add Detailed Error Propagation

```python
async def initialize_workspace(self, parent_page_id, workspace_name):
    try:
        # Get parent page
        parent = await Page.get(parent_page_id, client=self._client)
    except Exception as e:
        raise WorkspaceInitError(f"Failed to get parent page {parent_page_id}: {str(e)}")

    databases_created = []

    # Create each database with error tracking
    databases = [
        ("Organizations", self._create_organizations_db),
        ("Tags", self._create_tags_db),
        # ... etc
    ]

    for db_name, creator in databases:
        try:
            db_id = await creator(parent)
            databases_created.append(db_name)
            logger.info(f"Created {db_name} database: {db_id}")
        except Exception as e:
            raise WorkspaceInitError(
                f"Failed to create {db_name} database. "
                f"Already created: {databases_created}. "
                f"Error: {str(e)}"
            )
```

### Step 2: Validate Schemas

Add schema validation before API call:

```python
def validate_schema(schema: dict) -> bool:
    """Validate database schema against Notion API requirements."""
    required_fields = ["title", "properties"]
    for prop_name, prop_def in schema.get("properties", {}).items():
        prop_type = prop_def.get("type")
        if prop_type not in ["title", "text", "number", "select", "multi_select",
                              "date", "person", "files", "checkbox", "url", "email",
                              "phone", "formula", "relation", "rollup"]:
            raise ValueError(f"Invalid property type: {prop_type}")
```

### Step 3: Add Debug Mode

```bash
notion agents init --parent-page <id> --debug --verbose
```

Shows:
- Each database being created
- Schema being sent
- API responses
- Exact error on failure

## Priority

**CRITICAL** - Blocks all agents workflow functionality

## Related Issues

- #033 - pages create asyncio error
- #034 - SDK Plugin system

## Acceptance Criteria

- [ ] Clear error message indicating which database failed
- [ ] Validation of schemas before API calls
- [ ] Detailed error logs with API request/response
- [ ] `--debug` flag for troubleshooting
- [ ] Tests for workspace initialization
- [ ] Documentation of valid schema formats

## Additional Notes

This is a complex issue requiring:
1. Understanding Notion's database creation API limits
2. Validating all 8 database schemas
3. Proper error handling and reporting

Estimated effort: 4-6 hours

---

## Potential Schema Issues to Check

Based on Notion API documentation, verify:

1. **Relation properties** must reference existing databases
2. **Rollup properties** require valid referenced properties
3. **Formula properties** must have valid syntax
4. **Select options** must have at least 1 option
5. **Property names** must be unique within database
6. **Reserved property names** cannot be used

## Test Case for Minimal Reproduction

```python
# Test minimal database creation
from notion_client import Client

client = Client(auth="...")

# Minimal schema
schema = {
    "title": "Test DB",
    "properties": {
        "Name": {
            "title": {}
        }
    }
}

# This should work - use as baseline
database = client.databases.create(
    parent=parent_page_id,
    schema=schema
)
```

If this works, gradually add complexity to find breaking point.
