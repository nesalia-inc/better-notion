# Issue #047: Change History Tracking

## Problem Statement

The Agents CLI currently lacks change history tracking, making it impossible to audit changes, understand what happened, or troubleshoot issues. Users cannot see who changed what, when, or why.

### Current Limitation

```bash
# What users CANNOT do:
notion agents tasks history task_123
notion agents tasks log task_123 --limit 10
notion agents tasks diff task_123 --revision 2
notion agents audit --project proj_123 --days 7
```

### Current Workaround (Not Available)

```bash
# Users have to:
# 1. Use Notion web UI to see page history
# 2. Manually compare versions
# 3. No programmatic access to history
# 4. No way to see who made what change
# 5. No way to revert changes

# This is:
# - Impossible to automate
# - No audit trail
# - Difficult to troubleshoot
# - Can't track down who made a mistake
```

### Impact

Without change history:
- No audit trail for compliance or debugging
- Cannot track down who made what change
- Difficult to troubleshoot issues
- No way to see evolution of tasks/ideas
- Cannot revert accidental changes
- Harder to learn from past decisions
- No visibility into team activity patterns

### Real-World Use Cases

```bash
# Use case 1: Troubleshooting - why was this task rejected?
notion agents tasks history task_123
# Returns: Timeline of all changes with who/when/why

# Use case 2: Audit trail - who changed the priority?
notion agents tasks log task_123
# Returns: "Alice changed priority from Low to High on 2026-02-01"

# Use case 3: Compliance - show all changes this week
notion agents audit --project proj_123 --days 7
# Returns: All changes across the project in the last 7 days

# Use case 4: Revert - undo a mistaken change
notion agents tasks revert task_123 --to-revision 5
# Returns: Task restored to previous state
```

---

## Proposed Solution

### 1. Entity History Command

```bash
# Get full history of an entity
notion agents tasks history task_123
# Returns:
# {
#   "entity_id": "task_123",
#   "title": "Fix authentication bug",
#   "revisions": [
#     {
#       "revision_id": 1,
#       "timestamp": "2026-02-01T10:00:00Z",
#       "author": "Alice Chen",
#       "changes": [
#         {"property": "Status", "from": null, "to": "Backlog"},
#         {"property": "Priority", "from": null, "to": "Medium"}
#       ],
#       "reason": "Initial creation"
#     },
#     {
#       "revision_id": 2,
#       "timestamp": "2026-02-01T14:30:00Z",
#       "author": "Bob Smith",
#       "changes": [
#         {"property": "Priority", "from": "Medium", "to": "High"}
#       ],
#       "reason": "Urgent fix needed"
#     },
#     {
#       "revision_id": 3,
#       "timestamp": "2026-02-02T09:15:00Z",
#       "author": "Alice Chen",
#       "changes": [
#         {"property": "Status", "from": "Backlog", "to": "In Progress"}
#       ],
#       "reason": "Started working on it"
#     }
#   ],
#   "total_revisions": 3
# }
```

### 2. Change Log Command

```bash
# Get recent changes (simplified view)
notion agents tasks log task_123 --limit 5
# Returns:
# [
#   "2026-02-02 09:15 - Alice Chen: Changed Status from 'Backlog' to 'In Progress'",
#   "2026-02-01 14:30 - Bob Smith: Changed Priority from 'Medium' to 'High'",
#   "2026-02-01 10:00 - Alice Chen: Created task"
# ]
```

### 3. Diff Command

```bash
# Compare two revisions
notion agents tasks diff task_123 --revision 2 --vs 3
# Returns:
# {
#   "entity_id": "task_123",
#   "comparing": {
#     "from_revision": 2,
#     "to_revision": 3
#   },
#   "changes": [
#     {
#       "property": "Status",
#       "from": "Backlog",
#       "to": "In Progress"
#     },
#     {
#       "property": "Assignee",
#       "from": null,
#       "to": "Alice Chen"
#     }
#   ]
# }
```

### 4. Audit Log Command

```bash
# Get audit log for a project
notion agents audit --project proj_123 --days 7
# Returns:
# {
#   "project_id": "proj_123",
#   "time_range": {
#     "from": "2026-01-26T00:00:00Z",
#     "to": "2026-02-02T00:00:00Z"
#   },
#   "changes": [
#     {
#       "timestamp": "2026-02-02T09:15:00Z",
#       "author": "Alice Chen",
#       "entity_type": "task",
#       "entity_id": "task_123",
#       "entity_title": "Fix authentication bug",
#       "action": "updated",
#       "changes": ["Status: Backlog → In Progress"]
#     },
#     {
#       "timestamp": "2026-02-01T14:30:00Z",
#       "author": "Bob Smith",
#       "entity_type": "task",
#       "entity_id": "task_456",
#       "entity_title": "Add dark mode",
#       "action": "created",
#       "changes": []
#     }
#   ],
#   "summary": {
#     "total_changes": 25,
#     "by_author": {
#       "Alice Chen": 15,
#       "Bob Smith": 10
#     },
#     "by_action": {
#       "created": 8,
#       "updated": 17
#     }
#   }
# }
```

