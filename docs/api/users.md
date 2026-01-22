# Users

## Introduction

A **User** object represents a user in a Notion workspace. Users include:
- Full workspace members
- Guests
- Integrations (bots)

## Where Users Appear in the API

User objects appear in nearly all objects returned by the API:

| Location | Description |
|----------|-------------|
| **Block** | In `created_by` and `last_edited_by` fields |
| **Page** | In `created_by`, `last_edited_by`, and people property items |
| **Database** | In `created_by` and `last_edited_by` fields |
| **Rich Text** | As user mentions |
| **Property** | When the property is a people property |

## Capabilities and Access

User objects always contain `object` and `id` keys. Additional properties appear based on:
- Context (rich text or page property)
- Bot capabilities to access those properties

See the [Capabilities guide](https://developers.notion.com/docs/authorization) for details.

## User Object Structure

### All Users (Common Fields)

These fields are shared by all users, including people and bots.

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `object` | string | Always `"user"` | `"user"` |
| `id` | string (UUID) | Unique identifier | `"e79a0b74-3381-44d0-a1dc-9ed80e62b53d"` |
| `type` | string (enum) | User type: `"person"` or `"bot"` | `"person"` |
| `name` | string (optional) | Display name in Notion | `"Avocado Lovelace"` |
| `avatar_url` | string (optional) | Avatar image URL | `"https://secure.notion-static.com/..."` |

Fields marked with `*` are always present.

### Person User

When `type` is `"person"`, the user object includes additional fields:

```json
{
  "object": "user",
  "id": "e79a0b74-3aba-4149-9f74-0bb5791a6ee6",
  "type": "person",
  "name": "Avocado Lovelace",
  "avatar_url": "https://secure.notion-static.com/e6a352a8-8381-44d0-a1dc-9ed80e62b53d.jpg",
  "person": {
    "email": "avo@example.org"
  }
}
```

#### Person Fields

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `person` | object | Properties only for non-bot users | `{ "email": "..." }` |
| `person.email` | string | Email address (requires user capabilities) | `"avo@example.org"` |

**Note:** The `email` field is only present if the integration has user capabilities that allow access to email addresses.

### Bot User

When `type` is `"bot"`, the user object represents an integration:

```json
{
  "object": "user",
  "id": "9188c6a5-7381-452f-b3dc-d4865aa89bdf",
  "type": "bot",
  "name": "Test Integration",
  "avatar_url": null,
  "bot": {
    "owner": {
      "type": "workspace",
      "workspace": true
    },
    "workspace_name": "Ada Lovelace's Notion",
    "workspace_id": "17ab3186-873d-418f-b899-c3f6a43f68de",
    "workspace_limits": {
      "max_file_upload_size_in_bytes": 5242880
    }
  }
}
```

#### Bot Fields

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `bot` | object | Bot-specific properties | `{ "owner": {...}, ... }` |
| `bot.owner` | object | Information about bot owner | `{ "type": "workspace", ... }` |
| `bot.owner.type` | string (enum) | Owner type: `"workspace"` or `"user"` | `"workspace"` |
| `bot.workspace_name` | string (nullable) | Workspace name if owner is workspace | `"Ada's Notion"` |
| `bot.workspace_id` | string (UUID) | Bot's workspace ID | `"17ab3186-..."` |
| `bot.workspace_limits` | object | Workspace limits | `{ "max_file_upload_size_in_bytes": ... }` |
| `bot.workspace_limits.max_file_upload_size_in_bytes` | integer | Max file upload size in bytes | `5242880` |

**Note:** `workspace_name` is `null` when `owner.type` is `"user"`.

## API Endpoints

### Retrieve your token's user / bot info

```
GET /v1/users/me
```

Returns information about the bot/user associated with the API token.

**Example response:**
```json
{
  "object": "user",
  "id": "9188c6a5-7381-452f-b3dc-d4865aa89bdf",
  "name": "Test Integration",
  "avatar_url": null,
  "type": "bot",
  "bot": {
    "owner": {
      "type": "workspace",
      "workspace": true
    },
    "workspace_name": "Ada Lovelace's Notion",
    "workspace_id": "17ab3186-873d-418f-b899-c3f6a43f68de",
    "workspace_limits": {
      "max_file_upload_size_in_bytes": 5242880
    }
  }
}
```

### Retrieve a user

```
GET /v1/users/{user_id}
```

Retrieves a User object using the ID specified.

**Path parameters:**
- `user_id` (string): Identifier for a Notion user

**Example response (person):**
```json
{
  "object": "user",
  "id": "e79a0b74-3aba-4149-9f74-0bb5791a6ee6",
  "type": "person",
  "name": "Avocado Lovelace",
  "avatar_url": "https://secure.notion-static.com/e6a352a8-8381-44d0-a1dc-9ed80e62b53d.jpg"
}
```

### List all users

```
GET /v1/users
```

Returns a paginated list of [User](#user-object) objects for all users in the workspace.

**Query parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `start_cursor` | string | Cursor for pagination |
| `page_size` | integer | Number of users per page (default: 100, max: 100) |

**Example response:**
```json
{
  "object": "list",
  "results": [
    {
      "object": "user",
      "id": "e79a0b74-3aba-4149-9f74-0bb5791a6ee6",
      "type": "person",
      "name": "Avocado Lovelace",
      "avatar_url": "https://..."
    },
    {
      "object": "user",
      "id": "9188c6a5-7381-452f-b3dc-d4865aa89bdf",
      "type": "bot",
      "name": "Test Integration",
      "avatar_url": null
    }
  ],
  "next_cursor": "eyJza2lwIjo0LCJvd...",
  "has_more": true
}
```

## User Types Summary

| Type | Description | Additional Fields |
|------|-------------|-------------------|
| `person` | Human user (member or guest) | `person.email` |
| `bot` | Integration/bot | `bot.owner`, `bot.workspace_name`, `bot.workspace_id`, `bot.workspace_limits` |

## SDK Architecture

### User Class

```python
from dataclasses import dataclass
from typing import Optional
from datetime import datetime
from uuid import UUID

@dataclass
class PersonDetails:
    """Details specific to person users."""
    email: Optional[str] = None

@dataclass
class BotOwner:
    """Owner information for bot users."""
    type: str  # "workspace" or "user"
    workspace: bool = False

@dataclass
class WorkspaceLimits:
    """Workspace limits for bot users."""
    max_file_upload_size_in_bytes: int

@dataclass
class BotDetails:
    """Details specific to bot users."""
    owner: BotOwner
    workspace_name: Optional[str] = None
    workspace_id: Optional[UUID] = None
    workspace_limits: Optional[WorkspaceLimits] = None

@dataclass
class User:
    """Notion user object."""
    object: str = "user"
    id: UUID = None
    type: str = None  # "person" or "bot"
    name: Optional[str] = None
    avatar_url: Optional[str] = None
    person: Optional[PersonDetails] = None
    bot: Optional[BotDetails] = None

    def __post_init__(self):
        """Validate user object after initialization."""
        if self.type == "person" and self.person is None:
            self.person = PersonDetails()
        elif self.type == "bot" and self.bot is None:
            raise ValueError("Bot users must have bot details")

    @property
    def is_person(self) -> bool:
        """Check if user is a person."""
        return self.type == "person"

    @property
    def is_bot(self) -> bool:
        """Check if user is a bot."""
        return self.type == "bot"

    @property
    def email(self) -> Optional[str]:
        """Get email address (for person users)."""
        if self.person:
            return self.person.email
        return None

    @property
    def workspace_name(self) -> Optional[str]:
        """Get workspace name (for bot users)."""
        if self.bot:
            return self.bot.workspace_name
        return None

    @property
    def max_file_upload_size(self) -> Optional[int]:
        """Get max file upload size in bytes (for bot users)."""
        if self.bot and self.bot.workspace_limits:
            return self.bot.workspace_limits.max_file_upload_size_in_bytes
        return None
```

### UserManager

```python
from typing import List, Optional

class UserManager:
    """Manager for user-related operations."""

    def __init__(self, client: "Client"):
        self._client = client

    async def me(self) -> User:
        """
        Retrieve information about the current bot/user.

        Returns:
            User: Current user/bot information
        """
        response = await self._client._request("GET", "/v1/users/me")
        return User(**response)

    async def get(self, user_id: str) -> User:
        """
        Retrieve a specific user by ID.

        Args:
            user_id: UUID of the user

        Returns:
            User: User object
        """
        response = await self._client._request("GET", f"/v1/users/{user_id}")
        return User(**response)

    async def list(
        self,
        *,
        start_cursor: Optional[str] = None,
        page_size: int = 100
    ) -> PaginatedResponse[User]:
        """
        List all users in the workspace.

        Args:
            start_cursor: Cursor for pagination
            page_size: Number of users per page (max 100)

        Returns:
            PaginatedResponse of User objects
        """
        params = {"page_size": min(page_size, 100)}
        if start_cursor:
            params["start_cursor"] = start_cursor

        response = await self._client._request("GET", "/v1/users", params=params)
        return PaginatedResponse(
            results=[User(**u) for u in response["results"]],
            next_cursor=response.get("next_cursor"),
            has_more=response.get("has_more", False),
            client=self._client
        )
```

### Usage Examples

```python
import better_notion

# Initialize client
client = better_notion.Client(auth=token)

# Get current bot/user info
me = await client.users.me()
print(f"I am: {me.name} ({me.type})")
if me.is_bot:
    print(f"Workspace: {me.workspace_name}")
    print(f"Max upload size: {me.max_file_upload_size} bytes")

# Get a specific user
user = await client.users.get(user_id="e79a0b74-3aba-4149-9f74-0bb5791a6ee6")
print(f"User: {user.name}")
if user.is_person:
    print(f"Email: {user.email}")

# List all users (with pagination)
users = await client.users.list()
async for user in users:
    print(f"- {user.name} ({user.type})")

# Or iterate manually
response = await client.users.list(page_size=50)
for user in response.results:
    print(f"- {user.name}")

while response.has_more:
    response = await response.next()
    for user in response.results:
        print(f"- {user.name}")
```

## Partial User References

Many objects reference users with a subset of fields:

```python
@dataclass
class PartialUser:
    """Partial user reference (created_by, last_edited_by)."""
    object: str = "user"
    id: UUID = None

    async def fetch_full(self) -> User:
        """Fetch full user object from API."""
        if not self._client:
            raise RuntimeError("No client reference")
        return await self._client.users.get(str(self.id))
```

## Best Practices

### 1. User Type Handling

Always check user type before accessing type-specific fields:

```python
# Good
if user.is_person:
    print(user.email)
elif user.is_bot:
    print(user.workspace_name)

# Bad - may raise AttributeError
print(user.email)  # None if user is bot
```

### 2. Capabilities Awareness

Not all integrations have access to all user fields:

```python
# Email requires user capabilities
if user.email:
    print(user.email)
else:
    print("Email not available - check capabilities")
```

### 3. Caching User Information

Cache user lookups to reduce API calls:

```python
class UserCache:
    """Simple in-memory user cache."""
    def __init__(self, client):
        self._client = client
        self._cache = {}

    async def get(self, user_id: str) -> User:
        if user_id not in self._cache:
            self._cache[user_id] = await self._client.users.get(user_id)
        return self._cache[user_id]
```

## Enterprise Features

### SCIM Provisioning

The SCIM API is available for workspaces on Notion's Enterprise Plan, allowing:
- Automated user provisioning
- Group management
- Synchronization with identity providers

### Single Sign-On (SSO)

SSO can be configured for Enterprise Plan workspaces, providing:
- Centralized authentication
- Enhanced security
- Simplified user management

## Related Documentation

- [Authorization](https://developers.notion.com/docs/authorization) - Capabilities and access control
- [Rich Text Objects](./rich-text-objects.md) - User mentions in rich text
- [Page Properties](./pages/page-properties.md) - People property values
- [Database Implementation](./databases/database-implementation.md) - User references in databases

---

**Next:** See [Blocks](./block/blocks-overview.md) for information about blocks and their `created_by`/`last_edited_by` user references.
