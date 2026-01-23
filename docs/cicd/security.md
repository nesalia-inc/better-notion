# Security in CI/CD

Complete guide to security considerations and best practices for the Better Notion SDK CI/CD pipeline.

## Overview

Security is critical throughout the CI/CD pipeline. This document covers secrets management, secure workflows, and best practices.

**Principles:**
- **Least privilege**: Minimal access required
- **No hardcoded secrets**: Secrets in environment variables only
- **Auditability**: All actions logged and traceable
- **Secure by default**: Safe configurations out of the box

---

## Secrets Management

### Required Secrets

#### 1. PYPI_API_TOKEN

**Purpose:** Publish packages to PyPI

**Used in:** `.github/workflows/release.yml`

**How to generate:**
1. Visit https://pypi.org/manage/account/token/
2. Create new token
3. Scope: "entire account" or specific project
4. Copy token

**How to add to GitHub:**
```bash
# Using GitHub CLI
gh secret set PYPI_API_TOKEN

# Or via GitHub UI:
# Settings → Secrets and variables → Actions → New repository secret
```

**Permissions:** PyPI upload

**Security considerations:**
- Use project-scoped tokens when possible
- Rotate tokens regularly
- Revoke if compromised

#### 2. CODECOV_TOKEN

**Purpose:** Upload coverage reports to Codecov

**Used in:** `.github/workflows/ci.yml`, `.github/workflows/test.yml`

**How to get:**
1. Visit https://codecov.io/
2. Connect GitHub repository
3. Get token from repository settings

**How to add to GitHub:**
```bash
gh secret set CODECOV_TOKEN
```

**Permissions:** Upload coverage (read-only repo access)

**Security considerations:**
- Public repos: Can use public upload (no token)
- Private repos: Token required
- Rotate if access leaks

#### 3. NOTION_TEST_TOKEN (Optional)

**Purpose:** Run integration tests against real Notion API

**Used in:** `tests/integration/`

**How to add to GitHub:**
```bash
gh secret set NOTION_TEST_TOKEN
```

**Permissions:** Notion API access (integration-specific)

**Security considerations:**
- Use dedicated test integration
- Limit integration access (test workspace only)
- Rotate regularly
- Never use production token

### Optional Secrets

#### GITHUB_TOKEN

**Purpose:** GitHub Actions auto-provided token

**Used in:** All workflows (automatic)

**Permissions:** Configured per workflow

**Example:**
```yaml
permissions:
  contents: write  # For creating releases
```

**Security considerations:**
- Auto-generated, no manual setup
- Grant minimal permissions needed
- Different permissions per workflow

---

## Secret Usage in Workflows

### Reference Syntax

**In workflow files:**
```yaml
steps:
  - name: Publish to PyPI
    run: uv publish
    env:
      PYPI_API_TOKEN: ${{ secrets.PYPI_API_TOKEN }}
```

**In Python code:**
```python
import os

token = os.getenv("PYPI_API_TOKEN")
if not token:
    raise ValueError("PYPI_API_TOKEN not set")
```

### Environment Variables in CI

**Setting in workflow:**
```yaml
steps:
  - name: Run integration tests
    env:
      NOTION_TOKEN: ${{ secrets.NOTION_TEST_TOKEN }}
    run: uv run pytest tests/integration/
```

**Using in tests:**
```python
import os
import pytest

def test_real_api_call():
    token = os.getenv("NOTION_TOKEN")
    if not token:
        pytest.skip("NOTION_TOKEN not set")
    # Use token for test
```

---

## Security Best Practices

### 1. Never Commit Secrets

**AVOID:**
```python
# AVOID: Hardcoded secret
API_TOKEN = "secret_abc123..."

# AVOID: Secret in config
config = {
    "token": "secret_abc123..."
}
```

**GOOD:**
```python
# GOOD: Environment variable
import os
API_TOKEN = os.getenv("API_TOKEN")
if not API_TOKEN:
    raise ValueError("API_TOKEN not set")
```

### 2. Use GitHub Secrets

**Benefits:**
- Encrypted at rest
- Only exposed to workflows
- Audit log of access
- Can be revoked

**How to use:**
```yaml
env:
  MY_SECRET: ${{ secrets.MY_SECRET }}
```

### 3. Principle of Least Privilege

**Workflow permissions:**
```yaml
permissions:
  contents: read      # Only read code
  pull-requests: read # Only read PRs
```

**PyPI token scopes:**
- Use project-specific tokens when possible
- Don't use account-wide tokens unless needed

### 4. Secret Rotation

