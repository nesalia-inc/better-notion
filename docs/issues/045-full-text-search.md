# Issue #045: Full-Text Search Across Entities

## Problem Statement

The Agents CLI currently lacks full-text search functionality, making it impossible to find entities by their content (title, description, etc.). Users can only filter by exact property values, which is insufficient for real-world usage.

### Current Limitation

```bash
# What users CANNOT do:
notion agents tasks search "authentication"
notion agents ideas search "dark mode"
notion agents work-issues search "memory leak"
notion agents incidents search "database"
```

### Current Workaround (Not User-Friendly)

```bash
# Users have to:
# 1. List all tasks
notion agents tasks list
# Returns: 100+ tasks

# 2. Grep through the output manually
notion agents tasks list | grep -i "authentication"

# This is:
# - Inefficient (fetches all data)
# - Slow (requires manual filtering)
# - Doesn't search descriptions, only displayed output
# - No relevance ranking
# - Can't search across multiple entity types
```

### Impact

Without full-text search:
- Cannot find tasks/ideas by keywords
- Must remember exact titles or IDs
- Difficult to discover related work
- Makes the CLI much less usable for large projects
- Forces users to use Notion web UI for search
- Reduces productivity significantly

### Real-World Use Cases

```bash
# Use case 1: Find all tasks related to "authentication"
notion agents tasks search "authentication"
# Returns: Tasks with "authentication" in title or description

# Use case 2: Find ideas mentioning "performance"
notion agents ideas search "performance"

# Use case 3: Find incidents about "database"
notion agents incidents search "database"

# Use case 4: Find work issues mentioning "memory leak"
notion agents work-issues search "memory leak"

# Use case 5: Search across all entity types
notion agents search "API" --all-types
# Returns: Tasks, ideas, incidents, work-issues mentioning "API"
```

---

## Proposed Solution

### 1. CLI Interface for Full-Text Search

```bash
# Search within a single entity type
notion agents tasks search "authentication"
# Returns:
# {
#   "results": [
#     {
#       "id": "task_001",
#       "title": "Fix authentication bug",
#       "status": "In Progress",
#       "relevance": "high",
#       "matched_in": ["title"]
#     },
#     {
#       "id": "task_002",
#       "title": "Update user profile",
#       "description": "Add OAuth2 authentication to user profile page",
#       "status": "Backlog",
#       "relevance": "medium",
#       "matched_in": ["description"]
#     }
#   ],
#   "total": 2
# }

# Search with filters
notion agents tasks search "bug" --status "In Progress" --priority High
# Returns: High-priority in-progress tasks mentioning "bug"

# Search across all entity types
notion agents search "authentication" --all-types
# Returns:
# {
#   "results": {
#     "tasks": [...],
#     "ideas": [...],
#     "incidents": [...],
#     "work_issues": [...]
#   },
#   "total": 15
# }

# Search with limit
notion agents tasks search "api" --limit 10
# Returns: Top 10 most relevant results
```

### 2. Search Features

```bash
# Case-insensitive search
notion agents tasks search "AUTHENTICATION"
# Same as: "authentication"

# Partial word matching
notion agents tasks search "auth"
# Matches: "authentication", "authorization", "auth"

# Phrase search
notion agents tasks search '"database connection"'
# Matches: Exact phrase "database connection"

# Boolean operators
notion agents tasks search "authentication AND oauth"
# Matches: Both "authentication" and "oauth"

notion agents tasks search "authentication OR authorization"
# Matches: Either "authentication" or "authorization"

notion agents tasks search "authentication NOT token"
# Matches: "authentication" but not "token"
```

### 3. Search Scope

```bash
# Search in title only
notion agents tasks search "bug" --in title

# Search in description only
notion agents tasks search "bug" --in description

# Search in both (default)
notion agents tasks search "bug" --in title,description
```

---

## Implementation Architecture

### Phase 1: Search Implementation (1 day)

