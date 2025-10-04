// ==============================================================================
// Main Infrastructure Deployment - Loan Defenders (Azure Verified Modules)
// ==============================================================================
// Microsoft-verified modules for production-ready infrastructure
//
// Stages:
//   - foundation: VNet, NSGs, Private DNS zones
//   - security: Key Vault, Storage, Managed Identity
//   - ai: AI Services, AI Foundry Project, Monitoring
//   - apps: Container Apps Environment + Apps
//   - all: Deploy everything (default)
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
// Stage 1: Foundation - NSGs (must be created before VNet)
// ==============================================================================

// NSG for Container Apps
module nsgContainerApps 'br/public:avm/res/network/network-security-group:0.5.1' = if (deployFoundation) {
  name: 'nsg-container-apps-${deploymentStage}'
  params: {
    name: '${vnetName}-container-apps-nsg'
    location: location
    tags: commonTags

    securityRules: [
      // Inbound rules
      {
        name: 'AllowAPIMInbound'
        properties: {
          description: 'Allow HTTPS from APIM subnet'
          protocol: 'Tcp'
          sourcePortRange: '*'
          destinationPortRange: '443'
          sourceAddressPrefix: apimSubnetPrefix
          destinationAddressPrefix: containerAppsSubnetPrefix
          access: 'Allow'
          priority: 100
          direction: 'Inbound'
        }
      }
      {
        name: 'AllowContainerAppsInternalInbound'
        properties: {
          description: 'Allow internal communication (health probes, Dapr)'
          protocol: 'Tcp'
          sourcePortRange: '*'
          destinationPortRanges: ['443', '8080', '3500']
          sourceAddressPrefix: containerAppsSubnetPrefix
          destinationAddressPrefix: containerAppsSubnetPrefix
          access: 'Allow'
          priority: 105
          direction: 'Inbound'
        }
      }
      {
        name: 'AllowContainerAppsPlatformInbound'
        properties: {
          description: 'Allow Container Apps platform management'
          protocol: '*'
          sourcePortRange: '*'
          destinationPortRanges: ['1194', '9000']
          sourceAddressPrefix: 'AzureCloud'
          destinationAddressPrefix: containerAppsSubnetPrefix
          access: 'Allow'
          priority: 110
          direction: 'Inbound'
        }
      }
      {
        name: 'DenyAllInbound'
        properties: {
          description: 'Deny all other inbound traffic'
          protocol: '*'
          sourcePortRange: '*'
          destinationPortRange: '*'
          sourceAddressPrefix: '*'
          destinationAddressPrefix: '*'
          access: 'Deny'
          priority: 4096
          direction: 'Inbound'
        }
      }
      // Outbound rules
      {
        name: 'AllowPrivateEndpointsOutbound'
        properties: {
          description: 'Allow access to Azure services via private endpoints'
          protocol: 'Tcp'
          sourcePortRange: '*'
          destinationPortRange: '443'
          sourceAddressPrefix: containerAppsSubnetPrefix
          destinationAddressPrefix: privateEndpointsSubnetPrefix
          access: 'Allow'
          priority: 100
          direction: 'Outbound'
        }
      }
      {
        name: 'AllowAzureMonitorOutbound'
        properties: {
          description: 'Allow telemetry to Azure Monitor'
          protocol: 'Tcp'
          sourcePortRange: '*'
          destinationPortRange: '443'
          sourceAddressPrefix: containerAppsSubnetPrefix
          destinationAddressPrefix: 'AzureMonitor'
          access: 'Allow'
          priority: 110
          direction: 'Outbound'
        }
      }
      {
        name: 'AllowContainerRegistryOutbound'
        properties: {
          description: 'Allow container image pull'
          protocol: 'Tcp'
          sourcePortRange: '*'
          destinationPortRange: '443'
          sourceAddressPrefix: containerAppsSubnetPrefix
          destinationAddressPrefix: 'AzureContainerRegistry'
          access: 'Allow'
          priority: 120
          direction: 'Outbound'
        }
      }
      {
        name: 'DenyAllOutbound'
        properties: {
          description: 'Deny all other outbound traffic'
          protocol: '*'
          sourcePortRange: '*'
          destinationPortRange: '*'
          sourceAddressPrefix: '*'
          destinationAddressPrefix: '*'
          access: 'Deny'
          priority: 4096
          direction: 'Outbound'
        }
      }
    ]
  }
}

