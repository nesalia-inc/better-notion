# Comments Feature

Comprehensive documentation of comment-related operations and features in the Better Notion SDK.

## Overview

Comments enable discussions on pages and blocks. A comment:
- Has **rich text content** with formatting
- Can have **attachments** (up to 3 files)
- Belongs to a **parent** (page or block)
- May be part of a **discussion thread** (replies)

## Features

### Core CRUD Operations

#### Create a Comment

```python
# Simple text comment
comment = await client.comments.create(
    parent=page,
    text="This looks great!"
)

# With rich text
comment = await client.comments.create(
    parent=page,
    rich_text=[
        {"text": "Great work on "},
        {"text": "this project", "bold": True},
        {"text": "!"},
    ]
)

# On a block
comment = await client.comments.create(
    parent=block,
    text="Please update this section"
)

# In a discussion thread
comment = await client.comments.create(
    discussion_id=discussion_id,
    text="I agree with this approach"
)
```

**API Equivalent:** `POST /comments`

**Enhancements:**
- `text` parameter for simple text (auto-converts to rich text)
- Rich text builder for formatted content
- Accept Page or Block object directly

#### Retrieve a Comment

```python
# Get comment by ID
comment = await client.comments.get(comment_id)

print(comment.text)        # Plain text content
print(comment.rich_text)   # Rich text structure
print(comment.created_time)
print(comment.edited_time)

# Author information
author = comment.author
print(author.name)

# Attachments
for attachment in comment.attachments:
    print(attachment.type)  # "external", "file", etc.
    print(attachment.url)
```

**API Equivalent:** `GET /comments/{comment_id}`

#### List Comments

```python
# List comments on a page
async for comment in client.comments.list(block_id=page_id):
    print(f"{author.name}: {comment.text}")

# List comments on a block
async for comment in client.comments.list(block_id=block_id):
    process(comment)

# Collect all
comments = await client.comments.list(block_id=page_id).collect()
```

**API Equivalent:** `GET /comments` with block_id parameter

**Enhancements:**
- Async iterator handles pagination
- Direct object access (author, text, etc.)

### Thread Navigation

#### Get Thread

```python
# Get all comments in a discussion thread
thread = await comment.thread()

for reply in thread:
    print(f"{reply.author.name}: {reply.text}")
```

**Why SDK-Exclusive:**
- API doesn't provide thread navigation
- Requires multiple calls to fetch thread
- SDK handles parent/child relationships

#### Get Parent Comment

```python
# Get parent comment (for replies)
parent = await comment.parent()

if parent:
    print(f"Replying to: {parent.author.name}")
```

**Why SDK-Exclusive:**
- API doesn't provide parent reference
- SDK maintains thread structure

#### Get Replies

```python
# Iterate over replies to a comment
async for reply in comment.replies():
    print(f"Reply: {reply.text}")

# Collect replies
replies = await comment.replies().collect()
```

**Why SDK-Exclusive:**
- API treats all comments as flat list
- SDK structures them into threads

### Rich Text Comments

#### Formatted Text

```python
# With formatting
comment = await client.comments.create(
    parent=page,
    rich_text=RichText()
    .text("Check out ")
    .bold("this important point")
    .text(" in the document.")
)
```

#### With Mentions

```python
# Mention a user
comment = await client.comments.create(
    parent=page,
    rich_text=RichText()
    .text("Hey ")
    .user_mention(user_id)
    .text(", can you review this?")
)

# Mention a page
comment = await client.comments.create(
    parent=page,
    rich_text=RichText()
    .text("See also: ")
    .page_mention(page_id)
)

# Mention a database
comment = await client.comments.create(
    parent=page,
    rich_text=RichText()
    .text("Reference: ")
    .database_mention(database_id)
)
```

#### With Links

```python
# With hyperlink
comment = await client.comments.create(
    parent=page,
    rich_text=RichText()
    .text("Visit ")
    .link("Notion", "https://notion.so")
    .text(" for more info.")
)
```

### Attachments

#### Create with Attachments

```python
# With file attachments
comment = await client.comments.create(
    parent=page,
    text="Here are the files:",
    attachments=[
        "https://example.com/file1.pdf",
        "https://example.com/file2.png",
        "https://example.com/file3.docx"
    ]
)

# Maximum 3 attachments
# URLs can be external or from file uploads
```

#### Upload and Attach

```python
# Upload files and attach to comment
file1 = await client.files.upload("document.pdf", parent=page)
file2 = await client.files.upload("image.png", parent=page)

comment = await client.comments.create(
    parent=page,
    text="Uploaded files:",
    attachments=[file1, file2]
)
```

#### Access Attachments

```python
# Get comment attachments
for attachment in comment.attachments:
    print(f"Type: {attachment.type}")
    print(f"URL: {attachment.url}")

    if attachment.type == "file":
        print(f"Expiry time: {attachment.expiry_time}")
```

### Comment Helpers

#### Simple Comment Creation

```python
# Text-only comment (most common)
comment = await client.comments.create(
    parent=page,
    text="Please review when you get a chance."
)
```

#### Comment with User

```python
# Address specific user
comment = await client.comments.create(
    parent=page,
    text=f"@{user.name}, can you take a look?",
    mentions=[user]
)
```

#### Quick Reply

```python
# Reply to a comment
reply = await comment.reply(
    text="Thanks for the feedback!"
)

# Equivalent to:
reply = await client.comments.create(
    discussion_id=comment.discussion_id,
    text="Thanks for the feedback!"
)
```

### Discussion Management

#### Create Discussion

```python
# Start a new discussion thread
comment = await client.comments.create(
    parent=page,
    text="Let's discuss the project timeline"
)

# This creates a new discussion thread
discussion_id = comment.discussion_id
```

