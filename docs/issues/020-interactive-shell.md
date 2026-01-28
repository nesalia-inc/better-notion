---
Feature Request: Interactive Shell Mode
Author: Claude
Status: Proposed
Priority: High (Phase 1 - Quick Win)
Labels: enhancement, ux, shell
---

# Interactive Shell Mode

## Summary

Implement an interactive REPL shell for the Notion CLI that maintains context, reduces repetitive typing, and provides a more intuitive experience for complex operations.

## Problem Statement

Current CLI requires re-typing flags and IDs for every command:
```bash
notion pages get abc-123-def --format=json
notion pages update abc-123-def --property="status:done"
notion pages get abc-123-def
notion blocks append abc-123-def --type=todo --content="Follow up"
```

This is:
- **Tedious**: Repeating page IDs and flags
- **Error-prone**: Copy-paste errors
- **Inefficient**: No command history or context
- **Intimidating**: Long commands with many flags

## Proposed Solution

Create an interactive shell with:
1. **Context persistence**: Remember current database/page
2. **Command history**: Navigate previous commands
3. **Tab completion**: Auto-complete IDs, properties, values
4. **Shell variables**: Store and reuse values
5. **Pipelining**: Chain operations
6. **Multi-select**: Operate on multiple items
7. **Friendly prompts**: Guides user through complex operations

## User Stories

### As a regular user
- I want to "enter" a database and work with its items
- I want to select multiple items and perform bulk operations
- I want to use short commands without typing full IDs
- I want command history and tab completion

### As a power user
- I want to write shell scripts within the shell
- I want to define aliases for common operations
- I want to pipe command results

## Proposed CLI Interface

```bash
# Start shell
notion shell

# Or enter specific context
notion shell --database=<db_id>
notion shell --page=<page_id>
```

### Shell Session Example

```bash
$ notion shell
Notion Shell v0.9.9
Type 'help' for commands, 'exit' to quit

notion> use database <tasks_db>
Entering database: Tasks (abc-123)
Context set: database=abc-123

tasks> list --filter="status = active"
  [1] Task 1 (def-456) - Review PR
  [2] Task 2 (ghi-789) - Write docs
  [3] Task 3 (jkl-012) - Fix bug

tasks> select 1,3
Selected: 2 items [def-456, jkl-012]

tasks> update --property="status:done"
✓ Updated 2 items

tasks> cd 2
Entering page: Task 2 (ghi-789)
Context set: page=ghi-789

Task 2> append --type=todo "Follow up with team"
✓ Added todo block

Task 2> properties
Title: Task 2
Status: active
Assignee: john@example.com
Priority: High

Task 2> set status=done
✓ Updated property

Task 2> back
Returning to database: Tasks

tasks> export --format=csv --output=tasks.csv
✓ Exported 15 items to tasks.csv

tasks> exit
Goodbye!
```

## Shell Commands

### Navigation
```bash
# Context commands
use database <id>     # Enter database context
use page <id>         # Enter page context
cd                    # Go to parent
cd <id>              # Enter page/database by ID
back                 # Go back to previous context
pwd                  # Show current context
```

### Query & Selection
```bash
# List with smart defaults
list                   # List items in current context
list --filter="..."    # Filtered list
list --limit=10       # Limit results

# Multi-select
select 1,2,3          # Select by number
select all            # Select all
select --filter="..."  # Select by condition
unselect 2            # Deselect item

# Show selection
selection             # Show selected items
count                 # Count selected items
```

### Operations on Selection
```bash
# All operations work on selection
update --property="status:done"
delete
archive
export --format=markdown
move --to=<parent_id>
```

### Shell Variables
```bash
# Set variables
set status=done
set assignee=@me
set db=<database_id>

# Use variables
update --property="status:$status"
query --database=$db

# List variables
vars

# Unset variable
unset status
```

### Command History
```bash
history                # Show command history
history 10            # Last 10 commands
!5                    # Run command #5
!!                    # Run last command
!update              # Run last update command
```

### Aliases
```bash
# Create alias
alias done="update --property=status:done"
alias todo="append --type=todo"

# Use alias
done

# List aliases
aliases

# Remove alias
unalias done
```

### Pipelining
```bash
# Pipe operations
list --filter="status = active" | select 1,3,5 | update --property="priority:high"
list | export --format=json | jq '.[] | .title'
```

