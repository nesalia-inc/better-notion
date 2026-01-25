"""User model with profile information."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, AsyncIterator

from better_notion._sdk.base.entity import BaseEntity

if TYPE_CHECKING:
    from better_notion._sdk.client import NotionClient


class User(BaseEntity):
    """Notion User with profile information.

    This model represents a Notion user (person or bot) with:
    - BaseEntity: Core functionality (id, cache)
    - Profile info: name, email, avatar
    - Type detection: is_person, is_bot
    - Helpers: display_name, initials, mention

    Note:
        Users are read-only in Notion API.
        They cannot be created/updated/deleted through SDK.

    Example:
        >>> user = await client.users.get(user_id)
        >>>
        >>> # Profile info
        >>> print(f"Name: {user.name}")
        >>> print(f"Type: {user.type}")
        >>>
        >>> # Type checking
        >>> if user.is_person:
        ...     print(f"Email: {user.email}")
    """

    def __init__(self, client: "NotionClient", data: dict[str, Any]) -> None:
        """Initialize a User.

        Args:
            client: NotionClient instance
            data: Raw user data from Notion API
        """
        # Initialize BaseEntity
        super().__init__(client, data)

        # Cache user type for frequent access
        self._user_type = self._data.get("type", "")

    # ===== CLASS METHODS (AUTONOMOUS ENTITY) =====

    @classmethod
    async def get(
        cls,
        user_id: str,
        *,
        client: "NotionClient"
    ) -> "User":
        """Get a user by ID.

        Args:
            user_id: User UUID
            client: NotionClient instance

        Returns:
            User object

        Behavior:
            - Checks cache first (instant)
            - If cached, return cached version
            - If not cached, fetch from API
            - Stores in cache for next time

        Example:
            >>> user = await User.get(user_id, client=client)
            >>> print(f"Name: {user.name}")
        """
        # Check global cache first
        if user_id in client.user_cache:
            return client.user_cache[user_id]

        # Fetch from API
        data = await client.api.users.retrieve(user_id=user_id)
        user = cls(client, data)

        # Cache it
        client.user_cache[user_id] = user

        return user

    # ===== METADATA PROPERTIES =====

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

    # ===== TYPE CHECKERS =====

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

    # ===== PERSON-SPECIFIC PROPERTIES =====

    @property
    def email(self) -> str | None:
        """Get email address (for person users).

        Returns:
            Email address or None (for bots or if not visible)

        Example:
            >>> if user.is_person:
            ...     print(f"Email: {user.email}")

        Note:
            Returns None for bot users or if not visible due to permissions
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

    # ===== BOT-SPECIFIC PROPERTIES =====

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

    # ===== NAVIGATION =====

    async def parent(self) -> None:
        """Get parent object.

        Returns:
            None (users don't have parents)

        Note:
            Users are workspace-level objects with no hierarchy
        """
        return None

    async def children(self) -> AsyncIterator[None]:
        """Iterate over children.

        Yields:
            Nothing (users don't have children)

        Note:
            Users are workspace-level objects with no children
        """
        return
        yield  # Make it an async generator

    # ===== DISPLAY HELPERS =====

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

    # ===== SERIALIZATION =====

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
    def from_dict(
        cls,
        client: "NotionClient",
        data: dict[str, Any]
    ) -> "User":
        """Create user from dict (not from API).

        Args:
            client: NotionClient instance
            data: User dict

        Returns:
            User object

        Note:
            This is for creating User objects from cached data,
            not from fresh API responses

        Example:
            >>> user = User.from_dict(client, {"id": "...", "type": "person"})
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

        return cls(client, api_data)

    def __repr__(self) -> str:
        """String representation."""
        return f"User(id={self.id!r}, name={self.name!r}, type={self.type!r})"
