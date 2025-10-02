# Loan Defenders API Endpoints Specification

## Base URL

```
Production: https://api.loandefenders.com/api/v1
Staging: https://staging-api.loandefenders.com/api/v1
Development: http://localhost:8000/api/v1
```

## Authentication

All API endpoints require **Azure Entra ID** authentication using Bearer tokens.

**Header Required**:
```http
Authorization: Bearer <entra_id_token>
```

**Token Acquisition**:
```bash
# Azure CLI
az login
az account get-access-token --resource https://api.loandefenders.com
```

**Token Claims Required**:
- `aud`: `https://api.loandefenders.com`
- `roles`: One or more of `loan.apply`, `loan.view`, `loan.admin`

## Rate Limiting

- **Applications**: 10 applications per hour per user
- **Chat Messages**: 10 messages per minute per application
- **Document Uploads**: 20 uploads per hour per user
- **General API**: 1000 requests per minute per user

Rate limit headers in responses:
```http
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 995
X-RateLimit-Reset: 1727518800
```

---

## Application Management

### Create Application

Start a new loan application workflow.

**Endpoint**: `POST /applications`

**Required Roles**: `loan.apply`

**Request Body**:
```json
{
  "applicant_name": "Intake Agent Doe",
  "applicant_id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "john.doe@example.com",
  "phone": "+14155552671",
  "date_of_birth": "1985-06-15T00:00:00Z",
  "loan_amount": 50000.00,
  "loan_purpose": "home_purchase",
  "loan_term_months": 360,
  "annual_income": 75000.00,
  "employment_status": "employed",
  "employer_name": "Tech Corp",
  "months_employed": 24,
  "monthly_expenses": 3000.00,
  "existing_debt": 15000.00,
  "assets": 100000.00
}
```

**Response 201** (Created):
```json
{
  "application_id": "LN1234567890",
  "session_id": "thread_abc123",
  "status": "STARTED",
  "current_stage": "INTAKE",
  "intake_agent": {
    "name": "John_The_Eagle_Eye",
    "description": "Sharp-eyed application validator"
  },
  "initial_message": "Hi! I'm Intake Agent, your application validator. I'll help you get started with your loan application. Let me take a quick look at your information...",
  "created_at": "2025-09-28T10:30:00Z",
  "expires_at": "2025-09-28T11:00:00Z"
}
```

**Response 400** (Bad Request):
```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid request data",
    "details": [
      {
        "field": "email",
        "error": "Invalid email format"
      },
      {
        "field": "loan_amount",
        "error": "Must be greater than zero"
      }
    ]
  },
  "request_id": "req_abc123",
  "timestamp": "2025-09-28T10:30:00Z"
}
```

**Response 401** (Unauthorized):
```json
{
  "error": {
    "code": "AUTHENTICATION_REQUIRED",
    "message": "Valid Entra ID token required",
    "details": "Authorization header missing or invalid"
  },
  "request_id": "req_abc123",
  "timestamp": "2025-09-28T10:30:00Z"
}
```

**Response 403** (Forbidden):
```json
{
  "error": {
    "code": "INSUFFICIENT_PERMISSIONS",
    "message": "User lacks required permissions",
    "details": "Role 'loan.apply' required"
  },
  "request_id": "req_abc123",
  "timestamp": "2025-09-28T10:30:00Z"
}
```

**Response 429** (Too Many Requests):
```json
{
  "error": {
    "code": "RATE_LIMIT_EXCEEDED",
    "message": "Rate limit exceeded",
    "details": "Maximum 10 applications per hour. Try again at 2025-09-28T11:30:00Z"
  },
  "request_id": "req_abc123",
  "timestamp": "2025-09-28T10:30:00Z"
}
```

**cURL Example**:
```bash
curl -X POST https://api.loandefenders.com/api/v1/applications \
  -H "Authorization: Bearer ${ENTRA_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "applicant_name": "Intake Agent Doe",
    "applicant_id": "550e8400-e29b-41d4-a716-446655440000",
    "email": "john.doe@example.com",
    "phone": "+14155552671",
    "date_of_birth": "1985-06-15T00:00:00Z",
    "loan_amount": 50000.00,
    "loan_purpose": "home_purchase",
    "loan_term_months": 360,
    "annual_income": 75000.00,
    "employment_status": "employed"
  }'
```

