# Bug: Missing parameter validation in agents CLI commands

## Summary

Multiple agents commands accept invalid parameters without validation, leading to confusing behavior or generic API errors.

## Affected Commands

### 1. ideas review - Negative count

**Command**: `notion agents ideas review --count -5`

**Current Behavior**:
```json
{
  "success": true,
  "data": []  # Empty array, no error
}
```

**Expected**:
```json
{
  "error": {
    "code": "INVALID_PARAMETER",
    "message": "count must be a positive integer (got: -5)"
  }
}
```

**File**: `better_notion/plugins/official/agents_sdk/managers.py`

```python
async def review_batch(self, count: int = 10) -> list:
    # Should validate:
    if count <= 0:
        raise ValueError("count must be positive")
    # ...
```

---

### 2. incidents mttr - Zero or negative days

**Command**: `notion agents incidents mttr --within-days 0`

**Current Behavior**:
```json
{
  "success": true,
  "data": {
    "mttr_hours": {},
    "within_days": 0,
    "project_id": null
  }
}
```

**Expected**:
```json
{
  "error": {
    "code": "INVALID_PARAMETER",
    "message": "within_days must be a positive integer (got: 0)"
  }
}
```

**File**: `better_notion/plugins/official/agents_sdk/managers.py`

```python
async def calculate_mttr(
    self,
    project_id: str | None = None,
    within_days: int = 30
) -> dict:
    # Should validate:
    if within_days <= 0:
        raise ValueError("within_days must be positive")
    # ...
```

---

### 3. tasks complete - Negative hours

**Command**: `notion agents tasks complete "task-id" --actual-hours -3`

**Current Behavior**:
```
Error: Bad request  # Generic API error
```

**Expected**:
```json
{
  "error": {
    "code": "INVALID_PARAMETER",
    "message": "actual_hours must be non-negative (got: -3)"
  }
}
```

**File**: `better_notion/plugins/official/agents_cli.py`

```python
@tasks_app.command("complete")
def tasks_complete_cmd(
    task_id: str,
    actual_hours: float = typer.Option(0, "--actual-hours"),
):
    # Should validate:
    if actual_hours < 0:
        return format_error(
            "INVALID_PARAMETER",
            "actual_hours must be non-negative",
            retry=False
        )

    typer.echo(agents_cli.tasks_complete(task_id, actual_hours))
```

---

## Root Cause

**Systematic lack of input validation** across the codebase:

1. **CLI commands** don't validate parameters before passing to managers
2. **Manager methods** don't validate parameters before using them
3. **Model methods** don't validate before setting properties
4. **Rely on Notion API** for validation, but error messages are generic

## Impact

**MEDIUM** - Widespread across the codebase:

- **User Experience**: Confusing behavior
- **Debugging**: Difficult to trace root cause
- **API Efficiency**: Wasted API calls with invalid data
- **Automation**: Silent failures in scripts/agents

## Validation Strategy

### Layer 1: CLI Parameter Validation

Validate at the entry point:

```python
@app.command()
def ideas_review(count: int = typer.Option(10, "--count", "-c")):
    if count <= 0:
        typer.echo(format_error(
            "INVALID_PARAMETER",
            "count must be a positive integer"
        ))
        raise typer.Exit(code=2)

    typer.echo(agents_cli.ideas_review(count))
```

**Pros**: Early validation, better error messages
**Cons**: Duplicates validation logic

### Layer 2: Manager Method Validation

Validate in business logic:

```python
class IdeaManager:
    async def review_batch(self, count: int = 10) -> list:
        if count <= 0:
            raise ValueError("IdeaManager.review_batch: count must be positive")

        # ... rest of logic
```

**Pros**: Single source of truth, validates all callers
**Cons**: Error messages may not be CLI-friendly

### Layer 3: Pydantic Models

Use Pydantic for validation:

```python
from pydantic import BaseModel, Field, conf validator

class MTTRQuery(BaseModel):
    project_id: str | None = None
    within_days: int = Field(gt=0)  # Must be > 0

    @validator('within_days')
    def validate_days(cls, v):
        if v <= 0:
            raise ValueError('within_days must be positive')
        return v

# Usage
query = MTTRQuery(project_id=pid, within_days=days)
```

**Pros**: Declarative, reusable, type-safe
**Cons**: Requires refactoring models

## Recommended Approach: Hybrid

1. **CLI Level**: Basic validation for CLI-specific parameters
2. **Manager Level**: Business logic validation
3. **Model Level**: Data integrity validation

### Implementation Example

