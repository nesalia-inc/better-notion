"""Tests for User model."""

import pytest
from unittest.mock import AsyncMock, MagicMock

from better_notion._sdk.models.user import User
from better_notion._sdk.cache import Cache


@pytest.fixture
def mock_client():
    """Create mock NotionClient."""
    client = MagicMock()
    client.api = MagicMock()

    # Mock API methods
    client.api.users = MagicMock()
    client.api.users.retrieve = AsyncMock()

    # Setup caches
    client.user_cache = Cache()
    client._user_cache = client.user_cache

    return client


@pytest.fixture
def person_data():
    """Sample person user data from Notion API."""
    return {
        "id": "user-123",
        "object": "user",
        "type": "person",
        "name": "John Doe",
        "avatar_url": "https://example.com/avatar.png",
        "person": {
            "email": "john@example.com",
            "given_name": "John",
            "family_name": "Doe"
        }
    }


@pytest.fixture
def bot_data():
    """Sample bot user data from Notion API."""
    return {
        "id": "bot-123",
        "object": "user",
        "type": "bot",
        "name": "My Integration Bot",
        "avatar_url": None,
        "bot": {
            "owner": {
                "type": "workspace",
                "workspace": True
            }
        }
    }


class TestUserInit:
    """Tests for User initialization."""

    def test_init_with_client_and_data(self, mock_client, person_data):
        """Test initialization with client and data."""
        user = User(mock_client, person_data)

        assert user.id == "user-123"
        assert user._client is mock_client
        assert user._data == person_data

    def test_init_caches_user_type(self, mock_client, person_data):
        """Test initialization caches user type."""
        user = User(mock_client, person_data)

        assert user._user_type == "person"


class TestUserMetadata:
    """Tests for User metadata properties."""

    def test_type_person(self, mock_client, person_data):
        """Test type property for person."""
        user = User(mock_client, person_data)

        assert user.type == "person"

    def test_type_bot(self, mock_client, bot_data):
        """Test type property for bot."""
        user = User(mock_client, bot_data)

        assert user.type == "bot"

    def test_name_person(self, mock_client, person_data):
        """Test name property for person."""
        user = User(mock_client, person_data)

        assert user.name == "John Doe"

    def test_name_bot(self, mock_client, bot_data):
        """Test name property for bot."""
        user = User(mock_client, bot_data)

        assert user.name == "My Integration Bot"

    def test_name_empty(self, mock_client):
        """Test name with empty name."""
        data = {
            "id": "user-123",
            "object": "user",
            "type": "person",
            "name": ""
        }
        user = User(mock_client, data)

        assert user.name == ""

    def test_avatar_url(self, mock_client, person_data):
        """Test avatar_url property."""
        user = User(mock_client, person_data)

        assert user.avatar_url == "https://example.com/avatar.png"

    def test_avatar_url_none(self, mock_client, bot_data):
        """Test avatar_url when None."""
        user = User(mock_client, bot_data)

        assert user.avatar_url is None


class TestUserTypeCheckers:
    """Tests for User type checkers."""

    def test_is_person_true(self, mock_client, person_data):
        """Test is_person for person user."""
        user = User(mock_client, person_data)

        assert user.is_person is True
        assert user.is_bot is False

    def test_is_bot_true(self, mock_client, bot_data):
        """Test is_bot for bot user."""
        user = User(mock_client, bot_data)

        assert user.is_bot is True
        assert user.is_person is False


class TestPersonSpecificProperties:
    """Tests for person-specific properties."""

    def test_email(self, mock_client, person_data):
        """Test email property."""
        user = User(mock_client, person_data)

        assert user.email == "john@example.com"

    def test_email_for_bot(self, mock_client, bot_data):
        """Test email for bot returns None."""
        user = User(mock_client, bot_data)

        assert user.email is None

    def test_family_name(self, mock_client, person_data):
        """Test family_name property."""
        user = User(mock_client, person_data)

        assert user.family_name == "Doe"

    def test_family_name_for_bot(self, mock_client, bot_data):
        """Test family_name for bot returns None."""
        user = User(mock_client, bot_data)

        assert user.family_name is None

    def test_given_name(self, mock_client, person_data):
        """Test given_name property."""
        user = User(mock_client, person_data)

        assert user.given_name == "John"

    def test_given_name_for_bot(self, mock_client, bot_data):
        """Test given_name for bot returns None."""
        user = User(mock_client, bot_data)

        assert user.given_name is None


class TestBotSpecificProperties:
    """Tests for bot-specific properties."""

    def test_bot_owner(self, mock_client, bot_data):
        """Test bot_owner property."""
        user = User(mock_client, bot_data)

        owner = user.bot_owner
        assert owner is not None
        assert owner["type"] == "workspace"

    def test_bot_owner_for_person(self, mock_client, person_data):
        """Test bot_owner for person returns None."""
        user = User(mock_client, person_data)

        assert user.bot_owner is None


class TestUserClassMethods:
    """Tests for User class methods (autonomous entity)."""

    @pytest.mark.asyncio
    async def test_get_from_api(self, mock_client, person_data):
        """Test User.get() fetches from API."""
        mock_client.api.users.retrieve.return_value = person_data

        user = await User.get(user_id="user-123", client=mock_client)

        assert user.id == "user-123"
        assert user.name == "John Doe"
        mock_client.api.users.retrieve.assert_called_once_with(user_id="user-123")

    @pytest.mark.asyncio
    async def test_get_uses_cache(self, mock_client, person_data):
        """Test User.get() uses cache."""
        # Pre-populate cache
        cached_user = User(mock_client, person_data)
        mock_client.user_cache["user-123"] = cached_user

        user = await User.get(user_id="user-123", client=mock_client)

        assert user is cached_user
        # API should not be called
        mock_client.api.users.retrieve.assert_not_called()


