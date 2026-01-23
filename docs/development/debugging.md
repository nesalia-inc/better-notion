# Debugging Guide

Complete guide to debugging techniques and tools for the Better Notion SDK.

## Overview

Debugging is an essential skill for any developer. This document provides practical techniques and tools for debugging issues in the Better Notion SDK.

---

## Debugging Tools

### Python Debugger (pdb)

**Built-in Python debugger.**

**Basic usage:**
```python
import pdb; pdb.set_trace()

# Or in Python 3.7+
breakpoint()
```

**When to use:**
- Stepping through code
- Inspecting variables
- Understanding execution flow

**Example:**
```python
async def retrieve_page(page_id: str) -> dict:
    """Retrieve a page from Notion."""
    breakpoint()  # Execution stops here

    response = await self._http.get(f"/pages/{page_id}")
    return response.json()
```

**Common pdb commands:**

| Command | Description |
|---------|-------------|
| `l` (list) | Show current code |
| `n` (next) | Execute next line |
| `s` (step) | Step into function |
| `c` (continue) | Continue execution |
| `p variable` | Print variable value |
| `pp variable` | Pretty print variable |
| `w` (where) | Show stack trace |
| `q` (quit) | Quit debugger |

### VS Code Debugger

**Graphical debugger built into VS Code.**

**Setup:**
1. Create `.vscode/launch.json`:
```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Python: Current File",
      "type": "debugpy",
      "request": "launch",
      "program": "${file}",
      "console": "integratedTerminal",
      "justMyCode": false
    },
    {
      "name": "Python: Pytest",
      "type": "debugpy",
      "request": "launch",
      "module": "pytest",
      "args": ["tests/"],
      "console": "integratedTerminal",
      "justMyCode": false
    }
  ]
}
```

**Usage:**
1. Click in the gutter to set breakpoints
2. Press F5 to start debugging
3. Use debugging toolbar to step through code

**Keyboard shortcuts:**
- `F5` - Start debugging
- `F10` - Step over
- `F11` - Step into
- `Shift+F11` - Step out
- `Shift+F5` - Stop debugging

### Logging

**Structured logging for debugging.**

**Setup:**
```python
import logging

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)
```

**Log levels:**
```python
logger.debug("Detailed diagnostic information")
logger.info("General informational message")
logger.warning("Warning: something unexpected")
logger.error("Error occurred")
logger.exception("Error with exception traceback")
```

**Example:**
```python
async def retrieve_page(page_id: str) -> dict:
    """Retrieve a page from Notion."""
    logger.debug(f"Retrieving page: {page_id}")

    try:
        response = await self._http.get(f"/pages/{page_id}")
        logger.debug(f"Response status: {response.status_code}")
        return response.json()

    except Exception as e:
        logger.error(f"Failed to retrieve page: {page_id}", exc_info=True)
        raise
```

**Use logging instead of print:**
```python
# AVOID
print(f"Retrieving page: {page_id}")

# GOOD
logger.debug(f"Retrieving page: {page_id}")
```

---

## Common Issues and Solutions

### Import Errors

**Problem:** `ModuleNotFoundError: No module named 'better_notion'`

**Solutions:**

1. **Check PYTHONPATH:**
```bash
# Add project root to PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# Or use uv run
uv run python -c "import better_notion"
```

2. **Ensure venv is activated:**
```bash
source .venv/bin/activate  # macOS/Linux
.venv\Scripts\activate     # Windows
```

3. **Reinstall dependencies:**
```bash
uv sync
```

4. **Install in development mode:**
```bash
uv pip install -e .
```

### Tests Pass Locally, Fail in CI

**Problem:** Tests work locally but fail in CI.

**Solutions:**

1. **Check Python version:**
```bash
python --version  # Should be 3.10+
```

2. **Update dependencies:**
```bash
uv sync --upgrade
```

3. **Run tests as CI does:**
```bash
uv run pytest -v --tb=short
```

4. **Check for environment-specific code:**
```python
# AVOID
if os.getenv("IS_CI"):
    # CI-specific behavior

# GOOD - Use feature flags
if os.getenv("ENABLE_EXPERIMENTAL_FEATURE"):
    # Feature flag behavior
```

5. **Check for hardcoded paths:**
```python
# AVOID
file = open("/home/user/config.json")

# GOOD
file = open(os.path.expanduser("~/.config/better-notion/config.json"))
```

### Async Issues

**Problem:** Async functions not executing or hanging.

**Solutions:**

1. **Ensure async/await is used correctly:**
```python
# WRONG
async def retrieve_page():
    result = self._http.get(...)  # Missing await

# GOOD
async def retrieve_page():
    result = await self._http.get(...)
```

2. **Run async code in async context:**
```python
# WRONG
async def main():
    result = await api.pages.retrieve("id")

main()  # RuntimeError: coroutine was never awaited

# GOOD
import asyncio

async def main():
    result = await api.pages.retrieve("id")

asyncio.run(main())
```