// NSG for APIM
module nsgApim 'br/public:avm/res/network/network-security-group:0.5.1' = if (deployFoundation) {
  name: 'nsg-apim-${deploymentStage}'
  params: {
    name: '${vnetName}-apim-nsg'
    location: location
    tags: commonTags

    securityRules: [
      // Inbound rules
      {
        name: 'AllowHTTPSInbound'
        properties: {
          description: 'Allow HTTPS from internet'
          protocol: 'Tcp'
          sourcePortRange: '*'
          destinationPortRange: '443'
          sourceAddressPrefix: 'Internet'
          destinationAddressPrefix: apimSubnetPrefix
          access: 'Allow'
          priority: 100
          direction: 'Inbound'
        }
      }
      {
        name: 'AllowHTTPInbound'
        properties: {
          description: 'Allow HTTP for redirect to HTTPS'
          protocol: 'Tcp'
          sourcePortRange: '*'
          destinationPortRange: '80'
          sourceAddressPrefix: 'Internet'
          destinationAddressPrefix: apimSubnetPrefix
          access: 'Allow'
          priority: 105
          direction: 'Inbound'
        }
      }
      {
        name: 'AllowAPIMManagementInbound'
        properties: {
          description: 'Allow APIM management endpoint'
          protocol: 'Tcp'
          sourcePortRange: '*'
          destinationPortRange: '3443'
          sourceAddressPrefix: 'ApiManagement'
          destinationAddressPrefix: apimSubnetPrefix
          access: 'Allow'
          priority: 110
          direction: 'Inbound'
        }
      }
      {
        name: 'AllowAPIMHealthProbeInbound'
        properties: {
          description: 'Allow APIM health probe from Azure Load Balancer'
          protocol: 'Tcp'
          sourcePortRange: '*'
          destinationPortRange: '6390'
          sourceAddressPrefix: 'AzureLoadBalancer'
          destinationAddressPrefix: apimSubnetPrefix
          access: 'Allow'
          priority: 120
          direction: 'Inbound'
        }
      }
      {
        name: 'DenyAllInbound'
        properties: {
          description: 'Deny all other inbound traffic'
          protocol: '*'
          sourcePortRange: '*'
          destinationPortRange: '*'
          sourceAddressPrefix: '*'
          destinationAddressPrefix: '*'
          access: 'Deny'
          priority: 4096
          direction: 'Inbound'
        }
      }
      // Outbound rules
      {
        name: 'AllowContainerAppsOutbound'
        properties: {
          description: 'Allow HTTPS to Container Apps'
          protocol: 'Tcp'
          sourcePortRange: '*'
          destinationPortRange: '443'
          sourceAddressPrefix: apimSubnetPrefix
          destinationAddressPrefix: containerAppsSubnetPrefix
          access: 'Allow'
          priority: 100
          direction: 'Outbound'
        }
      }
      {
        name: 'AllowAPIMDependenciesOutbound'
        properties: {
          description: 'Allow APIM dependencies (Storage, Event Hub, SQL)'
          protocol: 'Tcp'
          sourcePortRange: '*'
          destinationPortRanges: ['443', '1433', '5671', '5672', '12000-12003']
          sourceAddressPrefix: apimSubnetPrefix
          destinationAddressPrefix: 'AzureCloud'
          access: 'Allow'
          priority: 110
          direction: 'Outbound'
        }
      }
      {
        name: 'DenyAllOutbound'
        properties: {
          description: 'Deny all other outbound traffic'
          protocol: '*'
          sourcePortRange: '*'
          destinationPortRange: '*'
          sourceAddressPrefix: '*'
          destinationAddressPrefix: '*'
          access: 'Deny'
          priority: 4096
          direction: 'Outbound'
        }
      }
    ]
  }
}

// NSG for Private Endpoints
module nsgPrivateEndpoints 'br/public:avm/res/network/network-security-group:0.5.1' = if (deployFoundation) {
  name: 'nsg-private-endpoints-${deploymentStage}'
  params: {
    name: '${vnetName}-private-endpoints-nsg'
    location: location
    tags: commonTags

    securityRules: [
      {
        name: 'AllowVNetInbound'
        properties: {
          description: 'Allow access from VNet subnets'
          protocol: 'Tcp'
          sourcePortRange: '*'
          destinationPortRange: '443'
          sourceAddressPrefix: 'VirtualNetwork'
          destinationAddressPrefix: privateEndpointsSubnetPrefix
          access: 'Allow'
          priority: 100
          direction: 'Inbound'
        }
      }
      {
        name: 'DenyAllInbound'
        properties: {
          description: 'Deny all other inbound'
          protocol: '*'
          sourcePortRange: '*'
          destinationPortRange: '*'
          sourceAddressPrefix: '*'
          destinationAddressPrefix: '*'
          access: 'Deny'
          priority: 4096
          direction: 'Inbound'
        }
      }
    ]
  }
}

// ==============================================================================
// Stage 1: Foundation - VNet with Subnets
// ==============================================================================

module vnet 'br/public:avm/res/network/virtual-network:0.7.1' = if (deployFoundation) {
  name: 'vnet-deployment-${deploymentStage}'
  params: {
    name: vnetName
    location: location
    addressPrefixes: [vnetAddressPrefix]
    tags: commonTags

    subnets: [
      // Container Apps Subnet
      {
        name: 'container-apps-subnet'
        addressPrefix: containerAppsSubnetPrefix
        delegation: 'Microsoft.App/environments'
        networkSecurityGroupResourceId: deployFoundation ? nsgContainerApps.outputs.resourceId : ''
      }
      // APIM Subnet
      {
        name: 'apim-subnet'
        addressPrefix: apimSubnetPrefix
        networkSecurityGroupResourceId: deployFoundation ? nsgApim.outputs.resourceId : ''
      }
      // Private Endpoints Subnet
      {
        name: 'private-endpoints-subnet'
        addressPrefix: privateEndpointsSubnetPrefix
        privateEndpointNetworkPolicies: 'Disabled'
        networkSecurityGroupResourceId: deployFoundation ? nsgPrivateEndpoints.outputs.resourceId : ''
      }
    ]
  }
  dependsOn: [
    nsgContainerApps
    nsgApim
    nsgPrivateEndpoints
  ]
}

