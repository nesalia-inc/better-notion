# CI Workflows

Complete specification of all CI/CD workflow files for the Better Notion SDK.

## Workflow Files

```
.github/
└── workflows/
    ├── ci.yml
    ├── lint.yml
    ├── test.yml
    └── release.yml
```

---

## 1. Main CI Workflow

**File:** `.github/workflows/ci.yml`

### Purpose

Main CI pipeline that runs on every push and pull request. Provides comprehensive checking of code quality, tests, and build verification.

### Triggers

```yaml
on:
  push:
    branches: [main]
  pull_request:
    branches: ["**"]
  workflow_dispatch:  # Allow manual trigger
```

### Jobs

#### Job 1: Lint

**Runs:** Ruff linter and formatter checks

**Why separate job?**
- Fast execution (<30 seconds)
- Provides immediate feedback
- Can run in parallel with tests

**Steps:**
1. Checkout code
2. Install uv
3. Set up Python 3.10
4. Install dependencies (uv sync)
5. Run ruff check
6. Run ruff format --check

#### Job 2: Test

**Runs:** Full test suite with coverage

**Matrix Strategy:**
- Python 3.10, 3.11, 3.12 (latest 3 versions)
- Ubuntu Linux only (primary deployment target)

**Steps:**
1. Checkout code
2. Install uv
3. Set up Python ${{ matrix.python-version }}
4. Install dependencies (uv sync)
5. Run pytest with coverage
6. Upload coverage to Codecov
7. Check coverage threshold (≥80%)

**Why matrix?**
- Ensures compatibility across Python versions
- Python 3.10 is minimum required version
- Test on latest to catch future issues

#### Job 3: Build (Optional)

**Runs:** Build distribution packages

**When:** Only on push to main (not on PRs)

**Purpose:**
- Verify package builds correctly
- Catch build errors before release
- Upload artifacts for use in releases

**Steps:**
1. Checkout code
2. Install uv
3. Set up Python
4. Install build dependencies
5. Build wheel (uv build)
6. Upload artifacts

### Complete Workflow

```yaml
name: CI

on:
  push:
    branches: [main]
  pull_request:
    branches: ["**"]
  workflow_dispatch:

jobs:
  lint:
    name: Lint
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v3

      - name: Install uv
        run: |
          curl -LsSf https://astral.sh/uv/install.sh | sh
          echo "$HOME/.local/bin" >> $GITHUB_PATH

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: "3.10"
          cache: 'pip'

      - name: Install dependencies
        run: uv sync

      - name: Run ruff check
        run: uv run ruff check better_notion

      - name: Run ruff format check
        run: uv run ruff format --check better_notion

      - name: Check import sorting
        run: uv run ruff check --select I better_notion

  test:
    name: Test
    runs-on: ubuntu-latest
    needs: lint
    strategy:
      matrix:
        python-version: ["3.10", "3.11", "3.12"]
    steps:
      - name: Checkout code
        uses: actions/checkout@v3

      - name: Install uv
        run: |
          curl -LsSf https://astral.sh/uv/install.sh | sh
          echo "$HOME/.local/bin" >> $GITHUB_PATH

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: ${{ matrix.python-version }}
          cache: 'pip'

      - name: Install dependencies
        run: uv sync

      - name: Run pytest with coverage
        run: |
          uv run pytest \
            --cov=better_notion \
            --cov-report=xml \
            --cov-report=html \
            --cov-report=term-missing \
            --cov-fail-under=80 \
            -v

      - name: Upload coverage to Codecov
        uses: codecov/codecov-action@v3
        with:
          token: ${{ secrets.CODECOV_TOKEN }}
          files: ./coverage.xml
          flags: unittests
          name: codecov-umbrella

  build:
    name: Build
    runs-on: ubuntu-latest
    needs: [lint, test]
    if: github.event_name == 'push' and github.ref == 'refs/heads/main'
    steps:
      - name: Checkout code
        uses: actions/checkout@v3

      - name: Install uv
        run: |
          curl -LsSf https://astral.sh/uv/install.sh | sh
          echo "$HOME/.local/bin" >> $GITHUB_PATH

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: "3.10"
          cache: 'pip'

      - name: Install build dependencies
        run: |
          uv sync

      - name: Build wheel
        run: uv build

      - name: Upload artifacts
        uses: actions/upload-artifact@v3
        with:
          name: dist
          path: dist/
```

### Features

#### Caching

```yaml
- name: Cache uv packages
  uses: actions/cache@v3
  with:
    path: ~/.cache/uv
    key: ${{ runner.os }}-uv-${{ hashFiles('**/uv.lock') }}
    restore-keys: |
      ${{ runner.os }}-uv-
```

