"""Personal plugin schema for AI agent documentation.

This module provides comprehensive documentation about the personal organization
system that AI agents can consume to understand how to work with the system.

This is the SINGLE SOURCE OF TRUTH for personal plugin documentation.
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

DOMAINS_DB_SCHEMA = {
    "title": "Domains",
    "property_types": {
        "Name": {
            "type": "title",
            "required": True,
            "description": "Domain name"
        },
        "Description": {
            "type": "text",
            "required": False,
            "description": "Domain description"
        },
        "Color": {
            "type": "select",
            "required": False,
            "options": ["Red", "Orange", "Yellow", "Green", "Blue", "Purple", "Gray"],
            "default": "Blue"
        },
    },
    "example_creation": {
        "command": "notion personal domains create --name 'Work' --description 'Professional activities' --color 'Blue'",
        "properties": {
            "Name": "Work",
            "Description": "Professional activities",
            "Color": "Blue"
        }
    }
}

TAGS_DB_SCHEMA = {
    "title": "Tags",
    "property_types": {
        "Name": {
            "type": "title",
            "required": True,
            "description": "Tag name"
        },
        "Color": {
            "type": "select",
            "required": False,
            "options": ["Red", "Orange", "Yellow", "Green", "Blue", "Purple", "Gray"],
            "default": "Gray"
        },
        "Category": {
            "type": "select",
            "required": False,
            "options": ["Context", "Energy", "Location", "Time", "Custom"],
            "default": "Custom"
        },
        "Description": {
            "type": "text",
            "required": False,
            "description": "Tag description"
        },
    },
    "example_creation": {
        "command": "notion personal tags create '@computer' --category 'Context' --color 'Blue'",
        "properties": {
            "Name": "@computer",
            "Category": "Context",
            "Color": "Blue"
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
        "Status": {
            "type": "select",
            "required": False,
            "options": ["Active", "On Hold", "Completed", "Archived"],
            "default": "Active"
        },
        "Domain": {
            "type": "relation",
            "required": True,
            "target": "Domains",
            "description": "Domain this project belongs to (resolved by name)"
        },
        "Deadline": {
            "type": "date",
            "required": False,
            "description": "Project deadline"
        },
        "Priority": {
            "type": "select",
            "required": False,
            "options": ["Critical", "High", "Medium", "Low"],
            "default": "Medium"
        },
        "Progress": {
            "type": "number",
            "required": False,
            "description": "Progress percentage (0-100)"
        },
    },
    "example_creation": {
        "command": "notion personal projects create --name 'Learn Python' --domain 'Learning' --priority 'High'",
        "properties": {
            "Name": "Learn Python",
            "Domain": "Learning",
            "Priority": "High"
        }
    }
}

TASKS_DB_SCHEMA = {
    "title": "Tasks",
    "property_types": {
        "Title": {
            "type": "title",
            "required": True,
            "description": "Task title"
        },
        "Status": {
            "type": "select",
            "required": True,
            "options": ["Todo", "In Progress", "Done", "Cancelled", "Archived"],
            "default": "Todo"
        },
        "Priority": {
            "type": "select",
            "required": False,
            "options": ["Critical", "High", "Medium", "Low"],
            "default": "Medium"
        },
        "Due Date": {
            "type": "date",
            "required": False,
            "description": "Task due date"
        },
        "Domain": {
            "type": "relation",
            "required": False,
            "target": "Domains",
            "description": "Domain this task belongs to (resolved by name)"
        },
        "Project": {
            "type": "relation",
            "required": False,
            "target": "Projects",
            "description": "Project this task belongs to (resolved by name)"
        },
        "Parent Task": {
            "type": "relation",
            "required": False,
            "target": "Tasks",
            "dual_property": "Subtasks",
            "description": "Parent task for hierarchical subtasks"
        },
        "Tags": {
            "type": "relation",
            "required": False,
            "target": "Tags",
            "dual_property": "Tasks",
            "description": "Associated tags (many-to-many)"
        },
        "Energy Required": {
            "type": "select",
            "required": False,
            "options": ["High", "Medium", "Low"],
            "description": "Required energy level"
        },
    },
    "example_creation": {
        "command": "notion personal tasks add 'Complete Python course' --domain 'Learning' --priority 'High' --due '2025-12-31'",
        "properties": {
            "Title": "Complete Python course",
            "Status": "Todo",
            "Priority": "High"
        }
    }
}

ROUTINES_DB_SCHEMA = {
    "title": "Routines",
    "property_types": {
        "Name": {
            "type": "title",
            "required": True,
            "description": "Routine name"
        },
        "Frequency": {
            "type": "select",
            "required": False,
            "options": ["Daily", "Weekly", "Weekdays", "Weekends"],
            "default": "Daily"
        },
        "Domain": {
            "type": "relation",
            "required": False,
            "target": "Domains",
            "description": "Domain this routine belongs to (resolved by name)"
        },
        "Best Time": {
            "type": "text",
            "required": False,
            "description": "Best time for routine"
        },
        "Estimated Duration": {
            "type": "number",
            "required": False,
            "description": "Duration in minutes"
        },
    },
    "example_creation": {
        "command": "notion personal routines create --name 'Morning meditation' --frequency 'Daily' --domain 'Health' --best-time '7:00 AM' --duration 15",
        "properties": {
            "Name": "Morning meditation",
            "Frequency": "Daily",
            "Best Time": "7:00 AM"
        }
    }
}

AGENDA_DB_SCHEMA = {
    "title": "Agenda",
    "property_types": {
        "Name": {
            "type": "title",
            "required": True,
            "description": "Agenda item name"
        },
        "Date & Time": {
            "type": "date",
            "required": True,
            "description": "Scheduled date and time"
        },
        "Duration": {
            "type": "number",
            "required": False,
            "description": "Duration in minutes"
        },
        "Type": {
            "type": "select",
            "required": False,
            "options": ["Event", "Time Block", "Reminder"],
            "default": "Event"
        },
        "Linked Task": {
            "type": "relation",
            "required": False,
            "target": "Tasks",
            "description": "Linked task"
        },
        "Linked Project": {
            "type": "relation",
            "required": False,
            "target": "Projects",
            "description": "Linked project"
        },
    },
    "example_creation": {
        "command": "notion personal agenda add --name 'Team meeting' --when '2025-01-15T10:00:00' --duration 60 --location 'Conference Room A'",
        "properties": {
            "Name": "Team meeting",
            "Type": "Event"
        }
    }
}

# =============================================================================
# CONCEPTS
# =============================================================================

WORKSPACE_CONCEPT = Concept(
    name="workspace",
    description=(
        "A personal workspace is a collection of 6 interconnected databases that implement "
        "a complete personal productivity system. It provides the structure for tracking "
        "domains, tags, projects, tasks, routines, and agenda in a unified manner."
    ),
    properties={
        "databases": [
            "Domains",
            "Tags",
            "Projects",
            "Tasks",
            "Routines",
            "Agenda",
        ],
        "initialization": "Created via 'personal init' command",
        "detection": "Automatically detected by scanning for expected databases",
        "uniqueness": "One workspace per Notion page",
    },
    relationships={
        "Domains → Projects": "One-to-many (one domain contains multiple projects)",
        "Domains → Tasks": "One-to-many (one domain contains multiple tasks)",
        "Domains → Routines": "One-to-many (one domain contains multiple routines)",
        "Projects → Tasks": "One-to-many (one project contains multiple tasks)",
        "Tasks → Tasks": "Self-referential (parent-child subtasks)",
        "Tags ↔ Tasks": "Many-to-many (tasks can have multiple tags)",
        "Tasks → Agenda": "One-to-many (tasks can be linked to agenda items)",
    },
)

DOMAIN_CONCEPT = Concept(
    name="domain",
    description=(
        "A domain represents a high-level life area for organizing different aspects "
        "of life like Work, Health, Finance, Learning, etc. Domains provide the primary "
        "categorization system for projects, tasks, and routines."
    ),
    properties={
        "database_schema": DOMAINS_DB_SCHEMA,
        "creation": {
            "command": "notion personal domains create --name 'Work' --description 'Professional activities' --color 'Blue'",
            "returns": "JSON with domain info",
            "required_flags": {"--name": "Domain name (required)"},
            "optional_flags": {
                "--description": "Domain description (optional)",
                "--color": "Domain color (default: Blue)"
            }
        },
        "listing": {
            "command": "notion personal domains list",
            "description": "List all domains in workspace",
            "returns": "JSON array of domains"
        }
    },
    relationships={
        "Projects": "One-to-many - domain contains multiple projects",
        "Tasks": "One-to-many - domain contains multiple tasks",
        "Routines": "One-to-many - domain contains multiple routines",
    },
)

TAG_CONCEPT = Concept(
    name="tag",
    description=(
        "Tags provide flexible context labels for tasks. Unlike domains (which are "
        "high-level life areas), tags capture situational context like @computer, "
        "#high-energy, ~morning, etc. Tags have categories: Context, Energy, Location, Time, Custom."
    ),
    properties={
        "database_schema": TAGS_DB_SCHEMA,
        "categories": {
            "Context": "Situational context (@computer, @phone, @home)",
            "Energy": "Energy level required (#high-energy, #low-energy)",
            "Location": "Physical location (~office, ~home)",
            "Time": "Time preferences (morning, afternoon, evening)",
            "Custom": "Any other custom tag",
        },
        "examples": [
            "@computer (Context)",
            "#high-energy (Energy)",
            "~morning (Time)",
            "home (Location)",
        ]
    },
    relationships={
        "Tasks": "Many-to-many - tasks can have multiple tags",
        "Categories": "Tags are organized into categories for better filtering",
    },
)

TASK_CONCEPT = Concept(
    name="task",
    description=(
        "A task represents an actionable item. Tasks can be standalone or belong to "
        "projects. They support hierarchical subtasks (parent-child relationships), "
        "can have multiple tags, and can be linked to agenda items."
    ),
    properties={
        "required_properties": {
            "Title": "Task title",
        },
        "optional_properties": {
            "Status": "Current state: Todo, In Progress, Done, Cancelled, Archived",
            "Priority": "Critical, High, Medium, Low",
            "Due Date": "Task due date",
            "Domain": "Domain this task belongs to (resolved by name)",
            "Project": "Project this task belongs to (resolved by name)",
            "Parent Task": "Parent task for subtasks (creates hierarchy)",
            "Tags": "Comma-separated tag names",
            "Energy Required": "High, Medium, Low",
        },
        "workflow": "Todo → In Progress → Done",
        "archival": "Completed tasks can be archived with archived_date",
    },
    relationships={
        "Domain": "Optional - task belongs to one domain",
        "Project": "Optional - task belongs to one project",
        "Parent Task": "Optional - for hierarchical subtasks",
        "Subtasks": "Inverse of parent task - tasks can have multiple subtasks",
        "Tags": "Many-to-many - tasks can have multiple tags",
        "Agenda": "Optional - task can be linked to agenda items",
    },
)

PROJECT_CONCEPT = Concept(
    name="project",
    description=(
        "A project represents a medium-term goal with clear objectives and deadlines. "
        "Projects group related tasks and help track progress toward specific outcomes."
    ),
    properties={
        "required_properties": {
            "Name": "Project name",
            "Domain": "Domain this project belongs to (required)",
        },
        "optional_properties": {
            "Status": "Active, On Hold, Completed, Archived (default: Active)",
            "Deadline": "Project deadline",
            "Priority": "Critical, High, Medium, Low",
            "Progress": "Progress percentage 0-100",
            "Goal": "Project goal description",
        },
        "contains": ["Tasks"],
    },
    relationships={
        "Domain": "Required - each project belongs to one domain",
        "Tasks": "One-to-many - project contains multiple tasks",
    },
)

ROUTINE_CONCEPT = Concept(
    name="routine",
    description=(
        "A routine represents a recurring activity or habit. Routines have frequency "
        "tracking (Daily, Weekly, Weekdays, Weekends) and streak management for "
        "building consistent habits."
    ),
    properties={
        "required_properties": {
            "Name": "Routine name",
            "Domain": "Domain this routine belongs to (required)",
        },
        "optional_properties": {
            "Frequency": "Daily, Weekly, Weekdays, Weekends (default: Daily)",
            "Best Time": "Best time for routine",
            "Duration": "Duration in minutes (default: 30)",
        },
        "tracking": {
            "Streak": "Current streak count",
            "Total Completions": "Lifetime completion count",
            "Last Completed": "Last completion date",
        }
    },
    relationships={
        "Domain": "Optional - routine belongs to one domain",
    },
)

AGENDA_CONCEPT = Concept(
    name="agenda",
    description=(
        "Agenda items represent scheduled events, time blocks, and reminders for "
        "daily planning and time management. Agenda items can be linked to tasks "
        "and projects for context."
    ),
    properties={
        "required_properties": {
            "Name": "Agenda item name",
            "Date & Time": "Scheduled date and time",
        },
        "optional_properties": {
            "Duration": "Duration in minutes (default: 30)",
            "Type": "Event, Time Block, Reminder (default: Event)",
            "Location": "Location string",
            "Notes": "Additional notes",
        },
        "types": {
            "Event": "Scheduled event with time",
            "Time Block": "Reserved time slot",
            "Reminder": "Time-based reminder",
        }
    },
    relationships={
        "Linked Task": "Optional - link to a task",
        "Linked Project": "Optional - link to a project",
    },
)

# =============================================================================
# WORKFLOWS
# =============================================================================

INITIALIZE_WORKSPACE = Workflow(
    name="initialize_workspace",
    description="Create a complete personal productivity system with 6 databases",
    steps=[
        WorkflowStep(
            description="Detect existing workspace in page",
            purpose="Prevent duplicate workspace creation",
        ),
        WorkflowStep(
            description="Create Domains database",
            command="notion personal init --parent-page PAGE_ID",
        ),
        WorkflowStep(
            description="Create Tags database with category support",
            purpose="Flexible context labels",
        ),
        WorkflowStep(
            description="Create Projects database",
            purpose="Medium-term goal tracking",
        ),
        WorkflowStep(
            description="Create Tasks database with subtask support",
            purpose="Actionable items with hierarchy",
        ),
        WorkflowStep(
            description="Create Routines database",
            purpose="Habit tracking with streaks",
        ),
        WorkflowStep(
            description="Create Agenda database",
            purpose="Time-based scheduling",
        ),
        WorkflowStep(
            description="Establish database relationships",
            purpose="Create relations between databases",
        ),
        WorkflowStep(
            description="Save workspace metadata",
            command="notion personal info --parent-page PAGE_ID",
            purpose="Verify setup",
        ),
    ],
    commands=[
        "notion personal init --parent-page PAGE_ID",
        "notion personal info --parent-page PAGE_ID",
    ],
    prerequisites=["valid_page_id"],
    error_recovery={
        "workspace_exists": {
            "message": "Workspace already exists in this page",
            "solutions": [
                {"action": "Use existing workspace", "command": "notion personal init --parent-page PAGE_ID"},
                {"action": "Force recreate (WARNING: data loss)", "command": "notion personal init --parent-page PAGE_ID --reset"},
            ]
        },
        "missing_parent_page": {
            "message": "No parent page ID provided",
            "solutions": [
                {"action": "Provide parent page ID", "command": "notion personal init --parent-page PAGE_ID"},
            ]
        }
    },
)

CREATE_TASK_WORKFLOW = Workflow(
    name="create_task",
    description="Create a new task with optional associations",
    steps=[
        WorkflowStep(
            description="Verify workspace is initialized",
            command="notion personal info --parent-page PAGE_ID",
        ),
        WorkflowStep(
            description="Create task with optional domain, project, parent, tags",
            command="notion personal tasks add 'Task title' --domain 'Work' --project 'Project X' --tags '@computer,#high-energy'",
        ),
        WorkflowStep(
            description="Task is created with resolved relations",
            purpose="Domain, project, and tags are resolved by name",
        ),
    ],
    commands=[
        "notion personal tasks add 'Task title'",
        "notion personal tasks add 'Task title' --domain 'Work'",
        "notion personal tasks add 'Task title' --project 'Learn Python' --priority 'High'",
    ],
    prerequisites=["workspace_initialized"],
    error_recovery={
        "domain_not_found": {
            "message": "Domain not found",
            "solutions": [
                {"action": "List available domains", "command": "notion personal domains list"},
                {"action": "Create domain first", "command": "notion personal domains create --name 'Work'"},
                {"action": "Omit --domain flag", "command": "notion personal tasks add 'Task title'"},
            ]
        }
    },
)

LIST_TODAY_TASKS_WORKFLOW = Workflow(
    name="list_today_tasks",
    description="List tasks due today using filters",
    steps=[
        WorkflowStep(
            description="Query tasks with today filter",
            command="notion personal tasks list --today",
        ),
        WorkflowStep(
            description="Filter excludes archived tasks",
            purpose="Only active tasks are shown",
        ),
    ],
    commands=[
        "notion personal tasks list --today",
        "notion personal tasks list --week",
        "notion personal tasks list --domain 'Work' --status 'Todo'",
    ],
    examples=[
        "notion personal tasks list --today",
        "notion personal tasks list --week --domain 'Work'",
        "notion personal tasks list --status 'In Progress'",
    ],
)

COMPLETE_TASK_WORKFLOW = Workflow(
    name="complete_task",
    description="Mark a task as done",
    steps=[
        WorkflowStep(
            description="Get task ID from list or search",
            command="notion personal tasks list --today",
        ),
        WorkflowStep(
            description="Mark task as done",
            command="notion personal tasks done TASK_ID",
        ),
        WorkflowStep(
            description="Completed date is automatically set",
            purpose="Track when tasks are completed",
        ),
    ],
    commands=[
        "notion personal tasks done TASK_ID",
        "notion personal tasks update TASK_ID --status 'Done'",
    ],
    examples=[
        "notion personal tasks done task_abc123",
    ],
)

SUBTASK_WORKFLOW = Workflow(
    name="create_subtask",
    description="Create hierarchical subtasks",
    steps=[
        WorkflowStep(
            description="Find parent task",
            command="notion personal tasks list --project 'Project X'",
        ),
        WorkflowStep(
            description="Create subtask with --parent flag",
            command="notion personal tasks add 'Subtask title' --parent PARENT_TASK_TITLE",
        ),
        WorkflowStep(
            description="View subtasks",
            command="notion personal tasks subtasks PARENT_TASK_ID",
        ),
    ],
    commands=[
        "notion personal tasks add 'Research' --parent 'Learn Python'",
        "notion personal tasks subtasks task_abc123",
    ],
)

# =============================================================================
# COMMANDS
# =============================================================================

INIT_COMMAND = Command(
    name="init",
    purpose="Initialize a new personal workspace",
    description="Creates 6 databases with proper relationships for personal productivity",
    flags={
        "--parent-page, -p": "Parent page ID where databases will be created",
        "--name, -n": "Workspace name (default: 'Personal Workspace')",
        "--reset, -r": "Delete existing workspace and recreate (WARNING: data loss)",
        "--debug, -d": "Enable debug logging",
    },
    workflow="initialize_workspace",
    when_to_use=["First time setup", "Starting fresh workspace", "After --reset"],
    error_recovery={
        "workspace_exists": "Use --reset to force recreate, or omit --reset to reuse existing",
        "missing_parent_page": "Provide --parent-page flag for first initialization",
    },
)

INFO_COMMAND = Command(
    name="info",
    purpose="Show workspace information",
    description="Display whether a workspace exists in the given page",
    flags={
        "--parent-page, -p": "Parent page ID to check",
    },
    when_to_use=["Verify workspace setup", "Check workspace status"],
)

DOMAINS_COMMAND = Command(
    name="domains",
    purpose="Domain management",
    description="Create, list, and manage domains (high-level life areas)",
    subcommands={
        "list": {
            "purpose": "List all domains",
            "command": "notion personal domains list",
        },
        "create": {
            "purpose": "Create a new domain",
            "command": "notion personal domains create --name 'Work' --description 'Professional' --color 'Blue'",
            "flags": {
                "--name, -n": "Domain name (required)",
                "--description, -d": "Domain description",
                "--color, -c": "Domain color (default: Blue)",
            }
        },
    },
)

TAGS_COMMAND = Command(
    name="tags",
    purpose="Tag management",
    description="Create, list, and manage tags (flexible context labels)",
    subcommands={
        "list": {
            "purpose": "List all tags",
            "command": "notion personal tags list",
        },
        "create": {
            "purpose": "Create a new tag",
            "command": "notion personal tags create '@computer' --category 'Context' --color 'Blue'",
            "flags": {
                "name": "Tag name (positional argument)",
                "--category": "Tag category (default: Custom)",
                "--color": "Tag color (default: Gray)",
            }
        },
        "get": {
            "purpose": "Get a tag by name",
            "command": "notion personal tags get '@computer'",
        }
    },
)

TASKS_COMMAND = Command(
    name="tasks",
    purpose="Task management",
    description="Create, list, update, complete, and delete tasks",
    subcommands={
        "add": {
            "purpose": "Add a new task",
            "command": "notion personal tasks add 'Task title' --domain 'Work' --priority 'High'",
            "flags": {
                "title": "Task title (positional argument)",
                "--priority, -p": "Task priority (default: Medium)",
                "--domain, -d": "Domain name (optional)",
                "--project": "Project name (optional)",
                "--due": "Due date (ISO format)",
                "--parent": "Parent task title for subtasks",
                "--tags": "Comma-separated tag names",
                "--energy": "Energy required (High/Medium/Low)",
            }
        },
        "list": {
            "purpose": "List tasks with filters",
            "command": "notion personal tasks list --today --domain 'Work'",
            "flags": {
                "--today, -t": "Show tasks due today",
                "--week, -w": "Show tasks due this week",
                "--domain, -d": "Filter by domain",
                "--project": "Filter by project",
                "--status, -s": "Filter by status",
                "--tag, -t": "Filter by tag",
            }
        },
        "get": {
            "purpose": "Get task details by ID",
            "command": "notion personal tasks get TASK_ID",
        },
        "update": {
            "purpose": "Update task status or priority",
            "command": "notion personal tasks update TASK_ID --status 'In Progress' --priority 'High'",
        },
        "done": {
            "purpose": "Mark task as done",
            "command": "notion personal tasks done TASK_ID",
        },
        "delete": {
            "purpose": "Delete a task",
            "command": "notion personal tasks delete TASK_ID",
        },
        "subtasks": {
            "purpose": "List subtasks of a task",
            "command": "notion personal tasks subtasks TASK_ID",
        },
        "archive": {
            "purpose": "Archive a task",
            "command": "notion personal tasks archive TASK_ID",
        },
    },
)

PROJECTS_COMMAND = Command(
    name="projects",
    purpose="Project management",
    description="Create, list, and manage projects",
    subcommands={
        "list": {
            "purpose": "List all projects",
            "command": "notion personal projects list --domain 'Work'",
        },
        "get": {
            "purpose": "Get project details",
            "command": "notion personal projects get PROJECT_ID",
        },
        "create": {
            "purpose": "Create a new project",
            "command": "notion personal projects create --name 'Learn Python' --domain 'Learning' --priority 'High'",
        },
        "delete": {
            "purpose": "Delete a project",
            "command": "notion personal projects delete PROJECT_ID",
        },
    },
)

ROUTINES_COMMAND = Command(
    name="routines",
    purpose="Routine management",
    description="Create, list, and track routines with streaks",
    subcommands={
        "list": {
            "purpose": "List all routines",
            "command": "notion personal routines list --domain 'Health'",
        },
        "create": {
            "purpose": "Create a new routine",
            "command": "notion personal routines create --name 'Meditation' --frequency 'Daily' --domain 'Health'",
        },
        "check": {
            "purpose": "Check off a routine (increment completions)",
            "command": "notion personal routines check ROUTINE_ID",
        },
        "stats": {
            "purpose": "Get routine statistics",
            "command": "notion personal routines stats --period 'all'",
        },
    },
)

AGENDA_COMMAND = Command(
    name="agenda",
    purpose="Agenda management",
    description="Schedule events, time blocks, and reminders",
    subcommands={
        "show": {
            "purpose": "Show agenda items",
            "command": "notion personal agenda show --week",
        },
        "add": {
            "purpose": "Add an agenda item",
            "command": "notion personal agenda add --name 'Meeting' --when '2025-01-15T10:00' --duration 60",
        },
        "timeblock": {
            "purpose": "Add a time block",
            "command": "notion personal agenda timeblock --name 'Deep work' --start '2025-01-15T09:00' --duration 120",
        },
    },
)

SEARCH_COMMAND = Command(
    name="search",
    purpose="Search across tasks, projects, and routines",
    description="Full-text search with filters",
    flags={
        "query": "Search query (positional argument)",
        "--domain, -d": "Filter by domain",
        "--tag, -t": "Filter by tag",
        "--status, -s": "Filter by status",
        "--priority, -p": "Filter by priority",
        "--limit, -n": "Limit results (default: 20)",
    },
)

ARCHIVE_COMMAND = Command(
    name="archive",
    purpose="Archive management",
    description="Archive, list, restore, and purge old tasks",
    subcommands={
        "tasks": {
            "purpose": "Archive old completed tasks",
            "command": "notion personal archive tasks --older-than 30",
        },
        "list": {
            "purpose": "List archived tasks",
            "command": "notion personal archive list --domain 'Work'",
        },
        "restore": {
            "purpose": "Restore an archived task",
            "command": "notion personal archive restore TASK_ID",
        },
        "purge": {
            "purpose": "Permanently delete old archived tasks",
            "command": "notion personal archive purge --older-than 365",
        },
    },
)

REVIEW_COMMAND = Command(
    name="review",
    purpose="Guided reviews",
    description="Daily, weekly, and monthly review summaries",
    subcommands={
        "daily": {
            "purpose": "Daily review summary",
            "command": "notion personal review daily",
        },
        "weekly": {
            "purpose": "Weekly review summary",
            "command": "notion personal review weekly",
        },
        "monthly": {
            "purpose": "Monthly review summary",
            "command": "notion personal review monthly",
        },
    },
)

# =============================================================================
# PERSONAL SCHEMA
# =============================================================================

PERSONAL_SCHEMA = Schema(
    name="personal",
    version="1.0.0",
    description=(
        "Personal productivity and organization system. "
        "Provides complete structure for tracking domains, tags, projects, "
        "tasks, routines, and agenda with hierarchical subtasks, "
        "flexible tagging, and archive management."
    ),
    concepts=[
        WORKSPACE_CONCEPT,
        DOMAIN_CONCEPT,
        TAG_CONCEPT,
        TASK_CONCEPT,
        PROJECT_CONCEPT,
        ROUTINE_CONCEPT,
        AGENDA_CONCEPT,
    ],
    workflows=[
        INITIALIZE_WORKSPACE,
        CREATE_TASK_WORKFLOW,
        LIST_TODAY_TASKS_WORKFLOW,
        COMPLETE_TASK_WORKFLOW,
        SUBTASK_WORKFLOW,
    ],
    commands={
        "init": INIT_COMMAND,
        "info": INFO_COMMAND,
        "domains": DOMAINS_COMMAND,
        "tags": TAGS_COMMAND,
        "tasks": TASKS_COMMAND,
        "projects": PROJECTS_COMMAND,
        "routines": ROUTINES_COMMAND,
        "agenda": AGENDA_COMMAND,
        "search": SEARCH_COMMAND,
        "archive": ARCHIVE_COMMAND,
        "review": REVIEW_COMMAND,
    },
    best_practices=[
        "Initialize workspace with 'personal init' before any other commands",
        "Create domains first before projects/tasks/routines",
        "Use tags for flexible context (@computer, #high-energy, ~morning)",
        "Create subtasks using --parent flag for hierarchical organization",
        "Use --today flag to see tasks due today",
        "Archive completed tasks regularly to keep workspace clean",
        "Check off routines daily to maintain streaks",
        "Use 'personal search' for full-text search across all entities",
        "Use 'personal review' for guided daily/weekly/monthly reviews",
        "Relations (domain, project) are resolved by NAME, not ID",
    ],
    examples={
        "initial_setup": """# First time setup
