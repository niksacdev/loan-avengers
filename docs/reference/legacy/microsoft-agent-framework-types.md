# Microsoft Agent Framework Architecture Deep Dive

## Overview

The Microsoft Agent Framework provides a comprehensive architecture for building enterprise multi-agent AI applications. This document explains the core components, their underlying protocols, architectural patterns, and practical usage for our loan processing system.

## Architectural Philosophy

The framework follows several key design principles:

1. **Protocol-Driven Design**: Uses protocols/interfaces for type safety and extensibility
2. **Composition Over Inheritance**: Agents are composed of chat clients, tools, and middleware
3. **Async-First**: Built for high-performance async operations
4. **Pydantic-Based**: Leverages Pydantic v2 for data validation and serialization
5. **Pregel-Like Workflows**: Graph-based execution model inspired by Google's Pregel system
6. **MCP Native**: First-class support for Model Context Protocol (MCP) servers

## Core Agent Architecture

### 1. BaseAgent - Foundation Layer

```python
from agent_framework import BaseAgent

class BaseAgent(AFBaseModel):
    """
    Foundation class built on Pydantic v2 providing:
    
    Core Fields:
    - id: str - Unique agent identifier (auto-generated UUID)
    - name: str | None - Human-readable agent name
    - description: str | None - Agent purpose description
    - context_providers: ContextProvider[] - Memory and context management
    - middleware: AgentMiddleware[] - Execution pipeline interceptors
    
    Architectural Benefits:
    - Pydantic validation ensures type safety
    - Immutable configuration prevents runtime issues
    - Built-in serialization for persistence
    - Event lifecycle hooks for observability
    """
```

**Underlying Protocol**: Pydantic BaseModel + Custom AFBaseModel extensions
**Usage Pattern**: Extended by all concrete agent implementations
**Loan Processing Application**: Base for all 5 loan processing agents

### 2. ChatAgent - Primary Implementation

```python
from agent_framework import ChatAgent, ChatClientProtocol

class ChatAgent(BaseAgent):
    """
    Primary agent implementation with extensive configuration:
    
    Core Architecture:
    - chat_client: ChatClientProtocol - Pluggable LLM integration
    - instructions: str - System prompt/persona definition
    - tools: ToolProtocol[] - Available functions and MCP servers
    - middleware: Middleware[] - Pre/post processing pipeline
    
    LLM Configuration (follows OpenAI API standard):
    - temperature: float [0.0-2.0] - Response randomness
    - max_tokens: int - Response length limit
    - tool_choice: 'auto'|'required'|'none' - Tool usage control
    - response_format: BaseModel - Structured output schema
    - frequency_penalty: float - Repetition reduction
    - presence_penalty: float - Topic diversity
    - seed: int - Deterministic outputs
    - stop: str[] - Custom stop sequences
    
    Enterprise Features:
    - metadata: dict - Custom tracking data
    - user: str - User identification for logging
    - store: bool - Conversation persistence toggle
    """
    
    async def invoke(
        self, 
        messages: List[ChatMessage],
        context: AgentRunContext = None
    ) -> ChatResponse:
        """
        Main agent execution method:
        1. Apply middleware pre-processing
        2. Add context from providers
        3. Execute via chat client
        4. Process tool calls if needed
        5. Apply middleware post-processing
        6. Return structured response
        """
        
    async def run(
        self,
        messages: List[ChatMessage], 
        context: AgentRunContext = None
    ) -> AsyncIterator[AgentRunResponseUpdate]:
        """
        Streaming execution method:
        - Same pipeline as invoke()
        - Yields incremental updates
        - Supports real-time UI updates
        """
```

**Underlying Protocol**: AsyncIterator pattern + OpenAI-compatible API
**Usage Pattern**: One agent per specialized domain (credit, income, risk, etc.)
**Loan Processing Application**: Replace agent personas with ChatAgent instances

### 3. AgentProtocol - Type Safety Interface

```python
from typing import Protocol
from agent_framework import AgentProtocol

class AgentProtocol(Protocol):
    """
    Structural typing protocol ensuring agent compatibility:
    
    Required Methods:
    - invoke(messages, context) -> ChatResponse
    - run(messages, context) -> AsyncIterator[AgentRunResponseUpdate]
    
    Benefits:
    - Static type checking with mypy/pyright
    - Duck typing with compile-time safety
    - Interface segregation principle
    - Framework extensibility
    """
```

**Underlying Protocol**: Python structural typing (PEP 544)
**Usage Pattern**: Type annotations and interface contracts
**Loan Processing Application**: Ensures orchestrator can work with any agent implementation

### 4. WorkflowAgent - Orchestration Wrapper

```python
from agent_framework import WorkflowAgent, Workflow

class WorkflowAgent(BaseAgent):
    """
    Wraps a Workflow to expose it as a single Agent:
    
    Architecture:
    - workflow: Workflow - Graph-based execution engine
    - Implements AgentProtocol interface
    - Maps agent invoke() to workflow.run()
    - Provides unified interface for complex orchestrations
    
    Use Cases:
    - Multi-agent coordination
    - Complex decision trees
    - Hierarchical agent compositions
    - Loan processing pipeline orchestration
    """
```

