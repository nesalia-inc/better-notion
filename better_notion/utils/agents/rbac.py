"""Role-based access control (RBAC) for the agents workflow system.

This module provides role-based permission management for different agent types.
Each role has specific permissions that control what actions they can perform.
"""

from typing import Dict, List, Literal, Optional


# Define valid roles
RoleType = Literal[
    "Developer",
    "PM",
    "Product Analyst",
    "QA",
    "Designer",
    "DevOps",
    "Admin",
]


# Define permission structure
# Format: resource:action (e.g., "tasks:claim", "projects:create")
PermissionType = str


class RoleManager:
    """Manages role-based access control for agent operations.

    The RoleManager defines permissions for each role and provides methods
    to check if a role has a specific permission.

    Roles:
        - Developer: Can work on tasks, submit ideas, report issues
        - PM: Can manage projects, tasks, review ideas, view analytics
        - Product Analyst: Can view projects, analyze data, generate reports
        - QA: Can review tasks, create incidents, report issues
        - Designer: Can work on design tasks, submit ideas
        - DevOps: Can manage deployments, infrastructure tasks
        - Admin: Full access to all resources and actions

    Example:
        >>> # Check if a role has a permission
        >>> RoleManager.check_permission("Developer", "tasks:claim")
        True

        >>> # Require a permission (raises PermissionError if denied)
        >>> RoleManager.require_permission("Developer", "projects:create")
        PermissionError: Role 'Developer' does not have permission 'projects:create'

        >>> # Get all permissions for a role
        >>> perms = RoleManager.get_permissions("PM")
        >>> print(perms)
        ['tasks:*', 'projects:create', 'projects:update', ...]
    """

    # Define permissions for each role
    PERMISSIONS: Dict[RoleType, List[PermissionType]] = {
        "Developer": [
            # Task operations
            "tasks:claim",
            "tasks:start",
            "tasks:complete",
            "tasks:list",
            "tasks:view",
            "tasks:comment",
            # Idea operations
            "ideas:submit",
            "ideas:view",
            # Issue operations
            "issues:report",
            "issues:view",
            # Version operations
            "versions:view",
            # Basic project visibility
            "projects:view",
        ],
        "PM": [
            # Full task access
            "tasks:*",
            # Project management
            "projects:create",
            "projects:update",
            "projects:delete",
            "projects:view",
            "projects:list",
            # Version management
            "versions:create",
            "versions:update",
            "versions:delete",
            "versions:view",
            "versions:list",
            # Idea management
            "ideas:*",
            # Issue management
            "issues:*",
            # Analytics and reporting
            "analytics:*",
            "report:*",
            # Organization visibility
            "organizations:view",
            "organizations:list",
        ],
        "Product Analyst": [
            # Read-only project access
            "projects:view",
            "projects:list",
            # Read-only task access
            "tasks:view",
            "tasks:list",
            # Analytics and reporting
            "analytics:view",
            "analytics:cycle-time",
            "analytics:completion-rate",
            "report:view",
            "report:generate",
            # Version visibility
            "versions:view",
            "versions:list",
            # Organization visibility
            "organizations:view",
            "organizations:list",
        ],
        "QA": [
            # Task review
            "tasks:view",
            "tasks:list",
            "tasks:review",
            "tasks:comment",
            # Incident management
            "incidents:create",
            "incidents:update",
            "incidents:resolve",
            "incidents:view",
            "incidents:list",
            # Issue reporting
            "issues:report",
            "issues:view",
            "issues:resolve",
            # Project visibility
            "projects:view",
            "projects:list",
            # Version visibility
            "versions:view",
            "versions:list",
        ],
        "Designer": [
            # Task operations
            "tasks:claim",
            "tasks:start",
            "tasks:complete",
            "tasks:list",
            "tasks:view",
            "tasks:comment",
            # Design task management
            "tasks:create:design",
            # Idea operations
            "ideas:submit",
            "ideas:view",
            # Issue operations
            "issues:report",
            "issues:view",
            # Project visibility
            "projects:view",
        ],
        "DevOps": [
            # Task operations
            "tasks:claim",
            "tasks:start",
            "tasks:complete",
            "tasks:list",
            "tasks:view",
            "tasks:comment",
            # Infrastructure task management
            "tasks:create:infrastructure",
            "tasks:create:deployment",
            # Incident management
            "incidents:*",
            # Issue operations
            "issues:report",
            "issues:view",
            "issues:resolve",
            # Version management
            "versions:create",
            "versions:update",
            "versions:view",
            # Project visibility
            "projects:view",
            "projects:list",
        ],
        "Admin": [
            # Full access to everything
            "*",
        ],
    }

    @classmethod
    def check_permission(
        cls,
        role: str,
        permission: str,
    ) -> bool:
        """Check if a role has a specific permission.

        Args:
            role: Role name (e.g., "Developer", "PM")
            permission: Permission string (e.g., "tasks:claim")

        Returns:
            True if role has the permission, False otherwise

        Example:
            >>> RoleManager.check_permission("Developer", "tasks:claim")
            True

            >>> RoleManager.check_permission("Developer", "projects:create")
            False
        """
        # Admin has all permissions
        if role == "Admin":
            return True

        # Check if role exists
        if role not in cls.PERMISSIONS:
            return False

        permissions = cls.PERMISSIONS[role]

        # Check for wildcard permission
        if "*" in permissions:
            return True

        # Check for exact match
        if permission in permissions:
            return True

        # Check for resource wildcard (e.g., "tasks:*" matches "tasks:claim")
        for perm in permissions:
            if perm.endswith(":*"):
                resource = perm[:-2]  # Remove ":*"
                if permission.startswith(resource + ":"):
                    return True

        # Check for action-specific wildcard (e.g., "tasks:create:*")
        # This would match "tasks:create:design" but not "tasks:update"
        if ":" in permission:
            perm_resource, perm_action = permission.split(":", 1)

            for role_perm in permissions:
                if ":" in role_perm:
                    role_resource, role_action = role_perm.split(":", 1)

                    # Match resource and action
                    if role_resource == perm_resource:
                        if role_action == "*" or role_action == perm_action:
                            return True

                        # Check for sub-action wildcard (e.g., "create:*")
                        if role_action.endswith(":*"):
                            action_prefix = role_action[:-2]
                            if perm_action.startswith(action_prefix):
                                return True

        return False

    @classmethod
    def require_permission(
        cls,
        role: str,
        permission: str,
    ) -> None:
        """Require a permission for a role, raising PermissionError if denied.

        This is a convenience method that raises an exception instead of
        returning a boolean, making it useful for guard clauses.

        Args:
            role: Role name (e.g., "Developer", "PM")
            permission: Permission string (e.g., "tasks:claim")

        Raises:
            PermissionError: If role does not have the permission

        Example:
            >>> RoleManager.require_permission("Developer", "tasks:claim")
            >>> # OK, no error

            >>> RoleManager.require_permission("Developer", "projects:create")
            PermissionError: Role 'Developer' does not have permission 'projects:create'
        """
        if not cls.check_permission(role, permission):
            raise PermissionError(
                f"Role '{role}' does not have permission '{permission}'"
            )

    @classmethod
    def get_permissions(cls, role: str) -> List[str]:
        """Get all permissions for a role.

        Args:
            role: Role name

        Returns:
            List of permission strings for the role

        Example:
            >>> perms = RoleManager.get_permissions("Developer")
            >>> print(perms)
            ['tasks:claim', 'tasks:start', 'tasks:complete', ...]
        """
        return cls.PERMISSIONS.get(role, [])

    @classmethod
    def get_all_roles(cls) -> List[str]:
        """Get list of all defined roles.

        Returns:
            List of role names

        Example:
            >>> roles = RoleManager.get_all_roles()
            >>> print(roles)
            ['Developer', 'PM', 'Product Analyst', 'QA', 'Designer', 'DevOps', 'Admin']
        """
        return list(cls.PERMISSIONS.keys())

    @classmethod
    def is_valid_role(cls, role: str) -> bool:
        """Check if a role name is valid.

        Args:
            role: Role name to validate

        Returns:
            True if role is defined, False otherwise

        Example:
            >>> RoleManager.is_valid_role("Developer")
            True

            >>> RoleManager.is_valid_role("InvalidRole")
            False
        """
        return role in cls.PERMISSIONS

    @classmethod
    def get_role_description(cls, role: str) -> Optional[str]:
        """Get a human-readable description for a role.

        Args:
            role: Role name

        Returns:
            Role description or None if role doesn't exist

        Example:
            >>> desc = RoleManager.get_role_description("Developer")
            >>> print(desc)
            'Can work on tasks, submit ideas, report issues'
        """
        descriptions = {
            "Developer": "Can work on tasks, submit ideas, report issues",
            "PM": "Can manage projects, tasks, review ideas, view analytics",
            "Product Analyst": "Can view projects, analyze data, generate reports",
            "QA": "Can review tasks, create incidents, report issues",
            "Designer": "Can work on design tasks, submit ideas",
            "DevOps": "Can manage deployments, infrastructure tasks",
            "Admin": "Full access to all resources and actions",
        }

        return descriptions.get(role)
