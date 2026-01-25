# Beyond API Helpers

Smart helper methods that go beyond the raw Notion API to provide convenient, high-level operations.

## Overview

The Notion API is low-level and verbose. While our entity-oriented architecture provides clean abstractions, we can add **smart helpers** that simplify common workflows and handle complex operations automatically.

### The Problem

**Raw API tasks are verbose:**
```python
# ❌ Verbose - manual pagination, rate limiting, loops
pages = []
cursor = None
while True:
    data = await api._request("POST", f"/databases/{db_id}/query", json={
        "start_cursor": cursor
    })
    pages.extend(data["results"])
    if not data["has_more"]:
        break
    cursor = data["next_cursor"]

# Then manual loop with rate limiting
for page in pages:
    if page["properties"]["Status"]["select"]["name"] == "Done":
        await asyncio.sleep(0.34)  # Manual rate limit
        await api._request("PATCH", f"/pages/{page['id']}", json={...})
```

**With smart helpers:**
```python
# ✅ Clean - automatic pagination, rate limiting, filtering
await database.update_all(
    client=client,
    filter={"status": "Done"},
    update={"archived": True}
)
```

## Categories of Helpers

### 1. Bulk Operations

Perform operations on multiple entities with automatic rate limiting.

#### Database.bulk_update()

```python
class Database(BaseEntity):
    """..."""

    async def update_all(
        self,
        client: NotionClient,
        filter: dict[str, Any] | None = None,
        update: dict[str, Any] | None = None,
        batch_size: int = 50,
        delay: float = 0.34
    ) -> int:
        """Update multiple pages with automatic rate limiting.

        Args:
            client: Notion client
            filter: Filter conditions (same as query())
            update: Properties to update
            batch_size: Pages per batch (default 50)
            delay: Delay between batches for rate limiting (default 0.34s)

        Returns:
            Number of pages updated

        Example:
            >>> # Archive all completed tasks
            >>> count = await database.update_all(
            ...     client=client,
            ...     filter={"status": "Done"},
            ...     update={"archived": True}
            ... )
            >>> print(f"Archived {count} pages")

        Note:
            - Handles pagination automatically
            - Respects Notion rate limits (3 requests/second)
            - Returns count of updated pages
        """
        query = self.query(client=client, **(filter or {}))

        count = 0
        batch = []

        async for page in query:
            batch.append(page)

            if len(batch) >= batch_size:
                # Process batch
                for page in batch:
                    await page.update(client=client, **update)
                    count += 1

                # Rate limit delay
                await asyncio.sleep(delay)
                batch = []

        # Process remaining pages
        for page in batch:
            await page.update(client=client, **update)
            count += 1

        return count

    async def delete_all(
        self,
        client: NotionClient,
        filter: dict[str, Any] | None = None,
        batch_size: int = 50,
        delay: float = 0.34
    ) -> int:
        """Delete multiple pages.

        Example:
            >>> # Delete all pages with "Delete" tag
            >>> count = await database.delete_all(
            ...     client=client,
            ...     filter={"tags": "Delete"}
            ... )
        """
        query = self.query(client=client, **(filter or {}))

        count = 0
        batch = []

        async for page in query:
            batch.append(page)

            if len(batch) >= batch_size:
                for page in batch:
                    await page.delete(client=client)
                    count += 1
                await asyncio.sleep(delay)
                batch = []

        for page in batch:
            await page.delete(client=client)
            count += 1

        return count

    async def collect_all(
        self,
        client: NotionClient,
        filter: dict[str, Any] | None = None,
        limit: int | None = None
    ) -> list[Page]:
        """Collect all pages into a list (with pagination).

        Args:
            client: Notion client
            filter: Filter conditions
            limit: Maximum pages to collect

        Returns:
            List of all pages matching filters

        Example:
            >>> # Get all incomplete tasks
            >>> pages = await database.collect_all(
            ...     client=client,
            ...     filter={"status": "Todo"}
            ... )
            >>> print(f"Found {len(pages)} tasks")
        """
        query = self.query(client=client, **(filter or {}))

        pages = []
        async for page in query:
            pages.append(page)
            if limit and len(pages) >= limit:
                break

        return pages
```

#### Page.bulk_update_children()

