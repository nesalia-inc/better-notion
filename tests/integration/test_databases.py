"""Integration tests for Database operations."""

from __future__ import annotations

import pytest

from better_notion._api.entities import Database
from better_notion._api.properties import Title


@pytest.mark.integration
@pytest.mark.slow
class TestDatabasesIntegration:
    """Integration tests for Database operations."""

    @pytest.mark.asyncio
    async def test_get_database(self, api, test_database):
        """Test retrieving a database by ID."""
        database = await api.databases.get(test_database["id"])

        assert database.id == test_database["id"]
        assert isinstance(database, Database)
        assert database.title == test_database["title"]

    @pytest.mark.asyncio
    async def test_database_properties(self, api, test_database):
        """Test accessing database properties."""
        database = await api.databases.get(test_database["id"])

        assert database.id == test_database["id"]
        assert database.properties == test_database["properties"]
        assert database.title == test_database["title"]

    @pytest.mark.asyncio
    async def test_query_database(self, api, test_database):
        """Test querying a database."""
        # Create some test pages first
        page_ids = []
        for i in range(3):
            created = await api._request(
                "POST",
                "/pages",
                json={
                    "parent": {"database_id": test_database["id"]},
                    "properties={
                        **Title(f"Query Test {i}").build(),
                    }
                }
            )
            page_ids.append(created["id"])

        # Query the database
        result = await api.databases.query(test_database["id"])

        assert "results" in result
        assert len(result["results"]) >= 3

        # Cleanup
        for page_id in page_ids:
            await api._request("PATCH", f"/pages/{page_id}", json={"archived": True})

    @pytest.mark.asyncio
    async def test_database_create_page(self, api, test_database):
        """Test creating a page through database collection."""
        page = await api.databases.create_page(
            test_database["id"],
            properties={
                **Title("Created via Database").build(),
            }
        )

        assert page.id is not None
        assert isinstance(page, page.__class__)

        # Cleanup
        await api._request("PATCH", f"/pages/{page.id}", json={"archived": True})
