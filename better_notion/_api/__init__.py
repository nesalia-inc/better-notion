"""Low-level API for Better Notion SDK.

This module provides an object-oriented interface to the Notion API.
Entity objects (Page, Block, etc.) know how to manipulate themselves.
"""

from better_notion._api.client import NotionAPI

__all__ = ["NotionAPI"]
