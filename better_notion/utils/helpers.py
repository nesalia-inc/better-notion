"""Helper functions."""

from __future__ import annotations

from datetime import datetime
from typing import Any


def parse_datetime(dt_string: str) -> datetime:
    """Parse an ISO 8601 datetime string.

    Args:
        dt_string: ISO 8601 datetime string.

    Returns:
        Parsed datetime object.

    Raises:
        NotImplementedError: Not yet implemented.
    """
    raise NotImplementedError("parse_datetime() not yet implemented")


def extract_title(properties: dict) -> str | None:
    """Extract title from page properties.

    Args:
        properties: Page properties dict.

    Returns:
        The title text or None.

    Raises:
        NotImplementedError: Not yet implemented.
    """
    raise NotImplementedError("extract_title() not yet implemented")


def extract_content(block_data: dict) -> Any:
    """Extract content from block data.

    Args:
        block_data: Block data dict.

    Returns:
        The block content.

    Raises:
        NotImplementedError: Not yet implemented.
    """
    raise NotImplementedError("extract_content() not yet implemented")
