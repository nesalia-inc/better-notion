---
Feature Request: Custom Property Types
Author: Claude
Status: Proposed
Priority: Low (Phase 3 - Advanced)
Labels: enhancement, properties, customization
---

# Custom Property Types

## Summary

Allow users to define custom property types with validation, formatting, and custom behavior for specialized use cases.

## Problem

**Current Limitations:**
- Limited to Notion's built-in property types
- No custom validation rules
- No custom formatters/display logic
- Can't create domain-specific types (GitHub URLs, JIRA tickets, etc.)

## Solution

Custom property type system with:
1. **Type definitions**: Define custom types with validation
2. **Formatters**: Custom display and input formatting
3. **Validators**: Rule-based validation
4. **Type registry**: Reusable custom types
5. **Type templates**: Pre-built custom types

## CLI Interface

```bash
# Create custom type
notion property-type create "github-link" \
  --validator="^https://github\.com/.*" \
  --formatter="link" \
  --icon="github"

# Apply to database
notion property-type apply "github-link" \
  --database=<db_id> \
  --property="Repository"

# List custom types
notion property-type list

# Show type details
notion property-type info "github-link"

# Delete type
notion property-type delete "github-link"
```

## Built-in Custom Types

### GitHub Link
```yaml
name: "github-link"
description: "GitHub repository link"
validator: "^https://github\.com/[^/]+/[^/]+/?$"
formatter:
  type: "link"
  display: "{repo}"
  icon: "github"
  color: "purple"
examples:
  - "https://github.com/user/repo"
  - "https://github.com/org/project"
```

### JIRA Ticket
```yaml
name: "jira-ticket"
description: "JIRA ticket reference"
validator: "^[A-Z]+-\d+$"
formatter:
  type: "link"
  url_template: "https://jira.example.com/browse/{value}"
  display: "{value}"
  icon: "jira"
examples:
  - "PROJ-123"
  - "TASK-456"
```

### Email (Enhanced)
```yaml
name: "smart-email"
description: "Email with validation"
validator: "^[^@]+@[^@]+\.[^@]+$"
formatter:
  type: "email"
  gravatar: true
  display: "{name} <{email}>"
autocomplete:
  - source: "workspace-users"
  - recent: true
```

## Acceptance Criteria

- [ ] Define custom property types
- [ ] Validation rules
- [ ] Custom formatters
- [ ] Type templates included
- [ ] Reusable type registry

**Estimated Effort**: 2 weeks
