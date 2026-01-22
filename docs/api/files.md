# Files and Media

## Overview

In the Notion API, any media asset is represented as a **file object**. A file object stores metadata about the file and indicates where and how the file is hosted.

## File Object Types

Every file object has a required `type` field that determines its structure:

| Type | Description | Use Case |
|------|-------------|----------|
| `file` | Notion-hosted files (uploaded via UI) | Existing content in Notion workspace |
| `file_upload` | Files uploaded via File Upload API | Programmatic uploads, automations |
| `external` | External publicly accessible files | CDN, S3, existing media servers |

## Type: Notion-Hosted Files (`file`)

### Description

Files uploaded manually through the Notion app - such as dragging an image into a page, adding a PDF block, or setting a page cover.

### When to Use

- Working with existing content in a Notion workspace
- Accessing files users manually added via drag-and-drop or upload

### Structure

```json
{
  "type": "file",
  "file": {
    "url": "https://s3.us-west-2.amazonaws.com/secure.notion-static.com/...",
    "expiry_time": "2025-04-24T22:49:22.765Z"
  }
}
```

### Fields

| Field | Type | Description |
|-------|------|-------------|
| `url` | string | Authenticated HTTP GET URL to the file (valid for 1 hour) |
| `expiry_time` | string (ISO 8601) | Link expiration timestamp |

### Tips

**⚠️ Important:**
- URLs are **valid for 1 hour only**
- **Don't cache** or statically reference these URLs
- To refresh access, re-fetch the file object to get a new URL

### SDK Implementation

```python
@dataclass
class NotionHostedFile:
    """Notion-hosted file (uploaded via UI)."""
    type: str = "file"
    url: str = ""
    expiry_time: datetime = None

    @classmethod
    def from_dict(cls, data: dict) -> "NotionHostedFile":
        """Parse from API response."""
        file_data = data.get("file", {})
        return cls(
            url=file_data.get("url", ""),
            expiry_time=_parse_datetime(file_data.get("expiry_time"))
        )

    @property
    def is_expired(self) -> bool:
        """Check if the download URL has expired."""
        if not self.expiry_time:
            return False
        return datetime.now(timezone.utc) > self.expiry_time

    async def refresh_url(self, client: Any) -> str:
        """Refresh the download URL by re-fetching the parent object."""
        # Re-fetch the parent (block, page, etc.) to get fresh URL
        # This is context-dependent on where the file is used
        pass
```

## Type: Files Uploaded via API (`file_upload`)

### Description

Files uploaded using the **File Upload API**. You create a File Upload, send file content, then reference it by ID to attach it.

### When to Use

- Programmatic file uploads to Notion
- Building automations or file-rich integrations
- Batch file processing

### Tips

