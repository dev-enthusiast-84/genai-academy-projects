# Architecture

A deep dive into Recall's system design and components.

## System Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    Recall Dashboard (Streamlit)             │
│                     http://127.0.0.1:8501                  │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                    Engine & Workflow Logic                  │
│  (Core consent, withdrawal, verification, audit)           │
└──────────────────────────┬──────────────────────────────────┘
                           │
        ┌──────────────────┼──────────────────┐
        │                  │                  │
        ▼                  ▼                  ▼
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│ LLM Agents   │  │ Service APIs │  │ Local SQLite │
│ (LiteLLM)    │  │ (Flask)      │  │ Database     │
└──────────────┘  └──────────────┘  └──────────────┘
        │                  │
    Ollama Models    3 Customer Services
```

## Component Architecture

### 1. Frontend Layer

**Streamlit Dashboard** (`app.py`)
- Reactive UI for investigation & withdrawal
- Model selection & configuration
- Real-time progress tracking
- Receipt & verification display

### 2. Engine Layer

**Core Engine** (`withdrawal/core.py`)
- Manages consent state
- Coordinates deletion workflow
- Enforces approval gates
- Tracks request lifecycle

### 3. LLM Agent Layer

**ModelClient** (`withdrawal/agent.py`)
- Communicates with LiteLLM proxy
- Defines tool schemas for agents
- Handles model errors gracefully

**Four Agent Roles:**

```
┌──────────────────────────────────────────────────┐
│          Investigation Workflow                  │
├──────────────────────────────────────────────────┤
│                                                  │
│  1. Investigator Agent                          │
│     ├─ discover_records()                       │
│     ├─ trace_lineage()                          │
│     └─ inspect_service()                        │
│                                                  │
│  2. Scope Reviewer Agent                        │
│     └─ Review & challenge findings              │
│                                                  │
│  3. Judge Agent                                 │
│     └─ Evaluate proposal against evidence       │
│                                                  │
│  4. Auditor Agent (post-deletion)               │
│     └─ Verify outcomes & report findings        │
│                                                  │
└──────────────────────────────────────────────────┘
```

### 4. Service Integration Layer

**HttpServices** (`withdrawal/services.py`)
- Proxies requests to three local Flask apps
- Enforces user-scoped access
- Returns authorized record metadata

**Service Endpoints:**

```
Club Portal (8101)
├─ GET /catalog          → List records
├─ GET /record/{id}      → Read record
├─ DELETE /record/{id}   → Delete record
└─ GET /health           → Service status

Class Booking (8102)
├─ GET /catalog
├─ GET /record/{id}
├─ DELETE /record/{id}
└─ GET /health

Member Offers (8103)
├─ GET /catalog
├─ GET /record/{id}
├─ DELETE /record/{id}
└─ GET /health
```

### 5. LLM Backend Layer

**LiteLLM Proxy** (localhost:4000)
```
litellm --model ollama/phi
├─ Ollama Connection
│  ├─ phi (2.7B)
│  └─ orca-mini (3B)
└─ OpenAI-Compatible API
   └─ /chat/completions
```

### 6. Data Layer

**SQLite Database** (`.runtime/fitness-local/recall/recall.db`)

```sql
-- Main tables
catalog              -- Records accessible to user
requests             -- Withdrawal requests
targets              -- Records targeted for deletion
edges                -- Dependencies between records
reviews              -- LLM agent findings
```

## Data Flow

### Investigation Flow

```
User Request
    ↓
investigator.discover_records("D1")
    ↓ (calls LLM)
LiteLLM → Ollama (phi 2.7B)
    ↓
Tool Response: [List of records]
    ↓
investigator.trace_lineage("D1")
    ↓ (calls LLM)
LiteLLM → Ollama
    ↓
Tool Response: [Dependency graph]
    ↓
investigator.inspect_service("V1")
    ↓ (calls LLM)
LiteLLM → Ollama
    ↓
Tool Response: [Record state: present/absent/unknown]
    ↓
scope_reviewer.review_plan(findings)
    ↓ (calls LLM)
LiteLLM → Ollama (orca-mini 3B)
    ↓
