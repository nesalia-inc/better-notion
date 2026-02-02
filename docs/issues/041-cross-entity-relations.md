# Issue #041: Cross-Entity Relations System

## Problem Statement

The Agents CLI currently lacks cross-entity relationship functionality, making it impossible to track relationships between different entity types. This is critical for real-world project management where:

- **Incidents** are often caused by **Work Issues** (bugs)
- **Ideas** are implemented as **Tasks**
- **Work Issues** can block **Tasks**
- **Tasks** can resolve **Work Issues**

### Current Limitation

```bash
# What users CANNOT do:
notion agents incidents link incident_123 --work-issue issue_456
notion agents ideas link idea_789 --task task_012
notion agents tasks link task_abc --blocks issue_xyz
notion agents incidents incident_123 --show-related  # Show linked work issue
```

### Impact

Without cross-entity relations:
- Cannot track root causes of incidents
- Cannot see which tasks implement which ideas
- Cannot see which work issues are blocking tasks
- Makes it impossible to trace the full lifecycle from idea → task → completion
- Reduces the system from a "project management tool" to a collection of isolated lists

---

## Proposed Solution

### 1. CLI Interface for Linking Entities

```bash
# Link an incident to a work issue (root cause)
notion agents incidents link incident_123 --work-issue issue_456
# Returns: {"incident_id": "incident_123", "work_issue_id": "issue_456", "linked": true}

# Link an idea to a task (implementation tracking)
notion agents ideas link idea_789 --task task_012
# Returns: {"idea_id": "idea_789", "task_id": "task_012", "linked": true}

# Link a task to a work issue (blocking relationship)
notion agents tasks link task_abc --blocks issue_xyz
# Returns: {"task_id": "task_abc", "work_issue_id": "issue_xyz", "linked": true}

# Unlink entities
notion agents incidents unlink incident_123 --work-issue
notion agents ideas unlink idea_789 --task
notion agents tasks unlink task_abc --blocks
```

### 2. Enhanced Get Commands to Show Relations

```bash
# Get incident with linked work issue
notion agents incidents get incident_123
# Returns:
# {
#   "id": "incident_123",
#   "title": "API downtime",
#   "work_issue": {
#     "id": "issue_456",
#     "title": "Database connection leak",
#     "status": "In Progress",
#     "severity": "Critical"
#   },
#   ...
# }

# Get idea with linked task
notion agents ideas get idea_789
# Returns:
# {
#   "id": "idea_789",
#   "title": "Add dark mode",
#   "task": {
#     "id": "task_012",
#     "title": "Implement dark mode toggle",
#     "status": "In Progress",
#     "priority": "High"
#   },
#   ...
# }

# Get work issue with related incidents and tasks
notion agents work-issues get issue_456 --show-related
# Returns:
# {
#   "id": "issue_456",
#   "title": "Database connection leak",
#   "related_incidents": [
#     {"id": "incident_123", "title": "API downtime", "status": "Resolved"}
#   ],
#   "blocking_tasks": [
#     {"id": "task_abc", "title": "Feature X", "status": "Claimed"}
#   ],
#   ...
# }
```

### 3. Query Commands for Finding Related Entities

```bash
# Find all incidents caused by a work issue
notion agents incidents list --caused-by issue_456
# Returns: {"incidents": [{"id": "incident_123", ...}]}

# Find all tasks implementing an idea
notion agents tasks list --implements idea_789
# Returns: {"tasks": [{"id": "task_012", ...}]}

# Find all tasks blocked by a work issue
notion agents tasks list --blocked-by issue_xyz
# Returns: {"tasks": [{"id": "task_abc", ...}]}

# Find the idea that led to a task
notion agents ideas list --implemented-by task_012
# Returns: {"ideas": [{"id": "idea_789", ...}]}
```

---

## Database Schema Changes

### 1. Add Relations to Incidents Schema

