// ==============================================================================
// Security Module - Azure Verified Modules
// ==============================================================================
// Key Vault, Storage Account, and Managed Identity
//
// Resources:
//   - 1x Managed Identity (User-Assigned)
//   - 1x Key Vault (RBAC-enabled, private network access)
//   - 1x Storage Account (encrypted, private network access)
//
// AVM Modules:
//   - avm/res/key-vault/vault:0.13.3
//   - avm/res/storage/storage-account:0.27.1
// ==============================================================================

targetScope = 'resourceGroup'

// ==============================================================================
// Parameters
// ==============================================================================

@description('Azure region for resources')
param location string = resourceGroup().location

@description('Environment name (dev, staging, prod)')
param environment string

@description('Key Vault name')
param keyVaultName string

@description('Storage Account name')
param storageAccountName string

@description('Managed Identity name')
param managedIdentityName string

@description('Common tags for all resources')
param tags object

// ==============================================================================
// Managed Identity
// ==============================================================================
// Note: No AVM module available yet for Managed Identity (as of Jan 2025)

resource managedIdentity 'Microsoft.ManagedIdentity/userAssignedIdentities@2023-01-31' = {
  name: managedIdentityName
  location: location
  tags: tags
}

// ==============================================================================
// Key Vault
// ==============================================================================

module keyVault 'br/public:avm/res/key-vault/vault:0.13.3' = {
  name: 'keyvault-deployment'
  params: {
    name: keyVaultName
    location: location
    tags: tags

    sku: 'standard'
    enableRbacAuthorization: true
    enableSoftDelete: true
    softDeleteRetentionInDays: 90
    enablePurgeProtection: true
    publicNetworkAccess: 'Disabled'

    networkAcls: {
      bypass: 'AzureServices'
      defaultAction: 'Deny'
    }
  }
}

// ==============================================================================
// Storage Account
// ==============================================================================

module storageAccount 'br/public:avm/res/storage/storage-account:0.27.1' = {
  name: 'storage-deployment'
  params: {
    name: storageAccountName
    location: location
    tags: tags

    skuName: 'Standard_LRS'
    kind: 'StorageV2'
    accessTier: 'Hot'
    allowBlobPublicAccess: false
    minimumTlsVersion: 'TLS1_2'
    supportsHttpsTrafficOnly: true
    publicNetworkAccess: 'Disabled'
  }
}

// ==============================================================================
// Outputs
// ==============================================================================

@description('Managed Identity resource ID')
output managedIdentityId string = managedIdentity.id

@description('Managed Identity principal ID')
output managedIdentityPrincipalId string = managedIdentity.properties.principalId

@description('Managed Identity client ID')
output managedIdentityClientId string = managedIdentity.properties.clientId

@description('Key Vault resource ID')
output keyVaultId string = keyVault.outputs.resourceId

@description('Key Vault name')
output keyVaultName string = keyVault.outputs.name

@description('Key Vault URI')
output keyVaultUri string = keyVault.outputs.uri

@description('Storage Account resource ID')
output storageAccountId string = storageAccount.outputs.resourceId

@description('Storage Account name')
output storageAccountName string = storageAccount.outputs.name