```python
class Page(BaseEntity):
    """..."""

    async def append_multiple(
        self,
        client: NotionClient,
        blocks: list[Block],
        batch_size: int = 50,
        delay: float = 0.34
    ) -> None:
        """Append multiple blocks with rate limiting.

        Args:
            client: Notion client
            blocks: Blocks to append
            batch_size: Blocks per batch
            delay: Delay between batches

        Example:
            >>> # Create document from structure
            >>> blocks = [
            ...     await Heading.create(parent=page, text="Chapter 1", level=1, client=client),
            ...     await Paragraph.create(parent=page, text="Intro...", client=client),
            ...     await Code.create(parent=page, code="print('x')", client=client),
            ... ]
            >>> await page.append_multiple(client=client, blocks=blocks)
        """
        for i in range(0, len(blocks), batch_size):
            batch = blocks[i:i + batch_size]

            # Append batch
            await client._api.blocks.children.append(
                self.id,
                children=[b._data for b in batch]
            )

            # Rate limit if not last batch
            if i + batch_size < len(blocks):
                await asyncio.sleep(delay)
```

### 2. Smart Search

Enhanced search with caching and multi-criteria queries.

#### NotionClient.smart_search()

```python
class NotionClient:
    """..."""

    async def smart_search(
        self,
        query: str = "",
        types: list[str] | None = None,
        filters: dict[str, Any] | None = None,
        sort: str = "relevance",
        limit: int = 100
    ) -> list[Page | Database | Block]:
        """Smart search with multiple criteria and caching.

        Args:
            query: Search query
            types: Entity types to search ["page", "database", "block"]
            filters: Additional filters (in_database, created_by, etc.)
            sort: Sort order ("relevance", "last_edited")
            limit: Max results

        Returns:
            List of matching entities

        Example:
            >>> # Find all pages containing "API" in specific database
            >>> results = await client.smart_search(
            ...     query="API",
            ...     types=["page"],
            ...     filters={"in_database": db_id},
            ...     limit=20
            ... )

        Note:
            - Caches recent searches
            - Supports multiple filters
            - Type-aware results
        """
        # Check cache first
        cache_key = f"{query}:{types}:{filters}:{sort}:{limit}"
        if cache_key in self._search_cache:
            return self._search_cache[cache_key]

        # Build filter
        filter_obj = {}
        if types and len(types) == 1:
            filter_obj["value"] = types[0]
            filter_obj["property"] = "object"

        # Execute search
        results = []
        async for result in self._api.search.query(
            query=query,
            filter=filter_obj if filter_obj else None,
            sort={"direction": "descending", "timestamp": "last_edited_time"} if sort == "last_edited" else None
        ):
            if len(results) >= limit:
                break

            obj_type = result.get("object")

            # Apply additional filters
            if filters:
                if "in_database" in filters:
                    if result.get("parent", {}).get("database_id") != filters["in_database"]:
                        continue
                if "created_by" in filters:
                    if result.get("created_by") != filters["created_by"]:
                        continue

            # Create entity
            if obj_type == "page":
                results.append(Page(self, result))
            elif obj_type == "database":
                results.append(Database(self, result))
            elif obj_type == "block":
                results.append(Block.from_data(self, result))

        # Cache result
        self._search_cache[cache_key] = results

        return results
```

#### Database.find_duplicates()

```python
class Database(BaseEntity):
    """..."""

    async def find_duplicates(
        self,
        client: NotionClient,
        property: str,
        case_sensitive: bool = False
    ) -> dict[str, list[Page]]:
        """Find duplicate values in a property.

        Args:
            client: Notion client
            property: Property name to check
            case_sensitive: Whether to consider case

        Returns:
            Dict mapping duplicate values to list of pages

        Example:
            >>> # Find duplicate emails
            >>> duplicates = await database.find_duplicates(
            ...     client=client,
            ...     property="Email"
            ... )
            >>> for email, pages in duplicates.items():
            ...     if len(pages) > 1:
            ...         print(f"{email}: {len(pages)} duplicates")
        """
        value_to_pages = {}

        async for page in self.query(client=client):
            value = page.get_property(property)

            if not case_sensitive and isinstance(value, str):
                value = value.lower()

            if value not in value_to_pages:
                value_to_pages[value] = []
            value_to_pages[value].append(page)

        # Return only duplicates
        return {
            value: pages
            for value, pages in value_to_pages.items()
            if len(pages) > 1
        }
```

### 3. Transform & Export

Convert Notion content to other formats.

#### Page.to_markdown()

