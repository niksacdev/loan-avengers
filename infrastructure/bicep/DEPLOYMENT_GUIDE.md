# Deployment Guide - Manual Azure Deployment

Step-by-step guide to deploy Loan Defenders infrastructure to your Azure subscription.

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

### 3. Login to Azure
```bash
# Interactive login
az login

# Login with specific tenant (if you have multiple)
az login --tenant YOUR_TENANT_ID

# Verify you're logged in
az account show
```

### 4. Set the Correct Subscription
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
# Should see: main.bicep, deploy.sh, environments/, modules/
```

### Step 3: Review Parameters (Optional)

```bash
# View default parameters for your environment
cat environments/${ENV}.parameters.json

# Edit if needed (optional)
code environments/${ENV}.parameters.json  # or vi/nano
```

**Default parameters are fine for first deployment!**

### Step 4: Deploy Infrastructure (Phase 1)

```bash
# Make deploy script executable (if not already)
chmod +x deploy.sh

# Run deployment
./deploy.sh ${ENV} ${RG_NAME}

# Example:
# ./deploy.sh dev loan-defenders-dev-rg
```

**What happens:**
- Script checks Azure CLI login ✅
- Creates resource group if it doesn't exist ✅
- Validates Bicep template ✅
- Deploys VNet, NSGs, DNS zones ✅
- Takes ~5-10 minutes ⏱️

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

After Step 4 completes, you have:

✅ **VNet** with 3 subnets:
- Container Apps: 10.0.1.0/23
- APIM: 10.0.3.0/24
- Private Endpoints: 10.0.4.0/24

✅ **Network Security Groups** (3):
- Least privilege rules
- Ready for services

✅ **Private DNS Zones** (5):
- VNet links configured
- Ready for private endpoints

❌ **Private Endpoints**: Not yet (services don't exist)

---

## 💰 Cost Check

```bash
# View estimated costs in Azure Portal
az portal show --resource-group ${RG_NAME}

# Or use Azure Cost Management
az consumption usage list --start-date 2025-01-01 --end-date 2025-01-31
```

**Current cost: ~$0/month**
- VNet: Free
- NSGs: Free
- DNS Zones: Free (first 25)

**After adding private endpoints: ~$30-38/month**

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

## 🔄 Next Steps (Phase 2 - Coming Soon)

After Phase 1 deployment succeeds, you'll deploy:

### Issue #57 - Security & Azure Services
1. **Azure Key Vault** (for secrets)
2. **Storage Account** (for documents)
3. **Azure AI Services** (for Content Safety)
4. **Application Insights** (for monitoring)
5. **Azure AI Foundry Projects** (for GPT-4 and agent AI models)

### Issue #58 - Container Apps
1. **Container Apps Environment** (in VNet)
2. **API App** (FastAPI backend)
3. **UI App** (React frontend)
4. **MCP Servers** (3 apps)

### Issue #95 - API Management
1. **APIM Standard v2** (in VNet)
2. **Rate limiting policies**
3. **JWT validation**

### Phase 2: Add Private Endpoints

After deploying Azure services:

```bash
# 1. Get resource IDs
KEYVAULT_ID=$(az keyvault show --name loan-defenders-kv --query id -o tsv)
STORAGE_ID=$(az storage account show --name loandefenderssa --query id -o tsv)
AI_ID=$(az cognitiveservices account show --name loan-defenders-ai --query id -o tsv)

# 2. Update parameters file
cat > environments/${ENV}.parameters.json <<EOF
{
  "deployPrivateEndpoints": { "value": true },
  "keyVaultId": { "value": "${KEYVAULT_ID}" },
  "storageAccountId": { "value": "${STORAGE_ID}" },
  "aiServicesId": { "value": "${AI_ID}" }
}
EOF

# 3. Re-deploy (adds private endpoints)
./deploy.sh ${ENV} ${RG_NAME}
```

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

## 🐛 Troubleshooting

### Issue: "az: command not found"
```bash
# Azure CLI not installed
# Install: https://learn.microsoft.com/en-us/cli/azure/install-azure-cli
```

### Issue: "ERROR: Please run 'az login' to setup account"
```bash
az login
az account set --subscription "YOUR_SUBSCRIPTION_NAME"
```

### Issue: "Deployment validation failed"
```bash
# Check Bicep syntax
az bicep build --file main.bicep

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

- **Azure Bicep Docs**: https://learn.microsoft.com/en-us/azure/azure-resource-manager/bicep/
- **Azure CLI Docs**: https://learn.microsoft.com/en-us/cli/azure/
- **Cost Calculator**: https://azure.microsoft.com/en-us/pricing/calculator/
- **GitHub Issues**:
  - [#94 - VNet Infrastructure](https://github.com/niksacdev/loan-defenders/issues/94) (current)
  - [#57 - Security](https://github.com/niksacdev/loan-defenders/issues/57) (next)
  - [#58 - Container Apps](https://github.com/niksacdev/loan-defenders/issues/58) (next)

---

## ✅ Success Criteria

You've successfully deployed when:

- ✅ Deploy script completes without errors
- ✅ Resource group exists in Azure Portal
- ✅ VNet shows 3 subnets
- ✅ 3 NSGs are created
- ✅ 5 Private DNS Zones exist
- ✅ Cost shows ~$0/month (no private endpoints yet)

**Next**: Proceed to Issue #57 or #58 to deploy services!
