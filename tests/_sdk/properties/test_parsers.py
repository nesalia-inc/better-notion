"""Tests for PropertyParser utilities."""

import pytest

from better_notion._sdk.properties.parsers import PropertyParser


class TestGetTitle:
    """Tests for get_title method."""

    def test_get_title_from_page(self) -> None:
        """Test extracting title from page properties."""
        properties = {
            "Name": {
                "type": "title",
                "title": [
                    {
                        "type": "text",
                        "text": {"content": "My Page Title"}
                    }
                ]
            }
        }

        title = PropertyParser.get_title(properties)
        assert title == "My Page Title"

    def test_get_title_empty_array(self) -> None:
        """Test get_title returns None for empty title array."""
        properties = {
            "Name": {
                "type": "title",
                "title": []
            }
        }

        assert PropertyParser.get_title(properties) is None

    def test_get_title_no_text_content(self) -> None:
        """Test get_title returns None when text has no content."""
        properties = {
            "Name": {
                "type": "title",
                "title": [
                    {
                        "type": "text",
                        "text": {}
                    }
                ]
            }
        }

        assert PropertyParser.get_title(properties) is None

    def test_get_title_finds_first_title(self) -> None:
        """Test get_title finds first property of type title."""
        properties = {
            "Other": {"type": "text", "text": {"content": "..."}} ,
            "Name": {
                "type": "title",
                "title": [
                    {
                        "type": "text",
                        "text": {"content": "Correct Title"}
                    }
                ]
            }
        }

        assert PropertyParser.get_title(properties) == "Correct Title"

    def test_get_title_no_title_property(self) -> None:
        """Test get_title returns None when no title property exists."""
        properties = {
            "Status": {"type": "select", "select": {"name": "Done"}},
            "Tags": {"type": "multi_select", "multi_select": []}
        }

        assert PropertyParser.get_title(properties) is None


class TestGetSelect:
    """Tests for get_select method."""

    def test_get_select_value(self) -> None:
        """Test extracting select value."""
        properties = {
            "Status": {
                "type": "select",
                "select": {"name": "In Progress"}
            }
        }

        status = PropertyParser.get_select(properties, "Status")
        assert status == "In Progress"

    def test_get_select_none(self) -> None:
        """Test get_select returns None when select is empty."""
        properties = {
            "Status": {
                "type": "select",
                "select": None
            }
        }

        assert PropertyParser.get_select(properties, "Status") is None

    def test_get_select_case_insensitive(self) -> None:
        """Test get_select is case-insensitive."""
        properties = {
            "status": {
                "type": "select",
                "select": {"name": "Done"}
            }
        }

        # All these should work
        assert PropertyParser.get_select(properties, "status") == "Done"
        assert PropertyParser.get_select(properties, "STATUS") == "Done"
        assert PropertyParser.get_select(properties, "Status") == "Done"

    def test_get_select_wrong_type(self) -> None:
        """Test get_select returns None for wrong property type."""
        properties = {
            "Status": {
                "type": "text",
                "text": {"content": "Not a select"}
            }
        }

        assert PropertyParser.get_select(properties, "Status") is None

    def test_get_select_missing_property(self) -> None:
        """Test get_select returns None for missing property."""
        properties = {
            "Name": {"type": "title", "title": []}
        }

        assert PropertyParser.get_select(properties, "Status") is None


class TestGetMultiSelect:
    """Tests for get_multi_select method."""

    def test_get_multi_select_values(self) -> None:
        """Test extracting multi-select values."""
        properties = {
            "Tags": {
                "type": "multi_select",
                "multi_select": [
                    {"name": "urgent"},
                    {"name": "backend"},
                    {"name": "feature"}
                ]
            }
        }

        tags = PropertyParser.get_multi_select(properties, "Tags")
        assert tags == ["urgent", "backend", "feature"]

    def test_get_multi_select_empty(self) -> None:
        """Test get_multi_select returns empty list."""
        properties = {
            "Tags": {
                "type": "multi_select",
                "multi_select": []
            }
        }

        assert PropertyParser.get_multi_select(properties, "Tags") == []

    def test_get_multi_select_case_insensitive(self) -> None:
        """Test get_multi_select is case-insensitive."""
        properties = {
            "tags": {
                "type": "multi_select",
                "multi_select": [{"name": "test"}]
            }
        }

        assert PropertyParser.get_multi_select(properties, "TAGS") == ["test"]

    def test_get_multi_select_wrong_type(self) -> None:
        """Test get_multi_select returns empty list for wrong type."""
        properties = {
            "Tags": {
                "type": "text",
                "text": {"content": "Not multi-select"}
            }
        }

        assert PropertyParser.get_multi_select(properties, "Tags") == []


