"""Test API endpoints."""

from __future__ import annotations

from better_notion._lowlevel.endpoints import (
    BlocksEndpoint,
    CommentsEndpoint,
    DatabasesEndpoint,
    PagesEndpoint,
    SearchEndpoint,
    UsersEndpoint,
)


class TestEndpoints:
    """Test suite for API endpoints."""

    def test_pages_endpoint_initialized(self, mock_api):
        """Test Pages endpoint is initialized correctly."""
        assert isinstance(mock_api.pages, PagesEndpoint)
        assert mock_api.pages._api is mock_api

    def test_blocks_endpoint_initialized(self, mock_api):
        """Test Blocks endpoint is initialized correctly."""
        assert isinstance(mock_api.blocks, BlocksEndpoint)
        assert mock_api.blocks._api is mock_api

    def test_databases_endpoint_initialized(self, mock_api):
        """Test Databases endpoint is initialized correctly."""
        assert isinstance(mock_api.databases, DatabasesEndpoint)
        assert mock_api.databases._api is mock_api

    def test_users_endpoint_initialized(self, mock_api):
        """Test Users endpoint is initialized correctly."""
        assert isinstance(mock_api.users, UsersEndpoint)
        assert mock_api.users._api is mock_api

    def test_search_endpoint_initialized(self, mock_api):
        """Test Search endpoint is initialized correctly."""
        assert isinstance(mock_api.search, SearchEndpoint)
        assert mock_api.search._api is mock_api

    def test_comments_endpoint_initialized(self, mock_api):
        """Test Comments endpoint is initialized correctly."""
        assert isinstance(mock_api.comments, CommentsEndpoint)
        assert mock_api.comments._api is mock_api
