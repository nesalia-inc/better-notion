# Better Notion

A comprehensive Python SDK for the Notion API, providing an elegant, object-oriented interface for interacting with Notion's platform.

## Overview

Better Notion is an open-source Python library designed to simplify integration with Notion's API. It offers a high-level abstraction layer that transforms Notion's REST API into intuitive Python objects, making it easier for developers to build applications, automation tools, and integrations on top of the Notion platform.

## Project Status

This project is currently in the documentation and planning phase. The API reference documentation is complete, covering all major Notion API endpoints and features. Implementation will follow a structured development roadmap.

## Key Features

### Authentication and Security
- Bot token authentication for integrations
- OAuth 2.0 support for public integrations with user authorization
- Built-in rate limiting and error handling
- Secure credential management

### Database Management
- Full CRUD operations for Notion databases
- Multi-data source architecture support
- Query and filter capabilities with complex conditions
- Property type handling for all Notion property types
- Sorting and pagination support

### Page Operations
- Create, read, update, and delete pages
- Property manipulation and management
- Page hierarchy and parent-child relationships
- Cover images and icons handling
- Template-based page creation

### Content Blocks
- Comprehensive block type support
- Nested block hierarchy management (up to 2 levels)
- Rich text formatting with annotations
- Media blocks (images, videos, files, audio)
- Code blocks, callouts, and tables

### Rich Text System
- Text formatting (bold, italic, underline, strikethrough, code)
- Text and background colors
- Hyperlinks and mentions
- User, page, and database mentions
- Mathematical equations

### Search and Discovery
- Search across pages and databases by title
- Filter by object type
- Sort by last edited time
- Pagination for large result sets

### Comments and Discussions
- Create comments on pages and blocks
- Retrieve and list comments
- Discussion thread support
- Rich text comments with attachments
- File attachment support (up to 3 per comment)

### File Management
- Single-part file uploads (up to 20MB)
- Multi-part uploads for large files (up to 1GB)
- External URL imports
- File upload progress tracking
- Upload completion and retrieval

### User Management
- List all workspace users
- Retrieve specific user information
- Bot user information with owner details
- User directory and search capabilities

## Architecture

### Design Principles

The SDK follows several core design principles:

- Entity-Oriented Object-Oriented Programming: Notion objects are represented as Python classes with methods and properties
- Type Safety: Comprehensive type hints throughout the codebase
- Async-First: Native async/await support for efficient operations
- High-Level Abstraction: Complex API operations hidden behind intuitive interfaces
- Performance Optimization: Smart caching and efficient API usage
- Extensibility: Easy to extend for custom use cases

### Project Structure

The planned package structure includes:

- Client module for API communication
- Entity models (pages, blocks, databases, users)
- Endpoint managers for each API resource
- Utility functions for conversions and helpers
- Custom exceptions for error handling
- Caching layer for performance
- Comprehensive test suite

## Documentation

Complete API reference documentation is available in the `docs/` directory:

- API structure and conventions
- Authentication and OAuth
- Database operations and data sources
- Page management and properties
- Block content and types
- Comments and discussions
- File uploads and media handling
- Search functionality
- User management

## Target Use Cases

Better Notion is designed for:

- Automation developers building workflows with Notion
- Data analysts extracting and analyzing Notion data
- Web application developers integrating with Notion
- CLI tool creators for Notion management
- Anyone building tools or applications on top of Notion's platform

## Requirements

- Python 3.10 or higher
- Async HTTP client (httpx or aiohttp)
- Pydantic for data validation

## Development Roadmap

The project follows a 7-phase development plan:

1. Foundations: Core client setup and base models
2. Search and Navigation: Search functionality and filtering
3. Databases: Database operations and data source queries
4. Pages and Blocks: Content management and manipulation
5. Users and Workspaces: User management and workspace information
6. Advanced Features: Comments, file uploads, and specialized features
7. Testing and Documentation: Comprehensive test coverage and user guides

## Contributing

As an open-source project, contributions are welcome. The project maintains comprehensive documentation to help contributors understand the architecture and implementation plan.

## License

This project is open source and available under the terms specified in the LICENSE file.

## Acknowledgments

Built to work with Notion's official API, providing developers with a better way to integrate Notion into their Python applications.
