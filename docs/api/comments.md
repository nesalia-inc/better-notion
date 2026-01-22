# Comments

## Overview

**Comments** allow users and integrations to add discussions to Notion pages and blocks. Comments are organized into discussion threads and support rich text formatting, mentions, attachments, and custom display names.

**Important:** Integrations must have **read comments** or **insert comments** capabilities to interact with the Comment object via the API.

## Comment Object Structure

### Example Comment Object

```json
{
  "object": "comment",
  "id": "7a793800-3e55-4d5e-8009-2261de026179",
  "parent": {
    "type": "page_id",
    "page_id": "5c6a2821-6bb1-4a7e-b6e1-c50111515c3d"
  },
  "discussion_id": "f4be6752-a539-4da2-a8a9-c3953e13bc0b",
  "created_time": "2022-07-15T21:17:00.000Z",
  "last_edited_time": "2022-07-15T21:17:00.000Z",
  "created_by": {
    "object": "user",
    "id": "e450a39e-9051-4d36-bc4e-8581611fc592"
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
    "type": "user",
    "resolved_name": "Avo Cado"
  }
}
```

## Comment Object Fields

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `object` | string | Always `"comment"` | `"comment"` |
| `id` | string (UUIDv4) | Unique identifier | `"7a793800-..."` |
| `parent` | object | Parent information (page or block) | `{ "type": "page_id", ...}` |
| `discussion_id` | string (UUIDv4) | Discussion thread identifier | `"f4be6752-..."` |
| `created_time` | string (ISO 8601) | Creation timestamp | `"2022-07-15T21:17:00.000Z"` |
| `last_edited_time` | string (ISO 8601) | Last update timestamp | `"2022-07-15T21:17:00.000Z"` |
| `created_by` | PartialUser | User who created the comment | `{ "object": "user", "id": "..."}` |
| `rich_text` | array of rich text objects | Comment content (supports formatting, links, mentions) | `[/* rich text */]` |
| `attachments` | array of CommentAttachment | File attachments (max 3) | `[/* attachments */]` |
| `display_name` | CommentDisplayName | Custom display name (overrides default author) | `{ "type": "user", ...}` |

## Parent Object

Comments can only be parented by pages or blocks:

### Page Parent
```json
{
  "type": "page_id",
  "page_id": "5c6a2821-6bb1-4a7e-b6e1-c50111515c3d"
}
```

### Block Parent
```json
{
  "type": "block_id",
  "block_id": "5d4ca33c-d6b7-4675-93d9-84b70af45d1c"
}
```

**Note:** Comments are only supported on pages and blocks, not on databases.

## Discussion Threads

### Discussion ID

The `discussion_id` field uniquely identifies a discussion thread. All comments in the same thread share the same `discussion_id`.

**When creating a comment:**
- Adding a comment to a page/block without existing comments → Creates a new discussion thread
- The comment's `discussion_id` is the new thread's identifier

**When retrieving comments:**
- Comments are returned in **ascending chronological order** (oldest first)
- All comments in the same discussion have the same `discussion_id`

## Rich Text Content

Comments support rich text formatting, including:

- **Text formatting** - Bold, italic, strikethrough, underline, code
- **Colors** - All text and background colors
- **Links** - URLs with optional custom text
- **Mentions** - @users, @dates, @pages, @databases
- **Emojis** - Inline emoji characters

See [Rich Text Objects](./rich-text-objects.md) for complete details on rich text formatting.

### Example Rich Text Comment

```json
{
  "rich_text": [
    {
      "type": "text",
      "text": {
        "content": "Check out this ",
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
      "plain_text": "Check out this ",
      "href": null
    },
    {
      "type": "text",
      "text": {
        "content": "helpful guide",
        "link": {
          "type": "url",
          "url": "https://example.com/guide"
        }
      },
      "annotations": {
        "bold": true,
        "italic": false,
        "strikethrough": false,
        "underline": false,
        "code": false,
        "color": "blue"
      },
      "plain_text": "helpful guide",
      "href": "https://example.com/guide"
    }
  ]
}
```