// ==============================================================================
// Stage 2: Security - Key Vault, Storage, Managed Identity
// ==============================================================================

// Managed Identity (native resource, no AVM module yet)
resource managedIdentity 'Microsoft.ManagedIdentity/userAssignedIdentities@2023-01-31' = if (deploySecurity) {
  name: managedIdentityName
  location: location
  tags: commonTags
}

// Key Vault
module keyVault 'br/public:avm/res/key-vault/vault:0.13.3' = if (deploySecurity) {
  name: 'keyvault-deployment-${deploymentStage}'
  params: {
    name: keyVaultName
    location: location
    tags: commonTags

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

// Storage Account
module storageAccount 'br/public:avm/res/storage/storage-account:0.27.1' = if (deploySecurity) {
  name: 'storage-deployment-${deploymentStage}'
  params: {
    name: storageAccountName
    location: location
    tags: commonTags

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
// Stage 3: AI - AI Services, Log Analytics, Application Insights
// ==============================================================================

// Log Analytics Workspace
module logAnalytics 'br/public:avm/res/operational-insights/workspace:0.12.0' = if (deployAI) {
  name: 'loganalytics-deployment-${deploymentStage}'
  params: {
    name: logAnalyticsName
    location: location
    tags: commonTags

    skuName: 'PerGB2018'
    dataRetention: 30
  }
}

// Application Insights
module appInsights 'br/public:avm/res/insights/component:0.6.0' = if (deployAI) {
  name: 'appinsights-deployment-${deploymentStage}'
  params: {
    name: appInsightsName
    location: location
    tags: commonTags

    kind: 'web'
    workspaceResourceId: deployAI ? logAnalytics.outputs.resourceId : ''
  }
}

// AI Services (Cognitive Services)
module aiServices 'br/public:avm/res/cognitive-services/account:0.13.2' = if (deployAI) {
  name: 'aiservices-deployment-${deploymentStage}'
  params: {
    name: aiServicesName
    location: location
    tags: commonTags

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
// Stage 4: Apps - Container Apps Environment
// ==============================================================================

// Note: Container Apps Environment doesn't have an AVM module yet (as of Jan 2025)
// Using native resource for now, will migrate when AVM module is available
resource containerAppsEnv 'Microsoft.App/managedEnvironments@2024-03-01' = if (deployApps) {
  name: containerAppsEnvName
  location: location
  tags: commonTags
  properties: {
    vnetConfiguration: {
      infrastructureSubnetId: deployFoundation ? vnet.outputs.subnetResourceIds[0] : ''
      internal: true
    }
    appLogsConfiguration: {
      destination: 'log-analytics'
      logAnalyticsConfiguration: {
        customerId: deployAI ? reference(logAnalytics.outputs.resourceId, '2023-09-01').customerId : ''
        sharedKey: deployAI ? logAnalytics.outputs.primarySharedKey : ''
      }
    }
  }
  dependsOn: [
    vnet
    logAnalytics
  ]
}

// ==============================================================================
// Outputs
// ==============================================================================

@description('VNet resource ID')
output vnetId string = deployFoundation ? vnet.outputs.resourceId : ''

@description('Container Apps subnet ID')
output containerAppsSubnetId string = deployFoundation ? vnet.outputs.subnetResourceIds[0] : ''

@description('APIM subnet ID')
output apimSubnetId string = deployFoundation ? vnet.outputs.subnetResourceIds[1] : ''

@description('Private endpoints subnet ID')
output privateEndpointsSubnetId string = deployFoundation ? vnet.outputs.subnetResourceIds[2] : ''

@description('Key Vault resource ID')
output keyVaultId string = deploySecurity ? keyVault.outputs.resourceId : ''

@description('Storage Account resource ID')
output storageAccountId string = deploySecurity ? storageAccount.outputs.resourceId : ''

@description('Managed Identity resource ID')
output managedIdentityId string = deploySecurity ? managedIdentity.id : ''

@description('Managed Identity client ID')
output managedIdentityClientId string = deploySecurity ? managedIdentity.properties.clientId : ''

@description('Log Analytics Workspace resource ID')
output logAnalyticsId string = deployAI ? logAnalytics.outputs.resourceId : ''

@description('Application Insights resource ID')
output appInsightsId string = deployAI ? appInsights.outputs.resourceId : ''

@description('AI Services resource ID')
output aiServicesId string = deployAI ? aiServices.outputs.resourceId : ''

@description('Container Apps Environment resource ID')
output containerAppsEnvId string = deployApps ? containerAppsEnv.id : ''
