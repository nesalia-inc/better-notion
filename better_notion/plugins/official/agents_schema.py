"""Agents plugin schema for AI agent documentation.

This module provides comprehensive documentation about the agents workflow
system that AI agents can consume to understand how to work with the system.

This is the SINGLE SOURCE OF TRUTH for agents documentation. All other
documentation (CLI help, website, etc.) should be derived from this schema.

IMPORTANT - Command signatures use IDs not names:
- Organization creation: --name (name), --slug (optional)
- Project creation: --name, --org-id (requires organization PAGE ID)
- Version creation: --name, --project-id (requires project PAGE ID)
- Task creation: --title, --version-id (requires version PAGE ID)

You must get entity IDs from previous command responses before creating
child entities.
"""

from better_notion._cli.docs.base import (
    Command,
    Concept,
    Schema,
    Workflow,
    WorkflowStep,
)

# =============================================================================
# DATABASE SCHEMAS
# =============================================================================

ORGANIZATIONS_DB_SCHEMA = {
    "title": "Organizations",
    "property_types": {
        "Name": {
            "type": "title",
            "required": True,
            "description": "Organization name"
        },
        "Slug": {
            "type": "rich_text",
            "required": False,
            "description": "URL-friendly identifier"
        },
        "Status": {
            "type": "select",
            "required": False,
            "options": ["Active", "Inactive"],
            "default": "Active"
        },
        "Website": {
            "type": "url",
            "required": False,
            "description": "Organization website URL"
        }
    },
    "example_creation": {
        "command": "notion agents orgs create --name 'WareflowX' --slug 'wareflowx'",
        "properties": {
            "Name": "WareflowX",
            "Slug": "wareflowx",
            "Status": "Active"
        }
    }
}

PROJECTS_DB_SCHEMA = {
    "title": "Projects",
    "property_types": {
        "Name": {
            "type": "title",
            "required": True,
            "description": "Project name"
        },
        "Organization": {
            "type": "relation",
            "required": True,
            "target": "Organizations",
            "description": "Organization this project belongs to (requires org PAGE ID)"
        },
        "Status": {
            "type": "select",
            "required": False,
            "options": ["Active", "On Hold", "Completed", "Archived"],
            "default": "Active"
        },
        "Description": {
            "type": "rich_text",
            "required": False,
            "description": "Project description"
        }
    },
    "example_creation": {
        "command": "notion agents projects create --name 'Website Redesign' --org-id ORG_PAGE_ID",
        "properties": {
            "Name": "Website Redesign",
            "Organization": "ORG_PAGE_ID",
            "Status": "Active"
        },
        "note": "ORG_PAGE_ID comes from 'notion agents orgs create' response (id field)"
    }
}

VERSIONS_DB_SCHEMA = {
    "title": "Versions",
    "property_types": {
        "Name": {
            "type": "title",
            "required": True,
            "description": "Version name (e.g., v1.0.0)"
        },
        "Project": {
            "type": "relation",
            "required": True,
            "target": "Projects",
            "description": "Project this version belongs to (requires project PAGE ID)"
        },
        "Status": {
            "type": "select",
            "required": False,
            "options": ["Planning", "In Progress", "Released", "Archived"],
            "default": "Planning"
        },
        "Release Date": {
            "type": "date",
            "required": False,
            "description": "Planned or actual release date"
        }
    },
    "example_creation": {
        "command": "notion agents versions create --name 'v1.0.0' --project-id PROJECT_PAGE_ID",
        "properties": {
            "Name": "v1.0.0",
            "Project": "PROJECT_PAGE_ID",
            "Status": "Planning"
        },
        "note": "PROJECT_PAGE_ID comes from 'notion agents projects create' response (id field)"
    }
}

