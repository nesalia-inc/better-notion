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
# COMPLETE SCHEMA
# =============================================================================

AGENTS_SCHEMA = Schema(
    name="agents",
    version="1.0.0",
    description=(
        "Workflow management system for software development. "
        "Provides complete structure for tracking organizations, projects, "
        "versions, tasks, ideas, work issues, and incidents."
    ),
    concepts=[
        WORKSPACE_CONCEPT,
        TASK_CONCEPT,
        PROJECT_CONCEPT,
        VERSION_CONCEPT,
    ],
    workflows=[
        INITIALIZE_WORKSPACE,
        CREATE_TASK_WORKFLOW,
        QUERY_TASKS_WORKFLOW,
    ],
    commands={
        "init": INIT_COMMAND,
        "info": INFO_COMMAND,
    },
    best_practices=[
        "Always run 'agents info' before database operations to verify workspace state",
        "Use --skip flag to safely check for existing workspaces (prevents duplicates)",
        "Use --reset flag only when you need to recreate workspace (causes data loss)",
        "Tasks must have a Version relation - always specify Version property",
        "Check task dependencies before marking tasks as complete",
        "Projects belong to Organizations - create organization first",
        "Versions belong to Projects - create project first",
        "Query tasks by Status to find next available task",
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

        "query_workspace": """# Get workspace info and database IDs
notion agents info --parent-page PAGE_ID""",

        "create_task": """# After workspace is initialized
notion pages create \\
  --parent TASKS_DB_ID \\
  --title "Fix login bug" \\
  --properties '{"Status": "Todo", "Version": "VERSION_ID"}'""",
    },
)