#### Get Discussion Comments

```python
# Get all comments in a discussion
async for comment in client.comments.get_discussion(discussion_id):
    print(f"{comment.author.name}: {comment.text}")
```

**Why SDK-Exclusive:**
- API doesn't have "get discussion" endpoint
- Requires filtering comments by discussion_id
- SDK handles filtering automatically

#### Resolve Discussion (Future)

```python
# Mark discussion as resolved (if API adds support)
await client.comments.resolve_discussion(discussion_id)

# Reopen discussion
await client.comments.reopen_discussion(discussion_id)
```

### Advanced Patterns

#### Comment Aggregation

```python
# Get all comments across a page
async def get_all_comments(page: Page) -> list[Comment]:
    """Get all comments on page and all blocks."""
    comments = []

    # Page-level comments
    async for comment in client.comments.list(block_id=page.id):
        comments.append(comment)

    # Block-level comments
    async for block in page.descendants():
        async for comment in client.comments.list(block_id=block.id):
            comments.append(comment)

    return comments

# Use
all_comments = await get_all_comments(page)
print(f"Total comments: {len(all_comments)}")
```

#### Comments by User

```python
# Filter comments by author
async def comments_by_user(
    page: Page,
    user: User
) -> list[Comment]:
    """Get all comments by specific user."""
    user_comments = []

    async for comment in client.comments.list(block_id=page.id):
        if comment.author.id == user.id:
            user_comments.append(comment)

    return user_comments
```

#### Recent Comments

```python
# Get recent comments
async def recent_comments(
    hours: int = 24
) -> list[Comment]:
    """Get comments from last N hours."""
    cutoff = datetime.now() - timedelta(hours=hours)
    recent = []

    async for page in client.pages.all():
        async for comment in client.comments.list(block_id=page.id):
            if comment.created_time > cutoff:
                recent.append(comment)

    return recent

# Use
latest = await recent_comments(hours=1)
print(f"Comments in last hour: {len(latest)}")
```

#### Comment Thread Summary

```python
# Summarize discussion thread
async def thread_summary(comment: Comment) -> dict:
    """Get summary of comment thread."""
    replies = await comment.replies().collect()

    return {
        "started_by": comment.author.name,
        "started_at": comment.created_time,
        "total_replies": len(replies),
        "participants": len(set(r.author.id for r in replies + [comment])),
        "last_activity": max(
            comment.created_time,
            *(r.created_time for r in replies)
        )
    }

# Use
summary = await thread_summary(comment)
print(f"Thread: {summary['total_replies']} replies")
print(f"Participants: {summary['participants']}")
```

## Implementation Considerations

### Comment Object Model

```python
class Comment(BaseEntity):
    id: str
    text: str  # Plain text
    rich_text: list  # Rich text structure
    created_time: datetime
    edited_time: datetime | None
    author: User
    parent: Page | Block
    discussion_id: str | None
    attachments: list[Attachment]

    # Thread navigation
    async def parent(self) -> Comment | None
    async def replies(self) -> AsyncIterator[Comment]
    async def thread(self) -> list[Comment]

    # Helpers
    async def reply(text: str) -> Comment
    @property
    def is_edited(self) -> bool
```

### Rich Text Builder for Comments

```python
class CommentRichText:
    @staticmethod
    def text(content: str) -> dict
    @staticmethod
    def bold(content: str) -> dict
    @staticmethod
    def italic(content: str) -> dict
    @staticmethod
    def link(text: str, url: str) -> dict
    @staticmethod
    def user_mention(user_id: str) -> dict
    @staticmethod
    def page_mention(page_id: str) -> dict
    @staticmethod
    def database_mention(db_id: str) -> dict
```

### Thread Structure

```python
# API returns flat list
# SDK structures into threads:

comment (parent)
  ├─ reply (child)
  ├─ reply (child)
  │   └─ reply to reply (grandchild)
  └─ reply (child)
```

## Error Scenarios

| Scenario | Error | Solution |
|----------|-------|----------|
| Comment not found | `CommentNotFound` | Verify ID |
| Invalid parent | `ValidationError` | Check parent exists |
| Too many attachments | `ValidationError` | Max 3 attachments |
| No permissions | `PermissionError` | Check capabilities |

## Performance Considerations

### Optimal Patterns

```python
# GOOD: Stream comments
async for comment in client.comments.list(block_id=page_id):
    process(comment)

# AVOID: Load all if not needed
comments = await client.comments.list(block_id=page_id).collect()

# GOOD: Use cache for author info
author = comment.author  # Cached user lookup

# AVOID: Repeated user fetches
author = await client.users.get(comment.author.id)  # API call
```

## Integration with Other Features

### Pages

```python
# Page comments
page = await client.pages.get(page_id)
async for comment in client.comments.list(block_id=page.id):
    print(comment.text)
```

### Blocks

```python
# Block-specific comments
block = await client.blocks.get(block_id)
async for comment in client.comments.list(block_id=block.id):
    print(comment.text)
```

### Users

```python
# Comment author is a User object
comment = await client.comments.get(comment_id)
author = comment.author  # User object with cache
print(author.display_name)
```

### Files

```python
# Attachments from file uploads
file = await client.files.upload("doc.pdf")
comment = await client.comments.create(
    parent=page,
    text="Attached document",
    attachments=[file]
)
```

## Future Enhancements

### Tier 2 (High Priority)
- [ ] Comment reactions (if API adds support)
- [ ] Comment editing
- [ ] Comment deletion

### Tier 3 (Medium Priority)
- [ ] Comment threading improvements
- [ ] Comment search
- [ ] Comment analytics

### Tier 4 (Future)
- [ ] Real-time comment updates
- [ ] Comment notifications
- [ ] Comment moderation
