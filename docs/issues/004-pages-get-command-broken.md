# `notion pages get` Command Broken

## Description
The `notion pages get` command fails with the error `'function' object has no attribute 'id'` when trying to retrieve page content.

## Current Behavior
```bash
notion pages get <page_id>
```

Returns error:
```json
{
  "success": false,
  "meta": {...},
  "error": {
    "code": "UNKNOWN_ERROR",
    "message": "'function' object has no attribute 'id'",
    "retry": false
  }
}
```

## Expected Behavior
Should return page details including title, properties, and content:
```json
{
  "success": true,
  "data": {
    "id": "<page_id>",
    "title": "Page Title",
    "parent_id": "...",
    "created_time": "...",
    "last_edited_time": "...",
    "properties": {...},
    "content": [...]
  }
}
```

## Root Cause
The same architectural issue as in Issue #003: trying to call methods/properties on async functions instead of awaiting them or creating proper collection objects.

In `better_notion/_cli/commands/pages.py`, the `get` command likely tries to:
1. Access properties on what is actually an async function
2. Use `client.api.pages.get()` incorrectly
3. Not properly handle the Page object's structure

The error `'function' object has no attribute 'id'` indicates the code is trying to access `.id` on a function object rather than calling it and accessing `.id` on the result.

## Impact
- **Cannot retrieve pages**: Users cannot view page details via CLI
- **Cannot verify content**: After creating pages, cannot confirm they were created correctly
- **Broken workflow**: Must use Notion web UI to inspect page structure
- **Blocks automation**: Cannot build scripts that read page content

## Affected Commands
- `notion pages get <page_id>` - Completely broken
- Potentially affects other page-related commands that read page data

## Similar Issues
- Issue #003: `notion blocks children` command (same root cause)
- Previously fixed: `BlockCollection.append()` bug (commit 6cc4373)

## Investigation Needed
Need to examine `better_notion/_cli/commands/pages.py` to identify the exact problem. Likely issues:

1. **Calling async function incorrectly**:
   ```python
   # Wrong
   page = client.api.pages.get(block_id)  # Returns coroutine, not page
   print(page.id)  # Error: coroutine object has no 'id'

   # Right
   page = await client.api.pages.get(block_id)  # Returns page dict
   print(page.get("id"))  # Works
   ```

2. **Using Page entity incorrectly**:
   ```python
   # Wrong
   page = await Page.get(block_id, client=client)
   # Then trying to access properties wrong way
   ```

3. **Collection vs API confusion**:
   ```python
   # Wrong
   pages = client.api.pages  # This is a method, not a collection
   page = pages.get(block_id)

   # Right (using collection)
   from better_notion._api.collections import PageCollection
   pages = PageCollection(client.api)
   page = await pages.get(block_id)
   ```

## Proposed Fix Pattern
Similar to the fix for `BlockCollection.append()`:

```python
@app.command()
def get(page_id: str) -> None:
    """Get a page by ID."""
    async def _get() -> str:
        try:
            client = get_client()

            # Use PageCollection properly
            from better_notion._api.collections import PageCollection
            pages = PageCollection(client.api)
            page_data = await pages.get(page_id)

            return format_success({
                "id": page_data.get("id"),
                "title": extract_title(page_data),
                "parent_id": page_data.get("parent", {}).get("id"),
                "created_time": page_data.get("created_time"),
                "last_edited_time": page_data.get("last_edited_time"),
            })
        except Exception as e:
            return format_error("UNKNOWN_ERROR", str(e), retry=False)

    result = asyncio.run(_get())
    typer.echo(result)
```

## Related Files
- `better_notion/_cli/commands/pages.py` - CLI command implementation
- `better_notion/_api/collections/pages.py` - PageCollection.get() method
- `better_notion/_sdk/models/page.py` - Page entity model

## Test Case
```bash
# Create a page
PAGE_ID=$(notion pages create --parent <db_id> --title "Test" | jq -r '.data.id')

# Try to get it - should fail with current code
notion pages get $PAGE_ID

# Expected: returns page details
# Actual: returns "'function' object has no attribute 'id'"
```

## Related
- Issue #003: notion blocks children command broken (same root cause)
- Commit 6cc4373: Fix for BlockCollection.append() usage (similar pattern)
