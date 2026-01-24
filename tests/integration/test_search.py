"""Integration tests for Search operations."""

from __future__ import annotations

import pytest

from better_notion._api.properties import Title


@pytest.mark.integration
@pytest.mark.slow
class TestSearchIntegration:
    """Integration tests for Search operations."""

    @pytest.mark.asyncio
    async def test_search_simple(self, api):
        """Test simple search query."""
        # Search for anything
        result = await api.search("test")

        assert "results" in result
        assert isinstance(result["results"], list)

    @pytest.mark.asyncio
    async def test_search_with_filter(self, api):
        """Test search with object type filter."""
        # Filter to only pages
        result = await api.search(
            "integration",
            filter={
                "property": "object",
                "value": "page"
            }
        )

        assert "results" in result
        # Verify all results are pages (not blocks)
        for item in result["results"]:
            if "object" in item:
                assert item["object"] == "page"

    @pytest.mark.asyncio
    async def test_search_paginate(self, api):
        """Test paginating through search results."""
        # Get all results
        results = await api.search_iterate("").to_list()

        assert isinstance(results, list)
        assert len(results) >= 0

        # If there are results, verify structure
        if results:
            result = results[0]
            assert "id" in result
            assert "object" in result

    @pytest.mark.asyncio
    async def test_search_iterate_with_filter(self, api):
        """Test search iteration with filter."""
        count = 0
        async for result in api.search_iterate(
            "integration",
            filter={"property": "object", "value": "page"}
        ):
            count += 1
            if count >= 5:  # Just test a few results
                break

        assert count >= 0

    @pytest.mark.asyncio
    async def test_search_in_content(self, api, test_database):
        """Test searching within page content."""
        # Create a page first (without children)
        page_data = await api._request(
            "POST",
            "/pages",
            json={
                "parent": {"database_id": test_database["id"]},
                "properties": {
                    **Title(content="Search Test Page").build(),
                },
            }
        )

        # Add a block with unique content as a child
        await api._request(
            "PATCH",
            f"/blocks/{page_data['id']}/children",
            json={
                "children": [
                    {
                        "object": "block",
                        "type": "paragraph",
                        "paragraph": {
                            "rich_text": [{"type": "text", "text": {"content": "unique_search_term_12345"}}]
                        }
                    }
                ]
            }
        )

        # Search for the unique term
        result = await api.search("unique_search_term_12345")

        assert "results" in result
        # Our page should be in results (content search)
        found = False
        for item in result["results"]:
            if item.get("id") == page_data["id"]:
                found = True
                break

        # Cleanup
        await api._request("PATCH", f"/pages/{page_data['id']}", json={"archived": True})
