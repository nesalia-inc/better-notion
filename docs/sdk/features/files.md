# Files Feature

Comprehensive documentation of file upload and management operations in the Better Notion SDK.

## Overview

Files in Notion include images, documents, media, and attachments. They can be:
- **Uploaded** from local files or URLs
- **Attached** to pages, blocks, or comments
- **Embedded** as file blocks or in properties

**Upload Modes:**
- **single_part**: For files ≤ 20MB
- **multi_part**: For files > 20MB (up to 1GB)
- **external_url**: Import from public URL

## Features

### Core Upload Operations

#### Simple Upload (Automatic Mode Selection)

```python
# Upload with automatic mode selection
file = await client.files.upload(
    file_path="document.pdf",
    parent=page
)

# SDK selects:
# - single_part if ≤ 20MB
# - multi_part if > 20MB

print(file.url)        # Download URL
print(file.type)       # "file" or "external"
print(file.expiry_time)  # URL expiration (for uploads)
```

**API Equivalent:** `POST /files` + mode selection logic

**Why SDK-Exclusive:**
- User doesn't need to know file size limits
- Automatic mode selection based on file size
- Single API regardless of upload mode

#### Upload Small File (Single-Part)

```python
# For files ≤ 20MB
file = await client.files.upload_small(
    file_path="image.png",
    parent=page
)

# Or explicitly specify mode
file = await client.files.upload(
    file_path="image.png",
    parent=page,
    mode="single_part"
)
```

**API Equivalent:** `POST /files` with single_part mode

#### Upload Large File (Multi-Part)

```python
# For files > 20MB (up to 1GB)
file = await client.files.upload_large(
    file_path="presentation.pdf",
    parent=page
)

# Automatically splits into chunks
# Uploads in parallel
# Reassembles on server

# Or explicit mode
file = await client.files.upload(
    file_path="presentation.pdf",
    parent=page,
    mode="multi_part"
)
```

**API Equivalent:** Multiple API calls (create, send parts, complete)

**Why SDK-Exclusive:**
- Abstracts complex multi-part workflow
- Handles chunking automatically
- Manages upload state and retries

#### Upload from URL

```python
# Import from external URL
file = await client.files.upload_from_url(
    url="https://example.com/image.png",
    parent=page
)

# Notion fetches the URL
# No file data transferred through SDK

print(file.url)
```

**API Equivalent:** `POST /files` with external_url mode

### Upload with Progress

#### Progress Callback

```python
# Track upload progress
def progress_callback(uploaded: int, total: int):
    percent = (uploaded / total) * 100
    print(f"Uploaded {percent:.1f}%")

file = await client.files.upload(
    file_path="large.zip",
    parent=page,
    progress_callback=progress_callback
)

# Output:
# Uploaded 10.0%
# Uploaded 20.0%
# ...
# Uploaded 100.0%
```

**Why SDK-Exclusive:**
- Essential for large file uploads
- User feedback for long operations
- Progress bars in UI applications

#### Progress with Details

```python
# Detailed progress information
def progress_callback(details: UploadProgress):
    print(f"Part {details.part_number}/{details.total_parts}")
    print(f"Uploaded: {details.uploaded_bytes}/{details.total_bytes}")
    print(f"Speed: {details.speed_mbps:.2f} MB/s")
    print(f"ETA: {details.eta_seconds}s")

file = await client.files.upload(
    file_path="video.mp4",
    parent=page,
    progress_callback=progress_callback
)
```

### Bulk Uploads

#### Upload Multiple Files

```python
# Upload multiple files efficiently
files = await client.files.upload_bulk(
    file_paths=[
        "doc1.pdf",
        "doc2.pdf",
        "doc3.pdf"
    ],
    parent=page
)

# Returns list of File objects
for file in files:
    print(f"Uploaded: {file.url}")
```

**Why SDK-Exclusive:**
- Common operation (upload multiple files)
- Parallel uploads where possible
- Rate limiting handled automatically

#### Upload from Directory

```python
# Upload all files from directory
import os

directory = "documents/"
file_names = [
    os.path.join(directory, f)
    for f in os.listdir(directory)
    if os.path.isfile(os.path.join(directory, f))
]

files = await client.files.upload_bulk(
    file_paths=file_names,
    parent=page
)
```