```python
# better_notion/plugins/official/agents_sdk/search.py (new file)

from typing import Any
from better_notion.plugins.official.agents_sdk.models import (
    Task, Idea, Incident, WorkIssue
)

class SearchResult:
    """Represents a search result."""

    def __init__(
        self,
        entity: Any,
        relevance: str,
        matched_in: list[str]
    ):
        self.entity = entity
        self.relevance = relevance  # "high", "medium", "low"
        self.matched_in = matched_in  # ["title", "description", etc.]

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "id": self.entity.id,
            "title": self.entity.title,
            "status": getattr(self.entity, "status", None),
            "relevance": self.relevance,
            "matched_in": self.matched_in,
            **self._entity_specific_fields()
        }

    def _entity_specific_fields(self) -> dict:
        """Get entity-specific fields for output."""
        result = {}

        if isinstance(self.entity, Task):
            result["priority"] = self.entity.priority
            result["type"] = self.entity.task_type
        elif isinstance(self.entity, Idea):
            result["category"] = self.entity.category
            result["effort"] = self.entity.effort_estimate
        elif isinstance(self.entity, Incident):
            result["severity"] = self.entity.severity
            result["incident_type"] = self.entity.incident_type
        elif isinstance(self.entity, WorkIssue):
            result["severity"] = self.entity.severity
            result["issue_type"] = self.entity.issue_type

        return result


class TextSearcher:
    """Full-text search implementation."""

    def __init__(self, client):
        self._client = client

    def _calculate_relevance(
        self,
        query: str,
        title: str,
        description: str | None = None
    ) -> tuple[str, list[str]]:
        """
        Calculate relevance score and matched fields.

        Returns: (relevance_level, matched_fields)
        """
        query_lower = query.lower()
        title_lower = title.lower()
        matched_in = []

        # Check title
        title_match = query_lower in title_lower
        if title_match:
            matched_in.append("title")

        # Check description
        desc_match = False
        if description:
            desc_lower = description.lower()
            desc_match = query_lower in desc_lower
            if desc_match:
                matched_in.append("description")

        # Calculate relevance
        if not matched_in:
            return "none", []

        if title_match and desc_match:
            return "high", matched_in
        elif title_match:
            # Exact phrase match in title = high relevance
            if query_lower == title_lower or query_lower in title_lower.split():
                return "high", matched_in
            return "medium", matched_in
        elif desc_match:
            return "low", matched_in

        return "none", []

    async def search_tasks(
        self,
        query: str,
        database_id: str,
        filters: dict | None = None,
        limit: int = 50
    ) -> list[SearchResult]:
        """Search tasks by text query."""
        # Get all tasks (with optional filters)
        query_obj: dict[str, Any] = {}
        if filters:
            query_obj["filter"] = filters

        response = await self._client._api._request(
            "POST",
            f"/databases/{database_id}/query",
            json=query_obj
        )

        results = []
        for page_data in response.get("results", []):
            task = Task(self._client, page_data)

            # Calculate relevance
            relevance, matched_in = self._calculate_relevance(
                query,
                task.title,
                getattr(task, 'description', None)
            )

            if relevance != "none":
                results.append(SearchResult(task, relevance, matched_in))

        # Sort by relevance and limit
        results.sort(key=lambda r: (
            {"high": 0, "medium": 1, "low": 2}[r.relevance],
            r.entity.title
        ))

        return results[:limit]

    async def search_ideas(
        self,
        query: str,
        database_id: str,
        filters: dict | None = None,
        limit: int = 50
    ) -> list[SearchResult]:
        """Search ideas by text query."""
        query_obj: dict[str, Any] = {}
        if filters:
            query_obj["filter"] = filters

        response = await self._client._api._request(
            "POST",
            f"/databases/{database_id}/query",
            json=query_obj
        )

        results = []
        for page_data in response.get("results", []):
            idea = Idea(self._client, page_data)

            relevance, matched_in = self._calculate_relevance(
                query,
                idea.title,
                getattr(idea, 'description', None)
            )

            if relevance != "none":
                results.append(SearchResult(idea, relevance, matched_in))

        results.sort(key=lambda r: (
            {"high": 0, "medium": 1, "low": 2}[r.relevance],
            r.entity.title
        ))

        return results[:limit]

    async def search_incidents(
        self,
        query: str,
        database_id: str,
        filters: dict | None = None,
        limit: int = 50
    ) -> list[SearchResult]:
        """Search incidents by text query."""
        query_obj: dict[str, Any] = {}
        if filters:
            query_obj["filter"] = filters

        response = await self._client._api._request(
            "POST",
            f"/databases/{database_id}/query",
            json=query_obj
        )

        results = []
        for page_data in response.get("results", []):
            incident = Incident(self._client, page_data)

            relevance, matched_in = self._calculate_relevance(
                query,
                incident.title,
                getattr(incident, 'description', None)
            )

            if relevance != "none":
                results.append(SearchResult(incident, relevance, matched_in))

        results.sort(key=lambda r: (
            {"high": 0, "medium": 1, "low": 2}[r.relevance],
            r.entity.title
        ))

        return results[:limit]

    async def search_work_issues(
        self,
        query: str,
        database_id: str,
        filters: dict | None = None,
        limit: int = 50
    ) -> list[SearchResult]:
        """Search work issues by text query."""
        query_obj: dict[str, Any] = {}
        if filters:
            query_obj["filter"] = filters

        response = await self._client._api._request(
            "POST",
            f"/databases/{database_id}/query",
            json=query_obj
        )

        results = []
        for page_data in response.get("results", []):
            issue = WorkIssue(self._client, page_data)

            relevance, matched_in = self._calculate_relevance(
                query,
                issue.title,
                getattr(issue, 'description', None)
            )

            if relevance != "none":
                results.append(SearchResult(issue, relevance, matched_in))

        results.sort(key=lambda r: (
            {"high": 0, "medium": 1, "low": 2}[r.relevance],
            r.entity.title
        ))

        return results[:limit]

    async def search_all(
        self,
        query: str,
        workspace_config: dict,
        limit_per_type: int = 10
    ) -> dict:
        """Search across all entity types."""
        results = {
            "tasks": [],
            "ideas": [],
            "incidents": [],
            "work_issues": []
        }

        # Search tasks
        tasks_db = workspace_config.get("Tasks")
        if tasks_db:
            task_results = await self.search_tasks(query, tasks_db, limit=limit_per_type)
            results["tasks"] = [r.to_dict() for r in task_results]

        # Search ideas
        ideas_db = workspace_config.get("Ideas")
        if ideas_db:
            idea_results = await self.search_ideas(query, ideas_db, limit=limit_per_type)
            results["ideas"] = [r.to_dict() for r in idea_results]

        # Search incidents
        incidents_db = workspace_config.get("Incidents")
        if incidents_db:
            incident_results = await self.search_incidents(query, incidents_db, limit=limit_per_type)
            results["incidents"] = [r.to_dict() for r in incident_results]

        # Search work issues
        issues_db = workspace_config.get("Work_issues")
        if issues_db:
            issue_results = await self.search_work_issues(query, issues_db, limit=limit_per_type)
            results["work_issues"] = [r.to_dict() for r in issue_results]

        total = sum(len(v) for v in results.values())
        results["total"] = total

        return results
```