**Benefits:**
- Faster dependency installation
- Reduced bandwidth
- More reliable builds

#### Fail-Fast Strategy

```yaml
jobs:
  lint:
    # Runs first, very fast
  test:
    needs: lint  # Only runs if lint passes
```

**Benefits:**
- Quick feedback on style issues
- Don't waste time testing broken code
- Clear indication of what failed

---

## 2. Lint Workflow

**File:** `.github/workflows/lint.yml`

### Purpose

Provides fast linting feedback for pull requests. Runs independently and in parallel with the test workflow.

### When to Use

- For quick style checks
- During development before running full test suite
- On every pull request

### Complete Workflow

```yaml
name: Lint

on:
  pull_request:
    branches: ["**"]
  push:
    branches: ["**"]
  workflow_dispatch:

jobs:
  lint:
    name: Lint
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v3

      - name: Install uv
        run: |
          curl -LsSf https://astral.sh/uv/install.sh | sh
          echo "$HOME/.local/bin" >> $GITHUB_PATH

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: "3.10"
          cache: 'pip'

      - name: Install dependencies
        run: uv sync

      - name: Run ruff linter
        run: uv run ruff check better_notion

      - name: Check formatting
        run: uv run ruff format --check better_notion

      - name: Check import sorting
        run: uv run ruff check --select I better_notion
```

### Ruff Configuration

**Checks:**
- `ruff check` - All ruff checks
- `ruff format --check` - Code formatting
- `ruff check --select I` - Import sorting

---

## 3. Test Workflow

**File:** `.github/workflows/test.yml`

### Purpose

Run the full test suite. Can be triggered manually for testing or validation.

### When to Use

- Manual testing before merging
- Validation after changes
- Running tests without full CI

### Complete Workflow

```yaml
name: Test

on:
  push:
    branches: ["**"]
  workflow_dispatch:

jobs:
  test:
    name: Test
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ["3.10", "3.11", "3.12"]
    steps:
      - name: Checkout code
        uses: actions/checkout@v3

      - name: Install uv
        run: |
          curl -LsSf https://astral.sh/uv/install.sh | sh
          echo "$HOME/.local/bin" >> $PATH

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: ${{ matrix.python-version }}
          cache: 'pip'

      - name: Install dependencies
        run: uv sync

      - name: Run tests
        run: |
          uv run pytest \
            -v \
            --tb=short \
            --cov=better_notion \
            --cov-report=xml

      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          token: ${{ secrets.CODECOV_TOKEN }}
          files: ./coverage.xml
          flags: unittests
```

### Features

- Matrix testing across Python versions
- Coverage reporting to Codecov
- Verbose output for debugging
- Short traceback format
- No coverage threshold (allows partial runs)

---

## 4. Release Workflow

**File:** `.github/workflows/release.yml`

### Purpose

Automated release process triggered by git tags. Creates GitHub releases and publishes to PyPI.

### Triggers

```yaml
on:
  push:
    tags:
      - "v*"  # Semantic version tags (v1.0.0, v2.0.0, etc.)
```

### Jobs

#### Job 1: Build

**Purpose:** Build distribution packages

**Builds:**
- Source distribution (`.tar.gz`)
- Wheel distribution (`.whl`)

**Steps:**
1. Checkout code
2. Install uv
3. Set up Python
4. Install build dependencies
5. Build sdist and wheel
6. Upload artifacts

#### Job 2: Create GitHub Release

**Purpose:** Create GitHub release with assets

**Steps:**
1. Checkout code
2. Extract tag version
3. Generate changelog
4. Create GitHub release
5. Upload release assets (sdist, wheel)

#### Job 3: Publish to PyPI

**Purpose:** Publish package to PyPI

**Steps:**
1. Checkout code
2. Install uv
3. Set up Python
4. Install publish dependencies
5. Publish to PyPI using trusted publishing

### Complete Workflow

