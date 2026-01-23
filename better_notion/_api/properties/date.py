"""Date property builders."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from better_notion._api.properties.base import Property


class Date(Property):
    """Builder for date properties."""

    def __init__(
        self,
        name: str,
        value: datetime | str | None = None,
        end: datetime | str | None = None,
    ) -> None:
        """Initialize a date property.

        Args:
            name: The property name.
            value: Start date as datetime or ISO string.
            end: Optional end date for date ranges.
        """
        super().__init__(name)
        self._value = value
        self._end = end

    def _format_date(self, date: datetime | str) -> str:
        """Format date to ISO string.

        Args:
            date: Date to format.

        Returns:
            ISO formatted date string.
        """
        if isinstance(date, datetime):
            return date.isoformat()
        return date

    def to_dict(self) -> dict[str, Any]:
        """Convert to Notion API format."""
        date_obj: dict[str, Any] = {}

        if self._value:
            date_obj["start"] = self._format_date(self._value)
        if self._end:
            date_obj["end"] = self._format_date(self._end)

        return {
            "type": "date",
            "date": date_obj if date_obj else None
        }


class CreatedTime(Property):
    """Builder for created time properties (read-only)."""

    def __init__(self, name: str = "Created time") -> None:
        """Initialize a created time property.

        Args:
            name: The property name.
        """
        super().__init__(name)

    def to_dict(self) -> dict[str, Any]:
        """Convert to Notion API format."""
        return {
            "type": "created_time",
            "created_time": None
        }


class LastEditedTime(Property):
    """Builder for last edited time properties (read-only)."""

    def __init__(self, name: str = "Last edited time") -> None:
        """Initialize a last edited time property.

        Args:
            name: The property name.
        """
        super().__init__(name)

    def to_dict(self) -> dict[str, Any]:
        """Convert to Notion API format."""
        return {
            "type": "last_edited_time",
            "last_edited_time": None
        }
