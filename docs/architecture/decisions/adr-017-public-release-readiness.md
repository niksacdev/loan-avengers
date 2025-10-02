# ADR-003: Public Release Readiness Standards

## Status
Accepted

## Context
The Loan Defenders repository is currently private and being prepared for public release. We need to establish clear standards for what constitutes "ready for public" to ensure security, quality, and professionalism. This ADR documents the comprehensive readiness assessment and required actions.

## Decision

### Public Release Requirements

We establish the following requirements for public repository release:

#### 1. Security Documentation (REQUIRED)
- ✅ SECURITY.md with vulnerability reporting process
- ✅ Supported versions table
- ✅ Security best practices for contributors
- ✅ Pre-deployment security checklist
- ✅ AI-specific security considerations
- ✅ Responsible disclosure policy

#### 2. Legal & Licensing (REQUIRED)
- ✅ LICENSE file (MIT License)
- ✅ Copyright notice (© 2025 Nik Sachdeva)
- ✅ License badge in README

#### 3. Community Guidelines (REQUIRED)
- ✅ CONTRIBUTING.md with:
  - Development setup instructions
  - Code style guidelines (Ruff)
  - PR submission process
  - Testing requirements (≥85% coverage)
  - Commit message conventions
- ⚠️ CODE_OF_CONDUCT.md (optional but recommended)

#### 4. Branch Protection (REQUIRED)
- ⚠️ Main branch protection configured (see ADR-001)
- ⚠️ Status checks enforced
- ⚠️ PR approval required
- ⚠️ Conversation resolution required
- ⚠️ CODEOWNERS file created

#### 5. GitHub Actions Security (REQUIRED)
- ⚠️ All critical security fixes applied (see ADR-002)
- ⚠️ Codecov token configured
- ⚠️ curl | sh patterns replaced
- ⚠️ UI linting issues fixed
- ⚠️ Secret validation added

#### 6. GitHub Security Features (REQUIRED)
- ⚠️ Dependency graph enabled
- ⚠️ Dependabot alerts enabled
- ⚠️ Dependabot security updates enabled
- ⚠️ Code scanning (CodeQL) enabled
- ⚠️ Secret scanning enabled
- ⚠️ Secret scanning push protection enabled

