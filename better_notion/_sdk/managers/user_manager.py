"""User manager for user operations."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from better_notion._sdk.client import NotionClient
    from better_notion._sdk.models.user import User
    from better_notion._sdk.cache import Cache


class UserManager:
    """Ultra-thin wrapper to autonomous User class.

    Focuses on cache population and fast user lookups.

    Example:
        >>> # Via manager (recommended)
        >>> user = await client.users.get(user_id)
        >>>
        >>> # Via entity directly (autonomous)
        >>> user = await User.get(user_id, client=client)
    """

    def __init__(self, client: "NotionClient") -> None:
        """Initialize user manager.

        Args:
            client: NotionClient instance
        """
        self._client = client

    # ===== CRUD OPERATIONS =====

    async def get(self, user_id: str) -> "User":
        """Get user by ID (with cache lookup).

        Args:
            user_id: User UUID

        Returns:
            User object

        Raises:
            UserNotFound: If user doesn't exist

        Behavior:
            1. Check cache first (instant)
            2. If cached, return immediately
            3. If not cached, fetch from API
            4. Store in cache for next time

        Example:
            >>> user = await client.users.get(user_id)
            >>> print(f"{user.name} ({user.email})")
        """
        from better_notion._sdk.models.user import User

        return await User.get(user_id, client=self._client)

    # ===== CACHE MANAGEMENT =====

    async def populate_cache(self) -> None:
        """Load ALL users into cache.

        Fetches all users from API and stores them in cache.
        Subsequent get() calls will be instant memory lookups.

        Use case:
            Call this at startup if you'll be looking up many users.
            Avoids repeated API calls in loops.

        Performance:
            - One-time: N API calls (paginated)
            - Afterwards: Instant lookups

        Example:
            >>> # Pre-load all users
            >>> await client.users.populate_cache()
            >>>
            >>> # Now all lookups are instant
            >>> for page in pages:
            ...     user = client.users.cache.get(page.created_by_id)
            ...     print(f"Created by: {user.name}")  # No API call!
        """
        from better_notion._sdk.models.user import User

        # Clear existing cache
        self._client._user_cache.clear()

        # Fetch all users (handles pagination)
        users = await self._client.api.users.list()
        for user in users:
            self._client._user_cache.set(user.id, user)

    # ===== FINDING =====

    async def find_by_email(
        self,
        email: str
    ) -> "User | None":
        """Find user by email address.

        Args:
            email: User email address

        Returns:
            User object or None if not found

        Note:
            Searches cache first. If not in cache, returns None
            (doesn't fall back to API to avoid listing all users).

        Example:
            >>> user = await client.users.find_by_email("user@example.com")
            >>> if user:
            ...     print(f"Found: {user.name}")
        """
        # Search in cache (linear scan but in-memory)
        for user in self._client._user_cache.get_all():
            if user.email == email:
                return user

        return None

    async def find_by_name(
        self,
        name: str
    ) -> "User | None":
        """Find user by name (case-insensitive).

        Args:
            name: User name to search for

        Returns:
            User object or None if not found

        Note:
            Searches cache first. Requires populate_cache() for full results.

        Example:
            >>> user = await client.users.find_by_name("John Doe")
            >>> if user:
            ...     print(f"Found: {user.email}")
        """
        # Search in cache
        name_lower = name.lower()
        for user in self._client._user_cache.get_all():
            if user.name.lower() == name_lower:
                return user

        return None

    # ===== CACHE ACCESS =====

    @property
    def cache(self) -> "Cache[User]":
        """Access to user cache.

        Returns:
            Cache object for users

        Example:
            >>> # Check if cached
            >>> if user_id in client.users.cache:
            ...     user = client.users.cache[user_id]
            >>>
            >>> # Get without API call
            >>> user = client.users.cache.get(user_id)
        """
        return self._client._user_cache

    # ===== BULK OPERATIONS =====

    async def get_multiple(
        self,
        user_ids: list[str]
    ) -> list["User"]:
        """Get multiple users by IDs.

        Args:
            user_ids: List of user IDs

        Returns:
            List of User objects (in same order)

        Example:
            >>> user_ids = ["id1", "id2", "id3"]
            >>> users = await client.users.get_multiple(user_ids)
        """
        from better_notion._sdk.models.user import User

        users = []
        for user_id in user_ids:
            user = await User.get(user_id, client=self._client)
            users.append(user)

        return users
