# Implementation Specifications

Technical specifications for implementing the high-level SDK.

## Overview

This directory contains detailed technical specifications for implementing the Better Notion SDK high-level features. Each document answers "HOW" to implement specific features.

## Design Principles

1. **Entity-Oriented**: Autonomous entities with class methods for all operations
2. **Manager Pattern**: Ultra-thin manager wrappers for convenient access
3. **Cache First**: Minimize API calls through intelligent caching
4. **Pythonic API**: Natural, intuitive interfaces
5. **Manual Control**: Users control cache invalidation, not automatic TTLs

## Architecture Overview

```
NotionClient (Entry Point)
    ├── Managers (Ultra-thin wrappers)
    │   ├── PageManager → delegates to Page.get(), Page.create()
    │   ├── DatabaseManager → delegates to Database.get(), Database.query()
    │   ├── BlockManager → delegates to specialized block classes
    │   └── UserManager → delegates to User.get(), User.populate_cache()
    │
    └── Autonomous Entities (All logic)
        ├── Page (get, create, update, delete, navigation)
        ├── Database (get, create, query, schema introspection)
        ├── Block (base class for specialized blocks)
        │   ├── Code, Todo, Paragraph, Heading, etc.
        │   └── get, create, type-specific methods
        └── User (get, populate_cache, find methods)
```

**Key Principle**: Managers delegate 100% to entities. Entities contain all business logic and can be used independently.

## Implementation Roadmap

### Phase 1: Foundations

1. **[NotionClient](./notion-client.md)** - Client with managers as wrappers ⭐ NEW
2. **[BaseEntity](./base-entity.md)** - Abstract base class for all entities
3. **[Property Parsers](./property-parsers.md)** - Extract values from Notion properties
4. **[Cache Strategy](./cache-strategy.md)** - Two-level caching system
5. **[Navigation](./navigation.md)** - Hierarchical navigation patterns
6. **[Query Builder](./query-builder.md)** - Transform kwargs to Notion filters

### Phase 2: Managers (Wrappers)

7. **[PageManager](../managers/page-manager.md)** - Page operations wrapper ⭐ NEW
8. **[DatabaseManager](../managers/database-manager.md)** - Database operations wrapper ⭐ NEW
9. **[BlockManager](../managers/block-manager.md)** - Block operations wrapper ⭐ NEW
10. **[UserManager](../managers/user-manager.md)** - User operations wrapper ⭐ NEW

### Phase 3: Autonomous Entities

11. **[Page Model](../models/page-model.md)** - Page entity (get, create, update, navigate)
12. **[Database Model](../models/database-model.md)** - Database entity (get, create, query)
13. **[Block Model](../models/block-model.md)** - Generic Block base class
14. **[Specialized Blocks](../models/blocks-specialized.md)** - Code, Todo, Paragraph, etc.
15. **[User Model](../models/user-model.md)** - User entity

### Phase 4: Architecture Documents

16. **[Entity-Oriented Architecture](./entity-oriented-architecture.md)** - Overall design philosophy
17. **[Beyond API Helpers](./beyond-api-helpers.md)** - Why SDK matters

## Implementation Order

**Dependencies**:
```
NotionClient (holds caches, creates managers)
    ↓
Managers (store client reference, delegate to entities)
    ↓
BaseEntity (shared foundation for all entities)
    ↓
Autonomous Entities (Page, Database, Block, User)
    ├── Property Parsers (extract typed values)
    ├── Cache (local + global)
    ├── Navigation (parent, children, ancestors, descendants)
    └── Query Builder (database filtering)
```

## Key Decisions Summary

| Area | Decision | Rationale |
|------|----------|-----------|
| **Architecture** | Hybrid: Managers + Autonomous Entities | Convenience + flexibility |
| **Managers** | Ultra-thin wrappers (0 logic) | Single source of truth in entities |
| **Entities** | All logic in class methods | Autonomous, testable, reusable |
| **Client Ref** | Store NotionClient in entities | Simpler, no passing client everywhere |
| **Cache** | Two-level (global + local) | Shared cache + navigation optimization |
| **Navigation** | ancestors(), descendants() in BaseEntity | DRY, all entities inherit |
| **Query** | Pythonic kwargs → Notion filters | Simpler than verbose API JSON |
| **Blocks** | Specialized classes (Code, Todo, etc.) | Type-safe, IDE autocomplete |

## Usage Patterns

### Via Manager (Recommended)

```python
# ✅ Shorter, discoverable
page = await client.pages.get(page_id)
new_page = await client.pages.create(db, title="...")
code = await client.blocks.create_code(page, code="...")
```

### Via Entity (Advanced)

```python
# ✅ Autonomous - can be used without client
page = await Page.get(page_id, client=client)
new_page = await Page.create(parent=db, title="...", client=client)
code = await Code.create(parent=page, code="...", client=client)
```

**Both approaches work identically. Managers just delegate to entities.**

## File Structure

```
docs/sdk/
├── implementation/       # Technical specs (HOW)
│   ├── base-entity.md
│   ├── property-parsers.md
│   ├── cache-strategy.md
│   ├── navigation.md
│   ├── query-builder.md
│   └── ...
├── models/               # Model schemas
│   ├── page-model.md
│   ├── database-model.md
│   ├── block-model.md
│   └── user-model.md
├── features/             # Feature docs (WHAT)
│   ├── pages.md
│   ├── databases.md
│   └── ...
└── architecture.md       # High-level design (WHY)
```

## Reading Order

For implementers:

1. Start here ([README.md](./README.md))
2. [BaseEntity](./base-entity.md) - Understand the foundation
3. [Property Parsers](./property-parsers.md) - How to extract data
4. [Cache Strategy](./cache-strategy.md) - Caching patterns
5. Then specific model docs ([models/](../models/))

For contributors:

1. [architecture.md](../architecture.md) - Understand overall design
2. [design-philosophy.md](../design-philosophy.md) - Principles
3. Then feature docs ([features/](../features/))

## Implementation Checklist

Use this checklist to track progress:

- [ ] BaseEntity abstract class
- [ ] Property parser utilities
- [ ] Generic cache implementation
- [ ] Page SDK model
- [ ] Database SDK model
- [ ] Block SDK model
- [ ] User SDK model
- [ ] Navigation methods (parent, children)
- [ ] Query builder
- [ ] Filter translation
- [ ] Bulk operations
- [ ] Enhanced search
- [ ] Workspace manager
- [ ] Unit tests for each component
- [ ] Integration tests with real Notion API

## Contributing

When adding new features:

1. Update this roadmap
2. Create corresponding spec document
3. Add to implementation checklist
4. Update related feature documentation

## Related Documentation

- [SDK Architecture](../architecture.md) - High-level design
- [Mental Model](../mental-model.md) - Conceptual model
- [API Surface](../api-surface.md) - Public interface
