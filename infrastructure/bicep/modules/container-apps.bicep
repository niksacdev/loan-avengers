// ==============================================================================
// Container Apps Module
// ==============================================================================
// Container Apps Environment with VNet integration and Log Analytics
//
// Resources:
//   - 1x Container Apps Environment (VNet-integrated, internal)
//
// Note: No AVM module available yet for Container Apps (as of Jan 2025)
//       Using native Azure resource
// ==============================================================================

targetScope = 'resourceGroup'

// ==============================================================================
// Parameters
// ==============================================================================

@description('Azure region for resources')
param location string = resourceGroup().location

@description('Environment name (dev, staging, prod)')
param environment string

@description('Container Apps Environment name')
param containerAppsEnvName string

@description('Container Apps subnet ID')
param containerAppsSubnetId string

@description('Log Analytics workspace customer ID')
param logAnalyticsCustomerId string

@description('Log Analytics workspace primary shared key')
@secure()
param logAnalyticsPrimarySharedKey string

@description('Common tags for all resources')
param tags object

// ==============================================================================
// Container Apps Environment
// ==============================================================================

resource containerAppsEnv 'Microsoft.App/managedEnvironments@2024-03-01' = {
  name: containerAppsEnvName
  location: location
  tags: tags
  properties: {
    vnetConfiguration: {
      infrastructureSubnetId: containerAppsSubnetId
      internal: true
    }
    appLogsConfiguration: {
      destination: 'log-analytics'
      logAnalyticsConfiguration: {
        customerId: logAnalyticsCustomerId
        sharedKey: logAnalyticsPrimarySharedKey
      }
    }
  }
}

// ==============================================================================
// Outputs
// ==============================================================================

@description('Container Apps Environment resource ID')
output containerAppsEnvId string = containerAppsEnv.id

@description('Container Apps Environment name')
output containerAppsEnvName string = containerAppsEnv.name

@description('Container Apps Environment default domain')
output containerAppsEnvDefaultDomain string = containerAppsEnv.properties.defaultDomain

@description('Container Apps Environment static IP')
output containerAppsEnvStaticIp string = containerAppsEnv.properties.staticIp
