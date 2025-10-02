# Loan Defenders API Architecture

## Overview

The Loan Defenders API exposes our multi-agent loan processing system to user interfaces through a REST API with real-time streaming capabilities. The architecture leverages **Microsoft Agent Framework** for workflow orchestration and conversation state management, aligned with the **Model Context Protocol (MCP)** Streamable HTTP transport pattern.

## System Architecture

```
┌─────────────┐
│     UI      │ (React/TypeScript)
└──────┬──────┘
       │ HTTPS + Entra ID
       │
┌──────▼──────────────────────────────────────┐
│         FastAPI Backend                     │
│  ┌────────────────────────────────────┐    │
│  │    Entra ID Authentication         │    │
│  └────────────────────────────────────┘    │
│  ┌────────────────────────────────────┐    │
│  │   Application Management API       │    │
│  └────────────────────────────────────┘    │
│  ┌────────────────────────────────────┐    │
│  │   Chat API (AgentThread)           │    │
│  └────────────────────────────────────┘    │
│  ┌────────────────────────────────────┐    │
│  │   Streamable HTTP Endpoint         │    │
│  └────────────────────────────────────┘    │
└──────┬──────────────────────────────────────┘
       │
┌──────▼──────────────────────────────────────┐
│  Agent Framework Sequential Workflow        │
│  ┌────┐  ┌────────┐  ┌────────┐  ┌──────┐ │
│  │Int │→│ Credit │→│ Income │→│ Risk │  │
│  │ake │  └────────┘  └────────┘  └──────┘ │
│  └────┘                                     │
│           AgentThread (Conversation State)  │
└──────┬──────────────────────────────────────┘
       │
┌──────▼──────────────────────────────────────┐
│        MCP Servers (Tools)                  │
│  ┌─────────────┐  ┌─────────────┐         │
│  │ Application │  │  Document   │         │
│  │ Verification│  │  Processing │         │
│  └─────────────┘  └─────────────┘         │
└─────────────────────────────────────────────┘

Storage Layer:
- Azure Cache for Redis: AgentThread state (30-min TTL)
- Azure Blob Storage: Document uploads
- Cosmos DB: Completed applications (long-term)
- Azure Key Vault: Secrets and credentials
```

## Core Design Principles

### 1. Agent Framework First

We leverage Microsoft Agent Framework's built-in capabilities rather than building custom infrastructure:

- **SequentialBuilder**: Orchestrates agents in sequential workflow (Intake → Credit → Income → Risk → Decision)
- **AgentThread**: Manages conversation state with built-in ChatMessageStore protocol
- **Workflow.run_stream()**: Streams WorkflowEvents as execution progresses
- **WorkflowEvent types**: ExecutorInvokedEvent, ExecutorCompletedEvent, WorkflowOutputEvent

**Benefits**:
- No custom message queues (Service Bus) needed
- No custom event streaming infrastructure
- Type-safe workflow construction
- Built-in error handling and observability

### 2. Streamable HTTP Transport

Aligned with MCP specification (2025-03-26), our API uses a **single HTTP POST endpoint** that can optionally stream events:

```http
POST /api/v1/applications/{id}/stream
Accept: text/event-stream
Authorization: Bearer <entra-id-token>
Content-Type: application/json

{
  "action": "process",
  "application": {...}
}
```

**Response Modes**:
- **JSON Response**: Single application status object (Accept: application/json)
- **Event Stream**: Server-Sent Events for real-time updates (Accept: text/event-stream)

**Event Format** (JSON-RPC style, aligned with MCP):
```json
{
  "jsonrpc": "2.0",
  "method": "workflow/executor_invoked",
  "params": {
    "executor_id": "intake_agent",
    "timestamp": "2025-09-28T10:30:00Z",
    "input_type": "LoanApplication"
  }
}
```

### 3. Conversation State with AgentThread

Microsoft Agent Framework provides **AgentThread** for conversation state management:

```python
from agent_framework import AgentThread

# Create thread with Redis-backed store
thread = AgentThread(message_store=RedisChatMessageStore(application_id))

# Pass thread to agent (conversation history maintained automatically)
response = await intake_agent.run(user_message, thread=thread)

# Thread contains full conversation history
messages = await thread.message_store.list_messages()
```