### 5. Revert Command

```bash
# Revert to a previous revision
notion agents tasks revert task_123 --to-revision 2
# Returns:
# {
#   "entity_id": "task_123",
#   "restored_to_revision": 2,
#   "changes_applied": [
#     {"property": "Status", "from": "In Progress", "to": "Backlog"},
#     {"property": "Assignee", "from": "Alice Chen", "to": null}
#   ]
# }
```

---

## Implementation Architecture

### Phase 1: History Tracking System (1-2 days)

```python
# better_notion/plugins/official/agents_sdk/history.py (new file)

from typing import Any, list
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

class ChangeType(Enum):
    CREATED = "created"
    UPDATED = "updated"
    DELETED = "deleted"
    STATUS_CHANGED = "status_changed"
    ASSIGNED = "assigned"
    UNASSIGNED = "unassigned"


@dataclass
class PropertyChange:
    """Represents a single property change."""
    property_name: str
    from_value: Any
    to_value: Any

    def to_dict(self) -> dict:
        return {
            "property": self.property_name,
            "from": self.from_value,
            "to": self.to_value
        }


@dataclass
class Revision:
    """Represents a single revision of an entity."""
    revision_id: int
    timestamp: datetime
    author: str
    changes: list[PropertyChange]
    reason: str | None

    def to_dict(self) -> dict:
        return {
            "revision_id": self.revision_id,
            "timestamp": self.timestamp.isoformat(),
            "author": self.author,
            "changes": [c.to_dict() for c in self.changes],
            "reason": self.reason
        }


class HistoryTracker:
    """Track and manage change history for entities."""

    def __init__(self, client: NotionClient):
        self._client = client
        self._storage = HistoryStorage(client)

    async def record_creation(
        self,
        entity_id: str,
        entity_type: str,
        author: str,
        properties: dict
    ) -> None:
        """Record entity creation."""
        changes = [
            PropertyChange(prop, None, self._format_value(value))
            for prop, value in properties.items()
        ]

        revision = Revision(
            revision_id=1,
            timestamp=datetime.now(timezone.utc),
            author=author,
            changes=changes,
            reason="Initial creation"
        )

        await self._storage.save_revision(entity_id, entity_type, revision)

    async def record_update(
        self,
        entity_id: str,
        entity_type: str,
        author: str,
        old_properties: dict,
        new_properties: dict,
        reason: str | None = None
    ) -> None:
        """Record entity update."""
        changes = []

        # Find changed properties
        all_keys = set(old_properties.keys()) | set(new_properties.keys())

        for key in all_keys:
            old_val = old_properties.get(key)
            new_val = new_properties.get(key)

            if old_val != new_val:
                changes.append(PropertyChange(
                    key,
                    self._format_value(old_val),
                    self._format_value(new_val)
                ))

        if not changes:
            return  # No changes to record

        # Get next revision number
        current_revisions = await self._storage.get_revisions(entity_id)
        next_revision_id = len(current_revisions) + 1

        revision = Revision(
            revision_id=next_revision_id,
            timestamp=datetime.now(timezone.utc),
            author=author,
            changes=changes,
            reason=reason
        )

        await self._storage.save_revision(entity_id, entity_type, revision)

    async def get_history(self, entity_id: str) -> list[Revision]:
        """Get full history for an entity."""
        return await self._storage.get_revisions(entity_id)

    async def get_revision(
        self,
        entity_id: str,
        revision_id: int
    ) -> dict | None:
        """Get entity state at a specific revision."""
        revisions = await self._storage.get_revisions(entity_id)

        if not revisions:
            return None

        # Reconstruct state by applying changes up to revision
        state = {}
        for revision in revisions[:revision_id]:
            for change in revision.changes:
                state[change.property_name] = change.to_value

        return state

    async def compare_revisions(
        self,
        entity_id: str,
        from_revision: int,
        to_revision: int
    ) -> dict:
        """Compare two revisions."""
        revisions = await self._storage.get_revisions(entity_id)

        if from_revision < 1 or from_revision > len(revisions):
            raise ValueError(f"Invalid from_revision: {from_revision}")

        if to_revision < 1 or to_revision > len(revisions):
            raise ValueError(f"Invalid to_revision: {to_revision}")

        # Get changes between revisions
        changes = []
        for revision in revisions[from_revision:to_revision]:
            changes.extend(revision.changes)

        return {
            "entity_id": entity_id,
            "comparing": {
                "from_revision": from_revision,
                "to_revision": to_revision
            },
            "changes": [c.to_dict() for c in changes]
        }

    def _format_value(self, value: Any) -> Any:
        """Format a value for storage."""
        if value is None:
            return None
        elif isinstance(value, dict):
            # Handle complex types like select, relation, etc.
            if "name" in value:
                return value["name"]
            elif "title" in value:
                return value["title"][0]["text"]["content"]
            else:
                return str(value)
        else:
            return value


class HistoryStorage:
    """Storage backend for history data."""

    def __init__(self, client: NotionClient):
        self._client = client

    async def save_revision(
        self,
        entity_id: str,
        entity_type: str,
        revision: Revision
    ) -> None:
        """Save a revision to storage."""
        # Option 1: Store in a separate Notion database
        database_id = self._client.workspace_config.get("Change_History")
        if database_id:
            await self._save_to_notion(database_id, entity_id, entity_type, revision)
        else:
            # Option 2: Store in local cache/file
            await self._save_to_local(entity_id, entity_type, revision)

    async def _save_to_notion(
        self,
        database_id: str,
        entity_id: str,
        entity_type: str,
        revision: Revision
    ) -> None:
        """Save revision to Notion database."""
        from better_notion._sdk.models.page import Page

        # Create a page in the Change History database
        await Page.create(
            client=self._client,
            database_id=database_id,
            title=f"{entity_type}:{entity_id} - r{revision.revision_id}",
            properties={
                "Entity ID": {"rich_text": [{"text": {"content": entity_id}}]},
                "Entity Type": {"select": {"name": entity_type}},
                "Revision": {"number": revision.revision_id},
                "Author": {"rich_text": [{"text": {"content": revision.author}}]},
                "Timestamp": {"date": {"start": revision.timestamp.isoformat()}},
                "Changes": {
                    "rich_text": [{
                        "text": {
                            "content": "\n".join([
                                f"{c.property_name}: {c.from_value} → {c.to_value}"
                                for c in revision.changes
                            ])
                        }
                    }]
                },
                "Reason": {
                    "rich_text": [{"text": {"content": revision.reason or ""}}]
                } if revision.reason else None
            }
        )

    async def _save_to_local(
        self,
        entity_id: str,
        entity_type: str,
        revision: Revision
    ) -> None:
        """Save revision to local storage."""
        import json
        from pathlib import Path

        # Create history directory
        history_dir = Path(".notion_history") / entity_type
        history_dir.mkdir(parents=True, exist_ok=True)

        # Save to file
        history_file = history_dir / f"{entity_id}.jsonl"

        # Append revision
        with open(history_file, "a") as f:
            f.write(json.dumps(revision.to_dict()) + "\n")

    async def get_revisions(self, entity_id: str) -> list[Revision]:
        """Get all revisions for an entity."""
        # Try local storage first
        revisions = await self._get_from_local(entity_id)

        if not revisions:
            # Try Notion storage
            revisions = await self._get_from_notion(entity_id)

        return revisions

    async def _get_from_local(self, entity_id: str) -> list[Revision]:
        """Get revisions from local storage."""
        import json
        from pathlib import Path

        # Search for entity in all entity type directories
        history_root = Path(".notion_history")

        if not history_root.exists():
            return []

        for entity_dir in history_root.iterdir():
            history_file = entity_dir / f"{entity_id}.jsonl"

            if history_file.exists():
                revisions = []
                with open(history_file) as f:
                    for line in f:
                        data = json.loads(line)
                        revisions.append(Revision(
                            revision_id=data["revision_id"],
                            timestamp=datetime.fromisoformat(data["timestamp"]),
                            author=data["author"],
                            changes=[
                                PropertyChange(
                                    c["property"],
                                    c.get("from"),
                                    c.get("to")
                                )
                                for c in data["changes"]
                            ],
                            reason=data.get("reason")
                        ))

                return revisions

        return []

    async def _get_from_notion(self, entity_id: str) -> list[Revision]:
        """Get revisions from Notion storage."""
        # Implement if using Notion database for storage
        return []
```

