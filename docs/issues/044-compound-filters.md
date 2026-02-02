# Issue #044: Compound Filters for Complex Queries

## Problem Statement

The Agents CLI currently only supports single-property filtering, making it impossible to perform complex queries that require combining multiple conditions. This severely limits the ability to find specific entities in real-world scenarios.

### Current Limitation

```bash
# What users CANNOT do:
# Filter by multiple properties simultaneously
notion agents tasks list --status In Progress --priority High
notion agents tasks list --assignee "Alice" --status "In Progress"
notion agents ideas list --category Feature --effort Medium --status Accepted
notion agents incidents list --severity Critical --status Active
```

### Current Workaround (Not User-Friendly)

```bash
# Users have to:
# 1. List all tasks
notion agents tasks list --project-id proj_123
# Returns: 50 tasks

# 2. Manually filter through the output
# (Users must grep/parse JSON themselves)

# This is:
# - Slow (fetches all data)
# - Error-prone (manual filtering)
# - Not scalable (large datasets)
# - Poor UX (requires scripting)
```

### Impact

Without compound filters:
- Cannot find specific tasks matching multiple criteria
- Must manually filter results (slow and error-prone)
- Cannot express complex queries naturally
- Makes the CLI less useful for real-world workflows
- Forces users to write scripts or use external tools
- Reduces productivity for common queries

### Real-World Use Cases

```bash
# Use case 1: Find high-priority work in progress
notion agents tasks list --status "In Progress" --priority High

# Use case 2: Find unassigned high-priority tasks
notion agents tasks list --unassigned --priority Critical

# Use case 3: Find all features accepted this week
notion agents ideas list --category Feature --status Accepted --project proj_123

# Use case 4: Find critical incidents that are still active
notion agents incidents list --severity Critical --status Active

# Use case 5: Find Alice's in-progress tasks
notion agents tasks list --assignee "Alice Chen" --status "In Progress"

# Use case 6: Find bugs blocking me
notion agents work-issues list --type Bug --severity High --status "In Progress"
```

---

## Proposed Solution

### 1. CLI Interface for Compound Filters

```bash
# Filter by multiple properties (AND logic by default)
notion agents tasks list --status "In Progress" --priority High
# Returns: All tasks that are BOTH "In Progress" AND High priority

notion agents tasks list --assignee "Alice" --status "In Progress" --project proj_123
# Returns: Alice's in-progress tasks in project proj_123

# Mix of filters
notion agents ideas list \
  --category Feature \
  --effort Medium \
  --status Accepted \
  --project proj_123
# Returns: Medium-sized feature ideas that are accepted in project proj_123
```

### 2. Advanced Filter Combinations

```bash
# Unassigned + high priority
notion agents tasks list --unassigned --priority Critical
# Equivalent to: Assignee is empty AND Priority is Critical

# Date range filters
notion agents tasks list --status Completed --completed-after "2026-01-01"
notion agents incidents list --created-before "2026-02-01"

# Negation filters (NOT logic)
notion agents tasks list --status "In Progress" --priority-not Low
# Returns: In Progress tasks that are NOT Low priority

# Or filters (for status values)
notion agents tasks list --status-any "Backlog,Claimed"
# Returns: Tasks that are Backlog OR Claimed
```

### 3. Filter Syntax Guidelines

```bash
# Rule 1: Multiple filters use AND logic (intersection)
--filter1 value1 --filter2 value2  → filter1=value1 AND filter2=value2

# Rule 2: Same filter multiple times uses OR logic (union)
--status Backlog --status Claimed  → status=Backlog OR status=Claimed

# Rule 3: Use explicit --*-any for OR logic
--status-any "Backlog,Claimed"      → status=Backlog OR status=Claimed

# Rule 4: Use --*-not for negation
--priority-not Low                  → priority != Low

# Rule 5: Special flags combine with filters
--unassigned                        → assignee is empty AND [other filters]
```

---

## Implementation Architecture

### Phase 1: Filter Building System (1 day)

