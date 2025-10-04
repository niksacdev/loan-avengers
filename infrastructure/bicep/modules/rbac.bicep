// ==============================================================================
// RBAC Module - Role Assignments for Azure AI Foundry
// ==============================================================================
// Configures role-based access control between resources
//
// Role Assignments:
//   1. Managed Identity → AI Services (Cognitive Services User)
//   2. Managed Identity → Key Vault (Key Vault Secrets User)
//   3. Managed Identity → Storage Account (Storage Blob Data Contributor)
//   4. AI Services → Storage Account (Storage Blob Data Contributor)
//
// Built-in Role IDs:
//   - Cognitive Services User: a97b65f3-24c7-4388-baec-2e87135dc908
//   - Key Vault Secrets User: 4633458b-17de-408a-b874-0445c86b69e6
//   - Storage Blob Data Contributor: ba92f5b4-2d11-453d-a403-e96b0029c9fe
// ==============================================================================

targetScope = 'resourceGroup'

// ==============================================================================
// Parameters
// ==============================================================================

@description('Managed Identity principal ID')
param managedIdentityPrincipalId string

@description('AI Services resource ID')
param aiServicesId string

@description('Key Vault resource ID')
param keyVaultId string

@description('Storage Account resource ID')
param storageAccountId string

// ==============================================================================
// Built-in Role Definition IDs
// ==============================================================================

var cognitiveServicesUserRoleId = 'a97b65f3-24c7-4388-baec-2e87135dc908'
var keyVaultSecretsUserRoleId = '4633458b-17de-408a-b874-0445c86b69e6'
var storageBlobDataContributorRoleId = 'ba92f5b4-2d11-453d-a403-e96b0029c9fe'

// ==============================================================================
// Role Assignment: Managed Identity → AI Services
// ==============================================================================

resource aiServicesRoleAssignment 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(managedIdentityPrincipalId, aiServicesId, cognitiveServicesUserRoleId)
  scope: resourceGroup()
  properties: {
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', cognitiveServicesUserRoleId)
    principalId: managedIdentityPrincipalId
    principalType: 'ServicePrincipal'
    description: 'Allow Managed Identity to use AI Services (Cognitive Services User)'
  }
}

// ==============================================================================
// Role Assignment: Managed Identity → Key Vault
// ==============================================================================

resource keyVaultRoleAssignment 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(managedIdentityPrincipalId, keyVaultId, keyVaultSecretsUserRoleId)
  scope: resourceGroup()
  properties: {
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', keyVaultSecretsUserRoleId)
    principalId: managedIdentityPrincipalId
    principalType: 'ServicePrincipal'
    description: 'Allow Managed Identity to read secrets from Key Vault'
  }
}

// ==============================================================================
// Role Assignment: Managed Identity → Storage Account
// ==============================================================================

resource storageRoleAssignment 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(managedIdentityPrincipalId, storageAccountId, storageBlobDataContributorRoleId)
  scope: resourceGroup()
  properties: {
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', storageBlobDataContributorRoleId)
    principalId: managedIdentityPrincipalId
    principalType: 'ServicePrincipal'
    description: 'Allow Managed Identity to read/write blobs in Storage Account'
  }
}

// ==============================================================================
// Outputs
// ==============================================================================

@description('AI Services role assignment ID')
output aiServicesRoleAssignmentId string = aiServicesRoleAssignment.id

@description('Key Vault role assignment ID')
output keyVaultRoleAssignmentId string = keyVaultRoleAssignment.id

@description('Storage Account role assignment ID')
output storageRoleAssignmentId string = storageRoleAssignment.id
