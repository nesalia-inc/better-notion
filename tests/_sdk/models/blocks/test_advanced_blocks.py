"""Tests for advanced block types."""

import pytest
from unittest.mock import AsyncMock, MagicMock

from better_notion._sdk.models.blocks.toggle import Toggle
from better_notion._sdk.models.blocks.table import Table
from better_notion._sdk.models.blocks.table_row import TableRow
from better_notion._sdk.models.blocks.column_list import ColumnList
from better_notion._sdk.models.blocks.column import Column
from better_notion._sdk.models.blocks.equation import Equation
from better_notion._sdk.models.blocks.synced_block import SyncedBlock
from better_notion._sdk.models.blocks.bookmark import Bookmark
from better_notion._sdk.models.blocks.embed import Embed


@pytest.fixture
def mock_client():
    """Create mock NotionClient."""
    client = MagicMock()
    client.api = MagicMock()
    client.api.blocks = MagicMock()
    client.api.blocks.children = MagicMock()
    client.api.blocks.children.append = AsyncMock()
    return client


@pytest.fixture
def mock_page():
    """Create mock page."""
    page = MagicMock()
    page.id = "page-123"
    return page


class TestToggle:
    """Tests for Toggle block."""

    def test_toggle_property(self, mock_client):
        """Test toggle block initialization."""
        data = {
            "id": "block-123",
            "object": "block",
            "type": "toggle",
            "toggle": {
                "rich_text": [
                    {
                        "type": "text",
                        "text": {"content": "Click to expand"}
                    }
                ]
            }
        }
        toggle = Toggle(mock_client, data)

        assert toggle.type == "toggle"
        assert toggle.text == "Click to expand"

    @pytest.mark.asyncio
    async def test_toggle_create(self, mock_client, mock_page):
        """Test creating toggle block."""
        mock_client.api.blocks.children.append.return_value = {
            "results": [{
                "id": "toggle-123",
                "type": "toggle",
                "toggle": {
                    "rich_text": [
                        {"type": "text", "text": {"content": "My Toggle"}}
                    ]
                }
            }]
        }

        toggle = await Toggle.create(
            parent=mock_page,
            client=mock_client,
            text="My Toggle"
        )

        assert toggle.text == "My Toggle"


class TestTable:
    """Tests for Table block."""

    def test_table_properties(self, mock_client):
        """Test table block properties."""
        data = {
            "id": "block-123",
            "object": "block",
            "type": "table",
            "table": {
                "table_width": 3,
                "has_column_header": True,
                "has_row_header": False
            }
        }
        table = Table(mock_client, data)

        assert table.type == "table"
        assert table.table_width == 3
        assert table.has_column_header is True
        assert table.has_row_header is False

    @pytest.mark.asyncio
    async def test_table_create(self, mock_client, mock_page):
        """Test creating table block."""
        mock_client.api.blocks.children.append.return_value = {
            "results": [{
                "id": "table-123",
                "type": "table",
                "table": {
                    "table_width": 3,
                    "has_column_header": True,
                    "has_row_header": False
                }
            }]
        }

        table = await Table.create(
            parent=mock_page,
            client=mock_client,
            columns=3,
            has_column_header=True
        )

        assert table.table_width == 3
        assert table.has_column_header is True


class TestTableRow:
    """Tests for TableRow block."""

    def test_table_row_cells(self, mock_client):
        """Test table row cells property."""
        data = {
            "id": "block-123",
            "object": "block",
            "type": "table_row",
            "table_row": {
                "cells": [
                    [{"type": "text", "text": {"content": "Cell 1"}}],
                    [{"type": "text", "text": {"content": "Cell 2"}}],
                    [{"type": "text", "text": {"content": "Cell 3"}}]
                ]
            }
        }
        row = TableRow(mock_client, data)

        assert row.type == "table_row"
        assert row.cells == ["Cell 1", "Cell 2", "Cell 3"]

    @pytest.mark.asyncio
    async def test_table_row_create(self, mock_client, mock_page):
        """Test creating table row block."""
        mock_client.api.blocks.children.append.return_value = {
            "results": [{
                "id": "row-123",
                "type": "table_row",
                "table_row": {
                    "cells": [
                        [{"type": "text", "text": {"content": "A"}}],
                        [{"type": "text", "text": {"content": "B"}}]
                    ]
                }
            }]
        }

        row = await TableRow.create(
            parent=mock_page,
            client=mock_client,
            cells=["A", "B"]
        )

        assert row.cells == ["A", "B"]