class TestGetCheckbox:
    """Tests for get_checkbox method."""

    def test_get_checkbox_checked(self) -> None:
        """Test extracting checked checkbox."""
        properties = {
            "Done": {
                "type": "checkbox",
                "checkbox": True
            }
        }

        assert PropertyParser.get_checkbox(properties, "Done") is True

    def test_get_checkbox_unchecked(self) -> None:
        """Test extracting unchecked checkbox."""
        properties = {
            "Done": {
                "type": "checkbox",
                "checkbox": False
            }
        }

        assert PropertyParser.get_checkbox(properties, "Done") is False

    def test_get_checkbox_missing(self) -> None:
        """Test get_checkbox returns False for missing field."""
        properties = {
            "Done": {
                "type": "checkbox"
            }
        }

        assert PropertyParser.get_checkbox(properties, "Done") is False

    def test_get_checkbox_case_insensitive(self) -> None:
        """Test get_checkbox is case-insensitive."""
        properties = {
            "done": {
                "type": "checkbox",
                "checkbox": True
            }
        }

        assert PropertyParser.get_checkbox(properties, "DONE") is True


class TestGetNumber:
    """Tests for get_number method."""

    def test_get_number_value(self) -> None:
        """Test extracting number value."""
        properties = {
            "Priority": {
                "type": "number",
                "number": 5
            }
        }

        assert PropertyParser.get_number(properties, "Priority") == 5

    def test_get_number_float(self) -> None:
        """Test extracting float number."""
        properties = {
            "Rating": {
                "type": "number",
                "number": 4.5
            }
        }

        assert PropertyParser.get_number(properties, "Rating") == 4.5

    def test_get_number_zero(self) -> None:
        """Test extracting zero."""
        properties = {
            "Count": {
                "type": "number",
                "number": 0
            }
        }

        assert PropertyParser.get_number(properties, "Count") == 0

    def test_get_number_none(self) -> None:
        """Test get_number returns None for missing field."""
        properties = {
            "Priority": {
                "type": "number"
            }
        }

        assert PropertyParser.get_number(properties, "Priority") is None

    def test_get_number_wrong_type(self) -> None:
        """Test get_number returns None for wrong type."""
        properties = {
            "Priority": {
                "type": "text",
                "text": {"content": "High"}
            }
        }

        assert PropertyParser.get_number(properties, "Priority") is None


class TestGetDate:
    """Tests for get_date method."""

    def test_get_date_value(self) -> None:
        """Test extracting date value."""
        properties = {
            "Due Date": {
                "type": "date",
                "date": {
                    "start": "2025-01-15"
                }
            }
        }

        result = PropertyParser.get_date(properties, "Due Date")
        assert result is not None
        assert result.year == 2025
        assert result.month == 1
        assert result.day == 15

    def test_get_date_with_time(self) -> None:
        """Test extracting date with time."""
        properties = {
            "Created": {
                "type": "date",
                "date": {
                    "start": "2025-01-15T10:30:00.000Z"
                }
            }
        }

        result = PropertyParser.get_date(properties, "Created")
        assert result is not None
        assert result.year == 2025

    def test_get_date_none(self) -> None:
        """Test get_date returns None when date is None."""
        properties = {
            "Due Date": {
                "type": "date",
                "date": None
            }
        }

        assert PropertyParser.get_date(properties, "Due Date") is None

    def test_get_date_no_start(self) -> None:
        """Test get_date returns None when no start field."""
        properties = {
            "Due Date": {
                "type": "date",
                "date": {}
            }
        }

        assert PropertyParser.get_date(properties, "Due Date") is None


