---
Feature Request: Bulk Operations & Batch Processing
Author: Claude
Status: Proposed
Priority: High (Phase 2 - Productivity)
Labels: enhancement, batch, performance
---

# Bulk Operations & Batch Processing

## Summary

Enable users to perform operations on multiple pages, blocks, or database items in a single command, with support for filtering, confirmation, and rollback.

## Problem Statement

Currently, all operations in the CLI work on single items. When users need to:
- Update 50 tasks to "completed" status
- Move multiple blocks to another page
- Export an entire database
- Reorganize content across pages

They must write scripts or execute commands manually, which is:
- Time-consuming
- Error-prone
- Lacks confirmation/safety mechanisms

## Proposed Solution

Implement a bulk operations system with:
1. Query-based selection (filters, search results)
2. Dry-run mode for preview
3. Confirmation prompts
4. Progress tracking
5. Atomic operations (all-or-nothing)
6. Rollback capability

## User Stories

### As a project manager
- I want to mark all completed tasks as "archived" in one command
- I want to move all meeting notes from Q1 to an archive page
- I want to see what will be affected before executing

### As a content manager
- I want to export an entire database to markdown
- I want to bulk-update properties across multiple pages
- I want to track progress of long-running operations

### As a developer
- I want scriptable batch operations
- I want atomic transactions (rollback on failure)
- I want rate limiting to avoid hitting API limits

## Proposed CLI Interface

```bash
# Bulk update pages based on query
notion pages bulk-update \
  --database=<db_id> \
  --filter='status = "active"' \
  --set-property='status:completed' \
  --dry-run

# Bulk move blocks
notion blocks bulk-move \
  --source-parent=<page_id> \
  --destination-parent=<new_page_id> \
  --filter='type = "to_do"' \
  --confirm

# Bulk delete
notion pages bulk-delete \
  --query='archived = true' \
  --older-than=90days \
  --confirm

# Export database
notion databases export <db_id> \
  --format=markdown \
  --output=./docs/ \
  --include-attachments

# Bulk create pages
notion pages bulk-create \
  --template="Meeting Notes" \
  --from-csv=./meetings.csv \
  --column-mapping='date:Name,attendees:Attendees'

# Check operation status
notion bulk status <operation_id>

# Cancel running operation
notion bulk cancel <operation_id>

# Rollback operation
notion bulk rollback <operation_id>
```

## Operation Modes

### 1. Dry-Run Mode (Default for safety)
```bash
notion pages bulk-update --filter='status = "review"' \
  --set-property='status:approved' --dry-run

# Output:
# ⚠️  Dry-run mode - no changes will be made
#
# Found 15 pages matching filter
# Will update:
#   • "Project A Review" (id: abc-123)
#   • "Task Review Q1" (id: def-456)
#   • ... (13 more)
#
# Confirm? [y/N]:
```

### 2. Interactive Mode
```bash
notion pages bulk-update ... --interactive
# Shows progress bar and asks for confirmation at each step
```

### 3. Silent/Batch Mode
```bash
notion pages bulk-update ... --yes --quiet
# No prompts, suitable for scripts
```

## Supported Operations

| Entity | Operations | Notes |
|--------|-----------|-------|
| **Pages** | update, delete, move, archive | Property updates, parent changes |
| **Blocks** | move, delete, update | Content updates, reorganization |
| **Databases** | export, query | Bulk data extraction |
| **Users** | N/A | Privacy concerns |

## Rate Limiting & Progress

```bash
notion pages bulk-update \
  --filter='status = "todo"' \
  --set-property='status:done' \
  --rate-limit=3 \
  --progress

# Output:
# Updating pages... [██████████████████░] 85% (450/529)
# ETA: 2m 15s | Rate: 3.2 req/s | Errors: 0
```

## Error Handling

```bash
notion pages bulk-update ... --on-error=continue

# Options:
# --on-error=stop     : Stop on first error (default)
# --on-error=continue : Skip failed items, continue
# --on-error=retry    : Retry failed items N times
# --max-retries=3     : Max retry attempts
```

