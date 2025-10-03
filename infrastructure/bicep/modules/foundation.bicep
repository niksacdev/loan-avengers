// ==============================================================================
// Foundation Module - Loan Defenders
// ==============================================================================
// Stage 1: Networking foundation (VNet, NSGs, Private DNS zones)
// This stage must be deployed first as other stages depend on it
// ==============================================================================

targetScope = 'resourceGroup'

// ==============================================================================
// Parameters
// ==============================================================================

@description('Azure region for resources')
param location string = resourceGroup().location

@description('Environment name (dev, staging, prod)')
@allowed([
  'dev'
  'staging'
  'prod'
])
param environment string

@description('VNet name')
param vnetName string

@description('VNet address space')
param vnetAddressPrefix string = '10.0.0.0/16'

@description('Container Apps subnet prefix')
param containerAppsSubnetPrefix string = '10.0.1.0/23'

@description('APIM subnet prefix')
param apimSubnetPrefix string = '10.0.3.0/24'

@description('Private Endpoints subnet prefix')
param privateEndpointsSubnetPrefix string = '10.0.4.0/24'

@description('Deploy private endpoints (set to false until Azure services exist)')
param deployPrivateEndpoints bool = false

@description('Key Vault resource ID (optional)')
param keyVaultId string = ''

@description('Storage Account resource ID (optional)')
param storageAccountId string = ''

@description('AI Services resource ID (optional)')
param aiServicesId string = ''

@description('Application Insights resource ID (optional)')
param appInsightsId string = ''

@description('Azure AI Foundry Project resource ID (optional)')
param aiFoundryProjectId string = ''

@description('Tags for resources')
param tags object

// ==============================================================================
// Module: VNet with Subnets and NSGs
// ==============================================================================

module vnet 'foundation/vnet.bicep' = {
  name: 'vnet-deployment'
  params: {
    location: location
    vnetName: vnetName
    vnetAddressPrefix: vnetAddressPrefix
    containerAppsSubnetPrefix: containerAppsSubnetPrefix
    apimSubnetPrefix: apimSubnetPrefix
    privateEndpointsSubnetPrefix: privateEndpointsSubnetPrefix
    tags: tags
  }
}

// ==============================================================================
// Module: Private DNS Zones
// ==============================================================================

module privateDns 'foundation/private-dns.bicep' = {
  name: 'private-dns-deployment'
  params: {
    vnetId: vnet.outputs.vnetId
    vnetName: vnet.outputs.vnetName
    tags: tags
  }
}

// ==============================================================================
// Module: Private Endpoints (conditional)
// ==============================================================================

module privateEndpoints 'foundation/private-endpoints.bicep' = if (deployPrivateEndpoints) {
  name: 'private-endpoints-deployment'
  params: {
    privateEndpointsSubnetId: vnet.outputs.privateEndpointsSubnetId
    location: location
    keyVaultId: keyVaultId
    storageAccountId: storageAccountId
    aiServicesId: aiServicesId
    appInsightsId: appInsightsId
    aiFoundryProjectId: aiFoundryProjectId
    keyVaultDnsZoneId: privateDns.outputs.keyVaultDnsZoneId
    blobDnsZoneId: privateDns.outputs.blobDnsZoneId
    aiServicesDnsZoneId: privateDns.outputs.aiServicesDnsZoneId
    monitorDnsZoneId: privateDns.outputs.monitorDnsZoneId
    aiFoundryDnsZoneId: privateDns.outputs.aiFoundryDnsZoneId
    tags: tags
  }
}

// ==============================================================================
// Outputs
// ==============================================================================

@description('VNet resource ID')
output vnetId string = vnet.outputs.vnetId

@description('VNet name')
output vnetName string = vnet.outputs.vnetName

@description('Container Apps subnet ID')
output containerAppsSubnetId string = vnet.outputs.containerAppsSubnetId

@description('APIM subnet ID')
output apimSubnetId string = vnet.outputs.apimSubnetId

@description('Private Endpoints subnet ID')
output privateEndpointsSubnetId string = vnet.outputs.privateEndpointsSubnetId

@description('Key Vault DNS Zone ID')
output keyVaultDnsZoneId string = privateDns.outputs.keyVaultDnsZoneId

@description('Blob Storage DNS Zone ID')
output blobDnsZoneId string = privateDns.outputs.blobDnsZoneId

@description('AI Services DNS Zone ID')
output aiServicesDnsZoneId string = privateDns.outputs.aiServicesDnsZoneId

@description('Monitor DNS Zone ID')
output monitorDnsZoneId string = privateDns.outputs.monitorDnsZoneId

@description('Azure AI Foundry DNS Zone ID')
output aiFoundryDnsZoneId string = privateDns.outputs.aiFoundryDnsZoneId

@description('Private endpoints deployed')
output privateEndpointsDeployed bool = deployPrivateEndpoints

@description('Foundation deployment complete')
output deploymentComplete bool = true
