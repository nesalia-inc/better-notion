# Environment Setup

Complete guide to setting up your development environment for the Better Notion SDK.

## Overview

This guide walks you through setting up a complete development environment for working on the Better Notion SDK.

---

## Prerequisites

### Required

- **Python 3.10 or higher** (3.11+ recommended)
- **Git** - For version control
- **uv** - Package manager (Rust-based, very fast)

### Optional but Recommended

- **GitHub CLI** - For working with GitHub from terminal
- **VS Code** - Recommended IDE with excellent Python support
- **Pre-commit** - For running checks before commits

---

## Step 1: Install Prerequisites

### Python

**Check Python version:**
```bash
python --version
# or
python3 --version
```

**Install Python if needed:**

**macOS (using Homebrew):**
```bash
brew install python@3.11
```

**Windows:**
- Download from [python.org](https://www.python.org/downloads/)
- During install, check "Add Python to PATH"

**Linux (Ubuntu/Debian):**
```bash
sudo apt update
sudo apt install python3.11 python3.11-venv
```

### Git

**Check if installed:**
```bash
git --version
```

**Install if needed:**

**macOS:**
```bash
# Usually pre-installed
# Or via Homebrew
brew install git
```

**Windows:**
- Download from [git-scm.com](https://git-scm.com/downloads)

**Linux:**
```bash
sudo apt install git
```

### uv (Package Manager)

**Install uv:**

**macOS/Linux:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Windows (PowerShell):**
```bash
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

**Verify installation:**
```bash
uv --version
# Should output: uv 0.x.x
```

**Note:** uv will be installed in `~/.local/bin` on macOS/Linux. Add to PATH if needed:
```bash
# Add to ~/.bashrc or ~/.zshrc
export PATH="$HOME/.local/bin:$PATH"
```

### GitHub CLI (Optional)

**Install:**

**macOS:**
```bash
brew install gh
```

**Windows:**
- Download from [cli.github.com](https://cli.github.com/)

**Linux:**
```bash
sudo apt install gh
```

**Authenticate:**
```bash
gh auth login
```

---

## Step 2: Clone the Repository

**Clone the repository:**
```bash
git clone https://github.com/nesalia/better-notion.git
cd better-notion
```

**Verify:**
```bash
ls
# Should see: better_notion/, tests/, docs/, pyproject.toml, etc.
```

---

## Step 3: Create Virtual Environment

**Using uv:**
```bash
uv venv
```

This creates a `.venv/` directory with a Python virtual environment.

**Verify:**
```bash
ls .venv/
# Should see: bin/ (or Scripts/ on Windows), lib/, etc.
```

---

## Step 4: Activate Virtual Environment

**macOS/Linux:**
```bash
source .venv/bin/activate
```

**Windows (Command Prompt):**
```bash
.venv\Scripts\activate.bat
```

**Windows (PowerShell):**
```bash
.venv\Scripts\Activate.ps1
```

**Verify activation:**
```bash
which python
# Should show: .venv/bin/python

# Windows:
where python
# Should show: .venv\Scripts\python.exe
```

**Your prompt should change:**
```bash
(better-notion) $
```

---

## Step 5: Install Dependencies

**Using uv:**
```bash
uv sync
```

This installs all dependencies defined in `pyproject.toml`.

**What gets installed:**
- **Runtime dependencies:** httpx, pydantic, etc.
- **Development dependencies:** pytest, ruff, mypy, etc.

**Verify installation:**
```bash
uv pip list
# Should show all installed packages
```

---

## Step 6: Verify Installation

**Test Python imports:**
```bash
uv run python -c "import better_notion; print('Success!')"
# Should output: Success!
```

**Test pytest:**
```bash
uv run pytest --version
# Should output: pytest 8.x.x
```

**Test ruff:**
```bash
uv run ruff --version
# Should output: ruff 0.x.x
```

---

## Step 7: Configure Git Hooks (Optional)

**Install pre-commit hooks:**
```bash
uv run pre-commit install
```

This will automatically run checks before each commit.

**Test pre-commit:**
```bash
uv run pre-commit run --all-files
```

---

## Step 8: Configure IDE

### VS Code

**Install VS Code:**
- Download from [code.visualstudio.com](https://code.visualstudio.com/)

**Install Python extension:**
- Open VS Code
- Press `Ctrl+Shift+X` (or `Cmd+Shift+X` on Mac)
- Search "Python"
- Install Microsoft's Python extension

**Configure workspace settings:**

Create `.vscode/settings.json`:
```json
{
  "python.defaultInterpreterPath": "${workspaceFolder}/.venv/bin/python",
  "python.linting.enabled": true,
  "python.linting.ruffEnabled": true,
  "python.linting.ruffArgs": ["--fix"],
  "python.formatting.provider": "black",
  "python.testing.pytestEnabled": true,
  "python.testing.pytestArgs": ["tests"],
  "editor.formatOnSave": true,
  "editor.codeActionsOnSave": {
    "source.fixAll": true
  },
  "files.exclude": {
    "**/__pycache__": true,
    "**/.pytest_cache": true,
    "**/.mypy_cache": true,
    "**/.ruff_cache": true
  }
}
```

**On Windows, use backslash:**
```json
{
  "python.defaultInterpreterPath": "${workspaceFolder}\\.venv\\Scripts\\python.exe",
  ...
}
```

### PyCharm

**Configure Python interpreter:**
1. File → Settings → Project → Python Interpreter
2. Click "Add Interpreter" → "Existing Environment"
3. Select `.venv/bin/python` (or `.venv\Scripts\python.exe` on Windows)

**Enable pytest:**
1. File → Settings → Tools → Python Integrated Tools
2. Default test runner: pytest

**Configure code style:**
1. File → Settings → Editor → Code Style → Python
2. Set line length to 100

---

## Environment Variables

### Optional: Test Tokens

**For integration tests**, create a `.env` file:

```bash
# .env file (NOT in version control)
NOTION_TEST_TOKEN=secret_...
NOTION_TEST_DATABASE_ID=...
NOTION_TEST_PAGE_ID=...
```

**Load in Python:**
```python
import os
from dotenv import load_dotenv

load_dotenv()

token = os.getenv("NOTION_TEST_TOKEN")
```

**Note:** `.env` is in `.gitignore` and won't be committed.

---

## Common Commands

### Development Commands

```bash
# Run tests
uv run pytest

# Run specific test file
uv run pytest tests/unit/test_http_client.py

# Run with coverage
uv run pytest --cov=better_notion --cov-report=html

# Format code
uv run ruff format better_notion

# Check linting
uv run ruff check better_notion

# Auto-fix linting issues
uv run ruff check --fix better_notion

# Type checking
uv run mypy better_notion
```

### Package Commands

```bash
# Install in development mode
uv pip install -e .

# Build package
uv build

# Install built package
uv pip install dist/better_notion-0.1.0-py3-none-any.whl
```

### Git Commands

```bash
# Check status
git status

# See commits
git log --oneline

# Create branch
git checkout -b feature/my-feature

# Push to remote
git push origin feature/my-feature

# Create PR (requires GitHub CLI)
gh pr create
```

---

## Troubleshooting

### Problem: uv command not found

**Solution:**
```bash
# Add to PATH
export PATH="$HOME/.local/bin:$PATH"

# Add to ~/.bashrc or ~/.zshrc for persistence
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
```

### Problem: Python version too old

**Solution:**
```bash
# Install newer Python
# macOS
brew install python@3.11

# Ubuntu/Debian
sudo apt install python3.11

# Set specific Python version for uv
uv venv --python 3.11
```

### Problem: Import errors

**Solution:**
```bash
# Ensure venv is activated
source .venv/bin/activate  # macOS/Linux
.venv\Scripts\activate     # Windows

# Reinstall dependencies
uv sync

# Verify PYTHONPATH
echo $PYTHONPATH  # Should be empty or include project root
```

### Problem: Tests failing locally

**Solution:**
```bash
# Update dependencies
uv sync --upgrade

# Clear cache
python -m pytest --cache-clear

# Run with verbose output
uv run pytest -vv
```

### Problem: VS Code not finding interpreter

**Solution:**
1. Press `Ctrl+Shift+P` (or `Cmd+Shift+P` on Mac)
2. Type "Python: Select Interpreter"
3. Choose the interpreter in `.venv/`

### Problem: Pre-commit hooks not running

**Solution:**
```bash
# Reinstall pre-commit
uv run pre-commit uninstall
uv run pre-commit install

# Run manually to test
uv run pre-commit run --all-files
```

---

## Updating Dependencies

### Update all dependencies

```bash
# Update uv lockfile
uv lock --upgrade

# Sync to install updated versions
uv sync
```

### Update specific package

```bash
# Update httpx only
uv add httpx --upgrade
```

### Check for outdated packages

```bash
# List outdated (requires pip)
uv pip list --outdated
```

---

## Clean Start

If you're having issues, start fresh:

```bash
# Deactivate venv
deactivate

# Remove venv
rm -rf .venv/

# Remove uv cache
rm -rf .uv-cache/

# Start over from step 3
uv venv
source .venv/bin/activate
uv sync
```

---

## Next Steps

Once your environment is set up:

1. **Read the project structure:**
   ```bash
   # Understand the codebase
   cat docs/development/project-structure.md
   ```

2. **Review coding standards:**
   ```bash
   # Learn how to write code
   cat docs/development/standards.md
   ```

3. **Check out Git workflow:**
   ```bash
   # Learn how we work with Git
   cat docs/development/git-workflow.md
   ```

4. **Make your first change:**
   ```bash
   # Create a branch
   git checkout -b feature/my-first-feature

   # Make a small change
   # Test it
   uv run pytest

   # Commit
   git add .
   git commit -m "feat: add my first feature"
   ```

---

## Summary

**Setup Checklist:**

- [ ] Python 3.10+ installed
- [ ] Git installed
- [ ] uv installed
- [ ] Repository cloned
- [ ] Virtual environment created
- [ ] Dependencies installed
- [ ] Installation verified
- [ ] IDE configured

**Essential Commands:**

```bash
# Activate venv
source .venv/bin/activate

# Install deps
uv sync

# Run tests
uv run pytest

# Format code
uv run ruff format better_notion

# Check linting
uv run ruff check better_notion
```

---

## Related Documentation

- [project-structure.md](./project-structure.md) - Understand the codebase
- [standards.md](./standards.md) - Code conventions
- [git-workflow.md](./git-workflow.md) - Git workflow
- [workflow.md](./workflow.md) - Development workflow

---

**Last Updated:** 2025-01-23