notion personal init --parent-page PAGE_ID

# Verify setup
notion personal info --parent-page PAGE_ID

# Create some domains
notion personal domains create --name 'Work' --color 'Blue'
notion personal domains create --name 'Health' --color 'Green'
notion personal domains create --name 'Learning' --color 'Yellow'""",

        "create_tags": """# Create context tags
notion personal tags create '@computer' --category 'Context' --color 'Blue'
notion personal tags create '#high-energy' --category 'Energy' --color 'Red'
notion personal tags create '~morning' --category 'Time' --color 'Yellow'""",

        "project_workflow": """# Create a project
notion personal projects create --name 'Learn Python' --domain 'Learning' --priority 'High'

# Add tasks to the project
notion personal tasks add 'Complete Python course' --project 'Learn Python' --priority 'High'
notion personal tasks add 'Build a project' --project 'Learn Python' --parent 'Complete Python course'""",

        "daily_usage": """# See today's tasks
notion personal tasks list --today

# Add a quick task
notion personal tasks add 'Call client' --domain 'Work' --priority 'High'

# Mark task as done
notion personal tasks done task_abc123""",

        "subtasks": """# Create a parent task
notion personal tasks add 'Learn Python' --domain 'Learning'

# Create subtasks
notion personal tasks add 'Complete course' --parent 'Learn Python'
notion personal tasks add 'Build project' --parent 'Learn Python'

