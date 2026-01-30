"""Tests for agents schema command.

This module tests the agents schema command to ensure it returns
proper documentation for AI agents.
"""

import json

import pytest

from click.testing import CliRunner

from better_notion.plugins.official.agents import agents_app


class TestAgentsSchemaCommand:
    """Test the agents schema command."""

    def test_schema_json_format(self):
        """Test that schema command returns valid JSON."""
        runner = CliRunner()
        result = runner.invoke(agents_app, ["schema", "--format", "json"])

        assert result.exit_code == 0

        # Verify it's valid JSON
        data = json.loads(result.output)
        assert "name" in data
        assert data["name"] == "agents"
        assert "version" in data

    def test_schema_has_required_fields(self):
        """Test that schema has all required top-level fields."""
        runner = CliRunner()
        result = runner.invoke(agents_app, ["schema", "--format", "json"])

        data = json.loads(result.output)

        # Required top-level fields
        assert "name" in data
        assert "version" in data
        assert "description" in data
        assert "concepts" in data
        assert "workflows" in data
        assert "commands" in data
        assert "best_practices" in data
        assert "examples" in data

    def test_schema_includes_organization_concept(self):
        """Test that schema includes organization concept."""
        runner = CliRunner()
        result = runner.invoke(agents_app, ["schema", "--format", "json"])

        data = json.loads(result.output)
        concepts = {c["name"]: c for c in data["concepts"]}

        # Should have organization concept
        assert "organization" in concepts

        org = concepts["organization"]
        assert "database_schema" in org.properties
        assert "creation" in org.properties

    def test_schema_includes_lifecycle_workflows(self):
        """Test that schema includes complete lifecycle workflows."""
        runner = CliRunner()
        result = runner.invoke(agents_app, ["schema", "--format", "json"])

        data = json.loads(result.output)
        workflows = {w["name"]: w for w in data["workflows"]}

        # Should have all lifecycle workflows
        assert "initialize_workspace" in workflows
        assert "create_organization" in workflows
        assert "create_project" in workflows
        assert "create_version" in workflows
        assert "create_task" in workflows

    def test_create_organization_workflow_has_steps(self):
        """Test that create_organization workflow has proper steps."""
        runner = CliRunner()
        result = runner.invoke(agents_app, ["schema", "--format", "json"])

        data = json.loads(result.output)
        workflows = {w["name"]: w for w in data["workflows"]}

        create_org = workflows["create_organization"]

        assert "steps" in create_org
        assert len(create_org["steps"]) > 0

        # Check that steps have proper structure
        for step in create_org["steps"]:
            assert "description" in step

    def test_workflow_has_error_recovery(self):
        """Test that workflows include error recovery strategies."""
        runner = CliRunner()
        result = runner.invoke(agents_app, ["schema", "--format", "json"])

        data = json.loads(result.output)
        workflows = {w["name"]: w for w in data["workflows"]}

        # Check initialize_workspace has error_recovery
        init = workflows["initialize_workspace"]
        assert "error_recovery" in init
        assert "workspace_exists" in init["error_recovery"]

        # Check that error recovery has solutions
        error = init["error_recovery"]["workspace_exists"]
        assert "solutions" in error
        assert len(error["solutions"]) > 0

    def test_commands_include_subcommands(self):
        """Test that commands include subcommands documentation."""
        runner = CliRunner()
        result = runner.invoke(agents_app, ["schema", "--format", "json"])

        data = json.loads(result.output)

        # Check that orgs command exists and has subcommands
        assert "orgs" in data["commands"]
        orgs = data["commands"]["orgs"]
        assert "subcommands" in orgs
        assert "list" in orgs["subcommands"]
        assert "create" in orgs["subcommands"]

    def test_orgs_create_subcommand_has_examples(self):
        """Test that orgs create subcommand includes examples."""
        runner = CliRunner()
        result = runner.invoke(agents_app, ["schema", "--format", "json"])

        data = json.loads(result.output)
        orgs_create = data["commands"]["orgs"]["subcommands"]["create"]

        assert "examples" in orgs_create
        assert len(orgs_create["examples"]) > 0

    def test_examples_include_complete_lifecycle(self):
        """Test that examples include complete_lifecycle example."""
        runner = CliRunner()
        result = runner.invoke(agents_app, ["schema", "--format", "json"])

        data = json.loads(result.output)

        assert "examples" in data
        assert "complete_lifecycle" in data["examples"]

        lifecycle = data["examples"]["complete_lifecycle"]
        # Should mention all 4 steps
        assert "orgs create" in lifecycle
        assert "projects create" in lifecycle
        assert "versions create" in lifecycle
        assert "tasks create" in lifecycle

    def test_yaml_format(self):
        """Test that schema supports YAML format."""
        runner = CliRunner()
        result = runner.invoke(agents_app, ["schema", "--format", "yaml"])

        # YAML format should work (even if pyyaml not installed, it falls back to JSON)
        assert result.exit_code == 0

    def test_pretty_format(self):
        """Test that schema supports pretty format."""
        runner = CliRunner()
        result = runner.invoke(agents_app, ["schema", "--format", "pretty"])

        # Pretty format should work
        assert result.exit_code == 0
        assert len(result.output) > 0

    def test_invalid_format_returns_error(self):
        """Test that invalid format returns error."""
        runner = CliRunner()
        result = runner.invoke(agents_app, ["schema", "--format", "invalid"])

        assert result.exit_code == 1
