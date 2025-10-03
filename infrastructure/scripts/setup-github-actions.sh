#!/bin/bash
# ==============================================================================
# GitHub Actions OIDC Setup Script - Loan Defenders
# ==============================================================================
# Automates the setup of Azure AD app registration, service principal, and
# federated credentials for secure GitHub Actions deployments.
#
# Usage:
#   ./setup-github-actions.sh <github-username> <repository-name>
#
# Example:
#   ./setup-github-actions.sh niksacdev loan-defenders
# ==============================================================================

set -e  # Exit on error

# ==============================================================================
# Colors for output
# ==============================================================================

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
BOLD='\033[1m'
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

log_step() {
    echo -e "\n${CYAN}${BOLD}==> $1${NC}"
}

# ==============================================================================
# Validate Input Parameters
# ==============================================================================

if [ $# -lt 2 ]; then
    log_error "Missing required parameters"
    echo ""
    echo "Usage: $0 <github-username> <repository-name>"
    echo ""
    echo "Examples:"
    echo "  $0 niksacdev loan-defenders"
    echo "  $0 mycompany myproject"
    exit 1
fi

GITHUB_USERNAME=$1
REPO_NAME=$2
APP_NAME="${REPO_NAME}-github-actions"
FULL_REPO="${GITHUB_USERNAME}/${REPO_NAME}"

log_info "GitHub Repository: ${FULL_REPO}"
log_info "Azure AD App Name: ${APP_NAME}"

# ==============================================================================
# Check Prerequisites
# ==============================================================================

log_step "Checking prerequisites..."

# Check if Azure CLI is installed
if ! command -v az &> /dev/null; then
    log_error "Azure CLI is not installed"
    log_info "Install from: https://learn.microsoft.com/en-us/cli/azure/install-azure-cli"
    exit 1
fi

log_success "Azure CLI found"

# Check if logged in to Azure
if ! az account show &> /dev/null; then
    log_error "Not logged in to Azure CLI"
    log_info "Run: az login"
    exit 1
fi

log_success "Logged in to Azure"

# Get current subscription details
SUB_NAME=$(az account show --query name -o tsv)
SUB_ID=$(az account show --query id -o tsv)
TENANT_ID=$(az account show --query tenantId -o tsv)

log_info "Subscription: ${SUB_NAME}"
log_info "Subscription ID: ${SUB_ID}"
log_info "Tenant ID: ${TENANT_ID}"

# Confirm with user
echo ""
read -p "Continue with this subscription? (yes/no): " CONFIRM
if [ "$CONFIRM" != "yes" ]; then
    log_info "Setup cancelled"
    exit 0
fi

# ==============================================================================
# Step 1: Create Azure AD App Registration
# ==============================================================================

log_step "Step 1: Creating Azure AD App Registration..."

# Check if app already exists
EXISTING_APP_ID=$(az ad app list --display-name "${APP_NAME}" --query "[0].appId" -o tsv 2>/dev/null || echo "")

if [ -n "$EXISTING_APP_ID" ]; then
    log_warning "App registration '${APP_NAME}' already exists (ID: ${EXISTING_APP_ID})"
    read -p "Do you want to use the existing app? (yes/no): " USE_EXISTING

    if [ "$USE_EXISTING" = "yes" ]; then
        APP_ID=$EXISTING_APP_ID
        log_info "Using existing app registration"
    else
        log_error "Please delete the existing app or choose a different name"
        log_info "To delete: az ad app delete --id ${EXISTING_APP_ID}"
        exit 1
    fi
else
    # Create new app registration
    APP_ID=$(az ad app create \
        --display-name "${APP_NAME}" \
        --query appId -o tsv)

    log_success "Created app registration: ${APP_NAME}"
    log_info "Application (Client) ID: ${APP_ID}"
fi

# ==============================================================================
# Step 2: Create Service Principal
# ==============================================================================

log_step "Step 2: Creating Service Principal..."

# Check if service principal exists
EXISTING_SP=$(az ad sp list --display-name "${APP_NAME}" --query "[0].id" -o tsv 2>/dev/null || echo "")

if [ -n "$EXISTING_SP" ]; then
    log_info "Service Principal already exists"
    SP_OBJECT_ID=$EXISTING_SP
else
    # Create service principal
    SP_OBJECT_ID=$(az ad sp create --id ${APP_ID} --query id -o tsv)
    log_success "Created Service Principal"
fi

log_info "Service Principal Object ID: ${SP_OBJECT_ID}"

# ==============================================================================
# Step 3: Assign Contributor Role
# ==============================================================================

log_step "Step 3: Assigning Contributor role..."

# Check if role assignment exists
EXISTING_ROLE=$(az role assignment list \
    --assignee ${APP_ID} \
    --role Contributor \
    --scope /subscriptions/${SUB_ID} \
    --query "[0].id" -o tsv 2>/dev/null || echo "")

if [ -n "$EXISTING_ROLE" ]; then
    log_info "Contributor role already assigned"
else
    # Assign Contributor role
    az role assignment create \
        --role Contributor \
        --assignee ${APP_ID} \
        --scope /subscriptions/${SUB_ID} \
        --description "GitHub Actions deployment for ${REPO_NAME}" \
        > /dev/null

    log_success "Assigned Contributor role to Service Principal"
fi

# ==============================================================================
# Step 4: Create Federated Credentials
# ==============================================================================

log_step "Step 4: Creating Federated Credentials..."

# Function to create federated credential
create_federated_credential() {
    local CRED_NAME=$1
    local SUBJECT=$2
    local DESCRIPTION=$3

    # Check if credential exists
    EXISTING_CRED=$(az ad app federated-credential list \
        --id ${APP_ID} \
        --query "[?name=='${CRED_NAME}'].name" -o tsv 2>/dev/null || echo "")

    if [ -n "$EXISTING_CRED" ]; then
        log_info "Federated credential '${CRED_NAME}' already exists"
        return
    fi

    # Create federated credential
    az ad app federated-credential create \
        --id ${APP_ID} \
        --parameters "{
            \"name\": \"${CRED_NAME}\",
            \"issuer\": \"https://token.actions.githubusercontent.com\",
            \"subject\": \"${SUBJECT}\",
            \"description\": \"${DESCRIPTION}\",
            \"audiences\": [\"api://AzureADTokenExchange\"]
        }" > /dev/null

    log_success "Created federated credential: ${CRED_NAME}"
}