### Phase 2: Integration with Models (0.5 day)

```python
# better_notion/plugins/official/agents_sdk/models.py

# Update all entity models to track history

class Task(DatabasePageEntityMixin, BaseEntity):
    async def update(self, **kwargs) -> None:
        """Update task with history tracking."""
        # Get old state
        old_properties = self._get_property_dict()

        # Perform update
        await super().update(**kwargs)

        # Record change
        new_properties = self._get_property_dict()
        from better_notion.plugins.official.agents_sdk.history import HistoryTracker

        tracker = HistoryTracker(self._client)
        await tracker.record_update(
            entity_id=self.id,
            entity_type="task",
            author=get_current_user(),  # Need to implement
            old_properties=old_properties,
            new_properties=new_properties,
            reason=kwargs.get("reason")
        )

    def _get_property_dict(self) -> dict:
        """Get properties as a dictionary."""
        return {
            "Status": self.status,
            "Priority": self.priority,
            "Assignee": getattr(self, 'assignee', None),
            # ... other properties
        }
```

### Phase 3: CLI Commands (1 day)

```bash
# better_notion/plugins/official/agents_cli.py

@app.command()
def tasks_history(
    task_id: str = typer.Argument(..., help="Task ID"),
    limit: int = typer.Option(50, "--limit", "-n")
):
    """Get full history of a task."""
    # ... implementation ...

@app.command()
def tasks_log(
    task_id: str = typer.Argument(..., help="Task ID"),
    limit: int = typer.Option(10, "--limit", "-n")
):
    """Get recent changes log for a task."""
    # ... implementation ...

@app.command()
def tasks_diff(
    task_id: str = typer.Argument(..., help="Task ID"),
    revision: int = typer.Option(..., "--revision", "-r", help="Base revision"),
    vs: int = typer.Option(..., "--vs", help="Compare to revision")
):
    """Compare two revisions of a task."""
    # ... implementation ...

@app.command()
def tasks_revert(
    task_id: str = typer.Argument(..., help="Task ID"),
    to_revision: int = typer.Option(..., "--to-revision", help="Revision to revert to")
):
    """Revert task to a previous revision."""
    # ... implementation ...

@app.command()
def audit(
    project_id: str = typer.Option(None, "--project", "-p"),
    days: int = typer.Option(7, "--days", "-d"),
    entity_type: str = typer.Option(None, "--type", "-t")
):
    """Get audit log for changes."""
    # ... implementation ...
```

