"""Tests for Block model and specialized blocks."""

import pytest
from unittest.mock import AsyncMock, MagicMock

from better_notion._sdk.models.block import Block
from better_notion._sdk.models.blocks.code import Code
from better_notion._sdk.models.blocks.todo import Todo
from better_notion._sdk.models.blocks.paragraph import Paragraph
from better_notion._sdk.models.blocks.heading import Heading
from better_notion._sdk.models.blocks.bullet import Bullet
from better_notion._sdk.models.blocks.numbered import Numbered
from better_notion._sdk.models.blocks.quote import Quote
from better_notion._sdk.models.blocks.divider import Divider
from better_notion._sdk.models.blocks.callout import Callout
from better_notion._sdk.cache import Cache


@pytest.fixture
def mock_client():
    """Create mock NotionClient."""
    client = MagicMock()
    client.api = MagicMock()

    # Mock API methods
    client.api.blocks = MagicMock()
    client.api.blocks.retrieve = AsyncMock()
    client.api.blocks.delete = AsyncMock()
    client.api.blocks.children = MagicMock()
    client.api.blocks.children.list = AsyncMock()
    client.api.blocks.children.append = AsyncMock()
    client.api.pages = MagicMock()
    client.api.pages.retrieve = AsyncMock()

    # Setup caches
    client.page_cache = Cache()
    client._page_cache = client.page_cache

    return client


@pytest.fixture
def block_data():
    """Sample block data from Notion API."""
    return {
        "id": "block-123",
        "object": "block",
        "created_time": "2024-01-01T00:00:00.000Z",
        "last_edited_time": "2024-01-01T00:00:00.000Z",
        "created_by": "user-123",
        "last_edited_by": "user-456",
        "has_children": False,
        "archived": False,
        "type": "paragraph",
        "paragraph": {
            "rich_text": [
                {
                    "type": "text",
                    "text": {"content": "Test paragraph"}
                }
            ]
        },
        "parent": {
            "type": "page_id",
            "page_id": "page-123"
        }
    }


class TestBlockInit:
    """Tests for Block initialization."""

    def test_init_with_client_and_data(self, mock_client, block_data):
        """Test initialization with client and data."""
        block = Block(mock_client, block_data)

        assert block.id == "block-123"
        assert block.object == "block"
        assert block._client is mock_client
        assert block._data == block_data

    def test_init_caches_block_type(self, mock_client, block_data):
        """Test initialization caches block type."""
        block = Block(mock_client, block_data)

        assert block._block_type == "paragraph"


class TestBlockMetadata:
    """Tests for Block metadata properties."""

    def test_type_property(self, mock_client, block_data):
        """Test type property."""
        block = Block(mock_client, block_data)

        assert block.type == "paragraph"

    def test_has_children(self, mock_client):
        """Test has_children property."""
        data = {
            "id": "block-123",
            "object": "block",
            "has_children": True,
            "type": "paragraph",
            "paragraph": {"rich_text": []}
        }
        block = Block(mock_client, data)

        assert block.has_children is True

    def test_archived(self, mock_client):
        """Test archived property."""
        data = {
            "id": "block-123",
            "object": "block",
            "archived": True,
            "type": "paragraph",
            "paragraph": {"rich_text": []}
        }
        block = Block(mock_client, data)

        assert block.archived is True

    def test_created_by(self, mock_client, block_data):
        """Test created_by property."""
        block = Block(mock_client, block_data)

        assert block.created_by == "user-123"

    def test_last_edited_by(self, mock_client, block_data):
        """Test last_edited_by property."""
        block = Block(mock_client, block_data)

        assert block.last_edited_by == "user-456"


