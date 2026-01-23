# Git Workflow

Complete guide to Git branching, commits, and pull requests for the Better Notion SDK.

## Overview

This document defines our Git workflow to ensure:
- Clean history
- Easy code review
- Minimal merge conflicts
- Clear traceability of changes

---

## Branch Strategy

### Main Branches

```
main        ← Production-ready code only
```

**Rules:**
- `main` is always deployable
- All code lands via PR
- Protected branch (requires reviews and passing CI)
- No direct commits

### Feature Branches

```
feature/xxx ← New features
fix/xxx     ← Bug fixes
docs/xxx    ← Documentation changes
refactor/xxx← Refactoring
```

**Rules:**
- Branch from `main`
- Merge back to `main` via PR
- Delete after merge
- Short-lived (days, not weeks)

### Branch Naming

**Pattern:** `<type>/<short-description>`

**Types:**
- `feature/` - New functionality
- `fix/` - Bug fixes
- `docs/` - Documentation only
- `refactor/` - Refactoring (no behavior change)
- `test/` - Adding/updating tests
- `chore/` - Maintenance, dependencies

**Examples:**
```bash
feature/add-pages-endpoint
feature/oauth-support
fix/rate-limit-retry
docs/update-readme
refactor/extract-retry-logic
test/add-pagination-tests
chore/upgrade-deps
```

---

## Commit Messages

### Conventional Commits

We use **Conventional Commits** format:

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

### Types

| Type | When to Use | Example |
|------|-------------|---------|
| `feat` | New feature | `feat(pages): add retrieve endpoint` |
| `fix` | Bug fix | `fix(auth): handle expired tokens` |
| `docs` | Documentation | `docs: add project structure guide` |
| `style` | Style/formatting | `style: format with ruff` |
| `refactor` | Refactoring | `refactor(http): extract retry logic` |
| `test` | Tests | `test: add pagination tests` |
| `chore` | Maintenance | `chore: upgrade httpx to 0.26.0` |

### Scope

**Optional.** Use parentheses after type.

**Common scopes:**
- `pages`, `databases`, `blocks` - For endpoint-specific changes
- `auth`, `http`, `cache` - For component-specific changes
- `ci`, `docs`, `test` - For meta changes

### Description

**Imperative mood, lowercase, no period.**

```bash
# GOOD
feat(pages): add retrieve endpoint
fix(auth): handle expired tokens
docs: update readme

# AVOID
feat(pages): Added retrieve endpoint  # Don't use past tense
fix(auth): Handles expired tokens     # Don't use third person
feat(pages): Add retrieve endpoint.   # No period
```

### Body

**Optional.** Explain WHAT and WHY.

```bash
feat(pages): add retrieve endpoint

Add retrieve() method to PagesEndpoint for fetching
individual pages by ID.

Closes #123
```

### Footer

**Optional.** References to issues, breaking changes.

```bash
feat(pages): add retrieve endpoint

Closes #123

BREAKING CHANGE: The page ID validation now requires
a valid UUID format.
```

### Examples

**Feature:**
```bash
git commit -m "feat(pages): add retrieve endpoint"
```

**With scope and body:**
```bash
git commit -m "feat(pages): add retrieve endpoint

Add retrieve() method to PagesEndpoint for fetching
single pages by ID. Supports optional expand parameter
for including child objects.

Closes #42"
```

**Bug fix:**
```bash
git commit -m "fix(auth): handle expired OAuth tokens

Implement automatic token refresh when expired
tokens are detected during API requests.

Fixes #87"
```

**Documentation:**
```bash
git commit -m "docs: add project structure documentation"
```

**Refactoring:**
```bash
git commit -m "refactor(http): extract retry logic to separate class

Move retry logic from HTTPClient to RetryHandler
for better separation of concerns and testability."
```

**Multiple commits in a PR:**
```bash
# Commit 1
git commit -m "feat(pages): add retrieve method skeleton"

# Commit 2
git commit -m "feat(pages): implement retrieve logic"

# Commit 3
git commit -m "test(pages): add tests for retrieve endpoint"
```