**Schedule:**
- PyPI tokens: Every 6 months
- Test tokens: Every 3 months
- After any suspected compromise

**Process:**
1. Generate new token
2. Update GitHub secret
3. Verify new token works
4. Revoke old token

### 5. Audit Secret Usage

**Check what secrets are used:**
```bash
# List all secrets
gh secret list

# Search for secret usage in workflows
grep -r "secrets\." .github/workflows/
```

**Review access:**
- GitHub Actions logs show when secrets are accessed
- PyPI shows upload history
- Codecov shows upload history

---

## Workflow Security

### Permission Management

**Minimal permissions:**

**CI workflow:**
```yaml
permissions:
  contents: read  # Only need to read code
```

**Release workflow:**
```yaml
permissions:
  contents: write  # Need to create releases
```

**Avoid:**
```yaml
# AVOID: Overly permissive
permissions: write-all
```

### Third-Party Actions

**Pin to specific versions:**
```yaml
# GOOD: Pinned version
- uses: actions/checkout@v3

# AVOID: Moving target
- uses: actions/checkout@main
```

**Use trusted actions:**
- Official GitHub actions
- Verified actions from trusted publishers
- Check action code before using

### Code Injection Prevention

**Don't use user input in commands:**
```yaml
# AVOID: Potential injection
- name: Run command
  run: ./script.sh ${{ github.event.comment.body }}

# GOOD: Validate input first
- name: Validate and run
  run: |
    if [[ "${{ github.event.comment.body }}" =~ ^[a-z0-9_]+$ ]]; then
      ./script.sh "${{ github.event.comment.body }}"
    fi
```

---

## Dependency Security

### Supply Chain Security

**Pin dependency versions:**
```toml
[project]
dependencies = [
    "httpx>=0.25.0,<0.26.0",  # Pinned minor version
]
```

**Use lock file:**
```bash
# Generate lock file
uv lock

# Commit lock file
git add uv.lock
git commit -m "Add lock file"
```

**Audit dependencies:**
```bash
# Check for vulnerabilities
pip-audit
```

### Dependency Updates

**Automated updates:**
- Use Dependabot or Renovate
- Review PRs before merging
- Run tests on update PRs

**Example Dependabot config:**
```yaml
# .github/dependabot.yml
version: 2
updates:
  - package-ecosystem: "pip"
    directory: "/"
    schedule:
      interval: "weekly"
```

---

## Test Data Security

### Never Commit Real Credentials

**Use test fixtures instead:**
```python
# GOOD: Mock data
@pytest.fixture
def mock_page_response():
    return {
        "id": "test_page_id",
        "object": "page",
        # ...
    }

# AVOID: Real credentials
TEST_TOKEN = "secret_abc123..."
```

### Test Integration Tokens

**Use dedicated test integration:**
- Create separate Notion integration for testing
- Limit to test workspace
- Minimal permissions

**Store in GitHub Secrets:**
```bash
gh secret set NOTION_TEST_TOKEN
```

### Local Testing

**Use `.env` file (gitignored):**
```bash
# .env
NOTION_TOKEN=secret_abc123...
```

**`.gitignore`:**
```
.env
.env.local
*.key
```

---

## Release Security

### PyPI Trusted Publishing

**Use trusted publishing (recommended):**

Instead of API tokens, use GitHub OIDC provider:

1. **Configure PyPI:**
   - Visit: https://pypi.org/manage/account/publishing/
   - Add GitHub repository as publisher
   - Specify workflow name

2. **Update workflow:**
```yaml
- name: Publish to PyPI
  run: uv publish
  # No PYPI_API_TOKEN needed!
```

**Benefits:**
- No token to manage
- More secure (OIDC-based)
- Auto-rotating credentials

**Fallback:** Use `PYPI_API_TOKEN` if trusted publishing unavailable

### Verify Before Publishing

**Verify builds locally:**
```bash
# Build
uv build

# Check contents
tar -tzf dist/better_notion-1.0.0.tar.gz

# Install and test
pip install dist/better_notion-1.0.0-py3-none-any.whl
python -c "from better_notion import NotionAPI"
```

### Tag Security

**Signed tags (optional):**
```bash
# Configure GPG signing
git config user.signingkey YOUR_KEY_ID
git config commit.gpgsign true

# Create signed tag
git tag -s v1.0.0 -m "Release v1.0.0"
```

**Verify tags:**
```bash
git tag -v v1.0.0
```

---

## Access Control

### Branch Protection

**Protected branches:**
- `main` branch should be protected
- Require status checks
- Require PR reviews

**GitHub settings:**
```
Settings → Branches → Add rule
Branch name pattern: main
☑ Require status checks to pass before merging
☑ Require pull request reviews before merging
```