3. **Avoid blocking calls in async functions:**
```python
# WRONG
async def fetch():
    time.sleep(1)  # Blocks event loop

# GOOD
async def fetch():
    await asyncio.sleep(1)  # Non-blocking
```

### Rate Limiting Issues

**Problem:** Getting 429 errors from Notion API.

**Debugging:**

1. **Add logging:**
```python
logger.debug(f"Rate limit: {response.headers.get('X-RateLimit-Remaining')}")
logger.debug(f"Retry after: {response.headers.get('Retry-After')}")
```

2. **Check rate limit tracking:**
```python
print(f"Requests made: {rate_limiter.requests_made}")
print(f"Reset time: {rate_limiter.reset_time}")
```

3. **Adjust rate limiting strategy:**
```python
# Use WAIT strategy (retry automatically)
api = NotionAPI(auth=token, rate_limit_strategy=RateLimitStrategy.WAIT)
```

### Network Issues

**Problem:** Connection errors, timeouts.

**Debugging:**

1. **Add timeout logging:**
```python
logger.debug(f"Request timeout: {timeout} seconds")
logger.debug(f"Request took: {elapsed_time} seconds")
```

2. **Check internet connection:**
```bash
# Test connectivity
curl -I https://api.notion.com
```

3. **Adjust timeouts:**
```python
client = HTTPClient(timeout=30.0)  # Increase timeout
```

4. **Enable HTTP logging:**
```python
import httpx

# Enable logging for httpx
logging.basicConfig(level=logging.DEBUG)
```

### Memory Leaks

**Problem:** Memory usage grows over time.

**Debugging:**

1. **Use memory profiler:**
```bash
uv pip install memory-profiler
uv run python -m memory_profiler script.py
```

2. **Check for caching issues:**
```python
# Check cache size
print(f"Cache size: {len(cache._data)}")

# Clear cache if needed
cache.clear()
```

3. **Use weak references for caches:**
```python
import weakref

cache = weakref.WeakValueDictionary()
```

---

## Debugging Specific Components

### HTTP Client

**Debug HTTP requests/responses:**

```python
import logging

# Enable httpx debug logging
logging.basicConfig(level=logging.DEBUG)
logging.getLogger("httpx").setLevel(logging.DEBUG)

# Or log manually
async def request(method, url, **kwargs):
    logger.debug(f"Request: {method} {url}")
    logger.debug(f"Headers: {kwargs.get('headers')}")
    logger.debug(f"Body: {kwargs.get('json')}")

    response = await self._session.request(method, url, **kwargs)

    logger.debug(f"Response: {response.status_code}")
    logger.debug(f"Response body: {response.text[:200]}")

    return response
```

### Authentication

**Debug auth issues:**

```python
def get_headers(self) -> dict[str, str]:
    """Get request headers with auth."""
    logger.debug(f"Auth type: {type(self._auth).__name__}")
    logger.debug(f"Token prefix: {self._auth.token[:10]}...")

    headers = self._auth.headers.copy()
    logger.debug(f"Headers: {headers}")

    return headers
```

### Pagination

**Debug pagination issues:**

```python
async def fetch_all(self) -> list[dict]:
    """Fetch all pages."""
    all_items = []
    page_count = 0

    while self.has_more:
        page_count += 1
        logger.debug(f"Fetching page {page_count}")

        response = await self._fetch_next()
        all_items.extend(response.results)

        logger.debug(f"Got {len(response.results)} items")
        logger.debug(f"Has more: {response.has_more}")

        # Safety check
        if page_count > 100:
            logger.warning(f"Too many pages: {page_count}")
            break

    return all_items
```

### Caching

**Debug cache hits/misses:**

```python
def get(self, key: str) -> Any | None:
    """Get from cache."""
    value = self._data.get(key)

    if value is not None:
        logger.debug(f"Cache HIT: {key}")
    else:
        logger.debug(f"Cache MISS: {key}")

    return value
```

---

## Performance Debugging

### Profile Code

**Use cProfile:**
```bash
uv run python -m cProfile -o profile.stats script.py
```

**View profile:**
```python
import pstats

p = pstats.Stats('profile.stats')
p.sort_stats('cumulative')
p.print_stats(20)  # Top 20 functions
```

### Profile Async Code

**Use snakeviz for visualization:**
```bash
uv pip install snakeviz
uv run python -m cProfile -o profile.stats script.py
uv run snakeviz profile.stats
```

### Measure Execution Time

```python
import time
import functools

def timed(func):
    """Decorator to time function execution."""
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        start = time.time()
        result = await func(*args, **kwargs)
        elapsed = time.time() - start
        logger.debug(f"{func.__name__} took {elapsed:.2f}s")
        return result
    return wrapper

# Usage
@timed
async def retrieve_page(page_id: str) -> dict:
    ...
```

