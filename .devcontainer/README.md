# 🚀 Loan Avengers Dev Container

This development container provides a complete, consistent development environment for the Loan Avengers project with all necessary tools pre-installed.

## 🛠️ What's Included

### **Core Development Tools**
- **Python 3.11** with UV package manager
- **Azure CLI** with extensions (containerapp, azure-devops, application-insights)
- **Terraform 1.6.0** for infrastructure management
- **Docker** (outside-of-docker) for container operations
- **GitHub CLI** for repository management

### **VS Code Extensions**
- **Python Development**: Python, Ruff (linting/formatting), Pytest
- **Azure & Infrastructure**: Azure Account, Terraform, Azure DevOps
- **DevOps & Git**: GitHub Copilot, GitLens, Pull Request management
- **Quality & Testing**: Ruff, Pytest, Test Explorer

### **Development Aliases & Commands**
```bash
# Loan Avengers specific
loan-dev          # Show available development commands
loan-test         # Run interactive test suite
start-mcp         # Start MCP application verification server
coverage          # Run coverage analysis

# Python/UV shortcuts
py                # uv run python
pytest            # uv run pytest
ruff-check        # uv run ruff check .
ruff-fix          # uv run ruff check . --fix
ruff-format       # uv run ruff format .

# Azure shortcuts
az-login          # az login --use-device-code
az-accounts       # az account list --output table

# Terraform shortcuts
tf                # terraform
tfinit            # terraform init
tfplan            # terraform plan
tfapply           # terraform apply
tfdestroy         # terraform destroy

# Git shortcuts
gst               # git status
glog              # git log --oneline --graph --decorate
gpush             # git push origin HEAD
```

## 🚀 Getting Started

### **1. Open in Dev Container**
```bash
# Using VS Code
# 1. Install "Dev Containers" extension
# 2. Open loan-avengers folder in VS Code
# 3. Command Palette (Cmd/Ctrl+Shift+P) > "Dev Containers: Reopen in Container"

# Using GitHub Codespaces
# 1. Go to GitHub repository
# 2. Click "Code" > "Codespaces" > "Create codespace on main"
```

### **2. First Time Setup**
```bash
# The post-create script runs automatically, but you may need to:

# Configure Git (if not already done)
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"

# Login to Azure (for Azure development)
az login

# Verify environment
loan-dev
```

### **3. Development Workflow**
```bash
# Run tests
loan-test

# Start MCP server for testing
start-mcp

# Run coverage analysis
coverage

# Check code quality
ruff-check

# Run specific test categories
uv run python tests/test_suite_runner.py
```

## 📁 **Container Configuration**

### **Port Forwarding**
- `8000` - FastAPI application
- `8010` - MCP Application Verification Server
- `8011` - MCP Document Processing Server (future)
- `8012` - MCP Financial Calculations Server (future)
- `5000` - General development server

### **Volume Mounts**
- **Project files**: Entire project mounted at `/workspaces/loan-avengers`
- **Azure config**: `~/.azure` mounted for Azure CLI persistence
- **SSH keys**: `~/.ssh` mounted for Git operations
- **VS Code extensions**: Persistent volume for extension data

### **Environment Variables**
- `PYTHONPATH=/workspaces/loan-avengers`
- `ENVIRONMENT=development`
- `UV_CACHE_DIR=/tmp/uv-cache`
- `AZURE_CLI_DISABLE_CONNECTION_VERIFICATION=1`

## 🔧 **Customization**

### **Adding Extensions**
Edit `.devcontainer/devcontainer.json` and add to the `extensions` array:
```json
"extensions": [
    "your-extension-id"
]
```

### **Adding System Packages**
Edit `.devcontainer/post-create.sh` and add to the apt-get install command:
```bash
sudo apt-get install -y -qq your-package
```

### **Adding Python Packages**
Use UV in the container:
```bash
uv add your-package
uv add --dev your-dev-package
```

### **Adding Aliases**
Edit `.devcontainer/post-create.sh` and add to the zshrc section:
```bash
alias your-alias='your-command'
```

## 🐛 **Troubleshooting**

### **Container Won't Start**
- Check Docker is running on host
- Ensure VS Code has Dev Containers extension
- Try rebuilding: Command Palette > "Dev Containers: Rebuild Container"

### **Python Dependencies Issues**
```bash
# Reinstall dependencies
uv sync --reinstall

# Clear UV cache
rm -rf /tmp/uv-cache/*
uv sync
```

### **Azure CLI Issues**
```bash
# Re-login to Azure
az logout
az login --use-device-code

# Check Azure CLI version
az version
```

### **VS Code Extensions Not Loading**
- Rebuild container
- Check internet connectivity
- Manually install extensions: Ctrl+Shift+X > search and install

### **Permission Issues**
```bash
# Fix file permissions
sudo chown -R vscode:vscode /workspaces/loan-avengers
```

## 📊 **Performance Tips**

### **Faster Rebuilds**
- Use `.dockerignore` to exclude unnecessary files
- Layer Docker commands efficiently
- Use multi-stage builds for complex setups

### **Optimize UV Cache**
```bash
# Check cache size
du -sh /tmp/uv-cache

# Clear cache if needed
uv cache clean
```

### **VS Code Performance**
- Disable unused extensions
- Use file watcher exclusions (already configured)
- Close unused editor tabs

## 🔗 **Related Documentation**

- **Development Setup**: See `README.md` in project root
- **Testing Guide**: See `tests/README.md`
- **Azure Deployment**: See `docs/deployment/azure-secure-deployment-guide.md`
- **Architecture**: See `docs/technical-specification.md`

## 🎯 **Next Steps**

1. **Explore the codebase**: Start with `loan_avengers/` directory
2. **Run tests**: Use `loan-test` to understand the test suite
3. **Start MCP server**: Use `start-mcp` to test integration
4. **Azure setup**: Follow Azure deployment guide for cloud development
5. **Contribute**: See contributing guidelines in project root

The dev container gives you everything needed to start developing the Loan Avengers system immediately! 🦸‍♂️