## Attachments

Comments can include file attachments (maximum **3 attachments** per comment).

### Attachment Categories

| Category | Description |
|----------|-------------|
| `audio` | Audio files (MP3, WAV, etc.) |
| `image` | Image files (PNG, JPG, etc.) |
| `pdf` | PDF documents |
| `productivity` | Productivity files (docs, sheets, etc.) |
| `video` | Video files (MP4, MOV, etc.) |

### Creating Attachments (Request Format)

When creating a comment with attachments, use the `attachments` parameter:

**Request Format:**

```json
{
  "parent": {
    "page_id": "d0a1ffaf-a4d8-4acf-a1ed-abae6e110418"
  },
  "rich_text": [
    {
      "text": {
        "content": "Thanks for the helpful page!"
      }
    }
  ],
  "attachments": [
    {
      "type": "file_upload",
      "file_upload_id": "2e2cdb8b-9897-4a6c-a935-82922b1cfb87"
    }
  ]
}
```

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `file_upload_id` | string (UUID) | ID of a File Upload with status "uploaded" |
| `type` | string (optional) | Must be `"file_upload"` if provided |

**Important:** After uploading a file using the File Upload API, use its ID to attach it to a comment.

### Retrieving Attachments (Response Format)

When retrieving comments, attachments include these fields:

| Field | Type | Description |
|-------|------|-------------|
| `category` | string (enum) | Attachment category: `"audio"`, `"image"`, `"pdf"`, `"productivity"`, `"video"` |
| `file.url` | string | Temporary download URL (expires at `expiry_time`) |
| `file.expiry_time` | string (ISO 8601) | URL expiration timestamp |

```json
{
  "attachments": [
    {
      "category": "video",
      "file": {
        "url": "https://s3.us-west-2.amazonaws.com/...",
        "expiry_time": "2025-06-10T21:26:03.070Z"
      }
    }
  ]
}
```

**Note:** File URLs are temporary and expire. For permanent access, retrieve the comment again to get a fresh URL.

### Attachment Display

In the Notion app, attachments are displayed based on their detected category:
- `.png` files → Inline images
- `.mp4` files → Embedded video player
- Other files → Download blocks

## Comment Display Name

The `display_name` field overrides the default author name shown for a comment.

### Creating with Display Name (Request Format)

**Request Format:**

```json
{
  "parent": {
    "page_id": "d0a1ffaf-a4d8-4acf-a1ed-abae6e110418"
  },
  "rich_text": [
    {
      "text": {
        "content": "Thanks for checking us out!"
      }
    }
  ],
  "display_name": {
    "type": "custom",
    "custom": {
      "name": "Notion Bot"
    }
  }
}
```

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `type` | string (enum) | Display name type: `"integration"`, `"user"`, or `"custom"` |
| `custom` | object | If `type` is `"custom"`, must include `{ "name": "<Custom Name>" }` |

**Type Values:**

| Type | Description |
|------|-------------|
| `"integration"` | Uses the integration's name |
| `"user"` | Uses the name of the user who authenticated (for Public Integrations) |
| `"custom"` | Custom name specified in `custom.name` |

### Display Name Response Format

When retrieving a comment, display_name includes:

| Field | Type | Description |
|-------|------|-------------|
| `type` | string (enum) | The display name type |
| `resolved_name` | string | The actual display name shown in UI |

```json
{
  "display_name": {
    "type": "custom",
    "resolved_name": "Notion Bot"
  }
}
```

## Working with Comments

### Retrieve Comments

**Endpoint:** Retrieve a page or block's comments (Notion API documentation)

**Returns:** Array of comment objects in **ascending chronological order** (oldest first)

### Create Comment

**Endpoint:** Create a comment on a page or block (Notion API documentation)

**Required Parameters:**
- `parent` - Page or block to comment on
- `rich_text` - Comment content (rich text array)