TASKS_DB_SCHEMA = {
    "title": "Tasks",
    "property_types": {
        "Name": {
            "type": "title",
            "required": True,
            "description": "Task name"
        },
        "Status": {
            "type": "select",
            "required": True,
            "options": ["Backlog", "Claimed", "In Progress", "Completed", "Cancelled"],
            "default": "Backlog"
        },
        "Version": {
            "type": "relation",
            "required": True,
            "target": "Versions",
            "description": "Version this task belongs to (requires version PAGE ID)"
        },
        "Dependencies": {
            "type": "relation",
            "required": False,
            "target": "Tasks",
            "dual_property": "Dependent Tasks",
            "description": "Tasks that must complete before this task"
        },
        "Dependent Tasks": {
            "type": "relation",
            "required": False,
            "target": "Tasks",
            "dual_property": "Dependencies",
            "description": "Tasks blocked by this task"
        },
        "Priority": {
            "type": "select",
            "required": False,
            "options": ["Low", "Medium", "High", "Critical"],
            "default": "Medium"
        }
    },
    "example_creation": {
        "command": "notion agents tasks create --title 'Fix login bug' --version-id VERSION_PAGE_ID",
        "properties": {
            "Name": "Fix login bug",
            "Status": "Backlog",
            "Version": "VERSION_PAGE_ID",
            "Priority": "High"
        },
        "note": "VERSION_PAGE_ID comes from 'notion agents versions create' response (id field)"
    }
}

# =============================================================================
# CONCEPTS
# =============================================================================

WORKSPACE_CONCEPT = Concept(
    name="workspace",
    description=(
        "A workspace is a collection of 8 interconnected databases that implement "
        "a complete software development workflow management system. It provides "
        "the structure for tracking organizations, projects, versions, tasks, ideas, "
        "work issues, and incidents in a unified manner."
    ),
    properties={
        "databases": [
            "Organizations",
            "Tags",
            "Projects",
            "Versions",
            "Tasks",
            "Ideas",
            "Work Issues",
            "Incidents",
        ],
        "initialization": "Created via 'agents init' command",
        "detection": "Automatically detected by scanning for expected databases",
        "uniqueness": "One workspace per Notion page",
    },
    relationships={
        "Organizations → Projects": "Many-to-one (many projects belong to one organization)",
        "Projects → Versions": "Many-to-one (many versions belong to one project)",
        "Versions → Tasks": "Many-to-one (many tasks belong to one version)",
        "Tasks → Tasks": "Self-referential (tasks can depend on other tasks)",
    },
)

ORGANIZATION_CONCEPT = Concept(
    name="organization",
    description=(
        "An organization represents a company, team, or entity that owns projects. "
        "Organizations are the top-level entities in the agents workflow hierarchy."
    ),
    properties={
        "database_schema": ORGANIZATIONS_DB_SCHEMA,
        "creation": {
            "command": "notion agents orgs create --name 'Org Name' --slug 'org-slug'",
            "returns": "JSON with 'id' field containing organization PAGE ID",
            "required_flags": {"--name": "Organization name (required)"},
            "optional_flags": {
                "--slug": "URL-friendly identifier (optional)",
                "--description": "Organization description (optional)",
                "--repository-url": "Git repository URL (optional)",
                "--status": "Active or Inactive (default: Active)"
            }
        },
        "listing": {
            "command": "notion agents orgs list",
            "description": "List all organizations in workspace",
            "returns": "JSON array of organizations with id, name, slug, status"
        }
    },
    relationships={
        "Projects": "One-to-many - organization contains multiple projects",
        "description": "All projects must belong to an organization",
    },
)

TASK_CONCEPT = Concept(
    name="task",
    description=(
        "A task represents a unit of work that needs to be completed as part of "
        "a project version. Tasks have states (Backlog, Claimed, In Progress, Completed) "
        "and can depend on other tasks."
    ),
    properties={
        "required_properties": {
            "Title": "Task name (title property)",
            "Status": "Current state: Backlog, Claimed, In Progress, Completed, Cancelled",
            "Version": "Relation to Version database (requires version PAGE ID)",
        },
        "optional_properties": {
            "Type": "Task type: New Feature, Bug Fix, Refactor, Documentation, Testing, Other",
            "Priority": "Low, Medium, High, Critical",
            "Dependencies": "Other tasks this task depends on (comma-separated task IDs)",
            "Estimated Hours": "Time estimate in hours",
        },
        "workflow": "Backlog → Claimed → In Progress → Completed",
    },
    relationships={
        "Version": "Required - each task must belong to one version",
        "Dependencies": "Optional - tasks that must complete before this task",
        "Dependent Tasks": "Inverse of dependencies - tasks blocked by this task",
    },
)

