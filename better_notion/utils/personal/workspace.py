"""Personal workspace initialization."""

from __future__ import annotations

import json
import uuid
from datetime import datetime
from pathlib import Path

from better_notion._sdk.client import NotionClient


class PersonalWorkspaceInitializer:
    """Initialize personal workspace with all databases and relationships."""

    EXPECTED_DATABASES = [
        "Domains",
        "Tags",
        "Projects",
        "Tasks",
        "Routines",
        "Agenda",
    ]

    def __init__(self, client: NotionClient):
        """Initialize workspace initializer.

        Args:
            client: Notion client instance
        """
        self.client = client
        self._database_ids: dict[str, str] = {}
        self._parent_page_id: str = ""
        self._workspace_id: str = ""
        self._workspace_name: str = ""

    async def initialize_workspace(
        self,
        parent_page_id: str,
        workspace_name: str = "Personal Workspace",
        skip_detection: bool = False,
    ) -> dict[str, str]:
        """Create all personal databases with relationships.

        Args:
            parent_page_id: Parent page ID where databases will be created
            workspace_name: Name for the workspace
            skip_detection: If True, skip workspace detection

        Returns:
            Dictionary mapping database names to their IDs
        """
        from better_notion._sdk.models.database import Database

        self._parent_page_id = parent_page_id
        self._workspace_name = workspace_name
        self._workspace_id = f"personal-{uuid.uuid4().hex[:8]}"

        # Step 1: Create Domains database
        domain_db = await self._create_database(
            parent_page_id,
            "Domains",
            [
                {"name": "Name", "type": "title"},
                {"name": "Description", "type": "text"},
                {"name": "Color", "type": "select", "select": {"options": [
                    {"name": "Red", "color": "red"},
                    {"name": "Orange", "color": "orange"},
                    {"name": "Yellow", "color": "yellow"},
                    {"name": "Green", "color": "green"},
                    {"name": "Blue", "color": "blue"},
                    {"name": "Purple", "color": "purple"},
                    {"name": "Gray", "color": "gray"},
                ]}},
            ]
        )

        # Step 2: Create Tags database
        tag_db = await self._create_database(
            parent_page_id,
            "Tags",
            [
                {"name": "Name", "type": "title"},
                {"name": "Color", "type": "select", "select": {"options": [
                    {"name": "Red", "color": "red"},
                    {"name": "Orange", "color": "orange"},
                    {"name": "Yellow", "color": "yellow"},
                    {"name": "Green", "color": "green"},
                    {"name": "Blue", "color": "blue"},
                    {"name": "Purple", "color": "purple"},
                    {"name": "Gray", "color": "gray"},
                ]}},
                {"name": "Category", "type": "select", "select": {"options": [
                    {"name": "Context"},
                    {"name": "Energy"},
                    {"name": "Location"},
                    {"name": "Time"},
                    {"name": "Custom"},
                ]}},
                {"name": "Description", "type": "text"},
            ]
        )

        # Step 3: Create Projects database
        project_db = await self._create_database(
            parent_page_id,
            "Projects",
            [
                {"name": "Name", "type": "title"},
                {"name": "Status", "type": "select", "select": {"options": [
                    {"name": "Active", "color": "green"},
                    {"name": "On Hold", "color": "orange"},
                    {"name": "Completed", "color": "blue"},
                    {"name": "Archived", "color": "gray"},
                ]}},
                {"name": "Domain", "type": "relation", "relation": {
                    "database_id": domain_db.id,
                    "type": "single_property",
                }},
                {"name": "Deadline", "type": "date"},
                {"name": "Priority", "type": "select", "select": {"options": [
                    {"name": "Critical", "color": "red"},
                    {"name": "High", "color": "orange"},
                    {"name": "Medium", "color": "yellow"},
                    {"name": "Low", "color": "blue"},
                ]}},
                {"name": "Progress", "type": "number", "number": {"format": "percent"}},
                {"name": "Goal", "type": "text"},
                {"name": "Notes", "type": "text"},
            ]
        )

        # Step 4: Create Tasks database
        task_db = await self._create_database(
            parent_page_id,
            "Tasks",
            [
                {"name": "Title", "type": "title"},
                {"name": "Status", "type": "select", "select": {"options": [
                    {"name": "Todo", "color": "gray"},
                    {"name": "In Progress", "color": "blue"},
                    {"name": "Done", "color": "green"},
                    {"name": "Cancelled", "color": "red"},
                    {"name": "Archived", "color": "gray"},
                ]}},
                {"name": "Priority", "type": "select", "select": {"options": [
                    {"name": "Critical", "color": "red"},
                    {"name": "High", "color": "orange"},
                    {"name": "Medium", "color": "yellow"},
                    {"name": "Low", "color": "blue"},
                ]}},
                {"name": "Due Date", "type": "date"},
                {"name": "Domain", "type": "relation", "relation": {
                    "database_id": domain_db.id,
                    "type": "single_property",
                }},
                {"name": "Project", "type": "relation", "relation": {
                    "database_id": project_db.id,
                    "type": "single_property",
                }},
                # Note: Parent Task (self-referential) and Subtasks (rollup) properties
                # need to be added after database creation via a separate API update
                # because task_db.id doesn't exist yet at this point
                # TODO: Implement update operation to add these properties
                {"name": "Tags", "type": "relation", "relation": {
                    "database_id": tag_db.id,
                    "type": "dual_property",
                    "dual_property": "Tasks",
                }},
                {"name": "Estimated Time", "type": "number"},
                {"name": "Energy Required", "type": "select", "select": {"options": [
                    {"name": "High", "color": "red"},
                    {"name": "Medium", "color": "yellow"},
                    {"name": "Low", "color": "blue"},
                ]}},
                {"name": "Context", "type": "text"},
                {"name": "Created Date", "type": "date"},
                {"name": "Completed Date", "type": "date"},
                {"name": "Archived Date", "type": "date"},
            ]
        )

        # Step 5: Create Routines database
        routine_db = await self._create_database(
            parent_page_id,
            "Routines",
            [
                {"name": "Name", "type": "title"},
                {"name": "Frequency", "type": "select", "select": {"options": [
                    {"name": "Daily", "color": "blue"},
                    {"name": "Weekly", "color": "green"},
                    {"name": "Weekdays", "color": "yellow"},
                    {"name": "Weekends", "color": "purple"},
                ]}},
                {"name": "Domain", "type": "relation", "relation": {
                    "database_id": domain_db.id,
                    "type": "single_property",
                }},
                {"name": "Best Time", "type": "text"},
                {"name": "Estimated Duration", "type": "number"},
                {"name": "Streak", "type": "number"},
                {"name": "Last Completed", "type": "date"},
                {"name": "Total Completions", "type": "number"},
            ]
        )

        # Step 6: Create Agenda database
        agenda_db = await self._create_database(
            parent_page_id,
            "Agenda",
            [
                {"name": "Name", "type": "title"},
                {"name": "Date & Time", "type": "date"},
                {"name": "Duration", "type": "number"},
                {"name": "Type", "type": "select", "select": {"options": [
                    {"name": "Event", "color": "blue"},
                    {"name": "Time Block", "color": "green"},
                    {"name": "Reminder", "color": "yellow"},
                ]}},
                {"name": "Linked Task", "type": "relation", "relation": {
                    "database_id": task_db.id,
                    "type": "single_property",
                }},
                {"name": "Linked Project", "type": "relation", "relation": {
                    "database_id": project_db.id,
                    "type": "single_property",
                }},
                {"name": "Location", "type": "text"},
                {"name": "Notes", "type": "text"},
            ]
        )

        # Store database IDs
        self._database_ids = {
            "domains": domain_db.id,
            "tags": tag_db.id,
            "projects": project_db.id,
            "tasks": task_db.id,
            "routines": routine_db.id,
            "agenda": agenda_db.id,
        }

        # Save configuration
        self.save_database_ids()

        return self._database_ids

    async def _create_database(
        self,
        parent_page_id: str,
        title: str,
        properties: list[dict],
    ):
        """Create a Notion database with given properties.

        Args:
            parent_page_id: Parent page ID
            title: Database title
            properties: List of property definitions

        Returns:
            Created Database object
        """

        # Format properties for API
        schema_properties = []
        for prop in properties:
            prop_schema = {"name": prop["name"], "type": prop["type"]}

            if prop["type"] == "title":
                prop_schema["title"] = {}
            elif prop["type"] == "text":
                prop_schema["text"] = {}
            elif prop["type"] == "number":
                prop_schema["number"] = {"format": prop.get("format", "number")}
            elif prop["type"] == "select":
                prop_schema["select"] = prop["select"]
            elif prop["type"] == "date":
                prop_schema["date"] = {}
            elif prop["type"] == "relation":
                prop_schema["relation"] = prop["relation"]
            elif prop["type"] == "rollup":
                prop_schema["rollup"] = prop["rollup"]

            schema_properties.append(prop_schema)

        # Create database via API
        parent = {"type": "page_id", "page_id": parent_page_id}

        # Log the request payload for debugging
        import json
        request_payload = {
            "parent": parent,
            "title": title,
            "properties": schema_properties,
        }
        print(f"[DEBUG] Creating database '{title}' with schema:", file=__import__('sys').stderr)
        print(json.dumps(request_payload, indent=2), file=__import__('sys').stderr)

        try:
            response = await self.client.api.databases.create(
                parent=parent,
                title=title,
                properties=schema_properties,
            )
            print(f"[DEBUG] Database '{title}' created successfully: {response.get('id')}", file=__import__('sys').stderr)
        except Exception as e:
            print(f"[ERROR] Failed to create database '{title}': {e}", file=__import__('sys').stderr)
            if hasattr(e, 'response'):
                print(f"[ERROR] API Response: {e.response.text if hasattr(e.response, 'text') else e.response}", file=__import__('sys').stderr)
            raise

        from better_notion._sdk.models.database import Database
        return Database(data=response, client=self.client)

    def save_database_ids(self) -> None:
        """Save database IDs and workspace configuration to disk."""
        config = {
            "workspace_id": self._workspace_id,
            "workspace_name": self._workspace_name,
            "parent_page_id": self._parent_page_id,
            "database_ids": self._database_ids,
            "initialized_at": datetime.now().isoformat(),
            "version": "1.0.0",
        }

        config_path = Path.home() / ".notion" / "personal.json"
        config_path.parent.mkdir(parents=True, exist_ok=True)

        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2)

    @staticmethod
    def load_parent_page() -> str | None:
        """Load parent page ID from saved config.

        Returns:
            Parent page ID if found, None otherwise
        """
        from better_notion.utils.personal.metadata import PersonalWorkspaceMetadata, CONFIG_PATH

        if CONFIG_PATH.exists():
            with open(CONFIG_PATH, encoding="utf-8") as f:
                config = json.load(f)
                return config.get("parent_page_id")
        return None
