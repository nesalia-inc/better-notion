"""Unit tests for database schema builders."""

import pytest

from better_notion.utils.agents.schemas import (
    IncidentSchema,
    IdeaSchema,
    OrganizationSchema,
    ProjectSchema,
    PropertyBuilder,
    SelectOption,
    TagSchema,
    TaskSchema,
    VersionSchema,
    WorkIssueSchema,
)


class TestSelectOption:
    """Tests for SelectOption helper."""

    def test_option_default_color(self) -> None:
        """Test creating option with default color."""
        option = SelectOption.option("Test")

        assert option == {"name": "Test", "color": "default"}

    def test_option_custom_color(self) -> None:
        """Test creating option with custom color."""
        option = SelectOption.option("Test", "green")

        assert option == {"name": "Test", "color": "green"}

    def test_options_multiple(self) -> None:
        """Test creating multiple options."""
        options = SelectOption.options("A", "B", "C")

        assert len(options) == 3
        assert options[0] == {"name": "A", "color": "default"}
        assert options[1] == {"name": "B", "color": "default"}
        assert options[2] == {"name": "C", "color": "default"}


class TestPropertyBuilder:
    """Tests for PropertyBuilder helper."""

    def test_title_default_name(self) -> None:
        """Test creating title property with default name."""
        prop = PropertyBuilder.title()

        assert prop["type"] == "title"
        assert prop["name"] == "Name"

    def test_title_custom_name(self) -> None:
        """Test creating title property with custom name."""
        prop = PropertyBuilder.title("Custom")

        assert prop["type"] == "title"
        assert prop["name"] == "Custom"

    def test_text(self) -> None:
        """Test creating text property."""
        prop = PropertyBuilder.text("Description")

        assert prop["type"] == "rich_text"
        assert prop["name"] == "Description"

    def test_number_no_format(self) -> None:
        """Test creating number property without format."""
        prop = PropertyBuilder.number("Count")

        assert prop["type"] == "number"
        assert prop["name"] == "Count"
        assert "number" not in prop or "format" not in prop.get("number", {})

    def test_number_with_format(self) -> None:
        """Test creating number property with format."""
        prop = PropertyBuilder.number("Percentage", "percent")

        assert prop["type"] == "number"
        assert prop["name"] == "Percentage"
        assert prop["number"]["format"] == "percent"

    def test_select(self) -> None:
        """Test creating select property."""
        options = [SelectOption.option("A", "red"), SelectOption.option("B", "blue")]
        prop = PropertyBuilder.select("Status", options)

        assert prop["type"] == "select"
        assert prop["name"] == "Status"
        assert len(prop["select"]["options"]) == 2

    def test_multi_select(self) -> None:
        """Test creating multi-select property."""
        options = SelectOption.options("X", "Y", "Z")
        prop = PropertyBuilder.multi_select("Tags", options)

        assert prop["type"] == "multi_select"
        assert prop["name"] == "Tags"
        assert len(prop["multi_select"]["options"]) == 3

    def test_date(self) -> None:
        """Test creating date property."""
        prop = PropertyBuilder.date("Due Date")

        assert prop["type"] == "date"
        assert prop["name"] == "Due Date"

    def test_checkbox(self) -> None:
        """Test creating checkbox property."""
        prop = PropertyBuilder.checkbox("Done")

        assert prop["type"] == "checkbox"
        assert prop["name"] == "Done"

    def test_url(self) -> None:
        """Test creating URL property."""
        prop = PropertyBuilder.url("Website")

        assert prop["type"] == "url"
        assert prop["name"] == "Website"

    def test_email(self) -> None:
        """Test creating email property."""
        prop = PropertyBuilder.email("Contact")

        assert prop["type"] == "email"
        assert prop["name"] == "Contact"

    def test_phone(self) -> None:
        """Test creating phone property."""
        prop = PropertyBuilder.phone("Phone")

        assert prop["type"] == "phone"
        assert prop["name"] == "Phone"

    def test_people(self) -> None:
        """Test creating people property."""
        prop = PropertyBuilder.people("Assignee")

        assert prop["type"] == "people"
        assert prop["name"] == "Assignee"

    def test_files(self) -> None:
        """Test creating files property."""
        prop = PropertyBuilder.files("Attachments")

        assert prop["type"] == "files"
        assert prop["name"] == "Attachments"

    def test_relation_without_database_id(self) -> None:
        """Test creating relation property without database ID."""
        prop = PropertyBuilder.relation("Related")

        assert prop["type"] == "relation"
        assert prop["name"] == "Related"
        assert "database_id" not in prop.get("relation", {})

    def test_relation_with_database_id(self) -> None:
        """Test creating relation property with database ID."""
        prop = PropertyBuilder.relation("Related", database_id="db123")

        assert prop["type"] == "relation"
        assert prop["name"] == "Related"
        assert prop["relation"]["database_id"] == "db123"

    def test_relation_dual_property(self) -> None:
        """Test creating dual_property relation."""
        prop = PropertyBuilder.relation("Related", dual_property=True)

        assert prop["relation"]["type"] == "dual_property"

    def test_relation_single_property(self) -> None:
        """Test creating single_property relation."""
        prop = PropertyBuilder.relation("Related", dual_property=False)

        assert "type" not in prop.get("relation", {})

    def test_formula(self) -> None:
        """Test creating formula property."""
        prop = PropertyBuilder.formula("Calc", "1 + 1")

        assert prop["type"] == "formula"
        assert prop["name"] == "Calc"
        assert prop["formula"]["expression"] == "1 + 1"

    def test_created_time_default_name(self) -> None:
        """Test creating created_time property with default name."""
        prop = PropertyBuilder.created_time()

        assert prop["type"] == "created_time"
        assert prop["name"] == "Created time"

    def test_created_time_custom_name(self) -> None:
        """Test creating created_time property with custom name."""
        prop = PropertyBuilder.created_time("Timestamp")

        assert prop["type"] == "created_time"
        assert prop["name"] == "Timestamp"

    def test_created_by_default_name(self) -> None:
        """Test creating created_by property with default name."""
        prop = PropertyBuilder.created_by()

        assert prop["type"] == "created_by"
        assert prop["name"] == "Created by"

    def test_created_by_custom_name(self) -> None:
        """Test creating created_by property with custom name."""
        prop = PropertyBuilder.created_by("Author")

        assert prop["type"] == "created_by"
        assert prop["name"] == "Author"


