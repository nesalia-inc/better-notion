# Issue #048: AI-Aware Commands and Agent Workflows

## Problem Statement

The Agents CLI is designed for AI agents but lacks commands specifically optimized for agent workflows. Current commands are generic and don't account for agent-specific needs like intelligent task selection, automatic triage, or batch operations.

### Current Limitation

```bash
# What users CANNOT do:
notion agents tasks pick --for-me                # Pick best task for agent
notion agents tasks next --smart                  # AI-recommended next task
notion agents incidents triage --auto             # Auto-classify incidents
notion agents batch --file commands.json          # Execute batch operations
notion agents tasks suggest --unassigned --count 3 # Suggest tasks to work on
```

### Current Agent Workflow (Not Optimized)

```bash
# AI agent must:
# 1. List all available tasks
notion agents tasks list --status Backlog
# Returns: 50 tasks, agent must parse and choose

# 2. Manually filter and prioritize
# (Agent must implement its own logic)

# 3. Pick a task and claim it
notion agents tasks claim task_123

# This is:
# - Inefficient for agents (too many API calls)
# - No intelligent recommendations
# - No batch operations
# - Agents must implement their own selection logic
# - No optimization for agent workflows
```

### Impact

Without AI-aware commands:
- Agents must implement complex selection logic themselves
- More API calls than necessary
- No intelligent task recommendations
- No batch operations for efficiency
- No automatic triage or classification
- Agents can't leverage Notion's context effectively
- Harder to build sophisticated agent workflows

### Real-World Use Cases

```bash
# Use case 1: Agent picks the best task to work on
notion agents tasks pick --for-me --skills "python,database"
# Returns: Best matching task based on skills and priority

# Use case 2: Get smart recommendations
notion agents tasks next --smart --context "I'm working on authentication"
# Returns: Contextually relevant tasks

# Use case 3: Auto-triage incoming incidents
notion agents incidents triage --auto --classify
# Returns: Incidents classified by severity and type

# Use case 4: Batch operations
notion agents batch --file ops.json
# Executes multiple operations efficiently

# Use case 5: Agent collaboration
notion agents tasks handoff task_123 --to-agent agent_456
# Smooth handoff between agents
```

---

## Proposed Solution

### 1. Task Picking Command

```bash
# Pick the best task for an agent to work on
notion agents tasks pick \
  --for-me \
  --skills "python,authentication" \
  --max-priority High \
  --exclude-regex "test.*" \
  --count 3
# Returns:
# {
#   "recommended": [
#     {
#       "id": "task_001",
#       "title": "Fix authentication bug",
#       "priority": "High",
#       "status": "Backlog",
#       "match_score": 0.95,
#       "match_reason": "Matches 'authentication' skill, high priority, no blockers"
#     },
#     {
#       "id": "task_002",
#       "title": "Update database schema",
#       "priority": "Medium",
#       "status": "Backlog",
#       "match_score": 0.82,
#       "match_reason": "Matches 'database' skill, no dependencies"
#     }
#   ],
#   "total_candidates": 15,
#   "filtered_by": {
#     "skills": ["python", "authentication"],
#     "max_priority": "High",
#     "excluded_patterns": ["test.*"]
#   }
# }
```

### 2. Smart Next Task Command

```bash
# Get AI-recommended next task with context
notion agents tasks next --smart --context "working on user authentication"
# Returns:
# {
#   "task": {
#     "id": "task_001",
#     "title": "Implement OAuth2 flow",
#     "priority": "High",
#     "status": "Backlog",
#     "related_to_context": true
#   },
#   "reasoning": "Task is high priority, relates to 'user authentication' context, and has no blocking dependencies",
#   "confidence": 0.92
# }

# Alternative: Get multiple options with explanations
notion agents tasks next --smart --options 5
# Returns: Top 5 candidate tasks with reasoning
```

### 3. Auto-Triage Command

