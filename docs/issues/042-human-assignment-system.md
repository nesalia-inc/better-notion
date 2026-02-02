# Issue #042: Human Assignment System

## Problem Statement

The Agents CLI currently only supports task assignment to AI agents, making it impossible to manage human team members and their workloads. This is a critical gap for real-world project management where:

- **Tasks** need to be assigned to specific human developers
- **Workload balancing** requires knowing how many tasks each person has
- **Team coordination** requires seeing who's working on what
- **Availability tracking** helps identify who can take new tasks

### Current Limitation

```bash
# What users CANNOT do:
notion agents tasks assign task_123 --to user_456  # Assign to human
notion agents tasks list --assignee user_456      # List by person
notion agents team list                           # List all team members
notion agents team workload user_456              # Check workload
notion agents tasks reassign task_123 --from user_456 --to user_789  # Reassign
```

### Impact

Without human assignment:
- Cannot manage team workload distribution
- No way to track who is responsible for what
- Makes coordination impossible in team settings
- Reduces the system from a "project management tool" to a "personal task list"
- Cannot balance work across team members
- No visibility into team capacity and availability

---

## Proposed Solution

### 1. CLI Interface for Assigning Tasks to Humans

```bash
# Assign a task to a human
notion agents tasks assign task_123 --to user_456
# Returns: {"task_id": "task_123", "assigned_to": "user_456", "previous": "ai_agent"}

# Assign multiple tasks to a human
notion agents tasks assign task_123 task_456 task_789 --to user_456
# Returns: {"assigned": 3, "to": "user_456"}

# Reassign a task from one person to another
notion agents tasks reassign task_123 --from user_456 --to user_789
# Returns: {"task_id": "task_123", "from": "user_456", "to": "user_789"}

# Unassign a task (return to backlog)
notion agents tasks unassign task_123
# Returns: {"task_id": "task_123", "assigned_to": null}
```

### 2. Team Management Commands

```bash
# List all team members
notion agents team list
# Returns:
# {
#   "members": [
#     {
#       "id": "user_456",
#       "name": "Alice Chen",
#       "role": "Developer",
#       "active_tasks": 3,
#       "completed_tasks": 15
#     },
#     {
#       "id": "user_789",
#       "name": "Bob Smith",
#       "role": "Designer",
#       "active_tasks": 5,
#       "completed_tasks": 22
#     }
#   ]
# }

# Check a team member's workload
notion agents team workload user_456
# Returns:
# {
#   "user_id": "user_456",
#   "name": "Alice Chen",
#   "active_tasks": 3,
#   "tasks": [
#     {"id": "task_001", "title": "Fix auth bug", "priority": "High", "status": "In Progress"},
#     {"id": "task_002", "title": "Add dark mode", "priority": "Medium", "status": "Backlog"},
#     {"id": "task_003", "title": "Update docs", "priority": "Low", "status": "Claimed"}
#   ]
# }

# Find available team members (those with low workload)
notion agents team available
# Returns:
# {
#   "available": [
#     {"id": "user_456", "name": "Alice Chen", "active_tasks": 2, "capacity_remaining": 8},
#     {"id": "user_789", "name": "Bob Smith", "active_tasks": 1, "capacity_remaining": 9}
#   ]
# }
```

### 3. Query Commands for Finding Tasks by Assignee

```bash
# List all tasks assigned to a person
notion agents tasks list --assignee user_456
# Returns:
# {
#   "tasks": [
#     {"id": "task_001", "title": "Fix auth bug", "status": "In Progress", "priority": "High"},
#     {"id": "task_002", "title": "Add dark mode", "status": "Backlog", "priority": "Medium"}
#   ]
# }

# List unassigned tasks
notion agents tasks list --unassigned
# Returns: {"tasks": [{"id": "task_003", "title": "Write tests", "status": "Backlog"}]}

# List tasks by status for a specific person
notion agents tasks list --assignee user_456 --status In Progress
# Returns: {"tasks": [{"id": "task_001", "title": "Fix auth bug", "status": "In Progress"}]}

# Get tasks assigned to me (current user)
notion agents tasks mine
# Returns: {"tasks": [...]}
```

### 4. Enhanced Task Get with Assignee Info

