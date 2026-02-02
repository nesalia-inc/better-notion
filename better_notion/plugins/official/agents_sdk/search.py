"""Full-text search implementation for the agents SDK.

This module provides text-based search functionality across all entity types
with relevance scoring and filtering capabilities.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from better_notion._sdk.client import NotionClient


class SearchResult:
    """Represents a search result with relevance information.

    Attributes:
        entity: The entity (Task, Idea, Incident, WorkIssue, etc.)
        relevance: Relevance level ("high", "medium", "low", "none")
        matched_in: List of fields that matched (e.g., ["title", "description"])
    """

    def __init__(
        self,
        entity: Any,
        relevance: str,
        matched_in: list[str],
    ) -> None:
        """Initialize a SearchResult.

        Args:
            entity: The entity that matched
            relevance: Relevance level
            matched_in: Which fields matched the query
        """
        self.entity = entity
        self.relevance = relevance
        self.matched_in = matched_in

    def to_dict(self) -> dict[str, Any]:
        """Convert search result to dictionary.

        Returns:
            Dictionary with entity details and search metadata
        """
        result = {
            "id": self.entity.id,
            "title": self.entity.title,
            "status": getattr(self.entity, "status", None),
            "relevance": self.relevance,
            "matched_in": self.matched_in,
        }

        # Add entity-specific fields
        result.update(self._entity_specific_fields())

        return result

    def _entity_specific_fields(self) -> dict[str, Any]:
        """Get entity-specific fields for output.

        Returns:
            Dictionary of entity-specific properties
        """
        result = {}

        # Import entity types to check instance
        from better_notion.plugins.official.agents_sdk.models import (
            Idea,
            Incident,
            Task,
            WorkIssue,
        )

        if isinstance(self.entity, Task):
            result["priority"] = getattr(self.entity, "priority", None)
            result["type"] = getattr(self.entity, "task_type", None)
        elif isinstance(self.entity, Idea):
            result["category"] = getattr(self.entity, "category", None)
            result["effort"] = getattr(self.entity, "effort_estimate", None)
        elif isinstance(self.entity, Incident):
            result["severity"] = getattr(self.entity, "severity", None)
            result["incident_type"] = getattr(self.entity, "incident_type", None)
        elif isinstance(self.entity, WorkIssue):
            result["severity"] = getattr(self.entity, "severity", None)
            result["issue_type"] = getattr(self.entity, "issue_type", None)

        return result


class TextSearcher:
    """Full-text search implementation for entities.

    Provides client-side text search with relevance scoring across
    Tasks, Ideas, Incidents, and WorkIssues.
    """

    def __init__(self, client: NotionClient) -> None:
        """Initialize the TextSearcher.

        Args:
            client: Notion API client
        """
        self._client = client

    def _calculate_relevance(
        self,
        query: str,
        title: str,
        description: str | None = None,
    ) -> tuple[str, list[str]]:
        """Calculate relevance score and matched fields.

        Args:
            query: Search query (lowercase)
            title: Entity title
            description: Entity description (optional)

        Returns:
            Tuple of (relevance_level, matched_fields)
            - relevance_level: "high", "medium", "low", or "none"
            - matched_fields: List of field names that matched
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
            # Exact phrase match or single word match in title = high relevance
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
        filters: dict[str, Any] | None = None,
        limit: int = 50,
    ) -> list[SearchResult]:
        """Search tasks by text query.

        Args:
            query: Text search query
            database_id: Tasks database ID
            filters: Optional Notion filters to apply
            limit: Maximum number of results to return

        Returns:
            List of SearchResults sorted by relevance
        """
        from better_notion.plugins.official.agents_sdk.models import Task

        # Build query object
        query_obj: dict[str, Any] = {}
        if filters:
            query_obj["filter"] = filters

        # Query the database
        response = await self._client._api._request(
            "POST",
            f"/databases/{database_id}/query",
            json=query_obj,
        )

        results = []
        for page_data in response.get("results", []):
            task = Task(self._client, page_data)

            # Get description if available
            description = None
            if hasattr(task, "description"):
                description = task.description

            # Calculate relevance
            relevance, matched_in = self._calculate_relevance(query, task.title, description)

            if relevance != "none":
                results.append(SearchResult(task, relevance, matched_in))

        # Sort by relevance (high > medium > low) and then by title
        results.sort(
            key=lambda r: (
                {"high": 0, "medium": 1, "low": 2}[r.relevance],
                r.entity.title,
            )
        )

        return results[:limit]

    async def search_ideas(
        self,
        query: str,
        database_id: str,
        filters: dict[str, Any] | None = None,
        limit: int = 50,
    ) -> list[SearchResult]:
        """Search ideas by text query.

        Args:
            query: Text search query
            database_id: Ideas database ID
            filters: Optional Notion filters to apply
            limit: Maximum number of results to return

        Returns:
            List of SearchResults sorted by relevance
        """
        from better_notion.plugins.official.agents_sdk.models import Idea

        query_obj: dict[str, Any] = {}
        if filters:
            query_obj["filter"] = filters

        response = await self._client._api._request(
            "POST",
            f"/databases/{database_id}/query",
            json=query_obj,
        )

        results = []
        for page_data in response.get("results", []):
            idea = Idea(self._client, page_data)

            description = None
            if hasattr(idea, "description"):
                description = idea.description

            relevance, matched_in = self._calculate_relevance(query, idea.title, description)

            if relevance != "none":
                results.append(SearchResult(idea, relevance, matched_in))

        results.sort(
            key=lambda r: (
                {"high": 0, "medium": 1, "low": 2}[r.relevance],
                r.entity.title,
            )
        )

        return results[:limit]

    async def search_incidents(
        self,
        query: str,
        database_id: str,
        filters: dict[str, Any] | None = None,
        limit: int = 50,
    ) -> list[SearchResult]:
        """Search incidents by text query.

        Args:
            query: Text search query
            database_id: Incidents database ID
            filters: Optional Notion filters to apply
            limit: Maximum number of results to return

        Returns:
            List of SearchResults sorted by relevance
        """
        from better_notion.plugins.official.agents_sdk.models import Incident

        query_obj: dict[str, Any] = {}
        if filters:
            query_obj["filter"] = filters

        response = await self._client._api._request(
            "POST",
            f"/databases/{database_id}/query",
            json=query_obj,
        )

        results = []
        for page_data in response.get("results", []):
            incident = Incident(self._client, page_data)

            description = None
            if hasattr(incident, "description"):
                description = incident.description

            relevance, matched_in = self._calculate_relevance(query, incident.title, description)

            if relevance != "none":
                results.append(SearchResult(incident, relevance, matched_in))

        results.sort(
            key=lambda r: (
                {"high": 0, "medium": 1, "low": 2}[r.relevance],
                r.entity.title,
            )
        )

        return results[:limit]

    async def search_work_issues(
        self,
        query: str,
        database_id: str,
        filters: dict[str, Any] | None = None,
        limit: int = 50,
    ) -> list[SearchResult]:
        """Search work issues by text query.

        Args:
            query: Text search query
            database_id: Work Issues database ID
            filters: Optional Notion filters to apply
            limit: Maximum number of results to return

        Returns:
            List of SearchResults sorted by relevance
        """
        from better_notion.plugins.official.agents_sdk.models import WorkIssue

        query_obj: dict[str, Any] = {}
        if filters:
            query_obj["filter"] = filters

        response = await self._client._api._request(
            "POST",
            f"/databases/{database_id}/query",
            json=query_obj,
        )

        results = []
        for page_data in response.get("results", []):
            issue = WorkIssue(self._client, page_data)

            description = None
            if hasattr(issue, "description"):
                description = issue.description

            relevance, matched_in = self._calculate_relevance(query, issue.title, description)

            if relevance != "none":
                results.append(SearchResult(issue, relevance, matched_in))

        results.sort(
            key=lambda r: (
                {"high": 0, "medium": 1, "low": 2}[r.relevance],
                r.entity.title,
            )
        )

        return results[:limit]

    async def search_all(
        self,
        query: str,
        workspace_config: dict[str, Any],
        limit_per_type: int = 10,
    ) -> dict[str, Any]:
        """Search across all entity types.

        Args:
            query: Text search query
            workspace_config: Workspace configuration with database IDs
            limit_per_type: Maximum results per entity type

        Returns:
            Dictionary with results for each entity type and total count
        """
        results = {
            "tasks": [],
            "ideas": [],
            "incidents": [],
            "work_issues": [],
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

        total = sum(len(v) for v in results.values() if isinstance(v, list))
        results["total"] = total

        return results
