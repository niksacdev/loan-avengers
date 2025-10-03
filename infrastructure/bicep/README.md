# Loan Defenders - VNet Infrastructure (Bicep)

Enterprise-grade Azure VNet infrastructure with private endpoints following Zero Trust architecture principles.

## 📋 Overview

This Bicep infrastructure deploys enterprise-grade networking following **Zero Trust** and **Azure Well-Architected Framework** principles.

### What Gets Deployed

- **VNet** (10.0.0.0/16) with 3 subnets
- **Network Security Groups (NSGs)** with least privilege rules
- **Private DNS Zones** (5 zones for Azure services)
- **Private Endpoints** (optional, for Key Vault, Storage, AI Services, App Insights, OpenAI)

### Why This Architecture?

This infrastructure implements **private networking** to eliminate public internet exposure for backend services:

1. **Zero Trust Security**: No Azure services exposed to public internet
2. **Compliance Ready**: Meets enterprise security requirements (SOC 2, ISO 27001)
3. **Performance**: Lower latency via Azure backbone (vs public internet)
4. **Cost Optimization**: Free data transfer within VNet (vs internet egress charges)

## 🏗️ Architecture

```
┌─────────────────────────────────────────────┐
│ VNet: loan-defenders-vnet (10.0.0.0/16)     │
│                                              │
│ ┌────────────────────────────────────────┐  │
│ │ Container Apps Subnet (10.0.1.0/23)    │  │
│ │ - 512 IPs, NSG attached                │  │
│ └────────────────────────────────────────┘  │
│                                              │
│ ┌────────────────────────────────────────┐  │
│ │ APIM Subnet (10.0.3.0/24)              │  │
│ │ - 256 IPs, NSG attached                │  │
│ └────────────────────────────────────────┘  │
│                                              │
│ ┌────────────────────────────────────────┐  │
│ │ Private Endpoints Subnet (10.0.4.0/24) │  │
│ │ - 256 IPs, private endpoints           │  │
│ └────────────────────────────────────────┘  │
└─────────────────────────────────────────────┘
```

## 🔐 Understanding Private Endpoints & DNS Zones

### Why Private Endpoints?

**Problem**: By default, Azure services (Key Vault, Storage, AI Services) are accessible via **public internet**:
- ❌ Exposed to internet attacks
- ❌ Data travels over public internet
- ❌ Higher latency
- ❌ Cannot enforce VNet-level network policies

**Solution**: **Private Endpoints** give Azure services a **private IP address inside your VNet**:
- ✅ **No public exposure**: Service accessible only from within VNet
- ✅ **Azure backbone**: Traffic never leaves Microsoft network
- ✅ **Lower latency**: Direct connection via Azure backbone
- ✅ **NSG enforcement**: Network policies apply to private endpoint traffic

**Example**:
```
WITHOUT Private Endpoint:
  Container App → Public Internet → Key Vault (public IP)
  ❌ Exposed, slower, compliance risk

WITH Private Endpoint:
  Container App (10.0.1.x) → Private Endpoint (10.0.4.4) → Key Vault
  ✅ Private, fast, compliant
```

### Why Private DNS Zones?

**Problem**: Even with private endpoints, DNS resolution is tricky:
```bash
# Without Private DNS:
nslookup loan-defenders-kv.vault.azure.net
# Returns: PUBLIC IP (13.x.x.x) ❌
# Traffic goes to public endpoint, fails (blocked by firewall)

# With Private DNS:
nslookup loan-defenders-kv.vault.azure.net
# Returns: PRIVATE IP (10.0.4.4) ✅
# Traffic goes to private endpoint, succeeds
```

**Solution**: **Private DNS Zones** automatically resolve Azure service names to **private IPs**:

1. **DNS Zone**: `privatelink.vaultcore.azure.net`
2. **VNet Link**: Connects DNS zone to your VNet
3. **A Record**: `loan-defenders-kv` → `10.0.4.4` (auto-created by private endpoint)
4. **Result**: Apps in VNet automatically resolve to private IP

