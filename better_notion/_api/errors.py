"""Exception classes for Better Notion SDK."""

from __future__ import annotations

from typing import Any


class NotionAPIError(Exception):
    """Base exception for all Notion API errors.

    Attributes:
        message: Error message.
        status_code: HTTP status code (optional).
        code: Error code from API (optional).
        info: Additional error info (optional).
        request_id: Request ID for correlation (optional).
        notion_code: Notion's error code (optional).
        request_method: HTTP method of the request (optional).
        request_path: Request path (optional).
        response_body: Response body (optional).
    """

    def __init__(
        self,
        message: str | int,
        code: str | None = None,
        info: dict | None = None,
        *,
        request_id: str | None = None,
        notion_code: str | None = None,
        request_method: str | None = None,
        request_path: str | None = None,
        response_body: dict | None = None,
    ) -> None:
        """Initialize Notion API error.

        Args:
            message: Error message (or status code if using 3-param form).
            code: Error code (optional, or message if using 3-param form).
            info: Additional error info (optional, only used in 3-param form).
            request_id: Request ID for correlation.
            notion_code: Notion's error code.
            request_method: HTTP method of the request.
            request_path: Request path.
            response_body: Response body.

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

        # Rich context attributes
        self.request_id = request_id
        self.notion_code = notion_code
        self.request_method = request_method
        self.request_path = request_path
        self.response_body = response_body or {}

    def get_user_friendly_message(self) -> str:
        """Generate a clear error message for users.

        Returns:
            A formatted error message with context.
        """
        if self.notion_code:
            return f"{self.notion_code}: {super().__str__()}"
        return super().__str__()

    def to_dict(self) -> dict[str, Any]:
        """Serialize error for logging/monitoring.

        Returns:
            Dictionary representation of the error.
        """
        return {
            "type": type(self).__name__,
            "message": self.message,
            "request_id": self.request_id,
            "status_code": self.status_code,
            "notion_code": self.notion_code,
            "request": f"{self.request_method} {self.request_path}" if self.request_method else None,
        }

    def get_context_summary(self) -> str:
        """Get a summary of the error context.

        Returns:
            A string summarizing the error context.
        """
        parts = []
        if self.request_id:
            parts.append(f"Request ID: {self.request_id}")
        if self.notion_code:
            parts.append(f"Notion Code: {self.notion_code}")
        if self.request_method and self.request_path:
            parts.append(f"Operation: {self.request_method} {self.request_path}")
        if self.status_code is not None:
            parts.append(f"Status Code: {self.status_code}")

        return " | ".join(parts) if parts else "No context"


class HTTPError(NotionAPIError):
    """Base class for HTTP-related errors.

    Attributes:
        message: Error message.
        status_code: HTTP status code.
    """

    def __init__(
        self,
        message: str,
        status_code: int | None = None,
        **kwargs: Any,
    ) -> None:
        """Initialize HTTP error.

        Args:
            message: Error message.
            status_code: HTTP status code.
            **kwargs: Additional context passed to NotionAPIError.
        """
        super().__init__(message, **kwargs)
        self.message = message
        self.status_code = status_code


class ClientError(HTTPError):
    """Base class for 4xx client errors."""


class ServerError(HTTPError):
    """Base class for 5xx server errors."""


# 4xx Errors


class BadRequestError(ClientError):
    """400 Bad Request - Invalid request."""

    def __init__(self, message: str = "Bad request", **kwargs: Any) -> None:
        super().__init__(message, status_code=400, **kwargs)


class UnauthorizedError(ClientError):
    """401 Unauthorized - Invalid or missing credentials."""

    def __init__(self, message: str = "Unauthorized", **kwargs: Any) -> None:
        super().__init__(message, status_code=401, **kwargs)


class ForbiddenError(ClientError):
    """403 Forbidden - Insufficient permissions."""

    def __init__(self, message: str = "Forbidden", **kwargs: Any) -> None:
        super().__init__(message, status_code=403, **kwargs)


class NotFoundError(ClientError):
    """404 Not Found - Resource not found."""

    def __init__(self, message: str = "Not found", **kwargs: Any) -> None:
        super().__init__(message, status_code=404, **kwargs)


class ConflictError(ClientError):
    """409 Conflict - Request conflicts with current state."""

    def __init__(self, message: str = "Conflict", **kwargs: Any) -> None:
        super().__init__(message, status_code=409, **kwargs)


class ValidationError(ClientError):
    """422 Validation Error - Invalid data."""

    def __init__(self, message: str = "Validation error", **kwargs: Any) -> None:
        super().__init__(message, status_code=422, **kwargs)


class RateLimitedError(ClientError):
    """429 Rate Limited - Too many requests.

    Attributes:
        retry_after: Seconds to wait before retrying.
    """

    def __init__(
        self,
        message: str = "Rate limited",
        retry_after: int | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(message, status_code=429, **kwargs)
        self.retry_after = retry_after


# 5xx Errors


class InternalServerError(ServerError):
    """500 Internal Server Error."""

    def __init__(self, message: str = "Internal server error", **kwargs: Any) -> None:
        super().__init__(message, status_code=500, **kwargs)


class BadGatewayError(ServerError):
    """502 Bad Gateway."""

    def __init__(self, message: str = "Bad gateway", **kwargs: Any) -> None:
        super().__init__(message, status_code=502, **kwargs)


class ServiceUnavailableError(ServerError):
    """503 Service Unavailable."""

    def __init__(self, message: str = "Service unavailable", **kwargs: Any) -> None:
        super().__init__(message, status_code=503, **kwargs)


# Other Errors


class NetworkError(NotionAPIError):
    """Network-related error (connection timeout, DNS failure, etc.)."""


class ConfigurationError(NotionAPIError):
    """Configuration or setup error."""
