# Public Documentation Structure

This document describes the organization and structure of the Better Notion SDK public documentation.

## Overview

The documentation is organized into logical sections to help developers quickly find the information they need, whether they are getting started or looking for specific API details.

## Documentation Sections

### 1. Home & Getting Started

**Target Audience**: New users evaluating or starting with the SDK

**Files**:
- `index.md` - Landing page with project overview, key features, and quick navigation
- `quickstart.md` - 5-minute getting started guide
- `getting-started/installation.md` - Installation instructions (pip, uv, requirements)
- `getting-started/authentication.md` - How to create a Notion integration and get API tokens
- `getting-started/basic-concepts.md` - Core concepts: Pages, Blocks, Databases, Users, entity model
- `getting-started/project-setup.md` - Setting up the SDK in a Python project

**Content Goals**:
- Get users from zero to first successful API call in under 10 minutes
- Explain the Notion API authentication model
- Introduce key SDK concepts

---

### 2. User Guides

**Target Audience**: Developers who need to perform specific tasks

**Files**:
- `guides/working-with-pages.md` - Complete CRUD operations for Page entities
- `guides/working-with-blocks.md` - Manipulating content blocks
- `guides/querying-databases.md` - Filtering, sorting, and paginating database queries
- `guides/search.md` - Searching across workspace with filters
- `guides/property-builders.md` - Using type-safe property builders (Title, Select, Date, etc.)
- `guides/error-handling.md` - Handling exceptions, retries, and edge cases

**Content Goals**:
- Provide practical, task-based documentation
- Show real-world usage patterns
- Cover common workflows end-to-end

---

### 3. API Reference

**Target Audience**: Developers who need detailed API information

**Structure**:

#### Client (`api-reference/client.md`)
- `NotionAPI` class
- Context manager usage
- Configuration options
- Connection lifecycle

#### Entities (`api-reference/entities/`)
- `page.md` - `Page` entity: properties, methods, examples
- `block.md` - `Block` entity: content manipulation
- `database.md` - `Database` entity: schema and queries
- `user.md` - `User` entity: user information

#### Collections (`api-reference/collections/`)
- `page-collection.md` - `PageCollection`: get, create, list, iterate
- `block-collection.md` - `BlockCollection`: get, children, append
- `database-collection.md` - `DatabaseCollection`: get, query, create_page
- `user-collection.md` - `UserCollection`: get, list, me

#### Properties (`api-reference/properties/`)
- `title.md` - `Title` property builder
- `text.md` - `Text` and `RichText` builders
- `select.md` - `Select` and `MultiSelect` builders
- `date.md` - `Date` and date range builders
- `checkbox.md` - `Checkbox` builder
- `number.md` - `Number` builder
- `url.md` - `URL`, `Email`, `Phone` builders

#### Exceptions (`api-reference/exceptions.md`)
- Exception hierarchy
- When each exception is raised
- How to handle different error types

**Content Goals**:
- Complete reference of all public APIs
- Type signatures and parameters
- Return types and raised exceptions
- Code examples for each method

---

### 4. Examples

**Target Audience**: Developers learning by example

**Files**:
- `examples/task-manager.md` - Build a task/project tracker with Notion database
- `examples/knowledge-base.md` - Create a wiki/knowledge base with pages and blocks
- `examples/automation.md` - Automate repetitive Notion workflows
- `examples/migration.md` - Migrate data from another system to Notion

**Content Goals**:
- Complete, runnable code examples
- Real-world use cases
- Best practices demonstrated

---

### 5. Advanced Topics

**Target Audience**: Experienced developers with complex requirements

**Files**:
- `advanced/pagination.md` - Manual pagination control for large datasets
- `advanced/async-patterns.md` - Async/await best practices and patterns
- `advanced/rate-limits.md` - Handling Notion API rate limiting
- `advanced/testing.md` - Testing SDK code with mocks and fixtures

**Content Goals**:
- Deep-dive into complex topics
- Performance optimization
- Production readiness

---

### 6. Reference

**Target Audience**: All users

**Files**:
- `changelog.md` - Version history and changes (mirror of CHANGELOG.md)
- `contributing.md` - How to contribute to the SDK (if applicable)

---

## File Naming Conventions

- Use lowercase with hyphens: `working-with-pages.md`
- Group related files in directories: `api-reference/entities/`
- Keep names descriptive but concise
- Match user mental model (they think "pages", not "PageEntity")

---

## Content Standards

### Code Examples

All code examples must:
- Be complete and runnable
- Follow project code style
- Include error handling where appropriate
- Show expected output or results

```python
# ✅ Good
async def get_page_title(api: NotionAPI, page_id: str) -> str:
    """Get the title of a page."""
    try:
        page = await api.pages.get(page_id)
        return page.properties["Name"]["title"][0]["plain_text"]
    except NotFoundError:
        logger.error(f"Page {page_id} not found")
        return ""

# ❌ Bad - incomplete
page = await api.pages.get(page_id)
title = page.properties["Name"]
```

### Cross-References

Use internal links to connect related topics:
- Link from guides to API reference
- Link from examples to relevant guides
- Link from error handling to exception reference

```markdown
See [API Reference - Page](api-reference/entities/page.md) for complete method list.
```

### Warnings and Notes

- Use **Warning** for potential issues or breaking changes
- Use **Note** for important information
- Use **Tip** for helpful suggestions

```markdown
> **Warning**: Always close the API client when done to avoid connection leaks.
> **Note**: The `iterate()` method is memory-efficient for large datasets.
> **Tip**: Use `async with` for automatic resource cleanup.
```

---

## Priority Order for Documentation Creation

1. **Phase 1**: Home + Quick Start + Installation + Authentication
2. **Phase 2**: Guides (Pages, Blocks, Databases, Properties)
3. **Phase 3**: API Reference (Client, Entities, Collections)
4. **Phase 4**: Examples
5. **Phase 5**: Advanced topics

---

## Maintenance

### When to Update Documentation

- **New feature**: Add guide section + API reference
- **Breaking change**: Update affected guides + add migration note to changelog
- **Bug fix**: Update affected examples if behavior changed
- **New Python version**: Update installation guide if needed

### Documentation Review Checklist

- [ ] All code examples run without errors
- [ ] All links work (internal and external)
- [ ] API reference matches actual implementation
- [ ] Type signatures are correct
- [ ] Examples follow best practices
- [ ] Changelog is up to date

---

## Tools & Technology

- **Generator**: MkDocs
- **Theme**: Material for MkDocs
- **Language**: Markdown
- **Code Highlighting**: Pygments
- **Search**: Built-in search plugin

---

## Next Steps

1. Create `mkdocs.yml` configuration file
2. Create initial file structure (empty files with titles)
3. Start with Phase 1 content (Home + Quick Start)
4. Review and iterate based on feedback
