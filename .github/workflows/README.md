# GitHub Actions Workflows

## Infrastructure Deployment

### Prerequisites

Set up Azure authentication using **OpenID Connect (OIDC)** - the secure, passwordless method.

#### 1. Create Azure AD App Registration

```bash
# Login to Azure
az login

# Create app registration
az ad app create --display-name "loan-defenders-github-actions"

# Get the Application (client) ID
APP_ID=$(az ad app list --display-name "loan-defenders-github-actions" --query [0].appId -o tsv)
echo "AZURE_CLIENT_ID: $APP_ID"

# Get Tenant ID
TENANT_ID=$(az account show --query tenantId -o tsv)
echo "AZURE_TENANT_ID: $TENANT_ID"

# Get Subscription ID
SUB_ID=$(az account show --query id -o tsv)
echo "AZURE_SUBSCRIPTION_ID: $SUB_ID"
```

#### 2. Create Service Principal

```bash
# Create service principal
az ad sp create --id $APP_ID

# Get the service principal object ID
SP_OBJECT_ID=$(az ad sp list --display-name "loan-defenders-github-actions" --query [0].id -o tsv)

# Grant Contributor role on subscription
az role assignment create \
  --role Contributor \
  --assignee $APP_ID \
  --scope /subscriptions/$SUB_ID
```

#### 3. Configure Federated Credentials for GitHub

```bash
# For main branch deployments
az ad app federated-credential create \
  --id $APP_ID \
  --parameters '{
    "name": "loan-defenders-main",
    "issuer": "https://token.actions.githubusercontent.com",
    "subject": "repo:niksacdev/loan-defenders:ref:refs/heads/main",
    "audiences": ["api://AzureADTokenExchange"]
  }'

# For pull request deployments (optional)
az ad app federated-credential create \
  --id $APP_ID \
  --parameters '{
    "name": "loan-defenders-pr",
    "issuer": "https://token.actions.githubusercontent.com",
    "subject": "repo:niksacdev/loan-defenders:pull_request",
    "audiences": ["api://AzureADTokenExchange"]
  }'
```

#### 4. Add Secrets to GitHub

Go to **Settings → Secrets and variables → Actions** and add:

- `AZURE_CLIENT_ID`: (the $APP_ID from step 1)
- `AZURE_TENANT_ID`: (the $TENANT_ID from step 1)
- `AZURE_SUBSCRIPTION_ID`: (the $SUB_ID from step 1)

**Note**: No client secret needed - OIDC uses federated identity!

### Running Deployments

#### Via GitHub Actions UI

1. Go to **Actions** tab
2. Select **Deploy Azure Infrastructure**
3. Click **Run workflow**
4. Choose:
   - **Environment**: `dev`, `staging`, or `prod`
   - **Stage**: `foundation`, `security`, `ai`, `apps`, or `all`
5. Click **Run workflow**

#### Deployment Order

**First deployment** (fresh environment):
```
1. Stage: foundation → Creates VNet, NSGs, DNS zones
2. Stage: security   → Creates Key Vault, Storage, Identity
3. Stage: ai         → Creates AI Services, AI Foundry, Monitoring
4. Stage: apps       → Creates Container Apps
```

**Or deploy everything at once**:
```
Stage: all → Deploys all stages sequentially
```

## Security Features

✅ **OIDC Authentication** - No secrets/passwords stored
✅ **Environment Protection** - Requires approval for production
✅ **Audit Trail** - All deployments logged in GitHub
✅ **Least Privilege** - Service principal has only Contributor role
✅ **Short-lived Tokens** - OIDC tokens expire automatically

## Troubleshooting

### Error: "AADSTS700016: Application not found"

The app registration doesn't exist. Re-run step 1.

### Error: "Insufficient privileges"

The service principal needs Contributor role. Re-run step 2.

### Error: "Federated credential subject does not match"

Check the repository name in federated credential matches exactly.

### Deployment Fails with Template Errors

Check deployment details in Azure Portal:
```bash
az deployment group show \
  --name <deployment-name> \
  --resource-group loan-defenders-dev-rg \
  --query properties.error
```

## Cost Estimation

| Stage | Resources | Monthly Cost |
|-------|-----------|--------------|
| foundation | VNet, NSGs, DNS | $0 |
| security | Key Vault, Storage | ~$10 |
| ai | AI Services, AI Foundry | ~$50 |
| apps | Container Apps (5) | ~$50 |
| **Total** | Complete infrastructure | **~$110/month** |

## Next Steps

After successful deployment:

1. **Verify resources** in Azure Portal
2. **Build container images** (Issue #58)
3. **Deploy APIM** (Issue #95)
4. **Set up monitoring** dashboards
