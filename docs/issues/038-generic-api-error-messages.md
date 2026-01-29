# Enhancement: Improve Notion API error messages with context

## Summary

When Notion API returns errors (404, 400, etc.), the CLI displays generic "Bad request" or "Not found" messages without helpful context, making debugging difficult.

## Examples

### Example 1: Get non-existent org

**Command**:
```bash
notion agents orgs get "invalid-id-12345"
```

**Current**:
```json
{
  "error": {
    "code": "GET_ORG_ERROR",
    "message": "Bad request"
  }
}
```

**Better**:
```json
{
  "error": {
    "code": "ORG_NOT_FOUND",
    "message": "Organization 'invalid-id-12345' not found. Please verify:\n  1. The organization ID is correct\n  2. The organization exists in your workspace\n  3. You have access to this organization",
    "suggestion": "Run 'notion agents orgs list' to see available organizations"
  }
}
```

---

### Example 2: Task claim on non-existent task

**Command**:
```bash
notion agents tasks claim "non-existent-task"
```

**Current**:
```json
{
  "error": {
    "code": "CLAIM_TASK_ERROR",
    "message": "Bad request"
  }
}
```

**Better**:
```json
{
  "error": {
    "code": "TASK_NOT_FOUND",
    "message": "Task 'non-existent-task' not found",
    "details": "The task may have been deleted or you may not have access",
    "suggestion": "Run 'notion agents tasks list' to see available tasks"
  }
}
```

---

### Example 3: Create with missing required field

**Command**:
```bash
notion agents orgs create --name "" --slug "test"
```

**Current**:
```json
{
  "error": {
    "code": "CREATE_ORG_ERROR",
    "message": "Organizations database ID not found in workspace config"
  }
}
```

**Better**:
```json
{
  "error": {
    "code": "WORKSPACE_NOT_INITIALIZED",
    "message": "Agents workspace not initialized",
    "details": "The Organizations database has not been created yet",
    "suggestion": "Run 'notion agents init --parent-page <page-id>' to initialize the workspace"
  }
}
```

---

## Root Cause

**Files**: `better_notion/_cli/response.py`, `better_notion/plugins/official/agents_cli.py`

Generic error handling:

```python
try:
    org = await manager.get(org_id)
except Exception as e:
    return format_error("GET_ORG_ERROR", str(e), retry=False)
```

All API errors caught and wrapped generically without:
1. Parsing error type
2. Adding context
3. Providing suggestions
4. Formatting for readability

## Proposed Solution

### Enhanced Error Handler

```python
# utils/error_handler.py
class NotionErrorHandler:
    """Enhanced error handling for Notion API errors."""

    @staticmethod
    def handle_api_error(error: Exception, context: dict) -> dict:
        """
        Convert Notion API errors into user-friendly messages.

        Args:
            error: The exception from Notion API
            context: Context about what operation failed

        Returns:
            Formatted error dict
        """
        error_str = str(error).lower()

        # Detect error type
        if "not found" in error_str or "404" in error_str:
            return {
                "code": "NOT_FOUND",
                "message": f"{context.get('entity', 'Resource')} '{context.get('id')}' not found",
                "details": f"The {context.get('entity', 'resource')} may have been deleted",
                "suggestion": context.get('suggestion')
            }

        elif "bad request" in error_str or "400" in error_str:
            return {
                "code": "INVALID_REQUEST",
                "message": f"Invalid request for {context.get('operation', 'operation')}",
                "details": f"Parameters: {context.get('params', {})}",
                "suggestion": "Check parameter values and types"
            }

        elif "unauthorized" in error_str or "401" in error_str:
            return {
                "code": "UNAUTHORIZED",
                "message": "Not authorized to access this resource",
                "details": "Your integration token may not have access",
                "suggestion": "Verify token permissions in Notion"
            }

        elif "rate limit" in error_str or "429" in error_str:
            return {
                "code": "RATE_LIMITED",
                "message": "Too many requests - rate limited",
                "details": "Notion API rate limit exceeded",
                "suggestion": "Wait a few seconds before retrying"
            }

        else:
            # Unknown error
            return {
                "code": "UNKNOWN_ERROR",
                "message": f"An error occurred: {error_str}",
                "details": str(error),
                "suggestion": "Check Notion status at https://notion.so"
            }
```

### Usage Examples

