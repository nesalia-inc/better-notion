"""Base property builder."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class Property(ABC):
    """Base class for all property builders."""

    def __init__(self, name: str) -> None:
        """Initialize a property.

        Args:
            name: The property name.
        """
        self._name = name

    @property
    def name(self) -> str:
        """Get the property name."""
        return self._name

    @abstractmethod
    def to_dict(self) -> dict[str, Any]:
        """Convert property to Notion API format.

        Returns:
            Dictionary representation for Notion API.
        """

    def build(self) -> dict[str, Any]:
        """Build the complete property for Notion API.

        Returns:
            Complete property dictionary with name and type.
        """
        return {self._name: self.to_dict()}
