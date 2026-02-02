"""Change history tracking for the agents SDK.

This module provides audit trail functionality to track who changed what,
when, and why, with revision history, diff capabilities, and revert functionality.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from better_notion._sdk.client import NotionClient


@dataclass
class PropertyChange:
    """Represents a single property change.

    Attributes:
        property_name: Name of the property that changed
        from_value: Previous value (None if property was added)
        to_value: New value (None if property was removed)
    """

    property_name: str
    from_value: Any
    to_value: Any

    def to_dict(self) -> dict[str, Any]:
        """Convert property change to dictionary.

        Returns:
            Dictionary with property, from, and to values
        """
        return {
            "property": self.property_name,
            "from": self.from_value,
            "to": self.to_value,
        }


@dataclass
class Revision:
    """Represents a single revision of an entity.

    Attributes:
        revision_id: Sequential revision number (starting at 1)
        timestamp: When the change was made
        author: Who made the change
        changes: List of property changes in this revision
        reason: Optional explanation for the change
    """

    revision_id: int
    timestamp: datetime
    author: str
    changes: list[PropertyChange]
    reason: str | None

    def to_dict(self) -> dict[str, Any]:
        """Convert revision to dictionary.

        Returns:
            Dictionary with all revision data
        """
        return {
            "revision_id": self.revision_id,
            "timestamp": self.timestamp.isoformat(),
            "author": self.author,
            "changes": [c.to_dict() for c in self.changes],
            "reason": self.reason,
        }


class HistoryStorage:
    """Storage backend for history data.

    Supports both local file storage (JSONL) and optional Notion database storage.
    """

    def __init__(self, client: NotionClient) -> None:
        """Initialize the HistoryStorage.

        Args:
            client: Notion API client
        """
        self._client = client
        self._history_root = Path(".notion_history")

    async def save_revision(
        self,
        entity_id: str,
        entity_type: str,
        revision: Revision,
    ) -> None:
        """Save a revision to storage.

        Args:
            entity_id: Entity ID
            entity_type: Entity type (e.g., "task", "idea")
            revision: Revision to save
        """
        # Try Notion storage first if configured
        database_id = self._client.workspace_config.get("Change_History")
        if database_id:
            try:
                await self._save_to_notion(database_id, entity_id, entity_type, revision)
                return
            except Exception:
                # Fall back to local storage on error
                pass

        # Default to local storage
        await self._save_to_local(entity_id, entity_type, revision)

    async def _save_to_notion(
        self,
        database_id: str,
        entity_id: str,
        entity_type: str,
        revision: Revision,
    ) -> None:
        """Save revision to Notion database.

        Args:
            database_id: Change History database ID
            entity_id: Entity ID
            entity_type: Entity type
            revision: Revision to save
        """
        from better_notion._sdk.models.page import Page

        # Create a page in the Change History database
        changes_text = "\n".join([
            f"{c.property_name}: {c.from_value} → {c.to_value}"
            for c in revision.changes
        ])

        properties = {
            "Entity ID": [{"type": "text", "text": {"content": entity_id}}],
            "Entity Type": {"select": {"name": entity_type}},
            "Revision": {"number": revision.revision_id},
            "Author": [{"type": "text", "text": {"content": revision.author}}],
            "Timestamp": {"date": {"start": revision.timestamp.isoformat()}},
            "Changes": [
                {
                    "type": "text",
                    "text": {
                        "content": changes_text,
                    },
                }
            ],
        }

        if revision.reason:
            properties["Reason"] = [
                {
                    "type": "text",
                    "text": {
                        "content": revision.reason,
                    },
                }
            ]

        await Page.create(
            client=self._client,
            database_id=database_id,
            title=f"{entity_type}:{entity_id} - r{revision.revision_id}",
            properties=properties,
        )

    async def _save_to_local(
        self,
        entity_id: str,
        entity_type: str,
        revision: Revision,
    ) -> None:
        """Save revision to local file storage.

        Args:
            entity_id: Entity ID
            entity_type: Entity type
            revision: Revision to save
        """
        # Create history directory
        history_dir = self._history_root / entity_type
        history_dir.mkdir(parents=True, exist_ok=True)

        # Save to JSONL file
        history_file = history_dir / f"{entity_id}.jsonl"

        # Append revision
        with open(history_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(revision.to_dict()) + "\n")

    async def get_revisions(self, entity_id: str, entity_type: str | None = None) -> list[Revision]:
        """Get all revisions for an entity.

        Args:
            entity_id: Entity ID
            entity_type: Optional entity type to narrow search

        Returns:
            List of revisions sorted by revision_id
        """
        # Try local storage first
        revisions = await self._get_from_local(entity_id, entity_type)

        if not revisions:
            # Try Notion storage (not implemented in v1)
            revisions = await self._get_from_notion(entity_id)

        return revisions

    async def _get_from_local(
        self,
        entity_id: str,
        entity_type: str | None = None,
    ) -> list[Revision]:
        """Get revisions from local storage.

        Args:
            entity_id: Entity ID
            entity_type: Optional entity type to narrow search

        Returns:
            List of revisions
        """
        if not self._history_root.exists():
            return []

        # If entity_type is specified, look in that directory
        if entity_type:
            history_file = self._history_root / entity_type / f"{entity_id}.jsonl"
            if history_file.exists():
                return self._load_revisions_from_file(history_file)
            return []

        # Otherwise, search all entity type directories
        for entity_dir in self._history_root.iterdir():
            if entity_dir.is_dir():
                history_file = entity_dir / f"{entity_id}.jsonl"
                if history_file.exists():
                    return self._load_revisions_from_file(history_file)

        return []

    def _load_revisions_from_file(self, history_file: Path) -> list[Revision]:
        """Load revisions from a JSONL file.

        Args:
            history_file: Path to the JSONL file

        Returns:
            List of revisions
        """
        revisions = []
        with open(history_file, encoding="utf-8") as f:
            for line in f:
                data = json.loads(line)
                revisions.append(
                    Revision(
                        revision_id=data["revision_id"],
                        timestamp=datetime.fromisoformat(data["timestamp"]),
                        author=data["author"],
                        changes=[
                            PropertyChange(
                                property_name=c["property"],
                                from_value=c.get("from"),
                                to_value=c.get("to"),
                            )
                            for c in data["changes"]
                        ],
                        reason=data.get("reason"),
                    )
                )

        # Sort by revision_id
        revisions.sort(key=lambda r: r.revision_id)
        return revisions

    async def _get_from_notion(self, entity_id: str) -> list[Revision]:
        """Get revisions from Notion storage.

        Args:
            entity_id: Entity ID

        Returns:
            List of revisions (empty in v1 - Notion storage not implemented)
        """
        # Not implemented in v1
        # Would query Change_History database and filter by Entity ID
        return []

    async def get_audit_log(
        self,
        project_id: str | None = None,
        days: int = 7,
        entity_type: str | None = None,
    ) -> list[dict[str, Any]]:
        """Get audit log for changes.

        Args:
            project_id: Optional project ID to filter by
            days: Number of days to look back
            entity_type: Optional entity type filter

        Returns:
            List of change records with metadata
        """
        # In v1, scan local storage for recent changes
        cutoff_time = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
        cutoff_time = cutoff_time.replace(day=cutoff_time.day - days)

        changes = []

        if not self._history_root.exists():
            return changes

        # Scan entity type directories
        for entity_dir in self._history_root.iterdir():
            if not entity_dir.is_dir():
                continue

            # Filter by entity type if specified
            if entity_type and entity_dir.name != entity_type:
                continue

            for history_file in entity_dir.glob("*.jsonl"):
                file_changes = self._load_recent_changes_from_file(history_file, cutoff_time)
                changes.extend(file_changes)

        # Sort by timestamp (newest first)
        changes.sort(key=lambda c: c["timestamp"], reverse=True)

        return changes

    def _load_recent_changes_from_file(
        self,
        history_file: Path,
        cutoff_time: datetime,
    ) -> list[dict[str, Any]]:
        """Load recent changes from a JSONL file.

        Args:
            history_file: Path to the JSONL file
            cutoff_time: Only include changes after this time

        Returns:
            List of change records
        """
        changes = []
        entity_id = history_file.stem  # Filename is entity ID
        entity_type = history_file.parent.name

        with open(history_file, encoding="utf-8") as f:
            for line in f:
                data = json.loads(line)
                timestamp = datetime.fromisoformat(data["timestamp"])

                if timestamp >= cutoff_time:
                    changes.append(
                        {
                            "timestamp": timestamp,
                            "author": data["author"],
                            "entity_type": entity_type,
                            "entity_id": entity_id,
                            "revision_id": data["revision_id"],
                            "changes": data["changes"],
                            "reason": data.get("reason"),
                        }
                    )

        return changes


class HistoryTracker:
    """Track and manage change history for entities.

    Provides methods to record changes, retrieve history, compare revisions,
    and generate audit logs.
    """

    def __init__(self, client: NotionClient) -> None:
        """Initialize the HistoryTracker.

        Args:
            client: Notion API client
        """
        self._client = client
        self._storage = HistoryStorage(client)

    async def record_creation(
        self,
        entity_id: str,
        entity_type: str,
        author: str,
        properties: dict[str, Any],
    ) -> None:
        """Record entity creation.

        Args:
            entity_id: Entity ID
            entity_type: Entity type (e.g., "task", "idea")
            author: Who created the entity
            properties: Initial property values
        """
        changes = [
            PropertyChange(
                property_name=prop,
                from_value=None,
                to_value=self._format_value(value),
            )
            for prop, value in properties.items()
        ]

        revision = Revision(
            revision_id=1,
            timestamp=datetime.now(timezone.utc),
            author=author,
            changes=changes,
            reason="Initial creation",
        )

        await self._storage.save_revision(entity_id, entity_type, revision)

    async def record_update(
        self,
        entity_id: str,
        entity_type: str,
        author: str,
        old_properties: dict[str, Any],
        new_properties: dict[str, Any],
        reason: str | None = None,
    ) -> None:
        """Record entity update.

        Args:
            entity_id: Entity ID
            entity_type: Entity type
            author: Who made the change
            old_properties: Property values before change
            new_properties: Property values after change
            reason: Optional explanation for the change
        """
        changes = []

        # Find changed properties
        all_keys = set(old_properties.keys()) | set(new_properties.keys())

        for key in all_keys:
            old_val = old_properties.get(key)
            new_val = new_properties.get(key)

            if old_val != new_val:
                changes.append(
                    PropertyChange(
                        property_name=key,
                        from_value=self._format_value(old_val),
                        to_value=self._format_value(new_val),
                    )
                )

        if not changes:
            return  # No changes to record

        # Get next revision number
        current_revisions = await self._storage.get_revisions(entity_id, entity_type)
        next_revision_id = len(current_revisions) + 1

        revision = Revision(
            revision_id=next_revision_id,
            timestamp=datetime.now(timezone.utc),
            author=author,
            changes=changes,
            reason=reason,
        )

        await self._storage.save_revision(entity_id, entity_type, revision)

    async def get_history(self, entity_id: str, entity_type: str) -> list[Revision]:
        """Get full history for an entity.

        Args:
            entity_id: Entity ID
            entity_type: Entity type

        Returns:
            List of revisions sorted by revision_id
        """
        return await self._storage.get_revisions(entity_id, entity_type)

    async def get_revision(
        self,
        entity_id: str,
        entity_type: str,
        revision_id: int,
    ) -> dict[str, Any] | None:
        """Get entity state at a specific revision.

        Args:
            entity_id: Entity ID
            entity_type: Entity type
            revision_id: Revision number to retrieve

        Returns:
            Dictionary of property values at that revision, or None if not found
        """
        revisions = await self._storage.get_revisions(entity_id, entity_type)

        if not revisions or revision_id < 1 or revision_id > len(revisions):
            return None

        # Reconstruct state by applying changes up to revision
        state: dict[str, Any] = {}
        for revision in revisions[:revision_id]:
            for change in revision.changes:
                state[change.property_name] = change.to_value

        return state

    async def compare_revisions(
        self,
        entity_id: str,
        entity_type: str,
        from_revision: int,
        to_revision: int,
    ) -> dict[str, Any]:
        """Compare two revisions.

        Args:
            entity_id: Entity ID
            entity_type: Entity type
            from_revision: Starting revision number
            to_revision: Ending revision number

        Returns:
            Dictionary with comparison results and changes
        """
        revisions = await self._storage.get_revisions(entity_id, entity_type)

        if not revisions:
            raise ValueError(f"No revisions found for {entity_type}:{entity_id}")

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
            "entity_type": entity_type,
            "comparing": {
                "from_revision": from_revision,
                "to_revision": to_revision,
            },
            "changes": [c.to_dict() for c in changes],
        }

    async def get_audit_log(
        self,
        project_id: str | None = None,
        days: int = 7,
        entity_type: str | None = None,
    ) -> dict[str, Any]:
        """Get audit log for changes.

        Args:
            project_id: Optional project ID to filter by (not implemented in v1)
            days: Number of days to look back
            entity_type: Optional entity type filter

        Returns:
            Dictionary with changes and summary statistics
        """
        changes = await self._storage.get_audit_log(project_id, days, entity_type)

        # Build summary statistics
        by_author: dict[str, int] = {}
        by_action: dict[str, int] = {"created": 0, "updated": 0}
        by_type: dict[str, int] = {}

        for change in changes:
            # Count by author
            author = change["author"]
            by_author[author] = by_author.get(author, 0) + 1

            # Count by action (creation has revision_id == 1)
            if change["revision_id"] == 1:
                by_action["created"] += 1
            else:
                by_action["updated"] += 1

            # Count by type
            etype = change["entity_type"]
            by_type[etype] = by_type.get(etype, 0) + 1

        return {
            "changes": changes,
            "summary": {
                "total_changes": len(changes),
                "by_author": by_author,
                "by_action": by_action,
                "by_type": by_type,
            },
        }

    def _format_value(self, value: Any) -> Any:
        """Format a value for storage.

        Args:
            value: Value to format

        Returns:
            Formatted value suitable for JSON serialization
        """
        if value is None:
            return None
        elif isinstance(value, dict):
            # Handle complex types like select, relation, etc.
            if "name" in value:
                return value["name"]
            elif "title" in value:
                # Extract text content from title
                title_list = value["title"]
                if title_list and len(title_list) > 0:
                    return title_list[0].get("text", {}).get("content", "")
                return ""
            elif "rich_text" in value:
                # Extract text content from rich_text
                text_list = value["rich_text"]
                if text_list and len(text_list) > 0:
                    return text_list[0].get("text", {}).get("content", "")
                return ""
            elif "date" in value:
                date_obj = value["date"]
                if date_obj:
                    return date_obj.get("start", "")
                return ""
            else:
                return str(value)
        elif isinstance(value, list):
            # Handle multi-select or relations
            if len(value) > 0 and isinstance(value[0], dict):
                return [v.get("name", str(v)) for v in value]
            return value
        else:
            return value