```python
# agents_cli.py
def orgs_get(org_id: str) -> str:
    async def _get() -> str:
        try:
            client = get_client()
            register_agents_sdk_plugin(client)

            manager = client.plugin_manager("organizations")
            org = await manager.get(org_id)

            return format_success({...})

        except Exception as e:
            # Enhanced error handling
            context = {
                "entity": "Organization",
                "id": org_id,
                "operation": "get",
                "suggestion": "Run 'notion agents orgs list' to see organizations"
            }

            error_info = NotionErrorHandler.handle_api_error(e, context)
            return format_error(
                error_info["code"],
                error_info["message"],
                details=error_info.get("details"),
                suggestion=error_info.get("suggestion"),
                retry=False
            )

    return asyncio.run(_get())
```

## Error Message Guidelines

### Good Error Messages

**Structure**:
1. **What happened** (clear, concise)
2. **Why it happened** (technical details)
3. **How to fix** (actionable suggestion)
4. **Where to get help** (documentation or command)

**Example**:
```
Error: Organization 'abc123' not found

What: The organization you're trying to access doesn't exist
Why: The ID 'abc123' may be incorrect or the org was deleted
Fix: Verify the organization ID
Help: Run 'notion agents orgs list' to see available organizations
```

### Error Codes

Define consistent error codes:

| Code | Description | HTTP Status |
|------|-------------|-------------|
| `NOT_FOUND` | Resource not found | 404 |
| `INVALID_PARAMETER` | Invalid parameter value | 400 |
| `UNAUTHORIZED` | No access to resource | 401 |
| `FORBIDDEN` | Insufficient permissions | 403 |
| `RATE_LIMITED` | Too many requests | 429 |
| `WORKSPACE_NOT_INITIALIZED` | Agents workspace not set up | N/A |
| `DATABASE_NOT_CONFIGURED` | Database ID missing from config | N/A |
| `INVALID_STATE` | Invalid state transition | 400 |
| `VALIDATION_ERROR` | Validation failed | 400 |

## Priority

**LOW-MEDIUM** - Improves user experience but doesn't block functionality

## Related Issues

- #033 - pages create asyncio error
- #034 - agents init bad request
- #035 - databases create bad request

## Acceptance Criteria

- [ ] Create `NotionErrorHandler` utility class
- [ ] Define error code standards
- [ ] Add context to all error handling
- [ ] Provide actionable suggestions in errors
- [ ] Test error messages with invalid inputs
- [ ] Document error message format

## Additional Considerations

### Error Severity Levels

Color-code errors in CLI output:

```bash
# Critical (red)
❌ Error: WORKSPACE_NOT_INITIALIZED
   Agents workspace not initialized
   Run: notion agents init --parent-page <id>

# Warning (yellow)
⚠️  Warning: TASK_ALREADY_CLAIMED
   Task is already claimed by another agent
   Run: notion agents tasks next

# Info (blue)
ℹ️  Note: NO_TASKS_AVAILABLE
   No tasks available for this project
   Try: notion agents tasks list --project-id <id>
```

### Logging

Add debug logging for errors:

```python
import logging

logger = logging.getLogger(__name__)

try:
    org = await manager.get(org_id)
except Exception as e:
    logger.error(f"Failed to get organization {org_id}", exc_info=True)
    logger.debug(f"Context: workspace_config={client._workspace_config}")
    # Return user-friendly error
```

Users can enable with:
```bash
notion --debug agents orgs get <id>
```

### Error Recovery

Where possible, suggest automated fixes:

```bash
# If workspace not initialized
Error: WORKSPACE_NOT_INITIALIZED
Would you like to initialize it now? [Y/n]

# If database missing
Error: DATABASE_NOT_CONFIGURED
Missing: Organizations database
Create it now? [Y/n]
```

## Estimated Effort

- **Error handler utility**: 3-4 hours
- **Update all error handling**: 4-5 hours
- **Testing**: 2 hours
- **Documentation**: 1-2 hours

**Total**: 10-13 hours for full implementation

---

## Quick Win: Common Error Messages

Start with the most common errors:

1. **Not found** (404) - Most common
2. **Bad request** (400) - Validation failures
3. **Unauthorized** (401) - Permission issues
4. **Rate limited** (429) - Too many requests

Do these first, then handle edge cases.

## References

- Notion API Error Codes: https://developers.notion.com/reference/errors
- HTTP Status Codes: https://developer.mozilla.org/en-US/docs/Web/HTTP/Status
- Error Message Best Practices: https://developer.apple.com/documentation/
