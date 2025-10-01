# Security Policy

## Supported Versions

We release patches for security vulnerabilities. Which versions are eligible for receiving such patches depends on the CVSS v3.0 Rating:

| Version | Supported          |
| ------- | ------------------ |
| 0.1.x   | :white_check_mark: |
| < 0.1   | :x:                |

## Reporting a Vulnerability

We take the security of Loan Avengers seriously. If you believe you have found a security vulnerability, please report it to us as described below.

### Where to Report

**For security vulnerabilities, please use GitHub Issues with the `security` label:**

1. **Create a GitHub Issue (Preferred)**:
   - Go to [Issues](https://github.com/niksacdev/loan-avengers/issues/new)
   - Add the `security` label
   - Provide detailed information about the vulnerability
   - If you have a fix, submit a PR and reference the issue

2. **Submit a Pull Request with Fix**:
   - Create a PR with your security fix
   - Add the `security` label to the PR
   - Reference the related security issue
   - Describe the vulnerability and your solution

### What to Include in Your Report

Please include as much of the following information as possible:

- Type of vulnerability (e.g., SQL injection, XSS, authentication bypass, prompt injection, etc.)
- Full paths of source file(s) related to the vulnerability
- Location of the affected source code (tag/branch/commit or direct URL)
- Step-by-step instructions to reproduce the issue
- Proof-of-concept or exploit code (if possible)
- Impact of the issue, including how an attacker might exploit it
- Any suggested fixes or mitigations

### Response Timeline

- **Initial Response**: We will acknowledge your issue within 48 hours
- **Investigation**: We will investigate and validate the issue within 7 days
- **Fix Development**: Critical issues will be patched within 14 days; other issues within 30 days
- **Recognition**: Contributors will be credited in release notes and issue comments

### What to Expect

After submitting a security issue or PR:

1. You will receive an acknowledgment comment within 48 hours
2. We will confirm the vulnerability and determine its severity
3. We will review your PR (if submitted) or develop a fix
4. We will merge the fix and create a release with security notes
5. You will be credited as a security contributor (unless you prefer to remain anonymous)

## Security Best Practices for Contributors

### For Developers

1. **Never commit secrets**:
   - Use `.env` files for local development (already in `.gitignore`)
   - Never hardcode API keys, passwords, or tokens
   - Use Azure Managed Identity for production deployments
   - Review `.env.example` for proper configuration patterns

2. **Input validation**:
   - Always validate and sanitize user input
   - Use Pydantic models for type-safe data validation
   - Validate UUIDs and ensure proper format
   - Sanitize file paths to prevent directory traversal

3. **Authentication & Authorization**:
   - Use Azure Entra ID for production authentication
   - Implement proper session management
   - Validate session tokens on every request
   - Use HTTPS in production (enforced by Azure Container Apps)

4. **Dependencies**:
   - Keep dependencies up to date (`uv sync` regularly)
   - Review security advisories for dependencies
   - Use `uv` for deterministic dependency resolution
   - Monitor Dependabot alerts

5. **Code Review**:
   - All code changes must go through PR review
   - Security-sensitive changes require extra scrutiny
   - Use pre-commit hooks for linting and security checks
   - Run `uv run ruff check .` before committing

### Security-Sensitive Areas

Pay extra attention when working with these components:

1. **API Endpoints** (`loan_avengers/api/app.py`):
   - Session validation
   - CORS configuration
   - Input sanitization
   - Rate limiting

2. **Agent Orchestration** (`loan_avengers/agents/`):
   - Prompt injection prevention
   - Tool access control
   - Context isolation between sessions

3. **MCP Servers** (`loan_avengers/tools/mcp_servers/`):
   - Input validation
   - Secure parameter handling
   - No PII in logs
   - Always use `applicant_id` (UUID), never SSN

4. **Data Models** (`loan_avengers/models/`):
   - PII handling
   - Data encryption requirements
   - Validation rules

### Pre-Deployment Security Checklist

Before deploying to production:

- [ ] All secrets stored in Azure Key Vault or environment variables
- [ ] CORS origins restricted to production domains
- [ ] Debug mode disabled (`APP_DEBUG=false`)
- [ ] HTTPS enforced (automatic with Azure Container Apps)
- [ ] Azure Managed Identity configured
- [ ] Application Insights configured for security monitoring
- [ ] Session timeout configured appropriately
- [ ] Input validation on all endpoints
- [ ] Rate limiting enabled
- [ ] Security headers configured (CSP, HSTS, X-Frame-Options)

## Known Security Considerations

### Development vs Production

This is a **demonstration application** showcasing AI agent patterns. For production use:

1. **Authentication**:
   - Demo uses session-based auth for simplicity
   - Production should use Azure Entra ID + OAuth 2.0
   - Implement proper user identity management

2. **PII Protection**:
   - Demo uses synthetic test data
   - Production must encrypt PII at rest and in transit
   - Implement proper data retention policies
   - Follow GDPR/CCPA compliance requirements

3. **Rate Limiting**:
   - Demo has no rate limits
   - Production should implement API rate limiting
   - Protect against denial-of-service attacks

4. **Audit Logging**:
   - Demo logs to stdout/Application Insights
   - Production should implement comprehensive audit trails
   - Log all access to sensitive data

### AI-Specific Security

When working with AI agents:

1. **Prompt Injection**:
   - Never trust user input in agent prompts
   - Sanitize and validate all inputs
   - Use structured outputs (Pydantic) instead of free text parsing

2. **Tool Access Control**:
   - Limit MCP server access based on agent role
   - Validate tool parameters before execution
   - Log all tool invocations

3. **Context Isolation**:
   - Ensure sessions are isolated
   - Clear sensitive data from agent context
   - Don't leak information between users

4. **Output Validation**:
   - Validate all agent outputs
   - Sanitize before displaying to users
   - Never execute agent-generated code without validation

## Disclosure Policy

We believe in responsible disclosure:

1. **Coordination**: We will work with you to understand and resolve the issue
2. **Timeline**: We aim to patch critical issues within 14 days
3. **Credit**: We will credit researchers in security advisories (if desired)
4. **Public Disclosure**: We will coordinate disclosure timing with you

## Security Updates

Security updates will be:

- Published in [GitHub Security Advisories](https://github.com/niksacdev/loan-avengers/security/advisories)
- Tagged in releases with `[SECURITY]` prefix
- Announced in the repository README
- Documented in CHANGELOG.md

## Resources

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [Azure Security Best Practices](https://learn.microsoft.com/en-us/azure/security/fundamentals/best-practices-and-patterns)
- [Microsoft Agent Framework Security](https://github.com/microsoft/agent-framework)
- [Python Security Best Practices](https://python.readthedocs.io/en/stable/library/security_warnings.html)

## Questions?

If you have questions about this security policy, please open a [GitHub Discussion](https://github.com/niksacdev/loan-avengers/discussions) in the Security category.

---

**Thank you for helping keep Loan Avengers and our users safe!**