## Rollback Support

```bash
# Operation is logged
notion bulk status abc-123
# Status: Completed
# Started: 2025-01-28 10:00:00
# Completed: 2025-01-28 10:05:23
# Affected: 529 pages
# Changes logged: .notion/logs/operation-abc-123.json

# Rollback if needed
notion bulk rollback abc-123
# ⚠️  This will revert 529 changes. Confirm? [y/N]
```

## Acceptance Criteria

- [ ] Can bulk-update pages with filters
- [ ] Can bulk-move blocks between pages
- [ ] Can bulk-delete with confirmation
- [ ] Dry-run mode shows exact changes
- [ ] Progress tracking for long operations
- [ ] Rate limiting to avoid API limits
- [ ] Error handling strategies (stop/continue/retry)
- [ ] Operation logging and rollback
- [ ] Export entire database to multiple formats
- [ ] Bulk create from CSV/JSON

## Implementation Notes

### Architecture
```
CLI Command → BulkOperationManager → BatchProcessor
                                      ↓
                                 ItemQueue → RateLimiter → API Client
                                      ↓
                                 OperationLog
```

### Components
1. **BulkOperationManager**: Orchestrates batch operations
2. **QueryParser**: Converts filters to Notion API queries
3. **RateLimiter**: Controls API request rate
4. **ProgressTracker**: Shows real-time progress
5. **OperationLogger**: Records all changes for rollback
6. **RollbackManager**: Reverts operations

### Transaction Safety
- Use optimistic locking for concurrent operations
- Log all operations before execution
- Store pre-operation state for rollback
- Support partial rollback on failure

### Performance Considerations
- Parallel processing where possible (with rate limiting)
- Chunk operations to avoid memory issues
- Cache frequently accessed entities
- Progress persistence (resume after interruption)

## Use Cases

### 1. Database Cleanup
```bash
# Archive completed tasks older than 90 days
notion pages bulk-update \
  --database=<tasks_db> \
  --filter='completed_before < -90days' \
  --set-property='archived:true' \
  --confirm
```

### 2. Content Reorganization
```bash
# Move all 2024 content to archive
notion pages bulk-move \
  --query='created < 2025-01-01 AND created > 2024-01-01' \
  --destination=<archive_page> \
  --dry-run
```

### 3. Bulk Import
```bash
# Create pages from CSV
notion pages bulk-create \
  --template="Task" \
  --from-csv=./tasks.csv \
  --mapping='title:Task,assigned:Assignee,due:Due Date'
```

### 4. Database Export
```bash
# Export with custom formatting
notion databases export <db_id> \
  --format=markdown \
  --output=./export/ \
  --filename-pattern='{title}-{id}.md' \
  --include-properties \
  --flatten-blocks
```

## Benefits

1. **Efficiency**: 100x faster than manual operations
2. **Consistency**: Apply same changes across all items
3. **Safety**: Dry-run, confirmation, and rollback
4. **Visibility**: Progress tracking and error reporting
5. **Automation**: Scriptable batch operations

## Risks & Mitigations

| Risk | Mitigation |
|------|------------|
| Accidental mass changes | Default dry-run mode, confirmations |
| API rate limits | Built-in rate limiting, chunking |
| Partial failures | Transaction logging, rollback |
| Performance issues | Progress bars, resume capability |

## Future Enhancements

- Scheduled bulk operations (cron-like)
- Bulk operations across workspaces
- Visual operation builder
- Operation templates
- Multi-step workflows
- Undo/redo at CLI level

## Related Issues

- #001: Templates System
- #003: Workflows System
- #013: Performance Monitoring

## Estimated Complexity

- **Backend**: High (transaction management, rate limiting)
- **CLI**: Medium (command design, progress display)
- **Testing**: High (many edge cases, error scenarios)

**Estimated Effort**: 3-4 weeks for MVP
