# Agents Plugin Testing - Issues Summary

## Overview

This document summarizes all issues discovered during real-world testing of the agents workflow management plugin (v1.4.0).

**Test Date**: 2026-01-29
**Version Tested**: better-notion 1.4.0
**Test Environment**: Windows 11, Python 3.14, Notion API
**Test Scope**: End-to-end testing of agents CLI commands

---

## Issue Summary

| # | Issue | Priority | Status | File |
|---|-------|----------|--------|------|
| #033 | pages create --root asyncio error | **CRITICAL** | Open | `docs/issues/033-pages-create-asyncio-error.md` |
| #034 | agents init Bad request | **CRITICAL** | Open | `docs/issues/034-agents-init-bad-request.md` |
| #035 | databases create Bad request | **CRITICAL** | Open | `docs/issues/035-databases-create-bad-request.md` |
| #036 | tasks next no project validation | **MEDIUM** | Open | `docs/issues/036-tasks-next-no-validation.md` |
| #037 | Missing parameter validation | **MEDIUM** | Open | `docs/issues/037-missing-parameter-validation.md` |
| #038 | Generic API error messages | **LOW** | Open | `docs/issues/038-generic-api-error-messages.md` |

---

## Critical Issues (Blockers)

### #033: `notion pages create --root` - AsyncIO Error

**Impact**: Cannot create pages via CLI
**Root Cause**: `asyncio.run()` called within running event loop
**Location**: `better_notion/_cli/commands/pages.py:130`

**Commands Affected**:
- `notion pages create --root --title "Test"`

**Fix Required**:
- Replace `asyncio.run()` with `typer.run_async()` or proper async handling
- Test on all platforms (Windows, Linux, Mac)

**Estimated Fix Time**: 2-3 hours

---

### #034: `notion agents init` - Generic Bad Request

**Impact**: Cannot initialize agents workspace
**Root Cause**: Unknown - error swallowed without details
**Location**: `better_notion/utils/agents/workspace.py`

**Commands Affected**:
- `notion agents init --parent-page <id> --name "Test"`

**Investigation Needed**:
- Add detailed logging to see which database creation fails
- Validate all 8 database schemas against Notion API
- Test with minimal database (1 property)

**Estimated Fix Time**: 4-6 hours (investigation + fix)

---

### #035: `notion databases create` - Schema Format Unclear

**Impact**: Cannot create databases via CLI
**Root Cause**: Schema format undocumented, no validation
**Location**: `better_notion/_cli/commands/databases.py`

**Commands Affected**:
- `notion databases create --parent <id> --title "Test" --schema "{...}"`

**Fix Required**:
1. Document schema format with examples
2. Add schema validation
3. Provide default schema (title-only)
4. Add --interactive mode or --schema-template

**Estimated Fix Time**: 3-4 hours

---

## Medium Priority Issues (UX Problems)

### #036: `notion agents tasks next` - No Project Validation

**Impact**: Silent failures, confusing
**Root Cause**: Doesn't validate if project_id exists
**Location**: `better_notion/plugins/official/agents_sdk/managers.py`

**Example**:
```bash
notion agents tasks next --project-id "invalid-id"
# Returns: {"success": true, "message": "No available tasks found"}
# Should: Error "Project not found"
```

**Fix Required**:
- Validate project_id exists (check workspace config)
- Add clear error if project doesn't exist
- Apply same fix to other managers (Project, Version, Idea, etc.)

**Estimated Fix Time**: 2-3 hours

---

### #037: Missing Parameter Validation

**Impact**: Invalid parameters accepted, confusing behavior
**Root Cause**: Systematic lack of input validation
**Location**: Multiple files

**Commands Affected**:
- `notion agents ideas review --count -5` (should error)
- `notion agents incidents mttr --within-days 0` (should error)
- `notion agents tasks complete --actual-hours -3` (should error)

**Fix Required**:
1. Add validation helpers
2. Validate at CLI level
3. Validate at manager level
4. Add comprehensive tests

**Estimated Fix Time**: 7-10 hours (systematic fix)

---

## Low Priority Issues (UX Improvements)

### #038: Generic API Error Messages

**Impact**: Difficult debugging, poor UX
**Root Cause**: All errors wrapped generically
**Location**: `better_notion/_cli/response.py`

**Example**:
```bash
notion agents orgs get "invalid-id"
# Returns: {"code": "GET_ORG_ERROR", "message": "Bad request"}
# Should: {"code": "NOT_FOUND", "message": "Organization not found", ...}
```

**Fix Required**:
1. Create NotionErrorHandler utility
2. Detect error types (404, 400, 401, 429)
3. Add context and suggestions
4. Define error code standards

**Estimated Fix Time**: 10-13 hours (comprehensive)

---

## Common Patterns

### Root Causes

1. **Async/Await Issues** - Improper use of `asyncio.run()`
2. **Error Swallowing** - Generic try/catch loses details
3. **No Validation** - Parameters not validated before use
4. **Poor Error Messages** - API errors not enriched with context

### Affected Components

| Component | Issues Count | Priority |
|-----------|---------------|----------|
| CLI Commands | 3 | Critical |
| Managers | 2 | Medium |
| Error Handling | 1 | Low |
| Validation | 2 | Medium |

---

## Recommended Fix Order

### Phase 1: Unblock Core Functionity (1-2 days)

1. **#033** - Fix pages create asyncio (2-3h)
2. **#034** - Fix agents init with detailed logging (4-6h)
3. **#035** - Fix databases create with schema validation (3-4h)

### Phase 2: Improve UX (1-2 days)

4. **#036** - Add project validation (2-3h)
5. **#037** - Add parameter validation systematically (7-10h)

### Phase 3: Polish (1 day)

6. **#038** - Enhance error messages (10-13h)

**Total Estimated Time**: 5-7 days

---

## Testing Recommendations

Once issues are fixed:

### Smoke Tests
```bash
# Basic CRUD
notion agents init --parent-page <id> --name "Test"
notion agents orgs create --name "Test Org" --slug "test"
notion agents projects create --name "Test Project" --org-id <org-id>

# Workflows
notion agents tasks next
notion agents tasks claim <task-id>
notion agents tasks start <task-id>
notion agents tasks complete <task-id> --actual-hours 2
```

### Error Case Tests
```bash
# Invalid IDs
notion agents orgs get "invalid-id"
notion agents tasks next --project-id "invalid-id"

# Invalid parameters
notion agents ideas review --count -5
notion agents incidents mttr --within-days 0
notion agents tasks complete <task-id> --actual-hours -3

# Missing workspace
notion agents orgs create --name "Test" --slug "test"
```

---

## Creation Commands

All issues created with:
```bash
# Issues are in docs/issues/
ls docs/issues/033-*.md
```

### To add to GitHub

```bash
# For each issue
gh issue create --title "$(basename $file .md)" --body "$(cat $file)"
```

Or create via GitHub UI using the markdown files.

---

## Conclusion

The agents plugin has **solid architecture** but suffers from **validation and error handling issues** that prevent real-world usage.

**Status**: **NOT PRODUCTION READY** - Requires fixes before deployment.

**Next Steps**:
1. Fix critical issues (#033, #034, #035)
2. Add validation systematically
3. Improve error messages
4. Comprehensive testing
5. User documentation

**After Fixes**: Plugin will be production-ready for AI agent workflow management.

---

**Tested By**: Claude Sonnet (AI Assistant)
**Date**: 2026-01-29
**Better Notion Version**: 1.4.0