class TestBlockTypeCheckers:
    """Tests for Block type checkers."""

    def test_is_paragraph(self, mock_client, block_data):
        """Test is_paragraph checker."""
        block = Block(mock_client, block_data)

        assert block.is_paragraph is True
        assert block.is_heading is False
        assert block.is_code is False

    def test_is_heading_1(self, mock_client):
        """Test is_heading_1 checker."""
        data = {
            "id": "block-123",
            "object": "block",
            "type": "heading_1",
            "heading_1": {"rich_text": []}
        }
        block = Block(mock_client, data)

        assert block.is_heading_1 is True
        assert block.is_heading is True

    def test_is_heading_2(self, mock_client):
        """Test is_heading_2 checker."""
        data = {
            "id": "block-123",
            "object": "block",
            "type": "heading_2",
            "heading_2": {"rich_text": []}
        }
        block = Block(mock_client, data)

        assert block.is_heading_2 is True
        assert block.is_heading is True

    def test_is_heading_3(self, mock_client):
        """Test is_heading_3 checker."""
        data = {
            "id": "block-123",
            "object": "block",
            "type": "heading_3",
            "heading_3": {"rich_text": []}
        }
        block = Block(mock_client, data)

        assert block.is_heading_3 is True
        assert block.is_heading is True

    def test_is_code(self, mock_client):
        """Test is_code checker."""
        data = {
            "id": "block-123",
            "object": "block",
            "type": "code",
            "code": {"rich_text": []}
        }
        block = Block(mock_client, data)

        assert block.is_code is True

    def test_is_todo(self, mock_client):
        """Test is_todo checker."""
        data = {
            "id": "block-123",
            "object": "block",
            "type": "to_do",
            "to_do": {"rich_text": []}
        }
        block = Block(mock_client, data)

        assert block.is_todo is True

    def test_is_bullet(self, mock_client):
        """Test is_bullet checker."""
        data = {
            "id": "block-123",
            "object": "block",
            "type": "bulleted_list_item",
            "bulleted_list_item": {"rich_text": []}
        }
        block = Block(mock_client, data)

        assert block.is_bullet is True

    def test_is_numbered(self, mock_client):
        """Test is_numbered checker."""
        data = {
            "id": "block-123",
            "object": "block",
            "type": "numbered_list_item",
            "numbered_list_item": {"rich_text": []}
        }
        block = Block(mock_client, data)

        assert block.is_numbered is True

    def test_is_quote(self, mock_client):
        """Test is_quote checker."""
        data = {
            "id": "block-123",
            "object": "block",
            "type": "quote",
            "quote": {"rich_text": []}
        }
        block = Block(mock_client, data)

        assert block.is_quote is True

    def test_is_divider(self, mock_client):
        """Test is_divider checker."""
        data = {
            "id": "block-123",
            "object": "block",
            "type": "divider",
            "divider": {}
        }
        block = Block(mock_client, data)

        assert block.is_divider is True

    def test_is_callout(self, mock_client):
        """Test is_callout checker."""
        data = {
            "id": "block-123",
            "object": "block",
            "type": "callout",
            "callout": {"rich_text": []}
        }
        block = Block(mock_client, data)

        assert block.is_callout is True


class TestBlockContent:
    """Tests for Block content properties."""

    def test_text_property(self, mock_client, block_data):
        """Test text property."""
        block = Block(mock_client, block_data)

        assert block.text == "Test paragraph"

    def test_text_empty(self, mock_client):
        """Test text with empty rich_text array."""
        data = {
            "id": "block-123",
            "object": "block",
            "type": "paragraph",
            "paragraph": {"rich_text": []}
        }
        block = Block(mock_client, data)

        assert block.text == ""