```python
# better_notion/plugins/official/agents_sdk/filters.py (new file)

from typing import Any

class FilterBuilder:
    """Build compound filters for Notion API queries."""

    def __init__(self):
        self._filters: list[dict[str, Any]] = []
        self._or_groups: list[list[dict[str, Any]]] = []

    def add_filter(self, property_name: str, condition: dict) -> "FilterBuilder":
        """Add a single filter condition (AND logic)."""
        self._filters.append({
            "property": property_name,
            **condition
        })
        return self

    def add_text_filter(self, property_name: str, value: str) -> "FilterBuilder":
        """Add a text equality filter."""
        return self.add_filter(property_name, {"text": {"equals": value}})

    def add_select_filter(self, property_name: str, value: str) -> "FilterBuilder":
        """Add a select equality filter."""
        return self.add_filter(property_name, {"select": {"equals": value}})

    def add_multi_select_filter(self, property_name: str, value: str) -> "FilterBuilder":
        """Add a multi-select contains filter."""
        return self.add_filter(property_name, {"multi_select": {"contains": value}})

    def add_relation_filter(self, property_name: str, value: str) -> "FilterBuilder":
        """Add a relation contains filter."""
        return self.add_filter(property_name, {"relation": {"contains": value}})

    def add_date_filter(
        self,
        property_name: str,
        on_or_before: str | None = None,
        on_or_after: str | None = None,
        is_empty: bool | None = None
    ) -> "FilterBuilder":
        """Add a date filter."""
        condition: dict[str, Any] = {"date": {}}

        if on_or_before:
            condition["date"]["on_or_before"] = on_or_before
        if on_or_after:
            condition["date"]["on_or_after"] = on_or_after
        if is_empty is not None:
            condition["date"]["is_empty"] = is_empty

        return self.add_filter(property_name, condition)

    def add_empty_filter(self, property_name: str, is_empty: bool = True) -> "FilterBuilder":
        """Add an 'is empty' or 'is not empty' filter."""
        # Determine property type (simplified approach)
        # In production, you'd check the schema
        return self.add_filter(property_name, {
            "select": {"is_empty": is_empty}
        })

    def add_not_filter(self, property_name: str, value: str) -> "FilterBuilder":
        """Add a NOT filter (negation)."""
        return self.add_filter(property_name, {
            "select": {"does_not_equal": value}
        })

    def add_or_filter(self, property_name: str, values: list[str]) -> "FilterBuilder":
        """Add an OR filter (multiple values for same property)."""
        or_conditions = [
            {"property": property_name, "select": {"equals": value}}
            for value in values
        ]
        self._or_groups.append(or_conditions)
        return self

    def build(self) -> dict[str, Any] | None:
        """Build the final filter for the Notion API."""
        # No filters
        if not self._filters and not self._or_groups:
            return None

        # Only AND filters
        if not self._or_groups:
            if len(self._filters) == 1:
                return self._filters[0]
            return {"and": self._filters}

        # Combine AND and OR filters
        result = []
        if self._filters:
            if len(self._filters) == 1:
                result.append(self._filters[0])
            else:
                result.append({"and": self._filters})

        for or_group in self._or_groups:
            if len(or_group) == 1:
                result.append(or_group[0])
            else:
                result.append({"or": or_group})

        # If only one group, return it directly
        if len(result) == 1:
            return result[0]

        # Otherwise, wrap in AND
        return {"and": result}


# Convenience functions
def build_task_filters(
    status: str | None = None,
    status_any: str | None = None,
    priority: str | None = None,
    priority_not: str | None = None,
    assignee: str | None = None,
    unassigned: bool = False,
    project_id: str | None = None,
    version_id: str | None = None,
    task_type: str | None = None
) -> dict[str, Any] | None:
    """Build compound filters for task queries."""
    builder = FilterBuilder()

    if status:
        builder.add_select_filter("Status", status)

    if status_any:
        values = [v.strip() for v in status_any.split(",")]
        builder.add_or_filter("Status", values)

    if priority:
        builder.add_select_filter("Priority", priority)

    if priority_not:
        builder.add_not_filter("Priority", priority_not)

    if assignee:
        builder.add_select_filter("Assignee", assignee)

    if unassigned:
        builder.add_empty_filter("Assignee", is_empty=True)

    if project_id:
        builder.add_relation_filter("Project", project_id)

    if version_id:
        builder.add_relation_filter("Version", version_id)

    if task_type:
        builder.add_select_filter("Type", task_type)

    return builder.build()


def build_idea_filters(
    status: str | None = None,
    category: str | None = None,
    effort: str | None = None,
    project_id: str | None = None
) -> dict[str, Any] | None:
    """Build compound filters for idea queries."""
    builder = FilterBuilder()

    if status:
        builder.add_select_filter("Status", status)

    if category:
        builder.add_select_filter("Category", category)

    if effort:
        builder.add_select_filter("Effort Estimate", effort)

    if project_id:
        builder.add_relation_filter("Project", project_id)

    return builder.build()


def build_incident_filters(
    status: str | None = None,
    severity: str | None = None,
    type_: str | None = None,
    project_id: str | None = None
) -> dict[str, Any] | None:
    """Build compound filters for incident queries."""
    builder = FilterBuilder()

    if status:
        builder.add_select_filter("Status", status)

    if severity:
        builder.add_select_filter("Severity", severity)

    if type_:
        builder.add_select_filter("Type", type_)

    if project_id:
        builder.add_relation_filter("Project", project_id)

    return builder.build()


def build_work_issue_filters(
    status: str | None = None,
    type_: str | None = None,
    severity: str | None = None,
    project_id: str | None = None
) -> dict[str, Any] | None:
    """Build compound filters for work issue queries."""
    builder = FilterBuilder()

    if status:
        builder.add_select_filter("Status", status)

    if type_:
        builder.add_select_filter("Type", type_)

    if severity:
        builder.add_select_filter("Severity", severity)

    if project_id:
        builder.add_relation_filter("Project", project_id)

    return builder.build()
```

