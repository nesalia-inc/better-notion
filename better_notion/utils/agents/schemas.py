"""Database schema builders for the agents workflow system.

This module provides schema builders for creating Notion databases with the
correct structure for the workflow management system.
"""

from typing import Any, Dict, List, Optional


class SelectOption:
    """Helper class for building select option properties."""

    @staticmethod
    def option(name: str, color: str = "default") -> Dict[str, str]:
        """Create a select option.

        Args:
            name: Option name
            color: Option color (default, gray, brown, orange, yellow, green,
                   blue, purple, pink, red)

        Returns:
            Select option dict

        Example:
            >>> SelectOption.option("Done", "green")
            {"name": "Done", "color": "green"}
        """
        return {"name": name, "color": color}

    @staticmethod
    def options(*names: str) -> List[Dict[str, str]]:
        """Create multiple select options with default colors.

        Args:
            *names: Option names

        Returns:
            List of select option dicts

        Example:
            >>> SelectOption.options("To Do", "In Progress", "Done")
            [
                {"name": "To Do", "color": "default"},
                {"name": "In Progress", "color": "default"},
                {"name": "Done", "color": "default"}
            ]
        """
        return [{"name": name, "color": "default"} for name in names]


class PropertyBuilder:
    """
    Helper class for building Notion database properties.

    Notion API create format:
        "Name": {"title": {}}
        "Status": {"select": {"options": [...]}}
    """

    @staticmethod
    def title(name: str = "Name") -> Dict[str, Any]:
        """
        Create a title property.

        Args:
            name: Property name (default: "Name")

        Returns:
            Title property schema for Notion API create
        """
        return {"title": {}}

    @staticmethod
    def text(name: str) -> Dict[str, Any]:
        """
        Create a text property.

        Args:
            name: Property name

        Returns:
            Text property schema for Notion API create
        """
        return {"rich_text": {}}

    @staticmethod
    def number(name: str, format: Optional[str] = None) -> Dict[str, Any]:
        """
        Create a number property.

        Args:
            name: Property name
            format: Number format (number, percent, dollar, euro, pound, yen, ruble)

        Returns:
            Number property schema for Notion API create
        """
        if format:
            return {"number": {"format": format}}
        return {"number": {}}

    @staticmethod
    def select(name: str, options: List[Dict[str, str]]) -> Dict[str, Any]:
        """
        Create a select property.

        Args:
            name: Property name
            options: List of option dicts from SelectOption.option()

        Returns:
            Select property schema for Notion API create
        """
        return {"select": {"options": options}}

    @staticmethod
    def multi_select(name: str, options: List[Dict[str, str]]) -> Dict[str, Any]:
        """
        Create a multi-select property.

        Args:
            name: Property name
            options: List of option dicts

        Returns:
            Multi-select property schema for Notion API create
        """
        return {"multi_select": {"options": options}}

    @staticmethod
    def date(name: str) -> Dict[str, Any]:
        """
        Create a date property.

        Args:
            name: Property name

        Returns:
            Date property schema for Notion API create
        """
        return {"date": {}}

    @staticmethod
    def checkbox(name: str) -> Dict[str, Any]:
        """
        Create a checkbox property.

        Args:
            name: Property name

        Returns:
            Checkbox property schema for Notion API create
        """
        return {"checkbox": {}}

    @staticmethod
    def url(name: str) -> Dict[str, Any]:
        """
        Create a URL property.

        Args:
            name: Property name

        Returns:
            URL property schema for Notion API create
        """
        return {"url": {}}

    @staticmethod
    def email(name: str) -> Dict[str, Any]:
        """
        Create an email property.

        Args:
            name: Property name

        Returns:
            Email property schema for Notion API create
        """
        return {"email": {}}

    @staticmethod
    def phone(name: str) -> Dict[str, Any]:
        """
        Create a phone property.

        Args:
            name: Property name

        Returns:
            Phone property schema for Notion API create
        """
        return {"phone_number": {}}

    @staticmethod
    def people(name: str) -> Dict[str, Any]:
        """
        Create a people property.

        Args:
            name: Property name

        Returns:
            People property schema for Notion API create
        """
        return {"people": {}}

    @staticmethod
    def files(name: str) -> Dict[str, Any]:
        """
        Create a files property.

        Args:
            name: Property name

        Returns:
            Files property schema for Notion API create
        """
        return {"files": {}}

    @staticmethod
    def relation(
        name: str,
        database_id: Optional[str] = None,
        dual_property: bool = True,
    ) -> Dict[str, Any]:
        """
        Create a relation property.

        Args:
            name: Property name
            database_id: Related database ID (can be set later)
            dual_property: Whether to create dual_property relation (bidirectional)

        Returns:
            Relation property schema

        Note:
            If database_id is None, it must be set later when the related
            database is created.
        """
        relation_config: Dict[str, Any] = {}

        if database_id:
            relation_config["database_id"] = database_id

        if dual_property:
            relation_config["dual_property"] = {}
        else:
            relation_config["single_property"] = {}

        return {"relation": relation_config}

    @staticmethod
    def formula(name: str, expression: str) -> Dict[str, Any]:
        """
        Create a formula property.

        Args:
            name: Property name
            expression: Formula expression

        Returns:
            Formula property schema
        """
        return {"formula": {"expression": expression}}

    @staticmethod
    def created_time(name: str = "Created time") -> Dict[str, Any]:
        """
        Create a created_time property.

        Args:
            name: Property name (default: "Created time")

        Returns:
            Created time property schema
        """
        return {"created_time": {}}

    @staticmethod
    def created_by(name: str = "Created by") -> Dict[str, Any]:
        """
        Create a created_by property.

        Args:
            name: Property name (default: "Created by")

        Returns:
            Created by property schema
        """
        return {"created_by": {}}


