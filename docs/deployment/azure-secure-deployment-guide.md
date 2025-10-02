# 🔐 Azure Secure Deployment Guide - Loan Defenders

A comprehensive guide to securely deploy the Loan Defenders multi-agent system in Azure using Infrastructure-as-Code (Terraform) and CI/CD pipelines.

## 📋 **Overview**

This guide will help you:
1. **Set up secure Azure infrastructure** with private networking
2. **Deploy Azure OpenAI** with proper access controls
3. **Create CI/CD pipeline** for automated deployments
4. **Implement security best practices** for financial applications
5. **Monitor and maintain** the production deployment

## 🏗️ **Architecture Overview**

```
┌─────────────────────────────────────────────────────────────┐
│                     Azure Subscription                      │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐    ┌──────────────────────────────┐   │
│  │   Resource      │    │         VNet (Private)       │   │
│  │   Group         │    │  ┌─────────┐ ┌─────────────┐ │   │
│  │                 │    │  │  Subnet │ │   Subnet    │ │   │
│  │                 │    │  │ (Apps)  │ │   (Data)    │ │   │
│  │                 │    │  └─────────┘ └─────────────┘ │   │
│  └─────────────────┘    └──────────────────────────────┘   │
│                                                             │
│  ┌─────────────────────────────────────────────────────────┤
│  │              Azure Services                             │
│  │  ┌──────────────┐ ┌──────────────┐ ┌─────────────────┐ │
│  │  │ Azure OpenAI │ │ Key Vault    │ │ Container Apps  │ │
│  │  │ (Private)    │ │ (Secrets)    │ │ (Loan Defenders) │ │
│  │  └──────────────┘ └──────────────┘ └─────────────────┘ │
│  │  ┌──────────────┐ ┌──────────────┐ ┌─────────────────┐ │
│  │  │ Cosmos DB    │ │ App Insights │ │ Log Analytics   │ │
│  │  │ (Data Store) │ │ (Monitoring) │ │ (Logs)          │ │
│  │  └──────────────┘ └──────────────┘ └─────────────────┘ │
│  └─────────────────────────────────────────────────────────┘
└─────────────────────────────────────────────────────────────┘
```

## 🚀 **Step-by-Step Deployment Process**

### **Phase 1: Prerequisites and Setup** (30 minutes)

#### Step 1.1: Azure Prerequisites
```bash
# Install Azure CLI
curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash

# Install Terraform
wget https://releases.hashicorp.com/terraform/1.6.0/terraform_1.6.0_linux_amd64.zip
unzip terraform_1.6.0_linux_amd64.zip
sudo mv terraform /usr/local/bin/

# Verify installations
az --version
terraform --version
```

#### Step 1.2: Azure Authentication & Subscription Setup
```bash
# Login to Azure
az login

# List subscriptions
az account list --output table

# Set active subscription
az account set --subscription "Your-Subscription-Name-or-ID"

# Verify current subscription
az account show
```

#### Step 1.3: Service Principal Creation (for CI/CD)
```bash
# Create service principal for deployment
az ad sp create-for-rbac --name "loan-defenders-deploy-sp" \
    --role "Contributor" \
    --scopes "/subscriptions/$(az account show --query id -o tsv)"

# Save the output - you'll need:
# - appId (CLIENT_ID)
# - password (CLIENT_SECRET)  
# - tenant (TENANT_ID)
# - subscriptionId (SUBSCRIPTION_ID)
```

### **Phase 2: Terraform State Storage** (15 minutes)

#### Step 2.1: Create Terraform State Storage
```bash
# Create resource group for Terraform state
az group create --name "loan-defenders-tf-state-rg" --location "East US"

# Create storage account (name must be globally unique)
STORAGE_ACCOUNT_NAME="loandefenderstfstate$(openssl rand -hex 4)"
az storage account create \
    --resource-group "loan-defenders-tf-state-rg" \
    --name "$STORAGE_ACCOUNT_NAME" \
    --sku "Standard_LRS" \
    --encryption-services blob

# Create blob container
az storage container create \
    --name "tfstate" \
    --account-name "$STORAGE_ACCOUNT_NAME"

# Get storage account key
ACCOUNT_KEY=$(az storage account keys list \
    --resource-group "loan-defenders-tf-state-rg" \
    --account-name "$STORAGE_ACCOUNT_NAME" \
    --query '[0].value' -o tsv)

echo "Storage Account Name: $STORAGE_ACCOUNT_NAME"
echo "Account Key: $ACCOUNT_KEY"
# Save these values - you'll need them in terraform backend configuration
```

### **Phase 3: Infrastructure Deployment** (30 minutes)

#### Step 3.1: Configure Terraform Backend
```bash
# Navigate to terraform directory
cd infrastructure/terraform/environments/dev

# Update main.tf backend configuration with your storage account details
# Replace "loandefenderstfstate" with your actual storage account name
```

#### Step 3.2: Deploy Infrastructure
```bash
# Initialize Terraform
terraform init

# Plan deployment
terraform plan -out=tfplan

# Review plan and apply
terraform apply tfplan
```

### **Phase 4: CI/CD Pipeline Setup** (45 minutes)

The GitHub Actions workflow will automatically deploy your infrastructure and application on code changes.

### **Phase 5: Application Deployment** (30 minutes)

Once infrastructure is deployed, configure your application with the Azure OpenAI endpoint:

```bash
# Get outputs from Terraform
terraform output azure_openai_endpoint
terraform output key_vault_name

# Configure application environment variables
# These will be automatically set by the CI/CD pipeline
```

## 🔐 **Security Best Practices**

1. **Private Networking**: All Azure services use private endpoints
2. **Managed Identity**: No hardcoded credentials in application
3. **Key Vault**: All secrets stored securely
4. **Network Security Groups**: Restrictive firewall rules
5. **RBAC**: Principle of least privilege access
6. **Monitoring**: Comprehensive logging and alerting

## 🎯 **Next Steps**

1. Run through the deployment steps above
2. Test the Azure OpenAI integration
3. Set up monitoring and alerts
4. Configure production environment
5. Implement disaster recovery

## 📞 **Support**

If you encounter issues during deployment:
1. Check the Terraform logs
2. Verify Azure permissions
3. Review security group rules
4. Check Key Vault access policies

For help, refer to the troubleshooting section below or create an issue in the repository.