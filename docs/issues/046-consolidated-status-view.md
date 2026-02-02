# Issue #046: Consolidated Status View and Dashboard

## Problem Statement

The Agents CLI currently lacks a consolidated view of all work items across entity types. Users must query each entity type separately to get a complete picture of project status, which is inefficient and makes it difficult to see the big picture.

### Current Limitation

```bash
# What users CANNOT do:
notion agents status --project proj_123
# Returns: Consolidated view of all work items

notion agents dashboard
# Returns: Interactive dashboard with key metrics

notion agents overview --version ver_123
# Returns: Overview of all items in a version
```

### Current Workaround (Not User-Friendly)

```bash
# Users have to run multiple commands:
notion agents tasks list --project-id proj_123
notion agents ideas list --project-id proj_123
notion agents work-issues list --project-id proj_123
notion agents incidents list --project-id proj_123

# Then manually aggregate:
# - Count total items
# - Group by status
# - Identify blockers
# - Calculate completion percentage

# This is:
# - Time-consuming (4+ separate commands)
# - Error-prone (manual aggregation)
# - No quick overview
# - Difficult to spot trends or issues
```

### Impact

Without consolidated status view:
- No single source of truth for project status
- Difficult to get project overview quickly
- Must run multiple commands to see full picture
- Harder to identify blockers or risks
- No visibility into team capacity
- Makes project management more difficult
- Difficult to communicate status to stakeholders

### Real-World Use Cases

```bash
# Use case 1: Daily standup - what's happening today?
notion agents status --project proj_123
# Returns: Summary of all work items, what's in progress, what's blocked

# Use case 2: Sprint review - how did we do?
notion agents overview --version ver_123
# Returns: All work completed, in progress, remaining for the sprint

# Use case 3: Team capacity - who's overloaded?
notion agents team status
# Returns: Workload across all team members

# Use case 4: Risk assessment - what's blocking us?
notion agents blockers --project proj_123
# Returns: All blockers (incidents, work issues, dependencies)
```

---

## Proposed Solution

### 1. Project Status Command

```bash
# Get consolidated status for a project
notion agents status --project proj_123
# Returns:
# {
#   "project_id": "proj_123",
#   "project_name": "E-Commerce Platform",
#   "summary": {
#     "total_items": 47,
#     "completed": 28,
#     "in_progress": 12,
#     "backlog": 7,
#     "completion_percentage": 60
#   },
#   "by_type": {
#     "tasks": {"total": 20, "completed": 12, "in_progress": 5, "backlog": 3},
#     "ideas": {"total": 15, "accepted": 5, "proposed": 7, "rejected": 3},
#     "work_issues": {"total": 8, "resolved": 4, "in_progress": 3, "backlog": 1},
#     "incidents": {"total": 4, "resolved": 2, "active": 2}
#   },
#   "high_priority_items": {
#     "critical": [
#       {"id": "task_001", "title": "Fix auth bug", "status": "In Progress"}
#     ],
#     "high": [...]
#   },
#   "blockers": {
#     "active_incidents": 2,
#     "blocking_issues": 1,
#     "blocked_tasks": 3
#   },
#   "team_workload": [
#     {"name": "Alice", "active_tasks": 5, "capacity": 10},
#     {"name": "Bob", "active_tasks": 3, "capacity": 10}
#   ]
# }
```

### 2. Version Overview Command

```bash
# Get overview for a specific version
notion agents overview --version ver_123
# Returns:
# {
#   "version_id": "ver_123",
#   "version_name": "Sprint 42",
#   "summary": {
#     "total_tasks": 15,
#     "completed": 8,
#     "in_progress": 4,
#     "backlog": 3,
#     "completion_percentage": 53
#   },
#   "tasks": [
#     {"id": "task_001", "title": "Feature A", "status": "Completed", "assignee": "Alice"},
#     {"id": "task_002", "title": "Feature B", "status": "In Progress", "assignee": "Bob"}
#   ],
#   "related_incidents": 1,
#   "related_work_issues": 2
# }
```

