# Blocks API Reference

Complete API reference for all block-related operations in the Notion API.

## Table of Contents

1. [Retrieve a Block](#retrieve-a-block)
2. [Retrieve Block Children](#retrieve-block-children)
3. [Append Block Children](#append-block-children)
4. [Update a Block](#update-a-block)
5. [Delete a Block](#delete-a-block)

---

## Retrieve a Block

Retrieves a Block object using the ID specified.

### Endpoint

```
GET https://api.notion.com/v1/blocks/{block_id}
```

### Path Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `block_id` | string (UUID) | Yes | Identifier for a Notion block |

### Headers

| Header | Type | Required | Description |
|--------|------|----------|-------------|
| `Authorization` | string | Yes | Bearer `{integration_token}` |
| `Notion-Version` | string | Yes | The API version to use (latest: `2025-09-03`) |

### Required Capabilities

This endpoint requires the **read content** capability. Attempting to call this API without read content capabilities will return a HTTP 403 status code.

### Response

Returns a Block object for the specified block ID.

**Response Structure:**

```json
{
  "object": "block",
  "id": "c02fc1d3-db8b-45c5-a222-27595b15aea7",
  "parent": {
    "type": "page_id",
    "page_id": "59833787-2cf9-4fdf-8782-e53db20768a5"
  },
  "created_time": "2022-03-01T19:05:00.000Z",
  "last_edited_time": "2022-03-01T19:05:00.000Z",
  "created_by": {
    "object": "user",
    "id": "ee5f0f84-409a-440f-983a-a5315961c6e4"
  },
  "last_edited_by": {
    "object": "user",
    "id": "ee5f0f84-409a-440f-983a-a5315961c6e4"
  },
  "has_children": false,
  "archived": false,
  "type": "heading_2",
  "heading_2": {
    "rich_text": [
      {
        "type": "text",
        "text": {
          "content": "Lacinato kale",
          "link": null
        },
        "annotations": {
          "bold": false,
          "italic": false,
          "strikethrough": false,
          "underline": false,
          "code": false,
          "color": "default"
        },
        "plain_text": "Lacinato kale",
        "href": null
      }
    ],
    "color": "default",
    "is_toggleable": false
  }
}
```

### SDK Implementation

```python
async def get_block(self, block_id: str) -> Block:
    """
    Retrieve a block by ID.

    Args:
        block_id: The UUID of the block to retrieve

    Returns:
        Block object

    Raises:
        NotFoundError: If the block doesn't exist
        PermissionError: If lacking read content capability
    """
    response = await self._client.request(
        "GET",
        f"/blocks/{block_id}"
    )

    return Block.from_dict(response, self._client)
```

### Errors

| Status Code | Error | Description |
|-------------|-------|-------------|
| 404 | `object_not_found` | Block doesn't exist or integration doesn't have access |
| 403 | `missing_permission` | Integration lacks read content capability |
| 429 | `rate_limited` | Request rate limit exceeded |

### Example Usage

```python
# Get a specific block
block = await client.blocks.get("block-id-here")

print(f"Block type: {block.type}")
print(f"Has children: {block.has_children}")

# Access type-specific properties
if block.type == BlockType.HEADING_2:
    print(f"Heading text: {block.plain_text}")
```

---

## Retrieve Block Children

Returns a paginated array of child block objects contained in the block.

### Endpoint

```
GET https://api.notion.com/v1/blocks/{block_id}/children
```

### Path Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `block_id` | string (UUID) | Yes | Identifier for a block (also accepts page ID) |

### Query Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `start_cursor` | string | No | - | Cursor to start pagination from |
| `page_size` | integer | No | 100 | Number of items (max: 100) |

### Headers

| Header | Type | Required | Description |
|--------|------|----------|-------------|
| `Authorization` | string | Yes | Bearer `{integration_token}` |
| `Notion-Version` | string | Yes | The API version to use (latest: `2025-09-03`) |

### Required Capabilities

This endpoint requires the **read content** capability.

### Response

Returns a paginated list of child block objects.

**Response Structure:**

```json
{
  "object": "list",
  "results": [
    {
      "object": "block",
      "id": "acc7eb06-05cd-4603-a384-5e1e4f1f4e72",
      "parent": {
        "type": "page_id",
        "page_id": "59833787-2cf9-4fdf-8782-e53db20768a5"
      },
      "created_time": "2022-03-01T19:05:00.000Z",
      "last_edited_time": "2022-03-01T19:05:00.000Z",
      "created_by": {
        "object": "user",
        "id": "ee5f0f84-409a-440f-983a-a5315961c6e4"
      },
      "last_edited_by": {
        "object": "user",
        "id": "ee5f0f84-409a-440f-983a-a5315961c6e4"
      },
      "has_children": false,
      "archived": false,
      "type": "paragraph",
      "paragraph": {
        "rich_text": [
          {
            "type": "text",
            "text": {
              "content": "Lacinato kale is a variety of kale...",
              "link": {
                "url": "https://en.wikipedia.org/wiki/Lacinato_kale"
              }
            },
            "annotations": {
              "bold": false,
              "italic": false,
              "strikethrough": false,
              "underline": false,
              "code": false,
              "color": "default"
            },
            "plain_text": "Lacinato kale is a variety of kale...",
            "href": "https://en.wikipedia.org/wiki/Lacinato_kale"
          }
        ],
        "color": "default"
      }
    }
  ],
  "next_cursor": null,
  "has_more": false
}
```

### SDK Implementation

```python
async def get_children(
    self,
    block_id: str,
    *,
    page_size: int = 100,
    start_cursor: Optional[str] = None
) -> PaginatedResponse[Block]:
    """
    Retrieve child blocks of a parent block.

    Args:
        block_id: The UUID of the parent block or page
        page_size: Number of blocks to return (max: 100)
        start_cursor: Cursor for pagination

    Returns:
        PaginatedResponse containing list of Block objects

    Raises:
        NotFoundError: If the block doesn't exist
        PermissionError: If lacking read content capability
    """
    params = {"page_size": page_size}
    if start_cursor:
        params["start_cursor"] = start_cursor

    response = await self._client.request(
        "GET",
        f"/blocks/{block_id}/children",
        params=params
    )

    return PaginatedResponse(
        results=[
            Block.from_dict(block_data, self._client)
            for block_data in response.get("results", [])
        ],
        has_more=response.get("has_more", False),
        next_cursor=response.get("next_cursor")
    )

async def get_all_children(self, block_id: str) -> List[Block]:
    """
    Retrieve all child blocks with automatic pagination.

    Args:
        block_id: The UUID of the parent block or page

    Returns:
        List of all child Block objects
    """
    all_blocks = []
    has_more = True
    cursor = None

    while has_more:
        response = await self.get_children(
            block_id,
            start_cursor=cursor
        )
        all_blocks.extend(response.results)
        has_more = response.has_more
        cursor = response.next_cursor

    return all_blocks
```

### Pagination

The endpoint uses cursor-based pagination:

1. First request: Call without `start_cursor` to get the first page
2. Check `has_more` in the response
3. If `has_more` is `true`, use `next_cursor` as `start_cursor` for the next request
4. Repeat until `has_more` is `false`

### Errors

| Status Code | Error | Description |
|-------------|-------|-------------|
| 404 | `object_not_found` | Block doesn't exist or integration doesn't have access |
| 403 | `missing_permission` | Integration lacks read content capability |
| 400 | `bad_request` | Invalid page size (must be ≤ 100) |
| 429 | `rate_limited` | Request rate limit exceeded |

### Example Usage

```python
# Get first page of children
children = await client.blocks.get_children("page-id")

for block in children.results:
    print(f"{block.type}: {block.plain_text}")

# Get all children with automatic pagination
all_blocks = await client.blocks.get_all_children("page-id")

print(f"Total blocks: {len(all_blocks)}")

# Iterate through pages
cursor = None
while True:
    page = await client.blocks.get_children(
        "page-id",
        start_cursor=cursor
    )

    for block in page.results:
        process_block(block)

    if not page.has_more:
        break

    cursor = page.next_cursor
```

---

## Append Block Children

Creates and appends new children blocks to a parent block.

### Endpoint

```
PATCH https://api.notion.com/v1/blocks/{block_id}/children
```

### Path Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `block_id` | string (UUID) | Yes | Identifier for a block (also accepts page ID) |

### Body Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `children` | array | Yes | Array of block objects to append |
| `after` | string | No | ID of existing block to append after |
| `position` | object | No | Position object for advanced positioning |

**Request Structure:**

```json
{
  "children": [
    {
      "object": "block",
      "type": "heading_2",
      "heading_2": {
        "rich_text": [
          {
            "type": "text",
            "text": {
              "content": "Lacinato kale"
            }
          }
        ]
      }
    },
    {
      "object": "block",
      "type": "paragraph",
      "paragraph": {
        "rich_text": [
          {
            "type": "text",
            "text": {
              "content": "Lacinato kale is a variety of kale...",
              "link": {
                "url": "https://en.wikipedia.org/wiki/Lacinato_kale"
              }
            }
          }
        ]
      }
    }
  ],
  "after": "some-block-id"  // Optional
}
```

### Headers

| Header | Type | Required | Description |
|--------|------|----------|-------------|
| `Authorization` | string | Yes | Bearer `{integration_token}` |
| `Content-Type` | string | Yes | `application/json` |
| `Notion-Version` | string | Yes | The API version to use (latest: `2025-09-03`) |

### Required Capabilities

This endpoint requires the **insert content** capability. Attempting to call this API without insert content capabilities will return a HTTP 403 status code.

### Response

Returns a paginated list of the newly created block objects.

```json
{
  "object": "list",
  "results": [
    {
      "object": "block",
      "id": "new-block-id-1",
      "type": "heading_2",
      "heading_2": { /* ... */ }
    },
    {
      "object": "block",
      "id": "new-block-id-2",
      "type": "paragraph",
      "paragraph": { /* ... */ }
    }
  ],
  "next_cursor": null,
  "has_more": false
}
```

### Limitations

1. **Maximum blocks per request**: 100 blocks
2. **Nesting limit**: Up to 2 levels of nesting in a single request
3. **Positioning**: Blocks are appended to the bottom by default
4. **Immutability**: Once a block is appended, it cannot be moved elsewhere via the API
5. **Special blocks**: Some block types cannot be created via API:
   - `link_preview`
   - `breadcrumb`
   - `child_database` (use database endpoints)
   - `child_page` (use page endpoints)

### Positioning

**Append after specific block:**
```json
{
  "children": [/* blocks */],
  "after": "existing-block-id"
}
```

**Use position object (newer approach):**
```json
{
  "children": [/* blocks */],
  "position": {
    "before": "block-id",  // Optional
    "after": "block-id"    // Optional
  }
}
```

### SDK Implementation

```python
async def append_children(
    self,
    block_id: str,
    children: List[Block],
    *,
    after: Optional[str] = None
) -> List[Block]:
    """
    Append new child blocks to a parent block.

    Args:
        block_id: The UUID of the parent block or page
        children: List of Block objects to append
        after: Optional block ID to append after

    Returns:
        List of created Block objects

    Raises:
        ValueError: If more than 100 blocks provided
        NotFoundError: If the parent block doesn't exist
        PermissionError: If lacking insert content capability
    """
    if len(children) > 100:
        raise ValueError("Cannot append more than 100 blocks in a single request")

    # Convert blocks to API format
    children_data = [block.to_dict() for block in children]

    payload = {"children": children_data}
    if after:
        payload["after"] = after

    response = await self._client.request(
        "PATCH",
        f"/blocks/{block_id}/children",
        json=payload
    )

    return [
        Block.from_dict(block_data, self._client)
        for block_data in response.get("results", [])
    ]

async def append_paragraph(
    self,
    block_id: str,
    text: str,
    **kwargs
) -> Paragraph:
    """Helper to append a paragraph block."""
    paragraph = Paragraph(**kwargs)
    paragraph.set_text(text)

    result = await self.append_children(block_id, [paragraph])
    return result[0] if result else None

async def append_heading(
    self,
    block_id: str,
    text: str,
    level: int = 1,
    **kwargs
) -> Heading:
    """Helper to append a heading block."""
    heading = Heading(level=level, **kwargs)
    heading.set_text(text)

    result = await self.append_children(block_id, [heading])
    return result[0] if result else None
```

### Errors

| Status Code | Error | Description |
|-------------|-------|-------------|
| 400 | `bad_request` | More than 100 blocks in request |
| 400 | `bad_request` | Invalid block type or data |
| 400 | `validation_error` | Block structure exceeds 2 levels of nesting |
| 403 | `missing_permission` | Integration lacks insert content capability |
| 404 | `object_not_found` | Parent block doesn't exist |
| 429 | `rate_limited` | Request rate limit exceeded |

### Example Usage

```python
# Append multiple blocks
heading = Heading(level=2)
heading.set_text("Recipe Instructions")

paragraph = Paragraph()
paragraph.set_text("Mix all ingredients together.")

todo = ToDo(checked=False)
todo.set_text("Preheat oven to 350°F")

blocks = await client.blocks.append_children(
    "page-id",
    children=[heading, paragraph, todo]
)

# Append after a specific block
new_block = Paragraph()
new_block.set_text("This comes after the specific block")

await client.blocks.append_children(
    "page-id",
    children=[new_block],
    after="specific-block-id"
)

# Use helper methods
await client.blocks.append_paragraph("page-id", "Some text")
await client.blocks.append_heading("page-id", "Title", level=2)
await client.blocks.append_to_do("page-id", "Task description", checked=False)
```

---

## Update a Block

Updates the content for the specified block based on the block type.

### Endpoint

```
PATCH https://api.notion.com/v1/blocks/{block_id}
```

### Path Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `block_id` | string (UUID) | Yes | Identifier for a Notion block |

### Body Parameters

The body parameters vary based on the block type. Only include the fields you want to update.

**Common parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `archived` | boolean | No | Set to `true` to archive (delete) a block |
| `{type}` | object | No | Type-specific block data |

**Example: Update a to_do block**

```json
{
  "to_do": {
    "rich_text": [
      {
        "text": {
          "content": "Lacinato kale"
        }
      }
    ],
    "checked": false
  }
}
```

**Example: Update a heading to toggleable**

```json
{
  "heading_2": {
    "is_toggleable": true
  }
}
```

### Headers

| Header | Type | Required | Description |
|--------|------|----------|-------------|
| `Authorization` | string | Yes | Bearer `{integration_token}` |
| `Content-Type` | string | Yes | `application/json` |
| `Notion-Version` | string | Yes | The API version to use (latest: `2025-09-03`) |

### Required Capabilities

This endpoint requires the **update content** capability.

### Response

Returns the updated block object.

```json
{
  "object": "block",
  "id": "c02fc1d3-db8b-45c5-a222-27595b15aea7",
  "parent": {
    "type": "page_id",
    "page_id": "59833787-2cf9-4fdf-8782-e53db20768a5"
  },
  "created_time": "2022-03-01T19:05:00.000Z",
  "last_edited_time": "2022-07-06T19:41:00.000Z",
  "created_by": {
    "object": "user",
    "id": "ee5f0f84-409a-440f-983a-a5315961c6e4"
  },
  "last_edited_by": {
    "object": "user",
    "id": "ee5f0f84-409a-440f-983a-a5315961c6e4"
  },
  "has_children": false,
  "archived": false,
  "type": "heading_2",
  "heading_2": {
    "rich_text": [/* ... */],
    "color": "default",
    "is_toggleable": false
  }
}
```

### Update Behavior

**Important notes:**
- The update **replaces the entire value** for a given field
- Omitted fields are **not changed**
- Block children **cannot** be updated with this endpoint (use Append Block Children)
- `child_page` blocks should be updated using the Update Page endpoint
- `child_database` blocks should be updated using the Update Database endpoint

### Toggleable Headings

To add toggle to a heading:
```json
{
  "heading_2": {
    "is_toggleable": true
  }
}
```

To remove toggle from a heading:
- Toggle **cannot** be removed if the heading has children
- All children must be removed first before revoking toggle

### SDK Implementation

```python
async def update(
    self,
    block_id: str,
    **changes
) -> Block:
    """
    Update a block's properties.

    Args:
        block_id: The UUID of the block to update
        **changes: Field values to update (varies by block type)

    Returns:
        Updated Block object

    Raises:
        NotFoundError: If the block doesn't exist or is archived
        PermissionError: If lacking update content capability
        ValueError: If invalid data for block type
    """
    # Get the block type if not provided
    if "type" not in changes:
        block = await self.get(block_id)
        block_type = block.type
    else:
        block_type = changes["type"]

    # Build update payload based on block type
    payload = self._build_update_payload(block_type, changes)

    response = await self._client.request(
        "PATCH",
        f"/blocks/{block_id}",
        json=payload
    )

    return Block.from_dict(response, self._client)

def _build_update_payload(self, block_type: BlockType, changes: dict) -> dict:
    """Build API update payload from changes dict."""
    payload = {}

    # Handle archived status
    if "archived" in changes:
        payload["archived"] = changes["archived"]

    # Get type-specific data
    type_key = BLOCK_TYPE_KEYS.get(block_type, block_type.value)
    type_data = {}

    if block_type == BlockType.TO_DO:
        if "rich_text" in changes or "text" in changes:
            type_data["rich_text"] = changes.get("rich_text", [])
        if "checked" in changes:
            type_data["checked"] = changes["checked"]

    elif block_type in (BlockType.HEADING_1, BlockType.HEADING_2, BlockType.HEADING_3):
        if "rich_text" in changes or "text" in changes:
            type_data["rich_text"] = changes.get("rich_text", [])
        if "is_toggleable" in changes:
            type_data["is_toggleable"] = changes["is_toggleable"]

    # ... handle other block types

    payload[type_key] = type_data
    return payload
```

### Block-Specific Update Examples

**Paragraph:**
```python
await block.update(
    text="New paragraph text",
    color="blue"
)
```

**To-Do:**
```python
await todo_block.update(
    text="Updated task",
    checked=True
)
```

**Heading:**
```python
await heading.update(
    text="New heading",
    is_toggleable=True
)
```

**Code:**
```python
await code_block.update(
    code="print('hello')",
    language="python"
)
```

### Errors

| Status Code | Error | Description |
|-------------|-------|-------------|
| 400 | `bad_request` | Invalid block type or data |
| 400 | `validation_error` | Attempting to remove toggle with children present |
| 403 | `missing_permission` | Integration lacks update content capability |
| 404 | `object_not_found` | Block doesn't exist or is archived |
| 429 | `rate_limited` | Request rate limit exceeded |

### Example Usage

```python
# Update a to-do block
todo = await client.blocks.get("todo-block-id")

await todo.update(
    checked=True,
    text="Completed task!"
)

# Update a heading
heading = await client.blocks.get("heading-block-id")

await heading.update(
    text="Updated Title",
    is_toggleable=True
)

# Archive a block (soft delete)
await block.update(archived=True)

# Restore an archived block
await block.update(archived=False)
```

---

## Delete a Block

Sets a Block object, including page blocks, to archived: true.

### Endpoint

```
DELETE https://api.notion.com/v1/blocks/{block_id}
```

### Path Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `block_id` | string (UUID) | Yes | Identifier for a Notion block |

### Headers

| Header | Type | Required | Description |
|--------|------|----------|-------------|
| `Authorization` | string | Yes | Bearer `{integration_token}` |
| `Notion-Version` | string | Yes | The API version to use (latest: `2025-09-03`) |

### Required Capabilities

This endpoint requires the **update content** capability.

### Response

Returns the archived block object.

```json
{
  "object": "block",
  "id": "7985540b-2e77-4ac6-8615-c3047e36f872",
  "parent": {
    "type": "page_id",
    "page_id": "59833787-2cf9-4fdf-8782-e53db20768a5"
  },
  "created_time": "2022-07-06T19:52:00.000Z",
  "last_edited_time": "2022-07-06T19:52:00.000Z",
  "created_by": {
    "object": "user",
    "id": "0c3e9826-b8f7-4f73-927d-2caaf86f1103"
  },
  "last_edited_by": {
    "object": "user",
    "id": "ee5f0f84-409a-440f-983a-a5315961c6e4"
  },
  "has_children": false,
  "archived": true,
  "type": "paragraph",
  "paragraph": {
    "rich_text": [],
    "color": "default"
  }
}
```

### Behavior

- The block is moved to the **Trash** in the Notion UI
- The block can still be accessed and restored via the API
- Deleting a parent block **also deletes all its children**
- The block is **not permanently deleted** (can be restored)

### Restoration

To restore a deleted block:
```python
# Using the update endpoint
await block.update(archived=False)
```

### SDK Implementation

```python
async def delete(self, block_id: str) -> Block:
    """
    Archive (soft delete) a block.

    Args:
        block_id: The UUID of the block to delete

    Returns:
        The archived Block object

    Raises:
        NotFoundError: If the block doesn't exist
        PermissionError: If lacking update content capability

    Note:
        This is a soft delete. The block is moved to trash and can be restored.
        Use update(block_id, archived=False) to restore.
    """
    response = await self._client.request(
        "DELETE",
        f"/blocks/{block_id}"
    )

    return Block.from_dict(response, self._client)

async def restore(self, block_id: str) -> Block:
    """
    Restore an archived block.

    Args:
        block_id: The UUID of the block to restore

    Returns:
        The restored Block object
    """
    return await self.update(block_id, archived=False)
```

### Cascading Deletes

When a parent block is deleted:
- All child blocks are **automatically** deleted
- This includes nested children at any depth
- The children are **not** returned in the response

**Example:**
```
Page
├── Heading
├── Paragraph
│   └── Nested Paragraph  ← Deleted when Paragraph is deleted
└── Bulleted List         ← Deleted when Page is deleted
    └── Nested Item       ← Deleted when List is deleted
```

### Errors

| Status Code | Error | Description |
|-------------|-------|-------------|
| 403 | `missing_permission` | Integration lacks update content capability |
| 404 | `object_not_found` | Block doesn't exist or integration doesn't have access |
| 429 | `rate_limited` | Request rate limit exceeded |

### Example Usage

```python
# Delete a single block
archived_block = await client.blocks.delete("block-id")

# Delete using the block's method
block = await client.blocks.get("block-id")
await block.delete()

# Restore a deleted block
restored = await client.blocks.restore("block-id")

# Or using update
restored = await client.blocks.update("block-id", archived=False)
```

---

## Common Patterns

### Recursively Fetch All Block Content

```python
async def get_block_tree(self, block_id: str) -> Block:
    """
    Fetch a block with all its descendants.

    Returns a Block object with all children loaded.
    """
    # Get the block
    block = await self.get(block_id)

    # If it has children, recursively fetch them
    if block.has_children:
        children_response = await self.get_children(block_id)

        block.children = []
        for child_data in children_response.results:
            child = await self.get_block_tree(str(child.id))
            block.children.append(child)

    return block
```

### Batch Block Operations

```python
async def append_many_blocks(
    self,
    block_id: str,
    blocks: List[Block],
    batch_size: int = 100
) -> List[Block]:
    """
    Append blocks in batches to handle large numbers.

    Args:
        block_id: Parent block ID
        blocks: List of blocks to append
        batch_size: Number of blocks per batch (max: 100)

    Returns:
        List of all created blocks
    """
    all_created = []

    for i in range(0, len(blocks), batch_size):
        batch = blocks[i:i + batch_size]
        created = await self.append_children(block_id, batch)
        all_created.extend(created)

    return all_created
```

### Find Blocks by Type

```python
async def find_blocks_by_type(
    self,
    block_id: str,
    block_type: BlockType
) -> List[Block]:
    """
    Find all blocks of a specific type within a block tree.

    Args:
        block_id: Root block ID to search from
        block_type: Type of blocks to find

    Returns:
        List of matching blocks
    """
    found = []

    async def search(current_id: str):
        children = await self.get_all_children(current_id)

        for child in children:
            if child.type == block_type:
                found.append(child)

            if child.has_children:
                await search(str(child.id))

    await search(block_id)
    return found
```

### Replace Block Content

```python
async def replace_block_children(
    self,
    block_id: str,
    new_blocks: List[Block]
) -> List[Block]:
    """
    Replace all children of a block with new blocks.

    This is done by deleting existing children and appending new ones.
    """
    # Get existing children
    existing = await self.get_all_children(block_id)

    # Delete all existing children
    for child in existing:
        await child.delete()

    # Append new blocks
    return await self.append_children(block_id, new_blocks)
```

---

## Error Handling

### Common Error Responses

```python
class BlockAPIError(Exception):
    """Base exception for block API errors."""
    pass

class BlockNotFoundError(BlockAPIError):
    """Block doesn't exist or no access."""
    pass

class BlockPermissionError(BlockAPIError):
    """Missing required capability."""
    pass

class BlockValidationError(BlockAPIError):
    """Invalid block data or structure."""
    pass

async def safe_block_operation(func):
    """Decorator for handling block API errors."""
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except HTTPError as e:
            if e.status == 404:
                raise BlockNotFoundError(f"Block not found: {e}")
            elif e.status == 403:
                raise BlockPermissionError(f"Permission denied: {e}")
            elif e.status == 400:
                raise BlockValidationError(f"Invalid request: {e}")
            elif e.status == 429:
                # Handle rate limiting with retry
                await asyncio.sleep(1)
                return await func(*args, **kwargs)
            else:
                raise BlockAPIError(f"Unexpected error: {e}")
    return wrapper
```

---

## Best Practices

1. **Pagination**: Always handle pagination when retrieving block children
2. **Batching**: Append blocks in batches of up to 100 for efficiency
3. **Error Handling**: Implement proper error handling for 404, 403, and 429 responses
4. **Rate Limiting**: Respect rate limits and implement retry logic
5. **Type Validation**: Validate block types before API calls
6. **Immutability**: Remember blocks cannot be moved after creation
7. **Cascading Deletes**: Be aware that deleting a parent deletes all children
8. **Capabilities**: Ensure your integration has the required capabilities

---

## Related Documentation

- [Blocks Overview](./blocks-overview.md) - Block concepts and structure
- [Block Types Reference](./block-types.md) - All block type specifications
- [Block Implementation Guide](./blocks-implementation.md) - SDK implementation details
- [Users API](../users-api.md) - User information for created_by/last_edited_by
- [Rich Text Reference](./rich-text.md) - Rich text formatting system
