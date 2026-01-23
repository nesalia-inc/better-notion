"""
Low-level API for Better Notion SDK.

This module provides a 1:1 mapping with the Notion API.
Use NotionClient for a higher-level interface.
"""

from better_notion._api.client import NotionAPI

__all__ = ["NotionAPI"]
