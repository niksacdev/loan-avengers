// ==============================================================================
// Container Apps Module - Loan Defenders
// ==============================================================================
// Stage 4: Application deployment (Container Apps Environment + Apps)
// Depends on: Foundation (VNet), Security (Managed Identity), AI (App Insights)
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

@description('Container Apps subnet ID (from foundation stage)')
param containerAppsSubnetId string

@description('Log Analytics workspace ID (from AI stage)')
param logAnalyticsId string

@description('Application Insights connection string (from AI stage)')
@secure()
param appInsightsConnectionString string

@description('Managed Identity resource ID (from security stage)')
param managedIdentityId string

@description('Key Vault URI (from security stage)')
param keyVaultUri string

@description('AI Foundry Project endpoint (from AI stage)')
param aiFoundryProjectEndpoint string

@description('Tags for resources')
param tags object

// ==============================================================================
// Variables
// ==============================================================================

var containerAppsEnvName = 'loan-defenders-${environment}-env'
var apiAppName = 'loan-defenders-${environment}-api'
var uiAppName = 'loan-defenders-${environment}-ui'
var mcpApplicationVerificationAppName = 'loan-defenders-${environment}-mcp-appverif'
var mcpDocumentProcessingAppName = 'loan-defenders-${environment}-mcp-docproc'
var mcpFinancialCalcAppName = 'loan-defenders-${environment}-mcp-fincalc'

// Container image settings (placeholder - update with actual images)
var apiImage = 'mcr.microsoft.com/azuredocs/containerapps-helloworld:latest' // TODO: Replace with actual API image
var uiImage = 'mcr.microsoft.com/azuredocs/containerapps-helloworld:latest'  // TODO: Replace with actual UI image
var mcpImage = 'mcr.microsoft.com/azuredocs/containerapps-helloworld:latest' // TODO: Replace with actual MCP image

// ==============================================================================
// Container Apps Environment (VNet-integrated)
// ==============================================================================

resource containerAppsEnv 'Microsoft.App/managedEnvironments@2024-03-01' = {
  name: containerAppsEnvName
  location: location
  tags: tags
  properties: {
    vnetConfiguration: {
      infrastructureSubnetId: containerAppsSubnetId
      internal: true // Internal environment (not exposed to internet)
    }
    appLogsConfiguration: {
      destination: 'log-analytics'
      logAnalyticsConfiguration: {
        customerId: reference(logAnalyticsId, '2023-09-01').customerId
        sharedKey: listKeys(logAnalyticsId, '2023-09-01').primarySharedKey
      }
    }
    zoneRedundant: false // Set to true for production
  }
}

// ==============================================================================
// API Container App (FastAPI backend)
// ==============================================================================

resource apiApp 'Microsoft.App/containerApps@2024-03-01' = {
  name: apiAppName
  location: location
  tags: tags
  identity: {
    type: 'UserAssigned'
    userAssignedIdentities: {
      '${managedIdentityId}': {}
    }
  }
  properties: {
    environmentId: containerAppsEnv.id
    configuration: {
      ingress: {
        external: false // Internal only (accessed via APIM)
        targetPort: 8000
        transport: 'http'
        allowInsecure: false
      }
      secrets: [
        {
          name: 'appinsights-connection-string'
          value: appInsightsConnectionString
        }
      ]
    }
    template: {
      containers: [
        {
          name: 'api'
          image: apiImage
          resources: {
            cpu: json('0.5')
            memory: '1Gi'
          }
          env: [
            {
              name: 'APPLICATIONINSIGHTS_CONNECTION_STRING'
              secretRef: 'appinsights-connection-string'
            }
            {
              name: 'AZURE_KEY_VAULT_URI'
              value: keyVaultUri
            }
            {
              name: 'AZURE_CLIENT_ID'
              value: reference(managedIdentityId, '2023-01-31').clientId
            }
            {
              name: 'AI_FOUNDRY_PROJECT_ENDPOINT'
              value: aiFoundryProjectEndpoint
            }
            {
              name: 'ENVIRONMENT'
              value: environment
            }
          ]
        }
      ]
      scale: {
        minReplicas: environment == 'prod' ? 2 : 1
        maxReplicas: environment == 'prod' ? 10 : 3
      }
    }
  }
}

// ==============================================================================
// UI Container App (React frontend)
// ==============================================================================

