"""Tests for FilterTranslator."""

import pytest
from datetime import datetime

from better_notion._sdk.query.filter_translator import FilterTranslator


@pytest.fixture
def database_schema():
    """Sample database schema."""
    return {
        "Name": {"id": "title", "type": "title"},
        "Status": {"id": "status", "type": "select"},
        "Tags": {"id": "tags", "type": "multi_select"},
        "Priority": {"id": "priority", "type": "number"},
        "DueDate": {"id": "due_date", "type": "date"},
        "Description": {"id": "description", "type": "text"},
        "IsDone": {"id": "is_done", "type": "checkbox"},
        "Assignee": {"id": "assignee", "type": "people"},
        "Attachments": {"id": "attachments", "type": "files"},
    }


class TestFilterTranslatorSelect:
    """Tests for select property filters."""

    def test_select_equals(self, database_schema):
        """Test select equals operator."""
        result = FilterTranslator.translate(
            prop_name="Status",
            operator="eq",
            value="Done",
            schema=database_schema
        )

        assert result == {
            "property": "Status",
            "select": {"equals": "Done"}
        }

    def test_select_not_equals(self, database_schema):
        """Test select does_not_equal operator."""
        result = FilterTranslator.translate(
            prop_name="Status",
            operator="ne",
            value="Done",
            schema=database_schema
        )

        assert result == {
            "property": "Status",
            "select": {"does_not_equal": "Done"}
        }

    def test_select_is_empty(self, database_schema):
        """Test select is_empty operator."""
        result = FilterTranslator.translate(
            prop_name="Status",
            operator="is_null",
            value=None,
            schema=database_schema
        )

        assert result == {
            "property": "Status",
            "select": {"is_empty": True}
        }

    def test_select_is_not_empty(self, database_schema):
        """Test select is_not_empty operator."""
        result = FilterTranslator.translate(
            prop_name="Status",
            operator="is_not_null",
            value=None,
            schema=database_schema
        )

        assert result == {
            "property": "Status",
            "select": {"is_not_empty": True}
        }

    def test_select_in_operator(self, database_schema):
        """Test select in operator (mapped to equals)."""
        result = FilterTranslator.translate(
            prop_name="Status",
            operator="in",
            value="Done",
            schema=database_schema
        )

        assert result == {
            "property": "Status",
            "select": {"equals": "Done"}
        }

    def test_select_unsupported_operator(self, database_schema):
        """Test select with unsupported operator raises error."""
        with pytest.raises(ValueError, match="Operator 'gt' not supported for select"):
            FilterTranslator.translate(
                prop_name="Status",
                operator="gt",
                value="Done",
                schema=database_schema
            )


class TestFilterTranslatorMultiSelect:
    """Tests for multi-select property filters."""

    def test_multi_select_contains(self, database_schema):
        """Test multi_select contains operator."""
        result = FilterTranslator.translate(
            prop_name="Tags",
            operator="contains",
            value="important",
            schema=database_schema
        )

        assert result == {
            "property": "Tags",
            "multi_select": {"contains": "important"}
        }

    def test_multi_select_is_empty(self, database_schema):
        """Test multi_select is_empty operator."""
        result = FilterTranslator.translate(
            prop_name="Tags",
            operator="is_null",
            value=None,
            schema=database_schema
        )

        assert result == {
            "property": "Tags",
            "multi_select": {"is_empty": True}
        }

    def test_multi_select_is_not_empty(self, database_schema):
        """Test multi_select is_not_empty operator."""
        result = FilterTranslator.translate(
            prop_name="Tags",
            operator="is_not_null",
            value=None,
            schema=database_schema
        )

        assert result == {
            "property": "Tags",
            "multi_select": {"is_not_empty": True}
        }

    def test_multi_select_in_operator(self, database_schema):
        """Test multi_select in operator (mapped to contains)."""
        result = FilterTranslator.translate(
            prop_name="Tags",
            operator="in",
            value="important",
            schema=database_schema
        )

        assert result == {
            "property": "Tags",
            "multi_select": {"contains": "important"}
        }

    def test_multi_select_unsupported_operator(self, database_schema):
        """Test multi_select with unsupported operator raises error."""
        with pytest.raises(ValueError, match="Operator 'eq' not supported for multi_select"):
            FilterTranslator.translate(
                prop_name="Tags",
                operator="eq",
                value="important",
                schema=database_schema
            )