---

### Get Application Status

Retrieve current status and progress of a loan application.

**Endpoint**: `GET /applications/{application_id}`

**Required Roles**: `loan.view` (own applications) or `loan.admin` (all applications)

**Path Parameters**:
- `application_id` (string, required): Application ID (format: `LN\d{10}`)

**Response 200** (OK):
```json
{
  "application_id": "LN1234567890",
  "status": "PROCESSING",
  "current_stage": "CREDIT",
  "current_agent": {
    "name": "credit",
    "display_name": "Hawk-Income - The Credit Guardian"
  },
  "progress": 0.5,
  "stages_completed": ["INTAKE"],
  "stages_remaining": ["CREDIT", "INCOME", "RISK", "DECISION"],
  "assessments": {
    "intake": {
      "validation_status": "COMPLETE",
      "routing_decision": "STANDARD",
      "data_quality_score": 0.95,
      "completed_at": "2025-09-28T10:32:00Z"
    }
  },
  "created_at": "2025-09-28T10:30:00Z",
  "updated_at": "2025-09-28T10:35:00Z",
  "expires_at": "2025-09-28T11:00:00Z"
}
```

**Response 404** (Not Found):
```json
{
  "error": {
    "code": "APPLICATION_NOT_FOUND",
    "message": "Application not found",
    "details": "Application LN1234567890 does not exist or has expired"
  },
  "request_id": "req_abc123",
  "timestamp": "2025-09-28T10:30:00Z"
}
```

**Response 403** (Forbidden):
```json
{
  "error": {
    "code": "ACCESS_DENIED",
    "message": "Access denied to this application",
    "details": "User can only access their own applications"
  },
  "request_id": "req_abc123",
  "timestamp": "2025-09-28T10:30:00Z"
}
```

**cURL Example**:
```bash
curl -X GET https://api.loandefenders.com/api/v1/applications/LN1234567890 \
  -H "Authorization: Bearer ${ENTRA_TOKEN}"
```

---

### Cancel Application

Cancel an in-progress loan application.

**Endpoint**: `DELETE /applications/{application_id}`

**Required Roles**: `loan.apply` (own applications) or `loan.admin` (all applications)

**Path Parameters**:
- `application_id` (string, required): Application ID

**Response 200** (OK):
```json
{
  "application_id": "LN1234567890",
  "status": "CANCELLED",
  "cancelled_at": "2025-09-28T10:40:00Z",
  "message": "Application cancelled successfully"
}
```

**Response 404** (Not Found):
```json
{
  "error": {
    "code": "APPLICATION_NOT_FOUND",
    "message": "Application not found",
    "details": "Application LN1234567890 does not exist"
  },
  "request_id": "req_abc123",
  "timestamp": "2025-09-28T10:30:00Z"
}
```

**Response 409** (Conflict):
```json
{
  "error": {
    "code": "CANNOT_CANCEL",
    "message": "Application cannot be cancelled",
    "details": "Application has already been completed or cancelled"
  },
  "request_id": "req_abc123",
  "timestamp": "2025-09-28T10:30:00Z"
}
```

**cURL Example**:
```bash
curl -X DELETE https://api.loandefenders.com/api/v1/applications/LN1234567890 \
  -H "Authorization: Bearer ${ENTRA_TOKEN}"
```

---

## Conversational Chat

### Send Chat Message

Send a chat message to the intake agent for conversational loan intake.

**Endpoint**: `POST /applications/{application_id}/chat`

**Required Roles**: `loan.apply`

**Path Parameters**:
- `application_id` (string, required): Application ID

**Request Body**:
```json
{
  "message": "My annual income is $75,000 and I work at Tech Corp"
}
```

