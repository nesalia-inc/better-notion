"""Formatters for schema documentation.

This module provides utilities to format Schema objects
into different output formats (JSON, YAML).
"""

import json
from typing import Any

from better_notion._cli.docs.base import Schema


def format_schema_json(schema: Schema, *, pretty: bool = True) -> str:
    """Format a Schema as JSON.

    Args:
        schema: Schema object to format
        pretty: Whether to pretty-print with indentation

    Returns:
        JSON string representation of the schema
    """
    schema_dict = schema.to_dict()
    if pretty:
        return json.dumps(schema_dict, indent=2)
    return json.dumps(schema_dict)


def format_schema_yaml(schema: Schema) -> str:
    """Format a Schema as YAML.

    Args:
        schema: Schema object to format

    Returns:
        YAML string representation of the schema
    """
    try:
        import yaml

        return yaml.dump(schema.to_dict(), default_flow_style=False)
    except ImportError:
        # Fall back to JSON if pyyaml not installed
        logger = __import__("logging").getLogger(__name__)
        logger.warning("PyYAML not installed, falling back to JSON")
        return format_schema_json(schema)


def format_schema_pretty(schema: Schema) -> str:
    """Format a Schema as human-readable text with sections.

    This provides a more readable format for human consumption
    while maintaining machine-parsable structure.

    Args:
        schema: Schema object to format

    Returns:
        Formatted text string
    """
    lines = []
    data = schema.to_dict()

    # Header
    lines.append(f"# {schema.name.upper()} SCHEMA")
    lines.append(f"Version: {schema.version}")
    lines.append(f"Description: {schema.description}")
    lines.append("")

    # Concepts
    if data["concepts"]:
        lines.append("## CONCEPTS")
        for concept in data["concepts"]:
            lines.append(f"### {concept['name']}")
            lines.append(f"{concept['description']}")
            if concept.get("properties"):
                lines.append("**Properties:**")
                for key, value in concept["properties"].items():
                    lines.append(f"  - {key}: {value}")
            if concept.get("relationships"):
                lines.append("**Relationships:**")
                for key, value in concept["relationships"].items():
                    lines.append(f"  - {key}: {value}")
            lines.append("")

    # Workflows
    if data["workflows"]:
        lines.append("## WORKFLOWS")
        for workflow in data["workflows"]:
            lines.append(f"### {workflow['name']}")
            lines.append(f"{workflow['description']}")
            if workflow.get("steps"):
                lines.append("**Steps:**")
                for i, step in enumerate(workflow["steps"], 1):
                    if isinstance(step, dict):
                        lines.append(f"  {i}. {step.get('description', step)}")
                    else:
                        lines.append(f"  {i}. {step}")
            if workflow.get("commands"):
                lines.append("**Commands:**")
                for cmd in workflow["commands"]:
                    lines.append(f"  - {cmd}")
            lines.append("")

    # Commands
    if data["commands"]:
        lines.append("## COMMANDS")
        for cmd_name, cmd in data["commands"].items():
            lines.append(f"### {cmd_name}")
            lines.append(f"**Purpose:** {cmd.get('purpose', 'N/A')}")
            if cmd.get("flags"):
                lines.append("**Flags:**")
                for flag, purpose in cmd["flags"].items():
                    lines.append(f"  - {flag}: {purpose}")
            if cmd.get("when_to_use"):
                lines.append("**When to use:**")
                for usage in cmd["when_to_use"]:
                    lines.append(f"  - {usage}")
            lines.append("")

    # Best Practices
    if data.get("best_practices"):
        lines.append("## BEST PRACTICES")
        for practice in data["best_practices"]:
            lines.append(f"- {practice}")
        lines.append("")

    return "\n".join(lines)
