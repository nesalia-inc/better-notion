---
Feature Request: Advanced Query Builder
Author: Claude
Status: Proposed
Priority: High (Phase 1 - Quick Win)
Labels: enhancement, query, ux
---

# Advanced Query Builder

## Summary

Create an interactive query builder that simplifies database filtering, allows saving queries, and exports results in multiple formats.

## Problem Statement

Notion's query syntax is complex and hard to remember:
```bash
notion databases query <db> \
  --filter='and(property("Status").equals("Active"), property("Priority").greater_than(2))'
```

Issues:
- Complex syntax for simple queries
- No way to save/reuse queries
- Can't incrementally build queries
- No visual feedback on query results
- Hard to share queries between team members

## Proposed Solution

Interactive query builder with:
1. **Wizard mode**: Step-by-step query building
2. **Query templates**: Pre-built queries for common cases
3. **Named queries**: Save and reuse queries
4. **Query chaining**: Use query results as input
5. **Multiple export formats**: CSV, JSON, Markdown, etc.
6. **Visual feedback**: Live results as you build query

## User Stories

### As a business user
- I want to find all tasks assigned to me due this week
- I don't want to write complex filter syntax
- I want to save this query and reuse it weekly

### As a data analyst
- I want to export query results to CSV/Excel
- I want to combine multiple filters
- I want to sort and group results

### As a developer
- I want to script queries in automation
- I want to share queries via version control
- I want to test queries before production use

## Proposed CLI Interface

### Interactive Builder
```bash
notion query build --database=<db_id>

? Select property to filter:
  > Status
    Priority
    Assignee
    Due Date

? Select operator:
  > equals
    not_equals
    contains
    is_empty
    greater_than
    less_than
    in_next

? Select value:
  > Active
    In Progress
    Done

? Add another filter? (y/n): y

? Select property: Priority
? Select operator: greater_than
? Select value: 2

? Sort by:
  > Due Date (ascending)
    Created time (descending)
    Priority (descending)

? Save this query? (y/n): y
? Query name: active-high-priority
✓ Query saved!

Run query now? (y/n): y
Found 23 results
```

### Quick Query Commands
```bash
# Run named query
notion query run "active-high-priority"

# List saved queries
notion query list

# Show query details
notion query info "active-high-priority"

# Edit query
notion query edit "active-high-priority"

# Delete query
notion query delete "active-high-priority"
```

### One-Shot Queries
```bash
# Simple query
notion query --database=<db> \
  --property="Status" \
  --operator="equals" \
  --value="Active"

# Multiple filters
notion query --database=<db> \
  --filter="Status=Active" \
  --filter="Priority>2" \
  --sort="Due Date:asc"

# Combined filters (AND/OR)
notion query --database=<db> \
  --and="Status=Active,Priority>2" \
  --or="Assignee=@me,Assignee=unassigned"
```

### Export Query Results
```bash
notion query run "my-query" \
  --export=csv \
  --output=./results.csv

notion query run "my-query" \
  --export=markdown \
  --output=./report.md

notion query run "my-query" \
  --export=json \
  --output=./data.json

notion query run "my-query" \
  --format=table  # Rich table output
```

## Query Syntax (Human-Friendly)

### Simple Filters
```
status=active                           # Property equals value
status!=done                            # Property not equals
priority>2                             # Greater than
due_date<2025-02-01                     # Less than
name~"project"                          # Contains
tags=["urgent","backend"]               # In list
assignee=@me                           # Current user
assignee=@unassigned                    # Unassigned
```

### Complex Filters
```
# AND logic
status=active&priority=high

# OR logic
status=active|status=in-review

# Grouping
(status=active|status=review)&priority>2

# Negation
!status=archived

# Nested
(priority>3|due_date<today)&!status=done
```

### Sorting
```
--sort="due_date:asc"
--sort="created_time:desc,priority:asc"
```

## Saved Queries Format

### YAML Format
```yaml
name: "active-high-priority"
description: "Active tasks with high priority"
database: "<database_id>"
filters:
  - property: "Status"
    operator: "equals"
    value: "Active"
  - property: "Priority"
    operator: "greater_than"
    value: 2
  - logic: and
sort:
  - property: "Due Date"
    direction: "ascending"
limit: 100
format:
  columns: ["Title", "Status", "Priority", "Due Date"]
```

### JSON Format
```json
{
  "name": "active-high-priority",
  "database": "<database_id>",
  "filters": [
    {"property": "Status", "operator": "equals", "value": "Active"},
    {"property": "Priority", "operator": "greater_than", "value": 2}
  ],
  "sort": [{"property": "Due Date", "direction": "asc"}]
}
```

## Query Templates

### Included Templates
```bash
# List templates
notion query templates

# Use template
notion query from-template "my-tasks" --customize
```

### Built-in Templates
1. **My Tasks**: `assignee=@me&status=active`
2. **Due This Week**: `due_date>today&due_date<+7days`
3. **High Priority**: `priority>=3&status=active`
4. **Overdue**: `due_date<today&status!=done`
5. **Recently Modified**: `last_edited>-7days`

## Query Chaining

### Use Query Results as Input
```bash
# Query 1: Get active tasks
notion query run "active-tasks" --save=./temp.json

# Query 2: Filter results
notion query --from=./temp.json \
  --filter="priority>2"

# Chain commands
notion query run "active-tasks" | \
  notion query --filter="priority>2" | \
  notion bulk-update --property="status:review"
```

## Live Results

### Incremental Query Building
```bash
$ notion query build --database=<db>
? Add filter: Status=active
Found 150 results

? Add filter: Priority>2
Found 45 results

? Add filter: Due Date<this week
Found 12 results

? Save as: urgent-this-week
✓ Saved!
```

## Acceptance Criteria

- [ ] Interactive query builder (wizard mode)
- [ ] Human-friendly query syntax
- [ ] Save/load named queries
- [ ] Query templates included
- [ ] Export to multiple formats (CSV, JSON, MD)
- [ ] Query chaining (use results as input)
- [ ] Sorting and limiting results
- [ ] Complex filters (AND/OR/NOT)
- [ ] Query validation before execution
- [ ] Share queries (import/export)

## Implementation Notes

### Query Parser
- Convert simple syntax (`status=active`) to Notion API format
- Support operator aliases (`=` → `equals`, `~` → `contains`)
- Parse complex logic (`&`, `|`, `!`, parentheses)

### Query Storage
- Saved queries: `~/.notion/queries/*.yaml`
- Query templates: `/usr/share/notion/queries/*.yaml`
- User templates: `~/.notion/query-templates/*.yaml`

### Components
1. **QueryBuilder**: Interactive wizard
2. **QueryParser**: Parse query syntax
3. **QueryStore**: Save/load queries
4. **QueryExecutor**: Run queries via API
5. **QueryExporter**: Export results
6. **QueryValidator**: Validate query syntax

## Benefits

1. **Simplicity**: No need to remember complex syntax
2. **Reusability**: Save and share queries
3. **Efficiency**: Build queries interactively
4. **Flexibility**: Export in any format
5. **Discovery**: Templates show what's possible

## Related Issues

- #002: Bulk Operations
- #005: Interactive Shell

## Estimated Complexity

- **Backend**: Medium (query parser, executor)
- **CLI**: High (interactive builder)
- **Testing**: Medium (query variations)

**Estimated Effort**: 2-3 weeks for MVP
