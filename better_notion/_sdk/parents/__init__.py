"""Parent type classes for Notion entities.

This module defines type-safe parent classes for creating Notion pages.
These classes represent different parent types: workspace, page, and database.

Example:
    >>> from better_notion._sdk.parents import WorkspaceParent, PageParent
    >>>
    >>> # Workspace root parent
    >>> workspace_parent = WorkspaceParent()
    >>>
    >>> # Page parent with explicit ID
    >>> page_parent = PageParent(page_id="page-id-123")
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Union


class ParentType(str, Enum):
    """Parent type enum for Notion API.

    Represents the valid parent types in Notion's API.
    """

    WORKSPACE = "workspace"
    PAGE_ID = "page_id"
    DATABASE_ID = "database_id"


@dataclass
class WorkspaceParent:
    """Workspace parent (root level).

    Used to create pages at the workspace root level,
    without a parent database or page.

    Example:
        >>> parent = WorkspaceParent()
        >>> print(parent.type)
        'workspace'
    """

    type: str = field(default="workspace")
    workspace: bool = field(default=True)


@dataclass
class PageParent:
    """Page parent.

    Used to explicitly specify a page as parent using its ID.

    Args:
        page_id: The UUID of the parent page

    Example:
        >>> parent = PageParent(page_id="page-id-123")
        >>> print(parent.type)
        'page_id'
    """

    page_id: str
    type: str = field(default="page_id")


@dataclass
class DatabaseParent:
    """Database parent.

    Used to explicitly specify a database as parent using its ID.

    Args:
        database_id: The UUID of the parent database

    Example:
        >>> parent = DatabaseParent(database_id="database-id-456")
        >>> print(parent.type)
        'database_id'
    """

    database_id: str
    type: str = field(default="database_id")


# Union type for all parent types
Parent = Union[WorkspaceParent, PageParent, DatabaseParent]
