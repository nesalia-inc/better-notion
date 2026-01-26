# CLI Design for Agent-to-Agent Communication via Notion

**Context**: Internal project for AI agents
**Use Case**: Agents manage projects by coordinating through Notion
**Status**: Revised Architecture
**Date**: 2025-01-25

---

## Executive Summary

This document revises the CLI architecture for a **specific use case**: AI agents coordinating work through Notion. This changes priorities, requirements, and implementation approach.

**Key Insight**: CLI is not for humans → CLI is for **agents**.

**Implications**:
- ✅ No complex UX needed
- ✅ No interactive prompts
- ✅ No fancy tables/progress bars
- ✅ No comprehensive documentation
- ❌ Must be **extremely reliable**
- ❌ Must have **structured JSON output**
- ❌ Must have **clear error codes**
- ❌ Must handle **rate limiting** perfectly

---

## Revised Requirements

### For Human Users vs Agents

| Requirement | Humans | Agents | Priority (Agent) |
|-------------|--------|--------|------------------|
| Pretty tables | ⭐⭐⭐⭐⭐ | ❌ | None |
| Interactive prompts | ⭐⭐⭐⭐ | ❌ | None |
| Progress bars | ⭐⭐⭐ | ❌ | None |
| Auto-completion | ⭐⭐⭐⭐ | ❌ | None |
| **JSON output** | ⭐⭐⭐ | 🔴 **CRITICAL** | P0 |
| **Error codes** | ⭐⭐ | 🔴 **CRITICAL** | P0 |
| **Reliability** | ⭐⭐⭐⭐ | 🔴 **CRITICAL** | P0 |
| **Performance** | ⭐⭐⭐ | 🟡 **HIGH** | P1 |
| **Rate limiting** | ⭐⭐ | 🟡 **HIGH** | P1 |
| **Predictable output** | ⭐⭐ | 🔴 **CRITICAL** | P0 |
| **Versioned API** | ⭐⭐ | 🟡 **HIGH** | P1 |
| **Logging** | ⭐⭐ | 🟡 **HIGH** | P1 |

### New Requirements

#### 1. **Structured JSON Output** (P0)

Agents need to parse output programmatically.

```bash
$ notion pages get page_123 --output json

{
  "success": true,
  "data": {
    "id": "page_123",
    "title": "Task: Implement feature X",
    "status": "In Progress",
    "assignee": "agent_001"
  },
  "meta": {
    "version": "0.4.0",
    "timestamp": "2025-01-25T10:00:00Z",
    "rate_limit": {
      "remaining": 48,
      "reset_at": "2025-01-25T10:01:00Z"
    }
  }
}
```

**Why:**
- Agents parse `.success` first
- Agents use `.data` for business logic
- Agents monitor `.meta.rate_limit` to throttle
- Agents use `.meta.version` for compatibility

#### 2. **Exit Codes** (P0)

Agents rely on exit codes, not error messages.

```bash
$ notion pages get invalid_page
$ echo $?
1  # Generic error

$ notion pages get page_123
$ echo $?
0  # Success
```

**Exit Code Standard:**

| Code | Meaning | Agent Action |
|------|---------|--------------|
| 0 | Success | Continue |
| 1 | Generic error | Log + Retry (if idempotent) |
| 2 | Invalid input | Don't retry (won't work) |
| 3 | Auth error | Re-auth needed |
| 4 | Rate limit | Backoff + Retry |
| 5 | Not found | Skip + Log |
| 6 | Conflict | Retry with different data |

#### 3. **Predictable Error Format** (P0)

Agents need structured errors to understand what went wrong.

```bash
$ notion pages create --title "Duplicate Task"

{
  "success": false,
  "error": {
    "code": "CONFLICT",
    "message": "Page with title 'Duplicate Task' already exists",
    "details": {
      "existing_page_id": "page_456",
      "suggestion": "Use a different title or update existing page"
    },
    "retry": false
  }
}
```

**Error Schema:**

```typescript
interface CLIResponse {
  success: boolean
  data?: T
  error?: {
    code: string  // Machine-readable
    message: string  // Human-readable (for logs)
    details?: Record<string, unknown>
    retry: boolean  // Should agent retry?
  }
  meta: {
    version: string
    timestamp: string
    rate_limit: {
      remaining: number
      reset_at: string
    }
  }
}
```

