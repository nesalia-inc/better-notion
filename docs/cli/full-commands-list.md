# Complete CLI Command Specification - Agent-Focused

**Scope**: All Notion API operations via CLI
**Target**: AI Agents (not humans)
**Output**: JSON only
**Timeline**: 6-7 weeks

---

## Complete Command Tree

```
notion                              # Root command
│
├── pages                           # Page operations (11 commands)
│   ├── get <id>                    # Retrieve page by ID
│   ├── create                      # Create new page
│   ├── update <id>                 # Update page
│   ├── delete <id>                 # Delete page
│   ├── list                        # List pages (from database parent)
│   ├── search <query>              # Search pages
│   ├── restore <id>                # Restore from trash
│   ├── blocks <id>                 # Get page children (blocks)
│   ├── copy <id>                   # Copy page with children
│   ├── move <id>                   # Move page to new parent
│   └── archive <id>                # Archive page
│
├── databases                       # Database operations (10 commands)
│   ├── get <id>                    # Retrieve database
│   ├── create                      # Create database
│   ├── update <id>                 # Update database
│   ├── delete <id>                 # Delete database
│   ├── list                        # List all databases
│   ├── query <id>                  # Query database
│   ├── columns <id>                # Get database schema (properties)
│   ├── add-column <id>             # Add property to database
│   ├── remove-column <id>          # Remove property from database
│   └── rows <id>                   # Alias for query
│
├── blocks                          # Block operations (14 commands)
│   ├── get <id>                    # Retrieve block
│   ├── create                      # Create block
│   ├── update <id>                 # Update block
│   ├── delete <id>                 # Delete block
│   ├── children <id>               # List child blocks
│   ├── append <id>                 # Append block to parent
│   ├── prepend <id>                # Prepend block to parent
│   ├── insert-after <block_id>     # Insert block after another
│   ├── copy <id>                   # Copy block
│   ├── move <id>                   # Move block to new parent
│   ├── type <id>                   # Get/change block type
│   ├── paragraph                   # Create paragraph (shortcut)
│   ├── heading                     # Create heading (shortcut)
│   └── todo                        # Create todo (shortcut)
│
├── users                           # User operations (5 commands)
│   ├── get <id>                    # Retrieve user
│   ├── me                          # Current user info
│   ├── list                        # List all users
│   ├── search <query>              # Search users
│   └── avatar <id>                 # Get user avatar URL
│
├── comments                        # Comment operations (6 commands)
│   ├── get <id>                    # Retrieve comment
│   ├── create                      # Create comment
│   ├── update <id>                 # Update comment
│   ├── delete <id>                 # Delete comment
│   ├── list <parent_id>            # List comments (parent)
│   └── threads <parent_id>         # Group by discussion ID
│
├── search                          # Global search (4 commands)
│   ├── all <query>                 # Search all content types
│   ├── pages <query>               # Search pages only
│   ├── databases <query>           # Search databases only
│   └── blocks <query>              # Search blocks only
│
├── workspace                       # Workspace operations (5 commands)
│   ├── get                         # Get workspace info
│   ├── users                       # List workspace users
│   ├── invite                      # Invite user to workspace
│   ├── export                      # Export workspace (PDF/HTML)
│   └── stats                       # Workspace statistics
│
├── auth                            # Authentication (3 commands)
│   ├── login                       # Configure token
│   ├── status                      # Check authentication
│   └── logout                      # Remove credentials
│
└── config                          # Configuration (4 commands)
    ├── get <key>                   # Get config value
    ├── set <key> <value>           # Set config value
    ├── list                        # List all config
    └── reset                       # Reset to defaults
```

**Total: 62 commands**

---

## Command Categories

### 1. Pages (11 commands)

Core operations for Notion pages.

#### `notion pages get <id>`

Get a page by ID.

```bash
notion pages get page_abc123
```

