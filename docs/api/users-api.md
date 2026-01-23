# Users API Reference

Complete API reference for the Users operation in the Notion API.

## Overview

The Users endpoint allows you to retrieve information about users in a workspace. This is particularly useful for:

- Getting user information and details
- Listing all workspace users
- Retrieving bot user information
- User profile management
- Displaying user names and avatars

**Important:** Guests are not included in the list of all users.

---

## List All Users

Retrieves all users in the workspace, including bot users. Guests are not included.

### Endpoint

```
GET https://api.notion.com/v1/users
```

### Query Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `start_cursor` | string | No | - | Pagination cursor |
| `page_size` | integer | No | 100 | Number of results (max: 100) |

### Headers

| Header | Type | Required | Description |
|--------|------|----------|-------------|
| `Authorization` | string | Yes | Bearer `{integration_token}` |
| `Notion-Version` | string | Yes | The API version to use (latest: `2025-09-03`) |

### Required Capabilities

This endpoint requires the **user information** capability.

### Response

Returns a paginated list of user objects.

```json
{
  "object": "list",
  "results": [
    {
      "object": "user",
      "id": "d401ed46-182f-412a-9cc9-cc2abf5cc866",
      "type": "person",
      "name": "John Doe",
      "avatar_url": "https://example.com/avatar.jpg",
      "person": {
        "email": "john.doe@example.com"
      }
    },
    {
      "object": "user",
      "id": "3c4994e7-aec3-460a-856f-852e45be6498",
      "type": "bot",
      "name": "My Integration",
      "avatar_url": null,
      "bot": {}
    }
  ],
  "next_cursor": null,
  "has_more": false,
  "type": "user"
}
```

**Response Fields:**
| Field | Type | Description |
|-------|------|-------------|
| `object` | string | Always `"list"` |
| `results` | array | List of user objects |
| `next_cursor` | string | Cursor for next page (if has_more is true) |
| `has_more` | boolean | Whether more results exist |
| `type` | string | Always `"user"` |

**User Object Fields:**
| Field | Type | Description |
|-------|------|-------------|
| `object` | string | Always `"user"` |
| `id` | string | UUIDv4 identifier |
| `type` | string | Either `"person"` or `"bot"` |
| `name` | string | User name (may be null or empty) |
| `avatar_url` | string|null | Avatar URL (null if not set) |
| `person` | object|null | Present only if type is `"person"` |
| `bot` | object|null | Present only if type is `"bot"` |

**Person Object Fields:**
| Field | Type | Description |
|-------|------|-------------|
| `email` | string | User email address |

**Bot Object Fields:**
| Field | Type | Description |
|-------|------|-------------|
| (empty) | - | Bot object is currently empty for list results |

### Pagination

The endpoint uses cursor-based pagination:

1. First request: Call without `start_cursor`
2. Check `has_more` in the response
3. If `has_more` is `true`, use `next_cursor` as `start_cursor` for next request
4. Repeat until `has_more` is `false`

### SDK Implementation

```python
async def list_users(
    self,
    *,
    page_size: int = 100,
    start_cursor: Optional[str] = None
) -> PaginatedResponse:
    """
    List all users in the workspace.

    Args:
        page_size: Number of results (max: 100)
        start_cursor: Pagination cursor

    Returns:
        PaginatedResponse with user objects

    Raises:
        ValueError: If page_size > 100
    """
    if page_size > 100:
        raise ValueError("page_size cannot exceed 100")

    params = {}
    if page_size:
        params["page_size"] = page_size
    if start_cursor:
        params["start_cursor"] = start_cursor

    response = await self._client.request(
        "GET",
        "/users",
        params=params
    )

    return PaginatedResponse(
        results=[
            User.from_dict(item, self._client)
            for item in response.get("results", [])
        ],
        has_more=response.get("has_more", False),
        next_cursor=response.get("next_cursor")
    )

async def list_all_users(self) -> List[User]:
    """
    List all users with automatic pagination.

    Returns:
        List of all user objects in the workspace
    """
    all_users = []
    cursor = None
    has_more = True

    while has_more:
        response = await self.list_users(start_cursor=cursor)

        all_users.extend(response.results)
        has_more = response.has_more
        cursor = response.next_cursor

    return all_users
```

---

## Retrieve a User

Retrieves a specific user by ID.

### Endpoint

```
GET https://api.notion.com/v1/users/{user_id}
```

### Path Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `user_id` | string | Yes | UUIDv4 identifier of the user |

### Headers

| Header | Type | Required | Description |
|--------|------|----------|-------------|
| `Authorization` | string | Yes | Bearer `{integration_token}` |
| `Notion-Version` | string | Yes | The API version to use (latest: `2025-09-03`) |