class TestFilterTranslatorNumber:
    """Tests for number property filters."""

    def test_number_equals(self, database_schema):
        """Test number equals operator."""
        result = FilterTranslator.translate(
            prop_name="Priority",
            operator="eq",
            value=5,
            schema=database_schema
        )

        assert result == {
            "property": "Priority",
            "number": {"equals": 5}
        }

    def test_number_not_equals(self, database_schema):
        """Test number does_not_equal operator."""
        result = FilterTranslator.translate(
            prop_name="Priority",
            operator="ne",
            value=5,
            schema=database_schema
        )

        assert result == {
            "property": "Priority",
            "number": {"does_not_equal": 5}
        }

    def test_number_greater_than(self, database_schema):
        """Test number greater_than operator."""
        result = FilterTranslator.translate(
            prop_name="Priority",
            operator="gt",
            value=5,
            schema=database_schema
        )

        assert result == {
            "property": "Priority",
            "number": {"greater_than": 5}
        }

    def test_number_greater_than_or_equal_to(self, database_schema):
        """Test number greater_than_or_equal_to operator."""
        result = FilterTranslator.translate(
            prop_name="Priority",
            operator="gte",
            value=5,
            schema=database_schema
        )

        assert result == {
            "property": "Priority",
            "number": {"greater_than_or_equal_to": 5}
        }

    def test_number_less_than(self, database_schema):
        """Test number less_than operator."""
        result = FilterTranslator.translate(
            prop_name="Priority",
            operator="lt",
            value=5,
            schema=database_schema
        )

        assert result == {
            "property": "Priority",
            "number": {"less_than": 5}
        }

    def test_number_less_than_or_equal_to(self, database_schema):
        """Test number less_than_or_equal_to operator."""
        result = FilterTranslator.translate(
            prop_name="Priority",
            operator="lte",
            value=5,
            schema=database_schema
        )

        assert result == {
            "property": "Priority",
            "number": {"less_than_or_equal_to": 5}
        }

    def test_number_with_float(self, database_schema):
        """Test number filter with float value."""
        result = FilterTranslator.translate(
            prop_name="Priority",
            operator="gte",
            value=3.5,
            schema=database_schema
        )

        assert result == {
            "property": "Priority",
            "number": {"greater_than_or_equal_to": 3.5}
        }

    def test_number_unsupported_operator(self, database_schema):
        """Test number with unsupported operator raises error."""
        with pytest.raises(ValueError, match="Operator 'contains' not supported for number"):
            FilterTranslator.translate(
                prop_name="Priority",
                operator="contains",
                value=5,
                schema=database_schema
            )