#### 4. **Idempotency** (P1)

Agents retry operations. Must be idempotent where possible.

```bash
# Idempotent: Create with same IDempotency key
$ notion pages create \
  --title "Task" \
  --idempotency-key "deploy-123" \
  --parent database_456

# First call: Creates page
# Second call: Returns existing page (doesn't duplicate)
```

**Implementation:**
```python
# Use Notion page properties for idempotency
# Or store idempotency keys in local cache
```

#### 5. **Rate Limiting Awareness** (P1)

Agents must avoid hitting rate limits.

**Approach A: CLI Manages Rate Limiting**
```python
# CLI tracks rate limits in local cache
# Blocks request if limit reached
# Returns special code 4 (rate limit) if exceeded
```

**Approach B: CLI Provides Info, Agents Decide**
```bash
$ notion pages get page_123

{
  "success": true,
  "data": {...},
  "meta": {
    "rate_limit": {
      "remaining": 3,
      "reset_at": "2025-01-25T10:01:00Z",
      "advice": "backoff_for_seconds: 45"
    }
  }
}
```

**Recommended:** Approach B (agents smarter, CLI simpler)

#### 6. **Atomic Operations** (P1)

Agents need guarantees that operations succeed or fail atomically.

```bash
# Bad: Two separate calls
$ notion pages create --title "Task"
$ notion blocks create --parent <new-page-id> --text "Subtask"

# Problem: Page created but block creation fails → orphaned page

# Good: Atomic operation
$ notion pages create \
  --title "Task" \
  --block "Subtask 1" \
  --block "Subtask 2"

# All-or-nothing: Either page + blocks created, or nothing
```

---

## Revised Architecture

### Remove Unnecessary Components

```
❌ Rich terminal output (tables, colors)
❌ Interactive prompts (questionary)
❌ Progress bars
❌ Shell completion
❌ User documentation (extensive)
❌ Auto-generated help from docstrings
❌ Fancy error messages for humans
```

### Keep/Add Essential Components

```
✅ JSON output (single format, no options)
✅ Structured errors with codes
✅ Exit codes
✅ Rate limit metadata
✅ Idempotency support
✅ Atomic operations
✅ Versioned output schema
✅ Comprehensive logging
```

### Simplified Directory Structure

```
better_notion/_cli/
├── __init__.py
├── main.py              # Entry point (minimal)
├── config.py            # Config (token, timeout, retry)
├── response.py          # Response formatter (JSON only)
├── errors.py            # Error codes and mapping
├── commands/
│   ├── __init__.py
│   ├── pages.py         # Pages CRUD
│   ├── databases.py     # Database query
│   ├── blocks.py        # Blocks CRUD
│   └── search.py        # Search
└── utils/
    ├── __init__.py
    ├── async_helper.py  # Async wrapper
    ├── idempotency.py   # Idempotency cache
    └── logger.py        # Structured logging
```

