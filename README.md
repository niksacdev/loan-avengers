# 🦸‍♂️ The Loan Avengers

A multi-agent loan processing system built that transforms traditional loan applications into a conversational experience using personality-driven AI agents.

> **⚠️ Experimental Application**: This is a sample demonstrating **Microsoft Agent Framework** and **Azure AI Foundry** capabilities through a practical multi-agent loan processing scenario. It highlights AI agent architecture patterns, secure cloud deployment, and AI-augmented agent development practices.
## 🎬 **How It Works**

### **The Avengers Assembly Sequence**
```
User: "I need 250K for this house I'm looking at"

🦸‍♂️ Cap-ital America: "That's exciting! Let me get my team to help you.
                      AVENGERS, ASSEMBLE! 🦅"

🦸‍♂️ Cap-ital America: [Streaming] "Eagle eyes engaged! 🦅 Scanning application data..."
🦸‍♂️ Cap-ital America: [Streaming] "Everything looks sharp! No missing pieces!"
🦸‍♂️ Cap-ital America: "Perfect! Specialists, this application is pristine - take it away!"

💼 Hawk-Income: "Thanks! I see you're crushing it with your $85k income!
                Let me verify those amazing earnings..."

📊 Scarlet Witch-Credit: "Hawk-Income shared great news about your income stability!
                         Your credit score is opening doors - let me show you what's possible!"

🛡️ Doctor Strange-Risk: "Scarlet Witch-Credit found solid credit strength! This loan fits well
                        with your financial goals. Let me finalize the terms..."

🦸‍♂️ Cap-ital America: "🎊 MISSION COMPLETE! Your loan application has been approved!"
```

## 🦸‍♂️ **Meet the Avengers**

### **🦸‍♂️ Cap-ital America - Loan Orchestrator**
- **Role**: Coordinates the entire loan application experience
- **Superpower**: Natural conversation and team coordination
- **Mission**: Collect application details through friendly conversation
- **Note**: AI assistant designed to help with loan applications

### **💼 Hawk-Income - Income Specialist**
- **Superpower**: Income verification and employment validation
- **Mission**: Verifies earnings, employment stability, and income adequacy
- **Tools**: Employment verification, document processing, financial calculations
- **Note**: AI assistant for comprehensive income verification

### **📊 Scarlet Witch-Credit - Credit Analyst**
- **Superpower**: Credit assessment and mystical credit analysis
- **Mission**: Credit history evaluation, identity verification, risk scoring
- **Tools**: Credit bureau integration, identity verification, financial calculations
- **Note**: AI assistant designed to analyze credit profiles

### **🛡️ Doctor Strange-Risk - Risk Assessor**
- **Superpower**: Dimensional risk analysis and comprehensive evaluation
- **Mission**: Final risk evaluation and loan recommendation synthesis
- **Tools**: All MCP servers for complete risk assessment
- **Note**: AI system providing advisory risk recommendations

## 🚀 **Capabilities**

### **🔄 Agent Framework Workflow**
Built with Microsoft Agent Framework leveraging Workflows, Agents, and Threads for orchestrated multi-agent collaboration
- Sequential agent coordination with automatic handoffs
- Context-aware processing across specialized agents
- Real-time state management and progress tracking

### **🔧 Agent-to-MCP Tools Integration**
Seamless integration between AI agents and Model Context Protocol (MCP) servers for specialized tool capabilities
- **3 specialized MCP servers**: Application verification, document processing, financial calculations
- **Streamable HTTP transport**: Real-time progress updates during agent execution
- **Autonomous tool selection**: Agents independently choose appropriate tools based on their assessment needs

### **🔒 Secure Azure Deployment**
Production-ready deployment architecture using Azure Container Apps with enterprise-grade security
- **Azure Container Apps**: Scalable, serverless container hosting
- **Entra ID authentication**: Enterprise identity and access management
- **Managed identities**: Secure, credential-free service authentication
- **Agent Framework observability**: Built-in telemetry and performance tracking across all agents

### **🤖 Agents Built by Agents**
Revolutionary AI-augmented development workflow using specialized developer agents
- **Multi-platform AI support**: Compatible with GitHub Copilot, Claude Code, Cursor, and universal AGENTS.md format
- **System architecture review**: AI agents validate design decisions and architectural patterns
- **Automated code review**: AI agents ensure best practices and code quality standards
- **Single developer productivity**: Achieves 8-12 person team output through AI-augmented workflow

### **Multi-Agent Workflow System**
Built on **Microsoft Agent Framework** with sequential agent processing:

```
Web App → Loan Coordinator → Intake Agent (Validation) → Income Agent → Credit Agent → Risk Agent → Result
```

### **Core Technologies**
- **Microsoft Agent Framework**: Multi-agent orchestration and workflow management
- **Pydantic v2**: Type-safe data models with comprehensive validation
- **MCP Servers**: External tool integration for verification and calculations
- **Real-time Streaming**: Live progress updates during agent processing
- **Agent Framework Observability**: Built-in telemetry and performance tracking

### **Microsoft Agent Framework Capabilities Used**
- **ChatAgent**: Personality-driven agent creation with structured responses
- **AgentThread**: Conversation context management for multi-turn interactions
- **Workflow Orchestration**: Sequential agent processing with automatic handoffs
- **Real-time Streaming**: Live progress updates during agent execution
- **Built-in Observability**: Automatic telemetry, usage tracking, and performance monitoring
- **Pydantic Integration**: Type-safe response parsing with `response_format` parameter
- **MCP Tool Integration**: External service connections for verification and calculations

## 🎯 **Performance Goals**

### **Loan Processing Targets**
- **Intake Agent (Validation)**: <5 seconds application validation and routing
- **Income Agent**: <30 seconds income verification and employment validation
- **Credit Agent**: <60 seconds credit assessment and scoring
- **Risk Agent**: <90 seconds comprehensive risk analysis and decision
- **Total Workflow**: <3 minutes end-to-end processing vs traditional 24-48 hours

### **Technical Benefits**
- **Agent Specialization**: Each agent focused on specific domain expertise
- **Workflow Orchestration**: Microsoft Agent Framework handles complex coordination
- **Observability**: Built-in telemetry and performance monitoring
- **Scalability**: Independent agent scaling based on processing bottlenecks

## 🚀 **Quick Start**

### **Prerequisites**
- Python 3.10+
- Azure OpenAI API access
- MCP server dependencies

### **Setup**
```bash
# Install dependencies
uv sync

# Configure credentials
cp .env.example .env
# Add your Azure OpenAI credentials

# Test the Avengers
uv run test_intake_agent.py
```
## 📚 **Documentation**

- **[Technical Specification](docs/technical-specification.md)** - Complete system architecture
- **[Business Case](docs/product/business-case.md)** - Implementation strategy and ROI
- **[Agent Personas](loan_avengers/agents/agent-persona/)** - Individual agent instructions

## 🎯 **Future Enhancements**

- **Voice Integration**: Voice-activated agent assembly
- **Advanced Workflows**: Complex loan types and conditional processing
- **Additional Agents**: Specialized agents for different financial products

---

**🦸‍♂️ The Loan Avengers