PROJECT_CONCEPT = Concept(
    name="project",
    description=(
        "A project represents a software project or product being developed. "
        "Projects belong to organizations and contain multiple versions."
    ),
    properties={
        "required_properties": {
            "Name": "Project name",
            "Organization ID": "Organization PAGE ID from 'agents orgs create' response",
        },
        "optional_properties": {
            "Slug": "URL-friendly identifier",
            "Description": "Project description",
            "Repository": "Git repository URL",
            "Tech Stack": "Comma-separated technologies",
            "Role": "Project role: Developer, Designer, PM, QA, DevOps (default: Developer)",
        },
        "contains": ["Versions", "Tasks", "Ideas", "Work Issues", "Incidents"],
    },
    relationships={
        "Organization": "Required - each project belongs to one organization (via org-id)",
        "Versions": "One-to-many - project contains multiple versions",
    },
)

VERSION_CONCEPT = Concept(
    name="version",
    description=(
        "A version represents a release or milestone of a project. Examples: "
        "v1.0.0, v1.1.0, v2.0.0. Tasks are created within versions."
    ),
    properties={
        "required_properties": {
            "Name": "Version name (e.g., v1.0.0)",
            "Project ID": "Project PAGE ID from 'agents projects create' response",
        },
        "optional_properties": {
            "Status": "Planning, In Progress, Released, Archived (default: Planning)",
            "Type": "Major, Minor, Patch, Hotfix (default: Minor)",
            "Branch": "Git branch name",
            "Progress": "Progress percentage 0-100 (default: 0)",
        },
        "contains": ["Tasks"],
        "examples": ["v1.0.0", "v1.1.0", "v2.0.0-beta", "sprint-1"],
    },
    relationships={
        "Project": "Required - each version belongs to one project (via project-id)",
        "Tasks": "One-to-many - version contains multiple tasks",
    },
)

# =============================================================================
# WORKFLOWS
# =============================================================================

INITIALIZE_WORKSPACE = Workflow(
    name="initialize_workspace",
    description="Create a complete agents workflow management system with 8 databases",
    steps=[
        WorkflowStep(
            description="Detect existing workspace in page",
            purpose="Prevent duplicate workspace creation",
        ),
        WorkflowStep(
            description="Create Organizations database",
            command="notion databases create --parent PAGE_ID --title Organizations",
        ),
        WorkflowStep(
            description="Create Tags database",
            command="notion databases create --parent PAGE_ID --title Tags",
        ),
        WorkflowStep(
            description="Create Projects database",
            command="notion databases create --parent PAGE_ID --title Projects",
        ),
        WorkflowStep(
            description="Create Versions database",
            command="notion databases create --parent PAGE_ID --title Versions",
        ),
        WorkflowStep(
            description="Create Tasks database",
            command="notion databases create --parent PAGE_ID --title Tasks",
        ),
        WorkflowStep(
            description="Create Ideas database",
            command="notion databases create --parent PAGE_ID --title Ideas",
        ),
        WorkflowStep(
            description="Create Work Issues database",
            command="notion databases create --parent PAGE_ID --title 'Work Issues'",
        ),
        WorkflowStep(
            description="Create Incidents database",
            command="notion databases create --parent PAGE_ID --title Incidents",
        ),
        WorkflowStep(
            description="Establish database relationships",
            purpose="Create relations between databases (Projects→Organizations, etc.)",
        ),
        WorkflowStep(
            description="Save workspace metadata",
            command="agents info --parent-page PAGE_ID",
            purpose="Verify setup and get database IDs",
        ),
    ],
    commands=[
        "agents init --parent-page PAGE_ID",
        "agents info --parent-page PAGE_ID",
    ],
    prerequisites=["valid_page_id"],
    error_recovery={
        "workspace_exists": {
            "message": "Detected 5+ expected databases in page",
            "meaning": "Workspace already initialized in this page",
            "solutions": [
                {
                    "flag": "--skip",
                    "action": "use_existing_workspace",
                    "description": "Skip initialization and use existing workspace",
                    "when_to_use": "You want to keep existing data",
                },
                {
                    "flag": "--reset",
                    "action": "recreate_workspace",
                    "description": "Delete all databases and recreate (WARNING: data loss)",
                    "warning": "This will delete all existing databases and their content",
                    "when_to_use": "You want to start completely fresh",
                },
            ],
        }
    },
)