### Required Reviewers

**Require review for changes:**
```
Settings → Branches → main → Require pull request reviews
☑ Require approvals: 1
☑ Dismiss stale reviews
```

### CI as Gatekeeper

**Require CI checks:**
```
Settings → Branches → main → Require status checks
☑ lint
☑ test (Python 3.10)
☑ test (Python 3.11)
☑ test (Python 3.12)
☑ coverage
```

---

## Security Monitoring

### Audit Logs

**GitHub Actions logs:**
- All workflow runs logged
- Secret usage visible (as `***`)
- Can download logs

**Check for anomalies:**
```bash
# List recent workflow runs
gh run list --limit 20

# View specific run
gh run view RUN_ID
```

### Dependency Vulnerability Scanning

**Use GitHub security features:**
- Dependabot alerts (automatic)
- Code scanning (optional)
- Secret scanning (automatic)

**Configure:**
```
Settings → Code security → Dependabot alerts
☑ Enable Dependabot security updates
```

### PyPI Security

**Monitor PyPI:**
- Check for unusual uploads
- Verify upload history
- Monitor download stats

**Visit:** https://pypi.org/manage/project/better-notion/

---

## Incident Response

### Secret Leaked

**If secret is committed:**
1. **Rotate secret immediately**
   - Generate new token
   - Update GitHub secret
   - Revoke old token

2. **Remove from git history:**
   ```bash
   # Using BFG Repo-Cleaner
   bfg --replace-text passwords.txt

   # Or using git filter-repo
   git filter-repo --invert-paths --path FILE_WITH_SECRET
   ```

3. **Force push:**
   ```bash
   git push origin --force
   ```

4. **Notify users** (if applicable)
   - Post announcement
   - Recommend rotation

### Malicious Package

**If PyPI package compromised:**
1. **Yank package:**
   ```bash
   twine yank better-notion==VERSION
   ```

2. **Create fix release:**
   ```bash
   git tag vVERSION+1
   git push origin vVERSION+1
   ```

3. **Notify users:**
   - GitHub advisory
   - PyPI advisory
   - Security announcement

### CI Compromise

**If workflow compromised:**
1. **Disable workflows:**
   ```bash
   gh workflow disable WORKFLOW_NAME
   ```

2. **Review workflow files:**
   - Check for unauthorized changes
   - Verify third-party actions
   - Check permissions

3. **Re-enable after fix:**
   ```bash
   gh workflow enable WORKFLOW_NAME
   ```

---

## Compliance Considerations

### Data Protection

**No PII in CI:**
- Don't test with real user data
- Use synthetic test data
- Anonymize logs

**No secrets in logs:**
- GitHub automatically masks secrets
- Verify masking works
- Don't echo secrets

### Licensing

**Check licenses:**
```bash
# List dependency licenses
pip-licenses
```

**Ensure compatible licenses:**
- All dependencies OSI-approved
- Compatible with MIT license

---

## Security Checklist

### Pre-Release

- [ ] No secrets in code
- [ ] Dependencies scanned for vulnerabilities
- [ ] Build verified locally
- [ ] Release workflow reviewed
- [ ] PyPI token rotated (if needed)

### Post-Release

- [ ] PyPI package verified
- [ ] Download monitored
- [ ] No unexpected issues reported
- [ ] Dependencies still secure

### Ongoing

- [ ] Dependabot alerts reviewed
- [ ] Secrets rotated regularly
- [ ] Access logs audited
- [ ] Security updates applied

---

## Related Documentation

- [CI Workflows](./ci-workflows.md) - Workflow security configurations
- [Release Process](./releases.md) - Secure release practices
- [Overview](./overview.md) - Security in CI/CD strategy

---

## Summary

**Security Best Practices:**

1. **Secrets:**
   - Store in GitHub Secrets only
   - Never commit to repository
   - Rotate regularly

2. **Permissions:**
   - Least privilege principle
   - Minimal workflow permissions
   - Branch protection enabled

3. **Dependencies:**
   - Pin versions
   - Use lock files
   - Scan for vulnerabilities

4. **Monitoring:**
   - Review audit logs
   - Check for anomalies
   - Respond to incidents

**Required Secrets:**
- `PYPI_API_TOKEN` - PyPI publishing
- `CODECOV_TOKEN` - Coverage uploads (optional for public repos)
- `NOTION_TEST_TOKEN` - Integration tests (optional)

**Tools:**
- GitHub Secrets - Secret management
- Dependabot - Dependency security
- PyPI Trusted Publishing - Secure publishing