**Underlying Protocol**: Facade pattern + Graph execution
**Usage Pattern**: High-level orchestration of multiple specialized agents
**Loan Processing Application**: Main orchestrator managing the 5-agent pipeline

### Agent Configuration for Loan Processing

```python
# Example: Credit Assessment Agent
credit_agent = ChatAgent(
    chat_client=foundry_client,
    name="Credit Assessment Agent",
    instructions="Analyze credit worthiness based on application data...",
    tools=[
        credit_bureau_tool,
        risk_calculation_tool,
        alternative_data_tool
    ],
    temperature=0.1,  # Lower temperature for consistent decisions
    tool_choice="auto",
    metadata={"agent_type": "credit", "version": "1.0"}
)
```

## Message and Content System

### 1. ChatMessage - Core Communication Unit

```python
from agent_framework import ChatMessage, Role, Contents

class ChatMessage:
    """
    OpenAI-compatible message structure with multi-content support:
    
    Fields:
    - role: Role - Message originator (USER, ASSISTANT, SYSTEM, TOOL)
    - contents: List[BaseContent] - Multiple content items per message
    - metadata: dict - Custom tracking data
    
    Advanced Features:
    - Multi-modal content support
    - Tool call/result embedding
    - Streaming update compatibility
    - Conversation threading
    """
    
    # Example: Multi-content loan application message
    loan_message = ChatMessage(
        role=Role.USER,
        contents=[
            TextContent(text="Please assess this loan application:"),
            DataContent(data=pdf_bytes, mime_type="application/pdf"),
            TextContent(text="Applicant credit score: 720")
        ]
    )
```

**Underlying Protocol**: OpenAI Messages API v1 + Extensions
**Usage Pattern**: Immutable message objects in conversation chains
**Loan Processing Application**: Carry application data, agent decisions, and tool results

### 2. Role System - Message Attribution

```python
from agent_framework import Role

# Built-in roles (Pydantic enum)
Role.USER       # Human or system input
Role.ASSISTANT  # Agent responses  
Role.SYSTEM     # System instructions/context
Role.TOOL       # Tool execution results

# Loan processing role mapping:
# USER -> Loan application data, human queries
# SYSTEM -> Agent personas, regulatory context
# ASSISTANT -> Agent assessments and decisions
# TOOL -> Credit bureau data, document analysis results
```

**Underlying Protocol**: OpenAI role convention + Pydantic enum validation
**Usage Pattern**: Message attribution and conversation flow control
**Loan Processing Application**: Track data sources and maintain audit trails

### 3. Content Types - Rich Message Payloads

```python
from agent_framework import (
    TextContent, DataContent, UriContent, 
    FunctionCallContent, FunctionResultContent, ErrorContent
)

class TextContent:
    """Plain text content with optional annotations"""
    text: str
    type: Literal["text"] = "text"

class DataContent:
    """Binary data with MIME type"""
    data: bytes
    mime_type: str
    filename: str | None = None
    type: Literal["data"] = "data"

class FunctionCallContent:
    """Tool invocation request"""
    function_name: str
    call_id: str  # Unique call identifier
    arguments: dict[str, Any]
    type: Literal["function_call"] = "function_call"

class FunctionResultContent:
    """Tool execution result"""
    call_id: str  # Links to FunctionCallContent
    result: str
    type: Literal["function_result"] = "function_result"

class ErrorContent:
    """Error information"""
    error: str
    code: str | None = None
    type: Literal["error"] = "error"
```

**Underlying Protocol**: MIME types + OpenAI function calling
**Usage Pattern**: Type-safe content polymorphism
**Loan Processing Application**: Handle documents, API responses, and structured data

### 4. ChatResponse - Execution Results

```python
from agent_framework import ChatResponse, FinishReason, UsageDetails

class ChatResponse:
    """
    Complete agent execution result:
    
    Fields:
    - messages: List[ChatMessage] - Generated messages
    - response_id: str - Unique response identifier
    - usage: UsageDetails - Token consumption metrics
    - finish_reason: FinishReason - Why execution completed
    - metadata: dict - Custom response data
    
    Finish Reasons:
    - STOP: Natural completion
    - LENGTH: Max tokens reached  
    - TOOL_CALLS: Stopped for tool execution
    - CONTENT_FILTER: Content policy triggered
    """
```

**Underlying Protocol**: OpenAI Completions API + Usage tracking
**Usage Pattern**: Structured execution results with observability
**Loan Processing Application**: Track agent decisions, token costs, and completion status

### Content Types for Loan Data

```python
from agent_framework import TextContent, FunctionCallContent, DataContent

# Text content - instructions and responses
text_content = TextContent(text="Analyze this loan application...")

# Function calls - tool invocations
function_call = FunctionCallContent(
    function_name="verify_credit_score",
    arguments={"applicant_id": "12345", "bureau": "experian"}
)

# Data content - documents and files
document_content = DataContent(
    data=pdf_bytes,
    mime_type="application/pdf",
    filename="pay_stub.pdf"
)
```

### Role Usage in Loan Processing