**Response:**
```json
{
  "success": true,
  "data": {
    "id": "page_abc123",
    "title": "My Page",
    "parent": {
      "type": "database_id",
      "database_id": "database_xyz"
    },
    "properties": {
      "Status": {
        "type": "select",
        "select": {"name": "In Progress"}
      }
    },
    "created_time": "2025-01-25T10:00:00.000Z",
    "last_edited_time": "2025-01-25T12:00:00.000Z",
    "archived": false,
    "url": "https://notion.so/page_abc123"
  },
  "meta": {
    "version": "0.4.0",
    "timestamp": "2025-01-25T10:00:00Z",
    "rate_limit": {"remaining": 48}
  }
}
```

**Options:**
- `--idempotency-key <key>` - Cache response for idempotent retries

---

#### `notion pages create`

Create a new page.

```bash
notion pages create \
  --parent database_abc \
  --title "New Task" \
  --property "Status:Backlog" \
  --property "Priority:High" \
  --content "Task description here"
```

**Options:**
- `--parent <id>` - Parent database or page (required)
- `--title <text>` - Page title
- `--property <key:value>` - Property value (can use multiple times)
- `--property-json <json>` - Property as JSON (for complex types)
- `--content <text>` - Page content (creates paragraph block)
- `--icon <emoji|url>` - Page icon
- `--cover <url>` - Page cover image
- `--idempotency-key <key>` - Idempotency key
- `--timeout <seconds>` - Request timeout

---

#### `notion pages update <id>`

Update a page.

```bash
notion pages update page_abc \
  --title "Updated Title" \
  --property "Status:In Progress" \
  --archived false
```

**Options:**
- `--title <text>` - New title
- `--property <key:value>` - Update property
- `--property-json <json>` - Update property as JSON
- `--icon <emoji|url>` - Update icon
- `--cover <url>` - Update cover
- `--archived <true|false>` - Archive/unarchive
- `--idempotency-key <key>` - Idempotency key

---

#### `notion pages delete <id>`

Delete a page (move to trash).

```bash
notion pages delete page_abc
```

**Options:**
- `--permanent` - Permanently delete (skip trash)

---

#### `notion pages list`

List pages from a database.

```bash
notion pages list --database database_abc --limit 10
```

**Options:**
- `--database <id>` - Parent database ID (required)
- `--filter <json>` - Filter as JSON
- `--sort <property:direction>` - Sort results
- `--limit <n>` - Max results (default: 100)
- `--start-cursor <cursor>` - Pagination cursor

---

#### `notion pages search <query>`

Search for pages.

```bash
notion pages search "project planning" --limit 20
```

**Options:**
- `--filter <json>` - Search filter
- `--sort <direction>` - Sort direction
- `--limit <n>` - Max results

---

#### `notion pages restore <id>`

Restore page from trash.

```bash
notion pages restore page_abc
```

---

#### `notion pages blocks <id>`

Get page children (blocks).

```bash
notion pages blocks page_abc --limit 50
```

**Options:**
- `--limit <n>` - Max blocks
- `--start-cursor <cursor>` - Pagination

**Response:**
```json
{
  "success": true,
  "data": {
    "blocks": [
      {
        "id": "block_123",
        "type": "paragraph",
        "content": "Block content"
      }
    ],
    "next_cursor": "cursor_xyz",
    "has_more": false
  }
}
```

---

#### `notion pages copy <id>`

Copy page with all children.

```bash
notion pages copy page_abc --parent database_xyz
```

**Options:**
- `--parent <id>` - Destination parent (required)
- `--title <text>` - New title (default: same as original)