### File Information

#### Get File Details

```python
# Retrieve file upload information
file = await client.files.get(upload_id)

print(file.type)          # "file" or "external"
print(file.url)           # Download URL
print(file.expiry_time)   # URL expiration time

# For uploaded files
if file.type == "file":
    print(file.file_size)     # Size in bytes
    print(file.mime_type)     # MIME type

# For external URLs
if file.type == "external":
    print(file.external_url)  # Original URL
```

**API Equivalent:** `GET /files/{upload_id}`

#### List File Uploads

```python
# List file uploads
async for file in client.files.list():
    print(f"{file.type}: {file.url}")

# Filter by type
async for file in client.files.list(file_type="file"):
    print(f"Uploaded file: {file.url}")

# With pagination limit
async for file in client.files.list().limit(100):
    process(file)
```

**API Equivalent:** `GET /files` + pagination

### File Attachments

#### Attach to Page

```python
# Upload and attach to page as file block
file = await client.files.upload(
    file_path="document.pdf",
    parent=page
)

# Creates file block automatically
```

#### Attach to Block

```python
# Upload and attach to block
file = await client.files.upload(
    file_path="image.png",
    parent=block
)
```

#### Attach to Comment

```python
# Upload and attach to comment
file = await client.files.upload(
    file_path="screenshot.png",
    parent=page
)

comment = await client.comments.create(
    parent=page,
    text="Here's the screenshot:",
    attachments=[file]
)
```

#### Attach to Property

```python
# Upload and attach to Files property
file = await client.files.upload(
    file_path="contract.pdf",
    parent=page
)

await client.pages.update(
    page,
    properties={
        "Contract": [file]  # Files property
    }
)
```

### File URL Handling

#### Get Permanent URL

```python
# Uploaded URLs expire after 1 hour
file = await client.files.upload("doc.pdf", parent=page)

print(file.url)  # Temporary URL

# To get permanent URL, add to page/block
# The URL in the page/block is permanent
```

#### URL Expiration

```python
# Check if URL is expired
file = await client.files.get(upload_id)

if file.expiry_time and file.expiry_time < datetime.now():
    print("URL has expired")
    # Need to re-upload or use permanent URL from page
```

### File as Block

#### Create File Block

```python
# Upload and create file block
file = await client.files.upload("document.pdf", parent=page)

# File block is created automatically
# Or create explicitly:
file_block = Block.file(file)
await page.append_children([file_block])
```

#### Create Image Block

```python
# Upload and create image block
file = await client.files.upload("image.png", parent=page)

image_block = Block.image(file)
await page.append_children([image_block])
```

#### Create Video Block

```python
# Upload and create video block
file = await client.files.upload("video.mp4", parent=page)

video_block = Block.video(file)
await page.append_children([video_block])
```

#### Create PDF Block

```python
# Upload and create PDF block
file = await client.files.upload("document.pdf", parent=page)

pdf_block = Block.pdf(file)
await page.append_children([pdf_block])
```

### Advanced Patterns

#### Upload with Retry

```python
# Upload with automatic retry on failure
file = await client.files.upload(
    file_path="large.zip",
    parent=page,
    max_retries=3,
    retry_backoff=True
)
```

#### Upload with Validation

```python
# Validate file before upload
import os

file_path = "document.pdf"

# Check file exists
if not os.path.exists(file_path):
    raise FileNotFoundError(f"File not found: {file_path}")

# Check file size (max 1GB for Notion)
file_size = os.path.getsize(file_path)
max_size = 1024 * 1024 * 1024  # 1GB

if file_size > max_size:
    raise ValueError(f"File too large: {file_size} bytes")

# Upload
file = await client.files.upload(file_path, parent=page)
```

#### Upload with Metadata

```python
# Store metadata alongside upload
file = await client.files.upload(
    file_path="report.pdf",
    parent=page,
    metadata={
        "original_name": "Q4 Report.pdf",
        "category": "reports",
        "version": "1.0"
    }
)

# Metadata stored in SDK for reference
print(file.metadata)
```

#### Upload Streaming

