#!/bin/bash
# 🚀 Loan Avengers - Azure Prerequisites Setup Script
# This script sets up the required Azure resources for Terraform state management

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
RESOURCE_GROUP_NAME="loan-avengers-tf-state-rg"
LOCATION="East US"
CONTAINER_NAME="tfstate"

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check prerequisites
check_prerequisites() {
    print_status "Checking prerequisites..."
    
    if ! command_exists az; then
        print_error "Azure CLI is not installed. Please install it first:"
        echo "curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash"
        exit 1
    fi
    
    if ! command_exists openssl; then
        print_error "OpenSSL is not installed. Please install it first."
        exit 1
    fi
    
    # Check if logged in to Azure
    if ! az account show >/dev/null 2>&1; then
        print_error "Not logged in to Azure. Please run 'az login' first."
        exit 1
    fi
    
    print_success "Prerequisites check passed!"
}

# Generate unique storage account name
generate_storage_name() {
    RANDOM_SUFFIX=$(openssl rand -hex 4)
    STORAGE_ACCOUNT_NAME="loanavengerstfstate${RANDOM_SUFFIX}"
    echo $STORAGE_ACCOUNT_NAME
}

# Create resource group
create_resource_group() {
    print_status "Creating resource group: ${RESOURCE_GROUP_NAME}"
    
    if az group show --name "$RESOURCE_GROUP_NAME" >/dev/null 2>&1; then
        print_warning "Resource group already exists. Skipping creation."
    else
        az group create --name "$RESOURCE_GROUP_NAME" --location "$LOCATION"
        print_success "Resource group created successfully!"
    fi
}

# Create storage account
create_storage_account() {
    local storage_name=$(generate_storage_name)
    
    print_status "Creating storage account: ${storage_name}"
    
    # Check if storage account name is available
    if ! az storage account check-name --name "$storage_name" --query "nameAvailable" -o tsv | grep -q "true"; then
        print_error "Storage account name ${storage_name} is not available. Retrying..."
        storage_name=$(generate_storage_name)
    fi
    
    az storage account create \
        --resource-group "$RESOURCE_GROUP_NAME" \
        --name "$storage_name" \
        --sku "Standard_LRS" \
        --encryption-services blob \
        --allow-blob-public-access false \
        --min-tls-version "TLS1_2"
    
    print_success "Storage account ${storage_name} created successfully!"
    echo "$storage_name"
}

# Create blob container
create_blob_container() {
    local storage_name=$1
    
    print_status "Creating blob container: ${CONTAINER_NAME}"
    
    az storage container create \
        --name "$CONTAINER_NAME" \
        --account-name "$storage_name" \
        --auth-mode login
    
    print_success "Blob container created successfully!"
}

# Get storage account key
get_storage_key() {
    local storage_name=$1
    
    print_status "Retrieving storage account key..."
    
    local account_key=$(az storage account keys list \
        --resource-group "$RESOURCE_GROUP_NAME" \
        --account-name "$storage_name" \
        --query '[0].value' -o tsv)
    
    echo "$account_key"
}

# Create service principal for GitHub Actions
create_service_principal() {
    local subscription_id=$(az account show --query id -o tsv)
    
    print_status "Creating service principal for GitHub Actions..."
    
    local sp_name="loan-avengers-deploy-sp"
    
    # Check if service principal already exists
    if az ad sp list --display-name "$sp_name" --query '[0].appId' -o tsv | grep -q "^[a-f0-9-]*$"; then
        print_warning "Service principal ${sp_name} already exists."
        local app_id=$(az ad sp list --display-name "$sp_name" --query '[0].appId' -o tsv)
        echo "Existing App ID: ${app_id}"
        return
    fi
    
    # Create service principal
    local sp_output=$(az ad sp create-for-rbac \
        --name "$sp_name" \
        --role "Contributor" \
        --scopes "/subscriptions/${subscription_id}" \
        --sdk-auth)
    
    print_success "Service principal created successfully!"
    
    # Extract values
    local app_id=$(echo "$sp_output" | jq -r '.clientId')
    local client_secret=$(echo "$sp_output" | jq -r '.clientSecret')
    local tenant_id=$(echo "$sp_output" | jq -r '.tenantId')
    
    echo ""
    print_status "Service Principal Details (save these for GitHub Secrets):"
    echo "AZURE_CLIENT_ID: ${app_id}"
    echo "AZURE_CLIENT_SECRET: ${client_secret}"
    echo "AZURE_TENANT_ID: ${tenant_id}"
    echo "AZURE_SUBSCRIPTION_ID: ${subscription_id}"
}

# Output final configuration
output_configuration() {
    local storage_name=$1
    local storage_key=$2
    
    echo ""
    print_success "🎉 Setup Complete!"
    echo ""
    print_status "Terraform Backend Configuration:"
    echo "=================================="
    echo "resource_group_name  = \"${RESOURCE_GROUP_NAME}\""
    echo "storage_account_name = \"${storage_name}\""
    echo "container_name       = \"${CONTAINER_NAME}\""
    echo "key                  = \"dev/terraform.tfstate\""
    echo ""
    print_status "GitHub Secrets to Configure:"
    echo "============================"
    echo "TF_STATE_STORAGE_ACCOUNT = \"${storage_name}\""
    echo "TF_STATE_ACCESS_KEY = \"${storage_key}\""
    echo ""
    print_warning "⚠️  Important: Update the backend configuration in main.tf with your storage account name!"
    echo ""
    print_status "Next Steps:"
    echo "1. Add the GitHub Secrets to your repository"
    echo "2. Update infrastructure/terraform/environments/dev/main.tf backend configuration"
    echo "3. Run the infrastructure deployment pipeline"
}

# Main execution
main() {
    echo ""
    print_status "🚀 Loan Avengers - Azure Prerequisites Setup"
    echo "============================================="
    
    check_prerequisites
    
    create_resource_group
    
    local storage_name=$(create_storage_account)
    
    create_blob_container "$storage_name"
    
    local storage_key=$(get_storage_key "$storage_name")
    
    create_service_principal
    
    output_configuration "$storage_name" "$storage_key"
}

# Run main function
main "$@"