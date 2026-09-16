# API Reference

Complete reference for Recall's LLM agents and tools.

## Overview

Recall uses a multi-agent system where specialized LLM agents work together to investigate data and manage withdrawals. Each agent has access to specific tools defined in the workflow.

## Agent Roles

### Investigator Agent

**Purpose**: Discover records, trace dependencies, inspect service state

**Model**: `LLM_INVESTIGATOR_MODEL` (default: `openai/gpt-5.4-mini`)

**Available Tools**:
- `discover_records`
- `trace_lineage`
- `inspect_service`

### Scope Reviewer Agent

**Purpose**: Review proposals, challenge assumptions, ensure correctness

**Model**: `LLM_SCOPE_REVIEWER_MODEL` (default: `anthropic/claude-sonnet-4.6`)

**Available Tools**:
- Review feedback (via LLM reasoning)

### Judge Agent

**Purpose**: Evaluate proposals against evidence, identify issues

**Model**: `LLM_JUDGE_MODEL` (default: `openai/gpt-5.4-mini`)

**Available Tools**:
- Evaluation feedback (via LLM reasoning)

### Auditor Agent

**Purpose**: Verify outcomes, report findings post-deletion

**Model**: `LLM_AUDITOR_MODEL` (default: `openai/gpt-5.4-mini`)

**Available Tools**:
- `inspect_service` (verification only)

## Tool Definitions

### discover_records

Discover authorized record metadata.

**Signature**:
```python
def discover_records(query: str) -> List[Dict]
```

**Parameters**:
- `query` (string): Search term or filter
  - Empty string: list all records
  - By ID: "D1", "V2"
  - By title: "questionnaire", "preference"
  - By service: "documents", "search"
  - By kind: "derived", "inferred"

**Returns**:
```python
[
  {
    "id": "D1",
    "title": "Fitness Questionnaire",
    "service": "documents",
    "kind": "root",
    "version": 1
  },
  # ... more records
]
```

**Constraints**:
- Only returns authorized records for the user
- No document content included
- Metadata only

**Raises**:
- `BoundaryError` if query fails

---

### trace_lineage

Trace explicit dependencies for a root record.

**Signature**:
```python
def trace_lineage(root_id: str) -> Dict
```

**Parameters**:
- `root_id` (string): ID of root record to trace from (e.g., "D1")

**Returns**:
```python
{
  "records": [
    {"id": "D1", "service": "documents", ...},
    {"id": "T1", "service": "search", ...},
    {"id": "V1", "service": "personalization", ...}
  ],
  "edges": [
    {"source": "D1", "target": "T1", "relationship": "derived_from"},
    {"source": "T1", "target": "V1", "relationship": "input_to"}
  ]
}
```

**Constraints**:
- Only explicit, recorded relationships
- Shared dependencies require clarification
- Returns empty if root doesn't exist

**Raises**:
- `BoundaryError` if read fails

---

### inspect_service

Check current presence and version of a record.

**Signature**:
```python
def inspect_service(record_id: str) -> Dict
```

**Parameters**:
- `record_id` (string): Record ID to check (e.g., "V1")

**Returns**:
```python
{
  "record_id": "V1",
  "state": "present",  # or "absent" or "unknown"
  "version": 3,
  "title": "Q1: Evening Yoga Preference",
  "service": "personalization"
}
```

**States**:
- `present`: Record exists and is accessible
- `absent`: Record has been verified deleted
- `unknown`: Service unavailable, state uncertain

**Raises**:
- `BoundaryError` if service rejects request

---

### delete_approved_records

Delete approved records (workflow only, not for agents).

**Signature**:
```python
def delete_approved_records(
  request_id: str,
  user_id: str,
  stop_after: Optional[int] = None
) -> Dict
```

**Parameters**:
- `request_id`: ID of approved withdrawal request
- `user_id`: User making the request
- `stop_after`: Optional max records to delete (for demos)

