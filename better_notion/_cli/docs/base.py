"""Base classes for documentation system.

This module provides the core data structures for documenting
CLI commands and workflows in a machine-readable format.
"""

from dataclasses import dataclass, field
from typing import Any


@dataclass
class Concept:
    """A concept represents a high-level idea in the system.

    Concepts help AI agents understand what things are
    (e.g., "workspace", "task", "version") beyond just
    command syntax.

    Attributes:
        name: Name of the concept
        description: Human-readable description
        properties: Dict of concept properties and their meanings
        relationships: Relationships to other concepts
    """

    name: str
    description: str
    properties: dict[str, Any] = field(default_factory=dict)
    relationships: dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "name": self.name,
            "description": self.description,
            "properties": self.properties,
            "relationships": self.relationships,
        }


@dataclass
class WorkflowStep:
    """A single step in a workflow.

    Attributes:
        description: What this step does
        command: Optional command to execute
        purpose: Why this step is needed
    """

    description: str
    command: str | None = None
    purpose: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "description": self.description,
            "command": self.command,
            "purpose": self.purpose,
        }


@dataclass
class ErrorRecovery:
    """Error recovery strategy for a command.

    Attributes:
        error_type: Type of error (e.g., "workspace_exists")
        message: Human-readable error message
        solutions: List of possible solutions with flags/actions
    """

    error_type: str
    message: str
    solutions: list[dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "error_type": self.error_type,
            "message": self.message,
            "solutions": self.solutions,
        }


@dataclass
class Workflow:
    """A workflow represents a sequence of operations.

    Workflows help AI agents understand how to accomplish
    high-level goals (e.g., "initialize_workspace",
    "create_task").

    Attributes:
        name: Workflow name
        description: What this workflow accomplishes
        steps: List of steps in the workflow
        commands: Example commands for this workflow
        prerequisites: Required conditions before starting
        error_recovery: Error handling strategies
    """

    name: str
    description: str
    steps: list[WorkflowStep | dict[str, Any]] = field(default_factory=list)
    commands: list[str] = field(default_factory=list)
    prerequisites: list[str] = field(default_factory=list)
    error_recovery: dict[str, dict[str, Any]] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "name": self.name,
            "description": self.description,
            "steps": [
                step.to_dict() if isinstance(step, WorkflowStep) else step
                for step in self.steps
            ],
            "commands": self.commands,
            "prerequisites": self.prerequisites,
            "error_recovery": self.error_recovery,
        }


@dataclass
class Command:
    """Documentation for a single command.

    Command docs go beyond --help text to provide semantic
    meaning and workflow context.

    Attributes:
        name: Command name
        purpose: What this command does (semantic meaning)
        description: Detailed description
        flags: Dict of flag -> purpose
        workflow: Which workflow this command belongs to
        when_to_use: When this command should be used
        error_recovery: Error handling strategies
        subcommands: Dict of subcommand name -> subcommand documentation
    """

    name: str
    purpose: str
    description: str = ""
    flags: dict[str, str] = field(default_factory=dict)
    workflow: str | None = None
    when_to_use: list[str] = field(default_factory=list)
    error_recovery: dict[str, dict[str, Any]] = field(default_factory=dict)
    subcommands: dict[str, dict[str, Any]] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        result = {
            "name": self.name,
            "purpose": self.purpose,
            "description": self.description,
            "flags": self.flags,
            "workflow": self.workflow,
            "when_to_use": self.when_to_use,
            "error_recovery": self.error_recovery,
        }

        # Add subcommands if present
        if self.subcommands:
            result["subcommands"] = self.subcommands

        return result


@dataclass
class Schema:
    """Complete schema documentation for a plugin.

    A Schema provides everything an AI agent needs to understand
    a plugin system at a high level.

    Attributes:
        name: Plugin name
        version: Schema version
        description: Plugin description
        concepts: High-level concepts in the system
        workflows: Available workflows
        commands: Command documentation
        best_practices: Recommended usage patterns
        examples: Usage examples
    """

    name: str
    version: str
    description: str
    concepts: list[Concept] = field(default_factory=list)
    workflows: list[Workflow] = field(default_factory=list)
    commands: dict[str, Command] = field(default_factory=dict)
    best_practices: list[str] = field(default_factory=list)
    examples: dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "name": self.name,
            "version": self.version,
            "description": self.description,
            "concepts": [concept.to_dict() for concept in self.concepts],
            "workflows": [workflow.to_dict() for workflow in self.workflows],
            "commands": {
                name: command.to_dict() for name, command in self.commands.items()
            },
            "best_practices": self.best_practices,
            "examples": self.examples,
        }
