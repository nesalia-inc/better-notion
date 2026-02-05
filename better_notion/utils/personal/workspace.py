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

        # Helper function to find existing database
        async def find_existing_database(title: str) -> str | None:
            """Check if a database with given title already exists in the parent page."""
            from better_notion._api.collections import DatabaseCollection

            # Query for child databases in the parent page
            # We need to search through children to find databases
            try:
                # Get all children blocks
                response = await self.client._api._request(
                    "GET",
                    f"/blocks/{parent_page_id}/children"
                )

                for child in response.get("results", []):
                    if child.get("type") == "database":
                        # Get database details to check title
                        db_response = await self.client._api._request(
                            "GET",
                            f"/databases/{child['id']}"
                        )
                        db_title = db_response.get("title", [])
                        if db_title and len(db_title) > 0:
                            title_text = db_title[0].get("plain_text", "")
                            if title_text == title:
                                return child["id"]
            except Exception:
                # If search fails, proceed with creation
                pass

            return None

        # Step 1: Create Domains database (or reuse existing)
        existing_domains_id = await find_existing_database("Domains")
        if existing_domains_id:
            print(f"[DEBUG] Reusing existing Domains database: {existing_domains_id}")
            domain_id = existing_domains_id
        else:
            print(f"[DEBUG] Creating new Domains database")
            domain_db = await self._create_database(
                parent_page_id,
                "Domains",
                [
                    {"name": "Name", "type": "title"},
                    {"name": "Description", "type": "rich_text"},
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
            domain_id = domain_db.id
            print(f"[DEBUG] Domains database created: {domain_id}")
        domain_db = type('obj', (object,), {'id': domain_id})  # Mock object with id attribute

        # Step 2: Create Tags database (or reuse existing)
        existing_tags_id = await find_existing_database("Tags")
        if existing_tags_id:
            print(f"[DEBUG] Reusing existing Tags database: {existing_tags_id}")
            tag_id = existing_tags_id
        else:
            print(f"[DEBUG] Creating new Tags database")
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
                    {"name": "Description", "type": "rich_text"},
                ]
            )
            tag_id = tag_db.id
            print(f"[DEBUG] Tags database created: {tag_id}")
        tag_db = type('obj', (object,), {'id': tag_id})  # Mock object with id attribute

        # Step 3: Create Projects database (or reuse existing)
        existing_projects_id = await find_existing_database("Projects")
        if existing_projects_id:
            print(f"[DEBUG] Reusing existing Projects database: {existing_projects_id}")
            project_id = existing_projects_id
        else:
            print(f"[DEBUG] Creating new Projects database")
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
                        "data_source_id": domain_db.id,
                        "single_property": {},
                    }},
                    {"name": "Deadline", "type": "date"},
                    {"name": "Priority", "type": "select", "select": {"options": [
                        {"name": "Critical", "color": "red"},
                        {"name": "High", "color": "orange"},
                        {"name": "Medium", "color": "yellow"},
                        {"name": "Low", "color": "blue"},
                    ]}},
                    {"name": "Progress", "type": "number", "number": {"format": "percent"}},
                    {"name": "Goal", "type": "rich_text"},
                    {"name": "Notes", "type": "rich_text"},
                ]
            )
            project_id = project_db.id
            print(f"[DEBUG] Projects database created: {project_id}")
        project_db = type('obj', (object,), {'id': project_id})  # Mock object with id attribute

        # Step 4: Create Tasks database (or reuse existing)
        existing_tasks_id = await find_existing_database("Tasks")
        if existing_tasks_id:
            print(f"[DEBUG] Reusing existing Tasks database: {existing_tasks_id}")
            task_id = existing_tasks_id
        else:
            print(f"[DEBUG] Creating new Tasks database")
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
                        "data_source_id": domain_db.id,
                        "single_property": {},
                    }},
                    {"name": "Project", "type": "relation", "relation": {
                        "data_source_id": project_db.id,
                        "single_property": {},
                    }},
                    # Note: Parent Task (self-referential) and Subtasks (rollup) properties
                    # need to be added after database creation via a separate API update
                    # because task_db.id doesn't exist yet at this point
                    # TODO: Implement update operation to add these properties
                    {"name": "Tags", "type": "relation", "relation": {
                        "data_source_id": tag_db.id,
                        "dual_property": {
                            "synced_property_name": "Tasks"
                        },
                    }},
                    {"name": "Estimated Time", "type": "number"},
                    {"name": "Energy Required", "type": "select", "select": {"options": [
                        {"name": "High", "color": "red"},
                        {"name": "Medium", "color": "yellow"},
                        {"name": "Low", "color": "blue"},
                    ]}},
                    {"name": "Context", "type": "rich_text"},
                    {"name": "Created Date", "type": "date"},
                    {"name": "Completed Date", "type": "date"},
                    {"name": "Archived Date", "type": "date"},
                ]
            )
            task_id = task_db.id
            print(f"[DEBUG] Tasks database created: {task_id}")
        task_db = type('obj', (object,), {'id': task_id})  # Mock object with id attribute

        # Step 5: Create Routines database (or reuse existing)
        existing_routines_id = await find_existing_database("Routines")
        if existing_routines_id:
            print(f"[DEBUG] Reusing existing Routines database: {existing_routines_id}")
            routine_id = existing_routines_id
        else:
            print(f"[DEBUG] Creating new Routines database")
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
                        "data_source_id": domain_db.id,
                        "single_property": {},
                    }},
                    {"name": "Best Time", "type": "rich_text"},
                    {"name": "Estimated Duration", "type": "number"},
                    {"name": "Streak", "type": "number"},
                    {"name": "Last Completed", "type": "date"},
                    {"name": "Total Completions", "type": "number"},
                ]
            )
            routine_id = routine_db.id
            print(f"[DEBUG] Routines database created: {routine_id}")
        routine_db = type('obj', (object,), {'id': routine_id})  # Mock object with id attribute

        # Step 6: Create Agenda database (or reuse existing)
        existing_agenda_id = await find_existing_database("Agenda")
        if existing_agenda_id:
            print(f"[DEBUG] Reusing existing Agenda database: {existing_agenda_id}")
            agenda_id = existing_agenda_id
        else:
            print(f"[DEBUG] Creating new Agenda database")
            agenda_db = await self._create_database(
                parent_page_id,
                "Agenda",
                [
                    {"name": "Name", "type": "title"},
                    {"name": "Start", "type": "date"},
                    {"name": "End", "type": "date"},
                    {"name": "Type", "type": "select", "select": {"options": [
                        {"name": "Event", "color": "blue"},
                        {"name": "Time Block", "color": "green"},
                        {"name": "Reminder", "color": "yellow"},
                    ]}},
                    {"name": "Linked Task", "type": "relation", "relation": {
                        "data_source_id": task_db.id,
                        "single_property": {},
                    }},
                    {"name": "Linked Project", "type": "relation", "relation": {
                        "data_source_id": project_db.id,
                        "single_property": {},
                    }},
                    {"name": "Location", "type": "rich_text"},
                    {"name": "Notes", "type": "rich_text"},
                ]
            )
            agenda_id = agenda_db.id
            print(f"[DEBUG] Agenda database created: {agenda_id}")
        agenda_db = type('obj', (object,), {'id': agenda_id})  # Mock object with id attribute

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
        # Notion API expects properties as a dict (not a list)
        # with property names as keys
        schema_properties = {}
        for prop in properties:
            prop_name = prop["name"]
            prop_type = prop["type"]

            # Build property schema without "name" field
            prop_schema = {"type": prop_type}

            if prop_type == "title":
                prop_schema["title"] = {}
            elif prop_type == "rich_text":
                prop_schema["rich_text"] = {}
            elif prop_type == "number":
                # Get number config from prop["number"] or default to {"format": "number"}
                number_config = prop.get("number", {"format": "number"})
                prop_schema["number"] = number_config
            elif prop_type == "select":
                prop_schema["select"] = prop["select"]
            elif prop_type == "date":
                prop_schema["date"] = {}
            elif prop_type == "relation":
                # Fix relation format for Notion API
                relation_config = prop["relation"].copy()
                # Convert data_source_id to database_id for /databases endpoint
                if "data_source_id" in relation_config:
                    relation_config["database_id"] = relation_config.pop("data_source_id")
                prop_schema["relation"] = relation_config
            elif prop_type == "rollup":
                prop_schema["rollup"] = prop["rollup"]
            # For date, checkbox, etc.: no additional fields needed

            schema_properties[prop_name] = prop_schema

        # Create database via API using the DatabaseCollection
        from better_notion._api.collections import DatabaseCollection

        # Create a DatabaseCollection instance
        db_collection = DatabaseCollection(self.client._api)

        # Log the request payload for debugging
        import json
        request_payload = {
            "parent": {"type": "page_id", "page_id": parent_page_id},
            "title": title,
            "properties": schema_properties,
        }
        print(f"[DEBUG] Creating database '{title}' with schema:", file=__import__('sys').stderr)
        print(json.dumps(request_payload, indent=2), file=__import__('sys').stderr)

        try:
            response = await db_collection.create(
                parent=request_payload["parent"],
                title=title,
                properties=schema_properties,
            )
            print(f"[DEBUG] Database '{title}' created successfully: {response.get('id')}", file=__import__('sys').stderr)
        except Exception as e:
            print(f"[ERROR] Failed to create database '{title}': {type(e).__name__}: {e}", file=__import__('sys').stderr)
            # Try to get more error details
            import traceback
            print(f"[ERROR] Traceback: {traceback.format_exc()}", file=__import__('sys').stderr)
            if hasattr(e, 'args') and e.args:
                print(f"[ERROR] Exception args: {e.args}", file=__import__('sys').stderr)
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
