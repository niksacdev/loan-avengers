// ==============================================================================
// Main Infrastructure Orchestrator - Loan Defenders (Azure Verified Modules)
// ==============================================================================
// Thin orchestrator that coordinates deployment of modular infrastructure
//
// Modules:
//   - networking.bicep     - VNet, NSGs, Subnets
//   - security.bicep       - Key Vault, Storage, Managed Identity
//   - ai-services.bicep    - AI Services, Log Analytics, App Insights
//   - container-apps.bicep - Container Apps Environment
//
// Deployment Stages:
//   - foundation: Networking (VNet, NSGs, subnets)
//   - security:   Security services (Key Vault, Storage, Identity)
//   - ai:         AI and monitoring services + RBAC permissions
//   - apps:       Container Apps Environment
//   - all:        Deploy everything (default)
//
// AVM Documentation: https://azure.github.io/Azure-Verified-Modules/
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

@description('VNet address prefix')
param vnetAddressPrefix string = '10.0.0.0/16'

@description('Container Apps subnet prefix')
param containerAppsSubnetPrefix string = '10.0.1.0/23'

@description('APIM subnet prefix')
param apimSubnetPrefix string = '10.0.3.0/24'

@description('Private endpoints subnet prefix')
param privateEndpointsSubnetPrefix string = '10.0.4.0/24'

// ==============================================================================
// Variables
// ==============================================================================

var vnetName = 'loan-defenders-${environment}-vnet'
var keyVaultName = 'kv-ldf-${environment}-${take(uniqueString(resourceGroup().id), 6)}'
var storageAccountName = 'stldf${environment}${take(uniqueString(resourceGroup().id), 10)}'
var managedIdentityName = 'loan-defenders-${environment}-identity'
var aiServicesName = 'loan-defenders-${environment}-ai'
var logAnalyticsName = 'loan-defenders-${environment}-logs'
var appInsightsName = 'loan-defenders-${environment}-insights'
var containerAppsEnvName = 'loan-defenders-${environment}-env'

var commonTags = {
  environment: environment
  project: 'loan-defenders'
  managedBy: 'bicep-avm'
  deploymentStage: deploymentStage
}

// Deployment stage conditions
var deployFoundation = deploymentStage == 'foundation' || deploymentStage == 'all'
var deploySecurity = deploymentStage == 'security' || deploymentStage == 'all'
var deployAI = deploymentStage == 'ai' || deploymentStage == 'all'
var deployApps = deploymentStage == 'apps' || deploymentStage == 'all'

// ==============================================================================
// Stage 1: Foundation - Networking
// ==============================================================================

module networking 'modules/networking.bicep' = if (deployFoundation) {
  name: 'networking-deployment-${deploymentStage}'
  params: {
    location: location
    environment: environment
    vnetName: vnetName
    vnetAddressPrefix: vnetAddressPrefix
    containerAppsSubnetPrefix: containerAppsSubnetPrefix
    apimSubnetPrefix: apimSubnetPrefix
    privateEndpointsSubnetPrefix: privateEndpointsSubnetPrefix
    tags: commonTags
  }
}

// ==============================================================================
// Stage 2: Security - Key Vault, Storage, Identity
// ==============================================================================

module security 'modules/security.bicep' = if (deploySecurity) {
  name: 'security-deployment-${deploymentStage}'
  params: {
    location: location
    environment: environment
    keyVaultName: keyVaultName
    storageAccountName: storageAccountName
    managedIdentityName: managedIdentityName
    tags: commonTags
  }
}

// ==============================================================================
// Stage 3: AI Services - AI, Log Analytics, App Insights
// ==============================================================================

module aiServices 'modules/ai-services.bicep' = if (deployAI) {
  name: 'ai-services-deployment-${deploymentStage}'
  params: {
    location: location
    environment: environment
    logAnalyticsName: logAnalyticsName
    appInsightsName: appInsightsName
    aiServicesName: aiServicesName
    tags: commonTags
  }
}

// ==============================================================================
// Stage 4: Apps - Container Apps Environment
// ==============================================================================

module containerApps 'modules/container-apps.bicep' = if (deployApps && deployFoundation && deployAI) {
  name: 'container-apps-deployment-${deploymentStage}'
  params: {
    location: location
    environment: environment
    containerAppsEnvName: containerAppsEnvName
    containerAppsSubnetId: networking!.outputs.containerAppsSubnetId
    logAnalyticsCustomerId: aiServices!.outputs.logAnalyticsCustomerId
    logAnalyticsPrimarySharedKey: aiServices!.outputs.logAnalyticsPrimarySharedKey
    tags: commonTags
  }
}

// ==============================================================================
// Stage 5: RBAC - Role Assignments for Azure AI Foundry
// ==============================================================================

// RBAC can only be deployed when both security and AI modules exist
module rbac 'modules/rbac.bicep' = if (deploySecurity && deployAI) {
  name: 'rbac-deployment-${deploymentStage}'
  params: {
    managedIdentityPrincipalId: security!.outputs.managedIdentityPrincipalId
    aiServicesId: aiServices!.outputs.aiServicesId
    keyVaultId: security!.outputs.keyVaultId
    storageAccountId: security!.outputs.storageAccountId
  }
}

// ==============================================================================
// Outputs
// ==============================================================================

// Networking Outputs (only if foundation was deployed)
@description('VNet resource ID')
output vnetId string = deployFoundation ? networking!.outputs.vnetId : ''

@description('Container Apps subnet ID')
output containerAppsSubnetId string = deployFoundation ? networking!.outputs.containerAppsSubnetId : ''

@description('APIM subnet ID')
output apimSubnetId string = deployFoundation ? networking!.outputs.apimSubnetId : ''

@description('Private endpoints subnet ID')
output privateEndpointsSubnetId string = deployFoundation ? networking!.outputs.privateEndpointsSubnetId : ''

// Security Outputs (only if security was deployed)
@description('Key Vault resource ID')
output keyVaultId string = deploySecurity ? security!.outputs.keyVaultId : ''

@description('Storage Account resource ID')
output storageAccountId string = deploySecurity ? security!.outputs.storageAccountId : ''

@description('Managed Identity resource ID')
output managedIdentityId string = deploySecurity ? security!.outputs.managedIdentityId : ''

@description('Managed Identity client ID')
output managedIdentityClientId string = deploySecurity ? security!.outputs.managedIdentityClientId : ''

// AI Services Outputs (only if AI was deployed)
@description('Log Analytics Workspace resource ID')
output logAnalyticsId string = deployAI ? aiServices!.outputs.logAnalyticsId : ''

@description('Application Insights resource ID')
output appInsightsId string = deployAI ? aiServices!.outputs.appInsightsId : ''

@description('AI Services resource ID')
output aiServicesId string = deployAI ? aiServices!.outputs.aiServicesId : ''

// Container Apps Outputs (only if apps was deployed)
@description('Container Apps Environment resource ID')
output containerAppsEnvId string = (deployApps && deployFoundation && deployAI) ? containerApps!.outputs.containerAppsEnvId : ''
