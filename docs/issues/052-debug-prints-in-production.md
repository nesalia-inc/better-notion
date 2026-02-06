# Debug Prints in Production Code

## Summary

Production code contains debug print statements that output to stderr. These print statements cannot be disabled, are not part of a proper logging system, and pollute user output in production environments.

## Problem Statement

### Current State

```python
# client.py:277-278
print(f"[DEBUG] Failed to parse error response: {parse_error}", file=sys.stderr)
print(f"[DEBUG] Response text: {response_text[:1000]}", file=sys.stderr)
```

### Issues

1. **No Proper Logging System**
   - Using print() instead of logging module
   - No log levels (debug, info, warning, error)
   - No log formatting
   - No log handlers or configuration

2. **Cannot Be Disabled**
   - Prints always execute
   - No environment-based control
   - No configuration option
   - Always pollutes stderr

3. **Unprofessional for Library**
   - Libraries should never print to stdout/stderr
   - Users cannot control the output
   - Breaks user applications that capture stderr
   - Violates principle of least surprise

4. **Inconsistent Format**
   - Manual "[DEBUG]" prefix instead of proper log levels
   - No timestamps
   - No module/function context
   - No structured logging

### Impact

- **User Applications**: Stderr pollution breaks log parsing
- **Production**: Debug output in production environments
- **Library Users**: Cannot control or disable output
- **Debugging**: No proper debugging tools (log levels, filtering)
- **Professionalism**: Not suitable for production-quality library

## Proposed Solution

### 1. Replace Print with Logging Module

```python
import logging

logger = logging.getLogger(__name__)

# In error handling:
try:
    error_data = e.response.json()
    error_message = error_data.get("message", "Bad request")
    error_code = error_data.get("code", "")
    if error_code:
        raise BadRequestError(f"{error_code}: {error_message}") from None
    else:
        raise BadRequestError(error_message) from None
except json.JSONDecodeError as parse_error:
    # Proper logging with context
    logger.debug("Failed to parse error response", exc_info=parse_error)
    logger.debug("Response text: %.1000s", response_text)
    raise BadRequestError(f"Bad request: {response_text[:500]}") from None
```

### 2. Configure Logging Behavior

```python
# Add to NotionAPI.__init__()
def __init__(self, ...):
    # Set up logging
    self._setup_logging()

def _setup_logging(self):
    """Configure logging for NotionAPI."""
    # Get logger for this module
    logger = logging.getLogger("better_notion")

    # Only configure if not already configured
    if not logger.handlers:
        # Default: only show warnings and errors in production
        logger.setLevel(logging.WARNING)

        # Add null handler to prevent "No handler" warnings
        logger.addHandler(logging.NullHandler())

# Allow users to enable debug logging:
# import logging
# logging.getLogger("better_notion").setLevel(logging.DEBUG)
```

### 3. Document Logging Configuration

```python
"""
Usage:
    # Basic usage (no debug output)
    api = NotionAPI(auth="secret_...")

    # Enable debug logging
    import logging
    logging.getLogger("better_notion").setLevel(logging.DEBUG)
    api = NotionAPI(auth="secret_...")

    # Configure logging to file
    import logging
    logging.basicConfig(
        level=logging.DEBUG,
        filename='notion_api.log',
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    api = NotionAPI(auth="secret_...")
"""
```

### 4. Add Structured Logging (Optional Enhancement)

```python
import structlog

# Configure structured logging
logger = structlog.get_logger("better_notion")

# In error handling:
try:
    error_data = e.response.json()
except Exception as e:
    logger.debug(
        "error_parse_failed",
        error=str(e),
        response_text=response_text[:1000],
        status_code=e.response.status_code
    )
```

## Implementation Plan

### Phase 1: Replace Prints (1 day)

1. Add `import logging` to all files with print statements
2. Create logger instance: `logger = logging.getLogger(__name__)`
3. Replace all `print("[DEBUG]...", file=sys.stderr)` with `logger.debug()`
4. Remove sys.stderr parameter

