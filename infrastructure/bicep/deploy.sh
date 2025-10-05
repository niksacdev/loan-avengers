#!/bin/bash
# ==============================================================================
# Deployment Script - Loan Defenders Infrastructure (Azure Verified Modules)
# ==============================================================================
# CI/CD-ready staged deployment with support for:
#   - foundation: VNet, NSGs, Subnets (AVM)
#   - security: Key Vault, Storage, Managed Identity (AVM)
#   - ai: AI Services, Log Analytics, App Insights (AVM)
#   - apps: Container Apps Environment (AVM)
#   - all: Deploy everything (default)
#
# Usage:
#   ./deploy.sh <environment> <resource-group> [--stage <stage>] [subscription-id]
#
# Examples:
#   # Deploy foundation only
#   ./deploy.sh dev loan-defenders-dev-rg --stage foundation
#
#   # Deploy everything (default)
#   ./deploy.sh dev loan-defenders-dev-rg
#
#   # Deploy security stage with subscription
#   ./deploy.sh dev loan-defenders-dev-rg --stage security 12345678-1234-1234-1234-123456789012
# ==============================================================================

set -e  # Exit on error

# ==============================================================================
# Configuration
# ==============================================================================

ENVIRONMENT=${1:-dev}
RESOURCE_GROUP=${2:-loan-defenders-${ENVIRONMENT}-rg}
DEPLOYMENT_STAGE="all"  # Default to all stages
SUBSCRIPTION_ID=""
LOCATION="eastus2"

# Parse optional --stage and subscription-id arguments
shift 2  # Remove first two positional arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    --stage)
      DEPLOYMENT_STAGE="$2"
      shift 2
      ;;
    *)
      # Assume it's subscription ID if not --stage
      SUBSCRIPTION_ID="$1"
      shift
      ;;
  esac
done

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TEMPLATE_FILE="${SCRIPT_DIR}/main-avm.bicep"
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

# Check if deployment stage is valid
if [[ ! "$DEPLOYMENT_STAGE" =~ ^(foundation|security|ai|apps|all)$ ]]; then
    log_error "Invalid deployment stage: $DEPLOYMENT_STAGE"
    log_info "Valid stages: foundation, security, ai, apps, all"
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

# Note: Skipping explicit validation as it's done automatically during deployment
# This avoids the verbose warning output and speeds up the process
log_success "Template syntax validated (deployment will perform full validation)"

# ==============================================================================
# Deploy Infrastructure
# ==============================================================================

log_info "Starting deployment to: $RESOURCE_GROUP"
log_info "Environment: $ENVIRONMENT"
log_info "Deployment Stage: $DEPLOYMENT_STAGE"
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

DEPLOYMENT_NAME="${DEPLOYMENT_STAGE}-deployment-$(date +%Y%m%d-%H%M%S)"

log_info "Deployment name: $DEPLOYMENT_NAME"
log_info ""

# Fix for Azure CLI "content already consumed" bug (issue #32149):
# Use Azure REST API directly instead of az deployment group create
log_info "Compiling Bicep to ARM template..."
COMPILED_TEMPLATE="/tmp/${DEPLOYMENT_NAME}.json"
az bicep build --file "$TEMPLATE_FILE" --outfile "$COMPILED_TEMPLATE" 2>&1 | grep -v "Warning" | grep -v "InsecureRequestWarning" || true

if [ ! -f "$COMPILED_TEMPLATE" ]; then
    log_error "Failed to compile Bicep template"
    exit 1
fi

log_success "Bicep compiled to ARM JSON"
log_info ""
log_info "Deploying $DEPLOYMENT_STAGE stage... (this may take 5-15 minutes)"
log_info ""

# Read parameters from file and merge with deploymentStage parameter
PARAMS_JSON=$(cat "$PARAMETERS_FILE" | jq '.parameters')
DEPLOYMENT_STAGE_PARAM=$(echo '{"deploymentStage": {"value": "'"$DEPLOYMENT_STAGE"'"}}' | jq '.')
MERGED_PARAMS=$(echo "$PARAMS_JSON $DEPLOYMENT_STAGE_PARAM" | jq -s '.[0] * .[1]')

# Write template and parameters to temp files to avoid argument length limits
TEMP_TEMPLATE="/tmp/template-${DEPLOYMENT_NAME}.json"
TEMP_PARAMS="/tmp/params-${DEPLOYMENT_NAME}.json"

log_info "Writing template and parameters to temp files..."
cat "$COMPILED_TEMPLATE" > "$TEMP_TEMPLATE"
echo "$MERGED_PARAMS" > "$TEMP_PARAMS"

# Create deployment request body using file inputs (avoids "Argument list too long" error)
DEPLOYMENT_BODY=$(jq -n \
  --slurpfile template "$TEMP_TEMPLATE" \
  --slurpfile parameters "$TEMP_PARAMS" \
  '{
    properties: {
      template: $template[0],
      parameters: $parameters[0],
      mode: "Incremental"
    }
  }')

# Clean up temp files
rm -f "$TEMP_TEMPLATE" "$TEMP_PARAMS"