**Optional Parameters:**
- `attachments` - File attachments (max 3)
- `display_name` - Custom display name

**Response:** The newly created Comment object

### Update Comment

Comments can be edited after creation. The `last_edited_time` field updates to reflect the most recent edit.

### Delete Comment

Comments can be removed from discussions.

## SDK Architecture

### Comment Class

```python
@dataclass
class Comment:
    """Notion comment object."""
    object: str = "comment"
    id: UUID = None
    parent: CommentParent = None
    discussion_id: UUID = None
    created_time: datetime = None
    last_edited_time: datetime = None
    created_by: PartialUser = None
    rich_text: List[RichTextObject] = field(default_factory=list)
    attachments: List["CommentAttachment"] = field(default_factory=list)
    display_name: "CommentDisplayName" = None

    @classmethod
    def from_dict(cls, data: dict, client: Any = None) -> "Comment":
        """Parse comment from API response."""
        instance = cls()

        instance.object = data.get("object")
        instance.id = UUID(data.get("id"))

        # Parent
        parent_data = data.get("parent", {})
        if parent_data.get("type") == "page_id":
            instance.parent = CommentPageParent(
                page_id=UUID(parent_data.get("page_id"))
            )
        elif parent_data.get("type") == "block_id":
            instance.parent = CommentBlockParent(
                block_id=UUID(parent_data.get("block_id"))
            )

        # Discussion
        instance.discussion_id = UUID(data.get("discussion_id"))

        # Timestamps
        instance.created_time = _parse_datetime(data.get("created_time"))
        instance.last_edited_time = _parse_datetime(data.get("last_edited_time"))

        # Created by
        created_by_data = data.get("created_by", {})
        instance.created_by = PartialUser(
            id=UUID(created_by_data.get("id")),
            name=created_by_data.get("name")
        )

        # Rich text
        instance.rich_text = RichTextParser.parse_array(
            data.get("rich_text", [])
        )

        # Attachments
        attachments_data = data.get("attachments", [])
        instance.attachments = [
            CommentAttachment.from_dict(att) for att in attachments_data
        ]

        # Display name
        display_name_data = data.get("display_name", {})
        instance.display_name = CommentDisplayName.from_dict(display_name_data)

        return instance

    @property
    def plain_text(self) -> str:
        """Get comment content as plain text."""
        return "".join(rt.plain_text for rt in self.rich_text)

    @property
    def is_edited(self) -> bool:
        """Whether comment has been edited since creation."""
        return self.last_edited_time != self.created_time

    async def refresh(self) -> "Comment":
        """Refresh comment data from API."""
        if not self._client:
            raise RuntimeError("Cannot refresh without client")

        updated = await self._client.comments.get(
            comment_id=str(self.id)
        )

        # Update fields
        self.last_edited_time = updated.last_edited_time
        self.rich_text = updated.rich_text
        self.attachments = updated.attachments

        return self

    async def edit(self, rich_text: List[dict]) -> "Comment":
        """Edit comment content."""
        if not self._client:
            raise RuntimeError("Cannot edit without client")

        updated = await self._client.comments.update(
            comment_id=str(self.id),
            rich_text=rich_text
        )

        # Update local instance
        self.rich_text = RichTextParser.parse_array(rich_text)
        self.last_edited_time = datetime.now(timezone.utc)

        return self

    async def delete(self) -> None:
        """Delete the comment."""
        if not self._client:
            raise RuntimeError("Cannot delete without client")

        await self._client.comments.delete(str(self.id))
```

### CommentAttachment Class

