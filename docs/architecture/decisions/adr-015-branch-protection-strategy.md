# ADR-001: Branch Protection Strategy for Public Release

## Status
Accepted

## Context
Before making the Loan Defenders repository public, we need to establish branch protection rules to ensure code quality, security, and proper review processes. This prevents direct pushes to main, enforces CI/CD checks, and maintains professional development standards.

## Decision

### Main Branch Protection Rules
We will enforce the following protection rules on the `main` branch:

1. **Require Pull Request with Approval**
   - Minimum 1 approval required
   - Dismiss stale reviews when new commits pushed
   - Require Code Owners approval (after CODEOWNERS created)

2. **Require Status Checks to Pass**
   - Test API App (from `test-apps.yml`)
   - Test UI App (from `test-apps.yml`)
   - Validate Monorepo Structure (from `test-apps.yml`)
   - Require Linked Issue (from `require-linked-issue.yml`)
   - Require branches up to date before merging

3. **Require Conversation Resolution**
   - All review comments must be resolved before merge

4. **Require Linear History**
   - Enforce squash or rebase merging
   - Disable merge commits

5. **Restrict Direct Pushes**
   - Only repository administrators can push
   - All changes go through PR process
   - No force pushes allowed
   - No branch deletions allowed

6. **No Bypassing Rules**
   - Even admins must follow rules
   - Exception: Emergency hotfixes (documented)

### GitHub Repository Settings

**Pull Requests**:
- Allow squash merging: ✅ Enabled
- Allow rebase merging: ✅ Enabled
- Allow merge commits: ❌ Disabled
- Automatically delete head branches: ✅ Enabled
- Allow auto-merge: ✅ Enabled (after approvals)

**Security & Analysis**:
- Dependency graph: ✅ Enabled
- Dependabot alerts: ✅ Enabled
- Dependabot security updates: ✅ Enabled
- Code scanning (CodeQL): ✅ Enabled
- Secret scanning: ✅ Enabled
- Secret scanning push protection: ✅ Enabled

### CODEOWNERS Configuration

Create `.github/CODEOWNERS`:
```
# Repository owner
* @niksacdev

# Workflow files require security review
/.github/workflows/ @niksacdev

# Security-sensitive files
/SECURITY.md @niksacdev
/.env.example @niksacdev
```

## Consequences

### Positive
- **Code Quality**: All code reviewed before merging
- **Security**: Automated security checks prevent vulnerabilities
- **Traceability**: Every change linked to GitHub issue
- **Professional**: Industry-standard development practices
- **Clean History**: Linear history easier to understand and debug

### Negative
- **Slower Merges**: PRs must wait for approvals and checks
- **Setup Complexity**: Initial configuration requires time
- **Contributor Friction**: New contributors face more requirements

### Mitigation Strategies
- Clear documentation in CONTRIBUTING.md
- Pre-commit hooks help catch issues early
- Automated checks provide fast feedback
- Code Owners expedite review process

## Implementation

### Phase 1: Immediate (Pre-Public)
1. Create `.github/CODEOWNERS` file
2. Configure main branch protection in GitHub Settings
3. Enable all security features
4. Test with sample PR

### Phase 2: Post-Public
1. Monitor for false positives in security scanning
2. Adjust status check requirements if needed
3. Add additional Code Owners as team grows

### Emergency Procedures
When branch protection must be disabled:
1. Document reason in GitHub issue
2. Admin temporarily disables specific rule
3. Make emergency change with justification
4. Re-enable protection immediately
5. Create PR documenting what was done
6. Conduct retrospective

## References
- GitHub Branch Protection Documentation: https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches
- CONTRIBUTING.md: Guidelines for contributors
- SECURITY.md: Security policy and reporting

## Review Schedule
- **Weekly**: Check for failed status checks
- **Monthly**: Review effectiveness of rules
- **Quarterly**: Audit admin access and bypass permissions
- **After incidents**: Update rules to prevent similar issues

---

**Date**: 2025-10-01
**Author**: Claude Code Security Review
**Stakeholders**: @niksacdev, future contributors
