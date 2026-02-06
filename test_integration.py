"""Integration tests for all architecture and error handling improvements.

This test suite validates:
- Entity/Collection architecture (#062)
- Property validation in entities (#063)
- Rich exception attributes (#064)
- Exception.add_note() usage (#065)
- Structured validation errors (#068)
- Request context tracking (#069)
- Retry decorator with exponential backoff (#067)
"""

import asyncio
import logging
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

from better_notion._api import NotionAPI
from better_notion._api.entities import Page, Database
from better_notion._api.errors import (
    NotionAPIError,
    BadRequestError,
    ValidationError,
)
from better_notion._api.properties import Title, Text, Number, Date, Relation
from better_notion._api.context import get_current_request_context


def test_entity_collection_architecture():
    """Test #062: Collections return Entity objects."""
    print("[TEST] Entity/Collection architecture (#062)")

    # Create mock API
    api = Mock(spec=NotionAPI)

    # Test Page entity creation
    page_data = {
        "id": "page_123",
        "created_time": "2025-01-01T00:00:00.000Z",
        "last_edited_time": "2025-01-01T00:00:00.000Z",
        "archived": False,
        "parent": {"type": "workspace", "workspace": True},
        "properties": {
            "Name": {
                "type": "title",
                "title": [{"plain_text": "Test Page"}]
            }
        }
    }

    page = Page(api, page_data)

    # Verify entity has methods
    assert hasattr(page, "id")
    assert hasattr(page, "save")
    assert hasattr(page, "delete")
    assert hasattr(page, "reload")
    assert hasattr(page, "update")

    assert page.id == "page_123"
    assert page.archived is False

    print("[OK] Page entity has all methods")

    # Test Database entity creation
    db_data = {
        "id": "db_123",
        "created_time": "2025-01-01T00:00:00.000Z",
        "last_edited_time": "2025-01-01T00:00:00.000Z",
        "archived": False,
        "parent": {"type": "workspace", "workspace": True},
        "title": [{"plain_text": "Test DB"}],
        "properties": {
            "Name": {"type": "title", "title": {}}
        }
    }

    database = Database(api, db_data)

    # Verify entity has methods
    assert hasattr(database, "id")
    assert hasattr(database, "query")
    assert hasattr(database, "save")
    assert hasattr(database, "delete")
    assert hasattr(database, "reload")

    assert database.id == "db_123"
    assert database.archived is False

    print("[OK] Database entity has all methods")


async def test_property_validation():
    """Test #063: Property validation in entity.update()."""
    print("[TEST] Property validation (#063)")

    api = Mock(spec=NotionAPI)
    page_data = {
        "id": "page_123",
        "created_time": "2025-01-01T00:00:00.000Z",
        "last_edited_time": "2025-01-01T00:00:00.000Z",
        "archived": False,
        "parent": {"type": "workspace", "workspace": True},
        "properties": {}
    }

    page = Page(api, page_data)

    # Test valid property
    await page.update(archived=True)
    assert page._modified

    # Test invalid property name
    try:
        await page.update(invalid_property="value")
        assert False, "Should raise ValueError for invalid property"
    except ValueError as e:
        assert "Invalid page property" in str(e)
        assert "invalid_property" in str(e)

    print("[OK] Property validation works")

    # Test invalid property value
    try:
        await page.update(archived="not_a_boolean")
        assert False, "Should raise ValueError for invalid value"
    except ValueError as e:
        assert "Invalid value for property 'archived'" in str(e)
        assert "boolean" in str(e)

    print("[OK] Property value validation works")


