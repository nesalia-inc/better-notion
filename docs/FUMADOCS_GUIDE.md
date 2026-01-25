# Fumadocs Quick Reference Guide

This guide serves as a quick reference for working with Fumadocs when building the Better Notion SDK documentation.

## Table of Contents

1. [MDX Syntax](#mdx-syntax)
2. [Frontmatter](#frontmatter)
3. [Components](#components)
4. [Layout Configuration](#layout-configuration)
5. [File Organization](#file-organization)
6. [Navigation](#navigation)
7. [Code Blocks](#code-blocks)

---

## MDX Syntax

### Basic Markdown

MDX is a superset of Markdown with JSX support.

```mdx
## Heading
### Heading
#### Heading

**Bold**, _Italic_, ~~Strikethrough~~

1. Ordered list
2. Item two

- Unordered list
- Item two

> Quote block

[Link text](https://example.com)

![Alt text](/image.png)

| Table Header | Description |
| ------------ | ----------- |
| Row 1        | Data        |
```

### JSX Components

Import and use React components in your MDX:

```mdx
import { Component } from './component';

<Component name="Hello" />
```

---

## Frontmatter

YAML-based metadata at the top of each MDX file:

```mdx
---
title: Page Title
description: Page description for SEO
icon: HomeIcon
---

Content goes here...
```

### Supported Properties

| Property | Description |
|----------|-------------|
| `title` | Page title (H1) |
| `description` | SEO description |
| `icon` | Icon name for sidebar |

**Note**: H1 headings are usually unnecessary as `title` in frontmatter serves as the page title.

---

## Components

### Callouts

Add tips, warnings, or notes:

```mdx
<Callout>
  Default info callout
</Callout>

<Callout type="warning" title="Warning">
  Warning message
</Callout>

<Callout type="error" title="Error">
  Error message
</Callout>

<Callout type="success" title="Success">
  Success message
</Callout>

<Callout type="idea" title="Idea">
  Idea or tip
</Callout>
```

### Cards

Useful for linking to related content:

```mdx
import { HomeIcon } from 'lucide-react';

<Cards>
  <Card
    href="/docs/guide"
    title="Guide Title"
    icon={<HomeIcon />}
  >
    Card description
  </Card>
  <Card title="No href">
    This card has no link
  </Card>
</Cards>
```

### Tabs

Group content into tabs:

```mdx
<Tabs>
  <Tab label="Tab 1">
    Content 1
  </Tab>
  <Tab label="Tab 2">
    Content 2
  </Tab>
</Tabs>
```

### Steps

Step-by-step instructions:

```mdx
<Steps>
  <Step>
    ### Step 1

    First step content
  </Step>
  <Step>
    ### Step 2

    Second step content
  </Step>
</Steps>
```

---

## Layout Configuration

### Docs Layout

Main documentation layout with sidebar:

```tsx
import { DocsLayout } from 'fumadocs-ui/layouts/docs';
import { source } from '@/lib/source';
import type { ReactNode } from 'react';

export default function Layout({ children }: { children: ReactNode }) {
  return (
    <DocsLayout tree={source.getPageTree()}>
      {children}
    </DocsLayout>
  );
}
```

### Home Layout

Landing page layout:

```tsx
import { HomeLayout } from 'fumadocs-ui/layouts/home';
import type { ReactNode } from 'react';

export default function Layout({ children }: { children: ReactNode }) {
  return (
    <HomeLayout>
      {children}
    </HomeLayout>
  );
}
```

### Layout Links

Add navigation links to layouts:

```tsx
import { BookIcon } from 'lucide-react';
import type { BaseLayoutProps } from 'fumadocs-ui/layouts/shared';

export function baseOptions(): BaseLayoutProps {
  return {
    links: [
      {
        icon: <BookIcon />,
        text: 'Blog',
        url: '/blog',
      },
      {
        type: 'menu',
        text: 'Resources',
        items: [
          {
            text: 'Getting Started',
            description: 'Learn the basics',
            url: '/docs/getting-started',
          },
        ],
      },
    ],
    githubUrl: 'https://github.com/user/repo',
  };
}
```

### Link Types

| Type | Description |
|------|-------------|
| Default | Standard link with icon |
| `icon` | Icon-only button |
| `menu` | Dropdown menu with items |
| `custom` | Custom React component |

---

## File Organization

### Basic Structure

```
content/docs/
├── index.mdx                    # /docs
├── getting-started.mdx          # /docs/getting-started
├── guides/
│   ├── index.mdx                # /docs/guides
│   ├── pages.mdx                # /docs/guides/pages
│   └── meta.json                # Folder configuration
└── (group-name)/                # Group folder (no slug impact)
    └── page.mdx                 # /docs/page
```

### Folder Configuration (meta.json)

```json
{
  "title": "Display Name",
  "description": "Folder description",
  "icon": "MyIcon",
  "defaultOpen": true,
  "collapsible": true,
  "pages": ["index", "getting-started"]
}
```

### meta.json Properties

| Property | Description |
|----------|-------------|
| `title` | Display name |
| `description` | Folder description |
| `icon` | Icon name |
| `defaultOpen` | Open folder by default |
| `collapsible` | Allow collapse/expand |
| `pages` | Ordered list of items |
| `root` | Mark as root folder (tab) |

### pages Array Syntax

```json
{
  "pages": [
    "index",                    # Include page
    "---Separator---",          # Separator
    "[Icon]---Separator---",    # Separator with icon
    "...folder",                # Extract from folder
    "...",                      # Include all remaining
    "!file",                    # Exclude item
    "[Text](url)",              # Link
    "external:[Text](url)"      # External link
  ]
}
```

### Root Folders (Tabs)

Folders marked as `root: true` create sidebar tabs:

```json
{
  "title": "Components",
  "description": "UI Components",
  "root": true
}
```

Only one root folder is visible at a time.

---

## Navigation

### Auto Links

Internal links use framework's `<Link />` for prefetching:

```mdx
[Internal Link](/docs/page)
```

External links get `rel="noreferrer noopener"`:

```mdx
[External Link](https://example.com)
```

### Heading Anchors

Auto-generated anchors for headings:

```mdx
## My Heading [#custom-anchor]

[!toc]     # Hide from TOC
[toc]      # TOC only (not rendered)
```

Link to heading: `/docs/page#custom-anchor`

---

## Code Blocks

### Basic Syntax Highlighting

``````mdx
```js
console.log('Hello World');
```
``````

### With Title

``````mdx
```js title="Filename"
console.log('Hello World');
```
``````

### Line Numbers

``````mdx
```js lineNumbers
console.log('Line 1');
console.log('Line 2');
```

```js lineNumbers=10
console.log('Starts from line 10');
```
``````

### Highlight Lines

``````mdx
```tsx
<div>Hello</div> // [!code highlight]
```
``````

### Word Highlight

``````mdx
```tsx
// [!code word:Fumadocs]
console.log('Fumadocs is great');
```
``````

### Diff Style

``````mdx
```ts
console.log('old'); // [!code --]
console.log('new'); // [!code ++]
```
``````

### Tab Groups

``````mdx
```ts tab="Tab 1"
console.log('A');
```

```ts tab="Tab 2"
console.log('B');
```
``````

---

## Source Configuration

### Basic Setup (lib/source.ts)

```ts
import { loader } from 'fumadocs-core/source';
import { createMDX } from 'fumadocs-mdx';

export const source = loader({
  baseUrl: '/docs',
  source: createMDX()
    .pages()
    .mapDocument((page) => ({
      ...page,
      meta: {
        title: page.frontmatter.title,
        description: page.frontmatter.description,
      },
    })),
});
```

---

## Best Practices

### 1. Content Structure

- Use `index.mdx` for folder overview pages
- Group related content in folders
- Use `meta.json` to control order and display

### 2. Frontmatter

Always include at least `title`:

```mdx
---
title: Page Title
description: Clear description
---
```

### 3. Code Examples

- Add titles to code blocks for context
- Use line numbers for long examples
- Highlight important lines

### 4. Callouts

- Use `warning` for breaking changes
- Use `error` for critical issues
- Use `success` for completed states
- Use `info` for general notes

### 5. Navigation

- Keep sidebar shallow (max 3 levels)
- Use root folders for large sections
- Add descriptions to menu items

---

## Common Patterns

### API Reference Page

```mdx
---
title: API Reference
description: Complete API reference
---

## Methods

### MethodName

Description of method.

#### Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `param1` | `string` | Description |

#### Returns

`Promise<void>`

#### Example

```ts
await methodName('value');
```
```

### Getting Started Guide

```mdx
---
title: Getting Started
---

## Prerequisites

- Node.js 18+
- Python 3.10+

## Installation

<Steps>
  <Step>
    ### Step 1: Install

    Run this command:
  </Step>
  <Step>
    ### Step 2: Configure

    Set up config
  </Step>
</Steps>
```

---

## Useful Resources

- [Fumadocs Documentation](https://fumadocs.vercel.app/)
- [MDX Syntax](https://mdxjs.com/docs/syntax/)
- [Next.js App Router](https://nextjs.org/docs/app)
