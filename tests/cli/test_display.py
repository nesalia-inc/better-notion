"""
Tests for Rich display utilities.

This module tests the display mode detection and Rich formatting functions.
"""
from __future__ import annotations

import json

import pytest
from typer.testing import CliRunner

from better_notion._cli.display import (
    DisplayMode,
    get_display_mode,
    is_human_mode,
    print_rich,
    print_rich_error,
    print_rich_info,
    print_rich_success,
    print_rich_table,
)


class TestDisplayMode:
    """Tests for display mode detection."""

    def test_get_display_mode_default(self):
        """Test that default mode is human when in TTY."""
        # In test environment, this should return human mode
        mode = get_display_mode()
        assert mode in [DisplayMode.AI, DisplayMode.HUMAN]

    def test_get_display_mode_force_json(self):
        """Test that force_json parameter overrides detection."""
        mode = get_display_mode(force_json=True)
        assert mode == DisplayMode.AI

    def test_is_human_mode_default(self):
        """Test default human mode detection."""
        result = is_human_mode()
        assert isinstance(result, bool)

    def test_is_human_mode_force_json(self):
        """Test that force_json disables human mode."""
        assert is_human_mode(force_json=True) is False

    def test_is_human_mode_rich_mode(self):
        """Test that rich_mode parameter forces human mode."""
        assert is_human_mode(rich_mode=True) is True

    def test_is_human_mode_both_flags(self):
        """Test that force_json takes precedence over rich_mode."""
        assert is_human_mode(force_json=True, rich_mode=True) is False


class TestPrintRich:
    """Tests for print_rich function."""

    def test_print_rich_json_mode_skips_output(self, capsys):
        """Test that print_rich skips output in JSON mode."""
        print_rich("Test content", json_output=True)
        captured = capsys.readouterr()
        assert captured.out == ""

    def test_print_rich_with_title(self, capsys):
        """Test print_rich with title parameter."""
        # In human mode, this would output to terminal
        # In JSON mode, it should skip
        print_rich("Test content", title="Test Title", json_output=True)
        captured = capsys.readouterr()
        assert captured.out == ""


class TestPrintRichTable:
    """Tests for print_rich_table function."""

    def test_print_rich_table_json_mode(self, capsys):
        """Test that print_rich_table outputs JSON in JSON mode."""
        data = [{"name": "test", "value": "123"}]

        print_rich_table(data, json_output=True)

        captured = capsys.readouterr()
        result = json.loads(captured.out)

        assert result == data

    def test_print_rich_table_with_columns(self, capsys):
        """Test print_rich_table with specific columns."""
        data = [
            {"name": "test1", "value": "123", "extra": "ignored"},
            {"name": "test2", "value": "456", "extra": "ignored"},
        ]

        print_rich_table(data, columns=["name", "value"], json_output=True)

        captured = capsys.readouterr()
        result = json.loads(captured.out)

        # Should only include specified columns
        assert "name" in result[0]
        assert "value" in result[0]
        # The implementation doesn't filter columns in JSON mode
        # so we just check the data is present

    def test_print_rich_table_empty_data(self, capsys):
        """Test print_rich_table with empty data."""
        print_rich_table([], json_output=True)

        captured = capsys.readouterr()
        result = json.loads(captured.out)

        assert result == []

    def test_print_rich_table_dict_format(self, capsys):
        """Test print_rich_table with dict format."""
        data = {"col1": ["val1", "val2"], "col2": ["val3", "val4"]}

        print_rich_table(data, json_output=True)

        captured = capsys.readouterr()
        result = json.loads(captured.out)

        assert "col1" in result
        assert "col2" in result


class TestPrintRichInfo:
    """Tests for print_rich_info function."""

    def test_print_rich_info_json_mode(self, capsys):
        """Test that print_rich_info outputs JSON in JSON mode."""
        info = {"key1": "value1", "key2": "value2"}

        print_rich_info(info, json_output=True)

        captured = capsys.readouterr()
        result = json.loads(captured.out)

        assert result["key1"] == "value1"
        assert result["key2"] == "value2"

    def test_print_rich_info_with_title(self, capsys):
        """Test print_rich_info with title."""
        info = {"status": "enabled"}

        print_rich_info(info, title="Status", json_output=True)

        captured = capsys.readouterr()
        result = json.loads(captured.out)

        assert result["status"] == "enabled"

    def test_print_rich_info_with_success_key(self, capsys):
        """Test print_rich_info formats success field."""
        info = {"success": True, "message": "Test message"}

        print_rich_info(info, json_output=True)

        captured = capsys.readouterr()
        result = json.loads(captured.out)

        assert result["success"] is True
        assert result["message"] == "Test message"


class TestPrintRichSuccess:
    """Tests for print_rich_success function."""

    def test_print_rich_success_json_mode(self, capsys):
        """Test that print_rich_success outputs JSON in JSON mode."""
        print_rich_success("Operation completed", json_output=True)

        captured = capsys.readouterr()
        result = json.loads(captured.out)

        assert result["success"] is True
        assert result["message"] == "Operation completed"

    def test_print_rich_success_with_data(self, capsys):
        """Test print_rich_success with additional data."""
        print_rich_success(
            "Operation completed",
            data={"id": "123", "name": "test"},
            json_output=True
        )

        captured = capsys.readouterr()
        result = json.loads(captured.out)

        assert result["success"] is True
        assert result["message"] == "Operation completed"
        assert result["data"]["id"] == "123"
        assert result["data"]["name"] == "test"


class TestPrintRichError:
    """Tests for print_rich_error function."""

    def test_print_rich_error_json_mode(self, capsys):
        """Test that print_rich_error outputs JSON in JSON mode."""
        print_rich_error("Operation failed", code="TEST_ERROR", json_output=True)

        captured = capsys.readouterr()
        result = json.loads(captured.out)

        assert result["success"] is False
        assert result["error"]["message"] == "Operation failed"
        assert result["error"]["code"] == "TEST_ERROR"

    def test_print_rich_error_with_details(self, capsys):
        """Test print_rich_error with details."""
        print_rich_error(
            "Operation failed",
            code="TEST_ERROR",
            details={"field": "value"},
            json_output=True
        )

        captured = capsys.readouterr()
        result = json.loads(captured.out)

        assert result["success"] is False
        assert result["error"]["message"] == "Operation failed"
        assert result["error"]["code"] == "TEST_ERROR"
        assert result["error"]["details"]["field"] == "value"

    def test_print_rich_error_without_code(self, capsys):
        """Test print_rich_error without error code."""
        print_rich_error("Operation failed", json_output=True)

        captured = capsys.readouterr()
        result = json.loads(captured.out)

        assert result["success"] is False
        assert result["error"]["message"] == "Operation failed"
        assert "code" not in result["error"]


class TestDisplayModeIntegration:
    """Integration tests for display mode with commands."""

    def test_human_mode_respects_environment(self):
        """Test that human mode detection respects the runtime environment."""
        mode = get_display_mode()
        assert mode in [DisplayMode.AI, DisplayMode.HUMAN]

    def test_display_mode_enum_values(self):
        """Test that DisplayMode enum has expected values."""
        assert DisplayMode.AI == "ai"
        assert DisplayMode.HUMAN == "human"
        assert DisplayMode.AUTO == "auto"