```python
class AttachmentCategory(str, Enum):
    """Comment attachment categories."""
    AUDIO = "audio"
    IMAGE = "image"
    PDF = "pdf"
    PRODUCTIVITY = "productivity"
    VIDEO = "video"

@dataclass
class CommentAttachment:
    """File attachment in a comment."""
    category: AttachmentCategory
    url: str
    expiry_time: datetime

    @classmethod
    def from_dict(cls, data: dict) -> "CommentAttachment":
        """Parse attachment from API response."""
        file_data = data.get("file", {})

        return cls(
            category=AttachmentCategory(data.get("category")),
            url=file_data.get("url", ""),
            expiry_time=_parse_datetime(file_data.get("expiry_time"))
        )

    @property
    def is_expired(self) -> bool:
        """Check if the download URL has expired."""
        return datetime.now(timezone.utc) > self.expiry_time

    async def refresh_url(self) -> str:
        """Refresh the download URL by re-fetching the comment."""
        if not self._client:
            raise RuntimeError("Cannot refresh without client")

        comment = await self._client.comments.get(
            comment_id=str(self._parent_comment_id)
        )

        # Find this attachment
        for att in comment.attachments:
            if att.category == self.category:
                self.url = att.url
                self.expiry_time = att.expiry_time
                break

        return self.url
```

### CommentDisplayName Class

```python
class DisplayNameType(str, Enum):
    """Comment display name types."""
    INTEGRATION = "integration"
    USER = "user"
    CUSTOM = "custom"

@dataclass
class CommentDisplayName:
    """Display name for a comment author."""
    type: DisplayNameType
    resolved_name: str

    @classmethod
    def from_dict(cls, data: dict) -> "CommentDisplayName":
        """Parse display name from API response."""
        name_type = DisplayNameType(data.get("type"))
        resolved = data.get("resolved_name")

        return cls(type=name_type, resolved_name=resolved)

    @classmethod
    def for_custom(cls, name: str) -> "CommentDisplayName":
        """Create a custom display name."""
        return cls(
            type=DisplayNameType.CUSTOM,
            resolved_name=name
        )

    @classmethod
    def for_integration(cls) -> "CommentDisplayName":
        """Use the integration's name."""
        return cls(
            type=DisplayNameType.INTEGRATION,
            resolved_name=""  # Filled by Notion
        )

    @classmethod
    def for_user(cls) -> "CommentDisplayName":
        """Use the authenticated user's name."""
        return cls(
            type=DisplayNameType.USER,
            resolved_name=""  # Filled by Notion
        )

    def to_dict(self) -> dict:
        """Convert to API request format."""
        if self.type == DisplayNameType.CUSTOM:
            return {
                "type": self.type.value,
                "custom": {
                    "name": self.resolved_name
                }
            }
        # For integration and user, type alone is sufficient
        return {
            "type": self.type.value
        }
```

### CommentParent Classes

```python
@dataclass
class CommentPageParent:
    """Page parent for comments."""
    type: str = "page_id"
    page_id: UUID = None

    def to_dict(self) -> dict:
        """Convert to API format."""
        return {
            "type": self.type,
            "page_id": str(self.page_id)
        }

@dataclass
class CommentBlockParent:
    """Block parent for comments."""
    type: str = "block_id"
    block_id: UUID = None

    def to_dict(self) -> dict:
        """Convert to API format."""
        return {
            "type": self.type,
            "block_id": str(self.block_id)
        }
```

## Usage Examples

### Creating Comments

```python
# Simple text comment
comment = await client.comments.create(
    parent={
        "page_id": page_id
    },
    rich_text=[
        {
            "type": "text",
            "text": {"content": "Great page!"}
        }
    ]
)

# Comment with formatting and link
comment = await client.comments.create(
    parent={
        "page_id": page_id
    },
    rich_text=[
        {
            "type": "text",
            "text": {"content": "Check out this "}
        },
        {
            "type": "text",
            "text": {
                "content": "guide",
                "link": {"url": "https://example.com"}
            },
            "annotations": {"bold": True, "color": "blue"}
        }
    ]
)

# Comment with attachment
comment = await client.comments.create(
    parent={
        "block_id": block_id
    },
    rich_text=[
        {
            "type": "text",
            "text": {"content": "Here's the file:"}
        }
    ],
    attachments=[{
        "type": "file_upload",
        "file_upload_id": file_upload_id
    }]
)

# Comment with custom display name
comment = await client.comments.create(
    parent={
        "page_id": page_id
    },
    rich_text=[
        {
            "type": "text",
            "text": {"content": "Automated response"}
        }
    ],
    display_name=CommentDisplayName.for_custom("Notion Bot")
)
```

