# Streaming Protocol Specification

## Overview

The Loan Defenders API uses **Streamable HTTP** transport, aligned with the Model Context Protocol (MCP) specification (2025-03-26). This provides real-time workflow event streaming to clients using Server-Sent Events (SSE).

## Streamable HTTP Transport

### Single Endpoint Pattern

Following MCP specification, we use a **single HTTP POST endpoint** that supports both:
- JSON responses for synchronous requests
- Server-Sent Events (SSE) for streaming responses

**Endpoint**: `POST /api/v1/applications/{id}/stream`

### Request Format

```http
POST /api/v1/applications/LN1234567890/stream HTTP/1.1
Host: api.loandefenders.com
Authorization: Bearer <entra_id_token>
Accept: text/event-stream
Content-Type: application/json

{
  "action": "process",
  "include_events": ["executor_invoked", "executor_completed", "workflow_output"]
}
```

**Headers**:
- `Authorization`: Entra ID bearer token (required)
- `Accept`: `text/event-stream` for streaming, `application/json` for single response
- `Content-Type`: `application/json`

### Response Format

**SSE Stream** (Accept: text/event-stream):
```http
HTTP/1.1 200 OK
Content-Type: text/event-stream
Cache-Control: no-cache
Connection: keep-alive

event: workflow_started
id: evt_001
data: {"jsonrpc":"2.0","method":"workflow/started","params":{...}}

event: executor_invoked
id: evt_002
data: {"jsonrpc":"2.0","method":"workflow/executor_invoked","params":{...}}
```

**JSON Response** (Accept: application/json):
```http
HTTP/1.1 200 OK
Content-Type: application/json

{
  "application_id": "LN1234567890",
  "status": "COMPLETED",
  "final_decision": {...}
}
```

## Event Format (JSON-RPC Style)

All events follow JSON-RPC 2.0 message format:

```json
{
  "jsonrpc": "2.0",
  "method": "workflow/event_type",
  "params": {
    "timestamp": "2025-09-28T10:30:00Z",
    ...
  }
}
```

## Event Types

### Workflow Lifecycle Events

#### workflow_started
Workflow execution began.

```json
{
  "jsonrpc": "2.0",
  "method": "workflow/started",
  "params": {
    "application_id": "LN1234567890",
    "workflow_id": "wf_abc123",
    "state": "RUNNING",
    "timestamp": "2025-09-28T10:30:00Z"
  }
}
```

#### workflow_status
Workflow state changed.

```json
{
  "jsonrpc": "2.0",
  "method": "workflow/status",
  "params": {
    "application_id": "LN1234567890",
    "workflow_id": "wf_abc123",
    "state": "PROCESSING",
    "current_executor": "credit_agent",
    "progress": 0.5,
    "timestamp": "2025-09-28T10:32:00Z"
  }
}
```

#### workflow_output
Workflow produced output (agent assessment).

```json
{
  "jsonrpc": "2.0",
  "method": "workflow/output",
  "params": {
    "application_id": "LN1234567890",
    "output_type": "IntakeAssessment",
    "data": {
      "validation_status": "COMPLETE",
      "routing_decision": "STANDARD",
      "confidence_score": 0.95,
      "data_quality_score": 1.0,
      "specialist_name": "Intake Agent",
      "celebration_message": "🦅 Eagle-eyed validation complete!",
      "next_agent": "credit"
    },
    "timestamp": "2025-09-28T10:30:15Z"
  }
}
```

#### workflow_failed
Workflow execution failed.

```json
{
  "jsonrpc": "2.0",
  "method": "workflow/failed",
  "params": {
    "application_id": "LN1234567890",
    "workflow_id": "wf_abc123",
    "error": {
      "code": "AGENT_TIMEOUT",
      "message": "Credit agent timed out after 30 seconds",
      "executor_id": "credit_agent",
      "recoverable": true
    },
    "timestamp": "2025-09-28T10:33:00Z"
  }
}
```

### Executor (Agent) Events

#### executor_invoked
Agent started processing.