class TestOrganizationSchema:
    """Tests for OrganizationSchema."""

    def test_get_schema_structure(self) -> None:
        """Test schema structure."""
        schema = OrganizationSchema.get_schema()

        assert isinstance(schema, dict)
        assert "Name" in schema
        assert "Slug" in schema
        assert "Description" in schema
        assert "Repository URL" in schema
        assert "Status" in schema

    def test_name_is_title(self) -> None:
        """Test Name property is title type."""
        schema = OrganizationSchema.get_schema()

        assert schema["Name"]["type"] == "title"

    def test_status_options(self) -> None:
        """Test Status property has correct options."""
        schema = OrganizationSchema.get_schema()

        options = schema["Status"]["select"]["options"]
        option_names = [opt["name"] for opt in options]

        assert "Active" in option_names
        assert "Archived" in option_names
        assert "On Hold" in option_names


class TestProjectSchema:
    """Tests for ProjectSchema."""

    def test_get_schema_structure(self) -> None:
        """Test schema structure."""
        schema = ProjectSchema.get_schema()

        assert "Name" in schema
        assert "Organization" in schema
        assert "Status" in schema
        assert "Tech Stack" in schema
        assert "Role" in schema

    def test_organization_is_relation(self) -> None:
        """Test Organization property is relation type."""
        schema = ProjectSchema.get_schema()

        assert schema["Organization"]["type"] == "relation"

    def test_tech_stack_is_multi_select(self) -> None:
        """Test Tech Stack property is multi_select type."""
        schema = ProjectSchema.get_schema()

        assert schema["Tech Stack"]["type"] == "multi_select"

    def test_role_options(self) -> None:
        """Test Role property has correct options."""
        schema = ProjectSchema.get_schema()

        options = schema["Role"]["select"]["options"]
        option_names = [opt["name"] for opt in options]

        assert "Developer" in option_names
        assert "PM" in option_names
        assert "QA" in option_names


