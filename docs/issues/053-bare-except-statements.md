# Bare Except Statements and Information Loss

## Summary

Production code contains bare `except:` statements that catch all exceptions including `KeyboardInterrupt` and `SystemExit`, and uses `from None` which loses valuable debugging information.

## Problem Statement

### Current State

```python
# client.py:280-281
except:
    raise BadRequestError() from None  # ❌ Loses all context
```

### Issues

**1. Bare Except Clauses**

```python
try:
    # ... some code
except:  # ❌ Bare except
    raise BadRequestError() from None
```

**Problems:**
- Catches **all exceptions** including:
  - `KeyboardInterrupt` (Ctrl+C)
  - `SystemExit` (sys.exit())
  - `GeneratorExit`
  - Regular exceptions
- Makes it impossible to interrupt the program
- Violates [PEP 8 - Programming Recommendations](https://peps.python.org/pep-0008/#programming-recommendations)

**2. Information Loss with `from None`**

```python
raise BadRequestError() from None  # ❌ Loses original traceback
```

**Problems:**
- Original exception is discarded
- Stack trace is lost
- Debugging becomes impossible
- No way to see what actually went wrong

**3. Poor Error Handling**

```python
# Current code pattern
try:
    error_data = e.response.json()
    error_message = error_data.get("message", "Bad request")
    error_code = error_data.get("code", "")
    if error_code:
        raise BadRequestError(f"{error_code}: {error_message}") from None
    else:
        raise BadRequestError(error_message) from None
except Exception as parse_error:  # Too broad
    try:
        response_text = e.response.text if hasattr(e.response, 'text') else str(e)
        import sys
        print(f"[DEBUG] Failed to parse error response: {parse_error}", file=sys.stderr)
        print(f"[DEBUG] Response text: {response_text[:1000]}", file=sys.stderr)
        raise BadRequestError(f"Bad request: {response_text[:500]}") from None
    except:  # ❌ Bare except - worst offender
        raise BadRequestError() from None  # ❌ Complete information loss
```

### Impact

1. **Impossible to Debug**: Original traceback is lost
2. **Cannot Interrupt**: Bare except catches KeyboardInterrupt
3. **Information Loss**: No context about what went wrong
4. **Security Risk**: Errors are silently caught and hidden
5. **Anti-Pattern**: Well-known Python anti-pattern

## Proposed Solution

### 1. Fix Bare Except Statements

```python
# ❌ BAD
try:
    error_data = e.response.json()
except:
    raise BadRequestError() from None

# ✅ GOOD - Specific exception
try:
    error_data = e.response.json()
except json.JSONDecodeError as parse_error:
    logger.debug("Failed to parse JSON error response", exc_info=parse_error)
    # Fall back to text representation
    response_text = e.response.text if hasattr(e.response, 'text') else str(e)
    raise BadRequestError(f"Bad request: {response_text[:500]}") from parse_error
```

### 2. Preserve Exception Chains

```python
# ❌ BAD - Loses context
raise BadRequestError() from None

# ✅ GOOD - Preserves context
raise BadRequestError("Message") from original_exception

# ✅ EVEN BETTER - Let exception bubble up naturally
# Don't catch and re-raise unless adding value
```

### 3. Refactor Error Handling Logic

```python
# Current problematic code (lines 261-281 in client.py)
if status_code == 400:
    from better_notion._api.errors import BadRequestError
    try:
        error_data = e.response.json()
        error_message = error_data.get("message", "Bad request")
        error_code = error_data.get("code", "")
        if error_code:
            raise BadRequestError(f"{error_code}: {error_message}") from None
        else:
            raise BadRequestError(error_message) from None
    except Exception as parse_error:
        try:
            response_text = e.response.text if hasattr(e.response, 'text') else str(e)
            import sys
            print(f"[DEBUG] Failed to parse error response: {parse_error}", file=sys.stderr)
            print(f"[DEBUG] Response text: {response_text[:1000]}", file=sys.stderr)
            raise BadRequestError(f"Bad request: {response_text[:500]}") from None
        except:
            raise BadRequestError() from None

# Proposed clean version
if status_code == 400:
    from better_notion._api.errors import BadRequestError
    import json
    import logging

    logger = logging.getLogger(__name__)

    # Try to extract structured error data
    try:
        error_data = e.response.json()
        error_message = error_data.get("message", "Bad request")
        error_code = error_data.get("code", "")

        if error_code:
            raise BadRequestError(f"{error_code}: {error_message}") from e
        else:
            raise BadRequestError(error_message) from e

    except json.JSONDecodeError as parse_error:
        # Response is not valid JSON - fall back to text
        logger.debug("Failed to parse error response as JSON", exc_info=parse_error)

        response_text = e.response.text if hasattr(e.response, 'text') else str(e)
        raise BadRequestError(f"Bad request: {response_text[:500]}") from e

    except Exception as unexpected_error:
        # Something else went wrong (shouldn't happen in production)
        logger.error("Unexpected error while parsing error response", exc_info=unexpected_error)
        raise BadRequestError("Bad request: unable to parse error details") from unexpected_error
```

### 4. Best Practices for Exception Handling

```python
# DO:
# - Catch specific exceptions (ValueError, json.JSONDecodeError, etc.)
# - Use 'from e' to preserve exception chain
# - Log unexpected errors with exc_info=True
# - Re-raise with additional context when useful
# - Let exceptions bubble up when you can't add value

# DON'T:
# - Use bare 'except:' clauses
# - Use 'from None' (loses debugging information)
# - Catch Exception when you mean something specific
# - Silently swallow exceptions
# - Add try/except around everything "just in case"
```

## Implementation Plan

### Phase 1: Audit (0.5 day)

1. Search for all bare `except:` statements in codebase
2. Search for all `from None` usage
3. Document each occurrence with severity level

### Phase 2: Fix Critical Issues (1 day)

1. Fix bare except in client.py error handling
2. Fix information loss with `from None`
3. Add specific exception types
4. Preserve exception chains properly

### Phase 3: Testing (0.5 day)

1. Test error handling with various error scenarios
2. Verify exception chains are preserved
3. Test KeyboardInterrupt still works
4. Verify debuggability with exception traces

### Phase 4: Code Review Guidelines (0.5 day)

1. Add exception handling guidelines to CONTRIBUTING.md
2. Add pre-commit check for bare except (if possible)
3. Document best practices
4. Add examples of correct patterns

## Code Examples

### Before (Current)

```python
# client.py lines 272-281
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
import json
import logging

logger = logging.getLogger(__name__)

# ... in error handling code
except json.JSONDecodeError as parse_error:
    # Response is not valid JSON - expected for some errors
    logger.debug("Failed to parse error response as JSON", exc_info=parse_error)

    response_text = e.response.text if hasattr(e.response, 'text') else str(e)
    raise BadRequestError(f"Bad request: {response_text[:500]}") from e

except Exception as unexpected_error:
    # Something unexpected happened
    logger.error("Unexpected error while parsing error response", exc_info=unexpected_error)
    raise BadRequestError("Bad request: unable to parse error details") from unexpected_error
```

## Benefits

1. **Debuggable**: Full exception traces preserved
2. **Interruptible**: Ctrl+C still works
3. **Professional**: Follows Python best practices
4. **Maintainable**: Clear error handling logic
5. **Secure**: Errors aren't silently hidden
6. **Standards Compliant**: Follows PEP 8 guidelines

## Related Issues

- #052: Debug prints in production (related error handling)
- #038: Generic API error messages (better error reporting)
- #054: Missing property validation (related error handling)

## Success Metrics

1. ✅ Zero bare `except:` statements in codebase
2. ✅ All exception chains preserved (no `from None`)
3. ✅ Specific exception types used (not just Exception)
4. ✅ All unexpected errors logged with exc_info
5. ✅ KeyboardInterrupt still works
6. ✅ Full tracebacks available for debugging

## Priority

**🔴 Critical** - Security and debugging issue:

1. **Security**: Bare except can hide security-relevant errors
2. **Debugging**: Lost tracebacks make debugging impossible
3. **User Experience**: Cannot interrupt with Ctrl+C
4. **Best Practices**: Violates fundamental Python principles
5. **Maintainability**: Code is harder to understand and debug

This is a **well-known anti-pattern** that should never appear in production code, especially in a library distributed on PyPI.

## Timeline

- **Audit**: 0.5 day
- **Fix critical issues**: 1 day
- **Testing**: 0.5 day
- **Documentation**: 0.5 day
- **Total**: 2.5 days

## Standards

This implementation follows:
- [PEP 8 - Programming Recommendations](https://peps.python.org/pep-0008/#programming-recommendations)
- [Python Documentation on Exceptions](https://docs.python.org/3/tutorial/errors.html)
- [The Zen of Python](https://peps.python.org/pep-0020/) - "Errors should never pass silently unless explicitly silenced"
- [Python Anti-Patterns - Bare Except](https://docs.quantifiedcode.com/python-anti-patterns/bare-except.html)
