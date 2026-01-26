# Async Support Decision for CLI

**Status**: Accepted
**Date**: 2025-01-26
**Decision**: Use AsyncTyper wrapper for async command support
**Document Version**: 1.0

---

## Executive Summary

This document records the technical decision for handling async/sync mismatch between Typer (sync) and the Better Notion SDK (async). After analyzing 5 years of community discussion on Typer issue #1309, we recommend implementing an `AsyncTyper` wrapper class.

**Key Finding**: The async/sync mismatch risk identified in `risks-and-challenges.md` is **confirmed** as a real, ongoing issue with no native solution after 5 years.

---

## Problem Statement

### The Core Issue

- **Typer** is fundamentally synchronous (built on Click)
- **Better Notion SDK** is entirely asynchronous (built on httpx + asyncio)
- Result: Cannot use `@app.command()` decorators with async functions directly

### Example of the Problem

```python
# ❌ DOESN'T WORK
from typer import Typer

app = Typer()

@app.command()
async def get_page(page_id: str):
    # RuntimeWarning: coroutine 'PageManager.get' was never awaited
    async with NotionClient(auth=token) as client:
        page = await client.pages.get(page_id)
        return page
```

### Why This Matters

For an **agent-focused CLI**, reliability is critical (P0 requirement). Creating a new event loop for every command is:
1. **Slow**: Event loop creation is expensive
2. **Unreliable**: Can't share connections between commands
3. **Wasteful**: Resources allocated/deallocated repeatedly

---

## Analysis: Typer Issue #1309

### Overview