```python
class Page(BaseEntity):
    """..."""

    async def to_markdown(
        self,
        client: NotionClient,
        include_children: bool = True
    ) -> str:
        """Export page as Markdown.

        Args:
            client: Notion client
            include_children: Include child blocks

        Returns:
            Markdown string

        Example:
            >>> markdown = await page.to_markdown(client=client)
            >>> with open("page.md", "w") as f:
            ...     f.write(markdown)
        """
        lines = []

        # Title
        lines.append(f"# {self.title}\n")

        if include_children:
            async for block in self.children:
                lines.append(await block.to_markdown(client=client))

        return "\n".join(lines)

    async def to_html(
        self,
        client: NotionClient,
        include_children: bool = True
    ) -> str:
        """Export page as HTML.

        Example:
            >>> html = await page.to_html(client=client)
        """
        # Similar implementation for HTML
        pass
```

#### Block.to_markdown()

```python
class Block(BaseEntity):
    """..."""

    async def to_markdown(self, client: NotionClient) -> str:
        """Convert block to Markdown.

        Example:
            >>> markdown = await block.to_markdown(client=client)
        """
        # Delegated to specialized classes
        return ""
```

#### Specialized to_markdown() implementations

```python
class Paragraph(Block):
    async def to_markdown(self, client: NotionClient) -> str:
        return self.text + "\n"

class Heading(Block):
    async def to_markdown(self, client: NotionClient) -> str:
        prefix = "#" * self.level
        return f"{prefix} {self.text}\n"

class Code(Block):
    async def to_markdown(self, client: NotionClient) -> str:
        return f"```{self.language}\n{self.code}\n```\n"

class Todo(Block):
    async def to_markdown(self, client: NotionClient) -> str:
        checkbox = "[x]" if self.checked else "[ ]"
        return f"{checkbox} {self.text}\n"

class BulletedListItem(Block):
    async def to_markdown(self, client: NotionClient) -> str:
        return f"- {self.text}\n"

class NumberedListItem(Block):
    async def to_markdown(self, client: NotionClient) -> str:
        # Would need to track number
        return f"1. {self.text}\n"

class Image(Block):
    async def to_markdown(self, client: NotionClient) -> str:
        caption = f" {self.caption}" if self.caption else ""
        return f"![{caption}]({self.url})\n"

class Callout(Block):
    async def to_markdown(self, client: NotionClient) -> str:
        icon = f"{self.icon} " if self.icon else ""
        return f"> {icon}{self.text}\n"

class Quote(Block):
    async def to_markdown(self, client: NotionClient) -> str:
        return f"> {self.text}\n"

class Divider(Block):
    async def to_markdown(self, client: NotionClient) -> str:
        return "---\n"
```

### 4. Workspace Operations

Operations that span multiple databases/pages.

#### NotionClient.export_database()

```python
class NotionClient:
    """..."""

    async def export_database(
        self,
        database_id: str,
        format: str = "markdown",
        output_dir: Path | None = None
    ) -> Path:
        """Export entire database to files.

        Args:
            database_id: Database to export
            format: Export format ("markdown", "json", "csv")
            output_dir: Output directory (default: current dir)

        Returns:
            Path to export directory

        Example:
            >>> await client.export_database(
            ...     database_id=db_id,
            ...     format="markdown",
            ...     output_dir=Path("./export")
            ... )
        """
        database = await Database.get(database_id, client=self)

        if output_dir is None:
            output_dir = Path(f"./export_{database.title.replace(' ', '_')}")
        output_dir.mkdir(parents=True, exist_ok=True)

        if format == "markdown":
            async for page in database.query(client=self):
                markdown = await page.to_markdown(client=self)
                filename = f"{page.title.replace(' ', '_')}.md"
                (output_dir / filename).write_text(markdown)

        elif format == "json":
            pages = []
            async for page in database.query(client=self):
                pages.append(page._data)

            (output_dir / "database.json").write_text(
                json.dumps(pages, indent=2)
            )

        elif format == "csv":
            # CSV export for properties
            import csv

            async for page in database.query(client=self):
                rows = []
                async for page in database.query(client=self):
                    row = {"id": page.id, "title": page.title}
                    for prop in database.schema.keys():
                        row[prop] = str(page.get_property(prop) or "")
                    rows.append(row)

                with open(output_dir / "database.csv", "w") as f:
                    writer = csv.DictWriter(f, fieldnames=rows[0].keys())
                    writer.writeheader()
                    writer.writerows(rows)

        return output_dir
```