**Response 200** (OK):
```json
{
  "message_id": "msg_abc123",
  "agent_name": "John_The_Eagle_Eye",
  "agent_response": "Great! That's a solid income. I see you work at Tech Corp. How long have you been with them?",
  "assessment": {
    "validation_status": "INCOMPLETE",
    "fields_collected": ["annual_income", "employer_name"],
    "fields_remaining": ["months_employed", "existing_debt"],
    "data_quality_score": 0.75
  },
  "next_question": "How many months have you been employed at Tech Corp?",
  "suggested_responses": [
    "Less than 6 months",
    "6-12 months",
    "1-2 years",
    "More than 2 years"
  ],
  "workflow_stage": "INTAKE",
  "intake_complete": false,
  "timestamp": "2025-09-28T10:31:00Z"
}
```

**Response 200** (Intake Complete):
```json
{
  "message_id": "msg_xyz789",
  "agent_name": "John_The_Eagle_Eye",
  "agent_response": "Perfect! I have all the information I need. Your application looks great! 🦅 Eagle eyes verified everything. You're all set for the next step!",
  "assessment": {
    "validation_status": "COMPLETE",
    "routing_decision": "STANDARD",
    "confidence_score": 0.95,
    "data_quality_score": 1.0,
    "celebration_message": "🦅 Eagle-eyed validation complete! Your application is ready to soar!",
    "next_agent": "credit"
  },
  "workflow_stage": "INTAKE_COMPLETE",
  "intake_complete": true,
  "next_step": {
    "agent": "Hawk-Income - The Credit Guardian",
    "description": "Hawk-Income will now assess your creditworthiness",
    "estimated_time": "2-3 minutes"
  },
  "timestamp": "2025-09-28T10:35:00Z"
}
```

**Response 429** (Too Many Requests):
```json
{
  "error": {
    "code": "RATE_LIMIT_EXCEEDED",
    "message": "Too many chat messages",
    "details": "Maximum 10 messages per minute. Try again in 30 seconds"
  },
  "request_id": "req_abc123",
  "timestamp": "2025-09-28T10:30:00Z"
}
```

**cURL Example**:
```bash
curl -X POST https://api.loandefenders.com/api/v1/applications/LN1234567890/chat \
  -H "Authorization: Bearer ${ENTRA_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"message": "My annual income is $75,000"}'
```

---

### Get Chat History

Retrieve the complete conversation history for an application.

**Endpoint**: `GET /applications/{application_id}/chat/history`

**Required Roles**: `loan.view`

**Path Parameters**:
- `application_id` (string, required): Application ID

**Query Parameters**:
- `limit` (integer, optional): Maximum number of messages (default: 100, max: 500)
- `offset` (integer, optional): Pagination offset (default: 0)

**Response 200** (OK):
```json
{
  "application_id": "LN1234567890",
  "total_messages": 8,
  "messages": [
    {
      "message_id": "msg_001",
      "role": "assistant",
      "agent_name": "John_The_Eagle_Eye",
      "text": "Hi! I'm Intake Agent, your application validator...",
      "timestamp": "2025-09-28T10:30:00Z"
    },
    {
      "message_id": "msg_002",
      "role": "user",
      "text": "My annual income is $75,000",
      "timestamp": "2025-09-28T10:31:00Z"
    },
    {
      "message_id": "msg_003",
      "role": "assistant",
      "agent_name": "John_The_Eagle_Eye",
      "text": "Great! That's a solid income...",
      "timestamp": "2025-09-28T10:31:15Z"
    }
  ],
  "pagination": {
    "offset": 0,
    "limit": 100,
    "has_more": false
  }
}
```

**cURL Example**:
```bash
curl -X GET "https://api.loandefenders.com/api/v1/applications/LN1234567890/chat/history?limit=50" \
  -H "Authorization: Bearer ${ENTRA_TOKEN}"
```

---

## Real-Time Streaming

### Stream Workflow Events

Stream real-time workflow events using Streamable HTTP (aligned with MCP).

**Endpoint**: `POST /applications/{application_id}/stream`

**Required Roles**: `loan.view`

**Path Parameters**:
- `application_id` (string, required): Application ID

**Headers**:
```http
Authorization: Bearer <entra_id_token>
Accept: text/event-stream
```

**Request Body** (optional):
```json
{
  "action": "process",
  "include_events": ["executor_invoked", "executor_completed", "workflow_output"]
}
```