**Note:** CLI implements this recursively (Notion API doesn't have copy endpoint)

---

#### `notion pages move <id>`

Move page to new parent.

```bash
notion pages move page_abc --parent page_xyz
```

**Options:**
- `--parent <id>` - New parent (required)

---

#### `notion pages archive <id>`

Archive a page (soft delete).

```bash
notion pages archive page_abc
```

---

### 2. Databases (10 commands)

#### `notion databases get <id>`

Get database by ID.

```bash
notion databases get database_abc
```

**Response:**
```json
{
  "success": true,
  "data": {
    "id": "database_abc",
    "title": "Tasks",
    "description": "Project tasks",
    "properties": [
      {
        "id": "prop_123",
        "name": "Status",
        "type": "select",
        "select": {
          "options": [
            {"name": "Backlog", "color": "gray"},
            {"name": "In Progress", "color": "blue"}
          ]
        }
      }
    ]
  }
}
```

---

#### `notion databases create`

Create a new database.

```bash
notion databases create \
  --parent page_abc \
  --title "New Database" \
  --description "Database description"
```

**Options:**
- `--parent <id>` - Parent page (required)
- `--title <text>` - Database title
- `--description <text>` - Database description
- `--properties <json>` - Properties schema (JSON)

---

#### `notion databases update <id>`

Update database.

```bash
notion databases update database_abc \
  --title "Updated Title" \
  --properties <json>
```

**Options:**
- `--title <text>` - New title
- `--description <text>` - New description
- `--properties <json>` - Update properties

---

#### `notion databases delete <id>`

Delete database.

```bash
notion databases delete database_abc
```

---

#### `notion databases list`

List all databases in workspace.

```bash
notion databases list
```

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "id": "database_abc",
      "title": "Tasks"
    },
    {
      "id": "database_xyz",
      "title": "Projects"
    }
  ],
  "meta": {"total": 2}
}
```

---

#### `notion databases query <id>`

Query a database.

```bash
notion databases query database_abc \
  --filter '{"property":"Status","select":{"equals":"Done"}}' \
  --sort "created_time:desc" \
  --limit 10
```

**Options:**
- `--filter <json>` - Filter as JSON
- `--filter-property <name>` - Simple filter by property
- `--filter-value <value>` - Simple filter value
- `--sort <property:direction>` - Sort results
- `--limit <n>` - Max results
- `--start-cursor <cursor>` - Pagination
- `--aggregate <function>` - Aggregate function (count, avg, etc.)

---

#### `notion databases columns <id>`

Get database schema (properties).

```bash
notion databases columns database_abc
```

**Response:**
```json
{
  "success": true,
  "data": {
    "properties": [
      {"id": "title", "name": "Name", "type": "title"},
      {"id": "prop_1", "name": "Status", "type": "select"},
      {"id": "prop_2", "name": "Date", "type": "date"}
    ]
  }
}
```

---

#### `notion databases add-column <id>`

Add property to database.

```bash
notion databases add-column database_abc \
  --name "Priority" \
  --type "select" \
  --options "High,Medium,Low"
```

**Options:**
- `--name <text>` - Property name (required)
- `--type <type>` - Property type (required)
- `--options <csv>` - Options for select/multi-select

---

#### `notion databases remove-column <id>`

Remove property from database.

```bash
notion databases remove-column database_abc --property "Priority"
```

**Options:**
- `--property <name>` - Property name to remove

---

#### `notion databases rows <id>`

Alias for `query`.

```bash
notion databases rows database_abc
```

---

### 3. Blocks (14 commands)

#### `notion blocks get <id>`

Get block by ID.

```bash
notion blocks get block_abc
```

---

#### `notion blocks create`

Create a block.

```bash
notion blocks create \
  --parent page_abc \
  --type paragraph \
  --text "Block content"
