// ==============================================================================
// Private DNS Zones Module - Loan Defenders
// ==============================================================================
// Creates private DNS zones for Azure services with VNet links
// Zones created:
// - Key Vault: privatelink.vaultcore.azure.net
// - Blob Storage: privatelink.blob.core.windows.net
// - Azure AI Services: privatelink.cognitiveservices.azure.com
// - Application Insights: privatelink.monitor.azure.com
// - Azure OpenAI: privatelink.openai.azure.com
// ==============================================================================

@description('VNet resource ID to link DNS zones to')
param vnetId string

@description('VNet name for link naming')
param vnetName string

@description('Tags for resources')
param tags object = {
  environment: 'production'
  project: 'loan-defenders'
  managedBy: 'bicep'
}

// ==============================================================================
// Private DNS Zones
// ==============================================================================

// Key Vault Private DNS Zone
resource keyVaultDnsZone 'Microsoft.Network/privateDnsZones@2020-06-01' = {
  name: 'privatelink.vaultcore.azure.net'
  location: 'global'
  tags: tags
}

// Blob Storage Private DNS Zone
resource blobDnsZone 'Microsoft.Network/privateDnsZones@2020-06-01' = {
  name: 'privatelink.blob.core.windows.net'
  location: 'global'
  tags: tags
}

// Azure AI Services Private DNS Zone
resource aiServicesDnsZone 'Microsoft.Network/privateDnsZones@2020-06-01' = {
  name: 'privatelink.cognitiveservices.azure.com'
  location: 'global'
  tags: tags
}

// Application Insights / Azure Monitor Private DNS Zone
resource monitorDnsZone 'Microsoft.Network/privateDnsZones@2020-06-01' = {
  name: 'privatelink.monitor.azure.com'
  location: 'global'
  tags: tags
}

// Azure AI Foundry (Projects) Private DNS Zone
// Note: AI Foundry uses Azure ML infrastructure for project endpoints
resource aiFoundryDnsZone 'Microsoft.Network/privateDnsZones@2020-06-01' = {
  name: 'privatelink.api.azureml.ms'
  location: 'global'
  tags: tags
}

// ==============================================================================
// VNet Links (Connect DNS zones to VNet)
// ==============================================================================

resource keyVaultDnsLink 'Microsoft.Network/privateDnsZones/virtualNetworkLinks@2020-06-01' = {
  parent: keyVaultDnsZone
  name: '${vnetName}-keyvault-link'
  location: 'global'
  tags: tags
  properties: {
    registrationEnabled: false
    virtualNetwork: {
      id: vnetId
    }
  }
}

resource blobDnsLink 'Microsoft.Network/privateDnsZones/virtualNetworkLinks@2020-06-01' = {
  parent: blobDnsZone
  name: '${vnetName}-blob-link'
  location: 'global'
  tags: tags
  properties: {
    registrationEnabled: false
    virtualNetwork: {
      id: vnetId
    }
  }
}

resource aiServicesDnsLink 'Microsoft.Network/privateDnsZones/virtualNetworkLinks@2020-06-01' = {
  parent: aiServicesDnsZone
  name: '${vnetName}-aiservices-link'
  location: 'global'
  tags: tags
  properties: {
    registrationEnabled: false
    virtualNetwork: {
      id: vnetId
    }
  }
}

resource monitorDnsLink 'Microsoft.Network/privateDnsZones/virtualNetworkLinks@2020-06-01' = {
  parent: monitorDnsZone
  name: '${vnetName}-monitor-link'
  location: 'global'
  tags: tags
  properties: {
    registrationEnabled: false
    virtualNetwork: {
      id: vnetId
    }
  }
}

resource aiFoundryDnsLink 'Microsoft.Network/privateDnsZones/virtualNetworkLinks@2020-06-01' = {
  parent: aiFoundryDnsZone
  name: '${vnetName}-aifoundry-link'
  location: 'global'
  tags: tags
  properties: {
    registrationEnabled: false
    virtualNetwork: {
      id: vnetId
    }
  }
}

// ==============================================================================
// Outputs
// ==============================================================================

@description('Key Vault DNS Zone resource ID')
output keyVaultDnsZoneId string = keyVaultDnsZone.id

@description('Blob Storage DNS Zone resource ID')
output blobDnsZoneId string = blobDnsZone.id

@description('AI Services DNS Zone resource ID')
output aiServicesDnsZoneId string = aiServicesDnsZone.id

@description('Monitor DNS Zone resource ID')
output monitorDnsZoneId string = monitorDnsZone.id

@description('Azure AI Foundry DNS Zone resource ID')
output aiFoundryDnsZoneId string = aiFoundryDnsZone.id

@description('Key Vault DNS Zone name')
output keyVaultDnsZoneName string = keyVaultDnsZone.name

@description('Blob Storage DNS Zone name')
output blobDnsZoneName string = blobDnsZone.name

@description('AI Services DNS Zone name')
output aiServicesDnsZoneName string = aiServicesDnsZone.name

@description('Monitor DNS Zone name')
output monitorDnsZoneName string = monitorDnsZone.name

@description('Azure AI Foundry DNS Zone name')
output aiFoundryDnsZoneName string = aiFoundryDnsZone.name
