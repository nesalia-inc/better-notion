# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- Project initial release with object-oriented Notion API SDK

## [0.1.0] - 2025-01-23

### Added

#### Core API
- Complete object-oriented architecture with entities and collections
- **Entities**: Page, Block, Database, User with full CRUD operations
- **Collections**: PageCollection, BlockCollection, DatabaseCollection, UserCollection
- Async-first design using `asyncio` and `httpx`
- Comprehensive error handling with specific exception types

#### Page Operations
- `get()` - Retrieve pages by ID
- `create()` - Create new pages with properties
- `list()` - List pages in databases (first page)
- `iterate()` - Iterate over all pages with automatic pagination
- `save()` - Save page changes to Notion
- `delete()` - Archive pages
- `reload()` - Reload page data from Notion
- `update()` - Update page properties locally
- Navigation via `page.blocks` property

#### Block Operations
- `get()` - Retrieve blocks by ID
- `save()` - Save block changes
- `delete()` - Delete blocks
- `reload()` - Reload block data
- `content` property - Get/set block content
- `children()` - Get children blocks
- `append()` - Append new blocks to parent

#### Database Operations
- `get()` - Retrieve databases by ID
- `query()` - Query databases with filters
- `create_page()` - Create pages in databases

#### User Operations
- `get()` - Retrieve users by ID
- `list()` - List all users
- `me()` - Get current bot user

#### Property Builders
- Type-safe builders for all Notion property types:
  - RichText, Text, Title
  - Select, MultiSelect
  - Checkbox, Date, CreatedTime, LastEditedTime
  - Number, URL, Email, Phone
- Fluent API for building properties without raw dict manipulation

#### Search
- `search()` - Search pages and blocks in workspace
- `search_iterate()` - Iterate over all search results with pagination
- Support for filters and sorting

#### Utilities
- Helper functions: `parse_datetime()`, `extract_title()`, `extract_content()`
- Async pagination with `AsyncPaginatedIterator`
- Memory-efficient iteration over large datasets

#### Documentation
- Comprehensive README with quick start guide
- Usage examples for common operations
- Complete API reference

#### Testing
- 110 unit tests with mocking
- Coverage for all major functionality

### Python Versions

- Python 3.10
- Python 3.11
- Python 3.12
- Python 3.13

[Unreleased]: https://github.com/nesalia-inc/better-notion/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/nesalia-inc/better-notion/releases/tag/v0.1.0
