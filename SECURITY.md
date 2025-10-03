# Security Policy

## Supported Versions

We release patches for security vulnerabilities. Which versions are eligible for receiving such patches depends on the CVSS v3.0 Rating:

| Version | Supported          |
| ------- | ------------------ |
| 0.1.x   | :white_check_mark: |
| < 0.1   | :x:                |

## Reporting a Vulnerability

We take the security of Loan Defenders seriously. If you believe you have found a security vulnerability, please report it to us as described below.

### Where to Report

**For security vulnerabilities, please use GitHub Issues with the `security` label:**

1. **Create a GitHub Issue (Preferred)**:
   - Go to [Issues](https://github.com/niksacdev/loan-defenders/issues/new)
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

1. **API Endpoints** (`loan_defenders/api/app.py`):
   - Session validation
   - CORS configuration
   - Input sanitization
   - Rate limiting

2. **Agent Orchestration** (`loan_defenders/agents/`):
   - Prompt injection prevention
   - Tool access control
   - Context isolation between sessions

3. **MCP Servers** (`loan_defenders/tools/mcp_servers/`):
   - Input validation
   - Secure parameter handling
   - No PII in logs
   - Always use `applicant_id` (UUID), never SSN

4. **Data Models** (`loan_defenders/models/`):
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

- Published in [GitHub Security Advisories](https://github.com/niksacdev/loan-defenders/security/advisories)
- Tagged in releases with `[SECURITY]` prefix
- Announced in the repository README
- Documented in CHANGELOG.md

## Secure Azure Deployments with GitHub Actions

This repository uses GitHub Actions for Azure deployments with enterprise-grade security practices suitable for **public repositories**.

### OIDC Authentication (Passwordless)

✅ **No secrets stored** - Uses OpenID Connect federated identity
✅ **Short-lived tokens** - Tokens expire in minutes
✅ **Repository-scoped** - Only this repository can authenticate
✅ **Audit trail** - All authentication logged in Azure AD

**How it works:**
```
GitHub Actions → Requests token from GitHub OIDC provider
                ↓
Azure AD → Validates federated credential (repo-specific)
         ↓
Azure AD → Issues short-lived access token
         ↓
Deployment → Uses token for deployment (expires quickly)
```

### GitHub Secrets Safety in Public Repos

**Common Question**: "Won't people see my secrets in a public repo?"

**Answer**: **NO!** GitHub Secrets are:
- ✅ Encrypted with AES-256
- ✅ Never exposed in logs (automatically redacted)
- ✅ Not copied when repo is forked
- ✅ Only accessible to workflows in YOUR repository
- ✅ Require write access to modify

**Example**: If someone forks this repo:
- They get the workflow files ✅
- They DON'T get your secrets ❌
- They must configure their own Azure credentials

### Setting Up Secure Deployments

#### Automated Setup (Recommended)

Use the automated setup script:

```bash
cd infrastructure/scripts
./setup-github-actions.sh <your-github-username> <repository-name>

# Example:
./setup-github-actions.sh niksacdev loan-defenders
```

The script will:
1. Create Azure AD app registration
2. Create service principal with Contributor role
3. Configure federated credentials for GitHub OIDC
4. Display GitHub Secrets values to add
5. Save configuration to `github-actions-config.txt`

#### Manual Setup

If you prefer manual setup:

**Step 1: Create Azure AD App Registration**

```bash
az ad app create --display-name "loan-defenders-github-actions"
APP_ID=$(az ad app list --display-name "loan-defenders-github-actions" --query [0].appId -o tsv)
```

**Step 2: Create Service Principal**

```bash
az ad sp create --id $APP_ID
az role assignment create \
  --role Contributor \
  --assignee $APP_ID \
  --scope /subscriptions/$SUB_ID
```

**Step 3: Configure Federated Credentials**

**Critical**: Federated credentials are scoped to **your repository only**:

```bash
az ad app federated-credential create \
  --id $APP_ID \
  --parameters '{
    "name": "loan-defenders-main",
    "issuer": "https://token.actions.githubusercontent.com",
    "subject": "repo:YOUR_USERNAME/loan-defenders:ref:refs/heads/main",
    "audiences": ["api://AzureADTokenExchange"]
  }'
```

**Security**: The `subject` field ensures only workflows from `YOUR_USERNAME/loan-defenders` on the `main` branch can authenticate.

**Step 4: Add Secrets to GitHub**

Go to **Settings → Secrets and variables → Actions → New repository secret**:

| Secret Name | Value | Notes |
|-------------|-------|-------|
| `AZURE_CLIENT_ID` | Application (client) ID | Just an ID, not sensitive |
| `AZURE_TENANT_ID` | Directory (tenant) ID | Just an ID, not sensitive |
| `AZURE_SUBSCRIPTION_ID` | Subscription ID | Just an ID, not sensitive |

**Note**: These are **identifiers**, not passwords. Even if exposed, they can't authenticate without GitHub's OIDC token.

### Environment Protection

Configure protected environments in **Settings → Environments**:

#### Production Environment

1. Go to **Settings → Environments → New environment**
2. Name: `prod`
3. Add protection rules:
   - ✅ **Required reviewers**: Add yourself (manual approval required)
   - ✅ **Wait timer**: 5 minutes (prevents accidental deployments)
   - ✅ **Deployment branches**: Only `main` branch

#### Staging Environment (Optional)

1. Name: `staging`
2. Protection rules:
   - ✅ **Deployment branches**: Only `main` and `release/*` branches
   - Optional: Required reviewers

#### Development Environment

1. Name: `dev`
2. Protection rules:
   - ✅ **Deployment branches**: Any branch (for testing)
   - No approval required (faster iteration)

### Deployment Workflow Security

Our workflows use minimal permissions:

```yaml
permissions:
  id-token: write   # Only for OIDC authentication
  contents: read    # Read-only access to code
  # No other permissions granted
```

Workflows use `workflow_dispatch` (manual trigger):
- ✅ Prevents accidental deployments
- ✅ Requires user to explicitly start deployment
- ✅ Provides deployment parameters (environment, stage)

### Azure RBAC (Role-Based Access Control)

The Azure service principal has **Contributor** role scoped to subscription:
- ✅ Can deploy resources
- ✅ Can modify resources
- ❌ Cannot manage access control (no Owner role)
- ❌ Cannot modify Azure AD settings

**Least privilege principle applied.**

### Deployment Best Practices

#### ✅ DO

- Use OIDC authentication (no passwords)
- Enable environment protection for production
- Restrict deployment branches
- Review deployment logs
- Rotate credentials if compromised (delete federated credential, create new one)
- Use branch protection rules on main
- Require PR reviews before merging

#### ❌ DON'T

- Store Azure passwords/keys in secrets (use OIDC instead)
- Allow deployments from forks (disabled by default)
- Grant Owner role to service principal (use Contributor)
- Skip environment protection for production
- Commit secrets to code (use GitHub Secrets)

### Incident Response for Deployments

#### If Credentials Are Compromised

1. **Immediately revoke federated credential:**
   ```bash
   az ad app federated-credential delete \
     --id $APP_ID \
     --federated-credential-id <credential-id>
   ```

2. **Create new federated credential** with different name

3. **Review Azure AD sign-in logs** for unauthorized access:
   ```bash
   az monitor activity-log list \
     --caller $APP_ID \
     --start-time 2025-01-01T00:00:00Z
   ```

4. **Check resource group deployments** for unexpected changes:
   ```bash
   az deployment group list \
     --resource-group loan-defenders-prod-rg \
     --query "[?properties.timestamp>'2025-01-01']"
   ```

#### If GitHub Secrets Are Exposed

**Reminder**: GitHub Secrets are encrypted and not visible. But if you suspect compromise:

1. **Delete exposed secrets** in Settings → Secrets
2. **Rotate Azure credentials** (delete and recreate federated credential)
3. **Check GitHub audit log** for unauthorized access
4. **Enable two-factor authentication** if not already enabled

### Deployment Audit and Monitoring

#### GitHub Actions Logs

All deployments logged in **Actions** tab:
- Who triggered deployment
- What parameters were used
- When deployment ran
- Full deployment output (secrets redacted)

#### Azure Deployment History

Check deployment history:
```bash
az deployment group list \
  --resource-group loan-defenders-dev-rg \
  --output table
```

#### Azure AD Sign-In Logs

Monitor service principal authentication:
- Azure Portal → Azure Active Directory → Sign-in logs
- Filter by Application: "loan-defenders-github-actions"

### Deployment FAQ

- **Q: Can forked repos use my secrets?**
  - A: No. Secrets are not copied to forks.

- **Q: Can I see secret values after adding them?**
  - A: No. Secrets are write-only, encrypted at rest.

- **Q: What if someone with write access adds malicious workflow?**
  - A: Use branch protection + required reviews on main branch. Use CODEOWNERS for `.github/workflows/`.

- **Q: Is OIDC more secure than service principal secrets?**
  - A: Yes. No long-lived secrets, tokens expire quickly, repository-scoped.

## Resources

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [Azure Security Best Practices](https://learn.microsoft.com/en-us/azure/security/fundamentals/best-practices-and-patterns)
- [Microsoft Agent Framework Security](https://github.com/microsoft/agent-framework)
- [Python Security Best Practices](https://python.readthedocs.io/en/stable/library/security_warnings.html)
- [GitHub Actions Security Hardening](https://docs.github.com/en/actions/security-guides/security-hardening-for-github-actions)
- [Azure OIDC with GitHub Actions](https://learn.microsoft.com/en-us/azure/developer/github/connect-from-azure)
- [GitHub Secrets Documentation](https://docs.github.com/en/actions/security-guides/encrypted-secrets)
- [Azure RBAC Best Practices](https://learn.microsoft.com/en-us/azure/role-based-access-control/best-practices)

## Questions?

If you have questions about this security policy, please open a [GitHub Discussion](https://github.com/niksacdev/loan-defenders/discussions) in the Security category.

---

**Thank you for helping keep Loan Defenders and our users safe!**