CREATE_ORGANIZATION_WORKFLOW = Workflow(
    name="create_organization",
    description="Create a new organization in the agents workspace",
    steps=[
        WorkflowStep(
            description="Verify workspace is initialized",
            command="agents info --parent-page PAGE_ID",
            purpose="Get Organizations database ID and verify workspace exists",
        ),
        WorkflowStep(
            description="Create organization using agents command",
            command="notion agents orgs create --name 'Org Name' --slug 'org-slug'",
            purpose="Create organization with proper properties",
        ),
    ],
    commands=[
        "agents info --parent-page PAGE_ID",
        "notion agents orgs create --name 'WareflowX' --slug 'wareflowx'",
    ],
    prerequisites=["workspace_initialized"],
    error_recovery={
        "workspace_not_found": {
            "message": "No workspace detected in page",
            "solution": "Run 'agents init --parent-page PAGE_ID' first to create workspace",
        },
        "missing_name": {
            "message": "Organization name is required",
            "solution": "Always specify --name flag when creating organization",
        },
    },
)

CREATE_PROJECT_WORKFLOW = Workflow(
    name="create_project",
    description="Create a new project in an organization",
    steps=[
        WorkflowStep(
            description="Verify workspace is initialized",
            command="agents info --parent-page PAGE_ID",
            purpose="Get database IDs and verify workspace exists",
        ),
        WorkflowStep(
            description="List organizations to get organization ID",
            command="notion agents orgs list",
            purpose="Get the organization PAGE ID from the response",
        ),
        WorkflowStep(
            description="Create project with organization ID",
            command="notion agents projects create --name 'Project Name' --org-id ORG_PAGE_ID",
            purpose="Create project with Organization relation (requires org PAGE ID, not name)",
        ),
    ],
    commands=[
        "agents info --parent-page PAGE_ID",
        "notion agents orgs list",
        "notion agents projects create --name 'Website Redesign' --org-id ORG_PAGE_ID",
    ],
    prerequisites=["workspace_initialized", "organization_exists"],
    error_recovery={
        "workspace_not_found": {
            "message": "No workspace detected in page",
            "solution": "Run 'agents init --parent-page PAGE_ID' first to create workspace",
        },
        "organization_not_found": {
            "message": "Organization ID not found",
            "solution": "Run 'agents orgs list' to get valid organization IDs, or create org first with 'agents orgs create --name NAME'",
        },
        "missing_org_id": {
            "message": "Project requires --org-id (organization PAGE ID), not name",
            "solution": "Use --org-id with the ID from 'agents orgs list' response",
        },
    },
)

CREATE_VERSION_WORKFLOW = Workflow(
    name="create_version",
    description="Create a new version in a project",
    steps=[
        WorkflowStep(
            description="Verify workspace is initialized",
            command="agents info --parent-page PAGE_ID",
            purpose="Get database IDs and verify workspace exists",
        ),
        WorkflowStep(
            description="List projects to get project ID",
            command="notion agents projects list",
            purpose="Get the project PAGE ID from the response",
        ),
        WorkflowStep(
            description="Create version with project ID",
            command="notion agents versions create --name 'v1.0.0' --project-id PROJECT_PAGE_ID",
            purpose="Create version with Project relation (requires project PAGE ID, not name)",
        ),
    ],
    commands=[
        "agents info --parent-page PAGE_ID",
        "notion agents projects list",
        "notion agents versions create --name 'v1.0.0' --project-id PROJECT_PAGE_ID",
    ],
    prerequisites=["workspace_initialized", "organization_exists", "project_exists"],
    error_recovery={
        "workspace_not_found": {
            "message": "No workspace detected in page",
            "solution": "Run 'agents init --parent-page PAGE_ID' first to create workspace",
        },
        "project_not_found": {
            "message": "Project ID not found",
            "solution": "Run 'agents projects list' to get valid project IDs, or create project first with 'agents projects create --name NAME --org-id ORG_ID'",
        },
        "missing_project_id": {
            "message": "Version requires --project-id (project PAGE ID), not name",
            "solution": "Use --project-id with the ID from 'agents projects list' response",
        },
    },
)