### Phase 2: Manager Updates (0.5 day)

```python
# better_notion/plugins/official/agents_sdk/managers.py

class TaskManager:
    # ... existing code ...

    async def search(
        self,
        query: str,
        status: str | None = None,
        priority: str | None = None,
        assignee: str | None = None,
        project_id: str | None = None,
        version_id: str | None = None,
        limit: int = 50
    ) -> list[dict]:
        """Search tasks by text query with optional filters."""
        from better_notion.plugins.official.agents_sdk.filters import build_task_filters
        from better_notion.plugins.official.agents_sdk.search import TextSearcher

        database_id = self._get_database_id("Tasks")
        if not database_id:
            return []

        # Build filters
        filters = build_task_filters(
            status=status,
            priority=priority,
            assignee=assignee,
            project_id=project_id,
            version_id=version_id
        )

        # Search
        searcher = TextSearcher(self._client)
        results = await searcher.search_tasks(query, database_id, filters, limit)

        return [r.to_dict() for r in results]


class IdeaManager:
    # ... existing code ...

    async def search(
        self,
        query: str,
        status: str | None = None,
        category: str | None = None,
        project_id: str | None = None,
        limit: int = 50
    ) -> list[dict]:
        """Search ideas by text query with optional filters."""
        from better_notion.plugins.official.agents_sdk.filters import build_idea_filters
        from better_notion.plugins.official.agents_sdk.search import TextSearcher

        database_id = self._get_database_id("Ideas")
        if not database_id:
            return []

        filters = build_idea_filters(
            status=status,
            category=category,
            project_id=project_id
        )

        searcher = TextSearcher(self._client)
        results = await searcher.search_ideas(query, database_id, filters, limit)

        return [r.to_dict() for r in results]
```

