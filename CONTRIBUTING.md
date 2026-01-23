# Contributing to Better Notion

First off, thank you for considering contributing to Better Notion! It's people like you that make Better Notion such a great tool.

## How to Contribute

### Reporting Bugs

Before creating bug reports, please check existing issues to avoid duplicates. When creating a bug report, include:

- **Clear title and description** of the problem
- **Minimal code example** to reproduce the issue
- **Python version** and OS version
- **Any error messages** or stack traces
- **Steps to reproduce** the issue

### Suggesting Enhancements

Enhancement suggestions are welcome! Please:

- **Use a clear title** describing the enhancement
- **Provide a detailed explanation** of the feature and why it would be useful
- **Consider the impact** on existing API and users
- **Think about backwards compatibility**

### Pull Requests

Pull requests are the best way to contribute. Here's how to get started:

## Development Setup

### Prerequisites

- Python 3.10 or higher
- [uv](https://github.com/astral-sh/uv) for fast package management
- Git

### Setting Up Your Development Environment

1. **Fork and clone the repository:**

```bash
git clone https://github.com/nesalia-inc/better-notion.git
cd better-notion
```

2. **Install development dependencies:**

```bash
uv sync
```

3. **Create a virtual environment and activate it:**

```bash
# uv creates a virtual environment automatically
uv run python --version
```

### Running Tests

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=better_notion --cov-report=html

# Run specific test file
uv run pytest tests/unit/test_client.py

# Run with verbose output
uv run pytest -v
```

### Code Quality

We use several tools to maintain code quality:

```bash
# Format code
uv run ruff format .

# Check linting
uv run ruff check .

# Type checking
uv run mypy better_notion
```

## Coding Standards

### Style Guide

We follow [PEP 8](https://pep8.org/) with these specifics:

- **Line length**: 100 characters
- **Indentation**: 4 spaces
- **Quotes**: Double quotes for strings
- **Import ordering**: Enforced by ruff

### Type Hints

- All public functions must have type hints
- Use `from __future__ import annotations` in all modules
- Prefer `str | None` over `Optional[str]`

### Documentation

- All public functions, classes, and methods must have docstrings
- Use Google style docstrings (see existing code for examples)
- Include examples for complex operations

### Async/Await

- All API operations are async
- Use `async def` for coroutines
- Always use `await` when calling async functions

## Project Structure

```
better_notion/
├── _api/                 # Low-level API implementation
│   ├── client.py        # Main NotionAPI client
│   ├── entities/        # Entity classes (Page, Block, etc.)
│   ├── collections/     # Collection classes
│   ├── properties/      # Property builders
│   └── utils/           # Utilities (pagination, etc.)
├── _sdk/                # High-level SDK (planned)
└── utils/              # Helper functions
```

## Making Changes

### 1. Create a Branch

```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/your-bug-fix
```

### 2. Make Your Changes

- Write clean, readable code
- Add tests for new functionality
- Update documentation as needed
- Follow the existing code style

### 3. Write Tests

- Add tests for any new functionality
- Maintain test coverage above 80%
- Write descriptive test names
- Use fixtures for common test data

### 4. Run Tests

```bash
uv run pytest
```

Make sure all tests pass before submitting.

### 5. Commit Your Changes

```bash
git add .
git commit -m "feat: add your feature description"
```

Commit messages should follow [Conventional Commits](https://www.conventionalcommits.org/):

- `feat:` - New features
- `fix:` - Bug fixes
- `docs:` - Documentation changes
- `test:` - Adding or updating tests
- `refactor:` - Code refactoring
- `chore:` - Maintenance tasks

### 6. Push and Create Pull Request

```bash
git push origin feature/your-feature-name
```

Then create a pull request on GitHub.

## Pull Request Guidelines

### Description

Provide a clear description of what your PR does and why it's useful.

### Tests

All PRs should include tests for new functionality. Existing tests should continue to pass.

### Documentation

Update documentation (README, docstrings, etc.) as needed.

### Small PRs

Keep PRs focused and relatively small. Large PRs are harder to review.

### One Change at a Time

Avoid bundling unrelated changes. Separate them into multiple PRs.

## Development Workflow

1. Discuss larger changes in an issue or discussion first
2. Fork the repo and create your branch
3. Make your changes following our standards
4. Add tests and documentation
5. Ensure all tests pass
6. Submit your pull request
7. Address review feedback
8. Once approved, your PR will be merged

## Release Process

Releases are managed by the maintainers. The versioning follows [Semantic Versioning](https://semver.org/):

- **MAJOR** version for incompatible API changes
- **MINOR** version for backwards-compatible functionality additions
- **PATCH** version for backwards-compatible bug fixes

## Getting Help

If you need help:

- Check existing [documentation](README.md)
- Search [existing issues](https://github.com/nesalia-inc/better-notion/issues)
- Start a [discussion](https://github.com/nesalia-inc/better-notion/discussions)
- Ask a question in an issue with the "question" label

## Code of Conduct

This project and its contributors are expected to adhere to the [Python Community Code of Conduct](https://www.python.org/psf/conduct/).

In short:

- Be respectful and inclusive
- Focus on constructive feedback
- Accept responsibility and apologize for mistakes

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
