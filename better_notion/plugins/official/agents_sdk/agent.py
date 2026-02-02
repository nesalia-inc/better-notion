"""AI-aware agent workflow utilities for the agents SDK.

This module provides intelligent task selection, incident triage, and batch
operations optimized for AI agent workflows.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from better_notion._sdk.client import NotionClient


@dataclass
class TaskRecommendation:
    """Represents a task recommendation for an agent.

    Attributes:
        task: The Task entity
        match_score: Score from 0-100 indicating how well the task matches
        match_reason: Human-readable explanation of why this task was recommended
    """

    task: Any
    match_score: float
    match_reason: str

    def to_dict(self) -> dict[str, Any]:
        """Convert recommendation to dictionary.

        Returns:
            Dictionary with task details and recommendation metadata
        """
        return {
            "id": self.task.id,
            "title": self.task.title,
            "priority": getattr(self.task, "priority", None),
            "status": getattr(self.task, "status", None),
            "match_score": self.match_score,
            "match_reason": self.match_reason,
        }


class TaskSelector:
    """Intelligent task selection for AI agents.

    Provides scoring algorithms to pick the best tasks for an agent to work on
    based on skills, priority, age, and other factors.
    """

    def __init__(self, client: NotionClient) -> None:
        """Initialize the TaskSelector.

        Args:
            client: Notion API client
        """
        self._client = client

    async def pick_best_tasks(
        self,
        skills: list[str] | None = None,
        max_priority: str | None = None,
        exclude_patterns: list[str] | None = None,
        count: int = 5,
        project_id: str | None = None,
        version_id: str | None = None,
    ) -> list[TaskRecommendation]:
        """Pick the best tasks for an agent to work on.

        Tasks are scored based on:
        - Priority (0-40 points): Critical > High > Medium > Low
        - Skills (0-30 points): Matching skills in title/description
        - Age (0-20 points): Older tasks get higher priority
        - Ready bonus (10 points): No blocking dependencies

        Args:
            skills: List of skills the agent has (e.g., ["python", "database"])
            max_priority: Maximum priority level to consider (e.g., "High")
            exclude_patterns: Regex patterns to exclude from task titles
            count: Maximum number of recommendations to return
            project_id: Filter to specific project
            version_id: Filter to specific version

        Returns:
            List of task recommendations sorted by match score (descending)
        """
        from better_notion.plugins.official.agents_sdk.managers import TaskManager

        task_mgr = TaskManager(self._client, getattr(self._client, "_workspace_config", {}))

        # Get candidate tasks - filter to backlog only
        candidates = await task_mgr.list(
            status="Backlog",
            project_id=project_id,
            version_id=version_id,
        )

        # Filter and score candidates
        recommendations = []

        for task in candidates:
            # Apply filters
            if max_priority:
                priority_order = {"Critical": 4, "High": 3, "Medium": 2, "Low": 1}
                task_prio = getattr(task, "priority", "Low")
                if priority_order.get(task_prio, 0) > priority_order.get(max_priority, 0):
                    continue

            if exclude_patterns:
                title_lower = task.title.lower()
                if any(re.search(pattern, title_lower) for pattern in exclude_patterns):
                    continue

            # Calculate match score
            score, reason = self._calculate_score(task, skills)

            recommendations.append(
                TaskRecommendation(
                    task=task,
                    match_score=score,
                    match_reason=reason,
                )
            )

        # Sort by score (descending)
        recommendations.sort(key=lambda r: r.match_score, reverse=True)

        return recommendations[:count]

    def _calculate_score(
        self,
        task: Any,
        skills: list[str] | None,
    ) -> tuple[float, str]:
        """Calculate a match score for a task.

        Args:
            task: The task entity to score
            skills: List of agent's skills

        Returns:
            Tuple of (score, reason) where score is 0-100 and reason explains the score
        """
        score = 0.0
        reasons = []

        # Priority scoring (0-40 points)
        priority_scores = {
            "Critical": 40,
            "High": 30,
            "Medium": 20,
            "Low": 10,
        }
        task_prio = getattr(task, "priority", "Low")
        prio_score = priority_scores.get(task_prio, 0)
        score += prio_score
        if prio_score > 0:
            reasons.append(f"{task_prio} priority")

        # Skill matching (0-30 points)
        if skills:
            task_title_lower = task.title.lower()
            task_desc_lower = getattr(task, "description", "") or ""
            if isinstance(task_desc_lower, str):
                task_desc_lower = task_desc_lower.lower()
            else:
                task_desc_lower = ""

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
        # Note: Not implemented in v1 due to limited created_at access
        # if hasattr(task, 'created_at') and task.created_at:
        #     days_old = (datetime.now(timezone.utc) - task.created_at).days
        #     age_points = min(20, days_old)
        #     score += age_points
        #     if age_points > 0:
        #         reasons.append(f"{days_old} days old")

        # Bonus for ready tasks (no blockers) - 10 points
        # Note: Not implemented in v1 - requires dependency resolution from issue #040
        # if hasattr(task, 'can_start') and await task.can_start():
        #     score += 10
        #     reasons.append("no blocking dependencies")

        reason = "; ".join(reasons) if reasons else "no specific match criteria"
        return score, reason


class IncidentTriager:
    """Automatic incident triage and classification.

    Uses keyword-based heuristics to classify incidents by severity and type,
    suggest team assignments, and provide confidence scores.
    """

    # Severity classification keywords
    CRITICAL_KEYWORDS = ["down", "outage", "critical", "emergency", "production down", "crash"]
    HIGH_KEYWORDS = ["slow", "degraded", "error", "bug", "broken", "failure"]
    MEDIUM_KEYWORDS = ["issue", "problem", "glitch"]

    # Type classification keywords
    TYPE_KEYWORDS: dict[str, list[str]] = {
        "Performance": ["slow", "latency", "performance", "timeout", "lag"],
        "Security": ["security", "auth", "unauthorized", "vulnerability", "injection", "exploit"],
        "Bug": ["bug", "error", "broken", "crash", "exception", "fault"],
        "Service Disruption": ["down", "outage", "unavailable", "can't access", "500"],
        "Data": ["data", "database", "corruption", "loss", "leak", "inconsistent"],
    }

    # Team assignment suggestions
    TEAM_MAPPING: dict[str, str] = {
        "Performance": "Performance Team",
        "Security": "Security Team",
        "Bug": "Engineering Team",
        "Service Disruption": "Operations Team",
        "Data": "Data Team",
        "General": "Engineering Team",
    }

    # Keywords for confidence calculation
    SPECIFIC_KEYWORDS = [
        "down",
        "outage",
        "slow",
        "security",
        "bug",
        "performance",
        "database",
        "api",
        "critical",
        "crash",
        "error",
        "timeout",
        "latency",
        "unauthorized",
    ]

    def __init__(self, client: NotionClient) -> None:
        """Initialize the IncidentTriager.

        Args:
            client: Notion API client
        """
        self._client = client

    async def triage_incident(self, incident: Any) -> dict[str, Any]:
        """Triage and classify an incident.

        Args:
            incident: The Incident entity to triage

        Returns:
            Dictionary with classification results:
            - severity: Classified severity level
            - type: Incident type
            - suggested_assignment: Team that should handle this
            - confidence: Confidence score (0-1)
            - reasoning: Explanation of the classification
        """
        title_lower = incident.title.lower()
        description = getattr(incident, "description", None) or ""
        if isinstance(description, str):
            description_lower = description.lower()
        else:
            description_lower = ""
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
            "reasoning": self._get_reasoning(text, severity, incident_type),
        }

    def _classify_severity(self, text: str) -> str:
        """Classify incident severity based on keywords.

        Args:
            text: Lowercase text to analyze

        Returns:
            Severity level: Critical, High, Medium, or Low
        """
        if any(kw in text for kw in self.CRITICAL_KEYWORDS):
            return "Critical"
        elif any(kw in text for kw in self.HIGH_KEYWORDS):
            return "High"
        elif any(kw in text for kw in self.MEDIUM_KEYWORDS):
            return "Medium"
        else:
            return "Low"

    def _classify_type(self, text: str) -> str:
        """Classify incident type based on keywords.

        Args:
            text: Lowercase text to analyze

        Returns:
            Incident type (e.g., Performance, Security, Bug, etc.)
        """
        for incident_type, keywords in self.TYPE_KEYWORDS.items():
            if any(kw in text for kw in keywords):
                return incident_type

        return "General"

    def _suggest_assignment(self, incident_type: str, severity: str) -> str:
        """Suggest team assignment based on type and severity.

        Args:
            incident_type: The classified incident type
            severity: The classified severity level

        Returns:
            Name of the team that should handle this incident
        """
        return self.TEAM_MAPPING.get(incident_type, "Engineering Team")

    def _calculate_confidence(self, text: str) -> float:
        """Calculate confidence in classification.

        More specific keywords = higher confidence.

        Args:
            text: Lowercase text to analyze

        Returns:
            Confidence score from 0.0 to 1.0
        """
        matches = sum(1 for kw in self.SPECIFIC_KEYWORDS if kw in text)

        # Base confidence 0.5, +0.1 for each matching keyword, max 0.95
        confidence = min(0.95, 0.5 + (matches * 0.1))

        return round(confidence, 2)

    def _get_reasoning(self, text: str, severity: str, incident_type: str) -> str:
        """Get reasoning for classification.

        Args:
            text: The analyzed text
            severity: Classified severity
            incident_type: Classified type

        Returns:
            Human-readable explanation of the classification
        """
        # Find matching keywords for reasoning
        matched_keywords = []
        for kw in self.SPECIFIC_KEYWORDS:
            if kw in text:
                matched_keywords.append(kw)

        if matched_keywords:
            keywords_str = ", ".join(matched_keywords[:3])  # Show top 3
            return (
                f"Classified as '{severity}' severity and '{incident_type}' type "
                f"based on keywords: {keywords_str}"
            )
        else:
            return (
                f"Classified as '{severity}' severity and '{incident_type}' type "
                "(low confidence - no specific keywords found)"
            )


class BatchOperationManager:
    """Manager for executing batch operations.

    Allows execution of multiple operations in sequence with error handling
    and summary statistics.
    """

    def __init__(self, client: NotionClient) -> None:
        """Initialize the BatchOperationManager.

        Args:
            client: Notion API client
        """
        self._client = client

    async def execute_batch(
        self,
        operations: list[dict[str, Any]],
        continue_on_error: bool = False,
    ) -> dict[str, Any]:
        """Execute a batch of operations.

        Args:
            operations: List of operation dicts with 'command' and 'args' keys
            continue_on_error: If True, continue after errors; if False, stop on first error

        Returns:
            Dictionary with results and summary:
            - results: List of operation results
            - summary: Total, succeeded, and failed counts
        """
        results = []
        succeeded = 0
        failed = 0

        for i, op in enumerate(operations):
            try:
                result = await self._execute_operation(op)
                results.append(
                    {
                        "operation": i + 1,
                        "status": "success",
                        "result": result,
                    }
                )
                succeeded += 1
            except Exception as e:
                results.append(
                    {
                        "operation": i + 1,
                        "status": "error",
                        "error": str(e),
                    }
                )
                failed += 1

                if not continue_on_error:
                    break

        return {
            "results": results,
            "summary": {
                "total": len(operations),
                "succeeded": succeeded,
                "failed": failed,
            },
        }

    async def _execute_operation(self, operation: dict[str, Any]) -> Any:
        """Execute a single operation.

        Args:
            operation: Dict with 'command' and 'args' keys

        Returns:
            Result from the operation

        Raises:
            ValueError: If command is unknown
        """
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

        elif command == "tasks complete":
            from better_notion.plugins.official.agents_sdk.managers import TaskManager

            mgr = TaskManager(self._client, self._client.workspace_config)
            return await mgr.complete(args["task_id"])

        elif command == "tasks create":
            from better_notion.plugins.official.agents_sdk.managers import TaskManager

            mgr = TaskManager(self._client, self._client.workspace_config)
            return await mgr.create(**args)

        else:
            raise ValueError(f"Unknown command: {command}")