```python
# Upload from stream (not file path)
from io import BytesIO

# Create file-like object
buffer = BytesIO(file_data)

file = await client.files.upload_stream(
    stream=buffer,
    filename="document.pdf",
    parent=page
)
```

#### Download File

```python
# Download file from URL (if you have the URL)
import httpx

async def download_file(url: str, destination: str):
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        with open(destination, "wb") as f:
            f.write(response.content)

# Use
file = await client.files.get(upload_id)
await download_file(file.url, "downloaded.pdf")
```

## Implementation Considerations

### File Object Model

```python
class File:
    id: str  # Upload ID
    type: str  # "file" or "external"
    url: str  # Download URL
    expiry_time: datetime | None

    # For uploaded files
    file_size: int | None
    mime_type: str | None

    # For external URLs
    external_url: str | None

    # Upload metadata
    metadata: dict[str, Any]

    # Methods
    async def refresh() -> File
    @property
    def is_expired(self) -> bool
```

### Upload Progress Model

```python
class UploadProgress:
    uploaded_bytes: int
    total_bytes: int
    part_number: int  # For multi-part
    total_parts: int  # For multi-part
    speed_mbps: float
    eta_seconds: int
```

### Upload Mode Selection

```python
def select_upload_mode(file_path: str) -> str:
    """Select upload mode based on file size."""
    file_size = os.path.getsize(file_path)

    SINGLE_PART_MAX = 20 * 1024 * 1024  # 20MB

    if file_size <= SINGLE_PART_MAX:
        return "single_part"
    else:
        return "multi_part"
```

### Multi-Part Upload Strategy

```python
# For multi-part uploads:
# 1. Create upload (get upload ID)
# 2. Split file into chunks (~5MB each)
# 3. Upload chunks in parallel (with retries)
# 4. Complete upload (reassemble on server)

# SDK handles all of this automatically
```

## Error Scenarios

| Scenario | Error | Solution |
|----------|-------|----------|
| File too large | `FileTooLargeError` | Max 1GB |
| Invalid file | `ValidationError` | Check file exists |
| Upload failed | `UploadError` | SDK retries |
| URL expired | `ExpiredURLError` | Re-upload needed |

## Performance Considerations

### Optimal Patterns

```python
# GOOD: Parallel bulk uploads
files = await client.files.upload_bulk(file_paths, parent=page)

# AVOID: Sequential uploads
for path in file_paths:
    await client.files.upload(path, parent=page)  # Slower

# GOOD: Use progress for large files
await client.files.upload(
    "large.zip",
    parent=page,
    progress_callback=callback
)

# GOOD: Validate before upload
if os.path.getsize(file_path) > MAX_SIZE:
    raise ValueError("File too large")
```

### Multi-Part Optimization

```python
# Multi-part uploads use:
# - Parallel chunk uploads (configurable concurrency)
# - Automatic retry on failure
# - Progress tracking across parts

# Configurable parameters
file = await client.files.upload(
    "large.zip",
    parent=page,
    chunk_size=5 * 1024 * 1024,  # 5MB chunks
    max_concurrency=5  # Upload 5 chunks at once
)
```

## Integration with Other Features

### Pages

```python
# Upload to page
file = await client.files.upload("doc.pdf", parent=page)

# Page cover
await client.pages.update(page, cover=file.url)
```

### Blocks

```python
# Image blocks
image_block = Block.image(await client.files.upload("img.png", parent=page))

# File blocks
file_block = Block.file(await client.files.upload("doc.pdf", parent=page))

# Video blocks
video_block = Block.video(await client.files.upload("video.mp4", parent=page))
```

### Comments

```python
# Attachments
file = await client.files.upload("screenshot.png", parent=page)

comment = await client.comments.create(
    parent=page,
    text="See screenshot:",
    attachments=[file]
)
```

## Future Enhancements

### Tier 2 (High Priority)
- [ ] Upload resumption (continue interrupted uploads)
- [ ] File deduplication (avoid duplicate uploads)
- [ ] Upload queue management

### Tier 3 (Medium Priority)
- [ ] Image compression before upload
- [ ] Thumbnail generation
- [ ] File format conversion

### Tier 4 (Future)
- [ ] Background upload processing
- [ ] File versioning
- [ ] Direct cloud storage integration
