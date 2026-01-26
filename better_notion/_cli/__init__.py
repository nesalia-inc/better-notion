"""
Better Notion CLI - Command-line interface for Better Notion SDK.

This package provides a CLI for interacting with Notion via the command line,
designed primarily for AI agents rather than human users.

Features:
- JSON-only output for programmatic parsing
- Structured error codes for reliable error handling
- Idempotency support for safe retries
- Rate limit awareness for avoiding throttling
- Async command support via AsyncTyper

Installation:
    pip install better-notion[cli]

Usage:
    $ notion pages get page_abc123
    $ notion databases query db_xyz --filter '{"property":"Status","select":{"equals":"Done"}}'
"""
