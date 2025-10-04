# ADR-021: Azure Verified Modules (AVM) Adoption for Infrastructure

**Status**: Accepted
**Date**: 2025-10-04
**Deciders**: Development Team
**Related**: Issue #94, PR #97

## Context

Our Azure infrastructure was initially built using custom Bicep modules. While functional, this approach had several limitations:

1. **No Microsoft Support**: Custom modules lack official Microsoft backing
2. **Manual Best Practices**: We had to research and implement Azure best practices ourselves
3. **Maintenance Burden**: Keeping up with Azure changes requires constant module updates
4. **Security Gaps**: No guarantee our custom modules follow latest security standards
5. **Limited Reusability**: Custom modules are specific to our use case

During infrastructure review (Issue #94), we discovered **Azure Verified Modules (AVM)** - Microsoft's official, supported, and verified Bicep module library available at `br/public:avm/res/*` in the public registry.

### What are Azure Verified Modules?

**Azure Verified Modules (AVM)** are:
- **Microsoft-maintained**: Official modules from the Azure product teams
- **Verified**: Tested, validated, and follow Azure best practices
- **Supported**: Backed by Microsoft support and SLAs
- **Up-to-date**: Automatically updated with new Azure features and security patches
- **Comprehensive**: Cover most Azure resources with standardized interfaces

**AVM Documentation**: https://azure.github.io/Azure-Verified-Modules/

### Options Considered

#### 1. Keep Custom Bicep Modules
**Pros**:
- No migration effort required
- Full control over implementation details
- Already tested in our environment

**Cons**:
- No Microsoft support or guarantees
- Manual security and best practices implementation
- Ongoing maintenance burden
- Risk of falling behind Azure updates
- Potential security vulnerabilities

#### 2. Adopt Azure Verified Modules (AVM)
**Pros**:
- Microsoft-verified security and best practices
- Official support and documentation
- Automatic updates with Azure platform
- Reduced maintenance burden
- Production-ready out of the box
- Better compliance and audit trails

**Cons**:
- Migration effort required
- Learning curve for AVM patterns
- Some resources may not have AVM modules yet

#### 3. Hybrid Approach (Custom + AVM)
**Pros**:
- Use AVM where available, custom elsewhere
- Gradual migration path

**Cons**:
- Inconsistent patterns
- Still maintains custom modules
- Confusion about which approach to use

## Decision

**We will adopt Azure Verified Modules (AVM) for all infrastructure resources.**

### Rationale

During review, the question was asked: *"are we using AVM azure verified modules for our bicep scripts"*

The answer was **no** - we were using custom modules. The response was decisive:

> *"i think if AVM are verified modules from Microsoft we should just use them for everything"*

This decision was based on:
1. **Trust in Microsoft verification** over custom implementations
2. **Reduced risk** with officially supported modules
3. **Better long-term maintainability** with automatic updates
4. **Production readiness** with built-in best practices

## Implementation

### Migration Strategy

We refactored our infrastructure into a **thin orchestrator pattern** with focused, modular Bicep files:

#### New Architecture (AVM-based)

```
infrastructure/bicep/
├── main-avm.bicep              # Thin orchestrator (211 lines)
├── modules/
│   ├── networking.bicep        # VNet, NSGs, Subnets (396 lines)
│   ├── security.bicep          # Key Vault, Storage, Identity (124 lines)
│   ├── ai-services.bicep       # AI Services, Monitoring (135 lines)
│   ├── container-apps.bicep    # Container Apps Environment (82 lines)
│   └── rbac.bicep             # RBAC permissions (104 lines)
└── environments/
    ├── dev.parameters.json
    ├── staging.parameters.json
    └── prod.parameters.json
```

#### AVM Modules Used

| Resource | AVM Module | Version |
|----------|------------|---------|
| Virtual Network | `avm/res/network/virtual-network` | 0.7.1 |
| Network Security Groups | `avm/res/network/network-security-group` | 0.5.1 |
| Key Vault | `avm/res/key-vault/vault` | 0.13.3 |
| Storage Account | `avm/res/storage/storage-account` | 0.27.1 |
| AI Services | `avm/res/cognitive-services/account` | 0.13.2 |
| Log Analytics | `avm/res/operational-insights/workspace` | 0.12.0 |
| Application Insights | `avm/res/insights/component` | 0.6.0 |

#### Resources Without AVM (Using Native Azure)

Some resources don't have AVM modules yet (as of October 2025):
- **Managed Identity**: Using native `Microsoft.ManagedIdentity/userAssignedIdentities@2023-01-31`
- **Container Apps**: Using native `Microsoft.App/managedEnvironments@2024-03-01`

These will be migrated to AVM when modules become available.

### Deployment Stages

The orchestrator supports staged deployments:

1. **Foundation** (`--stage foundation`): Networking (VNet, NSGs, Subnets)
2. **Security** (`--stage security`): Key Vault, Storage, Managed Identity
3. **AI** (`--stage ai`): AI Services, Log Analytics, App Insights + RBAC
4. **Apps** (`--stage apps`): Container Apps Environment
5. **All** (`--stage all`): Deploy everything (default)

### Example: Networking Module with AVM

```bicep
// Create NSG using AVM
module nsgContainerApps 'br/public:avm/res/network/network-security-group:0.5.1' = {
  name: 'nsg-container-apps-deployment'
  params: {
    name: '${vnetName}-container-apps-nsg'
    location: location
    tags: tags
    securityRules: [
      {
        name: 'AllowContainerAppsPlatformInbound'
        properties: {
          description: 'Allow Container Apps platform management'
          protocol: '*'
          sourcePortRange: '*'
          destinationPortRanges: ['1194', '9000']
          sourceAddressPrefix: 'AzureCloud'
          destinationAddressPrefix: containerAppsSubnetPrefix
          access: 'Allow'
          priority: 110
          direction: 'Inbound'
        }
      }
    ]
  }
}

// Create VNet using AVM
module vnet 'br/public:avm/res/network/virtual-network:0.7.1' = {
  name: 'vnet-deployment'
  params: {
    name: vnetName
    location: location
    addressPrefixes: [vnetAddressPrefix]
    tags: tags
    subnets: [
      {
        name: 'container-apps-subnet'
        addressPrefix: containerAppsSubnetPrefix
        delegation: 'Microsoft.App/environments'
        networkSecurityGroupResourceId: nsgContainerApps.outputs.resourceId
      }
    ]
  }
}
```

### Migration Process

1. **Created new AVM-based modules** in `infrastructure/bicep/modules/`
2. **Updated main orchestrator** to use `main-avm.bicep`
3. **Removed old custom modules**:
   - Deleted `modules/foundation/`, `modules/ai/`, `modules/apps/`, `modules/security/` directories
   - Removed old `foundation.bicep`, `ai.bicep`, `apps.bicep` files
   - Removed old `main.bicep` and compiled JSON artifacts
4. **Updated deployment script** (`deploy.sh`) to reference `main-avm.bicep`
5. **Added RBAC module** for Azure AI Foundry cross-resource permissions

## Consequences

### Positive

1. **Microsoft Support**: Official backing and SLA coverage
2. **Security Compliance**: Built-in Azure security best practices
3. **Automatic Updates**: Modules updated with Azure platform changes
4. **Reduced Maintenance**: No need to track Azure changes manually
5. **Production Ready**: Verified modules tested at scale
6. **Better Documentation**: Comprehensive AVM docs and examples
7. **Consistency**: Standardized patterns across resources
8. **Audit Trail**: Clear versioning and change tracking

### Negative

1. **Learning Curve**: Team needs to understand AVM patterns and conventions
2. **Version Management**: Must track and update AVM module versions
3. **Limited Coverage**: Some resources lack AVM modules (use native Azure temporarily)
4. **Module Constraints**: Less flexibility than custom implementations
5. **Breaking Changes**: AVM updates may introduce breaking changes

### Neutral

1. **Module Versioning**: Need to pin versions for stability (`avm/res/*/module:X.Y.Z`)
2. **Registry Dependency**: Reliant on public Bicep registry availability
3. **Testing Strategy**: Must validate AVM updates before production deployment

## Technical Debt Addressed

### Fixed Issues from PR #97 Review

During the migration, we addressed Priority 1 NSG security issues:

1. **APIM NSG Rules**: Added missing HTTP (port 80) and health probe (port 6390) rules
2. **Container Apps Platform Rules**: Added UDP/1194 and TCP/9000 for platform management
3. **Overly Permissive Rules**: Replaced `AzureCloud` with specific service tags (`AzureMonitor`)

See: Issue #98 - NSG Security Improvements

### Clean Architecture

- **Thin Orchestrator**: Main file is now 211 lines (was 600+)
- **Focused Modules**: Each module handles single responsibility
- **No Circular Dependencies**: Resolved NSG → VNet dependency issues
- **Name Length Constraints**: Fixed Key Vault and Storage Account naming

## Migration Results

### Files Changed
- **Created**: 6 new AVM-based Bicep modules
- **Updated**: `deploy.sh` script, GitHub Actions workflows
- **Removed**: 7+ old custom module files and directories
- **Total LOC**: ~1,000 lines of Bicep (down from ~1,200 custom)

### Quality Metrics
- ✅ **Bicep Validation**: All templates compile without errors
- ✅ **Linting**: No warnings or errors
- ✅ **Security**: Built-in AVM security best practices
- ✅ **Modular**: Clean separation of concerns

### Deployment Impact

**Breaking Changes**:
- Must use `main-avm.bicep` instead of `main.bicep`
- Different module structure and parameters
- Requires redeployment to all environments

**Migration Steps**:
1. Merge PR with AVM changes
2. Update GitHub Actions to reference `main-avm.bicep`
3. Deploy to dev environment first (test end-to-end)
4. Deploy to staging and production
5. Monitor for any AVM module updates

## Lessons Learned

### What Worked Well

1. **Staged Approach**: Building modules incrementally reduced complexity
2. **NSG-First Pattern**: Creating NSGs before VNet resolved dependencies
3. **Version Pinning**: Using specific AVM versions ensures stability
4. **Modular Design**: Easier to review, test, and maintain

### Challenges Faced

1. **NSG Module Version**: Initial version 0.6.0 didn't exist (corrected to 0.5.1)
2. **Circular Dependencies**: NSG/VNet reference required careful ordering
3. **Name Constraints**: Azure 24-character limits required naming convention changes
4. **Output References**: Had to use AVM output properties instead of `reference()` function

### Future Considerations

1. **Monitor AVM Updates**: Track new module releases and security patches
2. **Migrate Native Resources**: Move to AVM when modules become available
3. **Automate Version Updates**: Consider Renovate/Dependabot for AVM module versions
4. **Document Patterns**: Create team guidelines for AVM usage

## References

- **AVM Documentation**: https://azure.github.io/Azure-Verified-Modules/
- **Bicep Public Registry**: https://github.com/Azure/bicep-registry-modules
- **Issue #94**: Infrastructure deployment tracking
- **PR #97**: AVM migration implementation
- **Issue #98**: NSG security improvements
- **Related ADRs**:
  - ADR-009: Azure Container Apps Deployment
  - ADR-016: GitHub Actions Security