Review: [Approve/Challenge with findings]
    ↓
Workflow Continues or Loops
```

### Deletion Flow

```
User Approval
    ↓
engine.approve(request_id)
    ↓
For Each Target Record:
  delete_approved_records()
    ├─ Verify approval
    ├─ Check pre-conditions
    ├─ Call service DELETE
    └─ Retry up to 3x
    ↓
audit_outcome(request_id)
    ├─ Call auditor agent
    └─ Verify via inspect_service()
    ↓
Mark Complete
```

## Agent Tools

### Investigator Tools

```python
discover_records(query)
  - Read authorized record metadata
  - Search by ID, title, service, kind
  - No document content returned

trace_lineage(root_id)
  - Read explicit dependency graph
  - Follow source relationships
  - Return edges and nodes

inspect_service(record_id)
  - Check current record presence
  - Return version and state
  - Unavailable services return 'unknown'
```

### Workflow Tools

```python
# Only accessible after approval
delete_approved_records(request_id, user)
  - Delete targeted records
  - Enforce approval gates
  - Support bounded retries

verify_withdrawal(request_id, user)
  - Post-deletion verification
  - Check absence via inspect_service
  - Run behavior checks

notify_withdrawal_status(engine, user, request_id, config)
  - Optional email/Slack notification
  - Triggered on status changes
```

## Configuration

### Environment Variables

```env
# LLM Provider Configuration
LLM_PROVIDER=litellm
LLM_BASE_URL=http://localhost:4000/v1
LLM_API_KEY=sk-1234

# Role-specific Models
LLM_INVESTIGATOR_MODEL=ollama/phi
LLM_SCOPE_REVIEWER_MODEL=ollama/orca-mini
LLM_JUDGE_MODEL=ollama/phi
LLM_AUDITOR_MODEL=ollama/phi

# Optional Features
NOTIFICATION_ENABLED=false
RECALL_TOOL_TRANSPORT=http
```

## Performance Characteristics

### Latency (typical)

| Operation | Time | Factor |
|-----------|------|--------|
| LLM inference (phi) | 5-10s | Model size |
| LLM inference (orca-mini) | 10-20s | Model size + reasoning |
| Service call | 50-100ms | Network I/O |
| Database query | 10-50ms | Index usage |
| Deletion operation | 200-500ms | Cascading updates |

### Throughput

- **Concurrent requests**: 1 (designed for single user)
- **Requests per hour**: 10-20 (typical)
- **Models per hour**: ~2-3 complete workflows

## Security Considerations

### Authentication

- Single-user demo (U1 - Avery Example)
- No sign-in required
- User ID hardcoded in app.py

### Authorization

- User-scoped service queries
- Explicit approval gates
- Tools only accessible in correct workflow state

### Data Protection

- Local-only operation
- No external network calls
- No model training on data
- SQLite database on disk

## Scalability Notes

**Current Design**

- Single-user, single-process
- In-memory model inference
- Synchronous workflow execution

**Bottlenecks**

- LLM inference latency (30-50s per investigation)
- Model GPU memory (if using GPU)
- SQLite concurrency limits

**For Production**

Would need:
- Multi-user authentication
- Async task queues (Celery, RQ)
- Distributed LLM serving (vLLM, Ray)
- PostgreSQL or similar
- Request rate limiting

## Extension Points

### Adding New Services

1. Create Flask app on new port
2. Register in `withdrawal/services.py`
3. Implement GET /catalog, /record/{id}, DELETE endpoints
4. Add to `PORTS` dictionary

### Customizing Models

Edit `.env`:
```env
LLM_INVESTIGATOR_MODEL=ollama/neural-chat
```

Must be available in Ollama: `ollama list`

### Adding New Tools

1. Define in `withdrawal/agent.py` (TOOLS list)
2. Implement handler in engine
3. Add to agent's allowed tool set

### Custom Notifications

Configure in `.env`:
```env
NOTIFICATION_ENABLED=true
NOTIFICATION_PROVIDER=slack
NOTIFICATION_WEBHOOK_URL=...
```

---

**Next**: [Configuration Guide](configuration.md) | [API Reference](api.md)
