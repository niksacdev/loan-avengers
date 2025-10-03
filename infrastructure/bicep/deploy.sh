#!/bin/bash
# ==============================================================================
# Deployment Script - Loan Defenders VNet Infrastructure
# ==============================================================================
# Deploys VNet, subnets, NSGs, and private DNS zones to Azure
#
# Usage:
#   ./deploy.sh <environment> <resource-group> [subscription-id]
#
# Example:
#   ./deploy.sh dev loan-defenders-dev-rg
#   ./deploy.sh prod loan-defenders-prod-rg 12345678-1234-1234-1234-123456789012
# ==============================================================================

set -e  # Exit on error

# ==============================================================================
# Configuration
# ==============================================================================

ENVIRONMENT=${1:-dev}
RESOURCE_GROUP=${2:-loan-defenders-${ENVIRONMENT}-rg}
SUBSCRIPTION_ID=${3:-}
LOCATION="eastus"

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TEMPLATE_FILE="${SCRIPT_DIR}/main.bicep"
PARAMETERS_FILE="${SCRIPT_DIR}/environments/${ENVIRONMENT}.parameters.json"

# ==============================================================================
# Colors for output
# ==============================================================================

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# ==============================================================================
# Helper Functions
# ==============================================================================

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# ==============================================================================
# Validation
# ==============================================================================

log_info "Validating inputs..."

# Check if environment is valid
if [[ ! "$ENVIRONMENT" =~ ^(dev|staging|prod)$ ]]; then
    log_error "Invalid environment: $ENVIRONMENT"
    log_info "Valid environments: dev, staging, prod"
    exit 1
fi

# Check if parameters file exists
if [ ! -f "$PARAMETERS_FILE" ]; then
    log_error "Parameters file not found: $PARAMETERS_FILE"
    exit 1
fi

# Check if template file exists
if [ ! -f "$TEMPLATE_FILE" ]; then
    log_error "Template file not found: $TEMPLATE_FILE"
    exit 1
fi

log_success "Validation passed"

# ==============================================================================
# Azure CLI Login Check
# ==============================================================================

log_info "Checking Azure CLI login status..."

if ! az account show &>/dev/null; then
    log_warning "Not logged in to Azure CLI"
    log_info "Running: az login"
    az login
fi

log_success "Azure CLI logged in"

# ==============================================================================
# Set Subscription
# ==============================================================================

if [ -n "$SUBSCRIPTION_ID" ]; then
    log_info "Setting subscription to: $SUBSCRIPTION_ID"
    az account set --subscription "$SUBSCRIPTION_ID"
    log_success "Subscription set"
fi

# Display current subscription
CURRENT_SUB=$(az account show --query name -o tsv)
CURRENT_SUB_ID=$(az account show --query id -o tsv)
log_info "Current subscription: $CURRENT_SUB ($CURRENT_SUB_ID)"

# ==============================================================================
# Create Resource Group (if it doesn't exist)
# ==============================================================================

log_info "Checking resource group: $RESOURCE_GROUP"

if ! az group show --name "$RESOURCE_GROUP" &>/dev/null; then
    log_warning "Resource group does not exist. Creating..."
    az group create --name "$RESOURCE_GROUP" --location "$LOCATION"
    log_success "Resource group created: $RESOURCE_GROUP"
else
    log_info "Resource group exists: $RESOURCE_GROUP"
fi

# ==============================================================================
# Validate Bicep Template
# ==============================================================================

log_info "Validating Bicep template..."

az deployment group validate \
    --resource-group "$RESOURCE_GROUP" \
    --template-file "$TEMPLATE_FILE" \
    --parameters "@$PARAMETERS_FILE" \
    --output none

if [ $? -eq 0 ]; then
    log_success "Template validation passed"
else
    log_error "Template validation failed"
    exit 1
fi

# ==============================================================================
# Deploy Infrastructure
# ==============================================================================

log_info "Starting deployment to: $RESOURCE_GROUP"
log_info "Environment: $ENVIRONMENT"
log_info "Location: $LOCATION"
log_info ""

# Prompt for confirmation in production
if [ "$ENVIRONMENT" == "prod" ]; then
    log_warning "You are about to deploy to PRODUCTION environment"
    read -p "Are you sure you want to continue? (yes/no): " CONFIRM
    if [ "$CONFIRM" != "yes" ]; then
        log_info "Deployment cancelled"
        exit 0
    fi
fi

DEPLOYMENT_NAME="vnet-infrastructure-$(date +%Y%m%d-%H%M%S)"

log_info "Deployment name: $DEPLOYMENT_NAME"
log_info ""
log_info "Deploying infrastructure... (this may take 5-10 minutes)"

az deployment group create \
    --name "$DEPLOYMENT_NAME" \
    --resource-group "$RESOURCE_GROUP" \
    --template-file "$TEMPLATE_FILE" \
    --parameters "@$PARAMETERS_FILE" \
    --output table

if [ $? -eq 0 ]; then
    log_success "Deployment completed successfully!"
    log_info ""
    log_info "Deployment outputs:"
    az deployment group show \
        --name "$DEPLOYMENT_NAME" \
        --resource-group "$RESOURCE_GROUP" \
        --query properties.outputs \
        --output table
else
    log_error "Deployment failed"
    exit 1
fi

# ==============================================================================
# Post-Deployment Information
# ==============================================================================

log_info ""
log_success "========================================="
log_success "VNet Infrastructure Deployment Complete"
log_success "========================================="
log_info ""
log_info "Environment: $ENVIRONMENT"
log_info "Resource Group: $RESOURCE_GROUP"
log_info "Deployment Name: $DEPLOYMENT_NAME"
log_info ""
log_info "Next steps:"
log_info "1. Review deployed resources in Azure Portal"
log_info "2. Deploy Azure services (Key Vault, Storage, etc.)"
log_info "3. Re-run deployment with deployPrivateEndpoints=true"
log_info "4. Deploy Container Apps environment (#58)"
log_info ""
log_info "To view deployment details:"
log_info "  az deployment group show --name $DEPLOYMENT_NAME --resource-group $RESOURCE_GROUP"
log_info ""
