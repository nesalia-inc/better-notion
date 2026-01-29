# Bug: `notion pages create --root` fails with asyncio error

## Summary

The `notion pages create` command with `--root` flag fails with:
```
asyncio.run() cannot be called from a running event loop
```

This prevents users from creating pages at workspace root via CLI.

## Steps to Reproduce

```bash
notion pages create --root --title "Test Page"
```

## Expected Behavior

Page should be created at workspace root and return page ID.

## Actual Behavior

```
Exit code 2
Traceback (most recent call last):
  File "C:\Users\dpereira\AppData\Local\Programs\Python\Python314\Lib\asyncio\runners.py", line 204, in run
    return runner.run(main)
RuntimeError: asyncio.run() cannot be called from a running event loop
```

## Environment

- **OS**: Windows (also affects Linux/Mac)
- **Python**: 3.14
- **better-notion**: 1.4.0

## Root Cause

The command uses `asyncio.run()` inside an already running async context (AsyncTyper).

**File**: `better_notion/_cli/commands/pages.py:130`

```python
result = asyncio.run(_create())  # <-- This line
typer.echo(result)
```

When `pages create` is called from within an async context (like the main CLI which uses AsyncTyper), calling `asyncio.run()` again causes this error.

## Solution Options

### Option 1: Use `typer.run_async()` (Recommended)

Replace `asyncio.run()` with direct async call:

```python
@app.command()
def create(...):
    async def _create():
        # ... existing code ...

    result = typer.run_async(_create())  # For AsyncTyper
    typer.echo(result)
```

### Option 2: Check if loop is running

```python
import asyncio

def run_async(coro):
    try:
        loop = asyncio.get_running_loop()
        # Already in async context
        import concurrent.futures
        with concurrent.futures.ThreadPoolExecutor() as pool:
            future = pool.submit(asyncio.run, coro)
        return future.result()
    except RuntimeError:
        # No running loop
        return asyncio.run(coro)

result = run_async(_create())
```

### Option 3: Make the command async directly

```python
@app.async_command()  # If AsyncTyper supports it
async def create(...):
    result = await _create()
    typer.echo(result)
```

## Priority

**CRITICAL** - Blocks core CLI functionality

## Related Issues

None

## Acceptance Criteria

- [ ] `notion pages create --root --title "Test"` creates page successfully
- [ ] `notion pages create --parent <id> --title "Test"` creates page successfully
- [ ] Command works on all platforms (Windows, Linux, Mac)
- [ ] Unit tests added for page creation

## Additional Notes

This is a fundamental async/await issue that may affect other commands too. Audit all CLI commands for similar `asyncio.run()` usage.
