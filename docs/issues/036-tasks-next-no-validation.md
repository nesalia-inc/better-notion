# Bug: `notion agents tasks next` returns success for invalid project_id

## Summary

The `tasks next` command accepts any project_id string without validation and returns "No available tasks found" instead of an error, even for projects that don't exist.

## Steps to Reproduce

```bash
notion agents tasks next --project-id "invalid-project-id-that-does-not-exist"
```

## Expected Behavior

Should return an error like:
```json
{
  "error": {
    "code": "PROJECT_NOT_FOUND",
    "message": "Project 'invalid-project-id-that-does-not-exist' not found",
    "retry": false
  }
}
```

## Actual Behavior

```json
{
  "success": true,
  "meta": { ... },
  "data": {
    "message": "No available tasks found",
    "task": null
  }
}
```

This is misleading - the project doesn't exist, but the command returns "success: true".

## Environment

- **better-notion**: 1.4.0
- **Python**: 3.14
- **OS**: Windows 11

## Root Cause

**File**: `better_notion/plugins/official/agents_sdk/managers.py`

```python
class TaskManager:
    async def next(self, project_id: str | None = None) -> Any:
        """
        Find next available task.
        """
        from better_notion.plugins.official.agents_sdk.models import Task

        # Get database ID
        database_id = self._get_database_id("Tasks")
        if not database_id:
            return None  # <-- Just returns None, no validation

        # Query tasks
        query = self._build_task_query(...)
        response = await self._client._api.databases.query(
            database_id=database_id,
            query=query
        )

        results = response.get("results", [])
        if not results:
            return None  # <-- No validation of project_id

        # Return first task
        return Task(self._client, results[0])
```

The method doesn't validate:
1. If `project_id` is provided, does that project exist?
2. If filtering by project, are we actually filtering?

## Impact

**False Positives** - Users think everything is working when actually:
- They have a typo in project_id
- The project was deleted
- They're using the wrong project ID

This leads to:
- Confusion during debugging
- Silent failures in automation
- Difficult-to-trace bugs in agents

## Proposed Solution

### Option 1: Add Project Validation

```python
class TaskManager:
    async def next(self, project_id: str | None = None) -> Any:
        """
        Find next available task.

        Args:
            project_id: Filter by project ID (optional)

        Returns:
            Task instance or None if no tasks available

        Raises:
            ValueError: If project_id is provided but project doesn't exist
        """
        from better_notion.plugins.official.agents_sdk.models import Task, Project

        # Validate project_id if provided
        if project_id:
            try:
                project = await Project.get(project_id, client=self._client)
            except Exception as e:
                raise ValueError(
                    f"Project '{project_id}' not found. "
                    f"Please verify the project ID."
                ) from e

        # Get database ID
        database_id = self._get_database_id("Tasks")
        if not database_id:
            return None

        # Query tasks (with project filter if specified)
        query = self._build_task_query(...)

        # If project specified, add filter
        if project_id:
            query["filter"] = {
                "property": "project_id",
                "rich_text": {
                    "equals": project_id
                }
            }

        response = await self._client._api.databases.query(
            database_id=database_id,
            query=query
        )

        results = response.get("results", [])
        if not results:
            return None

        return Task(self._client, results[0])
```

### Option 2: Add Validation Helper

Create a generic validation helper:

```python
class TaskManager:
    def _validate_project_exists(self, project_id: str) -> bool:
        """Validate that a project exists."""
        import asyncio
        try:
            loop = asyncio.get_event_loop()
            future = asyncio.ensure_future(
                self._client._api.pages.retrieve(page_id=project_id)
            )
            loop.run_until_complete(future)
            return True
        except Exception:
            return False

    async def next(self, project_id: str | None = None) -> Any:
        if project_id and not self._validate_project_exists(project_id):
            raise ValueError(f"Project '{project_id}' not found")
        # ... rest of method
```

### Option 3: Add Database Query Validation (Recommended)

Instead of validating project exists (extra API call), validate the query results:

```python
async def next(self, project_id: str | None = None) -> Any:
    """Find next available task with validation."""

    # Check workspace config first
    if project_id:
        workspace_config = self._client._workspace_config
        projects_db = workspace_config.get("Projects")
        if not projects_db:
            raise ValueError(
                f"Projects database not configured. "
                f"Please initialize workspace first: notion agents init"
            )

    # Query tasks
    query = {...}

    # If project specified, add filter
    if project_id:
        query["filter"] = {
            "and": [
                {"property": "project_id", "rich_text": {"equals": project_id}},
                {"property": "status", "select": {"equals": "Backlog"}}
            ]
        }

    response = await self._client._api.databases.query(
        database_id=database_id,
        query=query
    )

    results = response.get("results", [])

    # If project specified but no results, validate project exists
    if project_id and not results:
        # Double-check project exists
        try:
            from better_notion.plugins.official.agents_sdk.models import Project
            await Project.get(project_id, client=self._client)
            # Project exists but no tasks
            return None
        except Exception:
            raise ValueError(
                f"Project '{project_id}' not found or no access. "
                f"Unable to find tasks for this project."
            )

    return Task(self._client, results[0]) if results else None
```

## Priority

**MEDIUM** - Causes confusion and silent failures, but doesn't crash

## Related Issues

- #036 - ideas review validation
- #037 - incidents mttr validation
- #038 - tasks complete validation

## Acceptance Criteria

- [ ] Validate project_id exists (or check in workspace config)
- [ ] Return clear error if project doesn't exist
- [ ] Add unit tests for invalid project_id
- [ ] Document behavior when project has no tasks vs invalid project

## Additional Notes

This same issue likely affects other managers:

1. **ProjectManager** - `list(organization_id)` should validate org
2. **VersionManager** - `list(project_id)` should validate project
3. **IdeaManager** - `list(project_id)` should validate project
4. **WorkIssueManager** - `list(project_id)` should validate project
5. **IncidentManager** - `list(project_id)` should validate project

Consider creating a generic validation helper:

```python
def _validate_entity_exists(entity_type: str, entity_id: str, client) -> bool:
    """Generic entity validator."""
    # Query the appropriate database
    # Return True if exists, False otherwise
```

## Test Cases

```python
# Test 1: Valid project with tasks
task = await manager.next(project_id="valid-project-with-tasks")
assert task is not None

# Test 2: Valid project with no tasks
task = await manager.next(project_id="valid-project-empty")
assert task is None  # But no error!

# Test 3: Invalid project ID
try:
    task = await manager.next(project_id="invalid-project")
    assert False, "Should raise ValueError"
except ValueError as e:
    assert "not found" in str(e)

# Test 4: No project filter (all tasks)
task = await manager.next(project_id=None)
assert task is not None or task is None  # Either way is fine
```

## User-Facing Error Messages

Good:
```
Error: Project 'xyz' not found
Please check:
  1. The project ID is correct
  2. You have access to this project
  3. The project exists in your workspace
```

Bad:
```
Error: PROJECT_NOT_FOUND
```

Worst (current):
```
{"success": true, "message": "No available tasks found"}
```

Estimated effort: 2-3 hours