### Phase 2: Manager Updates (0.5 day)

```python
# better_notion/plugins/official/agents_sdk/managers.py

class TaskManager:
    # ... existing code ...

    async def list(
        self,
        status: str | None = None,
        status_any: str | None = None,
        priority: str | None = None,
        priority_not: str | None = None,
        assignee: str | None = None,
        unassigned: bool = False,
        project_id: str | None = None,
        version_id: str | None = None,
        task_type: str | None = None
    ) -> list:
        """List tasks with compound filters."""
        from better_notion.plugins.official.agents_sdk.models import Task
        from better_notion.plugins.official.agents_sdk.filters import build_task_filters

        database_id = self._get_database_id("Tasks")
        if not database_id:
            return []

        filters = build_task_filters(
            status=status,
            status_any=status_any,
            priority=priority,
            priority_not=priority_not,
            assignee=assignee,
            unassigned=unassigned,
            project_id=project_id,
            version_id=version_id,
            task_type=task_type
        )

        query: dict[str, Any] = {}
        if filters:
            query["filter"] = filters

        response = await self._client._api._request(
            "POST",
            f"/databases/{database_id}/query",
            json=query
        )

        return [
            Task(self._client, page_data)
            for page_data in response.get("results", [])
        ]


class IdeaManager:
    # ... existing code ...

    async def list(
        self,
        status: str | None = None,
        category: str | None = None,
        effort: str | None = None,
        project_id: str | None = None
    ) -> list:
        """List ideas with compound filters."""
        from better_notion.plugins.official.agents_sdk.models import Idea
        from better_notion.plugins.official.agents_sdk.filters import build_idea_filters

        database_id = self._get_database_id("Ideas")
        if not database_id:
            return []

        filters = build_idea_filters(
            status=status,
            category=category,
            effort=effort,
            project_id=project_id
        )

        query: dict[str, Any] = {}
        if filters:
            query["filter"] = filters

        response = await self._client._api._request(
            "POST",
            f"/databases/{database_id}/query",
            json=query
        )

        return [
            Idea(self._client, page_data)
            for page_data in response.get("results", [])
        ]
```

### Phase 3: CLI Command Updates (1 day)