### Retrieving Comments

```python
# Get comments for a page
comments = await client.comments.list_for_page(page_id)

# Get comments for a block
comments = await client.comments.list_for_block(block_id)

# Comments are in chronological order (oldest first)
for comment in comments:
    print(f"{comment.display_name.resolved_name}: {comment.plain_text}")
    print(f"  Attachments: {len(comment.attachments)}")
    print(f"  Edited: {comment.is_edited}")
```

### Working with Attachments

```python
comment = await client.comments.get(comment_id)

# Check attachments
for attachment in comment.attachments:
    print(f"Category: {attachment.category}")
    print(f"URL: {attachment.url}")
    print(f"Expires: {attachment.expiry_time}")

    # Check if URL needs refresh
    if attachment.is_expired():
        print("URL expired, refreshing...")
        new_url = await attachment.refresh_url()
        print(f"New URL: {new_url}")

# Download attachment
import httpx
async with httpx.AsyncClient() as client:
    response = await client.get(attachment.url)
    with open("downloaded_file.png", "wb") as f:
        f.write(response.content)
```

### Editing Comments

```python
comment = await client.comments.get(comment_id)

# Edit the comment content
updated = await comment.edit(
    rich_text=[
        {
            "type": "text",
            "text": {
                "content": "Updated comment with ",
                "link": {
                    "url": "https://example.com/docs"
                }
            }
        },
        {
            "type": "text",
            "text": {"content": " more details."}
        }
    ]
)
```

## Capabilities Required

To work with comments, your integration needs these capabilities:

| Operation | Required Capability |
|-----------|-------------------|
| Retrieve comments | **Read comments** |
| Create comments | **Insert comments** |
| Update comments | **Insert comments** |
| Delete comments | **Insert comments** |

Ensure your integration has the appropriate capabilities enabled in the integration settings.

## Best Practices

### 1. Comment Organization

- Use meaningful discussion topics
- Group related comments in threads
- Create comments at the appropriate level (page vs block)

### 2. Rich Text Usage

- Use mentions (@users, @pages) to notify relevant people
- Add links for additional context
- Use formatting sparingly for emphasis

### 3. Attachments

- Keep attachments under the 3-file limit
- Use appropriate file types for the content
- Be aware of URL expiration (temporary links)

### 4. Display Names

- Use custom names for bots/automated responses
- Use user names for personal comments
- Consider user experience when choosing display names

## Implementation Checklist

### Core Classes
- [ ] `Comment` class with all fields
- [ ] `CommentPageParent` and `CommentBlockParent` classes
- [ ] `CommentAttachment` class
-   - Attachment category enum
-   - URL expiration handling
-   - Refresh URL functionality
- [ ] `CommentDisplayName` class
-   - Type enum (integration, user, custom)
-   - Request/response format conversion

### Comment Operations
- [ ] Retrieve comments (page/block)
- [ ] Create comment with all features
- [ ] Update comment content
- [ ] Delete comment
- [ ] List comments with pagination

### Helpers
- [ ] Plain text extraction
-   - Rich text parsing integration
-   - Attachments management
-   - Display name helpers
- [ ] Discussion thread management
-   - Chronological ordering

### Testing
- [ ] Unit tests for Comment class
- [ ] Tests for attachment handling
- [ ] Tests for display names
- [ ] Integration tests with Notion API
- [ ] Tests for comment CRUD operations

## Related Documentation

- [Rich Text Objects](./rich-text-objects.md) - Text formatting in comments
- [Blocks Overview](./block/blocks-overview.md) - Comments on blocks
- [Pages Overview](./pages/pages-overview.md) - Comments on pages

---

**Better Notion SDK** - Comment system documentation for Notion API integration.
