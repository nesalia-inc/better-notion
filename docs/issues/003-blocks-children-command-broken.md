# `notion blocks children` Command Broken

## Description
The `notion blocks children` command fails with the error `'function' object has no attribute 'list'` when trying to retrieve child blocks of a parent block.

## Current Behavior
```bash
notion blocks children <block_id>
```

Returns error:
```json
{
  "success": false,
  "meta": {...},
  "error": {
    "code": "UNKNOWN_ERROR",
    "message": "'function' object has no attribute 'list'",
    "retry": false
  }
}
```

## Expected Behavior
Should return a list of child blocks:
```json
{
  "success": true,
  "data": {
    "block_id": "<id>",
    "count": 5,
    "children": [
      {"id": "...", "type": "paragraph"},
      {"id": "...", "type": "heading"},
      ...
    ]
  }
}
```

## Root Cause
Similar to the bug fixed in Issue #003 (BlockCollection.append), the CLI command tries to call `.children` as a property, but `client.api.blocks.children` is an **async method** that returns a list, not a collection object.

In `better_notion/_cli/commands/blocks.py`:
```python
@app.command()
def children(block_id: str) -> None:
    """Get children of a block."""
    async def _children() -> str:
        try:
            client = get_client()
            block = await client.blocks.get(block_id)

            child_list = []
            async for child in block.children():  # ← This is the problem
                child_list.append({
                    "id": child.id,
                    "type": child.type,
                })
            ...
```

The issue is that `block.children()` is an async method that directly returns a list of dicts from the API, not an async iterator. The code tries to use it as an async iterator with `async for`, which is incorrect.

## Impact
- **Cannot retrieve block content**: Users cannot view what blocks exist on a page
- **Cannot debug**: When creating blocks via CLI, cannot verify they were created
- **Broken workflow**: Must use Notion web UI to verify CLI operations

## Affected Commands
- `notion blocks children <block_id>` - Completely broken

## Similar Issues
This is the same architectural problem as:
- Issue #004: `notion pages get` command (similar issue)
- Previously fixed: `BlockCollection.append()` bug (commit 6cc4373)

## Proposed Fix
The `BlockCollection.children()` method in `better_notion/_api/collections/blocks.py` returns a `list[dict]`, not an async iterator. The CLI command should be:

```python
@app.command()
def children(block_id: str) -> None:
    """Get children of a block."""
    async def _children() -> str:
        try:
            client = get_client()
            from better_notion._api.collections import BlockCollection

            blocks = BlockCollection(client.api, parent_id=block_id)
            child_list = await blocks.children()  # Direct call, not async for

            return format_success({
                "block_id": block_id,
                "count": len(child_list),
                "children": [{"id": child["id"], "type": child["type"]} for child in child_list]
            })
        except Exception as e:
            return format_error("UNKNOWN_ERROR", str(e), retry=False)

    result = asyncio.run(_children())
    typer.echo(result)
```

## Related Files
- `better_notion/_cli/commands/blocks.py` - CLI command implementation (line ~144)
- `better_notion/_api/collections/blocks.py` - BlockCollection.children() method (line ~69)
- `better_notion/_sdk/models/block.py` - Block.children property/method

## Related
- Issue #001: Missing dedicated block commands
- Issue #002: Todo command --checked parameter bug
- Issue #004: notion pages get command broken