```yaml
Root Cause Work Issue:
  type: relation
  relation:
    database_id: "<Work Issues Database ID>"
    dual_property: "Caused Incidents"
  description: "The work issue (bug) that caused this incident"
```

### 2. Add Relations to Ideas Schema

```yaml
Implementation Task:
  type: relation
  relation:
    database_id: "<Tasks Database ID>"
    dual_property: "Source Idea"
  description: "The task that implements this idea"
```

### 3. Add Relations to Work Issues Schema

```yaml
Blocking Tasks:
  type: relation
  relation:
    database_id: "<Tasks Database ID>"
    dual_property: "Blocked By"
  description: "Tasks that are blocked by this work issue"
```

### 4. Add Relations to Tasks Schema

```yaml
Related Work Issue:
  type: relation
  relation:
    database_id: "<Work Issues Database ID>"
    dual_property: "Blocking Tasks"
  description: "Work issue that this task resolves or is blocked by"
```

---

## Implementation Architecture

### Phase 1: Model Updates (1 day)

```python
# better_notion/plugins/official/agents_sdk/models.py

class Incident(DatabasePageEntityMixin, BaseEntity):
    # ... existing code ...

    @property
    def root_cause_work_issue_id(self) -> str | None:
        """Get the work issue ID that caused this incident."""
        prop = self._data["properties"].get("Root Cause Work Issue")
        if prop and prop.get("type") == "relation":
            relations = prop.get("relation", [])
            return relations[0]["id"] if relations else None
        return None

    @property
    async def root_cause_work_issue(self) -> "WorkIssue | None":
        """Get the WorkIssue object that caused this incident."""
        from better_notion.plugins.official.agents_sdk.models import WorkIssue

        issue_id = self.root_cause_work_issue_id
        if not issue_id:
            return None

        # Check cache first
        if issue_id in self._client.page_cache:
            return self._client.page_cache[issue_id]

        return await WorkIssue.get(issue_id, client=self._client)

    async def link_to_work_issue(self, work_issue_id: str) -> None:
        """Link this incident to a work issue."""
        from better_notion._sdk.models.page import Page

        await Page.update(
            self.id,
            client=self._client,
            properties={
                "Root Cause Work Issue": {
                    "relation": [{"id": work_issue_id}]
                }
            }
        )

    async def unlink_work_issue(self) -> None:
        """Unlink this incident from its work issue."""
        from better_notion._sdk.models.page import Page

        await Page.update(
            self.id,
            client=self._client,
            properties={
                "Root Cause Work Issue": {"relation": []}
            }
        )


class Idea(DatabasePageEntityMixin, BaseEntity):
    # ... existing code ...

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

    async def link_to_task(self, task_id: str) -> None:
        """Link this idea to a task."""
        from better_notion._sdk.models.page import Page

        await Page.update(
            self.id,
            client=self._client,
            properties={
                "Implementation Task": {
                    "relation": [{"id": task_id}]
                }
            }
        )

    async def unlink_task(self) -> None:
        """Unlink this idea from its task."""
        from better_notion._sdk.models.page import Page

        await Page.update(
            self.id,
            client=self._client,
            properties={
                "Implementation Task": {"relation": []}
            }
        )


class Task(DatabasePageEntityMixin, BaseEntity):
    # ... existing code ...

    @property
    def related_work_issue_id(self) -> str | None:
        """Get the work issue ID related to this task."""
        prop = self._data["properties"].get("Related Work Issue")
        if prop and prop.get("type") == "relation":
            relations = prop.get("relation", [])
            return relations[0]["id"] if relations else None
        return None

    @property
    async def related_work_issue(self) -> "WorkIssue | None":
        """Get the WorkIssue object related to this task."""
        from better_notion.plugins.official.agents_sdk.models import WorkIssue

        issue_id = self.related_work_issue_id
        if not issue_id:
            return None

        if issue_id in self._client.page_cache:
            return self._client.page_cache[issue_id]

        return await WorkIssue.get(issue_id, client=self._client)

    async def link_to_work_issue(self, work_issue_id: str) -> None:
        """Link this task to a work issue."""
        from better_notion._sdk.models.page import Page

        await Page.update(
            self.id,
            client=self._client,
            properties={
                "Related Work Issue": {
                    "relation": [{"id": work_issue_id}]
                }
            }
        )

    async def unlink_work_issue(self) -> None:
        """Unlink this task from its work issue."""
        from better_notion._sdk.models.page import Page

        await Page.update(
            self.id,
            client=self._client,
            properties={
                "Related Work Issue": {"relation": []}
            }
        )


class WorkIssue(DatabasePageEntityMixin, BaseEntity):
    # ... existing code ...

    @property
    def caused_incident_ids(self) -> list[str]:
        """Get incident IDs caused by this work issue."""
        prop = self._data["properties"].get("Caused Incidents")
        if prop and prop.get("type") == "relation":
            return [rel["id"] for rel in prop.get("relation", [])]
        return []

    @property
    def blocking_task_ids(self) -> list[str]:
        """Get task IDs blocked by this work issue."""
        prop = self._data["properties"].get("Blocking Tasks")
        if prop and prop.get("type") == "relation":
            return [rel["id"] for rel in prop.get("relation", [])]
        return []

    @property
    async def caused_incidents(self) -> list["Incident"]:
        """Get Incident objects caused by this work issue."""
        from better_notion.plugins.official.agents_sdk.models import Incident

        incidents = []
        for incident_id in self.caused_incident_ids:
            if incident_id in self._client.page_cache:
                incidents.append(self._client.page_cache[incident_id])
            else:
                incident = await Incident.get(incident_id, client=self._client)
                self._client.page_cache[incident_id] = incident
                incidents.append(incident)
        return incidents

    @property
    async def blocking_tasks(self) -> list["Task"]:
        """Get Task objects blocked by this work issue."""
        from better_notion.plugins.official.agents_sdk.models import Task

        tasks = []
        for task_id in self.blocking_task_ids:
            if task_id in self._client.page_cache:
                tasks.append(self._client.page_cache[task_id])
            else:
                task = await Task.get(task_id, client=self._client)
                self._client.page_cache[task_id] = task
                tasks.append(task)
        return tasks
```

