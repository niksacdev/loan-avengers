# Observability Guide - Loan Avengers

## Overview

The Loan Avengers application implements enterprise-grade observability using **out-of-the-box solutions** from OpenTelemetry, Azure Monitor, and Microsoft Agent Framework. This guide covers how to use observability features for debugging, performance analysis, and cost management.

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                      Azure Application Insights                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │   Traces     │  │    Logs      │  │   Metrics    │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
└─────────────────────────────────────────────────────────────────┘
                              ▲
                              │ OpenTelemetry Exporter
                              │
┌─────────────────────────────────────────────────────────────────┐
│                    Loan Avengers API (FastAPI)                   │
│                                                                   │
│  ┌──────────────────────────────────────────────────────┐      │
│  │  OpenTelemetry Auto-Instrumentation                   │      │
│  │  • configure_azure_monitor()                          │      │
│  │  • FastAPIInstrumentor.instrument_app()               │      │
│  └──────────────────────────────────────────────────────┘      │
│                                                                   │
│  ┌──────────────────────────────────────────────────────┐      │
│  │  Observability Utilities                              │      │
│  │  • Correlation ID tracking (ContextVar)               │      │
│  │  • Token usage logging                                │      │
│  │  • Agent Framework observability                      │      │
│  └──────────────────────────────────────────────────────┘      │
│                                                                   │
│  ┌──────────────────────────────────────────────────────┐      │
│  │  Application Components                               │      │
│  │  • API Endpoints (/api/chat, /api/sessions)           │      │
│  │  • Conversation Orchestrator                          │      │
│  │  • Sequential Pipeline (Agent Workflow)               │      │
│  │  • MCP Servers (Tools)                                │      │
│  └──────────────────────────────────────────────────────┘      │
└─────────────────────────────────────────────────────────────────┘
```

## Components

### 1. OpenTelemetry Auto-Instrumentation

**Automatically captures**:
- HTTP request/response (FastAPI endpoints)
- HTTP client calls (httpx, requests to external APIs)
- Database calls (if applicable)
- Exception stack traces

**Configuration** (`loan_avengers/api/app.py:56-82`):
```python
# Automatically configured from environment variables
configure_azure_monitor()
FastAPIInstrumentor.instrument_app(app, excluded_urls="/health,/docs,/redoc")
```

### 2. Microsoft Agent Framework Observability

**Automatically captures** (`loan_avengers/utils/observability.py:52-58`):
- Agent execution traces
- Token usage (input/output tokens)
- Agent performance metrics
- Cost estimation

**Configuration**:
```python
setup_observability(
    applicationinsights_connection_string=os.getenv("APPLICATIONINSIGHTS_CONNECTION_STRING"),
    enable_sensitive_data=False,  # Never log PII
    enable_live_metrics=True,      # Real-time monitoring
)
```

### 3. Correlation ID Tracking

**Purpose**: Track requests end-to-end across API → Agents → MCP servers

**Implementation** (`loan_avengers/api/app.py:93-136`):
- Middleware extracts `X-Correlation-ID` header or generates UUID
- Stored in ContextVar (thread-safe for async)
- Automatically added to all logs via `Observability.get_correlation_id()`
- Propagated through OpenTelemetry traces
- Returned in response headers

**Usage in code**:
```python
logger.info(
    "Processing request",
    extra={
        "correlation_id": Observability.get_correlation_id(),
        "application_id": app_id,
        # ... other fields
    }
)
```

### 4. Token Usage Tracking

**Purpose**: Cost management and optimization

**Implementation** (`loan_avengers/utils/observability.py:239-294`):
```python
Observability.log_token_usage(
    agent_name="Credit_Assessor",
    input_tokens=150,
    output_tokens=75,
    model="gpt-4",
    application_id="LN1234567890"
)
```

**Logged fields**:
- `event_type`: "token_usage"
- `agent_name`: Which agent consumed tokens
- `input_tokens`, `output_tokens`, `total_tokens`
- `model`: Model deployment name
- `application_id`: Masked for security
- `correlation_id`: For request tracing

## Environment Variables

Required for full observability:

```bash
# Required: Application Insights connection string
APPLICATIONINSIGHTS_CONNECTION_STRING=InstrumentationKey=...;IngestionEndpoint=...

# Recommended: Service identification
OTEL_SERVICE_NAME=loan-avengers-api
OTEL_SERVICE_VERSION=0.1.0
OTEL_RESOURCE_ATTRIBUTES=deployment.environment=production,cloud.provider=azure

# Optional: Logging configuration
LOG_LEVEL=INFO  # DEBUG for development
ENABLE_SENSITIVE_DATA=false  # NEVER enable in production

