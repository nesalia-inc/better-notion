---
Feature Request: Cross-Workspace Operations
Author: Claude
Status: Proposed
Priority: Low (Phase 3 - Advanced)
Labels: enhancement, workspace, multi-tenant
---

# Cross-Workspace Operations

## Summary

Enable operations across multiple Notion workspaces from a single CLI instance, including copying content, syncing databases, and managing multiple accounts.

## Problem

**Current Limitations:**
- Only one workspace per CLI config
- Can't copy content between workspaces
- Can't sync databases across workspaces
- Manual logout/login required for workspace switching
- No unified view of multiple workspaces

## Solution

Multi-workspace support with:
1. **Workspace profiles**: Multiple workspace configurations
2. **Cross-workspace copy**: Copy pages/databases between workspaces
3. **Cross-workspace sync**: Sync databases across workspaces
4. **Unified commands**: Operate on multiple workspaces
5. **Workspace switching**: Easy workspace context changes

## CLI Interface

```bash
# List workspaces
notion workspaces list
# Output:
# • Personal (john-workspace) [active]
# • Work (company-workspace)

# Add workspace
notion workspaces add \
  --name="Work" \
  --token=$WORK_TOKEN \
  --icon=briefcase

# Switch workspace
notion workspaces switch "Work"
# Output:
# Switched to workspace: Work

# Remove workspace
notion workspaces remove "Work"

# Cross-workspace copy
notion copy <page_id> \
  --to-workspace="Work" \
  --preserve-properties

# Cross-workspace sync
notion sync-databases \
  --source=<db1> \
  --source-workspace="Personal" \
  --target=<db2> \
  --target-workspace="Work" \
  --direction=both

# Multi-workspace query
notion query --all-workspaces \
  --filter="status=active"
```

## Use Cases

### 1. Personal vs Work
```bash
# Copy task from personal to work
notion copy <task_id> \
  --to-workspace="Work" \
  --convert-properties
```

### 2. Database Sync
```bash
# Sync task database across workspaces
notion sync-databases \
  --source="Personal:Tasks" \
  --target="Work:Tasks" \
  --conflict="source-wins"
```

### 3. Unified View
```bash
# Search across all workspaces
notion search --all-workspaces "project X"

# List tasks from all workspaces
notion databases query --all-workspaces \
  --filter="assignee=@me"
```

## Acceptance Criteria

- [ ] Multiple workspace profiles
- [ ] Switch between workspaces
- [ ] Cross-workspace copy (pages, databases)
- [ ] Cross-workspace database sync
- [ ] Multi-workspace queries
- [ ] Workspace-specific tokens

**Estimated Effort**: 3 weeks
