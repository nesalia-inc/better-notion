"""Integration tests for User operations."""

from __future__ import annotations

import pytest


@pytest.mark.integration
@pytest.mark.slow
class TestUsersIntegration:
    """Integration tests for User operations."""

    @pytest.mark.asyncio
    async def test_list_users(self, api):
        """Test listing all users."""
        result = await api.users.list()

        assert isinstance(result, list)
        assert len(result) >= 1  # At least the bot user

    @pytest.mark.asyncio
    async def test_get_user(self, api):
        """Test getting a specific user."""
        # First list users to get a user ID
        users = await api.users.list()
        if users:
            user_id = users[0].id

            # Get the specific user
            user = await api.users.get(user_id)

            assert user.id == user_id
            assert user.name is not None

    @pytest.mark.asyncio
    async def test_me(self, api):
        """Test getting the current bot user."""
        bot_user = await api.users.me()

        assert bot_user is not None
        assert bot_user.id is not None
        assert bot_user.type == "bot"

    @pytest.mark.asyncio
    async def test_user_properties(self, api):
        """Test accessing user properties."""
        bot_user = await api.users.me()

        assert bot_user.id is not None
        assert bot_user.type is not None
        assert hasattr(bot_user, "name") or hasattr(bot_user, "avatar_url")
