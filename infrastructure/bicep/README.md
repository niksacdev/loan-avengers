# Loan Defenders - VNet Infrastructure (Bicep)

Enterprise-grade Azure VNet infrastructure with private endpoints following Zero Trust architecture principles.

## 📋 Overview

This Bicep infrastructure deploys:

- **VNet** (10.0.0.0/16) with 3 subnets
- **Network Security Groups (NSGs)** with least privilege rules
- **Private DNS Zones** (5 zones for Azure services)
- **Private Endpoints** (optional, for Key Vault, Storage, AI Services, App Insights, OpenAI)

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
