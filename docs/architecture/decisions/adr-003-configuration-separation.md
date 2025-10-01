# ADR-003: Configuration Separation

## Status
Accepted

## Context
The original configuration mixed agent persona definitions with MCP server tool configurations in a single file. This violated the single responsibility principle and made it difficult to manage agent definitions separately from tool configurations. Framework integration would be cleaner with separated concerns.

## Decision
**Separate agent and MCP server configurations into dedicated files** with single responsibility for each configuration type.

## Rationale

### Single Responsibility Principle
Each configuration file should have one clear purpose:
- Agent definitions should not contain tool server details
- MCP server configurations should not be mixed with agent logic
- Framework integration should be able to load configurations independently

### Framework Integration Benefits
Separated configurations enable clean framework integration:
- Load agent personas independently of tool configurations
- Configure MCP servers without agent dependencies
- Override environment-specific settings without affecting agent definitions
- Support different deployment patterns (local, cloud, distributed)

### Maintenance Advantages
Separated configurations improve maintainability:
- Agent persona updates don't affect tool configurations
- MCP server changes don't require agent definition updates
- Environment-specific overrides are clearly scoped
- Configuration validation can be specialized per type

## Implementation

### File Structure
```
loan_processing/config/
├── agents.yaml          # Agent persona mappings only
├── mcp_servers.yaml     # MCP server tool configurations only
└── settings.py          # Configuration loading with overrides
```

### agents.yaml (45 lines)
**Single Responsibility**: Agent persona mappings and MCP server references
```yaml
agent_personas:
  credit:
    file: "credit-agent-persona.md"
    description: "Evaluates creditworthiness and financial risk"
    mcp_servers: ["application_verification", "financial_calculations"]
```

### mcp_servers.yaml (48 lines)
**Single Responsibility**: MCP server tool definitions and connection details
```yaml
servers:
  application_verification:
    host: "localhost"
    port: 8010
    url: "http://localhost:8010/sse"
    tools: ["verify_identity", "get_credit_report", ...]
```

### settings.py (85 lines)
**Single Responsibility**: Configuration loading with environment overrides
```python
class MCPServerConfig:
    @classmethod
    def load_from_yaml(cls, config_path: Path = None) -> "MCPServerConfig":
        # Load from mcp_servers.yaml with env overrides

    def get_server_url(self, server_name: str) -> str:
        # Clean API for framework integration
```

## Benefits

### Clean Framework Integration
Framework code can load configurations independently:
```python
# Microsoft Agent Framework integration
from loan_processing.utils import ConfigurationLoader
from loan_processing.config.settings import get_mcp_config

# Load agent personas
agent_config = ConfigurationLoader.load_config()
personas = agent_config['agent_personas']

# Load MCP server configurations
mcp_config = get_mcp_config()
server_url = mcp_config.get_server_url("application_verification")
```

### Environment Flexibility
MCP server settings can be overridden without touching agent definitions:
```bash
# Override MCP server hosts for production
export MCP_APPLICATION_VERIFICATION_HOST=prod-app-server.com
export MCP_FINANCIAL_CALCULATIONS_HOST=prod-calc-server.com

# Agent personas remain unchanged
```

### Independent Evolution
- **Agent Personas**: Can evolve business logic without affecting tool configs
- **MCP Servers**: Can change endpoints, add tools, modify deployment without agent updates
- **Framework Integration**: Can load different aspects of configuration as needed

## Migration Results

### Before (Mixed Configuration)
Single `agents.yaml` with 74 lines containing:
- Agent definitions
- MCP server configurations
- Provider abstractions
- Complex metadata

### After (Separated Configuration)
- `agents.yaml`: 45 lines of pure agent persona mappings
- `mcp_servers.yaml`: 48 lines of pure MCP server configurations
- `settings.py`: 85 lines of configuration loading logic
- **Total**: Clean separation with specialized APIs

### Configuration Loading
**Framework Integration Pattern**:
```python
# Load agent personas
from loan_processing.utils import ConfigurationLoader
config = ConfigurationLoader.load_config()
agent_personas = config['agent_personas']

# Load MCP servers
from loan_processing.config.settings import get_mcp_config
mcp_config = get_mcp_config()
available_servers = mcp_config.get_available_servers()
server_tools = mcp_config.get_server_tools("credit_assessment")
```

## Framework Integration Examples

### Microsoft Agent Framework
```python
# Load agent persona
personas = ConfigurationLoader.load_config()['agent_personas']
credit_persona_file = personas['credit']['file']
credit_instructions = PersonaLoader.load_persona('credit')

# Configure MCP tools
mcp_config = get_mcp_config()
mcp_servers = personas['credit']['mcp_servers']
for server_name in mcp_servers:
    server_url = mcp_config.get_server_url(server_name)
    # Connect to MCP server as framework tool
```

### OpenAI Assistants
```python
# Same configuration loading, different framework implementation
persona = PersonaLoader.load_persona('income')
assistant = openai.beta.assistants.create(
    instructions=persona,
    tools=[{"type": "function", "function": tool} for tool in mcp_tools]
)
```

## Environment Variable Support

### MCP Server Overrides
```bash
# Override individual server settings
MCP_APPLICATION_VERIFICATION_HOST=staging-server.com
MCP_APPLICATION_VERIFICATION_PORT=9010
MCP_DOCUMENT_PROCESSING_HOST=prod-docs.com
MCP_FINANCIAL_CALCULATIONS_PORT=8015
```

### Configuration Loading Priority
1. **Environment Variables** (highest priority)
2. **YAML Configuration Files** (default values)
3. **Hardcoded Defaults** (fallback)

## Consequences

### Positive
- ✅ **Single Responsibility**: Each file has one clear purpose
- ✅ **Framework Independence**: Load configurations as needed
- ✅ **Environment Flexibility**: Override settings for different deployments
- ✅ **Maintainability**: Changes are scoped to specific concerns
- ✅ **Clean APIs**: Specialized configuration loading methods

### Negative
- ❌ **Multiple Files**: Need to manage two configuration files instead of one
- ❌ **Reference Integrity**: Must ensure agent MCP references match server definitions
- ❌ **Documentation**: Need to document the relationship between files

### Risk Mitigation
- **File Management**: Clear documentation and examples in README
- **Reference Validation**: Configuration loading validates MCP server references
- **Documentation**: Comprehensive examples for framework integration

## Related Decisions
- ADR-001: Multi-Agent Strategic Foundation
- ADR-002: Business Logic First Approach

**Decision Date**: 2024-09-24
**Decision Authors**: Development Team
**Impact**: Configuration separated for clean framework integration and single responsibility