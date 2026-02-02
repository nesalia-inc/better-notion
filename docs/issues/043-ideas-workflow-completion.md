# Issue #043: Ideas Workflow Completion

## Problem Statement

The Agents CLI currently lacks the ability to convert accepted Ideas into Tasks, creating a manual gap in the workflow. This is a critical missing piece for the idea-to-implementation lifecycle:

- **Ideas** are proposed, reviewed, and accepted
- **Tasks** need to be created from accepted ideas
- **Linkage** between idea and task must be maintained
- **Status tracking** from idea to task completion is broken

### Current Limitation

```bash
# What users CANNOT do:
notion agents ideas convert idea_123 --to-task  # Convert accepted idea to task
notion agents ideas convert idea_123 --task-title "Implement feature"  # Custom title
notion agents ideas track idea_123  # Track implementation progress
```

### Current Manual Workflow (Problematic)

```bash
# Step 1: Accept an idea
notion agents ideas accept idea_123

# Step 2: Manually create a task (need to remember idea details)
notion agents tasks create \
  "Build authentication service" \
  --version-id ver_123

# Step 3: Manually link task to idea (if cross-entity relations are implemented)
notion agents ideas link idea_123 --task task_456

# Problems:
# - No automatic transfer of idea properties to task
# - Easy to forget details or make mistakes
# - Two separate manual steps
# - No clear audit trail
```

### Impact

Without idea-to-task conversion:
- Broken workflow from idea → implementation
- Manual copy-paste of information
- No automatic linking between idea and task
- Difficult to track which ideas are implemented
- Lost context during conversion
- Additional friction in the development process

---

## Proposed Solution

### 1. CLI Interface for Converting Ideas to Tasks

```bash
# Convert an accepted idea to a task (auto-generated title)
notion agents ideas convert idea_123
# Returns:
# {
#   "idea_id": "idea_123",
#   "task_id": "task_456",
#   "title": "Implement: Add authentication system",
#   "status": "converted"
# }

# Convert with custom task title
notion agents ideas convert idea_123 --task-title "Build OAuth2 authentication"
# Returns:
# {
#   "idea_id": "idea_123",
#   "task_id": "task_456",
#   "title": "Build OAuth2 authentication",
#   "status": "converted"
# }

# Convert with specific version and priority
notion agents ideas convert idea_123 \
  --version-id ver_123 \
  --priority High \
  --type "New Feature"
# Returns: {...}

# Convert and assign to a person
notion agents ideas convert idea_123 --assign-to "Alice Chen"
# Returns:
# {
#   "idea_id": "idea_123",
#   "task_id": "task_456",
#   "assigned_to": "Alice Chen",
#   ...
# }
```

### 2. Automatic Property Mapping

The convert command should automatically map idea properties to task properties:

```python
# Mapping logic:
Idea Properties → Task Properties
─────────────────────────────────
Title → Title (prefixed with "Implement:")
Description → Description
Project → Project (inherited)
Version → Version (specified via --version-id, or idea's project's active version)
Category → Type (e.g., "Feature" → "New Feature")
Effort Estimate → (can be used for Estimated Hours if implemented)
Priority → Priority (inherited, or defaults to Medium)
```

### 3. Enhanced Idea Status

Ideas should have a new status to track conversion:

```yaml
Status values:
  - Proposed      # Initial state
  - In Review     # Being reviewed
  - Accepted      # Approved, ready to convert
  - Converting    # Conversion in progress
  - Implemented   # Task created from this idea
  - Rejected      # Not approved
```

### 4. Progress Tracking Commands

```bash
# Track implementation progress of an idea
notion agents ideas track idea_123
# Returns:
# {
#   "idea_id": "idea_123",
#   "title": "Add authentication system",
#   "status": "Implemented",
#   "task": {
#     "id": "task_456",
#     "title": "Implement: Add authentication system",
#     "status": "In Progress",
#     "progress": "60%"
#   },
#   "conversion_date": "2026-02-01T10:30:00Z"
# }

# List all accepted ideas ready to convert
notion agents ideas list --status Accepted
# Returns: {"ideas": [...]}

# List all implemented ideas and their task status
notion agents ideas list --status Implemented --show-task-progress
# Returns:
# {
#   "ideas": [
#     {
#       "id": "idea_123",
#       "title": "Add authentication",
#       "task": {"id": "task_456", "status": "In Progress"}
#     }
#   ]
# }
```

---

## Database Schema Changes

### 1. Update Ideas Schema Status Options

```yaml
Status:
  type: select
  select:
    options:
      - name: "Proposed"
        color: "gray"
      - name: "In Review"
        color: "yellow"
      - name: "Accepted"
        color: "blue"
      - name: "Implemented"
        color: "green"
      - name: "Rejected"
        color: "red"
  description: "Current status of the idea"
```

