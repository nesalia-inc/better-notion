# Development Documentation

**INTERNAL USE ONLY** - This documentation is for the Better Notion SDK development team.

This section contains practical guides for working on the project day-to-day. It complements the design documentation in `/docs/sdk/` and `/docs/cicd/`.

---

## Purpose

This documentation answers the practical questions of development:

- **How is the project organized?** → `project-structure.md`
- **How should I write code?** → `standards.md`
- **How do I work with Git?** → `git-workflow.md`
- **How do I set up my environment?** → `setup.md`
- **What's the development workflow?** → `workflow.md`
- **How do I write tests?** → `testing-strategy.md`
- **How do I debug issues?** → `debugging.md`

---

## Quick Start

### First Time Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/nesalia/better-notion.git
   cd better-notion
   ```

2. **Install dependencies**
   ```bash
   uv venv
   source .venv/bin/activate  # Windows: .venv\Scripts\activate
   uv sync
   ```

3. **Verify installation**
   ```bash
   uv run pytest --version
   uv run ruff --version
   ```

See [`setup.md`](./setup.md) for detailed setup instructions.

### Daily Workflow

1. **Update main**
   ```bash
   git checkout main
   git pull
   ```

2. **Create feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Make changes**
   ```bash
   # Write code
   uv run ruff format better_notion  # Format
   uv run ruff check better_notion   # Lint
   uv run pytest                     # Test
   git commit -m "feat: description"
   ```

4. **Create PR**
   ```bash
   git push origin feature/your-feature-name
   gh pr create
   ```

See [`workflow.md`](./workflow.md) for the complete development cycle.

---

## Documentation Structure

```
docs/development/
├── README.md                   # This file - navigation
├── project-structure.md        # Folder/file organization
├── standards.md                # Code style and conventions
├── git-workflow.md             # Branch strategy, commits, PRs
├── setup.md                    # Environment setup
├── workflow.md                 # Development cycle
├── testing-strategy.md         # How to write tests
└── debugging.md                # Debugging techniques
```

---

## Key Documents

### For New Developers

Start here if you're new to the project:

1. [setup.md](./setup.md) - Set up your development environment
2. [project-structure.md](./project-structure.md) - Understand the codebase
3. [standards.md](./standards.md) - Learn coding conventions
4. [workflow.md](./workflow.md) - Understand the development process

### For Daily Development

Reference these while working:

- [standards.md](./standards.md) - Code style guide
- [testing-strategy.md](./testing-strategy.md) - How to write tests
- [git-workflow.md](./git-workflow.md) - Git conventions
- [debugging.md](./debugging.md) - Debugging help

---

## Related Documentation

This development documentation complements:

- **[SDK Design](../sdk/README.md)** - Architecture and design philosophy
- **[Low-Level API](../sdk/api/README.md)** - Technical specifications
- **[CI/CD](../cicd/overview.md)** - CI/CD strategy and workflows
- **[PROJECT.md](../PROJECT.md)** - Original project vision

---

## Important Concepts

### Two-Level Architecture

The SDK has two layers:

- **Low-level** (`_lowlevel/`) - Direct 1:1 mapping with Notion API
- **High-level** (`_highlevel/`) - Rich abstractions and caching

See [SDK Architecture](../sdk/architecture.md) for details.

### Internal vs Public

- Modules starting with `_` are **internal** (not public API)
- Public API is exported from `better_notion/__init__.py`
- Internal modules can change without notice
- Public API follows semantic versioning

### Testing Philosophy

- **Unit tests** - Fast, isolated, no network
- **Integration tests** - Slower, may use network
- Target: ≥80% coverage

See [testing-strategy.md](./testing-strategy.md) for details.

---

## Common Tasks

### Run Tests

```bash
# All tests
uv run pytest

# Unit tests only
uv run pytest tests/unit/

# With coverage
uv run pytest --cov=better_notion --cov-report=html
```

### Format and Lint

```bash
# Format code
uv run ruff format better_notion

# Check linting
uv run ruff check better_notion

# Check import sorting
uv run ruff check --select I better_notion
```

### Create Feature

```bash
# From main
git checkout main
git pull

# Create branch
git checkout -b feature/my-feature

# Work
# ... write code ...
git add .
git commit -m "feat: add my feature"

# Push and PR
git push origin feature/my-feature
gh pr create
```

---

## Getting Help

### Documentation

- **Can't find a file?** → Check [project-structure.md](./project-structure.md)
- **Not sure how to style code?** → See [standards.md](./standards.md)
- **Test failing?** → Check [testing-strategy.md](./testing-strategy.md)
- **Git issues?** → Review [git-workflow.md](./git-workflow.md)

### Debugging

- **Can't figure out what's wrong?** → See [debugging.md](./debugging.md)
- **Tests passing locally but not in CI?** → Check Python version, dependencies

### Questions

If documentation doesn't answer your question:

1. Check related design docs in `/docs/sdk/`
2. Check CI/CD docs in `/docs/cicd/`
3. Ask the team

---

## Status

**Documentation:** Complete
**Ready for:** Implementation phase

---

**Last Updated:** 2025-01-23
