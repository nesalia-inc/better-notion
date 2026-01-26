"""
Error codes and exception mapping for Better Notion CLI.

This module defines error codes and exit codes used throughout the CLI,
and provides functions to map exceptions to error responses.
"""
from __future__ import annotations

from enum import Enum, IntEnum
from typing import Any


class ExitCode(IntEnum):
    """
    CLI exit codes for agents.

    Agents rely on exit codes to determine command success or failure.
    These codes follow standard conventions.

    Attributes:
        SUCCESS: Command executed successfully
        GENERIC_ERROR: Generic error (retry if idempotent)
        INVALID_INPUT: Invalid input (don't retry - won't work)
        AUTH_ERROR: Authentication error (re-auth needed)
        RATE_LIMIT: Rate limit error (backoff + retry)
        NOT_FOUND: Resource not found (skip + log)
        CONFLICT: Conflict error (retry with different data)
    """

    SUCCESS = 0
    GENERIC_ERROR = 1
    INVALID_INPUT = 2
    AUTH_ERROR = 3
    RATE_LIMIT = 4
    NOT_FOUND = 5
    CONFLICT = 6


class ErrorCode(str, Enum):
    """
    Machine-readable error codes.

    These codes are used in JSON error responses and allow agents to
    programmatically determine what went wrong.

    Values:
        VALIDATION_ERROR: Input validation failed
        NOT_FOUND: Resource not found
        UNAUTHORIZED: Authentication failed
        FORBIDDEN: Permission denied
        RATE_LIMITED: Rate limit exceeded
        CONFLICT: Resource conflict (duplicate, etc.)
        INTERNAL_ERROR: Unexpected internal error
        NETWORK_ERROR: Network connectivity issue
        TIMEOUT: Request timed out
    """

    VALIDATION_ERROR = "VALIDATION_ERROR"
    NOT_FOUND = "NOT_FOUND"
    UNAUTHORIZED = "UNAUTHORIZED"
    FORBIDDEN = "FORBIDDEN"
    RATE_LIMITED = "RATE_LIMITED"
    CONFLICT = "CONFLICT"
    INTERNAL_ERROR = "INTERNAL_ERROR"
    NETWORK_ERROR = "NETWORK_ERROR"
    TIMEOUT = "TIMEOUT"


def map_exception_to_error(exception: Exception) -> tuple[ExitCode, dict[str, Any]]:
    """
    Map exceptions to CLI error responses.

    This function converts various exception types into standardized
    error codes and messages for CLI responses.

    Args:
        exception: The exception to map

    Returns:
        Tuple of (exit_code, error_dict) where error_dict contains:
        - code: Machine-readable error code (ErrorCode)
        - message: Human-readable error message
        - retry: Whether the operation should be retried
        - details: Optional additional error details

    Examples:
        >>> try:
        ...     raise ValueError("Invalid page ID")
        ... except Exception as e:
        ...     exit_code, error = map_exception_to_error(e)
        >>> exit_code
        2
        >>> error["code"]
        'VALIDATION_ERROR'

    Note:
        This is a placeholder implementation. The full implementation
        should map specific Notion SDK exceptions to appropriate
        error codes based on the SDK's exception hierarchy.
    """
    # Import SDK exceptions if available
    # For now, handle common Python exceptions
    if isinstance(exception, ValueError):
        return (
            ExitCode.INVALID_INPUT,
            {
                "code": ErrorCode.VALIDATION_ERROR,
                "message": str(exception) or "Invalid input provided",
                "retry": False,
            },
        )

    if isinstance(exception, (KeyError, AttributeError)):
        return (
            ExitCode.NOT_FOUND,
            {
                "code": ErrorCode.NOT_FOUND,
                "message": str(exception) or "Resource not found",
                "retry": False,
            },
        )

    if isinstance(exception, PermissionError):
        return (
            ExitCode.AUTH_ERROR,
            {
                "code": ErrorCode.FORBIDDEN,
                "message": str(exception) or "Permission denied",
                "retry": False,
            },
        )

    # Check for timeout-related exceptions
    exception_type = type(exception).__name__
    if "timeout" in exception_type.lower() or "timed out" in str(exception).lower():
        return (
            ExitCode.GENERIC_ERROR,
            {
                "code": ErrorCode.TIMEOUT,
                "message": str(exception) or "Request timed out",
                "retry": True,
                "details": {"suggestion": "Consider increasing timeout with --timeout flag"},
            },
        )

    # Check for network-related exceptions
    if "connection" in exception_type.lower() or "network" in str(exception).lower():
        return (
            ExitCode.GENERIC_ERROR,
            {
                "code": ErrorCode.NETWORK_ERROR,
                "message": str(exception) or "Network connectivity issue",
                "retry": True,
                "details": {"suggestion": "Check your internet connection"},
            },
        )

    # Default: generic error
    return (
        ExitCode.GENERIC_ERROR,
        {
            "code": ErrorCode.INTERNAL_ERROR,
            "message": str(exception) or "An unexpected error occurred",
            "retry": False,
        },
    )