**Response 200** (Server-Sent Events):
```http
HTTP/1.1 200 OK
Content-Type: text/event-stream
Cache-Control: no-cache
Connection: keep-alive

event: workflow_started
id: evt_001
data: {"jsonrpc":"2.0","method":"workflow/started","params":{"state":"RUNNING","timestamp":"2025-09-28T10:30:00Z"}}

event: executor_invoked
id: evt_002
data: {"jsonrpc":"2.0","method":"workflow/executor_invoked","params":{"executor_id":"intake_agent","timestamp":"2025-09-28T10:30:01Z"}}

event: executor_completed
id: evt_003
data: {"jsonrpc":"2.0","method":"workflow/executor_completed","params":{"executor_id":"intake_agent","duration_ms":1500,"timestamp":"2025-09-28T10:30:02.5Z"}}

event: workflow_output
id: evt_004
data: {"jsonrpc":"2.0","method":"workflow/output","params":{"output_type":"IntakeAssessment","data":{"validation_status":"COMPLETE","routing_decision":"STANDARD"},"timestamp":"2025-09-28T10:30:02.5Z"}}

event: executor_invoked
id: evt_005
data: {"jsonrpc":"2.0","method":"workflow/executor_invoked","params":{"executor_id":"credit_agent","timestamp":"2025-09-28T10:30:03Z"}}
```

**Event Types**:
- `workflow_started`: Workflow execution began
- `workflow_status`: Workflow state change
- `executor_invoked`: Agent started processing
- `executor_completed`: Agent finished processing
- `executor_failed`: Agent encountered error
- `workflow_output`: Agent produced assessment
- `workflow_failed`: Workflow failed
- `agent_run_update`: Agent streaming update (progress, thinking)

**JavaScript Client Example**:
```javascript
const eventSource = new EventSource(
  'https://api.loandefenders.com/api/v1/applications/LN1234567890/stream',
  {
    headers: {
      'Authorization': `Bearer ${entraToken}`
    }
  }
);

eventSource.addEventListener('workflow_output', (event) => {
  const data = JSON.parse(event.data);
  console.log('Assessment received:', data.params.data);
});

eventSource.addEventListener('executor_completed', (event) => {
  const data = JSON.parse(event.data);
  console.log(`Agent ${data.params.executor_id} completed`);
});

eventSource.onerror = (error) => {
  console.error('EventSource error:', error);
  eventSource.close();
};
```

**Python Client Example**:
```python
import httpx

async with httpx.AsyncClient() as client:
    async with client.stream(
        "POST",
        "https://api.loandefenders.com/api/v1/applications/LN1234567890/stream",
        headers={
            "Authorization": f"Bearer {entra_token}",
            "Accept": "text/event-stream"
        },
        timeout=None
    ) as response:
        async for line in response.aiter_lines():
            if line.startswith("data: "):
                data = json.loads(line[6:])
                print(f"Event: {data['method']}")
```

---

## Document Upload

### Upload Document

Upload a document for loan application processing.

**Endpoint**: `POST /applications/{application_id}/documents`

**Required Roles**: `loan.apply`

**Path Parameters**:
- `application_id` (string, required): Application ID

**Request** (multipart/form-data):
```http
Content-Type: multipart/form-data; boundary=----WebKitFormBoundary

------WebKitFormBoundary
Content-Disposition: form-data; name="file"; filename="paystub.pdf"
Content-Type: application/pdf

<binary content>
------WebKitFormBoundary
Content-Disposition: form-data; name="document_type"

pay_stub
------WebKitFormBoundary--
```

**Supported Document Types**:
- `pay_stub`: Pay stub or salary slip
- `bank_statement`: Bank account statement
- `tax_return`: Tax return document
- `id_document`: Government-issued ID
- `proof_of_address`: Utility bill or lease agreement
- `employment_letter`: Employment verification letter
- `other`: Other supporting documents

**Supported File Formats**:
- PDF: `.pdf`
- Images: `.jpg`, `.jpeg`, `.png`
- Documents: `.docx`

**File Size Limits**:
- Maximum per file: 10 MB
- Maximum total per application: 50 MB

