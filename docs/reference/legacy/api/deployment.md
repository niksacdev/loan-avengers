# Azure Container Apps Deployment Guide

## Prerequisites

- Azure CLI installed (`az --version`)
- Azure subscription with appropriate permissions
- GitHub repository access
- Docker installed locally

## Quick Start

```bash
# Login to Azure
az login

# Set subscription
az account set --subscription "YOUR_SUBSCRIPTION_ID"

# Deploy infrastructure and application
./scripts/deploy-azure.sh
```

## Infrastructure Setup

### 1. Resource Group

```bash
az group create \
  --name rg-loan-defenders-prod \
  --location eastus
```

### 2. Container Registry

```bash
az acr create \
  --resource-group rg-loan-defenders-prod \
  --name loandefendersacr \
  --sku Standard
```

### 3. Key Vault

```bash
az keyvault create \
  --name kv-loan-defenders-prod \
  --resource-group rg-loan-defenders-prod \
  --location eastus
```

### 4. Azure Cache for Redis

```bash
az redis create \
  --resource-group rg-loan-defenders-prod \
  --name redis-loan-defenders-prod \
  --location eastus \
  --sku Standard \
  --vm-size C1
```

### 5. Cosmos DB

```bash
az cosmosdb create \
  --name cosmos-loan-defenders-prod \
  --resource-group rg-loan-defenders-prod \
  --locations regionName=eastus
```

### 6. Blob Storage

```bash
az storage account create \
  --name stloandefendersprod \
  --resource-group rg-loan-defenders-prod \
  --location eastus \
  --sku Standard_LRS
```

### 7. Container Apps Environment

```bash
az containerapp env create \
  --name env-loan-defenders-prod \
  --resource-group rg-loan-defenders-prod \
  --location eastus
```

## Application Deployment

### Build and Push Docker Image

```bash
# Build image
docker build -t loandefendersacr.azurecr.io/loan-defenders-api:latest .

# Login to ACR
az acr login --name loandefendersacr

# Push image
docker push loandefendersacr.azurecr.io/loan-defenders-api:latest
```

### Deploy Container App

```bash
az containerapp create \
  --name app-loan-defenders-api \
  --resource-group rg-loan-defenders-prod \
  --environment env-loan-defenders-prod \
  --image loandefendersacr.azurecr.io/loan-defenders-api:latest \
  --target-port 8000 \
  --ingress external \
  --min-replicas 1 \
  --max-replicas 10 \
  --cpu 1.0 \
  --memory 2Gi \
  --secrets \
    foundry-endpoint=keyvaultref:https://kv-loan-defenders-prod.vault.azure.net/secrets/foundry-endpoint,identityref:system \
    redis-connection=keyvaultref:https://kv-loan-defenders-prod.vault.azure.net/secrets/redis-connection,identityref:system \
  --env-vars \
    FOUNDRY_PROJECT_ENDPOINT=secretref:foundry-endpoint \
    REDIS_CONNECTION_STRING=secretref:redis-connection
```

## Environment Configuration

Store secrets in Azure Key Vault:

```bash
# Foundry endpoint
az keyvault secret set \
  --vault-name kv-loan-defenders-prod \
  --name foundry-endpoint \
  --value "https://your-project.projects.ai.azure.com"

# Redis connection
REDIS_CONN=$(az redis list-keys --name redis-loan-defenders-prod --resource-group rg-loan-defenders-prod --query primaryKey -o tsv)
az keyvault secret set \
  --vault-name kv-loan-defenders-prod \
  --name redis-connection \
  --value "rediss://redis-loan-defenders-prod.redis.cache.windows.net:6380,password=${REDIS_CONN},ssl=True"
```

## CI/CD Pipeline

GitHub Actions workflow (`.github/workflows/deploy-api.yml`) handles automated deployments.

## Monitoring

Application Insights automatically collects telemetry. View in Azure Portal.

## Scaling

Auto-scaling rules are configured based on CPU and HTTP requests. Adjust in Container App settings.