## Tab Completion

### Context-Aware Completion
```bash
tasks> upd<TAB>
update

tasks> update --prop<TAB>
--property

tasks> update --property=<TAB>
Title
Status
Priority
Assignee
Due Date

tasks> update --property=Status=<TAB>
active
done
blocked
```

### ID Completion
```bash
tasks> use database <TAB>
# Shows all databases with IDs
Tasks (abc-123-def)
Projects (def-456-ghi)
...

tasks> cd <TAB>
# Shows all pages with IDs
Task 1 (jkl-012-mno)
Task 2 (pqr-345-stu)
...
```

## Shell Features

### 1. Smart Context
```bash
# In database context
tasks> list           # Lists database entries
tasks> query          # Queries database
tasks> create         # Creates new entry

# In page context
Task 1> show          # Shows page content
Task 1> blocks        # Lists blocks
Task 1> properties    # Shows properties
Task 1> append        # Appends block
Task 1> update        # Updates content
```

### 2. Numbered References
```bash
tasks> list
  [1] Task 1 (abc-123)
  [2] Task 2 (def-456)
  [3] Task 3 (ghi-789)

tasks> select 1,2,3   # Use numbers instead of IDs
tasks> delete 1       # Delete first item
tasks> cd 2           # Enter second item
```

### 3. Bulk Operations
```bash
tasks> list --filter="status = active"
  [1] Task 1
  [2] Task 2
  [3] Task 3

tasks> select all
Selected: 3 items

tasks> update --property="priority:high"
✓ Updated 3 items

tasks> update --property="status:review"
✓ Updated 3 items

tasks> export --format=csv --output=review.csv
✓ Exported 3 items
```

### 4. Interactive Prompts
```bash
tasks> create --interactive
? Title: My Task
? Status [active]:
? Priority [1-5]: 3
? Assignee (tab to complete): <TAB>
  john@example.com
  jane@example.com
? Assignee: john@example.com
✓ Created page (new-id-123)
```

### 5. Command Chaining
```bash
# One-liners
list --filter="status = active" | select all | update --property="status=review"

# Multi-line
tasks> begin
  list --filter="status = active"
  select all
  update --property="status=review"
  export --format=markdown
end
```

## Configuration

### Shell Profile
```bash
# ~/.notion/shell-profile
alias active="list --filter=status:active"
alias done="update --property=status:done"
alias mine="list --filter=assignee=@me"

# Default context
set default_database=<db_id>

# Custom prompts
set prompt="[{context}] {selection_count}> "
```

### Shell Options
```bash
notion shell --options
# Display options:
colors=on
confirmation=on
numbers=on
timestamps=off
```

## Acceptance Criteria

- [ ] Interactive shell with REPL
- [ ] Context persistence (database, page)
- [ ] Command history (up/down arrows)
- [ ] Tab completion for IDs, properties, values
- [ ] Shell variables ($var)
- [ ] Aliases
- [ ] Multi-select with numbered references
- [ ] Pipelining commands
- [ ] Interactive prompts
- [ ] Shell profile/configuration

## Implementation Notes

### Technology
- **prompt_toolkit**: Rich CLI prompts, autocompletion
- **cmd2**: Shell framework with history
- **readline**: Alternative line editing

### Architecture
```
Shell REPL → CommandParser → ContextManager → Executor
                ↓                ↓
           CompletionEngine → CommandHistory
                ↓
           VariableStore
```

### Components
1. **Shell REPL**: Read-eval-print loop
2. **ContextManager**: Tracks current context (db, page, selection)
3. **CommandParser**: Parses shell commands (shorter syntax)
4. **CompletionEngine**: Tab completion logic
5. **CommandHistory**: Persistent history
6. **VariableStore**: Shell variables
7. **AliasManager**: Command aliases

## Benefits

1. **Efficiency**: Less typing, more doing
2. **Context**: Work with related items naturally
3. **Discoverability**: Tab completion shows options
4. **Safety**: See what you're operating on
5. **Learnability**: Easier for new users

## Related Issues

- #001: Templates System
- #002: Bulk Operations
- #007: Query Builder

## Estimated Complexity

- **Backend**: Medium (shell framework, context management)
- **CLI**: High (interactive features, completion)
- **Testing**: Medium (shell interactions)

**Estimated Effort**: 2-3 weeks for MVP
