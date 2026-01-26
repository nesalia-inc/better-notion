"""
Response formatting for Better Notion CLI.

This module handles formatting CLI responses in JSON format for
programmatic parsing by AI agents.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any


def format_response(
    *,
    success: bool,
    data: Any = None,
    error: dict[str, Any] | None = None,
    rate_limit: dict[str, Any] | None = None,
) -> str:
    """
    Format CLI response as JSON.

    This function creates a standardized JSON response format for all CLI
    commands, making it easy for agents to parse and handle responses.

    Args:
        success: Whether the operation succeeded
        data: Response data (for successful operations)
        error: Error information (for failed operations)
        rate_limit: Rate limit information from API response

    Returns:
        JSON-formatted response string

    Examples:
        Successful response:
        >>> format_response(success=True, data={"id": "page_123"})
        {
          "success": true,
          "data": {"id": "page_123"},
          "meta": {
            "version": "0.4.0",
            "timestamp": "2025-01-26T10:00:00Z",
            "rate_limit": {"remaining": null, "reset_at": null}
          }
        }

        Error response:
        >>> format_response(
        ...     success=False,
        ...     error={"code": "NOT_FOUND", "message": "Page not found", "retry": False}
        ... )
        {
          "success": false,
          "error": {"code": "NOT_FOUND", "message": "Page not found", "retry": false},
          "meta": {
            "version": "0.4.0",
            "timestamp": "2025-01-26T10:00:00Z",
            "rate_limit": {"remaining": null, "reset_at": null}
          }
        }
    """
    response: dict[str, Any] = {
        "success": success,
        "meta": {
            "version": "0.5.0",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "rate_limit": rate_limit or {"remaining": None, "reset_at": None},
        },
    }

    if success:
        if data is not None:
            response["data"] = data
    else:
        if error is not None:
            response["error"] = error

    return json.dumps(response, indent=2)


def format_error(
    code: str,
    message: str,
    *,
    retry: bool = False,
    details: dict[str, Any] | None = None,
) -> str:
    """
    Format an error response.

    This is a convenience function for formatting error responses.

    Args:
        code: Machine-readable error code
        message: Human-readable error message
        retry: Whether the operation should be retried
        details: Additional error details

    Returns:
        JSON-formatted error response string

    Examples:
        >>> format_error("NOT_FOUND", "Page not found", retry=False)
        {
          "success": false,
          "error": {
            "code": "NOT_FOUND",
            "message": "Page not found",
            "retry": false
          },
          "meta": {...}
        }
    """
    error_info: dict[str, Any] = {
        "code": code,
        "message": message,
        "retry": retry,
    }

    if details:
        error_info["details"] = details

    return format_response(success=False, error=error_info)


def format_success(data: Any, *, rate_limit: dict[str, Any] | None = None) -> str:
    """
    Format a success response.

    This is a convenience function for formatting success responses.

    Args:
        data: Response data
        rate_limit: Rate limit information from API response

    Returns:
        JSON-formatted success response string

    Examples:
        >>> format_success({"id": "page_123", "title": "My Page"})
        {
          "success": true,
          "data": {"id": "page_123", "title": "My Page"},
          "meta": {...}
        }
    """
    return format_response(success=True, data=data, rate_limit=rate_limit)