**How it works**:
```
Container App queries: loan-defenders-kv.vault.azure.net
  ↓
Azure DNS checks: Is there a private DNS zone for "vault.azure.net"?
  ↓
Finds: privatelink.vaultcore.azure.net (linked to VNet)
  ↓
Returns: 10.0.4.4 (private endpoint IP)
  ↓
Container App connects to Key Vault via private IP ✅
```

### The 5 DNS Zones We Create

| Azure Service | Public FQDN | Private DNS Zone | Purpose |
|---------------|-------------|------------------|---------|
| **Key Vault** | `*.vault.azure.net` | `privatelink.vaultcore.azure.net` | Secrets, API keys |
| **Blob Storage** | `*.blob.core.windows.net` | `privatelink.blob.core.windows.net` | Document storage |
| **Azure AI** | `*.cognitiveservices.azure.com` | `privatelink.cognitiveservices.azure.com` | Content Safety, AI services |
| **App Insights** | `*.monitor.azure.com` | `privatelink.monitor.azure.com` | Telemetry, logs |
| **Azure AI Foundry** | `*.api.azureml.ms` | `privatelink.api.azureml.ms` | AI Projects, GPT-4 inference |

**Why pre-create DNS zones?**
- ✅ **Ready for private endpoints**: When you deploy private endpoints later, DNS just works
- ✅ **No downtime**: No DNS reconfiguration needed
- ✅ **Cost**: Free (first 25 zones)

## 📦 Phased Deployment Strategy

### Why `deployPrivateEndpoints=false` in Dev?

**Phase 1** (Initial Deployment): **Foundation Only**
```json
{
  "deployPrivateEndpoints": {
    "value": false  // ⬅️ This is intentional!
  }
}
```

**Why?** Private endpoints require Azure resources to exist first:
- ❌ **Can't create private endpoint** for Key Vault that doesn't exist yet
- ❌ **Deployment would fail** with "Key Vault not found" error

**Phase 1 deploys**:
- ✅ VNet + subnets + NSGs (networking foundation)
- ✅ Private DNS zones (ready for private endpoints)
- ✅ VNet links to DNS zones
- ❌ NO private endpoints (nothing to connect to yet)

**Phase 2** (After Azure Services Exist): **Add Private Endpoints**
```bash
# 1. First, deploy Azure services separately
az keyvault create --name loan-defenders-kv ...
az storage account create --name loandefenderssa ...
az cognitiveservices account create --name loan-defenders-ai ...

# 2. Get resource IDs
KEYVAULT_ID=$(az keyvault show --name loan-defenders-kv --query id -o tsv)
STORAGE_ID=$(az storage account show --name loandefenderssa --query id -o tsv)

# 3. Update parameters file
vi environments/dev.parameters.json
{
  "deployPrivateEndpoints": { "value": true },  // ⬅️ Enable now
  "keyVaultId": { "value": "/subscriptions/.../loan-defenders-kv" },
  "storageAccountId": { "value": "/subscriptions/.../loandefenderssa" }
}

# 4. Re-deploy (adds private endpoints)
./deploy.sh dev loan-defenders-dev-rg
```

**Phase 2 deploys**:
- ✅ Private endpoints for all services
- ✅ Automatic DNS zone group creation (A records added)
- ✅ Immediate DNS resolution to private IPs

### Deployment Flow

```
┌─────────────────────────────────────────────────────┐
│ Phase 1: Foundation (deployPrivateEndpoints=false)  │
│ ./deploy.sh dev loan-defenders-dev-rg               │
│                                                      │
│ ✅ VNet created                                      │
│ ✅ Subnets created (Container Apps, APIM, PE)       │
│ ✅ NSGs created with rules                          │
│ ✅ Private DNS zones created (5 zones)              │
│ ✅ VNet links created                               │
│ ❌ Private endpoints skipped (no services yet)      │
└─────────────────────────────────────────────────────┘
              ↓
┌─────────────────────────────────────────────────────┐
│ (Manual) Deploy Azure Services                      │
│ - Create Key Vault, Storage, AI Services, etc.     │
│ - Save resource IDs                                 │
└─────────────────────────────────────────────────────┘
              ↓
┌─────────────────────────────────────────────────────┐
│ Phase 2: Private Endpoints (deployPrivateEndpoints=true) │
│ ./deploy.sh dev loan-defenders-dev-rg               │
│                                                      │
│ ✅ Private endpoints created for all services        │
│ ✅ DNS zone groups created (A records auto-added)   │
│ ✅ DNS resolution working (10.0.4.x IPs)            │
│                                                      │
│ Result: All services now private! 🎉               │
└─────────────────────────────────────────────────────┘
```