```bash
# Automatically triage and classify incidents
notion agents incidents triage --auto --classify
# Returns:
# {
#   "triaged": [
#     {
#       "id": "inc_001",
#       "title": "API is slow",
#       "auto_classification": {
#         "severity": "Medium",
#         "type": "Performance",
#         "confidence": 0.87
#       },
#       "suggested_assignment": "Performance Team",
#       "reasoning": "Keywords 'slow', 'API' suggest performance issue"
#     }
#   ],
#   "summary": {
#     "total_incidents": 10,
#     "auto_classified": 8,
#     "needs_review": 2
#   }
# }
```

### 4. Batch Operations Command

```bash
# Execute multiple operations in a batch
notion agents batch --file ops.json --continue-on-error
# ops.json:
# {
#   "operations": [
#     {"command": "tasks claim", "args": {"task_id": "task_001"}},
#     {"command": "tasks start", "args": {"task_id": "task_001"}},
#     {"command": "tasks create", "args": {"title": "Subtask A", ...}},
#     {"command": "tasks complete", "args": {"task_id": "task_002"}}
#   ]
# }
# Returns:
# {
#   "results": [
#     {"operation": 1, "status": "success", "result": {...}},
#     {"operation": 2, "status": "success", "result": {...}},
#     {"operation": 3, "status": "error", "error": "..."},
#     {"operation": 4, "status": "success", "result": {...}}
#   ],
#   "summary": {
#     "total": 4,
#     "succeeded": 3,
#     "failed": 1
#   }
# }
```

### 5. Agent Handoff Command

```bash
# Hand off a task to another agent
notion agents tasks handoff task_123 --to-agent agent_456 --notes "Started auth flow, need to complete refresh token"
# Returns:
# {
#   "task_id": "task_123",
#   "from_agent": "agent_001",
#   "to_agent": "agent_456",
#   "handoff_notes": "Started auth flow, need to complete refresh token",
#   "status": "handed_off"
# }
```

### 6. Suggest Command

```bash
# Suggest tasks based on various criteria
notion agents tasks suggest \
  --unassigned \
  --priority High,Critical \
  --count 5 \
  --reason
# Returns:
# {
#   "suggestions": [
#     {
#       "id": "task_001",
#       "title": "Fix critical security bug",
#       "priority": "Critical",
#       "status": "Backlog",
#       "estimated_hours": 4,
#       "reason": "Critical priority, unassigned, no dependencies, small effort"
#     }
#   ]
# }
```

---

## Implementation Architecture

### Phase 1: Task Selection Algorithm (1 day)

