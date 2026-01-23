"""Test property builders."""

from __future__ import annotations

import pytest
from datetime import datetime

from better_notion._api.properties import (
    Checkbox,
    Date,
    Email,
    MultiSelect,
    Number,
    Phone,
    RichText,
    Select,
    Text,
    Title,
    URL,
)


class TestRichText:
    """Test suite for RichText builder."""

    def test_rich_text_simple(self):
        """Test simple rich text."""
        rt = RichText("description", "Hello World")
        result = rt.to_dict()

        assert result["type"] == "text"
        assert result["text"]["content"] == "Hello World"

    def test_rich_text_with_formatting(self):
        """Test rich text with formatting."""
        rt = RichText(
            "description",
            "Hello",
            bold=True,
            italic=True,
            link="https://example.com"
        )
        result = rt.to_dict()

        assert result["text"]["content"] == "Hello"
        assert result["text"]["link"]["url"] == "https://example.com"
        assert result["annotations"]["bold"] is True
        assert result["annotations"]["italic"] is True


class TestText:
    """Test suite for Text builder."""

    def test_text_property(self):
        """Test text property."""
        text = Text("Notes", "Some notes")
        result = text.to_dict()

        assert result["type"] == "text"
        assert result["text"][0]["text"]["content"] == "Some notes"


class TestTitle:
    """Test suite for Title builder."""

    def test_title_default(self):
        """Test title with default name."""
        title = Title(content="My Page")
        result = title.to_dict()

        assert title.name == "Name"
        assert result["type"] == "title"
        assert result["title"][0]["text"]["content"] == "My Page"

    def test_title_custom_name(self):
        """Test title with custom name."""
        title = Title("Custom Title", "My Page")
        result = title.to_dict()

        assert title.name == "Custom Title"
        assert result["title"][0]["text"]["content"] == "My Page"


class TestSelect:
    """Test suite for Select builder."""

    def test_select_property(self):
        """Test select property."""
        select = Select("Status", "Done")
        result = select.to_dict()

        assert result["type"] == "select"
        assert result["select"]["name"] == "Done"


class TestMultiSelect:
    """Test suite for MultiSelect builder."""

    def test_multi_select_property(self):
        """Test multi-select property."""
        ms = MultiSelect("Tags", ["tag1", "tag2"])
        result = ms.to_dict()

        assert result["type"] == "multi_select"
        assert len(result["multi_select"]) == 2
        assert result["multi_select"][0]["name"] == "tag1"
        assert result["multi_select"][1]["name"] == "tag2"


class TestCheckbox:
    """Test suite for Checkbox builder."""

    def test_checkbox_checked(self):
        """Test checked checkbox."""
        cb = Checkbox("Done", True)
        result = cb.to_dict()

        assert result["type"] == "checkbox"
        assert result["checkbox"] is True

    def test_checkbox_unchecked(self):
        """Test unchecked checkbox."""
        cb = Checkbox("Done", False)
        result = cb.to_dict()

        assert result["checkbox"] is False


class TestDate:
    """Test suite for Date builder."""

    def test_date_with_datetime(self):
        """Test date with datetime object."""
        dt = datetime(2025, 1, 15, 12, 0, 0)
        date = Date("Due", dt)
        result = date.to_dict()

        assert result["type"] == "date"
        assert "2025-01-15T12:00:00" in result["date"]["start"]

    def test_date_with_string(self):
        """Test date with ISO string."""
        date = Date("Due", "2025-01-15")
        result = date.to_dict()

        assert result["date"]["start"] == "2025-01-15"

    def test_date_range(self):
        """Test date with end date (range)."""
        date = Date("Schedule", "2025-01-15", end="2025-01-20")
        result = date.to_dict()

        assert result["date"]["start"] == "2025-01-15"
        assert result["date"]["end"] == "2025-01-20"


class TestNumber:
    """Test suite for Number builder."""

    def test_number_integer(self):
        """Test number with integer."""
        num = Number("Count", 42)
        result = num.to_dict()

        assert result["type"] == "number"
        assert result["number"] == 42

    def test_number_float(self):
        """Test number with float."""
        num = Number("Price", 19.99)
        result = num.to_dict()

        assert result["number"] == 19.99

    def test_number_none(self):
        """Test number with None value."""
        num = Number("Count", None)
        result = num.to_dict()

        assert result["number"] is None


class TestURL:
    """Test suite for URL builder."""

    def test_url_property(self):
        """Test URL property."""
        url = URL("Website", "https://example.com")
        result = url.to_dict()

        assert result["type"] == "url"
        assert result["url"] == "https://example.com"


class TestEmail:
    """Test suite for Email builder."""

    def test_email_property(self):
        """Test email property."""
        email = Email("Contact", "user@example.com")
        result = email.to_dict()

        assert result["type"] == "email"
        assert result["email"] == "user@example.com"


class TestPhone:
    """Test suite for Phone builder."""

    def test_phone_property(self):
        """Test phone property."""
        phone = Phone("Mobile", "+1234567890")
        result = phone.to_dict()

        assert result["type"] == "phone_number"
        assert result["phone_number"] == "+1234567890"


class TestPropertyBuild:
    """Test suite for Property.build() method."""

    def test_property_build(self):
        """Test Property.build() returns complete dict."""
        title = Title("My Title", "Content")
        result = title.build()

        assert "My Title" in result
        assert result["My Title"]["type"] == "title"