CREATE_TASK_WORKFLOW = Workflow(
    name="create_task",
    description="Create a new task in the agents workflow system",
    steps=[
        WorkflowStep(
            description="Verify workspace is initialized",
            command="agents info --parent-page PAGE_ID",
            purpose="Get database IDs and verify workspace exists",
        ),
        WorkflowStep(
            description="List versions to get version ID",
            command="notion agents versions list",
            purpose="Get the version PAGE ID from the response",
        ),
        WorkflowStep(
            description="Create task with version ID",
            command="notion agents tasks create --title 'Task Name' --version-id VERSION_PAGE_ID",
            purpose="Create task with Version relation (requires version PAGE ID, not name)",
        ),
    ],
    commands=[
        "agents info --parent-page PAGE_ID",
        "notion agents versions list",
        "notion agents tasks create --title 'Fix login bug' --version-id VERSION_PAGE_ID",
    ],
    prerequisites=["workspace_initialized"],
    error_recovery={
        "workspace_not_found": {
            "message": "No workspace detected in page",
            "solution": "Run 'agents init' first to create workspace",
        },
        "version_not_found": {
            "message": "Version ID not found",
            "solution": "Run 'agents versions list' to get valid version IDs, or create version first with 'agents versions create --name NAME --project-id PROJECT_ID'",
        },
        "missing_version_id": {
            "message": "Task requires --version-id (version PAGE ID), not name",
            "solution": "Use --version-id with the ID from 'agents versions list' response",
        },
    },
)

QUERY_TASKS_WORKFLOW = Workflow(
    name="query_tasks",
    description="Query and filter tasks in the workspace",
    steps=[
        WorkflowStep(
            description="Get workspace database IDs",
            command="agents info --parent-page PAGE_ID",
            purpose="Obtain tasks database ID",
        ),
        WorkflowStep(
            description="Query tasks database",
            command="notion databases query --database TASKS_DB_ID --filter '{...}'",
            purpose="Retrieve tasks with optional filtering",
        ),
    ],
    commands=[
        "agents info --parent-page PAGE_ID",
        "notion databases query --database TASKS_DB_ID",
    ],
    prerequisites=["workspace_initialized"],
)

# =============================================================================
# COMMANDS
# =============================================================================

INIT_COMMAND = Command(
    name="init",
    purpose="Initialize a new agents workspace or manage existing one",
    description=(
        "Creates a complete workflow management system with 8 databases "
        "and their relationships. Can detect existing workspaces to prevent duplicates."
    ),
    flags={
        "--parent-page": "Parent page ID where workspace will be created",
        "--workspace-name": "Name for the workspace (default: 'Agents Workspace')",
        "--reset": "Force recreation (deletes existing databases and recreates)",
        "--skip": "Skip initialization if workspace already exists",
        "--debug": "Enable debug output",
    },
    workflow="initialize_workspace",
    when_to_use=[
        "First time setting up agents system in a page",
        "Starting fresh in a new page",
        "Recovering from corrupted workspace (use --reset)",
        "Safely checking for existing workspace (use --skip)",
    ],
    error_recovery={
        "workspace_exists": {
            "solutions": [
                {"flag": "--skip", "use_case": "Keep existing workspace"},
                {"flag": "--reset", "use_case": "Delete and recreate (data loss)"},
            ]
        }
    },
)

INFO_COMMAND = Command(
    name="info",
    purpose="Display workspace status and metadata",
    description="Shows whether a workspace exists, database IDs, and workspace info",
    flags={
        "--parent-page": "Parent page ID to check for workspace",
    },
    workflow=None,
    when_to_use=[
        "Verify workspace initialization",
        "Get database IDs for queries",
        "Check workspace version and metadata",
        "Debug workspace issues",
    ],
)

# =============================================================================
# SUBCOMMANDS
# =============================================================================

