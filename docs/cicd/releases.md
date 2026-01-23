# Release Process

Complete guide to the release process for the Better Notion SDK.

## Overview

Releases are **automated** and triggered by **git tags** following semantic versioning.

### Release Philosophy

- **Automated**: No manual building or publishing
- **Triggered by tags**: Git tags drive the entire process
- **Semantic versioning**: MAJOR.MINOR.PATCH format
- **Multiple destinations**: GitHub Releases + PyPI
- **Safe**: CI must pass before release

---

## Versioning

### Semantic Versioning

We follow **Semantic Versioning 2.0.0**: `MAJOR.MINOR.PATCH`

**Format:** `v1.2.3`

- **MAJOR** (1): Incompatible API changes
- **MINOR** (2): Backwards-compatible functionality
- **PATCH** (3): Backwards-compatible bug fixes

**Examples:**
- `v1.0.0` → Initial stable release
- `v1.1.0` → New feature (backwards-compatible)
- `v1.1.1` → Bug fix
- `v2.0.0` → Breaking changes

### Version Bumping Guidelines

#### MAJOR version (X.0.0)

**When to bump:**
- Remove or rename public APIs
- Change function signatures
- Modify behavior of existing features
- Drop support for Python versions

**Example:**
```python
# v1.0.0
api.pages.retrieve(page_id)

# v2.0.0 (BREAKING)
api.pages.get(page_id)  # Renamed method
```

#### MINOR version (0.X.0)

**When to bump:**
- Add new features
- Add new endpoints
- Add new optional parameters
- Add new functionality

**Example:**
```python
# v1.0.0
api.pages.retrieve(page_id)

# v1.1.0 (NEW FEATURE)
api.pages.retrieve(page_id, expand=False)  # New optional param
```

#### PATCH version (0.0.X)

**When to bump:**
- Bug fixes
- Internal refactoring
- Documentation updates
- Performance improvements
- Dependency updates

**Example:**
```python
# v1.0.0
def retrieve(page_id: str) -> dict:
    # Had bug with empty page_id
    ...

# v1.0.1 (BUG FIX)
def retrieve(page_id: str) -> dict:
    if not page_id:
        raise ValueError("page_id cannot be empty")  # Fixed
    ...
```

### Pre-Releases

**Format:** `v1.2.3-alpha.1`, `v1.2.3-beta.1`, `v1.2.3-rc.1`

**When to use:**
- `alpha`: Early development, incomplete features
- `beta`: Feature complete, testing needed
- `rc`: Release candidate, ready for production

**Example:**
```
v1.0.0-alpha.1  → First alpha
v1.0.0-alpha.2  → Second alpha
v1.0.0-beta.1   → First beta
v1.0.0-rc.1     → First release candidate
v1.0.0          → Stable release
```

---

## Release Workflow

### Automated Process

**Trigger:** Push git tag matching `v*`

```bash
git tag v1.0.0
git push origin v1.0.0
```

**Workflow:** `.github/workflows/release.yml`

**Steps:**

1. **CI Check** (implicit)
   - Full CI pipeline runs on the tag
   - All checks must pass
   - If CI fails, release workflow doesn't run

2. **Build Packages**
   - Build source distribution (`.tar.gz`)
   - Build wheel distribution (`.whl`)
   - Upload as artifacts

3. **Create GitHub Release**
   - Create release from tag
   - Attach artifacts (sdist, wheel)
   - Generate release notes

4. **Publish to PyPI**
   - Publish using trusted publishing
   - Package available immediately
   - Downloadable via `pip install better-notion`

### Release Workflow Diagram

```
Git Tag Pushed (v1.0.0)
    ↓
┌──────────────────────┐
│   CI Pipeline        │  → Must pass first
└──────────────────────┘
    ↓ (CI passes)
┌──────────────────────┐
│ Build Distributions  │  → sdist + wheel
└──────────────────────┘
    ↓
┌──────────────────────┐
│ Create GitHub Release│  → Upload artifacts
└──────────────────────┘
    ↓
┌──────────────────────┐
│ Publish to PyPI      │  → Live on PyPI
└──────────────────────┘
    ↓
Release Complete ✅
```

---

## Pre-Release Checklist

Before creating a release tag, ensure:

### Code Quality

- [ ] All tests pass locally (`uv run pytest`)
- [ ] Coverage threshold met (≥80%)
- [ ] No linting errors (`uv run ruff check`)
- [ ] Code formatted (`uv run ruff format`)

### Documentation

- [ ] README.md is up to date
- [ ] CHANGELOG.md updated with version
- [ ] API documentation is current
- [ ] Migration guide (if breaking changes)

### Version

- [ ] Version bumped in `pyproject.toml`
- [ ] Version consistent everywhere
- [ ] Git history is clean

### Testing

- [ ] Tested on Python 3.10, 3.11, 3.12
- [ ] Manual testing of new features
- [ ] Integration tests pass

---

## Release Steps