```

**Options:**
- `--parent <id>` - Parent page or block (required)
- `--type <type>` - Block type (paragraph, heading, todo, etc.)
- `--text <text>` - Block text content
- `--checked <true|false>` - For todo blocks
- `--code <code>` - For code blocks
- `--language <lang>` - Code language
- `--url <url>` - For bookmark/embed blocks

---

#### `notion blocks update <id>`

Update a block.

```bash
notion blocks update block_abc --text "Updated content"
```

**Options:**
- `--text <text>` - New text content
- `--checked <true|false>` - For todo blocks
- `--type <type>` - Change block type
- `--archived <true|false>` - Archive/unarchive

---

#### `notion blocks delete <id>`

Delete a block.

```bash
notion blocks delete block_abc
```

---

#### `notion blocks children <id>`

List child blocks.

```bash
notion blocks children block_abc --limit 50
```

**Options:**
- `--limit <n>` - Max blocks
- `--start-cursor <cursor>` - Pagination

---

#### `notion blocks append <id>`

Append block to parent.

```bash
notion blocks append page_abc --type heading --text "New Section"
```

**Options:**
- Same as `create`

---

#### `notion blocks prepend <id>`

Prepend block to parent.

```bash
notion blocks prepend page_abc --type todo --text "First task"
```

**Options:**
- Same as `create`

---

#### `notion blocks insert-after <block_id>`

Insert block after another block.

```bash
notion blocks insert-after block_abc --type paragraph --text "New block"
```

**Options:**
- Same as `create`

---

#### `notion blocks copy <id>`

Copy a block.

```bash
notion blocks copy block_abc --parent page_xyz
```

**Options:**
- `--parent <id>` - Destination parent

---

#### `notion blocks move <id>`

Move block to new parent.

```bash
notion blocks move block_abc --parent page_xyz
```

**Options:**
- `--parent <id>` - New parent
- `--position <position>` - before/after/child

---

#### `notion blocks type <id>`

Get or change block type.

```bash
# Get type
notion blocks type block_abc

# Change type
notion blocks type block_abc --type heading
```

**Options:**
- `--type <type>` - New block type

---

#### `notion blocks paragraph`

Shortcut to create paragraph.

```bash
notion blocks paragraph page_abc --text "Paragraph text"
```

---

#### `notion blocks heading`

Shortcut to create heading.

```bash
notion blocks heading page_abc --text "Heading" --level 2
```

**Options:**
- `--level <n>` - Heading level (1-3, default: 1)

---

#### `notion blocks todo`

Shortcut to create todo.

```bash
notion blocks todo page_abc --text "Task" --checked false
```

---

### 4. Users (5 commands)

#### `notion users get <id>`

Get user by ID.

```bash
notion users get user_abc
```

**Response:**
```json
{
  "success": true,
  "data": {
    "id": "user_abc",
    "name": "John Doe",
    "email": "john@example.com",
    "type": "person",
    "avatar_url": "https://..."
  }
}
```

---

#### `notion users me`

Get current user info.

```bash
notion users me
```

---

#### `notion users list`

List all users in workspace.

```bash
notion users list
```

---

#### `notion users search <query>`

Search for users.

```bash
notion users search "john"
```

---

#### `notion users avatar <id>`

Get user avatar URL.

```bash
notion users avatar user_abc
```

---

### 5. Comments (6 commands)

#### `notion comments get <id>`

Get comment by ID.

```bash
notion comments get comment_abc
```

---

#### `notion comments create`

Create a comment.

```bash
notion comments create \
  --parent page_abc \
  --text "Great work!" \
  --thread comment_xyz
