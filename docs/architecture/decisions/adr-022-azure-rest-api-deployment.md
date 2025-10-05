# ADR-022: Azure REST API for Bicep Deployments

## Status
Accepted

## Context
Azure Bicep deployments via `az deployment group create` were failing with "The content for this response was already consumed" error across all deployment stages (foundation, security, ai, apps). This error is a known Azure CLI bug (Azure/azure-cli#32149) that occurs in the CLI's internal HTTP response handling, not in the Bicep templates themselves.

### Problem Impact
- **Blocked all infrastructure deployments**: CI/CD pipeline completely non-functional
- **Blocked OIDC authentication testing**: Could not validate GitHub Actions → Azure authentication
- **Blocked feature work**: Issues #95 (APIM), #96 (AI Content Safety), #98 (NSG rules) all dependent on infrastructure
- **Poor developer experience**: Deployment never registered in Azure portal, showing "NotFound" state indefinitely

### Investigation Results
Attempted solutions that did NOT fix the issue:
1. ✅ Fixed BCP318 warnings with null-forgiving operator (!)
2. ✅ Compiled Bicep to ARM JSON (CI/CD best practice)
3. ❌ Downgraded Azure CLI to 2.72.0 - error persisted
4. ❌ Used `--no-wait` flag - error occurred before async deployment
5. ❌ Added debug output - no additional information
6. ✅ Verified OIDC authentication - auth succeeded, resource group created

**Key observation**: Bicep compilation succeeded with zero warnings. Error occurred in Azure CLI command execution, not template validation.

## Decision
**Replace `az deployment group create` with direct Azure REST API calls using `az rest` command.**

### Deployment Pattern
```bash
# Construct deployment request body
DEPLOYMENT_BODY=$(jq -n \
  --argjson template "$TEMPLATE_CONTENT" \
  --argjson parameters "$MERGED_PARAMS" \
  '{
    properties: {
      template: $template,
      parameters: $parameters,
      mode: "Incremental"
    }
  }')

# Deploy via REST API (bypasses CLI bug)
az rest --method PUT \
  --uri "https://management.azure.com/subscriptions/$SUB_ID/resourcegroups/$RG/providers/Microsoft.Resources/deployments/$NAME?api-version=2021-04-01" \
  --body "$DEPLOYMENT_BODY" \
  --headers "Content-Type=application/json"

# Poll for completion via REST API
az rest --method GET \
  --uri "https://management.azure.com/subscriptions/$SUB_ID/resourcegroups/$RG/providers/Microsoft.Resources/deployments/$NAME?api-version=2021-04-01"
```

## Rationale

### Why REST API Over Azure CLI
1. **Bypasses CLI bug completely**: Direct HTTP calls avoid CLI's response stream handling issue
2. **Better control**: Full control over HTTP request/response lifecycle
3. **Clearer errors**: JSON error responses directly from Azure Resource Manager
4. **CI/CD standard**: More explicit, testable, and debuggable in automation
5. **Provider agnostic**: Works identically across GitHub Actions, Azure DevOps, GitLab CI, etc.

### Why Not Other Solutions
- **Deploy .bicep directly**: Against CI/CD best practice (should compile in CI)
- **Test with `deploymentStage: all`**: Defeats purpose of staged deployment architecture
- **Retry with backoff**: Doesn't address root cause, increases deployment time
- **Service principal instead of OIDC**: Defeats purpose of OIDC migration

### Azure Resource Manager API
Using ARM REST API is an official, supported approach:
- **API Version**: 2021-04-01 (stable, widely used)
- **Documentation**: https://learn.microsoft.com/en-us/rest/api/resources/deployments
- **Method**: Standard Azure Resource Manager deployment pattern
- **Authentication**: Uses existing Azure CLI authentication (OIDC or service principal)

## Implementation

### Files Changed
1. **infrastructure/bicep/deploy.sh**: Local deployment script
   - Replaced `az deployment group create` with REST API calls
   - Added parameter merging using `jq`
   - Improved polling with proper state checking
   - Better error handling with JSON output

2. **.github/workflows/deploy-infrastructure.yml**: CI/CD workflow
   - Consistent REST API approach with local script
   - Added subscription ID resolution
   - Improved output/error handling
   - 15-minute timeout with 10-second polling interval

### Key Changes
```bash
# OLD (fails with "content consumed" error)
az deployment group create \
    --name "$DEPLOYMENT_NAME" \
    --resource-group "$RESOURCE_GROUP" \
    --template-file "$COMPILED_TEMPLATE" \
    --parameters "@$PARAMETERS_FILE" \
    --parameters deploymentStage="$DEPLOYMENT_STAGE"

# NEW (uses REST API)
az rest --method PUT \
  --uri "https://management.azure.com/.../deployments/$DEPLOYMENT_NAME?api-version=2021-04-01" \
  --body "$DEPLOYMENT_BODY"
```

## Consequences

### Positive
1. ✅ **Deployments work**: All 5 stages (foundation, security, ai, apps, all) can deploy successfully
2. ✅ **Better error messages**: JSON error responses from Azure Resource Manager are clearer than CLI errors
3. ✅ **Deployment visibility**: Deployments register immediately in Azure portal with valid deployment ID
4. ✅ **CI/CD unblocked**: GitHub Actions workflow can proceed, OIDC authentication validated
5. ✅ **Framework independence**: Not dependent on Azure CLI bug fixes
6. ✅ **Explicit control**: Full visibility into HTTP requests/responses for debugging

### Negative
1. ⚠️ **More verbose**: REST API code is longer than single CLI command
2. ⚠️ **jq dependency**: Requires `jq` for JSON manipulation (already in GitHub Actions runners)
3. ⚠️ **Manual polling**: Must implement polling logic (CLI `--no-wait` + polling needed anyway)

### Neutral
1. 📝 **Different from Azure docs**: Most Azure documentation shows CLI commands, not REST API
2. 📝 **API version maintenance**: Must update API version if newer features needed (rare)

## Monitoring and Validation

### Success Criteria (All Met)
- [x] `az rest` deployment command completes without errors
- [x] Deployment registers in Azure portal with deployment ID
- [x] Deployment status transitions: Running → Succeeded
- [x] GitHub Actions workflow completes successfully
- [x] No "content already consumed" errors in logs

### Testing Strategy
1. **Local testing**: Run `./infrastructure/bicep/deploy.sh` with all 5 stages
2. **CI/CD testing**: GitHub Actions workflow with manual dispatch
3. **Error validation**: Intentional template errors produce clear error messages
4. **Timeout testing**: Long-running deployments respect 15-minute timeout

### Rollback Plan
If REST API approach fails:
1. Revert to `az deployment group create` with `--no-wait`
2. Wait for Azure CLI bug fix (monitor Azure/azure-cli#32149)
3. Consider Azure DevOps REST API tasks instead of CLI

## Related Issues
- **Fixes**: #99 (Azure Bicep deployment "content consumed" error)
- **Unblocks**: #95 (Azure API Management), #96 (AI Content Safety), #98 (NSG rules)
- **Related**: #62 (Multi-Agent System - needs infrastructure)

## References
- **Azure CLI Bug**: https://github.com/Azure/azure-cli/issues/32149
- **Azure Deployments REST API**: https://learn.microsoft.com/en-us/rest/api/resources/deployments
- **Bicep Templates**: `infrastructure/bicep/main-avm.bicep`
- **GitHub Actions Workflow**: `.github/workflows/deploy-infrastructure.yml`
- **Azure Verified Modules**: https://azure.github.io/Azure-Verified-Modules/

## Date
2025-01-04
