# Issue #040: Task Dependencies System

## Problem Statement

The Agents CLI currently lacks task dependency functionality, making it impossible to create real-world workflows where tasks depend on each other. This is a critical blocker for project management use cases.

### Current Limitation

```bash
# What users CANNOT do:
notion agents tasks create "Implement feature B" --version-id ver_123 --depends-on "task_A"
notion agents tasks can-start task_B  # Check if dependencies are completed
notion agents tasks deps task_B       # List all dependencies
```

### Impact

Without task dependencies:
- Teams cannot model real workflows where tasks have prerequisites
- The `next` command may suggest tasks that cannot actually be started
- No way to enforce task completion order
- Makes the system a "TODO list" rather than a "project management tool"

---

## Proposed Solution

### 1. CLI Interface for Creating Tasks with Dependencies

```bash
# Create a task with single dependency
notion agents tasks create \
  --title "Build authentication service" \
  --version-id ver_123 \
  --depends-on "task_456" \
  --priority High

# Create a task with multiple dependencies
notion agents tasks create \
  --title "Frontend integration" \
  --version-id ver_123 \
  --depends-on "task_456,task_789,task_012" \
  --type "Integration" \
  --priority Medium
```

### 2. CLI Interface for Checking Dependencies

```bash
# Check if a task can be started (all dependencies completed)
notion agents tasks can-start task_789
# Returns: {"can_start": false, "incomplete_dependencies": ["task_456"]}

# List all dependencies of a task
notion agents tasks deps task_789
# Returns:
# {
#   "task_id": "task_789",
#   "dependencies": [
#     {"id": "task_456", "title": "Setup database", "status": "Completed"},
#     {"id": "task_789", "title": "API development", "status": "In Progress"}
#   ]
# }
```

### 3. Enhanced `next` Command

The `notion agents tasks next` command should be updated to respect dependencies:

```bash
notion agents tasks next --project-id proj_123
# Should ONLY return tasks that:
# 1. Are in Backlog or Claimed status
# 2. Have ALL dependencies completed
```

### 4. Update `can-start` Command

```bash
notion agents tasks can-start task_789 --explain
# Returns:
# {
#   "can_start": false,
#   "blocking_tasks": [
#     {"id": "task_456", "title": "Database setup", "status": "In Progress"}
#   ],
#   "suggestion": "Wait for task_456 to complete before starting"
# }
```

---

## Database Schema Changes

### Update Tasks Database Schema

Add a new relation property:

```yaml
Dependencies:
  type: relation
  relation:
    database_id: "<Tasks Database ID>"
    dual_property: "Dependent Tasks"
  description: "Tasks this task depends on"
```

### Property Name: `Dependencies` (plural)

---

## Implementation Architecture

### Phase 1: Core Dependencies (2-3 days)

1. **Update Task Model**

```python
# better_notion/plugins/official/agents_sdk/models.py

class Task(DatabasePageEntityMixin, BaseEntity):
    # ... existing code ...

    @property
    def dependency_ids(self) -> list[str]:
        """Get list of task IDs this task depends on."""
        dep_prop = self._data["properties"].get("Dependencies")
        if dep_prop and dep_prop.get("type") == "relation":
            return [rel["id"] for rel in dep_prop.get("relation", [])]

        return []

    @property
    def dependencies(self) -> list["Task"]:
        """Get Task objects for all dependencies."""
        from better_notion._sdk.models.page import Page

        deps = []
        for dep_id in self.dependency_ids:
            try:
                # Check cache first
                cache = self._client.page_cache
                if dep_id in cache:
                    deps.append(cache[dep_id])
                else:
                    page = await Page.get(dep_id, client=self._client)
                    self._client.page_cache[dep_id] = page
                    deps.append(page)
            except Exception:
                pass  # Task may have been deleted
        return deps

    async def can_start(self) -> bool:
        """Check if this task can be started (all dependencies completed)."""
        for dep in await self.dependencies():
            if dep.status != "Completed":
                return False
        return True
```

