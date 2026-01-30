"""Agents plugin schema for AI agent documentation.

This module provides comprehensive documentation about the agents workflow
system that AI agents can consume to understand how to work with the system.

This is the SINGLE SOURCE OF TRUTH for agents documentation. All other
documentation (CLI help, website, etc.) should be derived from this schema.
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
        "command": "notion pages create --parent ORG_DB_ID --title 'WareflowX'",
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
            "description": "Organization this project belongs to"
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
        "command": "notion pages create --parent PROJECTS_DB_ID --title 'Website Redesign'",
        "properties": {
            "Name": "Website Redesign",
            "Organization": "ORG_PAGE_ID",
            "Status": "Active"
        }
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
            "description": "Project this version belongs to"
        },
        "Status": {
            "type": "select",
            "required": False,
            "options": ["Planned", "In Progress", "Released", "Archived"],
            "default": "Planned"
        },
        "Release Date": {
            "type": "date",
            "required": False,
            "description": "Planned or actual release date"
        }
    },
    "example_creation": {
        "command": "notion pages create --parent VERSIONS_DB_ID --title 'v1.0.0'",
        "properties": {
            "Name": "v1.0.0",
            "Project": "PROJECT_PAGE_ID",
            "Status": "Planned"
        }
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
            "options": ["Todo", "In Progress", "Done", "Cancelled"],
            "default": "Todo"
        },
        "Version": {
            "type": "relation",
            "required": True,
            "target": "Versions",
            "description": "Version this task belongs to (REQUIRED)"
        },
        "Target Version": {
            "type": "relation",
            "required": False,
            "target": "Versions",
            "description": "Version where task should be implemented"
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
        "command": "notion pages create --parent TASKS_DB_ID --title 'Fix login bug'",
        "properties": {
            "Name": "Fix login bug",
            "Status": "Todo",
            "Version": "VERSION_PAGE_ID",
            "Priority": "High"
        }
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
            "alternative": "notion pages create --parent ORG_DB_ID --title 'Org Name' --properties '{...}'",
            "required_properties": ["Name"],
            "property_types": {
                "Name": "title (required)",
                "Slug": "rich_text (optional, URL-friendly identifier)",
                "Status": "select [Active, Inactive] (optional, default: Active)",
                "Website": "url (optional)"
            }
        },
        "listing": {
            "command": "notion agents orgs list",
            "description": "List all organizations in workspace"
        }
    },
    relationships={
        "Projects": "One-to-many - organization contains multiple projects",
        "description": "All projects must belong to an organization"
    },
)

TASK_CONCEPT = Concept(
    name="task",
    description=(
        "A task represents a unit of work that needs to be completed as part of "
        "a project version. Tasks have states (Todo, In Progress, Done, Cancelled) "
        "and can depend on other tasks."
    ),
    properties={
        "required_properties": {
            "Title": "Task name (title property)",
            "Status": "Current state: Todo, In Progress, Done, Cancelled",
            "Version": "Relation to Version database (required)",
        },
        "optional_properties": {
            "Target Version": "Version where task should be implemented",
            "Dependencies": "Other tasks this task depends on",
            "Dependent Tasks": "Tasks that depend on this task",
        },
        "workflow": "Todo → In Progress → Done",
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
            "Title": "Project name",
            "Organization": "Relation to organization (required)",
        },
        "contains": ["Versions", "Tasks", "Ideas", "Work Issues", "Incidents"],
    },
    relationships={
        "Organization": "Required - each project belongs to one organization",
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
            "Title": "Version name (e.g., v1.0.0)",
            "Project": "Relation to project (required)",
        },
        "contains": ["Tasks"],
        "examples": ["v1.0.0", "v1.1.0", "v2.0.0-beta", "sprint-1"],
    },
    relationships={
        "Project": "Required - each version belongs to one project",
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
            description="List organizations to find target",
            command="notion agents orgs list",
            purpose="Identify which organization the project belongs to",
        ),
        WorkflowStep(
            description="Create project with organization relation",
            command="notion agents projects create --org 'Org Name/Slug' --name 'Project Name'",
            purpose="Create project with Organization relation (required)",
        ),
    ],
    commands=[
        "agents info --parent-page PAGE_ID",
        "notion agents orgs list",
        "notion agents projects create --org 'WareflowX' --name 'Website Redesign'",
    ],
    prerequisites=["workspace_initialized", "organization_exists"],
    error_recovery={
        "workspace_not_found": {
            "message": "No workspace detected in page",
            "solution": "Run 'agents init --parent-page PAGE_ID' first to create workspace",
        },
        "organization_not_found": {
            "message": "Organization not found",
            "solution": "Create organization first with 'agents orgs create --name NAME'",
        },
        "missing_org_relation": {
            "message": "Project must have Organization relation",
            "solution": "Always specify --org flag when creating project",
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
            description="List projects to find target",
            command="notion agents projects list",
            purpose="Identify which project the version belongs to",
        ),
        WorkflowStep(
            description="Create version with project relation",
            command="notion agents versions create --project 'Project Name' --name 'v1.0.0'",
            purpose="Create version with Project relation (required)",
        ),
    ],
    commands=[
        "agents info --parent-page PAGE_ID",
        "notion agents projects list",
        "notion agents versions create --project 'Website Redesign' --name 'v1.0.0'",
    ],
    prerequisites=["workspace_initialized", "organization_exists", "project_exists"],
    error_recovery={
        "workspace_not_found": {
            "message": "No workspace detected in page",
            "solution": "Run 'agents init --parent-page PAGE_ID' first to create workspace",
        },
        "project_not_found": {
            "message": "Project not found",
            "solution": "Create project first with 'agents projects create --org ORG --name NAME'",
        },
        "missing_project_relation": {
            "message": "Version must have Project relation",
            "solution": "Always specify --project flag when creating version",
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
            description="Identify target Version",
            purpose="Tasks must belong to a Version (required relation)",
        ),
        WorkflowStep(
            description="Create task page with proper properties",
            command="notion pages create --parent TASKS_DB_ID --title 'Task Name' --properties '{...}'",
            purpose="Create task with Status and Version relation",
        ),
    ],
    commands=[
        "agents info --parent-page PAGE_ID",
        "notion pages create --parent TASKS_DB_ID --title 'Task' --properties '{\"Status\": \"Todo\", \"Version\": \"VERSION_ID\"}'",
    ],
    prerequisites=["workspace_initialized"],
    error_recovery={
        "workspace_not_found": {
            "message": "No workspace detected in page",
            "solution": "Run 'agents init' first to create workspace",
        },
        "missing_version_relation": {
            "message": "Task must have a Version relation",
            "solution": "Always specify Version property when creating task",
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
            "output": "Returns list of organizations with their IDs and properties"
        },
        "create": {
            "purpose": "Create a new organization",
            "usage": "notion agents orgs create --name NAME [--slug SLUG] [--status STATUS]",
            "required_flags": {
                "--name": "Organization name (required)"
            },
            "optional_flags": {
                "--slug": "URL-friendly identifier (optional)",
                "--status": "Active or Inactive (default: Active)"
            },
            "examples": [
                "notion agents orgs create --name 'WareflowX'",
                "notion agents orgs create --name 'WareflowX' --slug 'wareflowx' --status 'Active'"
            ]
        },
        "info": {
            "purpose": "Get organization details",
            "usage": "notion agents orgs info --org ORG_NAME_OR_SLUG",
            "output": "Returns organization details with projects count"
        }
    }
)

# PROJECTS_SUBCOMMAND documents the agents projects commands
PROJECTS_COMMAND = Command(
    name="projects",
    purpose="Projects management - belongs to organizations",
    description=(
        "Projects represent software development efforts. "
        "Every project must belong to an organization."
    ),
    subcommands={
        "list": {
            "purpose": "List all projects (optionally filtered by organization)",
            "usage": "notion agents projects list [--org ORG_NAME]",
            "output": "Returns list of projects with their organizations"
        },
        "create": {
            "purpose": "Create a new project in an organization",
            "usage": "notion agents projects create --org ORG_NAME --name NAME",
            "required_flags": {
                "--org": "Organization name or slug (required)",
                "--name": "Project name (required)"
            },
            "examples": [
                "notion agents projects create --org 'WareflowX' --name 'Website Redesign'"
            ]
        },
        "info": {
            "purpose": "Get project details",
            "usage": "notion agents projects info --project PROJECT_NAME"
        }
    }
)

# VERSIONS_SUBCOMMAND documents the agents versions commands
VERSIONS_COMMAND = Command(
    name="versions",
    purpose="Versions management - releases and milestones",
    description=(
        "Versions represent releases or milestones. "
        "Every version must belong to a project."
    ),
    subcommands={
        "list": {
            "purpose": "List all versions (optionally filtered by project)",
            "usage": "notion agents versions list [--project PROJECT_NAME]",
            "output": "Returns list of versions with their projects"
        },
        "create": {
            "purpose": "Create a new version in a project",
            "usage": "notion agents versions create --project PROJECT_NAME --name VERSION",
            "required_flags": {
                "--project": "Project name (required)",
                "--name": "Version name e.g. v1.0.0 (required)"
            },
            "examples": [
                "notion agents versions create --project 'Website Redesign' --name 'v1.0.0'",
                "notion agents versions create --project 'Website Redesign' --name 'sprint-1'"
            ]
        }
    }
)

# TASKS_SUBCOMMAND documents the agents tasks commands
TASKS_COMMAND = Command(
    name="tasks",
    purpose="Tasks management - units of work in versions",
    description=(
        "Tasks represent work items. Every task must belong to a version. "
        "Tasks can have dependencies on other tasks."
    ),
    subcommands={
        "list": {
            "purpose": "List all tasks (optionally filtered by version or status)",
            "usage": "notion agents tasks list [--version VERSION] [--status STATUS]",
            "output": "Returns list of tasks with their versions and status"
        },
        "create": {
            "purpose": "Create a new task in a version",
            "usage": "notion agents tasks create --version VERSION_NAME --name TASK_NAME",
            "required_flags": {
                "--version": "Version name (required)",
                "--name": "Task name (required)"
            },
            "optional_flags": {
                "--status": "Todo, In Progress, Done (default: Todo)",
                "--priority": "Low, Medium, High, Critical (default: Medium)"
            },
            "examples": [
                "notion agents tasks create --version 'v1.0.0' --name 'Fix login bug'",
                "notion agents tasks create --version 'v1.0.0' --name 'Add feature' --status 'Todo' --priority 'High'"
            ]
        },
        "next": {
            "purpose": "Find next available task to work on",
            "usage": "notion agents tasks next [--version VERSION]",
            "description": "Finds tasks with status 'Todo' and no incomplete dependencies"
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
        "Create organization before creating projects",
        "Create project before creating versions",
        "Create version before creating tasks",
        "Tasks must have a Version relation (required)",
        "Projects must have an Organization relation (required)",
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

# 1. Create organization
notion agents orgs create --name "WareflowX" --slug "wareflowx"

# 2. Create project in organization
notion agents projects create --org "WareflowX" --name "Website Redesign"

# 3. Create version in project
notion agents versions create --project "Website Redesign" --name "v1.0.0"

# 4. Create task in version
notion agents tasks create --version "v1.0.0" --name "Fix login bug" --priority "High".""",

        "query_and_create": """# List existing organizations
notion agents orgs list

# List projects in organization
notion agents projects list --org "WareflowX"

# List tasks in version
notion agents tasks list --version "v1.0.0"

# Find next task to work on
notion agents tasks next --version "v1.0.0\"""",

        "create_task": """# Create task using agents command (recommended)
notion agents tasks create --version "v1.0.0" --name "Fix login bug"

# Alternative: Create task directly with pages command
notion pages create \\
  --parent TASKS_DB_ID \\
  --title "Fix login bug" \\
  --properties '{"Status": "Todo", "Version": "VERSION_ID", "Priority": "High"}'""",
    },
)
