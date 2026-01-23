"""Test API collections."""

from __future__ import annotations

from better_notion._api.collections import (
    BlockCollection,
    DatabaseCollection,
    PageCollection,
    UserCollection,
)


class TestCollections:
    """Test suite for API collections."""

    def test_pages_collection_initialized(self, mock_api):
        """Test Pages collection is initialized correctly."""
        assert isinstance(mock_api.pages, PageCollection)
        assert mock_api.pages._api is mock_api

    def test_blocks_collection_initialized(self, mock_api):
        """Test Blocks collection is initialized correctly."""
        assert isinstance(mock_api.blocks, BlockCollection)
        assert mock_api.blocks._api is mock_api

    def test_databases_collection_initialized(self, mock_api):
        """Test Databases collection is initialized correctly."""
        assert isinstance(mock_api.databases, DatabaseCollection)
        assert mock_api.databases._api is mock_api

    def test_users_collection_initialized(self, mock_api):
        """Test Users collection is initialized correctly."""
        assert isinstance(mock_api.users, UserCollection)
        assert mock_api.users._api is mock_api
