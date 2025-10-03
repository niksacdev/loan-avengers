# Quick Start - Deploy in 5 Minutes

**TL;DR**: Deploy VNet infrastructure to Azure subscription.

## Prerequisites (One-Time Setup)

```bash
# 1. Install Azure CLI (if not installed)
az --version || curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash

# 2. Login to Azure
az login

# 3. Set subscription
az account set --subscription "YOUR_SUBSCRIPTION_NAME"

# 4. Verify
az account show
```

## Deploy (3 Commands)

```bash
# 1. Navigate to infrastructure
cd infrastructure/bicep

# 2. Set environment
export ENV=dev  # or 'prod'
export RG_NAME="loan-defenders-${ENV}-rg"

# 3. Deploy!
./deploy.sh ${ENV} ${RG_NAME}
```

**Done!** ✅ Takes ~5-10 minutes.

## What Gets Deployed

- ✅ VNet (10.0.0.0/16)
- ✅ 3 Subnets (Container Apps, APIM, Private Endpoints)
- ✅ 3 NSGs (security rules)
- ✅ 5 Private DNS Zones
- 💰 Cost: **$0/month** (no private endpoints yet)

## Verify

```bash
# View resources in Azure Portal
az resource list --resource-group ${RG_NAME} --output table
```

## Next Steps

1. Deploy Azure services (Issue #57)
2. Deploy Container Apps (Issue #58)
3. Add private endpoints (Phase 2)

## Clean Up (Delete Everything)

```bash
az group delete --name ${RG_NAME} --yes
```

---

**Need help?** See [DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md) for detailed instructions.
