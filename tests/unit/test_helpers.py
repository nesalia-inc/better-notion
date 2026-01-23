"""Test helper functions."""

from __future__ import annotations

import pytest

from better_notion.utils.helpers import extract_content, extract_title, parse_datetime


class TestParseDatetime:
    """Test suite for parse_datetime function."""

    def test_parse_iso_datetime_with_z(self):
        """Test parsing ISO datetime with Z suffix."""
        dt = parse_datetime("2025-01-15T00:00:00.000Z")
        assert dt.year == 2025
        assert dt.month == 1
        assert dt.day == 15

    def test_parse_iso_datetime_with_timezone(self):
        """Test parsing ISO datetime with timezone offset."""
        dt = parse_datetime("2025-01-15T00:00:00.000+00:00")
        assert dt.year == 2025
        assert dt.month == 1
        assert dt.day == 15

    def test_parse_iso_datetime_without_fractional_seconds(self):
        """Test parsing ISO datetime without fractional seconds."""
        dt = parse_datetime("2025-01-15T00:00:00Z")
        assert dt.year == 2025
        assert dt.month == 1
        assert dt.day == 15

    def test_parse_empty_string_raises_error(self):
        """Test parsing empty string raises ValueError."""
        with pytest.raises(ValueError, match="cannot be empty"):
            parse_datetime("")

    def test_parse_invalid_format_raises_error(self):
        """Test parsing invalid format raises ValueError."""
        with pytest.raises(ValueError, match="Invalid datetime format"):
            parse_datetime("invalid")


class TestExtractTitle:
    """Test suite for extract_title function."""

    def test_extract_title_from_sample_data(self, sample_page_data):
        """Test extracting title from sample page data."""
        title = extract_title(sample_page_data["properties"])
        assert title == "Test Page"

    def test_extract_title_returns_none_for_empty_properties(self):
        """Test extracting title from empty properties."""
        assert extract_title({}) is None

    def test_extract_title_returns_none_for_none_input(self):
        """Test extracting title from None input."""
        assert extract_title(None) is None

    def test_extract_title_handles_multiple_properties(self):
        """Test extracting title when there are multiple properties."""
        properties = {
            "Name": {
                "type": "title",
                "title": [{"type": "text", "text": {"content": "My Title"}}]
            },
            "Tags": {
                "type": "multi_select",
                "multi_select": []
            }
        }
        assert extract_title(properties) == "My Title"

    def test_extract_title_handles_empty_title_array(self):
        """Test extracting title when title array is empty."""
        properties = {
            "Name": {
                "type": "title",
                "title": []
            }
        }
        assert extract_title(properties) is None

    def test_extract_title_handles_missing_content(self):
        """Test extracting title when content is missing."""
        properties = {
            "Name": {
                "type": "title",
                "title": [{"type": "text"}]
            }
        }
        assert extract_title(properties) is None

    def test_extract_title_handles_no_title_property(self):
        """Test extracting title when no title property exists."""
        properties = {
            "Tags": {
                "type": "multi_select",
                "multi_select": []
            }
        }
        assert extract_title(properties) is None


class TestExtractContent:
    """Test suite for extract_content function."""

    def test_extract_content_from_paragraph_block(self):
        """Test extracting content from paragraph block."""
        block_data = {
            "type": "paragraph",
            "paragraph": {
                "text": [{"text": {"content": "Hello World"}}]
            }
        }
        content = extract_content(block_data)
        assert "text" in content
        assert content["text"][0]["text"]["content"] == "Hello World"

    def test_extract_content_from_heading_block(self):
        """Test extracting content from heading block."""
        block_data = {
            "type": "heading_1",
            "heading_1": {
                "text": [{"text": {"content": "Title"}}]
            }
        }
        content = extract_content(block_data)
        assert "text" in content
        assert content["text"][0]["text"]["content"] == "Title"

    def test_extract_content_returns_none_for_empty_dict(self):
        """Test extracting content from empty dict."""
        assert extract_content({}) is None

    def test_extract_content_returns_none_for_none_input(self):
        """Test extracting content from None input."""
        assert extract_content(None) is None

    def test_extract_content_handles_missing_type(self):
        """Test extracting content when type is missing."""
        block_data = {
            "paragraph": {
                "text": [{"text": {"content": "Hello"}}]
            }
        }
        assert extract_content(block_data) is None

    def test_extract_content_handles_missing_type_field(self):
        """Test extracting content when type field is missing."""
        block_data = {
            "type": "paragraph",
            # Missing "paragraph" field
        }
        content = extract_content(block_data)
        assert content is None
