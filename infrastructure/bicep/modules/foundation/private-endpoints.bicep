// ==============================================================================
// Private Endpoints Module - Loan Defenders
// ==============================================================================
// Creates private endpoints for Azure services
// Note: Requires existing Azure resources (Key Vault, Storage, etc.)
// ==============================================================================

@description('Private Endpoints subnet ID')
param privateEndpointsSubnetId string

@description('Azure region for resources')
param location string = resourceGroup().location

@description('Key Vault resource ID (if exists)')
param keyVaultId string = ''

@description('Storage Account resource ID (if exists)')
param storageAccountId string = ''

@description('AI Services resource ID (if exists)')
param aiServicesId string = ''

@description('Application Insights resource ID (if exists)')
param appInsightsId string = ''

@description('Azure AI Foundry Project resource ID (if exists)')
param aiFoundryProjectId string = ''

@description('Key Vault DNS Zone ID')
param keyVaultDnsZoneId string

@description('Blob Storage DNS Zone ID')
param blobDnsZoneId string

@description('AI Services DNS Zone ID')
param aiServicesDnsZoneId string

@description('Monitor DNS Zone ID')
param monitorDnsZoneId string

@description('Azure AI Foundry DNS Zone ID')
param aiFoundryDnsZoneId string

@description('Tags for resources')
param tags object = {
  environment: 'production'
  project: 'loan-defenders'
  managedBy: 'bicep'
}

// ==============================================================================
// Private Endpoints
// ==============================================================================

// Key Vault Private Endpoint (only if Key Vault exists)
resource keyVaultPrivateEndpoint 'Microsoft.Network/privateEndpoints@2023-05-01' = if (!empty(keyVaultId)) {
  name: 'loan-defenders-kv-pe'
  location: location
  tags: tags
  properties: {
    subnet: {
      id: privateEndpointsSubnetId
    }
    privateLinkServiceConnections: [
      {
        name: 'kv-pe-connection'
        properties: {
          privateLinkServiceId: keyVaultId
          groupIds: [
            'vault'
          ]
        }
      }
    ]
  }
}

// Key Vault Private DNS Zone Group
resource keyVaultDnsZoneGroup 'Microsoft.Network/privateEndpoints/privateDnsZoneGroups@2023-05-01' = if (!empty(keyVaultId)) {
  parent: keyVaultPrivateEndpoint
  name: 'default'
  properties: {
    privateDnsZoneConfigs: [
      {
        name: 'privatelink-vaultcore-azure-net'
        properties: {
          privateDnsZoneId: keyVaultDnsZoneId
        }
      }
    ]
  }
}

// Blob Storage Private Endpoint (only if Storage Account exists)
resource blobPrivateEndpoint 'Microsoft.Network/privateEndpoints@2023-05-01' = if (!empty(storageAccountId)) {
  name: 'loan-defenders-blob-pe'
  location: location
  tags: tags
  properties: {
    subnet: {
      id: privateEndpointsSubnetId
    }
    privateLinkServiceConnections: [
      {
        name: 'blob-pe-connection'
        properties: {
          privateLinkServiceId: storageAccountId
          groupIds: [
            'blob'
          ]
        }
      }
    ]
  }
}

// Blob Storage Private DNS Zone Group
resource blobDnsZoneGroup 'Microsoft.Network/privateEndpoints/privateDnsZoneGroups@2023-05-01' = if (!empty(storageAccountId)) {
  parent: blobPrivateEndpoint
  name: 'default'
  properties: {
    privateDnsZoneConfigs: [
      {
        name: 'privatelink-blob-core-windows-net'
        properties: {
          privateDnsZoneId: blobDnsZoneId
        }
      }
    ]
  }
}

// AI Services Private Endpoint (only if AI Services exists)
resource aiServicesPrivateEndpoint 'Microsoft.Network/privateEndpoints@2023-05-01' = if (!empty(aiServicesId)) {
  name: 'loan-defenders-ai-pe'
  location: location
  tags: tags
  properties: {
    subnet: {
      id: privateEndpointsSubnetId
    }
    privateLinkServiceConnections: [
      {
        name: 'ai-pe-connection'
        properties: {
          privateLinkServiceId: aiServicesId
          groupIds: [
            'account'
          ]
        }
      }
    ]
  }
}