```

**Options:**
- `--parent <id>` - Parent page or block (required)
- `--text <text>` - Comment text
- `--thread <id>` - Discussion ID (for replies)

---

#### `notion comments update <id>`

Update comment.

```bash
notion comments update comment_abc --text "Updated comment"
```

---

#### `notion comments delete <id>`

Delete comment.

```bash
notion comments delete comment_abc
```

---

#### `notion comments list <parent_id>`

List comments for parent.

```bash
notion comments list page_abc
```

---

#### `notion comments threads <parent_id>`

List comments grouped by thread.

```bash
notion comments threads page_abc
```

**Response:**
```json
{
  "success": true,
  "data": {
    "threads": [
      {
        "discussion_id": "discussion_abc",
        "comments": [
          {"id": "comment_1", "text": "First comment"},
          {"id": "comment_2", "text": "Reply"}
        ]
      }
    ]
  }
}
```

---

### 6. Search (4 commands)

#### `notion search all <query>`

Search all content types.

```bash
notion search all "project" --limit 20
```

---

#### `notion search pages <query>`

Search pages only.

```bash
notion search pages "planning"
```

---

#### `notion search databases <query>`

Search databases only.

```bash
notion search databases "tasks"
```

---

#### `notion search blocks <query>`

Search blocks only.

```bash
notion search blocks "todo"
```

---

### 7. Workspace (5 commands)

#### `notion workspace get`

Get workspace information.

```bash
notion workspace get
```

**Response:**
```json
{
  "success": true,
  "data": {
    "id": "workspace_abc",
    "name": "My Workspace",
    "icon": "🏢",
    "created_time": "2025-01-01T00:00:00Z"
  }
}
```

---

#### `notion workspace users`

List workspace users.

```bash
notion workspace users
```

---

#### `notion workspace invite`

Invite user to workspace.

```bash
notion workspace invite --email "user@example.com"
```

**Options:**
- `--email <email>` - Email to invite

---

#### `notion workspace export`

Export workspace or page.

```bash
notion workspace export --type markdown --output ./export
```

**Options:**
- `--type <type>` - Export type (markdown, html, pdf)
- `--output <path>` - Output directory
- `--page <id>` - Export specific page

---

#### `notion workspace stats`

Workspace statistics.

```bash
notion workspace stats
```

**Response:**
```json
{
  "success": true,
  "data": {
    "total_pages": 150,
    "total_databases": 12,
    "total_users": 5,
    "storage_used": "45.2 MB"
  }
}
```

---

### 8. Auth (3 commands)

#### `notion auth login`

Configure authentication.

```bash
notion auth login
? Paste your Notion token: secret_********************
✅ Token saved to ~/.notion/config.json
```

**Options:**
- `--token <token>` - Set token non-interactively
- `--workspace <id>` - Workspace ID (for multiple workspaces)

---

#### `notion auth status`

Check authentication status.

```bash
notion auth status
✅ Authenticated
Workspace: My Workspace
User: john@example.com
Token: secret_...abc123
```

---

#### `notion auth logout`

Remove credentials.

```bash
notion auth logout
✅ Removed credentials from ~/.notion/config.json
```

---

### 9. Config (4 commands)

#### `notion config get <key>`

Get config value.

```bash
notion config get timeout
```

---

#### `notion config set <key> <value>`

Set config value.

```bash
notion config set timeout 60
notion config set default_output json
```

---

#### `notion config list`

List all config.

```bash
notion config list
```

**Response:**
```json
{
  "success": true,
  "data": {
    "token": "secret_...abc123",
    "timeout": 30,
    "default_output": "json",
    "retry_attempts": 3
  }
}
```

---

#### `notion config reset`

Reset to defaults.

```bash
notion config reset
```

---

## Implementation Plan

### Phase 1: Infrastructure (Week 1)

- [ ] CLI module structure
- [ ] Response formatter (JSON)
- [ ] Error codes and mapping
- [ ] Async helper
- [ ] Config management
- [ ] Logging

### Phase 2: Auth + Config (Week 1)

- [ ] `notion auth login`/`status`/`logout`
- [ ] `notion config get`/`set`/`list`/`reset`

### Phase 3: Pages (Week 2)

- [ ] All 11 page commands
- [ ] Idempotency support
- [ ] Atomic operations

### Phase 4: Databases (Week 3)

- [ ] All 10 database commands
- [ ] Query with filters/sorts
- [ ] Schema management

### Phase 5: Blocks (Week 4)

- [ ] All 14 block commands
- [ ] Block type conversions
- [ ] Bulk operations

### Phase 6: Users + Comments + Search (Week 5)

- [ ] 5 user commands
- [ ] 6 comment commands
- [ ] 4 search commands

### Phase 7: Workspace + Polish (Week 6)

- [ ] 5 workspace commands
- [ ] Rate limiting
- [ ] Error handling
- [ ] Documentation

### Phase 8: Testing + Release (Week 7)

- [ ] Comprehensive tests (95%+ coverage)
- [ ] Performance optimization
- [ ] Documentation
- [ ] Release v0.4.0

---

## Total Scope

- **62 commands** across 9 categories
- **6-7 weeks** implementation time
- **Agent-focused** (JSON output, reliable, no UX)
- **Production-ready** (idempotency, rate limiting, error handling)

---

This is the complete command specification for the agent-focused CLI with all Notion API operations covered.