```bash
# Get task with assignee details
notion agents tasks get task_123
# Returns:
# {
#   "id": "task_123",
#   "title": "Build authentication service",
#   "status": "In Progress",
#   "assigned_to": {
#     "id": "user_456",
#     "name": "Alice Chen",
#     "email": "alice@example.com"
#   },
#   ...
# }
```

---

## Database Schema Changes

### 1. Add Assignee Property to Tasks Schema

```yaml
Assignee:
  type: select
  select:
    options:
      - name: "Alice Chen"
        color: "blue"
      - name: "Bob Smith"
        color: "green"
      - name: "AI Agent"
        color: "gray"
  description: "Person or agent responsible for this task"
```

**Alternative Approach (Better for scalability)**:

```yaml
Assignee:
  type: person
  people:
    - name: "Alice Chen"
      email: "alice@example.com"
    - name: "Bob Smith"
      email: "bob@example.com"
  description: "Person responsible for this task"
```

### 2. Create Team Members Database (Optional)

For more advanced team management:

```yaml
Title: "Team Members"
Properties:
  Name:
    type: title
  Email:
    type: email
  Role:
    type: select
  Active:
    type: checkbox
  Max Tasks:
    type: number
  Skills:
    type: multi_select
```

---

## Implementation Architecture

### Phase 1: Model Updates (1 day)

```python
# better_notion/plugins/official/agents_sdk/models.py

class Task(DatabasePageEntityMixin, BaseEntity):
    # ... existing code ...

    @property
    def assignee(self) -> str | None:
        """Get the assignee of this task."""
        prop = self._data["properties"].get("Assignee")

        # Handle select type
        if prop and prop.get("type") == "select":
            select_data = prop.get("select")
            return select_data.get("name") if select_data else None

        # Handle person type
        if prop and prop.get("type") == "people":
            people = prop.get("people", [])
            return people[0].get("name") if people else None

        return None

    @property
    def assignee_id(self) -> str | None:
        """Get the assignee ID (for person type)."""
        prop = self._data["properties"].get("Assignee")

        if prop and prop.get("type") == "people":
            people = prop.get("people", [])
            return people[0].get("id") if people else None

        return None

    async def assign_to(self, assignee: str) -> None:
        """Assign this task to a person."""
        from better_notion._sdk.models.page import Page

        await Page.update(
            self.id,
            client=self._client,
            properties={
                "Assignee": {"select": {"name": assignee}}
            }
        )

    async def unassign(self) -> None:
        """Unassign this task."""
        from better_notion._sdk.models.page import Page

        await Page.update(
            self.id,
            client=self._client,
            properties={
                "Assignee": {"select": None}
            }
        )


class TeamMember(BaseEntity):
    """Represents a team member (if using Team Members database)."""

    def __init__(self, client, data):
        super().__init__(client, data)
        self.id = data["id"]
        self._data = data

    @property
    def name(self) -> str:
        """Get the team member's name."""
        return self._data["properties"]["Name"]["title"][0]["text"]["content"]

    @property
    def email(self) -> str | None:
        """Get the team member's email."""
        prop = self._data["properties"].get("Email")
        if prop and prop.get("type") == "email":
            return prop.get("email")
        return None

    @property
    def role(self) -> str | None:
        """Get the team member's role."""
        prop = self._data["properties"].get("Role")
        if prop and prop.get("type") == "select":
            select_data = prop.get("select")
            return select_data.get("name") if select_data else None
        return None

    @property
    def max_tasks(self) -> int:
        """Get the maximum number of tasks this member can handle."""
        prop = self._data["properties"].get("Max Tasks")
        if prop and prop.get("type") == "number":
            return prop.get("number") or 10
        return 10  # Default

    @property
    def is_active(self) -> bool:
        """Check if this team member is active."""
        prop = self._data["properties"].get("Active")
        if prop and prop.get("type") == "checkbox":
            return prop.get("checkbox", False)
        return True

    @property
    def skills(self) -> list[str]:
        """Get the team member's skills."""
        prop = self._data["properties"].get("Skills")
        if prop and prop.get("type") == "multi_select":
            return [m.get("name") for m in prop.get("multi_select", [])]
        return []

    @classmethod
    async def get(cls, member_id: str, client):
        """Get a team member by ID."""
        from better_notion._sdk.models.page import Page

        page_data = await Page.get(member_id, client=client)
        return cls(client, page_data._data)
```