class OrganizationSchema:
    """Schema builder for Organizations database."""

    @staticmethod
    def get_schema() -> Dict[str, Dict[str, Any]]:
        """
        Return Notion database schema for Organizations.

        Returns:
            Dict mapping property names to property schemas

        Example:
            >>> schema = OrganizationSchema.get_schema()
            >>> # Use with Notion API to create database
        """
        return {
            "Name": PropertyBuilder.title("Name"),
            "Slug": PropertyBuilder.text("Slug"),
            "Description": PropertyBuilder.text("Description"),
            "Repository URL": PropertyBuilder.url("Repository URL"),
            "Status": PropertyBuilder.select(
                "Status",
                [
                    SelectOption.option("Active", "green"),
                    SelectOption.option("Archived", "gray"),
                    SelectOption.option("On Hold", "yellow"),
                ],
            ),
        }


class ProjectSchema:
    """Schema builder for Projects database."""

    @staticmethod
    def get_schema() -> Dict[str, Dict[str, Any]]:
        """Return Notion database schema for Projects."""
        return {
            "Name": PropertyBuilder.title("Name"),
            "Organization": PropertyBuilder.relation("Organization"),
            "Slug": PropertyBuilder.text("Slug"),
            "Description": PropertyBuilder.text("Description"),
            "Repository": PropertyBuilder.url("Repository"),
            "Status": PropertyBuilder.select(
                "Status",
                [
                    SelectOption.option("Active", "green"),
                    SelectOption.option("Archived", "gray"),
                    SelectOption.option("Planning", "blue"),
                    SelectOption.option("Completed", "purple"),
                ],
            ),
            "Tech Stack": PropertyBuilder.multi_select(
                "Tech Stack",
                [
                    SelectOption.option("Python", "blue"),
                    SelectOption.option("JavaScript", "yellow"),
                    SelectOption.option("TypeScript", "blue"),
                    SelectOption.option("React", "blue"),
                    SelectOption.option("Vue", "green"),
                    SelectOption.option("Node.js", "green"),
                    SelectOption.option("Go", "blue"),
                    SelectOption.option("Rust", "orange"),
                    SelectOption.option("Java", "red"),
                    SelectOption.option("C++", "blue"),
                    SelectOption.option("SQL", "purple"),
                    SelectOption.option("NoSQL", "pink"),
                ],
            ),
            "Role": PropertyBuilder.select(
                "Role",
                [
                    SelectOption.option("Developer", "blue"),
                    SelectOption.option("PM", "purple"),
                    SelectOption.option("Product Analyst", "orange"),
                    SelectOption.option("QA", "green"),
                    SelectOption.option("Designer", "pink"),
                    SelectOption.option("DevOps", "gray"),
                    SelectOption.option("Admin", "red"),
                ],
            ),
        }