```json
{
  "jsonrpc": "2.0",
  "method": "workflow/executor_invoked",
  "params": {
    "application_id": "LN1234567890",
    "executor_id": "intake_agent",
    "executor_name": "John_The_Eagle_Eye",
    "input_type": "LoanApplication",
    "timestamp": "2025-09-28T10:30:01Z"
  }
}
```

#### executor_completed
Agent finished processing.

```json
{
  "jsonrpc": "2.0",
  "method": "workflow/executor_completed",
  "params": {
    "application_id": "LN1234567890",
    "executor_id": "intake_agent",
    "executor_name": "John_The_Eagle_Eye",
    "output_type": "IntakeAssessment",
    "duration_ms": 1500,
    "success": true,
    "timestamp": "2025-09-28T10:30:02.5Z"
  }
}
```

#### executor_failed
Agent processing failed.

```json
{
  "jsonrpc": "2.0",
  "method": "workflow/executor_failed",
  "params": {
    "application_id": "LN1234567890",
    "executor_id": "credit_agent",
    "executor_name": "Hawk-Income - The Credit Guardian",
    "error": {
      "code": "MCP_SERVER_UNAVAILABLE",
      "message": "Credit verification service unavailable",
      "retryable": true
    },
    "timestamp": "2025-09-28T10:32:30Z"
  }
}
```

### Agent Streaming Events

#### agent_run_update
Agent streaming progress update.

```json
{
  "jsonrpc": "2.0",
  "method": "workflow/agent_run_update",
  "params": {
    "application_id": "LN1234567890",
    "executor_id": "intake_agent",
    "update_type": "thinking",
    "message": "Analyzing loan amount and income ratio...",
    "progress": 0.3,
    "timestamp": "2025-09-28T10:30:01.5Z"
  }
}
```

## Client Implementation

### JavaScript/TypeScript

```typescript
const eventSource = new EventSource(
  'https://api.loandefenders.com/api/v1/applications/LN1234567890/stream',
  {
    headers: {
      'Authorization': `Bearer ${entraToken}`
    }
  }
);

// Handle workflow lifecycle events
eventSource.addEventListener('workflow_started', (event) => {
  const data = JSON.parse(event.data);
  console.log('Workflow started:', data.params);
});

eventSource.addEventListener('workflow_output', (event) => {
  const data = JSON.parse(event.data);
  const assessment = data.params.data;

  // Update UI with assessment
  updateAgentCard(data.params.output_type, assessment);
});

// Handle executor events
eventSource.addEventListener('executor_invoked', (event) => {
  const data = JSON.parse(event.data);
  showAgentProcessing(data.params.executor_name);
});

eventSource.addEventListener('executor_completed', (event) => {
  const data = JSON.parse(event.data);
  markAgentComplete(data.params.executor_name, data.params.duration_ms);
});

// Handle errors
eventSource.addEventListener('workflow_failed', (event) => {
  const data = JSON.parse(event.data);
  showError(data.params.error.message);
});

eventSource.onerror = (error) => {
  console.error('EventSource error:', error);

  // Reconnect after 5 seconds
  setTimeout(() => {
    eventSource.close();
    connectToStream();
  }, 5000);
};

// Clean up
window.addEventListener('beforeunload', () => {
  eventSource.close();
});
```

### Python

```python
import httpx
import json

async def stream_workflow_events(application_id: str, entra_token: str):
    url = f"https://api.loandefenders.com/api/v1/applications/{application_id}/stream"

    async with httpx.AsyncClient() as client:
        async with client.stream(
            "POST",
            url,
            headers={
                "Authorization": f"Bearer {entra_token}",
                "Accept": "text/event-stream"
            },
            timeout=None
        ) as response:
            async for line in response.aiter_lines():
                if line.startswith("event: "):
                    event_type = line[7:]
                elif line.startswith("data: "):
                    event_data = json.loads(line[6:])

                    # Handle event
                    if event_data["method"] == "workflow/output":
                        assessment = event_data["params"]["data"]
                        print(f"Assessment: {assessment}")

                    elif event_data["method"] == "workflow/executor_completed":
                        executor = event_data["params"]["executor_name"]
                        duration = event_data["params"]["duration_ms"]
                        print(f"{executor} completed in {duration}ms")
```