### Phase 2: Manager Updates (1 day)

```python
# better_notion/plugins/official/agents_sdk/managers.py

class TaskManager:
    # ... existing code ...

    async def assign(
        self,
        task_id: str,
        assignee: str
    ) -> dict:
        """Assign a task to a person."""
        from better_notion.plugins.official.agents_sdk.models import Task

        task = await Task.get(task_id, client=self._client)
        previous = task.assignee

        await task.assign_to(assignee)

        return {
            "task_id": task_id,
            "assigned_to": assignee,
            "previous": previous
        }

    async def unassign(self, task_id: str) -> dict:
        """Unassign a task."""
        from better_notion.plugins.official.agents_sdk.models import Task

        task = await Task.get(task_id, client=self._client)
        previous = task.assignee

        await task.unassign()

        return {
            "task_id": task_id,
            "assigned_to": None,
            "previous": previous
        }

    async def reassign(
        self,
        task_id: str,
        from_assignee: str,
        to_assignee: str
    ) -> dict:
        """Reassign a task from one person to another."""
        from better_notion.plugins.official.agents_sdk.models import Task

        task = await Task.get(task_id, client=self._client)

        if task.assignee != from_assignee:
            raise ValueError(f"Task is not assigned to {from_assignee}")

        await task.assign_to(to_assignee)

        return {
            "task_id": task_id,
            "from": from_assignee,
            "to": to_assignee
        }

    async def list_by_assignee(
        self,
        assignee: str,
        status: str | None = None
    ) -> list:
        """List tasks assigned to a person."""
        from better_notion.plugins.official.agents_sdk.models import Task

        database_id = self._get_database_id("Tasks")
        if not database_id:
            return []

        filters = {
            "property": "Assignee",
            "select": {"equals": assignee}
        }

        if status:
            # Need compound filter (see Issue #043)
            filters = {
                "and": [
                    filters,
                    {
                        "property": "Status",
                        "select": {"equals": status}
                    }
                ]
            }

        response = await self._client._api._request(
            "POST",
            f"/databases/{database_id}/query",
            json={"filter": filters}
        )

        return [
            Task(self._client, page_data)
            for page_data in response.get("results", [])
        ]

    async def list_unassigned(self) -> list:
        """List unassigned tasks."""
        from better_notion.plugins.official.agents_sdk.models import Task

        database_id = self._get_database_id("Tasks")
        if not database_id:
            return []

        response = await self._client._api._request(
            "POST",
            f"/databases/{database_id}/query",
            json={
                "filter": {
                    "property": "Assignee",
                    "select": {"is_empty": True}
                }
            }
        )

        return [
            Task(self._client, page_data)
            for page_data in response.get("results", [])
        ]


class TeamManager(BaseManager):
    """Manager for team members."""

    def __init__(self, client: NotionClient, workspace_config: dict):
        super().__init__(client, workspace_config)
        self._database_id = workspace_config.get("Team_Members")

    async def list_members(self) -> list:
        """List all team members."""
        from better_notion.plugins.official.agents_sdk.models import TeamMember

        if not self._database_id:
            return []

        response = await self._client._api._request(
            "POST",
            f"/databases/{self._database_id}/query",
            json={}
        )

        return [
            TeamMember(self._client, page_data)
            for page_data in response.get("results", [])
        ]

    async def get_workload(self, member_name: str) -> dict:
        """Get workload for a team member."""
        from better_notion.plugins.official.agents_sdk.models import Task

        # Get all tasks assigned to this person
        database_id = self._get_database_id("Tasks")
        if not database_id:
            return {"error": "Tasks database not configured"}

        response = await self._client._api._request(
            "POST",
            f"/databases/{database_id}/query",
            json={
                "filter": {
                    "property": "Assignee",
                    "select": {"equals": member_name}
                }
            }
        )

        tasks = [
            Task(self._client, page_data)
            for page_data in response.get("results", [])
        ]

        active_tasks = [t for t in tasks if t.status in ("Backlog", "Claimed", "In Progress")]

        return {
            "user_name": member_name,
            "active_tasks": len(active_tasks),
            "completed_tasks": len([t for t in tasks if t.status == "Completed"]),
            "tasks": [
                {
                    "id": t.id,
                    "title": t.title,
                    "priority": t.priority,
                    "status": t.status
                }
                for t in active_tasks
            ]
        }

    async def list_available(self, max_active_tasks: int = 5) -> list:
        """List available team members (those with low workload)."""
        members = await self.list_members()
        available = []

        for member in members:
            if not member.is_active:
                continue

            workload = await self.get_workload(member.name)
            active_count = workload.get("active_tasks", 0)

            if active_count < max_active_tasks:
                available.append({
                    "id": member.id,
                    "name": member.name,
                    "role": member.role,
                    "active_tasks": active_count,
                    "capacity_remaining": member.max_tasks - active_count,
                    "skills": member.skills
                })

        return available
```

