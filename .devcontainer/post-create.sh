#!/bin/bash
# 🚀 Loan Avengers Dev Container - Post Creation Setup Script
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
    print_header "🚀 Setting up Loan Avengers Development Environment"
    echo "================================================================"
    
    # Update system packages
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
        build-essential
    
    # Install UV package manager (Python)
    print_status "Installing UV package manager..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    export PATH="$HOME/.cargo/bin:$PATH"
    
    # Install Python dependencies
    print_status "Installing Python dependencies with UV..."
    cd /workspaces/loan-avengers
    
    if [ -f "pyproject.toml" ]; then
        uv sync
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
    
    # Setup Azure CLI extensions
    print_status "Installing Azure CLI extensions..."
    az extension add --name azure-devops --yes 2>/dev/null || true
    az extension add --name containerapp --yes 2>/dev/null || true
    az extension add --name application-insights --yes 2>/dev/null || true
    
    # Setup shell aliases and functions
    print_status "Setting up development aliases..."
    cat >> /home/vscode/.zshrc << 'EOF'

# Loan Avengers Development Aliases
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

# Loan Avengers specific
alias start-mcp='uv run python -m loan_avengers.tools.mcp_servers.application_verification.server'
alias test-unit='uv run pytest tests/unit/ -v'
alias test-integration='uv run pytest tests/integration/ -v'
alias test-all='uv run pytest tests/ -v'
alias coverage='uv run python tests/coverage_report.py'

# Function to quickly run the test suite
loan-test() {
    echo "🧪 Running Loan Avengers Test Suite..."
    uv run python tests/test_suite_runner.py "$@"
}

# Function to start development environment
loan-dev() {
    echo "🚀 Starting Loan Avengers Development Environment..."
    echo "Available commands:"
    echo "  loan-test [type] - Run test suite"
    echo "  start-mcp        - Start MCP server"
    echo "  coverage         - Run coverage analysis"
    echo "  ruff-check       - Run code quality checks"
}

# Welcome message
echo "🦸‍♂️ Welcome to the Loan Avengers Development Environment!"
echo "Type 'loan-dev' for available development commands"
EOF

    # Create development workspace directories
    print_status "Creating workspace directories..."
    mkdir -p /workspaces/loan-avengers/{logs,temp,docs/notes}
    
    # Setup VS Code workspace settings
    print_status "Setting up VS Code workspace..."
    mkdir -p /workspaces/loan-avengers/.vscode
    cat > /workspaces/loan-avengers/.vscode/settings.json << 'EOF'
{
    "python.defaultInterpreterPath": "/workspaces/loan-avengers/.venv/bin/python",
    "python.terminal.activateEnvironment": true,
    "terminal.integrated.cwd": "/workspaces/loan-avengers",
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
    cat > /workspaces/loan-avengers/.vscode/launch.json << 'EOF'
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
            "module": "loan_avengers.tools.mcp_servers.application_verification.server",
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

    # Fix permissions
    print_status "Fixing file permissions..."
    sudo chown -R vscode:vscode /workspaces/loan-avengers
    chmod +x /workspaces/loan-avengers/.devcontainer/post-create.sh
    
    # Final success message
    echo ""
    print_header "🎉 Development Environment Setup Complete!"
    echo "================================================================"
    print_success "Loan Avengers development container is ready!"
    echo ""
    echo "🛠️  Available Tools:"
    echo "   • Python 3.11 with UV package manager"
    echo "   • Azure CLI with extensions"
    echo "   • Terraform 1.6.0"
    echo "   • Docker (outside-of-docker)"
    echo "   • GitHub CLI"
    echo "   • Pre-commit hooks"
    echo ""
    echo "🚀 Quick Start:"
    echo "   • Run 'loan-dev' for development commands"
    echo "   • Run 'loan-test' to run the test suite"
    echo "   • Run 'az login' to authenticate with Azure"
    echo "   • Run 'start-mcp' to start the MCP server"
    echo ""
    echo "📚 Next Steps:"
    echo "   1. Configure Git if not already done"
    echo "   2. Login to Azure CLI"
    echo "   3. Start developing!"
    echo ""
}

# Run main function
main "$@"