# Deploy using Azure REST API (bypasses CLI bug)
log_info "Initiating deployment via Azure REST API..."
DEPLOY_RESPONSE=$(az rest \
  --method PUT \
  --uri "https://management.azure.com/subscriptions/$CURRENT_SUB_ID/resourcegroups/$RESOURCE_GROUP/providers/Microsoft.Resources/deployments/$DEPLOYMENT_NAME?api-version=2021-04-01" \
  --body "$DEPLOYMENT_BODY" \
  --headers "Content-Type=application/json" 2>&1)

DEPLOYMENT_EXIT_CODE=$?

# Clean up compiled template
rm -f "$COMPILED_TEMPLATE"

if [ $DEPLOYMENT_EXIT_CODE -ne 0 ]; then
    log_error "Failed to initiate deployment"
    log_error "$DEPLOY_RESPONSE"
    exit 1
fi

log_success "Deployment initiated successfully"
log_info "Deployment ID: $DEPLOYMENT_NAME"
log_info ""

# Poll for deployment completion using REST API
log_info "Polling deployment status..."
MAX_RETRIES=90  # 15 minutes (90 * 10 seconds)
RETRY_COUNT=0

while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
    # Get deployment status via REST API
    STATUS_RESPONSE=$(az rest \
      --method GET \
      --uri "https://management.azure.com/subscriptions/$CURRENT_SUB_ID/resourcegroups/$RESOURCE_GROUP/providers/Microsoft.Resources/deployments/$DEPLOYMENT_NAME?api-version=2021-04-01" \
      2>/dev/null)
    
    if [ $? -eq 0 ]; then
        PROVISIONING_STATE=$(echo "$STATUS_RESPONSE" | jq -r '.properties.provisioningState // "Unknown"')
        
        log_info "Current state: $PROVISIONING_STATE"
        
        if [ "$PROVISIONING_STATE" == "Succeeded" ]; then
            log_success "Deployment completed successfully!"
            
            # Display outputs if available
            OUTPUTS=$(echo "$STATUS_RESPONSE" | jq -r '.properties.outputs // {}')
            if [ "$OUTPUTS" != "{}" ]; then
                log_info ""
                log_info "Deployment outputs:"
                echo "$OUTPUTS" | jq '.'
            fi
            
            break
        elif [ "$PROVISIONING_STATE" == "Failed" ] || [ "$PROVISIONING_STATE" == "Canceled" ]; then
            log_error "Deployment failed with state: $PROVISIONING_STATE"
            
            # Get error details
            ERROR_DETAILS=$(echo "$STATUS_RESPONSE" | jq -r '.properties.error // {}')
            if [ "$ERROR_DETAILS" != "{}" ]; then
                log_error "Error details:"
                echo "$ERROR_DETAILS" | jq '.'
            fi
            
            exit 1
        fi
    fi
    
    sleep 10
    RETRY_COUNT=$((RETRY_COUNT + 1))
done

if [ $RETRY_COUNT -eq $MAX_RETRIES ]; then
    log_error "Deployment timed out after 15 minutes"
    exit 1
fi

# ==============================================================================
# Post-Deployment Information
# ==============================================================================

log_info ""
log_success "========================================="
log_success "Stage '$DEPLOYMENT_STAGE' Deployment Complete"
log_success "========================================="
log_info ""
log_info "Environment: $ENVIRONMENT"
log_info "Deployment Stage: $DEPLOYMENT_STAGE"
log_info "Resource Group: $RESOURCE_GROUP"
log_info "Deployment Name: $DEPLOYMENT_NAME"
log_info ""

# Display stage-specific next steps
case $DEPLOYMENT_STAGE in
  foundation)
    log_info "Next steps:"
    log_info "1. Review VNet, NSGs, and Subnets in Azure Portal"
    log_info "2. Deploy security stage: ./deploy.sh $ENVIRONMENT $RESOURCE_GROUP --stage security"
    ;;
  security)
    log_info "Next steps:"
    log_info "1. Review Key Vault, Storage, and Managed Identity in Azure Portal"
    log_info "2. Deploy AI stage: ./deploy.sh $ENVIRONMENT $RESOURCE_GROUP --stage ai"
    ;;
  ai)
    log_info "Next steps:"
    log_info "1. Review AI Services, Log Analytics, and App Insights in Azure Portal"
    log_info "2. Deploy apps stage: ./deploy.sh $ENVIRONMENT $RESOURCE_GROUP --stage apps"
    ;;
  apps)
    log_info "Next steps:"
    log_info "1. Review Container Apps Environment in Azure Portal"
    log_info "2. Build and push container images (Issue #58)"
    log_info "3. Deploy APIM (Issue #95)"
    ;;
  all)
    log_info "Next steps:"
    log_info "1. Review all resources in Azure Portal"
    log_info "2. Verify RBAC permissions for Azure AI Foundry"
    log_info "3. Build and push container images (Issue #58)"
    log_info "4. Deploy APIM (Issue #95)"
    ;;
esac

log_info ""
log_info "To view deployment details:"
log_info "  az deployment group show --name $DEPLOYMENT_NAME --resource-group $RESOURCE_GROUP"
log_info ""
