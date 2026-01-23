"""Helper functions."""

from __future__ import annotations

from datetime import datetime
from typing import Any


def parse_datetime(dt_string: str) -> datetime:
    """Parse an ISO 8601 datetime string.

    Args:
        dt_string: ISO 8601 datetime string (e.g., "2025-01-15T00:00:00.000Z").

    Returns:
        Parsed datetime object.

    Raises:
        ValueError: If the datetime string is invalid.
    """
    if not dt_string:
        raise ValueError("datetime string cannot be empty")

    # Handle timezone suffix (Z for UTC)
    dt_string_clean = dt_string.replace("Z", "+00:00")

    try:
        return datetime.fromisoformat(dt_string_clean)
    except ValueError as e:
        raise ValueError(f"Invalid datetime format: {dt_string}") from e


def extract_title(properties: dict) -> str | None:
    """Extract title from page properties.

    Args:
        properties: Page properties dict from Notion API.

    Returns:
        The title text or None if no title property exists.

    Examples:
        >>> props = {"Name": {"type": "title", "title": [{"text": {"content": "Hello"}}]}}
        >>> extract_title(props)
        'Hello'
    """
    if not properties:
        return None

    # Find the first property with type "title"
    for prop_name, prop_data in properties.items():
        if isinstance(prop_data, dict) and prop_data.get("type") == "title":
            title_array = prop_data.get("title", [])
            if title_array and len(title_array) > 0:
                # The title is an array of rich text objects
                text_obj = title_array[0].get("text", {})
                return text_obj.get("content")

    return None


def extract_content(block_data: dict) -> Any:
    """Extract content from block data.

    Args:
        block_data: Block data dict from Notion API.

    Returns:
        The block content (structure varies by block type).

    Examples:
        >>> block = {"type": "paragraph", "paragraph": {"text": [{"text": {"content": "Hello"}}]}}
        >>> extract_content(block)
        {'text': [{'text': {'content': 'Hello'}}]}
    """
    if not block_data:
        return None

    block_type = block_data.get("type")
    if not block_type:
        return None

    # The content is in the field named after the block type
    return block_data.get(block_type)
