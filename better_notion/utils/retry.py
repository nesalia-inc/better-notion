"""Retry logic with exponential backoff for API requests."""

from __future__ import annotations

import asyncio
import inspect
import time
from typing import Any, Callable, TypeVar

from better_notion._api.errors import NotionAPIError


T = TypeVar("T")


class RetryConfig:
    """Configuration for retry behavior."""

    def __init__(
        self,
        *,
        max_retries: int = 3,
        initial_delay: float = 1.0,
        max_delay: float = 60.0,
        exponential_base: float = 2.0,
        jitter: bool = True
    ) -> None:
        """Initialize retry configuration.

        Args:
            max_retries: Maximum number of retry attempts
            initial_delay: Initial delay in seconds before first retry
            max_delay: Maximum delay between retries
            exponential_base: Base for exponential backoff
            jitter: Whether to add random jitter to delays

        Example:
            >>> config = RetryConfig(max_retries=5, initial_delay=0.5)
        """
        self.max_retries = max_retries
        self.initial_delay = initial_delay
        self.max_delay = max_delay
        self.exponential_base = exponential_base
        self.jitter = jitter

    def get_delay(self, attempt: int) -> float:
        """Calculate delay for given attempt number.

        Args:
            attempt: Attempt number (0-based)

        Returns:
            Delay in seconds

        Example:
            >>> config = RetryConfig()
            >>> config.get_delay(0)  # First retry
            1.0
            >>> config.get_delay(1)  # Second retry
            2.0
            >>> config.get_delay(2)  # Third retry
            4.0
        """
        # Calculate exponential delay
        delay = self.initial_delay * (self.exponential_base ** attempt)

        # Cap at max_delay
        delay = min(delay, self.max_delay)

        # Add jitter if enabled
        if self.jitter:
            import random
            delay = delay * (0.5 + random.random() * 0.5)

        return delay


class RetryHandler:
    """Handle retries with exponential backoff.

    Example:
        >>> handler = RetryHandler()
        >>> result = await handler.retry(
        ...     lambda: api_call(),
        ...     retry_config=RetryConfig(max_retries=3)
        ... )
    """

    def __init__(self, default_config: RetryConfig | None = None) -> None:
        """Initialize retry handler.

        Args:
            default_config: Default retry configuration
        """
        self._default_config = default_config or RetryConfig()

    async def retry(
        self,
        func: Callable[..., T],
        *,
        config: RetryConfig | None = None,
        on_retry: Callable[[Exception, int], None] | None = None
    ) -> T:
        """Execute function with retry logic.

        Args:
            func: Async function to execute
            config: Retry configuration (uses default if None)
            on_retry: Optional callback called on each retry

        Returns:
            Function result

        Raises:
            Last exception if all retries exhausted

        Example:
            >>> async def api_call():
            ...     return await client.api.pages.retrieve(page_id="...")
            >>>
            >>> handler = RetryHandler()
            >>> result = await handler.retry(api_call)
        """
        config = config or self._default_config
        last_exception = None

        for attempt in range(config.max_retries + 1):
            try:
                # Try to execute the function
                if inspect.iscoroutinefunction(func):
                    return await func()
                else:
                    return func()  # type: ignore

            except Exception as e:
                last_exception = e

                # Check if we should retry this error
                if not self._should_retry(e, attempt, config):
                    raise

                # Calculate delay and wait
                delay = config.get_delay(attempt)
                if on_retry:
                    on_retry(e, attempt + 1)

                await asyncio.sleep(delay)

        # All retries exhausted
        if last_exception:
            raise last_exception

        # Should never reach here
        raise RuntimeError("Retry logic failed")

    def _should_retry(
        self,
        exception: Exception,
        attempt: int,
        config: RetryConfig
    ) -> bool:
        """Determine if exception should be retried.

        Args:
            exception: The exception that occurred
            attempt: Current attempt number (0-based)
            config: Retry configuration

        Returns:
            True if should retry

        Example:
            >>> handler = RetryHandler()
            >>> handler._should_retry(
            ...     NotionAPIError(429, \"rate_limited\", {}),
            ...     0,
            ...     RetryConfig()
            ... )
            True
        """
        # Don't retry if we've exhausted attempts
        if attempt >= config.max_retries:
            return False

        # Retry on rate limiting (429)
        if isinstance(exception, NotionAPIError):
            if exception.status_code == 429:  # Rate limited
                return True
            if exception.status_code and exception.status_code >= 500:  # Server errors
                return True
            if exception.status_code == 408:  # Request timeout
                return True

        # Retry on connection errors
        if isinstance(exception, (ConnectionError, OSError)):
            return True

        # Don't retry on client errors (4xx except 429, 408)
        if isinstance(exception, NotionAPIError):
            if exception.status_code and 400 <= exception.status_code < 500 and exception.status_code not in (408, 429):
                return False

        # Default: don't retry
        return False


def retry(
    *,
    max_retries: int = 3,
    initial_delay: float = 1.0,
    max_delay: float = 60.0,
    exponential_base: float = 2.0,
    jitter: bool = True
) -> Callable:
        """Decorator for adding retry logic to async functions.

        Args:
            max_retries: Maximum number of retry attempts
            initial_delay: Initial delay before first retry
            max_delay: Maximum delay between retries
            exponential_base: Base for exponential backoff
            jitter: Whether to add random jitter

        Example:
            >>> @retry(max_retries=5)
            >>> async def my_api_call():
            ...     return await client.api.pages.retrieve(page_id="...")
        """
        config = RetryConfig(
            max_retries=max_retries,
            initial_delay=initial_delay,
            max_delay=max_delay,
            exponential_base=exponential_base,
            jitter=jitter
        )
        handler = RetryHandler(config)

        def decorator(func: Callable) -> Callable:
            async def wrapper(*args: Any, **kwargs: Any) -> Any:
                async def _func() -> Any:
                    return await func(*args, **kwargs)

                return await handler.retry(_func)

            return wrapper

        return decorator