class TestFilterTranslatorDate:
    """Tests for date property filters."""

    def test_date_equals(self, database_schema):
        """Test date equals operator."""
        result = FilterTranslator.translate(
            prop_name="DueDate",
            operator="eq",
            value="2024-01-01",
            schema=database_schema
        )

        assert result == {
            "property": "DueDate",
            "date": {"equals": "2024-01-01"}
        }

    def test_date_not_equals(self, database_schema):
        """Test date does_not_equal operator."""
        result = FilterTranslator.translate(
            prop_name="DueDate",
            operator="ne",
            value="2024-01-01",
            schema=database_schema
        )

        assert result == {
            "property": "DueDate",
            "date": {"does_not_equal": "2024-01-01"}
        }

    def test_date_before(self, database_schema):
        """Test date before operator."""
        result = FilterTranslator.translate(
            prop_name="DueDate",
            operator="before",
            value="2024-01-01",
            schema=database_schema
        )

        assert result == {
            "property": "DueDate",
            "date": {"before": "2024-01-01"}
        }

    def test_date_lt_alias(self, database_schema):
        """Test date lt operator (alias for before)."""
        result = FilterTranslator.translate(
            prop_name="DueDate",
            operator="lt",
            value="2024-01-01",
            schema=database_schema
        )

        assert result == {
            "property": "DueDate",
            "date": {"before": "2024-01-01"}
        }

    def test_date_after(self, database_schema):
        """Test date after operator."""
        result = FilterTranslator.translate(
            prop_name="DueDate",
            operator="after",
            value="2024-01-01",
            schema=database_schema
        )

        assert result == {
            "property": "DueDate",
            "date": {"after": "2024-01-01"}
        }

    def test_date_gt_alias(self, database_schema):
        """Test date gt operator (alias for after)."""
        result = FilterTranslator.translate(
            prop_name="DueDate",
            operator="gt",
            value="2024-01-01",
            schema=database_schema
        )

        assert result == {
            "property": "DueDate",
            "date": {"after": "2024-01-01"}
        }

    def test_date_on_or_before(self, database_schema):
        """Test date on_or_before operator."""
        result = FilterTranslator.translate(
            prop_name="DueDate",
            operator="on_or_before",
            value="2024-01-01",
            schema=database_schema
        )

        assert result == {
            "property": "DueDate",
            "date": {"on_or_before": "2024-01-01"}
        }

    def test_date_lte_alias(self, database_schema):
        """Test date lte operator (alias for on_or_before)."""
        result = FilterTranslator.translate(
            prop_name="DueDate",
            operator="lte",
            value="2024-01-01",
            schema=database_schema
        )

        assert result == {
            "property": "DueDate",
            "date": {"on_or_before": "2024-01-01"}
        }

    def test_date_on_or_after(self, database_schema):
        """Test date on_or_after operator."""
        result = FilterTranslator.translate(
            prop_name="DueDate",
            operator="on_or_after",
            value="2024-01-01",
            schema=database_schema
        )

        assert result == {
            "property": "DueDate",
            "date": {"on_or_after": "2024-01-01"}
        }

    def test_date_gte_alias(self, database_schema):
        """Test date gte operator (alias for on_or_after)."""
        result = FilterTranslator.translate(
            prop_name="DueDate",
            operator="gte",
            value="2024-01-01",
            schema=database_schema
        )

        assert result == {
            "property": "DueDate",
            "date": {"on_or_after": "2024-01-01"}
        }

    def test_date_with_datetime_object(self, database_schema):
        """Test date filter with datetime object converts to ISO string."""
        dt = datetime(2024, 1, 1, 12, 30, 45)
        result = FilterTranslator.translate(
            prop_name="DueDate",
            operator="eq",
            value=dt,
            schema=database_schema
        )

        assert result == {
            "property": "DueDate",
            "date": {"equals": "2024-01-01T12:30:45"}
        }

    def test_date_is_empty(self, database_schema):
        """Test date is_empty operator."""
        result = FilterTranslator.translate(
            prop_name="DueDate",
            operator="is_null",
            value=None,
            schema=database_schema
        )

        assert result == {
            "property": "DueDate",
            "date": {"is_empty": True}
        }

    def test_date_is_not_empty(self, database_schema):
        """Test date is_not_empty operator."""
        result = FilterTranslator.translate(
            prop_name="DueDate",
            operator="is_not_null",
            value=None,
            schema=database_schema
        )

        assert result == {
            "property": "DueDate",
            "date": {"is_not_empty": True}
        }