**AgentThread provides**:
- Automatic conversation history management
- Serialization/deserialization for persistence
- Thread-per-application isolation
- Type-safe message passing

**Redis Storage**:
- Key: `thread:{application_id}`
- Value: Serialized AgentThread state (ChatMessage list)
- TTL: 30 minutes (session timeout)

### 4. Security by Design

**Authentication**: Entra ID (Azure Active Directory) on every endpoint
- Uses DefaultAzureCredential for Azure-managed identity
- Token validation on every API request
- No API keys or passwords

**Authorization**: Role-based access control
- `loan.apply`: Submit loan applications
- `loan.view`: View own applications
- `loan.admin`: Admin operations

**Data Protection**:
- TLS 1.3 for all connections
- PII encryption at rest (Cosmos DB)
- Secrets in Azure Key Vault
- No SSN in API calls (use applicant_id UUID)
- Audit logging (immutable)

### 5. Cloud-Native Deployment

**Azure Container Apps**:
- Serverless container platform
- Auto-scaling (1-10 replicas based on CPU/memory)
- Integrated with Azure services (Key Vault, Application Insights)
- VNet integration for private networking
- Zero-downtime deployments

## API Endpoints

### Application Management

#### Start New Application
```http
POST /api/v1/applications
Authorization: Bearer <entra-id-token>
Content-Type: application/json

{
  "applicant_name": "Intake Agent Doe",
  "loan_amount": 50000.00,
  "loan_purpose": "home_purchase",
  ...
}

Response 201:
{
  "application_id": "LN1234567890",
  "session_id": "thread_abc123",
  "status": "STARTED",
  "intake_agent": "John_The_Eagle_Eye",
  "initial_message": "Hi! I'm Intake Agent, your application validator...",
  "created_at": "2025-09-28T10:30:00Z"
}
```

#### Get Application Status
```http
GET /api/v1/applications/{id}
Authorization: Bearer <entra-id-token>

Response 200:
{
  "application_id": "LN1234567890",
  "status": "PROCESSING",
  "current_stage": "CREDIT",
  "current_agent": "credit",
  "progress": 0.5,
  "created_at": "2025-09-28T10:30:00Z",
  "updated_at": "2025-09-28T10:35:00Z"
}
```

### Conversational Chat

#### Send Chat Message
```http
POST /api/v1/applications/{id}/chat
Authorization: Bearer <entra-id-token>
Content-Type: application/json

{
  "message": "My annual income is $75,000"
}

Response 200:
{
  "agent_name": "John_The_Eagle_Eye",
  "agent_response": "Great! That's a solid income. Now let's talk about...",
  "assessment": {
    "validation_status": "COMPLETE",
    "routing_decision": "STANDARD",
    "next_agent": "credit",
    ...
  },
  "next_question": "Do you have any existing debt?",
  "workflow_stage": "INTAKE_COMPLETE"
}
```

#### Get Chat History
```http
GET /api/v1/applications/{id}/chat/history
Authorization: Bearer <entra-id-token>

Response 200:
{
  "messages": [
    {
      "role": "assistant",
      "text": "Hi! I'm Intake Agent...",
      "timestamp": "2025-09-28T10:30:00Z"
    },
    {
      "role": "user",
      "text": "My annual income is $75,000",
      "timestamp": "2025-09-28T10:31:00Z"
    },
    ...
  ]
}
```

### Real-Time Streaming

#### Streamable HTTP Endpoint
```http
POST /api/v1/applications/{id}/stream
Accept: text/event-stream
Authorization: Bearer <entra-id-token>

Response 200:
Content-Type: text/event-stream

event: workflow_started
data: {"state": "RUNNING", "timestamp": "2025-09-28T10:30:00Z"}

event: executor_invoked
data: {"executor_id": "intake_agent", "input_type": "LoanApplication"}

event: executor_completed
data: {"executor_id": "intake_agent", "output": {...}}

event: workflow_output
data: {"output_type": "IntakeAssessment", "data": {...}}
```

### Document Upload

#### Upload Document
```http
POST /api/v1/applications/{id}/documents
Authorization: Bearer <entra-id-token>
Content-Type: multipart/form-data

file: <binary>
document_type: "pay_stub"

Response 201:
{
  "document_id": "doc_abc123",
  "filename": "paystub.pdf",
  "size": 524288,
  "document_type": "pay_stub",
  "uploaded_at": "2025-09-28T10:30:00Z"
}
```