```python
# System message - agent instructions
system_msg = ChatMessage(
    role=Role.SYSTEM,
    contents=[TextContent(text="You are a credit assessment agent...")]
)

# User input - loan application data
user_msg = ChatMessage(
    role=Role.USER, 
    contents=[TextContent(text="Please assess this application: {...}")]
)

# Assistant response - agent decision
assistant_msg = ChatMessage(
    role=Role.ASSISTANT,
    contents=[TextContent(text="Credit assessment complete. Score: 720...")]
)

# Tool results - external data
tool_msg = ChatMessage(
    role=Role.TOOL,
    contents=[TextContent(text="Credit bureau response: {...}")]
)
```

## Tool Integration System

### 1. ToolProtocol - Universal Tool Interface

```python
from agent_framework import ToolProtocol
from typing import Protocol, runtime_checkable

@runtime_checkable
class ToolProtocol(Protocol):
    """
    Universal interface for all agent tools:
    
    Required Attributes:
    - name: str - Unique tool identifier
    - description: str - What the tool does (for AI understanding)
    - parameters: dict - JSON Schema for input validation
    
    Required Methods:
    - invoke(arguments: dict, context: InvocationContext) -> Any
    
    Optional Methods:
    - validate_arguments(arguments: dict) -> bool
    - get_examples() -> List[dict] - Usage examples for AI
    - handle_error(error: Exception) -> ErrorResponse
    
    Benefits:
    - Type-safe tool integration
    - Automatic parameter validation
    - Consistent error handling
    - Tool composition and chaining
    """
```

**Underlying Protocol**: Python Protocol (PEP 544) + JSON Schema + OpenAI Function Calling
**Usage Pattern**: Implement for custom tools, use built-in implementations for common cases
**Loan Processing Application**: Credit bureau APIs, document processors, calculation engines

### 2. AIFunction - Decorated Function Tools

```python
from agent_framework import ai_function, AIFunction
from typing import Annotated

@ai_function
def calculate_dti_ratio(
    monthly_income: Annotated[float, "Monthly gross income in dollars"],
    monthly_debt: Annotated[float, "Total monthly debt payments in dollars"]
) -> Annotated[float, "Debt-to-income ratio as percentage"]:
    """
    Calculate debt-to-income ratio for loan qualification.
    
    The DTI ratio is used to assess borrower's ability to repay.
    Ratios above 43% typically require additional documentation.
    """
    if monthly_income <= 0:
        raise ValueError("Monthly income must be positive")
    
    dti = (monthly_debt / monthly_income) * 100
    return round(dti, 2)

# Auto-generated AIFunction wrapper provides:
class AIFunction:
    """
    Automatic function wrapper with AI integration:
    
    Generated Features:
    - name: str - Function name
    - description: str - Docstring
    - parameters: dict - JSON Schema from type hints
    - invoke() method - Type-safe execution
    
    Advanced Features:
    - Automatic type conversion
    - Parameter validation
    - Error handling and retries
    - Usage example generation
    - Documentation extraction
    """
```

**Underlying Protocol**: Python decorators + Type introspection + JSON Schema generation
**Usage Pattern**: Decorate business logic functions for AI use
**Loan Processing Application**: Financial calculations, validation rules, business logic

### 3. MCP (Model Context Protocol) Integration

```python
from agent_framework import MCPStdioTool, MCPWebsocketTool, MCPStreamableHTTPTool

class MCPStdioTool:
    """
    MCP Server via subprocess stdin/stdout communication:
    
    Configuration:
    - name: str - Tool identifier
    - command: List[str] - Command and arguments to start server
    - args: List[str] - Additional command line arguments
    - env: dict - Environment variables
    - cwd: str - Working directory
    - timeout: float - Request timeout
    
    Protocol Features:
    - JSON-RPC 2.0 over stdio
    - Automatic process lifecycle management
    - Error recovery and restart
    - Resource cleanup on shutdown
    
    Example: Credit Bureau Integration
    """
    credit_bureau_tool = MCPStdioTool(
        name="credit_bureau",
        command=["python", "-m", "credit_bureau_mcp_server"],
        env={
            "API_KEY": "secret_key",
            "ENDPOINT": "https://api.creditbureau.com"
        },
        timeout=30.0
    )

class MCPWebsocketTool:
    """
    MCP Server via WebSocket communication:
    
    Configuration:
    - name: str - Tool identifier  
    - uri: str - WebSocket URI (ws:// or wss://)
    - headers: dict - Authentication headers
    - timeout: float - Connection timeout
    - reconnect: bool - Auto-reconnection
    - max_retries: int - Retry attempts
    
    Protocol Features:
    - JSON-RPC 2.0 over WebSocket
    - Persistent connection with heartbeat
    - Binary data support
    - Real-time updates
    
    Example: Document Processing Service
    """
    document_processor = MCPWebsocketTool(
        name="document_processor",
        uri="wss://docprocessor.internal.com/mcp",
        headers={"Authorization": "Bearer token"},
        reconnect=True,
        max_retries=3
    )

class MCPStreamableHTTPTool:
    """
    MCP Server via HTTP with streaming support:
    
    Configuration:
    - name: str - Tool identifier
    - base_url: str - Server base URL
    - headers: dict - Request headers
    - auth: AuthProvider - Authentication
    - stream: bool - Enable streaming responses
    - chunk_size: int - Streaming chunk size
    
    Protocol Features:
    - HTTP/2 with Server-Sent Events
    - Streaming JSON responses
    - File upload/download
    - RESTful resource access
    """
```