### 3. Dashboard Command

```bash
# Get overall dashboard
notion agents dashboard
# Returns:
# {
#   "active_projects": 3,
#   "total_work_items": 127,
#   "items_by_status": {
#     "completed": 68,
#     "in_progress": 31,
#     "backlog": 28
#   },
#   "active_incidents": 2,
#   "active_blockers": 5,
#   "team_capacity": {
#     "available": 3,
#     "at_capacity": 2,
#     "overloaded": 1
#   },
#   "recent_activity": [
#     {"type": "task", "action": "completed", "title": "Fix login bug", "time": "2 hours ago"},
#     {"type": "incident", "action": "reported", "title": "API downtime", "time": "4 hours ago"}
#   ],
#   "upcoming_deadlines": [
#     {"version": "ver_123", "name": "Sprint 42", "deadline": "3 days", "completion": "53%"}
#   ]
# }
```

### 4. Team Status Command

```bash
# Get team workload status
notion agents team status
# Returns:
# {
#   "team_members": [
#     {
#       "name": "Alice Chen",
#       "active_tasks": 5,
#       "completed_this_week": 3,
#       "capacity_remaining": 5,
#       "status": "available",
#       "tasks": [
#         {"id": "task_001", "title": "Feature A", "priority": "High", "status": "In Progress"}
#       ]
#     },
#     {
#       "name": "Bob Smith",
#       "active_tasks": 10,
#       "completed_this_week": 1,
#       "capacity_remaining": 0,
#       "status": "at_capacity",
#       "tasks": [...]
#     }
#   ],
#   "summary": {
#     "total_members": 6,
#     "available": 3,
#     "at_capacity": 2,
#     "overloaded": 1
#   }
# }
```

### 5. Blockers Command

```bash
# Get all blockers across the project
notion agents blockers --project proj_123
# Returns:
# {
#   "project_id": "proj_123",
#   "blockers": {
#     "active_incidents": [
#       {"id": "inc_001", "title": "API downtime", "severity": "Critical", "affected_tasks": 5}
#     ],
#     "blocking_work_issues": [
#       {"id": "issue_001", "title": "Auth bug", "severity": "High", "blocked_tasks": 3}
#     ],
#     "task_dependencies": [
#       {"id": "task_005", "title": "Feature C", "waiting_for": "task_004"}
#     ]
#   },
#   "total_blocked_items": 8,
#   "recommendation": "Focus on resolving inc_001 (API downtime) first"
# }
```

---

## Implementation Architecture

### Phase 1: Status View Models (1 day)

