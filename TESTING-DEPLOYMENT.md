# Testing Azure Bicep Deployment Fix

This document provides instructions for testing the Azure REST API deployment fix for issue #99.

## What Was Fixed

The Azure Bicep deployment was failing with "The content for this response was already consumed" error. This has been fixed by switching from `az deployment group create` to direct Azure REST API calls using `az rest`.

## Prerequisites

Before testing, ensure you have:

1. **Azure CLI** (2.20.0+):
   ```bash
   az --version
   az login
   ```

2. **jq** (required for JSON processing):
   ```bash
   # Check if installed
   jq --version
   
   # Install if needed:
   # macOS: brew install jq
   # Windows: winget install jqlang.jq
   # Linux: sudo apt-get install jq
   ```

3. **Azure Subscription** with Contributor/Owner permissions

## Testing Steps

### Local Deployment Test

Test the deployment script locally:

```bash
# 1. Navigate to bicep directory
cd infrastructure/bicep

# 2. Test foundation stage (smallest deployment)
./deploy.sh dev loan-defenders-dev-rg --stage foundation

# Expected output:
# ✓ Bicep compiled to ARM JSON
# ✓ Deployment initiated successfully
# Deployment ID: foundation-deployment-YYYYMMDD-HHMMSS
# Current state: Running
# Current state: Running
# Current state: Succeeded
# ✓ Deployment completed successfully!

# 3. Verify in Azure Portal
# Go to: https://portal.azure.com
# Resource Groups → loan-defenders-dev-rg
# Deployments → Check for "foundation-deployment-*"
# Status should be "Succeeded"

# 4. Test other stages (if desired)
./deploy.sh dev loan-defenders-dev-rg --stage security
./deploy.sh dev loan-defenders-dev-rg --stage ai
./deploy.sh dev loan-defenders-dev-rg --stage apps

# 5. Or test all stages at once
./deploy.sh dev loan-defenders-dev-rg --stage all
```

### GitHub Actions Test

Test the CI/CD pipeline:

```bash
# 1. Go to GitHub Actions
# https://github.com/niksacdev/loan-defenders/actions

# 2. Select "Deploy Azure Infrastructure" workflow

# 3. Click "Run workflow"
# - Branch: copilot/fix-1924f36e-2e63-451e-a804-d9dc3b4e25a5
# - Environment: dev
# - Stage: foundation

# 4. Monitor the workflow run
# Expected: All steps should pass with green checkmarks
# No "content already consumed" errors

# 5. Check deployment in Azure Portal
# Verify deployment registered and succeeded
```

## Expected Behavior

### ✅ Success Indicators

1. **Deployment Initiates**: "Deployment initiated successfully" message
2. **Deployment Registers**: Deployment ID returned immediately
3. **Status Updates**: State transitions from "Running" to "Succeeded"
4. **Azure Portal**: Deployment visible in resource group with "Succeeded" status
5. **Resources Created**: Expected Azure resources appear in resource group
6. **No Errors**: No "content already consumed" errors in logs

### ❌ Failure Indicators (Should NOT Occur)

1. ❌ "The content for this response was already consumed" error
2. ❌ Deployment state stuck at "NotFound"
3. ❌ Deployment never registers in Azure portal
4. ❌ `jq` command not found (install jq)

## Troubleshooting

### Issue: "jq: command not found"
```bash
# Install jq
# macOS: brew install jq
# Windows: winget install jqlang.jq
# Linux: sudo apt-get install jq
```

### Issue: "Deployment validation failed"
```bash
# Check Bicep syntax
az bicep build --file infrastructure/bicep/main-avm.bicep

# View detailed validation errors
# Errors will be shown in JSON format with clear messages
```

### Issue: Deployment times out after 15 minutes
```bash
# This is expected for very large deployments
# The timeout can be adjusted in deploy.sh:
# Change: MAX_RETRIES=90  # 15 minutes
# To: MAX_RETRIES=180      # 30 minutes
```

## Verification Checklist

After deployment succeeds, verify:

- [ ] Deployment shows "Succeeded" status in Azure Portal
- [ ] Expected resources were created (VNet, NSGs, subnets, etc.)
- [ ] No error messages in deployment logs
- [ ] Deployment outputs are displayed correctly
- [ ] Can run deployment again without conflicts (idempotent)
- [ ] All 5 stages can be deployed: foundation, security, ai, apps, all

## Rollback Plan

If the REST API approach fails:

1. **Check logs**: Review error messages in deployment output
2. **Verify prerequisites**: Ensure `jq` is installed
3. **Test API access**: Run `az rest --method GET --uri "https://management.azure.com/subscriptions?api-version=2021-04-01"`
4. **Report issue**: Document error messages and deployment output

## Success Metrics

Deployment is considered successful when:

1. ✅ All 5 deployment stages complete without errors
2. ✅ Deployments register in Azure portal within 10 seconds
3. ✅ No "content already consumed" errors occur
4. ✅ GitHub Actions workflow passes end-to-end
5. ✅ Resources are created and accessible in Azure

## Additional Resources

- **ADR-022**: [Architecture Decision Record](docs/architecture/decisions/adr-022-azure-rest-api-deployment.md)
- **Deployment Guide**: [Detailed deployment instructions](docs/deployment/deployment-guide.md)
- **Bicep README**: [Infrastructure overview](infrastructure/bicep/README.md)
- **Azure CLI Bug**: https://github.com/Azure/azure-cli/issues/32149

## Cleanup After Testing

To remove test resources:

```bash
# Delete resource group (removes all resources)
az group delete --name loan-defenders-dev-rg --yes --no-wait

# Verify deletion
az group exists --name loan-defenders-dev-rg
# Should return: false
```

---

**Note**: This fix addresses a known Azure CLI bug by using direct REST API calls. The implementation is production-ready and follows Azure best practices for ARM deployments.