2. **Update TaskManager**

```python
# better_notion/plugins/official/agents_sdk/managers.py

async def create(
    self,
    title: str,
    version_id: str,
    status: str = "Backlog",
    task_type: str = "New Feature",
    priority: str = "Medium",
    dependency_ids: list[str] | None = None,
    estimated_hours: int | None = None,
) -> "Task":
    """Create a new task with optional dependencies."""
    from better_notion.plugins.official.agents_sdk.models import Task

    database_id = self._get_database_id("Tasks")
    return await Task.create(
        client=self._client,
        database_id=database_id,
        title=title,
        version_id=version_id,
        status=status,
        task_type=task_type,
        priority=priority,
        dependency_ids=dependency_ids,
        estimated_hours=estimated_hours,
    )

async def can_start(self, task_id: str) -> dict:
    """Check if a task can be started (all dependencies completed)."""
    from better_notion.plugins.official.agents_sdk.models import Task

    task = await Task.get(task_id, client=self._client)
    deps = await task.dependencies()
    incomplete = [d for d in deps if d.status != "Completed"]

    return {
        "can_start": len(incomplete) == 0,
        "task_id": task_id,
        "incomplete_dependencies": [
            {"id": d.id, "title": d.title, "status": d.status}
            for d in incomplete
        ],
    }

async def find_ready(self, version_id: str | None = None) -> list:
    """Find all tasks that are ready to start (dependencies completed)."""
    from better_notion.plugins.official.agents_sdk.models import Task

    database_id = self._get_database_id("Tasks")
    if not database_id:
        return []

    # Get all backlog/claimed/in-progress tasks
    filters = []
    if version_id:
        filters.append({
            "property": "Version",
            "relation": {"contains": version_id}
        })

    response = await self._client._api._request(
        "POST",
        f"/databases/{database_id}/query",
        json={"filter": filters[0] if len(filters) == 1 else None}
    )

    ready_tasks = []
    for page_data in response.get("results", []):
        task = Task(self._client, page_data)
        # Check status and dependencies
        if task.status in ("Backlog", "Claimed", "In Progress"):
            if await task.can_start():
                ready_tasks.append(task)

    return ready_tasks
```

### Phase 2: CLI Commands (1-2 days)

```bash
# Add to better_notion/plugins/official/agents_cli.py

@app.command()
def tasks_create(
    title: str,
    version_id: str,
    status: str = "Backlog",
    task_type: str = "New Feature",
    priority: str = "Medium",
    dependencies: Optional[str] = typer.Option(None, "--dependencies", "-d"),
    estimated_hours: Optional[int] = typer.Option(None, "--estimate", "-e"),
):
    """Create a new task with optional dependencies."""
    # ... implementation ...

@app.command()
def tasks_deps(task_id: str):
    """List all dependencies of a task."""
    # ... implementation ...

@app.command()
def tasks_can_start(task_id: str, explain: bool = False):
    """Check if a task can be started (all dependencies completed)."""
    # ... implementation ...

@app.command()
def tasks_ready(version_id: Optional[str] = None):
    """List all tasks ready to start (dependencies completed)."""
    # ... implementation ...
```

---

## CLI Examples

### Example 1: Creating Dependent Tasks

```bash
# Create first task (no dependencies)
notion agents tasks create \
  "Setup database schema" \
  --version-id ver_123

# Returns: {"id": "task_001", ...}

# Create task that depends on first task
notion agents tasks create \
  "Build API layer" \
  --version-id ver_123 \
  --dependencies task_001 \
  --priority High

# Returns: {"id": "task_002", ...}

# Try to start second task (will be blocked)
notion agents tasks start task_002
# Returns: ERROR - Task has incomplete dependencies

# Check why it's blocked
notion agents tasks can-start task_002 --explain
# Returns:
# {
#   "can_start": false,
#   "blocking_tasks": [
#     {"id": "task_001", "title": "Setup database schema", "status": "Backlog"}
#   ]
# }
```

