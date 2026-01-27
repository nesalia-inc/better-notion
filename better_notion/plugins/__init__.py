"""
Plugin system for Better Notion CLI.

This module provides the plugin infrastructure that allows users to extend
the CLI functionality through custom plugins.
"""
from __future__ import annotations

from better_notion.plugins.base import CommandPlugin, DataPlugin

__all__ = ["CommandPlugin", "DataPlugin"]