### Phase 3: CLI Commands (1 day)

```bash
# better_notion/plugins/official/agents_cli.py

@app.command()
def tasks_search(
    query: str = typer.Argument(..., help="Search query"),
    status: Optional[str] = typer.Option(None, "--status", "-s"),
    priority: Optional[str] = typer.Option(None, "--priority", "-p"),
    assignee: Optional[str] = typer.Option(None, "--assignee", "-a"),
    project_id: Optional[str] = typer.Option(None, "--project-id"),
    version_id: Optional[str] = typer.Option(None, "--version-id"),
    limit: int = typer.Option(50, "--limit", "-n")
):
    """Search tasks by text content."""
    # ... implementation ...

@app.command()
def ideas_search(
    query: str = typer.Argument(..., help="Search query"),
    status: Optional[str] = typer.Option(None, "--status", "-s"),
    category: Optional[str] = typer.Option(None, "--category", "-c"),
    project_id: Optional[str] = typer.Option(None, "--project-id"),
    limit: int = typer.Option(50, "--limit", "-n")
):
    """Search ideas by text content."""
    # ... implementation ...

@app.command()
def incidents_search(
    query: str = typer.Argument(..., help="Search query"),
    status: Optional[str] = typer.Option(None, "--status", "-s"),
    severity: Optional[str] = typer.Option(None, "--severity"),
    project_id: Optional[str] = typer.Option(None, "--project-id"),
    limit: int = typer.Option(50, "--limit", "-n")
):
    """Search incidents by text content."""
    # ... implementation ...

@app.command()
def work_issues_search(
    query: str = typer.Argument(..., help="Search query"),
    status: Optional[str] = typer.Option(None, "--status", "-s"),
    type_: Optional[str] = typer.Option(None, "--type", "-t"),
    project_id: Optional[str] = typer.Option(None, "--project-id"),
    limit: int = typer.Option(50, "--limit", "-n")
):
    """Search work issues by text content."""
    # ... implementation ...

@app.command()
def search(
    query: str = typer.Argument(..., help="Search query"),
    all_types: bool = typer.Option(False, "--all-types", "-a"),
    limit: int = typer.Option(10, "--limit", "-n")
):
    """Search across all entity types."""
    # ... implementation ...
```

---

## CLI Examples

### Example 1: Basic Search

```bash
# Search for tasks about authentication
notion agents tasks search "authentication"
# Returns:
# {
#   "results": [
#     {
#       "id": "task_001",
#       "title": "Fix authentication bug",
#       "status": "In Progress",
#       "priority": "High",
#       "relevance": "high",
#       "matched_in": ["title"]
#     },
#     {
#       "id": "task_002",
#       "title": "Update user profile",
#       "status": "Backlog",
#       "priority": "Medium",
#       "relevance": "medium",
#       "matched_in": ["title"]
#     }
#   ],
#   "total": 2
# }
```

### Example 2: Search with Filters

```bash
# Search for high-priority bugs
notion agents tasks search "bug" --priority High
# Returns: High-priority tasks mentioning "bug"

# Search for accepted ideas about performance
notion agents ideas search "performance" --status Accepted
# Returns: Accepted ideas mentioning "performance"
```