### Phase 3: CLI Commands (1-2 days)

```bash
# better_notion/plugins/official/agents_cli.py

@app.command()
def tasks_assign(
    task_ids: list[str] = typer.Argument(..., help="Task IDs to assign"),
    to: str = typer.Option(..., "--to", help="Person to assign to")
):
    """Assign task(s) to a person."""
    # ... implementation ...

@app.command()
def tasks_unassign(
    task_id: str = typer.Argument(..., help="Task ID to unassign")
):
    """Unassign a task."""
    # ... implementation ...

@app.command()
def tasks_reassign(
    task_id: str = typer.Argument(..., help="Task ID to reassign"),
    from_: str = typer.Option(..., "--from", help="Current assignee"),
    to: str = typer.Option(..., "--to", help="New assignee")
):
    """Reassign a task from one person to another."""
    # ... implementation ...

@app.command()
def tasks_list_by_assignee(
    assignee: str = typer.Option(..., "--assignee", help="Filter by assignee"),
    status: Optional[str] = typer.Option(None, "--status", help="Filter by status")
):
    """List tasks assigned to a person."""
    # ... implementation ...

@app.command()
def tasks_unassigned():
    """List unassigned tasks."""
    # ... implementation ...

@app.command()
def tasks_mine():
    """List tasks assigned to the current user."""
    # ... implementation ...

@app.command()
def team_list():
    """List all team members."""
    # ... implementation ...

@app.command()
def team_workload(
    member_name: str = typer.Argument(..., help="Team member name")
):
    """Show workload for a team member."""
    # ... implementation ...

@app.command()
def team_available(
    max_active: int = typer.Option(5, "--max-active", help="Max active tasks to be considered available")
):
    """List available team members (those with low workload)."""
    # ... implementation ...
```

---

## CLI Examples

### Example 1: Assigning Tasks to Team Members

```bash
# Create a task
notion agents tasks create \
  "Build authentication service" \
  --version-id ver_123

# Returns: {"id": "task_123", ...}

# Assign to Alice
notion agents tasks assign task_123 --to "Alice Chen"
# Returns: {"task_id": "task_123", "assigned_to": "Alice Chen", "previous": null}

# Check Alice's workload
notion agents team workload "Alice Chen"
# Returns:
# {
#   "user_name": "Alice Chen",
#   "active_tasks": 1,
#   "tasks": [
#     {"id": "task_123", "title": "Build authentication service", "priority": "Medium", "status": "Backlog"}
#   ]
# }
```

### Example 2: Finding Available Team Members

```bash
# Find who can take new tasks
notion agents team available
# Returns:
# {
#   "available": [
#     {"name": "Alice Chen", "active_tasks": 2, "capacity_remaining": 8},
#     {"name": "Bob Smith", "active_tasks": 1, "capacity_remaining": 9}
#   ]
# }

# Assign task to the most available person
notion agents tasks assign task_456 --to "Bob Smith"
```

### Example 3: Reassigning Tasks

```bash
# Alice is overloaded, reassign one of her tasks to Bob
notion agents tasks reassign task_123 --from "Alice Chen" --to "Bob Smith"
# Returns: {"task_id": "task_123", "from": "Alice Chen", "to": "Bob Smith"}
```

### Example 4: Viewing All Tasks for a Person

