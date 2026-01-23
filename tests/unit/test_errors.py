"""Test exception classes."""

from __future__ import annotations

from better_notion._api.errors import (
    BadRequestError,
    ConfigurationError,
    ConflictError,
    ForbiddenError,
    HTTPError,
    InternalServerError,
    NotFoundError,
    NotionAPIError,
    RateLimitedError,
    UnauthorizedError,
)


class TestErrors:
    """Test suite for exception classes."""

    def test_notion_api_error(self):
        """Test base NotionAPIError."""
        error = NotionAPIError("Test error")
        assert str(error) == "Test error"

    def test_http_error(self):
        """Test HTTPError."""
        error = HTTPError("Not found", status_code=404)
        assert error.message == "Not found"
        assert error.status_code == 404

    def test_http_error_without_status_code(self):
        """Test HTTPError without status code."""
        error = HTTPError("Generic error")
        assert error.message == "Generic error"
        assert error.status_code is None

    def test_bad_request_error(self):
        """Test BadRequestError."""
        error = BadRequestError()
        assert error.status_code == 400
        assert str(error) == "Bad request"

    def test_unauthorized_error(self):
        """Test UnauthorizedError."""
        error = UnauthorizedError()
        assert error.status_code == 401
        assert str(error) == "Unauthorized"

    def test_forbidden_error(self):
        """Test ForbiddenError."""
        error = ForbiddenError()
        assert error.status_code == 403
        assert str(error) == "Forbidden"

    def test_not_found_error(self):
        """Test NotFoundError."""
        error = NotFoundError()
        assert error.status_code == 404
        assert str(error) == "Not found"

    def test_conflict_error(self):
        """Test ConflictError."""
        error = ConflictError()
        assert error.status_code == 409
        assert str(error) == "Conflict"

    def test_rate_limited_error(self):
        """Test RateLimitedError."""
        error = RateLimitedError(retry_after=60)
        assert error.status_code == 429
        assert error.retry_after == 60

    def test_rate_limited_error_without_retry_after(self):
        """Test RateLimitedError without retry_after."""
        error = RateLimitedError()
        assert error.status_code == 429
        assert error.retry_after is None

    def test_internal_server_error(self):
        """Test InternalServerError."""
        error = InternalServerError()
        assert error.status_code == 500
        assert str(error) == "Internal server error"

    def test_configuration_error(self):
        """Test ConfigurationError."""
        error = ConfigurationError("Invalid configuration")
        assert str(error) == "Invalid configuration"

    def test_inheritance(self):
        """Test exception inheritance."""
        assert issubclass(BadRequestError, HTTPError)
        assert issubclass(HTTPError, NotionAPIError)
        assert issubclass(ConfigurationError, NotionAPIError)