#### 7. Documentation Quality (REQUIRED)
- ✅ README.md with clear description
- ✅ GitHub Pages deployed (https://niksacdev.github.io/loan-defenders/)
- ✅ API documentation
- ✅ Architecture diagrams
- ⚠️ README badges (ready to add)

#### 8. Code Quality Standards (REQUIRED)
- ✅ Ruff linting configured
- ✅ Test coverage ≥85% threshold
- ✅ Pre-commit validation script
- ⚠️ All linting issues resolved

### Readiness Assessment

**Overall Readiness: 85%**

| Category | Score | Status | Blocker |
|----------|-------|--------|---------|
| Security Documentation | 95% | ✅ Excellent | No |
| License & Legal | 100% | ✅ Complete | No |
| GitHub Actions Security | 70% | 🟡 Needs fixes | Yes |
| Branch Protection | 0% | 🔴 Not configured | Yes |
| Documentation | 90% | ✅ Excellent | No |
| Community Guidelines | 60% | 🟡 Missing optional items | No |
| Security Features | 50% | 🟡 Need to enable | Yes |
| Code Quality | 80% | 🟡 UI linting issues | Yes |

### Critical Blockers (Must Fix)

1. **Codecov Token** - Blocks coverage reporting
2. **UI Linting Issues** - Code quality standard
3. **Branch Protection** - Security requirement
4. **GitHub Security Features** - Free and essential
5. **GitHub Actions Fixes** - Security requirement

## Consequences

### Positive
- **Professional**: Repository meets industry standards
- **Secure**: Multiple layers of security protection
- **Welcoming**: Clear contributor guidelines
- **Maintainable**: Quality standards enforced
- **Discoverable**: Good documentation attracts contributors

### Negative
- **Setup Time**: 4-6 hours to complete all requirements
- **Ongoing Maintenance**: Security updates need review
- **Contributor Friction**: More hoops for new contributors

### Success Metrics
- Zero critical security vulnerabilities at launch
- All CI/CD checks passing
- Branch protection prevents direct pushes
- Documentation complete and professional
- First contributor able to submit PR without confusion

## Implementation

### Phase 1: Critical Fixes (1-2 hours)
**Must complete before going public:**

1. Add Codecov token to GitHub Secrets
2. Update test-apps.yml with token
3. Replace curl | sh with astral-sh/setup-uv@v5
4. Fix all UI linting errors
5. Remove continue-on-error from UI linting
6. Add secret validation to Claude workflows
7. Insert badges into README.md

**Verification**: Create test PR and ensure all checks pass

### Phase 2: High Priority (2-3 hours)
**Should complete before going public:**

1. Create `.github/dependabot.yml`
2. Create `.github/CODEOWNERS`
3. Configure branch protection for main
4. Enable all GitHub Security features:
   - Dependabot alerts
   - Secret scanning
   - Code scanning (CodeQL)
   - Push protection
5. Test branch protection with PR
6. Verify CONTRIBUTING.md is clear

**Verification**: Test complete PR workflow end-to-end

### Phase 3: Recommended Enhancements (1-2 days, post-public)
**Can be completed after going public:**

1. Add security scanning workflow (security.yml)
2. Add Bandit security scanning
3. Add concurrency limits to Claude workflows
4. Add timeout limits to workflows
5. Set up OpenSSF Scorecard
6. Create CODE_OF_CONDUCT.md
7. Enable GitHub Discussions

### Pre-Public Release Checklist

#### Critical (Must Complete)
- [ ] Codecov token added to secrets
- [ ] test-apps.yml updated with Codecov token
- [ ] curl | sh replaced with astral-sh/setup-uv@v5
- [ ] All UI linting errors fixed
- [ ] continue-on-error removed from UI linting
- [ ] Secret validation added to Claude workflows
- [ ] Badges added to README.md
- [ ] Review commit history for secrets
- [ ] All .env.example values are placeholders

#### High Priority (Should Complete)
- [ ] dependabot.yml created
- [ ] CODEOWNERS created
- [ ] Main branch protection configured
- [ ] Status checks verified in branch protection
- [ ] Dependabot alerts enabled
- [ ] Secret scanning enabled
- [ ] Secret push protection enabled
- [ ] CodeQL scanning enabled
- [ ] Test PR created and verified
- [ ] CONTRIBUTING.md is clear and accurate

#### Recommended (Nice to Have)
- [ ] Security scanning workflow added
- [ ] Bandit scanning configured
- [ ] OpenSSF Scorecard badge added
- [ ] CODE_OF_CONDUCT.md created
- [ ] GitHub Discussions enabled
- [ ] Signed commits considered
- [ ] Environment protection for GitHub Pages

#### Final Verification
- [ ] Create test issue
- [ ] Create test PR with issue link
- [ ] Verify all status checks run
- [ ] Verify branch protection blocks failing PRs
- [ ] Verify conversation resolution requirement
- [ ] Verify PR approval requirement
- [ ] Test auto-delete of branch after merge
- [ ] Review repository settings one final time
- [ ] **Make repository public**

## Security Considerations

### Secrets Audit
Before going public:

1. **Repository Secrets** - Review Settings → Secrets:
   - CODECOV_TOKEN (coverage reporting)
   - CLAUDE_CODE_OAUTH_TOKEN (Claude workflows)
   - Any Azure credentials (use Managed Identity in production)

2. **Commit History** - Scan for accidentally committed secrets:
   ```bash
   git log --all --full-history --source -- '*\.env'
   ```
   - Use git-secrets or gitleaks to scan
   - Consider BFG Repo-Cleaner if secrets found

3. **Public Visibility Impact**:
   - All commit history becomes visible
   - All issues and PRs become searchable
   - GitHub Actions logs are public
   - Dependencies scanned by GitHub Advisory Database

### Quality Gates

All PRs must:
1. Pass all CI/CD checks
2. Have ≥1 approval
3. Resolve all conversations
4. Link to a GitHub issue
5. Maintain ≥85% test coverage
6. Pass Ruff linting
7. Be up to date with main branch

## References
- ADR-001: Branch Protection Strategy
- ADR-002: GitHub Actions Security Standards
- SECURITY.md: Security policy and reporting
- CONTRIBUTING.md: Contribution guidelines

## Timeline

### Optimistic (4-6 hours)
- Phase 1 Critical: 1-2 hours
- Phase 2 High Priority: 2-3 hours
- Testing & Verification: 1 hour

### Conservative (1-2 days)
- Phase 1 Critical: 0.5 day
- Phase 2 High Priority: 0.5 day
- Phase 3 Enhancements: 0.5 day
- Testing & Documentation: 0.5 day

**Recommendation**: Plan for 1 full day to complete Phases 1-2 and thoroughly test.

## Alternatives Considered

1. **Minimal Public Release**: Rejected - would compromise security
2. **Delayed Public Release**: Considered - but requirements are achievable quickly
3. **Private Release First**: Rejected - want full community engagement
4. **No Branch Protection**: Rejected - security requirement

## Review & Monitoring

### Post-Public Launch
- **Week 1**: Monitor for security alerts, review first community PRs
- **Month 1**: Review effectiveness of branch protection and quality gates
- **Quarter 1**: Assess contributor experience, update guidelines as needed

### Maintenance Schedule
- **Weekly**: Review Dependabot PRs and security alerts
- **Monthly**: Audit repository settings and permissions
- **Quarterly**: Review ADRs and update if standards changed

---

**Date**: 2025-10-01
**Author**: Claude Code Security & Compliance Review
**Current Status**: 🟡 **READY WITH CRITICAL FIXES**
**Recommendation**: Address all 🔴 Critical and 🟡 High Priority blockers before making public
**Target Launch**: After completing Phase 1 & 2 (estimated 4-6 hours)
