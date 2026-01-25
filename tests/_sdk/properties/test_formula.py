"""Tests for FormulaParser."""

import pytest
from datetime import datetime

from better_notion._sdk.properties.formula import FormulaParser


class TestFormulaParserString:
    """Tests for formula string results."""

    def test_parse_string(self):
        """Test parsing string formula result."""
        data = {
            "type": "formula",
            "formula": {
                "type": "string",
                "string": "Hello World"
            }
        }

        result = FormulaParser.parse(data)

        assert result == "Hello World"

    def test_parse_empty_string(self):
        """Test parsing empty string formula."""
        data = {
            "type": "formula",
            "formula": {
                "type": "string",
                "string": ""
            }
        }

        result = FormulaParser.parse(data)

        assert result == ""


class TestFormulaParserNumber:
    """Tests for formula number results."""

    def test_parse_integer(self):
        """Test parsing integer formula result."""
        data = {
            "type": "formula",
            "formula": {
                "type": "number",
                "number": 42
            }
        }

        result = FormulaParser.parse(data)

        assert result == 42
        assert isinstance(result, int)

    def test_parse_float(self):
        """Test parsing float formula result."""
        data = {
            "type": "formula",
            "formula": {
                "type": "number",
                "number": 3.14
            }
        }

        result = FormulaParser.parse(data)

        assert result == 3.14
        assert isinstance(result, float)

    def test_parse_float_that_is_integer(self):
        """Test parsing float that equals integer."""
        data = {
            "type": "formula",
            "formula": {
                "type": "number",
                "number": 5.0
            }
        }

        result = FormulaParser.parse(data)

        assert result == 5
        assert isinstance(result, int)

    def test_parse_null_number(self):
        """Test parsing null number formula."""
        data = {
            "type": "formula",
            "formula": {
                "type": "number",
                "number": None
            }
        }

        result = FormulaParser.parse(data)

        assert result is None


class TestFormulaParserBoolean:
    """Tests for formula boolean results."""

    def test_parse_true(self):
        """Test parsing true boolean formula."""
        data = {
            "type": "formula",
            "formula": {
                "type": "boolean",
                "boolean": True
            }
        }

        result = FormulaParser.parse(data)

        assert result is True

    def test_parse_false(self):
        """Test parsing false boolean formula."""
        data = {
            "type": "formula",
            "formula": {
                "type": "boolean",
                "boolean": False
            }
        }

        result = FormulaParser.parse(data)

        assert result is False


class TestFormulaParserDate:
    """Tests for formula date results."""

    def test_parse_date_with_time(self):
        """Test parsing date formula with time."""
        data = {
            "type": "formula",
            "formula": {
                "type": "date",
                "date": {
                    "start": "2024-01-15T10:30:00.000Z",
                    "end": None
                }
            }
        }

        result = FormulaParser.parse(data)

        assert isinstance(result, datetime)
        assert result.year == 2024
        assert result.month == 1
        assert result.day == 15

    def test_parse_date_only(self):
        """Test parsing date formula without time."""
        data = {
            "type": "formula",
            "formula": {
                "type": "date",
                "date": {
                    "start": "2024-01-15",
                    "end": None
                }
            }
        }

        result = FormulaParser.parse(data)

        assert isinstance(result, datetime)
        assert result.year == 2024
        assert result.month == 1
        assert result.day == 15

    def test_parse_null_date(self):
        """Test parsing null date formula."""
        data = {
            "type": "formula",
            "formula": {
                "type": "date",
                "date": None
            }
        }

        result = FormulaParser.parse(data)

        assert result is None


class TestFormulaParserEmpty:
    """Tests for empty formula results."""

    def test_parse_empty(self):
        """Test parsing empty formula result."""
        data = {
            "type": "formula",
            "formula": {
                "type": "empty"
            }
        }

        result = FormulaParser.parse(data)

        assert result is None


class TestFormulaParserErrors:
    """Tests for formula parser error handling."""

    def test_unsupported_type_raises_error(self):
        """Test that unsupported type raises ValueError."""
        data = {
            "type": "formula",
            "formula": {
                "type": "unsupported_type"
            }
        }

        with pytest.raises(ValueError, match="Unsupported formula result type"):
            FormulaParser.parse(data)


class TestFormulaParserHelpers:
    """Tests for formula parser helper methods."""

    def test_get_type(self):
        """Test getting formula result type."""
        data = {
            "type": "formula",
            "formula": {
                "type": "number",
                "number": 42
            }
        }

        result_type = FormulaParser.get_type(data)

        assert result_type == "number"

    def test_get_type_empty(self):
        """Test getting type from empty formula."""
        data = {
            "type": "formula",
            "formula": {}
        }

        result_type = FormulaParser.get_type(data)

        assert result_type == "empty"

    def test_get_expression(self):
        """Test getting formula expression."""
        data = {
            "type": "formula",
            "formula": {
                "expression": "prop(\"Status\") == \"Done\""
            }
        }

        expr = FormulaParser.get_expression(data)

        assert expr == "prop(\"Status\") == \"Done\""

    def test_get_expression_empty(self):
        """Test getting expression when not present."""
        data = {
            "type": "formula",
            "formula": {}
        }

        expr = FormulaParser.get_expression(data)

        assert expr == ""