- **Issue**: [fastapi/typer#1309](https://github.com/fastapi/typer/discussions/1309)
- **Opened**: April 13, 2020
- **Status**: Still open as of January 2025 (5 years!)
- **Participants**: 42 developers, 79 comments

### Key Insights from Discussion

#### 1. No Native Solution After 5 Years 🔴

**Timeline**:
- 2020: Issue opened by @csheppard
- 2021-2023: Community workarounds proposed
- September 2023: @tiangolo (maintainer) states:
  > *"I want to add support for async in Typer, without making it required or default, using AnyIO as an optional dependency. This is one of the top priorities for Typer."*
- 2025: **Still no implementation**

#### 2. Common Problems Reported

Multiple developers report the same issue:
- RuntimeWarning: coroutine was never awaited
- Nested event loops causing crashes
- No way to share async context between commands
- Testing complications with pytest-asyncio

#### 3. Community Solutions Evaluated

The community has proposed several workarounds (see "Options Evaluated" below).

#### 4. Users Switching Frameworks

Some users abandoned Typer entirely:
- @borissmidt: *"I switched to golang"*
- @borissmidt: *"Recently I made a python CLI using cyclopts which comes with async support out of the box"*

---

## Options Evaluated

### Option 1: asyncio.run() in Each Command ❌

```python
import asyncio
import typer

def get_page(page_id: str):
    async def _get():
        async with NotionClient(auth=token) as client:
            return await client.pages.get(page_id)

    result = asyncio.run(_get())
    return result
```

**Pros**:
- ✅ Simple to implement
- ✅ No external dependencies

**Cons**:
- ❌ Creates new event loop for each command
- ❌ Poor performance (event loop creation is expensive)
- ❌ Can't share connections between commands
- ❌ Potential for nested event loop errors

**Verdict**: Not suitable for production CLI requiring high reliability.

---

### Option 2: Decorator Pattern ⭐⭐

```python
from functools import wraps
import anyio

def run_async(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        return anyio.run(func(*args, **kwargs))
    return wrapper

@app.command()
@run_async
async def get_page(page_id: str):
    async with NotionClient(auth=token) as client:
        return await client.pages.get(page_id)
```

**Pros**:
- ✅ Cleaner than inline asyncio.run()
- ✅ Supports anyio (asyncio/trio compatibility)
- ✅ Reusable decorator

**Cons**:
- ❌ Must add decorator to every async command
- ❌ AnyIO dependency required
- ❌ Still creates new event loop each time

**Verdict**: Workable but not ideal for large CLI (62 commands).

---

### Option 3: AsyncTyper Custom Class ⭐⭐⭐ **RECOMMENDED**

```python
import inspect
from functools import partial, wraps
import asyncer
from typer import Typer

class AsyncTyper(Typer):
    @staticmethod
    def maybe_run_async(decorator, f):
        if inspect.iscoroutinefunction(f):
            @wraps(f)
            def runner(*args, **kwargs):
                return asyncer.runnify(f)(*args, **kwargs)
            decorator(runner)
        else:
            decorator(f)
        return f

    def command(self, *args, **kwargs):
        decorator = super().command(*args, **kwargs)
        return partial(self.maybe_run_async, decorator)

app = AsyncTyper()

@app.command()
async def get_page(page_id: str):
    """Works natively with async!"""
    async with NotionClient(auth=token) as client:
        return await client.pages.get(page_id)

@app.command()
def hello():
    """Sync commands still work"""
    print("Hello")
```

**Pros**:
- ✅ Transparent async/sync support
- ✅ No decorator needed on each command
- ✅ Compatible with existing Typer API
- ✅ Validated by community (used in production)
- ✅ Minimal code changes required

**Cons**:
- ⚠️ Custom class to maintain
- ⚠️ `asyncer` dependency required

**Verdict**: **Best option** for our use case. Community-tested and proven.

---

### Option 4: Switch to cyclopts ⚠️

**cyclopts** is a newer CLI framework with native async support:

```python
from cyclopts import App

app = App()

@app.command
async def get_page(page_id: str):
    async with NotionClient(auth=token) as client:
        return await client.pages.get(page_id)
```

**Pros**:
- ✅ Native async support (no workaround)
- ✅ Similar API to Typer
- ✅ Active development
- ✅ Better Enum handling

**Cons**:
- ❌ Framework change (rewrite docs/cli/*)
- ❌ Younger ecosystem (fewer users)
- ❌ Less mature than Typer
- ❌ Unknown performance characteristics

**Verdict**: Good fallback option if AsyncTyper proves problematic.

---

### Option 5: asyncclick (Fork of Click) ❌

```python
import asyncclick as click

@click.command()
async def get_page(page_id: str):
    async with NotionClient(auth=token) as client:
        return await client.pages.get(page_id)
```

**Pros**:
- ✅ Native async support

**Cons**:
- ❌ Fork of Click (maintenance risk)
- ❌ Not integrated with Typer
- ❌ Loses Typer's type hints magic
- ❌ Smaller community

**Verdict**: Not recommended. Too much divergence from Typer ecosystem.

---

### Option 6: Sync Wrapper around NotionClient ❌

```python
class SyncNotionClient:
    def __init__(self, auth: str):
        self._client = NotionClient(auth=auth)
        self._loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self._loop)

    def pages_get(self, page_id: str):
        return self._loop.run_until_complete(
            self._client.pages.get(page_id)
        )
```

**Pros**:
- ✅ Keeps CLI synchronous

**Cons**:
- ❌ Massive code duplication
- ❌ Architectural antipattern
- ❌ Maintenance nightmare
- ❌ Defeats purpose of async SDK

**Verdict**: Strongly discouraged.

---

## Decision Matrix

| Criterion | AsyncTyper | cyclopts | Decorator | asyncio.run() |
|-----------|------------|----------|-----------|---------------|
| **Code Complexity** | 🟡 Medium | 🟢 Low | 🟡 Medium | 🟢 Low |
| **Maintenance** | 🟡 Custom | 🟢 Native | 🔴 Repetitive | 🟡 Manual |
| **Performance** | 🟢 Good | 🟢 Good | 🟡 Medium | 🔴 Poor |
| **Developer Experience** | 🟢 Transparent | 🟢 Transparent | 🟡 Verbose | 🔴 Verbose |
| **Documentation Impact** | ✅ Compatible | ❌ Rewrite | ✅ Compatible | ✅ Compatible |
| **Risk Level** | 🟡 Medium | 🟡 Low | 🟡 Medium | 🔴 High |
| **Community Validation** | ✅ Yes | ⚠️ New | ✅ Yes | ✅ Yes |

**Winner**: **AsyncTyper**

---

## Final Decision

### **Choice: AsyncTyper**

We will implement an `AsyncTyper` wrapper class that:
1. Extends `typer.Typer`
2. Automatically detects async functions with `inspect.iscoroutinefunction()`
3. Runs async commands via `asyncer.runnify()`
4. Passes sync commands through unchanged

### Rationale

1. **Validated by Community**: Used in production by multiple developers (see Typer #1309)
2. **Minimal Code Changes**: Works with existing Typer API
3. **Documentation Compatible**: No need to rewrite `docs/cli/`
4. **Performance**: Acceptable for agent use case (single-shot commands)
5. **Fallback Path**: Can switch to cyclopts if needed

---

## Implementation Plan

### Phase 0: Proof of Concept (Week 1)

**Goal**: Validate AsyncTyper works with Better Notion SDK.

**Tasks**:
- [ ] Create `better_notion/_cli/async_typer.py`
- [ ] Implement `AsyncTyper` class (see code below)
- [ ] Add `asyncer` to dependencies
- [ ] Create test command: `notion pages get <id>`
- [ ] Benchmark: cold start, warm start, memory usage
- [ ] Test error handling: network failures, invalid tokens
- [ ] **Go/No-Go decision**: Continue or switch to cyclopts?

### Phase 1: Update Dependencies

**File**: `pyproject.toml`

```toml
[project.optional-dependencies]
cli = [
    "typer>=0.12.0,<0.13.0",
    "rich>=13.0.0,<14.0.0",
    "asyncer>=0.0.5",  # Added for async support
]
```

### Phase 2: Core Infrastructure

**Files**:
- `better_notion/_cli/async_typer.py` (new)
- `better_notion/_cli/main.py` (update to use AsyncTyper)
- `better_notion/_cli/config.py` (unchanged)
- `better_notion/_cli/response.py` (unchanged)

### Phase 3: Migrate Commands

Convert all command files to use AsyncTyper:

```python
# before
from typer import Typer
app = Typer()

# after
from ..async_typer import AsyncTyper
app = AsyncTyper()
```

---

## Code: AsyncTyper Implementation

```python
# better_notion/_cli/async_typer.py
"""
AsyncTyper - Typer with async command support

Based on community solutions from:
https://github.com/fastapi/typer/discussions/1309

This class extends typer.Typer to automatically detect and run async functions
using asyncer.runnify(), while passing sync functions through unchanged.
"""
from __future__ import annotations

import inspect
from functools import partial, wraps
from typing import Any, Callable

import asyncer
from typer import Typer
from typer.core import TyperCommand
from typer.models import CommandFunctionType, Default


class AsyncTyper(Typer):
    """
    Typer subclass with automatic async command support.

    Features:
    - Detects async functions automatically via inspect.iscoroutinefunction()
    - Runs async commands with asyncer.runnify()
    - Passes sync commands through unchanged
    - Compatible with all Typer features (options, arguments, callbacks, etc.)

    Example:
        app = AsyncTyper()

        @app.command()
        async def async_command(name: str):
            await do_something_async(name)

        @app.command()
        def sync_command(name: str):
            do_something_sync(name)
    """

    @staticmethod
    def maybe_run_async(
        decorator: Callable[[CommandFunctionType], Any],
        f: CommandFunctionType,
    ) -> CommandFunctionType:
        """
        Run async functions with asyncer, sync functions normally.

        Args:
            decorator: Typer's command decorator
            f: Command function (sync or async)

        Returns:
            The wrapped function
        """
        if inspect.iscoroutinefunction(f):
            @wraps(f)
            def runner(*args: Any, **kwargs: Any) -> Any:
                return asyncer.runnify(f)(*args, **kwargs)

            decorator(runner)
        else:
            decorator(f)

        return f

    def command(
        self,
        name: str | None = None,
        *,
        cls: type[TyperCommand] | None = None,
        context_settings: dict | None = None,
        help: str | None = None,
        epilog: str | None = None,
        short_help: str | None = None,
        options_metavar: str = "[OPTIONS]",
        add_help_option: bool = True,
        no_args_is_help: bool = False,
        hidden: bool = False,
        deprecated: bool = False,
        rich_help_panel: str | None = Default(None),
    ) -> Callable[[CommandFunctionType], CommandFunctionType]:
        """
        Override command decorator to support async functions.

        This method intercepts the Typer.command() decorator and wraps it
        with maybe_run_async() to handle async functions.

        All parameters are passed through to Typer.command() unchanged.
        """
        decorator = super().command(
            name=name,
            cls=cls,
            context_settings=context_settings,
            help=help,
            epilog=epilog,
            short_help=short_help,
            options_metavar=options_metavar,
            add_help_option=add_help_option,
            no_args_is_help=no_args_is_help,
            hidden=hidden,
            deprecated=deprecated,
            rich_help_panel=rich_help_panel,
        )
        return partial(self.maybe_run_async, decorator)
```

---

## Usage Example

### CLI Command with AsyncTyper

```python
# better_notion/_cli/commands/pages.py
from ..async_typer import AsyncTyper
from ..config import get_config
from ..response import format_response
from better_notion import NotionClient
import typer

app = AsyncTyper()

@app.command()
async def get(page_id: str):
    """Get a page by ID.

    Args:
        page_id: Notion page ID (e.g., page_abc123)

    Returns:
        JSON response with page data
    """
    try:
        config = get_config()

        async with NotionClient(auth=config.token) as client:
            page = await client.pages.get(page_id)
            typer.echo(format_response(success=True, data=page.to_dict()))

    except Exception as e:
        code, error = map_exception_to_error(e)
        typer.echo(format_response(success=False, error=error))
        raise typer.Exit(code)

@app.command()
async def create(
    parent: str,
    title: str,
    property: list[str] = [],
    content: str = None,
):
    """Create a new page.

    Args:
        parent: Parent database or page ID
        title: Page title
        property: Properties as key:value pairs
        content: Page content (creates paragraph block)
    """
    # Implementation...
    pass
```

---

## Testing Strategy

### Unit Tests

```python
# tests/cli/test_async_typer.py
import pytest
from better_notion._cli.async_typer import AsyncTyper
import inspect

def test_async_typer_detects_async_functions():
    """Test that AsyncTyper correctly detects async functions."""
    app = AsyncTyper()

    @app.command()
    async def async_func():
        pass

    @app.command()
    def sync_func():
        pass

    assert inspect.iscoroutinefunction(async_func.__wrapped__)
    assert not inspect.iscoroutinefunction(sync_func)

def test_async_command_execution():
    """Test that async commands execute correctly."""
    from typer.testing import CliRunner

    app = AsyncTyper()

    @app.command()
    async def hello(name: str = "World"):
        return f"Hello {name}"

    runner = CliRunner()
    result = runner.invoke(app, ["hello", "Alice"])

    assert result.exit_code == 0
    assert "Hello Alice" in result.stdout
```

### Integration Tests

```python
# tests/cli/integration/test_pages_integration.py
import pytest
from typer.testing import CliRunner
from better_notion._cli.commands.pages import app

@pytest.mark.asyncio
async def test_pages_get_with_mock_client(mock_notion_client):
    """Test pages get command with mocked NotionClient."""
    runner = CliRunner()

    result = runner.invoke(app, ["get", "page_abc123"])

    assert result.exit_code == 0
    # Verify JSON output structure
    assert '"success": true' in result.stdout
    assert '"data"' in result.stdout
```

### Performance Benchmarks

```python
# tests/cli/benchmark/test_performance.py
import time
from typer.testing import CliRunner
from better_notion._cli.main import app

def test_cold_start_time():
    """Measure CLI cold start time."""
    start = time.time()

    runner = CliRunner()
    result = runner.invoke(app, ["--version"])

    elapsed = time.time() - start

    # Target: <500ms for cold start (see cli-design-proposal.md)
    assert elapsed < 0.5, f"Cold start too slow: {elapsed:.2f}s"

def test_warm_start_time():
    """Measure CLI warm start time."""
    runner = CliRunner()

    # First call (cold)
    runner.invoke(app, ["--version"])

    # Second call (warm)
    start = time.time()
    result = runner.invoke(app, ["--version"])
    elapsed = time.time() - start

    # Target: <100ms for warm start
    assert elapsed < 0.1, f"Warm start too slow: {elapsed:.2f}s"
```

---

## Risk Mitigation

### Risk 1: asyncer Dependency

**Risk**: `asyncer` might not be maintained or could have bugs.

**Mitigation**:
- `asyncer` is a wrapper around `anyio` (well-maintained)
- Can implement `asyncio.run()` fallback if needed
- Monitor `asyncer` repository for updates

### Risk 2: Performance Degradation

**Risk**: `asyncer.runnify()` might be slower than native async.

**Mitigation**:
- Benchmark in Phase 0 (POC)
- Target: <500ms cold start, <100ms warm start
- If too slow, consider daemon mode or cyclopts

### Risk 3: Testing Complexity

**Risk**: Testing async commands in sync context is difficult.

**Mitigation**:
- Use `CliRunner` from typer.testing
- Mock async functions with `pytest-asyncio`
- Integration tests with real Notion API (optional)

### Risk 4: Error Handling

**Risk**: Async errors might not propagate correctly.

**Mitigation**:
- Comprehensive error mapping in `errors.py`
- Test all error scenarios in Phase 0
- Clear error messages with exit codes

---

## Success Criteria

AsyncTyper implementation is successful if:

- [ ] All async commands execute without RuntimeWarning
- [ ] Error handling works correctly (exit codes 0-6)
- [ ] Performance targets met (<500ms cold, <100ms warm)
- [ ] Test coverage >90% for async code
- [ ] No regressions in existing SDK tests
- [ ] Documentation updated with async examples

---

## Fallback Plan

If AsyncTyper proves problematic during POC:

1. **Week 1**: Implement AsyncTyper POC
2. **Week 2**: Test and benchmark
3. **Go/No-Go Decision**:
   - ✅ **Go**: Continue with AsyncTyper
   - ❌ **No-Go**: Switch to cyclopts

### Switching to cyclopts

If we switch to cyclopts:
1. Update `docs/cli/` to reflect cyclopts API
2. Rewrite `main.py` and command files
3. Update dependencies (remove typer, add cyclopts)
4. Add 2 weeks to timeline (learning curve)

**Estimated impact**: +2 weeks, but more robust async support

---

## References

### Typer Issue #1309
- URL: https://github.com/fastapi/typer/discussions/1309
- **Key comments**:
  - @jessekrubin (Jul 28, 2021): asyncio.run() workaround
  - @cauebs (Jul 29, 2021): Decorator pattern with anyio
  - @gilcu2 (Sep 24, 2023): AsyncTyper implementation
  - @tiangolo (Sep 6, 2023): Official maintainer response
  - @borissmidt (Aug 14, 2025): Recommendation to use cyclopts

### Alternative Solutions
- **cyclopts**: https://github.com/BrianPugh/cyclopts
- **asyncclick**: https://github.com/python-trio/asyncclick
- **asyncer**: https://github.com/tiangolo/asyncer

### Internal Documentation
- `docs/cli/cli-design-proposal.md` (revised for agents)
- `docs/cli/risks-and-challenges.md` (async/sync mismatch section)
- `docs/cli/full-commands-list.md` (62 command specifications)

---

## Appendix: Comparison with Other Projects

### How Other Projects Handle Async CLI

| Project | Framework | Async Support | Solution |
|---------|-----------|---------------|----------|
| **AWS CLI** | argparse | ❌ No | Multi-processing |
| **GitHub CLI** | Go | ✅ Native | Go has goroutines |
| **gcloud** | Python | ❌ No | Sync wrapper around async SDK |
| **heroku** | Ruby | ✅ Native | Ruby has threads |
| **kubectl** | Cobra (Go) | ✅ Native | Go has goroutines |

**Key Insight**: Most Python CLIs avoid async entirely or use workarounds. Better Notion is pioneering async CLI for agents.

---

## Changelog

### 2025-01-26 - v1.0
- Initial decision document
- Analyzed Typer #1309 (5 years of discussion)
- Evaluated 6 options
- Decided on AsyncTyper
- Created implementation plan

---

**Document Status**: ✅ Accepted
**Next Review**: After Phase 0 POC completion (target: 2025-02-02)
**Owner**: Better Notion Team
