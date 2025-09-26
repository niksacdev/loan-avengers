# Loan Avengers - Development Environment Infrastructure
# This configures a secure Azure deployment for the multi-agent loan processing system

terraform {
  required_version = ">= 1.5"
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.80"
    }
    random = {
      source  = "hashicorp/random"
      version = "~> 3.4"
    }
  }
  
  # Backend configuration - update with your storage account details
  backend "azurerm" {
    resource_group_name  = "loan-avengers-tf-state-rg"
    storage_account_name = "loanavengerstfstate"  # Must be globally unique - update this
    container_name       = "tfstate"
    key                  = "dev/terraform.tfstate"
  }
}

# Configure the Azure Provider
provider "azurerm" {
  features {
    key_vault {
      purge_soft_delete_on_destroy    = true
      recover_soft_deleted_key_vaults = true
    }
    cognitive_account {
      purge_soft_delete_on_destroy = true
    }
  }
}

# Random suffix for globally unique names
resource "random_string" "suffix" {
  length  = 8
  special = false
  upper   = false
}

# Local values for consistent naming
locals {
  environment = "dev"
  project     = "loan-avengers"
  location    = "East US"
  
  # Naming convention: {project}-{component}-{environment}-{suffix}
  naming_suffix = "${local.environment}-${random_string.suffix.result}"
  
  common_tags = {
    Project     = local.project
    Environment = local.environment
    ManagedBy   = "Terraform"
    Owner       = "DevOps"
    CostCenter  = "AI-Innovation"
  }
}

# Resource Group
resource "azurerm_resource_group" "main" {
  name     = "${local.project}-rg-${local.naming_suffix}"
  location = local.location
  tags     = local.common_tags
}

# Virtual Network Module
module "networking" {
  source = "../../modules/networking"
  
  resource_group_name = azurerm_resource_group.main.name
  location           = azurerm_resource_group.main.location
  naming_suffix      = local.naming_suffix
  tags               = local.common_tags
}

# Security Module (Key Vault, Managed Identity)
module "security" {
  source = "../../modules/security"
  
  resource_group_name = azurerm_resource_group.main.name
  location           = azurerm_resource_group.main.location
  naming_suffix      = local.naming_suffix
  tags               = local.common_tags
  
  # Network integration
  subnet_id = module.networking.private_subnet_id
}

# AI Services Module (Azure OpenAI, Cognitive Services)
module "ai_services" {
  source = "../../modules/ai-services"
  
  resource_group_name = azurerm_resource_group.main.name
  location           = local.location
  naming_suffix      = local.naming_suffix
  tags               = local.common_tags
  
  # Security integration
  key_vault_id       = module.security.key_vault_id
  managed_identity_id = module.security.managed_identity_id
  
  # Network integration
  subnet_id = module.networking.private_subnet_id
}

# Monitoring Module (Application Insights, Log Analytics)
module "monitoring" {
  source = "../../modules/monitoring"
  
  resource_group_name = azurerm_resource_group.main.name
  location           = azurerm_resource_group.main.location
  naming_suffix      = local.naming_suffix
  tags               = local.common_tags
}

# Container Apps Environment for Loan Avengers
resource "azurerm_container_app_environment" "main" {
  name                       = "${local.project}-cae-${local.naming_suffix}"
  location                  = azurerm_resource_group.main.location
  resource_group_name       = azurerm_resource_group.main.name
  log_analytics_workspace_id = module.monitoring.log_analytics_workspace_id
  
  infrastructure_subnet_id = module.networking.container_apps_subnet_id
  
  tags = local.common_tags
}

# Output values for use in application deployment
output "resource_group_name" {
  description = "Name of the main resource group"
  value       = azurerm_resource_group.main.name
}

output "azure_openai_endpoint" {
  description = "Azure OpenAI service endpoint"
  value       = module.ai_services.openai_endpoint
  sensitive   = true
}

output "azure_openai_key_vault_secret_name" {
  description = "Key Vault secret name containing OpenAI API key"
  value       = module.ai_services.openai_key_secret_name
}

output "gpt4_deployment_name" {
  description = "GPT-4 deployment name"
  value       = module.ai_services.gpt4_deployment_name
}

output "gpt35_deployment_name" {
  description = "GPT-3.5 Turbo deployment name"
  value       = module.ai_services.gpt35_deployment_name
}

output "key_vault_name" {
  description = "Name of the Key Vault"
  value       = module.security.key_vault_name
}

output "managed_identity_client_id" {
  description = "Managed Identity Client ID for application authentication"
  value       = module.security.managed_identity_client_id
}

output "container_app_environment_id" {
  description = "Container App Environment ID for application deployment"
  value       = azurerm_container_app_environment.main.id
}

output "application_insights_connection_string" {
  description = "Application Insights connection string"
  value       = module.monitoring.application_insights_connection_string
  sensitive   = true
}