# Withdrawal System Usage Guide

Rebuilt multi-agent system with MCP, tools, and LLM judge.

## System Overview

The withdrawal system orchestrates a multi-agent investigation:

1. **Investigator Agent** — Uses tools to discover records and trace dependencies
2. **Scope Reviewer Agent** — Challenges findings and checks completeness
3. **Judge Agent** — Evaluates proposal against evidence (LLM as judge)
4. **Auditor Agent** — Verifies deletion completion

## Quick Start

```python
from withdrawal import Engine, ModelClient
from withdrawal.review import review_plan

# Initialize engine
engine = Engine(".runtime/fitness-local")

# Create model clients for each agent
clients = {
    "investigator": ModelClient(
        base_url="https://openrouter.ai/api/v1",
        api_key="your-provider-key",
        model="openai/gpt-5.4-mini",
        provider="openrouter",
    ),
    "reviewer": ModelClient(
        base_url="https://openrouter.ai/api/v1",
        api_key="your-provider-key",
        model="anthropic/claude-sonnet-4.6",
        provider="openrouter",
    ),
    "judge": ModelClient(
        base_url="https://openrouter.ai/api/v1",
        api_key="your-provider-key",
        model="anthropic/claude-sonnet-4.6",
        provider="openrouter",
    ),
    "auditor": ModelClient(
        base_url="https://openrouter.ai/api/v1",
        api_key="your-provider-key",
        model="openai/gpt-5.4-mini",
        provider="openrouter",
    ),
}

# Run multi-agent review
result = review_plan(
    engine=engine,
    clients=clients,
    user="U1",
    request_text="I want to withdraw my fitness data from all connected apps"
)

print(f"Action: {result.action}")  # propose, clarify, reject
print(f"Message: {result.message}")
print(f"Judge Recommendation: {result.judge_recommendation}")
print(f"Judge Reasoning: {result.judge_reasoning}")
```

## Core Components

### Engine (core.py)

Manages withdrawal workflow and state:

```python
from withdrawal import Engine, BoundaryError

engine = Engine(".runtime/data")

# Discover records
records = engine.discover_records("U1", query="D1")

# Trace dependencies
lineage = engine.trace_lineage("U1", "D1")

# Check record state
state = engine.inspect_service("U1", "V1")

# Manage consent
engine.grant_consent("U1")
engine.withdraw_consent("U1")

# Create withdrawal request
request = engine.create_request(
    user_id="U1",
    root_ids=["D1"],
    target_ids=["D1", "T1", "V1"],
)

# Approve and execute
engine.approve_request(request["id"], "U1")
result = engine.execute_deletion(request["id"], "U1")
```

### Model Client (agent.py)

Communicates with LLM providers:

```python
from withdrawal.agent import ModelClient, INVESTIGATOR_TOOLS

client = ModelClient(
    base_url="https://openrouter.ai/api/v1",
    api_key="your-provider-key",
    model="openai/gpt-5.4-mini",
)

# List available models
models = client.models()

# Make inference with tools
response = client.complete(
    messages=[{"role": "user", "content": "Find records for D1"}],
    tools=INVESTIGATOR_TOOLS,
)

if response.get("tool_calls"):
    for call in response["tool_calls"]:
        print(f"Tool: {call['function']['name']}")
```

### Multi-Agent Review (review.py)

Orchestrates investigation:

```python
from withdrawal.review import MultiAgentReview

review = MultiAgentReview(engine, clients, user_id="U1")

# Investigation phase
investigation = review.investigate("Withdraw my fitness data")

# Scope review phase
feedback = review.review_proposal(
    investigation["findings"],
    ["D1", "T1", "V1"]
)

# Judge evaluation (LLM as judge)
judge_result = review.judge_proposal(
    investigation["findings"],
    feedback,
    ["D1", "T1", "V1"]
)

# Full review
result = review.review_plan("Withdraw my fitness data")
```

### Judge Agent (evaluate.py)

Evaluates proposals using LLM:

```python
from withdrawal.evaluate import JudgeAgent, Recommendation

judge = JudgeAgent(clients["judge"], engine, "U1")

# Evaluate proposal
evaluation = judge.evaluate(
    investigation="Found records D1, T1, V1 with dependencies...",
    review_feedback="Scope looks complete",
    proposed_targets=["D1", "T1", "V1"],
)

print(evaluation.recommendation)  # APPROVE, REJECT, CLARIFY
print(evaluation.reasoning)
print(evaluation.issues)
print(evaluation.suggestions)

# Check for protected records
protected = judge.check_protected_records(["D1", "T1"])

# Check scope completeness
completeness = judge.check_scope_completeness(["D1"], ["D1", "T1", "V1"])
```