---

## Debugging Tests

### Run Specific Test

```bash
# By file
uv run pytest tests/unit/test_http_client.py

# By function
uv run pytest tests/unit/test_http_client.py::TestHTTPClient::test_request_success

# By keyword
uv run pytest -k "test_retrieve_page"
```

### Run with Verbose Output

```bash
# Verbose
uv run pytest -v

# Very verbose
uv run pytest -vv

# Show output
uv run pytest -s

# Show local variables on failure
uv run pytest -l
```

### Debug Specific Test

```bash
# Drop into pdb on failure
uv run pytest --pdb

# Drop into pdb on error
uv run pytest --pdb --trace

# Use Python debugger in test
def test_something():
    breakpoint()
    assert something
```

### Print Debugging in Tests

```python
def test_with_debug():
    """Test with debug output."""
    print(f"Variable value: {variable}")

    # Or use pytest's capsys fixture
    def test_with_capsys(capsys):
        print("Debug output")
        captured = capsys.readouterr()
        assert "Debug output" in captured.out
```

---

## IDE Debugging Tips

### VS Code

**Breakpoint types:**
- **Regular breakpoint** - Click in gutter
- **Conditional breakpoint** - Right-click → Add Conditional Breakpoint
- **Logpoint** - Right-click → Add Logpoint (prints message without stopping)

**Watch expressions:**
- Add variables to watch panel
- See values as you step through code

**Launch configurations:**
- Create different configs for different scenarios
- Example: Debug tests, debug script, debug module

### PyCharm

**Breakpoints:**
- Click in gutter to set breakpoint
- Right-click for conditional breakpoint
- View breakpoints in debugger panel

**Evaluate expression:**
- Alt+F8 (Windows/Linux)
- Option+F8 (Mac)

**Console:**
- Execute code while debugging
- Inspect and modify variables

---

## Remote Debugging

**Debug running applications:**

```python
# Use debugpy for remote debugging
import debugpy

debugpy.listen(("0.0.0.0", 5678))
debugpy.wait_for_client()  # Wait for debugger to attach

# Your code here
```

**Connect from VS Code:**
```json
{
  "name": "Python: Remote Attach",
  "type": "debugpy",
  "request": "attach",
  "connect": {
    "host": "localhost",
    "port": 5678
  }
}
```

---

## Checklist for Debugging

### Before Debugging

- [ ] Understand the problem
- [ ] Reproduce the issue
- [ ] Check logs
- [ ] Search for similar issues

### During Debugging

- [ ] Add logging/breakpoints
- [ ] Test hypotheses
- [ ] Isolate the problem
- [ ] Document findings

### After Debugging

- [ ] Fix the root cause
- [ ] Add tests to prevent regression
- [ ] Remove debug code
- [ ] Document the issue/solution

---

## Best Practices

### Do's

- ✅ Use logging instead of print
- ✅ Use descriptive log messages
- ✅ Log at appropriate levels
- ✅ Add breakpoints strategically
- ✅ Test hypotheses systematically
- ✅ Document debugging findings

### Don'ts

- ❌ Leave debug code in production
- ❌ Use print for debugging
- ❌ Add breakpoints without understanding
- ❌ Debug without reproducing first
- ❌ Ignore warning signs

---

## Quick Reference

### pdb Commands

```
l (list)     - Show code
n (next)     - Next line
s (step)     - Step into
c (continue) - Continue
p var        - Print variable
w (where)    - Stack trace
q (quit)     - Quit
```

### Logging Levels

```
DEBUG   - Detailed info
INFO    - General info
WARNING - Warning
ERROR   - Error
EXCEPTION - Error with traceback
```

### Common Issues

| Issue | Solution |
|-------|----------|
| Import error | Check PYTHONPATH, activate venv |
| Tests fail in CI | Check Python version, update deps |
| Async hangs | Ensure async/await used correctly |
| Rate limiting | Check rate limit strategy |
| Memory leak | Profile memory, check cache |

---

## Related Documentation

- [setup.md](./setup.md) - Environment setup
- [testing-strategy.md](./testing-strategy.md) - Test debugging
- [standards.md](./standards.md) - Logging conventions

---

## Summary

**Debugging Tools:**

1. **pdb** - Built-in debugger
2. **VS Code debugger** - Graphical debugging
3. **Logging** - Structured debugging output

**Common Issues:**

- Import errors → Check PYTHONPATH, venv
- Tests in CI → Check Python version, deps
- Async issues → Ensure async/await correct
- Rate limiting → Log headers, adjust strategy
- Network issues → Check connectivity, timeouts

**Best Practices:**

- Use logging, not print
- Add breakpoints strategically
- Test hypotheses
- Document findings
- Remove debug code

---

**Last Updated:** 2025-01-23