#### Database.sync_from()

```python
class Database(BaseEntity):
    """..."""

    async def sync_from(
        self,
        client: NotionClient,
        source: "Database",
        mapping: dict[str, str],
        conflict: str = "skip"
    ) -> dict[str, int]:
        """Sync pages from another database.

        Args:
            client: Notion client
            source: Source database
            mapping: Property name mapping {"source_prop": "target_prop"}
            conflict: Conflict resolution ("skip", "overwrite", "rename")

        Returns:
            Dict with counts {"created": X, "updated": Y, "skipped": Z}

        Example:
            >>> # Sync from staging to production
            >>> stats = await prod_db.sync_from(
            ...     client=client,
            ...     source=staging_db,
            ...     mapping={"Title": "Name", "Status": "State"},
            ...     conflict="skip"
            ... )
            >>> print(f"Created: {stats['created']}")
        """
        stats = {"created": 0, "updated": 0, "skipped": 0}

        async for source_page in source.query(client=client):
            # Check if exists by title
            existing = await self._find_by_title(client, source_page.title)

            if existing:
                if conflict == "skip":
                    stats["skipped"] += 1
                    continue
                elif conflict == "overwrite":
                    # Map properties and update
                    update_data = {}
                    for src_prop, tgt_prop in mapping.items():
                        value = source_page.get_property(src_prop)
                        if value is not None:
                            update_data[tgt_prop] = value
                    await existing.update(client=client, **update_data)
                    stats["updated"] += 1
            else:
                # Create new page
                create_data = {}
                for src_prop, tgt_prop in mapping.items():
                    value = source_page.get_property(src_prop)
                    if value is not None:
                        create_data[tgt_prop] = value

                await Page.create(
                    parent=self,
                    title=source_page.title,
                    client=client,
                    **create_data
                )
                stats["created"] += 1

        return stats

    async def _find_by_title(
        self,
        client: NotionClient,
        title: str
    ) -> Page | None:
        """Find page by title."""
        async for page in self.query(client=client):
            if page.title == title:
                return page
        return None
```

### 5. Template Operations

Create pages from templates.

#### Page.from_template()

```python
class Page(BaseEntity):
    """..."""

    @classmethod
    async def from_template(
        cls,
        template_id: str,
        parent: Database | Page,
        title: str,
        client: NotionClient,
        replace_vars: dict[str, str] | None = None
    ) -> "Page":
        """Create page from template.

        Args:
            template_id: Template page ID
            parent: Parent database or page
            title: New page title
            client: Notion client
            replace_vars: Variables to replace in template

        Returns:
            Created page

        Example:
            >>> # Create from project template
            >>> page = await Page.from_template(
            ...     template_id=template_page_id,
            ...     parent=database,
            ...     title="Project Alpha",
            ...     client=client,
            ...     replace_vars={
            ...         "{{PROJECT_NAME}}": "Project Alpha",
            ...         "{{START_DATE}}": "2025-01-15"
            ...     }
            ... )
        """
        # Load template
        template = await cls.get(template_id, client=client)

        # Create new page
        new_page = await cls.create(
            parent=parent,
            title=title,
            client=client
        )

        # Copy blocks with variable replacement
        if replace_vars:
            async for block in template.children:
                new_block_data = block._data.copy()

                # Replace variables in text content
                if hasattr(block, 'text'):
                    for var, value in replace_vars.items():
                        new_block_data = cls._replace_in_dict(
                            new_block_data,
                            var,
                            value
                        )

                # Create block
                await client._api.blocks.children.append(
                    new_page.id,
                    children=[new_block_data]
                )

        return new_page

    @staticmethod
    def _replace_in_dict(data: dict, var: str, value: str) -> dict:
        """Replace variable in nested dict."""
        import copy

        result = copy.deepcopy(data)

        if isinstance(result, dict):
            for key, val in result.items():
                if isinstance(val, str):
                    result[key] = val.replace(var, value)
                elif isinstance(val, dict):
                    result[key] = Page._replace_in_dict(val, var, value)
                elif isinstance(val, list):
                    result[key] = [
                        Page._replace_in_dict(item, var, value)
                        if isinstance(item, dict) else item
                        for item in val
                    ]

        return result
```

## Usage Examples

### Example 1: Bulk Archive

