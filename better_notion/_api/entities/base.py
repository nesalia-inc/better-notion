"""Base Entity ABCs for Notion API entities."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from better_notion._api import NotionAPI


class ReadOnlyEntity(ABC):
    """Abstract base class for read-only Notion entities.

    Defines the common interface that all entities must implement,
    including User which is read-only.

    Attributes:
        _api: The NotionAPI client instance.
        _data: Raw entity data from Notion API.
    """

    def __init__(self, api: NotionAPI, data: dict[str, Any]) -> None:
        """Initialize entity.

        Args:
            api: The NotionAPI client instance.
            data: Raw entity data from Notion API.
        """
        self._api = api
        self._data = data

    @property
    @abstractmethod
    def id(self) -> str:
        """Get the entity ID.

        Returns:
            The entity's unique identifier.
        """
        ...

    @abstractmethod
    async def reload(self) -> None:
        """Reload entity data from Notion.

        Fetches the latest entity data from Notion and updates
        the internal state.

        Raises:
            NotFoundError: If the entity no longer exists.
        """
        pass

    def __repr__(self) -> str:
        """String representation.

        Returns:
            String representation showing class name and ID.
        """
        return f"{self.__class__.__name__}(id={self.id!r})"


class Entity(ReadOnlyEntity):
    """Abstract base class for writable Notion entities.

    Extends ReadOnlyEntity to add methods for modifying entities
    in Notion (save, delete).

    Implementations:
        - Page
        - Database
        - Block
        - Comment

    Note:
        User entity extends ReadOnlyEntity only (read-only).
    """

    @abstractmethod
    async def save(self) -> None:
        """Save changes to Notion.

        Persists local modifications to Notion API.

        Raises:
            NotFoundError: If the entity no longer exists.
            ValidationError: If properties are invalid.
            NotImplementedError: If the entity doesn't support updates.
        """
        pass

    @abstractmethod
    async def delete(self) -> None:
        """Delete (archive) this entity.

        Permanently deletes or archives the entity in Notion.

        Raises:
            NotFoundError: If the entity no longer exists.
        """
        pass
