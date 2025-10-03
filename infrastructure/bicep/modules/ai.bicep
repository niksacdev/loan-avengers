// ==============================================================================
// AI Services Module - Loan Defenders
// ==============================================================================
// Stage 3: AI services (Azure AI Services, AI Foundry Project, Monitoring)
// Depends on: Foundation (VNet, DNS), Security (Key Vault, Managed Identity)
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

@description('Private Endpoints subnet ID (from foundation stage)')
param privateEndpointsSubnetId string

@description('AI Services DNS Zone ID (from foundation stage)')
param aiServicesDnsZoneId string

@description('Monitor DNS Zone ID (from foundation stage)')
param monitorDnsZoneId string

@description('Azure AI Foundry DNS Zone ID (from foundation stage)')
param aiFoundryDnsZoneId string

@description('Managed Identity principal ID (from security stage)')
param managedIdentityPrincipalId string

@description('Tags for resources')
param tags object

// ==============================================================================
// Variables
// ==============================================================================

var aiServicesName = 'loan-defenders-${environment}-ai'
var logAnalyticsName = 'loan-defenders-${environment}-logs'
var appInsightsName = 'loan-defenders-${environment}-appinsights'
var aiFoundryHubName = 'loan-defenders-${environment}-aihub'
var aiFoundryProjectName = 'loan-defenders-${environment}-aiproject'

// ==============================================================================
// Log Analytics Workspace (required for App Insights)
// ==============================================================================

resource logAnalytics 'Microsoft.OperationalInsights/workspaces@2023-09-01' = {
  name: logAnalyticsName
  location: location
  tags: tags
  properties: {
    sku: {
      name: 'PerGB2018'
    }
    retentionInDays: 30
    publicNetworkAccessForIngestion: 'Enabled' // Required for data ingestion
    publicNetworkAccessForQuery: 'Enabled'
  }
}

// ==============================================================================
// Application Insights
// ==============================================================================

resource appInsights 'Microsoft.Insights/components@2020-02-02' = {
  name: appInsightsName
  location: location
  tags: tags
  kind: 'web'
  properties: {
    Application_Type: 'web'
    WorkspaceResourceId: logAnalytics.id
    publicNetworkAccessForIngestion: 'Enabled'
    publicNetworkAccessForQuery: 'Enabled'
  }
}

// ==============================================================================
// Azure AI Services (for Content Safety)
// ==============================================================================

resource aiServices 'Microsoft.CognitiveServices/accounts@2023-10-01-preview' = {
  name: aiServicesName
  location: location
  tags: tags
  kind: 'CognitiveServices' // Multi-service account
  sku: {
    name: 'S0' // Standard tier
  }
  properties: {
    customSubDomainName: aiServicesName
    publicNetworkAccess: 'Disabled' // Zero Trust - only private endpoint access
    networkAcls: {
      defaultAction: 'Deny'
      bypass: 'AzureServices'
    }
  }
  identity: {
    type: 'SystemAssigned'
  }
}

// Grant managed identity access to AI Services
resource aiServicesUser 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(aiServices.id, managedIdentityPrincipalId, 'Cognitive Services User')
  scope: aiServices
  properties: {
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', 'a97b65f3-24c7-4388-baec-2e87135dc908') // Cognitive Services User
    principalId: managedIdentityPrincipalId
    principalType: 'ServicePrincipal'
  }
}

// ==============================================================================
// Azure AI Foundry Hub (required for AI Foundry Projects)
// ==============================================================================

resource aiFoundryHub 'Microsoft.MachineLearningServices/workspaces@2024-04-01' = {
  name: aiFoundryHubName
  location: location
  tags: tags
  kind: 'hub' // AI Foundry Hub
  sku: {
    name: 'Basic'
    tier: 'Basic'
  }
  identity: {
    type: 'SystemAssigned'
  }
  properties: {
    friendlyName: 'Loan Defenders AI Hub'
    description: 'AI Foundry Hub for Loan Defenders multi-agent system'
    publicNetworkAccess: 'Disabled' // Zero Trust
  }
}