```python
# Archive all completed tasks older than 30 days
from datetime import datetime, timedelta

cutoff = datetime.now() - timedelta(days=30)

db = await Database.get(db_id, client=client)

count = await db.update_all(
    client=client,
    filter={
        "status": "Done",
        "completed_date__before": cutoff
    },
    update={"archived": True}
)

print(f"Archived {count} old tasks")
```

### Example 2: Export Database

```python
# Export entire database to Markdown
db = await Database.get(db_id, client=client)

export_dir = await client.export_database(
    database_id=db.id,
    format="markdown",
    output_dir=Path("./docs_export")
)

print(f"Exported to {export_dir}")
```

### Example 3: Find Duplicates

```python
# Find duplicate emails in contacts database
contacts_db = await Database.get(contacts_id, client=client)

duplicates = await contacts_db.find_duplicates(
    client=client,
    property="Email"
)

for email, pages in duplicates.items():
    print(f"{email}: {len(pages)} duplicates")
    for page in pages:
        print(f"  - {page.title} ({page.id})")
```

### Example 4: Smart Search

```python
# Find all pages mentioning "API" in specific database, edited this week
from datetime import datetime, timedelta

week_ago = datetime.now() - timedelta(days=7)

results = await client.smart_search(
    query="API",
    types=["page"],
    filters={
        "in_database": db_id,
        "last_edited_time__after": week_ago
    },
    sort="last_edited",
    limit=20
)

for item in results:
    print(f"{item.title} - {item.last_edited_time}")
```

### Example 5: Create from Template

```python
# Create project pages from template
projects = ["Alpha", "Beta", "Gamma"]

for project in projects:
    page = await Page.from_template(
        template_id=template_id,
        parent=database,
        title=f"Project {project}",
        client=client,
        replace_vars={
            "{{PROJECT_NAME}}": project,
            "{{START_DATE}}": datetime.now().strftime("%Y-%m-%d")
        }
    )

    print(f"Created {page.title}")
```

## Performance Considerations

### Rate Limiting

Notion API limits:
- Integrations: 3 requests/second
- We need delays between batch operations

```python
# Automatic rate limiting
await database.update_all(
    client=client,
    filter={...},
    update={...},
    batch_size=50,      # Process 50 at a time
    delay=0.34          # Wait 0.34s between batches (~3 req/s)
)
```

### Caching

Search results are cached:

```python
# First call - hits API
results1 = await client.smart_search(query="test")

# Second call - cache hit (instant)
results2 = await client.smart_search(query="test")
```

### Pagination

All helpers handle pagination automatically:

```python
# Just use the helper, pagination is handled
pages = await database.collect_all(client=client)
# No manual pagination needed!
```

## Design Decisions

### Q1: Should helpers be in entities or client?

**Decision**: Both, depending on scope

- **Entity methods**: Operations on that entity (`database.update_all()`)
- **Client methods**: Cross-entity operations (`client.smart_search()`)

### Q2: Should helpers cache results?

**Decision**: Yes, for expensive operations

```python
# Search cache
self._search_cache: dict[str, list[Entity]] = {}

# Export cache (optional)
async def export_database(..., use_cache: bool = True):
    if use_cache and cache_key in self._export_cache:
        return self._export_cache[cache_key]
```

### Q3: Error handling in bulk operations?

**Decision**: Continue on error, collect errors

```python
async def update_all(..., on_error: str = "continue") -> dict:
    results = {"updated": 0, "errors": []}

    for page in pages:
        try:
            await page.update(...)
            results["updated"] += 1
        except Exception as e:
            results["errors"].append({"page": page.id, "error": str(e)})
            if on_error == "stop":
                break

    return results
```

### Q4: Template variables format?

**Decision**: Mustache-style `{{var}}`

```python
# Clear and standard
replace_vars={
    "{{PROJECT_NAME}}": "Alpha",
    "{{DATE}}": "2025-01-15"
}
```

## Next Steps

1. ✅ Entity-oriented architecture
2. ✅ Specialized block classes
3. ✅ Beyond API helpers
4. ⏭️ **Implementation** - Start coding the SDK
5. ⏭️ **Testing** - Unit and integration tests
6. ⏭️ **Documentation** - User-facing docs

## Related Documentation

- [Entity-Oriented Architecture](./entity-oriented-architecture.md) - Core architecture
- [Block Specialized Classes](../models/blocks-specialized.md) - Block types
- [Database Model](../models/database-model.md) - Database entity
- [Page Model](../models/page-model.md) - Page entity
