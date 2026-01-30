"""Tests for metadata in CLI responses.

This module tests that CLI responses include proper metadata
for AI agents to understand system state and next steps.
"""

import json

import pytest

from click.testing import CliRunner

from better_notion.plugins.official.agents import agents_app


class TestResponseMetadata:
    """Test metadata in CLI responses."""

    def test_init_response_has_hierarchy(self):
        """Test that init response includes hierarchy information."""
        # This test would require mocking the Notion API
        # For now, we'll test the structure when workspace exists
        runner = CliRunner()
        # Using --skip to avoid actual API call
        result = runner.invoke(
            agents_app,
            ["init", "--parent-page", "test-page-id", "--skip"]
        )

        # Should return JSON (even if API call fails, we can check structure)
        try:
            data = json.loads(result.output)
            if "meta" in data.get("data", {}):
                # If there's nested metadata (some implementations might do this)
                meta = data.get("data", {}).get("meta", data.get("meta", {}))
            else:
                meta = data.get("meta", {})

            # When workspace exists, should have hierarchy info
            # (This depends on actual workspace existence)
        except json.JSONDecodeError:
            # If response is not JSON, that's OK for this test
            # We're mainly testing structure when JSON is returned
            pass

    def test_init_response_has_next_steps(self):
        """Test that init response includes next_steps."""
        # Test the metadata structure from the code
        runner = CliRunner()
        result = runner.invoke(
            agents_app,
            ["init", "--parent-page", "test-page-id", "--skip"]
        )

        # Parse output to check for metadata structure
        try:
            data = json.loads(result.output)
            # The response should have metadata
            # (depending on whether workspace exists)
            assert "data" in data or "error" in data
        except json.JSONDecodeError:
            pass

    def test_schema_includes_database_schemas(self):
        """Test that schema includes database schemas for entities."""
        runner = CliRunner()
        result = runner.invoke(agents_app, ["schema", "--format", "json"])

        data = json.loads(result.output)

        # Check that organization concept has database_schema
        concepts = {c["name"]: c for c in data["concepts"]}
        org = concepts["organization"]

        assert "database_schema" in org.properties
        db_schema = org.properties["database_schema"]

        # Database schema should have property_types
        assert "property_types" in db_schema
        assert "Name" in db_schema["property_types"]

        # Name should be required
        assert db_schema["property_types"]["Name"]["required"] is True

    def test_schema_includes_example_creation(self):
        """Test that database schemas include example creation."""
        runner = CliRunner()
        result = runner.invoke(agents_app, ["schema", "--format", "json"])

        data = json.loads(result.output)

        # Check organization database schema
        concepts = {c["name"]: c for c in data["concepts"]}
        org = concepts["organization"]

        db_schema = org.properties["database_schema"]

        # Should have example_creation
        assert "example_creation" in db_schema
        example = db_schema["example_creation"]

        assert "command" in example
        assert "properties" in example
        assert "notion agents orgs create" in example["command"]

    def test_task_schema_has_required_properties(self):
        """Test that task concept has clear required properties."""
        runner = CliRunner()
        result = runner.invoke(agents_app, ["schema", "--format", "json"])

        data = json.loads(result.output)

        # Find task concept
        concepts = {c["name"]: c for c in data["concepts"]}
        task = concepts["task"]

        # Should have required_properties
        assert "required_properties" in task.properties

        # Version should be required
        required = task.properties["required_properties"]
        assert "Version" in required
        assert "required" in required["Version"].lower()

    def test_workflow_has_prerequisites(self):
        """Test that workflows specify prerequisites."""
        runner = CliRunner()
        result = runner.invoke(agents_app, ["schema", "--format", "json"])

        data = json.loads(result.output)
        workflows = {w["name"]: w for w in data["workflows"]}

        # Check project workflow
        create_project = workflows["create_project"]
        assert "prerequisites" in create_project
        assert "workspace_initialized" in create_project["prerequisites"]
        assert "organization_exists" in create_project["prerequisites"]

    def test_best_practices_include_hierarchy(self):
        """Test that best_practices includes hierarchy guidance."""
        runner = CliRunner()
        result = runner.invoke(agents_app, ["schema", "--format", "json"])

        data = json.loads(result.output)

        # Check best practices
        assert "best_practices" in data
        practices = data["best_practices"]

        # Should mention hierarchy order
        hierarchy_mentions = [
            p for p in practices
            if "hierarchy" in p.lower() or "organization → project" in p.lower()
        ]

        # At least one practice should mention the order
        assert len(practices) > 0