class TestFilterTranslatorText:
    """Tests for text property filters."""

    def test_text_equals(self, database_schema):
        """Test text equals operator."""
        result = FilterTranslator.translate(
            prop_name="Description",
            operator="eq",
            value="Hello world",
            schema=database_schema
        )

        assert result == {
            "property": "Description",
            "rich_text": {"equals": "Hello world"}
        }

    def test_text_not_equals(self, database_schema):
        """Test text does_not_equal operator."""
        result = FilterTranslator.translate(
            prop_name="Description",
            operator="ne",
            value="Hello world",
            schema=database_schema
        )

        assert result == {
            "property": "Description",
            "rich_text": {"does_not_equal": "Hello world"}
        }

    def test_text_contains(self, database_schema):
        """Test text contains operator."""
        result = FilterTranslator.translate(
            prop_name="Description",
            operator="contains",
            value="world",
            schema=database_schema
        )

        assert result == {
            "property": "Description",
            "rich_text": {"contains": "world"}
        }

    def test_text_starts_with(self, database_schema):
        """Test text starts_with operator."""
        result = FilterTranslator.translate(
            prop_name="Description",
            operator="starts_with",
            value="Hello",
            schema=database_schema
        )

        assert result == {
            "property": "Description",
            "rich_text": {"starts_with": "Hello"}
        }

    def test_text_ends_with(self, database_schema):
        """Test text ends_with operator."""
        result = FilterTranslator.translate(
            prop_name="Description",
            operator="ends_with",
            value="world",
            schema=database_schema
        )

        assert result == {
            "property": "Description",
            "rich_text": {"ends_with": "world"}
        }

    def test_text_is_empty(self, database_schema):
        """Test text is_empty operator."""
        result = FilterTranslator.translate(
            prop_name="Description",
            operator="is_null",
            value=None,
            schema=database_schema
        )

        assert result == {
            "property": "Description",
            "rich_text": {"is_empty": True}
        }

    def test_text_is_not_empty(self, database_schema):
        """Test text is_not_empty operator."""
        result = FilterTranslator.translate(
            prop_name="Description",
            operator="is_not_null",
            value=None,
            schema=database_schema
        )

        assert result == {
            "property": "Description",
            "rich_text": {"is_not_empty": True}
        }

    def test_text_unsupported_operator(self, database_schema):
        """Test text with unsupported operator raises error."""
        with pytest.raises(ValueError, match="Operator 'gt' not supported for text"):
            FilterTranslator.translate(
                prop_name="Description",
                operator="gt",
                value="Hello",
                schema=database_schema
            )


class TestFilterTranslatorCheckbox:
    """Tests for checkbox property filters."""

    def test_checkbox_equals_true(self, database_schema):
        """Test checkbox equals operator with True."""
        result = FilterTranslator.translate(
            prop_name="IsDone",
            operator="eq",
            value=True,
            schema=database_schema
        )

        assert result == {
            "property": "IsDone",
            "checkbox": {"equals": True}
        }

    def test_checkbox_equals_false(self, database_schema):
        """Test checkbox equals operator with False."""
        result = FilterTranslator.translate(
            prop_name="IsDone",
            operator="eq",
            value=False,
            schema=database_schema
        )

        assert result == {
            "property": "IsDone",
            "checkbox": {"equals": False}
        }

    def test_checkbox_not_equals(self, database_schema):
        """Test checkbox does_not_equal operator."""
        result = FilterTranslator.translate(
            prop_name="IsDone",
            operator="ne",
            value=True,
            schema=database_schema
        )

        assert result == {
            "property": "IsDone",
            "checkbox": {"does_not_equal": True}
        }

    def test_checkbox_unsupported_operator(self, database_schema):
        """Test checkbox with unsupported operator raises error."""
        with pytest.raises(ValueError, match="Operator 'gt' not supported for checkbox"):
            FilterTranslator.translate(
                prop_name="IsDone",
                operator="gt",
                value=True,
                schema=database_schema
            )


class TestFilterTranslatorPeople:
    """Tests for people property filters."""

    def test_people_contains(self, database_schema):
        """Test people contains operator."""
        result = FilterTranslator.translate(
            prop_name="Assignee",
            operator="contains",
            value="user-123",
            schema=database_schema
        )

        assert result == {
            "property": "Assignee",
            "people": {"contains": "user-123"}
        }

    def test_people_is_empty(self, database_schema):
        """Test people is_empty operator."""
        result = FilterTranslator.translate(
            prop_name="Assignee",
            operator="is_null",
            value=None,
            schema=database_schema
        )

        assert result == {
            "property": "Assignee",
            "people": {"is_empty": True}
        }

    def test_people_is_not_empty(self, database_schema):
        """Test people is_not_empty operator."""
        result = FilterTranslator.translate(
            prop_name="Assignee",
            operator="is_not_null",
            value=None,
            schema=database_schema
        )

        assert result == {
            "property": "Assignee",
            "people": {"is_not_empty": True}
        }

    def test_people_unsupported_operator(self, database_schema):
        """Test people with unsupported operator raises error."""
        with pytest.raises(ValueError, match="Operator 'eq' not supported for people"):
            FilterTranslator.translate(
                prop_name="Assignee",
                operator="eq",
                value="user-123",
                schema=database_schema
            )