**Underlying Protocol**: Model Context Protocol (MCP) + JSON-RPC 2.0 + Various transports
**Usage Pattern**: Connect to external services and APIs as tools
**Loan Processing Application**: Integrate existing MCP servers for verification, documents, calculations

### 4. Tool Execution and Management

```python
from agent_framework import ChatToolMode, FunctionInvocationContext

# Tool execution modes
class ChatToolMode:
    AUTO = "auto"         # Agent decides when to use tools
    REQUIRED = "required" # Must use at least one tool
    NONE = "none"        # No tool usage allowed
    REQUIRED_ANY = "required_any"  # Must use any available tool

# Tool invocation context
class FunctionInvocationContext:
    """
    Context for tool execution:
    
    Request Data:
    - function_name: str - Tool being invoked
    - arguments: dict - Validated parameters
    - call_id: str - Unique invocation identifier
    - metadata: dict - Custom tracking data
    
    Agent Context:
    - agent_id: str - Calling agent
    - conversation_id: str - Thread context
    - user_id: str - Request originator
    - session_data: dict - Shared session state
    
    Execution Environment:
    - timeout: float - Maximum execution time
    - retry_policy: RetryPolicy - Error handling
    - security_context: SecurityContext - Permissions
    - telemetry: TelemetryClient - Observability
    """

# Tool middleware for cross-cutting concerns
from agent_framework import function_middleware, FunctionMiddleware

@function_middleware
class SecurityMiddleware(FunctionMiddleware):
    """Example: Add security checks to tool calls"""
    
    async def __call__(self, context: FunctionInvocationContext, next_handler):
        # Pre-execution: Validate permissions
        if not await self.check_permissions(context.user_id, context.function_name):
            raise PermissionError(f"User {context.user_id} cannot call {context.function_name}")
        
        # Execute tool
        await next_handler(context)
        
        # Post-execution: Audit logging
        await self.audit_log(context.user_id, context.function_name, context.arguments)
```

**Underlying Protocol**: Middleware pattern + Context management + Security framework
**Usage Pattern**: Apply cross-cutting concerns to tool execution
**Loan Processing Application**: Security, auditing, rate limiting, compliance validation

### MCP (Model Context Protocol) Tools

```python
from agent_framework import MCPStdioTool, MCPWebsocketTool, HostedMCPTool

# Connect to our existing MCP servers
application_verification = MCPStdioTool(
    name="application_verification",
    command=["python", "-m", "loan_processing.tools.mcp_servers.application_verification.server"],
    env={"PORT": "8010"}
)

document_processing = MCPWebsocketTool(
    name="document_processing", 
    uri="ws://localhost:8011/mcp"
)

# Microsoft-hosted tools
web_search = HostedWebSearchTool(
    name="web_search",
    description="Search for regulatory information"
)
```

## Chat Client Architecture

### 1. ChatClientProtocol - Provider Abstraction

```python
from agent_framework import ChatClientProtocol, BaseChatClient

class ChatClientProtocol(Protocol):
    """
    Standardized interface for all LLM providers:
    
    Required Methods:
    - invoke(messages, options) -> ChatResponse
    - invoke_stream(messages, options) -> AsyncIterator[ChatResponseUpdate]
    
    Benefits:
    - Provider-agnostic agent code
    - Easy provider switching
    - Testing with mock clients
    - Consistent error handling
    """
```

**Underlying Protocol**: Abstract base class + Protocol interface
**Usage Pattern**: Dependency injection into ChatAgent
**Loan Processing Application**: Switch between OpenAI, Azure, and Foundry without code changes

### 2. BaseChatClient - Common Implementation

```python
from agent_framework import BaseChatClient

class BaseChatClient(ChatClientProtocol, AFBaseModel):
    """
    Shared functionality across all providers:
    
    Common Features:
    - Request/response logging
    - Token usage tracking
    - Error standardization
    - Retry logic with exponential backoff
    - Rate limiting compliance
    - Request ID generation
    - User-Agent header management
    
    Observability:
    - OpenTelemetry integration
    - Request/response tracing
    - Performance metrics
    - Error categorization
    """
```

**Underlying Protocol**: Template method pattern + OpenTelemetry
**Usage Pattern**: Base class for provider implementations
**Loan Processing Application**: Consistent logging and monitoring across all agents

### 3. Provider-Specific Clients

```python
from agent_framework.openai import OpenAIChatClient
from agent_framework.azure import AzureChatClient  
from agent_framework.foundry import FoundryChatClient

# OpenAI - Direct API access
class OpenAIChatClient(BaseChatClient):
    """
    Official OpenAI API integration:
    - Direct openai-python SDK usage
    - Full feature parity
    - Latest model support
    - Function calling native support
    """

# Azure OpenAI - Enterprise features
class AzureChatClient(BaseChatClient):
    """
    Azure OpenAI Service integration:
    - Managed Azure identity
    - Private endpoint support
    - Content filtering policies
    - Regional deployment options
    - Enterprise compliance features
    """

# Azure AI Foundry - Microsoft's AI platform
class FoundryChatClient(BaseChatClient):
    """
    Azure AI Foundry integration (Recommended for Enterprise):
    - Integrated AI safety features  
    - Model management and versioning
    - Built-in evaluation and monitoring
    - Multi-modal model support
    - Responsible AI guardrails
    - Enterprise security controls
    """
```

