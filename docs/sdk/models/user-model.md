# User Model

High-level User SDK model with profile access and cache integration.

## Overview

The `User` model represents a Notion user (person or bot) with profile information and type detection.

```python
# Access user
user = await client.users.get(user_id)

# Profile info
print(f"Name: {user.name}")
print(f"Email: {user.email}")

# Type checking
if user.is_person:
    print(f"Person: {user.name}")
elif user.is_bot:
    print(f"Bot: {user.name}")
```

## Architecture

### User Class Structure

```python
# better_notion/_sdk/models/user.py

from better_notion._sdk.models.base import BaseEntity
from typing import Any

class User(BaseEntity):
    """SDK User model with profile information."""

    def __init__(self, api: NotionAPI, data: dict[str, Any]) -> None:
        """Initialize user with API response data.

        Args:
            api: Low-level NotionAPI client
            data: User object from Notion API
        """
        super().__init__(api, data)

        # Cache user type for frequent access
        self._user_type = self._data.get("type", "")

    @property
    def object(self) -> str:
        """Object type (always "user")."""
        return "user"
```

## Properties

### Metadata

```python
@property
def id(self) -> str:
    """Get user ID.

    Returns:
        User UUID

    Example:
        >>> user.id
        '123e4567-e89b-12d3-a456-426614174000'
    """
    return self._data["id"]

@property
def type(self) -> str:
    """Get user type.

    Returns:
        'person' or 'bot'

    Example:
        >>> user.type
        'person'
    """
    return self._user_type
```

### Type Checkers

```python
@property
def is_person(self) -> bool:
    """Check if user is a person.

    Returns:
        True if user is a person

    Example:
        >>> if user.is_person:
        ...     print(f"Email: {user.email}")
    """
    return self._user_type == "person"

@property
def is_bot(self) -> bool:
    """Check if user is a bot.

    Returns:
        True if user is a bot (integration, workspace, etc.)

    Example:
        >>> if user.is_bot:
        ...     print(f"Bot: {user.name}")
    """
    return self._user_type == "bot"
```

### Profile Information

#### Common Properties

```python
@property
def name(self) -> str:
    """Get user name.

    Returns:
        Display name (full name for person, bot name for bot)

    Example:
        >>> user.name
        'John Doe'
    """
    return self._data.get("name", "")

@property
def avatar_url(self) -> str | None:
    """Get avatar image URL.

    Returns:
        Avatar URL or None

    Example:
        >>> if user.avatar_url:
        ...     print(f"Avatar: {user.avatar_url}")
    """
    avatar_data = self._data.get("avatar_url")
    return avatar_data if avatar_data else None
```

#### Person-Specific Properties

```python
@property
def email(self) -> str | None:
    """Get email address (for person users).

    Returns:
        Email address or None (for bots)

    Example:
        >>> if user.is_person:
        ...     print(f"Email: {user.email}")

    Note:
        Returns None for bot users
        Requires appropriate permissions
    """
    if self._user_type == "person":
        return self._data.get("person", {}).get("email")
    return None

@property
def family_name(self) -> str | None:
    """Get family name (for person users).

    Returns:
        Family name (last name) or None

    Example:
        >>> if user.is_person:
        ...     print(f"Last name: {user.family_name}")
    """
    if self._user_type == "person":
        return self._data.get("person", {}).get("family_name")
    return None

@property
def given_name(self) -> str | None:
    """Get given name (for person users).

    Returns:
        Given name (first name) or None

    Example:
        >>> if user.is_person:
        ...     print(f"First name: {user.given_name}")
    """
    if self._user_type == "person":
        return self._data.get("person", {}).get("given_name")
    return None
```

#### Bot-Specific Properties

```python
@property
def bot_owner(self) -> dict[str, Any] | None:
    """Get bot owner information (for bot users).

    Returns:
        Bot owner dict with 'type' and user info, or None

    Example:
        >>> if user.is_bot:
        ...     owner = user.bot_owner
        ...     if owner:
        ...         print(f"Owner type: {owner.get('type')}")
    """
    if self._user_type == "bot":
        return self._data.get("bot", {}).get("owner")
    return None
```

### Navigation

```python
async def owned_pages(self) -> AsyncIterator[Page]:
    """Iterate over pages created by this user.

    Yields:
        Page objects created by this user

    Example:
        >>> async for page in user.owned_pages:
        ...     print(f"Created: {page.title}")

    Note:
        Uses search API to find pages
        Requires search permission
    """
    # This would use search API with filter
    # Notion doesn't have direct "pages by user" endpoint
    # Would need to use search with created_by filter
    raise NotImplementedError("Use client.search with filters instead")

async def recent_edits(self) -> AsyncIterator[Page]:
    """Iterate over pages recently edited by this user.

    Yields:
        Page objects recently edited by this user

    Example:
        >>> async for page in user.recent_edits():
        ...     print(f"Edited: {page.title}")

    Note:
        Uses search API with last_edited_time filter
    """
    raise NotImplementedError("Use client.search with filters instead")
```

