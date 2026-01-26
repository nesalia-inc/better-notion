"""
Tests for CLI response formatting.

This module tests the response formatting functions that create
standardized JSON responses for CLI commands.
"""
from __future__ import annotations

import json

from better_notion._cli.response import (
    format_error,
    format_response,
    format_success,
)


def test_format_response_success() -> None:
    """Test formatting a successful response."""
    result = format_response(success=True, data={"id": "page_123", "title": "My Page"})

    response = json.loads(result)

    assert response["success"] is True
    assert response["data"]["id"] == "page_123"
    assert response["data"]["title"] == "My Page"
    assert "meta" in response
    assert "version" in response["meta"]
    assert "timestamp" in response["meta"]
    assert "rate_limit" in response["meta"]


def test_format_response_error() -> None:
    """Test formatting an error response."""
    error_info = {"code": "NOT_FOUND", "message": "Page not found", "retry": False}
    result = format_response(success=False, error=error_info)

    response = json.loads(result)

    assert response["success"] is False
    assert response["error"]["code"] == "NOT_FOUND"
    assert response["error"]["message"] == "Page not found"
    assert response["error"]["retry"] is False
    assert "meta" in response


def test_format_response_with_rate_limit() -> None:
    """Test formatting response with rate limit information."""
    rate_limit = {"remaining": 48, "reset_at": "2025-01-26T10:01:00Z"}
    result = format_response(
        success=True, data={"id": "page_123"}, rate_limit=rate_limit
    )

    response = json.loads(result)

    assert response["meta"]["rate_limit"]["remaining"] == 48
    assert response["meta"]["rate_limit"]["reset_at"] == "2025-01-26T10:01:00Z"


def test_format_response_without_data() -> None:
    """Test formatting success response without data."""
    result = format_response(success=True)

    response = json.loads(result)

    assert response["success"] is True
    assert "data" not in response


def test_format_response_without_error() -> None:
    """Test formatting error response without error info."""
    result = format_response(success=False)

    response = json.loads(result)

    assert response["success"] is False
    assert "error" not in response


def test_format_error_convenience() -> None:
    """Test format_error convenience function."""
    result = format_error("VALIDATION_ERROR", "Invalid input", retry=False)

    response = json.loads(result)

    assert response["success"] is False
    assert response["error"]["code"] == "VALIDATION_ERROR"
    assert response["error"]["message"] == "Invalid input"
    assert response["error"]["retry"] is False


def test_format_error_with_details() -> None:
    """Test format_error with additional details."""
    result = format_error(
        "CONFLICT",
        "Page already exists",
        retry=False,
        details={"existing_page_id": "page_456"},
    )

    response = json.loads(result)

    assert response["error"]["code"] == "CONFLICT"
    assert response["error"]["details"]["existing_page_id"] == "page_456"


def test_format_error_retry_true() -> None:
    """Test format_error with retry=True."""
    result = format_error("RATE_LIMITED", "Rate limit exceeded", retry=True)

    response = json.loads(result)

    assert response["error"]["retry"] is True


def test_format_success_convenience() -> None:
    """Test format_success convenience function."""
    result = format_success({"id": "page_123"})

    response = json.loads(result)

    assert response["success"] is True
    assert response["data"]["id"] == "page_123"


def test_format_success_with_rate_limit() -> None:
    """Test format_success with rate limit information."""
    rate_limit = {"remaining": 50, "reset_at": "2025-01-26T11:00:00Z"}
    result = format_success({"id": "page_123"}, rate_limit=rate_limit)

    response = json.loads(result)

    assert response["meta"]["rate_limit"]["remaining"] == 50


def test_format_response_json_valid() -> None:
    """Test that all format functions return valid JSON."""
    # Test success response
    result1 = format_response(success=True, data={"test": "data"})
    json.loads(result1)  # Should not raise

    # Test error response
    result2 = format_error("TEST_ERROR", "Test message")
    json.loads(result2)  # Should not raise

    # Test success convenience
    result3 = format_success({"test": "data"})
    json.loads(result3)  # Should not raise


def test_format_response_meta_structure() -> None:
    """Test that meta field has correct structure."""
    result = format_response(success=True, data={"test": "data"})

    response = json.loads(result)
    meta = response["meta"]

    assert "version" in meta
    assert isinstance(meta["version"], str)
    assert "timestamp" in meta
    assert isinstance(meta["timestamp"], str)
    assert "rate_limit" in meta
    assert isinstance(meta["rate_limit"], dict)


def test_format_response_empty_rate_limit() -> None:
    """Test that default rate limit is null values."""
    result = format_response(success=True, data={"test": "data"})

    response = json.loads(result)
    rate_limit = response["meta"]["rate_limit"]

    assert rate_limit["remaining"] is None
    assert rate_limit["reset_at"] is None
