"""Exception classes for Better Notion SDK."""

from __future__ import annotations


class NotionAPIError(Exception):
    """Base exception for all Notion API errors.

    Attributes:
        message: Error message.
        status_code: HTTP status code (optional).
        code: Error code from API (optional).
        info: Additional error info (optional).
    """

    def __init__(
        self,
        message: str | int,
        code: str | None = None,
        info: dict | None = None
    ) -> None:
        """Initialize Notion API error.

        Args:
            message: Error message (or status code if using 3-param form)
            code: Error code (optional, or message if using 3-param form)
            info: Additional error info (optional, only used in 3-param form)

        Supports two calling conventions:
            1. NotionAPIError("message") - simple message
            2. NotionAPIError(status_code, code, info) - with status info
        """
        # Support 3-parameter form: NotionAPIError(status_code, code, info)
        if isinstance(message, int):
            self.status_code = message
            self.code = code or ""
            self.info = info or {}
            self.message = f"{self.code}: {self.status_code}"
            super().__init__(self.message)
        else:
            # Support 1-parameter form: NotionAPIError("message")
            self.message = message
            self.status_code = None
            self.code = None
            self.info = info or {}
            super().__init__(message)


class HTTPError(NotionAPIError):
    """Base class for HTTP-related errors.

    Attributes:
        message: Error message.
        status_code: HTTP status code.
    """

    def __init__(self, message: str, status_code: int | None = None) -> None:
        """Initialize HTTP error.

        Args:
            message: Error message.
            status_code: HTTP status code.
        """
        super().__init__(message)
        self.message = message
        self.status_code = status_code


class ClientError(HTTPError):
    """Base class for 4xx client errors."""


class ServerError(HTTPError):
    """Base class for 5xx server errors."""


# 4xx Errors


class BadRequestError(ClientError):
    """400 Bad Request - Invalid request."""

    def __init__(self, message: str = "Bad request") -> None:
        super().__init__(message, status_code=400)


class UnauthorizedError(ClientError):
    """401 Unauthorized - Invalid or missing credentials."""

    def __init__(self, message: str = "Unauthorized") -> None:
        super().__init__(message, status_code=401)


class ForbiddenError(ClientError):
    """403 Forbidden - Insufficient permissions."""

    def __init__(self, message: str = "Forbidden") -> None:
        super().__init__(message, status_code=403)


class NotFoundError(ClientError):
    """404 Not Found - Resource not found."""

    def __init__(self, message: str = "Not found") -> None:
        super().__init__(message, status_code=404)


class ConflictError(ClientError):
    """409 Conflict - Request conflicts with current state."""

    def __init__(self, message: str = "Conflict") -> None:
        super().__init__(message, status_code=409)


class ValidationError(ClientError):
    """422 Validation Error - Invalid data."""

    def __init__(self, message: str = "Validation error") -> None:
        super().__init__(message, status_code=422)


class RateLimitedError(ClientError):
    """429 Rate Limited - Too many requests.

    Attributes:
        retry_after: Seconds to wait before retrying.
    """

    def __init__(
        self,
        message: str = "Rate limited",
        retry_after: int | None = None,
    ) -> None:
        super().__init__(message, status_code=429)
        self.retry_after = retry_after


# 5xx Errors


class InternalServerError(ServerError):
    """500 Internal Server Error."""

    def __init__(self, message: str = "Internal server error") -> None:
        super().__init__(message, status_code=500)


class BadGatewayError(ServerError):
    """502 Bad Gateway."""

    def __init__(self, message: str = "Bad gateway") -> None:
        super().__init__(message, status_code=502)


class ServiceUnavailableError(ServerError):
    """503 Service Unavailable."""

    def __init__(self, message: str = "Service unavailable") -> None:
        super().__init__(message, status_code=503)


# Other Errors


class NetworkError(NotionAPIError):
    """Network-related error (connection timeout, DNS failure, etc.)."""


class ConfigurationError(NotionAPIError):
    """Configuration or setup error."""