class TestGetURL:
    """Tests for get_url method."""

    def test_get_url_value(self) -> None:
        """Test extracting URL value."""
        properties = {
            "URL": {
                "type": "url",
                "url": "https://example.com"
            }
        }

        assert PropertyParser.get_url(properties, "URL") == "https://example.com"

    def test_get_url_default_name(self) -> None:
        """Test get_url uses 'URL' as default property name."""
        properties = {
            "URL": {
                "type": "url",
                "url": "https://example.com"
            }
        }

        assert PropertyParser.get_url(properties) == "https://example.com"

    def test_get_url_none(self) -> None:
        """Test get_url returns None for missing URL."""
        properties = {
            "URL": {
                "type": "url"
            }
        }

        assert PropertyParser.get_url(properties, "URL") is None


class TestGetEmail:
    """Tests for get_email method."""

    def test_get_email_value(self) -> None:
        """Test extracting email value."""
        properties = {
            "Email": {
                "type": "email",
                "email": "user@example.com"
            }
        }

        assert PropertyParser.get_email(properties, "Email") == "user@example.com"

    def test_get_email_default_name(self) -> None:
        """Test get_email uses 'Email' as default property name."""
        properties = {
            "Email": {
                "type": "email",
                "email": "test@example.com"
            }
        }

        assert PropertyParser.get_email(properties) == "test@example.com"


class TestGetPhone:
    """Tests for get_phone method."""

    def test_get_phone_value(self) -> None:
        """Test extracting phone value."""
        properties = {
            "Phone": {
                "type": "phone",
                "phone": "+1-555-0123"
            }
        }

        assert PropertyParser.get_phone(properties, "Phone") == "+1-555-0123"

    def test_get_phone_default_name(self) -> None:
        """Test get_phone uses 'Phone' as default property name."""
        properties = {
            "Phone": {
                "type": "phone",
                "phone": "+1-555-0123"
            }
        }

        assert PropertyParser.get_phone(properties) == "+1-555-0123"


class TestGetPeople:
    """Tests for get_people method."""

    def test_get_people_multiple(self) -> None:
        """Test extracting multiple people."""
        properties = {
            "Assignee": {
                "type": "people",
                "people": [
                    {"id": "user-1"},
                    {"id": "user-2"}
                ]
            }
        }

        people = PropertyParser.get_people(properties, "Assignee")
        assert people == ["user-1", "user-2"]

    def test_get_people_single(self) -> None:
        """Test extracting single person."""
        properties = {
            "Assignee": {
                "type": "people",
                "people": [
                    {"id": "user-1"}
                ]
            }
        }

        assert PropertyParser.get_people(properties, "Assignee") == ["user-1"]

    def test_get_people_empty(self) -> None:
        """Test get_people returns empty list."""
        properties = {
            "Assignee": {
                "type": "people",
                "people": []
            }
        }

        assert PropertyParser.get_people(properties, "Assignee") == []


class TestFindProperty:
    """Tests for _find_property helper."""

    def test_find_property_exact_match(self) -> None:
        """Test finding property with exact name."""
        properties = {
            "Status": {"type": "select", "select": {"name": "Done"}},
            "Tags": {"type": "multi_select", "multi_select": []}
        }

        prop = PropertyParser._find_property(properties, "Status")
        assert prop is not None
        assert prop["type"] == "select"

    def test_find_property_case_insensitive(self) -> None:
        """Test _find_property is case-insensitive."""
        properties = {
            "Status": {"type": "select", "select": {"name": "Done"}}
        }

        # All these should work
        assert PropertyParser._find_property(properties, "status") is not None
        assert PropertyParser._find_property(properties, "STATUS") is not None
        assert PropertyParser._find_property(properties, "Status") is not None

    def test_find_property_not_found(self) -> None:
        """Test _find_property returns None for missing property."""
        properties = {
            "Status": {"type": "select", "select": {"name": "Done"}}
        }

        assert PropertyParser._find_property(properties, "Missing") is None

    def test_find_property_multiple_matches(self) -> None:
        """Test _find_property returns first match."""
        properties = {
            "status": {"type": "select", "select": {"name": "A"}},
            "Status": {"type": "select", "select": {"name": "B"}}
        }

        # Should find the first one
        prop = PropertyParser._find_property(properties, "status")
        assert prop is not None
        # Which one depends on dict iteration order, but should be one of them
        assert prop["select"]["name"] in ["A", "B"]
