// ==============================================================================
// Main Infrastructure Deployment - Loan Defenders
// ==============================================================================
// CI/CD-ready staged deployment with conditional execution
//
// Stages:
//   - foundation: VNet, NSGs, Private DNS zones
//   - security: Key Vault, Storage, Managed Identity
//   - ai: AI Services, AI Foundry Project, Monitoring
//   - apps: Container Apps Environment + Apps
//   - all: Deploy everything (default)
//
// Usage:
//   # Deploy specific stage
//   ./deploy.sh dev loan-defenders-dev-rg --stage foundation
//
//   # Deploy everything (default)
//   ./deploy.sh dev loan-defenders-dev-rg
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

@description('Deployment stage (foundation, security, ai, apps, all)')
@allowed([
  'foundation'
  'security'
  'ai'
  'apps'
  'all'
])
param deploymentStage string = 'all'

@description('VNet name')
param vnetName string = 'loan-defenders-${environment}-vnet'

@description('VNet address space')
param vnetAddressPrefix string = '10.0.0.0/16'

@description('Container Apps subnet prefix')
param containerAppsSubnetPrefix string = '10.0.1.0/23'

@description('APIM subnet prefix')
param apimSubnetPrefix string = '10.0.3.0/24'

@description('Private Endpoints subnet prefix')
param privateEndpointsSubnetPrefix string = '10.0.4.0/24'

// ==============================================================================
// Variables
// ==============================================================================

var commonTags = {
  environment: environment
  project: 'loan-defenders'
  managedBy: 'bicep'
  deploymentStage: deploymentStage
}

// Stage enablement flags
var deployFoundation = deploymentStage == 'foundation' || deploymentStage == 'all'
var deploySecurity = deploymentStage == 'security' || deploymentStage == 'all'
var deployAI = deploymentStage == 'ai' || deploymentStage == 'all'
var deployApps = deploymentStage == 'apps' || deploymentStage == 'all'

// ==============================================================================
// Stage 1: Foundation (VNet, NSGs, Private DNS zones)
// ==============================================================================

module foundation 'modules/foundation.bicep' = if (deployFoundation) {
  name: 'foundation-deployment'
  params: {
    location: location
    environment: environment
    vnetName: vnetName
    vnetAddressPrefix: vnetAddressPrefix
    containerAppsSubnetPrefix: containerAppsSubnetPrefix
    apimSubnetPrefix: apimSubnetPrefix
    privateEndpointsSubnetPrefix: privateEndpointsSubnetPrefix
    deployPrivateEndpoints: false // Private endpoints created by security/ai stages
    tags: commonTags
  }
}

// ==============================================================================
// Stage 2: Security (Key Vault, Storage, Managed Identity)
// ==============================================================================

// Reference existing VNet for security stage (if foundation not deployed)
resource existingVnet 'Microsoft.Network/virtualNetworks@2023-05-01' existing = if (!deployFoundation && deploySecurity) {
  name: vnetName
}

module security 'modules/security.bicep' = if (deploySecurity) {
  name: 'security-deployment'
  params: {
    location: location
    environment: environment
    vnetId: deployFoundation ? foundation.outputs.vnetId : existingVnet.id
    privateEndpointsSubnetId: deployFoundation ? foundation.outputs.privateEndpointsSubnetId : existingVnet.properties.subnets[2].id
    keyVaultDnsZoneId: deployFoundation ? foundation.outputs.keyVaultDnsZoneId : resourceId('Microsoft.Network/privateDnsZones', 'privatelink.vaultcore.azure.net')
    blobDnsZoneId: deployFoundation ? foundation.outputs.blobDnsZoneId : resourceId('Microsoft.Network/privateDnsZones', 'privatelink.blob.core.windows.net')
    tags: commonTags
  }
}

// ==============================================================================
// Stage 3: AI Services (Azure AI Services, AI Foundry, Monitoring)
// ==============================================================================

resource existingVnetForAI 'Microsoft.Network/virtualNetworks@2023-05-01' existing = if (!deployFoundation && deployAI) {
  name: vnetName
}

resource existingManagedIdentity 'Microsoft.ManagedIdentity/userAssignedIdentities@2023-01-31' existing = if (!deploySecurity && deployAI) {
  name: 'loan-defenders-${environment}-id'
}

