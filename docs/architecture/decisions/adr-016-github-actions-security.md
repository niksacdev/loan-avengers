# ADR-002: GitHub Actions Security Standards

## Status
Accepted

## Context
Before making the repository public, we performed a comprehensive security review of all GitHub Actions workflows. We identified security issues ranging from critical (missing tokens) to best practice improvements. This ADR documents the security standards and required fixes.

## Decision

### Security Standards for All Workflows

1. **Action Version Pinning**
   - Always use specific version tags (`@v4`, `@v5`)
   - Never use `@main` or `@latest`
   - Update versions via Dependabot

2. **Minimal Permissions**
   - Use principle of least privilege
   - Specify exact permissions needed
   - Default to read-only where possible

3. **Secret Handling**
   - Reference secrets via `${{ secrets.NAME }}`
   - Never hardcode credentials
   - Validate secrets exist before use
   - Add validation steps to workflows

4. **Secure Installation Methods**
   - Use official GitHub Actions over `curl | sh`
   - Prefer `astral-sh/setup-uv@v5` over curl script
   - Validate checksums when downloading binaries

5. **No Sensitive Data in Logs**
   - Mask secrets in workflow output
   - Avoid printing environment variables
   - Sanitize error messages

### Critical Fixes Required

#### 1. Add Codecov Token (CRITICAL)
**Location**: `.github/workflows/test-apps.yml:44-48`

```yaml
- name: Upload coverage to Codecov
  uses: codecov/codecov-action@v4
  with:
    token: ${{ secrets.CODECOV_TOKEN }}
    file: ./apps/api/coverage.xml
    flags: api
    name: api-coverage
```

**Action**: Add `CODECOV_TOKEN` to repository secrets

#### 2. Replace curl | sh Pattern (HIGH PRIORITY)
**Location**: `.github/workflows/test-apps.yml:24`

Replace:
```yaml
- name: Install uv
  run: curl -LsSf https://astral.sh/uv/install.sh | sh
```

With:
```yaml
- name: Install uv
  uses: astral-sh/setup-uv@v5
  with:
    version: "latest"
    enable-cache: true
```

#### 3. Remove Linting continue-on-error (HIGH PRIORITY)
**Location**: `.github/workflows/test-apps.yml:69-72`

After fixing all linting issues, change:
```yaml
- name: Run linting
  working-directory: apps/ui
  run: npm run lint || echo "⚠️  Linting has warnings"
  continue-on-error: true
```

To:
```yaml
- name: Run linting
  working-directory: apps/ui
  run: npm run lint
```

#### 4. Add Secret Validation (HIGH PRIORITY)
**Location**: `.github/workflows/claude-code-review.yml` and `.github/workflows/claude.yml`

Add validation step:
```yaml
- name: Validate secrets
  run: |
    if [ -z "${{ secrets.CLAUDE_CODE_OAUTH_TOKEN }}" ]; then
      echo "❌ CLAUDE_CODE_OAUTH_TOKEN not configured"
      echo "See: https://docs.claude.com/en/docs/claude-code"
      exit 1
    fi
    echo "✅ Claude Code token configured"
```

### Workflow-Specific Security Grades

1. **test-apps.yml**: B+ (needs Codecov token, uv action, linting fix)
2. **docs.yml**: A- (excellent, minimal issues)
3. **require-linked-issue.yml**: A (well-designed)
4. **claude-code-review.yml**: B+ (needs secret validation)
5. **claude.yml**: A- (needs secret validation)

### Recommended Enhancements

#### Enable Dependabot
Create `.github/dependabot.yml`:
```yaml
version: 2
updates:
  - package-ecosystem: "pip"
    directory: "/apps/api"
    schedule:
      interval: "weekly"
    open-pull-requests-limit: 10

  - package-ecosystem: "npm"
    directory: "/apps/ui"
    schedule:
      interval: "weekly"
    open-pull-requests-limit: 10

  - package-ecosystem: "github-actions"
    directory: "/"
    schedule:
      interval: "weekly"
```

#### Add Workflow Concurrency Limits
For Claude workflows, add:
```yaml
concurrency:
  group: claude-review-${{ github.event.pull_request.number }}
  cancel-in-progress: true

timeout-minutes: 15
```

#### Add Security Scanning
Create `.github/workflows/security.yml` with:
- CodeQL analysis for Python and JavaScript
- Bandit security scanning for Python
- Weekly scheduled runs
- Upload results to GitHub Security tab

## Consequences

### Positive
- **Secure CI/CD**: Workflows follow security best practices
- **Automated Updates**: Dependabot keeps actions current
- **Cost Control**: Timeouts and concurrency prevent runaway costs
- **Visibility**: Security scanning provides early warning

### Negative
- **Initial Setup Time**: Configuring tokens and secrets takes effort
- **False Positives**: Security scans may flag benign code
- **Maintenance**: Regular review of Dependabot PRs needed

### Metrics
- All workflows must pass security review before public release
- Zero critical security issues in production workflows
- Dependabot PRs reviewed within 7 days
- Security scanning results reviewed weekly

## Implementation

### Pre-Public Release Checklist
- [ ] Add CODECOV_TOKEN to repository secrets
- [ ] Update test-apps.yml with Codecov token
- [ ] Replace curl | sh with astral-sh/setup-uv@v5
- [ ] Fix all UI linting issues
- [ ] Remove continue-on-error from UI linting
- [ ] Add secret validation to Claude workflows
- [ ] Create .github/dependabot.yml
- [ ] Enable GitHub Security features
- [ ] Test all workflows with sample PR

### Post-Public Enhancements
- [ ] Create security.yml workflow with CodeQL
- [ ] Add Bandit scanning
- [ ] Add concurrency limits to Claude workflows
- [ ] Set up automated security scanning reports
- [ ] Configure workflow usage alerts

## References
- GitHub Actions Security Best Practices: https://docs.github.com/en/actions/security-guides/security-hardening-for-github-actions
- Dependabot Configuration: https://docs.github.com/en/code-security/dependabot
- CodeQL Documentation: https://docs.github.com/en/code-security/code-scanning
- SECURITY.md: Repository security policy

## Alternatives Considered

1. **Self-hosted Runners**: Rejected due to maintenance overhead
2. **Third-party Security Tools**: Using GitHub native features for simplicity
3. **Manual Reviews Only**: Rejected; automated checks catch issues faster

---

**Date**: 2025-10-01
**Author**: Claude Code Security Review
**Overall Security Grade**: B+ (Good, with room for improvement)
**Target Grade**: A (after critical fixes)
