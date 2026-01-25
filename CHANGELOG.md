# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.3.0] - Unreleased

### Added

#### Advanced Block Types
- Added 16 specialized block types with full property support:
  - **Toggle**: Collapsible accordion blocks
  - **Table & TableRow**: Table structures with headers
  - **ColumnList & Column**: Multi-column layouts
  - **Equation**: LaTeX math equations
  - **SyncedBlock**: Blocks synced across pages
  - **Bookmark**: URL bookmarks with captions
  - **Embed**: Generic embeds for external content
  - **Video, Audio, File, Image, PDF**: Media file blocks
  - **Breadcrumb**: Navigation breadcrumbs
  - **Template**: Template blocks
- Updated `Block.from_data()` factory to return specialized instances
- All block types now inherit from `BaseBlock` with consistent interface

#### Property Parsers
- **FormulaParser**: Parse formula property values
  - Supports string, number, boolean, date result types
  - Automatic type conversion (e.g., float.is_integer() → int)
  - Handles empty formulas
- **RelationParser**: Parse relation properties
  - Extract related page IDs
  - Count relations
  - Check for specific page in relation

#### Comments API
- **Comment model**: Full entity with BaseEntity navigation
  - `text` property for plain text extraction
  - Rich mention support (@user, @page, @database)
  - Attachments and metadata properties
- **CommentsManager**: Complete comment operations
  - `get()`: Retrieve comments by ID
  - `create()`: Create comments with rich text and attachments
  - `list_all()`: List all comments for a page/block
- Integrated into `NotionClient` with `client.comments` manager
- Dedicated comment cache for performance

#### Retry Logic
- **RetryConfig**: Configurable retry behavior
  - Exponential backoff with configurable base
  - Optional random jitter to prevent thundering herd
  - Max delay capping
  - Configurable max retries and initial delay
- **RetryHandler**: Smart retry execution
  - Retries on 429 rate limiting
  - Retries on 5xx server errors
  - Retries on 408 timeouts
  - No retry on 4xx client errors (except 408, 429)
  - Optional `on_retry` callback for monitoring
- **@retry decorator**: Easy function decoration
  - Add retry logic to any async function
  - Same configuration as RetryHandler

#### Error Handling
- Extended `NotionAPIError` to support 3-parameter constructor
  - `NotionAPIError(status_code, code, info)` for testing
  - Maintains backward compatibility with `NotionAPIError("message")`
  - Added `status_code`, `code`, and `info` attributes

### Testing
- All 563 tests passing
- 17 new tests for advanced block types
- 17 new tests for FormulaParser
- 14 new tests for RelationParser
- 20 new tests for Comments API
- 14 new tests for retry logic

## [0.2.0] - 2025-01-24

### Fixed

#### Page Entity
- Fixed `Page.update()` method to properly unpack `properties` kwarg
- Fixed `Page.save()` method to send only modified properties in request format
- Fixed `Page.reload()` method to reset modified properties tracking
- Added `_modified_properties` tracking to separate request format from response format
- Fixed issue where update/save methods mixed response and request formats

#### Testing
- Fixed integration tests for block children API (POST → PATCH)
- Fixed paragraph block format to use `rich_text` instead of `text`
- Updated Page entity unit tests for new behavior
- Fixed Title property usage across all tests
- All 137 tests now passing (100%)

#### Documentation
- Fixed README import paths for property builders
- Fixed block examples to use correct `rich_text` format

### Changed

- Development status updated from Alpha to Beta
- Integration tests now use page-level parent instead of workspace

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
- Python 3.14

[Unreleased]: https://github.com/nesalia-inc/better-notion/compare/v0.3.0...HEAD
[0.3.0]: https://github.com/nesalia-inc/better-notion/releases/tag/v0.3.0
[0.2.0]: https://github.com/nesalia-inc/better-notion/releases/tag/v0.2.0
[0.1.0]: https://github.com/nesalia-inc/better-notion/releases/tag/v0.1.0