---

## Pull Request Process

### Creating a PR

**1. Update main**
```bash
git checkout main
git pull origin main
```

**2. Create feature branch**
```bash
git checkout -b feature/add-pages-endpoint
```

**3. Make changes**
```bash
# Write code
git add .
git commit -m "feat(pages): add retrieve endpoint"
```

**4. Push to remote**
```bash
git push origin feature/add-pages-endpoint
```

**5. Create PR**
```bash
# Using GitHub CLI
gh pr create \
  --title "feat: Add pages retrieve endpoint" \
  --body "Description of changes"

# Or create via GitHub web interface
```

### PR Title

**Use conventional commit format:**

```bash
# GOOD
feat: Add pages retrieve endpoint
fix: Handle rate limiting errors
docs: Update installation guide

# AVOID
Add pages endpoint  # Missing type
Fixes rate limiting  # Not imperative
adds pages endpoint  # Wrong case
```

### PR Description

**Template:**

```markdown
## Summary
Brief description of what this PR does and why.

## Changes
- Added `retrieve()` method to PagesEndpoint
- Implemented error handling for 404 responses
- Added unit tests for new functionality

## Testing
- Added unit tests in `tests/unit/test_pages.py`
- All tests pass locally
- Manually tested with real Notion API

## Checklist
- [ ] Code follows project standards
- [ ] Tests added/updated
- [ ] Docstrings added
- [ ] No breaking changes (or documented if yes)
- [ ] Linked to relevant issue

## Related
Closes #123
Related to #45
```

### PR Review Checklist

**For Author:**
- [ ] Title follows conventional commits
- [ ] Description explains WHAT and WHY
- [ ] Linked to issue (if applicable)
- [ ] Tests pass locally (`uv run pytest`)
- [ ] Code formatted (`uv run ruff format`)
- [ ] No linting errors (`uv run ruff check`)
- [ ] No merge conflicts with main
- [ ] Documentation updated (if needed)

**For Reviewer:**
- [ ] Code follows project standards
- [ ] Logic is correct
- [ ] Tests added/updated
- [ ] Docstrings present
- [ ] No secrets/credentials
- [ ] No commented-out code
- [ ] Performance acceptable
- [ ] No breaking changes (or documented)

### Review Process

**1. Request review**
```bash
# Using GitHub CLI
gh pr edit --add-reviewer @username

# Or via GitHub UI
```

**2. Reviewer reviews**
- Check code quality
- Verify tests
- Suggest improvements
- Approve or request changes

**3. Address feedback**
- Make requested changes
- Push updates to branch
- Request re-review if needed

**4. Approve and merge**
- After approval
- Ensure CI passes
- Merge using approved method

### Merge Methods

**Recommended: Squash merge**

```bash
# Squash all commits into one
# Keeps main history clean
# PR title becomes commit message
```

**Alternative: Rebase and merge**

```bash
# Replaces branch commits onto main
# Linear history
# Original commit messages preserved
```

**Avoid: Merge commit**

```bash
# Creates merge commit
- Clutters history
- Use only if necessary
```

### After Merge

**1. Delete branch**
```bash
# Local
git branch -d feature/add-pages-endpoint

# Remote (usually automatic)
git push origin --delete feature/add-pages-endpoint
```

**2. Update local main**
```bash
git checkout main
git pull origin main
```

**3. Close related issues**
- Link PR to issue with "Closes #123"
- Or close manually via GitHub UI

---

## Daily Workflow

### Morning Routine

```bash
# Start on main
git checkout main
git pull origin main

# Check what's new
git log --oneline -10
```

### Working on a Feature

```bash
# Create feature branch
git checkout -b feature/my-feature

# Make changes
# ... write code ...

# Stage changes
git add .

# Commit with conventional message
git commit -m "feat: add my feature"

# Push to remote
git push origin feature/my-feature

# Create PR
gh pr create
```

### During Development

