# CLI Issues Index

This directory contains documented issues discovered during CLI testing of version 0.7.3.

## Test Summary
**Test Date**: 2026-01-27
**Test Document**: Complete Python Course (30+ blocks created)
**Status**: Creation works, retrieval broken

## Issues Overview

| ID | Title | Status |
|----|-------|--------|
| [001](./001-missing-dedicated-block-commands.md) | Missing Dedicated Block Commands | Open |
| [002](./002-todo-checked-parameter-bug.md) | Todo Command `--checked` Parameter Bug | Open |
| [003](./003-blocks-children-command-broken.md) | `notion blocks children` Command Broken | Open |
| [004](./004-pages-get-command-broken.md) | `notion pages get` Command Broken | Open |
| [005](./005-markdown-import-feature.md) | Feature Request: Create/Update Pages from Markdown | Open |

## Quick Reference

### Core Functionality Broken
- **Issue #003**: Cannot retrieve block children
- **Issue #004**: Cannot retrieve page content

### Usability Issues
- **Issue #002**: Todo `--checked` parameter doesn't accept values

### Enhancements
- **Issue #001**: Missing dedicated commands for common block types
- **Issue #005**: Create/Update pages from markdown files (Feature Request)

## Workarounds

### For Issue #001 (Missing Commands)
Use the generic `create` command instead:
```bash
# Instead of: notion blocks bullet --parent <id> --text "Item"
notion blocks create --parent <id> --type bullet --content "Item"

# Instead of: notion blocks quote --parent <id> --text "Quote"
notion blocks create --parent <id> --type quote --content "Quote"
```

### For Issue #002 (Todo --checked)
Omit the flag for unchecked, include it for checked:
```bash
# Unchecked (default)
notion blocks todo --parent <id> --text "Task"

# Checked
notion blocks todo --parent <id} --text "Task" --checked
```

### For Issue #003 & #004 (Broken Retrieval)
No workaround - must use Notion web UI to verify content.

## Pattern Analysis

All high-severity issues (#003, #004) share the same root cause:
- **Architectural confusion** between async functions and collection objects
- **Not properly awaiting** async functions before accessing attributes
- **Same pattern** as the previously fixed `BlockCollection.append()` bug (commit 6cc4373)

This suggests a systematic review of all CLI commands is needed to ensure proper async/await patterns.

## Next Steps

1. **Fix Issue #003** - BlockCollection.children() usage in CLI
2. **Fix Issue #004** - Page retrieval in CLI
3. **Fix Issue #002** - Make --checked accept values or use --checked/--unchecked flags
4. **Add Issue #001** - Add dedicated commands for consistency

## Testing Notes

The test created a comprehensive Python course with:
- ✅ Headings (H1, H2, H3)
- ✅ Paragraphs
- ✅ Bullet lists (via `create --type bullet`)
- ✅ Numbered lists (via `create --type numbered`)
- ✅ Code blocks with syntax highlighting
- ✅ Callouts (via `create --type callout`)
- ✅ Quotes (via `create --type quote`)
- ✅ Todo items

All **creation** commands work correctly. Only **retrieval** commands are broken.
