# CI/CD Overview

This document provides an overview of the Continuous Integration and Continuous Deployment strategy for the Better Notion SDK project.

## Philosophy

Our CI/CD strategy follows these core principles:

1. **Fast Feedback** - Get results to developers quickly
2. **Quality Gates** - Enforce code quality standards
3. **Automation** - Automate repetitive tasks (releases, publishing)
4. **Safety** - Prevent broken code from being merged
5. **Transparency** - Make CI/CD status visible and understandable

## Platform Choice

### GitHub Actions

We use **GitHub Actions** for our CI/CD pipeline.

**Rationale:**

- **Native Integration**: Repository is hosted on GitHub
- **Free & Generous**: Free for public repositories
- **Python Support**: Excellent Python ecosystem
- **Marketplace**: Rich library of community actions
- **Community**: Large user base and documentation

**Alternatives Considered:**
- GitLab CI: Not applicable (not using GitLab)
- CircleCI: Good option, but GitHub Actions is sufficient
- Travis CI: Deprecated/no longer free

## CI Pipeline Overview

### What Triggers CI

```
Events:
├─ Push to main branch
├─ Pull Request (any branch)
└─ Manual workflow dispatch (optional)
```

### CI Pipeline Flow

```
Code Change
    ↓
┌─────────────┐
│   Lint Job  │  → Runs ruff check, ruff format check
└─────────────┘
    ↓ (if passes)
┌─────────────┐
│  Test Job   │  → Runs pytest with coverage
│              │  → Tests on Python 3.10, 3.11, 3.12
└─────────────┘
    ↓ (if passes)
┌─────────────┐
│ Build Job   │  → (Optional) Build wheel package
└─────────────┘
    ↓
All Pass → CI Green ✅
Any Fail → CI Red ❌
```

### CD Pipeline Flow

```
Git Tag Pushed (v1.0.0)
    ↓
┌──────────────┐
│   Run CI     │  → Full CI pipeline must pass
└──────────────┘
    ↓ (CI passes)
┌──────────────────┐
│ Build Packages  │  → Build sdist and wheel
└──────────────────┘
    ↓
┌──────────────────┐
│ GitHub Release  │  → Create GitHub release
│                 │  → Upload artifacts
└──────────────────┘
    ↓
┌──────────────────┐
│ PyPI Publish   │  → Publish to PyPI
└──────────────────┘
    ↓
Release Complete 🎉
```

## Key Features

### 1. Fast Feedback

**Approach:**
- Parallel job execution (lint + tests run simultaneously)
- Caching (uv cache, pip cache)
- Lightweight Docker images (ubuntu-latest only)
- Fail-fast on lint (cheap check, quick feedback)

**Benefits:**
- Developers get feedback in <5 minutes
- Don't waste resources on failing code
- Faster iteration cycle

### 2. Quality Gates

**Requirements:**
- All lint checks must pass
- All tests must pass
- Minimum coverage threshold (80%)
- All Python versions must pass tests

**Enforcement:**
- Branch protection rules on `main` branch
- Required status checks before merge
- No bypass possible

### 3. Automation

**Automated Tasks:**
- Code linting and formatting checks
- Running full test suite
- Building distribution packages
- Creating GitHub releases
- Publishing to PyPI

**Manual Tasks:**
- Version bumping (manual decision)
- Changelog updates (manual decision)
- Git tagging (manual trigger)

### 4. Safety

**Safety Measures:**
- Required PR reviews (branch protection)
- All checks must pass before merge
- Tests on multiple Python versions
- Coverage threshold enforcement
- Semantic versioning required for releases

### 5. Transparency

**Visibility:**
- CI status visible on PRs (green/red checks)
- Coverage reports as PR comments
- Test results in workflow logs
- Release notes in GitHub Releases

**Communication:**
- Clear commit messages in workflows
- Descriptive job names
- Helpful error messages

## Workflow Files

### Primary Workflows

| Workflow | File | Purpose | Trigger |
|----------|------|---------|---------|
| **Main CI** | `.github/workflows/ci.yml` | Full CI pipeline | Push, PR |
| **Lint** | `.github/workflows/lint.yml` | Fast lint checks | PR, Push |
| **Test** | `.github/workflows/test.yml` | Run tests only | Manual, Push |
| **Release** | `.github/workflows/release.yml` | Automated releases | Git tags |

## Job Strategies

### Parallel Execution

```yaml
jobs:
  lint:
    # Runs independently
  test:
    # Runs independently (parallel with lint)

# Benefit: Faster overall pipeline
```

### Matrix Testing

```yaml
strategy:
  matrix:
    python-version: ["3.10", "3.11", "3.12"]

# Benefit: Test compatibility
```

### Dependency Management

```yaml
jobs:
  test:
    needs: lint
    # Only run if lint passes
```

## Success Criteria

### CI Success

All of the following must pass:

1. ✓ Code style checks (ruff)
2. ✓ Code formatting checks (ruff format)
3. ✓ Unit tests pass (all Python versions)
4. ✓ Coverage threshold met (≥80%)
5. ✓ Package builds successfully

### Release Success

All of the following must succeed:

1. ✓ All CI checks pass
2. ✓ Distribution packages build correctly
3. ├── ✓ sdist builds
4. └── ✓ wheel builds
5. ✓ GitHub release created
6. ✓ Published to PyPI successfully

## Repository Settings

### Branch Protection

**Protected Branch:** `main`

**Rules:**
- Require status checks to pass before merging
- Require branches to be up to date before merging
- Optional: Require pull request reviews

### Required Checks

```
lint
test (Python 3.10)
test (Python 3.11)
test (Python 3.12)
coverage
```

## Performance

### CI Speed Goals

| Metric | Target |
|--------|--------|
| Lint job | < 30 seconds |
| Single test job | < 2 minutes |
| Full CI pipeline | < 5 minutes |

### Optimization Techniques

- **Caching**: uv cache, pip cache
- **Parallel jobs**: Run independent jobs simultaneously
- **Minimal dependencies**: Only test what's needed
- **Fast tests**: Unit tests should be fast (<100ms each)

## Monitoring

### Metrics to Track

**CI Metrics:**
- Workflow run duration
- Job success/failure rate
- Average test duration
- Coverage percentage trend

**Release Metrics:**
- Release frequency
- Time from tag to PyPI publication
- Download statistics (from PyPI)

## Related Documentation

- [CI Workflows](./ci-workflows.md) - Detailed workflow specifications
- [Testing Strategy](./testing.md) - Test configuration
- [Release Process](./releases.md) - Release automation
- [Secrets & Security](./security.md) - Security considerations

## Next Steps

1. Set up GitHub repository settings
2. Configure branch protection rules
3. Add required secrets (PYPI_API_TOKEN)
4. Create workflow files
5. Set up Codecov integration
6. Add badges to README
7. Test CI/CD with test PR
