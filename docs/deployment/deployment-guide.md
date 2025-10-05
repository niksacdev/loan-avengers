# Deployment Guide - Azure Infrastructure

Step-by-step guide to deploy Loan Defenders infrastructure to Azure using Azure Verified Modules (AVM).

## 📋 Prerequisites

### 1. Azure Subscription
- Active Azure subscription
- Contributor or Owner permissions
- Subscription ID handy

### 2. Azure CLI Installed
```bash
# Check if installed
az --version

# If not installed:
# macOS: brew install azure-cli
# Windows: winget install Microsoft.AzureCLI
# Linux: curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash
```

### 3. jq Installed (for JSON processing)
```bash
# Check if installed
jq --version

# If not installed:
# macOS: brew install jq
# Windows: winget install jqlang.jq
# Linux: sudo apt-get install jq
```

**Note**: `jq` is required for REST API deployment approach (see ADR-022)

### 4. Login to Azure
```bash
# Interactive login
az login

# Login with specific tenant (if you have multiple)
az login --tenant YOUR_TENANT_ID

# Verify you're logged in
az account show
```

### 5. Set the Correct Subscription
```bash
# List all subscriptions
az account list --output table

# Set the subscription you want to use
az account set --subscription "YOUR_SUBSCRIPTION_NAME_OR_ID"

# Verify
az account show --query name -o tsv
```

---

## 🚀 Deployment Steps

### Step 1: Choose Your Environment

**Development** (for testing):
- Lower cost
- Smaller scale
- Use for learning/testing

**Production** (for real workloads):
- Higher cost
- Larger scale
- Enterprise-grade

```bash
# Set environment variable
export ENV=dev  # or 'prod'
export RG_NAME="loan-defenders-${ENV}-rg"
export LOCATION="eastus"  # or your preferred region
```

### Step 2: Navigate to Infrastructure Directory

```bash
cd infrastructure/bicep

# Verify you're in the right place
ls -la
# Should see: main-avm.bicep, deploy.sh, environments/, modules/
```

### Step 3: Review Parameters (Optional)

```bash
# View default parameters for your environment
cat environments/${ENV}.parameters.json

# Edit if needed (optional)
code environments/${ENV}.parameters.json  # or vi/nano
```

**Default parameters are fine for first deployment!**

### Step 4: Deploy Infrastructure

Choose your deployment method:

=== "All Stages (Recommended)"
    Deploy everything in one command:
    ```bash
    ./deploy.sh ${ENV} ${RG_NAME}
    # or explicitly:
    ./deploy.sh ${ENV} ${RG_NAME} --stage all
    ```

=== "Staged Deployment"
    Deploy in stages for more control:
    ```bash
    # Stage 1: Networking (VNet, NSGs, Subnets)
    ./deploy.sh ${ENV} ${RG_NAME} --stage foundation

    # Stage 2: Security (Key Vault, Storage, Identity)
    ./deploy.sh ${ENV} ${RG_NAME} --stage security

    # Stage 3: AI Services (AI, Log Analytics, App Insights)
    ./deploy.sh ${ENV} ${RG_NAME} --stage ai

    # Stage 4: Container Apps (Environment)
    ./deploy.sh ${ENV} ${RG_NAME} --stage apps
    ```

**What happens:**
- Script checks Azure CLI login ✅
- Creates resource group if it doesn't exist ✅
- Compiles Bicep to ARM JSON ✅
- Deploys resources using Azure Verified Modules ✅
- Takes ~10-15 minutes (all stages) ⏱️

**Expected output:**
```
[INFO] Validating inputs...
[SUCCESS] Validation passed
[INFO] Checking Azure CLI login status...
[SUCCESS] Azure CLI logged in
[INFO] Current subscription: Your Subscription Name (12345678-1234...)
[INFO] Checking resource group: loan-defenders-dev-rg
[WARNING] Resource group does not exist. Creating...
[SUCCESS] Resource group created: loan-defenders-dev-rg
[INFO] Validating Bicep template...
[SUCCESS] Template validation passed
[INFO] Starting deployment to: loan-defenders-dev-rg
[INFO] Deploying infrastructure... (this may take 5-10 minutes)

Name                     State
-----------------------  -----------
vnet-deployment          Succeeded
private-dns-deployment   Succeeded

[SUCCESS] Deployment completed successfully!
```