```python
# better_notion/plugins/official/agents_sdk/dashboard.py (new file)

from typing import Any
from dataclasses import dataclass
from datetime import datetime, timedelta

@dataclass
class StatusSummary:
    """Summary statistics for status view."""
    total: int
    completed: int
    in_progress: int
    backlog: int
    completion_percentage: float

    def to_dict(self) -> dict:
        return {
            "total_items": self.total,
            "completed": self.completed,
            "in_progress": self.in_progress,
            "backlog": self.backlog,
            "completion_percentage": self.completion_percentage
        }


@dataclass
class TypeBreakdown:
    """Breakdown by entity type."""
    tasks: dict
    ideas: dict
    work_issues: dict
    incidents: dict

    def to_dict(self) -> dict:
        return {
            "tasks": self.tasks,
            "ideas": self.ideas,
            "work_issues": self.work_issues,
            "incidents": self.incidents
        }


class DashboardManager:
    """Manager for consolidated status views."""

    def __init__(self, client: NotionClient, workspace_config: dict):
        self._client = client
        self._workspace_config = workspace_config

    async def get_project_status(self, project_id: str) -> dict:
        """Get consolidated status for a project."""
        from better_notion.plugins.official.agents_sdk.managers import (
            TaskManager, IdeaManager, WorkIssueManager, IncidentManager
        )

        # Get all items for the project
        task_mgr = TaskManager(self._client, self._workspace_config)
        idea_mgr = IdeaManager(self._client, self._workspace_config)
        issue_mgr = WorkIssueManager(self._client, self._workspace_config)
        incident_mgr = IncidentManager(self._client, self._workspace_config)

        tasks = await task_mgr.list(project_id=project_id)
        ideas = await idea_mgr.list(project_id=project_id)
        work_issues = await issue_mgr.list(project_id=project_id)
        incidents = await incident_mgr.list(project_id=project_id)

        # Calculate summary
        total_items = len(tasks) + len(ideas) + len(work_issues) + len(incidents)

        # Count by status
        completed = len([t for t in tasks if t.status == "Completed"])
        in_progress = len([t for t in tasks if t.status == "In Progress"])
        backlog = len([t for t in tasks if t.status in ("Backlog", "Claimed")])

        completion_percentage = (completed / len(tasks) * 100) if tasks else 0

        summary = StatusSummary(
            total=total_items,
            completed=completed,
            in_progress=in_progress,
            backlog=backlog,
            completion_percentage=round(completion_percentage, 1)
        )

        # Type breakdown
        type_breakdown = TypeBreakdown(
            tasks=self._summarize_tasks(tasks),
            ideas=self._summarize_ideas(ideas),
            work_issues=self._summarize_work_issues(work_issues),
            incidents=self._summarize_incidents(incidents)
        )

        # High priority items
        high_priority = self._get_high_priority_items(tasks, work_issues, incidents)

        # Blockers
        blockers = await self._get_blockers(project_id, tasks, work_issues, incidents)

        # Team workload (if human assignment is implemented)
        team_workload = await self._get_team_workload(tasks)

        return {
            "project_id": project_id,
            "summary": summary.to_dict(),
            "by_type": type_breakdown.to_dict(),
            "high_priority_items": high_priority,
            "blockers": blockers,
            "team_workload": team_workload
        }

    def _summarize_tasks(self, tasks: list) -> dict:
        """Summarize tasks by status."""
        total = len(tasks)
        completed = len([t for t in tasks if t.status == "Completed"])
        in_progress = len([t for t in tasks if t.status == "In Progress"])
        backlog = len([t for t in tasks if t.status in ("Backlog", "Claimed")])

        return {
            "total": total,
            "completed": completed,
            "in_progress": in_progress,
            "backlog": backlog
        }

    def _summarize_ideas(self, ideas: list) -> dict:
        """Summarize ideas by status."""
        total = len(ideas)
        accepted = len([i for i in ideas if i.status == "Accepted"])
        proposed = len([i for i in ideas if i.status in ("Proposed", "In Review")])
        rejected = len([i for i in ideas if i.status == "Rejected"])

        return {
            "total": total,
            "accepted": accepted,
            "proposed": proposed,
            "rejected": rejected
        }

    def _summarize_work_issues(self, issues: list) -> dict:
        """Summarize work issues by status."""
        total = len(issues)
        resolved = len([i for i in issues if i.status == "Resolved"])
        in_progress = len([i for i in issues if i.status == "In Progress"])
        backlog = len([i for i in issues if i.status == "Backlog"])

        return {
            "total": total,
            "resolved": resolved,
            "in_progress": in_progress,
            "backlog": backlog
        }

    def _summarize_incidents(self, incidents: list) -> dict:
        """Summarize incidents by status."""
        total = len(incidents)
        resolved = len([i for i in incidents if i.status == "Resolved"])
        active = len([i for i in incidents if i.status == "Active"])

        return {
            "total": total,
            "resolved": resolved,
            "active": active
        }

    def _get_high_priority_items(self, tasks, work_issues, incidents) -> dict:
        """Get high and critical priority items."""
        critical = []
        high = []

        for task in tasks:
            if task.priority == "Critical":
                critical.append({
                    "id": task.id,
                    "title": task.title,
                    "status": task.status,
                    "type": "task"
                })
            elif task.priority == "High":
                high.append({
                    "id": task.id,
                    "title": task.title,
                    "status": task.status,
                    "type": "task"
                })

        for issue in work_issues:
            if issue.severity == "Critical":
                critical.append({
                    "id": issue.id,
                    "title": issue.title,
                    "status": issue.status,
                    "type": "work_issue"
                })
            elif issue.severity == "High":
                high.append({
                    "id": issue.id,
                    "title": issue.title,
                    "status": issue.status,
                    "type": "work_issue"
                })

        for incident in incidents:
            if incident.severity == "Critical":
                critical.append({
                    "id": incident.id,
                    "title": incident.title,
                    "status": incident.status,
                    "type": "incident"
                })
            elif incident.severity == "High":
                high.append({
                    "id": incident.id,
                    "title": incident.title,
                    "status": incident.status,
                    "type": "incident"
                })

        return {"critical": critical[:10], "high": high[:10]}

    async def _get_blockers(self, project_id: str, tasks, work_issues, incidents) -> dict:
        """Get all blockers."""
        active_incidents = [
            {
                "id": i.id,
                "title": i.title,
                "severity": i.severity,
                "status": i.status
            }
            for i in incidents if i.status == "Active"
        ]

        blocking_issues = [
            {
                "id": i.id,
                "title": i.title,
                "severity": i.severity,
                "status": i.status
            }
            for i in work_issues if i.status in ("Backlog", "In Progress")
        ]

        # Count blocked tasks (requires task dependencies feature)
        blocked_tasks_count = 0  # Placeholder

        return {
            "active_incidents": len(active_incidents),
            "blocking_issues": len(blocking_issues),
            "blocked_tasks": blocked_tasks_count,
            "details": {
                "incidents": active_incidents,
                "work_issues": blocking_issues
            }
        }

    async def _get_team_workload(self, tasks) -> list:
        """Get team workload distribution."""
        # Group by assignee
        workload = {}

        for task in tasks:
            assignee = getattr(task, 'assignee', None)
            if not assignee:
                continue

            if assignee not in workload:
                workload[assignee] = {
                    "name": assignee,
                    "active_tasks": 0,
                    "tasks": []
                }

            if task.status in ("Backlog", "Claimed", "In Progress"):
                workload[assignee]["active_tasks"] += 1
                workload[assignee]["tasks"].append({
                    "id": task.id,
                    "title": task.title,
                    "priority": task.priority,
                    "status": task.status
                })

        # Convert to list and add capacity
        result = []
        for name, data in workload.items():
            capacity = 10  # Default max tasks
            result.append({
                "name": name,
                "active_tasks": data["active_tasks"],
                "capacity": capacity,
                "capacity_remaining": capacity - data["active_tasks"],
                "tasks": data["tasks"][:5]  # Limit to 5 tasks per person
            })

        return result

    async def get_version_overview(self, version_id: str) -> dict:
        """Get overview for a version."""
        from better_notion.plugins.official.agents_sdk.managers import TaskManager

        task_mgr = TaskManager(self._client, self._workspace_config)
        tasks = await task_mgr.list(version_id=version_id)

        total = len(tasks)
        completed = len([t for t in tasks if t.status == "Completed"])
        in_progress = len([t for t in tasks if t.status == "In Progress"])
        backlog = len([t for t in tasks if t.status in ("Backlog", "Claimed")])

        completion_percentage = (completed / total * 100) if total else 0

        return {
            "version_id": version_id,
            "summary": {
                "total_tasks": total,
                "completed": completed,
                "in_progress": in_progress,
                "backlog": backlog,
                "completion_percentage": round(completion_percentage, 1)
            },
            "tasks": [
                {
                    "id": t.id,
                    "title": t.title,
                    "status": t.status,
                    "assignee": getattr(t, 'assignee', None),
                    "priority": t.priority
                }
                for t in tasks
            ]
        }
```

