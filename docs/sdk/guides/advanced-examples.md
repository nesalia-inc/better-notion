# Advanced Examples

Advanced patterns and real-world use cases for the Better Notion SDK.

## Examples by Use Case

### 1. Task Management System

#### Setup

```python
from better_notion import NotionClient
from datetime import datetime, timedelta

client = NotionClient(auth=os.getenv("NOTION_KEY"))
```

#### Create Task with Due Date

```python
# Get tasks database
tasks_db = await client.databases.get("tasks_db_id")

# Create task with due date next week
next_week = datetime.now() + timedelta(days=7)

task = await client.pages.create(
    parent=tasks_db,
    title="Complete project documentation",
    status="Todo",
    priority=8,
    due_date=next_week.isoformat()
)

print(f"Created task: {task.url}")
```

#### Find Overdue Tasks

```python
from datetime import datetime

today = datetime.now().isoformat()

# Find tasks that are overdue or due today
overdue_tasks = await tasks_db.query(
    client=client,
    status__in=["Todo", "In Progress"],
    due_date__before=today
).collect()

for task in overdue_tasks:
    due = task.get_property("Due Date")
    print(f"OVERDUE: {task.title} (due {due})")
```

#### Weekly Task Report

```python
# Get this week's tasks
week_ago = (datetime.now() - timedelta(days=7)).isoformat()

recent_tasks = await tasks_db.query(
    client=client,
    created_time__after=week_ago
).collect()

# Group by status
by_status = {}
for task in recent_tasks:
    status = task.get_property("Status", default="No Status")
    by_status.setdefault(status, []).append(task)

# Print report
print("Weekly Task Report")
print("=" * 40)

for status, tasks in by_status.items():
    print(f"\n{status}: {len(tasks)}")
    for task in tasks:
        print(f"  - {task.title}")
```

### 2. Document Publishing System

#### Create Document with Structure

```python
async def create_document(parent_db, title, sections):
    """Create a structured document with multiple sections.

    Args:
        parent_db: Parent database
        title: Document title
        sections: List of (heading, content) tuples
    """
    # Create document page
    doc = await client.pages.create(
        parent=parent_db,
        title=title,
        status="Draft"
    )

    # Add each section
    for heading, content in sections:
        # Add heading
        await client.blocks.create_heading(
            parent=doc,
            text=heading,
            level=2
        )

        # Add content paragraph
        await client.blocks.create_paragraph(
            parent=doc,
            text=content
        )

    return doc

# Usage
doc = await create_document(
    parent_db=database,
    title="API Documentation",
    sections=[
        ("Introduction", "This API provides access to..."),
        ("Authentication", "Use your API key to authenticate..."),
        ("Rate Limits", "100 requests per minute..."),
    ]
)

print(f"Created: {doc.url}")
```

#### Export Page to Markdown

```python
async def page_to_markdown(page):
    """Convert page to markdown format.

    Args:
        page: Page object

    Returns:
        Markdown string
    """
    markdown = f"# {page.title}\n\n"

    async for block in page.children:
        if block.type == "paragraph":
            markdown += f"{block.text}\n\n"
        elif block.type == "heading_1":
            markdown += f"# {block.text}\n\n"
        elif block.type == "heading_2":
            markdown += f"## {block.text}\n\n"
        elif block.type == "heading_3":
            markdown += f"### {block.text}\n\n"
        elif block.type == "code":
            markdown += f"```{block.language}\n{block.code}\n```\n\n"
        elif block.type == "quote":
            markdown += f"> {block.text}\n\n"
        elif block.type == "to_do":
            checked = "x" if block.checked else " "
            markdown += f"- [{checked}] {block.text}\n\n"
        elif block.type == "divider":
            markdown += "---\n\n"

    return markdown

# Usage
page = await client.pages.get(page_id)
markdown = await page_to_markdown(page)

# Save to file
with open("export.md", "w") as f:
    f.write(markdown)

print("Exported to export.md")
```

### 3. Meeting Notes System

#### Create Meeting Template

```python
async def create_meeting_notes(db, title, attendees, date):
    """Create a meeting notes page from template.

    Args:
        db: Database to create page in
        title: Meeting title
        attendees: List of user IDs
        date: Meeting date
    """
    # Create page
    meeting = await client.pages.create(
        parent=db,
        title=f"Meeting: {title}",
        date=date.isoformat(),
        status="Notes"
    )

    # Add structure
    await client.blocks.create_heading(parent=meeting, text="Attendees", level=2)
    await client.blocks.create_bullet(
        parent=meeting,
        text=", ".join(attendees)
    )

    await client.blocks.create_heading(parent=meeting, text="Agenda", level=2)
    await client.blocks.create_to_do(parent=meeting, text="Add agenda items")

    await client.blocks.create_heading(parent=meeting, text="Notes", level=2)
    await client.blocks.create_paragraph(
        parent=meeting,
        text="Meeting notes go here..."
    )

    await client.blocks.create_heading(parent=meeting, text="Action Items", level=2)

    return meeting

# Usage
meeting = await create_meeting_notes(
    db=database,
    title="Weekly Standup",
    attendees=["user_1", "user_2"],
    date=datetime.now()
)
```