```bash
# better_notion/plugins/official/agents_cli.py

@app.command()
def tasks_list(
    project_id: Optional[str] = typer.Option(None, "--project-id", "-p"),
    version_id: Optional[str] = typer.Option(None, "--version-id", "-v"),
    status: Optional[str] = typer.Option(None, "--status", "-s"),
    status_any: Optional[str] = typer.Option(None, "--status-any"),
    priority: Optional[str] = typer.Option(None, "--priority"),
    priority_not: Optional[str] = typer.Option(None, "--priority-not"),
    assignee: Optional[str] = typer.Option(None, "--assignee", "-a"),
    unassigned: bool = typer.Option(False, "--unassigned", "-u"),
    type_: Optional[str] = typer.Option(None, "--type", "-t")
):
    """List tasks with compound filters."""
    # ... implementation using updated manager ...

@app.command()
def ideas_list(
    project_id: Optional[str] = typer.Option(None, "--project-id", "-p"),
    status: Optional[str] = typer.Option(None, "--status", "-s"),
    category: Optional[str] = typer.Option(None, "--category", "-c"),
    effort: Optional[str] = typer.Option(None, "--effort", "-e")
):
    """List ideas with compound filters."""
    # ... implementation using updated manager ...

@app.command()
def incidents_list(
    project_id: Optional[str] = typer.Option(None, "--project-id", "-p"),
    status: Optional[str] = typer.Option(None, "--status", "-s"),
    severity: Optional[str] = typer.Option(None, "--severity"),
    type_: Optional[str] = typer.Option(None, "--type", "-t")
):
    """List incidents with compound filters."""
    # ... implementation using updated manager ...

@app.command()
def work_issues_list(
    project_id: Optional[str] = typer.Option(None, "--project-id", "-p"),
    status: Optional[str] = typer.Option(None, "--status", "-s"),
    type_: Optional[str] = typer.Option(None, "--type", "-t"),
    severity: Optional[str] = typer.Option(None, "--severity")
):
    """List work issues with compound filters."""
    # ... implementation using updated manager ...
```

---

## CLI Examples

### Example 1: Multi-Property Task Filters

```bash
# Find high-priority tasks in progress
notion agents tasks list --status "In Progress" --priority High
# Returns:
# {
#   "tasks": [
#     {"id": "task_001", "title": "Fix auth bug", "status": "In Progress", "priority": "High"},
#     {"id": "task_002", "title": "Security patch", "status": "In Progress", "priority": "High"}
#   ]
# }

# Find Alice's in-progress tasks
notion agents tasks list --assignee "Alice Chen" --status "In Progress"
# Returns: Alice's tasks that are in progress

# Find unassigned critical tasks
notion agents tasks list --unassigned --priority Critical
# Returns: Critical tasks that need assignment
```

### Example 2: Status OR Filters

```bash
# Find backlog or claimed tasks
notion agents tasks list --status-any "Backlog,Claimed"
# Returns:
# {
#   "tasks": [
#     {"id": "task_001", "status": "Backlog"},
#     {"id": "task_002", "status": "Claimed"}
#   ]
# }

# Find high or critical priority tasks
notion agents tasks list --status "In Progress" --priority-any "High,Critical"
# Returns: In-progress tasks with high or critical priority
```

### Example 3: Negation Filters

```bash
# Find in-progress tasks that are NOT low priority
notion agents tasks list --status "In Progress" --priority-not Low
# Returns: Medium/High/Critical tasks in progress

# Find ideas that are NOT improvements
notion agents ideas list --status Accepted --category-not Improvement
# Returns: Features or bugs that are accepted
```

### Example 4: Complex Multi-Property Filters

```bash
# Find specific type of work issues
notion agents work-issues list \
  --type Bug \
  --severity High \
  --status "In Progress" \
  --project-id proj_123
# Returns: High-severity bugs in progress in project proj_123

# Find feature ideas ready to implement
notion agents ideas list \
  --category Feature \
  --effort Medium \
  --status Accepted \
  --project-id proj_123
# Returns: Medium-sized feature ideas ready for conversion
```

### Example 5: Combining with New Features

```bash
# Find tasks ready for me to start (dependencies + compound filters)
notion agents tasks list --status Backlog --assignee "Alice Chen" --ready
# Returns: Alice's backlog tasks that have all dependencies completed

# Find critical incidents caused by specific work issue
notion agents incidents list --severity Critical --caused-by issue_456
# Returns: Critical incidents caused by issue_456
```

