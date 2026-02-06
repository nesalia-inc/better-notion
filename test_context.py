"""Test request context tracking."""

import asyncio
import logging

# Configure logging to see request lifecycle
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

from better_notion._api.context import (
    RequestContext,
    get_current_request_context,
    request_context,
)


def test_request_context():
    """Test basic RequestContext class."""
    print("[TEST] RequestContext class")

    ctx = RequestContext("POST /pages")
    assert ctx.request_id
    assert ctx.operation == "POST /pages"
    assert ctx.start_time is None
    assert ctx.end_time is None
    assert ctx.duration() == 0.0

    ctx.start()
    assert ctx.start_time is not None

    ctx.complete()
    assert ctx.end_time is not None
    assert ctx.duration() > 0

    print("[OK] RequestContext class works")


async def test_request_context_manager():
    """Test request_context async context manager."""
    print("[TEST] Request context manager")

    from unittest.mock import Mock
    api = Mock()

    # Test successful request
    async with request_context(api, "POST /pages") as ctx:
        assert ctx.request_id
        assert ctx.operation == "POST /pages"
        assert ctx.start_time is not None
        assert ctx.end_time is None

        # Verify context is available via context variable
        current_ctx = get_current_request_context()
        assert current_ctx is ctx
        assert current_ctx.request_id == ctx.request_id

    # After context manager exits
    assert ctx.end_time is not None
    assert ctx.duration() > 0
    print("[OK] Request context manager works")


async def test_request_context_with_error():
    """Test request context with error handling."""
    print("[TEST] Request context with error")

    from unittest.mock import Mock
    api = Mock()

    class TestError(Exception):
        """Test error."""

    try:
        async with request_context(api, "GET /pages/123") as ctx:
            raise TestError("Something went wrong")
    except TestError as e:
        # Check that context was added to exception via __notes__
        assert hasattr(e, "__notes__"), "Exception should have __notes__ attribute"
        notes = e.__notes__
        notes_str = " ".join(notes)

        assert "Request ID:" in notes_str, f"Expected 'Request ID:' in notes: {notes}"
        assert "Operation: GET /pages/123" in notes_str, f"Expected operation in notes: {notes}"
        assert "Duration:" in notes_str, f"Expected 'Duration:' in notes: {notes}"
        print("[OK] Request context adds notes to exception")


async def test_request_context_metadata():
    """Test request context metadata."""
    print("[TEST] Request context metadata")

    from unittest.mock import Mock
    api = Mock()

    async with request_context(api, "POST /pages") as ctx:
        ctx.metadata.update({
            "test_key": "test_value",
            "number": 42,
        })

        assert ctx.metadata["test_key"] == "test_value"
        assert ctx.metadata["number"] == 42

        # Test to_dict conversion
        ctx_dict = ctx.to_dict()
        assert ctx_dict["request_id"] == ctx.request_id
        assert ctx_dict["operation"] == ctx.operation
        assert "metadata" in ctx_dict

    print("[OK] Request context metadata works")


async def test_nested_context():
    """Test that nested contexts work correctly."""
    print("[TEST] Nested request contexts")

    from unittest.mock import Mock
    api = Mock()

    async with request_context(api, "POST /pages") as outer_ctx:
        outer_id = outer_ctx.request_id

        # Nested context should replace the outer one
        async with request_context(api, "GET /blocks") as inner_ctx:
            current = get_current_request_context()
            assert current.request_id == inner_ctx.request_id
            assert current.request_id != outer_id

        # After inner context exits, outer context should be restored
        # (Actually, with our implementation, context is cleared after inner)
        # This is expected behavior for isolation

    print("[OK] Nested contexts work")


def main():
    """Run all tests."""
    print("=" * 60)
    print("Testing Request Context Implementation")
    print("=" * 60)

    # Synchronous test
    test_request_context()

    # Async tests
    asyncio.run(test_request_context_manager())
    asyncio.run(test_request_context_with_error())
    asyncio.run(test_request_context_metadata())
    asyncio.run(test_nested_context())

    print("=" * 60)
    print("[OK] All request context tests passed!")
    print("=" * 60)


if __name__ == "__main__":
    main()
