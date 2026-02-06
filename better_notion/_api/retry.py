"""Retry decorator with exponential backoff for handling rate limiting."""

from __future__ import annotations

import asyncio
import logging
import random
from functools import wraps
from typing import Any, Callable, ParamSpec, TypeVar

from better_notion._api.errors import RateLimitedError

logger = logging.getLogger(__name__)

P = ParamSpec("P")
T = TypeVar("T")


def retry_on_rate_limit(
    max_retries: int = 3,
    initial_backoff: float = 1.0,
    max_backoff: float = 60.0,
    jitter: bool = True,
) -> Callable[[Callable[P, T]], Callable[P, T]]:
    """Decorator to retry async functions on rate limiting with exponential backoff.

    This decorator automatically retries async functions when they encounter
    RateLimitedError (HTTP 429) from the Notion API. It uses exponential backoff
    with optional jitter to prevent synchronized retry storms.

    Args:
        max_retries: Maximum number of retry attempts (default: 3).
        initial_backoff: Initial backoff duration in seconds (default: 1.0).
        max_backoff: Maximum backoff duration in seconds (default: 60.0).
        jitter: Add random jitter to prevent synchronized retries (default: True).

    Returns:
        Decorator function that can be applied to async functions.

    The backoff follows an exponential pattern: initial_backoff * 2^attempt.
    With jitter, the actual backoff is: backoff * (0.5 + random()).

    Example:
        @retry_on_rate_limit(max_retries=5)
        async def create_page(api, page_data):
            return await api.pages.create(**page_data)

        # Will automatically retry up to 5 times if rate limited
        await create_page(api, page_data)

    Note:
        - Only retries on RateLimitedError, other exceptions propagate immediately.
        - Retry-After header from Notion is respected but overridden by backoff.
        - Each retry adds context notes to the exception for debugging.
    """
    def decorator(func: Callable[P, T]) -> Callable[P, T]:
        @wraps(func)
        async def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
            for attempt in range(max_retries):
                try:
                    return await func(*args, **kwargs)

                except RateLimitedError as e:
                    if attempt == max_retries - 1:
                        # Last attempt - add note and re-raise
                        e.add_note(f"Max retries ({max_retries}) exceeded")
                        logger.error(
                            f"Rate limited: max retries ({max_retries}) exceeded"
                        )
                        raise

                    # Extract retry_after from RateLimitedError
                    retry_after = e.retry_after or 5

                    # Calculate exponential backoff
                    backoff = min(
                        initial_backoff * (2 ** attempt),
                        max_backoff
                    )

                    # Add jitter to prevent synchronized retries
                    if jitter:
                        backoff *= (0.5 + random.random())

                    # Add retry context to exception
                    e.add_note(
                        f"Retry {attempt + 1}/{max_retries} after {backoff:.1f}s wait "
                        f"(Retry-After: {retry_after}s, backoff: {backoff:.1f}s)"
                    )

                    logger.warning(
                        f"Rate limited: retrying in {backoff:.1f}s "
                        f"(attempt {attempt + 1}/{max_retries})"
                    )

                    # Wait before retrying
                    await asyncio.sleep(backoff)

            # Should never reach here
            raise RuntimeError("Retry loop completed unexpectedly")

        return wrapper
    return decorator


def retry_on_rate_limit_sync(
    max_retries: int = 3,
    initial_backoff: float = 1.0,
    max_backoff: float = 60.0,
    jitter: bool = True,
) -> Callable[[Callable[P, T]], Callable[P, T]]:
    """Decorator to retry synchronous functions on rate limiting with exponential backoff.

    This is the synchronous version of retry_on_rate_limit for use with
    synchronous functions. See retry_on_rate_limit for full documentation.

    Args:
        max_retries: Maximum number of retry attempts (default: 3).
        initial_backoff: Initial backoff duration in seconds (default: 1.0).
        max_backoff: Maximum backoff duration in seconds (default: 60.0).
        jitter: Add random jitter to prevent synchronized retries (default: True).

    Returns:
        Decorator function that can be applied to synchronous functions.
    """
    def decorator(func: Callable[P, T]) -> Callable[P, T]:
        @wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
            import time

            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)

                except RateLimitedError as e:
                    if attempt == max_retries - 1:
                        # Last attempt - add note and re-raise
                        e.add_note(f"Max retries ({max_retries}) exceeded")
                        logger.error(
                            f"Rate limited: max retries ({max_retries}) exceeded"
                        )
                        raise

                    # Extract retry_after from RateLimitedError
                    retry_after = e.retry_after or 5

                    # Calculate exponential backoff
                    backoff = min(
                        initial_backoff * (2 ** attempt),
                        max_backoff
                    )

                    # Add jitter to prevent synchronized retries
                    if jitter:
                        backoff *= (0.5 + random.random())

                    # Add retry context to exception
                    e.add_note(
                        f"Retry {attempt + 1}/{max_retries} after {backoff:.1f}s wait "
                        f"(Retry-After: {retry_after}s, backoff: {backoff:.1f}s)"
                    )

                    logger.warning(
                        f"Rate limited: retrying in {backoff:.1f}s "
                        f"(attempt {attempt + 1}/{max_retries})"
                    )

                    # Wait before retrying
                    time.sleep(backoff)

            # Should never reach here
            raise RuntimeError("Retry loop completed unexpectedly")

        return wrapper
    return decorator
