# Better Notion SDK Design Documentation

This directory contains the design documentation for the Better Notion SDK architecture and developer experience.

## Overview

Better Notion is a Python SDK for the Notion API that prioritizes developer experience through:

- Two-level architecture (low-level API + high-level client)
- Rich abstractions that go beyond simple API wrapping
- Async-first design with comprehensive type hints
- Intelligent caching and pagination
- Semantic operations that map to user intent

Inspired by discord.py, we believe an SDK should provide more features than the underlying API, making developers significantly more productive than they would be with raw API access.

## Documentation Structure

### [Architecture](./architecture.md)
**Start here for understanding the overall design**

Discusses the two-level architecture:
- **Low-level (`NotionAPI`)**: Direct API mapping for precision and control
- **High-level (`NotionClient`)**: Rich abstractions for productivity
- Technical implementation strategy
- Feature distribution between levels
- Maintenance and versioning approach

### [Design Philosophy](./design-philosophy.md)
**The "why" behind our design decisions**

Explains the core principles:
- Developer experience first
- Cache aggressively to avoid API calls
- Hide pagination behind async iterators
- Provide semantic operations
- Enable hierarchical thinking
- Fail clearly with helpful errors
- Type everything for better IDE support

Inspired by discord.py's approach to being "feature-rich" rather than just an API wrapper.

### [Mental Model](./mental-model.md)
**How developers should think about the SDK**

Defines the conceptual model:
- Notion as objects (Page, Database, Block, User)
- Hierarchical relationships and navigation
- Query model as mental model, not API syntax
- Cache behavior and strategies
- Type hierarchy and safety
- Comparison of API-centric vs SDK-centric thinking

### [Feature Catalog](./feature-catalog.md)
**Complete inventory of SDK features**

Comprehensive list of:
- API-mirrored features (exist in Notion API)
- SDK-exclusive features (go beyond the API)
- Organized by manager (Pages, Databases, Blocks, Users, etc.)
- Priority classification (Tier 1-4)
- Code examples for each feature

### [API Surface](./api-surface.md)
**Public API specification**

Detailed specification of:
- Client initialization options
- Manager interfaces and methods
- Entity object APIs
- Method signatures and return types
- Async iterator interface
- Cache interface
- Exception hierarchy
- Type aliases and conventions

## Key Concepts

### Two Levels of Abstraction

The SDK provides two distinct levels:

**Level 1: `NotionAPI` (Low-level)**
```python
api = NotionAPI(auth=token)
response = await api.blocks.retrieve(block_id="...")
```

For: Developers familiar with Notion API, precise control needs, migrations from other SDKs

**Level 2: `NotionClient` (High-level)**
```python
client = NotionClient(auth=token)
page = await client.pages.get(page_id)
print(page.title)  # Rich object with methods
```

For: Rapid development, standard applications, developers prioritizing ergonomics

### Features Beyond the API

The SDK provides capabilities that don't exist in the Notion API:

1. **Cache Management**: Instant lookups without API calls
2. **Semantic List Operations**: `client.pages.all()`, `.find_by_title()`
3. **Hierarchical Navigation**: `page.parent`, `page.children`
4. **Bulk Operations**: Create/update multiple items efficiently
5. **Smart Search**: Local cache search, fuzzy matching
6. **Content Operations**: Duplicate, copy, move pages
7. **Workspace Awareness**: `client.workspace` with user directory
8. **Async Iterators**: Automatic pagination with `async for`

### Design Principles

1. **What does the user want to achieve?** (Not what endpoints exist)
2. **How can we make this more Pythonic?** (Not how does the API work)
3. **Can we cache this to avoid API calls?** (Optimize by default)
4. **What would a developer naturally expect?** (Follow Python conventions)
5. **How can we prevent misuse?** (Make wrong code look wrong)

## Development Roadmap

These documents inform implementation. The recommended order:

### Phase 1: Foundations
- Implement low-level `NotionAPI`
- Base entity classes
- HTTP client with authentication
- Error handling framework

### Phase 2: Caching and Types
- Cache implementation
- Type hints throughout
- Entity model base classes

### Phase 3: High-Level Client
- `NotionClient` with managers
- Basic CRUD operations
- Entity objects with methods

### Phase 4: Enhanced Features
- Async iterators for pagination
- Property shortcuts
- Hierarchical navigation
- Cache population

### Phase 5: Advanced Features
- Bulk operations
- Find operations
- Smart search
- Content operations

### Phase 6: Polish
- Comprehensive testing
- Documentation
- Examples
- Performance optimization

## Success Metrics

The SDK is successful when:

1. Developers are productive in minutes, not hours
2. Common tasks require minimal code
3. API calls are minimized through caching
4. Errors provide clear, actionable guidance
5. IDE autocomplete suggests the right methods
6. Users rarely need to read Notion API docs
7. Complex operations feel simple

## Related Documentation

- [API Reference](../api/) - Complete Notion API endpoint documentation
- [PROJECT.md](../PROJECT.md) - Overall project documentation
- [API Structure](../api/api-structure.md) - Notion API conventions

## Contributing

When designing new features or making changes:

1. Start with the philosophy: What does the user want to achieve?
2. Check the mental model: Does this fit the conceptual framework?
3. Review the feature catalog: Is this a new capability or enhancement?
4. Update the API surface: Document the public interface
5. Maintain consistency: Follow existing patterns and conventions

## Goals vs Non-Goals

### Goals
- Delight developers using Notion API in Python
- Provide abstractions that feel natural to Python developers
- Reduce boilerplate and common friction points
- Make common tasks simple and complex tasks possible
- Enable users to be productive without learning API details

### Non-Goals
- 1:1 API coverage (focus on commonly used features)
- Sync interface (async-only by design)
- Support for every Python version (3.10+ only)
- Compatibility with other Notion SDKs (fresh design)
- Feature parity with Notion web app (API limitations apply)

---

**Next Steps:**

1. Read [Architecture](./architecture.md) for understanding the two-level design
2. Review [Design Philosophy](./design-philosophy.md) to understand the principles
3. Study [Mental Model](./mental-model.md) to understand the abstractions
4. Explore [Feature Catalog](./feature-catalog.md) to see what will be built
5. Reference [API Surface](./api-surface.md) when implementing interfaces