### Step 5: Verify Deployment

```bash
# Check resources created
az resource list --resource-group ${RG_NAME} --output table

# Expected resources:
# - VNet: loan-defenders-dev-vnet
# - NSGs: 3 (container-apps, apim, private-endpoints)
# - Private DNS Zones: 5
```

---

## 🎯 What You've Deployed

After deployment completes, you have:

### Foundation Stage
✅ **VNet** with 3 subnets:
- Container Apps: 10.0.1.0/23 (delegated to Microsoft.App/environments)
- APIM: 10.0.3.0/24
- Private Endpoints: 10.0.4.0/24

✅ **Network Security Groups** (3):
- Container Apps NSG (platform communication rules)
- APIM NSG (HTTP/HTTPS, health probe rules)
- Private Endpoints NSG (minimal rules)

### Security Stage
✅ **Managed Identity** (User-Assigned):
- For application authentication
- RBAC roles pre-configured

✅ **Key Vault**:
- RBAC-enabled (no access policies)
- Soft delete + purge protection
- Private network access only

✅ **Storage Account**:
- StorageV2, Hot tier
- Private network access only
- TLS 1.2+ enforced

### AI Stage
✅ **AI Services** (Cognitive Services):
- Multi-service account (GPT-4, embeddings, etc.)
- Private network access only
- Custom subdomain configured

✅ **Log Analytics Workspace**:
- 30-day retention
- PerGB2018 pricing tier

✅ **Application Insights**:
- Workspace-based
- Connected to Log Analytics

✅ **RBAC Permissions**:
- Managed Identity → AI Services (Cognitive Services User)
- Managed Identity → Key Vault (Secrets User)
- Managed Identity → Storage (Blob Data Contributor)

### Apps Stage
✅ **Container Apps Environment**:
- VNet-integrated (internal)
- Connected to Log Analytics
- Ready for container apps

---

## 💰 Cost Estimate

**Foundation Stage: ~$0/month**
- VNet: Free
- NSGs: Free

**Security Stage: ~$5-10/month**
- Key Vault: ~$0.03/10k operations
- Storage Account: ~$5/month (100GB)
- Managed Identity: Free

**AI Stage: ~$0 (pay-per-use)**
- AI Services: Pay per API call (no base cost)
- Log Analytics: ~$2.30/GB ingested
- Application Insights: Free tier (first 5GB/month)

**Apps Stage: ~$20-30/month**
- Container Apps Environment: ~$0
- Container Apps: ~$20-30/month (consumption-based)

**Total Estimated: ~$25-40/month** (dev environment)

---

## 📊 View in Azure Portal

```bash
# Open resource group in browser
az group show --name ${RG_NAME} --query 'id' -o tsv | \
  xargs -I {} echo "https://portal.azure.com/#@/resource{}/overview"

# Or manually:
# https://portal.azure.com
# → Resource Groups → loan-defenders-dev-rg
```

---

## 🔄 Next Steps

After infrastructure deployment succeeds:

### 1. Deploy Container Apps
Build and deploy your applications to Container Apps:

- **API App** (FastAPI backend) - See [Container Apps Guide](../deployment/cicd.md)
- **UI App** (React frontend)
- **MCP Servers** (3 microservices)

### 2. Add New Services (Future)
To add additional Azure services (e.g., AI Search, Cosmos DB):

1. Create new Bicep module: `infrastructure/bicep/modules/service-name.bicep`
2. Add module reference in `main-avm.bicep`
3. Redeploy: `./deploy.sh dev loan-defenders-dev-rg --stage <stage>`

See [ADR-021](../architecture/decisions/adr-021-azure-verified-modules-adoption.md) for details.

### 3. API Management (Optional)
Deploy APIM for advanced API features:
- Rate limiting and throttling
- JWT validation
- API versioning
- See Issue #95

---

## 🧹 Clean Up (Delete Everything)

**Warning**: This deletes ALL resources in the resource group!

