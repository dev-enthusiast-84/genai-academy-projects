# Recall: agent framework

## One-liner

Recall helps fitness-club members withdraw personalization consent and remove linked questionnaire copies through a privacy dashboard, replacing manual requests and removal checks across three apps; it autonomously investigates with three read tools, coordinates reviewed and human-approved removal and verification, hands off when intent or evidence is unclear and before deletion, and targets verified removal with the paid booking preserved in under three minutes in at least 9 of 10 completable controlled live trials.

This is a target, not a measured live success rate. Manual effort means repeated requests, finding retained copies, and checking each app; no baseline time or financial saving has been measured.

## Handout questionnaire

| Handout field | Answer |
| --- | --- |
| Agent goal | Withdraw the member's selected personalization consent, remove its explicitly linked copies, and verify the result while preserving the paid booking. |
| Where do people use it? | The Recall Streamlit privacy dashboard, alongside Club Portal, Class Booking, and Member Offers running as three separate local HTTP services. The public browser demo is a smaller, simulated deployment described below. |
| What steps does it take, in order? | 1. Interpret the request and choose read tools; 2. trace and inspect the selected source's descendants; 3. perform scope review, deterministic checks, and model judging with bounded repairs; 4. obtain exact human approval; 5. withdraw consent, block reuse, delete with bounded retries, and verify; 6. audit the outcome. |
| What can it actually do? | Three model-callable reads: `discover_records`, `trace_lineage`, `inspect_service`. Application actions are `delete_approved_records` (approved write), `verify_withdrawal` (service reads and saved receipt), and optional `notify_withdrawal_status` (Slack send, configured and explicitly enabled by the operator). |
| What does it need to remember? | SQLite stores plans, lineage, versions, exact approval, retry counts, and verification across restarts; request payloads expire after 24 hours when cleanup runs. Consent, provenance, suppression, and notification deduplication remain until reset; UI inputs and configuration are separate from receipts, and the local `.env` can persist credentials. |
| What should it never do? | Delete without current exact approval, widen scope silently, infer lineage from similar text, expose another user's records through the scoped tools, delete protected bookings/listings, or call a partial/unknown result complete. It does not claim external deletion, backup erasure, legal compliance, or model unlearning. |
| Human-in-the-loop | The user reviews readable record/app names and checks the approval box before withdrawal; technical mappings remain expandable. Clarifications require a revised request; changed scope/versions require a fresh plan and approval, and further attempts can be revoked. |
| What happens when something breaks? | Investigation is bounded to 8 model turns and 24 read calls per round; review allows 2 repairs, and each target allows 2 deletion retries after the first attempt. Uncertain writes are inspected before retry, progress is saved, unavailable services remain unknown, and unresolved work is reported as partial. |
| How do you know it worked? | The target is at least 9/10 completable controlled live trials finishing within 3 minutes, with every approved record independently absent, ingestion blocked, consent withdrawn, and the booking preserved. Any unauthorized deletion or false completion fails a trial; outages and clarification scenarios are scored separately for correct handling. |

## Why this is agentic

The investigator chooses read tools, their arguments, their order, and whether to propose or clarify. Scope reviewer and outcome auditor are separate roles, with an independent model judge stage; application code controls bounded repair and durable execution rather than giving the model a delete tool.

The connected Python app uses LangGraph StateGraph orchestration for investigation, deterministic checks, scope review, the separate judge, and at most two repair rounds. A second graph runs approved execution followed by verification/auditing. The investigator retains its bounded direct-provider read-tool loop. SQLite Engine remains the authority for saved plans, approval and execution recovery; this adoption does not use LangGraph checkpointing or interrupt-based approval. The browser-hosted demo does not run LangGraph.

## Local versus hosted

| Capability | Local connected app | Hosted browser demo |
| --- | --- | --- |
| Customer data | Three local processes, three SQLite service stores | Three service objects in same-origin browser storage |
| Model workflow | Investigator, scope reviewer, judge, outcome auditor | One live investigator |
| Approval/execution | Persisted Python guards and HTTP service operations | JavaScript guards and simulated store mutations |
| Recovery | SQLite survives process restart | Browser storage survives reload; clearing it resets data |
| Optional tools | Read-only MCP transport and opt-in Slack notification | Neither MCP nor Slack |
| Purpose | Primary Week 3 implementation | Accessible interaction/workflow demonstration |

Queued invitations are synthetic previews: there is no real sender or delivery queue. Removing one verifies deletion of the stored preview; cancellation of a real external queue is not implemented.

See [architecture](architecture.md), [evaluation](EVALUATION.md), and [submission checklist](SUBMISSION.md).
