# Documentation Page Standards & Structure Guide

This guide defines the standards, templates, and best practices for creating high-quality documentation pages for the Better Notion SDK.

## Table of Contents

1. [Universal Page Template](#universal-page-template)
2. [Page Type Structures](#page-type-structures)
3. [Mandatory Quality Elements](#mandatory-quality-elements)
4. [Writing Standards](#writing-standards)
5. [Code Conventions](#code-conventions)
6. [Quality Checklist](#quality-checklist)
7. [Global Navigation Structure](#global-navigation-structure)

---

## Universal Page Template

Every documentation page should follow this base structure:

```mdx
---
title: Clear Page Title
description: Action-oriented description (50-160 characters)
icon: IconName (optional)
---

<!-- Context Section -->
<Callout type="info">
  Quick context or prerequisite information
</Callout>

<!-- Overview -->
Brief paragraph explaining what this page covers and why it matters.

<!-- Main Content -->
## Section 1
Content...

## Section 2
Content...

<!-- Examples -->
## Examples

### Example 1: Descriptive Title
Description + complete, runnable code

<!-- Related Content -->
<Callout type="info">
  **See also**: [Related Page](path/to/page)
</Calloint>
```

### Frontmatter Requirements

Every page MUST have:

```yaml
---
title: "Clear, Descriptive Title"        # Required
description: "Action-oriented what/why"  # Required (50-160 chars)
icon: "IconName"                         # Optional (for sidebar)
---
```

**Title Guidelines:**
- Use clear, descriptive names
- Match the feature/functionality name
- Avoid "How to" - just name the topic
- Examples: "Working with Pages", "Authentication", "Error Handling"

**Description Guidelines:**
- Start with a verb (Learn, Build, Configure, etc.)
- Explain WHAT the user will accomplish
- Keep between 50-160 characters (SEO best practice)
- Examples:
  - ✅ "Learn how to create, read, update, and delete Notion pages"
  - ❌ "This page is about pages"
  - ❌ "A comprehensive guide to page operations in the Better Notion SDK for Python"

---

## Page Type Structures

### 1. Getting Started Page

**Goal:** Get user from zero to first success in 5 minutes.

**Template:**

```mdx
---
title: Getting Started
description: Get up and running with Better Notion in 5 minutes
---

## What You'll Learn

In this guide, you'll:
- Install the SDK
- Configure authentication
- Make your first API call
- Understand basic concepts

## Prerequisites

Before starting, ensure you have:

<Steps>
  <Step>
    ### Python 3.10+

    Check your version:
    ```bash
    python --version
    ```
  </Step>
  <Step>
    ### Notion Integration

    Create an integration at [notion.so/my-integrations](https://notion.so/my-integrations)
  </Step>
  <Step>
    ### API Token

    Copy your integration token (starts with `secret_`)
  </Step>
</Steps>

## Installation

<Callout type="info">
  **Recommended**: Use a virtual environment
</Callout>

```bash
pip install better-notion
```

## Quick Example

Create a file `main.py`:

```python
import asyncio
from better_notion import NotionAPI

async def main():
    async with NotionAPI(auth="secret_...") as api:
        # Get a page
        page = await api.pages.get("page_id")
        print(page.properties)

        # List database pages
        async for page in api.pages.iterate("database_id"):
            print(page.id)

asyncio.run(main())
```

## Next Steps

- Learn [Basic Concepts](basic-concepts)
- Explore [Guides](../guides)
- Check [Examples](../examples)
```

**Key Elements:**
- "What You'll Learn" bullet list
- Prerequisites in `<Steps>` component
- Minimal, working example
- Clear next steps

---

### 2. Guide Page (Task-Based)

**Goal:** Teach user how to accomplish a specific task.

**Template:**

```mdx
---
title: Working with Pages
description: Learn how to create, read, update, and delete Notion pages
---

<Callout type="info">
  This guide covers the Page entity operations. For block manipulation, see [Working with Blocks](working-with-blocks).
</Callout>

## Overview

The Page entity represents a Notion page with full CRUD operations. You can retrieve, create, update, and delete pages programmatically.

## Retrieving Pages

### Get a Single Page

Retrieve a page by its ID:

```python
page = await api.pages.get("page_id")
```

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `page_id` | `str` | Yes | The page identifier |

**Returns:** `Page` entity

**Raises:** `NotFoundError` if the page doesn't exist or integration lacks access

### List Pages in a Database

List all pages in a database:

```python
pages = await api.pages.list("database_id")

for page in pages:
    print(page.id)
```

<Callout type="warning">
  `list()` only returns the first page of results. Use `iterate()` for large datasets.
</Callout>

### Iterate Over All Pages

Memory-efficient iteration over large datasets:

```python
async for page in api.pages.iterate("database_id"):
    print(page.id)
```

## Updating Pages

Update pages in two steps:

<Steps>
  <Step>
    ### Retrieve the page

    ```python
    page = await api.pages.get("page_id")
    ```
  </Step>
  <Step>
    ### Update properties locally

    ```python
    from better_notion._api.properties import Select

    await page.update(**Select("Status", "Done").build())
    ```
  </Step>
  <Step>
    ### Save changes to Notion

    ```python
    await page.save()
    ```
  </Step>
</Steps>

<Callout type="warning">
  Changes are NOT persisted to Notion until you call `save()`.
</Callout>

## Deleting Pages

Archive a page (Notion doesn't support permanent deletion):

```python
await page.delete()
```

## Complete Example

```python
from better_notion import NotionAPI
from better_notion._api.properties import Title, Select

async def manage_task():
    async with NotionAPI(auth="secret_...") as api:
        # Get a task
        task = await api.pages.get("page_id")

        # Update status
        await task.update(**Select("Status", "In Progress").build())

        # Save to Notion
        await task.save()

        print(f"Task updated: {task.id}")

asyncio.run(manage_task())
```

## Common Patterns

### Update Multiple Properties

```python
await page.update(
    **Title("New Title").build(),
    **Select("Status", "Done").build(),
    **Select("Priority", "High").build()
)
await page.save()
```

### Update Without Retrieving First

<Callout type="info">
  You can update pages without retrieving them first by using the API directly.
</Callout>

```python
await api.pages.update(
    page_id="page_id",
    properties={
        **Select("Status", "Done").build()
    }
)
```

## Troubleshooting

### Error: Page not found

**Problem:** `NotFoundError: Page not found`

**Solutions:**
- Verify the page ID is correct
- Check integration has access to the page
- Ensure page is not in a restricted workspace

### Changes not saving

**Problem:** Updated properties don't appear in Notion

**Solutions:**
- Ensure you called `await page.save()` after `update()`
- Check for validation errors in the response
- Verify property names match your database schema

## See Also

- [Property Builders](property-builders) - Build type-safe properties
- [Working with Blocks](working-with-blocks) - Manipulate content
- [Error Handling](error-handling) - Handle exceptions properly
```

**Key Elements:**
- Overview explaining WHAT and WHY
- Code examples for each operation
- Parameter tables
- `<Steps>` for multi-step processes
- `<Callout>` for warnings and tips
- "Common Patterns" section
- "Troubleshooting" section
- "See Also" links

---

### 3. API Reference Page

**Goal:** Complete technical reference for developers.

**Template:**

```mdx
---
title: Page Entity
description: Complete API reference for the Page entity
---

<Callout type="info">
  This is the complete API reference. For a gentler introduction, see [Working with Pages](../guides/working-with-pages).
</Callout>

## Overview

The `Page` entity represents a Notion page with CRUD operations. It provides methods for retrieving, updating, saving, and deleting pages.

## Class Definition

```python
class Page:
    def __init__(self, api: NotionAPI, data: dict[str, Any]) -> None: ...
```

## Constructor

### `Page(api, data)`

Create a Page instance from API response data.

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `api` | `NotionAPI` | Yes | The API client instance |
| `data` | `dict[str, Any]` | Yes | Raw page data from Notion API |

**Example:**

```python
from better_notion import NotionAPI
from better_notion._api.entities import Page

api = NotionAPI(auth="secret_...")
raw_data = await api._request("GET", "/pages/page_id")
page = Page(api, raw_data)
```

---

## Properties

| Property | Type | Description |
|----------|------|-------------|
| `id` | `str` | Unique page identifier |
| `created_time` | `datetime` | Creation timestamp |
| `last_edited_time` | `datetime` | Last edit timestamp |
| `archived` | `bool` | Whether the page is archived |
| `parent` | `dict` | Parent object (database or page) |
| `properties` | `dict` | Page properties |
| `blocks` | `BlockCollection` | Children blocks collection |

**Example:**

```python
page = await api.pages.get("page_id")

print(f"Page ID: {page.id}")
print(f"Created: {page.created_time}")
print(f"Archived: {page.archived}")
```

---

## Methods

### `update(**kwargs)`

Update page properties locally (not persisted to Notion).

```python
async def update(**kwargs: Any) -> None
```

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `**kwargs` | `Any` | No | Property updates in request format |

**Raises:**
- `ValidationError`: If properties are invalid

**Example:**

```python
from better_notion._api.properties import Select

await page.update(**Select("Status", "Done").build())
```

<Callout type="warning">
  This only updates the local object. Call `save()` to persist changes.
</Callout>

---

### `save()`

Save modified properties to Notion.

```python
async def save() -> None
```

**Raises:**
- `NotFoundError`: If the page no longer exists
- `ValidationError`: If properties are invalid

**Example:**

```python
await page.update(**Title("New Title").build())
await page.save()  # Persist to Notion
```

<Callout type="tip">
  Only modified properties are sent to Notion. Unchanged properties are omitted from the request.
</Callout>

---

### `delete()`

Archive the page (Notion doesn't support permanent deletion).

```python
async def delete() -> None
```

**Raises:**
- `NotFoundError`: If the page no longer exists

**Example:**

```python
await page.delete()
```

<Callout type="warning">
  This archives the page. To permanently delete, use the Notion UI.
</Callout>

---

### `reload()`

Reload page data from Notion, discarding local changes.

```python
async def reload() -> None
```

**Raises:**
- `NotFoundError`: If the page no longer exists

**Example:**

```python
await page.reload()
```

<Callout type="info">
  This resets any unsaved changes made via `update()`.
</Callout>

---

## Complete Type Definition

```python
class Page:
    """Represents a Notion page."""

    def __init__(self, api: NotionAPI, data: dict[str, Any]) -> None:
        """Initialize a Page entity."""
        ...

    @property
    def id(self) -> str:
        """Get the page ID."""
        ...

    @property
    def created_time(self) -> datetime:
        """Get the creation time."""
        ...

    @property
    def last_edited_time(self) -> datetime:
        """Get the last edited time."""
        ...

    @property
    def archived(self) -> bool:
        """Check if page is archived."""
        ...

    @property
    def properties(self) -> dict[str, Any]:
        """Get the page properties."""
        ...

    @property
    def blocks(self) -> BlockCollection:
        """Get blocks collection for this page."""
        ...

    async def update(self, **kwargs: Any) -> None:
        """Update page properties locally."""
        ...

    async def save(self) -> None:
        """Save changes to Notion."""
        ...

    async def delete(self) -> None:
        """Archive this page."""
        ...

    async def reload(self) -> None:
        """Reload page data from Notion."""
        ...

    def __repr__(self) -> str:
        """String representation."""
        ...
```

## Usage Example

```python
import asyncio
from better_notion import NotionAPI
from better_notion._api.properties import Title, Select

async def page_lifecycle():
    async with NotionAPI(auth="secret_...") as api:
        # Retrieve
        page = await api.pages.get("page_id")
        print(f"Retrieved: {page.id}")

        # Update
        await page.update(**Select("Status", "In Progress").build())

        # Save
        await page.save()
        print("Saved")

        # Reload
        await page.reload()
        print("Reloaded")

        # Delete
        await page.delete()
        print("Archived")

asyncio.run(page_lifecycle())
```

## See Also

- [PageCollection](../collections/page-collection) - Collection methods
- [Block Entity](block) - Block entity reference
- [Property Builders](../properties/title) - Property types
```

**Key Elements:**
- Clear separation: Constructor → Properties → Methods
- Parameter tables for each method
- Return types and raised exceptions
- Code examples for each method
- Complete type definition
- Usage example showing full lifecycle

---

### 4. Example Page (Real-World Use Case)

**Goal:** Complete, runnable example solving a real problem.

**Template:**

```mdx
---
title: Build a Task Manager
description: Learn how to build a task manager with Better Notion
---

<Callout type="success">
  **Time**: ~30 minutes | **Difficulty**: Beginner | **Topics**: Pages, Properties, Databases
</Callout>

## What We'll Build

A simple task manager application with:
- Tasks database in Notion
- Create new tasks
- Update task status
- List and filter tasks
- Mark tasks as complete

**Final result:**

```python
# A complete CLI task manager
python task_manager.py create "Review PR #123"
python task_manager.py list
python task_manager.py complete "page_id"
```

## Prerequisites

- Completed [Quick Start](../quickstart)
- Python 3.10+
- Notion integration with database access
- Basic understanding of async/await

## Step 1: Set Up the Database

Create a Notion database with these properties:

| Property | Type | Name | Options |
|----------|------|------|---------|
| Title | Title | Task | - |
| Status | Select | Status | To Do, In Progress, Done |
| Priority | Select | Priority | Low, Medium, High |

<Callout type="tip">
  Copy the **Database ID** from the URL: `notion.so/workspace/DATABASE_ID?v=...`
</Callout>

## Step 2: Project Setup

Create a new project:

```bash
mkdir task_manager
cd task_manager

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install dependencies
pip install better-notion python-dotenv
```

Create `.env`:

```env
NOTION_TOKEN=secret_your_token_here
DATABASE_ID=your_database_id_here
```

## Step 3: Basic Implementation

Create `task_manager.py`:

```python
import asyncio
import os
from better_notion import NotionAPI
from better_notion._api.properties import Title, Select
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

NOTION_TOKEN = os.getenv("NOTION_TOKEN")
DATABASE_ID = os.getenv("DATABASE_ID")

async def create_task(title: str, priority: str = "Medium"):
    """Create a new task."""
    api = NotionAPI(auth=NOTION_TOKEN)

    task = await api.pages.create(
        parent={"database_id": DATABASE_ID},
        properties={
            **Title(title).build(),
            **Select("Status", "To Do").build(),
            **Select("Priority", priority).build()
        }
    )

    await api.close()
    return task

async def list_tasks():
    """List all tasks."""
    api = NotionAPI(auth=NOTION_TOKEN)

    tasks = await api.pages.list(DATABASE_ID)

    for task in tasks:
        status = task.properties["Status"]["select"]["name"]
        title = task.properties["Name"]["title"][0]["plain_text"]
        print(f"[{status}] {title}")

    await api.close()

async def complete_task(page_id: str):
    """Mark a task as complete."""
    api = NotionAPI(auth=NOTION_TOKEN)

    task = await api.pages.get(page_id)
    await task.update(**Select("Status", "Done").build())
    await task.save()

    await api.close()
```

## Step 4: Add CLI Interface

```python
import sys

async def main():
    command = sys.argv[1] if len(sys.argv) > 1 else "list"

    if command == "create":
        title = sys.argv[2]
        task = await create_task(title)
        print(f"✅ Created task: {task.id}")

    elif command == "list":
        await list_tasks()

    elif command == "complete":
        page_id = sys.argv[2]
        await complete_task(page_id)
        print(f"✅ Task completed")

    else:
        print("Unknown command")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
```

## Step 5: Test It

```bash
# Create tasks
python task_manager.py create "Fix bug in auth"
python task_manager.py create "Write documentation"

# List tasks
python task_manager.py list
# Output:
# [To Do] Fix bug in auth
# [To Do] Write documentation

# Complete a task
python task_manager.py complete PAGE_ID
```

## Expected Output

```
✅ Created task: 5c6a28216bb14a7eb6e1c50111515c3d
[To Do] Fix bug in auth
[To Do] Write documentation
[In Progress] Review PR #123
✅ Task completed
```

## Extensions

### Add Due Dates

```python
from better_notion._api.properties import Date

async def create_task_with_due_date(title: str, due_date: str):
    """Create a task with a due date."""
    api = NotionAPI(auth=NOTION_TOKEN)

    task = await api.pages.create(
        parent={"database_id": DATABASE_ID},
        properties={
            **Title(title).build(),
            **Select("Status", "To Do").build(),
            **Date("Due Date", due_date).build()
        }
    )

    await api.close()
    return task
```

### Add Description

```python
from better_notion._api.properties import Text

await page.update(
    **Text("Description", "Task details...").build()
)
```

### Filter by Status

```python
async def list_tasks_by_status(status: str):
    """List tasks filtered by status."""
    # Note: This requires database query with filter
    # See Querying Databases guide
    pass
```

## Full Source Code

<details>
<summary>task_manager.py (complete)</summary>

```python
import asyncio
import os
import sys
from better_notion import NotionAPI
from better_notion._api.properties import Title, Select, Text, Date
from dotenv import load_dotenv

load_dotenv()

NOTION_TOKEN = os.getenv("NOTION_TOKEN")
DATABASE_ID = os.getenv("DATABASE_ID")

async def create_task(title: str, priority: str = "Medium", due_date: str = None):
    """Create a new task."""
    api = NotionAPI(auth=NOTION_TOKEN)

    properties = {
        **Title(title).build(),
        **Select("Status", "To Do").build(),
        **Select("Priority", priority).build()
    }

    if due_date:
        properties.update(**Date("Due Date", due_date).build())

    task = await api.pages.create(
        parent={"database_id": DATABASE_ID},
        properties=properties
    )

    await api.close()
    return task

async def list_tasks():
    """List all tasks."""
    api = NotionAPI(auth=NOTION_TOKEN)

    tasks = await api.pages.list(DATABASE_ID)

    print("\n📋 Tasks:")
    for task in tasks:
        status = task.properties["Status"]["select"]["name"]
        title = task.properties["Name"]["title"][0]["plain_text"]
        print(f"  [{status}] {title}")

    await api.close()

async def update_status(page_id: str, status: str):
    """Update task status."""
    api = NotionAPI(auth=NOTION_TOKEN)

    task = await api.pages.get(page_id)
    await task.update(**Select("Status", status).build())
    await task.save()

    await api.close()

async def main():
    if len(sys.argv) < 2:
        print("Usage: python task_manager.py <command> [args]")
        print("Commands:")
        print("  create <title> [priority]")
        print("  list")
        print("  complete <page_id>")
        sys.exit(1)

    command = sys.argv[1]

    if command == "create":
        title = sys.argv[2]
        priority = sys.argv[3] if len(sys.argv) > 3 else "Medium"
        task = await create_task(title, priority)
        print(f"✅ Created task: {task.id}")

    elif command == "list":
        await list_tasks()

    elif command == "complete":
        page_id = sys.argv[2]
        await update_status(page_id, "Done")
        print("✅ Task completed")

    else:
        print(f"Unknown command: {command}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
```
</details>

## Troubleshooting

### ImportError: No module named 'dotenv'

Install dependencies:
```bash
pip install python-dotenv
```

### NotFoundError: Database not found

Check:
- Database ID is correct
- Integration has access to the database
- Database is shared with integration

### Properties not updating

Ensure:
- Property names match database schema exactly
- Select options exist in database
- You're calling `save()` after `update()`

## What's Next

- Add task deletion command
- Implement status filtering with database queries
- Add task descriptions with Text property
- Build a web UI with FastAPI

## See Also

- [Working with Pages](../guides/working-with-pages)
- [Property Builders](../guides/property-builders)
- [Querying Databases](../guides/querying-databases)
- [Knowledge Base Example](knowledge-base)
```

**Key Elements:**
- Clear goal statement
- Prerequisites with difficulty/time estimate
- Numbered steps with `<Steps>` component
- Complete, runnable source code
- Expected output shown
- Extension ideas
- `<details>` for full code
- Troubleshooting section
- Next steps

---

## Mandatory Quality Elements

### Every Page MUST Have:

1. **Complete Frontmatter**
   ```yaml
   ---
   title: Clear Title
   description: Action-oriented description (50-160 chars)
   ---
   ```

2. **Immediate Context**
   - First paragraph explains WHAT and WHY
   - `<Callout>` for prerequisites or important warnings

3. **Runnable Code Examples**
   - All examples are complete and functional
   - Imports included
   - Error handling shown where relevant
   - Can be copy-pasted and run

4. **Parameter Tables**
   Standardized format for all parameters:

   | Parameter | Type | Required | Description |
   |-----------|------|----------|-------------|
   | `name` | `type` | Yes/No | Clear description |

5. **Internal Links**
   - Links to related pages
   - Links to prerequisite concepts
   - "See Also" section at bottom

### Every Page SHOULD Have:

1. **Complete Example** at the end of page
2. **Callouts** for warnings, tips, important notes
3. **Troubleshooting** section (for guides/examples)
4. **Next Steps** or related pages section

---

## Writing Standards

### Tone and Voice

**DO:**
- ✅ Use active voice: "Create a page" (not "A page is created")
- ✅ Be direct: "Use this method" (not "You should use this method")
- ✅ Be precise: Avoid "some", "various", "etc."
- ✅ Keep paragraphs short: One idea per paragraph
- ✅ Use present tense: "This method returns" (not "will return")

**DON'T:**
- ❌ Use passive voice: "Pages can be created"
- ❌ Be wordy: "In order to" → "To"
- ❌ Use vague terms: "some users", "various methods"
- ❌ Use future tense: "This will return"

### Headings

```
# (H1 - NEVER USE, frontmatter.title is H1)
## Section (H2 - Main sections)
### Subsection (H3 - Subsections)
#### Detail (H4 - Rarely used)
```

**Heading Guidelines:**
- Use verb-based headings for actions: "Creating Pages", "Updating Properties"
- Use noun-based headings for concepts: "Error Handling", "Authentication"
- Keep headings short and descriptive
- Don't use "Introduction" or "Conclusion" sections

### Lists

**Bullet Lists:**
- Use for unordered items
- Start with capital letter
- No periods for short items (< 1 sentence)
- Periods for long items (≥ 1 sentence)

**Numbered Lists:**
1. Use for sequential steps
2. Must be in order
3. Complete sentences with periods

**Definition Lists (Tables):**
Use tables for parameters, properties, return values.

### Code Blocks

**Good:**
```python
import asyncio
from better_notion import NotionAPI

async def get_page():
    api = NotionAPI(auth="secret_...")
    page = await api.pages.get("page_id")
    return page
```

**Bad:**
```python
# No imports
api = NotionAPI(auth="...")  # Incomplete
page = await api.pages.get("page_id")
```

### Links

**Internal Links:**
```mdx
[Working with Pages](../guides/working-with-pages)
```

**External Links:**
```mdx
[Notion API](https://developers.notion.com)
```

**Reference Links:**
```mdx
See the [Page entity](../api/entities/page) for details.
```

---

## Code Conventions

### Python Code Style

All Python examples MUST follow:

**Docstrings:**
```python
async def get_page(api: NotionAPI, page_id: str) -> Page:
    """Get a page by ID.

    Args:
        api: The NotionAPI client instance.
        page_id: The page identifier.

    Returns:
        The Page entity.

    Raises:
        NotFoundError: If page doesn't exist.
        UnauthorizedError: If token is invalid.
    """
    return await api.pages.get(page_id)
```

**Type Hints:**
```python
# ✅ GOOD
def process(page: Page) -> dict[str, Any]:
    pass

# ❌ BAD
def process(page):
    pass
```

**Imports:**
```python
# ✅ GOOD - Grouped and organized
import asyncio
import os
from datetime import datetime

from better_notion import NotionAPI
from better_notion._api.properties import Title, Select

# ❌ BAD - Unorganized
from better_notion import NotionAPI
import os
from better_notion._api.properties import Select
import asyncio
```

**Async/Await:**
```python
# ✅ GOOD - Shows proper async usage
async def main():
    async with NotionAPI(auth="secret_...") as api:
        page = await api.pages.get("page_id")
        return page

asyncio.run(main())
```

### Code Block Metadata

**Always add title when helpful:**

``````mdx
```python title="Create a task"
task = await api.pages.create(...)
```
``````

**Use line numbers for long examples:**
``````mdx
```python lineNumbers
line 1
line 2
line 3
```
``````

**Highlight specific lines:**
``````mdx
```python
api = NotionAPI(auth="secret_...")  # [!code highlight]
page = await api.pages.get("page_id")
```
``````

---

## Quality Checklist

Before marking a page as complete, verify:

### Content
- [ ] Frontmatter with title AND description
- [ ] First paragraph explains what the page covers
- [ ] All code examples are runnable
- [ ] Imports included in code examples
- [ ] Parameter tables for functions/methods
- [ ] Callouts for warnings and important notes
- [ ] Links to related pages
- [ ] "See Also" or "Next Steps" section

### Code Quality
- [ ] All examples tested manually
- [ ] No placeholder code
- [ ] Error handling shown where relevant
- [ ] Type hints included
- [ ] Docstrings for functions

### Links
- [ ] No broken internal links
- [ ] No broken external links
- [ ] All referenced pages exist
- [ ] Links use correct relative paths

### SEO
- [ ] Description between 50-160 characters
- [ ] Title is descriptive and clear
- [ ] Frontmatter is complete

### Accessibility
- [ ] Alt text for images (if any)
- [ ] Callout types used appropriately
- [ ] Code blocks have language specified
- [ ] Tables have proper headers

### Spelling & Grammar
- [ ] No spelling errors
- [ ] Consistent terminology
- [ ] Proper capitalization
- [ ] No trailing whitespace

---

## Global Navigation Structure

### Recommended Hierarchy

```
Home
├── Quick Start              # Get started in 5 min
├── Getting Started          # Foundation knowledge
│   ├── Installation
│   ├── Authentication
│   ├── Basic Concepts
│   └── Project Setup
├── Guides                   # Task-based tutorials
│   ├── Working with Pages
│   ├── Working with Blocks
│   ├── Querying Databases
│   ├── Search
│   ├── Property Builders
│   └── Error Handling
├── API Reference            # Complete technical docs
│   ├── Client
│   ├── Entities
│   │   ├── Page
│   │   ├── Block
│   │   ├── Database
│   │   └── User
│   ├── Collections
│   │   ├── PageCollection
│   │   ├── BlockCollection
│   │   ├── DatabaseCollection
│   │   └── UserCollection
│   ├── Properties
│   │   ├── Title
│   │   ├── Text
│   │   ├── Select
│   │   ├── Date
│   │   ├── Checkbox
│   │   ├── Number
│   │   └── URL
│   └── Exceptions
├── Examples                 # Real-world projects
│   ├── Task Manager
│   ├── Knowledge Base
│   ├── Automation
│   └── Migration
└── Advanced                 # Deep dives
    ├── Pagination
    ├── Async Patterns
    ├── Rate Limits
    └── Testing
```

### File Structure

```
website/content/docs/
├── index.mdx                          # Home / Overview
├── quickstart.mdx                     # Quick Start
├── getting-started/
│   ├── index.mdx                      # Getting Started overview
│   ├── installation.mdx
│   ├── authentication.mdx
│   ├── basic-concepts.mdx
│   └── project-setup.mdx
├── guides/
│   ├── index.mdx
│   ├── working-with-pages.mdx
│   ├── working-with-blocks.mdx
│   ├── querying-databases.mdx
│   ├── search.mdx
│   ├── property-builders.mdx
│   └── error-handling.mdx
├── api/
│   ├── index.mdx                      # API overview
│   ├── client.mdx
│   ├── entities/
│   │   ├── index.mdx
│   │   ├── page.mdx
│   │   ├── block.mdx
│   │   ├── database.mdx
│   │   └── user.mdx
│   ├── collections/
│   │   ├── index.mdx
│   │   ├── page-collection.mdx
│   │   ├── block-collection.mdx
│   │   ├── database-collection.mdx
│   │   └── user-collection.mdx
│   ├── properties/
│   │   ├── index.mdx
│   │   ├── title.mdx
│   │   ├── text.mdx
│   │   ├── select.mdx
│   │   ├── date.mdx
│   │   ├── checkbox.mdx
│   │   ├── number.mdx
│   │   └── url.mdx
│   └── exceptions.mdx
├── examples/
│   ├── index.mdx
│   ├── task-manager.mdx
│   ├── knowledge-base.mdx
│   ├── automation.mdx
│   └── migration.mdx
├── advanced/
│   ├── index.mdx
│   ├── pagination.mdx
│   ├── async-patterns.mdx
│   ├── rate-limits.mdx
│   └── testing.mdx
└── meta/
    ├── changelog.mdx                  # From CHANGELOG.md
    └── contributing.mdx
```

---

## Quick Reference Cards

### Callout Types

| Type | Usage |
|------|-------|
| `info` | General information, prerequisites |
| `warning` | Breaking changes, important warnings |
| `error` | Critical errors, deprecations |
| `success` | Completed states, achievements |
| `idea` | Tips, suggestions, best practices |

### Page Purpose Matrix

| Page Type | Goal | Audience | Length |
|-----------|------|----------|--------|
| Quick Start | First success in 5 min | New users | Short |
| Getting Started | Foundation knowledge | New users | Medium |
| Guide | Accomplish specific task | Users | Medium-Long |
| API Reference | Complete technical info | Developers | Long |
| Example | Real-world use case | Learners | Long |

### Content Flow

```
Home → Quick Start → Getting Started → Guides → API Reference
              ↓            ↓              ↓
           Examples ←←←←←←←←←←←←←←←←
```

---

This guide ensures consistent, high-quality documentation across all pages. Follow these standards when creating or updating documentation content.