```bash
# See all of Alice's tasks
notion agents tasks list --assignee "Alice Chen"
# Returns:
# {
#   "tasks": [
#     {"id": "task_001", "title": "Fix auth bug", "status": "In Progress", "priority": "High"},
#     {"id": "task_002", "title": "Add dark mode", "status": "Backlog", "priority": "Medium"}
#   ]
# }

# See only Alice's in-progress tasks
notion agents tasks list --assignee "Alice Chen" --status "In Progress"
```

### Example 5: Finding Unassigned Tasks

```bash
# Find all tasks that need assignment
notion agents tasks list --unassigned
# Returns:
# {
#   "tasks": [
#     {"id": "task_003", "title": "Write unit tests", "status": "Backlog"}
#   ]
# }

# Assign them to available team members
notion agents tasks assign task_003 --to "Bob Smith"
```

---

## Acceptance Criteria

### Phase 1: Model Updates

- [ ] Task model has `assignee` and `assignee_id` properties
- [ ] Task model has `assign_to()` and `unassign()` methods
- [ ] TeamMember model exists (optional, if using Team Members database)

### Phase 2: Manager Updates

- [ ] TaskManager has `assign()` method
- [ ] TaskManager has `unassign()` method
- [ ] TaskManager has `reassign()` method
- [ ] TaskManager has `list_by_assignee()` method
- [ ] TaskManager has `list_unassigned()` method
- [ ] TeamManager has `list_members()` method
- [ ] TeamManager has `get_workload()` method
- [ ] TeamManager has `list_available()` method

### Phase 3: CLI Commands

- [ ] `notion agents tasks assign <id> --to <name>` works
- [ ] `notion agents tasks assign <id1> <id2> --to <name>` works (multiple tasks)
- [ ] `notion agents tasks unassign <id>` works
- [ ] `notion agents tasks reassign <id> --from <name> --to <name>` works
- [ ] `notion agents tasks list --assignee <name>` works
- [ ] `notion agents tasks list --unassigned` works
- [ ] `notion agents tasks list --assignee <name> --status <status>` works
- [ ] `notion agents tasks mine` works
- [ ] `notion agents team list` works
- [ ] `notion agents team workload <name>` works
- [ ] `notion agents team available` works

### Phase 4: Integration

- [ ] Task get command shows assignee details
- [ ] Assignment changes are reflected in task status
- [ ] Workload calculations are accurate
- [ ] Available members list is correctly filtered

---

## Related Issues

- Enables: #040 (Task dependencies - for dependent task assignment)
- Related to: #029 (Task workflow commands)
- Blocks: #044 (Consolidated status view - for team overview)
- Related to: #041 (Cross-entity relations - for assigning related entities)

---

## Migration Path

### For Existing Workspaces

1. Add `Assignee` property to Tasks database (select type with team member names)
2. Optionally create Team Members database for advanced management
3. Existing tasks without assignees will be considered unassigned

### For Code

1. Update Task model with assignee properties
2. Update TaskManager with assignment methods
3. Create TeamManager
4. Add CLI commands
5. Update agents schema

---

## Rollout Plan

1. **Phase 1**: Implement model changes (Task assignee properties)
2. **Phase 2**: Implement manager changes (assignment logic)
3. **Phase 3**: Add CLI commands for individual task operations
4. **Phase 4**: Add team management commands (workload, available)
5. **Phase 5**: Integration testing with real team workflows

---

## Open Questions

1. Should we support both human and AI agent assignment in the same field?
   - **Recommendation**: Yes, use a select field with options for each human + "AI Agent"
2. Should we use a separate Team Members database or just a select field?
   - **Recommendation**: Start with select field (simpler), add Team Members database in v2 if needed
3. How should we handle authentication/authorization for `tasks mine`?
   - **Recommendation**: Use environment variable or config file for current user identity
4. Should we support skill-based task assignment?
   - **Recommendation**: Add in Phase 4 using Skills multi-select property

---

## Edge Cases to Handle

1. **Assigning to non-existent team member**: Should fail gracefully with clear error message
2. **Unassigning already unassigned task**: Should be idempotent (no error if already unassigned)
3. **Reassigning from wrong person**: Should fail with clear error message
4. **Task completion**: Should keep assignee for historical tracking
5. **Deleting a team member**: Should handle or reassign their tasks
6. **Case sensitivity**: Should handle assignee names case-insensitively or enforce exact match