### Phase 2: Manager Updates (1 day)

```python
# better_notion/plugins/official/agents_sdk/managers.py

class IncidentManager:
    # ... existing code ...

    async def link_to_work_issue(
        self,
        incident_id: str,
        work_issue_id: str
    ) -> dict:
        """Link an incident to a work issue."""
        from better_notion.plugins.official.agents_sdk.models import Incident

        incident = await Incident.get(incident_id, client=self._client)
        await incident.link_to_work_issue(work_issue_id)

        return {
            "incident_id": incident_id,
            "work_issue_id": work_issue_id,
            "linked": True
        }

    async def unlink_work_issue(self, incident_id: str) -> dict:
        """Unlink an incident from its work issue."""
        from better_notion.plugins.official.agents_sdk.models import Incident

        incident = await Incident.get(incident_id, client=self._client)
        await incident.unlink_work_issue()

        return {
            "incident_id": incident_id,
            "unlinked": True
        }

    async def list_caused_by(self, work_issue_id: str) -> list:
        """List all incidents caused by a work issue."""
        from better_notion.plugins.official.agents_sdk.models import Incident

        database_id = self._get_database_id("Incidents")
        if not database_id:
            return []

        response = await self._client._api._request(
            "POST",
            f"/databases/{database_id}/query",
            json={
                "filter": {
                    "property": "Root Cause Work Issue",
                    "relation": {"contains": work_issue_id}
                }
            }
        )

        return [
            Incident(self._client, page_data)
            for page_data in response.get("results", [])
        ]


class IdeaManager:
    # ... existing code ...

    async def link_to_task(
        self,
        idea_id: str,
        task_id: str
    ) -> dict:
        """Link an idea to a task."""
        from better_notion.plugins.official.agents_sdk.models import Idea

        idea = await Idea.get(idea_id, client=self._client)
        await idea.link_to_task(task_id)

        return {
            "idea_id": idea_id,
            "task_id": task_id,
            "linked": True
        }

    async def unlink_task(self, idea_id: str) -> dict:
        """Unlink an idea from its task."""
        from better_notion.plugins.official.agents_sdk.models import Idea

        idea = await Idea.get(idea_id, client=self._client)
        await idea.unlink_task()

        return {
            "idea_id": idea_id,
            "unlinked": True
        }

    async def list_implemented_by(self, task_id: str) -> list:
        """List ideas implemented by a task."""
        from better_notion.plugins.official.agents_sdk.models import Idea

        database_id = self._get_database_id("Ideas")
        if not database_id:
            return []

        response = await self._client._api._request(
            "POST",
            f"/databases/{database_id}/query",
            json={
                "filter": {
                    "property": "Implementation Task",
                    "relation": {"contains": task_id}
                }
            }
        )

        return [
            Idea(self._client, page_data)
            for page_data in response.get("results", [])
        ]


class TaskManager:
    # ... existing code ...

    async def link_to_work_issue(
        self,
        task_id: str,
        work_issue_id: str
    ) -> dict:
        """Link a task to a work issue."""
        from better_notion.plugins.official.agents_sdk.models import Task

        task = await Task.get(task_id, client=self._client)
        await task.link_to_work_issue(work_issue_id)

        return {
            "task_id": task_id,
            "work_issue_id": work_issue_id,
            "linked": True
        }

    async def unlink_work_issue(self, task_id: str) -> dict:
        """Unlink a task from its work issue."""
        from better_notion.plugins.official.agents_sdk.models import Task

        task = await Task.get(task_id, client=self._client)
        await task.unlink_work_issue()

        return {
            "task_id": task_id,
            "unlinked": True
        }

    async def list_blocked_by(self, work_issue_id: str) -> list:
        """List tasks blocked by a work issue."""
        from better_notion.plugins.official.agents_sdk.models import Task

        database_id = self._get_database_id("Tasks")
        if not database_id:
            return []

        response = await self._client._api._request(
            "POST",
            f"/databases/{database_id}/query",
            json={
                "filter": {
                    "property": "Related Work Issue",
                    "relation": {"contains": work_issue_id}
                }
            }
        )

        return [
            Task(self._client, page_data)
            for page_data in response.get("results", [])
        ]

    async def list_implements(self, idea_id: str) -> list:
        """List tasks that implement an idea."""
        from better_notion.plugins.official.agents_sdk.models import Task

        database_id = self._get_database_id("Tasks")
        if not database_id:
            return []

        response = await self._client._api._request(
            "POST",
            f"/databases/{database_id}/query",
            json={
                "filter": {
                    "property": "Source Idea",
                    "relation": {"contains": idea_id}
                }
            }
        )

        return [
            Task(self._client, page_data)
            for page_data in response.get("results", [])
        ]
```