### 1. Update Version

**File:** `pyproject.toml`

```toml
[project]
name = "better-notion"
version = "1.0.0"  # Bump this
```

### 2. Update Changelog

**File:** `CHANGELOG.md`

```markdown
## [1.0.0] - 2025-01-15

### Added
- Initial stable release
- Pages, databases, blocks endpoints
- OAuth support
- Rate limiting

### Fixed
- Bug with pagination

### Changed
- Improved error messages
```

### 3. Commit Changes

```bash
git add pyproject.toml CHANGELOG.md
git commit -m "chore: prepare for v1.0.0 release"
git push origin main
```

### 4. Wait for CI

- Ensure CI passes on the commit
- Don't proceed if CI fails

### 5. Create Tag

```bash
git tag v1.0.0
git push origin v1.0.0
```

### 6. Monitor Release

- Watch GitHub Actions: https://github.com/YOUR_ORG/napi/actions
- Verify release workflow completes
- Check GitHub Releases page
- Verify PyPI publication

---

## Post-Release

### Verify Release

1. **Check GitHub Release**
   - Visit: https://github.com/YOUR_ORG/napi/releases
   - Verify release notes
   - Download artifacts

2. **Check PyPI**
   - Visit: https://pypi.org/project/better-notion/
   - Verify version displayed
   - Check metadata

3. **Test Installation**

```bash
# Create clean venv
python -m venv test_env
source test_env/bin/activate  # Windows: test_env\Scripts\activate

# Install from PyPI
pip install better-notion

# Test import
python -c "from better_notion import NotionAPI; print('Success!')"

# Cleanup
deactivate
rm -rf test_env
```

### Announce Release

**Places to announce:**
- GitHub release (already created)
- Project README (update badges)
- Twitter/Mastodon (if applicable)
- Project documentation
- Release notes email

---

## Rollback Procedure

If a critical issue is found after release:

### 1. Yank from PyPI (Optional)

```bash
# Using twine
pip install twine
twine yank better-notion==1.0.0
```

**Note:** Yanked versions remain installable but warn users.

### 2. Create Fix Release

```bash
# Patch version bump
version = "1.0.1"

# Commit fix
git add .
git commit -m "fix: critical bug in v1.0.0"

# Tag patch release
git tag v1.0.1
git push origin v1.0.1
```

### 3. Deprecate Old Release

- Add deprecation notice to GitHub release
- Update documentation to recommend new version

---

## Release Frequency

### Guidelines

**Patch releases (X.X.X):**
- As needed for bug fixes
- Can be frequent (weekly/daily)

**Minor releases (X.X.0):**
- New features ready
- Monthly or quarterly

**Major releases (X.0.0):**
- Breaking changes accumulated
- Announce well in advance
- Provide migration guide

### Branch Strategy

**Current strategy:**
- Single branch (`main`)
- Tags for releases
- No long-lived release branches

**Future consideration:**
- If major releases need maintenance, create release branches:
  - `v1.x` branch for v1.x releases
  - `main` for v2.x development

---

## Troubleshooting

### Release Workflow Fails

**Problem:** Release workflow doesn't trigger

**Causes:**
- Tag doesn't match `v*` pattern
- CI hasn't finished yet
- Tag not pushed to remote

**Solutions:**
```bash
# Check tag format
git tag -l

# Push tag correctly
git push origin v1.0.0

# Wait for CI to complete first
```

### PyPI Publish Fails

**Problem:** Publishing to PyPI fails

**Causes:**
- Version already exists on PyPI
- Invalid package name
- Missing metadata
- Auth token not configured

**Solutions:**
```bash
# Check if version exists
pip index versions better-notion

# Verify package name
grep "^name = " pyproject.toml

# Check trusted publishing configured on PyPI
# Visit: https://pypi.org/manage/account/publishing/
```

### Build Fails

**Problem:** Building distribution fails

**Causes:**
- Missing dependencies
- Invalid `pyproject.toml`
- Build script errors

**Solutions:**
```bash
# Test build locally
uv build

# Check build output
ls -la dist/

# Install locally to test
pip install dist/better_notion-1.0.0-py3-none-any.whl
```

---

## Related Documentation

- [CI Workflows](./ci-workflows.md) - Release workflow specification
- [Overview](./overview.md) - CI/CD strategy
- [Security](./security.md) - Secrets and tokens
- [Testing](./testing.md) - Release testing requirements

---

## Summary

**Release Process:**

1. Bump version in `pyproject.toml`
2. Update `CHANGELOG.md`
3. Commit and push to `main`
4. Wait for CI to pass
5. Create git tag: `git tag v1.0.0`
6. Push tag: `git push origin v1.0.0`
7. CI runs, then release workflow triggers
8. GitHub release created automatically
9. Published to PyPI automatically

**Key Points:**

- Tags must match `v*` pattern
- CI must pass before release
- Semantic versioning required
- Fully automated after tag push
- Rollback via patch releases
