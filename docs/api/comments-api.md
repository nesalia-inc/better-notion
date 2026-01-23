# Comments API Reference

Complete API reference for all comment-related operations in the Notion API.

## Table of Contents

1. [Create a Comment](#create-a-comment)
2. [Retrieve a Comment](#retrieve-a-comment)
3. [List Comments](#list-comments)

---

## Create a Comment

Creates a comment in a page, block, or existing discussion thread.

### Endpoint

```
POST https://api.notion.com/v1/comments
```

### Body Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `parent` | object | Conditional* | Page or block parent |
| `discussion_id` | string | Conditional* | Discussion thread UUID |
| `rich_text` | array | Yes | Rich text content |
| `attachments` | array | No | File attachments (max 3) |
| `display_name` | object | No | Custom display name |

\* Either `parent` or `discussion_id` must be provided (not both).

### Parent Object (for new discussion)

**Page parent:**
```json
{
  "parent": {
    "page_id": "5c6a28216bb14a7eb6e1c50111515c3d"
  }
}
```

**Block parent:**
```json
{
  "parent": {
    "block_id": "5d4ca33c-d6b7-4675-93d9-84b70af45d1c"
  }
}
```

### Rich Text Object

```json
{
  "rich_text": [
    {
      "text": {
        "content": "Hello world"
      }
    }
  ]
}
```

**Rich text supports:**
- Text formatting (bold, italic, underline, strikethrough, code)
- Links
- Mentions (@users, @pages, @databases)
- Equations

### Attachments

```json
{
  "attachments": [
    {
      "file_upload_id": "48656c6c-6f20-576f-726c-64212048692e"
    }
  ]
}
```

**Note:** Max 3 attachments per comment.

### Display Name

```json
{
  "display_name": {
    "type": "integration"
  }
}
```

**Display name types:**
- `integration` - Integration name
- `user` - User name (default)
- `custom` - Custom name

### Headers

| Header | Type | Required | Description |
|--------|------|----------|-------------|
| `Authorization` | string | Yes | Bearer `{integration_token}` |
| `Content-Type` | string | Yes | `application/json` |
| `Notion-Version` | string | Yes | The API version to use (latest: `2025-09-03`) |

### Required Capabilities

This endpoint requires the **insert comments** capability.

**Important:** Comment capabilities are off by default. Enable them in the integration dashboard.

### Response

Returns the created Comment object.

```json
{
  "object": "comment",
  "id": "249911a-125e-803e-a164-001cf338b8ec",
  "parent": {
    "type": "block_id",
    "block_id": "247vw11a-125e-8053-8e73-d3b3ed4f5768"
  },
  "discussion_id": "1mv7b911a-125e-80df-8c9e-001c179f63ef",
  "created_time": "2025-08-06T20:36:00.000Z",
  "last_edited_time": "2025-08-06T20:36:00.000Z",
  "created_by": {
    "object": "user",
    "id": "2092e755-4912-81f0-98dd-0002ad4ec952"
  },
  "rich_text": [
    {
      "type": "text",
      "text": {
        "content": "Hello world",
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
      "plain_text": "Hello world",
      "href": null
    }
  ],
  "attachments": [
    {
      "category": "image",
      "file": {
        "url": "https://s3.us-west-2.amazonaws.com/...",
        "expiry_time": "2025-06-10T21:58:51.599Z"
      }
    }
  ],
  "display_name": {
    "type": "integration",
    "resolved_name": "Public Integration"
  }
}
```

### SDK Implementation

```python
async def create(
    self,
    *,
    parent: Optional[str] = None,
    discussion_id: Optional[str] = None,
    rich_text: List[dict],
    attachments: Optional[List[dict]] = None,
    display_name: Optional[str] = None
) -> Comment:
    """
    Create a comment.

    Args:
        parent: Page ID or block ID (for new discussion)
        discussion_id: Discussion thread ID (to reply to thread)
        rich_text: Comment content (rich text array)
        attachments: Optional file attachments
        display_name: Optional display name type

    Returns:
        Created Comment object

    Raises:
        ValueError: If neither parent nor discussion_id provided
        PermissionError: If lacking insert comments capability

    Note:
        Exactly one of parent or discussion_id must be provided.
    """
    if not parent and not discussion_id:
        raise ValueError("Either parent or discussion_id must be provided")
    if parent and discussion_id:
        raise ValueError("Only one of parent or discussion_id can be provided")

    payload = {"rich_text": rich_text}

    if parent:
        # Determine if it's a page or block
        parent_obj = {"type": "page_id", "page_id": parent}
        payload["parent"] = parent_obj

    if discussion_id:
        payload["discussion_id"] = discussion_id

    if attachments:
        payload["attachments"] = attachments

    if display_name:
        payload["display_name"] = {"type": display_name}

    response = await self._client.request(
        "POST",
        "/comments",
        json=payload
    )

    return Comment.from_dict(response, self._client)
```

### Errors

| Status Code | Error | Description |
|-------------|-------|-------------|
| 400 | `bad_request` | Invalid rich text or both parent and discussion_id |
| 403 | `missing_permission` | Integration lacks insert comments capability |
| 404 | `object_not_found` | Page/block/discussion doesn't exist |
| 429 | `rate_limited` | Request rate limit exceeded |

### Example Usage

```python
# Create comment on page
comment = await client.comments.create(
    parent="page-id-here",
    rich_text=[{
        "text": {"content": "This looks great!"}
    }],
    display_name="integration"
)

# Create comment on block
comment = await client.comments.create(
    parent="block-id-here",
    rich_text=[{
        "text": {"content": "Please review this section."}
    }]
)

# Reply to discussion thread
comment = await client.comments.create(
    discussion_id="discussion-id-here",
    rich_text=[{
        "text": {"content": "I agree with the above."}
    }]
)

# Create comment with attachment
comment = await client.comments.create(
    parent="page-id-here",
    rich_text=[{
        "text": {"content": "Here's the screenshot:"}
    }],
    attachments=[{
        "file_upload_id": "file-upload-id-here"
    }]
)

# Rich text with formatting
comment = await client.comments.create(
    parent="page-id-here",
    rich_text=[
        {
            "text": {"content": "This is "},
            "annotations": {"bold": False}
        },
        {
            "text": {"content": "bold"},
            "annotations": {"bold": True}
        },
        {
            "text": {"content": " text."},
            "annotations": {"bold": False}
        }
    ]
)
```

---

## Retrieve a Comment

Retrieves a Comment object using its ID.

### Endpoint

```
GET https://api.notion.com/v1/comments/{comment_id}
```

### Path Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `comment_id` | string (UUID) | Yes | Identifier for a Notion comment |

### Headers

| Header | Type | Required | Description |
|--------|------|----------|-------------|
| `Authorization` | string | Yes | Bearer `{integration_token}` |
| `Notion-Version` | string | Yes | The API version to use (latest: `2025-09-03`) |

### Required Capabilities

This endpoint requires the **read comments** capability.

**Important:** Comment capabilities are off by default. Enable them in the integration dashboard.

### Response

Returns a Comment object.

```json
{
  "object": "comment",
  "id": "249911a-125e-803e-a164-001cf338b8ec",
  "parent": {
    "type": "block_id",
    "block_id": "247vw11a-125e-8053-8e73-d3b3ed4f5768"
  },
  "discussion_id": "1mv7b911a-125e-80df-8c9e-001c179f63ef",
  "created_time": "2025-08-06T20:36:00.000Z",
  "last_edited_time": "2025-08-06T20:36:00.000Z",
  "created_by": {
    "object": "user",
    "id": "2092e755-4912-81f0-98dd-0002ad4ec952"
  },
  "rich_text": [
    {
      "type": "text",
      "text": {
        "content": "hello there",
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
      "plain_text": "hello there",
      "href": null
    }
  ],
  "display_name": {
    "type": "integration",
    "resolved_name": "int"
  }
}
```

### SDK Implementation

```python
async def get(self, comment_id: str) -> Comment:
    """
    Retrieve a comment by ID.

    Args:
        comment_id: The UUID of the comment

    Returns:
        Comment object

    Raises:
        NotFoundError: If comment doesn't exist
        PermissionError: If lacking read comments capability
    """
    response = await self._client.request(
        "GET",
        f"/comments/{comment_id}"
    )

    return Comment.from_dict(response, self._client)
```

### Errors

| Status Code | Error | Description |
|-------------|-------|-------------|
| 403 | `missing_permission` | Integration lacks read comments capability |
| 404 | `object_not_found` | Comment doesn't exist |
| 429 | `rate_limited` | Request rate limit exceeded |

### Example Usage

```python
# Get a comment
comment = await client.comments.get("comment-id-here")

print(f"Comment: {comment.plain_text}")
print(f"Author: {comment.created_by.id}")
print(f"Created: {comment.created_time}")
print(f"Discussion: {comment.discussion_id}")

# Check attachments
if comment.attachments:
    for attachment in comment.attachments:
        print(f"Attachment: {attachment.category} - {attachment.file.url}")
```

---

## List Comments

Retrieves a list of un-resolved Comment objects from a page or block.

### Endpoint

```
GET https://api.notion.com/v1/comments
```

### Query Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `block_id` | string | Yes | Identifier for a Notion block or page |
| `start_cursor` | string | No | Cursor for pagination |
| `page_size` | integer | No | Number of results (max: 100) |

**Note:** The `block_id` parameter accepts both page IDs and block IDs.

### Headers

| Header | Type | Required | Description |
|--------|------|----------|-------------|
| `Authorization` | string | Yes | Bearer `{integration_token}` |
| `Notion-Version` | string | Yes | The API version to use (latest: `2025-09-03`) |

### Required Capabilities

This endpoint requires the **read comments** capability.

**Important:** Comment capabilities are off by default. Enable them in the integration dashboard.

### Response

Returns a paginated list of Comment objects.

```json
{
  "object": "list",
  "results": [
    {
      "object": "comment",
      "id": "94cc56ab-9f02-409d-9f99-1037e9fe502f",
      "parent": {
        "type": "page_id",
        "page_id": "5c6a2821-6bb1-4a7e-b6e1-c50111515c3d"
      },
      "discussion_id": "f1407351-36f5-4c49-a13c-49f8ba11776d",
      "created_time": "2022-07-15T16:52:00.000Z",
      "last_edited_time": "2022-07-15T19:16:00.000Z",
      "created_by": {
        "object": "user",
        "id": "9b15170a-9941-4297-8ee6-83fa7649a87a"
      },
      "rich_text": [
        {
          "type": "text",
          "text": {
            "content": "Single comment",
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
          "plain_text": "Single comment",
          "href": null
        }
      ]
    }
  ],
  "next_cursor": null,
  "has_more": false,
  "type": "comment"
}
```

### Pagination

The endpoint uses cursor-based pagination:

1. First request: Call without `start_cursor` to get the first page
2. Check `has_more` in the response
3. If `has_more` is `true`, use `next_cursor` as `start_cursor` for the next request
4. Repeat until `has_more` is `false`

**Important:** Only un-resolved comments are returned. Resolved comments are not included in the results.

### SDK Implementation

```python
async def list(
    self,
    block_id: str,
    *,
    page_size: int = 100,
    start_cursor: Optional[str] = None
) -> PaginatedResponse:
    """
    List comments for a page or block.

    Args:
        block_id: Page ID or block ID
        page_size: Number of comments per page (max: 100)
        start_cursor: Pagination cursor

    Returns:
        PaginatedResponse with Comment objects

    Raises:
        NotFoundError: If page/block doesn't exist
        PermissionError: If lacking read comments capability
    """
    params = {"block_id": block_id, "page_size": page_size}

    if start_cursor:
        params["start_cursor"] = start_cursor

    response = await self._client.request(
        "GET",
        "/comments",
        params=params
    )

    return PaginatedResponse(
        results=[
            Comment.from_dict(comment_data, self._client)
            for comment_data in response.get("results", [])
        ],
        has_more=response.get("has_more", False),
        next_cursor=response.get("next_cursor")
    )

async def list_all(self, block_id: str) -> List[Comment]:
    """
    List all comments with automatic pagination.

    Args:
        block_id: Page ID or block ID

    Returns:
        List of all Comment objects
    """
    all_comments = []
    cursor = None
    has_more = True

    while has_more:
        response = await self.list(
            block_id,
            start_cursor=cursor
        )

        all_comments.extend(response.results)
        has_more = response.has_more
        cursor = response.next_cursor

    return all_comments
```

### Errors

| Status Code | Error | Description |
|-------------|-------|-------------|
| 400 | `bad_request` | Invalid block_id |
| 403 | `missing_permission` | Integration lacks read comments capability |
| 404 | `object_not_found` | Page/block doesn't exist |
| 429 | `rate_limited` | Request rate limit exceeded |

### Example Usage

```python
# Get first page of comments
comments = await client.comments.list("page-id")

for comment in comments.results:
    print(f"{comment.plain_text}")

# Get all comments with automatic pagination
all_comments = await client.comments.list_all("page-id")

print(f"Total comments: {len(all_comments)}")

# Manual pagination
cursor = None
while True:
    response = await client.comments.list(
        "page-id",
        start_cursor=cursor
    )

    for comment in response.results:
        process_comment(comment)

    if not response.has_more:
        break

    cursor = response.next_cursor

# Group by discussion
from collections import defaultdict

comments_by_discussion = defaultdict(list)
for comment in all_comments:
    comments_by_discussion[comment.discussion_id].append(comment)

# Display discussion threads
for discussion_id, thread_comments in comments_by_discussion.items():
    print(f"\nDiscussion {discussion_id}:")
    for comment in thread_comments:
        print(f"  - {comment.plain_text}")
```

---

## Common Patterns

### Get Comments for Discussion Thread

```python
async def get_discussion_comments(
    self,
    discussion_id: str
) -> List[Comment]:
    """
    Get all comments in a discussion thread.

    Args:
        discussion_id: The discussion thread ID

    Returns:
        List of comments in the thread, sorted chronologically
    """
    # Get all comments from parent page/block
    # Filter by discussion_id
    pass
```

### Create Comment with Mention

```python
async def create_with_mention(
    self,
    parent: str,
    text: str,
    mention_user_id: str
) -> Comment:
    """
    Create a comment with a user mention.

    Args:
        parent: Page or block ID
        text: Comment text
        mention_user_id: User ID to mention

    Returns:
        Created Comment object
    """
    rich_text = [
        {
            "type": "text",
            "text": {"content": f"{text} "}
        },
        {
            "type": "mention",
            "mention": {
                "type": "user",
                "user": {"id": mention_user_id}
            }
        }
    ]

    return await self.create(
        parent=parent,
        rich_text=rich_text
    )
```

### Create Comment with Link

```python
async def create_with_link(
    self,
    parent: str,
    text: str,
    url: str
) -> Comment:
    """Create a comment with a hyperlink."""
    rich_text = [
        {
            "type": "text",
            "text": {"content": f"{text} "}
        },
        {
            "type": "text",
            "text": {
                "content": "click here",
                "link": {"url": url}
            }
        }
    ]

    return await self.create(
        parent=parent,
        rich_text=rich_text
    )
```

### Create Comment with Attachment

```python
async def create_with_attachment(
    self,
    parent: str,
    text: str,
    file_upload_id: str
) -> Comment:
    """Create a comment with file attachment."""
    return await self.create(
        parent=parent,
        rich_text=[{
            "type": "text",
            "text": {"content": text}
        }],
        attachments=[{
            "file_upload_id": file_upload_id
        }]
    )
```

### Bot Comment Helper

```python
async def bot_comment(
    self,
    parent: str,
    message: str
) -> Comment:
    """
    Create a bot comment with integration display name.

    Args:
        parent: Page or block ID
        message: Comment message

    Returns:
        Created Comment object
    """
    return await self.create(
        parent=parent,
        rich_text=[{
            "type": "text",
            "text": {"content": message}
        }],
        display_name="integration"
    )
```

### Format Rich Text

```python
class RichTextBuilder:
    """Helper for building rich text arrays."""

    @staticmethod
    def text(content: str, **annotations) -> dict:
        """Create a text segment."""
        return {
            "type": "text",
            "text": {"content": content},
            "annotations": {
                "bold": annotations.get("bold", False),
                "italic": annotations.get("italic", False),
                "strikethrough": annotations.get("strikethrough", False),
                "underline": annotations.get("underline", False),
                "code": annotations.get("code", False),
                "color": annotations.get("color", "default")
            }
        }

    @staticmethod
    def link(content: str, url: str) -> dict:
        """Create a link segment."""
        return {
            "type": "text",
            "text": {
                "content": content,
                "link": {"url": url}
            }
        }

    @staticmethod
    def mention_user(user_id: str) -> dict:
        """Create a user mention."""
        return {
            "type": "mention",
            "mention": {
                "type": "user",
                "user": {"id": user_id}
            }
        }

    @staticmethod
    def mention_page(page_id: str) -> dict:
        """Create a page mention."""
        return {
            "type": "mention",
            "mention": {
                "type": "page",
                "page": {"id": page_id}
            }
        }

# Usage
rich_text = [
    RichTextBuilder.text("This is "),
    RichTextBuilder.text("bold", bold=True),
    RichTextBuilder.text(" and "),
    RichTextBuilder.link("click here", "https://example.com")
]

comment = await client.comments.create(
    parent="page-id",
    rich_text=rich_text
)
```

---

## Error Handling

### Comment Error Classes

```python
class CommentAPIError(Exception):
    """Base exception for comment API errors."""
    pass

class CommentNotFoundError(CommentAPIError):
    """Comment doesn't exist."""
    pass

class CommentPermissionError(CommentAPIError):
    """Missing required capability."""
    pass

class CommentValidationError(CommentAPIError):
    """Invalid comment data."""
    pass

async def handle_comment_errors(func):
    """Decorator for comment API error handling."""
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except HTTPError as e:
            if e.status == 404:
                raise CommentNotFoundError(f"Comment not found: {e}")
            elif e.status == 403:
                raise CommentPermissionError(f"Permission denied: {e}")
            elif e.status == 400:
                raise CommentValidationError(f"Invalid request: {e}")
            elif e.status == 429:
                await asyncio.sleep(1)
                return await func(*args, **kwargs)
            else:
                raise CommentAPIError(f"Unexpected error: {e}")
    return wrapper
```

---

## Best Practices

1. **Enable Capabilities** - Ensure insert/read comments are enabled in integration dashboard
2. **Rich Text** - Use rich text for formatting and mentions
3. **Attachments** - Limit to 3 attachments per comment
4. **Display Names** - Use "integration" type for bot comments
5. **Pagination** - Handle has_more/next_cursor for large comment lists
6. **Discussion Threads** - Use discussion_id to reply to existing threads
7. **Error Handling** - Handle 403 for missing comment capabilities
8. **URL Expiration** - Be aware attachment URLs expire
9. **Mentions** - Use mentions to notify users
10. **Comment Organization** - Create comments at appropriate level (page vs block)

---

## Related Documentation

- [Comments Overview](./comments.md) - Comment concepts and structure
- [Users API](./users-api.md) - Comment author information
- [Rich Text Objects](./rich-text-objects.md) - Text formatting in comments
- [Blocks API](./block/blocks-api.md) - Comments on blocks
- [Pages API](./pages/pages-api.md) - Comments on pages