### Phase 3: CLI Commands (1-2 days)

```bash
# better_notion/plugins/official/agents_cli.py

@app.command()
def incidents_link(
    incident_id: str,
    work_issue: str = typer.Option(None, "--work-issue", help="Work issue ID to link")
):
    """Link an incident to a work issue (root cause)."""
    # ... implementation ...

@app.command()
def incidents_unlink(
    incident_id: str,
    work_issue: bool = typer.Option(False, "--work-issue", help="Unlink work issue")
):
    """Unlink an incident from a work issue."""
    # ... implementation ...

@app.command()
def ideas_link(
    idea_id: str,
    task: str = typer.Option(None, "--task", help="Task ID to link")
):
    """Link an idea to a task."""
    # ... implementation ...

@app.command()
def ideas_unlink(
    idea_id: str,
    task: bool = typer.Option(False, "--task", help="Unlink task")
):
    """Unlink an idea from a task."""
    # ... implementation ...

@app.command()
def tasks_link(
    task_id: str,
    work_issue: str = typer.Option(None, "--work-issue", help="Work issue ID to link")
):
    """Link a task to a work issue."""
    # ... implementation ...

@app.command()
def tasks_unlink(
    task_id: str,
    work_issue: bool = typer.Option(False, "--work-issue", help="Unlink work issue")
):
    """Unlink a task from a work issue."""
    # ... implementation ...
```