### Example 3: Search Across All Types

```bash
# Search everything for "API"
notion agents search "API" --all-types
# Returns:
# {
#   "tasks": [
#     {"id": "task_001", "title": "API authentication", ...}
#   ],
#   "ideas": [
#     {"id": "idea_001", "title": "REST API improvements", ...}
#   ],
#   "incidents": [],
#   "work_issues": [
#     {"id": "issue_001", "title": "API rate limiting", ...}
#   ],
#   "total": 3
# }
```

### Example 4: Limited Results

```bash
# Get top 10 results
notion agents tasks search "authentication" --limit 10
# Returns: Top 10 most relevant results
```

---

## Acceptance Criteria

### Phase 1: Search Implementation

- [ ] `TextSearcher` class exists
- [ ] `TextSearcher.search_tasks()` works
- [ ] `TextSearcher.search_ideas()` works
- [ ] `TextSearcher.search_incidents()` works
- [ ] `TextSearcher.search_work_issues()` works
- [ ] `TextSearcher.search_all()` works
- [ ] `SearchResult` class exists with to_dict() method
- [ ] Relevance scoring is accurate (high/medium/low)
- [ ] Results are sorted by relevance

### Phase 2: Manager Updates

- [ ] TaskManager has search() method
- [ ] IdeaManager has search() method
- [ ] IncidentManager has search() method
- [ ] WorkIssueManager has search() method

### Phase 3: CLI Commands

- [ ] `notion agents tasks search <query>` works
- [ ] `notion agents ideas search <query>` works
- [ ] `notion agents incidents search <query>` works
- [ ] `notion agents work-issues search <query>` works
- [ ] `notion agents search <query> --all-types` works
- [ ] Search with filters works (e.g., `--status`, `--priority`)
- [ ] `--limit` option works

### Phase 4: Search Quality

- [ ] Case-insensitive search works
- [ ] Partial word matching works
- [ ] Searches both title and description
- [ ] Relevance scoring is intuitive
- [ ] Empty results are handled gracefully

---

## Related Issues

- Related to: #044 (Compound filters - for filtering search results)
- Related to: #046 (Consolidated status view - for search dashboard)
- Enhances: All entity list commands

---

## Migration Path

### For Existing Workspaces

No migration needed - this is a new feature.

### For Code

1. Create `search.py` with `TextSearcher` and `SearchResult` classes
2. Update managers with search methods
3. Add CLI search commands
4. Add tests for search functionality

---

## Rollout Plan

1. **Phase 1**: Implement basic search (title + description)
2. **Phase 2**: Add filters to search
3. **Phase 3**: Add cross-entity search
4. **Phase 4**: Add advanced search features (phrase search, boolean operators)
5. **Phase 5**: Optimize performance for large datasets

---

## Open Questions

1. Should we use Notion's native search API or implement client-side?
   - **Recommendation**: Client-side for now (Notion's search API has limitations)
2. Should we support regular expressions?
   - **Recommendation**: Not in v1, add in v2 if requested
3. Should we index search results for faster repeated searches?
   - **Recommendation**: Not in v1, consider for v2 if performance is an issue
4. Should search support fuzzy matching (typos)?
   - **Recommendation**: Not in v1, consider adding in v2
5. Should we show snippets of matched text in results?
   - **Recommendation**: Add in Phase 4 (nice-to-have feature)

---

## Edge Cases to Handle

1. **Empty query**: Should return all results or error?
   - **Recommendation**: Error with clear message
2. **Very short query** (1-2 characters): Should enforce minimum length?
   - **Recommendation**: Minimum 3 characters
3. **Special characters** in query: Should escape or remove?
   - **Recommendation**: Escape special regex characters
4. **Very large result sets**: Should paginate?
   - **Recommendation**: Default limit of 50, configurable via --limit
5. **No matches found**: Return empty array with helpful message
6. **Unicode and non-ASCII text**: Should work correctly
7. **Search in properties without text** (e.g., dates, numbers): Should skip