**Underlying Protocol**: Provider-specific SDKs + Standardized interface
**Usage Pattern**: Configuration-driven provider selection
**Loan Processing Application**: Use Foundry for enterprise features, fallback to Azure/OpenAI

### 4. ChatOptions - Request Configuration

```python
from agent_framework import ChatOptions, ChatToolMode

class ChatOptions:
    """
    Comprehensive request configuration:
    
    Core Parameters:
    - ai_model_id: str - Model identifier
    - temperature: float [0.0-2.0] - Response creativity
    - max_tokens: int - Response length limit
    - top_p: float [0.0-1.0] - Nucleus sampling
    - frequency_penalty: float [-2.0-2.0] - Repetition reduction
    - presence_penalty: float [-2.0-2.0] - Topic diversity
    - seed: int - Deterministic generation
    - stop: str[] - Custom stop sequences
    
    Tool Configuration:
    - tools: ToolProtocol[] - Available functions
    - tool_choice: ChatToolMode - Tool usage control
    - allow_multiple_tool_calls: bool - Parallel tool execution
    
    Enterprise Features:
    - user: str - User identification for compliance
    - metadata: dict - Request tracking data
    - conversation_id: str - Thread management
    - store: bool - Conversation persistence
    - response_format: BaseModel - Structured outputs
    
    Advanced Options:
    - logit_bias: dict - Token probability adjustment
    - additional_properties: dict - Provider-specific options
    """
```

**Underlying Protocol**: OpenAI API parameters + Provider extensions
**Usage Pattern**: Per-request configuration override
**Loan Processing Application**: Different settings per agent type (conservative for credit, creative for explanations)

### Chat Client Configuration

```python
# Configuration options for loan processing
chat_options = ChatOptions(
    temperature=0.1,  # Consistent decisions
    max_tokens=2000,  # Adequate response length
    tools=[mcp_tools],  # Available tools
    tool_choice="auto",  # Let agent decide when to use tools
    response_format=LoanDecision,  # Structured output
    user="loan_system",  # System identifier
    stop=["END_ASSESSMENT"]  # Stop sequences
)
```

## Workflow System - Pregel-Inspired Orchestration

### 1. Workflow - Graph Execution Engine

```python
from agent_framework import Workflow, WorkflowContext

class Workflow:
    """
    Pregel-like graph execution engine:
    
    Architecture:
    - Directed graph of executors (nodes) and edges
    - Superstep-based execution model
    - Message passing between executors
    - Distributed computation support
    - Fault tolerance and checkpointing
    
    Execution Model:
    1. Superstep begins - all executors receive messages
    2. Executors process messages and compute results
    3. Executors send messages to successor nodes
    4. Superstep ends - synchronization barrier
    5. Repeat until no more messages or terminal condition
    
    Benefits:
    - Scalable parallel execution
    - Deterministic results
    - Easy debugging and monitoring
    - Fault recovery capabilities
    """
    
    async def run(
        self,
        input_data: Any,
        context: WorkflowContext,
        checkpoint: CheckpointStorage = None
    ) -> WorkflowRunResult:
        """
        Execute workflow with fault tolerance:
        1. Load checkpoint if resuming
        2. Initialize executor states
        3. Run supersteps until completion
        4. Save final checkpoint
        5. Return aggregated results
        """
```

**Underlying Protocol**: Google Pregel + Actor model + Message passing
**Usage Pattern**: Complex multi-agent orchestrations with dependencies
**Loan Processing Application**: Coordinate 5 agents with parallel and sequential phases

### 2. WorkflowBuilder - Declarative Construction

```python
from agent_framework import WorkflowBuilder, Edge

class WorkflowBuilder:
    """
    Fluent builder for workflow graphs:
    
    Construction Methods:
    - add_executor(id, executor) - Add processing node
    - add_edge(from, to) - Simple sequential connection
    - add_fan_out_edge(from, to_list) - One-to-many distribution
    - add_fan_in_edge(from_list, to) - Many-to-one aggregation
    - add_switch_case_edge(from, cases) - Conditional routing
    - set_start_executor(id) - Entry point designation
    
    Validation:
    - Cycle detection
    - Reachability analysis
    - Type compatibility checking
    - Resource constraint validation
    """
    
    # Loan processing workflow example
    def build_loan_workflow(self) -> Workflow:
        return (
            WorkflowBuilder()
            # Add specialized agents as executors
            .add_executor("intake", IntakeAgentExecutor(intake_agent))
            .add_executor("credit", CreditAgentExecutor(credit_agent))
            .add_executor("income", IncomeAgentExecutor(income_agent))
            .add_executor("risk", RiskAgentExecutor(risk_agent))
            .add_executor("decision", DecisionAggregatorExecutor())
            
            # Define execution flow
            .add_edge("intake", "credit")      # Sequential validation
            .add_edge("intake", "income")      # Parallel assessment
            .add_fan_in_edge(["credit", "income"], "risk")  # Aggregation
            .add_edge("risk", "decision")      # Final decision
            
            # Set entry point
            .set_start_executor("intake")
            .build()
        )
```