### Phase 2: CLI Commands (1 day)

```bash
# better_notion/plugins/official/agents_cli.py

@app.command()
def status(
    project_id: str = typer.Option(..., "--project", "-p", help="Project ID")
):
    """Get consolidated status for a project."""
    # ... implementation ...

@app.command()
def overview(
    version_id: str = typer.Option(..., "--version", "-v", help="Version ID")
):
    """Get overview for a version."""
    # ... implementation ...

@app.command()
def dashboard():
    """Get overall dashboard."""
    # ... implementation ...

@app.command()
def team_status_cmd(
    project_id: Optional[str] = typer.Option(None, "--project", "-p")
):
    """Get team workload status."""
    # ... implementation ...

@app.command()
def blockers(
    project_id: str = typer.Option(..., "--project", "-p", help="Project ID")
):
    """Get all blockers for a project."""
    # ... implementation ...
```

### Phase 3: Integration (0.5 day)

Add these commands to `agents.py` wrapper.

---

## CLI Examples

### Example 1: Project Status

```bash
# Daily standup - what's the project status?
notion agents status --project proj_123
# Returns: Comprehensive view of all work items, blockers, team workload
```

### Example 2: Sprint Overview

```bash
# Sprint review - how did version 1.2 go?
notion agents overview --version ver_123
# Returns: All tasks for the sprint with completion metrics
```