---

## Acceptance Criteria

### Phase 1: Filter Building System

- [ ] `FilterBuilder` class exists
- [ ] `FilterBuilder.add_filter()` works
- [ ] `FilterBuilder.add_select_filter()` works
- [ ] `FilterBuilder.add_relation_filter()` works
- [ ] `FilterBuilder.add_empty_filter()` works
- [ ] `FilterBuilder.add_not_filter()` works
- [ ] `FilterBuilder.add_or_filter()` works
- [ ] `FilterBuilder.build()` returns valid Notion API filter
- [ ] Convenience functions exist for all entity types

### Phase 2: Manager Updates

- [ ] TaskManager.list() accepts multiple filter parameters
- [ ] IdeaManager.list() accepts multiple filter parameters
- [ ] IncidentManager.list() accepts multiple filter parameters
- [ ] WorkIssueManager.list() accepts multiple filter parameters
- [ ] All managers use `FilterBuilder` for compound filters

### Phase 3: CLI Commands

- [ ] `tasks list --status X --priority Y` works
- [ ] `tasks list --assignee X --status Y` works
- [ ] `tasks list --unassigned --priority X` works
- [ ] `tasks list --status-any "X,Y"` works
- [ ] `tasks list --priority-not Low` works
- [ ] `ideas list --category X --effort Y --status Z` works
- [ ] `incidents list --severity X --status Y` works
- [ ] `work-issues list --type X --severity Y` works

### Phase 4: Integration Testing

- [ ] AND filters work correctly (intersection)
- [ ] OR filters work correctly (union)
- [ ] NOT filters work correctly (exclusion)
- [ ] Empty filters work correctly (null checks)
- [ ] Compound filters with 3+ conditions work
- [ ] Filters combine correctly with project/version relations

---

## Related Issues

- Enables: #040 (Task dependencies - for `--ready` filter)
- Enables: #041 (Cross-entity relations - for `--caused-by`, `--blocks` filters)
- Enables: #042 (Human assignment - for `--assignee` filters)
- Related to: #045 (Full-text search - for text-based filtering)

---

## Migration Path

### For Existing Workspaces

No migration needed - this is a pure enhancement to existing functionality.

### For Code

1. Create `filters.py` with `FilterBuilder` class
2. Update all manager list() methods to accept multiple filter parameters
3. Update all CLI list commands to accept multiple filter options
4. Update tests to cover compound filter scenarios

---

## Rollout Plan

1. **Phase 1**: Implement FilterBuilder system
2. **Phase 2**: Update managers to use compound filters
3. **Phase 3**: Update CLI commands with new options
4. **Phase 4**: Add comprehensive testing
5. **Phase 5**: Document filter syntax and examples

---

## Open Questions

1. Should we support date range filters for created/updated dates?
   - **Recommendation**: Yes, add `--created-after`, `--created-before`, `--completed-after` in Phase 4
2. Should we support regex or wildcard text matching?
   - **Recommendation**: Not in v1, Notion API doesn't support it natively
3. Should we add a `--filter` option for custom filter expressions?
   - **Recommendation**: Not in v1, keep it simple with named options
4. How should we handle case sensitivity in filters?
   - **Recommendation**: Case-sensitive (Notion API default), document this clearly
5. Should we support sorting with filters?
   - **Recommendation**: Add in Phase 4 (separate issue for sorting/pagination)

---

## Edge Cases to Handle

1. **Conflicting filters**: `--status Backlog --status-any "Claimed,In Progress"`
   - Should validate and warn about conflicts
2. **Invalid filter values**: `--priority InvalidValue`
   - Should validate against schema and fail gracefully
3. **Empty results**: Return empty array with clear message
4. **Too many filters**: Notion API has limits on filter complexity
   - Should document limits and fail gracefully
5. **Property type mismatch**: Applying text filter to date property
   - Should validate property types and fail with clear error
6. **Combining --unassigned with --assignee**: Mutually exclusive
   - Should detect and error with clear message
