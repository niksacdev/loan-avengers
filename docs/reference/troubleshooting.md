# Troubleshooting Guide

Common issues and solutions for local development of the Loan Defenders system.

## CORS Configuration Issues

### Problem: "I'm sorry, I'm having trouble connecting right now"

**Symptoms:**
- UI displays connection error message
- Browser console shows CORS preflight errors
- API returns 400 Bad Request on OPTIONS requests

**Root Cause:**
The frontend is running on a port that's not included in the API's CORS allowed origins.

**Solution:**

1. Check which port your frontend is running on:
   ```bash
   # Look for "Local: http://localhost:XXXX" in the terminal
   cd apps/ui
   npm run dev
   ```

2. Edit the root `.env` file and add your port to `APP_CORS_ORIGINS`:
   ```bash
   # Add your port to the comma-separated list
   APP_CORS_ORIGINS="http://localhost:5173,http://localhost:5174,http://localhost:5175,http://localhost:3000"
   ```

3. Restart the API server:
   ```bash
   # Kill existing API process
   ps aux | grep "loan_defenders.api.app" | grep -v grep | awk '{print $2}' | xargs kill

   # Start API server
   cd apps/api
   uv run python -m loan_defenders.api.app
   ```

4. Verify the API health:
   ```bash
   curl http://localhost:8000/health
   # Should return: {"status":"healthy"}
   ```

!!! tip "Common Frontend Ports"
    Vite usually assigns ports sequentially: 5173, 5174, 5175, etc. If one port is in use, it automatically tries the next available port.

---

## Port Already in Use

### Problem: "Address already in use" or "Port XXXX is already allocated"

**Symptoms:**
- Server fails to start
- Error message mentions specific port number
- `lsof` shows process using the port

**Solution:**

1. **Check which ports are in use:**
   ```bash
   # Check API port
   lsof -i :8000

   # Check MCP server ports
   lsof -i :8010
   lsof -i :8011
   lsof -i :8012

   # Check frontend port
   lsof -i :5173
   ```

2. **Kill the process using the port:**
   ```bash
   # Option 1: Kill by PID (from lsof output)
   kill -9 <PID>

   # Option 2: Kill all API server processes
   ps aux | grep "loan_defenders.api.app" | grep -v grep | awk '{print $2}' | xargs kill

   # Option 3: Kill all MCP server processes
   pkill -f "loan_defenders.tools.mcp_servers"
   ```

3. **Restart the affected service**

!!! warning "Force Kill"
    Using `kill -9` forcefully terminates processes. Only use this if graceful shutdown (`kill` without `-9`) doesn't work.

---

## Environment Variables Not Loading

### Problem: "AZURE_AI_PROJECT_ENDPOINT not set" or similar environment variable errors

**Symptoms:**
- API fails to start with missing environment variable errors
- MCP servers can't connect
- Azure authentication fails

**Root Cause:**
Environment variables are not being loaded from the `.env` file.

**Solution:**

1. **Verify `.env` file exists in project root:**
   ```bash
   ls -la /workspaces/loan-defenders/.env
   ```

2. **If missing, create from template:**
   ```bash
   cd /workspaces/loan-defenders
   cp .env.example .env
   ```

3. **Edit `.env` with your Azure credentials:**
   ```bash
   # Required fields
   AZURE_AI_PROJECT_ENDPOINT=https://your-resource.services.ai.azure.com/api/projects/your-project
   AZURE_AI_MODEL_DEPLOYMENT_NAME=your-deployment-name
   ```

4. **Verify environment variables are loaded:**
   ```bash
   # API should print this on startup:
   # [INFO] Loaded environment variables from /workspaces/loan-defenders/.env
   ```

!!! tip "Environment Variable Hierarchy"
    The API loads environment variables in this order:
    1. System environment variables (highest priority)
    2. Root `.env` file
    3. Default values in code (lowest priority)

---

## Azure Authentication Errors

### Problem: "DefaultAzureCredential failed to retrieve a token" or authentication errors