**Underlying Protocol**: Builder pattern + Graph theory + Fluent interface
**Usage Pattern**: Declarative workflow definition with validation
**Loan Processing Application**: Visual workflow definition matching business process

### 3. WorkflowExecutor - Node Implementation

```python
from agent_framework import WorkflowExecutor, ExecutorContext

class WorkflowExecutor:
    """
    Base class for workflow nodes:
    
    Core Methods:
    - can_handle(input) -> bool - Input validation
    - execute(input, context) -> ExecutorResult - Main processing
    - handle_error(error, context) -> ErrorHandlingResult - Error recovery
    
    Execution Context:
    - Input data and metadata
    - Shared state access
    - Message passing capabilities
    - Checkpoint management
    - Logging and telemetry
    """
    
    async def execute(
        self, 
        input_data: Any, 
        context: ExecutorContext
    ) -> ExecutorResult:
        """
        Template method for node execution:
        1. Validate input data
        2. Load shared state
        3. Execute business logic
        4. Update shared state
        5. Return results and next messages
        """

# Custom executor for loan processing
class CreditAgentExecutor(WorkflowExecutor):
    def __init__(self, credit_agent: ChatAgent):
        self.credit_agent = credit_agent
    
    async def execute(self, loan_app: LoanApplication, context: ExecutorContext) -> ExecutorResult:
        # Execute credit assessment
        response = await self.credit_agent.invoke([
            ChatMessage(role=Role.USER, contents=[
                TextContent(text=f"Assess credit for: {loan_app.json()}")
            ])
        ])
        
        # Parse structured result
        credit_assessment = CreditAssessment.parse_raw(
            response.messages[-1].contents[0].text
        )
        
        # Pass to next nodes
        return ExecutorResult(
            output=credit_assessment,
            messages=[
                Message(target="risk", data=credit_assessment),
                Message(target="decision", data={"credit_score": credit_assessment.score})
            ]
        )
```

**Underlying Protocol**: Template method + Message passing + State management
**Usage Pattern**: Wrap agents as workflow nodes with standardized interface
**Loan Processing Application**: Each agent becomes a specialized executor

### 4. WorkflowContext - Execution Environment

```python
from agent_framework import WorkflowContext, SharedState

class WorkflowContext:
    """
    Execution environment for workflows:
    
    Context Data:
    - workflow_id: str - Unique execution identifier
    - user_id: str - Request originator
    - session_id: str - Conversation thread
    - metadata: dict - Custom tracking data
    
    Shared State:
    - persistent: dict - Survives checkpoints
    - transient: dict - In-memory only
    - thread_local: dict - Executor-specific
    
    Services:
    - logger: Logger - Structured logging
    - telemetry: TelemetryClient - Metrics and tracing
    - checkpoint: CheckpointStorage - State persistence
    - message_queue: MessageQueue - Inter-executor communication
    """
    
    # Loan processing context
    loan_context = WorkflowContext(
        workflow_id="loan_processing_v1",
        user_id="applicant_12345",
        session_id="session_67890",
        metadata={
            "application_id": "LN123456789",
            "priority": "standard",
            "compliance_level": "strict"
        }
    )
```

**Underlying Protocol**: Context pattern + Dependency injection + State management
**Usage Pattern**: Shared execution environment across all workflow nodes
**Loan Processing Application**: Maintain application context and audit trail throughout process

### Workflow Execution Patterns

```python
# Sequential execution
sequential_workflow = (
    WorkflowBuilder()
    .add_executor("step1", agent1)
    .add_executor("step2", agent2)
    .add_edge("step1", "step2")
    .build()
)

# Parallel execution  
parallel_workflow = (
    WorkflowBuilder()
    .add_executor("credit_check", credit_agent)
    .add_executor("income_verify", income_agent)
    .add_executor("combine", decision_agent)
    .add_edge(["credit_check", "income_verify"], "combine")
    .build()
)

# Conditional execution
conditional_workflow = (
    WorkflowBuilder()
    .add_executor("triage", triage_agent)
    .add_executor("simple_path", simple_agent)
    .add_executor("complex_path", complex_agent)
    .add_switch_case_edge("triage", [
        ("simple", "simple_path"),
        ("complex", "complex_path")
    ])
    .build()
)
```

## Memory and Context Management

### Context Providers

```python
from agent_framework import ContextProvider, AggregateContextProvider

class LoanApplicationContextProvider(ContextProvider):
    """Provides loan application context to agents."""
    
    async def on_agent_run_start(self, context: AgentRunContext):
        # Add application data to context
        context.context["application"] = await self.get_application(
            context.request.metadata.get("application_id")
        )
    
    async def on_agent_run_complete(self, context: AgentRunContext):
        # Save agent decision
        await self.save_decision(
            context.request.metadata.get("application_id"),
            context.response
        )

# Combine multiple context providers
context_provider = AggregateContextProvider([
    LoanApplicationContextProvider(),
    RegulatoryContextProvider(),
    AuditTrailContextProvider()
])
```

### Message Storage