---

## CLI Examples

### Example 1: View History

```bash
# See full history of a task
notion agents tasks history task_123
# Returns: Complete timeline of all changes
```

### Example 2: Recent Changes

```bash
# See recent changes
notion agents tasks log task_123 --limit 5
# Returns: Simplified log of recent changes
```

### Example 3: Compare Revisions

```bash
# See what changed between revisions
notion agents tasks diff task_123 --revision 2 --vs 3
# Returns: Differences between the two revisions
```

### Example 4: Revert Change

```bash
# Undo a mistaken change
notion agents tasks revert task_123 --to-revision 2
# Returns: Task restored to previous state
```

### Example 5: Audit Trail

```bash
# Get audit log for the last week
notion agents audit --project proj_123 --days 7
# Returns: All changes with summary statistics
```

---

## Database Schema Changes

### Change History Database (Optional)

```yaml
Title: "Change History"
Properties:
  Entity ID:
    type: rich_text
  Entity Type:
    type: select
    options:
      - name: "task"
      - name: "idea"
      - name: "incident"
      - name: "work_issue"
  Revision:
    type: number
  Author:
    type: rich_text
  Timestamp:
    type: date
  Changes:
    type: rich_text
  Reason:
    type: rich_text
```

---

## Acceptance Criteria

### Phase 1: History Tracking

- [ ] HistoryTracker class exists
- [ ] Can record entity creation
- [ ] Can record entity updates
- [ ] Can get full history
- [ ] Can get specific revision state
- [ ] Can compare revisions

### Phase 2: Model Integration

- [ ] Tasks track history on update
- [ ] Ideas track history on update
- [ ] Incidents track history on update
- [ ] Work issues track history on update

### Phase 3: CLI Commands

- [ ] `tasks history` works
- [ ] `tasks log` works
- [ ] `tasks diff` works
- [ ] `tasks revert` works
- [ ] `audit` works

---

## Related Issues

- Related to: All entity management issues
- Related to: #042 (Human assignment - for tracking who made changes)

---

## Open Questions

1. Should history be stored in Notion or locally?
   - **Recommendation**: Both - prefer Notion for collaboration, fallback to local
2. How long should we keep history?
   - **Recommendation**: Indefinitely, but consider archival for old data
3. Should we track who viewed entities (not just changed)?
   - **Recommendation**: No, too much noise
4. Should we track history for all properties or just important ones?
   - **Recommendation**: All properties for v1
5. Should we support exporting history?
   - **Recommendation**: Yes, JSON export in Phase 4

---

## Edge Cases to Handle

1. **Concurrent edits**: Last write wins, but both are recorded
2. **Large change sets**: Limit to N changes per revision
3. **Missing author**: Use "Unknown" if author not available
4. **Storage failure**: Gracefully degrade without breaking main operation
5. **Very old history**: Consider archival after X time
6. **Reverting to same state**: No-op with clear message
7. **Binary data**: Skip or store reference only