# Optional: Exclude health checks from tracing
OTEL_PYTHON_FASTAPI_EXCLUDED_URLS=/health,/docs,/redoc,/openapi.json
```

## Azure Application Insights Queries (KQL)

### 1. Request Tracing

**Find request by correlation ID**:
```kql
union requests, traces, exceptions
| where customDimensions.correlation_id == "your-correlation-id-here"
| project timestamp, itemType, operation_Name, message, customDimensions
| order by timestamp asc
```

**Track full loan application journey**:
```kql
let correlationId = "your-correlation-id";
union requests, traces
| where customDimensions.correlation_id == correlationId
| extend
    phase = tostring(customDimensions.phase),
    agent = tostring(customDimensions.agent_name),
    app_id = tostring(customDimensions.application_id)
| project timestamp, itemType, operation_Name, phase, agent, message
| order by timestamp asc
```

### 2. Performance Analysis

**API endpoint latency (p50, p95, p99)**:
```kql
requests
| where name == "POST /api/chat"
| summarize
    count = count(),
    avg_duration = avg(duration),
    p50 = percentile(duration, 50),
    p95 = percentile(duration, 95),
    p99 = percentile(duration, 99)
    by bin(timestamp, 5m)
| order by timestamp desc
```

**Agent execution time**:
```kql
traces
| where message contains "Agent processing"
| extend
    agent = tostring(customDimensions.agent_name),
    phase = tostring(customDimensions.phase),
    duration_ms = todouble(customDimensions.duration_ms)
| summarize
    count(),
    avg(duration_ms),
    percentile(duration_ms, 50),
    percentile(duration_ms, 95)
    by agent, phase
```

**Slowest requests in last hour**:
```kql
requests
| where timestamp > ago(1h)
| top 20 by duration desc
| project
    timestamp,
    name,
    duration,
    resultCode,
    operation_Id,
    customDimensions.correlation_id,
    customDimensions.application_id
```

### 3. Error Analysis

**Error rate by endpoint**:
```kql
requests
| where timestamp > ago(1h)
| summarize
    total = count(),
    errors = countif(success == false),
    error_rate = (countif(success == false) * 100.0 / count())
    by name
| where error_rate > 0
| order by error_rate desc
```

**Recent exceptions with context**:
```kql
exceptions
| where timestamp > ago(1h)
| extend
    correlation_id = tostring(customDimensions.correlation_id),
    application_id = tostring(customDimensions.application_id),
    error_type = tostring(customDimensions.error_type)
| project
    timestamp,
    type,
    outerMessage,
    correlation_id,
    application_id,
    error_type,
    operation_Id
| order by timestamp desc
```

**Agent failure analysis**:
```kql
traces
| where severityLevel >= 3  // Error or Critical
| where message contains "failed"
| extend
    agent = tostring(customDimensions.agent_name),
    phase = tostring(customDimensions.phase),
    error_type = tostring(customDimensions.error_type)
| summarize
    failure_count = count(),
    unique_errors = dcount(error_type)
    by agent, phase
| order by failure_count desc
```

### 4. Cost Management

**Token usage by agent**:
```kql
traces
| where customDimensions.event_type == "token_usage"
| extend
    agent = tostring(customDimensions.agent_name),
    total_tokens = toint(customDimensions.total_tokens),
    model = tostring(customDimensions.model)
| summarize
    total_tokens = sum(total_tokens),
    avg_tokens_per_call = avg(total_tokens),
    call_count = count()
    by agent, model
| extend estimated_cost_usd = total_tokens * 0.00001  // Adjust rate for your model
| order by estimated_cost_usd desc
```

**Daily token usage trend**:
```kql
traces
| where customDimensions.event_type == "token_usage"
| extend total_tokens = toint(customDimensions.total_tokens)
| summarize
    total_tokens = sum(total_tokens),
    call_count = count()
    by bin(timestamp, 1d)
| extend daily_cost_usd = total_tokens * 0.00001
| order by timestamp desc
```

**Expensive applications (top token consumers)**:
```kql
traces
| where customDimensions.event_type == "token_usage"
| extend
    app_id = tostring(customDimensions.application_id),
    total_tokens = toint(customDimensions.total_tokens)
| summarize
    total_tokens = sum(total_tokens),
    agent_calls = count()
    by app_id
| extend estimated_cost = total_tokens * 0.00001
| top 20 by total_tokens desc
```

### 5. User Behavior

**Loan application funnel**:
```kql
traces
| where customDimensions.agent_name == "Cap-ital America"
  or customDimensions.phase in ("intake", "credit", "income", "risk")
| extend
    correlation_id = tostring(customDimensions.correlation_id),
    phase = tostring(customDimensions.phase),
    completion = toint(customDimensions.completion_percentage)
| summarize arg_max(timestamp, *) by correlation_id, phase
| summarize
    started = dcountif(correlation_id, phase == "collecting"),
    completed_intake = dcountif(correlation_id, completion >= 100),
    reached_credit = dcountif(correlation_id, phase == "credit"),
    reached_income = dcountif(correlation_id, phase == "income"),
    reached_decision = dcountif(correlation_id, phase == "risk")
```

**Session duration analysis**:
```kql
requests
| where name == "POST /api/chat"
| extend session_id = tostring(customDimensions.session_id)
| summarize
    session_start = min(timestamp),
    session_end = max(timestamp),
    message_count = count()
    by session_id