```python
from agent_framework import ChatMessageStore

class LoanChatMessageStore(ChatMessageStore):
    """Store loan processing conversations."""
    
    async def add_message(self, thread_id: str, message: ChatMessage):
        # Store with encryption for sensitive loan data
        await self.db.store_encrypted_message(thread_id, message)
    
    async def get_messages(self, thread_id: str) -> List[ChatMessage]:
        # Retrieve and decrypt messages
        return await self.db.get_encrypted_messages(thread_id)
```

## Configuration and Middleware

### Agent Middleware for Loan Processing

```python
from agent_framework import AgentMiddleware, agent_middleware

@agent_middleware
class ComplianceMiddleware(AgentMiddleware):
    """Ensures all agent decisions comply with regulations."""
    
    async def __call__(self, context: AgentRunContext, next_handler):
        # Pre-processing: Add compliance context
        context.context["regulations"] = await self.get_regulations()
        
        # Execute agent
        await next_handler(context)
        
        # Post-processing: Validate compliance
        if not await self.validate_compliance(context.response):
            raise ComplianceViolationError("Decision violates regulations")

# Apply to all loan processing agents
credit_agent = ChatAgent(
    chat_client=client,
    instructions="...",
    middleware=[ComplianceMiddleware(), AuditMiddleware()]
)
```

### Configuration Types

```python
from agent_framework import ChatToolMode, FinishReason

# Tool execution modes
ChatToolMode.AUTO      # Agent decides when to use tools
ChatToolMode.REQUIRED  # Must use at least one tool
ChatToolMode.NONE      # No tool usage allowed

# Completion reasons
FinishReason.STOP         # Natural completion
FinishReason.LENGTH       # Max tokens reached
FinishReason.TOOL_CALLS   # Stopped for tool execution
FinishReason.CONTENT_FILTER  # Content filtered
```

## Integration with Existing Loan System

### Mapping to Current Architecture

```python
# Replace current agent personas with ChatAgent instances
from loan_processing.agents.agent_persona import get_persona_path

# Load persona instructions
with open(get_persona_path("credit"), 'r') as f:
    credit_instructions = f.read()

# Create ChatAgent with persona
credit_agent = ChatAgent(
    chat_client=foundry_client,
    instructions=credit_instructions,
    tools=[
        application_verification,
        financial_calculations, 
        document_processing
    ],
    name="Credit Assessment Agent",
    middleware=[ComplianceMiddleware()]
)

# Integrate with existing data models
from loan_processing.models import LoanApplication, LoanDecision

async def process_application(application: LoanApplication) -> LoanDecision:
    response = await credit_agent.invoke([
        ChatMessage(
            role=Role.USER,
            contents=[TextContent(text=f"Assess application: {application.json()}")]
        )
    ])
    
    # Parse structured response
    return LoanDecision.parse_raw(response.messages[-1].contents[0].text)
```

## Memory and Context Management

### 1. ContextProvider - Dynamic Context Injection

```python
from agent_framework import ContextProvider, AgentRunContext

class ContextProvider:
    """
    Dynamic context injection into agent execution:
    
    Lifecycle Hooks:
    - on_agent_run_start(context: AgentRunContext) - Pre-execution setup
    - on_agent_run_complete(context: AgentRunContext) - Post-execution cleanup
    - on_function_call(context: FunctionInvocationContext) - Tool call interception
    - on_error(context: AgentRunContext, error: Exception) - Error handling
    
    Use Cases:
    - Load relevant data from databases
    - Inject regulatory context
    - Add user preferences
    - Maintain conversation history
    - Cache expensive operations
    """

# Loan processing context provider
class LoanApplicationContextProvider(ContextProvider):
    """Provides loan application context to agents"""
    
    async def on_agent_run_start(self, context: AgentRunContext):
        # Load application data
        app_id = context.metadata.get("application_id")
        if app_id:
            application = await self.db.get_application(app_id)
            context.context["application"] = application
            
            # Add regulatory context
            regulations = await self.get_regulations(application.state)
            context.context["regulations"] = regulations
    
    async def on_agent_run_complete(self, context: AgentRunContext):
        # Save agent decision with audit trail
        await self.audit_service.log_decision(
            agent_id=context.agent.id,
            decision=context.response,
            timestamp=datetime.utcnow()
        )
```

**Underlying Protocol**: Observer pattern + Dependency injection + Lifecycle management
**Usage Pattern**: Inject dynamic context without modifying agent code
**Loan Processing Application**: Load application data, regulations, user preferences

### 2. ChatMessageStore - Conversation Persistence