# Create federated credential for main branch
create_federated_credential \
    "${REPO_NAME}-main" \
    "repo:${FULL_REPO}:ref:refs/heads/main" \
    "GitHub Actions deployment from main branch"

# Create federated credential for pull requests
create_federated_credential \
    "${REPO_NAME}-pr" \
    "repo:${FULL_REPO}:pull_request" \
    "GitHub Actions deployment from pull requests"

# Create federated credential for any branch (optional, for testing)
read -p "Create federated credential for ALL branches? (yes/no): " CREATE_ALL_BRANCHES
if [ "$CREATE_ALL_BRANCHES" = "yes" ]; then
    create_federated_credential \
        "${REPO_NAME}-all-branches" \
        "repo:${FULL_REPO}:ref:refs/heads/*" \
        "GitHub Actions deployment from any branch (testing)"
fi

# ==============================================================================
# Step 5: Display GitHub Secrets Configuration
# ==============================================================================

log_step "Step 5: GitHub Secrets Configuration"

echo ""
log_success "Setup complete! Now configure GitHub Secrets:"
echo ""
echo -e "${BOLD}Go to: https://github.com/${FULL_REPO}/settings/secrets/actions${NC}"
echo ""
echo -e "${CYAN}Add the following secrets:${NC}"
echo ""
echo -e "${BOLD}1. AZURE_CLIENT_ID${NC}"
echo -e "   Value: ${GREEN}${APP_ID}${NC}"
echo ""
echo -e "${BOLD}2. AZURE_TENANT_ID${NC}"
echo -e "   Value: ${GREEN}${TENANT_ID}${NC}"
echo ""
echo -e "${BOLD}3. AZURE_SUBSCRIPTION_ID${NC}"
echo -e "   Value: ${GREEN}${SUB_ID}${NC}"
echo ""

