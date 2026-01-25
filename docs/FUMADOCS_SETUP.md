# Documentation Technology: Fumadocs

**Decision**: Using Fumadocs for the Better Notion SDK documentation website.

## What is Fumadocs?

Fumadocs is a modern documentation framework designed to be fast, flexible, and composable with React frameworks.

## Architecture

### Components

| Component | Purpose |
|-----------|---------|
| **Fumadocs Core** | Logic: search, content adapters, Markdown extensions |
| **Fumadocs UI** | Default theme, beautiful look, interactive components |
| **Content Source** | CMS or local (Fumadocs MDX for local MDX files) |
| **Fumadocs CLI** | Install UI components, automation |

## Requirements

- **Node.js 22+** (minimum)
- **React knowledge** (for customizations)
- **Bun** (for running scripts)

## Installation Command

```bash
npm create fumadocs-app
```

**Template choices**:
- React framework: Next.js, Waku, React Router, or Tanstack Start
- Content source: Fumadocs MDX

## Project Structure

```
docs-site/                    # New separate repo or subdirectory
├── content/
│   └── docs/                # MDX files go here
│       ├── index.mdx        # Home page
│       ├── quickstart.mdx
│       └── ...
├── app/                     # Next.js app directory
├── components/              # Custom components
├── lib/                     # Fumadocs configuration
├── package.json
└── fumadocs.json           # Fumadocs config
```

## Content Format

**MDX files** with frontmatter:

```mdx
---
title: Quick Start
description: Get started with Better Notion in 5 minutes
---

## Content here...
```

## Key Differences from MkDocs

| Aspect | MkDocs | Fumadocs |
|--------|--------|----------|
| **Format** | Markdown | MDX (Markdown + JSX) |
| **Runtime** | Python | Node.js/React |
| **Hosting** | Any static host | Vercel, Netlify, or static export |
| **Customization** | Limited themes | Full React component power |
| **Search** | Built-in (lunr.js) | Built-in (flexible) |
| **Language** | Jinja2 templates | React/JSX |

## Migration Plan

1. **Phase 1**: Set up Fumadocs project
   - Initialize with Next.js template
   - Configure Fumadocs MDX
   - Set up basic navigation

2. **Phase 2**: Create content structure
   - Convert documentation plan to MDX files
   - Set up navigation tree
   - Configure metadata

3. **Phase 3**: Author content
   - Write documentation in MDX
   - Add code examples with syntax highlighting
   - Create interactive components if needed

4. **Phase 4**: Deploy
   - Configure build
   - Deploy to Vercel/Netlify (or internal hosting)

## Advantages for This Project

✅ **Modern & Fast**: Built on Next.js, excellent performance
✅ **Flexible**: Can create custom React components for docs
✅ **Great DX**: Hot reload, TypeScript support
✅ **Searchable**: Built-in fuzzy search
✅ **MDX**: Can embed interactive code examples
✅ **Themeable**: Easy to customize for company branding

## Notes

- Separate from Python SDK repository (frontend project)
- Can host on Vercel, Netlify, or export static for internal hosting
- Build process: MDX → static HTML/CSS/JS
- Can integrate with company design system

## Next Steps (When Ready)

1. Create documentation site project: `npm create fumadocs-app`
2. Choose Next.js + Fumadocs MDX template
3. Configure navigation structure
4. Start writing content in MDX format
5. Deploy and integrate with company infrastructure

---

**Status**: ✅ Decision made, not yet implemented
**Documentation Structure**: See `DOCUMENTATION_STRUCTURE.md` for content plan
