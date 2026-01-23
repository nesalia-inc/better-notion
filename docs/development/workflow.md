# Development Workflow

Complete guide to the day-to-day development process for the Better Notion SDK.

## Overview

This document explains the complete development cycle, from planning to implementation to review. It's your guide for "how do I actually work on this project?"

---

## Development Cycle

The typical workflow for a feature:

```
1. Plan → 2. Branch → 3. Implement → 4. Test → 5. Commit → 6. PR → 7. Review → 8. Merge
```

---

## 1. Planning

### Before You Code

**Find an issue to work on:**
- Browse GitHub issues: https://github.com/nesalia/better-notion/issues
- Check "good first issue" label
- Ask the team for suggestions

**Understand the requirements:**
- Read the issue description
- Check related design docs in `/docs/sdk/`
- Understand the API endpoint (check `/docs/api/`)
- Clarify anything unclear

**Example:**
```
Issue: Add pages retrieve endpoint
Design: docs/sdk/features/pages.md
API: docs/api/pages.md
```

---

## 2. Create Branch

**Start from main:**
```bash
git checkout main
git pull origin main
```

**Create feature branch:**
```bash
# Format: <type>/<description>
git checkout -b feature/add-pages-retrieve
```

**Branch types:**
- `feature/` - New functionality
- `fix/` - Bug fixes
- `docs/` - Documentation
- `refactor/` - Refactoring
- `test/` - Tests

---

## 3. Implementation

### File Organization

**Know where to put code:**
- Low-level API → `better_notion/_lowlevel/`
- High-level API → `better_notion/_highlevel/`
- Utilities → `better_notion/utils/`
- Tests → `tests/unit/` or `tests/integration/`

See [project-structure.md](./project-structure.md) for details.

### Write Code

**Follow the standards:**
- Use type hints
- Write docstrings
- Follow naming conventions
- Handle errors properly

See [standards.md](./standards.md) for details.

**Example implementation:**

```python
# better_notion/_lowlevel/endpoints/pages.py
from typing import Any

class PagesEndpoint(EndpointBase):
    """Pages API endpoint."""

    async def retrieve(self, page_id: str) -> dict[str, Any]:
        """Retrieve a page by ID.

        Args:
            page_id: The unique identifier of the page.

        Returns:
            The page data as a dictionary.

        Raises:
            NotFoundError: If the page doesn't exist.
            HTTPError: For other HTTP errors.
        """
        if not page_id:
            raise ValueError("page_id cannot be empty")

        return await self._api._request(
            "GET",
            f"/pages/{page_id}"
        )
```

---

## 4. Testing

### Write Tests First (TDD)

**Create test file:**
```python
# tests/unit/test_pages.py
import pytest
from unittest.mock import AsyncMock, patch

class TestPagesEndpoint:
    """Test suite for Pages endpoint."""

    @pytest.mark.asyncio
    async def test_retrieve_page_success(self, mock_api):
        """Test retrieving a page successfully."""
        # Arrange
        page_id = "test_page_id"
        mock_response = {
            "id": page_id,
            "object": "page",
            "created_time": "2025-01-01T00:00:00.000Z"
        }

        # Act
        with patch.object(mock_api._http, "request", return_value=mock_response):
            result = await mock_api.pages.retrieve(page_id)

        # Assert
        assert result["id"] == page_id
        assert result["object"] == "page"
```

### Run Tests

**Run all tests:**
```bash
uv run pytest
```

**Run specific test file:**
```bash
uv run pytest tests/unit/test_pages.py
```

**Run with coverage:**
```bash
uv run pytest --cov=better_notion --cov-report=html
```

**Run verbose:**
```bash
uv run pytest -vv
```

### Test Checklist

- [ ] Unit tests added for new code
- [ ] Integration tests if applicable
- [ ] Edge cases covered
- [ ] Error cases tested
- [ ] All tests pass

See [testing-strategy.md](./testing-strategy.md) for details.

---

## 5. Code Quality

### Format Code

**Format with ruff:**
```bash
uv run ruff format better_notion
```

**Check formatting:**
```bash
uv run ruff format --check better_notion
```

### Lint Code

**Run linter:**
```bash
uv run ruff check better_notion
```

**Auto-fix issues:**
```bash
uv run ruff check --fix better_notion
```

### Type Check

**Run mypy:**
```bash
uv run mypy better_notion
```

