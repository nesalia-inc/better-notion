"""
Official plugins for Better Notion CLI.

This package contains officially maintained plugins that extend
the CLI with commonly-needed functionality.
"""
from better_notion.plugins.official.productivity import ProductivityPlugin

__all__ = ["ProductivityPlugin"]

OFFICIAL_PLUGINS = [
    ProductivityPlugin,
]
