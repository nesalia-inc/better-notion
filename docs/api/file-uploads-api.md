# File Uploads API Reference

Complete API reference for all file upload operations in the Notion API.

## Table of Contents

1. [Create a File Upload](#create-a-file-upload)
2. [Send a File Upload](#send-a-file-upload)
3. [Complete a File Upload](#complete-a-file-upload)
4. [Retrieve a File Upload](#retrieve-a-file-upload)
5. [List File Uploads](#list-file-uploads)

---

## Create a File Upload

Initiates the file upload process and returns a File Upload object with upload instructions.

### Endpoint

```
POST https://api.notion.com/v1/file_uploads
```

### Body Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `mode` | string | No | `single_part` | Upload mode |
| `filename` | string | Conditional* | - | Name of the file to create |
| `content_type` | string | Conditional* | - | MIME type of the file |
| `number_of_parts` | integer | Conditional* | - | Number of parts (1-1000) |
| `external_url` | string | Conditional* | - | Public HTTPS URL to import |

\* Required when mode is `multi_part` or `external_url`

### Upload Modes

#### 1. Single Part (`single_part`)

Default mode for files up to 20MB. Use for most uploads.

```json
{
  "mode": "single_part"
}
```

**Response includes:**
- `upload_url`: URL to send file content to
- `status`: `"pending"`
- `expiry_time`: When upload URL expires (typically 1 hour)

#### 2. Multi Part (`multi_part`)

For files larger than 20MB. File is split into parts and uploaded separately.

```json
{
  "mode": "multi_part",
  "filename": "large-file.zip",
  "content_type": "application/zip",
  "number_of_parts": 5
}
```

**Required fields:**
- `filename` - Must include extension or inferred from content_type
- `content_type` - Must match actual file content
- `number_of_parts` - Between 1 and 1000

**Next steps:**
1. Send each part (1 to number_of_parts) to Send endpoint
2. Call Complete endpoint after all parts sent

**Parts can be:**
- Sent concurrently (up to rate limits)
- Sent out of order
- Any size (but equal sizes recommended)

#### 3. External URL (`external_url`)

Import from a publicly accessible URL. Notion downloads the file.

```json
{
  "mode": "external_url",
  "external_url": "https://example.com/files/document.pdf"
}
```

**Required fields:**
- `external_url` - Public HTTPS URL

**Use cases:**
- Files already hosted elsewhere
- CDN-hosted assets
- Temporary uploads

### Headers

| Header | Type | Required | Description |
|--------|------|----------|-------------|
| `Authorization` | string | Yes | Bearer `{integration_token}` |
| `Content-Type` | string | Yes | `application/json` |
| `Notion-Version` | string | Yes | The API version to use (latest: `2025-09-03`) |

### Response

Returns a File Upload object.

```json
{
  "id": "b52b8ed6-e029-4707-a671-832549c09de3",
  "object": "file_upload",
  "created_time": "2025-03-15T20:53:00.000Z",
  "last_edited_time": "2025-03-15T20:53:00.000Z",
  "expiry_time": "2025-03-15T21:53:00.000Z",
  "upload_url": "https://api.notion.com/v1/file_uploads/b52b8ed6-e029-4707-a671-832549c09de3/send",
  "archived": false,
  "status": "pending",
  "filename": "test.txt",
  "content_type": "text/plain",
  "content_length": 1024
}
```

### Response Fields

| Field | Type | Description |
|-------|------|-------------|
| `id` | string (UUID) | File Upload ID (use to reference this upload) |
| `object` | string | Always `"file_upload"` |
| `created_time` | string (ISO 8601) | Creation timestamp |
| `last_edited_time` | string (ISO 8601) | Last update timestamp |
| `expiry_time` | string (ISO 8601) | When upload URL expires |
| `upload_url` | string | URL to send file content (single_part mode) |
| `archived` | boolean | Whether upload is archived |
| `status` | string | Status: `pending`, `uploaded`, `expired`, `failed` |
| `filename` | string | Filename |
| `content_type` | string | MIME type |
| `content_length` | integer | File size in bytes |

### Filename Constraints

**Maximum length:** 900 bytes (including extension)

**Recommendations:**
- Use shorter names for performance
- Include file extension
- Match extension to content_type

### SDK Implementation

```python
async def create(
    self,
    *,
    mode: str = "single_part",
    filename: Optional[str] = None,
    content_type: Optional[str] = None,
    number_of_parts: Optional[int] = None,
    external_url: Optional[str] = None
) -> FileUpload:
    """
    Initiate a file upload.

    Args:
        mode: Upload mode (single_part, multi_part, external_url)
        filename: File name (required for multi_part/external_url)
        content_type: MIME type
        number_of_parts: Number of parts (multi_part mode)
        external_url: Public URL to import (external_url mode)

    Returns:
        FileUpload object with upload instructions

    Raises:
        ValueError: If invalid parameters
        PermissionError: If lacking file upload capability
    """
    payload = {"mode": mode}

    if filename:
        payload["filename"] = filename
    if content_type:
        payload["content_type"] = content_type
    if number_of_parts:
        if not (1 <= number_of_parts <= 1000):
            raise ValueError("number_of_parts must be between 1 and 1000")
        payload["number_of_parts"] = number_of_parts
    if external_url:
        payload["external_url"] = external_url

    response = await self._client.request(
        "POST",
        "/file_uploads",
        json=payload
    )

    return FileUpload.from_dict(response, self._client)

async def upload_single_part(
    self,
    file_path: str,
    filename: Optional[str] = None
) -> FileUpload:
    """
    Upload a single file (up to 20MB).

    Args:
        file_path: Path to file on disk
        filename: Optional custom filename

    Returns:
        FileUpload object after successful upload

    Raises:
        FileNotFoundError: If file doesn't exist
        ValueError: If file too large (>20MB)
    """
    import os
    import pathlib

    file_path = pathlib.Path(file_path)

    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    file_size = file_path.stat().st_size
    if file_size > 20 * 1024 * 1024:  # 20MB
        raise ValueError("File too large for single_part mode")

    # Create file upload
    file_upload = await self.create(
        filename=filename or file_path.name,
        content_type=self._get_mime_type(file_path)
    )

    # Send file content
    with open(file_path, "rb") as f:
        await self.send(file_upload.id, f.read())

    return file_upload

async def upload_from_url(
    self,
    url: str,
    filename: Optional[str] = None
) -> FileUpload:
    """
    Import a file from a public URL.

    Args:
        url: Public HTTPS URL
        filename: Optional custom filename

    Returns:
        FileUpload object

    Raises:
        ValueError: If URL is not HTTPS or invalid
    """
    if not url.startswith("https://"):
        raise ValueError("URL must use HTTPS")

    return await self.create(
        mode="external_url",
        external_url=url,
        filename=filename
    )
```

### Errors

| Status Code | Error | Description |
|-------------|-------|-------------|
| 400 | `bad_request` | Invalid parameters or filename too long |
| 400 | `validation_error` | Invalid mode or parameters |
| 429 | `rate_limited` | Request rate limit exceeded |

### Example Usage

```python
# Simple single-part upload
file_upload = await client.file_uploads.create(
    mode="single_part",
    filename="document.pdf",
    content_type="application/pdf"
)

# Get upload URL and send file
upload_url = file_upload.upload_url
# ... send file content to upload_url ...

# Multi-part upload (large files)
file_upload = await client.file_uploads.create(
    mode="multi_part",
    filename="large-video.mp4",
    content_type="video/mp4",
    number_of_parts=5
)

# Send each part
for part_number in range(1, 6):
    await client.file_uploads.send(
        file_upload.id,
        part_data,
        part_number=part_number
    )

# Complete upload
await client.file_uploads.complete(file_upload.id)

# Import from URL
file_upload = await client.file_uploads.upload_from_url(
    url="https://example.com/images/photo.jpg",
    filename="imported-photo.jpg"
)
```

---

## Send a File Upload

Transmits file contents to Notion for an upload.

### Endpoint

```
POST https://api.notion.com/v1/file_uploads/{file_upload_id}/send
```

### Path Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `file_upload_id` | string (UUID) | Yes | File Upload ID from Create endpoint |

### Body Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `file` | file | Yes | Raw binary file contents |
| `part_number` | string | Conditional* | Current part number (1-1000) |

\* Required when mode is `multi_part`

### Content-Type

**Important:** This endpoint uses `multipart/form-data` (not JSON like other Notion APIs).

```
Content-Type: multipart/form-data; boundary=----WebKitFormBoundary
```

Most request libraries handle this automatically when given a form data object.

### Headers

| Header | Type | Required | Description |
|--------|------|----------|-------------|
| `Authorization` | string | Yes | Bearer `{integration_token}` |
| `Notion-Version` | string | Yes | The API version to use (latest: `2025-09-03`) |

### Response

Returns updated File Upload object.

```json
{
  "id": "b52b8ed6-e029-4707-a671-832549c09de3",
  "object": "file_upload",
  "created_time": "2025-03-15T20:53:00.000Z",
  "last_edited_time": "2025-03-15T20:57:00.000Z",
  "expiry_time": "2025-03-15T21:53:00.000Z",
  "upload_url": null,
  "archived": false,
  "status": "uploaded",
  "filename": "test.txt",
  "content_type": "text/plain",
  "content_length": 1024
}
```

**Status changes:**
- After single-part send: `"pending"` → `"uploaded"`
- After multi-part send: Status remains `"pending"` until Complete is called

### SDK Implementation

```python
async def send(
    self,
    file_upload_id: str,
    file_data: bytes,
    part_number: Optional[int] = None
) -> FileUpload:
    """
    Send file content for upload.

    Args:
        file_upload_id: File Upload ID
        file_data: Raw binary file content
        part_number: Part number for multi-part uploads (1-1000)

    Returns:
        Updated FileUpload object

    Raises:
        NotFoundError: If file upload doesn't exist
        ValueError: If part_number out of range
    """
    files = {"file": file_data}
    data = {}

    if part_number:
        if not (1 <= part_number <= 1000):
            raise ValueError("part_number must be between 1 and 1000")
        data["part_number"] = str(part_number)

    response = await self._client.request(
        "POST",
        f"/file_uploads/{file_upload_id}/send",
        files=files,
        data=data
    )

    return FileUpload.from_dict(response, self._client)

async def send_from_path(
    self,
    file_upload_id: str,
    file_path: str
) -> FileUpload:
    """
    Send file content from disk.

    Args:
        file_upload_id: File Upload ID
        file_path: Path to file

    Returns:
        Updated FileUpload object
    """
    with open(file_path, "rb") as f:
        file_data = f.read()

    return await self.send(file_upload_id, file_data)
```

### Errors

| Status Code | Error | Description |
|-------------|-------|-------------|
| 400 | `bad_request` | Invalid part number |
| 404 | `object_not_found` | File upload doesn't exist |
| 429 | `rate_limited` | Request rate limit exceeded |

### Example Usage

```python
# Using requests library (single part)
import requests

file_upload = await client.file_uploads.create(
    filename="document.pdf",
    content_type="application/pdf"
)

with open("document.pdf", "rb") as f:
    response = requests.post(
        file_upload.upload_url,
        data=f,
        headers={"Authorization": f"Bearer {token}"}
    )

# Using SDK helper
file_upload = await client.file_uploads.upload_single_part(
    file_path="document.pdf"
)

# Multi-part upload
file_upload = await client.file_uploads.create(
    mode="multi_part",
    filename="large.zip",
    content_type="application/zip",
    number_of_parts=3
)

# Send parts (can be concurrent)
chunk_size = os.path.getsize("large.zip") // 3

with open("large.zip", "rb") as f:
    for part in range(3):
        f.seek(chunk_size * part)
        chunk = f.read(chunk_size)
        await client.file_uploads.send(
            file_upload.id,
            chunk,
            part_number=part + 1
        )

# Complete upload
await client.file_uploads.complete(file_upload.id)
```

---

## Complete a File Upload

Finalizes a multi-part file upload after all parts have been sent.

### Endpoint

```
POST https://api.notion.com/v1/file_uploads/{file_upload_id}/complete
```

### Path Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `file_upload_id` | string (UUID) | Yes | File Upload ID from Create endpoint |

### Headers

| Header | Type | Required | Description |
|--------|------|----------|-------------|
| `Authorization` | string | Yes | Bearer `{integration_token}` |
| `Notion-Version` | string | Yes | The API version to use (latest: `2025-09-03`) |

### When to Call

Only required for `multi_part` mode uploads. Call after all parts (1 through number_of_parts) have been successfully sent.

**Skip for:**
- `single_part` mode uploads (automatically complete)
- `external_url` mode uploads (automatically complete)

### Response

Returns updated File Upload object with status `"uploaded"`.

```json
{
  "id": "b52b8ed6-e029-4707-a671-832549c09de3",
  "object": "file_upload",
  "created_time": "2025-03-15T20:53:00.000Z",
  "last_edited_time": "2025-03-15T20:57:00.000Z",
  "expiry_time": "2025-03-15T21:53:00.000Z",
  "upload_url": null,
  "archived": false,
  "status": "uploaded",
  "filename": "test.txt",
  "content_type": "text/plain",
  "content_length": 1024
}
```

### SDK Implementation

```python
async def complete(
    self,
    file_upload_id: str
) -> FileUpload:
    """
    Complete a multi-part file upload.

    Args:
        file_upload_id: File Upload ID

    Returns:
        Updated FileUpload object with status "uploaded"

    Raises:
        NotFoundError: If file upload doesn't exist
        ValueError: If not all parts have been sent
    """
    response = await self._client.request(
        "POST",
        f"/file_uploads/{file_upload_id}/complete"
    )

    return FileUpload.from_dict(response, self._client)
```

### Errors

| Status Code | Error | Description |
|-------------|-------|-------------|
| 400 | `bad_request` | Not all parts sent or invalid upload |
| 404 | `object_not_found` | File upload doesn't exist |
| 429 | `rate_limited` | Request rate limit exceeded |

### Example Usage

```python
# Complete multi-part upload
file_upload = await client.file_uploads.complete(
    "file-upload-id-here"
)

print(f"Upload complete: {file_upload.status}")
```

---

## Retrieve a File Upload

Gets details of a File Upload object.

### Endpoint

```
GET https://api.notion.com/v1/file_uploads/{file_upload_id}
```

### Path Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `file_upload_id` | string (UUID) | Yes | File Upload ID |

### Headers

| Header | Type | Required | Description |
|--------|------|----------|-------------|
| `Authorization` | string | Yes | Bearer `{integration_token}` |
| `Notion-Version` | string | Yes | The API version to use (latest: `2025-09-03`) |

### Response

Returns a File Upload object with current status.

```json
{
  "id": "b52b8ed6-e029-4707-a671-832549c09de3",
  "object": "file_upload",
  "created_time": "2025-03-15T20:53:00.000Z",
  "last_edited_time": "2025-03-15T20:57:00.000Z",
  "expiry_time": "2025-03-15T21:53:00.000Z",
  "upload_url": null,
  "archived": false,
  "status": "uploaded",
  "filename": "test.txt",
  "content_type": "text/plain",
  "content_length": 1024
}
```

### SDK Implementation

```python
async def get(
    self,
    file_upload_id: str
) -> FileUpload:
    """
    Retrieve file upload details.

    Args:
        file_upload_id: File Upload ID

    Returns:
        FileUpload object

    Raises:
        NotFoundError: If file upload doesn't exist
    """
    response = await self._client.request(
        "GET",
        f"/file_uploads/{file_upload_id}"
    )

    return FileUpload.from_dict(response, self._client)

async def wait_for_upload(
    self,
    file_upload_id: str,
    timeout: int = 60
) -> FileUpload:
    """
    Wait for upload to complete (for external URL imports).

    Args:
        file_upload_id: File Upload ID
        timeout: Maximum wait time in seconds

    Returns:
        Completed FileUpload object

    Raises:
        TimeoutError: If upload doesn't complete in time
    """
    import asyncio

    start = time.time()
    while time.time() - start < timeout:
        file_upload = await self.get(file_upload_id)

        if file_upload.status == "uploaded":
            return file_upload

        if file_upload.status in ("expired", "failed"):
            raise RuntimeError(f"Upload failed with status: {file_upload.status}")

        await asyncio.sleep(1)

    raise TimeoutError("Upload did not complete in time")
```

### Errors

| Status Code | Error | Description |
|-------------|-------|-------------|
| 404 | `object_not_found` | File upload doesn't exist |
| 429 | `rate_limited` | Request rate limit exceeded |

### Example Usage

```python
# Get upload details
file_upload = await client.file_uploads.get("file-upload-id")

print(f"Status: {file_upload.status}")
print(f"Filename: {file_upload.filename}")
print(f"Size: {file_upload.content_length} bytes")
print(f"Expires: {file_upload.expiry_time}")

# Wait for external URL import to complete
file_upload = await client.file_uploads.wait_for_upload(
    "file-upload-id",
    timeout=120
)
```

---

## List File Uploads

Retrieves file uploads for the current bot integration, sorted by most recent first.

### Endpoint

```
GET https://api.notion.com/v1/file_uploads
```

### Query Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `status` | string | No | - | Filter by status (`pending`, `uploaded`, `expired`, `failed`) |
| `start_cursor` | string | No | - | Pagination cursor |
| `page_size` | integer | No | 100 | Number of results (max: 100) |

### Headers

| Header | Type | Required | Description |
|--------|------|----------|-------------|
| `Authorization` | string | Yes | Bearer `{integration_token}` |
| `Notion-Version` | string | Yes | The API version to use (latest: `2025-09-03`) |

### Response

Returns a paginated list of File Upload objects.

```json
{
  "object": "list",
  "results": [
    {
      "id": "file-upload-id-1",
      "object": "file_upload",
      "created_time": "2025-03-15T20:53:00.000Z",
      "last_edited_time": "2025-03-15T20:57:00.000Z",
      "status": "uploaded",
      "filename": "document.pdf",
      "content_type": "application/pdf",
      "content_length": 1024
    },
    {
      "id": "file-upload-id-2",
      "object": "file_upload",
      "created_time": "2025-03-14T10:30:00.000Z",
      "last_edited_time": "2025-03-14T10:35:00.000Z",
      "status": "expired",
      "filename": "image.png",
      "content_type": "image/png",
      "content_length": 51200
    }
  ],
  "next_cursor": null,
  "has_more": false
}
```

### Pagination

The endpoint uses cursor-based pagination:

1. First request: Call without `start_cursor`
2. Check `has_more` in the response
3. If `has_more` is `true`, use `next_cursor` for next request
4. Repeat until `has_more` is `false`

### SDK Implementation

```python
async def list(
    self,
    *,
    status: Optional[str] = None,
    page_size: int = 100,
    start_cursor: Optional[str] = None
) -> PaginatedResponse:
    """
    List file uploads for the integration.

    Args:
        status: Filter by status (pending, uploaded, expired, failed)
        page_size: Results per page (max: 100)
        start_cursor: Pagination cursor

    Returns:
        PaginatedResponse with FileUpload objects

    Raises:
        ValueError: If invalid status value
    """
    params = {"page_size": page_size}

    if status:
        valid_statuses = ["pending", "uploaded", "expired", "failed"]
        if status not in valid_statuses:
            raise ValueError(f"Invalid status. Must be one of: {valid_statuses}")
        params["status"] = status

    if start_cursor:
        params["start_cursor"] = start_cursor

    response = await self._client.request(
        "GET",
        "/file_uploads",
        params=params
    )

    return PaginatedResponse(
        results=[
            FileUpload.from_dict(data, self._client)
            for data in response.get("results", [])
        ],
        has_more=response.get("has_more", False),
        next_cursor=response.get("next_cursor")
    )

async def list_all(
    self,
    *,
    status: Optional[str] = None
) -> List[FileUpload]:
    """
    List all file uploads with automatic pagination.

    Args:
        status: Filter by status

    Returns:
        List of all FileUpload objects
    """
    all_uploads = []
    cursor = None
    has_more = True

    while has_more:
        response = await self.list(
            status=status,
            start_cursor=cursor
        )

        all_uploads.extend(response.results)
        has_more = response.has_more
        cursor = response.next_cursor

    return all_uploads
```

### Errors

| Status Code | Error | Description |
|-------------|-------|-------------|
| 400 | `bad_request` | Invalid status value |
| 429 | `rate_limited` | Request rate limit exceeded |

### Example Usage

```python
# Get all uploads
uploads = await client.file_uploads.list_all()

for upload in uploads:
    print(f"{upload.filename} - {upload.status}")

# Filter by status
pending = await client.file_uploads.list_all(status="pending")
expired = await client.file_uploads.list_all(status="expired")
failed = await client.file_uploads.list_all(status="failed")

# Manual pagination
cursor = None
while True:
    response = await client.file_uploads.list(
        start_cursor=cursor
    )

    for upload in response.results:
        process_upload(upload)

    if not response.has_more:
        break

    cursor = response.next_cursor

# Clean up expired uploads
expired = await client.file_uploads.list_all(status="expired")
print(f"Found {len(expired)} expired uploads")
```

---

## Common Patterns

### Complete File Upload Workflow

```python
async def upload_file(
    self,
    file_path: str,
    use_file_upload_id: Optional[str] = None
) -> str:
    """
    Complete workflow to upload a file.

    Args:
        file_path: Path to file
        use_file_upload_id: Optionally return the file_upload_id

    Returns:
        File Upload ID if use_file_upload_id is True
    """
    # Create file upload
    file_upload = await self.upload_single_part(file_path)

    # Use file_upload_id in other operations
    # For example, attach to a comment
    if use_file_upload_id:
        return file_upload.id

    return "Upload complete"
```

### Attach File to Comment

```python
async def attach_file_to_comment(
    self,
    page_id: str,
    file_upload_id: str,
    comment_text: str
) -> Comment:
    """Attach uploaded file to a comment."""
    return await self.comments.create(
        parent=page_id,
        rich_text=[{
            "type": "text",
            "text": {"content": comment_text}
        }],
        attachments=[{
            "file_upload_id": file_upload_id
        }]
    )
```

### Upload Multiple Files

```python
async def upload_multiple_files(
    self,
    file_paths: List[str],
    callback: Optional[callable] = None
) -> List[FileUpload]:
    """
    Upload multiple files concurrently.

    Args:
        file_paths: List of file paths
        callback: Optional callback after each upload

    Returns:
        List of FileUpload objects
    """
    uploads = []

    for file_path in file_paths:
        try:
            upload = await self.upload_single_part(file_path)
            uploads.append(upload)

            if callback:
                callback(file_path, upload, None)
        except Exception as e:
            if callback:
                callback(file_path, None, e)

    return uploads
```

### Upload with Progress Tracking

```python
async def upload_with_progress(
    self,
    file_path: str,
    chunk_size: int = 1024 * 1024  # 1MB
) -> FileUpload:
    """
    Upload large file with progress tracking.

    Args:
        file_path: Path to file
        chunk_size: Size of each chunk

    Returns:
        FileUpload object
    """
    import os
    import pathlib

    file_path = pathlib.Path(file_path)
    file_size = file_path.stat().st_size

    # Determine if multi-part is needed
    if file_size <= 20 * 1024 * 1024:  # 20MB
        # Single part
        return await self.upload_single_part(file_path)
    else:
        # Multi-part upload
        num_parts = (file_size + chunk_size - 1) // chunk_size
        num_parts = max(1, min(num_parts, 1000))

        file_upload = await self.create(
            mode="multi_part",
            filename=file_path.name,
            content_type=self._get_mime_type(file_path),
            number_of_parts=num_parts
        )

        parts_sent = 0

        with open(file_path, "rb") as f:
            while parts_sent < num_parts:
                chunk = f.read(chunk_size)
                if not chunk:
                    break

                await self.send(
                    file_upload.id,
                    chunk,
                    part_number=parts_sent + 1
                )

                parts_sent += 1
                progress = (parts_sent / num_parts) * 100
                print(f"Progress: {progress:.1f}%")

        # Complete upload
        return await self.complete(file_upload.id)
```

### Retry Failed Uploads

```python
async def upload_with_retry(
    self,
    file_path: str,
    max_retries: int = 3
) -> FileUpload:
    """
    Upload file with retry logic.

    Args:
        file_path: Path to file
        max_retries: Maximum number of retry attempts

    Returns:
        FileUpload object

    Raises:
        RuntimeError: If all retries fail
    """
    import asyncio

    for attempt in range(max_retries):
        try:
            return await self.upload_single_part(file_path)
        except Exception as e:
            if attempt == max_retries - 1:
                raise RuntimeError(f"Upload failed after {max_retries} attempts: {e}")

            print(f"Upload failed (attempt {attempt + 1}), retrying...")
            await asyncio.sleep(2 ** attempt)  # Exponential backoff
```

---

## Best Practices

1. **Choose Right Mode**
   - Files ≤ 20MB: Use `single_part`
   - Files > 20MB: Use `multi_part`
   - Already hosted: Use `external_url`

2. **Filename Management**
   - Keep names under 900 bytes
   - Include file extensions
   - Match extensions to content_type

3. **Handle Expiration**
   - Upload URLs expire in ~1 hour
   - Send files promptly after creation
   - Don't cache upload URLs

4. **Progress Tracking**
   - Implement progress for large files
   - Report progress to users
   - Track parts in multi-part uploads

5. **Error Handling**
   - Handle failed uploads gracefully
   - Implement retry logic with exponential backoff
   - Validate files before upload

6. **Clean Up**
   - Periodically clean up expired uploads
   - Use List File Uploads to track status
   - Remove references to failed uploads

7. **Security**
   - Validate file types before upload
   - Scan for malware if needed
   - Don't expose sensitive file URLs
   - Validate external URLs before importing

8. **Performance**
   - Use multi-part for large files
   - Upload concurrently when possible
   - Implement async operations
   - Monitor rate limits

---

## MIME Type Reference

### Common MIME Types

| File Type | MIME Type |
|-----------|-----------|
| PDF | `application/pdf` |
| JPEG | `image/jpeg` |
| PNG | `image/png` |
| GIF | `image/gif` |
| SVG | `image/svg+xml` |
| MP4 | `video/mp4` |
| MP3 | `audio/mpeg` |
| ZIP | `application/zip` |
| JSON | `application/json` |
| Text | `text/plain` |
| HTML | `text/html` |

### Detect MIME Type

```python
import mimetypes

def get_mime_type(file_path: str) -> str:
    """Detect MIME type from file extension."""
    mime_type, _ = mimetypes.guess_type(file_path)
    return mime_type or "application/octet-stream"
```

---

## Related Documentation

- [Files and Media](./files.md) - File object types and concepts
- [Comments API](./comments-api.md) - Using file uploads in comments
- [Blocks API](./block/blocks-api.md) - Image, file, PDF blocks
- [Pages API](./pages/pages-api.md) - Page covers/icons
