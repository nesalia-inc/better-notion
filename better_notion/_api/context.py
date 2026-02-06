"""Request context tracking for correlation and observability."""

from __future__ import annotations

import contextvars
import logging
import time
import uuid
from contextlib import asynccontextmanager
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from better_notion._api import NotionAPI

logger = logging.getLogger(__name__)

# Context variable for async-safe request tracking
_request_context: contextvars.ContextVar["RequestContext | None"] = contextvars.ContextVar(
    "_request_context",
    default=None,
)


class RequestContext:
    """Context for tracking request lifecycle.

    Attributes:
        request_id: Unique identifier for this request.
        operation: Description of the operation (e.g., "POST /pages").
        start_time: Request start timestamp.
        end_time: Request end timestamp.
        notion_request_id: Notion's request ID from response headers.
        metadata: Additional metadata for debugging.
    """

    def __init__(self, operation: str) -> None:
        """Initialize request context.

        Args:
            operation: Description of the operation (e.g., "POST /pages").
        """
        self.request_id = uuid.uuid4().hex[:8]
        self.operation = operation
        self.start_time: float | None = None
        self.end_time: float | None = None
        self.notion_request_id: str | None = None
        self.metadata: dict[str, Any] = {}

    def start(self) -> None:
        """Mark the start of the request."""
        self.start_time = time.time()

    def complete(self) -> None:
        """Mark the completion of the request."""
        self.end_time = time.time()

    def duration(self) -> float:
        """Get the request duration in seconds.

        Returns:
            Request duration in seconds, or 0.0 if timing incomplete.
        """
        if self.start_time and self.end_time:
            return self.end_time - self.start_time
        return 0.0

    def to_dict(self) -> dict[str, Any]:
        """Convert context to dictionary for logging.

        Returns:
            Dictionary representation of the request context.
        """
        return {
            "request_id": self.request_id,
            "operation": self.operation,
            "notion_request_id": self.notion_request_id,
            "duration": self.duration(),
            "metadata": self.metadata,
        }


def get_current_request_context() -> RequestContext | None:
    """Get the current request context (async-safe).

    Returns:
        The current RequestContext or None if not in a request context.
    """
    return _request_context.get()


def set_current_request_context(context: RequestContext) -> Any:
    """Set the current request context (async-safe).

    Args:
        context: The RequestContext to set as current.

    Returns:
        Token to reset the context later.
    """
    return _request_context.set(context)


def clear_current_request_context(token: Any) -> None:
    """Clear the current request context (async-safe).

    Args:
        token: Token returned by set_current_request_context().
    """
    _request_context.reset(token)


@asynccontextmanager
async def request_context(api: "NotionAPI", operation: str):
    """Track request context for better error messages and logging.

    This context manager automatically:
    - Generates a unique request ID
    - Tracks request timing
    - Captures Notion's request ID from response
    - Adds context to exceptions
    - Logs request lifecycle events

    Args:
        api: The NotionAPI instance.
        operation: Description of the operation (e.g., "POST /pages").

    Yields:
        RequestContext: The request context object.

    Example:
        >>> async with request_context(api, "POST /pages") as ctx:
        ...     result = await api._request("POST", "/pages", json={...})
        ...     print(f"Duration: {ctx.duration()}s")

    Note:
        Request context is stored in async context variables, so it's
        automatically available to all async code called within the context.
    """
    context = RequestContext(operation)
    context.start()

    # Set context for this async task
    token = set_current_request_context(context)

    # Log request start
    logger.info(f"Request {context.request_id} started: {operation}")

    try:
        yield context
        context.complete()

        # Log request completion
        duration = context.duration()
        logger.info(
            f"Request {context.request_id} completed in {duration:.3f}s: {operation}"
        )

    except Exception as e:
        context.complete()

        # Add context to exception
        if hasattr(e, "add_note"):
            import json

            e.add_note(f"Request ID: {context.request_id}")
            e.add_note(f"Operation: {operation}")
            e.add_note(f"Duration: {context.duration():.3f}s")

            if context.notion_request_id:
                e.add_note(f"Notion Request ID: {context.notion_request_id}")

            if context.metadata:
                try:
                    metadata_str = json.dumps(context.metadata, indent=2)
                    e.add_note(f"Context: {metadata_str}")
                except Exception:
                    e.add_note(f"Context: {context.metadata}")

        # Log request failure
        duration = context.duration()
        logger.error(
            f"Request {context.request_id} failed after {duration:.3f}s: {operation}",
            exc_info=e,
        )

        raise

    finally:
        # Clear context from async task
        clear_current_request_context(token)
