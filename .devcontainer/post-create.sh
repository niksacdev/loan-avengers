#!/bin/bash
# 🚀 Loan Defenders Dev Container - Post Creation Setup Script
# This script sets up the development environment after container creation

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m' # No Color

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

print_header() {
    echo -e "${PURPLE}$1${NC}"
}

# Main setup function
main() {
    print_header "🚀 Setting up Loan Defenders Development Environment"
    echo "================================================================"

    # Update system packages (required for stability)
    print_status "Updating system packages..."
    sudo apt-get update -qq

    # Install additional development tools
    print_status "Installing additional development tools..."
    sudo apt-get install -y -qq \
        curl \
        wget \
        unzip \
        jq \
        tree \
        htop \
        git-lfs \
        make \
        build-essential    # Install UV package manager (Python) - optimized
    print_status "Installing UV package manager..."
    if ! command -v uv >/dev/null 2>&1; then
        curl -LsSf https://astral.sh/uv/install.sh | sh
        export PATH="$HOME/.cargo/bin:$PATH"
        print_success "UV package manager installed"
    else
        print_success "UV package manager already available"
    fi

    # Configure npm (if available)
    print_status "Configuring npm..."
    if command -v npm >/dev/null 2>&1; then
        # Set npm registry (can be overridden later)
        npm config set registry https://registry.npmjs.org/
        # Configure npm audit to not break on vulnerabilities
        npm config set audit-level moderate
        # Enable package-lock.json
        npm config set package-lock true
        print_success "npm configured successfully"
        print_status "npm version: $(npm --version)"

        # Install GitHub Copilot CLI (official package)
        print_status "Installing GitHub Copilot CLI..."
        if npm install -g @github/copilot 2>/dev/null; then
            print_success "GitHub Copilot CLI installed successfully"
            print_status "Use 'copilot' command to interact with GitHub Copilot"
        else
            print_warning "GitHub Copilot CLI installation failed (requires Node.js >=22)"
            print_warning "You can try installing manually after container starts"
        fi
    else
        print_warning "npm not found, skipping npm configuration"
    fi

    # Install Python dependencies (with caching optimization)
    print_status "Installing Python dependencies with UV..."
    cd /workspaces/loan-defenders

    if [ -f "pyproject.toml" ]; then
        # Use UV with optimized settings for container environments
        UV_CACHE_DIR=/tmp/uv-cache uv sync --no-progress
        print_success "Python dependencies installed successfully"
    else
        print_warning "No pyproject.toml found, skipping Python dependencies"
    fi

    # Install pre-commit hooks
    print_status "Setting up pre-commit hooks..."
    if command -v pre-commit >/dev/null 2>&1; then
        uv add --dev pre-commit
        uv run pre-commit install
        print_success "Pre-commit hooks installed"
    else
        print_warning "Pre-commit not available, skipping hooks setup"
    fi

    # Configure Git (if not already configured)
    print_status "Configuring Git..."
    if [ -z "$(git config --global user.name)" ]; then
        print_warning "Git user.name not configured. Please run:"
        echo "  git config --global user.name 'Your Name'"
        echo "  git config --global user.email 'your.email@example.com'"
    else
        print_success "Git already configured for $(git config --global user.name)"
    fi

    # Setup Azure CLI extensions (optimized installation)
    print_status "Installing essential Azure CLI extensions..."
    az extension add --name azure-devops --yes 2>/dev/null || true &
    az extension add --name containerapp --yes 2>/dev/null || true &
    wait  # Wait for background installations to complete
    print_success "Azure CLI extensions installed"

    # Setup shell aliases and functions
    print_status "Setting up development aliases..."
    cat >> /home/vscode/.zshrc << 'EOF'

# Loan Defenders Development Aliases
alias ll='ls -la'
alias la='ls -la'
alias ..='cd ..'
alias ...='cd ../..'

# Python/UV aliases
alias py='uv run python'
alias pytest='uv run pytest'
alias ruff-check='uv run ruff check .'
alias ruff-fix='uv run ruff check . --fix'
alias ruff-format='uv run ruff format .'

# Node.js/npm aliases
alias ni='npm install'
alias nid='npm install --save-dev'
alias nig='npm install --global'
alias nr='npm run'
alias ns='npm start'
alias nt='npm test'
alias nb='npm run build'
alias nci='npm ci'
alias nls='npm list --depth=0'



# Azure aliases
alias az-login='az login --use-device-code'
alias az-accounts='az account list --output table'

# Terraform aliases
alias tf='terraform'
alias tfinit='terraform init'
alias tfplan='terraform plan'
alias tfapply='terraform apply'
alias tfdestroy='terraform destroy'

# Git aliases
alias gst='git status'
alias glog='git log --oneline --graph --decorate'
alias gpush='git push origin HEAD'

# Docker aliases
alias dps='docker ps'
alias di='docker images'

# Loan Defenders specific
alias test-unit='uv run pytest tests/unit/ -v'
alias test-integration='uv run pytest tests/integration/ -v'
alias test-all='uv run pytest tests/ -v'
alias coverage='uv run python tests/coverage_report.py'



    # Welcome message
    echo "🦸‍♂️ Welcome to the Loan Defenders Development Environment!"
EOF    # Create development workspace directories
    print_status "Creating workspace directories..."
    mkdir -p /workspaces/loan-defenders/{logs,temp,docs/notes}

    # Setup VS Code workspace settings
    print_status "Setting up VS Code workspace..."
    mkdir -p /workspaces/loan-defenders/.vscode
    cat > /workspaces/loan-defenders/.vscode/settings.json << 'EOF'
{
    "python.defaultInterpreterPath": "/workspaces/loan-defenders/.venv/bin/python",
    "python.terminal.activateEnvironment": true,
    "terminal.integrated.cwd": "/workspaces/loan-defenders",
    "files.watcherExclude": {
        "**/.git/objects/**": true,
        "**/.git/subtree-cache/**": true,
        "**/node_modules/*/**": true,
        "**/.venv/**": true,
        "**/venv/**": true,
        "**/__pycache__/**": true,
        "**/.pytest_cache/**": true,
        "**/htmlcov/**": true
    }
}
EOF

    # Create launch configuration for debugging
    cat > /workspaces/loan-defenders/.vscode/launch.json << 'EOF'
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Python: Current File",
            "type": "python",
            "request": "launch",
            "program": "${file}",
            "console": "integratedTerminal",
            "cwd": "${workspaceFolder}",
            "env": {
                "PYTHONPATH": "${workspaceFolder}"
            }
        },
        {
            "name": "MCP Server: Application Verification",
            "type": "python",
            "request": "launch",
            "module": "loan_defenders.tools.mcp_servers.application_verification.server",
            "console": "integratedTerminal",
            "cwd": "${workspaceFolder}"
        },
        {
            "name": "Test: Current File",
            "type": "python",
            "request": "launch",
            "module": "pytest",
            "args": ["${file}", "-v"],
            "console": "integratedTerminal",
            "cwd": "${workspaceFolder}"
        }
    ]
}
EOF

    # Make post-create script executable (if needed)
    chmod +x /workspaces/loan-defenders/.devcontainer/post-create.sh 2>/dev/null || true

    # Final success message
    echo ""
    print_header "🎉 Development Environment Setup Complete!"
    echo "================================================================"
    print_success "Loan Defenders development container is ready!"
    echo ""
    echo "🛠️  Available Tools:"
    echo "   • Python 3.11 with UV package manager"
    echo "   • Node.js LTS with npm"
    echo "   • Azure CLI with extensions"
    echo "   • Terraform 1.6.0"
    echo "   • Docker (outside-of-docker)"
    echo "   • GitHub CLI"
    echo "   • Pre-commit hooks"
    echo ""
    echo " Next Steps:"
    echo "   1. Configure Git if not already done"
    echo "   2. Login to Azure CLI"
    echo "   3. Start developing!"
    echo ""
}

# Run main function
main "$@"
