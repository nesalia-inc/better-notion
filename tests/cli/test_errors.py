"""
Tests for CLI error codes and exception mapping.

This module tests error code definitions and exception mapping
functionality.
"""
from __future__ import annotations

import pytest

from better_notion._cli.errors import (
    ErrorCode,
    ExitCode,
    map_exception_to_error,
)


class TestExitCode:
    """Test ExitCode enum."""

    def test_exit_code_values(self) -> None:
        """Test that ExitCode has correct values."""
        assert ExitCode.SUCCESS == 0
        assert ExitCode.GENERIC_ERROR == 1
        assert ExitCode.INVALID_INPUT == 2
        assert ExitCode.AUTH_ERROR == 3
        assert ExitCode.RATE_LIMIT == 4
        assert ExitCode.NOT_FOUND == 5
        assert ExitCode.CONFLICT == 6

    def test_exit_code_is_int_enum(self) -> None:
        """Test that ExitCode is an IntEnum."""
        assert isinstance(ExitCode.SUCCESS, int)
        assert ExitCode.SUCCESS == 0


class TestErrorCode:
    """Test ErrorCode enum."""

    def test_error_code_values(self) -> None:
        """Test that ErrorCode has correct string values."""
        assert ErrorCode.VALIDATION_ERROR == "VALIDATION_ERROR"
        assert ErrorCode.NOT_FOUND == "NOT_FOUND"
        assert ErrorCode.UNAUTHORIZED == "UNAUTHORIZED"
        assert ErrorCode.FORBIDDEN == "FORBIDDEN"
        assert ErrorCode.RATE_LIMITED == "RATE_LIMITED"
        assert ErrorCode.CONFLICT == "CONFLICT"
        assert ErrorCode.INTERNAL_ERROR == "INTERNAL_ERROR"
        assert ErrorCode.NETWORK_ERROR == "NETWORK_ERROR"
        assert ErrorCode.TIMEOUT == "TIMEOUT"

    def test_error_code_is_string_enum(self) -> None:
        """Test that ErrorCode is a string enum."""
        assert isinstance(ErrorCode.VALIDATION_ERROR, str)


class TestMapExceptionToError:
    """Test exception mapping function."""

    def test_map_value_error(self) -> None:
        """Test mapping ValueError to validation error."""
        exit_code, error = map_exception_to_error(ValueError("Invalid input"))

        assert exit_code == ExitCode.INVALID_INPUT
        assert error["code"] == ErrorCode.VALIDATION_ERROR
        assert error["message"] == "Invalid input"
        assert error["retry"] is False

    def test_map_key_error(self) -> None:
        """Test mapping KeyError to not found error."""
        exit_code, error = map_exception_to_error(KeyError("page_id"))

        assert exit_code == ExitCode.NOT_FOUND
        assert error["code"] == ErrorCode.NOT_FOUND
        assert error["retry"] is False

    def test_map_attribute_error(self) -> None:
        """Test mapping AttributeError to not found error."""
        exit_code, error = map_exception_to_error(AttributeError("Page not found"))

        assert exit_code == ExitCode.NOT_FOUND
        assert error["code"] == ErrorCode.NOT_FOUND
        assert error["retry"] is False

    def test_map_permission_error(self) -> None:
        """Test mapping PermissionError to auth error."""
        exit_code, error = map_exception_to_error(PermissionError("Access denied"))

        assert exit_code == ExitCode.AUTH_ERROR
        assert error["code"] == ErrorCode.FORBIDDEN
        assert error["message"] == "Access denied"
        assert error["retry"] is False

    def test_map_timeout_exception(self) -> None:
        """Test mapping timeout exceptions."""
        # Test with exception type containing "timeout"
        class TimeoutError(Exception):
            pass

        exit_code, error = map_exception_to_error(TimeoutError("Request timed out"))

        assert exit_code == ExitCode.GENERIC_ERROR
        assert error["code"] == ErrorCode.TIMEOUT
        assert error["retry"] is True
        assert "details" in error
        assert "suggestion" in error["details"]

    def test_map_network_exception(self) -> None:
        """Test mapping network exceptions."""
        # Test with exception type containing "connection"
        class ConnectionError(Exception):
            pass

        exit_code, error = map_exception_to_error(ConnectionError("Network error"))

        assert exit_code == ExitCode.GENERIC_ERROR
        assert error["code"] == ErrorCode.NETWORK_ERROR
        assert error["retry"] is True
        assert "details" in error

    def test_map_generic_exception(self) -> None:
        """Test mapping generic exception to internal error."""
        exit_code, error = map_exception_to_error(RuntimeError("Something went wrong"))

        assert exit_code == ExitCode.GENERIC_ERROR
        assert error["code"] == ErrorCode.INTERNAL_ERROR
        assert error["retry"] is False

    def test_map_exception_without_message(self) -> None:
        """Test mapping exception with empty message."""
        exit_code, error = map_exception_to_error(ValueError(""))

        assert exit_code == ExitCode.INVALID_INPUT
        assert error["code"] == ErrorCode.VALIDATION_ERROR
        assert error["message"] == "Invalid input provided"
        assert error["retry"] is False

    def test_error_dict_structure(self) -> None:
        """Test that error dict has correct structure."""
        exit_code, error = map_exception_to_error(ValueError("Test error"))

        assert "code" in error
        assert isinstance(error["code"], str)
        assert "message" in error
        assert isinstance(error["message"], str)
        assert "retry" in error
        assert isinstance(error["retry"], bool)

    def test_error_dict_with_details(self) -> None:
        """Test that error dict includes details when applicable."""
        class TimeoutError(Exception):
            pass

        exit_code, error = map_exception_to_error(TimeoutError("Request timed out"))

        assert "details" in error
        assert isinstance(error["details"], dict)