### Example 3: Team Status

```bash
# Check if anyone is overloaded
notion agents team status
# Returns: Workload across all team members
```

### Example 4: Blockers

```bash
# What's blocking us?
notion agents blockers --project proj_123
# Returns: All active incidents, blocking issues, and blocked tasks
```

---

## Acceptance Criteria

### Phase 1: Status View Models

- [ ] `DashboardManager` class exists
- [ ] `get_project_status()` method works
- [ ] `get_version_overview()` method works
- [ ] Status summary calculations are accurate
- [ ] Type breakdowns are correct
- [ ] High priority items are identified

### Phase 2: CLI Commands

- [ ] `notion agents status --project <id>` works
- [ ] `notion agents overview --version <id>` works
- [ ] `notion agents dashboard` works
- [ ] `notion agents team status` works
- [ ] `notion agents blockers --project <id>` works

### Phase 3: Data Accuracy

- [ ] Completion percentages are calculated correctly
- [ ] Team workload is accurate
- [ ] Blockers are identified correctly
- [ ] High priority items are listed correctly

---

## Related Issues

- Related to: #042 (Human assignment - for team workload)
- Related to: #040 (Task dependencies - for blocked tasks)
- Related to: #041 (Cross-entity relations - for related incidents)
- Enhances: All entity commands

---

## Migration Path

No migration needed - this is a new feature.

---

## Rollout Plan

1. **Phase 1**: Implement project status view
2. **Phase 2**: Implement version overview
3. **Phase 3**: Implement dashboard
4. **Phase 4**: Implement team status
5. **Phase 5**: Implement blockers view

---

## Open Questions

1. Should dashboard be real-time or cached?
   - **Recommendation**: Real-time for v1, consider caching for v2 if performance is an issue
2. Should we support historical data (trends over time)?
   - **Recommendation**: Not in v1, consider adding in v2
3. Should we support customizable dashboard layouts?
   - **Recommendation**: Not in v1, keep it simple with fixed layout
4. Should we support exporting status to reports?
   - **Recommendation**: Add in Phase 4 (JSON output is already supported)
5. Should we integrate with external dashboards (Grafana, etc.)?
   - **Recommendation**: Not in v1, consider in v2

---

## Edge Cases to Handle

1. **Project with no items**: Return empty summary with clear message
2. **Version with no tasks**: Return empty overview
3. **No team members configured**: Return empty team workload
4. **Large projects** (1000+ items): Consider pagination or limits
5. **Missing data** (e.g., no assignee information): Handle gracefully
6. **Projects with mixed entity types**: Aggregate correctly
7. **Active incidents with no affected tasks**: Still show in blockers
