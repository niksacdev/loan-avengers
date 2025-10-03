# Security Guide for GitHub Actions Deployments

## Overview

This repository uses GitHub Actions for Azure deployments with enterprise-grade security practices suitable for **public repositories**.

## Security Features

### 1. OIDC Authentication (Passwordless)

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

### 2. Environment Protection

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

### 3. Secrets Safety in Public Repos

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

### 4. Workflow Permissions (Least Privilege)

Our workflows use minimal permissions:

```yaml
permissions:
  id-token: write   # Only for OIDC authentication
  contents: read    # Read-only access to code
  # No other permissions granted
```

### 5. Manual Triggers Only

Workflows use `workflow_dispatch` (manual trigger):
- ✅ Prevents accidental deployments
- ✅ Requires user to explicitly start deployment
- ✅ Provides deployment parameters (environment, stage)

### 6. Azure RBAC (Role-Based Access Control)

The Azure service principal has **Contributor** role scoped to subscription:
- ✅ Can deploy resources
- ✅ Can modify resources
- ❌ Cannot manage access control (no Owner role)
- ❌ Cannot modify Azure AD settings

**Least privilege principle applied.**

## Setting Up Secure Deployments

### Step 1: Create Azure AD App Registration

```bash
az ad app create --display-name "loan-defenders-github-actions"
```

### Step 2: Configure Federated Credentials

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

### Step 3: Add Secrets to GitHub

**Settings → Secrets and variables → Actions → New repository secret**:

| Secret Name | Value | Notes |
|-------------|-------|-------|
| `AZURE_CLIENT_ID` | Application (client) ID | Just an ID, not sensitive |
| `AZURE_TENANT_ID` | Directory (tenant) ID | Just an ID, not sensitive |
| `AZURE_SUBSCRIPTION_ID` | Subscription ID | Just an ID, not sensitive |

**Note**: These are **identifiers**, not passwords. Even if exposed, they can't authenticate without GitHub's OIDC token.

### Step 4: Configure Environment Protection

**For production deployments**:

1. **Settings → Environments → New environment**
2. Name: `prod`
3. **Environment protection rules**:
   - ✅ Required reviewers: Add your GitHub username
   - ✅ Wait timer: 5 minutes
   - ✅ Deployment branches: Only `main`

**Result**: Production deployments require manual approval.

## Security Best Practices

### ✅ DO

- Use OIDC authentication (no passwords)
- Enable environment protection for production
- Restrict deployment branches
- Review deployment logs
- Rotate credentials if compromised (delete federated credential, create new one)
- Use branch protection rules on main
- Require PR reviews before merging

### ❌ DON'T

- Store Azure passwords/keys in secrets (use OIDC instead)
- Allow deployments from forks (disabled by default)
- Grant Owner role to service principal (use Contributor)
- Skip environment protection for production
- Commit secrets to code (use GitHub Secrets)

## Incident Response

### If Credentials Are Compromised

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

### If GitHub Secrets Are Exposed

**Reminder**: GitHub Secrets are encrypted and not visible. But if you suspect compromise:

1. **Delete exposed secrets** in Settings → Secrets
2. **Rotate Azure credentials** (delete and recreate federated credential)
3. **Check GitHub audit log** for unauthorized access
4. **Enable two-factor authentication** if not already enabled

## Audit and Monitoring

### GitHub Actions Logs

All deployments logged in **Actions** tab:
- Who triggered deployment
- What parameters were used
- When deployment ran
- Full deployment output (secrets redacted)

### Azure Deployment History

Check deployment history:
```bash
az deployment group list \
  --resource-group loan-defenders-dev-rg \
  --output table
```

### Azure AD Sign-In Logs

Monitor service principal authentication:
- Azure Portal → Azure Active Directory → Sign-in logs
- Filter by Application: "loan-defenders-github-actions"

## Additional Security Resources

- [GitHub Actions Security Hardening](https://docs.github.com/en/actions/security-guides/security-hardening-for-github-actions)
- [Azure OIDC with GitHub Actions](https://learn.microsoft.com/en-us/azure/developer/github/connect-from-azure)
- [GitHub Secrets Documentation](https://docs.github.com/en/actions/security-guides/encrypted-secrets)
- [Azure RBAC Best Practices](https://learn.microsoft.com/en-us/azure/role-based-access-control/best-practices)

## Questions?

- **Q: Can forked repos use my secrets?**
  - A: No. Secrets are not copied to forks.

- **Q: Can I see secret values after adding them?**
  - A: No. Secrets are write-only, encrypted at rest.

- **Q: What if someone with write access adds malicious workflow?**
  - A: Use branch protection + required reviews on main branch. Use CODEOWNERS for `.github/workflows/`.

- **Q: Is OIDC more secure than service principal secrets?**
  - A: Yes. No long-lived secrets, tokens expire quickly, repository-scoped.