class TestVersionSchema:
    """Tests for VersionSchema."""

    def test_get_schema_structure(self) -> None:
        """Test schema structure."""
        schema = VersionSchema.get_schema()

        assert "Version" in schema
        assert "Project" in schema
        assert "Status" in schema
        assert "Type" in schema
        assert "Progress" in schema

    def test_progress_is_percent(self) -> None:
        """Test Progress property is number with percent format."""
        schema = VersionSchema.get_schema()

        assert schema["Progress"]["type"] == "number"
        assert schema["Progress"]["number"]["format"] == "percent"


class TestTaskSchema:
    """Tests for TaskSchema."""

    def test_get_schema_structure(self) -> None:
        """Test schema structure."""
        schema = TaskSchema.get_schema()

        assert "Title" in schema
        assert "Version" in schema
        assert "Type" in schema
        assert "Status" in schema
        assert "Priority" in schema
        assert "Dependencies" in schema
        assert "Estimated Hours" in schema

    def test_status_options(self) -> None:
        """Test Status property has workflow states."""
        schema = TaskSchema.get_schema()

        options = schema["Status"]["select"]["options"]
        option_names = [opt["name"] for opt in options]

        assert "Backlog" in option_names
        assert "Claimed" in option_names
        assert "In Progress" in option_names
        assert "Completed" in option_names

    def test_priority_options(self) -> None:
        """Test Priority property has correct levels."""
        schema = TaskSchema.get_schema()

        options = schema["Priority"]["select"]["options"]
        option_names = [opt["name"] for opt in options]

        assert "Critical" in option_names
        assert "High" in option_names
        assert "Medium" in option_names
        assert "Low" in option_names


class TestIdeaSchema:
    """Tests for IdeaSchema."""

    def test_get_schema_structure(self) -> None:
        """Test schema structure."""
        schema = IdeaSchema.get_schema()

        assert "Title" in schema
        assert "Project" in schema
        assert "Category" in schema
        assert "Status" in schema
        assert "Effort Estimate" in schema

    def test_related_task_is_relation(self) -> None:
        """Test Related Task property is relation."""
        schema = IdeaSchema.get_schema()

        assert schema["Related Task"]["type"] == "relation"


class TestWorkIssueSchema:
    """Tests for WorkIssueSchema."""

    def test_get_schema_structure(self) -> None:
        """Test schema structure."""
        schema = WorkIssueSchema.get_schema()

        assert "Title" in schema
        assert "Project" in schema
        assert "Task" in schema
        assert "Type" in schema
        assert "Severity" in schema
        assert "Status" in schema

    def test_fix_tasks_is_relation(self) -> None:
        """Test Fix Tasks property is relation."""
        schema = WorkIssueSchema.get_schema()

        assert schema["Fix Tasks"]["type"] == "relation"


class TestIncidentSchema:
    """Tests for IncidentSchema."""

    def test_get_schema_structure(self) -> None:
        """Test schema structure."""
        schema = IncidentSchema.get_schema()

        assert "Title" in schema
        assert "Project" in schema
        assert "Affected Version" in schema
        assert "Severity" in schema
        assert "Type" in schema
        assert "Fix Task" in schema

    def test_severity_options(self) -> None:
        """Test Severity property has correct levels."""
        schema = IncidentSchema.get_schema()

        options = schema["Severity"]["select"]["options"]
        option_names = [opt["name"] for opt in options]

        assert "Critical" in option_names
        assert "High" in option_names
        assert "Medium" in option_names
        assert "Low" in option_names


class TestTagSchema:
    """Tests for TagSchema."""

    def test_get_schema_structure(self) -> None:
        """Test schema structure."""
        schema = TagSchema.get_schema()

        assert "Name" in schema
        assert "Category" in schema
        assert "Color" in schema
        assert "Description" in schema

    def test_color_options(self) -> None:
        """Test Color property has color options."""
        schema = TagSchema.get_schema()

        options = schema["Color"]["select"]["options"]
        option_names = [opt["name"] for opt in options]

        assert "Red" in option_names
        assert "Blue" in option_names
        assert "Green" in option_names
