"""Test the NotionAPI client."""

from __future__ import annotations

from better_notion._api import NotionAPI
from better_notion._api.collections import (
    BlockCollection,
    DatabaseCollection,
    PageCollection,
    UserCollection,
)


class TestNotionAPI:
    """Test suite for NotionAPI client."""

    def test_init_with_valid_token(self):
        """Test initialization with valid token."""
        api = NotionAPI(auth="secret_test_token")
        assert api._token == "secret_test_token"
        assert api._base_url == "https://api.notion.com/v1"

    def test_init_with_invalid_token(self):
        """Test initialization fails with invalid token."""
        try:
            NotionAPI(auth="invalid_token")
        except ValueError as e:
            assert 'must start with "secret_"' in str(e)

    def test_default_headers(self):
        """Test default headers are set correctly."""
        api = NotionAPI(auth="secret_test")
        headers = api._default_headers()

        assert headers["Authorization"] == "Bearer secret_test"
        assert headers["Notion-Version"] == "2022-06-28"
        assert headers["Content-Type"] == "application/json"

    def test_custom_base_url(self):
        """Test custom base URL."""
        api = NotionAPI(
            auth="secret_test",
            base_url="https://custom.example.com"
        )
        assert api._base_url == "https://custom.example.com"

    def test_custom_timeout(self):
        """Test custom timeout."""
        api = NotionAPI(auth="secret_test", timeout=60.0)
        assert api._timeout == 60.0

    def test_collections_initialized(self):
        """Test all collections are initialized."""
        api = NotionAPI(auth="secret_test")

        assert isinstance(api.pages, PageCollection)
        assert isinstance(api.blocks, BlockCollection)
        assert isinstance(api.databases, DatabaseCollection)
        assert isinstance(api.users, UserCollection)