def test_rich_exception_attributes():
    """Test #064: Rich exception attributes."""
    print("[TEST] Rich exception attributes (#064)")

    error = BadRequestError(
        "Test error",
        request_id="req_123",
        notion_code="invalid_request",
        request_method="POST",
        request_path="/pages",
        response_body={"test": "data"}
    )

    # Verify rich attributes
    assert error.request_id == "req_123"
    assert error.notion_code == "invalid_request"
    assert error.request_method == "POST"
    assert error.request_path == "/pages"
    assert error.response_body == {"test": "data"}

    print("[OK] Rich exception attributes work")

    # Test to_dict() method
    error_dict = error.to_dict()
    assert error_dict["type"] == "BadRequestError"
    assert error_dict["request_id"] == "req_123"
    assert error_dict["notion_code"] == "invalid_request"

    print("[OK] Error serialization works")

    # Test get_context_summary() method
    summary = error.get_context_summary()
    assert "Request ID: req_123" in summary
    assert "Notion Code: invalid_request" in summary
    assert "Operation: POST /pages" in summary

    print("[OK] Context summary works")


def test_exception_add_notes():
    """Test #065: Exception.add_note() for rich context."""
    print("[TEST] Exception.add_note() usage (#065)")

    error = BadRequestError("Test error")

    # Add notes
    error.add_note("Request ID: req_123")
    error.add_note("Operation: POST /pages")
    error.add_note("Duration: 0.234s")

    # Verify notes
    assert hasattr(error, "__notes__")
    notes = error.__notes__
    assert len(notes) == 3
    assert "Request ID: req_123" in notes
    assert "Operation: POST /pages" in notes
    assert "Duration: 0.234s" in notes

    print("[OK] Exception.add_note() works")


def test_structured_validation_errors():
    """Test #068: Structured validation errors."""
    print("[TEST] Structured validation errors (#068)")

    error = ValidationError("Validation failed")

    # Add property-level errors
    error.add_error("title", "Title is required", "required")
    error.add_error("status", "Invalid status value", "invalid_value", "invalid")
    error.add_error("date", "Date must be in the future", "invalid_date")

    # Verify error structure
    assert error.has_errors()
    assert len(error.errors) == 3

    # Test get_errors_for_property
    title_errors = error.get_errors_for_property("title")
    assert len(title_errors) == 1
    assert title_errors[0]["message"] == "Title is required"

    # Test serialization
    error_dict = error.to_dict()
    assert error_dict["type"] == "validation_error"
    assert len(error_dict["errors"]) == 3

    # Test user-friendly message
    message = error.get_user_friendly_message()
    assert "Validation failed" in message
    assert "title: Title is required" in message
    assert "status: Invalid status value" in message

    print("[OK] Structured validation errors work")


async def test_request_context_tracking():
    """Test #069: Request context tracking."""
    print("[TEST] Request context tracking (#069)")

    from better_notion._api.context import RequestContext, request_context

    # Test RequestContext class
    ctx = RequestContext("POST /pages")
    assert ctx.request_id
    assert ctx.operation == "POST /pages"
    assert ctx.start_time is None

    ctx.start()
    ctx.complete()
    assert ctx.duration() >= 0

    print("[OK] RequestContext class works")

    # Test context manager
    api = Mock(spec=NotionAPI)

    async with request_context(api, "GET /pages/123") as ctx:
        # Verify context is available
        current = get_current_request_context()
        assert current is ctx
        assert current.request_id == ctx.request_id

        # Test metadata
        ctx.metadata["test_key"] = "test_value"

    # After context completes
    assert ctx.end_time is not None
    assert ctx.duration() > 0

    print("[OK] Request context manager works")

    # Test error handling with context
    class TestError(Exception):
        pass

    try:
        async with request_context(api, "DELETE /pages/123") as ctx:
            raise TestError("Test error")
    except TestError as e:
        # Verify notes were added
        assert hasattr(e, "__notes__")
        notes_str = " ".join(e.__notes__)
        assert "Request ID:" in notes_str
        assert "Operation: DELETE /pages/123" in notes_str
        assert "Duration:" in notes_str

    print("[OK] Request context error handling works")