**Response 201** (Created):
```json
{
  "document_id": "doc_abc123",
  "filename": "paystub.pdf",
  "size": 524288,
  "mime_type": "application/pdf",
  "document_type": "pay_stub",
  "storage_url": "https://loandefenders.blob.core.windows.net/documents/LN1234567890/doc_abc123.pdf",
  "uploaded_at": "2025-09-28T10:30:00Z",
  "expires_at": "2025-10-28T10:30:00Z"
}
```

**Response 400** (Bad Request):
```json
{
  "error": {
    "code": "INVALID_FILE",
    "message": "Invalid file upload",
    "details": "File size exceeds 10MB limit"
  },
  "request_id": "req_abc123",
  "timestamp": "2025-09-28T10:30:00Z"
}
```

**Response 413** (Payload Too Large):
```json
{
  "error": {
    "code": "FILE_TOO_LARGE",
    "message": "File exceeds size limit",
    "details": "Maximum file size is 10MB"
  },
  "request_id": "req_abc123",
  "timestamp": "2025-09-28T10:30:00Z"
}
```

**cURL Example**:
```bash
curl -X POST https://api.loandefenders.com/api/v1/applications/LN1234567890/documents \
  -H "Authorization: Bearer ${ENTRA_TOKEN}" \
  -F "file=@paystub.pdf" \
  -F "document_type=pay_stub"
```

---

### List Documents

Get all documents uploaded for an application.

**Endpoint**: `GET /applications/{application_id}/documents`

**Required Roles**: `loan.view`

**Path Parameters**:
- `application_id` (string, required): Application ID

**Response 200** (OK):
```json
{
  "application_id": "LN1234567890",
  "total_documents": 3,
  "total_size": 1572864,
  "documents": [
    {
      "document_id": "doc_abc123",
      "filename": "paystub.pdf",
      "size": 524288,
      "mime_type": "application/pdf",
      "document_type": "pay_stub",
      "uploaded_at": "2025-09-28T10:30:00Z"
    },
    {
      "document_id": "doc_def456",
      "filename": "bank_statement.pdf",
      "size": 1048576,
      "mime_type": "application/pdf",
      "document_type": "bank_statement",
      "uploaded_at": "2025-09-28T10:35:00Z"
    }
  ]
}
```

**cURL Example**:
```bash
curl -X GET https://api.loandefenders.com/api/v1/applications/LN1234567890/documents \
  -H "Authorization: Bearer ${ENTRA_TOKEN}"
```

---

### Delete Document

Delete an uploaded document.

**Endpoint**: `DELETE /applications/{application_id}/documents/{document_id}`

**Required Roles**: `loan.apply`

**Path Parameters**:
- `application_id` (string, required): Application ID
- `document_id` (string, required): Document ID

**Response 200** (OK):
```json
{
  "document_id": "doc_abc123",
  "deleted_at": "2025-09-28T10:40:00Z",
  "message": "Document deleted successfully"
}
```

**cURL Example**:
```bash
curl -X DELETE https://api.loandefenders.com/api/v1/applications/LN1234567890/documents/doc_abc123 \
  -H "Authorization: Bearer ${ENTRA_TOKEN}"
```

---

## Health & Monitoring

### Health Check

Check API service health status.

**Endpoint**: `GET /health`

**Authentication**: None (public endpoint)

**Response 200** (Healthy):
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "timestamp": "2025-09-28T10:30:00Z",
  "checks": {
    "database": "healthy",
    "redis": "healthy",
    "blob_storage": "healthy",
    "foundry": "healthy"
  },
  "uptime_seconds": 86400
}
```

**Response 503** (Unhealthy):
```json
{
  "status": "unhealthy",
  "version": "1.0.0",
  "timestamp": "2025-09-28T10:30:00Z",
  "checks": {
    "database": "healthy",
    "redis": "unhealthy",
    "blob_storage": "healthy",
    "foundry": "healthy"
  },
  "errors": [
    {
      "component": "redis",
      "message": "Connection timeout"
    }
  ]
}
```

**cURL Example**:
```bash
curl https://api.loandefenders.com/api/v1/health
```

---

### Metrics

Prometheus-compatible metrics endpoint.

**Endpoint**: `GET /metrics`

**Authentication**: None (public endpoint, internal network only)

**Response 200**:
```
# HELP http_requests_total Total HTTP requests
# TYPE http_requests_total counter
http_requests_total{method="POST",endpoint="/applications",status="201"} 1250