```python
# better_notion/plugins/official/agents_sdk/agent.py (new file)

from typing import Any
import re
from dataclasses import dataclass

@dataclass
class TaskRecommendation:
    """Represents a task recommendation."""
    task: Any
    match_score: float
    match_reason: str

    def to_dict(self) -> dict:
        return {
            "id": self.task.id,
            "title": self.task.title,
            "priority": self.task.priority,
            "status": self.task.status,
            "match_score": self.match_score,
            "match_reason": self.match_reason
        }


class TaskSelector:
    """Intelligent task selection for agents."""

    def __init__(self, client: NotionClient):
        self._client = client

    async def pick_best_tasks(
        self,
        skills: list[str] | None = None,
        max_priority: str | None = None,
        exclude_patterns: list[str] | None = None,
        count: int = 5,
        project_id: str | None = None,
        version_id: str | None = None
    ) -> list[TaskRecommendation]:
        """Pick the best tasks for an agent to work on."""
        from better_notion.plugins.official.agents_sdk.managers import TaskManager

        task_mgr = TaskManager(self._client, self._client.workspace_config)

        # Get candidate tasks
        # Use compound filters (see Issue #044)
        candidates = await task_mgr.list(
            status="Backlog",
            project_id=project_id,
            version_id=version_id
        )

        # Filter and score candidates
        recommendations = []

        for task in candidates:
            # Apply filters
            if max_priority:
                priority_order = {"Critical": 4, "High": 3, "Medium": 2, "Low": 1}
                if priority_order.get(task.priority, 0) > priority_order.get(max_priority, 0):
                    continue

            if exclude_patterns:
                title_lower = task.title.lower()
                if any(re.search(pattern, title_lower) for pattern in exclude_patterns):
                    continue

            # Calculate match score
            score, reason = self._calculate_score(task, skills)

            recommendations.append(TaskRecommendation(
                task=task,
                match_score=score,
                match_reason=reason
            ))

        # Sort by score
        recommendations.sort(key=lambda r: r.match_score, reverse=True)

        return recommendations[:count]

    def _calculate_score(
        self,
        task: Any,
        skills: list[str] | None
    ) -> tuple[float, str]:
        """Calculate a match score for a task."""
        score = 0.0
        reasons = []

        # Priority scoring (0-40 points)
        priority_scores = {
            "Critical": 40,
            "High": 30,
            "Medium": 20,
            "Low": 10
        }
        score += priority_scores.get(task.priority, 0)
        reasons.append(f"{task.priority} priority")

        # Skill matching (0-30 points)
        if skills:
            task_title_lower = task.title.lower()
            task_desc_lower = getattr(task, 'description', '').lower()

            matched_skills = []
            for skill in skills:
                skill_lower = skill.lower()
                if skill_lower in task_title_lower or skill_lower in task_desc_lower:
                    matched_skills.append(skill)

            if matched_skills:
                skill_points = min(30, len(matched_skills) * 10)
                score += skill_points
                reasons.append(f"matches skills: {', '.join(matched_skills)}")

        # Age scoring (0-20 points) - older tasks get higher priority
        # (Assuming task has created_at property)
        # if hasattr(task, 'created_at'):
        #     days_old = (datetime.now() - task.created_at).days
        #     age_points = min(20, days_old)
        #     score += age_points

        # Bonus for ready tasks (no blockers) - 10 points
        # if hasattr(task, 'can_start'):
        #     if await task.can_start():
        #         score += 10
        #         reasons.append("no blocking dependencies")

        return score, "; ".join(reasons)


class IncidentTriager:
    """Automatic incident triage and classification."""

    def __init__(self, client: NotionClient):
        self._client = client

    async def triage_incident(self, incident: Any) -> dict:
        """Triage and classify an incident."""
        title_lower = incident.title.lower()
        description_lower = getattr(incident, 'description', '').lower()
        text = f"{title_lower} {description_lower}"

        # Classify severity
        severity = self._classify_severity(text)

        # Classify type
        incident_type = self._classify_type(text)

        # Suggest assignment
        suggested_team = self._suggest_assignment(incident_type, severity)

        # Calculate confidence
        confidence = self._calculate_confidence(text)

        return {
            "severity": severity,
            "type": incident_type,
            "suggested_assignment": suggested_team,
            "confidence": confidence,
            "reasoning": self._get_reasoning(text, severity, incident_type)
        }

    def _classify_severity(self, text: str) -> str:
        """Classify incident severity based on keywords."""
        critical_keywords = ["down", "outage", "critical", "emergency", "production down"]
        high_keywords = ["slow", "degraded", "error", "bug", "broken"]
        medium_keywords = ["issue", "problem", "glitch"]

        text_lower = text.lower()

        if any(kw in text_lower for kw in critical_keywords):
            return "Critical"
        elif any(kw in text_lower for kw in high_keywords):
            return "High"
        elif any(kw in text_lower for kw in medium_keywords):
            return "Medium"
        else:
            return "Low"

    def _classify_type(self, text: str) -> str:
        """Classify incident type based on keywords."""
        type_keywords = {
            "Performance": ["slow", "latency", "performance", "timeout"],
            "Security": ["security", "auth", "unauthorized", "vulnerability"],
            "Bug": ["bug", "error", "broken", "crash"],
            "Service Disruption": ["down", "outage", "unavailable"],
            "Data": ["data", "database", "corruption", "loss"]
        }

        text_lower = text.lower()

        for incident_type, keywords in type_keywords.items():
            if any(kw in text_lower for kw in keywords):
                return incident_type

        return "General"

    def _suggest_assignment(self, incident_type: str, severity: str) -> str:
        """Suggest team assignment based on type and severity."""
        team_mapping = {
            "Performance": "Performance Team",
            "Security": "Security Team",
            "Bug": "Engineering Team",
            "Service Disruption": "Operations Team",
            "Data": "Data Team",
            "General": "Engineering Team"
        }

        return team_mapping.get(incident_type, "Engineering Team")

    def _calculate_confidence(self, text: str) -> float:
        """Calculate confidence in classification."""
        # Simple heuristic: more specific keywords = higher confidence
        specific_keywords = [
            "down", "outage", "slow", "security", "bug",
            "performance", "database", "api", "critical"
        ]

        text_lower = text.lower()
        matches = sum(1 for kw in specific_keywords if kw in text_lower)

        # Base confidence 0.5, +0.1 for each matching keyword, max 0.95
        confidence = min(0.95, 0.5 + (matches * 0.1))

        return round(confidence, 2)

    def _get_reasoning(self, text: str, severity: str, incident_type: str) -> str:
        """Get reasoning for classification."""
        return f"Classified as '{severity}' severity and '{incident_type}' type based on keyword analysis"


class BatchOperationManager:
    """Manager for batch operations."""

    def __init__(self, client: NotionClient):
        self._client = client

    async def execute_batch(
        self,
        operations: list[dict],
        continue_on_error: bool = False
    ) -> dict:
        """Execute a batch of operations."""
        results = []
        succeeded = 0
        failed = 0

        for i, op in enumerate(operations):
            try:
                result = await self._execute_operation(op)
                results.append({
                    "operation": i + 1,
                    "status": "success",
                    "result": result
                })
                succeeded += 1
            except Exception as e:
                results.append({
                    "operation": i + 1,
                    "status": "error",
                    "error": str(e)
                })
                failed += 1

                if not continue_on_error:
                    break

        return {
            "results": results,
            "summary": {
                "total": len(operations),
                "succeeded": succeeded,
                "failed": failed
            }
        }

    async def _execute_operation(self, operation: dict) -> Any:
        """Execute a single operation."""
        command = operation.get("command")
        args = operation.get("args", {})

        # Map commands to manager methods
        if command == "tasks claim":
            from better_notion.plugins.official.agents_sdk.managers import TaskManager
            mgr = TaskManager(self._client, self._client.workspace_config)
            return await mgr.claim(args["task_id"])

        elif command == "tasks start":
            from better_notion.plugins.official.agents_sdk.managers import TaskManager
            mgr = TaskManager(self._client, self._client.workspace_config)
            return await mgr.start(args["task_id"])

        elif command == "tasks create":
            from better_notion.plugins.official.agents_sdk.managers import TaskManager
            mgr = TaskManager(self._client, self._client.workspace_config)
            return await mgr.create(**args)

        # ... more command mappings ...

        else:
            raise ValueError(f"Unknown command: {command}")
```