---

## CLI Examples

### Example 1: Incident Root Cause Tracking

```bash
# An incident occurs
notion agents incidents create \
  "API downtime" \
  --project-id proj_123 \
  --severity Critical \
  --type "Service Disruption"

# Returns: {"id": "incident_123", ...}

# Investigation reveals the root cause (a bug)
notion agents work-issues create \
  "Database connection leak" \
  --project-id proj_123 \
  --type Bug \
  --severity Critical

# Returns: {"id": "issue_456", ...}

# Link the incident to the work issue
notion agents incidents link incident_123 --work-issue issue_456
# Returns: {"incident_id": "incident_123", "work_issue_id": "issue_456", "linked": true}

# View incident with root cause
notion agents incidents get incident_123
# Returns:
# {
#   "id": "incident_123",
#   "title": "API downtime",
#   "root_cause_work_issue": {
#     "id": "issue_456",
#     "title": "Database connection leak",
#     "status": "Backlog",
#     "severity": "Critical"
#   }
# }

# Find all incidents caused by this work issue
notion agents incidents list --caused-by issue_456
# Returns: {"incidents": [{"id": "incident_123", "title": "API downtime", ...}]}
```

### Example 2: Idea to Task Implementation

```bash
# Submit an idea
notion agents ideas create \
  "Add dark mode support" \
  --project-id proj_123 \
  --category "Feature" \
  --effort Medium

# Returns: {"id": "idea_789", ...}

# Idea gets accepted
notion agents ideas accept idea_789

# Create a task to implement the idea
notion agents tasks create \
  "Implement dark mode toggle" \
  --version-id ver_123 \
  --priority High

# Returns: {"id": "task_012", ...}

# Link the task to the idea
notion agents ideas link idea_789 --task task_012
# Returns: {"idea_id": "idea_789", "task_id": "task_012", "linked": true}

# View idea with implementation task
notion agents ideas get idea_789
# Returns:
# {
#   "id": "idea_789",
#   "title": "Add dark mode support",
#   "status": "Accepted",
#   "implementation_task": {
#     "id": "task_012",
#     "title": "Implement dark mode toggle",
#     "status": "Backlog",
#     "priority": "High"
#   }
# }
```

### Example 3: Work Issue Blocking Tasks

```bash
# A bug is discovered
notion agents work-issues create \
  "Authentication token expires prematurely" \
  --project-id proj_123 \
  --type Bug \
  --severity High

# Returns: {"id": "issue_xyz", ...}

# Some tasks depend on this being fixed
notion agents tasks create \
  "Build user profile feature" \
  --version-id ver_123

# Returns: {"id": "task_abc", ...}

# Link the task to the blocking work issue
notion agents tasks link task_abc --work-issue issue_xyz
# Returns: {"task_id": "task_abc", "work_issue_id": "issue_xyz", "linked": true}

# Find all tasks blocked by this work issue
notion agents tasks list --blocked-by issue_xyz
# Returns:
# {
#   "tasks": [
#     {"id": "task_abc", "title": "Build user profile feature", "status": "Backlog"}
#   ]
# }

# View work issue with blocked tasks
notion agents work-issues get issue_xyz --show-related
# Returns:
# {
#   "id": "issue_xyz",
#   "title": "Authentication token expires prematurely",
#   "blocking_tasks": [
#     {"id": "task_abc", "title": "Build user profile feature", "status": "Backlog"}
#   ]
# }
```