# ORGS_SUBCOMMAND documents the agents orgs commands
ORGS_COMMAND = Command(
    name="orgs",
    purpose="Organizations management - top-level entities in workflow hierarchy",
    description=(
        "Organizations are the starting point for all projects. "
        "Every project must belong to an organization."
    ),
    subcommands={
        "list": {
            "purpose": "List all organizations in workspace",
            "usage": "notion agents orgs list",
            "output": "Returns JSON array with organization objects containing id, name, slug, status"
        },
        "get": {
            "purpose": "Get organization by ID",
            "usage": "notion agents orgs get ORG_PAGE_ID",
            "output": "Returns organization details"
        },
        "create": {
            "purpose": "Create a new organization",
            "usage": "notion agents orgs create --name NAME [--slug SLUG] [--description DESC] [--repository-url URL] [--status STATUS]",
            "required_flags": {
                "--name": "Organization name (required)"
            },
            "optional_flags": {
                "--slug": "URL-friendly identifier (optional)",
                "--description": "Organization description (optional)",
                "--repository-url": "Git repository URL (optional)",
                "--status": "Active or Inactive (default: Active)"
            },
            "returns": "JSON with 'id' field containing organization PAGE ID (needed for creating projects)",
            "examples": [
                "notion agents orgs create --name 'WareflowX'",
                "notion agents orgs create --name 'WareflowX' --slug 'wareflowx' --status 'Active'"
            ]
        }
    }
)

# PROJECTS_SUBCOMMAND documents the agents projects commands
PROJECTS_COMMAND = Command(
    name="projects",
    purpose="Projects management - belongs to organizations",
    description=(
        "Projects represent software development efforts. "
        "Every project must belong to an organization (requires org PAGE ID)."
    ),
    subcommands={
        "list": {
            "purpose": "List all projects (optionally filtered by organization)",
            "usage": "notion agents projects list [--org-id ORG_PAGE_ID]",
            "output": "Returns JSON array with project objects containing id, name, slug, status, organization_id"
        },
        "get": {
            "purpose": "Get project by ID",
            "usage": "notion agents projects get PROJECT_PAGE_ID",
            "output": "Returns project details"
        },
        "create": {
            "purpose": "Create a new project in an organization",
            "usage": "notion agents projects create --name NAME --org-id ORG_PAGE_ID [--slug SLUG] [--description DESC] [--repository REPO] [--tech-stack STACK]",
            "required_flags": {
                "--name": "Project name (required)",
                "--org-id": "Organization PAGE ID (required) - use ID from 'agents orgs list' or 'agents orgs create' response"
            },
            "optional_flags": {
                "--slug": "URL-friendly identifier (optional)",
                "--description": "Project description (optional)",
                "--repository": "Git repository URL (optional)",
                "--tech-stack": "Comma-separated tech stack (optional)",
                "--status": "Active, On Hold, Completed, Archived (default: Active)",
                "--role": "Developer, Designer, PM, QA, DevOps (default: Developer)"
            },
            "returns": "JSON with 'id' field containing project PAGE ID (needed for creating versions)",
            "examples": [
                "notion agents projects create --name 'Website Redesign' --org-id org_12345"
            ],
            "note": "IMPORTANT: Use --org-id with organization PAGE ID, not organization name"
        }
    }
)

# VERSIONS_SUBCOMMAND documents the agents versions commands
VERSIONS_COMMAND = Command(
    name="versions",
    purpose="Versions management - releases and milestones",
    description=(
        "Versions represent releases or milestones. "
        "Every version must belong to a project (requires project PAGE ID)."
    ),
    subcommands={
        "list": {
            "purpose": "List all versions (optionally filtered by project)",
            "usage": "notion agents versions list [--project-id PROJECT_PAGE_ID]",
            "output": "Returns JSON array with version objects containing id, name, status, type, project_id"
        },
        "get": {
            "purpose": "Get version by ID",
            "usage": "notion agents versions get VERSION_PAGE_ID",
            "output": "Returns version details"
        },
        "create": {
            "purpose": "Create a new version in a project",
            "usage": "notion agents versions create --name NAME --project-id PROJECT_PAGE_ID [--type TYPE] [--status STATUS]",
            "required_flags": {
                "--name": "Version name e.g. v1.0.0 (required)",
                "--project-id": "Project PAGE ID (required) - use ID from 'agents projects list' or 'agents projects create' response"
            },
            "optional_flags": {
                "--status": "Planning, In Progress, Released, Archived (default: Planning)",
                "--type": "Major, Minor, Patch, Hotfix (default: Minor)",
                "--branch": "Git branch name (optional)",
                "--progress": "Progress percentage 0-100 (default: 0)"
            },
            "returns": "JSON with 'id' field containing version PAGE ID (needed for creating tasks)",
            "examples": [
                "notion agents versions create --name 'v1.0.0' --project-id proj_12345"
            ],
            "note": "IMPORTANT: Use --project-id with project PAGE ID, not project name"
        }
    }
)