class TestEquation:
    """Tests for Equation block."""

    def test_equation_property(self, mock_client):
        """Test equation expression property."""
        data = {
            "id": "block-123",
            "object": "block",
            "type": "equation",
            "equation": {
                "expression": "E = mc^2"
            }
        }
        equation = Equation(mock_client, data)

        assert equation.type == "equation"
        assert equation.expression == "E = mc^2"

    @pytest.mark.asyncio
    async def test_equation_create(self, mock_client, mock_page):
        """Test creating equation block."""
        mock_client.api.blocks.children.append.return_value = {
            "results": [{
                "id": "eq-123",
                "type": "equation",
                "equation": {"expression": "a^2 + b^2 = c^2"}
            }]
        }

        equation = await Equation.create(
            parent=mock_page,
            client=mock_client,
            expression="a^2 + b^2 = c^2"
        )

        assert equation.expression == "a^2 + b^2 = c^2"


class TestBookmark:
    """Tests for Bookmark block."""

    def test_bookmark_properties(self, mock_client):
        """Test bookmark properties."""
        data = {
            "id": "block-123",
            "object": "block",
            "type": "bookmark",
            "bookmark": {
                "url": "https://example.com",
                "caption": [
                    {"type": "text", "text": {"content": "My bookmark"}}
                ]
            }
        }
        bookmark = Bookmark(mock_client, data)

        assert bookmark.type == "bookmark"
        assert bookmark.url == "https://example.com"
        assert bookmark.caption == "My bookmark"

    @pytest.mark.asyncio
    async def test_bookmark_create(self, mock_client, mock_page):
        """Test creating bookmark block."""
        mock_client.api.blocks.children.append.return_value = {
            "results": [{
                "id": "bookmark-123",
                "type": "bookmark",
                "bookmark": {"url": "https://example.com"}
            }]
        }

        bookmark = await Bookmark.create(
            parent=mock_page,
            client=mock_client,
            url="https://example.com"
        )

        assert bookmark.url == "https://example.com"


class TestEmbed:
    """Tests for Embed block."""

    def test_embed_property(self, mock_client):
        """Test embed url property."""
        data = {
            "id": "block-123",
            "object": "block",
            "type": "embed",
            "embed": {
                "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
            }
        }
        embed = Embed(mock_client, data)

        assert embed.type == "embed"
        assert embed.url == "https://www.youtube.com/watch?v=dQw4w9WgXcQ"

    @pytest.mark.asyncio
    async def test_embed_create(self, mock_client, mock_page):
        """Test creating embed block."""
        mock_client.api.blocks.children.append.return_value = {
            "results": [{
                "id": "embed-123",
                "type": "embed",
                "embed": {"url": "https://example.com"}
            }]
        }

        embed = await Embed.create(
            parent=mock_page,
            client=mock_client,
            url="https://example.com"
        )

        assert embed.url == "https://example.com"


class TestColumnList:
    """Tests for ColumnList block."""

    def test_column_list_init(self, mock_client):
        """Test column list initialization."""
        data = {
            "id": "block-123",
            "object": "block",
            "type": "column_list",
            "column_list": {}
        }
        column_list = ColumnList(mock_client, data)

        assert column_list.type == "column_list"

    @pytest.mark.asyncio
    async def test_column_list_create(self, mock_client, mock_page):
        """Test creating column list block."""
        mock_client.api.blocks.children.append.return_value = {
            "results": [{
                "id": "column-list-123",
                "type": "column_list",
                "column_list": {}
            }]
        }

        column_list = await ColumnList.create(
            parent=mock_page,
            client=mock_client
        )

        assert column_list.type == "column_list"


class TestColumn:
    """Tests for Column block."""

    def test_column_init(self, mock_client):
        """Test column initialization."""
        data = {
            "id": "block-123",
            "object": "block",
            "type": "column",
            "column": {}
        }
        column = Column(mock_client, data)

        assert column.type == "column"

    @pytest.mark.asyncio
    async def test_column_create(self, mock_client, mock_page):
        """Test creating column block."""
        mock_client.api.blocks.children.append.return_value = {
            "results": [{
                "id": "column-123",
                "type": "column",
                "column": {}
            }]
        }

        column = await Column.create(
            parent=mock_page,
            client=mock_client
        )

        assert column.type == "column"


class TestSyncedBlock:
    """Tests for SyncedBlock."""

    def test_synced_block_property(self, mock_client):
        """Test synced_from property."""
        data = {
            "id": "block-123",
            "object": "block",
            "type": "synced_block",
            "synced_block": {
                "synced_from": "original-block-123"
            }
        }
        synced = SyncedBlock(mock_client, data)

        assert synced.type == "synced_block"
        assert synced.synced_from == "original-block-123"