#### Extract Action Items

```python
async def find_action_items(page):
    """Find all unchecked todos in page.

    Args:
        page: Page to search

    Returns:
        List of todo blocks
    """
    action_items = []

    async for block in page.descendants():
        if block.type == "to_do" and not block.checked:
            action_items.append(block)

    return action_items

# Usage
page = await client.pages.get(page_id)
actions = await find_action_items(page)

print(f"Found {len(actions)} action items:")
for item in actions:
    print(f"  - {item.text}")
```

### 4. Content Migration

#### Copy Page Structure

```python
async def copy_page(source_page, target_parent):
    """Copy a page and all its blocks to a new parent.

    Args:
        source_page: Page to copy
        target_parent: Parent database or page

    Returns:
        New page object
    """
    # Create new page
    new_page = await client.pages.create(
        parent=target_parent,
        title=f"Copy of {source_page.title}"
    )

    # Copy all blocks
    async for block in source_page.children:
        if block.type == "paragraph":
            await client.blocks.create_paragraph(
                parent=new_page,
                text=block.text
            )
        elif block.type == "to_do":
            await client.blocks.create_todo(
                parent=new_page,
                text=block.text,
                checked=block.checked
            )
        elif block.type == "code":
            await client.blocks.create_code(
                parent=new_page,
                code=block.code,
                language=block.language
            )
        # Add more block types as needed...

    return new_page

# Usage
source = await client.pages.get(source_page_id)
target_db = await client.databases.get(target_db_id)

copy = await copy_page(source, target_db)
print(f"Copied to: {copy.url}")
```

#### Move Pages Between Databases

```python
async def move_pages(pages, target_database):
    """Move multiple pages to a different database.

    Args:
        pages: List of pages to move
        target_database: Destination database
    """
    moved = []

    for page in pages:
        # Update parent to target database
        await page.update(client=client, parent=target_database.id)
        moved.append(page)

    return moved

# Usage
db1 = await client.databases.get(db1_id)
db2 = await client.databases.get(db2_id)

# Get pages from db1
pages = await db1.query(client=client, status="Archived").collect()

# Move to db2
moved = await move_pages(pages, db2)
print(f"Moved {len(moved)} pages")
```

### 5. Analytics & Reporting

#### Database Statistics

```python
async def get_database_stats(database):
    """Get statistics for a database.

    Args:
        database: Database to analyze

    Returns:
        Dict with statistics
    """
    stats = {
        "total": 0,
        "by_status": {},
        "by_priority": {},
        "with_assignee": 0,
        "overdue": 0
    }

    from datetime import datetime
    today = datetime.now().isoformat()

    async for page in database.query(client=client):
        stats["total"] += 1

        # Count by status
        status = page.get_property("Status", default="None")
        stats["by_status"][status] = stats["by_status"].get(status, 0) + 1

        # Count by priority
        priority = page.get_property("Priority")
        if priority:
            stats["by_priority"][priority] = stats["by_priority"].get(priority, 0) + 1

        # Count assigned
        assignee = page.get_property("Assignee")
        if assignee:
            stats["with_assignee"] += 1

        # Count overdue
        due_date = page.get_property("Due Date")
        if due_date and due_date < datetime.now():
            stats["overdue"] += 1

    return stats

# Usage
db = await client.databases.get(db_id)
stats = await get_database_stats(db)

print(f"Total pages: {stats['total']}")
print(f"\nBy Status:")
for status, count in stats["by_status"].items():
    print(f"  {status}: {count}")
print(f"\nAssigned: {stats['with_assignee']}/{stats['total']}")
print(f"Overdue: {stats['overdue']}")
```

#### User Activity Report

```python
async def user_activity_report(database):
    """Generate report of user activity.

    Args:
        database: Database to analyze
    """
    # Populate user cache
    await client.users.populate_cache()

    # Track user activity
    activity = {}

    async for page in database.query(client=client):
        creator_id = page.created_by
        activity.setdefault(creator_id, {"created": 0, "edited": 0})
        activity[creator_id]["created"] += 1

        last_editor = page.last_edited_by
        if last_editor != creator_id:
            activity.setdefault(last_editor, {"created": 0, "edited": 0})
            activity[last_editor]["edited"] += 1

    # Print report
    print("User Activity Report")
    print("=" * 40)

    for user_id, counts in activity.items():
        user = client.users.cache.get(user_id)
        name = user.name if user else user_id
        print(f"\n{name}:")
        print(f"  Created: {counts['created']}")
        print(f"  Edited: {counts['edited']}")

# Usage
db = await client.databases.get(db_id)
await user_activity_report(db)
```