# HELP http_request_duration_seconds HTTP request latency
# TYPE http_request_duration_seconds histogram
http_request_duration_seconds_bucket{le="0.1"} 980
http_request_duration_seconds_bucket{le="0.5"} 1200
http_request_duration_seconds_bucket{le="1.0"} 1240
http_request_duration_seconds_bucket{le="+Inf"} 1250
http_request_duration_seconds_sum 125.5
http_request_duration_seconds_count 1250

# HELP workflow_completions_total Total workflow completions
# TYPE workflow_completions_total counter
workflow_completions_total{status="success"} 950
workflow_completions_total{status="failed"} 25

# HELP agent_processing_duration_seconds Agent processing time
# TYPE agent_processing_duration_seconds histogram
agent_processing_duration_seconds{agent="intake"} 1.5
agent_processing_duration_seconds{agent="credit"} 2.3
```

---

## Error Codes Reference

| Code | HTTP Status | Description |
|------|-------------|-------------|
| `VALIDATION_ERROR` | 400 | Request validation failed |
| `INVALID_FILE` | 400 | File upload validation failed |
| `AUTHENTICATION_REQUIRED` | 401 | Missing or invalid token |
| `TOKEN_EXPIRED` | 401 | Entra ID token expired |
| `ACCESS_DENIED` | 403 | User lacks access to resource |
| `INSUFFICIENT_PERMISSIONS` | 403 | User lacks required role |
| `APPLICATION_NOT_FOUND` | 404 | Application does not exist |
| `DOCUMENT_NOT_FOUND` | 404 | Document does not exist |
| `CANNOT_CANCEL` | 409 | Application cannot be cancelled |
| `FILE_TOO_LARGE` | 413 | File exceeds size limit |
| `RATE_LIMIT_EXCEEDED` | 429 | Too many requests |
| `INTERNAL_SERVER_ERROR` | 500 | Server error |
| `SERVICE_UNAVAILABLE` | 503 | Service temporarily unavailable |

---

## SDK Examples

### TypeScript/JavaScript

```typescript
import { LoanDefendersClient } from '@loandefenders/api-client';

const client = new LoanDefendersClient({
  baseUrl: 'https://api.loandefenders.com/api/v1',
  getAccessToken: async () => {
    // Acquire Entra ID token
    return await acquireEntraIdToken();
  }
});

// Create application
const application = await client.applications.create({
  applicant_name: 'Intake Agent Doe',
  email: 'john.doe@example.com',
  loan_amount: 50000,
  loan_purpose: 'home_purchase',
  // ...
});

// Stream workflow events
const stream = await client.applications.stream(application.application_id);
stream.on('workflow_output', (assessment) => {
  console.log('Assessment:', assessment);
});

// Send chat message
const chatResponse = await client.chat.send(application.application_id, {
  message: 'My annual income is $75,000'
});
```

### Python

```python
from loan_defenders_client import LoanDefendersClient
from azure.identity.aio import DefaultAzureCredential

credential = DefaultAzureCredential()
client = LoanDefendersClient(
    base_url="https://api.loandefenders.com/api/v1",
    credential=credential
)

# Create application
application = await client.applications.create(
    applicant_name="Intake Agent Doe",
    email="john.doe@example.com",
    loan_amount=50000.0,
    loan_purpose="home_purchase"
)

# Stream workflow events
async for event in client.applications.stream(application.application_id):
    if event.method == "workflow/output":
        print(f"Assessment: {event.params.data}")

# Send chat message
response = await client.chat.send(
    application.application_id,
    message="My annual income is $75,000"
)
```

---

## Changelog

### v1.0.0 (2025-09-28)
- Initial API release
- Application management endpoints
- Conversational chat with intake agent
- Streamable HTTP for real-time events
- Document upload support
- Entra ID authentication