# TASKS_SUBCOMMAND documents the agents tasks commands
TASKS_COMMAND = Command(
    name="tasks",
    purpose="Tasks management - units of work in versions",
    description=(
        "Tasks represent work items. Every task must belong to a version (requires version PAGE ID). "
        "Tasks can have dependencies on other tasks."
    ),
    subcommands={
        "list": {
            "purpose": "List all tasks (optionally filtered by version or status)",
            "usage": "notion agents tasks list [--version-id VERSION_PAGE_ID] [--status STATUS]",
            "output": "Returns JSON array with task objects containing id, title, status, type, priority, version_id"
        },
        "get": {
            "purpose": "Get task by ID",
            "usage": "notion agents tasks get TASK_PAGE_ID",
            "output": "Returns task details"
        },
        "create": {
            "purpose": "Create a new task in a version",
            "usage": "notion agents tasks create --title TITLE --version-id VERSION_PAGE_ID [--type TYPE] [--priority PRIORITY] [--dependencies DEP_IDS]",
            "required_flags": {
                "--title": "Task name (required)",
                "--version-id": "Version PAGE ID (required) - use ID from 'agents versions list' or 'agents versions create' response"
            },
            "optional_flags": {
                "--status": "Backlog, Claimed, In Progress, Completed, Cancelled (default: Backlog)",
                "--type": "New Feature, Bug Fix, Refactor, Documentation, Testing, Other (default: New Feature)",
                "--priority": "Low, Medium, High, Critical (default: Medium)",
                "--dependencies": "Comma-separated dependency task IDs (optional)",
                "--estimate": "Estimated hours (optional)"
            },
            "returns": "JSON with 'id' field containing task PAGE ID",
            "examples": [
                "notion agents tasks create --title 'Fix login bug' --version-id ver_12345",
                "notion agents tasks create --title 'Add feature' --version-id ver_12345 --priority 'High' --type 'New Feature'"
            ],
            "note": "IMPORTANT: Use --version-id with version PAGE ID, not version name"
        },
        "next": {
            "purpose": "Find next available task to work on",
            "usage": "notion agents tasks next [--project-id PROJECT_PAGE_ID]",
            "description": "Finds tasks with status 'Backlog' or 'Claimed' and no incomplete dependencies",
            "output": "Returns task object or message if no tasks available"
        },
        "claim": {
            "purpose": "Claim a task (transition to Claimed status)",
            "usage": "notion agents tasks claim TASK_PAGE_ID",
            "output": "Returns updated task with agent ID"
        },
        "start": {
            "purpose": "Start working on a task (transition to In Progress)",
            "usage": "notion agents tasks start TASK_PAGE_ID",
            "output": "Returns updated task with agent ID",
            "note": "Will fail if task has incomplete dependencies"
        },
        "complete": {
            "purpose": "Complete a task (transition to Completed)",
            "usage": "notion agents tasks complete TASK_PAGE_ID [--actual-hours HOURS]",
            "output": "Returns completed task with actual hours"
        },
        "can-start": {
            "purpose": "Check if a task can start (all dependencies completed)",
            "usage": "notion agents tasks can-start TASK_PAGE_ID",
            "output": "Returns boolean and lists incomplete dependencies if any"
        }
    }
)

# =============================================================================
# COMPLETE SCHEMA
# =============================================================================

