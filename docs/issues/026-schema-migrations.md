---
Feature Request: Database Schema Migrations
Author: Claude
Status: Proposed
Priority: Medium (Phase 2 - Productivity)
Labels: enhancement, database, schema
---

# Database Schema Migrations

## Summary

Version control and migration system for database schema changes, enabling safe evolution of database structures.

## Problem

Currently, database schema changes are risky:
- No way to version schema changes
- Can't roll back if something breaks
- Manual schema updates are error-prone
- No migration planning or testing
- Hard to coordinate schema changes across team

## Solution

Migration system with:
1. **Migration files**: Versioned schema changes
2. **Up/down migrations**: Apply and rollback changes
3. **Dry-run mode**: Test migrations before applying
4. **Migration status**: Track applied migrations
5. **Conflict detection**: Detect breaking changes
6. **Auto-rollback**: Revert on failure

## CLI Interface

```bash
# Create migration
notion schema migrate create \
  --database=<db_id> \
  --name="add_priority_column" \
  --description="Add priority select property"

# Interactive migration builder
notion schema migrate create --interactive

# List migrations
notion schema migrate list --database=<db_id>

# Show migration details
notion schema migrate info "add_priority_column"

# Check migration status
notion schema migrate status --database=<db_id>

# Apply pending migrations
notion schema migrate apply --database=<db_id>

# Apply specific migration
notion schema migrate apply "add_priority_column" \
  --database=<db_id>

# Dry-run (test without applying)
notion schema migrate apply --dry-run --database=<db_id>

# Rollback migration
notion schema migrate rollback "add_priority_column" \
  --database=<db_id>

# Validate schema
notion schema validate --database=<db_id>
```

## Migration File Format

```yaml
name: "add_priority_column"
version: "001"
created_at: "2025-01-28T10:00:00Z"
description: "Add priority select property"

# Up migration
up:
  - type: "property.add"
    property:
      name: "Priority"
      type: "select"
      options: ["Low", "Medium", "High"]
      default: "Medium"

  - type: "property.update"
    property: "Status"
    default: "Not Started"

# Down migration (rollback)
down:
  - type: "property.remove"
    property: "Priority"

  - type: "property.update"
    property: "Status"
    default: null
```

## Migration Types

### Property Operations
```yaml
# Add property
- type: "property.add"
  property:
    name: "Tags"
    type: "multi_select"

# Remove property
- type: "property.remove"
  property: "OldField"

# Update property
- type: "property.update"
  property: "Status"
  changes:
    type: "select"
    options: ["Todo", "In Progress", "Done"]

# Rename property
- type: "property.rename"
  old_name: "OldName"
  new_name: "NewName"
```

### Data Migrations
```yaml
# Migrate data
- type: "data.migrate"
  source_property: "old_status"
  target_property: "new_status"
  mapping:
    "TODO": "Backlog"
    "DOING": "In Progress"
    "DONE": "Complete"

# Transform data
- type: "data.transform"
  property: "title"
  transform: "uppercase"

# Copy data
- type: "data.copy"
  source: "title"
  target: "summary"
```

## Migration Safety

### Dry-run Mode
```bash
notion schema migrate apply --dry-run
# Output:
# ⚠️  Dry-run mode - no changes will be made
#
# Migration: 001_add_priority_column
# Changes:
#   • Add property: Priority (select)
#   • Update 150 rows
#
# Estimated time: 2 minutes
# Confirm? [y/N]:
```

### Validation
```bash
notion schema migrate validate "001_add_priority"
# Checks:
# ✓ Migration syntax valid
# ✓ Property doesn't exist
# ✓ Options are unique
# ⚠️  Will modify 150 rows
```

### Conflict Detection
```bash
notion schema migrate check-conflicts
# Output:
# ⚠️  Potential conflicts detected:
#   • Migration 003 removes "Status" property
#   • Migration 005 uses "Status" property
#   • Order migrations to avoid issues
```

## Acceptance Criteria

- [ ] Create migration files
- [ ] Apply migrations (up/down)
- [ ] Dry-run mode
- [ ] Migration status tracking
- [ ] Rollback support
- [ ] Migration validation
- [ ] Conflict detection
- [ ] Data migration support
- [ ] Interactive migration builder

## Implementation Notes

### Components
1. **MigrationGenerator**: Create migration files
2. **MigrationRunner**: Apply/rollback migrations
3. **MigrationTracker**: Track applied migrations
4. **SchemaValidator**: Validate schema changes
5. **ConflictDetector**: Detect migration conflicts

### Storage
- Migrations: `~/.notion/migrations/*.yaml`
- State: `~/.notion/migrations/state.json`

**Estimated Effort**: 3 weeks
