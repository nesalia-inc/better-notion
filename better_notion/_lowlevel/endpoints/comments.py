"""Comments API endpoint."""

from __future__ import annotations

from typing import Any


class CommentsEndpoint:
    """Comments API endpoint.

    Provides methods for interacting with Notion comments.
    """

    def __init__(self, api: Any) -> None:
        """Initialize the Comments endpoint.

        Args:
            api: The NotionAPI client instance.
        """
        self._api = api

    async def retrieve(self, comment_id: str) -> dict[str, Any]:
        """Retrieve a comment object.

        Args:
            comment_id: The identifier for the Notion comment.

        Returns:
            The comment data as a dictionary.

        Raises:
            NotFoundError: If the comment doesn't exist.
        """
        raise NotImplementedError("Not yet implemented")