// AI Services Private DNS Zone Group
resource aiServicesDnsZoneGroup 'Microsoft.Network/privateEndpoints/privateDnsZoneGroups@2023-05-01' = if (!empty(aiServicesId)) {
  parent: aiServicesPrivateEndpoint
  name: 'default'
  properties: {
    privateDnsZoneConfigs: [
      {
        name: 'privatelink-cognitiveservices-azure-com'
        properties: {
          privateDnsZoneId: aiServicesDnsZoneId
        }
      }
    ]
  }
}

// Application Insights Private Endpoint (only if App Insights exists)
resource appInsightsPrivateEndpoint 'Microsoft.Network/privateEndpoints@2023-05-01' = if (!empty(appInsightsId)) {
  name: 'loan-defenders-appinsights-pe'
  location: location
  tags: tags
  properties: {
    subnet: {
      id: privateEndpointsSubnetId
    }
    privateLinkServiceConnections: [
      {
        name: 'appinsights-pe-connection'
        properties: {
          privateLinkServiceId: appInsightsId
          groupIds: [
            'azuremonitor'
          ]
        }
      }
    ]
  }
}

// Application Insights Private DNS Zone Group
resource appInsightsDnsZoneGroup 'Microsoft.Network/privateEndpoints/privateDnsZoneGroups@2023-05-01' = if (!empty(appInsightsId)) {
  parent: appInsightsPrivateEndpoint
  name: 'default'
  properties: {
    privateDnsZoneConfigs: [
      {
        name: 'privatelink-monitor-azure-com'
        properties: {
          privateDnsZoneId: monitorDnsZoneId
        }
      }
    ]
  }
}

// Azure AI Foundry Project Private Endpoint (only if AI Foundry Project exists)
resource aiFoundryPrivateEndpoint 'Microsoft.Network/privateEndpoints@2023-05-01' = if (!empty(aiFoundryProjectId)) {
  name: 'loan-defenders-aifoundry-pe'
  location: location
  tags: tags
  properties: {
    subnet: {
      id: privateEndpointsSubnetId
    }
    privateLinkServiceConnections: [
      {
        name: 'aifoundry-pe-connection'
        properties: {
          privateLinkServiceId: aiFoundryProjectId
          groupIds: [
            'amlworkspace'
          ]
        }
      }
    ]
  }
}

// Azure AI Foundry Private DNS Zone Group
resource aiFoundryDnsZoneGroup 'Microsoft.Network/privateEndpoints/privateDnsZoneGroups@2023-05-01' = if (!empty(aiFoundryProjectId)) {
  parent: aiFoundryPrivateEndpoint
  name: 'default'
  properties: {
    privateDnsZoneConfigs: [
      {
        name: 'privatelink-api-azureml-ms'
        properties: {
          privateDnsZoneId: aiFoundryDnsZoneId
        }
      }
    ]
  }
}

// ==============================================================================
// Outputs
// ==============================================================================

@description('Key Vault Private Endpoint ID')
output keyVaultPrivateEndpointId string = !empty(keyVaultId) ? keyVaultPrivateEndpoint.id : ''

@description('Blob Storage Private Endpoint ID')
output blobPrivateEndpointId string = !empty(storageAccountId) ? blobPrivateEndpoint.id : ''

@description('AI Services Private Endpoint ID')
output aiServicesPrivateEndpointId string = !empty(aiServicesId) ? aiServicesPrivateEndpoint.id : ''

@description('Application Insights Private Endpoint ID')
output appInsightsPrivateEndpointId string = !empty(appInsightsId) ? appInsightsPrivateEndpoint.id : ''

@description('Azure AI Foundry Project Private Endpoint ID')
output aiFoundryPrivateEndpointId string = !empty(aiFoundryProjectId) ? aiFoundryPrivateEndpoint.id : ''