### 2. Add Conversion Metadata to Ideas (Optional)

For tracking when ideas were converted:

```yaml
Implementation Task:
  type: relation
  relation:
    database_id: "<Tasks Database ID>"
    dual_property: "Source Idea"
  description: "The task that implements this idea"

Conversion Date:
  type: date
  description: "When this idea was converted to a task"
```

---

## Implementation Architecture

### Phase 1: Model Updates (0.5 day)

```python
# better_notion/plugins/official/agents_sdk/models.py

class Idea(DatabasePageEntityMixin, BaseEntity):
    # ... existing code ...

    @property
    def status(self) -> str:
        """Get the status of this idea."""
        prop = self._data["properties"].get("Status")
        if prop and prop.get("type") == "select":
            select_data = prop.get("select")
            return select_data.get("name") if select_data else "Proposed"
        return "Proposed"

    async def convert_to_task(
        self,
        task_title: str | None = None,
        version_id: str | None = None,
        priority: str | None = None,
        task_type: str | None = None,
        assignee: str | None = None,
        estimated_hours: int | None = None
    ) -> "Task":
        """Convert this idea to a task."""
        from better_notion.plugins.official.agents_sdk.models import Task
        from better_notion._sdk.models.page import Page

        # Validate idea is accepted
        if self.status not in ("Accepted", "Implementing"):
            raise ValueError(f"Cannot convert idea with status '{self.status}'. Must be 'Accepted'.")

        # Generate task title if not provided
        if not task_title:
            task_title = f"Implement: {self.title}"

        # Determine version (use provided or get from project)
        if not version_id:
            # Could implement logic to get active version from project
            raise ValueError("version_id must be provided")

        # Map properties
        task_priority = priority or self.priority or "Medium"
        task_type_value = task_type or self.category or "New Feature"

        # Create the task
        database_id = self._client.workspace_config.get("Tasks")
        task = await Task.create(
            client=self._client,
            database_id=database_id,
            title=task_title,
            version_id=version_id,
            status="Backlog",
            task_type=task_type_value,
            priority=task_priority,
            assignee=assignee,
            estimated_hours=estimated_hours,
            description=self.description
        )

        # Link idea to task (if cross-entity relations are implemented)
        await self.link_to_task(task.id)

        # Update idea status to Implemented
        await Page.update(
            self.id,
            client=self._client,
            properties={
                "Status": {"select": {"name": "Implemented"}},
                "Conversion Date": {
                    "date": {"start": datetime.now(timezone.utc).isoformat()}
                }
            }
        )

        return task

    @property
    def implementation_task_id(self) -> str | None:
        """Get the task ID that implements this idea."""
        prop = self._data["properties"].get("Implementation Task")
        if prop and prop.get("type") == "relation":
            relations = prop.get("relation", [])
            return relations[0]["id"] if relations else None
        return None

    @property
    async def implementation_task(self) -> "Task | None":
        """Get the Task object that implements this idea."""
        from better_notion.plugins.official.agents_sdk.models import Task

        task_id = self.implementation_task_id
        if not task_id:
            return None

        if task_id in self._client.page_cache:
            return self._client.page_cache[task_id]

        return await Task.get(task_id, client=self._client)

    async def get_implementation_progress(self) -> dict:
        """Get the implementation progress of this idea."""
        if self.status != "Implemented":
            return {
                "idea_id": self.id,
                "status": self.status,
                "message": "Idea has not been implemented yet"
            }

        task = await self.implementation_task
        if not task:
            return {
                "idea_id": self.id,
                "status": "Implemented",
                "error": "Task not found"
            }

        # Calculate progress based on task status
        progress_map = {
            "Backlog": "0%",
            "Claimed": "10%",
            "In Progress": "50%",
            "Review": "90%",
            "Completed": "100%",
            "Cancelled": "0%"
        }

        return {
            "idea_id": self.id,
            "title": self.title,
            "status": "Implemented",
            "task": {
                "id": task.id,
                "title": task.title,
                "status": task.status,
                "progress": progress_map.get(task.status, "0%")
            }
        }
```

### Phase 2: Manager Updates (0.5 day)

