"""Pagination utilities for async iteration over Notion API results."""

from __future__ import annotations

from typing import Any, AsyncIterator, Callable, TypeVar

T = TypeVar("T")


class AsyncPaginatedIterator(AsyncIterator[T]):
    """Async iterator for paginated Notion API results.

    Example:
        >>> async for page in pages:
        ...     print(page.title)
    """

    def __init__(
        self,
        fetch_fn: Callable[[str | None], dict[str, Any]],
        item_parser: Callable[[dict[str, Any]], T],
    ) -> None:
        """Initialize the paginated iterator.

        Args:
            fetch_fn: Async function that fetches a page with optional cursor.
            item_parser: Function that parses raw item data into entity.
        """
        self._fetch_fn = fetch_fn
        self._item_parser = item_parser
        self._next_cursor: str | None = None
        self._has_more = True
        self._buffer: list[T] = []
        self._buffer_index = 0

    def __aiter__(self) -> AsyncPaginatedIterator[T]:
        """Return the async iterator."""
        return self

    async def __anext__(self) -> T:
        """Get the next item from pagination.

        Returns:
            The next parsed item.

        Raises:
            StopAsyncIteration: When no more items are available.
        """
        # If buffer is exhausted, fetch next page
        if self._buffer_index >= len(self._buffer):
            if not self._has_more:
                raise StopAsyncIteration

            data = await self._fetch_fn(self._next_cursor)
            self._has_more = data.get("has_more", False)
            self._next_cursor = data.get("next_cursor")

            results = data.get("results", [])
            if not results:
                raise StopAsyncIteration

            self._buffer = [self._item_parser(item) for item in results]
            self._buffer_index = 0

        # Get next item from buffer
        item = self._buffer[self._buffer_index]
        self._buffer_index += 1
        return item

    async def to_list(self) -> list[T]:
        """Collect all items into a list.

        Returns:
            List of all items across all pages.

        Example:
            >>> pages = await AsyncPaginatedIterator(...).to_list()
        """
        items = []
        async for item in self:
            items.append(item)
        return items
