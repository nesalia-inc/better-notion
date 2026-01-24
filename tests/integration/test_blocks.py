"""Integration tests for Block operations."""

from __future__ import annotations

import pytest

from better_notion._api.entities import Block
from better_notion._api.properties import Title


@pytest.mark.integration
@pytest.mark.slow
class TestBlocksIntegration:
    """Integration tests for Block operations."""

    @pytest.mark.asyncio
    async def test_get_block(self, api, test_database):
        """Test retrieving a block by ID."""
        # Create a page first (without children)
        page_data = await api._request(
            "POST",
            "/pages",
            json={
                "parent": {"database_id": test_database["id"]},
                "properties": {
                    **Title(content="Get Block Test").build(),
                },
            }
        )

        # Add a block as a child
        await api._request(
            "POST",
            f"/blocks/{page_data['id']}/children",
            json={
                "children": [
                    {
                        "object": "block",
                        "type": "paragraph",
                        "paragraph": {
                            "text": [{"type": "text", "text": {"content": "Test block"}}]
                        }
                    }
                ]
            }
        )

        page = await api.pages.get(page_data["id"])
        children = await page.blocks.children()

        if children:
            # Get first block
            block = await api.blocks.get(children[0].id)
            assert block.id == children[0].id
            assert isinstance(block, Block)
            assert block.type == "paragraph"

        # Cleanup
        await api._request("PATCH", f"/pages/{page.id}", json={"archived": True})

    @pytest.mark.asyncio
    async def test_block_content_property(self, api, test_database):
        """Test getting and setting block content."""
        # Create a page first (without children)
        page_data = await api._request(
            "POST",
            "/pages",
            json={
                "parent": {"database_id": test_database["id"]},
                "properties": {
                    **Title(content="Block Content Test").build(),
                },
            }
        )

        # Add a block as a child
        await api._request(
            "POST",
            f"/blocks/{page_data['id']}/children",
            json={
                "children": [
                    {
                        "object": "block",
                        "type": "paragraph",
                        "paragraph": {
                            "text": [{"type": "text", "text": {"content": "Original content"}}]
                        }
                    }
                ]
            }
        )

        page = await api.pages.get(page_data["id"])
        children = await page.blocks.children()

        if children:
            block = children[0]
            original_content = block.content

            # Update content
            new_content = {
                "text": [{"type": "text", "text": {"content": "Updated content"}}]
            }
            block.content = new_content
            await block.save()

            # Verify update
            updated_block = await api.blocks.get(block.id)
            assert updated_block.content["text"][0]["text"]["content"] == "Updated content"

        # Cleanup
        await api._request("PATCH", f"/pages/{page.id}", json={"archived": True})

    @pytest.mark.asyncio
    async def test_list_block_children(self, api, test_database):
        """Test listing children blocks."""
        # Create a page first (without children)
        page_data = await api._request(
            "POST",
            "/pages",
            json={
                "parent": {"database_id": test_database["id"]},
                "properties": {
                    **Title(content="List Children Test").build(),
                },
            }
        )

        # Add multiple blocks as children
        children_blocks = [
            {
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "text": [{"type": "text", "text": {"content": f"Paragraph {i}"}}]
                }
            }
            for i in range(3)
        ]

        await api._request(
            "POST",
            f"/blocks/{page_data['id']}/children",
            json={"children": children_blocks}
        )

        page = await api.pages.get(page_data["id"])
        children = await page.blocks.children()

        assert len(children) >= 3

        # Cleanup
        await api._request("PATCH", f"/pages/{page.id}", json={"archived": True})

    @pytest.mark.asyncio
    async def test_append_block(self, api, test_database):
        """Test appending a block to a page."""
        # Create a page first (without children)
        page_data = await api._request(
            "POST",
            "/pages",
            json={
                "parent": {"database_id": test_database["id"]},
                "properties": {
                    **Title(content="Append Block Test").build(),
                },
            }
        )

        # Add initial block as a child
        await api._request(
            "POST",
            f"/blocks/{page_data['id']}/children",
            json={
                "children": [
                    {
                        "object": "block",
                        "type": "paragraph",
                        "paragraph": {
                            "text": [{"type": "text", "text": {"content": "Original"}}]
                        }
                    }
                ]
            }
        )

        page = await api.pages.get(page_data["id"])
        original_children = await page.blocks.children()
        original_count = len(original_children)

        # Append a new block
        await page.blocks.append(children=[
            {
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "text": [{"type": "text", "text": {"content": "Appended block"}}]
                }
            }
        ])

        # Verify block was added
        new_children = await page.blocks.children()
        assert len(new_children) == original_count + 1

        # Cleanup
        await api._request("PATCH", f"/pages/{page.id}", json={"archived": True})

    @pytest.mark.asyncio
    async def test_delete_block(self, api, test_database):
        """Test deleting a block."""
        page_data = await api._request(
            "POST",
            "/pages",
            json={
                "parent": {"database_id": test_database["id"]},
                "properties": {
                    **Title(content="Delete Block Test").build(),
                },
                "children": [
                    {
                        "object": "block",
                        "type": "paragraph",
                        "paragraph": {
                            "text": [{"type": "text", "text": {"content": "Delete me"}}]
                        }
                    }
                ]
            }
        )

        page = await api.pages.get(page_data["id"])
        children = await page.blocks.children()

        if children:
            # Delete the first block
            block = children[0]
            await block.delete()

            # Verify block was deleted
            updated_children = await page.blocks.children()
            assert len(updated_children) == len(children) - 1

        # Cleanup
        await api._request("PATCH", f"/pages/{page.id}", json={"archived": True})

    @pytest.mark.asyncio
    async def test_block_reload(self, api, test_database):
        """Test reloading block data."""
        page_data = await api._request(
            "POST",
            "/pages",
            json={
                "parent": {"database_id": test_database["id"]},
                "properties": {
                    **Title(content="Reload Block Test").build(),
                },
                "children": [
                    {
                        "object": "block",
                        "type": "paragraph",
                        "paragraph": {
                            "text": [{"type": "text", "text": {"content": "Original content"}}]
                        }
                    }
                ]
            }
        )

        page = await api.pages.get(page_data["id"])
        children = await page.blocks.children()

        if children:
            block = children[0]

            # Reload the block
            await block.reload()
            assert block.content is not None

        # Cleanup
        await api._request("PATCH", f"/pages/{page.id}", json={"archived": True})
