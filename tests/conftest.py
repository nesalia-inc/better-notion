"""Shared pytest configuration and fixtures."""

from __future__ import annotations

from unittest.mock import AsyncMock

import pytest

from better_notion._api import NotionAPI


@pytest.fixture
async def mock_api():
    """Create a mock NotionAPI client for testing.

    Yields:
        Mocked NotionAPI instance.
    """
    api = NotionAPI(auth="secret_test_token")

    # Mock the HTTP client
    api._http = AsyncMock()

    yield api

    # Cleanup
    await api.close()


@pytest.fixture
def sample_page_data():
    """Sample page data for testing.

    Returns:
        Dictionary with sample page data.
    """
    return {
        "id": "5c6a28216bb14a7eb6e1c50111515c3d",
        "object": "page",
        "created_time": "2025-01-15T00:00:00.000Z",
        "last_edited_time": "2025-01-15T00:00:00.000Z",
        "archived": False,
        "properties": {
            "Name": {
                "type": "title",
                "title": [
                    {
                        "type": "text",
                        "text": {"content": "Test Page"}
                    }
                ]
            }
        }
    }


@pytest.fixture
def sample_database_data():
    """Sample database data for testing.

    Returns:
        Dictionary with sample database data.
    """
    return {
        "id": "5c6a28216bb14a7eb6e1c50111515c3d",
        "object": "database",
        "created_time": "2025-01-15T00:00:00.000Z",
        "last_edited_time": "2025-01-15T00:00:00.000Z",
        "title": [
            {
                "type": "text",
                "text": {"content": "Test Database"}
            }
        ],
        "properties": {
            "Name": {
                "type": "title",
                "title": {}}
        }
    }