# ==============================================================================
# Step 6: Save Configuration to File
# ==============================================================================

log_step "Step 6: Saving configuration..."

CONFIG_FILE="github-actions-config.txt"
cat > ${CONFIG_FILE} <<EOF
# GitHub Actions OIDC Configuration
# Generated: $(date)
# Repository: ${FULL_REPO}

Azure AD App Registration:
  Name: ${APP_NAME}
  Application (Client) ID: ${APP_ID}

Service Principal:
  Object ID: ${SP_OBJECT_ID}
  Role: Contributor
  Scope: /subscriptions/${SUB_ID}

Azure Subscription:
  Name: ${SUB_NAME}
  Subscription ID: ${SUB_ID}
  Tenant ID: ${TENANT_ID}

GitHub Secrets (add these to GitHub):
  AZURE_CLIENT_ID: ${APP_ID}
  AZURE_TENANT_ID: ${TENANT_ID}
  AZURE_SUBSCRIPTION_ID: ${SUB_ID}

Federated Credentials:
  - ${REPO_NAME}-main (main branch deployments)
  - ${REPO_NAME}-pr (pull request deployments)
EOF

if [ "$CREATE_ALL_BRANCHES" = "yes" ]; then
    echo "  - ${REPO_NAME}-all-branches (all branch deployments)" >> ${CONFIG_FILE}
fi

cat >> ${CONFIG_FILE} <<EOF

GitHub Actions Workflow:
  Location: .github/workflows/deploy-infrastructure.yml
  Trigger: workflow_dispatch (manual)

Next Steps:
  1. Add secrets to GitHub: https://github.com/${FULL_REPO}/settings/secrets/actions
  2. Run workflow: https://github.com/${FULL_REPO}/actions
  3. Select environment (dev/staging/prod) and stage (foundation/security/ai/apps/all)

Security:
  - OIDC authentication (no passwords stored)
  - Short-lived tokens (expire in minutes)
  - Repository-scoped (only ${FULL_REPO} can authenticate)
  - Audit trail in Azure AD and GitHub Actions

To delete this setup:
  az ad app delete --id ${APP_ID}
EOF

log_success "Configuration saved to: ${CONFIG_FILE}"

# ==============================================================================
# Step 7: Instructions for Next Steps
# ==============================================================================

log_step "Next Steps"

echo ""
echo -e "${BOLD}1. Add Secrets to GitHub:${NC}"
echo "   https://github.com/${FULL_REPO}/settings/secrets/actions"
echo ""
echo -e "${BOLD}2. (Optional) Configure Environment Protection:${NC}"
echo "   https://github.com/${FULL_REPO}/settings/environments"
echo "   - Create 'prod' environment"
echo "   - Add required reviewers (yourself)"
echo "   - Set deployment branch restriction to 'main'"
echo ""
echo -e "${BOLD}3. Test Deployment:${NC}"
echo "   https://github.com/${FULL_REPO}/actions"
echo "   - Select 'Deploy Azure Infrastructure' workflow"
echo "   - Click 'Run workflow'"
echo "   - Choose environment: dev"
echo "   - Choose stage: foundation"
echo ""
echo -e "${BOLD}4. Review Configuration:${NC}"
echo "   cat ${CONFIG_FILE}"
echo ""

log_success "Setup complete! 🎉"
echo ""
echo -e "${YELLOW}Security Note:${NC}"
echo "  - The configuration file contains IDs (not secrets)"
echo "  - Safe to commit to private repository"
echo "  - Do NOT commit to public repository (contains subscription ID)"
echo ""
