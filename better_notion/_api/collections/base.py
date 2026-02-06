"""Base collection ABCs for Notion API collections."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Generic, TypeVar

if TYPE_CHECKING:
    from better_notion._api import NotionAPI

E = TypeVar("E")


class BaseCollection(ABC, Generic[E]):
    """Abstract base for all collections with strong typing.

    Provides the foundation that all collections must extend.

    Type Args:
        E: The entity type this collection returns (e.g., Page, Block).

    Attributes:
        _api: The NotionAPI client instance.
    """

    def __init__(self, api: NotionAPI) -> None:
        """Initialize collection.

        Args:
            api: The NotionAPI client instance.
        """
        self._api = api

    @abstractmethod
    async def get(self, id: str) -> E:
        """Get an item by ID - strongly typed.

        Args:
            id: The item ID.

        Returns:
            Entity instance.

        Raises:
            NotFoundError: If the item does not exist.
        """
        pass

    async def _request(self, method: str, path: str, **kwargs: object) -> dict[str, object]:
        """Shared request method for all collections.

        Args:
            method: HTTP method.
            path: API path.
            **kwargs: Additional arguments for the request.

        Returns:
            Response data as dict.
        """
        return await self._api._request(method, path, **kwargs)


class EntityCollection(BaseCollection[E], ABC):
    """For collections that return Entity objects.

    Provides get() and get_many() methods with strong typing.

    Type Args:
        E: The Entity type this collection returns (e.g., Page, Block).

    Example:
        class PageCollection(EntityCollection[Page]):
            _entity_class = Page

            def _get_path(self, id: str) -> str:
                return f"/pages/{id}"

        # get() inherited with -> Page return type!
        # get_many() inherited with -> list[Page] return type!
    """

    @property
    @abstractmethod
    def _entity_class(self) -> type[E]:
        """The Entity class this collection returns.

        Returns:
            The entity class.
        """
        pass

    async def get(self, id: str) -> E:
        """Get entity with strong typing.

        Args:
            id: The entity ID.

        Returns:
            Entity instance.

        Raises:
            NotFoundError: If the entity does not exist.
        """
        data = await self._request("GET", self._get_path(id))
        return self._entity_class(self._api, data)  # type: ignore[call-arg]

    async def get_many(self, ids: list[str]) -> list[E]:
        """Get multiple entities - returns list[E].

        Args:
            ids: List of entity IDs.

        Returns:
            List of entity instances.
        """
        entities = []
        for entity_id in ids:
            entity = await self.get(entity_id)
            entities.append(entity)
        return entities

    @abstractmethod
    def _get_path(self, id: str) -> str:
        """Get API path for entity.

        Args:
            id: The entity ID.

        Returns:
            API path for the entity.
        """
        pass