**Symptoms:**
- API starts but fails when processing loan applications
- Azure SDK authentication errors in logs
- 401 Unauthorized responses from Azure

**Solution:**

1. **Verify Azure CLI is logged in:**
   ```bash
   az login
   az account show
   ```

2. **Test Azure credentials:**
   ```bash
   uv run python -c "from azure.identity import DefaultAzureCredential; DefaultAzureCredential().get_token('https://cognitiveservices.azure.com/.default')"
   ```

3. **Check `.env` configuration:**
   ```bash
   # Verify these are set correctly
   AZURE_AI_PROJECT_ENDPOINT=https://your-resource.services.ai.azure.com/api/projects/your-project
   AZURE_AI_MODEL_DEPLOYMENT_NAME=your-deployment-name
   ```

4. **For CI/CD environments, set service principal credentials:**
   ```bash
   export AZURE_TENANT_ID=your-tenant-id
   export AZURE_CLIENT_ID=your-client-id
   export AZURE_CLIENT_SECRET=your-client-secret
   ```

!!! info "DefaultAzureCredential Chain"
    DefaultAzureCredential tries these authentication methods in order:
    1. Environment variables (service principal)
    2. Managed identity (Azure hosted)
    3. Azure CLI credentials (`az login`)
    4. Visual Studio Code credentials
    5. Azure PowerShell credentials

---

## Module Not Found Errors

### Problem: "ModuleNotFoundError" or "No module named 'loan_defenders'"

**Symptoms:**
- Import errors when running Python scripts
- Tests fail with module not found
- `uv run` commands fail

**Solution:**

1. **Reinstall dependencies:**
   ```bash
   cd /workspaces/loan-defenders
   uv sync --no-cache
   ```

2. **Verify Python path:**
   ```bash
   # Should include project root
   echo $PYTHONPATH
   ```

3. **Check `pyproject.toml` configuration:**
   ```bash
   cat pyproject.toml | grep -A 5 "\[project\]"
   ```

4. **For frontend module errors:**
   ```bash
   cd apps/ui
   rm -rf node_modules package-lock.json
   npm install
   ```

!!! tip "Clean Install"
    If issues persist, perform a complete clean install:
    ```bash
    # Backend
    rm -rf .venv
    uv sync

    # Frontend
    cd apps/ui
    rm -rf node_modules package-lock.json
    npm ci
    ```

---

## MCP Server Connection Failures

### Problem: "Failed to connect to MCP server" or timeouts

**Symptoms:**
- Loan processing hangs or fails
- Agent logs show MCP server connection errors
- Timeout errors in API logs

**Solution:**

1. **Verify all MCP servers are running:**
   ```bash
   # Check if servers are listening on correct ports
   lsof -i :8010  # Application Verification
   lsof -i :8011  # Document Processing
   lsof -i :8012  # Financial Calculations
   ```

2. **Check MCP server logs for errors:**
   - Look at the terminal windows where you started the servers
   - Check for startup errors or exceptions

3. **Verify MCP server URLs in `.env`:**
   ```bash
   # Should use localhost for local development
   MCP_APPLICATION_VERIFICATION_URL=http://localhost:8010/mcp
   MCP_DOCUMENT_PROCESSING_URL=http://localhost:8011/mcp
   MCP_FINANCIAL_CALCULATIONS_URL=http://localhost:8012/mcp
   ```

4. **Test MCP server connectivity:**
   ```bash
   # Test each server endpoint
   curl http://localhost:8010/health
   curl http://localhost:8011/health
   curl http://localhost:8012/health
   ```

5. **Restart all MCP servers:**
   ```bash
   # Kill existing processes
   pkill -f "loan_defenders.tools.mcp_servers"

   # Start servers in separate terminals
   uv run python -m loan_defenders.tools.mcp_servers.application_verification.server
   uv run python -m loan_defenders.tools.mcp_servers.document_processing.server
   uv run python -m loan_defenders.tools.mcp_servers.financial_calculations.server
   ```