**Removed:**
- `output.py` (too complex, just JSON)
- `commands/auth.py` (agents don't need interactive auth)
- `commands/users.py` (probably not needed)
- `commands/comments.py` (probably not needed)
- `formatters.py` (not needed)

---

## Agent Use Cases

### Use Case 1: Task Coordination

**Scenario:** Agent A creates task, Agent B picks it up, Agent C reviews it.

```bash
# Agent A: Create task
$ notion pages create \
  --parent database_tasks \
  --title "Implement auth" \
  --property "Status:Backlog" \
  --property "Assignee:unassigned" \
  --output json

# Response:
{
  "success": true,
  "data": {
    "id": "page_123",
    "url": "https://notion.so/page_123"
  }
}

# Agent B: Poll for backlog tasks
$ notion databases query \
  database_tasks \
  --filter '{"property":"Status","select":{"equals":"Backlog"}}' \
  --sort "created_time:asc" \
  --limit 1

# Response:
{
  "success": true,
  "data": [
    {
      "id": "page_123",
      "title": "Implement auth",
      "status": "Backlog"
    }
  ]
}

# Agent B: Claim task
$ notion pages update \
  page_123 \
  --property "Status:In Progress" \
  --property "Assignee:Agent B"

# Agent C: Monitor for review needed
$ notion databases query \
  database_tasks \
  --filter '{"property":"Status","select":{"equals":"In Progress"}}'
```

### Use Case 2: Deploy Coordination

**Scenario:** Deploy agent coordinates deployment steps.

```bash
# Deploy Agent: Create deployment page
DEPLOY_ID=$(notion pages create \
  --title "Deploy $(date +%Y%m%d_%H%M%S)" \
  --property "Status:Started" \
  --output json \
  | jq -r '.data.id')

notion blocks children append \
  $DEPLOY_ID \
  --block '{"type":"heading","text":"Deployment Checklist"}'

notion blocks children append \
  $DEPLOY_ID \
  --block '{"type":"to_do","text":"Run tests","checked":false}'

notion blocks children append \
  $DEPLOY_ID \
  --block '{"type":"to_do","text":"Build Docker image","checked":false}'

# Test Agent: Mark test step as complete
notion blocks update \
  block_test \
  --to_do '{"checked":true,"text":"Run tests - PASSED"}'

# Build Agent: Mark build step as complete
notion blocks update \
  block_build \
  --to_do '{"checked":true,"text":"Build Docker image - SUCCESS"}'

# Deploy Agent: Update status
notion pages update \
  $DEPLOY_ID \
  --property "Status:Completed"
```

### Use Case 3: Knowledge Sharing

**Scenario:** Research agent stores findings, Analysis agent reads them.

```bash
# Research Agent: Document finding
notion pages create \
  --parent database_knowledge \
  --title "Benchmark results" \
  --block '{"type":"code","code":{"language":"json","text":"{\\"fps\\": 60}"}}' \
  --block '{"type":"paragraph","text":"Optimized rendering loop"}'

# Analysis Agent: Read findings
notion databases query \
  database_knowledge \
  --filter '{"property":"Type","select":{"equals":"Benchmark"}}' \
  --output json | jq '.data[] | .blocks'
```

---

## Implementation Changes

### 1. Simplified Output Formatter

```python
# better_notion/_cli/response.py
from typing import Any
import json
from datetime import datetime, timezone

def format_response(
    success: bool,
    data: Any = None,
    error: dict = None,
    rate_limit: dict = None
) -> str:
    """Format CLI response (JSON only)"""

    response = {
        "success": success,
        "meta": {
            "version": "0.4.0",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "rate_limit": rate_limit or {
                "remaining": None,
                "reset_at": None
            }
        }
    }

    if success:
        response["data"] = data
    else:
        response["error"] = error

    return json.dumps(response, indent=2)
```

### 2. Error Code Mapping

```python
# better_notion/_cli/errors.py
from enum import IntEnum

class ExitCode(IntEnum):
    """CLI exit codes for agents"""
    SUCCESS = 0
    GENERIC_ERROR = 1
    INVALID_INPUT = 2
    AUTH_ERROR = 3
    RATE_LIMIT = 4
    NOT_FOUND = 5
    CONFLICT = 6

class ErrorCode(str, Enum):
    """Machine-readable error codes"""
    VALIDATION_ERROR = "VALIDATION_ERROR"
    NOT_FOUND = "NOT_FOUND"
    UNAUTHORIZED = "UNAUTHORIZED"
    FORBIDDEN = "FORBIDDEN"
    RATE_LIMITED = "RATE_LIMITED"
    CONFLICT = "CONFLICT"
    INTERNAL_ERROR = "INTERNAL_ERROR"

def map_exception_to_error(e: Exception) -> tuple[ExitCode, dict]:
    """Map SDK exceptions to CLI errors"""

    if isinstance(e, UnauthorizedError):
        return (
            ExitCode.AUTH_ERROR,
            {
                "code": ErrorCode.UNAUTHORIZED,
                "message": "Authentication failed",
                "retry": False,
                "details": {
                    "suggestion": "Check NOTION_TOKEN environment variable"
                }
            }
        )

    elif isinstance(e, RateLimitError):
        return (
            ExitCode.RATE_LIMIT,
            {
                "code": ErrorCode.RATE_LIMITED,
                "message": "Rate limit exceeded",
                "retry": True,
                "details": {
                    "retry_after": e.retry_after
                }
            }
        )

    # ... more mappings
```

### 3. Idempotency Cache

```python
# better_notion/_cli/utils/idempotency.py
from pathlib import Path
import json
import hashlib

class IdempotencyCache:
    """Local cache for idempotency keys"""

    def __init__(self, cache_dir: str = "~/.notion/cache"):
        self.cache_dir = Path(cache_dir).expanduser()
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def get(self, key: str) -> dict | None:
        """Get cached response for idempotency key"""
        cache_file = self.cache_dir / f"{hash(key)}.json"

        if cache_file.exists():
            with open(cache_file) as f:
                return json.load(f)
        return None

    def set(self, key: str, response: dict):
        """Cache response for idempotency key"""
        cache_file = self.cache_dir / f"{hash(key)}.json"

        with open(cache_file, "w") as f:
            json.dump(response, f)

# Usage in commands
def create_page(..., idempotency_key: str = None):
    if idempotency_key:
        cached = cache.get(idempotency_key)
        if cached:
            return cached

    page = await client.pages.create(...)

    if idempotency_key:
        cache.set(idempotency_key, page)

    return page
```

### 4. Atomic Operations

```python
# better_notion/_cli/commands/pages.py

def create_page_with_blocks(
    parent: str,
    title: str,
    blocks: list[str]
):
    """Create page with blocks atomically"""

    async def _create():
        async with NotionClient(auth=token) as client:
            # Create page
            page = await client.pages.create(
                parent=parent,
                title=title
            )

            # Create all blocks
            block_ids = []
            for block_text in blocks:
                block = await client.blocks.create(
                    parent=page.id,
                    text=block_text
                )
                block_ids.append(block.id)

            # If any block creation fails, rollback
            # (Notion doesn't support transactions, so we delete page)
            return {
                "page": page.to_dict(),
                "blocks": block_ids
            }

    try:
        result = run_async(_create())
        return format_response(success=True, data=result)

    except Exception as e:
        # Rollback: delete created page
        async def _rollback():
            async with NotionClient(auth=token) as client:
                await client.pages.delete(result["page"]["id"])

        run_async(_rollback())

        # Return error
        code, error = map_exception_to_error(e)
        return format_response(success=False, error=error)
```

---

## Revised Implementation Plan

### Phase 1: Core Infrastructure (1 week)

**Goals:**
- Basic CLI with JSON output
- Error code mapping
- Async wrapper

**Tasks:**
- [ ] Create `better_notion/_cli/` structure
- [ ] Implement `response.py` (JSON formatter)
- [ ] Implement `errors.py` (error codes)
- [ ] Implement `async_helper.py` (proven to work)
- [ ] Add `notion --version` command
- [ ] Write tests for infrastructure

**Deliverable:** Working CLI that outputs JSON

---

### Phase 2: Pages CRUD (1 week)

**Goals:**
- Basic page operations for agents

**Tasks:**
- [ ] `notion pages get <id>`
- [ ] `notion pages create`
- [ ] `notion pages update <id>`
- [ ] `notion pages delete <id>`
- [ ] `notion pages list` (from database)
- [ ] Add idempotency support
- [ ] Write tests

**Deliverable:** Agents can manage pages

---

### Phase 3: Databases & Blocks (1 week)

**Goals:**
- Query databases, create blocks

**Tasks:**
- [ ] `notion databases query <id>`
- [ ] `notion blocks create`
- [ ] `notion blocks update <id>`
- [ ] `notion blocks children <id>` (list)
- [ ] Add atomic operations (create page + blocks)
- [ ] Write tests

**Deliverable:** Agents can query databases and create blocks

---

### Phase 4: Rate Limiting & Reliability (1 week)

**Goals:**
- Handle rate limits gracefully
- Add retry logic
- Improve error messages

**Tasks:**
- [ ] Add rate limit metadata to responses
- [ ] Implement retry logic with exponential backoff
- [ ] Add timeout support
- [ ] Improve error mapping
- [ ] Write tests for edge cases

**Deliverable:** Production-ready CLI for agents

---

### Phase 5: Testing & Polish (1 week)

**Goals:**
- Comprehensive testing
- Documentation for agents
- Performance optimization

**Tasks:**
- [ ] Unit tests (90%+ coverage)
- [ ] Integration tests with mock Notion API
- [ ] E2E tests with real Notion (token from env)
- [ ] Write agent usage documentation
- [ ] Benchmark performance
- [ ] Optimize cold start time

**Deliverable:** CLI v0.4.0 release for agents

---

**Total Timeline:** 5 weeks (vs 10 weeks for human-focused CLI)

---

## Dependencies

### Remove (Not Needed for Agents)

```toml
[project.optional-dependencies]
# Remove:
# "questionary>=2.0.0",  # No interactive prompts
# "pyperclip>=1.8.0",    # No clipboard
```

### Keep

```toml
[project.optional-dependencies]
cli = [
    "typer>=0.12.0,<0.13.0",  # CLI framework
    "rich>=13.0.0,<14.0.0",   # Keep for JSON syntax highlighting only
]
```

**Note:** Rich still useful for pretty JSON output in logs

---

## Configuration

### Environment Variables Only

No interactive config. Agents use environment variables.

```bash
export NOTION_TOKEN="secret_..."
export NOTION_TIMEOUT=30
export NOTION_RETRY_ATTEMPTS=3
```

### No Config File

Agents run in containers/environments where config files are annoying.

**Exception:** Idempotency cache (local file, but auto-managed)

---

## Testing Strategy

### Focus on Reliability

```python
# tests/cli/test_agent_workflows.py
import pytest
from typer.testing import CliRunner
from better_notion._cli.main import app

def test_task_creation_workflow():
    """Test complete agent task workflow"""
    runner = CliRunner()

    # Create task
    result = runner.invoke(app, [
        "pages", "create",
        "--title", "Test Task",
        "--parent", "database_123"
    ])

    assert result.exit_code == 0

    response = json.loads(result.stdout)
    assert response["success"] == True
    assert "id" in response["data"]

    task_id = response["data"]["id"]

    # Update task
    result = runner.invoke(app, [
        "pages", "update", task_id,
        "--property", "Status:In Progress"
    ])

    assert result.exit_code == 0

    # Delete task
    result = runner.invoke(app, [
        "pages", "delete", task_id
    ])

    assert result.exit_code == 0

def test_rate_limit_handling():
    """Test that rate limits are properly reported"""
    # Mock rate limit response
    with mock_rate_limit():
        result = runner.invoke(app, ["pages", "get", "page_123"])

        assert result.exit_code == 4  # RATE_LIMIT exit code

        response = json.loads(result.stdout)
        assert response["error"]["code"] == "RATE_LIMITED"
        assert response["error"]["retry"] == True
        assert "retry_after" in response["error"]["details"]
```

---

## Performance Requirements

For agents, performance matters more than UX.

### Target Performance

| Metric | Target | Why |
|--------|--------|-----|
| Cold start | <500ms | Agents spawn frequently |
| Warm start | <100ms | Normal operation |
| API call | <200ms + network | Depends on Notion |
| Memory | <50MB | Run many agents |

### Optimization Strategies

1. **Lazy Imports**
```python
# Don't import heavy modules until needed
def main():
    if not sys.argv[1] == "pages":
        return

    from better_notion._cli.commands import pages
    pages.app()
```

2. **Persistent Process (Daemon Mode)**
```bash
# Start daemon
$ notion daemon --start

# Fast calls via daemon
$ notion daemon-call pages get page_123
```

3. **Connection Pooling**
```python
# Reuse HTTP client across calls
# Store in local cache or daemon
```

---

## Documentation

### Minimal Documentation Needed

```markdown
# CLI for Agents

## Installation

pip install better-notion[cli]

## Configuration

export NOTION_TOKEN="secret_..."

## Usage

### Create Page

notion pages create --parent database_123 --title "Task"

### Response Format

All commands return JSON:

{
  "success": true | false,
  "data": {...},
  "error": {...},
  "meta": {
    "version": "0.4.0",
    "timestamp": "...",
    "rate_limit": {...}
  }
}

### Exit Codes

0 = Success
1 = Error
2 = Invalid input
3 = Auth error
4 = Rate limit
5 = Not found
6 = Conflict
```

**That's it.** Agents don't need tutorials.

---

## Success Metrics

For agent use case, metrics are different:

### Technical Metrics

- [ ] **Reliability**: 99.9% commands succeed (given valid input)
- [ ] **Predictability**: 100% consistent JSON schema
- [ ] **Error Clarity**: 100% errors have retry flag
- [ ] **Performance**: <500ms cold start, <100ms warm
- [ ] **Test Coverage**: 95%+ (agents need reliability)

### Agent Metrics

- [ ] **Integration**: Can agents complete workflows?
- [ ] **Error Recovery**: Can agents handle all error codes?
- [ ] **Rate Limiting**: Do agents avoid hitting limits?
- [ ] **Idempotency**: Do retries work correctly?

---

## Revised Risk Assessment

### Risks Resolved (Agent Context)

| Risk | Before | Now | Resolution |
|------|--------|-----|------------|
| **Demand** | Uncertain | ✅ **Internal need** | Agents need it |
| **UX complexity** | High | ✅ **None** | No interactive UX |
| **Documentation** | Extensive | ✅ **Minimal** | Just JSON schema |
| **Maintenance** | High | 🟡 **Medium** | Simpler scope |
| **Scope creep** | 50 commands | ✅ **10 commands** | Focused MVP |

### New Risks (Agent Context)

| Risk | Impact | Mitigation |
|------|--------|------------|
| **Output predictability** | High | Versioned JSON schema |
| **Error handling** | High | Comprehensive error codes |
| **Rate limiting** | Medium | Metadata in response |
| **Idempotency** | Medium | Local cache |
| **Testing burden** | Medium | 95% coverage goal |

---

## Comparison: Original vs Agent

| Aspect | Original (Human) | Revised (Agent) |
|--------|------------------|-----------------|
| **Output format** | 5 formats | 1 format (JSON) |
| **Commands** | 50+ | ~10 |
| **Documentation** | Extensive | Minimal |
| **Interactive** | Yes | No |
| **Error messages** | Human-friendly | Machine-readable |
| **Focus** | UX/Discoverability | Reliability/Predictability |
| **Timeline** | 10 weeks | 5 weeks |
| **Maintenance** | High | Medium |
| **Complexity** | High | Medium |

---

## Recommendations

### ✅ **GO** - Build for Agents

The agent use case **resolves most critical risks**:

1. ✅ **Demand is real** (internal need)
2. ✅ **UX complexity gone** (no humans)
3. ✅ **Documentation minimal** (just JSON schema)
4. ✅ **Scope focused** (agents don't need 50 commands)
5. ✅ **Maintenance manageable** (simpler architecture)

### **Revised Scope**

Build **minimal, reliable CLI** for agents:

**Phase 1-2 (2 weeks):**
- Infrastructure + Pages CRUD
- JSON output only
- Error codes
- Idempotency

**Phase 3-4 (2 weeks):**
- Databases + Blocks
- Rate limiting
- Comprehensive testing

**Phase 5 (1 week):**
- Polish + Documentation
- Performance optimization

**Total: 5 weeks** (vs 10 weeks for human CLI)

### **Success Criteria**

- [ ] Agents can complete task workflows
- [ ] 99.9% reliability (given valid input)
- [ ] <500ms cold start
- [ ] 95%+ test coverage
- [ ] All errors actionable (retry flag)

---

## Conclusion

**Building a CLI for agents is a MUCH better fit** than for human users.

**Key Advantages:**
1. **Clear requirement**: Agents need programmatic access
2. **Simpler architecture**: No UX complexity
3. **Focused scope**: 10 commands, not 50
4. **Realistic timeline**: 5 weeks, not 10
5. **Justified investment**: Internal use case

**Priority Order:**
1. **Reliability** (agents break if CLI unreliable)
2. **Predictability** (consistent JSON schema)
3. **Performance** (agents make many calls)
4. **Error handling** (agents must know how to recover)

**Don't Build:**
- Interactive prompts (agents can't use them)
- Pretty tables (agents can't read them)
- Extensive docs (agents don't read them)
- 50+ commands (start with 10)

**Do Build:**
- JSON output only (single format, versioned)
- Error codes (machine-readable)
- Idempotency (for retries)
- Rate limit metadata (for throttling)
- Comprehensive tests (95%+ coverage)

---

**Verdict:** **Proceed with agent-focused CLI.**

This is a well-defined, valuable use case with clear requirements and realistic scope.

---

**Next Step:** Start Phase 1 (Infrastructure) - build async wrapper and JSON formatter.