### Quality Checklist

- [ ] Code formatted (`uv run ruff format`)
- [ ] No linting errors (`uv run ruff check`)
- [ ] Type hints present
- [ ] Docstrings present
- [ ] No commented-out code
- [ ] No debug prints
- [ ] No secrets/credentials

---

## 6. Commit Changes

### Stage Files

**Stage all changes:**
```bash
git add .
```

**Stage specific files:**
```bash
git add better_notion/_lowlevel/endpoints/pages.py
git add tests/unit/test_pages.py
```

### Commit with Conventional Message

**Format:**
```
<type>[optional scope]: <description>

[optional body]
```

**Examples:**
```bash
# Simple feature
git commit -m "feat(pages): add retrieve endpoint"

# With body
git commit -m "feat(pages): add retrieve endpoint

Add retrieve() method to PagesEndpoint for fetching
individual pages by ID. Supports error handling for
404 responses.

Closes #42"

# Bug fix
git commit -m "fix(pages): handle empty page_id

Raise ValueError when page_id is empty instead of
passing it to the API.

Fixes #87"
```

### Multiple Commits

**Break work into logical commits:**
```bash
# Commit 1: Add method skeleton
git commit -m "feat(pages): add retrieve method signature"

# Commit 2: Implement logic
git commit -m "feat(pages): implement retrieve logic"

# Commit 3: Add tests
git commit -m "test(pages): add tests for retrieve endpoint"

# Commit 4: Add docstrings
git commit -m "docs(pages): add docstrings to retrieve method"
```

See [git-workflow.md](./git-workflow.md) for details.

---

## 7. Push and Create PR

### Push to Remote

**Push branch:**
```bash
git push origin feature/add-pages-retrieve
```

**Force push if needed (after rebase):**
```bash
git push origin feature/add-pages-retrieve --force-with-lease
```

### Create Pull Request

**Using GitHub CLI:**
```bash
# Simple
gh pr create

# With title and body
gh pr create \
  --title "feat: Add pages retrieve endpoint" \
  --body "Description of changes"
```

**Using GitHub web:**
1. Go to https://github.com/nesalia/better-notion
2. Click "Pull requests"
3. Click "New pull request"
4. Select your branch
5. Fill in the PR template

### PR Description Template

```markdown
## Summary
Brief description of what this PR does.

## Changes
- Added `retrieve()` method to PagesEndpoint
- Implemented error handling for 404 responses
- Added unit tests for new functionality
- Added docstrings following Google style

## Type of Change
- [ ] Bug fix
- [x] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [x] Unit tests added
- [ ] Integration tests added
- [x] All tests pass locally
- [ ] Manually tested

## Checklist
- [x] Code follows project standards
- [x] Tests added/updated
- [x] Docstrings added
- [x] No breaking changes (or documented if yes)
- [x] Linked to relevant issue

## Related
Closes #42
Related to #15
```

---

## 8. Code Review

### Request Review

**Add reviewers:**
```bash
gh pr edit --add-reviewer @username
```

**Or via GitHub UI:**
- Click "Reviewers"
- Select reviewers

### During Review

**Respond to feedback:**
- Make requested changes
- Push updates to branch
- Ask questions if unclear
- Explain your reasoning

**Update commit history:**
```bash
# Make changes
git add .
git commit -m "fix: address review feedback"

# Push
git push origin feature/add-pages-retrieve
```

### Reviewer Responsibilities

**Check:**
- [ ] Code follows standards
- [ ] Logic is correct
- [ ] Tests are adequate
- [ ] Docstrings present
- [ ] No security issues
- [ ] No breaking changes (or documented)

**Provide constructive feedback:**
- Explain what needs to change
- Suggest improvements
- Ask questions
- Be respectful

---

## 9. Merge

### Before Merging

**Ensure:**
- [ ] All approvals received
- [ ] All CI checks pass
- [ ] No merge conflicts
- [ ] Tests pass
- [ ] Documentation updated

### Merge Methods

**Squash merge (recommended):**
- Squashes all commits into one
- Clean history
- PR title becomes commit message

**Rebase and merge:**
- Linear history
- Preserves individual commits

### Merge

**Using GitHub CLI:**
```bash
gh pr merge --squash
```

**Using GitHub UI:**
- Click "Merge pull request"
- Select merge method
- Click "Confirm merge"

---

## 10. After Merge

### Delete Branch