class TestUserNavigation:
    """Tests for User navigation methods."""

    @pytest.mark.asyncio
    async def test_parent(self, mock_client, person_data):
        """Test parent() returns None."""
        user = User(mock_client, person_data)

        parent = await user.parent()

        assert parent is None

    @pytest.mark.asyncio
    async def test_children(self, mock_client, person_data):
        """Test children() yields nothing."""
        user = User(mock_client, person_data)

        children = []
        async for child in user.children():
            children.append(child)

        assert len(children) == 0


class TestUserDisplayHelpers:
    """Tests for User display helper methods."""

    def test_display_name_person(self, mock_client, person_data):
        """Test display_name for person."""
        user = User(mock_client, person_data)

        assert user.display_name() == "John Doe (john@example.com)"

    def test_display_name_person_no_email(self, mock_client):
        """Test display_name for person without email."""
        data = {
            "id": "user-123",
            "object": "user",
            "type": "person",
            "name": "John Doe",
            "person": {}
        }
        user = User(mock_client, data)

        assert user.display_name() == "John Doe (no email)"

    def test_display_name_bot(self, mock_client, bot_data):
        """Test display_name for bot."""
        user = User(mock_client, bot_data)

        assert user.display_name() == "My Integration Bot"

    def test_initials_person(self, mock_client, person_data):
        """Test initials for person with names."""
        user = User(mock_client, person_data)

        assert user.initials() == "JD"

    def test_initials_person_no_names(self, mock_client):
        """Test initials for person without given/family name."""
        data = {
            "id": "user-123",
            "object": "user",
            "type": "person",
            "name": "John Doe",
            "person": {}
        }
        user = User(mock_client, data)

        assert user.initials() == "JD"  # Falls back to name

    def test_initials_bot(self, mock_client, bot_data):
        """Test initials for bot."""
        user = User(mock_client, bot_data)

        assert user.initials() == "MY"

    def test_initials_no_name(self, mock_client):
        """Test initials for user without name."""
        data = {
            "id": "user-123",
            "object": "user",
            "type": "bot",
            "name": ""
        }
        user = User(mock_client, data)

        assert user.initials() == "??"  # Bot returns 2 chars

    def test_mention(self, mock_client, person_data):
        """Test mention method."""
        user = User(mock_client, person_data)

        assert user.mention() == "@John Doe"


class TestUserSerialization:
    """Tests for User serialization methods."""

    def test_to_dict_person(self, mock_client, person_data):
        """Test to_dict for person."""
        user = User(mock_client, person_data)

        data = user.to_dict()

        assert data["id"] == "user-123"
        assert data["type"] == "person"
        assert data["name"] == "John Doe"
        assert data["email"] == "john@example.com"
        assert data["avatar_url"] == "https://example.com/avatar.png"

    def test_to_dict_bot(self, mock_client, bot_data):
        """Test to_dict for bot."""
        user = User(mock_client, bot_data)

        data = user.to_dict()

        assert data["id"] == "bot-123"
        assert data["type"] == "bot"
        assert data["name"] == "My Integration Bot"
        assert data["email"] is None
        assert data["avatar_url"] is None

    def test_from_dict_person(self, mock_client):
        """Test from_dict for person."""
        data = {
            "id": "user-123",
            "type": "person",
            "name": "John Doe",
            "email": "john@example.com",
            "avatar_url": "https://example.com/avatar.png"
        }

        user = User.from_dict(mock_client, data)

        assert user.id == "user-123"
        assert user.type == "person"
        assert user.name == "John Doe"
        assert user.email == "john@example.com"
        assert user.avatar_url == "https://example.com/avatar.png"

    def test_from_dict_bot(self, mock_client):
        """Test from_dict for bot."""
        data = {
            "id": "bot-123",
            "type": "bot",
            "name": "My Bot"
        }

        user = User.from_dict(mock_client, data)

        assert user.id == "bot-123"
        assert user.type == "bot"
        assert user.name == "My Bot"

    def test_from_dict_missing_id(self, mock_client):
        """Test from_dict with missing id."""
        data = {
            "type": "person",
            "name": "John"
        }

        with pytest.raises(ValueError, match="must have 'id'"):
            User.from_dict(mock_client, data)

    def test_from_dict_missing_type(self, mock_client):
        """Test from_dict with missing type."""
        data = {
            "id": "user-123",
            "name": "John"
        }

        with pytest.raises(ValueError, match="must have 'type'"):
            User.from_dict(mock_client, data)


class TestUserRepr:
    """Tests for User string representation."""

    def test_repr_person(self, mock_client, person_data):
        """Test __repr__ for person."""
        user = User(mock_client, person_data)

        repr_str = repr(user)

        assert "User" in repr_str
        assert "user-123" in repr_str
        assert "John Doe" in repr_str
        assert "person" in repr_str

    def test_repr_bot(self, mock_client, bot_data):
        """Test __repr__ for bot."""
        user = User(mock_client, bot_data)

        repr_str = repr(user)

        assert "User" in repr_str
        assert "bot-123" in repr_str
        assert "My Integration Bot" in repr_str
        assert "bot" in repr_str