class VersionSchema:
    """Schema builder for Versions database."""

    @staticmethod
    def get_schema() -> Dict[str, Dict[str, Any]]:
        """Return Notion database schema for Versions."""
        return {
            "Version": PropertyBuilder.title("Version"),
            "Project": PropertyBuilder.relation("Project"),
            "Status": PropertyBuilder.select(
                "Status",
                [
                    SelectOption.option("Planning", "gray"),
                    SelectOption.option("Alpha", "blue"),
                    SelectOption.option("Beta", "purple"),
                    SelectOption.option("RC", "orange"),
                    SelectOption.option("In Progress", "yellow"),
                    SelectOption.option("Released", "green"),
                    SelectOption.option("On Hold", "default"),
                    SelectOption.option("Cancelled", "red"),
                ],
            ),
            "Type": PropertyBuilder.select(
                "Type",
                [
                    SelectOption.option("Major", "red"),
                    SelectOption.option("Minor", "orange"),
                    SelectOption.option("Patch", "yellow"),
                    SelectOption.option("Hotfix", "red"),
                ],
            ),
            "Branch Name": PropertyBuilder.text("Branch Name"),
            "Progress": PropertyBuilder.number("Progress", format="percent"),
            "Release Date": PropertyBuilder.date("Release Date"),
            # Note: "Superseded By" self-referential relation removed because
            # it can't be created during initial database creation (needs its own ID)
        }


class TaskSchema:
    """Schema builder for Tasks database."""

    @staticmethod
    def get_schema() -> Dict[str, Dict[str, Any]]:
        """Return Notion database schema for Tasks."""
        return {
            "Title": PropertyBuilder.title("Title"),
            "Version": PropertyBuilder.relation("Version"),
            "Target Version": PropertyBuilder.relation("Target Version", dual_property=False),
            "Type": PropertyBuilder.select(
                "Type",
                [
                    SelectOption.option("New Feature", "green"),
                    SelectOption.option("Refactor", "blue"),
                    SelectOption.option("Documentation", "gray"),
                    SelectOption.option("Test", "purple"),
                    SelectOption.option("Bug Fix", "red"),
                    SelectOption.option("Performance", "orange"),
                    SelectOption.option("Security", "red"),
                ],
            ),
            "Status": PropertyBuilder.select(
                "Status",
                [
                    SelectOption.option("Backlog", "gray"),
                    SelectOption.option("Claimed", "blue"),
                    SelectOption.option("In Progress", "yellow"),
                    SelectOption.option("In Review", "purple"),
                    SelectOption.option("Completed", "green"),
                    SelectOption.option("Cancelled", "red"),
                ],
            ),
            "Priority": PropertyBuilder.select(
                "Priority",
                [
                    SelectOption.option("Critical", "red"),
                    SelectOption.option("High", "orange"),
                    SelectOption.option("Medium", "yellow"),
                    SelectOption.option("Low", "blue"),
                ],
            ),
            # Note: Self-referential relations (Dependencies, Dependent Tasks) removed because
            # they can't be created during initial database creation (need the database's own ID)
            "Estimated Hours": PropertyBuilder.number("Estimated Hours"),
            "Actual Hours": PropertyBuilder.number("Actual Hours"),
            "Assignee": PropertyBuilder.people("Assignee"),
            "Created Date": PropertyBuilder.date("Created Date"),
            "Completed Date": PropertyBuilder.date("Completed Date"),
        }


class IdeaSchema:
    """Schema builder for Ideas database."""

    @staticmethod
    def get_schema() -> Dict[str, Dict[str, Any]]:
        """Return Notion database schema for Ideas."""
        return {
            "Title": PropertyBuilder.title("Title"),
            "Project": PropertyBuilder.relation("Project"),
            "Category": PropertyBuilder.select(
                "Category",
                [
                    SelectOption.option("Feature", "green"),
                    SelectOption.option("Improvement", "blue"),
                    SelectOption.option("Refactor", "purple"),
                    SelectOption.option("Process", "orange"),
                    SelectOption.option("Tool", "pink"),
                ],
            ),
            "Status": PropertyBuilder.select(
                "Status",
                [
                    SelectOption.option("New", "gray"),
                    SelectOption.option("Evaluated", "blue"),
                    SelectOption.option("Accepted", "green"),
                    SelectOption.option("Rejected", "red"),
                    SelectOption.option("Deferred", "yellow"),
                ],
            ),
            "Description": PropertyBuilder.text("Description"),
            "Proposed Solution": PropertyBuilder.text("Proposed Solution"),
            "Benefits": PropertyBuilder.text("Benefits"),
            "Effort Estimate": PropertyBuilder.select(
                "Effort Estimate",
                [
                    SelectOption.option("Small", "green"),
                    SelectOption.option("Medium", "yellow"),
                    SelectOption.option("Large", "red"),
                ],
            ),
            "Context": PropertyBuilder.text("Context"),
            "Related Task": PropertyBuilder.relation("Related Task", dual_property=False),
        }