## Agent Workflow Orchestration

### Sequential Workflow Pattern

Using Agent Framework's SequentialBuilder:

```python
from agent_framework import SequentialBuilder
from loan_defenders.agents import IntakeAgent, CreditAgent, IncomeAgent, RiskAgent

# Initialize agents
intake_agent = IntakeAgent()
credit_agent = CreditAgent()
income_agent = IncomeAgent()
risk_agent = RiskAgent()

# Build sequential workflow
workflow = SequentialBuilder().participants([
    intake_agent,
    credit_agent,
    income_agent,
    risk_agent,
]).build()

# Execute with streaming
application = LoanApplication(...)
thread = AgentThread(message_store=RedisChatMessageStore(application.application_id))

async for event in workflow.run_stream(application, thread=thread):
    if isinstance(event, WorkflowOutputEvent):
        # Agent produced assessment
        publish_to_client(event.data)
    elif isinstance(event, ExecutorCompletedEvent):
        # Agent finished processing
        update_progress(event.executor_id)
    elif isinstance(event, WorkflowFailedEvent):
        # Handle failure
        handle_error(event.error_details)
```

### Conversation State Flow

```
User Message → FastAPI → Load AgentThread from Redis
                          ↓
                    IntakeAgent.run(message, thread=thread)
                          ↓
                    Agent processes with conversation history
                          ↓
                    AgentThread updated with new messages
                          ↓
                    Save AgentThread to Redis
                          ↓
                    Return response to UI
```

## Error Handling Strategy

### Workflow-Level Errors

Agent Framework provides built-in error handling through WorkflowEvents:

```python
async for event in workflow.run_stream(application):
    if isinstance(event, WorkflowFailedEvent):
        error_details = event.error_details

        # Log error
        logger.error(f"Workflow failed: {error_details.message}")

        # Fallback to manual review
        return create_manual_review_response(application, error_details)
```

### Agent-Level Errors

Individual agents handle errors internally and return fallback assessments:

```python
# IntakeAgent error handling (built-in)
try:
    assessment = await agent.run(application, thread=thread)
except Exception as e:
    # Agent returns fallback IntakeAssessment
    assessment = IntakeAssessment(
        validation_status="FAILED",
        routing_decision="MANUAL",
        processing_notes=f"Processing failed: {str(e)}"
    )
```

### API-Level Errors

FastAPI handles HTTP errors with structured responses:

```json
{
  "error": {
    "code": "AUTHENTICATION_FAILED",
    "message": "Invalid Entra ID token",
    "details": "Token expired at 2025-09-28T10:00:00Z"
  },
  "request_id": "req_abc123",
  "timestamp": "2025-09-28T10:30:00Z"
}
```

## Performance Considerations

### Scaling Strategy

**Horizontal Scaling**:
- Azure Container Apps auto-scales based on CPU/memory
- Each replica is stateless (state in Redis)
- Load balanced automatically

**Agent Workflow**:
- Sequential processing per application (no parallelization needed)
- Agents are lightweight (no pre-warming required)
- MCP servers scale independently

**Caching**:
- AgentThread state cached in Redis (30-min TTL)
- Completed assessments cached for duplicate requests
- Azure Front Door CDN for static assets

### Latency Targets

- **Application creation**: < 200ms
- **Chat response**: < 2 seconds (includes agent processing)
- **Full workflow**: < 30 seconds (all agents)
- **Stream event delivery**: < 100ms

## Deployment Architecture

### Azure Container Apps Configuration