### 6. Search & Discovery

#### Multi-Database Search

```python
async def search_multiple_databases(database_ids, query):
    """Search across multiple databases.

    Args:
        database_ids: List of database IDs to search
        query: Search query

    Returns:
        List of matching pages
    """
    results = []

    for db_id in database_ids:
        db = await client.databases.get(db_id)

        # Search title contains query
        matches = await db.query(
            client=client,
            title__contains=query
        ).collect()

        results.extend(matches)

    return results

# Usage
dbs = ["db1_id", "db2_id", "db3_id"]
results = await search_multiple_databases(dbs, "urgent")

print(f"Found {len(results)} pages with 'urgent' in title")
for page in results:
    print(f"  - {page.title}")
```

#### Find Duplicate Pages

```python
async def find_duplicates(database):
    """Find pages with duplicate titles.

    Args:
        database: Database to search

    Returns:
        Dict of title -> list of pages
    """
    titles = {}

    async for page in database.query(client=client):
        title = page.title.lower()
        titles.setdefault(title, []).append(page)

    # Return only duplicates
    duplicates = {t: pages for t, pages in titles.items() if len(pages) > 1}

    return duplicates

# Usage
db = await client.databases.get(db_id)
duplicates = await find_duplicates(db)

for title, pages in duplicates.items():
    print(f"\nDuplicate: {title}")
    for page in pages:
        print(f"  - {page.id}")
```

### 7. Automation Workflows

#### Auto-Assign Tasks

```python
async def auto_assign_tasks(database, assignee_id):
    """Assign unassigned high-priority tasks.

    Args:
        database: Tasks database
        assignee_id: User ID to assign to
    """
    # Find unassigned high-priority tasks
    tasks = await database.query(
        client=client,
        priority__gte=7,
        assignee__is_null=True
    ).collect()

    # Assign each task
    for task in tasks:
        await task.update(
            client=client,
            Assignee=assignee_id
        )
        print(f"Assigned: {task.title}")

    return len(tasks)

# Usage
db = await client.databases.get(db_id)
user_id = "user_123"

count = await auto_assign_tasks(db, user_id)
print(f"Assigned {count} tasks")
```

#### Status-Based Workflows

```python
async def transition_status(database, from_status, to_status):
    """Transition all pages from one status to another.

    Args:
        database: Database to update
        from_status: Current status
        to_status: New status
    """
    # Find pages with from_status
    pages = await database.query(
        client=client,
        status=from_status
    ).collect()

    # Update to to_status
    for page in pages:
        await page.update(client=client, status=to_status)

    return len(pages)

# Usage: Mark all "Done" tasks as "Archived"
db = await client.databases.get(db_id)
count = await transition_status(db, "Done", "Archived")

print(f"Transitioned {count} pages")
```

## Performance Tips

### 1. Batch Operations

```python
# ❌ BAD: Multiple API calls
for page_id in page_ids:
    page = await client.pages.get(page_id)  # API call each time

# ✅ GOOD: Batch when possible
pages = await client.pages.get_multiple(page_ids)
```

### 2. Use Cache Effectively

```python
# ✅ GOOD: Populate cache once
await client.users.populate_cache()

for page in pages:
    user = client.users.cache.get(page.created_by_id)  # Instant
```

### 3. Stream Large Results

```python
# ❌ BAD: Loads all into memory
all_pages = await database.query(client=client).collect()

# ✅ GOOD: Stream processing
async for page in database.query(client=client):
    process(page)  # Process one at a time
```

### 4. Minimize API Calls in Loops

```python
# ❌ BAD: API call in loop
for page in pages:
    parent = await page.parent  # API call each time

# ✅ GOOD: Cache or batch differently
# First pass: cache parents
parent_cache = {}
for page in pages:
    parent_id = page.parent_id
    if parent_id not in parent_cache:
        parent_cache[parent_id] = await page.parent

# Second pass: use cache
for page in pages:
    parent = parent_cache[page.parent_id]
```

## Error Handling

```python
from better_notion.errors import NotFoundError, ValidationError

try:
    page = await client.pages.get(page_id)
    await page.update(client=client, status="Done")
except NotFoundError:
    print("Page not found")
except ValidationError as e:
    print(f"Validation error: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

## Next Steps

- **[Quick Start](./quick-start.md)** - Get started basics
- **[Managers](../managers/)** - Manager documentation
- **[Models](../models/)** - Model documentation
- **[Implementation](../implementation/)** - Technical specs