class TestBlockSpecialization:
    """Tests for Block specialization (from_data factory)."""

    def test_from_data_returns_paragraph(self, mock_client, block_data):
        """Test from_data returns Paragraph for paragraph type."""
        block = Block.from_data(mock_client, block_data)

        assert isinstance(block, Paragraph)

    def test_from_data_returns_code(self, mock_client):
        """Test from_data returns Code for code type."""
        data = {
            "id": "block-123",
            "object": "block",
            "type": "code",
            "code": {"rich_text": [{"type": "text", "text": {"content": "code"}}]}
        }
        block = Block.from_data(mock_client, data)

        assert isinstance(block, Code)

    def test_from_data_returns_todo(self, mock_client):
        """Test from_data returns Todo for to_do type."""
        data = {
            "id": "block-123",
            "object": "block",
            "type": "to_do",
            "to_do": {"rich_text": [], "checked": False}
        }
        block = Block.from_data(mock_client, data)

        assert isinstance(block, Todo)

    def test_from_data_returns_heading(self, mock_client):
        """Test from_data returns Heading for heading types."""
        data = {
            "id": "block-123",
            "object": "block",
            "type": "heading_1",
            "heading_1": {"rich_text": []}
        }
        block = Block.from_data(mock_client, data)

        assert isinstance(block, Heading)

    def test_from_data_returns_bullet(self, mock_client):
        """Test from_data returns Bullet for bulleted_list_item."""
        data = {
            "id": "block-123",
            "object": "block",
            "type": "bulleted_list_item",
            "bulleted_list_item": {"rich_text": []}
        }
        block = Block.from_data(mock_client, data)

        assert isinstance(block, Bullet)

    def test_from_data_returns_numbered(self, mock_client):
        """Test from_data returns Numbered for numbered_list_item."""
        data = {
            "id": "block-123",
            "object": "block",
            "type": "numbered_list_item",
            "numbered_list_item": {"rich_text": []}
        }
        block = Block.from_data(mock_client, data)

        assert isinstance(block, Numbered)

    def test_from_data_returns_quote(self, mock_client):
        """Test from_data returns Quote for quote type."""
        data = {
            "id": "block-123",
            "object": "block",
            "type": "quote",
            "quote": {"rich_text": []}
        }
        block = Block.from_data(mock_client, data)

        assert isinstance(block, Quote)

    def test_from_data_returns_divider(self, mock_client):
        """Test from_data returns Divider for divider type."""
        data = {
            "id": "block-123",
            "object": "block",
            "type": "divider",
            "divider": {}
        }
        block = Block.from_data(mock_client, data)

        assert isinstance(block, Divider)

    def test_from_data_returns_callout(self, mock_client):
        """Test from_data returns Callout for callout type."""
        data = {
            "id": "block-123",
            "object": "block",
            "type": "callout",
            "callout": {"rich_text": []}
        }
        block = Block.from_data(mock_client, data)

        assert isinstance(block, Callout)

    def test_from_data_returns_base_block_for_unknown(self, mock_client):
        """Test from_data returns base Block for unknown type."""
        data = {
            "id": "block-123",
            "object": "block",
            "type": "unknown_type",
            "unknown_type": {}
        }
        block = Block.from_data(mock_client, data)

        assert isinstance(block, Block)
        assert type(block) == Block  # Exactly Block, not a subclass


class TestBlockNavigation:
    """Tests for Block navigation methods."""

    @pytest.mark.asyncio
    async def test_parent_page(self, mock_client, block_data):
        """Test getting parent page."""
        # Mock page fetch
        page_data = {
            "id": "page-123",
            "object": "page",
            "properties": {
                "Name": {
                    "id": "prop-name",
                    "type": "title",
                    "title": [
                        {
                            "type": "text",
                            "text": {"content": "Parent Page"}
                        }
                    ]
                }
            }
        }
        mock_client.api.pages.retrieve.return_value = page_data

        block = Block(mock_client, block_data)
        parent = await block.parent()

        assert parent.id == "page-123"
        assert parent.title == "Parent Page"

    @pytest.mark.asyncio
    async def test_parent_uses_cache(self, mock_client, block_data):
        """Test parent() caches result."""
        page_data = {
            "id": "page-123",
            "object": "page",
            "properties": {
                "Name": {
                    "id": "prop-name",
                    "type": "title",
                    "title": [
                        {
                            "type": "text",
                            "text": {"content": "Parent Page"}
                        }
                    ]
                }
            }
        }
        mock_client.api.pages.retrieve.return_value = page_data

        block = Block(mock_client, block_data)

        # First call - fetches from API
        parent1 = await block.parent()

        # Second call - uses cache
        parent2 = await block.parent()

        assert parent1 is parent2
        # API should only be called once
        mock_client.api.pages.retrieve.assert_called_once()

    @pytest.mark.asyncio
    async def test_children_empty(self, mock_client):
        """Test children() with no children."""
        mock_client.api.blocks.children.list.return_value = {
            "results": [],
            "has_more": False,
            "next_cursor": None
        }

        data = {
            "id": "block-123",
            "object": "block",
            "type": "paragraph",
            "paragraph": {"rich_text": []}
        }
        block = Block(mock_client, data)

        children = []
        async for child in block.children():
            children.append(child)

        assert len(children) == 0