// ==============================================================================
// Azure AI Foundry Project (for GPT-4 deployment)
// ==============================================================================

resource aiFoundryProject 'Microsoft.MachineLearningServices/workspaces@2024-04-01' = {
  name: aiFoundryProjectName
  location: location
  tags: tags
  kind: 'project' // AI Foundry Project
  sku: {
    name: 'Basic'
    tier: 'Basic'
  }
  identity: {
    type: 'SystemAssigned'
  }
  properties: {
    friendlyName: 'Loan Defenders AI Project'
    description: 'AI Foundry Project for Loan Defenders agents with GPT-4'
    hubResourceId: aiFoundryHub.id
    publicNetworkAccess: 'Disabled' // Zero Trust
  }
}

// Grant managed identity access to AI Foundry Project
resource aiFoundryContributor 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(aiFoundryProject.id, managedIdentityPrincipalId, 'AzureML Data Scientist')
  scope: aiFoundryProject
  properties: {
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', 'f6c7c914-8db3-469d-8ca1-694a8f32e121') // AzureML Data Scientist
    principalId: managedIdentityPrincipalId
    principalType: 'ServicePrincipal'
  }
}

// ==============================================================================
// Private Endpoints
// ==============================================================================

// AI Services Private Endpoint
resource aiServicesPrivateEndpoint 'Microsoft.Network/privateEndpoints@2023-05-01' = {
  name: '${aiServicesName}-pe'
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
          privateLinkServiceId: aiServices.id
          groupIds: ['account']
        }
      }
    ]
  }
}

resource aiServicesDnsZoneGroup 'Microsoft.Network/privateEndpoints/privateDnsZoneGroups@2023-05-01' = {
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

// App Insights Private Endpoint
resource appInsightsPrivateEndpoint 'Microsoft.Network/privateEndpoints@2023-05-01' = {
  name: '${appInsightsName}-pe'
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
          privateLinkServiceId: appInsights.id
          groupIds: ['azuremonitor']
        }
      }
    ]
  }
}

resource appInsightsDnsZoneGroup 'Microsoft.Network/privateEndpoints/privateDnsZoneGroups@2023-05-01' = {
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

// AI Foundry Project Private Endpoint
resource aiFoundryPrivateEndpoint 'Microsoft.Network/privateEndpoints@2023-05-01' = {
  name: '${aiFoundryProjectName}-pe'
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
          privateLinkServiceId: aiFoundryProject.id
          groupIds: ['amlworkspace']
        }
      }
    ]
  }
}

resource aiFoundryDnsZoneGroup 'Microsoft.Network/privateEndpoints/privateDnsZoneGroups@2023-05-01' = {
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

@description('AI Services resource ID')
output aiServicesId string = aiServices.id

@description('AI Services name')
output aiServicesName string = aiServices.name

@description('AI Services endpoint')
output aiServicesEndpoint string = aiServices.properties.endpoint

@description('Application Insights resource ID')
output appInsightsId string = appInsights.id

@description('Application Insights name')
output appInsightsName string = appInsights.name

@description('Application Insights instrumentation key')
@secure()
output appInsightsInstrumentationKey string = appInsights.properties.InstrumentationKey

@description('Application Insights connection string')
@secure()
output appInsightsConnectionString string = appInsights.properties.ConnectionString

@description('Log Analytics workspace ID')
output logAnalyticsId string = logAnalytics.id

@description('Log Analytics workspace name')
output logAnalyticsName string = logAnalytics.name

@description('AI Foundry Hub resource ID')
output aiFoundryHubId string = aiFoundryHub.id

@description('AI Foundry Hub name')
output aiFoundryHubName string = aiFoundryHub.name

@description('AI Foundry Project resource ID')
output aiFoundryProjectId string = aiFoundryProject.id

@description('AI Foundry Project name')
output aiFoundryProjectName string = aiFoundryProject.name

@description('AI deployment complete')
output deploymentComplete bool = true