```python
# cli.py
@app.command()
def incidents_mttr(
    project_id: str = typer.Option(None, "--project-id", "-p"),
    within_days: int = typer.Option(30, "--within-days", "-d"),
):
    # CLI-level validation
    if within_days <= 0:
        typer.echo(format_error(
            "INVALID_PARAMETER",
            "within_days must be positive (greater than 0)"
        ))
        raise typer.Exit(2)

    typer.echo(agents_cli.incidents_mttr(project_id, within_days))

# agents_cli.py
def incidents_mttr(project_id: str | None, within_days: int) -> str:
    async def _mttr() -> str:
        client = get_client()
        register_agents_sdk_plugin(client)

        # Manager-level validation
        manager = client.plugin_manager("incidents")
        try:
            result = await manager.calculate_mttr(
                project_id=project_id,
                within_days=within_days
            )
        except ValueError as e:
            return format_error("INVALID_PARAMETER", str(e), retry=False)

        return format_success(result)

    return asyncio.run(_mttr())

# managers.py
class IncidentManager:
    async def calculate_mttr(
        self,
        project_id: str | None = None,
        within_days: int = 30
    ) -> dict:
        # Data-level validation
        if within_days <= 0:
            raise ValueError("within_days must be positive")

        if within_days > 365:
            raise ValueError("within_days must be <= 365 days")

        # ... calculation logic
```

## Validation Rules

Define clear validation rules:

| Parameter | Type | Validation |
|-----------|------|------------|
| `count` (review_batch) | int | count > 0 |
| `within_days` (mttr) | int | 0 < within_days <= 365 |
| `actual_hours` (complete) | float | actual_hours >= 0 |
| `estimated_hours` (create) | float | estimated_hours > 0 |
| `priority` | str | Must be in [Critical, High, Medium, Low] |
| `status` | str | Must be valid status for entity |
| `effort_estimate` | str | Must be in [Small, Medium, Large] |

## Priority

**MEDIUM** - Affects usability but not core functionality

## Related Issues

- #036 - tasks next validation
- #038 - tasks complete validation
- #039 - Generic parameter validation needed

## Acceptance Criteria

- [ ] Add parameter validation to all CLI commands
- [ ] Add validation to all manager methods
- [ ] Clear error messages for invalid input
- [ ] Unit tests for validation
- [ ] Integration tests for edge cases

## Additional Notes

### Validation Helpers

Create reusable validators:

```python
# utils/validators.py
class Validators:
    @staticmethod
    def positive_int(value: int, name: str = "value") -> None:
        if value <= 0:
            raise ValueError(f"{name} must be positive (got: {value})")

    @staticmethod
    def non_negative_float(value: float, name: str = "value") -> None:
        if value < 0:
            raise ValueError(f"{name} must be non-negative (got: {value})")

    @staticmethod
    def enum(value: str, name: str, allowed: list) -> None:
        if value not in allowed:
            raise ValueError(f"{name} must be one of {allowed} (got: {value})")

# Usage
Validators.positive_int(count, "count")
Validators.non_negative_float(actual_hours, "actual_hours")
Validators.enum(priority, "priority", ["Critical", "High", "Medium", "Low"])
```

### Error Message Format

Consistent error format:

```json
{
  "error": {
    "code": "INVALID_PARAMETER",
    "message": "Clear description of what's wrong and what's expected",
    "parameter": "count",
    "value": -5,
    "expected": "positive integer (> 0)",
    "retry": false
  }
}
```

## Test Cases

```python
# Test 1: Negative count
assert_raises(ValueError) {
    await manager.review_batch(count=-5)
}

# Test 2: Zero days
assert_raises(ValueError) {
    await manager.calculate_mttr(within_days=0)
}

# Test 3: Negative hours
assert_raises(ValueError) {
    await task.complete(actual_hours=-3)
}

# Test 4: Valid parameters
assert_no_raise() {
    await manager.review_batch(count=5)
    await manager.calculate_mttr(within_days=30)
    await task.complete(actual_hours=2.5)
}
```

## Estimated Effort

- **Validation framework**: 2-3 hours
- **Add validation to all commands**: 3-4 hours
- **Tests**: 2-3 hours

**Total**: 7-10 hours for comprehensive validation coverage

---

## Commands Requiring Validation

Based on code audit, these commands need validation:

1. `ideas review` - count
2. `ideas create` - category, effort_estimate, status
3. `incidents mttr` - within_days
4. `incidents create` - severity, type, status
5. `work-issues create` - severity, type, status
6. `work-issues resolve` - resolution (should not be empty?)
7. `tasks create` - priority, type, status
8. `tasks complete` - actual_hours
9. `tasks create` - estimated_hours
10. `orgs create` - status
11. `projects create` - status
12. `versions create` - status, type

Plus all update commands for the above.
