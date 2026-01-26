# CLI Design Proposal - Better Notion

**Status**: Proposed
**Author**: Better Notion Team
**Created**: 2025-01-25
**Version**: 1.0

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [Why a CLI?](#why-a-cli)
3. [Framework Selection](#framework-selection)
4. [Architecture Overview](#architecture-overview)
5. [Command Structure](#command-structure)
6. [Integration with Existing Code](#integration-with-existing-code)
7. [Configuration Management](#configuration-management)
8. [Output Formatting](#output-formatting)
9. [Async Support](#async-support)
10. [Dependencies](#dependencies)
11. [Usage Examples](#usage-examples)
12. [Implementation Plan](#implementation-plan)
13. [Testing Strategy](#testing-strategy)
14. [Documentation](#documentation)
15. [Success Metrics](#success-metrics)

---

## Executive Summary

This document proposes the implementation of a comprehensive Command Line Interface (CLI) for Better Notion, a modern Python SDK for the Notion API. The CLI will enable developers and power users to interact with Notion directly from their terminal, providing quick access to common operations without writing Python code.

**Key Benefits:**
- Rapid prototyping and testing of Notion API interactions
- Automation and scripting capabilities
- Developer-friendly interface with auto-completion
- Consistent with modern Python CLI best practices
- Minimal coupling with existing SDK code

**Recommended Framework:** [Typer](https://typer.tiangolo.com/)
**Estimated Implementation Time:** 6-8 weeks (7 phases)
**Target Release:** v0.4.0

---

## Why a CLI?

### Use Cases

#### 1. **Quick Testing & Debugging**
Developers often need to quickly test API calls or inspect data structure without writing a full Python script.

```bash
# Instead of writing a script:
# test.py
# from better_notion import NotionClient
# async with NotionClient(auth=token) as client:
#     page = await client.pages.get("page_id")
#     print(page)

# Just run:
$ notion pages get page_id
```

#### 2. **Automation & Scripting**
Integrate Notion operations into shell scripts, CI/CD pipelines, or automation workflows.

```bash
#!/bin/bash
# Deploy automation
PAGE_ID=$(notion pages create --title "Deploy $(date)" --parent deploy_db)
notion blocks create --parent $PAGE_ID --text "Build started at $(date)"

# Run tests...
pytest

notion blocks create --parent $PAGE_ID --text "Build completed successfully"
```

#### 3. **Data Export & Migration**
Quickly export data from Notion for backup, analysis, or migration to other systems.

```bash
# Export all tasks to CSV
$ notion databases query tasks_db --output csv > tasks_$(date +%Y%m%d).csv

# Backup all pages in a workspace
$ notion pages list --recursive --output json > backup.json
```

#### 4. **Interactive Operations**
Interactive mode for complex operations like creating pages with multiple properties.

```bash
$ notion pages create --interactive
? Select parent database: Project Database [database_abc]
? Page title: Q1 Planning
? Status: [In Progress]
? Priority: [High]
? Assignee: John Doe
✅ Page created: page_xyz123
```

#### 5. **Developer Experience**
Lower barrier to entry for users who prefer terminal over Python code.

### Competitive Analysis

| Project | CLI? | Language | Notes |
|---------|------|----------|-------|
| **Notion official** | ❌ No | - | REST API only |
| **notion-py** | ❌ No | Python | Library only |
| **notion-sdk-py** | ❌ No | Python | Library only |
| **PyNotion** | ❌ No | Python | Library only |
| **Better Notion** | ✅ **Planned** | Python | **First with CLI!** |

**Opportunity:** Better Notion can be the **first** Python SDK for Notion with a comprehensive CLI.

---

## Framework Selection

### Evaluation Criteria

We evaluated four popular CLI frameworks for Python:

| Framework | Type Safety | Async Support | DX* | Maturity | Ecosystem |
|-----------|-------------|---------------|-----|----------|-----------|
| **Typer** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | Growing |
| **Click** | ⭐⭐ | ⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | Massive |
| **Argparse** | ⭐ | ⭐ | ⭐⭐ | ⭐⭐⭐⭐ | Built-in |
| **Cloup** | ⭐⭐ | ⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ | Small |

\*DX = Developer Experience

### Why Typer?

**1. Native Type Hints**
```python
# Typer - Type annotations drive CLI
def create_user(name: str, age: int = 18, admin: bool = False):
    """Create a new user"""
    pass

# Click - Manual type specification
@click.command()
@click.option("--name", type=str, required=True)
@click.option("--age", type=int, default=18)
@click.option("--admin", type=bool, default=False)
def create_user(name, age, admin):
    """Create a new user"""
    pass
```

**2. Automatic --help Generation**
Typer automatically generates beautiful help text from docstrings and type hints.

**3. Async Support**
Works seamlessly with async functions (critical for Notion API).

**4. Click Compatibility**
Can use Click extensions and plugins.

**5. Modern & Active**
Actively maintained by the FastAPI creator (Tiangolo).

### Alternatives Considered

**Click** - Rejected due to verbose syntax and lack of native typing. However, we can use Click's ecosystem (plugins, extensions) via Typer's compatibility.

**Argparse** - Rejected due to poor developer experience and manual type handling.

---

## Architecture Overview

### Directory Structure

```
better-notion/
├── better_notion/
│   ├── __init__.py
│   ├── _api/              # Existing low-level API
│   ├── _sdk/              # Existing high-level SDK
│   └── _cli/              # 🆕 CLI module (proposed)
│       ├── __init__.py
│       ├── main.py        # Entry point
│       ├── config.py      # Configuration management
│       ├── output.py      # Output formatters
│       ├── commands/      # CLI commands
│       │   ├── __init__.py
│       │   ├── pages.py
│       │   ├── databases.py
│       │   ├── blocks.py
│       │   ├── users.py
│       │   ├── comments.py
│       │   ├── search.py
│       │   └── auth.py
│       └── utils/         # CLI utilities
│           ├── __init__.py
│           ├── async_helper.py
│           ├── validators.py
│           └── formatters.py
├── tests/
│   └── cli/              # 🆕 CLI tests
│       ├── test_commands.py
│       ├── test_output.py
│       └── fixtures/
└── docs/
    └── cli/              # 🆕 CLI documentation
        ├── cli-design-proposal.md  # This document
        ├── installation.md
        ├── getting-started.md
        └── commands.md
```

### Design Principles

1. **Separation of Concerns**: CLI is a thin interface layer; business logic remains in SDK
2. **Async-First**: All operations use async under the hood
3. **Type-Safe**: Leverage Python type hints for validation
4. **User-Friendly**: Clear error messages, helpful suggestions
5. **Testable**: Each command is independently testable
6. **Extensible**: Easy to add new commands

### Component Diagram

```
┌─────────────────────────────────────────────────────────┐
│                     User (Terminal)                      │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│                    CLI Layer (Typer)                     │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌────────┐  │
│  │ Pages    │  │Database  │  │ Blocks   │  │ Auth   │  │
│  │ Commands │  │Commands  │  │Commands  │  │Commands│  │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬───┘  │
│       │             │             │             │        │
│       └─────────────┴─────────────┴─────────────┘        │
│                     │                                     │
│              ┌──────▼──────┐                             │
│              │ Output      │                             │
│              │ Formatter   │                             │
│              └──────┬──────┘                             │
└─────────────────────┼────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────┐
│              Async Helper (run_async wrapper)            │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│            SDK Layer (NotionClient)                      │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐   │
│  │PageMgr  │  │Databse  │  │BlockMgr │  │UserMgr  │   │
│  │         │  │Mgr      │  │         │  │         │   │
│  └────┬────┘  └────┬────┘  └────┬────┘  └────┬────┘   │
│       │            │            │            │          │
│       └────────────┴────────────┴────────────┘          │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│              API Layer (NotionAPI)                       │
│              HTTP Client (httpx)                         │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
              Notion API (https://api.notion.com)
```

---

## Command Structure

### Command Hierarchy

```
notion                          # Root command
│
├── auth                        # Authentication commands
│   ├── login                   # Configure token
│   ├── status                  # Check authentication
│   └── logout                  # Remove credentials
│
├── pages                       # Page operations
│   ├── get <id>                # Retrieve page by ID
│   ├── create                  # Create new page
│   ├── list                    # List pages (from database)
│   ├── update <id>             # Update page
│   ├── delete <id>             # Delete page
│   └── search <query>          # Search pages
│
├── databases                   # Database operations
│   ├── get <id>                # Retrieve database
│   ├── query <id>              # Query database
│   ├── list                    # List databases
│   └── create                  # Create database
│
├── blocks                      # Block operations
│   ├── get <id>                # Retrieve block
│   ├── create                  # Create block
│   ├── update <id>             # Update block
│   ├── delete <id>             # Delete block
│   └── children <id>           # List child blocks
│
├── users                       # User operations
│   ├── get <id>                # Retrieve user
│   ├── me                      # Current user info
│   └── list                    # List users
│
├── comments                    # Comment operations
│   ├── get <id>                # Retrieve comment
│   ├── create                  # Create comment
│   ├── list <parent_id>        # List comments
│   └── delete <id>             # Delete comment
│
└── search                      # Global search
    ├── all <query>             # Search all types
    ├── pages <query>           # Search pages only
    └── databases <query>       # Search databases only
```

### Command Examples

#### Get Page
```bash
$ notion pages get page_abc123 --output json

{
  "id": "page_abc123",
  "title": "My Page",
  "created_time": "2025-01-25T10:00:00.000Z",
  "last_edited_time": "2025-01-25T12:00:00.000Z",
  ...
}
```

#### Create Page
```bash
$ notion pages create \
  --parent database_xyz \
  --title "New Task" \
  --property "Status:To Do" \
  --property "Priority:High"

✅ Page created: page_def456
```

#### Query Database
```bash
$ notion databases query db_123 \
  --filter "Status=Done" \
  --sort "created_at:desc" \
  --output table

┏━━━━━━━━━━━━┳━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━┓
┃ ID         ┃ Title   ┃ Status             ┃
┡━━━━━━━━━━━━╇━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━┩
┃ page_001   ┃ Task 1  ┃ Done               ┃
┃ page_002   ┃ Task 2  ┃ Done               ┃
└────────────┴─────────┴────────────────────┘
```

#### Search
```bash
$ notion search pages "project" --limit 5

Found 3 pages:
  • page_abc123 - "Project Planning"
  • page_def456 - "Project Timeline"
  • page_ghi789 - "Project Resources"
```

---

## Integration with Existing Code

### Which API to Use?

**Decision:** Use **NotionClient** (high-level SDK)

**Rationale:**
1. **Simplicity**: Cleaner API for common operations
2. **Caching**: Built-in cache improves performance
3. **Type Safety**: Works with rich model types
4. **Future-Proof**: Less likely to break with API changes

**NotionAPI** (low-level) will be used only for edge cases not covered by SDK.

### Example: Page Get Command

```python
# better_notion/_cli/commands/pages.py
from better_notion import NotionClient
from better_notion._cli.config import get_config
from better_notion._cli.utils import run_async

def get_page(page_id: str, output: str = "json"):
    """Get a page by ID"""

    async def _get():
        config = get_config()  # Load token from config

        async with NotionClient(auth=config.token) as client:
            # Use SDK's high-level API
            page = await client.pages.get(page_id)

            # Return dict for output formatting
            return page.to_dict()

    result = run_async(_get())

    # Format and print output
    formatter = OutputFormatter(output)
    formatter.print(result)
```

### No Code Duplication

The CLI will **not** duplicate business logic. It will:
1. Parse command-line arguments
2. Load configuration
3. Call SDK methods
4. Format output
5. Handle errors

All API interaction logic remains in the SDK.

---

## Configuration Management

### Configuration File Location

**Unix/Linux/macOS:** `~/.notion/config.json`
**Windows:** `%USERPROFILE%\.notion\config.json`

### Configuration Schema

```json
{
  "token": "secret_abc123...",
  "default_database": "database_xyz",
  "default_output": "json",
  "timeout": 30,
  "retry_attempts": 3
}
```

### Configuration API

```python
# better_notion/_cli/config.py
from dataclasses import dataclass
from pathlib import Path
import json
import typer

@dataclass
class Config:
    """CLI configuration"""
    token: str
    default_database: str | None = None
    default_output: str = "json"
    timeout: int = 30
    retry_attempts: int = 3

    @classmethod
    def load(cls) -> "Config":
        """Load configuration from ~/.notion/config.json"""
        config_path = Path.home() / ".notion" / "config.json"

        if not config_path.exists():
            typer.echo(
                "⚠️  Not configured. Run 'notion auth login' first.",
                err=True
            )
            raise typer.Exit(1)

        with open(config_path) as f:
            data = json.load(f)

        return cls(**data)

    @classmethod
    def save(cls, **kwargs) -> "Config":
        """Save configuration to ~/.notion/config.json"""
        config_dir = Path.home() / ".notion"
        config_dir.mkdir(exist_ok=True)

        config_path = config_dir / "config.json"

        with open(config_path, "w") as f:
            json.dump(kwargs, f, indent=2)

        typer.echo(f"✅ Configuration saved to {config_path}")

        return cls(**kwargs)
```

### Authentication Commands

```bash
# Login (store token)
$ notion auth login
? Enter your Notion integration token: secret_********************
✅ Token saved to ~/.notion/config.json

# Status (check authentication)
$ notion auth status
✅ Authenticated as: workspace-name
📧 Email: user@example.com

# Logout (remove credentials)
$ notion auth logout
✅ Removed configuration from ~/.notion/config.json
```

---

## Output Formatting

### Supported Formats

| Format | Description | Use Case |
|--------|-------------|----------|
| `json` | JSON with syntax highlighting | Scripts, APIs, debugging |
| `table` | Rich table format | Human-readable output |
| `markdown` | Markdown table | Documentation, reports |
| `csv` | Comma-separated values | Data export, analysis |
| `plain` | Plain text | Simple output, logs |

### Output Formatter Implementation

```python
# better_notion/_cli/output.py
from enum import Enum
from typing import Any
import json
import csv
from rich.console import Console
from rich.table import Table
from rich.json import RichJson

class OutputFormat(str, Enum):
    JSON = "json"
    TABLE = "table"
    MARKDOWN = "markdown"
    CSV = "csv"
    PLAIN = "plain"

class OutputFormatter:
    """Format and print CLI output"""

    def __init__(self, format: OutputFormat = OutputFormat.JSON):
        self.format = format
        self.console = Console()

    def print(self, data: Any, **kwargs):
        """Print data in specified format"""

        if self.format == OutputFormat.JSON:
            self._print_json(data)

        elif self.format == OutputFormat.TABLE:
            self._print_table(data, **kwargs)

        elif self.format == OutputFormat.MARKDOWN:
            self._print_markdown(data)

        elif self.format == OutputFormat.CSV:
            self._print_csv(data, **kwargs)

        else:  # PLAIN
            self._print_plain(data)

    def _print_json(self, data: Any):
        """Print JSON with syntax highlighting"""
        self.console.print_json(data)

    def _print_table(self, data: Any, columns: list[str] = None):
        """Print rich table"""
        table = Table(title="Results")

        # Add columns
        if columns:
            for col in columns:
                table.add_column(col)

        # Add rows
        if isinstance(data, list):
            for item in data:
                table.add_row(*[str(item.get(col)) for col in columns])

        self.console.print(table)

    def _print_csv(self, data: Any, columns: list[str] = None):
        """Print CSV format"""
        import sys

        writer = csv.writer(sys.stdout)

        if isinstance(data, list) and data:
            # Write header
            if columns:
                writer.writerow(columns)
            else:
                writer.writerow(data[0].keys())

            # Write rows
            for item in data:
                if columns:
                    writer.writerow([item.get(col) for col in columns])
                else:
                    writer.writerow(item.values())
```

### Usage Examples

```bash
# JSON output (default)
$ notion pages get page_123 --output json
{
  "id": "page_123",
  "title": "My Page"
}

# Table output
$ notion pages list --output table
┏━━━━━━━━━━━━┳━━━━━━━━━━━━━━┓
┃ ID         ┃ Title        ┃
┡━━━━━━━━━━━━╇━━━━━━━━━━━━━━┩
┃ page_001   ┃ Page 1       ┃
┃ page_002   ┃ Page 2       ┃
└────────────┴──────────────┘

# CSV export
$ notion databases query db_123 --output csv > tasks.csv
```

---

## Async Support

### The Async Challenge

Typer doesn't natively support async commands. We need a wrapper to run async functions in a sync context.

### Solution: Async Helper

```python
# better_notion/_cli/utils/async_helper.py
import asyncio
from typing import Awaitable, TypeVar

T = TypeVar("T")

def run_async(coro: Awaitable[T]) -> T:
    """
    Run async function in sync context (for CLI commands).

    Args:
        coro: Async coroutine to execute

    Returns:
        Result of the async operation
    """
    try:
        # Try to get existing event loop
        loop = asyncio.get_event_loop()
    except RuntimeError:
        # Create new loop if none exists
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    return loop.run_until_complete(coro)
```

### Usage in Commands

```python
from better_notion._cli.utils import run_async
from better_notion import NotionClient

def get_page(page_id: str):
    """Sync wrapper for async page retrieval"""

    async def _get():
        async with NotionClient(auth=token) as client:
            page = await client.pages.get(page_id)
            return page.to_dict()

    result = run_async(_get)
    formatter.print(result)
```

### Context Manager Support

```python
async def get_client():
    """Get configured NotionClient"""
    config = Config.load()
    return NotionClient(auth=config.token)

# Usage
async def _get():
    async with await get_client() as client:
        return await client.pages.get(page_id)
```

---

## Dependencies

### New Dependencies

```toml
[project.optional-dependencies]
cli = [
    "typer>=0.12.0,<0.13.0",      # CLI framework
    "rich>=13.0.0,<14.0.0",       # Terminal formatting
    "questionary>=2.0.0,<3.0.0",  # Interactive prompts
    "pyperclip>=1.8.0,<2.0.0",    # Clipboard support
]
```

### Dependency Breakdown

| Package | Version | Purpose | License |
|---------|---------|---------|---------|
| **typer** | ^0.12.0 | CLI framework with type hints | MIT |
| **rich** | ^13.0.0 | Terminal formatting (tables, colors) | MIT |
| **questionary** | ^2.0.0 | Interactive prompts (like Inquirer.js) | MIT |
| **pyperclip** | ^1.8.0 | Clipboard access for copying IDs | BSD |

### Installation

```bash
# Install CLI dependencies
pip install better-notion[cli]

# Or install everything
pip install better-notion[all]
```

### Entry Point

```toml
[project.scripts]
notion = "better_notion._cli.main:app"
```

This creates the `notion` command when installed.

---

## Usage Examples

### Basic Operations

#### Authentication
```bash
$ notion auth login
? Paste your Notion token: secret_abc123...
✅ Token saved to ~/.notion/config.json

$ notion auth status
✅ Authenticated
Workspace: My Workspace
Email: user@example.com
```

#### Get Page
```bash
$ notion pages get page_abc123
{
  "id": "page_abc123",
  "title": "Project Planning",
  "created_time": "2025-01-25T10:00:00.000Z",
  "parent": {
    "type": "database_id",
    "database_id": "database_xyz"
  },
  "properties": {
    "Status": {
      "type": "select",
      "select": {
        "name": "In Progress"
      }
    }
  }
}
```

#### Create Page
```bash
$ notion pages create \
  --parent database_xyz \
  --title "New Task" \
  --property "Status:To Do" \
  --property "Priority:High"

✅ Page created: page_def456

# Or use interactive mode
$ notion pages create --interactive
? Select parent database: Project Database
? Page title: Q1 Planning
? Status: [In Progress]
? Priority: [High]
✅ Page created: page_ghi789
```

#### List Pages
```bash
$ notion pages list --database database_xyz --output table
┏━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━┓
┃ ID             ┃ Title         ┃ Status       ┃
┡━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━┩
┃ page_001       ┃ Task 1        ┃ To Do        ┃
┃ page_002       ┃ Task 2        ┃ In Progress  ┃
┃ page_003       ┃ Task 3        ┃ Done         ┃
└────────────────┴───────────────┴──────────────┘
```

### Advanced Operations

#### Query Database
```bash
# Query with filter
$ notion databases query db_123 \
  --filter "Status=Done" \
  --sort "created_at:desc" \
  --limit 10

# Query and export to CSV
$ notion databases query db_123 --output csv > tasks.csv

# Query with complex filter
$ notion databases query db_123 \
  --filter-json '{
    "property": "Status",
    "select": {
      "equals": "Done"
    }
  }'
```

#### Search
```bash
# Search all pages
$ notion search pages "project planning"

# Search with limit
$ notion search all "deploy" --limit 5

# Search specific types
$ notion search databases "tasks"
```

#### Blocks
```bash
# Create paragraph block
$ notion blocks create \
  --parent page_123 \
  --type paragraph \
  --text "Project started"

# Create to-do block
$ notion blocks create \
  --parent page_123 \
  --type todo \
  --text "Review code" \
  --checked

# List child blocks
$ notion blocks children page_123 --output table
```

### Automation Examples

#### Backup Script
```bash
#!/bin/bash
# backup_notion.sh

DATE=$(date +%Y%m%d)
BACKUP_DIR="/backups/notion/$DATE"
mkdir -p "$BACKUP_DIR"

# Backup all databases
notion databases list --output json | \
  jq -r '.[].id' | \
  while read db_id; do
    name=$(notion databases get "$db_id" | jq -r '.title')
    notion databases query "$db_id" --output json \
      > "$BACKUP_DIR/${name}.json"
  done

echo "✅ Backup complete: $BACKUP_DIR"
```

#### CI/CD Integration
```bash
#!/bin/bash
# ci_deploy.sh

# Log deploy start
PAGE_ID=$(notion pages create \
  --parent deploy_db \
  --title "Deploy $(date +%Y-%m-%d_%H%M%S)")

notion blocks create \
  --parent "$PAGE_ID" \
  --text "Build started"

# Run tests
if pytest; then
  notion blocks create \
    --parent "$PAGE_ID" \
    --text "✅ Tests passed"
else
  notion blocks create \
    --parent "$PAGE_ID" \
    --text "❌ Tests failed"
  exit 1
fi

# Deploy...
```

---

## Implementation Plan

### Phase 1: Infrastructure (Week 1)

**Goals:**
- Set up project structure
- Implement configuration management
- Create output formatters
- Add CLI dependencies

**Tasks:**
- [ ] Add `typer`, `rich`, `questionary`, `pyperclip` to dependencies
- [ ] Create `better_notion/_cli/` module
- [ ] Implement `config.py` (Config class, load/save)
- [ ] Implement `output.py` (OutputFormatter)
- [ ] Implement `utils/async_helper.py` (run_async)
- [ ] Create entry point in `pyproject.toml`
- [ ] Write tests for infrastructure
- [ ] Update README with CLI installation instructions

**Deliverable:** Working CLI skeleton with `notion --help`

---

### Phase 2: Authentication (Week 1-2)

**Goals:**
- Implement authentication commands
- Secure token storage
- Validate credentials

**Tasks:**
- [ ] Implement `commands/auth.py`
  - [ ] `notion auth login` command
  - [ ] `notion auth status` command
  - [ ] `notion auth logout` command
- [ ] Add token validation (test API call)
- [ ] Implement secure file permissions (~/.notion/config.json)
- [ ] Write tests for auth commands
- [ ] Document authentication flow

**Deliverable:** Users can configure and authenticate CLI

---

### Phase 3: Pages Commands (Week 2-3)

**Goals:**
- Implement core page operations
- Support all output formats
- Interactive mode

**Tasks:**
- [ ] Implement `commands/pages.py`
  - [ ] `notion pages get <id>`
  - [ ] `notion pages create`
  - [ ] `notion pages list`
  - [ ] `notion pages update <id>`
  - [ ] `notion pages delete <id>`
  - [ ] `notion pages search <query>`
- [ ] Add `--parent`, `--title`, `--property` options
- [ ] Implement interactive mode with questionary
- [ ] Add property builders for CLI
- [ ] Write tests for pages commands
- [ ] Document pages commands

**Deliverable:** Complete page management from CLI

---

### Phase 4: Databases Commands (Week 3-4)

**Goals:**
- Implement database operations
- Support complex queries
- Export capabilities

**Tasks:**
- [ ] Implement `commands/databases.py`
  - [ ] `notion databases get <id>`
  - [ ] `notion databases query <id>`
  - [ ] `notion databases list`
- [ ] Add `--filter`, `--sort`, `--limit` options
- [ ] Support `--filter-json` for complex filters
- [ ] Implement CSV export
- [ ] Write tests for database commands
- [ ] Document database commands

**Deliverable:** Database querying and export

---

### Phase 5: Blocks, Users, Comments (Week 4-5)

**Goals:**
- Implement remaining entity commands
- Complete feature parity

**Tasks:**
- [ ] Implement `commands/blocks.py`
- [ ] Implement `commands/users.py`
- [ ] Implement `commands/comments.py`
- [ ] Write tests for all commands
- [ ] Document all commands

**Deliverable:** Full CRUD for all Notion entities

---

### Phase 6: Search & Advanced Features (Week 5-6)

**Goals:**
- Implement global search
- Add advanced features
- Polish user experience

**Tasks:**
- [ ] Implement `commands/search.py`
- [ ] Add progress bars for long operations
- [ ] Implement clipboard support (copy IDs)
- [ ] Add shell completion (bash/zsh/fish)
- [ ] Add aliases for common commands
- [ ] Implement configuration file validation
- [ ] Add `--verbose` and `--quiet` flags
- [ ] Write tests

**Deliverable:** Production-ready CLI

---

### Phase 7: Documentation & Polish (Week 6-7)

**Goals:**
- Complete documentation
- Fix bugs
- Prepare release

**Tasks:**
- [ ] Write `/docs/cli/installation.md`
- [ ] Write `/docs/cli/getting-started.md`
- [ ] Write `/docs/cli/commands.md` (reference)
- [ ] Write `/docs/cli/examples.md`
- [ ] Add video tutorials (optional)
- [ ] Fix bugs from testing
- [ ] Update main README
- [ ] Prepare changelog for v0.4.0

**Deliverable:** Complete CLI documentation

---

### Phase 8: Testing & Release (Week 7-8)

**Goals:**
- Comprehensive testing
- Beta testing
- Release v0.4.0

**Tasks:**
- [ ] Run full test suite
- [ ] Test on Python 3.10, 3.11, 3.12, 3.13
- [ ] Test on Linux, macOS, Windows
- [ ] Beta testing with community
- [ ] Fix reported issues
- [ ] Tag and release v0.4.0
- [ ] Publish to PyPI
- [ ] Announce release

**Deliverable:** CLI v0.4.0 release

---

## Testing Strategy

### Test Structure

```
tests/cli/
├── conftest.py              # Shared fixtures
├── test_commands.py         # Command tests
├── test_output.py           # Output formatter tests
├── test_config.py           # Configuration tests
└── fixtures/
    ├── mock_responses.json  # Mock API responses
    └── test_config.json     # Test configuration
```

### Unit Tests

Test individual functions and components:

```python
# tests/cli/test_config.py
import pytest
from better_notion._cli.config import Config

def test_config_load(tmp_path):
    """Test loading configuration from file"""
    config_file = tmp_path / "config.json"
    config_file.write_text('{"token": "secret_test"}')

    # Mock ~/.notion/config.json path
    with patch.object(Path, "home", return_value=tmp_path):
        config = Config.load()
        assert config.token == "secret_test"

def test_config_save(tmp_path):
    """Test saving configuration"""
    with patch.object(Path, "home", return_value=tmp_path):
        config = Config.save(token="secret_new")

        assert config.token == "secret_new"
        assert (tmp_path / ".notion" / "config.json").exists()
```

### Integration Tests

Test complete command flows:

```python
# tests/cli/test_commands.py
from typer.testing import CliRunner
from better_notion._cli.main import app

runner = CliRunner()

def test_pages_get_valid():
    """Test 'notion pages get' with valid ID"""
    result = runner.invoke(app, ["pages", "get", "page_abc123"])
    assert result.exit_code == 0
    assert "title" in result.stdout

def test_pages_get_invalid():
    """Test 'notion pages get' with invalid ID"""
    result = runner.invoke(app, ["pages", "get", "invalid_id"])
    assert result.exit_code != 0
    assert "not found" in result.stdout.lower()

def test_pages_create_missing_title():
    """Test 'notion pages create' without title"""
    result = runner.invoke(app, ["pages", "create"])
    assert result.exit_code == 2  # Typer validation error
    assert "missing" in result.stdout.lower()
```

### Mock API Responses

```python
# tests/cli/conftest.py
import pytest
from unittest.mock import AsyncMock, patch

@pytest.fixture
def mock_notion_client():
    """Mock NotionClient with predefined responses"""
    client = AsyncMock()

    # Mock page get
    client.pages.get.return_value = {
        "id": "page_abc",
        "title": "Test Page"
    }

    # Mock page create
    client.pages.create.return_value = {
        "id": "page_xyz",
        "title": "New Page"
    }

    return client
```

### End-to-End Tests

Test with real Notion API (optional):

```python
# tests/cli/test_e2e.py
import pytest
from better_notion import NotionClient

@pytest.mark.e2e
def test_pages_get_real():
    """Test with real Notion API"""
    import os

    token = os.getenv("NOTION_TOKEN")
    if not token:
        pytest.skip("NOTION_TOKEN not set")

    async with NotionClient(auth=token) as client:
        page = await client.pages.get("real_page_id")
        assert page["id"] == "real_page_id"
```

### Test Coverage Goals

- **Unit Tests**: 90%+ coverage for CLI code
- **Integration Tests**: All command flows
- **E2E Tests**: Optional, for smoke testing

---

## Documentation

### Documentation Structure

```
docs/cli/
├── installation.md         # How to install CLI
├── getting-started.md      # First steps
├── commands/
│   ├── auth.md            # Authentication commands
│   ├── pages.md           # Page commands
│   ├── databases.md       # Database commands
│   ├── blocks.md          # Block commands
│   ├── users.md           # User commands
│   ├── comments.md        # Comment commands
│   └── search.md          # Search commands
├── configuration.md       # Advanced configuration
├── output-formats.md      # Output format reference
├── examples.md            # Real-world examples
└── troubleshooting.md     # Common issues
```

### Installation Guide

```markdown
# Installing the Better Notion CLI

## Prerequisites

- Python 3.10 or higher
- A Notion integration token ([get one here](https://notion.so/my-integrations))

## Install with pip

\`\`\`bash
pip install better-notion[cli]
\`\`\`

## Verify Installation

\`\`\`bash
$ notion --version
Better Notion CLI v0.4.0
\`\`\`

## First Time Setup

\`\`\`bash
$ notion auth login
\`\`\`
```

### Command Reference

Auto-generated from docstrings:

```bash
$ notion pages --help
```

Should output:
```
Usage: notion pages [OPTIONS] COMMAND [ARGS]...

  Page operations

Options:
  --help  Show this message and exit.

Commands:
  create     Create a new page
  delete     Delete a page
  get        Get a page by ID
  list       List pages from a database
  search     Search for pages
  update     Update a page
```

### Examples Documentation

Real-world examples organized by use case:

```markdown
# CLI Examples

## Automation

### Backup Your Workspace

\`\`\`bash
#!/bin/bash
# Backup all databases

notion databases list --output json | \
  jq -r '.[].id' | \
  while read db_id; do
    notion databases query "$db_id" --output json > "backup/$db_id.json"
  done
\`\`\`

## CI/CD Integration

### Log Deploys to Notion

\`\`\`bash
notion pages create \
  --parent deploy_db \
  --title "Deploy $(date)" \
  --property "Status:In Progress"
\`\`\`
```

---

## Success Metrics

### Technical Metrics

- [ ] **Code Coverage**: >90% for CLI code
- [ ] **Type Checking**: 100% type annotated, passes mypy
- [ ] **Test Suite**: All tests passing (pytest)
- [ ] **Performance**: Commands complete in <2s (local), <5s (network)
- [ ] **Compatibility**: Works on Python 3.10, 3.11, 3.12, 3.13, 3.14
- [ ] **Platform Support**: Linux, macOS, Windows

### User Experience Metrics

- [ ] **Onboarding**: New user can run first command in <5 minutes
- [ ] **Documentation**: All commands documented with examples
- [ ] **Error Messages**: Clear, actionable errors
- [ ] **Auto-completion**: Shell completion available for bash/zsh/fish
- [ ] **Help Text**: `--help` provides all necessary information

### Adoption Metrics

- [ ] **Installation**: CLI can be installed via `pip install better-notion[cli]`
- [ ] **Usage**: All common operations can be performed via CLI
- [ ] **Parity**: CLI covers 80%+ of SDK functionality

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| **Async complexity** | Medium | Use `run_async` wrapper; keep async logic simple |
| **Dependency bloat** | Low | Make CLI optional dependency `[cli]` |
| **Token security** | High | Secure file permissions (600); warn user |
| **Cross-platform issues** | Medium | Test on Linux/macOS/Windows; use pathlib |
| **Maintenance burden** | Medium | Keep CLI thin; business logic in SDK |
| **User confusion** | Low | Clear documentation; helpful error messages |

---

## Future Enhancements

### Potential Features (Post-v0.4.0)

- [ ] **Shell Plugin**: Direct shell integration (like `kubectl`)
- [ ] **Interactive Mode**: REPL-style interface
- [ ] **Batch Operations**: Execute multiple commands in one call
- [ ] **Configuration Profiles**: Multiple workspaces/tokens
- [ ] **Webhooks CLI**: Manage webhook subscriptions
- [ ] **Sync Commands**: Bidirectional sync with local files
- [ ] **GUI Mode**: TUI mode with textual (curses-like interface)

### Community Contributions

- [ ] Plugin system for custom commands
- [ ] Command templates/snippets
- [ ] Third-party integrations

---

## Conclusion

This CLI proposal provides a comprehensive plan for adding a powerful, user-friendly command-line interface to Better Notion. The design prioritizes:

1. **Developer Experience**: Type-safe, modern, intuitive
2. **Maintainability**: Thin CLI layer, business logic in SDK
3. **Extensibility**: Easy to add new commands
4. **Performance**: Async operations, caching
5. **Documentation**: Comprehensive guides and examples

**Next Steps:**

1. Review and approve this proposal
2. Create GitHub project board for implementation phases
3. Begin Phase 1 (Infrastructure)
4. Target release: v0.4.0

**Questions or Feedback?**

Please open a GitHub discussion or issue for any questions about this proposal.

---

## References

- [Typer Documentation](https://typer.tiangolo.com/)
- [Rich Documentation](https://rich.readthedocs.io/)
- [Notion API Documentation](https://developers.notion.com/reference)
- [Click Documentation](https://click.palletsprojects.com/)
- [Python Packaging Guide](https://packaging.python.org/)

---

**Document Version:** 1.0
**Last Updated:** 2025-01-25
**Status:** Ready for Review