class TestFilterTranslatorFiles:
    """Tests for files property filters."""

    def test_files_is_empty(self, database_schema):
        """Test files is_empty operator."""
        result = FilterTranslator.translate(
            prop_name="Attachments",
            operator="is_null",
            value=None,
            schema=database_schema
        )

        assert result == {
            "property": "Attachments",
            "files": {"is_empty": True}
        }

    def test_files_is_not_empty(self, database_schema):
        """Test files is_not_empty operator."""
        result = FilterTranslator.translate(
            prop_name="Attachments",
            operator="is_not_null",
            value=None,
            schema=database_schema
        )

        assert result == {
            "property": "Attachments",
            "files": {"is_not_empty": True}
        }

    def test_files_unsupported_operator(self, database_schema):
        """Test files with unsupported operator raises error."""
        with pytest.raises(ValueError, match="Operator 'eq' not supported for files"):
            FilterTranslator.translate(
                prop_name="Attachments",
                operator="eq",
                value="file-123",
                schema=database_schema
            )


class TestFilterTranslatorEdgeCases:
    """Tests for edge cases and error handling."""

    def test_case_insensitive_property_lookup(self, database_schema):
        """Test property name lookup is case-insensitive."""
        result = FilterTranslator.translate(
            prop_name="status",  # lowercase
            operator="eq",
            value="Done",
            schema=database_schema
        )

        assert result == {
            "property": "status",
            "select": {"equals": "Done"}
        }

    def test_case_insensitive_property_lookup_uppercase(self, database_schema):
        """Test property name lookup with uppercase."""
        result = FilterTranslator.translate(
            prop_name="STATUS",  # uppercase
            operator="eq",
            value="Done",
            schema=database_schema
        )

        assert result == {
            "property": "STATUS",
            "select": {"equals": "Done"}
        }

    def test_property_not_found_raises_error(self, database_schema):
        """Test error when property not found in schema."""
        with pytest.raises(ValueError, match="Property not found: NonExistent"):
            FilterTranslator.translate(
                prop_name="NonExistent",
                operator="eq",
                value="value",
                schema=database_schema
            )

    def test_unsupported_property_type(self):
        """Test error for unsupported property type."""
        schema = {
            "Formula": {"id": "formula", "type": "formula"}
        }

        with pytest.raises(ValueError, match="Unsupported property type: formula"):
            FilterTranslator.translate(
                prop_name="Formula",
                operator="eq",
                value="value",
                schema=schema
            )

    def test_title_uses_text_translation(self):
        """Test title property uses rich_text translation."""
        schema = {
            "Name": {"id": "name", "type": "title"}
        }

        result = FilterTranslator.translate(
            prop_name="Name",
            operator="contains",
            value="Test",
            schema=schema
        )

        assert result == {
            "property": "Name",
            "rich_text": {"contains": "Test"}
        }

    def test_url_uses_text_translation(self):
        """Test url property uses rich_text translation."""
        schema = {
            "Website": {"id": "website", "type": "url"}
        }

        result = FilterTranslator.translate(
            prop_name="Website",
            operator="eq",
            value="https://example.com",
            schema=schema
        )

        assert result == {
            "property": "Website",
            "rich_text": {"equals": "https://example.com"}
        }

    def test_email_uses_text_translation(self):
        """Test email property uses rich_text translation."""
        schema = {
            "Email": {"id": "email", "type": "email"}
        }

        result = FilterTranslator.translate(
            prop_name="Email",
            operator="eq",
            value="test@example.com",
            schema=schema
        )

        assert result == {
            "property": "Email",
            "rich_text": {"equals": "test@example.com"}
        }

    def test_phone_uses_text_translation(self):
        """Test phone property uses rich_text translation."""
        schema = {
            "Phone": {"id": "phone", "type": "phone"}
        }

        result = FilterTranslator.translate(
            prop_name="Phone",
            operator="eq",
            value="+1234567890",
            schema=schema
        )

        assert result == {
            "property": "Phone",
            "rich_text": {"equals": "+1234567890"}
        }