class WorkIssueSchema:
    """Schema builder for Work Issues database."""

    @staticmethod
    def get_schema() -> Dict[str, Dict[str, Any]]:
        """Return Notion database schema for Work Issues."""
        return {
            "Title": PropertyBuilder.title("Title"),
            "Project": PropertyBuilder.relation("Project"),
            "Task": PropertyBuilder.relation("Task"),
            "Type": PropertyBuilder.select(
                "Type",
                [
                    SelectOption.option("Blocker", "red"),
                    SelectOption.option("Confusion", "yellow"),
                    SelectOption.option("Documentation", "gray"),
                    SelectOption.option("Tooling", "orange"),
                    SelectOption.option("Process", "purple"),
                ],
            ),
            "Severity": PropertyBuilder.select(
                "Severity",
                [
                    SelectOption.option("Critical", "red"),
                    SelectOption.option("High", "orange"),
                    SelectOption.option("Medium", "yellow"),
                    SelectOption.option("Low", "blue"),
                ],
            ),
            "Status": PropertyBuilder.select(
                "Status",
                [
                    SelectOption.option("Open", "red"),
                    SelectOption.option("Investigating", "yellow"),
                    SelectOption.option("Resolved", "green"),
                    SelectOption.option("Won't Fix", "gray"),
                    SelectOption.option("Deferred", "blue"),
                ],
            ),
            "Description": PropertyBuilder.text("Description"),
            "Context": PropertyBuilder.text("Context"),
            "Proposed Solution": PropertyBuilder.text("Proposed Solution"),
            "Related Idea": PropertyBuilder.relation("Related Idea", dual_property=False),
            "Fix Tasks": PropertyBuilder.relation("Fix Tasks", dual_property=False),
        }


class IncidentSchema:
    """Schema builder for Incidents database."""

    @staticmethod
    def get_schema() -> Dict[str, Dict[str, Any]]:
        """Return Notion database schema for Incidents."""
        return {
            "Title": PropertyBuilder.title("Title"),
            "Project": PropertyBuilder.relation("Project"),
            "Affected Version": PropertyBuilder.relation("Affected Version"),
            "Severity": PropertyBuilder.select(
                "Severity",
                [
                    SelectOption.option("Critical", "red"),
                    SelectOption.option("High", "orange"),
                    SelectOption.option("Medium", "yellow"),
                    SelectOption.option("Low", "blue"),
                ],
            ),
            "Type": PropertyBuilder.select(
                "Type",
                [
                    SelectOption.option("Bug", "red"),
                    SelectOption.option("Crash", "purple"),
                    SelectOption.option("Performance", "orange"),
                    SelectOption.option("Security", "red"),
                    SelectOption.option("Data Loss", "red"),
                ],
            ),
            "Status": PropertyBuilder.select(
                "Status",
                [
                    SelectOption.option("Open", "red"),
                    SelectOption.option("Investigating", "yellow"),
                    SelectOption.option("Fix In Progress", "blue"),
                    SelectOption.option("Resolved", "green"),
                ],
            ),
            "Fix Task": PropertyBuilder.relation("Fix Task", dual_property=False),
            "Root Cause": PropertyBuilder.text("Root Cause"),
            "Detected Date": PropertyBuilder.date("Detected Date"),
            "Resolved Date": PropertyBuilder.date("Resolved Date"),
        }


class TagSchema:
    """Schema builder for Tags database."""

    @staticmethod
    def get_schema() -> Dict[str, Dict[str, Any]]:
        """Return Notion database schema for Tags."""
        return {
            "Name": PropertyBuilder.title("Name"),
            "Category": PropertyBuilder.select(
                "Category",
                [
                    SelectOption.option("Type", "blue"),
                    SelectOption.option("Domain", "green"),
                    SelectOption.option("Component", "purple"),
                    SelectOption.option("Priority", "orange"),
                ],
            ),
            "Color": PropertyBuilder.select(
                "Color",
                [
                    SelectOption.option("Red", "red"),
                    SelectOption.option("Orange", "orange"),
                    SelectOption.option("Yellow", "yellow"),
                    SelectOption.option("Green", "green"),
                    SelectOption.option("Blue", "blue"),
                    SelectOption.option("Purple", "purple"),
                ],
            ),
            "Description": PropertyBuilder.text("Description"),
        }