### Why This Matters

**Without this phased approach**:
```bash
# If we tried deployPrivateEndpoints=true initially:
❌ ERROR: KeyVault 'loan-defenders-kv' not found
❌ ERROR: StorageAccount 'loandefenderssa' not found
❌ Deployment fails
```

**With phased approach**:
```bash
# Phase 1: Foundation succeeds
✅ VNet, NSGs, DNS zones deployed
✅ Ready for services

# Phase 2: Private endpoints succeed
✅ Services exist, private endpoints connect
✅ DNS automatically resolves
✅ Zero Trust architecture complete
```

## 🚀 Quick Start

### Prerequisites

1. **Azure CLI** (2.20.0+):
   ```bash
   az --version
   az login
   ```

2. **Azure Subscription** with Contributor/Owner permissions

### Deployment

```bash
cd infrastructure/bicep

# Development environment
./deploy.sh dev loan-defenders-dev-rg

# Production environment
./deploy.sh prod loan-defenders-prod-rg
```

## 📁 File Structure

```
infrastructure/bicep/
├── main.bicep                   # Main orchestration
├── deploy.sh                    # Deployment script
├── README.md                    # This file
├── modules/
│   ├── vnet.bicep              # VNet + NSGs
│   ├── private-dns.bicep       # DNS zones
│   └── private-endpoints.bicep # Private endpoints
└── environments/
    ├── dev.parameters.json     # Dev config
    └── prod.parameters.json    # Prod config
```

## ⚙️ Configuration

Key parameters in `environments/*.parameters.json`:

- `location`: Azure region (default: `eastus`)
- `environment`: `dev`, `staging`, or `prod`
- `vnetAddressPrefix`: VNet CIDR (default: `10.0.0.0/16`)
- `deployPrivateEndpoints`: Deploy private endpoints (default: `false`)

## 🧪 Testing

### Validate Template

```bash
az deployment group validate \
  --resource-group loan-defenders-dev-rg \
  --template-file main.bicep \
  --parameters @environments/dev.parameters.json
```

### Test DNS Resolution

```bash
# Should resolve to private IP (10.0.4.x)
nslookup loan-defenders-kv.vault.azure.net
```

## 💰 Cost Estimation

| Resource | Monthly Cost |
|----------|-------------|
| VNet | Free |
| NSGs | Free |
| Private DNS Zones (5) | Free |
| Private Endpoints (5) | $37.50 |
| **Total** | **~$38/month** |

## 🔧 Troubleshooting

### Deployment Validation Errors

```bash
# Check Bicep syntax
az bicep build --file main.bicep

# Validate against Azure
az deployment group validate \
  --resource-group loan-defenders-dev-rg \
  --template-file main.bicep \
  --parameters @environments/dev.parameters.json
```

### Private Endpoint DNS Not Resolving

```bash
# Check DNS zone links
az network private-dns link vnet list \
  --resource-group loan-defenders-dev-rg \
  --zone-name privatelink.vaultcore.azure.net
```

## 📖 References

- **GitHub Issue**: [#94 - VNet Infrastructure](https://github.com/niksacdev/loan-defenders/issues/94)
- **Related**: [#57 Security](https://github.com/niksacdev/loan-defenders/issues/57), [#58 Container Apps](https://github.com/niksacdev/loan-defenders/issues/58)
- **Azure Docs**: [Bicep](https://learn.microsoft.com/en-us/azure/azure-resource-manager/bicep/), [Private Link](https://learn.microsoft.com/en-us/azure/private-link/)

## 🎯 Next Steps

1. Deploy Azure services (Key Vault, Storage, AI Services)
2. Re-deploy with `deployPrivateEndpoints=true`
3. Deploy Container Apps (#58)
4. Deploy APIM (#95)
