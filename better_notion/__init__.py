"""
Better Notion SDK - A high-level Python SDK for the Notion API.

This package provides both low-level and high-level interfaces for
interacting with the Notion API.
"""

__version__ = "0.1.0"

# Low-level API (1:1 mapping with Notion API)
# High-level API (rich abstractions)
from better_notion._api import NotionAPI

# Exceptions
from better_notion._api.errors import (
    BadRequestError,
    ClientError,
    ConfigurationError,
    ConflictError,
    ForbiddenError,
    HTTPError,
    NetworkError,
    NotFoundError,
    NotionAPIError,
    RateLimitedError,
    ServerError,
    UnauthorizedError,
    ValidationError,
)
from better_notion._sdk import NotionClient

__all__ = [
    # Version
    "__version__",
    # Low-level API
    "NotionAPI",
    # High-level API
    "NotionClient",
    # Exceptions
    "NotionAPIError",
    "HTTPError",
    "ClientError",
    "ServerError",
    "BadRequestError",
    "UnauthorizedError",
    "ForbiddenError",
    "NotFoundError",
    "ConflictError",
    "ValidationError",
    "RateLimitedError",
    "NetworkError",
    "ConfigurationError",
]
