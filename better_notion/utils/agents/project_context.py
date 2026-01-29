"""Project context management for agents workflow system.

This module provides the ProjectContext class for managing project context
stored in .notion files. Each project directory contains a .notion file
that identifies the project, organization, and role for that directory.
"""

from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Optional

import yaml


@dataclass
class ProjectContext:
    """Project context stored in .notion file.

    The .notion file identifies which project the current directory belongs to,
    allowing CLI commands to know which Notion database to query and what
    permissions the current role has.

    Attributes:
        project_id: Notion page ID for the project
        project_name: Human-readable project name
        org_id: Notion page ID for the organization
        role: Current role for this project context (default: Developer)

    Example:
        >>> context = ProjectContext.create(
        ...     project_id="abc123",
        ...     project_name="my-project",
        ...     org_id="org789",
        ...     role="Developer"
        ... )
        >>> print(context.project_id)
        'abc123'

        >>> # Load from current directory
        >>> context = ProjectContext.from_current_directory()
        >>> if context:
        ...     print(f"Working on {context.project_name} as {context.role}")
    """

    project_id: str
    project_name: str
    org_id: str
    role: str = "Developer"

    @classmethod
    def from_current_directory(cls) -> Optional["ProjectContext"]:
        """Load .notion file from current directory or parent directories.

        This method searches up the directory tree from the current working
        directory until it finds a .notion file. This allows commands to work
        from any subdirectory within a project.

        Returns:
            ProjectContext if .notion file is found, None otherwise

        Example:
            >>> # In /Users/dev/projects/my-project/src
            >>> # .notion is in /Users/dev/projects/my-project
            >>> context = ProjectContext.from_current_directory()
            >>> # Will find and load the .notion file from parent directory
        """
        cwd = Path.cwd()

        # Search up the directory tree
        for parent in [cwd, *cwd.parents]:
            notion_file = parent / ".notion"

            if notion_file.exists() and notion_file.is_file():
                try:
                    with open(notion_file, encoding="utf-8") as f:
                        data = yaml.safe_load(f)

                    if data and isinstance(data, dict):
                        return cls(**data)

                except (yaml.YAMLError, TypeError, ValueError) as e:
                    # Invalid YAML or data structure
                    # Log and continue searching
                    continue

        return None

    @classmethod
    def from_path(cls, path: Path) -> Optional["ProjectContext"]:
        """Load .notion file from specific path.

        Args:
            path: Path to directory containing .notion file

        Returns:
            ProjectContext if .notion file exists and is valid, None otherwise

        Example:
            >>> path = Path("/Users/dev/projects/my-project")
            >>> context = ProjectContext.from_path(path)
        """
        notion_file = path / ".notion"

        if not notion_file.exists() or not notion_file.is_file():
            return None

        try:
            with open(notion_file, encoding="utf-8") as f:
                data = yaml.safe_load(f)

            if data and isinstance(data, dict):
                return cls(**data)

        except (yaml.YAMLError, TypeError, ValueError):
            return None

    @classmethod
    def create(
        cls,
        project_id: str,
        project_name: str,
        org_id: str,
        role: str = "Developer",
        path: Optional[Path] = None,
    ) -> "ProjectContext":
        """Create new .notion file with project context.

        Args:
            project_id: Notion page ID for the project
            project_name: Human-readable project name
            org_id: Notion page ID for the organization
            role: Role for this project context (default: Developer)
            path: Directory where to create .notion file (default: cwd)

        Returns:
            New ProjectContext instance

        Raises:
            IOError: If unable to write to the .notion file

        Example:
            >>> context = ProjectContext.create(
            ...     project_id="abc123def456",
            ...     project_name="my-awesome-project",
            ...     org_id="org789xyz012",
            ...     role="Developer",
            ...     path=Path.cwd()
            ... )
        """
        if path is None:
            path = Path.cwd()

        context = cls(
            project_id=project_id,
            project_name=project_name,
            org_id=org_id,
            role=role,
        )

        notion_file = path / ".notion"

        with open(notion_file, "w", encoding="utf-8") as f:
            yaml.dump(asdict(context), f, default_flow_style=False, sort_keys=False)

        return context

    def save(self, path: Optional[Path] = None) -> None:
        """Save context to .notion file.

        Args:
            path: Directory where to save .notion file (default: cwd)

        Raises:
            IOError: If unable to write to the .notion file

        Example:
            >>> context.role = "PM"
            >>> context.save()
        """
        if path is None:
            path = Path.cwd()

        notion_file = path / ".notion"

        with open(notion_file, "w", encoding="utf-8") as f:
            yaml.dump(asdict(self), f, default_flow_style=False, sort_keys=False)

    def update_role(self, new_role: str, path: Optional[Path] = None) -> None:
        """Update project role and save to .notion file.

        Args:
            new_role: New role value
            path: Directory where .notion file is located (default: cwd)

        Example:
            >>> context.update_role("PM")
            >>> print(context.role)
            'PM'
        """
        self.role = new_role
        self.save(path)

    def has_permission(self, permission: str) -> bool:
        """Check if current role has a specific permission.

        This is a convenience method that will integrate with the
        RoleManager class. For now, it returns True for all permissions.

        Args:
            permission: Permission string (e.g., "tasks:claim")

        Returns:
            True if role has permission, False otherwise

        Example:
            >>> if context.has_permission("tasks:claim"):
            ...     # Claim the task
        """
        # TODO: Integrate with RoleManager
        # For now, allow all permissions
        return True

    def __repr__(self) -> str:
        """String representation of project context."""
        return (
            f"ProjectContext("
            f"project_id={self.project_id!r}, "
            f"project_name={self.project_name!r}, "
            f"org_id={self.org_id!r}, "
            f"role={self.role!r}"
            f")"
        )