```python
# better_notion/plugins/official/agents_sdk/managers.py

class IdeaManager:
    # ... existing code ...

    async def convert_to_task(
        self,
        idea_id: str,
        task_title: str | None = None,
        version_id: str | None = None,
        priority: str | None = None,
        task_type: str | None = None,
        assignee: str | None = None,
        estimated_hours: int | None = None
    ) -> dict:
        """Convert an idea to a task."""
        from better_notion.plugins.official.agents_sdk.models import Idea

        idea = await Idea.get(idea_id, client=self._client)

        # Update idea status to "Converting" temporarily
        from better_notion._sdk.models.page import Page
        await Page.update(
            idea.id,
            client=self._client,
            properties={"Status": {"select": {"name": "Converting"}}}
        )

        try:
            task = await idea.convert_to_task(
                task_title=task_title,
                version_id=version_id,
                priority=priority,
                task_type=task_type,
                assignee=assignee,
                estimated_hours=estimated_hours
            )

            return {
                "idea_id": idea_id,
                "task_id": task.id,
                "title": task.title,
                "status": "converted",
                "task_status": task.status,
                "task_priority": task.priority
            }
        except Exception as e:
            # Revert idea status on error
            await Page.update(
                idea.id,
                client=self._client,
                properties={"Status": {"select": {"name": "Accepted"}}}
            )
            raise

    async def track_progress(self, idea_id: str) -> dict:
        """Track the implementation progress of an idea."""
        from better_notion.plugins.official.agents_sdk.models import Idea

        idea = await Idea.get(idea_id, client=self._client)
        return await idea.get_implementation_progress()

    async def list_ready_to_convert(self, project_id: str | None = None) -> list:
        """List all accepted ideas ready to be converted."""
        from better_notion.plugins.official.agents_sdk.models import Idea

        database_id = self._get_database_id("Ideas")
        if not database_id:
            return []

        filters = {
            "property": "Status",
            "select": {"equals": "Accepted"}
        }

        if project_id:
            filters = {
                "and": [
                    filters,
                    {"property": "Project", "relation": {"contains": project_id}}
                ]
            }

        response = await self._client._api._request(
            "POST",
            f"/databases/{database_id}/query",
            json={"filter": filters}
        )

        return [
            Idea(self._client, page_data)
            for page_data in response.get("results", [])
        ]
```

### Phase 3: CLI Commands (1 day)

```bash
# better_notion/plugins/official/agents_cli.py

@app.command()
def ideas_convert(
    idea_id: str = typer.Argument(..., help="Idea ID to convert"),
    task_title: Optional[str] = typer.Option(None, "--task-title", "-t", help="Custom task title"),
    version_id: Optional[str] = typer.Option(None, "--version-id", "-v", help="Target version ID"),
    priority: Optional[str] = typer.Option(None, "--priority", "-p", help="Task priority"),
    type_: Optional[str] = typer.Option(None, "--type", help="Task type"),
    assignee: Optional[str] = typer.Option(None, "--assign-to", "-a", help="Assign to person"),
    estimated_hours: Optional[int] = typer.Option(None, "--estimate", "-e", help="Estimated hours")
):
    """Convert an accepted idea to a task."""
    # ... implementation ...

@app.command()
def ideas_track(idea_id: str):
    """Track the implementation progress of an idea."""
    # ... implementation ...

# Update existing ideas list command
@app.command()
def ideas_list(
    project_id: Optional[str] = None,
    status: Optional[str] = None,
    show_task_progress: bool = False
):
    """List ideas with optional filters."""
    # ... implementation ...
    # If show_task_progress is True, fetch and include task status for Implemented ideas
```

---

## CLI Examples

### Example 1: Basic Conversion

```bash
# Accept an idea
notion agents ideas accept idea_123
# Returns: {"id": "idea_123", "status": "Accepted", ...}

# Convert to task (auto-generated title)
notion agents ideas convert idea_123 --version-id ver_123
# Returns:
# {
#   "idea_id": "idea_123",
#   "task_id": "task_456",
#   "title": "Implement: Add authentication system",
#   "status": "converted",
#   "task_status": "Backlog",
#   "task_priority": "Medium"
# }

# Track progress
notion agents ideas track idea_123
# Returns:
# {
#   "idea_id": "idea_123",
#   "title": "Add authentication system",
#   "status": "Implemented",
#   "task": {
#     "id": "task_456",
#     "title": "Implement: Add authentication system",
#     "status": "Backlog",
#     "progress": "0%"
#   }
# }
```

### Example 2: Conversion with Custom Properties

```bash
# Convert with custom title and priority
notion agents ideas convert idea_123 \
  --task-title "Build OAuth2 authentication service" \
  --version-id ver_123 \
  --priority High \
  --type "New Feature" \
  --assign-to "Alice Chen"

# Returns:
# {
#   "idea_id": "idea_123",
#   "task_id": "task_456",
#   "title": "Build OAuth2 authentication service",
#   "assigned_to": "Alice Chen",
#   "status": "converted"
# }
```

### Example 3: Finding Ideas to Convert