class TestBlockCRUD:
    """Tests for Block CRUD operations."""

    @pytest.mark.asyncio
    async def test_delete(self, mock_client):
        """Test delete method."""
        mock_client.api.blocks.delete.return_value = {}

        data = {
            "id": "block-123",
            "object": "block",
            "type": "paragraph",
            "paragraph": {"rich_text": []}
        }
        block = Block(mock_client, data)

        await block.delete()

        mock_client.api.blocks.delete.assert_called_once_with(block_id="block-123")


class TestBlockRepr:
    """Tests for Block string representation."""

    def test_repr(self, mock_client, block_data):
        """Test __repr__ method."""
        block = Block(mock_client, block_data)

        repr_str = repr(block)

        assert "Block" in repr_str
        assert "block-123" in repr_str
        assert "paragraph" in repr_str


class TestCodeBlock:
    """Tests for Code specialized block."""

    def test_code_property(self, mock_client):
        """Test code property."""
        data = {
            "id": "block-123",
            "object": "block",
            "type": "code",
            "code": {
                "rich_text": [
                    {
                        "type": "text",
                        "text": {"content": "print('hello')"}
                    }
                ],
                "language": "python"
            }
        }
        code = Code(mock_client, data)

        assert code.code == "print('hello')"

    def test_language_property(self, mock_client):
        """Test language property."""
        data = {
            "id": "block-123",
            "object": "block",
            "type": "code",
            "code": {
                "rich_text": [],
                "language": "javascript"
            }
        }
        code = Code(mock_client, data)

        assert code.language == "javascript"


class TestTodoBlock:
    """Tests for Todo specialized block."""

    def test_checked_property(self, mock_client):
        """Test checked property."""
        data = {
            "id": "block-123",
            "object": "block",
            "type": "to_do",
            "to_do": {
                "rich_text": [],
                "checked": True
            }
        }
        todo = Todo(mock_client, data)

        assert todo.checked is True


class TestHeadingBlock:
    """Tests for Heading specialized block."""

    def test_level_property_heading_1(self, mock_client):
        """Test level property for heading_1."""
        data = {
            "id": "block-123",
            "object": "block",
            "type": "heading_1",
            "heading_1": {"rich_text": []}
        }
        heading = Heading(mock_client, data)

        assert heading.level == 1

    def test_level_property_heading_2(self, mock_client):
        """Test level property for heading_2."""
        data = {
            "id": "block-123",
            "object": "block",
            "type": "heading_2",
            "heading_2": {"rich_text": []}
        }
        heading = Heading(mock_client, data)

        assert heading.level == 2

    def test_level_property_heading_3(self, mock_client):
        """Test level property for heading_3."""
        data = {
            "id": "block-123",
            "object": "block",
            "type": "heading_3",
            "heading_3": {"rich_text": []}
        }
        heading = Heading(mock_client, data)

        assert heading.level == 3


class TestCalloutBlock:
    """Tests for Callout specialized block."""

    def test_icon_property(self, mock_client):
        """Test icon property."""
        data = {
            "id": "block-123",
            "object": "block",
            "type": "callout",
            "callout": {
                "rich_text": [],
                "icon": {
                    "type": "emoji",
                    "emoji": "💡"
                }
            }
        }
        callout = Callout(mock_client, data)

        assert callout.icon == "💡"

    def test_icon_none(self, mock_client):
        """Test icon property when no icon."""
        data = {
            "id": "block-123",
            "object": "block",
            "type": "callout",
            "callout": {
                "rich_text": []
            }
        }
        callout = Callout(mock_client, data)

        assert callout.icon is None