### Phase 2: Add Configuration (0.5 day)

1. Add `_setup_logging()` method to NotionAPI
2. Configure default logging level (WARNING)
3. Add NullHandler to prevent warnings
4. Document logging configuration

### Phase 3: Update Documentation (0.5 day)

1. Add logging section to README
2. Document environment variables
3. Provide examples for common scenarios
4. Add troubleshooting guide

### Phase 4: Testing (0.5 day)

1. Test that no output in normal usage
2. Test debug logging works when enabled
3. Test log levels filter correctly
4. Test user's logging configuration is respected

## Migration Guide

### For Library Users

**Before (2.x):**
```python
# Debug output appears automatically (cannot be disabled)
api = NotionAPI(auth="secret_...")
# stderr: [DEBUG] Some debug message
```

**After (3.x):**
```python
# No debug output by default
api = NotionAPI(auth="secret_...")
# stderr: (clean)

# Enable debug logging if needed
import logging
logging.getLogger("better_notion").setLevel(logging.DEBUG)

# Or configure file logging
logging.basicConfig(
    level=logging.DEBUG,
    filename='notion_debug.log'
)
```

## Breaking Changes

**None** - This is purely additive. Removing print statements is a bug fix, not a breaking change.

However, if users were relying on debug output in stderr, they will need to configure logging explicitly.

## Code Examples

### Before (Current)

```python
# client.py
except Exception as parse_error:
    try:
        response_text = e.response.text if hasattr(e.response, 'text') else str(e)
        import sys
        print(f"[DEBUG] Failed to parse error response: {parse_error}", file=sys.stderr)
        print(f"[DEBUG] Response text: {response_text[:1000]}", file=sys.stderr)
        raise BadRequestError(f"Bad request: {response_text[:500]}") from None
    except:
        raise BadRequestError() from None
```

### After (Proposed)

```python
# client.py
import logging

logger = logging.getLogger(__name__)

except Exception as parse_error:
    try:
        response_text = e.response.text if hasattr(e.response, 'text') else str(e)
        logger.debug("Failed to parse error response", exc_info=parse_error)
        logger.debug("Response text: %.1000s", response_text)
        raise BadRequestError(f"Bad request: {response_text[:500]}") from None
    except Exception:
        logger.error("Failed to extract error details from response", exc_info=True)
        raise BadRequestError() from None
```

## Benefits

1. **Professional**: Uses standard Python logging practices
2. **Controllable**: Users can enable/disable debug logging
3. **Structured**: Proper log levels and formatting
4. **Production-Ready**: No output pollution in production
5. **Debuggable**: Rich logging when enabled for debugging
6. **Flexible**: Users can configure handlers, formatters, levels

## Related Issues

- #053: Bare except statements (related error handling issue)
- #038: Generic API error messages (better error reporting)

## Success Metrics

1. ✅ No print() statements in production code
2. ✅ All debug output uses logging module
3. ✅ Logging is configurable by users
4. ✅ No stderr pollution in normal usage
5. ✅ Debug logging available when needed
6. ✅ Documentation shows logging configuration

## Priority

**🟠 High** - Not blocking but highly unprofessional:

1. **Production Issue**: Debug output appears in production
2. **User Experience**: Pollutes stderr, breaks log parsing
3. **Best Practices**: Violates Python logging standards
4. **Library Quality**: Not suitable for public PyPI package
5. **Maintainability**: Hard to debug issues without proper logging

This should be fixed before the next major release (3.0.0) to establish professional logging practices from the start.

## Timeline

- **Implementation**: 1 day
- **Testing**: 0.5 day
- **Documentation**: 0.5 day
- **Total**: 2 days

## Standards

This implementation follows:
- [Python Logging Best Practices](https://docs.python.org/3/howto/logging.html)
- [Twelve-Factor App - Logging](https://12factor.net/logs) (treating logs as event streams)
- [PEP 282 - A Logging System](https://peps.python.org/pep-0282/)