### Required Capabilities

This endpoint requires the **user information** capability.

### Response

Returns a user object.

```json
{
  "object": "user",
  "id": "d401ed46-182f-412a-9cc9-cc2abf5cc866",
  "type": "person",
  "name": "John Doe",
  "avatar_url": "https://example.com/avatar.jpg",
  "person": {
    "email": "john.doe@example.com"
  }
}
```

### SDK Implementation

```python
async def get_user(
    self,
    user_id: str
) -> User:
    """
    Retrieve a specific user by ID.

    Args:
        user_id: UUIDv4 identifier of the user

    Returns:
        User object

    Raises:
        ValueError: If user_id is not a valid UUID
        NotFoundError: If user does not exist
    """
    # Validate UUID format
    try:
        uuid.UUID(user_id)
    except ValueError:
        raise ValueError(f"Invalid user_id format: {user_id}")

    response = await self._client.request(
        "GET",
        f"/users/{user_id}"
    )

    return User.from_dict(response, self._client)
```

---

## Retrieve Your Token's Bot User

Retrieves the bot user associated with the API token. This includes the owner information for the bot.

### Endpoint

```
GET https://api.notion.com/v1/users/me
```

### Headers

| Header | Type | Required | Description |
|--------|------|----------|-------------|
| `Authorization` | string | Yes | Bearer `{integration_token}` |
| `Notion-Version` | string | Yes | The API version to use (latest: `2025-09-03`) |

### Required Capabilities

This endpoint requires the **user information** capability.

### Response

Returns the bot user object with owner information.

```json
{
  "object": "user",
  "id": "3c4994e7-aec3-460a-856f-852e45be6498",
  "type": "bot",
  "name": "My Integration",
  "avatar_url": null,
  "bot": {
    "owner": {
      "type": "workspace",
      "workspace": true
    }
  }
}
```

**Bot Owner Types:**

**Workspace owner:**
```json
{
  "owner": {
    "type": "workspace",
    "workspace": true
  }
}
```

**User owner:**
```json
{
  "owner": {
    "type": "user",
    "user": {
      "object": "user",
      "id": "d401ed46-182f-412a-9cc9-cc2abf5cc866",
      "type": "person",
      "name": "John Doe",
      "avatar_url": "https://example.com/avatar.jpg",
      "person": {
        "email": "john.doe@example.com"
      }
    }
  }
}
```

### SDK Implementation

```python
async def get_bot_user(self) -> User:
    """
    Retrieve the bot user associated with the API token.

    Returns:
        Bot user object with owner information
    """
    response = await self._client.request(
        "GET",
        "/users/me"
    )

    return User.from_dict(response, self._client)
```

---

## User Object Model

```python
from typing import Optional
from dataclasses import dataclass
from datetime import datetime
import uuid

@dataclass
class UserOwner:
    """Owner information for a bot user."""
    type: str  # "workspace" or "user"
    workspace: Optional[bool] = None
    user: Optional['User'] = None

    @classmethod
    def from_dict(cls, data: dict, client) -> 'UserOwner':
        """Create UserOwner from API response."""
        owner = cls(type=data["type"])

        if data.get("workspace"):
            owner.workspace = data["workspace"]

        if data.get("user"):
            # Avoid circular import
            from .users import User
            owner.user = User.from_dict(data["user"], client)

        return owner

@dataclass
class UserPerson:
    """Person-specific user information."""
    email: str

    @classmethod
    def from_dict(cls, data: dict) -> 'UserPerson':
        """Create UserPerson from API response."""
        return cls(email=data["email"])

@dataclass
class UserBot:
    """Bot-specific user information."""
    owner: Optional[UserOwner] = None

    @classmethod
    def from_dict(cls, data: dict, client) -> 'UserBot':
        """Create UserBot from API response."""
        bot = cls()

        if data.get("owner"):
            bot.owner = UserOwner.from_dict(data["owner"], client)

        return bot

@dataclass
class User:
    """Notion user object."""
    id: uuid.UUID
    type: str  # "person" or "bot"
    name: Optional[str]
    avatar_url: Optional[str]
    person: Optional[UserPerson] = None
    bot: Optional[UserBot] = None

    def __init__(self, client):
        self._client = client

    @classmethod
    def from_dict(cls, data: dict, client) -> 'User':
        """Create User from API response."""
        user = cls(client)
        user.id = uuid.UUID(data["id"])
        user.type = data["type"]
        user.name = data.get("name")
        user.avatar_url = data.get("avatar_url")

        if data.get("person"):
            user.person = UserPerson.from_dict(data["person"])

        if data.get("bot"):
            user.bot = UserBot.from_dict(data["bot"], client)

        return user

    @property
    def email(self) -> Optional[str]:
        """Get email for person users."""
        return self.person.email if self.person else None

    @property
    def is_bot(self) -> bool:
        """Check if user is a bot."""
        return self.type == "bot"

    @property
    def is_person(self) -> bool:
        """Check if user is a person."""
        return self.type == "person"

    @property
    def display_name(self) -> str:
        """Get display name, falling back to email or ID."""
        if self.name:
            return self.name
        if self.email:
            return self.email
        return str(self.id)

    def __repr__(self) -> str:
        return f"User(id={self.id}, type={self.type}, name={self.name})"
```