AGENTS_SCHEMA = Schema(
    name="agents",
    version="2.0.0",
    description=(
        "Workflow management system for software development. "
        "Provides complete structure for tracking organizations, projects, "
        "versions, tasks, ideas, work issues, and incidents."
    ),
    concepts=[
        WORKSPACE_CONCEPT,
        ORGANIZATION_CONCEPT,
        PROJECT_CONCEPT,
        VERSION_CONCEPT,
        TASK_CONCEPT,
    ],
    workflows=[
        INITIALIZE_WORKSPACE,
        CREATE_ORGANIZATION_WORKFLOW,
        CREATE_PROJECT_WORKFLOW,
        CREATE_VERSION_WORKFLOW,
        CREATE_TASK_WORKFLOW,
        QUERY_TASKS_WORKFLOW,
    ],
    commands={
        "init": INIT_COMMAND,
        "info": INFO_COMMAND,
        "orgs": ORGS_COMMAND,
        "projects": PROJECTS_COMMAND,
        "versions": VERSIONS_COMMAND,
        "tasks": TASKS_COMMAND,
    },
    best_practices=[
        "Follow the hierarchy: Organization → Project → Version → Task",
        "Always run 'agents info' before operations to verify workspace state",
        "Use --skip flag to safely check for existing workspaces (prevents duplicates)",
        "Use --reset flag only when you need to recreate workspace (causes data loss)",
        "IMPORTANT: Child entities require parent PAGE IDs, not names",
        "Save the 'id' field from create responses - you need it for creating child entities",
        "Use 'agents orgs/projects/versions list' to get valid entity IDs",
        "Create organization before creating projects",
        "Create project before creating versions",
        "Create version before creating tasks",
        "Tasks must have a Version relation (required via --version-id)",
        "Projects must have an Organization relation (required via --org-id)",
        "Use 'agents tasks next' to find next available task",
    ],
    examples={
        "initial_setup": """# First time setup
notion agents init --parent-page PAGE_ID

# Verify setup
notion agents info --parent-page PAGE_ID""",

        "safe_initialization": """# Check if workspace exists, use if found
notion agents init --parent-page PAGE_ID --skip""",

        "force_recreate": """# Delete existing workspace and recreate (WARNING: data loss)
notion agents init --parent-page PAGE_ID --reset""",

        "complete_lifecycle": """# Complete workflow: Org → Project → Version → Task
# IMPORTANT: Each command returns an ID that the next command needs!

# 1. Create organization - SAVE THE ID from response!
notion agents orgs create --name "WareflowX" --slug "wareflowx"
# Response: {id: "org_abc123", "name": "WareflowX", ...}
# Save: ORG_ID="org_abc123"

# 2. Create project - requires org PAGE ID, not name!
notion agents projects create --name "Website Redesign" --org-id "org_abc123"
# Response: {id: "proj_def456", "name": "Website Redesign", ...}
# Save: PROJECT_ID="proj_def456"

# 3. Create version - requires project PAGE ID, not name!
notion agents versions create --name "v1.0.0" --project-id "proj_def456"
# Response: {id: "ver_ghi789", "name": "v1.0.0", ...}
# Save: VERSION_ID="ver_ghi789"

# 4. Create task - requires version PAGE ID, not name!
notion agents tasks create --title "Fix login bug" --version-id "ver_ghi789" --priority "High\"""",

        "list_and_filter": """# List all organizations
notion agents orgs list

# List all projects (unfiltered)
notion agents projects list

# List all versions (unfiltered)
notion agents versions list

# List tasks in a specific version
notion agents tasks list --version-id "ver_ghi789"

# Find next task to work on
notion agents tasks next""",

        "task_workflow": """# Find a task
notion agents tasks next

# Claim a task (uses task ID from list or next)
notion agents tasks claim task_xyz123

# Start working on task (fails if dependencies not complete)
notion agents tasks start task_xyz123

# Complete task
notion agents tasks complete task_xyz123 --actual-hours 3.5""",

        "get_entity_by_id": """# Get organization details
notion agents orgs get org_abc123

# Get project details
notion agents projects get proj_def456

# Get version details
notion agents versions get ver_ghi789

# Get task details
notion agents tasks get task_xyz123""",

        "check_dependencies": """# Check if task can start (all deps complete?)
notion agents tasks can-start task_xyz123
# Returns: {can_start: false, incomplete_dependencies: [...]}

# List tasks with dependencies
notion agents tasks list --version-id ver_ghi789""",
    },
)
