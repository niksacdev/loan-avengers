// ==============================================================================
// Networking Module - Azure Verified Modules
// ==============================================================================
// VNet, NSGs, and Subnets using Microsoft-verified modules
//
// Resources:
//   - 3x Network Security Groups (Container Apps, APIM, Private Endpoints)
//   - 1x Virtual Network with 3 subnets
//
// AVM Modules:
//   - avm/res/network/network-security-group:0.5.1
//   - avm/res/network/virtual-network:0.7.1
// ==============================================================================

targetScope = 'resourceGroup'

// ==============================================================================
// Parameters
// ==============================================================================

@description('Azure region for resources')
param location string = resourceGroup().location

@description('Environment name (dev, staging, prod)')
param environment string

@description('VNet name')
param vnetName string

@description('VNet address prefix')
param vnetAddressPrefix string

@description('Container Apps subnet prefix')
param containerAppsSubnetPrefix string

@description('APIM subnet prefix')
param apimSubnetPrefix string

@description('Private endpoints subnet prefix')
param privateEndpointsSubnetPrefix string

@description('Common tags for all resources')
param tags object

// ==============================================================================
// NSG: Container Apps
// ==============================================================================

module nsgContainerApps 'br/public:avm/res/network/network-security-group:0.5.1' = {
  name: 'nsg-container-apps-deployment'
  params: {
    name: '${vnetName}-container-apps-nsg'
    location: location
    tags: tags

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
          description: 'Allow Container Apps platform management (UDP/1194, TCP/9000)'
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

// ==============================================================================
// NSG: APIM
// ==============================================================================

module nsgApim 'br/public:avm/res/network/network-security-group:0.5.1' = {
  name: 'nsg-apim-deployment'
  params: {
    name: '${vnetName}-apim-nsg'
    location: location
    tags: tags

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
          description: 'Allow APIM health probe from Azure Load Balancer (port 6390)'
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

// ==============================================================================
// NSG: Private Endpoints
// ==============================================================================

module nsgPrivateEndpoints 'br/public:avm/res/network/network-security-group:0.5.1' = {
  name: 'nsg-private-endpoints-deployment'
  params: {
    name: '${vnetName}-private-endpoints-nsg'
    location: location
    tags: tags

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
// VNet with Subnets
// ==============================================================================

module vnet 'br/public:avm/res/network/virtual-network:0.7.1' = {
  name: 'vnet-deployment'
  params: {
    name: vnetName
    location: location
    addressPrefixes: [vnetAddressPrefix]
    tags: tags

    subnets: [
      // Container Apps Subnet
      {
        name: 'container-apps-subnet'
        addressPrefix: containerAppsSubnetPrefix
        delegation: 'Microsoft.App/environments'
        networkSecurityGroupResourceId: nsgContainerApps.outputs.resourceId
      }
      // APIM Subnet
      {
        name: 'apim-subnet'
        addressPrefix: apimSubnetPrefix
        networkSecurityGroupResourceId: nsgApim.outputs.resourceId
      }
      // Private Endpoints Subnet
      {
        name: 'private-endpoints-subnet'
        addressPrefix: privateEndpointsSubnetPrefix
        privateEndpointNetworkPolicies: 'Disabled'
        networkSecurityGroupResourceId: nsgPrivateEndpoints.outputs.resourceId
      }
    ]
  }
}

// ==============================================================================
// Outputs
// ==============================================================================

@description('VNet resource ID')
output vnetId string = vnet.outputs.resourceId

@description('VNet name')
output vnetName string = vnet.outputs.name

@description('Container Apps subnet ID')
output containerAppsSubnetId string = vnet.outputs.subnetResourceIds[0]

@description('APIM subnet ID')
output apimSubnetId string = vnet.outputs.subnetResourceIds[1]

@description('Private endpoints subnet ID')
output privateEndpointsSubnetId string = vnet.outputs.subnetResourceIds[2]

@description('Container Apps NSG resource ID')
output nsgContainerAppsId string = nsgContainerApps.outputs.resourceId

@description('APIM NSG resource ID')
output nsgApimId string = nsgApim.outputs.resourceId

@description('Private Endpoints NSG resource ID')
output nsgPrivateEndpointsId string = nsgPrivateEndpoints.outputs.resourceId