module ai 'modules/ai.bicep' = if (deployAI) {
  name: 'ai-deployment'
  params: {
    location: location
    environment: environment
    privateEndpointsSubnetId: deployFoundation ? foundation.outputs.privateEndpointsSubnetId : existingVnetForAI.properties.subnets[2].id
    aiServicesDnsZoneId: deployFoundation ? foundation.outputs.aiServicesDnsZoneId : resourceId('Microsoft.Network/privateDnsZones', 'privatelink.cognitiveservices.azure.com')
    monitorDnsZoneId: deployFoundation ? foundation.outputs.monitorDnsZoneId : resourceId('Microsoft.Network/privateDnsZones', 'privatelink.monitor.azure.com')
    aiFoundryDnsZoneId: deployFoundation ? foundation.outputs.aiFoundryDnsZoneId : resourceId('Microsoft.Network/privateDnsZones', 'privatelink.api.azureml.ms')
    managedIdentityPrincipalId: deploySecurity ? security.outputs.managedIdentityPrincipalId : existingManagedIdentity.properties.principalId
    tags: commonTags
  }
}

// ==============================================================================
// Stage 4: Container Apps (Environment + Apps)
// ==============================================================================

resource existingVnetForApps 'Microsoft.Network/virtualNetworks@2023-05-01' existing = if (!deployFoundation && deployApps) {
  name: vnetName
}

resource existingLogAnalytics 'Microsoft.OperationalInsights/workspaces@2023-09-01' existing = if (!deployAI && deployApps) {
  name: 'loan-defenders-${environment}-logs'
}

resource existingAppInsights 'Microsoft.Insights/components@2020-02-02' existing = if (!deployAI && deployApps) {
  name: 'loan-defenders-${environment}-appinsights'
}

resource existingManagedIdentityForApps 'Microsoft.ManagedIdentity/userAssignedIdentities@2023-01-31' existing = if (!deploySecurity && deployApps) {
  name: 'loan-defenders-${environment}-id'
}

resource existingKeyVault 'Microsoft.KeyVault/vaults@2023-07-01' existing = if (!deploySecurity && deployApps) {
  name: 'loan-defenders-${environment}-kv'
}

resource existingAIProject 'Microsoft.MachineLearningServices/workspaces@2024-04-01' existing = if (!deployAI && deployApps) {
  name: 'loan-defenders-${environment}-aiproject'
}

module apps 'modules/apps.bicep' = if (deployApps) {
  name: 'apps-deployment'
  params: {
    location: location
    environment: environment
    containerAppsSubnetId: deployFoundation ? foundation.outputs.containerAppsSubnetId : existingVnetForApps.properties.subnets[0].id
    logAnalyticsId: deployAI ? ai.outputs.logAnalyticsId : existingLogAnalytics.id
    appInsightsConnectionString: deployAI ? ai.outputs.appInsightsConnectionString : existingAppInsights.properties.ConnectionString
    managedIdentityId: deploySecurity ? security.outputs.managedIdentityId : existingManagedIdentityForApps.id
    keyVaultUri: deploySecurity ? security.outputs.keyVaultUri : existingKeyVault.properties.vaultUri
    aiFoundryProjectEndpoint: deployAI ? 'https://${ai.outputs.aiFoundryProjectName}.api.azureml.ms' : 'https://${existingAIProject.name}.api.azureml.ms'
    tags: commonTags
  }
}

// ==============================================================================
// Outputs
// ==============================================================================

@description('Deployment stage executed')
output deploymentStage string = deploymentStage

@description('Environment deployed')
output environment string = environment

// Foundation outputs
@description('VNet resource ID')
output vnetId string = deployFoundation ? foundation.outputs.vnetId : ''

@description('VNet name')
output vnetName string = deployFoundation ? foundation.outputs.vnetName : vnetName

// Security outputs
@description('Key Vault URI')
output keyVaultUri string = deploySecurity ? security.outputs.keyVaultUri : ''

@description('Managed Identity client ID')
output managedIdentityClientId string = deploySecurity ? security.outputs.managedIdentityClientId : ''

// AI outputs
@description('Application Insights connection string')
@secure()
output appInsightsConnectionString string = deployAI ? ai.outputs.appInsightsConnectionString : ''

@description('AI Foundry Project name')
output aiFoundryProjectName string = deployAI ? ai.outputs.aiFoundryProjectName : ''

// Apps outputs
@description('API app FQDN')
output apiAppFqdn string = deployApps ? apps.outputs.apiAppFqdn : ''

@description('UI app FQDN')
output uiAppFqdn string = deployApps ? apps.outputs.uiAppFqdn : ''

@description('Deployment complete')
output deploymentComplete bool = true