**Local:**
```bash
git checkout main
git branch -d feature/add-pages-retrieve
```

**Remote (usually automatic):**
```bash
git push origin --delete feature/add-pages-retrieve
```

### Update Main

```bash
git checkout main
git pull origin main
```

### Close Related Issues

- If PR was linked with "Closes #42", issue closes automatically
- Otherwise, close manually via GitHub UI

---

## Daily Workflow Example

### Morning: Start Fresh

```bash
# Update main
git checkout main
git pull origin main

# Check what's new
git log --oneline -10

# See what needs doing
gh issue list
```

### During Day: Work on Feature

```bash
# Create feature branch
git checkout -b feature/my-feature

# Write code
# ... work work work ...

# Test
uv run pytest

# Format and lint
uv run ruff format better_notion
uv run ruff check better_notion

# Commit
git add .
git commit -m "feat: add my feature"

# Push
git push origin feature/my-feature

# Create PR
gh pr create
```

### End of Day: Wrap Up

```bash
# Check PR status
gh pr status

# See what's merged
git log --oneline --since="9am"
```

---

## Troubleshooting Workflow

### Tests Failing in CI

**Problem:** Tests pass locally but fail in CI.

**Solutions:**
```bash
# Check Python version
python --version  # Should be 3.10+

# Update dependencies
uv sync

# Clear cache
uv run pytest --cache-clear

# Run tests as CI does
uv run pytest -v --tb=short
```

### Merge Conflicts

**Problem:** Can't merge due to conflicts.

**Solutions:**
```bash
# Update main
git checkout main
git pull origin main

# Rebase your branch
git checkout feature/my-feature
git rebase main/main

# Resolve conflicts
# Edit files
git add .
git rebase --continue

# Force push
git push origin feature/my-feature --force-with-lease
```

### PR Checks Failing

**Problem:** CI checks failing on PR.

**Solutions:**
1. Check the logs
2. Fix the issue
3. Commit and push
4. Checks will re-run automatically

---

## Best Practices

### Do's

- ✅ Write tests as you write code
- ✅ Commit frequently with meaningful messages
- ✅ Keep branches focused and short-lived
- ✅ Request reviews early
- ✅ Respond to feedback promptly
- ✅ Keep PRs small and focused
- ✅ Update documentation
- ✅ Follow coding standards

### Don'ts

- ❌ Commit directly to main
- ❌ Work on huge PRs (break them up)
- ❌ Ignore CI failures
- ❌ Skip tests
- ❌ Leave PRs hanging for days
- ❌ Ignore review feedback
- ❌ Commit secrets or credentials

---

## Quick Reference

### Essential Commands

```bash
# Branching
git checkout -b feature/my-feature
git checkout main
git pull origin main

# Working
git add .
git commit -m "feat: add feature"
git push origin feature/my-feature

# Testing
uv run pytest
uv run pytest --cov=better_notion

# Quality
uv run ruff format better_notion
uv run ruff check better_notion

# PRs
gh pr create
gh pr status
gh pr merge --squash
```

### Workflow Checklist

**Before coding:**
- [ ] Issue understood
- [ ] Design reviewed
- [ ] Branch created

**During coding:**
- [ ] Tests written
- [ ] Code formatted
- [ ] No linting errors
- [ ] Docstrings added

**Before PR:**
- [ ] All tests pass
- [ ] Code reviewed by self
- [ ] Documentation updated

**After PR:**
- [ ] Review requested
- [ ] Feedback addressed
- [ ] CI checks passing
- [ ] Ready to merge

---

## Related Documentation

- [setup.md](./setup.md) - Environment setup
- [standards.md](./standards.md) - Code conventions
- [git-workflow.md](./git-workflow.md) - Git workflow
- [testing-strategy.md](./testing-strategy.md) - Testing guide

---

## Summary

**The Development Cycle:**

1. **Plan** - Understand what to build
2. **Branch** - Create feature branch from main
3. **Implement** - Write code following standards
4. **Test** - Write and run tests
5. **Commit** - Commit with conventional messages
6. **PR** - Create pull request
7. **Review** - Address feedback
8. **Merge** - Merge after approval
9. **Clean up** - Delete branch, update main

**Remember:**
- Small, focused PRs
- Test as you go
- Commit frequently
- Request reviews early
- Be responsive to feedback

---

**Last Updated:** 2025-01-23