```bash
# List all accepted ideas ready to convert
notion agents ideas list --status Accepted
# Returns:
# {
#   "ideas": [
#     {
#       "id": "idea_123",
#       "title": "Add authentication system",
#       "category": "Feature",
#       "status": "Accepted",
#       "project_id": "proj_123"
#     },
#     {
#       "id": "idea_456",
#       "title": "Improve error handling",
#       "category": "Improvement",
#       "status": "Accepted",
#       "project_id": "proj_123"
#     }
#   ]
# }

# Convert them to tasks
notion agents ideas convert idea_123 --version-id ver_123
notion agents ideas convert idea_456 --version-id ver_123
```

### Example 4: Tracking Implemented Ideas

```bash
# List all implemented ideas with task progress
notion agents ideas list --status Implemented --show-task-progress
# Returns:
# {
#   "ideas": [
#     {
#       "id": "idea_789",
#       "title": "Add dark mode",
#       "status": "Implemented",
#       "task": {
#         "id": "task_001",
#         "title": "Implement: Add dark mode",
#         "status": "In Progress",
#         "progress": "50%"
#       }
#     }
#   ]
# }
```

---

## Acceptance Criteria

### Phase 1: Model Updates

- [ ] Idea model has `convert_to_task()` method
- [ ] Idea model has `implementation_task_id` property
- [ ] Idea model has `implementation_task` async property
- [ ] Idea model has `get_implementation_progress()` method
- [ ] Idea status includes "Implemented" option

### Phase 2: Manager Updates

- [ ] IdeaManager has `convert_to_task()` method
- [ ] IdeaManager has `track_progress()` method
- [ ] IdeaManager has `list_ready_to_convert()` method
- [ ] Conversion automatically creates linked task
- [ ] Conversion updates idea status to "Implemented"
- [ ] Conversion reverts status on error

### Phase 3: CLI Commands

- [ ] `notion agents ideas convert <id>` works
- [ ] `notion agents ideas convert <id> --task-title <title>` works
- [ ] `notion agents ideas convert <id> --version-id <id>` works
- [ ] `notion agents ideas convert <id> --priority <p>` works
- [ ] `notion agents ideas convert <id> --assign-to <name>` works
- [ ] `notion agents ideas track <id>` works
- [ ] `notion agents ideas list --status Implemented --show-task-progress` works

### Phase 4: Integration

- [ ] Conversion requires idea to be in "Accepted" status
- [ ] Task title is auto-generated if not provided
- [ ] Idea properties are correctly mapped to task properties
- [ ] Task is automatically linked to idea (requires cross-entity relations)
- [ ] Progress tracking shows accurate task status
- [ ] Error handling rolls back idea status on failure

---

## Related Issues

- Depends on: #041 (Cross-entity relations - for automatic linking)
- Related to: #030 (Ideas workflow integration)
- Related to: #040 (Task dependencies - for dependent task creation)
- Related to: #042 (Human assignment - for assigning converted tasks)

---

## Migration Path

### For Existing Workspaces

1. Update Ideas database schema to include "Implemented" status option
2. Add "Implementation Task" relation property to Ideas database
3. Add "Conversion Date" date property to Ideas database (optional)

### For Code

1. Update Idea model with conversion methods
2. Update IdeaManager with conversion logic
3. Add CLI commands for conversion
4. Update agents schema

---

## Rollout Plan

1. **Phase 1**: Implement model changes (conversion methods)
2. **Phase 2**: Implement manager changes (conversion logic)
3. **Phase 3**: Add CLI commands for conversion
4. **Phase 4**: Add progress tracking commands
5. **Phase 5**: Integration testing with idea workflow

---

## Open Questions

1. Should conversion automatically assign the task based on project/team?
   - **Recommendation**: No, require explicit `--assign-to` or leave unassigned
2. Should we support converting multiple ideas at once?
   - **Recommendation**: Not in v1, can add in v2 if requested
3. What should happen if the idea's project has no active version?
   - **Recommendation**: Require explicit `--version-id` parameter
4. Should we support converting an idea to multiple tasks?
   - **Recommendation**: Not in v1, keep it simple (1 idea → 1 task)
5. Should implemented ideas be editable?
   - **Recommendation**: Yes, but changes don't affect the created task

---

## Edge Cases to Handle

1. **Converting non-accepted idea**: Should fail with clear error message
2. **Converting already implemented idea**: Should fail with clear error message
3. **Missing required parameters**: Should validate and prompt for missing info
4. **Conversion failure**: Should revert idea status to "Accepted" and log error
5. **Deleting linked task**: Idea should remain "Implemented" but show warning in `track`
6. **Updating implemented idea**: Should allow edits but warn that task won't be updated
7. **Version ID not found**: Should validate version exists before creating task