!!! warning "MCP Server Dependencies"
    All three MCP servers must be running before starting the API server. The API won't start if it can't connect to the MCP servers.

---

## Frontend Build Errors

### Problem: TypeScript compilation errors or build failures

**Symptoms:**
- `npm run dev` fails
- TypeScript type errors in console
- Build hangs or times out

**Solution:**

1. **Clear TypeScript cache:**
   ```bash
   cd apps/ui
   rm -rf node_modules/.vite
   rm -rf dist
   ```

2. **Reinstall dependencies:**
   ```bash
   rm -rf node_modules package-lock.json
   npm install
   ```

3. **Check TypeScript configuration:**
   ```bash
   cat tsconfig.json
   ```

4. **Update dependencies to latest compatible versions:**
   ```bash
   npm update
   ```

---

## Slow Agent Response Times

### Problem: Agent processing takes 30+ seconds or responses are very slow

**Symptoms:**
- Long wait times during loan processing
- UI shows "analyzing" for extended periods
- High token usage in logs

**Root Cause:**
Agent personas may be too large or verbose, causing excessive token consumption.

**Solution:**

1. **Check agent persona file sizes:**
   ```bash
   wc -l apps/api/loan_defenders/agents/agent-persona/*.md
   ```

2. **Personas should be 300-500 lines max**, not 2000+

3. **Review persona content:**
   - Remove verbose explanations
   - Focus on clear directives (WHAT not HOW)
   - Link to external docs instead of inline explanations

4. **Monitor token usage in API logs**

!!! tip "Token Optimization"
    Reducing persona files from 2000+ lines to 300-500 focused lines can result in 75% token reduction and 10x faster agent responses.

---

## Database or State Issues

### Problem: Session not found, state inconsistencies, or cached data issues

**Symptoms:**
- "Session not found" errors
- Loan applications show stale data
- Agents process incorrect information

**Solution:**

1. **Clear session data** (API maintains in-memory sessions):
   ```bash
   # Restart the API server to clear sessions
   ps aux | grep "loan_defenders.api.app" | grep -v grep | awk '{print $2}' | xargs kill
   uv run python -m loan_defenders.api.app
   ```

2. **Clear browser storage:**
   - Open browser DevTools (F12)
   - Application tab → Clear storage
   - Refresh the page

3. **Check session timeout configuration in `.env`:**
   ```bash
   APP_SESSION_TIMEOUT_HOURS=24
   APP_SESSION_CLEANUP_INTERVAL_HOURS=6
   ```

---

## Still Having Issues?

If none of these solutions work:

1. **Check the logs** for detailed error messages:
   - API logs in the terminal running `loan_defenders.api.app`
   - MCP server logs in their respective terminals
   - Browser console logs (F12 → Console)

2. **Search existing issues**: [GitHub Issues](https://github.com/niksacdev/loan-defenders/issues)

3. **Create a new issue** with:
   - Detailed description of the problem
   - Steps to reproduce
   - Error messages and logs
   - Environment details (OS, Python version, Node version)

4. **Join discussions**: [GitHub Discussions](https://github.com/niksacdev/loan-defenders/discussions)

---

## Useful Debugging Commands

```bash
# Check all service health
curl http://localhost:8000/health  # API
curl http://localhost:8010/health  # MCP Application Verification
curl http://localhost:8011/health  # MCP Document Processing
curl http://localhost:8012/health  # MCP Financial Calculations

# View running processes
ps aux | grep loan_defenders
ps aux | grep node

# Check port usage
lsof -i :8000
lsof -i :8010-8012
lsof -i :5173

# Test Azure authentication
uv run python -c "from azure.identity import DefaultAzureCredential; print(DefaultAzureCredential().get_token('https://cognitiveservices.azure.com/.default'))"

# Validate environment
cat .env | grep -v "^#" | grep -v "^$"

# Check Python environment
uv run python --version
uv pip list

# Check Node environment
node --version
npm --version
npm list --depth=0
```