```python
from agent_framework import ChatMessageStore, ChatMessage

class ChatMessageStore:
    """
    Thread-based conversation persistence:
    
    Core Methods:
    - add_message(thread_id: str, message: ChatMessage) - Store message
    - get_messages(thread_id: str, limit: int, offset: int) - Retrieve history
    - delete_thread(thread_id: str) - Remove conversation
    - get_threads(user_id: str) - List user conversations
    
    Enterprise Features:
    - Encryption at rest
    - Retention policies
    - Compliance tagging
    - Search and indexing
    - Backup and recovery
    """

# Secure loan processing message store
class SecureLoanMessageStore(ChatMessageStore):
    """Encrypted message storage for sensitive loan data"""
    
    async def add_message(self, thread_id: str, message: ChatMessage):
        # Encrypt sensitive content
        encrypted_message = await self.encrypt_pii(message)
        
        # Store with metadata
        await self.db.store_message(
            thread_id=thread_id,
            message=encrypted_message,
            timestamp=datetime.utcnow(),
            retention_date=datetime.utcnow() + timedelta(days=2555)  # 7 years
        )
    
    async def get_messages(self, thread_id: str, limit: int = 100) -> List[ChatMessage]:
        # Retrieve and decrypt
        encrypted_messages = await self.db.get_messages(thread_id, limit)
        return [await self.decrypt_pii(msg) for msg in encrypted_messages]
```

**Underlying Protocol**: Repository pattern + Encryption + Compliance framework
**Usage Pattern**: Persistent conversation history with security
**Loan Processing Application**: Maintain audit trail, conversation threading, compliance retention

## Middleware System - Cross-Cutting Concerns

### 1. AgentMiddleware - Agent Execution Pipeline

```python
from agent_framework import AgentMiddleware, agent_middleware, AgentRunContext

@agent_middleware
class ComplianceMiddleware(AgentMiddleware):
    """
    Regulatory compliance enforcement:
    
    Pre-execution:
    - Validate agent permissions
    - Load compliance rules
    - Check data access rights
    
    Post-execution:
    - Validate decision compliance  
    - Generate audit logs
    - Apply disclosure requirements
    """
    
    async def __call__(self, context: AgentRunContext, next_handler):
        # Pre-processing: Load compliance context
        regulations = await self.load_regulations(context.metadata.get("jurisdiction"))
        context.context["compliance_rules"] = regulations
        
        # Execute agent
        await next_handler(context)
        
        # Post-processing: Validate compliance
        decision = context.response.messages[-1].contents[0].text
        compliance_check = await self.validate_compliance(decision, regulations)
        
        if not compliance_check.passed:
            raise ComplianceViolationError(
                f"Decision violates {compliance_check.violated_rules}"
            )
```

**Underlying Protocol**: Middleware pattern + Chain of responsibility + Compliance framework
**Usage Pattern**: Apply consistent cross-cutting concerns to all agents
**Loan Processing Application**: Compliance, security, auditing, performance monitoring

### 2. Integration Architecture Summary

```python
# Complete loan processing integration example
from agent_framework import *
from loan_processing.models import LoanApplication, LoanDecision

class LoanProcessingOrchestrator:
    """
    Complete integration of Microsoft Agent Framework with existing business logic
    """
    
    def __init__(self):
        # Initialize chat client (enterprise-grade)
        self.chat_client = FoundryChatClient(
            endpoint=os.getenv("FOUNDRY_ENDPOINT"),
            credential=DefaultAzureCredential(),
            model_deployment_name="gpt-4o"
        )
        
        # Load existing agent personas
        self.agents = {
            "intake": self.create_intake_agent(),
            "credit": self.create_credit_agent(),
            "income": self.create_income_agent(),
            "risk": self.create_risk_agent()
        }
        
        # Build workflow from existing business process
        self.workflow = self.build_loan_workflow()
    
    def create_credit_agent(self) -> ChatAgent:
        """Convert existing credit agent persona to ChatAgent"""
        
        # Load existing persona instructions
        with open("loan_processing/agents/agent-persona/credit-agent-persona.md") as f:
            instructions = f.read()
        
        # Convert existing MCP servers to tools
        tools = [
            MCPStdioTool(
                name="application_verification",
                command=["python", "-m", "loan_processing.tools.mcp_servers.application_verification.server"]
            ),
            MCPStdioTool(
                name="financial_calculations", 
                command=["python", "-m", "loan_processing.tools.mcp_servers.financial_calculations.server"]
            )
        ]
        
        # Add business logic as AI functions
        tools.extend([
            ai_function(self.calculate_dti_ratio),
            ai_function(self.validate_credit_score),
            ai_function(self.assess_credit_risk)
        ])
        
        return ChatAgent(
            chat_client=self.chat_client,
            name="Credit Assessment Agent",
            instructions=instructions,
            tools=tools,
            temperature=0.1,  # Conservative for financial decisions
            response_format=CreditAssessment,  # Structured output
            middleware=[
                ComplianceMiddleware(),
                AuditMiddleware(),
                SecurityMiddleware()
            ],
            context_providers=[
                LoanApplicationContextProvider(),
                RegulatoryContextProvider()
            ]
        )
    
    async def process_application(self, application: LoanApplication) -> LoanDecision:
        """
        Process loan application through Agent Framework workflow
        while maintaining existing business logic and compliance
        """
        
        # Execute workflow with application context
        result = await self.workflow.run(
            input_data=application,
            context=WorkflowContext(
                user_id=application.applicant_id,
                metadata={
                    "application_id": application.application_id,
                    "compliance_level": "strict",
                    "audit_required": True
                }
            )
        )
        
        # Return structured business decision
        return LoanDecision.parse_obj(result.output)
```

This comprehensive architecture provides enterprise-grade agent orchestration while preserving all existing business logic, compliance requirements, and domain expertise from your current framework-agnostic foundation.