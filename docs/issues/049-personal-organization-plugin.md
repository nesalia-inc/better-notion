# Personal Organization Plugin

## Summary

Design and implement a comprehensive personal organization system for managing tasks, projects, routines, and schedule through Notion. This plugin enables personal productivity with quick task capture, multi-level task breakdown, and daily/weekly/monthly reviews.

## Problem Statement

### Current Limitations

The agents plugin (#031) provides excellent workflow management for AI agents coordinating on software development projects, but lacks personal productivity features:

**1. No Personal Task Management**
- Can't manage daily personal tasks across different life domains
- No support for personal projects (non-development related)
- Missing health & wellness tracking
- No habit/routine management

**2. Limited Task Breakdown**
- Agents plugin focuses on version-based development workflow
- No support for multi-level subtasks for personal use
- Missing time blocking and agenda management

**3. No Personal Review System**
- No daily/weekly/monthly review workflows
- Missing guided reflection questions
- No analytics on personal productivity patterns
- Can't track habit streaks and completion rates

**4. Separate Context from Work**
- Personal tasks mixed with work tasks creates mental clutter
- Need separation between professional coordination and personal organization
- Different workflows for personal vs professional contexts

### What's Missing

1. **Personal Task Management**: Quick capture, hierarchical subtasks, domain-based organization
2. **Routine/Habit Tracking**: Daily habits, streaks, best time tracking
3. **Agenda/Time Blocking**: Schedule events and time-block dedicated work sessions
4. **Personal Projects**: Long-term personal goals and projects separate from work
5. **Daily Reviews**: Guided morning/evening review workflows

## Proposed Solution

Implement a new **personal plugin** that is independent from the agents plugin but follows similar architectural patterns. The personal plugin manages 5 Notion databases with CLI commands optimized for personal productivity.

### Core Philosophy

- **Quick Capture**: Add tasks, ideas, events in seconds
- **Break Down Everything**: Multi-level subtasks for complex projects
- **Context-Aware**: Filter by domain (Work, Health, Personal), energy level, time available
- **Review-Driven**: Daily, weekly, monthly reviews to stay aligned
- **Action-Oriented**: Concrete next steps through subtask breakdown

### Architecture Overview

#### Database Structure (6 databases)

```
Personal Workspace
├── Domains Database          # Life areas (Work, Health, Personal)
├── Tags Database             # Flexible labels (@phone, @computer, @errands)
├── Projects Database         # Personal projects
├── Tasks Database            # Tasks with subtasks, tags, archive status
├── Routines Database         # Habits and recurring activities
└── Agenda Database           # Events and time blocks
```

#### Entity Relationships

```
Domains (1) ──────────< (Many) Projects
       ↓                     ↓
    Routines              Tasks
                              ↓
                         Subtasks (self-relation)
                              ↓
                           Agenda (optional time blocks)

Tags (Many) ──────────< (Many) Tasks  # Many-to-many relation
```

### Database Schemas

#### 1. Domains Database

**Purpose:** Define life areas for categorization.

| Property | Type | Description |
|----------|------|-------------|
| Name | Title | Domain name |
| Description | Text | What this domain encompasses |
| Color | Select | Visual identification (Red, Blue, Green, etc.) |

**Default Domains:**
- Work (professional tasks, projects)
- Health (exercise, nutrition, sleep, wellness)
- Personal (hobbies, relationships, finances)

#### 2. Tags Database

**Purpose:** Flexible cross-cutting labels for context-based organization.

| Property | Type | Description |
|----------|------|-------------|
| Name | Title | Tag name (typically starts with @) |
| Color | Select | Visual identification |
| Category | Select | Context, Energy, Location, Tool, Custom |
| Description | Text | When to use this tag |

**Default Tags:**
- **Context**: @home, @work, @errands, @computer, @phone
- **Energy**: @high-energy, @low-energy, @brain-fog
- **Location**: @online, @outside, @in-person
- **Time**: @quick (<5min), @slow (>30min)

**Examples:**
```bash
personal tags create "@phone" --category Context --color Blue
personal tags create "@quick" --category Time --color Green
```

#### 3. Projects Database

**Purpose:** Track long-term personal projects.

| Property | Type | Description |
|----------|------|-------------|
| Name | Title | Project name |
| Status | Select | Active, On Hold, Completed, Archived |
| Domain | Relation | Links to Domains |
| Deadline | Date | Target completion date |
| Priority | Select | Critical, High, Medium, Low |
| Progress | Number | 0-100 percentage |
| Goal | Text | Objective/Outcome |
| Notes | Text | Additional context |
| Linked Tasks | Rollup | Count of related tasks |

**Project Examples:**
- "Get in shape" (Health domain)
- "Learn Spanish" (Personal domain)
- "Build portfolio website" (Work domain)

#### 4. Tasks Database

**Purpose:** Capture and track all tasks with multi-level subtasks.

| Property | Type | Description |
|----------|------|-------------|
| Title | Title | Task description |
| Status | Select | Todo, In Progress, Done, Cancelled, Archived |
| Priority | Select | Critical, High, Medium, Low |
| Due Date | Date | When it's due |
| Domain | Relation | Links to Domains |
| Project | Relation | Links to Projects (optional) |
| Parent Task | Relation | Self-referential for subtasks |
| Subtasks | Rollup | Count of subtasks |
| Tags | Relation | Links to Tags (many-to-many) |
| Estimated Time | Number | Minutes/hours estimate |
| Energy Required | Select | High, Medium, Low |
| Context | Text | @home, @work, @errands, etc. |
| Created Date | Date | When task was created |
| Completed Date | Date | When finished |
| Archived Date | Date | When task was archived |

**Task Workflow:**
```
Todo → In Progress → Done
          ↓            ↓
      Cancelled    Cancelled
```

**Subtask Structure:**
```
Project: "Get in shape"
  └── Task: "Research gym options"
  └── Task: "Create workout plan"
      └── Subtask: "Define goals (strength, cardio, flexibility)"
      └── Subtask: "Choose exercises for each goal"
          └── Sub-subtask: "Research strength exercises"
          └── Sub-subtask: "Research cardio options"
      └── Subtask: "Create weekly schedule"
  └── Task: "Buy gym membership"
```

#### 5. Routines Database

**Purpose:** Track habits and recurring activities.

| Property | Type | Description |
|----------|------|-------------|
| Name | Title | Routine/habit name |
| Frequency | Select | Daily, Weekly, Weekdays, Weekends |
| Domain | Relation | Links to Domains |
| Best Time | Text | Morning, afternoon, evening, specific time |
| Estimated Duration | Number | Minutes |
| Streak | Number | Current consecutive days |
| Last Completed | Date | Most recent completion |
| Total Completions | Number | All-time count |

**Routine Examples:**
- "Morning meditation" (Daily, Health, Morning)
- "Exercise" (Weekdays, Health, Morning)
- "Read for 30 minutes" (Daily, Personal, Evening)
- "Weekly review" (Weekly, Personal, Sunday afternoon)

#### 6. Agenda Database

**Purpose:** Manage scheduled events and time blocking.

| Property | Type | Description |
|----------|------|-------------|
| Name | Title | Event/block name |
| Date & Time | Date | When it occurs |
| Duration | Number | Minutes |
| Type | Select | Event, Time Block, Reminder |
| Linked Task | Relation | Associated task (optional) |
| Linked Project | Relation | Associated project (optional) |
| Location | Text | Where (for events) |
| Notes | Text | Details |

**Use Cases:**
- **Events**: Meetings, appointments, social engagements
- **Time Blocks**: "Deep work: Portfolio website 9AM-11AM"
- **Reminders**: "Pay rent", "Call mom"

## CLI Commands

### Command Structure

All commands are under the `personal` namespace:

```bash
personal init                    # Initialize workspace
personal info                    # Show workspace info

personal tasks add/list/get/update/delete/done/archive
personal projects create/list/get/delete
personal routines create/list/check/stats
personal agenda show/add/timeblock
personal domains create/list
personal tags create/list/add/remove
personal search QUERY            # Global search
personal archive list/restore     # Archive management
personal review daily/weekly/monthly
```

### Initialization Commands

```bash
# Initialize complete personal workspace
personal init --parent-page PAGE_ID

# Shows workspace status and database IDs
personal info --parent-page PAGE_ID
```

**Similar to agents plugin:**
- Creates all 6 databases with proper relationships
- Auto-detects existing workspace
- Saves configuration to `~/.notion/personal.json`
- Generates unique workspace ID

### Task Commands

```bash
# Add task (quick capture)
personal tasks add "Buy groceries" \
  --priority Medium \
  --domain Personal \
  --due today

# Add task with project and subtask
personal tasks add "Research gyms" \
  --project "Get in shape" \
  --parent "Create workout plan" \
  --priority High

# List tasks
personal tasks list                          # All incomplete tasks
personal tasks list --today                  # Due today or overdue
personal tasks list --week                   # This week
personal tasks list --domain Health          # Filter by domain
personal tasks list --project "Get in shape" # Filter by project

# Get task details
personal tasks get TASK_ID

# Update task
personal tasks update TASK_ID \
  --status "In Progress" \
  --priority High

# Mark task done
personal tasks done TASK_ID

# Delete task
personal tasks delete TASK_ID

# Show subtasks
personal tasks subtasks TASK_ID
```

### Project Commands

```bash
# Create project
personal projects create "Learn Spanish" \
  --domain Personal \
  --priority Medium \
  --deadline "2025-06-01"

# List projects
personal projects list                      # All active projects
personal projects list --domain Health      # Filter by domain

# Get project details
personal projects get PROJECT_ID

# Delete project
personal projects delete PROJECT_ID
```

### Routine Commands

```bash
# Create routine
personal routines create "Morning meditation" \
  --frequency Daily \
  --domain Health \
  --best-time "Morning" \
  --duration 10

# List routines
personal routines list                      # All routines
personal routines list --domain Health      # Filter by domain

# Check off routine (increments streak)
personal routines check ROUTINE_ID

# Show statistics
personal routines stats                     # All routines
personal routines stats --period week       # Last 7 days
personal routines stats --period month      # Last 30 days
```

### Agenda Commands

```bash
# Show agenda
personal agenda show                        # Today's agenda
personal agenda show --week                 # Full week

# Add event
personal agenda add "Doctor appointment" \
  --when "2025-02-10 14:00" \
  --duration 60 \
  --location "Medical Center"

# Add time block
personal agenda timeblock \
  --name "Deep work: Portfolio" \
  --start "2025-02-10 09:00" \
  --duration 120 \
  --type "Time Block"
```

### Domain Commands

```bash
# List domains
personal domains list

# Create custom domain
personal domains create "Finance" --color "Green"
```

### Tags Commands

```bash
# List all tags
personal tags list

# Create new tag
personal tags create "@phone" --category Context --color Blue
personal tags create "@quick" --category Time --color Green
personal tags create "@high-energy" --category Energy --color Orange

# Add tag to task
personal tasks update TASK_ID --tags "@phone,@quick"

# Remove tag from task
personal tasks update TASK_ID --remove-tags "@phone"

# List tasks by tag
personal tasks list --tag "@phone"
personal tasks list --tag "@quick,@computer"  # Multiple tags

# Show tag details
personal tags get "@phone"
```

### Search Commands

```bash
# Global search across all tasks
personal search "gym"

# Search in specific domain
personal search "workout" --domain Health

# Search by tag
personal search "call" --tag "@phone"

# Search with status filter
personal search "project" --status "In Progress"

# Search with multiple filters
personal search "meeting" \
  --domain Work \
  --tag "@computer" \
  --priority High

# Search results show:
# - Task title
# - Domain
# - Tags
# - Status
# - Priority
# - Due date
# - Matching score (highlighted terms)
```

**Search Features:**
- Full-text search across title, context, notes
- Fuzzy matching (typos tolerated)
- Searches archived tasks optionally
- Supports regex patterns with `--regex` flag
- Limits results with `--limit N` (default 20)

### Archive Commands

```bash
# Archive completed tasks older than N days
personal archive tasks --older-than 90      # Archive Done tasks > 90 days old
personal archive tasks --completed-before "2025-01-01"

# Archive specific task
personal tasks archive TASK_ID

# Archive all completed tasks in a project
personal archive project --project "Get in shape" --only-completed

# List archived items
personal archive list                        # All archived tasks
personal archive list --domain Health        # Filter by domain
personal archive list --tag "@phone"         # Filter by tag

# Restore from archive
personal archive restore TASK_ID
personal archive restore --multiple ID1,ID2,ID3

# Permanently delete archived items
personal archive delete TASK_ID              # Permanently delete
personal archive purge --older-than 365      # Delete archived > 1 year old
```

**Archive Behavior:**
- Archived tasks have status "Archived"
- Hidden from normal `list` commands
- Use `--include-archived` flag to show them
- Automatically sets Archived Date
- Original completion date preserved

**Why Archive Instead of Delete:**
- Keeps historical data for analytics
- Can restore if needed
- Doesn't count against active task counts
- Clean workspace without data loss

### Review Commands

```bash
# Daily review (morning or evening)
personal review daily

# Interactive guided workflow:
# - Morning: Plan today, check routine status
# - Evening: Reflect on day, plan tomorrow

# Weekly review
personal review weekly

# Interactive guided workflow:
# - Review completed tasks
# - Analyze time allocation by domain
# - Set intentions for next week
# - Check project progress

# Monthly review
personal review monthly

# Interactive guided workflow:
# - Monthly achievements
# - Domain balance analysis
# - Goal progress check
# - Adjust priorities
```

## Key Features

### 1. Multi-Level Subtasks

Tasks can have unlimited subtasks via self-referential relation:

```
Task: "Create workout plan" (In Progress)
  ├── Subtask: "Define goals" (Done)
  ├── Subtask: "Choose exercises" (In Progress)
  │   ├── Sub-subtask: "Research strength exercises" (Done)
  │   └── Sub-subtask: "Research cardio options" (Todo)
  └── Subtask: "Create weekly schedule" (Todo)
```

**Benefits:**
- Break down complex tasks into actionable steps
- Progress tracking at every level
- Concrete next steps always available

### 2. Guided Reviews

**Daily Review (Morning):**
```bash
personal review daily
```

Interactive prompts:
1. "What's your main focus for today?"
2. Shows today's high-priority tasks
3. "Which 3 tasks will you complete today?"
4. Shows routines for morning
5. "Any time blocks to schedule?"

**Daily Review (Evening):**
1. "What did you accomplish today?"
2. Shows tasks completed
3. "What went well?"
4. "What could be improved?"
5. Preview of tomorrow's priorities

**Weekly Review:**
1. Review all completed tasks this week
2. Show domain breakdown (how much time in Work vs Health vs Personal)
3. Show project progress
4. "What are your top 3 priorities for next week?"
5. Check routine streaks
6. "Any areas of your life that need attention?"

**Monthly Review:**
1. Monthly achievements summary
2. Domain balance analytics
3. Goal progress check
4. "What worked well this month?"
5. "What to improve next month?"
6. Adjust project priorities

### 3. Quick Capture Design

All commands optimized for speed:

```bash
# Minimal typing for quick capture
personal tasks add "Call mom" -p High -d Personal
personal routines check abc123
personal tasks list --today
```

**Autocompletion:**
- Domains autocomplete (Work, Health, Personal)
- Projects autocomplete from existing
- Routines autocomplete by name
- Tasks autocomplete by title prefix
- Tags autocomplete with @ prefix

### 4. Flexible Tagging System

Tags provide cross-cutting organization that complements Domains:

```bash
# A task can belong to multiple contexts
personal tasks add "Call dentist" \
  --domain Personal \
  --tags "@phone,@errands,@afternoon"

# Find all phone tasks regardless of domain
personal tasks list --tag "@phone"

# Find quick tasks when you only have 5 minutes
personal tasks list --tag "@quick"

# Find low-energy tasks for when you're tired
personal tasks list --tag "@low-energy"
```

**Tag Categories:**
- **Context**: @home, @work, @errands, @computer, @phone
- **Energy**: @high-energy, @low-energy, @brain-fog-ok
- **Time**: @quick (<5min), @medium, @slow (>30min)
- **Location**: @online, @outside, @in-person
- **Custom**: Create your own

**Benefits:**
- A task can be in Domain "Health" AND tagged "@phone" AND "@quick"
- Filter by context when planning your day
- Time-based filtering matches available energy
- Unlike rigid domains, tags are flexible and overlapping

### 5. Powerful Search

Find anything instantly with full-text search:

```bash
# Simple search
personal search "gym"
# Results: "Research gym options", "Buy gym membership", "Create gym routine"

# Filtered search
personal search "workout" --domain Health --tag "@high-energy"

# Search for recent conversations
personal search "call" --tag "@phone" --status "In Progress"

# Regex pattern search
personal search "^(Buy|Call)" --regex --tag "@errands"
```

**Search Capabilities:**
- Full-text search across title, context, notes
- Fuzzy matching (tolerates typos)
- Combine with domain, tag, priority filters
- Search archived tasks with `--include-archived`
- Regex patterns for power users
- Result highlighting shows matching terms

**Use Cases:**
- "What was that thing about the gym?"
- Find all @phone calls to make today
- Search all Work tasks mentioning "meeting"
- Find all quick tasks I can do right now

### 6. Archive System

Keep workspace clean while preserving history:

```bash
# Clean up old completed tasks
personal archive tasks --older-than 90

# Archive a specific task
personal tasks archive TASK_ID

# See what's archived
personal archive list

# Restore if needed
personal archive restore TASK_ID

# Yearly cleanup
personal archive purge --older-than 365
```

**Archive Benefits:**
- Clean workspace without data loss
- Archived tasks hidden from normal views
- Historical data preserved for analytics
- Easy restoration if needed
- One-command cleanup

**Archive Workflow:**
1. Complete task → `personal tasks done`
2. After 90 days → `personal archive tasks --older-than 90`
3. Task disappears from normal lists
4. Still searchable with `personal search --include-archived`
5. Restore anytime with `personal archive restore`

## Implementation Plan

### Phase 1: Foundation (1 week)

**Deliverables:**
1. `personal init` - Initialize workspace with 6 databases
2. `personal info` - Show workspace status
3. Basic plugin structure following agents pattern
4. Workspace metadata and auto-detection

**Files:**
- `better_notion/plugins/official/personal.py` (main plugin)
- `better_notion/plugins/official/personal_cli.py` (CLI functions)
- `better_notion/plugins/official/personal_schema.py` (schema docs)
- `better_notion/plugins/official/personal_sdk/` (SDK extensions)

### Phase 2: Core CRUD + Tags (1 week)

**Deliverables:**
1. Tasks: add, list, get, update, done, delete
2. Projects: create, list, get, delete
3. Domains: create, list
4. Tags: create, list, add/remove from tasks
5. Basic filtering and querying

**Commands:**
```bash
personal tasks add/list/get/update/delete/done
personal projects create/list/get/delete
personal domains create/list
personal tags create/list/add/remove
```

### Phase 3: Subtasks & Hierarchy (1 week)

**Deliverables:**
1. Parent task relation in Tasks database
2. Subtask rollup and filtering
3. `personal tasks subtasks` command
4. Hierarchical display in list/get

### Phase 4: Routines (1 week)

**Deliverables:**
1. Routines database
2. create, list, check, stats commands
3. Streak tracking
4. Frequency-based filtering

**Commands:**
```bash
personal routines create/list/check/stats
```

### Phase 5: Agenda (3 days)

**Deliverables:**
1. Agenda database
2. show, add, timeblock commands
3. Date/time filtering
4. Integration with tasks (link agenda items to tasks)

**Commands:**
```bash
personal agenda show/add/timeblock
```

### Phase 6: Search & Archive (1 week)

**Deliverables:**
1. Full-text search implementation
2. Search filtering (domain, tag, status, priority)
3. Archive system with status changes
4. Archive listing and restoration
5. Purge old archived items
6. Search integration with archived items

**Commands:**
```bash
personal search QUERY [--domain] [--tag] [--status] [--priority]
personal archive tasks --older-than N
personal archive list [--domain] [--tag]
personal archive restore TASK_ID
personal archive purge --older-than N
```

### Phase 7: Reviews (1 week)

**Deliverables:**
1. Daily review (morning/evening modes)
2. Weekly review with analytics
3. Monthly review with summaries
4. Interactive prompts and questions

**Commands:**
```bash
personal review daily/weekly/monthly
```

### Phase 8: Polish & Documentation (3 days)

**Deliverables:**
1. Comprehensive README
2. Command reference
3. Examples and tutorials
4. Integration tests
5. Performance optimization

**Total: 6-7 weeks**

## Technical Implementation

### Plugin Structure

Following the agents plugin pattern:

```python
# better_notion/plugins/official/personal.py

class PersonalPlugin(CombinedPluginInterface):
    """Personal organization plugin."""

    def register_commands(self, app: typer.Typer) -> None:
        """Register personal commands."""
        personal_app = typer.Typer(
            name="personal",
            help="Personal organization commands"
        )

        # Init command
        @personal_app.command("init")
        def init_workspace(...):
            """Initialize personal workspace."""
            pass

        # Tasks sub-commands
        tasks_app = typer.Typer(name="tasks")
        @tasks_app.command("add")
        def tasks_add(...): pass
        @tasks_app.command("list")
        def tasks_list(...): pass
        # ... etc

        personal_app.add_typer(tasks_app)

        # Projects sub-commands
        projects_app = typer.Typer(name="projects")
        # ...

        # Routines sub-commands
        routines_app = typer.Typer(name="routines")
        # ...

        # Agenda sub-commands
        agenda_app = typer.Typer(name="agenda")
        # ...

        # Review sub-commands
        review_app = typer.Typer(name="review")
        # ...

        # Domains sub-commands
        domains_app = typer.Typer(name="domains")
        # ...

        # Tags sub-commands
        tags_app = typer.Typer(name="tags")
        # ...

        # Search command
        @personal_app.command("search")
        def search(query: str, ...):
            """Search across all tasks."""
            pass

        # Archive sub-commands
        archive_app = typer.Typer(name="archive")
        # ...

        app.add_typer(personal_app)

    def register_sdk_models(self) -> dict[str, type[BaseEntity]]:
        """Register personal models."""
        from better_notion.plugins.official.personal_sdk.models import (
            Domain, Tag, Project, Task, Routine, Agenda
        )
        return {
            "Domain": Domain,
            "Tag": Tag,
            "Project": Project,
            "Task": Task,
            "Routine": Routine,
            "Agenda": Agenda,
        }

    def register_sdk_caches(self, client: NotionClient) -> dict[str, Cache]:
        """Register personal caches."""
        return {
            "domains": Cache(),
            "tags": Cache(),
            "projects": Cache(),
            "tasks": Cache(),
            "routines": Cache(),
            "agenda": Cache(),
        }

    def register_sdk_managers(self, client: NotionClient) -> dict[str, Any]:
        """Register personal managers."""
        from better_notion.plugins.official.personal_sdk.managers import (
            TaskManager, ProjectManager, RoutineManager, TagManager
        )
        return {
            "tasks": TaskManager(client),
            "projects": ProjectManager(client),
            "routines": RoutineManager(client),
            "tags": TagManager(client),
        }

    def get_info(self) -> dict:
        return {
            "name": "personal",
            "version": "1.0.0",
            "description": "Personal organization and productivity system",
            "author": "Better Notion Team",
            "official": True,
            "category": "productivity",
        }
```

### Workspace Initialization

```python
class PersonalWorkspaceInitializer(WorkspaceInitializer):
    """Initialize personal workspace."""

    EXPECTED_DATABASES = [
        "Domains",
        "Tags",
        "Projects",
        "Tasks",
        "Routines",
        "Agenda",
    ]

    async def initialize_workspace(
        self,
        parent_page_id: str,
        workspace_name: str = "Personal Workspace",
    ) -> dict[str, str]:
        """Create all personal databases with relationships."""

        # Create databases
        domain_db = await self._create_database(parent_page_id, "Domains", ...)
        tag_db = await self._create_database(parent_page_id, "Tags", ...)
        project_db = await self._create_database(parent_page_id, "Projects", ...)
        task_db = await self._create_database(parent_page_id, "Tasks", ...)
        routine_db = await self._create_database(parent_page_page_id, "Routines", ...)
        agenda_db = await self._create_database(parent_page_id, "Agenda", ...)

        # Create relationships
        await self._create_relation(
            database=project_db,
            name="Domain",
            target=domain_db,
        )
        await self._create_relation(
            database=task_db,
            name="Domain",
            target=domain_db,
        )
        await self._create_relation(
            database=task_db,
            name="Project",
            target=project_db,
        )
        await self._create_relation(
            database=task_db,
            name="Parent Task",
            target=task_db,  # Self-referential
        )
        await self._create_relation(
            database=task_db,
            name="Tags",
            target=tag_db,  # Many-to-many
            dual_property="Tasks"
        )
        await self._create_relation(
            database=routine_db,
            name="Domain",
            target=domain_db,
        )
        await self._create_relation(
            database=agenda_db,
            name="Task",
            target=task_db,
        )
        await self._create_relation(
            database=agenda_db,
            name="Project",
            target=project_db,
        )

        # Save configuration
        self.save_database_ids()

        return self._database_ids
```

### Review Command Implementation

```python
async def review_command(review_type: str):
    """Run interactive review."""

    client = get_client()

    if review_type == "daily":
        # Determine morning vs evening
        hour = datetime.now().hour
        mode = "morning" if hour < 12 else "evening"

        if mode == "morning":
            await daily_morning_review(client)
        else:
            await daily_evening_review(client)

    elif review_type == "weekly":
        await weekly_review(client)
    elif review_type == "monthly":
        await monthly_review(client)

async def daily_morning_review(client):
    """Guided morning review."""

    # 1. Ask for focus
    focus = typer.prompt("What's your main focus for today?")

    # 2. Show today's priorities
    tasks = await get_priority_tasks(client, days=1)
    typer.echo("\n📋 Today's Priorities:")
    for task in tasks:
        typer.echo(f"  [ ] {task.title}")

    # 3. Ask for top 3
    top_3 = typer.prompt("Which 3 tasks will you complete? (comma-separated)")

    # 4. Show morning routines
    routines = await get_routines_due(client, time_of_day="morning")
    typer.echo("\n🌅 Morning Routines:")
    for routine in routines:
        typer.echo(f"  [ ] {routine.name}")

    # 5. Ask for time blocks
    blocks = typer.prompt("Any time blocks to schedule today?")

    # Save responses to journal or notes
    # ...

async def weekly_review(client):
    """Guided weekly review."""

    # 1. Show completed tasks this week
    completed = await get_completed_tasks(client, days=7)
    typer.echo(f"\n✅ Completed {len(completed)} tasks this week")

    # 2. Show domain breakdown
    domain_stats = await get_domain_breakdown(client, days=7)
    typer.echo("\n📊 Time by Domain:")
    for domain, count in domain_stats.items():
        typer.echo(f"  {domain}: {count} tasks")

    # 3. Show project progress
    projects = await get_active_projects(client)
    typer.echo("\n🚀 Project Progress:")
    for project in projects:
        typer.echo(f"  {project.name}: {project.progress}%")

    # 4. Ask for priorities
    priorities = typer.prompt("What are your top 3 priorities for next week?")

    # 5. Check routine streaks
    routines = await get_all_routines(client)
    typer.echo("\n🔥 Routine Streaks:")
    for routine in routines:
        typer.echo(f"  {routine.name}: {routine.streak} days")

    # 6. Ask for neglected areas
    neglected = typer.prompt("Any areas of your life that need attention?")

    # Save and plan next week
    # ...
```

## Integration with Existing Features

### Independent from Agents Plugin

The personal plugin is **completely independent** from the agents plugin:

- Separate workspace (`~/.notion/personal.json` vs `~/.notion/workspace.json`)
- Separate databases in Notion (can be in different pages)
- Different commands (`personal` vs `agents`)
- No risk of conflicts or confusion

**Why separate?**
- Mental clarity: separate contexts (work vs personal)
- Different workflows: personal doesn't need versions, bug reports, etc.
- Can use personal plugin without agents plugin
- Can have both active simultaneously

### Reusable Infrastructure

The personal plugin will leverage:

1. **#32 SDK Plugin System** - Register models, caches, managers
2. **#16 Templates System** - Generate database structures (optional)
3. **#22 Query Builder** - Complex task queries (optional)
4. **#17 Bulk Operations** - Batch operations on tasks (optional)

### Example Workflow

```bash
# Initialize separate workspace
personal init --parent-page PAGE_ID

# Add personal task
personal tasks add "Buy groceries" --domain Personal --priority Medium

# Later, switch to work context
agents tasks next  # Different system

# Switch back to personal
personal tasks list --today
```

## Benefits

1. **Personal Productivity**: Quick task capture, break down complex tasks
2. **Life Balance**: Track across domains (Work, Health, Personal)
3. **Flexible Organization**: Tags provide cross-cutting context beyond domains
4. **Powerful Search**: Find anything instantly with full-text search
5. **Clean Workspace**: Archive system keeps history without clutter
6. **Habit Formation**: Routine tracking with streaks
7. **Clarity**: Multi-level subtasks provide concrete next steps
8. **Reflection**: Guided reviews for continuous improvement
9. **Independence**: Separate from work/agents context
10. **Simplicity**: Static filters, no AI complexity
11. **Speed**: Optimized for quick capture and action

## Risks & Mitigations

| Risk | Mitigation |
|------|------------|
| **Scope creep** | Start with MVP (tasks + projects + subtasks), expand incrementally |
| **Subtask complexity** | Self-referential relation is simple, limit depth to 3 levels |
| **Performance** | Use caching, limit queries to today/this week |
| **Confusion with agents** | Clear separation, different commands, different workspaces |
| **Maintenance burden** | Follow agents pattern, reuse infrastructure |

## Success Metrics

1. ✅ Can add a task in < 5 seconds
2. ✅ Task filtering shows actionable subtasks (not just high-level tasks)
3. ✅ Daily review takes < 3 minutes
4. ✅ Subtasks work reliably (no circular references)
5. ✅ Routines track streaks correctly
6. ✅ Zero confusion between personal and agents plugins

## Related Issues

This plugin is inspired by but independent from:
- #031: Workflow Management System (agents plugin) - different use case
- #032: SDK Plugin System - infrastructure used by both
- #016: Templates System - could generate personal workspace

## Next Steps

1. **Approve this spec** for the personal plugin
2. **Phase 1 implementation** (foundation + init)
3. **Phase 2 implementation** (core CRUD)
4. **Test with real data** (personal tasks, routines)
5. **Iterate** based on usage
6. **Add advanced features** (search, archive, reviews)
7. **Document and polish**

## Estimated Timeline

- **Phase 1-2** (Foundation + CRUD + Tags): 2 weeks
- **Phase 3-5** (Subtasks + Routines + Agenda): 2.5 weeks
- **Phase 6** (Search & Archive): 1 week
- **Phase 7** (Reviews): 1 week
- **Phase 8** (Polish): 3 days

**Total: 6-7 weeks** for complete implementation

**MVP** (Phases 1-3): 3 weeks - Can add tasks with tags, break into subtasks, basic filtering

---

## Appendix: Sample Usage Session

```bash
# First time setup
$ personal init --parent-page page123
✓ Personal workspace initialized
  - 6 databases created (Domains, Tags, Projects, Tasks, Routines, Agenda)
  - Workspace ID: personal-abc123
  - Config saved to ~/.notion/personal.json

# Set up domains (auto-created)
$ personal domains list
Domains:
  • Work
  • Health
  • Personal

# Set up tags (auto-created)
$ personal tags list
Tags:
  • @home (Context)
  • @work (Context)
  • @phone (Context)
  • @quick (Time)
  • @high-energy (Energy)

# Create custom tag
$ personal tags create "@errands" --category Context --color Orange
✓ Tag created: @errands

# Create a project
$ personal projects create "Get in shape" --domain Health --priority High
✓ Project created: "Get in shape"
  ID: proj-456

# Add top-level tasks with tags
$ personal tasks add "Create workout plan" \
  --project "Get in shape" \
  --priority High \
  --tags "@computer,@high-energy"
✓ Task created: "Create workout plan"
  ID: task-789

# Break down into subtasks
$ personal tasks add "Define goals" --parent task-789 --tags "@quick"
✓ Subtask created

$ personal tasks add "Choose exercises" --parent task-789 --tags "@computer"
✓ Subtask created

$ personal tasks add "Create weekly schedule" --parent task-789
✓ Subtask created

# Break down subtask further
$ personal tasks add "Research strength exercises" --parent <choose-exercises-id>
✓ Sub-subtask created

$ personal tasks add "Research cardio options" --parent <choose-exercises-id>
✓ Sub-subtask created

# Add routine
$ personal routines create "Morning exercise" --frequency Weekdays --domain Health --best-time "Morning" --duration 45
✓ Routine created: "Morning exercise"

# Mark routine done
$ personal routines check routine-123
✓ Routine completed! Streak: 1 day

# Mark subtask done
$ personal tasks done task-456
✓ Task marked as Done

# Evening review
$ personal review daily

DAILY REVIEW - Monday Evening

✅ What you accomplished:
  • Completed 2 tasks
  • Checked off 1 routine
  • Worked on: "Get in shape"

💭 Reflection:
  What went well today? > Started workout plan
  What could be improved? > Need more time for exercise

📅 Tomorrow's preview:
  • 2 high-priority tasks
  • Morning routine: Exercise
  • Focus: Choose exercises for workout plan

✓ Review saved

# Search for tasks
$ personal search "gym"
Searching for "gym"...

Found 3 tasks:
  1. "Research gym options" - Health, High Priority, @computer
  2. "Buy gym membership" - Health, Medium Priority, @errands
  3. "Create gym routine" - Health, Low Priority, @high-energy

# Filter by tag
$ personal tasks list --tag "@quick"
Quick tasks (5):
  • "Define goals" - Done
  • "Call dentist" - Todo, @phone
  • "Pay electricity bill" - Todo, @errands

# Archive old completed tasks
$ personal archive tasks --older-than 90
Archived 47 tasks completed more than 90 days ago
✓ Archive complete

# List archived items
$ personal archive list --domain Health
Archived Health tasks (12):
  • "Summer workout plan" - Archived 2024-11-15
  • "Annual checkup" - Archived 2024-10-20

# Restore if needed
$ personal archive restore task-abc123
✓ Task "Summer workout plan" restored to active status
```

This plugin provides a complete personal productivity system with flexible tagging, powerful search, and archive management while maintaining clean separation from the agents workflow system.