## CRUD Operations

User objects are read-only in Notion API. No create/update/delete operations.

```python
# Users cannot be created/updated/deleted through SDK
# They are managed by Notion workspace settings
```

## SDK-Exclusive Methods

### Display Helpers

```python
def display_name(self) -> str:
    """Get formatted display name.

    Returns:
        Formatted name with email for persons

    Example:
        >>> user.display_name()
        'John Doe (john@example.com)'
        >>> bot.display_name()
        'My Integration Bot'
    """
    if self._user_type == "person":
        email = self.email or "no email"
        return f"{self.name} ({email})"
    else:
        return self.name

def initials(self) -> str:
    """Get user initials.

    Returns:
        1-2 character initials

    Example:
        >>> user.initials()
        'JD'
    """
    if self._user_type == "person":
        # Use given_name + family_name if available
        first = self.given_name or ""
        last = self.family_name or ""

        if first and last:
            return f"{first[0]}{last[0]}".upper()
        elif self.name:
            # Fallback to name
            parts = self.name.split()
            if len(parts) >= 2:
                return f"{parts[0][0]}{parts[1][0]}".upper()
            else:
                return parts[0][0].upper() if parts else "?"

        return "?"

    # Bot: use first 2 chars of name
    return self.name[:2].upper() if self.name else "??"

def mention(self) -> str:
    """Get Notion @mention format.

    Returns:
        Notion mention string for use in text

    Example:
        >>> text = f"Assigned to {user.mention()}"
    """
    return f"@{self.name}"
```

### Comparison

```python
def __eq__(self, other: object) -> bool:
    """Check equality by ID.

    Args:
        other: Other object to compare

    Returns:
        True if same user (same ID)

    Example:
        >>> user1 == user2
        True
    """
    if not isinstance(other, User):
        return NotImplemented
    return self.id == other.id

def __hash__(self) -> int:
    """Hash user by ID.

    Returns:
        Hash of user ID

    Example:
        >>> users_set = {user1, user2}
    """
    return hash(self.id)
```

### Serialization

```python
def to_dict(self) -> dict[str, Any]:
    """Convert user to dict.

    Returns:
        Dict representation with key fields

    Example:
        >>> data = user.to_dict()
        >>> json.dumps(data)
    """
    return {
        "id": self.id,
        "type": self.type,
        "name": self.name,
        "email": self.email if self.is_person else None,
        "avatar_url": self.avatar_url
    }

@classmethod
def from_dict(cls, api: NotionAPI, data: dict[str, Any]) -> "User":
    """Create user from dict (not from API).

    Args:
        api: NotionAPI client
        data: User dict

    Returns:
        User object

    Note:
        This is for creating User objects from cached data,
        not from fresh API responses
    """
    # Ensure required fields
    if "id" not in data:
        raise ValueError("User dict must have 'id'")
    if "type" not in data:
        raise ValueError("User dict must have 'type'")

    # Convert dict to API-like format
    api_data = {
        "id": data["id"],
        "type": data["type"],
        "name": data.get("name", ""),
        "avatar_url": data.get("avatar_url")
    }

    if data["type"] == "person":
        api_data["person"] = {
            "email": data.get("email")
        }

    return cls(api, api_data)
```

## Cache Integration

### Manager Cache Usage

```python
# User objects are typically cached in UserManager
# This is automatic - users don't manage their own cache

# When using UserManager:
user1 = await client.users.get(user_id)  # Fetches + caches
user2 = await client.users.get(user_id)  # Returns cached

# Direct cache access:
if user_id in client.users.cache:
    user = client.users.cache[user_id]  # No API call
```

## Usage Examples

### Example 1: Display User Information

```python
async def show_user(user_id: str):
    """Display user information."""
    user = await client.users.get(user_id)

    print(f"User: {user.display_name()}")
    print(f"Type: {user.type}")

    if user.is_person:
        print(f"Email: {user.email}")
        if user.family_name:
            print(f"Family: {user.given_name} {user.family_name}")

    if user.avatar_url:
        print(f"Avatar: {user.avatar_url}")
```

### Example 2: Get Page Creators

```python
async def get_page_creators(page_ids: list[str]) -> dict[str, User]:
    """Get all users who created given pages.

    Args:
        page_ids: List of page IDs

    Returns:
        Dict mapping user_id to User object
    """
    # Pre-populate cache
    await client.users.populate_cache()

    creators = {}

    for page_id in page_ids:
        page = await client.pages.get(page_id)
        user_id = page.created_by

        if user_id not in creators:
            user = client.users.cache.get(user_id)
            if user:
                creators[user_id] = user

    return creators
```

