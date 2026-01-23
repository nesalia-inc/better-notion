# SDK Architecture

## Two-Level Design

Better Notion SDK provides two distinct levels of abstraction to accommodate different use cases and developer preferences.

## Level 1: Low-Level API (`NotionAPI`)

### Purpose
Direct mapping to the Notion REST API with minimal abstraction.

### Characteristics
- 1:1 mapping with Notion API endpoints
- Method names mirror endpoint names (`blocks.retrieve`, `databases.query`)
- Parameters match API specifications exactly
- Returns raw or minimally processed responses
- No caching, no state management
- Full access to all API features

### Target Users
- Developers already familiar with the Notion API
- Migrations from other Notion SDKs
- Use cases requiring precise control
- Access to new API features immediately

### Example Usage
```python
api = NotionAPI(auth=token)

# Direct API mapping
response = await api.blocks.retrieve(block_id="...")
response = await api.databases.query(
    database_id="...",
    filter={"property": "Status", "select": {"equals": "Done"}}
)
```

### Design Principles
- Fidelity to the API
- Predictable behavior
- No hidden magic
- Transparent error responses
- Explicit pagination handling

## Level 2: High-Level Client (`NotionClient`)

### Purpose
Rich abstraction layer that prioritizes developer experience and productivity.

### Characteristics
- Object-oriented entity model (Page, Database, Block)
- Semantic methods that map to user intent
- Automatic caching for instant lookups
- Intelligent pagination with async iterators
- Opinionated conventions for common operations
- Composed operations (multiple API calls in one method)
- Type-safe with comprehensive type hints

### Target Users
- Developers new to Notion API
- Rapid application development
- Standard business applications
- Developers prioritizing ergonomics

### Example Usage
```python
client = NotionClient(auth=token)

# Rich entities with methods
page = await client.pages.get(page_id)
print(page.title)  # Direct property access

# Semantic operations
tasks = await client.databases.get(database_id)
in_progress = await tasks.query(status="In Progress")

# Hierarchical navigation
parent = await page.parent
children = await page.children

# Built-in features not in API
all_pages = await client.pages.all()  # API doesn't have "list all"
user = client.users.cache.get(user_id)  # Instant cache lookup
```

### Design Principles
- Developer experience first
- Pragmatic defaults
- Hide complexity behind intuitive interfaces
- Cache-first where appropriate
- Fail with helpful errors

## Technical Architecture

### Dependency Graph
```
NotionClient (High Level)
    └── uses → NotionAPI (Low Level)
                  └── uses → HTTP Client (httpx)
```

### Implementation Strategy

#### Low-Level (`NotionAPI`)
- Independent module
- Can be used standalone
- Thin wrapper around HTTP client
- Handles authentication, rate limiting headers
- Minimal data transformation

#### High-Level (`NotionClient`)
- Builds on top of `NotionAPI`
- Managers for each resource (pages, databases, blocks, users)
- Entity models with rich behavior
- Cache layer
- Validation and transformation

#### Coexistence
Both levels can be used simultaneously:

```python
# Use high-level by default
client = NotionClient(auth=token)

# Access low-level when needed
raw_response = await client._api.blocks.retrieve(block_id)

# Or create independently
api = NotionAPI(auth=token)
```

## Feature Distribution

### Low-Level Features
- All CRUD operations
- Query and filter endpoints
- Search
- File uploads
- User retrieval
- Comment operations
- Block operations

### High-Level Exclusive Features
- Cache management
- Async iterators for pagination
- Semantic list operations (`.all()`, `.filter()`)
- Hierarchical navigation (`.parent`, `.children`)
- Bulk operations
- Property shortcuts (`.title`, `.status`)
- Local search in cache
- Operation composition
- Smart defaults and conventions

## Maintenance Strategy

### New Notion API Features
1. Immediately available in low-level `NotionAPI`
2. Added to high-level `NotionClient` when:
   - Commonly used
   - Can be improved with abstraction
   - Fits the mental model

### Version Compatibility
- Low-level tracks Notion API version closely
- High-level provides stable abstraction across API changes
- Breaking changes in high-level minimized through careful design

## Migration Path

Users can:
1. Start with high-level for productivity
2. Drop to low-level for edge cases
3. Use both in same application
4. Gradually migrate from low to high-level

## Documentation Strategy

### Low-Level Documentation
- API reference mirroring Notion docs
- Parameter specifications
- Response structure details
- Examples showing direct API usage

### High-Level Documentation
- Conceptual guides
- Usage patterns
- Best practices
- Examples focusing on productivity
- Migration guide from low-level

## Benefits of Two-Level Architecture

### For Users
- Choice based on needs
- Gradual learning curve
- No lock-in to one style
- Future-proof (low-level always available)

### For Maintainers
- Clear separation of concerns
- Low-level is stable (changes with API)
- High-level can evolve independently
- Easy to test each level

### For Ecosystem
- Multiple SDKs can build on same low-level
- Community can extend high-level patterns
- Clear extension points