---

## Acceptance Criteria

### Phase 1: Model Updates

- [ ] Incident model has `root_cause_work_issue_id` and `root_cause_work_issue` properties
- [ ] Idea model has `implementation_task_id` and `implementation_task` properties
- [ ] Task model has `related_work_issue_id` and `related_work_issue` properties
- [ ] WorkIssue model has `caused_incident_ids` and `caused_incidents` properties
- [ ] WorkIssue model has `blocking_task_ids` and `blocking_tasks` properties
- [ ] All models have `link_to_*` and `unlink_*` methods

### Phase 2: Manager Updates

- [ ] IncidentManager has `link_to_work_issue()` and `unlink_work_issue()` methods
- [ ] IncidentManager has `list_caused_by()` method
- [ ] IdeaManager has `link_to_task()` and `unlink_task()` methods
- [ ] IdeaManager has `list_implemented_by()` method
- [ ] TaskManager has `link_to_work_issue()` and `unlink_work_issue()` methods
- [ ] TaskManager has `list_blocked_by()` and `list_implements()` methods

### Phase 3: CLI Commands

- [ ] `notion agents incidents link <id> --work-issue <id>` works
- [ ] `notion agents incidents unlink <id> --work-issue` works
- [ ] `notion agents ideas link <id> --task <id>` works
- [ ] `notion agents ideas unlink <id> --task` works
- [ ] `notion agents tasks link <id> --work-issue <id>` works
- [ ] `notion agents tasks unlink <id> --work-issue` works
- [ ] `notion agents incidents list --caused-by <id>` works
- [ ] `notion agents tasks list --blocked-by <id>` works
- [ ] `notion agents tasks list --implements <id>` works
- [ ] `notion agents ideas list --implemented-by <id>` works

### Phase 4: Enhanced Get Commands

- [ ] `incidents get` shows linked work issue
- [ ] `ideas get` shows linked task
- [ ] `tasks get` shows linked work issue
- [ ] `work-issues get --show-related` shows caused incidents and blocking tasks

---

## Related Issues

- Enables: #040 (Task dependencies)
- Related to: #030 (Ideas workflow integration)
- Related to: #029 (Task workflow commands)
- Blocks: #042 (Human assignment - for assigning responsible parties for related entities)

---

## Migration Path

### For Existing Workspaces

No migration needed - this is a new feature. Existing databases will be updated with the new relation properties via a schema migration.

### For Code

1. Update entity models with relation properties
2. Update entity managers with link/unlink methods
3. Add CLI commands for linking entities
4. Update get/list commands to show relations
5. Update agents schema

---

## Rollout Plan

1. **Phase 1**: Implement model changes (properties and link methods)
2. **Phase 2**: Implement manager changes (query methods)
3. **Phase 3**: Add CLI commands for linking/unlinking
4. **Phase 4**: Update existing get/list commands to display relations
5. **Phase 5**: Add comprehensive testing for cross-entity workflows

---

## Open Questions

1. Should we allow multiple relations (e.g., one task → multiple work issues)?
   - **Recommendation**: Start with single relations, extend to multiple if needed
2. Should we add validation to prevent circular links (e.g., Task A ↔ Task B via work issues)?
   - **Recommendation**: Yes, add validation in Phase 4
3. Should we support cross-entity dependencies (e.g., Task depends on Idea being accepted)?
   - **Recommendation**: No, keep relations simple and explicit

---

## Edge Cases to Handle

1. **Linking to non-existent entities**: Should fail gracefully with clear error message
2. **Unlinking when no relation exists**: Should be idempotent (no error if already unlinked)
3. **Deleting an entity**: Should handle broken references in related entities
4. **Circular relations**: Should detect and reject (e.g., A blocks B, B blocks A)
5. **Updating relation properties**: Should support changing the linked entity (unlink + link)
