# Architecture & Development Workflow Diagrams

This directory contains comprehensive architecture diagrams and revolutionary AI-augmented development workflow visualizations for the Loan Avengers multi-agent system.

## AI-Augmented Development Workflow Diagrams (NEW)

### Development Process Innovation
These diagrams document the revolutionary shift from traditional multi-disciplinary human teams to human-AI collaborative development, achieving 10x productivity gains.

#### 1. [Development Workflow Comparison](./development-workflow-comparison.mermaid)
**High-level comparison** between traditional teams (8-12 specialists, weeks) vs AI-augmented workflow (1 human + AI agents, hours).

#### 2. [Workflow Phases Detailed](./workflow-phases-detailed.mermaid)  
**Phase-by-phase breakdown** showing time and resource differences:
- Ideation & Conceptualization: Weeks → Hours
- Specification & Design: Days → Minutes  
- Implementation: Sequential weeks → Parallel days
- Review & Testing: Review bottlenecks → Multi-layer AI validation

#### 3. [AI Agent Orchestration](./ai-agent-orchestration.mermaid)
**Detailed orchestration architecture** showing human coordination of specialized agents across Strategy, Design, Development, Quality, and Integration layers.

## System Architecture Diagrams

## Available Diagrams

### Mermaid Diagrams
- **[System Architecture](./system-architecture-diagram.md)** - Complete end-to-end agent workflow and component interactions
- **[Azure Deployment Architecture](./azure-deployment-architecture.md)** - Complete cloud infrastructure and deployment topology

### Draw.io Professional Specifications
- **[System Architecture Draw.io Spec](./system-architecture-drawio-spec.md)** - Detailed specifications for creating professional system diagram
- **[Azure Deployment Draw.io Spec](./azure-deployment-drawio-spec.md)** - Detailed specifications for creating professional Azure deployment diagram
- **[Draw.io Quick Start Guide](./drawio-quick-start.md)** - Step-by-step instructions for creating the diagrams

## Converting to Draw.io Format

The mermaid diagrams can be converted to Draw.io format using the `drawio-mcp-server` tool for enhanced editing and presentation capabilities.

### Prerequisites
1. **Node.js** v20 or higher
2. **Draw.io Browser Extension** - [Chrome](https://chrome.google.com/webstore/detail/drawio-mcp-extension/okdbbjbbccdhhfaefmcmekalmmdjjide) or [Firefox](https://addons.mozilla.org/en-US/firefox/addon/drawio-mcp-extension/)
3. **MCP Client** (Claude Desktop, Zed, or MCP Inspector)

### Setup Instructions

#### 1. Install Draw.io MCP Server
```bash
# Clone and build the server (already completed in /tmp/drawio-mcp-server)
cd /tmp/drawio-mcp-server
npm install
npm run build
```

#### 2. Configure MCP Client

For **Claude Desktop**, add to `~/Library/Application Support/Claude/claude_desktop_config.json`:
```json
{
  "mcpServers": {
    "drawio": {
      "command": "node",
      "args": ["/tmp/drawio-mcp-server/build/index.js"]
    }
  }
}
```

For **Zed Editor**, add to Assistant Settings:
```json
{
  "drawio": {
    "command": {
      "path": "node",
      "args": ["/tmp/drawio-mcp-server/build/index.js"],
      "env": {}
    }
  }
}
```

#### 3. Browser Extension Setup
1. Open [Draw.io](https://app.diagrams.net/) in your browser
2. Install the Draw.io MCP Browser Extension
3. Ensure extension shows green connection indicator

### Conversion Process

Once setup is complete, you can use Claude with the drawio-mcp-server to convert diagrams:

#### System Architecture Diagram
```
Create a Draw.io diagram based on the system architecture from docs/diagrams/system-architecture-diagram.md.

The diagram should include:
- User Experience Layer (React UI with Alisha coordinator)
- API Gateway Layer (FastAPI with streaming)
- Microsoft Agent Framework workflow (Intake Agent → Hawk-Income → Scarlet Witch-Credit → Doctor Strange-Risk)
- MCP Tool Integration (3 servers on ports 8010-8012)
- Data Models & State Management (Pydantic, AgentThread, Redis)
- External Service Integration (Azure OpenAI, Credit APIs, Banking APIs)

Use proper grouping, colors, and connections to show the sequential agent workflow and tool interactions.
```

#### Azure Deployment Architecture
```
Create a Draw.io diagram based on the Azure deployment architecture from docs/diagrams/azure-deployment-architecture.md.

The diagram should include:
- Global Layer (Azure Front Door, CDN, Entra ID)
- Application Layer (Container Apps Environment with UI, API, and MCP servers)
- Data Layer (Redis Cache, Blob Storage, Cosmos DB)
- Security Layer (Key Vault, Managed Identity, Private Networking)
- DevOps Layer (Container Registry, GitHub Actions)
- External Integrations (Azure OpenAI, Credit Bureau APIs, Banking APIs)

Use Azure-standard icons and colors for professional presentation.
```

### Available Draw.io Tools

The MCP server provides these tools for diagram creation:
- `add-rectangle` - Create boxes/containers
- `add-edge` - Create connections between components
- `add-cell-of-shape` - Add specific shapes from Draw.io library
- `get-shape-categories` - Browse available shape libraries
- `list-paged-model` - Inspect current diagram structure

### Professional Presentation Tips

When creating Draw.io versions:
1. **Use consistent colors** - Group related components with similar colors
2. **Add proper labels** - Include component names and key technologies
3. **Show data flow** - Use arrows to indicate workflow direction
4. **Include legends** - Explain color coding and symbols used
5. **Layer information** - Use different detail levels for different audiences

## Benefits of Draw.io Format

- **Professional presentation** - Publication-ready diagrams for stakeholders
- **Interactive editing** - Easy to modify and update as system evolves
- **Multiple export formats** - PNG, SVG, PDF for documentation
- **Collaboration features** - Share and collaborate with team members
- **Version control** - Export as XML for git-friendly version tracking

## Usage in Documentation

Once converted, the Draw.io diagrams can be:
- Embedded in technical specifications
- Included in stakeholder presentations
- Used for architecture review meetings
- Referenced in ADR (Architecture Decision Record) documents
- Shared with development teams for implementation guidance