### Example 2: Finding Ready Tasks

```bash
# Get all tasks ready to start
notion agents tasks ready --version-id ver_123
# Returns:
# {
#   "ready_tasks": [
#     {"id": "task_003", "title": "Write unit tests", "status": "Backlog"}
#   ]
# }
```

### Example 3: Workflow with Dependencies

```bash
# Create a chain of dependent tasks
task_001=$(notion agents tasks create "Design API" --version-id ver_123 --output json | jq -r '.id')
task_002=$(notion agents tasks create "Implement API" --version-id ver_123 --dependencies $task_001 --output json | jq -r '.id')
task_003=$(notion agents tasks create "Test API" --version-id ver_123 --dependencies $task_002 --output json | jq -r '.id')

# Check what can be started
notion agents tasks ready --version-id ver_123
# Returns only task_001 (no dependencies)

# Complete first task
notion agents tasks complete task_001

# Now task_002 is ready
notion agents tasks ready --version-id ver_123
# Returns task_001 and task_002
```

---

## Database Schema Updates

### 1. Add Dependencies Property to Tasks Database

Update `TasksSchema` in `better_notion/plugins/official/agents_schema.py`:

```python
TasksSchema.get_schema():
    return {
        "title": "Tasks",
        "properties": {
            # ... existing properties ...

            "Dependencies": {
                "type": "relation",
                "relation": {
                    "database_id": "<Tasks Database ID>",
                    "dual_property": "Dependent Tasks",
                    "cached": True
                },
                "description": "Tasks this task depends on (must be completed before starting)",
            }
        }
    }
```

### 2. Update Task Creation Template

```python
# Template for creating task with dependencies
TASK_TEMPLATE = {
    "Dependencies": []  # Array of task page IDs
}
```

---

## Acceptance Criteria

### Phase 1: Core Functionality

- [ ] CLI accepts `--dependencies` parameter with comma-separated task IDs
- [ ] Task model stores and retrieves dependency relations
- [ ] `tasks can-start` correctly identifies blocking tasks
- [ ] `tasks ready` lists only tasks with completed dependencies

### Phase 2: CLI Commands

- [ ] `notion agents tasks deps <task_id>` lists all dependencies
- [ ] `notion agents tasks can-start <task_id> --explain` shows blocking details
- [ ] `notion agents tasks ready --version-id <id>` shows ready tasks

### Phase 3: Integration

- [ ] `notion agents tasks next` respects dependencies
- [ ] `notion agents tasks start` validates dependencies before starting
- [ ] Dependencies are displayed in task get output

### Phase 4: Edge Cases

- [ ] Circular dependencies are detected and rejected
- [ ] Deleting a task updates all dependent tasks
- [ ] Transitive dependencies (A→B→C) work correctly

---

## Related Issues

- Blocks: #029 (Task workflow commands)
- Blocks: #037 (Parameter validation)
- Related to: #030 (Ideas workflow integration)

---

## Migration Path

### For Existing Workspaces

No migration needed - this is a new feature. Existing databases will be updated with the new `Dependencies` property via a schema migration.

### For Code

1. Update Task model with dependency properties
2. Update TaskManager with new methods
3. Add CLI commands
4. Update agents schema

---

## Rollout Plan

1. **Phase 1**: Implement core model changes
2. **Phase 2**: Add CLI commands
3. **Phase 3**: Update existing commands to respect dependencies
4. **Phase 4**: Add dependency visualization in get/list commands

---

## Open Questions

1. Should circular dependencies be allowed? (Probably not)
2. Should there be a maximum depth of dependencies? (Recommend: 5 levels max)
3. Should dependency completion be automatic or manual? (Manual for now)