- **Reuse File Upload IDs** to attach the same file to multiple pages/blocks
- See [Working with files and media](https://developers.notion.com/docs/working-with-files-and-media) for comprehensive guide

### Structure

```json
{
  "type": "file_upload",
  "file_upload": {
    "id": "43833259-72ae-404e-8441-b657f3159b4"
  }
}
```

### Fields

| Field | Type | Description |
|-------|------|-------------|
| `id` | UUID | ID of a File Upload object with status "uploaded" |

### SDK Implementation

```python
@dataclass
class UploadedFile:
    """File uploaded via API (File Upload API)."""
    type: str = "file_upload"
    upload_id: UUID = None

    @classmethod
    def from_dict(cls, data: dict) -> "UploadedFile":
        """Parse from API response."""
        upload_data = data.get("file_upload", {})
        return cls(upload_id=UUID(upload_data.get("id")))

    @classmethod
    def from_id(cls, upload_id: str) -> "UploadedFile":
        """Create from upload ID."""
        return cls(upload_id=UUID(upload_id))

    def to_dict(self) -> dict:
        """Convert to API format."""
        return {
            "type": self.type,
            "file_upload": {
                "id": str(self.upload_id)
            }
        }
```

## Type: External Files (`external`)

### Description

Files hosted elsewhere (S3, Dropbox, CDN) with publicly accessible URLs.

### When to Use

- You have an existing CDN or media server
- Stable, permanent URLs
- Files are publicly accessible and don't require authentication
- You don't want to upload files into Notion

### How to Use

Pass an HTTPS URL when creating or updating file-supporting blocks or properties.

### Structure

```json
{
  "type": "external",
  "external": {
    "url": "https://example.com/photo.png"
  }
}
```

### Fields

| Field | Type | Description |
|-------|------|-------------|
| `url` | string | Link to externally hosted content |

### Tips

- **Links never expire** - Always returned as-is in API responses
- **Must be publicly accessible** - No authentication
- **HTTPS required** - Secure URLs only

### SDK Implementation

```python
@dataclass
class ExternalFile:
    """External file hosted elsewhere."""
    type: str = "external"
    url: str = ""

    @classmethod
    def from_dict(cls, data: dict) -> "ExternalFile":
        """Parse from API response."""
        external_data = data.get("external", {})
        return cls(url=external_data.get("url", ""))

    @classmethod
    def from_url(cls, url: str) -> "ExternalFile":
        """Create from URL."""
        return cls(url=url)

    def to_dict(self) -> dict:
        """Convert to API format."""
        return {
            "type": self.type,
            "external": {
                "url": self.url
            }
        }
```

## File Upload Object

The **File Upload** object tracks the lifecycle of a file uploaded to Notion via the API.

### Object Properties

| Field | Type | Description |
|-------|------|-------------|
| `object` | string | Always `"file_upload"` |
| `id` | UUID | ID of the FileUpload |
| `created_time` | string (ISO 8601) | Creation timestamp |
| `last_edited_time` | string (ISO 8601) | Last modification timestamp |
| `expiry_time` | string \| null | Expiration timestamp (null if attached) |
| `status` | string | Upload status: `"pending"`, `"uploaded"`, `"expired"`, `"failed"` |
| `filename` | string \| null | File name |
| `content_type` | string \| null | MIME content type |
| `content_length` | integer \| null | File size in bytes |
| `upload_url` | string | URL for uploading (pending uploads only) |
| `complete_url` | string | URL for multi-part uploads (pending uploads only) |
| `file_import_result` | string | External URL import result (failed/uploaded status only) |

### Upload Status

| Status | Description |
|--------|-------------|
| `pending` | Awaiting upload or completion |
| `uploaded` | File contents sent and attached to workspace |
| `expired` | File upload expired (not attached in time) |
| `failed` | Upload failed (external URL mode only) |

### SDK Implementation

```python
from enum import Enum
from datetime import datetime
from typing import Optional
from uuid import UUID

class FileUploadStatus(str, Enum):
    """File upload lifecycle status."""
    PENDING = "pending"
    UPLOADED = "uploaded"
    EXPIRED = "expired"
    FAILED = "failed"

@dataclass
class FileUpload:
    """File Upload object tracking upload lifecycle."""
    object: str = "file_upload"
    id: UUID = None
    created_time: Optional[datetime] = None
    last_edited_time: Optional[datetime] = None
    expiry_time: Optional[datetime] = None
    status: FileUploadStatus = FileUploadStatus.PENDING
    filename: Optional[str] = None
    content_type: Optional[str] = None
    content_length: Optional[int] = None
    upload_url: Optional[str] = None  # pending uploads only
    complete_url: Optional[str] = None  # multi-part uploads only
    file_import_result: Optional[str] = None

    @classmethod
    def from_dict(cls, data: dict) -> "FileUpload":
        """Parse from API response."""
        instance = cls()

        instance.object = data.get("object")
        instance.id = UUID(data.get("id"))
        instance.created_time = _parse_datetime(data.get("created_time"))
        instance.last_edited_time = _parse_datetime(data.get("last_edited_time"))
        instance.expiry_time = _parse_datetime(data.get("expiry_time"))
        instance.status = FileUploadStatus(data.get("status", "pending"))
        instance.filename = data.get("filename")
        instance.content_type = data.get("content_type")
        instance.content_length = data.get("content_length")
        instance.upload_url = data.get("upload_url")
        instance.complete_url = data.get("complete_url")
        instance.file_import_result = data.get("file_import_result")

        return instance

    @property
    def is_pending(self) -> bool:
        """Check if upload is pending."""
        return self.status == FileUploadStatus.PENDING

    @property
    def is_uploaded(self) -> bool:
        """Check if file is successfully uploaded."""
        return self.status == FileUploadStatus.UPLOADED

    @property
    def is_expired(self) -> bool:
        """Check if upload has expired."""
        return self.status == FileUploadStatus.EXPIRED

    @property
    def is_failed(self) -> bool:
        """Check if upload failed."""
        return self.status == FileUploadStatus.FAILED

    @property
    def can_be_used(self) -> bool:
        """Check if upload ID can be used to attach file."""
        return self.is_uploaded and not self.is_expired

    @property
    def size_mb(self) -> Optional[float]:
        """Get file size in megabytes."""
        if self.content_length:
            return self.content_length / (1024 * 1024)
        return None
```

## Choosing the Right File Type

### Decision Tree

```
Do you need to upload a new file to Notion?
├── Yes → Use File Upload API (type: file_upload)
│
└── No → Is the file already in Notion?
    ├── Yes → Use Notion-hosted file (type: file)
    └── No → Use external file (type: external)
```

### Comparison Table

| Aspect | `file` | `file_upload` | `external` |
|--------|-------|----------------|------------|
| **Source** | Uploaded via UI | Uploaded via API | External host |
| **URL Expiration** | 1 hour | Never (once attached) | Never |
| **Storage** | Notion S3 | Notion S3 | External |
| **Authentication** | Notion-managed | Notion-managed | Public |
| **Upload Control** | Manual | Programmatic | N/A |
| **Best For** | Existing content | Automations | CDNs |

### Use Cases

#### Use `type: file` (Notion-hosted) when:
- Working with existing Notion content
- Accessing user-uploaded files
- Integration needs to read existing media

#### Use `type: file_upload` when:
- Uploading files programmatically
- Building automation workflows
- Creating file-rich integrations
- Batch processing files

#### Use `type: external` when:
- Files already hosted on CDN/S3
- Need permanent URLs
- Building lightweight integrations
- Files don't need Notion storage

## File Upload Workflow

### Complete Upload Process

```
1. Create File Upload
   POST /file_upload
   ← Returns FileUpload object with status="pending"
   ← Contains upload_url or complete_url

2. Upload File Content
   PUT <upload_url> (single part)
   OR
   POST <complete_url> (multi-part)
   ← Send file data as binary/stream

3. Complete Upload
   PATCH /file_upload/{id}
   ← Mark as complete (if needed)

4. Use File Upload ID
   → Attach to blocks, pages, databases
   ← Reference via file_upload type
```

### Example: Single-Part Upload

```python
# 1. Create file upload
file_upload = await client.file_uploads.create(
    filename="document.pdf",
    content_type="application/pdf",
    size=1024000
)

# 2. Upload content (using upload_url)
import httpx

async with httpx.AsyncClient() as http_client:
    with open("document.pdf", "rb") as f:
        await http_client.put(
            file_upload.upload_url,
            content=f.read(),
            headers={"Content-Type": "application/pdf"}
        )

# 3. Mark as complete
await client.file_uploads.complete(file_upload.id)

# 4. Use in block/page
await client.blocks.children.append(
    block_id=block_id,
    children=[{
        "object": "block",
        "type": "file",
        "file": {
            "type": "file_upload",
            "file_upload": {
                "id": str(file_upload.id)
            },
            "name": "document.pdf"
        }
    }]
)
```

### Example: External File

```python
# Use external URL directly
await client.blocks.children.append(
    block_id=block_id,
    children=[{
        "object": "block",
        "type": "image",
        "image": {
            "type": "external",
            "external": {
                "url": "https://example.com/image.png"
            }
        }
    }]
)
```

## File Usage in Notion Objects

### In Blocks

```json
{
  "type": "image",
  "image": {
    "type": "file_upload",
    "file_upload": {
      "id": "43833259-72ae-404e-8441-b657f3159b4"
    }
  }
}
```

### In Pages (Covers/Icons)

```json
{
  "icon": {
    "type": "file_upload",
    "file_upload": {
      "id": "43833259-72ae-404e-8441-b657f3159b4"
    }
  }
}
```

### In Database Properties (Files column)

```json
{
  "Attachments": {
    "type": "files",
    "files": [
      {
        "type": "file_upload",
        "file_upload": {
          "id": "43833259-72ae-404e-8441-b657f3159b4"
        },
        "name": "Blueprint.pdf"
      }
    ]
  }
}
```

## SDK Implementation

### Unified File Class

```python
from dataclasses import dataclass, field
from typing import Optional, Union
from enum import Enum

class FileType(str, Enum):
    """File source types."""
    NOTION_HOSTED = "file"
    UPLOADED = "file_upload"
    EXTERNAL = "external"

@dataclass
class File:
    """Unified file object for all file types."""
    type: FileType
    notion_hosted: Optional[NotionHostedFile] = None
    uploaded: Optional[UploadedFile] = None
    external: Optional[ExternalFile] = None

    @classmethod
    def from_dict(cls, data: dict) -> "File":
        """Parse file object from API response."""
        file_type = FileType(data.get("type"))

        if file_type == FileType.NOTION_HOSTED:
            notion_file = NotionHostedFile.from_dict(data)
            return cls(type=file_type, notion_hosted=notion_file)
        elif file_type == FileType.UPLOADED:
            uploaded_file = UploadedFile.from_dict(data)
            return cls(type=file_type, uploaded=uploaded_file)
        elif file_type == FileType.EXTERNAL:
            external_file = ExternalFile.from_dict(data)
            return cls(type=file_type, external=external_file)

        raise ValueError(f"Unknown file type: {file_type}")

    @classmethod
    def from_upload_id(cls, upload_id: str) -> "File":
        """Create file from File Upload ID."""
        return cls(
            type=FileType.UPLOADED,
            uploaded=UploadedFile.from_id(upload_id)
        )

    @classmethod
    def from_url(cls, url: str) -> "File":
        """Create file from external URL."""
        return cls(
            type=FileType.EXTERNAL,
            external=ExternalFile.from_url(url)
        )

    @property
    def url(self) -> Optional[str]:
        """Get the file URL (if available)."""
        if self.type == FileType.NOTION_HOSTED:
            return self.notion_hosted.url
        elif self.type == FileType.EXTERNAL:
            return self.external.url
        return None

    @property
    def is_expired(self) -> bool:
        """Check if the file URL has expired."""
        if self.type == FileType.NOTION_HOSTED:
            return self.notion_hosted.is_expired()
        return False

    @property
    def needs_refresh(self) -> bool:
        """Check if URL needs to be refreshed."""
        return self.type == FileType.NOTION_HOSTED and self.is_expired

    async def refresh(self, parent_client: Any, parent_id: str) -> str:
        """Refresh the file URL by re-fetching the parent."""
        # Re-fetch parent object to get updated file
        if self.type != FileType.NOTION_HOSTED:
            return self.url

        # Implementation depends on parent type (block, page, etc.)
        parent = await parent_client.get(parent_id)

        # Find and return this file from parent
        # (implementation varies by parent type)
        pass

    def to_dict(self) -> dict:
        """Convert to API format."""
        if self.type == FileType.NOTION_HOSTED:
            return {
                "type": self.type.value,
                "file": {
                    "url": self.notion_hosted.url,
                    "expiry_time": _format_datetime(
                        self.notion_hosted.expiry_time
                    ) if self.notion_hosted.expiry_time else None
                }
            }
        elif self.type == FileType.UPLOADED:
            return self.uploaded.to_dict()
        elif self.type == FileType.EXTERNAL:
            return self.external.to_dict()

        raise ValueError(f"Unknown file type: {self.type}")
```

## Usage Examples

### Creating File Upload

```python
# Upload a file
file_upload = await client.file_uploads.upload(
    file_path="document.pdf",
    filename="Project Blueprint.pdf"
)

# Check status
if file_upload.is_uploaded:
    print(f"Upload complete: {file_upload.id}")
elif file_upload.is_pending:
    print(f"Upload pending, URL: {file_upload.upload_url}")
```

### Attaching Files to Blocks

```python
# Attach uploaded file
await client.blocks.children.append(
    block_id=block_id,
    children=[{
        "object": "block",
        "type": "file",
        "file": {
            "type": "file_upload",
            "file_upload": {
                "id": str(file_upload_id)
            },
            "caption": [{"type": "text", "text": {"content": "Blueprint"}}]
        }
    }]
)

# Attach external file
await client.blocks.children.append(
    block_id=block_id,
    children=[{
        "object": "block",
        "type": "image",
        "image": {
            "type": "external",
            "external": {
                "url": "https://example.com/image.png"
            }
        }
    }]
)
```

### Setting Page Cover/Icon

```python
# Set page cover with uploaded file
await client.pages.update(
    page_id=page_id,
    cover={
        "type": "external",
        "external": {
            "url": "https://example.com/cover.png"
        }
    }
)

# Set page icon with uploaded file
await client.pages.update(
    page_id=page_id,
    icon={
        "type": "file_upload",
        "file_upload": {
            "id": str(file_upload_id)
        }
    }
)
```

## Implementation Checklist

### Core Classes
- [ ] `NotionHostedFile` class
- [ ] `UploadedFile` class
- [ ] `ExternalFile` class
- [ ] `FileUpload` class (complete with all fields)
- [ ] `File` unified class
- [ ] `FileType` enum

### File Upload Management
- [ ] File Upload API client methods
- [ ] Upload (single-part)
- [ ] Upload (multi-part)
- [ ] Complete upload
- [ ] Check upload status
- [ ] List file uploads

### Integration Points
- [ ] Block file attachments
- [ ] Page cover/icon
- [ ] Database file properties
- [ ] Comment attachments
- [ ] Rich text file objects

### Utilities
- [ ] URL refresh mechanism
- [ ] Expiration checking
- [ ] File size formatting
- [ ] Content type detection
- [ ] Error handling

### Testing
- [ ] Unit tests for each file type
- [ ] Integration tests with File Upload API
- [ ] Tests for URL refresh
- [ ] Tests for attachment operations

## Best Practices

### 1. URL Management

**For Notion-hosted files:**
- Never cache URLs permanently
- Implement refresh mechanism
- Check expiry before using URLs

**For external files:**
- Ensure public accessibility
- Use HTTPS only
- Document URL requirements

### 2. Upload Strategy

**When using File Upload API:**
- Reuse File Upload IDs when possible
- Handle upload failures gracefully
- Track upload status
- Clean up expired uploads

### 3. Performance

**For large files:**
- Use multi-part upload
- Implement progress tracking
- Handle timeouts appropriately
- Consider async operations

**For multiple files:**
- Upload in parallel when possible
- Implement queue management
- Track all File Upload IDs

### 4. Error Handling

Common scenarios:
- Upload expiration before attachment
- External URL becoming inaccessible
- File type mismatches
- Size limitations

### 5. Security

**For Notion-hosted files:**
- URLs are authenticated but temporary
- Don't expose URLs outside session context

**For external files:**
- Validate URLs before using
- Check accessibility
- Document security implications

## Related Documentation

- [Blocks Overview](./block/blocks-overview.md) - File blocks
- [Block Types](./block/block-types.md) - Image, file, PDF blocks
- [Pages Overview](./pages/pages-overview.md) - Page covers/icons
- [Database Properties](./databases/data-sources.md) - File properties
- [Comments](./comments.md) - Comment attachments

---

**Better Notion SDK** - Files and media handling for Notion API integration.
