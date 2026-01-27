## Overview
This PR implements a comprehensive plugin system for the Better Notion CLI, allowing users to extend CLI functionality through custom plugins. This addresses Issue #12.

## Features Implemented

### 1. Plugin Interface & Protocol
- CommandPlugin protocol for CLI commands
- DataPlugin protocol for data processing
- PluginInterface base class with validation

### 2. Plugin Loader
- Discovers plugins from multiple directories
- Supports function-based and class-based plugins
- Configuration management

### 3. Plugin CLI Commands
- add: Install from git/PyPI/local
- remove: Uninstall plugins
- list: List all plugins
- info: Show plugin details
- init: Create new plugin (scaffolding)
- validate: Validate plugin structure
- enable/disable: Manage active plugins
- update: Update git-based plugins

### 4. Official Plugins
- Productivity plugin with commands:
  - quick-capture
  - inbox-zero
  - my-tasks
  - daily-notes

### 5. Comprehensive Tests
- Plugin interface tests
- Loader tests
- Official plugin tests

### 6. Documentation
- Plugin system overview
- Installation and usage guides
- Plugin development tutorial
- Examples and troubleshooting

## Benefits
- Portable plugins (git-tracked code)
- Team distribution
- Custom workflows
- Version controlled
- CI/CD friendly

Closes #12