### Example 3: User Selection

```python
def select_user(users: list[User]) -> User:
    """Interactive user selection.

    Args:
        users: List of users to choose from

    Returns:
        Selected user
    """
    print("Select a user:")

    for i, user in enumerate(users, 1):
        print(f"{i}. {user.display_name()}")

    while True:
        choice = input("Enter number: ")
        try:
            index = int(choice) - 1
            if 0 <= index < len(users):
                return users[index]
        except ValueError:
            pass

        print("Invalid choice, try again")
```

### Example 4: User Avatar Download

```python
import httpx
from pathlib import Path

async def download_avatar(user: User, output_dir: Path) -> Path | None:
    """Download user avatar to file.

    Args:
        user: User object
        output_dir: Directory to save avatar

    Returns:
        Path to downloaded avatar or None

    Example:
        >>> path = await download_avatar(user, Path("./avatars"))
        >>> print(f"Saved to: {path}")
    """
    if not user.avatar_url:
        return None

    output_dir.mkdir(parents=True, exist_ok=True)
    filename = f"{user.id}.png"
    output_path = output_dir / filename

    async with httpx.AsyncClient() as client:
        response = await client.get(user.avatar_url)
        output_path.write_bytes(response.content)

    return output_path
```

### Example 5: User Statistics

```python
async def get_user_stats(user_id: str) -> dict[str, Any]:
    """Get statistics for a user.

    Args:
        user_id: User ID

    Returns:
        Dict with user statistics

    Note:
        Requires search API access
    """
    user = await client.users.get(user_id)

    stats = {
        "user": user.to_dict(),
        "pages_created": 0,
        "pages_edited": 0,
        "databases_owned": 0
    }

    # Search for pages created by user
    # (requires search API implementation)
    # results = await client.search.query(filter={"value": "page", "property": "object"})

    return stats
```

## Design Decisions

### Q1: Should email be accessible property?

**Decision**: Yes, `email` returns str | None

**Rationale**:
- Email is None for bots (not applicable)
- Some person users may not have visible email (permissions)
- None is clear signal vs empty string

```python
if user.is_person and user.email:
    print(user.email)
```

### Q2: Should User be hashable/equatable?

**Decision**: Yes, by ID

**Rationale**:
- Users can be used in sets/dicts
- Equality by ID (same user, same object)
- Essential for deduplication

```python
# Deduplicate users
unique_users = set(users_list)

# Group by user
from collections import defaultdict
pages_by_user = defaultdict(list)
for page in pages:
    pages_by_user[page.created_by].append(page)
```

### Q3: Navigation methods for owned pages?

**Decision**: No, use search API instead

**Rationale**:
- No direct "pages by user" endpoint in Notion API
- Search API is proper way to filter
- Don't hide the complexity in User model

```python
# Instead of:
async for page in user.owned_pages():
    ...

# Use:
pages = await client.search.query(
    filter={"property": "created_by", "value": user_id}
)
```

### Q4: Support creating users?

**Decision**: No, users are read-only

**Rationale**:
- Notion API doesn't support user creation
- Users are managed by workspace settings
- SDK should reflect API capabilities

## Type Safety

### Type Guards

```python
# Use type guards for narrowed types
if user.is_person:
    # Type checker knows user is person
    email: str | None = user.email
    print(f"Contact: {email}")
```

### Union Types

```python
def get_contact(user: User) -> str:
    """Get contact info for user."""
    if user.is_person:
        return user.email or "No email"
    else:
        return f"Bot: {user.name}"
```

## Error Handling

### Missing Permissions

```python
# Email may be None due to permissions
if user.is_person:
    if user.email:
        print(f"Email: {user.email}")
    else:
        print("Email not visible")
```

### Avatar Not Set

```python
# Graceful handling of missing avatar
if user.avatar_url:
    display_avatar(user.avatar_url)
else:
    display_default_avatar()
```

## Best Practices

### DO ✅

```python
# Pre-populate cache for batch operations
await client.users.populate_cache()

# Check user type before accessing type-specific fields
if user.is_person:
    email = user.email

# Use display_name() for UI display
label = user.display_name()
```

### DON'T ❌

```python
# Don't assume email exists
print(user.email)  # Could be None!

# Don't ignore bot users
if user.is_person:
    process(user)  # Skips bots!
```

## Next Steps

After User model:

1. **Managers** - High-level managers (UserManager, PageManager, DatabaseManager, BlockManager)
2. **NotionClient** - Main client that ties everything together

## Related Documentation

- [BaseEntity](../implementation/base-entity.md) - Foundation class
- [Cache Strategy](../implementation/cache-strategy.md) - User caching
- [User Manager](../managers/user-manager.md) - User management
- [Page Model](./page-model.md) - Pages reference users (created_by, last_edited_by)
