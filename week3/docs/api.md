# Implemented API

These interfaces are defined in `withdrawal/core.py`, `agent.py`, `review.py`, and `service_app.py`. The demo is scoped to synthetic user `U1`.

## Model-callable reads

| Tool | Arguments | Result |
| --- | --- | --- |
| `discover_records` | `query: str`; empty string lists authorized metadata | List of ID, service, user_id, version, kind, title; no body content |
| `trace_lineage` | `root_id: str` | Root, records, edges, and shared_dependencies |
| `inspect_service` | `record_id: str` | Metadata, observed version and state: present / absent / unknown |

Discovery is a case-insensitive substring filter, not a structured query language or semantic search. `kind:paid_booking user_id:U1` is not a supported filter expression; use an empty query and inspect the metadata. Shared dependencies have incoming edges from outside the selected source closure; ordinary descendant chains are not shared ownership.

## Python workflow

```python
from withdrawal.agent import ModelClient, settings
from withdrawal.core import Engine
from withdrawal.review import review_plan
from withdrawal.services import configured_services

config = settings('.env')
clients = {role: ModelClient(config['base_url'], config['api_key'], model, config['provider'])
           for role, model in config['models'].items()}
engine = Engine('.runtime/fitness/recall', configured_services(), require_review=True)
try:
    result = review_plan(engine, clients, 'U1',
                        'Withdraw my fitness interests questionnaire and its linked copies; keep my paid booking.')
    # Present result to the user. Do not approve or execute automatically.
finally:
    engine.close()
```

Run with the same service URLs/token as the launcher to use connected stores. `review_plan` returns action, message, trace and, when a proposal exists, plan. A passing plan is `awaiting_approval`; model clarification is not authorization.

After actual human approval, application code calls `engine.approve(request_id, user)`, then `execute_with_audit(engine, user, request_id, audit_callback, stop_after=None)` from `withdrawal.workflow`. Its LangGraph execution node calls `delete_approved_records`; the next node invokes the verification/audit callback unless execution was interrupted. Recovery uses the same saved request; `revoke` stops further attempts, and `verify_withdrawal` saves current independent presence/behavior results. `audit_outcome` adds the model auditor report without upgrading failed verification. `BoundaryError` signals scope/approval violations; `ModelError` signals provider/model output problems.

## Service HTTP contract

`GET /` serves the customer page; `GET /health` returns the service identity. Club Portal supports CSRF-protected `POST /consent` with `agree=on` and `POST /delete-profile`.

The internal adapter sends JSON to `POST /api/{operation}` with `Authorization: Bearer <runtime token>`:

| Operation | Fields | Effect |
| --- | --- | --- |
| `read` | id, user | Return record or null |
| `behavior` | user | Return active, blocked, consent-linked and visible IDs |
| `delete` | id, user, version | Version-checked removal and local blocking |
| `block` | user, ids | Block consent-linked stable IDs |
| `share` | id, user | Record sharing permission and insert permitted synthetic fixture record |
| `replay` | id, user | Reinsert only if sharing is permitted and ID not blocked |
| `reset` | none | Explicit demo reset of that service |

There are no running `/catalog` or `/record/<id>` REST routes. Paid booking deletion is rejected. The runtime token is for this loopback demo, not a production authentication system.

## Optional MCP and notifications

`make install-mcp` installs the official MCP SDK; `RECALL_TOOL_TRANSPORT=mcp` starts streamable HTTP on `http://127.0.0.1:8104/mcp`. Three investigator reads plus a read-only customer-experience inspection are exposed; the investigator adapter allows only its three tools.

Only Slack incoming-webhook status notifications are implemented. Configure and opt in through the dashboard; there is no SMTP/email provider. See [configuration](configuration.md).