---

## Errors

| Status Code | Error | Description |
|-------------|-------|-------------|
| 400 | `bad_request` | Invalid user_id format |
| 403 | `missing_permission` | Integration lacks user information capability |
| 404 | `object_not_found` | User not found |
| 429 | `rate_limited` | Request rate limit exceeded |

---

## Example Usage

```python
# List all users
response = await client.users.list_users(page_size=50)

for user in response.results:
    if user.is_person:
        print(f"Person: {user.display_name} ({user.email})")
    else:
        print(f"Bot: {user.display_name}")

# Get all users with pagination
all_users = await client.users.list_all_users()

people = [u for u in all_users if u.is_person]
bots = [u for u in all_users if u.is_bot]

print(f"Found {len(people)} people and {len(bots)} bots")

# Get a specific user
user = await client.users.get_user(
    user_id="d401ed46-182f-412a-9cc9-cc2abf5cc866"
)

print(f"User: {user.name}")
if user.email:
    print(f"Email: {user.email}")

# Get bot user info
bot_user = await client.users.get_bot_user()

print(f"Bot: {bot_user.name}")
if bot_user.bot and bot_user.bot.owner:
    owner_type = bot_user.bot.owner.type
    print(f"Owner type: {owner_type}")

    if owner_type == "user" and bot_user.bot.owner.user:
        owner = bot_user.bot.owner.user
        print(f"Owner: {owner.display_name}")
```

---

## Users Use Cases

### 1. Build User Directory

```python
async def build_user_directory(
    self
) -> dict:
    """
    Build a user directory for quick lookups.

    Returns:
        Dictionary mapping user_id to user object
    """
    users = await self.users.list_all_users()

    return {
        str(user.id): user
        for user in users
    }

# Usage
directory = await client.users.build_user_directory()

# Quick lookup
user_id = "d401ed46-182f-412a-9cc9-cc2abf5cc866"
user = directory.get(user_id)
if user:
    print(f"Found: {user.display_name}")
```

### 2. Find User by Email

```python
async def find_user_by_email(
    self,
    email: str
) -> Optional[User]:
    """
    Find a user by their email address.

    Args:
        email: Email address to search for

    Returns:
        User object if found, None otherwise
    """
    users = await self.users.list_all_users()

    for user in users:
        if user.email and user.email.lower() == email.lower():
            return user

    return None

# Usage
user = await client.users.find_user_by_email("john.doe@example.com")
if user:
    print(f"Found user: {user.name}")
```

### 3. Resolve User Mentions

```python
async def resolve_user_mentions(
    self,
    user_ids: List[str]
) -> List[User]:
    """
    Resolve a list of user IDs to user objects.

    Args:
        user_ids: List of user UUIDs

    Returns:
        List of user objects
    """
    # Build directory once
    directory = await self.users.build_user_directory()

    # Look up each user
    users = []
    for user_id in user_ids:
        user = directory.get(user_id)
        if user:
            users.append(user)

    return users

# Usage
mentioned_users = await client.users.resolve_user_mentions([
    "d401ed46-182f-412a-9cc9-cc2abf5cc866",
    "3c4994e7-aec3-460a-856f-852e45be6498"
])

for user in mentioned_users:
    print(f"@{user.display_name}")
```

### 4. Get Team Members

```python
async def get_team_members(
    self
) -> List[User]:
    """
    Get all human team members (excluding bots).

    Returns:
        List of person user objects
    """
    all_users = await self.users.list_all_users()

    return [u for u in all_users if u.is_person]

# Usage
team = await client.users.get_team_members()
print(f"Team size: {len(team)}")
```

### 5. Check Bot Owner

```python
async def get_bot_owner_info(self) -> dict:
    """
    Get information about the bot's owner.

    Returns:
        Dictionary with owner type and details
    """
    bot_user = await client.users.get_bot_user()

    if not bot_user.bot or not bot_user.bot.owner:
        return {"type": "unknown"}

    owner = bot_user.bot.owner

    if owner.type == "workspace":
        return {
            "type": "workspace",
            "name": "Workspace"
        }

    elif owner.type == "user" and owner.user:
        return {
            "type": "user",
            "id": str(owner.user.id),
            "name": owner.user.display_name,
            "email": owner.user.email
        }

    return {"type": owner.type}

# Usage
owner_info = await client.users.get_bot_owner_info()
print(f"Bot owned by: {owner_info['type']}")
```