```yaml
name: Release

on:
  push:
    tags:
      - "v*"

permissions:
  contents: write

jobs:
  build:
    name: Build Packages
    runs-on: ubuntu-latest
    outputs:
      version: ${{ steps.version.outputs.version }}
    steps:
      - name: Checkout code
        uses: actions/checkout@v3

      - name: Install uv
        run: |
          curl -LsSf https://astral.sh/uv/install.sh | sh
          echo "$HOME/.local/bin" >> $GITHUB_PATH

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: "3.10"
          cache: 'pip'

      - name: Install build dependencies
        run: uv sync

      - name: Extract version from tag
        id: version
        run: |
          VERSION=${GITHUB_REF#refs/tags/v}
          echo "version=${VERSION#v}" >> $GITHUB_OUTPUT

      - name: Build distributions
        run: |
          uv build

      - name: Upload build artifacts
        uses: actions/upload-artifact@v3
        with:
          name: dist
          path: dist/

  release-github:
    name: Create GitHub Release
    needs: build
    runs-on: ubuntu-latest
    outputs:
      release_url: ${{ steps.release.outputs.url }}
    steps:
      - name: Checkout code
        uses: actions/checkout@v3
        with:
          fetch-depth: 0

      - name: Get version
        id: version
        run: echo "version=${{GITHUB_REF#refs/tags/v}}" >> $GITHUB_OUTPUT

      - name: Generate changelog
        id: changelog
        run: |
          # Extract changelog for this version
          gh release view ${{ steps.version.outputs.version }} --json > release.json
          cat release.json

      - name: Create GitHub Release
        id: release
        uses: softprops/action-gh-release@v1
        with:
          tag_name: ${{ steps.version.outputs.version }}
          name: Release ${{ steps.version.outputs.version }}
          body: ${{ steps.changelog.outputs.content }}
          draft: false
          files: dist/*

  release-github:
    name: Update release metadata
    needs: release-github
    runs-on: ubuntu-latest
    steps:
      - name: Upload release assets
        uses: actions/upload-artifact@v3
        with:
          name: release-assets
          path: dist/

  publish-pypi:
    name: Publish to PyPI
    needs: [build, release-github]
    runs-on: ubuntu-latest
    environment:
      PYPI_API_TOKEN: ${{ secrets.PYPI_API_TOKEN }}
    steps:
      - name: Checkout code
        uses: actions/checkout@v3

      - name: Install uv
        run: |
          curl -LsSf https://astral.sh/uv/install.sh | sh
          echo "$HOME/.local/bin" >> $GITHUB_PATH

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: "3.10"
          cache: 'pip'

      - name: Install publish dependencies
        run: uv sync

      - name: Publish to PyPI
        run: |
          uv publish
```

---

## Workflow Orchestration

### Dependency Graph

```
Lint
    └── (parallel) ───→ Test (3.10)
                          ├──→ Test (3.11)
                          └──→ Test (3.12)
                                    ↓
                                Build (on push to main only)
```

### Branch-Specific Behavior

**On Pull Request:**
- Lint runs
- Test runs (all versions)
- Build does NOT run
- Provides feedback without artifacts

**On Push to main:**
- Lint runs
- Test runs (all versions)
- Build runs (creates artifacts)
- No release (no tag)

**On Git Tag:**
- Full CI pipeline runs first
- Then release workflow runs
- Creates release and publishes

---

## Status Checks

### Required Checks

For merging to `main` branch:

```
✓ lint
✓ test (Python 3.10)
✓ test (Python 3.11)
✓ test (Python 3.12)
✓ coverage
```

### Check Definitions

**lint**
- All ruff checks pass
- Code is formatted correctly
- Imports are sorted

**test (Python X.Y)**
- All tests pass on Python X.Y
- Coverage threshold met (≥80%)

**coverage**
- Coverage report generated
- Uploads to Codecov successfully

---

## Execution Time

### Target Times

| Job | Target Time |
|-----|-------------|
| lint | < 30 seconds |
| test (single version) | < 2 minutes |
| test (all versions) | < 4 minutes |
| build | < 1 minute |
| Full CI | < 5 minutes |

### Optimization

- Parallel jobs (lint + test)
- Caching (uv cache)
- Minimal dependencies
- Fast tests (unit tests only in CI)

---

## Workflow Usage

### Manual Trigger

```bash
# Trigger lint workflow
gh workflow run lint

# Trigger test workflow
gh workflow run test

# Trigger release workflow
gh workflow run release
```

### Local Testing

```bash
# Install act (GitHub Actions runner)
brew install act

# Test workflows locally
act -j lint
act -j test
```

---

## Related Documentation

- [Overview](./overview.md) - CI/CD strategy overview
- [Testing Strategy](./testing.md) - Test configuration
- [Release Process](./releases.md) - Release details
- [Security](./security.md) - Secrets and security

---

## Summary

**4 Workflows:**
1. **ci.yml** - Full CI pipeline
2. **lint.yml** - Fast lint checks
3. **test.yml** - Test suite only
4. **release.yml** - Automated releases

**Key Features:**
- Parallel execution for speed
- Matrix testing (Python 3.10, 3.11, 3.12)
- Coverage reporting (Codecov)
- Automated PyPI publishing
- GitHub release creation

**Triggers:**
- Pull requests → CI
- Push to main → CI + Build
- Git tags → CI + Release

**Performance:**
- Target: < 5 minutes for full CI
- Lint: < 30 seconds
- Single test suite: < 2 minutes