```bash
# Delete resource group (removes all resources)
az group delete --name ${RG_NAME} --yes --no-wait

# Verify deletion
az group exists --name ${RG_NAME}
# Should return: false
```

---

## 🔧 Technical Details

### Deployment Method: Azure REST API

The deployment script uses Azure REST API directly instead of `az deployment group create` to avoid a known Azure CLI bug that causes "content already consumed" errors.

**Why REST API?**
- ✅ Bypasses Azure CLI bug (Azure/azure-cli#32149)
- ✅ Better error messages from Azure Resource Manager
- ✅ More reliable in CI/CD pipelines
- ✅ Direct control over HTTP requests/responses

**Technical Implementation:**
```bash
# 1. Compile Bicep to ARM JSON
az bicep build --file main-avm.bicep --outfile /tmp/deployment.json

# 2. Deploy via REST API
az rest --method PUT \
  --uri "https://management.azure.com/subscriptions/$SUB_ID/resourcegroups/$RG/providers/Microsoft.Resources/deployments/$NAME?api-version=2021-04-01" \
  --body "$DEPLOYMENT_BODY" \
  --headers "Content-Type=application/json"

# 3. Poll for completion
az rest --method GET \
  --uri "https://management.azure.com/subscriptions/$SUB_ID/resourcegroups/$RG/providers/Microsoft.Resources/deployments/$NAME?api-version=2021-04-01"
```

**For more details**, see [ADR-022: Azure REST API for Bicep Deployments](../architecture/decisions/adr-022-azure-rest-api-deployment.md)

---

## 🐛 Troubleshooting

### Issue: "az: command not found"
```bash
# Azure CLI not installed
# Install: https://learn.microsoft.com/en-us/cli/azure/install-azure-cli
```

### Issue: "jq: command not found"
```bash
# jq not installed (required for REST API JSON processing)
# macOS: brew install jq
# Windows: winget install jqlang.jq
# Linux: sudo apt-get install jq
```

### Issue: "ERROR: Please run 'az login' to setup account"
```bash
az login
az account set --subscription "YOUR_SUBSCRIPTION_NAME"
```

### Issue: "Deployment validation failed"
```bash
# Check Bicep syntax
az bicep build --file main-avm.bicep

# View detailed errors
az deployment group validate \
  --resource-group ${RG_NAME} \
  --template-file main.bicep \
  --parameters @environments/${ENV}.parameters.json
```

### Issue: "Insufficient permissions"
```bash
# You need Contributor or Owner role
# Ask your Azure admin to grant permissions
az role assignment list --assignee YOUR_EMAIL --output table
```

### Issue: "Subscription not found"
```bash
# List available subscriptions
az account list --output table

# Set correct subscription
az account set --subscription "SUBSCRIPTION_NAME_OR_ID"
```

---

## 📖 Additional Resources

- **Azure Verified Modules**: https://azure.github.io/Azure-Verified-Modules/
- **Azure Bicep Docs**: https://learn.microsoft.com/en-us/azure/azure-resource-manager/bicep/
- **Azure CLI Docs**: https://learn.microsoft.com/en-us/cli/azure/
- **Cost Calculator**: https://azure.microsoft.com/en-us/pricing/calculator/
- **Architecture Decisions**:
  - [ADR-021: Azure Verified Modules Adoption](../architecture/decisions/adr-021-azure-verified-modules-adoption.md)
  - [ADR-016: GitHub Actions Security](../architecture/decisions/adr-016-github-actions-security.md)

---

## ✅ Success Criteria

You've successfully deployed when:

- ✅ Deploy script completes without errors
- ✅ Resource group exists in Azure Portal
- ✅ All stages deployed (foundation, security, ai, apps)
- ✅ VNet shows 3 subnets with NSGs
- ✅ Key Vault, Storage Account, and Managed Identity created
- ✅ AI Services, Log Analytics, and App Insights configured
- ✅ Container Apps Environment ready
- ✅ RBAC permissions assigned

**Verification commands**:
```bash
# Check all resources
az resource list --resource-group ${RG_NAME} --output table

# Verify RBAC assignments
az role assignment list --resource-group ${RG_NAME} --output table
```

**Next**: Build and deploy container apps to the environment!