# View subtasks
notion personal tasks subtasks PARENT_TASK_ID""",

        "routines": """# Create a routine
notion personal routines create --name 'Morning meditation' --frequency 'Daily' --domain 'Health' --best-time '7:00 AM'

# Check off routine (increment streak)
notion personal routines check ROUTINE_ID

# View stats
notion personal routines stats""",

        "agenda": """# Add an event
notion personal agenda add --name 'Team meeting' --when '2025-01-15T10:00' --duration 60 --location 'Conference Room'

# Add a time block
notion personal agenda timeblock --name 'Deep work' --start '2025-01-15T09:00' --duration 120 --type 'Time Block'

# Show this week's agenda
notion personal agenda show --week""",

        "search_and_filter": """# Search across all entities
notion personal search 'Python'

# List tasks with filters
notion personal tasks list --domain 'Work' --status 'Todo'
notion personal tasks list --week --priority 'High'
notion personal tasks list --tag '@computer'""",

        "archive": """# Archive tasks completed more than 30 days ago
notion personal archive tasks --older-than 30

# List archived tasks
notion personal archive list --domain 'Work'

# Restore a task
notion personal archive restore TASK_ID

# Purge old archived tasks (1+ year)
notion personal archive purge --older-than 365""",

        "reviews": """# Daily review
notion personal review daily

# Weekly review
notion personal review weekly

# Monthly review
notion personal review monthly""",
    },
)
