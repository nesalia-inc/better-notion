"""Test to reproduce Database cache bug."""

import pytest
from unittest.mock import AsyncMock, MagicMock
from better_notion._sdk.client import NotionClient
from better_notion._sdk.models.database import Database


def test_database_cache_contains():
    """Test that database cache __contains__ works correctly."""
    client = NotionClient(auth="test_token")

    # Test with string ID
    assert "test-id" not in client.database_cache

    # Create a mock database
    mock_db_data = {
        "id": "test-id",
        "object": "database",
        "properties": {}
    }
    db = Database(client, mock_db_data)

    # Add to cache
    client.database_cache["test-id"] = db

    # Test __contains__ with string
    assert "test-id" in client.database_cache

    # Test that Database object is NOT in cache (should use ID, not object)
    # This is where the bug might be - if code does `db in cache` instead of `db.id in cache`
    result = db in client.database_cache  # This should be False
    assert result is False, "Database object should not be in cache, only IDs"

    print("✅ Cache __contains__ works correctly")
