"""Utility functions and classes for agents workflow management."""

from better_notion.utils.agents.auth import (
    AgentContext,
    clear_agent_id,
    get_agent_id_path,
    get_agent_info,
    get_or_create_agent_id,
    is_valid_agent_id,
    set_agent_id,
)
from better_notion.utils.agents.dependency_resolver import DependencyResolver
from better_notion.utils.agents.project_context import ProjectContext
from better_notion.utils.agents.rbac import RoleManager
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
from better_notion.utils.agents.state_machine import TaskStatus, TaskStateMachine

__all__ = [
    # Agent authentication
    "AgentContext",
    "clear_agent_id",
    "get_agent_id_path",
    "get_agent_info",
    "get_or_create_agent_id",
    "is_valid_agent_id",
    "set_agent_id",
    # Dependency resolution
    "DependencyResolver",
    # Project context
    "ProjectContext",
    # Role-based access control
    "RoleManager",
    # Database schemas
    "IncidentSchema",
    "IdeaSchema",
    "OrganizationSchema",
    "ProjectSchema",
    "PropertyBuilder",
    "SelectOption",
    "TagSchema",
    "TaskSchema",
    "VersionSchema",
    "WorkIssueSchema",
    # State machine
    "TaskStatus",
    "TaskStateMachine",
]
