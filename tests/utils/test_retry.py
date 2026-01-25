"""Tests for retry logic with exponential backoff."""

import asyncio
import pytest

from better_notion._api.errors import NotionAPIError
from better_notion.utils.retry import RetryConfig, RetryHandler, retry


class TestRetryConfig:
    """Tests for RetryConfig."""

    def test_default_initialization(self):
        """Test default configuration."""
        config = RetryConfig()

        assert config.max_retries == 3
        assert config.initial_delay == 1.0
        assert config.max_delay == 60.0
        assert config.exponential_base == 2.0
        assert config.jitter is True

    def test_custom_initialization(self):
        """Test custom configuration."""
        config = RetryConfig(
            max_retries=5,
            initial_delay=0.5,
            max_delay=30.0,
            exponential_base=3.0,
            jitter=False
        )

        assert config.max_retries == 5
        assert config.initial_delay == 0.5
        assert config.max_delay == 30.0
        assert config.exponential_base == 3.0
        assert config.jitter is False

    def test_get_delay_exponential(self):
        """Test exponential delay calculation."""
        config = RetryConfig(
            initial_delay=1.0,
            exponential_base=2.0,
            jitter=False
        )

        assert config.get_delay(0) == 1.0
        assert config.get_delay(1) == 2.0
        assert config.get_delay(2) == 4.0
        assert config.get_delay(3) == 8.0

    def test_get_delay_max_cap(self):
        """Test delay capping at max_delay."""
        config = RetryConfig(
            initial_delay=10.0,
            max_delay=15.0,
            exponential_base=2.0,
            jitter=False
        )

        assert config.get_delay(0) == 10.0
        assert config.get_delay(1) == 15.0  # Capped
        assert config.get_delay(2) == 15.0  # Capped

    def test_get_delay_with_jitter(self):
        """Test jitter adds randomness."""
        config = RetryConfig(
            initial_delay=1.0,
            jitter=True
        )

        delays = [config.get_delay(0) for _ in range(10)]

        # All delays should be between 0.5 and 1.5
        for delay in delays:
            assert 0.5 <= delay <= 1.5


class TestRetryHandler:
    """Tests for RetryHandler."""

    @pytest.mark.asyncio
    async def test_retry_on_success(self):
        """Test retry returns immediately on success."""
        handler = RetryHandler()

        async def success_func():
            return "success"

        result = await handler.retry(success_func)

        assert result == "success"

    @pytest.mark.asyncio
    async def test_retry_no_retry_on_404(self):
        """Test 404 errors are not retried."""
        handler = RetryHandler()

        async def not_found_func():
            raise NotionAPIError(404, "object_not_found", {})

        with pytest.raises(NotionAPIError) as exc_info:
            await handler.retry(not_found_func)

        assert exc_info.value.status_code == 404

    @pytest.mark.asyncio
    async def test_retry_on_429_rate_limit(self):
        """Test retry on 429 rate limit."""
        handler = RetryHandler(
            default_config=RetryConfig(
                max_retries=3,
                initial_delay=0.01,
                jitter=False
            )
        )

        attempts = []

        async def rate_limited_func():
            attempts.append(1)
            if len(attempts) < 2:
                raise NotionAPIError(429, "rate_limited", {})
            return "success"

        result = await handler.retry(rate_limited_func)

        assert result == "success"
        assert len(attempts) == 2

    @pytest.mark.asyncio
    async def test_retry_on_500_server_error(self):
        """Test retry on 500 server error."""
        handler = RetryHandler(
            default_config=RetryConfig(
                max_retries=2,
                initial_delay=0.01,
                jitter=False
            )
        )

        attempts = []

        async def server_error_func():
            attempts.append(1)
            if len(attempts) < 2:
                raise NotionAPIError(500, "internal_server_error", {})
            return "success"

        result = await handler.retry(server_error_func)

        assert result == "success"
        assert len(attempts) == 2

    @pytest.mark.asyncio
    async def test_retry_exhausted_raises_last_error(self):
        """Test that exhausting retries raises last error."""
        handler = RetryHandler(
            default_config=RetryConfig(
                max_retries=2,
                initial_delay=0.01,
                jitter=False
            )
        )

        async def always_fail_func():
            raise NotionAPIError(500, "server_error", {})

        with pytest.raises(NotionAPIError) as exc_info:
            await handler.retry(always_fail_func)

        assert exc_info.value.status_code == 500

    @pytest.mark.asyncio
    async def test_retry_with_callback(self):
        """Test retry with on_retry callback."""
        handler = RetryHandler(
            default_config=RetryConfig(
                max_retries=2,
                initial_delay=0.01,
                jitter=False
            )
        )

        callback_calls = []

        def on_retry(exception: Exception, attempt: int) -> None:
            callback_calls.append(attempt)

        attempts = []

        async def sometimes_fail_func():
            attempts.append(1)
            if len(attempts) < 2:
                raise NotionAPIError(500, "server_error", {})
            return "success"

        result = await handler.retry(
            sometimes_fail_func,
            on_retry=on_retry
        )

        assert result == "success"
        assert len(callback_calls) == 1
        assert callback_calls[0] == 1  # First retry


class TestRetryDecorator:
    """Tests for @retry decorator."""

    @pytest.mark.asyncio
    async def test_retry_decorator_success(self):
        """Test decorator doesn't affect successful calls."""

        @retry(max_retries=3, initial_delay=0.01)
        async def my_function():
            return "result"

        result = await my_function()

        assert result == "result"

    @pytest.mark.asyncio
    async def test_retry_decorator_retries_on_error(self):
        """Test decorator retries on retriable errors."""

        @retry(max_retries=3, initial_delay=0.01)
        async def failing_function():
            nonlocal attempt
            attempt += 1
            if attempt < 2:
                raise NotionAPIError(429, "rate_limited", {})
            return "success"

        attempt = 0
        result = await failing_function()

        assert result == "success"
        assert attempt == 2

    @pytest.mark.asyncio
    async def test_retry_decorator_raises_on_non_retriable(self):
        """Test decorator doesn't retry on non-retriable errors."""

        @retry(max_retries=3)
        async def not_found_function():
            raise NotionAPIError(404, "not_found", {})

        with pytest.raises(NotionAPIError) as exc_info:
            await not_found_function()

        assert exc_info.value.status_code == 404