```bash
# Check status
git status

# See commits
git log --oneline

# See changes
git diff

# Stage specific files
git add better_notion/pages.py
git commit -m "feat(pages): add retrieve method"
```

### Syncing with Main

**If main has changed while you're working:**

```bash
# Update main
git checkout main
git pull origin main

# Rebase your feature branch
git checkout feature/my-feature
git rebase main/main

# If conflicts occur
# Resolve them
git add .
git rebase --continue

# Force push (rebase rewrote history)
git push origin feature/my-feature --force-with-lease
```

### Before Creating PR

```bash
# Ensure branch is up to date
git fetch origin main
git rebase origin/main

# Run tests
uv run pytest

# Format and lint
uv run ruff format better_notion
uv run ruff check better_notion

# Push
git push origin feature/my-feature
```

---

## Common Scenarios

### Undo Last Commit

```bash
# Keep changes
git reset --soft HEAD~1

# Discard changes
git reset --hard HEAD~1
```

### Change Commit Message

```bash
# Most recent commit
git commit --amend -m "new message"

# Already pushed
git commit --amend -m "new message"
git push origin branch-name --force-with-lease
```

### Fix Mistake in Previous Commit

```bash
# Make new commit that fixes it
git commit -m "fix: correct logic"

# Squash the two commits
git rebase -i HEAD~2
# Change "pick" to "squash" for second commit
```

### Resolve Merge Conflicts

```bash
# During rebase/merge
git status

# Edit conflicting files
# Remove conflict markers

# Mark as resolved
git add <file>

# Continue
git rebase --continue  # Or git merge for merges

# Or abort
git rebase --abort
```

### Recover Lost Commit

```bash
# Find lost commit
git reflog

# Checkout
git checkout <sha>

# Create branch from it
git checkout -b recovery-branch
```

---

## Branch Protection

**Recommended settings for `main` branch:**

### Via GitHub UI

**Settings → Branches → Add rule:**

**Branch name pattern:** `main`

**Checkboxes:**
- ✅ Require status checks to pass before merging
- ✅ Require branches to be up to date before merging
- ✅ Require pull request reviews before merging
  - Approvals: 1
- ✅ Do not allow bypassing the above settings

**Required status checks:**
- lint
- test (Python 3.10)
- test (Python 3.11)
- test (Python 3.12)

### Via GitHub CLI

```bash
gh api repos/:owner/:repo/branches/main/protection \
  --method PUT \
  -f required_status_checks='{"strict":true,"checks":[{"context":"lint"},{"context":"test"}]}' \
  -f enforce_admins=true \
  -f required_pull_request_reviews='{"required_approving_review_count":1}' \
  -f restrictions=null
```

---

## Git Configuration

### User Info

```bash
git config --global user.name "Your Name"
git config --global user.email "you@example.com"
```

### Default Branch Name

```bash
git config --global init.defaultBranch main
```

### Rebase vs Merge

```bash
# Prefer rebase for pulling
git config --global pull.rebase true
```

### Aliases (Optional)

```bash
# Useful aliases
git config --global alias.co checkout
git config --global alias.br branch
git config --global alias.ci commit
git config --global alias.st status
git config --global alias.lg "log --oneline --graph --all"
```

---

## Related Documentation

- [standards.md](./standards.md) - Code conventions
- [workflow.md](./workflow.md) - Development workflow
- [setup.md](./setup.md) - Git setup

---

## Summary

**Key Points:**

1. **Branch strategy:** Simple - `main` + feature branches
2. **Branch naming:** `<type>/<description>` (feature/xxx, fix/xxx)
3. **Commit messages:** Conventional commits format
4. **PRs:** Required for all changes
5. **Code review:** At least one approval required
6. **Merge method:** Squash merge recommended
7. **Protected branches:** main requires reviews + passing CI

**Golden Rules:**

- Never commit directly to main
- Always write meaningful commit messages
- Keep branches short-lived
- Request reviews early
- Ensure CI passes before requesting review
- Delete branches after merge

---

**Last Updated:** 2025-01-23
