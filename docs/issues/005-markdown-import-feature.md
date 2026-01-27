# Feature Request: Create/Update Pages from Markdown Files

## Summary
Add ability to create and update Notion pages directly from markdown files instead of running multiple CLI commands.

## Motivation

### Current Workflow (Painful)
Creating a complex page requires 30+ CLI commands:
```bash
notion pages create --parent <db_id> --title "Python Course"
notion blocks heading --parent <page_id> --text "Chapter 1" --level 1
notion blocks paragraph --parent <page_id> --text "Introduction..."
notion blocks code --parent <page_id> --code "print('hello')"
# ... 25+ more commands
```

### Proposed Workflow (Simple)
```bash
notion pages create-from-md --file course.md --parent <db_id>
```

### Use Cases
1. **Documentation teams** - Write docs locally, push to Notion
2. **Content migration** - Convert existing markdown repos to Notion
3. **Note-taking** - Quick sync from local editor to Notion
4. **Version control** - Keep Notion content in git
5. **Backup/restore** - Export and restore Notion pages

## Proposed CLI Interface

### Create Page from Markdown
```bash
notion pages create-from-md [OPTIONS]

Options:
  --file, -f PATH      Markdown file to import [required]
  --parent, -p TEXT    Parent database ID [required]
  --title TEXT         Custom title (default: first H1 or filename)
  --icon EMOJI         Page icon
  --cover URL          Cover image URL
  --dry-run           Show what would be created without creating
```

### Update Existing Page
```bash
notion pages update-from-md [OPTIONS]

Options:
  --file, -f PATH      Markdown file [required]
  --page, -p TEXT      Page ID to update [required]
  --sync, -s           Sync strategy: replace|merge|smart [default: smart]
```

### Watch and Auto-Sync
```bash
notion pages watch [OPTIONS]

Options:
  --file, -f PATH      Markdown file to watch [required]
  --page, -p TEXT      Page ID to update [required]
  --debounce MS        Debounce delay in ms [default: 1000]
```

## Markdown to Notion Block Mapping

### Standard Mapping (Table 1)
| Markdown | Notion Block |
|----------|--------------|
| `# H1` | Heading 1 |
| `## H2` | Heading 2 |
| `### H3` | Heading 3 |
| Plain text | Paragraph |
| `- item` | Bullet list |
| `1. item` | Numbered list |
| `> quote` | Quote |
| `` `code` `` | Code (inline) |
| ` ```lang\n...\n``` ` | Code block |
| `---` or `***` | Divider |

### Advanced Syntax (Table 2)
| Markdown | Notion Block |
|----------|--------------|
| `:::callout 💡\nText\n:::` | Callout with icon |
| `:::todo\nTask\n:::` | Todo (unchecked) |
| `:::todo checked\nTask\n:::` | Todo (checked) |
| `[x] Task` | Todo (checked) |
| `[ ] Task` | Todo (unchecked) |
| `[!TIP]` | Callout with 💡 |
| `[!WARNING]` | Callout with ⚠️ |
| `[!IMPORTANT]` | Callout with ⭐ |

### Example Markdown File
```markdown
# Python Course

## Chapter 1: Introduction

Python is a high-level programming language.

### Key Features
- Easy to learn
- Powerful libraries
- Large community

### Installation Steps
1. Download Python from python.org
2. Run the installer
3. Verify installation

### Example Code
\`\`\`python
print("Hello, World!")

name = "Alice"
age = 25
print(f"{name} is {age} years old")
\`\`\`

> "Code is read much more often than it is written."
> — Guido van Rossum

## Exercises

:::callout 💡
Remember to use proper indentation (4 spaces)!
:::

- [ ] Install Python
- [ ] Write your first program
- [ ] Complete the exercises
```

## Implementation Phases

### Phase 1: Basic Import (MVP)
- Parse markdown file
- Map basic elements (headings, paragraphs, lists, code, quotes)
- Create page with blocks
- Error handling and validation

**Dependencies**: `markdown-it` (already in project)

### Phase 2: Advanced Syntax
- Callouts with custom syntax
- Todo items (`[ ]` and `:::todo`)
- Dividers
- Nested lists

### Phase 3: Smart Sync
- Update existing pages
- Match blocks by content/hash
- Preserve unchanged blocks
- Handle reordering

### Phase 4: Watch Mode
- File watcher for auto-sync
- Debounce rapid changes
- Conflict resolution

## Technical Considerations

### Parser Library
The project already uses `markdown-it` (in dependencies). Extend with:
- Custom plugins for Notion-specific syntax
- AST traversal for block extraction
- Preserve source positions for error reporting

### Block Matching for Updates
For smart sync, need to:
1. Calculate hash of each block's content
2. Match existing blocks by hash + type
3. Update changed blocks, delete removed, add new
4. Preserve block IDs to maintain links/references

### Error Handling
```python
# Show helpful errors
notion pages create-from-md course.md
# Error: Line 15: Unclosed code block
#    15 | ```python
#    16 | print("test"
#    17 | Missing closing ```
```

## Edge Cases to Handle

1. **Empty files** → Create empty page or error?
2. **No H1 in file** → Use filename as title
3. **Multiple H1s** → First one is page title, rest are headings
4. **Deep nesting** → Notion supports limited nesting
5. **Huge files** → Chunk into multiple pages?
6. **Images** - Upload or keep as external URLs
7. **Links** - Convert to Notion format
8. **Tables** - Complex, maybe Phase 2+

## Examples

### Example 1: Create Course
```bash
# Create comprehensive Python course
notion pages create-from-md --file python-course.md --parent <db_id>

# With custom icon
notion pages create-from-md \
  --file python-course.md \
  --parent <db_id> \
  --icon "🐍"
```

### Example 2: Update Documentation
```bash
# Update docs after local edits
notion pages update-from-md \
  --file README.md \
  --page <page_id> \
  --sync smart
```

### Example 3: Watch Mode
```bash
# Auto-sync while editing
notion pages watch \
  --file notes.md \
  --page <page_id> \
  --debounce 2000

# Edit file in VS Code
# Every 2 seconds, changes automatically sync to Notion
```

## Related Features
- Export to markdown (already exists in Notion web)
-双向同步 (Two-way sync)
- Batch import multiple files
- Recursive directory import

## Benefits

1. **Productivity** - 10x faster than manual commands
2. **Developer Experience** - Natural workflow
3. **Version Control** - Content in git
4. **Offline Editing** - Work without internet
5. **CI/CD Integration** - Auto-generate docs from code
6. **Differentiation** - No other Notion CLI has this

## Potential Challenges

1. **Table support** - Complex table formatting
2. **Block references** - Hard to preserve in markdown
3. **Databases** - Not representable in markdown
4. **Sync conflicts** - Concurrent edits
5. **Performance** - Large files (1000+ blocks)

## Success Metrics
- Usage: % of pages created from markdown
- Time savings: Compare command-based vs file-based
- User feedback: Satisfaction with mapping accuracy
