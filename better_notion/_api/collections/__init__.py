"""Collection classes for managing Notion objects."""

from better_notion._api.collections.base import BaseCollection, EntityCollection
from better_notion._api.collections.blocks import BlockCollection
from better_notion._api.collections.comments import CommentCollection
from better_notion._api.collections.databases import DatabaseCollection
from better_notion._api.collections.pages import PageCollection
from better_notion._api.collections.users import UserCollection

__all__ = [
    "BaseCollection",
    "EntityCollection",
    "PageCollection",
    "BlockCollection",
    "DatabaseCollection",
    "UserCollection",
    "CommentCollection",
]
