"""Test the NotionAPI client."""

from __future__ import annotations

import pytest

from better_notion._api import NotionAPI


class TestNotionAPI:
    """Test suite for NotionAPI client."""

    def test_init_with_valid_token(self):
        """Test initialization with valid token."""
        api = NotionAPI(auth="secret_test_token")
        assert api._token == "secret_test_token"
        assert api._base_url == "https://api.notion.com/v1"

    def test_init_with_invalid_token(self):
        """Test initialization fails with invalid token."""
        with pytest.raises(ValueError, match='must start with "secret_"'):
            NotionAPI(auth="invalid_token")

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

    def test_endpoints_initialized(self):
        """Test all endpoints are initialized."""
        api = NotionAPI(auth="secret_test")

        assert api.blocks is not None
        assert api.pages is not None
        assert api.databases is not None
        assert api.users is not None
        assert api.search is not None
        assert api.comments is not None
