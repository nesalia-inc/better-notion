"""Shared configuration and fixtures for integration tests."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import pytest
import pytest_asyncio
from dotenv import load_dotenv

from better_notion import NotionAPI
from better_notion._api.properties import Title, Text

# Load environment variables from .env.local
# Find the .env.local file in the project root (tests/integration/ -> project root)
project_root = Path(__file__).parent.parent.parent
env_path = project_root / ".env.local"
load_dotenv(env_path)

# Get Notion API token from environment
NOTION_KEY = os.getenv("NOTION_KEY")
if not NOTION_KEY:
    raise RuntimeError(
        "NOTION_KEY not found in environment. "
        "Create a .env.local file with your Notion API token."
    )

# Test database ID (optional, can be set in .env.local)
TEST_DATABASE_ID = os.getenv("NOTION_TEST_DATABASE_ID")
TEST_PAGE_ID = os.getenv("NOTION_TEST_PAGE_ID")


@pytest_asyncio.fixture
async def api() -> NotionAPI:
    """Create a NotionAPI client for integration tests.

    Each test gets its own client to avoid test pollution.
    """
    client = NotionAPI(auth=NOTION_KEY)
    yield client
    # Close the client after each test
    await client.close()


@pytest.fixture
async def test_database(api: NotionAPI) -> dict[str, Any]:
    """Create a test database for integration testing.

    Creates a temporary database with a title property.
    The database is archived after tests complete.

    Requires NOTION_TEST_PAGE_ID to be set in .env.local.

    Returns:
        Database data dictionary with ID and properties.
    """
    if not TEST_PAGE_ID:
        pytest.skip("NOTION_TEST_PAGE_ID not set in .env.local")

    database_data = await api._request(
        "POST",
        "/databases",
        json={
            "parent": {"type": "page_id", "page_id": TEST_PAGE_ID},
            "title": [
                {"type": "text", "text": {"content": "Better Notion Integration Tests"}}
            ],
            "properties": {
                "Name": {
                    "type": "title",
                    "title": {}
                },
                "Notes": {
                    "type": "rich_text",
                    "rich_text": {}
                }
            }
        }
    )

    database_id = database_data["id"]

    yield database_data

    # Archive the database after tests
    try:
        await api._request(
            "PATCH",
            f"/databases/{database_id}",
            json={"archived": True}
        )
    except Exception:
        # Best effort cleanup
        pass


@pytest.fixture
async def test_page(api: NotionAPI) -> dict[str, Any]:
    """Create a test page for integration testing.

    Creates a temporary page in the test database.
    The page is deleted (archived) after tests complete.

    Requires NOTION_TEST_DATABASE_ID to be set in .env.local.

    Returns:
        Page data dictionary with ID and properties.
    """
    if not TEST_DATABASE_ID:
        pytest.skip("NOTION_TEST_DATABASE_ID not set in .env.local")

    page_data = await api._request(
        "POST",
        "/pages",
        json={
            "parent": {"database_id": TEST_DATABASE_ID},
            "properties": {
                **Title(content="Integration Test Page").build(),
                **Text("Notes", "Created by integration tests").build(),
            }
        }
    )

    yield page_data

    # Archive the page after tests
    try:
        await api._request(
            "PATCH",
            f"/pages/{page_data['id']}",
            json={"archived": True}
        )
    except Exception:
        # Best effort cleanup
        pass


@pytest.fixture
def cleanup_pages(api: NotionAPI):
    """Fixture to cleanup pages created during tests.

    This is a generator that yields a list. Append page IDs to this list
    and they will be archived (deleted) after the test.

    Example:
        async def test_something(cleanup_pages):
            async with cleanup_pages(api) as page_ids:
                page = await api.pages.create(...)
                page_ids.append(page.id)
                # Test the page
    """
    page_ids = []

    yield page_ids

    # Cleanup: archive all created pages
    async def _cleanup():
        for page_id in page_ids:
            try:
                await api._request(
                    "PATCH",
                    f"/pages/{page_id}",
                    json={"archived": True}
                )
            except Exception:
                pass  # Best effort cleanup

    # Run cleanup asynchronously
    import asyncio
    asyncio.create_task(_cleanup())