| extend session_duration_minutes = datetime_diff('minute', session_end, session_start)
| summarize
    avg(session_duration_minutes),
    percentile(session_duration_minutes, 50),
    percentile(session_duration_minutes, 95)
```

## Debugging Workflows

### Scenario 1: User Reports Error

1. **Get correlation ID** from user or response headers
2. **Find full request trace**:
   ```kql
   union requests, traces, exceptions
   | where customDimensions.correlation_id == "CORRELATION_ID"
   | order by timestamp asc
   ```
3. **Identify failure point** from trace timeline
4. **Check exception details** if present
5. **Review agent logs** for that correlation ID

### Scenario 2: Slow Performance

1. **Identify slow endpoint**:
   ```kql
   requests
   | where duration > 5000  // >5 seconds
   | top 50 by duration desc
   ```
2. **Check agent execution times** for those requests
3. **Review external dependencies** (httpx calls)
4. **Analyze token usage** - high tokens = longer processing

### Scenario 3: Cost Spike

1. **Identify high token usage**:
   ```kql
   traces
   | where customDimensions.event_type == "token_usage"
   | where timestamp > ago(1h)
   | summarize total_tokens = sum(toint(customDimensions.total_tokens)) by bin(timestamp, 5m)
   | order by total_tokens desc
   ```
2. **Find applications causing spike**
3. **Review agent prompts** - are they too verbose?
4. **Check for loops** - is same request retrying?

## Dashboards

### Create Application Insights Workbook

1. **Navigate** to Azure Portal → Application Insights → Workbooks
2. **Create** new workbook
3. **Add queries** from above (Performance, Errors, Cost)
4. **Set auto-refresh** to 5 minutes
5. **Pin to dashboard** for monitoring

### Recommended Tiles

1. **Request Rate** - requests/minute over time
2. **Error Rate** - percentage of failed requests
3. **P95 Latency** - 95th percentile response time
4. **Token Usage** - daily/hourly token consumption
5. **Active Sessions** - current session count
6. **Agent Performance** - avg duration by agent

## Alerts

Configure alerts in Azure Application Insights:

### Critical Alerts

1. **High Error Rate**
   - Condition: Error rate > 5% over 5 minutes
   - Action: Email, Slack notification

2. **Slow Performance**
   - Condition: P95 latency > 5 seconds over 5 minutes
   - Action: Email notification

3. **Service Down**
   - Condition: Availability < 99% over 5 minutes
   - Action: PagerDuty/Slack

### Warning Alerts

1. **High Token Usage**
   - Condition: Tokens > 100K over 1 hour
   - Action: Email notification

2. **Agent Failures**
   - Condition: Agent failures > 10 over 15 minutes
   - Action: Slack notification

## Best Practices

### DO ✅

- **Always include correlation_id** in logs
- **Mask PII** (use `Observability.mask_application_id()`)
- **Use structured logging** with `extra={}` dict
- **Log business events** (application submitted, approved, rejected)
- **Track token usage** for cost management
- **Set appropriate log levels** (INFO in prod, DEBUG in dev)

### DON'T ❌

- **Log sensitive data** (SSN, full names, addresses)
- **Log full prompts** (token waste in logs)
- **Log on every line** (noise and performance)
- **Ignore correlation IDs** (breaks tracing)
- **Skip error context** (always log error_type and stack trace)
- **Over-instrument** (exclude health checks, static assets)

## Troubleshooting

### Traces not appearing in Application Insights

1. **Check connection string**: Verify `APPLICATIONINSIGHTS_CONNECTION_STRING`
2. **Check firewall**: Ensure outbound HTTPS to `dc.services.visualstudio.com`
3. **Check sampling**: Traces may be sampled (default 100% in dev)
4. **Wait 2-3 minutes**: Ingestion delay is normal

### High latency from instrumentation

1. **Check batch settings**: Default batching should be <1ms overhead
2. **Exclude noisy endpoints**: Add to `OTEL_PYTHON_FASTAPI_EXCLUDED_URLS`
3. **Reduce attribute cardinality**: Limit unique values in custom dimensions
4. **Disable sensitive data**: Set `ENABLE_SENSITIVE_DATA=false`

### Missing correlation IDs

1. **Verify middleware**: Check `add_correlation_id_middleware` is registered
2. **Check ContextVar**: Ensure async context propagation
3. **Clear between requests**: Middleware should call `clear_correlation_id()`

## Resources

- [Azure Application Insights Docs](https://learn.microsoft.com/en-us/azure/azure-monitor/app/app-insights-overview)
- [OpenTelemetry Python](https://opentelemetry.io/docs/languages/python/)
- [KQL Query Language](https://learn.microsoft.com/en-us/azure/data-explorer/kusto/query/)
- [Agent Framework Observability](https://github.com/microsoft/agent-framework)

## Support

For observability issues:
1. Check this guide first
2. Review Application Insights logs
3. Contact DevOps team with correlation ID
