// ==============================================================================
// AI Services Module - Azure Verified Modules
// ==============================================================================
// AI Services, Log Analytics, and Application Insights
//
// Resources:
//   - 1x Log Analytics Workspace
//   - 1x Application Insights
//   - 1x Cognitive Services Account (multi-service AI)
//
// AVM Modules:
//   - avm/res/operational-insights/workspace:0.12.0
//   - avm/res/insights/component:0.6.0
//   - avm/res/cognitive-services/account:0.13.2
// ==============================================================================

targetScope = 'resourceGroup'

// ==============================================================================
// Parameters
// ==============================================================================

@description('Azure region for resources')
param location string = resourceGroup().location

@description('Environment name (dev, staging, prod)')
param environment string

@description('Log Analytics Workspace name')
param logAnalyticsName string

@description('Application Insights name')
param appInsightsName string

@description('AI Services name')
param aiServicesName string

@description('Common tags for all resources')
param tags object

// ==============================================================================
// Log Analytics Workspace
// ==============================================================================

module logAnalytics 'br/public:avm/res/operational-insights/workspace:0.12.0' = {
  name: 'loganalytics-deployment'
  params: {
    name: logAnalyticsName
    location: location
    tags: tags

    skuName: 'PerGB2018'
    dataRetention: 30
  }
}

// ==============================================================================
// Application Insights
// ==============================================================================

module appInsights 'br/public:avm/res/insights/component:0.6.0' = {
  name: 'appinsights-deployment'
  params: {
    name: appInsightsName
    location: location
    tags: tags

    kind: 'web'
    workspaceResourceId: logAnalytics.outputs.resourceId
  }
}

// ==============================================================================
// AI Services (Cognitive Services)
// ==============================================================================

module aiServices 'br/public:avm/res/cognitive-services/account:0.13.2' = {
  name: 'aiservices-deployment'
  params: {
    name: aiServicesName
    location: location
    tags: tags

    kind: 'CognitiveServices'
    sku: 'S0'
    customSubDomainName: aiServicesName
    publicNetworkAccess: 'Disabled'

    networkAcls: {
      defaultAction: 'Deny'
      bypass: 'AzureServices'
    }
  }
}

// ==============================================================================
// Outputs
// ==============================================================================

@description('Log Analytics Workspace resource ID')
output logAnalyticsId string = logAnalytics.outputs.resourceId

@description('Log Analytics Workspace name')
output logAnalyticsName string = logAnalytics.outputs.name

@description('Log Analytics primary shared key')
output logAnalyticsPrimarySharedKey string = logAnalytics.outputs.primarySharedKey

@description('Log Analytics customer ID')
output logAnalyticsCustomerId string = logAnalytics.outputs.logAnalyticsWorkspaceId

@description('Application Insights resource ID')
output appInsightsId string = appInsights.outputs.resourceId

@description('Application Insights name')
output appInsightsName string = appInsights.outputs.name

@description('Application Insights instrumentation key')
output appInsightsInstrumentationKey string = appInsights.outputs.instrumentationKey

@description('Application Insights connection string')
output appInsightsConnectionString string = appInsights.outputs.connectionString

@description('AI Services resource ID')
output aiServicesId string = aiServices.outputs.resourceId

@description('AI Services name')
output aiServicesName string = aiServices.outputs.name

@description('AI Services endpoint')
output aiServicesEndpoint string = aiServices.outputs.endpoint