### Phase 2: Manager Integration (0.5 day)

Add agent-focused methods to existing managers.

### Phase 3: CLI Commands (1 day)

```bash
# better_notion/plugins/official/agents_cli.py

@app.command()
def tasks_pick(
    for_me: bool = typer.Option(True, "--for-me"),
    skills: Optional[str] = typer.Option(None, "--skills", "-s"),
    max_priority: Optional[str] = typer.Option(None, "--max-priority"),
    exclude: Optional[str] = typer.Option(None, "--exclude"),
    count: int = typer.Option(5, "--count", "-n"),
    project_id: Optional[str] = typer.Option(None, "--project-id", "-p"),
    version_id: Optional[str] = typer.Option(None, "--version-id", "-v")
):
    """Pick the best tasks for an agent to work on."""
    # ... implementation ...

@app.command()
def tasks_next_smart(
    context: Optional[str] = typer.Option(None, "--context", "-c"),
    options: int = typer.Option(1, "--options", "-o")
):
    """Get AI-recommended next task."""
    # ... implementation ...

@app.command()
def incidents_triage(
    auto: bool = typer.Option(True, "--auto"),
    classify: bool = typer.Option(False, "--classify")
):
    """Triage and classify incidents."""
    # ... implementation ...

@app.command()
def batch(
    file: str = typer.Option(..., "--file", "-f"),
    continue_on_error: bool = typer.Option(False, "--continue-on-error")
):
    """Execute batch operations."""
    # ... implementation ...

@app.command()
def tasks_handoff(
    task_id: str = typer.Argument(...),
    to_agent: str = typer.Option(..., "--to-agent"),
    notes: Optional[str] = typer.Option(None, "--notes")
):
    """Hand off a task to another agent."""
    # ... implementation ...

@app.command()
def tasks_suggest(
    unassigned: bool = typer.Option(False, "--unassigned", "-u"),
    priority: Optional[str] = typer.Option(None, "--priority", "-p"),
    count: int = typer.Option(5, "--count", "-n"),
    reason: bool = typer.Option(False, "--reason", "-r")
):
    """Suggest tasks based on criteria."""
    # ... implementation ...
```

