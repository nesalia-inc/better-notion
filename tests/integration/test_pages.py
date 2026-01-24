"""Integration tests for Page operations."""

from __future__ import annotations

import pytest

from better_notion._api.entities import Page
from better_notion._api.properties import Select, Text, Title


@pytest.mark.integration
@pytest.mark.slow
class TestPagesIntegration:
    """Integration tests for Page CRUD operations."""

    @pytest.mark.asyncio
    async def test_create_page(self, api, test_database):
        """Test creating a new page in a database."""
        page = await api.pages.create(
            parent={"database_id": test_database["id"]},
            properties={
                **Title(content="Integration Test Page").build(),
            }
        )

        assert page.id is not None
        assert isinstance(page, Page)
        assert page.archived is False

        # Cleanup
        await api._request(
            "PATCH",
            f"/pages/{page.id}",
            json={"archived": True}
        )

    @pytest.mark.asyncio
    async def test_get_page(self, api, test_database):
        """Test retrieving a page by ID."""
        # First create a page
        created = await api._request(
            "POST",
            "/pages",
            json={
                "parent": {"database_id": test_database["id"]},
                "properties": {
                    **Title(content="Get Test Page").build(),
                }
            }
        )
        page_id = created["id"]

        # Now retrieve it
        page = await api.pages.get(page_id)

        assert page.id == page_id
        assert isinstance(page, Page)

        # Cleanup
        await api._request("PATCH", f"/pages/{page_id}", json={"archived": True})

    @pytest.mark.asyncio
    async def test_update_page(self, api, test_database):
        """Test updating page properties."""
        # Create a page
        created = await api._request(
            "POST",
            "/pages",
            json={
                "parent": {"database_id": test_database["id"]},
                "properties": {
                    **Title(content="Update Test Page - Original").build(),
                }
            }
        )
        page_id = created["id"]

        # Retrieve and update
        page = await api.pages.get(page_id)
        await page.update(**Title(content="Update Test Page - Modified").build())
        await page.save()

        # Verify the update
        updated = await api.pages.get(page_id)
        assert updated._data["properties"]["Name"]["title"][0]["plain_text"] == "Update Test Page - Modified"

        # Cleanup
        await api._request("PATCH", f"/pages/{page_id}", json={"archived": True})

    @pytest.mark.asyncio
    async def test_delete_page(self, api, test_database):
        """Test deleting (archiving) a page."""
        # Create a page
        created = await api._request(
            "POST",
            "/pages",
            json={
                "parent": {"database_id": test_database["id"]},
                "properties": {
                    **Title(content="Delete Test Page").build(),
                }
            }
        )
        page_id = created["id"]

        # Delete the page
        page = await api.pages.get(page_id)
        await page.delete()

        # Verify it's archived
        updated = await api.pages.get(page_id)
        assert updated.archived is True

    @pytest.mark.asyncio
    async def test_list_pages(self, api, test_database):
        """Test listing pages in a database."""
        # Create a few test pages
        page_ids = []
        for i in range(3):
            created = await api._request(
                "POST",
                "/pages",
                json={
                    "parent": {"database_id": test_database["id"]},
                    "properties": {
                        **Title(content=f"List Test Page {i}").build(),
                    }
                }
            )
            page_ids.append(created["id"])

        # List pages
        pages = await api.pages.list(test_database["id"])
        assert len(pages) >= 3

        # Cleanup
        for page_id in page_ids:
            await api._request("PATCH", f"/pages/{page_id}", json={"archived": True})

    @pytest.mark.asyncio
    async def test_paginate_pages(self, api, test_database):
        """Test paginating through pages with iterate()."""
        # Create multiple pages
        page_ids = []
        for i in range(5):
            created = await api._request(
                "POST",
                "/pages",
                json={
                    "parent": {"database_id": test_database["id"]},
                    "properties": {
                        **Title(content=f"Paginate Test {i}").build(),
                    }
                }
            )
            page_ids.append(created["id"])

        # Iterate through pages
        count = 0
        async for page in api.pages.iterate(test_database["id"]):
            count += 1
            if count >= 5:
                break

        assert count >= 5

        # Cleanup
        for page_id in page_ids:
            await api._request("PATCH", f"/pages/{page_id}", json={"archived": True})

    @pytest.mark.asyncio
    async def test_page_properties(self, api, test_database):
        """Test accessing page properties."""
        created = await api._request(
            "POST",
            "/pages",
            json={
                "parent": {"database_id": test_database["id"]},
                "properties": {
                    **Title(content="Properties Test").build(),
                }
            }
        )
        page = await api.pages.get(created["id"])

        # Test properties
        assert page.id == created["id"]
        assert page.properties == created["properties"]
        assert page.archived is False
        assert page.created_time is not None
        assert page.last_edited_time is not None

        # Cleanup
        await api._request("PATCH", f"/pages/{page.id}", json={"archived": True})

    @pytest.mark.asyncio
    async def test_page_blocks_navigation(self, api, test_database):
        """Test page.blocks property for block navigation."""
        # Create a page with content
        created = await api._request(
            "POST",
            "/pages",
            json={
                "parent": {"database_id": test_database["id"]},
                "properties": {
                    **Title(content="Blocks Navigation Test").build(),
                },
                "children": [
                    {
                        "object": "block",
                        "type": "paragraph",
                        "paragraph": {
                            "text": [{"type": "text", "text": {"content": "Test paragraph"}}]
                        }
                    }
                ]
            }
        )
        page = await api.pages.get(created["id"])

        # Get children blocks
        children = await page.blocks.children()
        assert len(children) > 0
        assert children[0].type == "paragraph"

        # Cleanup
        await api._request("PATCH", f"/pages/{page.id}", json={"archived": True})
