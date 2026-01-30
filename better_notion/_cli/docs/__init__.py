"""Documentation system for AI agents.

This module provides infrastructure for documenting CLI commands
in a machine-readable format that AI agents can consume to understand
the system at a high level of abstraction.
"""

from better_notion._cli.docs.base import (
    Command,
    Concept,
    Schema,
    Workflow,
)

__all__ = [
    "Schema",
    "Concept",
    "Workflow",
    "Command",
]