---

## CLI Examples

### Example 1: Agent Picks Tasks

```bash
# Agent looking for Python tasks
notion agents tasks pick --skills "python,api" --priority High --count 3
# Returns: Top 3 matching Python/API tasks
```

### Example 2: Smart Next Task

```bash
# Get contextually relevant task
notion agents tasks next --smart --context "I'm fixing authentication bugs"
# Returns: Best matching task with reasoning
```

### Example 3: Auto-Triage Incidents

```bash
# Classify all unclassified incidents
notion agents incidents triage --auto --classify
# Returns: All incidents with severity/type classifications
```

### Example 4: Batch Operations

```bash
# Execute multiple operations
cat > ops.json <<EOF
{
  "operations": [
    {"command": "tasks claim", "args": {"task_id": "task_001"}},
    {"command": "tasks start", "args": {"task_id": "task_001"}}
  ]
}
EOF

notion agents batch --file ops.json
```

---

## Acceptance Criteria

### Phase 1: Task Selection

- [ ] TaskSelector can pick best tasks
- [ ] Scoring algorithm is reasonable
- [ ] Filters work correctly
- [ ] Returns explanations for choices

### Phase 2: Incident Triage

- [ ] IncidentTriager can classify severity
- [ ] IncidentTriager can classify type
- [ ] Confidence scoring works
- [ ] Suggests appropriate assignments

### Phase 3: Batch Operations

- [ ] Can execute batch operations
- [ ] Handles errors correctly
- [ ] Continue-on-error works
- [ ] Returns summary statistics

### Phase 4: CLI Commands

- [ ] `tasks pick` works
- [ ] `tasks next --smart` works
- [ ] `incidents triage` works
- [ ] `batch` works
- [ ] `tasks handoff` works
- [ ] `tasks suggest` works

---

## Related Issues

- Related to: #040 (Task dependencies - for ready task detection)
- Related to: #042 (Human assignment - for agent assignment)
- Related to: #044 (Compound filters - for filtering candidates)
- Related to: #045 (Full-text search - for context matching)

---

## Open Questions

1. Should task selection use machine learning?
   - **Recommendation**: Not in v1, use rule-based scoring, consider ML for v2
2. How should agents identify themselves?
   - **Recommendation**: Use config file or environment variable
3. Should we support agent-to-agent communication?
   - **Recommendation**: Not in v1, handoff is sufficient for now
4. Should batch operations support transactions (all or nothing)?
   - **Recommendation**: Not in v1, continue-on-error is sufficient
5. How should we handle conflicting assignments (human vs agent)?
   - **Recommendation**: Use different assignee field values

---

## Edge Cases to Handle

1. **No tasks match criteria**: Return empty list with clear message
2. **Multiple agents pick same task**: Use optimistic locking
3. **Batch operation fails mid-way**: Handle based on continue-on-error flag
4. **Low confidence triage**: Flag for manual review
5. **Agent skills don't match any tasks**: Suggest closest matches
6. **Context-based selection finds nothing**: Fall back to priority-based
7. **Handoff to non-existent agent**: Validate and error clearly