### HTTP Services (services.py)

Integrate with customer apps:

```python
from withdrawal.services import HttpServices

services = HttpServices()

# Check health
health = services.health_check()

# Get catalogs
catalogs = services.catalog_all("U1")

# Delete from specific service
success = services.delete_record("documents", "U1", "D1")
```

### MCP Server (mcp_server.py)

Expose tools via MCP protocol:

```python
from withdrawal.mcp_server import create_mcp_server

server = create_mcp_server(engine, "U1", port=8104)

# List available tools
tools = server.get_tools()

# Run server
server.run()  # Blocking

# Or async
import asyncio
asyncio.run(server.start())
```

### MCP Client (mcp_client.py)

Call MCP server tools:

```python
from withdrawal.mcp_client import create_mcp_client

client = create_mcp_client()

# Check health
is_healthy = client.health_check()

# Get tools
tools = client.get_tools()

# Call tool synchronously
result = client.call_tool_sync(
    "discover_records",
    {"query": ""}
)
```

### Notifications (notifications.py)

Optional event notifications:

```python
from withdrawal.notifications import NotificationManager, NotificationEvent

manager = NotificationManager()

# Send notification
manager.notify(
    event=NotificationEvent.AWAITING_APPROVAL,
    message="Your withdrawal request is ready for approval",
    context={"user_id": "U1", "request_id": "abc123"}
)

# Or use convenience function
from withdrawal.notifications import notify

notify(
    NotificationEvent.COMPLETE,
    "Your withdrawal has been verified complete"
)
```

## Configuration

Set environment variables:

```bash
# LLM Provider
LLM_PROVIDER=openrouter
LLM_BASE_URL=https://openrouter.ai/api/v1
OPENROUTER_API_KEY=your-key

# Agent Models
LLM_INVESTIGATOR_MODEL=openai/gpt-5.4-mini
LLM_SCOPE_REVIEWER_MODEL=anthropic/claude-sonnet-4.6
LLM_JUDGE_MODEL=anthropic/claude-sonnet-4.6
LLM_AUDITOR_MODEL=openai/gpt-5.4-mini

# Notifications (optional)
NOTIFICATION_ENABLED=true
NOTIFICATION_PROVIDER=email
NOTIFICATION_SMTP_HOST=smtp.gmail.com
NOTIFICATION_SMTP_PORT=587
NOTIFICATION_SMTP_USERNAME=your-email@gmail.com
NOTIFICATION_SMTP_PASSWORD=app-password
NOTIFICATION_FROM_EMAIL=your-email@gmail.com
NOTIFICATION_TO_EMAIL=recipient@example.com

# MCP
RECALL_TOOL_TRANSPORT=mcp
RECALL_MCP_PORT=8104
```

## Architecture

```
User Request
    ↓
MultiAgentReview.review_plan()
    ↓
    ├─ Investigator (discovers/traces records via tools)
    ├─ Scope Reviewer (challenges findings)
    ├─ Judge Agent (evaluates proposal) ← LLM as judge
    └─ Auditor (verifies completion)
    ↓
ReviewResult (action: propose/clarify/reject)
```

## Workflow States

1. **awaiting_approval** — Plan created, awaiting human approval
2. **approved** — Human approved withdrawal
3. **executing** — Deletions in progress
4. **partial** — Some deletions succeeded
5. **complete** — All deletions verified

## Exception Handling

```python
from withdrawal import BoundaryError
from withdrawal.agent import ModelError

try:
    engine.create_request(...)
except BoundaryError as e:
    print(f"Workflow boundary violation: {e}")

try:
    response = client.complete(messages)
except ModelError as e:
    print(f"LLM service error: {e}")
```

## Testing

```python
# Use scripted mode for testing
request = engine.create_request(
    user_id="U1",
    root_ids=["D1"],
    target_ids=["D1", "T1"],
    origin="scripted_rehearsal",  # Not a live agent
)
```

## See Also

- `docs/architecture.md` — System design
- `docs/configuration.md` — Detailed configuration
- `docs/api.md` — API reference
- `docs/troubleshooting.md` — Common issues