### 6. Format User Names

```python
def format_user_name(user: User) -> str:
    """
    Format user name for display with fallbacks.

    Args:
        user: User object

    Returns:
        Formatted display name
    """
    if user.name:
        return user.name

    if user.is_person and user.email:
        # Extract name from email
        local_part = user.email.split("@")[0]
        return local_part.replace(".", " ").title()

    if user.is_bot:
        return f"Bot ({user.id})"

    return f"User ({user.id})"

# Usage
for user in await client.users.list_all_users():
    print(f"- {format_user_name(user)}")
```

### 7. User Avatar URL Helper

```python
def get_avatar_url(user: User, default: str = None) -> str:
    """
    Get user avatar URL with fallback.

    Args:
        user: User object
        default: Default URL if no avatar set

    Returns:
        Avatar URL or default
    """
    if user.avatar_url:
        return user.avatar_url

    if default:
        return default

    # Generate initials-based avatar
    if user.name:
        initials = "".join([n[0] for n in user.name.split()]).upper()[:2]
        return f"https://ui-avatars.com/api/?name={initials}&background=random"

    return "https://ui-avatars.com/api/?name=??&background=ccc"
```

---

## Optimization Tips

### 1. Cache User Directory

```python
from functools import lru_cache
from datetime import datetime, timedelta

class CachedUsers:
    def __init__(self, client):
        self._client = client
        self._cache = None
        self._cache_time = None
        self._cache_ttl = timedelta(minutes=5)

    async def get_directory(self) -> dict:
        """Get cached user directory."""
        now = datetime.now()

        if self._cache and (now - self._cache_time) < self._cache_ttl:
            return self._cache

        self._cache = await self._client.users.build_user_directory()
        self._cache_time = now
        return self._cache
```

### 2. Batch User Lookups

```python
# Good: Build directory once for multiple lookups
directory = await client.users.build_user_directory()

for user_id in user_id_list:
    user = directory.get(user_id)
    process(user)

# Avoid: Making individual API calls for each user
for user_id in user_id_list:
    user = await client.users.get_user(user_id)
    process(user)
```

### 3. Filter Server-Side

```python
# Good: Iterate once and filter
all_users = await client.users.list_all_users()
people = [u for u in all_users if u.is_person]

# Avoid: Multiple API calls for different types
people = await client.users.list_all_users()
bots = await client.users.list_all_users()
```

---

## Error Handling

```python
class UsersAPIError(Exception):
    """Base exception for users API errors."""
    pass

class UserNotFoundError(UsersAPIError):
    """User not found."""
    pass

class UsersPermissionError(UsersAPIError):
    """Missing user information capability."""
    pass

async def handle_user_errors(func):
    """Decorator for user error handling."""
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except HTTPError as e:
            if e.status == 403:
                raise UsersPermissionError(
                    "Integration requires user information capability"
                )
            elif e.status == 404:
                raise UserNotFoundError(f"User not found: {e}")
            elif e.status == 429:
                await asyncio.sleep(1)
                return await func(*args, **kwargs)
            else:
                raise UsersAPIError(f"Unexpected error: {e}")
    return wrapper
```

---

## Best Practices

1. **Cache User Data** - User information changes infrequently, cache appropriately
2. **Use Directory Pattern** - Build a lookup directory for multiple user operations
3. **Handle Missing Names** - Names may be null, provide fallbacks
4. **Check User Type** - Verify person vs bot before accessing type-specific fields
5. **Validate UUIDs** - Validate user_id format before making API calls
6. **Batch Operations** - Avoid individual API calls when possible
7. **Handle Avatars** - Avatar URLs may be null, provide defaults
8. **Email Privacy** - Handle email addresses appropriately
9. **Pagination** - Always handle has_more/next_cursor for large workspaces
10. **Error Handling** - Implement proper retry logic for rate limits

---

## Related Documentation

- [User Objects](./user-objects.md) - User object structure
- [Comments API](./comments-api.md) - Comment author information
- [Page Properties](./pages/page-properties.md) - People property type
- [Database Properties](./databases/database-properties.md) - People property type

---

**Users API Notes:**

- Requires **user information** capability
- Guests are excluded from user listings
- Bot users include owner information for /users/me endpoint
- Names and avatars may be null
- Email only available for person users
- Use /users/me to identify the bot user
