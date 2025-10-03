// ==============================================================================
// Main Infrastructure Deployment - Loan Defenders
// ==============================================================================
// Deploys enterprise VNet infrastructure with private endpoints
//
// Usage:
//   az deployment group create \
//     --resource-group loan-defenders-rg \
//     --template-file main.bicep \
//     --parameters main.parameters.json
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
param environment string = 'dev'

@description('VNet name')
param vnetName string = 'loan-defenders-vnet'

@description('VNet address space')
param vnetAddressPrefix string = '10.0.0.0/16'

@description('Container Apps subnet prefix')
param containerAppsSubnetPrefix string = '10.0.1.0/23'

@description('APIM subnet prefix')
param apimSubnetPrefix string = '10.0.3.0/24'

@description('Private Endpoints subnet prefix')
param privateEndpointsSubnetPrefix string = '10.0.4.0/24'

@description('Key Vault resource ID (optional, leave empty if not yet created)')
param keyVaultId string = ''

@description('Storage Account resource ID (optional, leave empty if not yet created)')
param storageAccountId string = ''

@description('AI Services resource ID (optional, leave empty if not yet created)')
param aiServicesId string = ''

@description('Application Insights resource ID (optional, leave empty if not yet created)')
param appInsightsId string = ''

@description('Azure OpenAI resource ID (optional, leave empty if not yet created)')
param openAIId string = ''

@description('Deploy private endpoints (set to false if Azure resources don\'t exist yet)')
param deployPrivateEndpoints bool = false

// ==============================================================================
// Variables
// ==============================================================================

var commonTags = {
  environment: environment
  project: 'loan-defenders'
  managedBy: 'bicep'
}

// ==============================================================================
// Module: VNet with Subnets and NSGs
// ==============================================================================

module vnet 'modules/vnet.bicep' = {
  name: 'vnet-deployment'
  params: {
    location: location
    vnetName: vnetName
    vnetAddressPrefix: vnetAddressPrefix
    containerAppsSubnetPrefix: containerAppsSubnetPrefix
    apimSubnetPrefix: apimSubnetPrefix
    privateEndpointsSubnetPrefix: privateEndpointsSubnetPrefix
    tags: commonTags
  }
}

// ==============================================================================
// Module: Private DNS Zones
// ==============================================================================

module privateDns 'modules/private-dns.bicep' = {
  name: 'private-dns-deployment'
  params: {
    vnetId: vnet.outputs.vnetId
    vnetName: vnet.outputs.vnetName
    tags: commonTags
  }
}

// ==============================================================================
// Module: Private Endpoints (optional, deploy after Azure resources exist)
// ==============================================================================

module privateEndpoints 'modules/private-endpoints.bicep' = if (deployPrivateEndpoints) {
  name: 'private-endpoints-deployment'
  params: {
    privateEndpointsSubnetId: vnet.outputs.privateEndpointsSubnetId
    location: location
    keyVaultId: keyVaultId
    storageAccountId: storageAccountId
    aiServicesId: aiServicesId
    appInsightsId: appInsightsId
    openAIId: openAIId
    keyVaultDnsZoneId: privateDns.outputs.keyVaultDnsZoneId
    blobDnsZoneId: privateDns.outputs.blobDnsZoneId
    aiServicesDnsZoneId: privateDns.outputs.aiServicesDnsZoneId
    monitorDnsZoneId: privateDns.outputs.monitorDnsZoneId
    openaiDnsZoneId: privateDns.outputs.openaiDnsZoneId
    tags: commonTags
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

@description('OpenAI DNS Zone ID')
output openaiDnsZoneId string = privateDns.outputs.openaiDnsZoneId

@description('Deployment completed successfully')
output deploymentComplete bool = true

@description('Private endpoints deployed')
output privateEndpointsDeployed bool = deployPrivateEndpoints