async def test_retry_decorator():
    """Test #067: Retry decorator with exponential backoff."""
    print("[TEST] Retry decorator (#067)")

    from better_notion._api.retry import retry_on_rate_limit
    from better_notion._api.errors import RateLimitedError

    call_count = 0

    @retry_on_rate_limit(max_retries=3, initial_backoff=0.01, max_backoff=0.1)
    async def test_func():
        nonlocal call_count
        call_count += 1
        if call_count < 3:
            raise RateLimitedError("Rate limited", retry_after=1)
        return "success"

    result = await test_func()
    assert result == "success"
    assert call_count == 3  # Failed twice, succeeded on third try

    print("[OK] Retry decorator works")

    # Test max retries exceeded
    call_count = 0

    @retry_on_rate_limit(max_retries=2, initial_backoff=0.01, max_backoff=0.1)
    async def test_func_fail():
        nonlocal call_count
        call_count += 1
        raise RateLimitedError("Rate limited", retry_after=1)

    try:
        await test_func_fail()
        assert False, "Should raise RateLimitedError"
    except RateLimitedError as e:
        assert e.__notes__
        assert "Max retries" in " ".join(e.__notes__)
        assert call_count == 2  # Tried max_retries times

    print("[OK] Retry decorator max retries works")


async def test_property_builders():
    """Test property builder API consistency (#055)."""
    print("[TEST] Property builder API consistency (#055)")

    # Test Relation property with name parameter
    relation = Relation("Domain", ["page_123"])
    assert relation._name == "Domain"
    assert relation._page_ids == ["page_123"]

    relation_dict = relation.to_dict()
    # Note: Property name is used as key in properties dict, not in to_dict()
    assert relation_dict["type"] == "relation"
    assert relation_dict["relation"] == [{"id": "page_123"}]

    # Test that it works correctly when used in properties
    properties = {}
    properties[relation._name] = relation_dict
    assert "Domain" in properties
    assert properties["Domain"]["type"] == "relation"

    print("[OK] Relation property with name parameter works")

    # Test other property builders
    title = Title("Test Page")
    title_dict = title.to_dict()
    assert "title" in title_dict

    # Text requires name and content
    text = Text("Description", "Some text")
    text_dict = text.to_dict()
    assert "text" in text_dict

    number = Number("Count", 42)
    number_dict = number.to_dict()
    assert "number" in number_dict
    assert number_dict["number"] == 42

    date = Date("Due Date", "2025-01-01")
    date_dict = date.to_dict()
    assert "date" in date_dict

    print("[OK] All property builders work")


async def test_end_to_end_scenario():
    """Test end-to-end scenario combining all features."""
    print("[TEST] End-to-end scenario")

    # This would normally require a real API connection
    # For now, we test the structure

    # Mock API client
    api = Mock(spec=NotionAPI)

    # Create page entity
    page_data = {
        "id": "page_123",
        "created_time": "2025-01-01T00:00:00.000Z",
        "last_edited_time": "2025-01-01T00:00:00.000Z",
        "archived": False,
        "parent": {"type": "workspace", "workspace": True},
        "properties": {
            "Name": {
                "type": "title",
                "title": [{"plain_text": "Test Page"}]
            }
        }
    }

    page = Page(api, page_data)

    # Test property validation
    await page.update(archived=True)
    assert page._modified

    # Test error handling with rich context
    try:
        await page.update(invalid_property="value")
        assert False, "Should raise ValueError"
    except ValueError as e:
        # Verify error message is clear
        assert "Invalid page property" in str(e)

    # Test structured validation error
    validation_error = ValidationError("Page validation failed")
    validation_error.add_error("properties", "Missing required field", "required")

    assert validation_error.has_errors()
    assert "properties" in validation_error.get_user_friendly_message()

    print("[OK] End-to-end scenario works")


async def run_all_tests():
    """Run all integration tests."""
    print("=" * 60)
    print("Integration Tests - Architecture & Error Handling")
    print("=" * 60)

    # Synchronous tests
    test_entity_collection_architecture()
    await test_property_validation()
    test_rich_exception_attributes()
    test_exception_add_notes()
    test_structured_validation_errors()
    await test_request_context_tracking()
    await test_retry_decorator()
    await test_property_builders()
    await test_end_to_end_scenario()

    print("=" * 60)
    print("[OK] All integration tests passed!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(run_all_tests())
