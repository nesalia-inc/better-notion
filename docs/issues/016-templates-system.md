---
Feature Request: Templates & Snippets System
Author: Claude
Status: Proposed
Priority: High (Phase 1 - Quick Win)
Labels: enhancement, templates, ux
---

# Template & Snippets Management System

## Summary

Create and manage reusable page/block templates to standardize documentation and save time.

## Problem Statement

Users often create similar page structures repeatedly (meeting notes, project specs, roadmaps, etc.). Currently, there's no way to save and reuse these structures, leading to:
- Recreating the same layouts manually
- Inconsistent documentation across the workspace
- Wasted time on repetitive formatting

## Proposed Solution

Implement a template system that allows users to:
1. Create templates from existing pages
2. Build templates interactively
3. Apply templates to new pages with variable substitution
4. Share and manage templates across teams

## User Stories

### As a content creator
- I want to save a page structure as a template so I can reuse it later
- I want to use variables like `{{date}}`, `{{user}}`, `{{project}}` in templates
- I want to apply a template when creating a new page

### As a team lead
- I want to create standard templates for my team (meeting notes, reviews)
- I want to share templates with team members
- I want to ensure consistent documentation across the team

### As a power user
- I want to organize templates in categories
- I want to import/export templates
- I want to use templates in CLI commands

## Proposed CLI Interface

```bash
# List available templates
notion templates list
notion templates list --category="meetings"

# Create template from existing page
notion templates create "Meeting Notes" \
  --from-page=<page_id> \
  --category="meetings" \
  --description="Standard meeting notes template"

# Create template interactively
notion templates create "Project Spec" --interactive

# Apply template
notion templates apply "Meeting Notes" \
  --parent=<page_id> \
  --set="date:2025-01-28" \
  --set="project:Q1 Goals"

# Edit template
notion templates edit "Meeting Notes" --interactive

# Show template details
notion templates info "Meeting Notes"

# Delete template
notion templates delete "Meeting Notes"

# Export/Import
notion templates export "Meeting Notes" --output=./meeting-notes.json
notion templates import ./meeting-notes.json
```

## Template Format

Templates should support:
- **Block structure**: Preserve all block types and hierarchy
- **Properties**: Define property schemas with default values
- **Variables**: Placeholders for dynamic content
- **Instructions**: Help text for each section

Example template structure:
```json
{
  "name": "Meeting Notes",
  "description": "Standard meeting notes template",
  "category": "meetings",
  "variables": [
    {"name": "date", "type": "date", "default": "today"},
    {"name": "attendees", "type": "text", "prompt": true},
    {"name": "project", "type": "text", "required": false}
  ],
  "properties": {
    "Name": "{{date}} - Meeting",
    "Category": "Meeting"
  },
  "blocks": [
    {
      "type": "heading_1",
      "content": "Meeting Notes - {{date}}"
    },
    {
      "type": "heading_2",
      "content": "Attendees"
    },
    {
      "type": "bullet_list",
      "content": "{{attendees}}"
    },
    {
      "type": "heading_2",
      "content": "Agenda"
    },
    {
      "type": "to_do",
      "content": "Agenda item 1"
    },
    {
      "type": "heading_2",
      "content": "Notes"
    },
    {
      "type": "paragraph",
      "content": "Meeting notes go here..."
    }
  ]
}
```

## Acceptance Criteria

- [ ] Can create template from existing page
- [ ] Can create template interactively
- [ ] Can list all templates with filtering
- [ ] Can apply template with variable substitution
- [ ] Can edit existing templates
- [ ] Can delete templates
- [ ] Can export/import templates as JSON
- [ ] Can organize templates by category
- [ ] Variables are properly substituted
- [ ] Property schemas are applied

## Implementation Notes

### Storage Options
1. **Local storage** (`~/.notion/templates/`): Simple, offline-first
2. **Notion database**: Sync across devices, team sharing
3. **Hybrid**: Local cache + Notion backup

### Variable Types
- `{{date}}`: Date with optional format
- `{{user}}`: Current user name
- `{{timestamp}}`: Current datetime
- `{{prompt:name}}`: Interactive prompt
- Custom variables with `--set` flag

### Integration Points
- Works with `notion pages create` command
- Available in interactive shell
- Can be used in workflows

## Benefits

1. **Time Savings**: Eliminate repetitive setup work
2. **Consistency**: Standardized documentation
3. **Quality**: Ensure all required sections are included
4. **Team Alignment**: Everyone uses the same formats
5. **Flexibility**: Variables allow customization

## Future Enhancements

- Template inheritance (extend existing templates)
- Template marketplace (community templates)
- Template validation (required fields)
- Template versioning
- Template preview before application
- Conditional blocks based on variables

## Related Issues

- #002: Interactive Shell Mode
- #006: Workflows System
- #008: Plugin Marketplace

## Estimated Complexity

- **Backend**: Medium (template engine, storage)
- **CLI**: Medium (new commands, interactive mode)
- **Testing**: Medium (template variations, variable substitution)

**Estimated Effort**: 2-3 weeks for MVP