resource uiApp 'Microsoft.App/containerApps@2024-03-01' = {
  name: uiAppName
  location: location
  tags: tags
  properties: {
    environmentId: containerAppsEnv.id
    configuration: {
      ingress: {
        external: false // Internal only (accessed via APIM)
        targetPort: 3000
        transport: 'http'
        allowInsecure: false
      }
    }
    template: {
      containers: [
        {
          name: 'ui'
          image: uiImage
          resources: {
            cpu: json('0.25')
            memory: '0.5Gi'
          }
          env: [
            {
              name: 'API_URL'
              value: 'http://${apiApp.properties.configuration.ingress.fqdn}'
            }
            {
              name: 'ENVIRONMENT'
              value: environment
            }
          ]
        }
      ]
      scale: {
        minReplicas: environment == 'prod' ? 2 : 1
        maxReplicas: environment == 'prod' ? 5 : 2
      }
    }
  }
}

// ==============================================================================
// MCP Server Container Apps
// ==============================================================================

// MCP Application Verification Server
resource mcpApplicationVerificationApp 'Microsoft.App/containerApps@2024-03-01' = {
  name: mcpApplicationVerificationAppName
  location: location
  tags: tags
  identity: {
    type: 'UserAssigned'
    userAssignedIdentities: {
      '${managedIdentityId}': {}
    }
  }
  properties: {
    environmentId: containerAppsEnv.id
    configuration: {
      ingress: {
        external: false // Internal only (accessed by API)
        targetPort: 8010
        transport: 'http'
        allowInsecure: false
      }
    }
    template: {
      containers: [
        {
          name: 'mcp-appverif'
          image: mcpImage
          resources: {
            cpu: json('0.25')
            memory: '0.5Gi'
          }
          env: [
            {
              name: 'AZURE_CLIENT_ID'
              value: reference(managedIdentityId, '2023-01-31').clientId
            }
            {
              name: 'ENVIRONMENT'
              value: environment
            }
          ]
        }
      ]
      scale: {
        minReplicas: 1
        maxReplicas: 3
      }
    }
  }
}

// MCP Document Processing Server
resource mcpDocumentProcessingApp 'Microsoft.App/containerApps@2024-03-01' = {
  name: mcpDocumentProcessingAppName
  location: location
  tags: tags
  identity: {
    type: 'UserAssigned'
    userAssignedIdentities: {
      '${managedIdentityId}': {}
    }
  }
  properties: {
    environmentId: containerAppsEnv.id
    configuration: {
      ingress: {
        external: false
        targetPort: 8011
        transport: 'http'
        allowInsecure: false
      }
    }
    template: {
      containers: [
        {
          name: 'mcp-docproc'
          image: mcpImage
          resources: {
            cpu: json('0.25')
            memory: '0.5Gi'
          }
          env: [
            {
              name: 'AZURE_CLIENT_ID'
              value: reference(managedIdentityId, '2023-01-31').clientId
            }
            {
              name: 'ENVIRONMENT'
              value: environment
            }
          ]
        }
      ]
      scale: {
        minReplicas: 1
        maxReplicas: 3
      }
    }
  }
}

// MCP Financial Calculations Server
resource mcpFinancialCalcApp 'Microsoft.App/containerApps@2024-03-01' = {
  name: mcpFinancialCalcAppName
  location: location
  tags: tags
  identity: {
    type: 'UserAssigned'
    userAssignedIdentities: {
      '${managedIdentityId}': {}
    }
  }
  properties: {
    environmentId: containerAppsEnv.id
    configuration: {
      ingress: {
        external: false
        targetPort: 8012
        transport: 'http'
        allowInsecure: false
      }
    }
    template: {
      containers: [
        {
          name: 'mcp-fincalc'
          image: mcpImage
          resources: {
            cpu: json('0.25')
            memory: '0.5Gi'
          }
          env: [
            {
              name: 'AZURE_CLIENT_ID'
              value: reference(managedIdentityId, '2023-01-31').clientId
            }
            {
              name: 'ENVIRONMENT'
              value: environment
            }
          ]
        }
      ]
      scale: {
        minReplicas: 1
        maxReplicas: 3
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

@description('API app FQDN')
output apiAppFqdn string = apiApp.properties.configuration.ingress.fqdn

@description('UI app FQDN')
output uiAppFqdn string = uiApp.properties.configuration.ingress.fqdn

@description('MCP Application Verification FQDN')
output mcpAppVerifFqdn string = mcpApplicationVerificationApp.properties.configuration.ingress.fqdn

@description('MCP Document Processing FQDN')
output mcpDocProcFqdn string = mcpDocumentProcessingApp.properties.configuration.ingress.fqdn

@description('MCP Financial Calc FQDN')
output mcpFinCalcFqdn string = mcpFinancialCalcApp.properties.configuration.ingress.fqdn

@description('Apps deployment complete')
output deploymentComplete bool = true
