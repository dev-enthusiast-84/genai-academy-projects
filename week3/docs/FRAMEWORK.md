# Recall Framework

## One-liner

My agent helps fitness-club members withdraw personalization consent and remove linked questionnaire data across three independent services, with automated discovery and verification.

## Target Performance

- Investigate, review, and obtain approval: under 3 minutes in 9 of 10 controlled scenarios
- Zero false positives (records never deleted without explicit approval)
- Zero undetected deletions (every deletion verified)
- Graceful handling of transient service outages

## Template Mapping

| Template Placeholder | Recall Answer |
|---|---|
| **Who the agent helps** | Fitness-club members managing personal data privacy |
| **Task or outcome** | Withdraw personalization consent and remove linked questionnaire data |
| **Where it works** | Club Portal, Class Booking, and Member Offers, through the Recall privacy dashboard |
| **Manual work replaced** | Contacting each service, finding retained copies, and checking removal |
| **Main steps** | Investigate the trail → Review scope → Evaluate proposal → Obtain approval → Remove → Verify |
| **Tools used** | Six workflow tools (discover_records, trace_lineage, inspect_service, delete_approved_records, verify_withdrawal, notify_withdrawal_status) |
| **Human handoff** | Unclear intent or evidence; always before deletion |
| **Success criterion** | Proposed target: complete a verified withdrawal in under three minutes in at least 9 of 10 controlled scenarios, zero false positives, zero undetected deletions |

## Six Workflow Tools

| Tool | Responsibility |
|---|---|
| **discover_records** | Investigator reads authorized record metadata |
| **trace_lineage** | Investigator follows explicit source relationships |
| **inspect_service** | Investigator checks current record presence and version |
| **delete_approved_records** | Guarded executor performs only approved removal |
| **verify_withdrawal** | Application verifies absence and configured customer-experience checks |
| **notify_withdrawal_status** | Optional application notification after relevant status transitions |

## Questionnaire Answers

| Field | Answer |
|---|---|
| **Agent goal** | Withdraw the selected fitness consent and its explicitly linked information across the tracked apps, not guessing about shared dependencies or silent scope expansion |
| **Surface** | Recall's local privacy dashboard alongside Club Portal, Class Booking, and Member Offers. A fixed system with no external deletion or model unlearning |
| **Steps** | Consent and sharing → visible source deletion → interpret → discover → trace → inspect → scope review → propose → judge → obtain approval → delete with retries → verify independently |
| **Tools** | `discover_records`, `trace_lineage`, `inspect_service`, `delete_approved_records`, `verify_withdrawal`, `notify_withdrawal_status` |
| **Memory** | Session conversation and credentials are separate from persistent SQLite workflow state. Requests retain lineage and withdrawal markers until explicit demo reset |
| **Hard limits** | No unapproved or cross-user deletion; no guessed lineage, silent scope expansion, or protected-booking deletion |
| **Human-in-the-loop** | Review the exact targets, consent withdrawal, suppression, and evaluation findings before execution |
| **Failure handling** | Bound investigation and revision rounds; block unsafe or unverifiable proposals; inspect uncertain workflows with human judgment |
| **Success measure** | Proposed target: complete a verified withdrawal in under three minutes in at least 9 of 10 controlled scenarios, zero false positives, zero undetected deletions |

## Roles and Responsibilities

| Component | Decision or Responsibility |
|---|---|
| **Investigator agent** | Selects authorized read tools, identifies the intended source, and follows recorded sharing evidence |
| **Scope reviewer agent** | Challenges intent alignment, preservation, shared dependencies, and unsupported assumptions |
| **LLM judge stage** | Assesses the proposal against evidence and returns findings for bounded correction before approval |
| **Guarded application code** | Enforces hard checks, exact human approval, versions, execution order, consent withdrawal, retries, and blocking re-ingestion |
| **Outcome auditor agent** | Interprets independent post-execution checks and reports unresolved evidence without expanding authorization |

There are three operational agent roles plus a model-based evaluation stage. The three customer applications and Recall operate independently with no cross-service infrastructure; each test scenario resets or corrupts state to verify behavior under realistic conditions.

## Customer Workflow

1. **Consent** — User gives consent in Club Portal
2. **Sharing** — Data shared to Class Booking and Member Offers
3. **Personalization** — User sees personalized content in both apps
4. **Request** — User requests withdrawal in Recall Dashboard
5. **Investigation** — LLM agents discover and trace data
6. **Review** — Multiple agents review the proposal
7. **Approval** — User approves the exact deletion plan
8. **Execution** — Records deleted from all three services
9. **Verification** — Independent verification that data is gone

## Boundaries and Human Control

Only explicit source relationships establish lineage. Shared-source derivatives require clarification before inclusion. Persisted workflow metadata supports interruption and recovery. Source bodies and credentials are excluded from the system—only metadata and user consent flow through the workflow.

## Evaluation

Measure:
- Missed records
- Unrelated proposals
- Clarification requests (should be rare)
- Unsupported completion
- Protected booking deletion
- False positives or negatives
- Cycle time

See [evaluation methodology](EVALUATION.md) for detailed metrics.

---

**Framework Version**: 1.0  
**Last Updated**: 2026-09-16