### React Hook Example

```typescript
import { useEffect, useState } from 'react';

interface WorkflowEvent {
  method: string;
  params: any;
}

export function useWorkflowStream(applicationId: string, token: string) {
  const [events, setEvents] = useState<WorkflowEvent[]>([]);
  const [isConnected, setIsConnected] = useState(false);
  const [error, setError] = useState<Error | null>(null);

  useEffect(() => {
    const eventSource = new EventSource(
      `https://api.loandefenders.com/api/v1/applications/${applicationId}/stream`,
      {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      }
    );

    eventSource.onopen = () => setIsConnected(true);

    eventSource.addEventListener('workflow_output', (event) => {
      const data = JSON.parse(event.data);
      setEvents(prev => [...prev, data]);
    });

    eventSource.addEventListener('executor_completed', (event) => {
      const data = JSON.parse(event.data);
      setEvents(prev => [...prev, data]);
    });

    eventSource.onerror = (err) => {
      setError(new Error('Stream connection error'));
      setIsConnected(false);
    };

    return () => {
      eventSource.close();
      setIsConnected(false);
    };
  }, [applicationId, token]);

  return { events, isConnected, error };
}
```

## Error Handling

### Connection Errors

**Client disconnected**: Server detects client disconnect and stops sending events.

**Server unavailable**: Client should implement exponential backoff retry:
```javascript
let retryDelay = 1000; // Start with 1 second

eventSource.onerror = () => {
  setTimeout(() => {
    retryDelay = Math.min(retryDelay * 2, 30000); // Max 30 seconds
    reconnect();
  }, retryDelay);
};
```

### Event Processing Errors

Clients should handle malformed events gracefully:

```javascript
eventSource.addEventListener('workflow_output', (event) => {
  try {
    const data = JSON.parse(event.data);
    processAssessment(data.params.data);
  } catch (error) {
    console.error('Failed to process event:', error);
    // Continue listening for next event
  }
});
```

## Performance Considerations

### Event Filtering

Clients can request specific event types to reduce bandwidth:

```json
{
  "action": "process",
  "include_events": ["workflow_output", "executor_completed"],
  "exclude_events": ["agent_run_update"]
}
```

### Compression

Server supports gzip compression for event streams:

```http
Accept-Encoding: gzip
```

### Keep-Alive

Server sends heartbeat comments every 30 seconds:

```
: heartbeat
```

This prevents proxy timeouts and confirms connection is alive.

## Security

### Authentication

Every SSE connection requires valid Entra ID token in `Authorization` header.

**Token Expiration**: Clients must handle token expiration:
1. Detect 401 Unauthorized response
2. Acquire new token
3. Reconnect with new token

### Rate Limiting

SSE connections count toward API rate limits:
- Maximum 10 concurrent streams per user
- Maximum 1000 events per minute per connection

### Data Privacy

Events never contain PII in plaintext:
- Use `applicant_id` (UUID) instead of names
- Application IDs are masked in logs (`LN123456****`)
- Sensitive assessment data is encrypted in transit (TLS 1.3)

## Testing

### Manual Testing with cURL

```bash
curl -N \
  -H "Authorization: Bearer ${ENTRA_TOKEN}" \
  -H "Accept: text/event-stream" \
  -X POST \
  https://api.loandefenders.com/api/v1/applications/LN1234567890/stream
```

### Automated Testing

```python
import pytest
from httpx_sse import aconnect_sse

@pytest.mark.asyncio
async def test_workflow_stream():
    async with aconnect_sse(
        client,
        "POST",
        f"/applications/{application_id}/stream",
        headers={"Authorization": f"Bearer {token}"}
    ) as event_source:
        events = []
        async for event in event_source.aiter_sse():
            events.append(json.loads(event.data))
            if event.event == "workflow_output":
                break

        assert len(events) > 0
        assert events[-1]["method"] == "workflow/output"
```

## Changelog

### v1.0.0 (2025-09-28)
- Initial streaming protocol
- Streamable HTTP transport (MCP-aligned)
- JSON-RPC 2.0 event format
- Workflow and executor event types