**Enforces**:
- Explicit approval (checked before deletion)
- Targeted scope only (won't delete unapproved records)
- Retry logic (up to 3 attempts per record)
- Audit trail (all deletions logged)

**Returns**:
```python
{
  "deleted": ["D1", "T1"],
  "failed": [],
  "total": 2,
  "status": "complete"
}
```

**Raises**:
- `BoundaryError` if approval missing or invalid

---

### verify_withdrawal

Verify deletion was successful (workflow only).

**Signature**:
```python
def verify_withdrawal(request_id: str, user_id: str) -> Dict
```

**Parameters**:
- `request_id`: ID of withdrawal request to verify
- `user_id`: User who made the request

**Process**:
1. Call `inspect_service()` for each target
2. Confirm `state == "absent"`
3. Run behavior checks
4. Report findings

**Returns**:
```python
{
  "verified_absent": 2,
  "unable_to_verify": 0,
  "total": 2,
  "behavior_checks": {
    "consent_withdrawn": "pass",
    "reingestion_blocked": "pass"
  }
}
```

**Raises**:
- `BoundaryError` if verification fails

---

## Data Models

### Record Metadata

```python
{
  "id": str,              # Unique record ID
  "service": str,         # Which service owns it
  "title": str,           # Human-readable title
  "version": int,         # Record version number
  "kind": str,            # "root", "derived", "inferred", etc.
  "created_at": int,      # Timestamp (seconds)
  "modified_at": int      # Timestamp (seconds)
}
```

### Withdrawal Request

```python
{
  "id": str,              # Request ID
  "user_id": str,         # User making request
  "status": str,          # "pending", "approved", "executing", "complete"
  "targets": [Record],    # Records to delete
  "created_at": int,      # Timestamp
  "approved_at": int,     # Approval timestamp
  "completed_at": int     # Completion timestamp
}
```

### Agent Message

LLM messages follow OpenAI format:

```python
{
  "role": "user" | "assistant",
  "content": str,
  "tool_calls": Optional[List]
}
```

---

## Error Handling

### BoundaryError

Raised when workflow boundaries are violated.

```python
from withdrawal.core import BoundaryError

try:
    records = engine.discover_records(user_id, query)
except BoundaryError as e:
    # Handle: "Application rejected the scoped service request"
    print(f"Error: {e}")
```

### ModelError

Raised when LLM requests fail.

```python
from withdrawal.agent import ModelError

try:
    message = client.complete(messages, tools)
except ModelError as e:
    # Handle: "Provider returned HTTP 402"
    print(f"Model error: {e}")
```

---

## Configuration

### Environment Variables

```env
# LLM Provider
LLM_PROVIDER=openrouter
LLM_BASE_URL=https://openrouter.ai/api/v1
OPENROUTER_API_KEY=your-key

# Model Selection
LLM_INVESTIGATOR_MODEL=openai/gpt-5.4-mini
LLM_SCOPE_REVIEWER_MODEL=anthropic/claude-sonnet-4.6
LLM_JUDGE_MODEL=anthropic/claude-sonnet-4.6
LLM_AUDITOR_MODEL=openai/gpt-5.4-mini
```

### Programmatic Configuration

```python
from withdrawal.agent import ModelClient

client = ModelClient(
    base_url='https://openrouter.ai/api/v1',
    api_key='your-provider-key',
    model='openai/gpt-5.4-mini',
    provider='openrouter'
)

# Get available models
models = client.models()

# Make completion request
response = client.complete(
    messages=[{"role": "user", "content": "..."}],
    tools=[...]
)
```

---

## Usage Examples

### Discover Records

```python
from withdrawal.core import Engine

engine = Engine('.runtime/fitness-local')

# Find all records
all_records = engine.discover_records('U1', '')

# Search by ID
d1_records = engine.discover_records('U1', 'D1')

# Search by service
documents = engine.discover_records('U1', 'documents')
```

### Trace Dependencies

```python
# Get full dependency graph
lineage = engine.trace_lineage('U1', 'D1')

for record in lineage['records']:
    print(f"{record['id']}: {record['title']}")

for edge in lineage['edges']:
    print(f"{edge['source']} -> {edge['target']}")
```

### Inspect Services

```python
# Check if record exists
state = engine.inspect_service('U1', 'V1')

print(f"State: {state['state']}")  # present, absent, unknown
print(f"Version: {state['version']}")
print(f"Title: {state['title']}")
```

### Multi-Agent Investigation

```python
from withdrawal.review import review_plan

clients = {
    'investigator': ModelClient(..., model='openai/gpt-5.4-mini'),
    'scope_reviewer': ModelClient(..., model='anthropic/claude-sonnet-4.6'),
    'judge': ModelClient(..., model='anthropic/claude-sonnet-4.6'),
    'auditor': ModelClient(..., model='openai/gpt-5.4-mini')
}

# Run full investigation
result = review_plan(
    engine=engine,
    clients=clients,
    user='U1',
    request_text='Withdraw my personalization consent for D1'
)

print(f"Action: {result['action']}")  # propose, clarify, reject
print(f"Message: {result['message']}")
```

---

## Rate Limits & Quotas

### OpenAI and OpenRouter

- **Requests**: Based on account quota
- **Rate limit**: Subject to OpenRouter limits
- **Timeout**: 45 seconds per request

---

## Versioning

API versioning follows semantic versioning:

- **MAJOR**: Breaking changes (incompatible agent tools)
- **MINOR**: New features (new tools, new agents)
- **PATCH**: Bug fixes, improvements

Current version: **1.0.0**

---

## Support

For questions about the API:

1. Check [Architecture](architecture.md) for design
2. See [Configuration](configuration.md) for setup
3. Review [Troubleshooting](troubleshooting.md) for issues
4. Check [Contributing](contributing.md) for development

---

**Last Updated**: 2026-09-16