```yaml
apiVersion: 2024-03-01
properties:
  managedEnvironmentId: /subscriptions/.../managedEnvironments/loan-defenders-env
  configuration:
    activeRevisionsMode: Single
    ingress:
      external: true
      targetPort: 8000
      traffic:
        - latestRevision: true
          weight: 100
      corsPolicy:
        allowedOrigins:
          - https://loandefenders.com
        allowedMethods:
          - GET
          - POST
          - DELETE
        allowedHeaders:
          - Authorization
          - Content-Type
          - Accept
      customDomains:
        - name: api.loandefenders.com
          certificateId: /subscriptions/.../certificates/api-cert
    secrets:
      - name: foundry-endpoint
        keyVaultUrl: https://loan-defenders-kv.vault.azure.net/secrets/foundry-endpoint
      - name: redis-connection-string
        keyVaultUrl: https://loan-defenders-kv.vault.azure.net/secrets/redis-connection-string
  template:
    containers:
      - name: loan-defenders-api
        image: loandefendersacr.azurecr.io/loan-defenders-api:latest
        resources:
          cpu: 1.0
          memory: 2Gi
        env:
          - name: FOUNDRY_PROJECT_ENDPOINT
            secretRef: foundry-endpoint
          - name: REDIS_CONNECTION_STRING
            secretRef: redis-connection-string
          - name: APPLICATIONINSIGHTS_CONNECTION_STRING
            secretRef: appinsights-connection-string
        probes:
          liveness:
            httpGet:
              path: /api/v1/health
              port: 8000
            initialDelaySeconds: 10
            periodSeconds: 30
          readiness:
            httpGet:
              path: /api/v1/health
              port: 8000
            initialDelaySeconds: 5
            periodSeconds: 10
    scale:
      minReplicas: 1
      maxReplicas: 10
      rules:
        - name: http-rule
          http:
            metadata:
              concurrentRequests: "100"
        - name: cpu-rule
          custom:
            type: cpu
            metadata:
              value: "70"
```

### Environment Variables

Required environment variables (from Azure Key Vault):

```bash
# Azure AI Foundry
FOUNDRY_PROJECT_ENDPOINT=https://your-project.projects.ai.azure.com
FOUNDRY_MODEL_DEPLOYMENT_NAME=gpt-4

# Azure Cache for Redis
REDIS_CONNECTION_STRING=rediss://loan-defenders-redis.redis.cache.windows.net:6380,...

# Azure Blob Storage
AZURE_STORAGE_CONNECTION_STRING=DefaultEndpointsProtocol=https;...

# Azure Cosmos DB
COSMOS_DB_ENDPOINT=https://loan-defenders-cosmos.documents.azure.com:443/
COSMOS_DB_DATABASE_NAME=loandefenders

# Application Insights
APPLICATIONINSIGHTS_CONNECTION_STRING=InstrumentationKey=...;IngestionEndpoint=https://...

# MCP Servers (internal networking)
MCP_APP_VERIFICATION_PORT=8010
MCP_DOCUMENT_PROCESSING_PORT=8011
MCP_FINANCIAL_CALCULATIONS_PORT=8012

# Security
ALLOWED_ORIGINS=https://loandefenders.com,https://app.loandefenders.com
```

## Observability

### Application Insights Integration

All components send telemetry to Azure Application Insights:

- **API Metrics**: Request rate, latency, error rate
- **Agent Metrics**: Processing time per agent, success rate
- **Workflow Metrics**: Completion rate, average duration
- **Custom Events**: Agent decisions, routing decisions

### Logging Structure

```python
{
  "timestamp": "2025-09-28T10:30:00Z",
  "level": "INFO",
  "logger": "loan_defenders.api",
  "message": "Application processed",
  "application_id": "LN123456****",  # Masked PII
  "agent": "intake",
  "validation_status": "COMPLETE",
  "routing_decision": "STANDARD",
  "tokens_used": 1250,
  "duration_ms": 1850,
  "trace_id": "abc123",
  "span_id": "def456"
}
```

### Monitoring Dashboards

Key metrics to monitor:

1. **API Health**:
   - Request rate (requests/second)
   - Latency (p50, p95, p99)
   - Error rate (%)
   - 4xx vs 5xx errors

2. **Workflow Performance**:
   - Workflow completion rate (%)
   - Average workflow duration (seconds)
   - Agent processing time (seconds per agent)
   - Failure rate by agent

3. **Infrastructure**:
   - Container CPU/memory usage
   - Redis hit rate
   - Blob Storage throughput
   - Cosmos DB RU consumption

## Next Steps

1. Review [API Endpoints Specification](./api-endpoints.md) for detailed endpoint documentation
2. Review [Streaming Protocol](./streaming-protocol.md) for event formats
3. Review [Deployment Guide](./deployment.md) for deployment instructions
4. Review Architecture Decision Records in `docs/decisions/adr-00*.md`