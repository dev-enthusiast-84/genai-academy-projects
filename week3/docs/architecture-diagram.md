# Architecture Diagrams

Visual representations of Recall's system architecture.

## System Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                                                                               │
│                         🎯 RECALL SYSTEM ARCHITECTURE                        │
│                                                                               │
└─────────────────────────────────────────────────────────────────────────────┘

                            ┌──────────────────────┐
                            │  User's Browser      │
                            │  (Single Tab)        │
                            └──────────┬───────────┘
                                       │
                    ┌──────────────────┼──────────────────┐
                    │                  │                  │
                    ▼                  ▼                  ▼
            ┌────────────────┐  ┌────────────────┐  ┌────────────────┐
            │ Club Portal    │  │ Class Booking  │  │ Member Offers  │
            │ (8101)         │  │ (8102)         │  │ (8103)         │
            │                │  │                │  │                │
            │ Flask App      │  │ Flask App      │  │ Flask App      │
            │ Documents DB   │  │ Search DB      │  │ Personalization│
            └────────────────┘  └────────────────┘  └────────────────┘
                    ▲                  ▲                  ▲
                    │                  │                  │
                    │    ┌─────────────┴─────────────┐    │
                    │    │                           │    │
                    └────┤    Service Layer          ├────┘
                         │    (withdrawal/core.py)  │
                         │    - Consent Management  │
                         │    - Deletion Workflow   │
                         │    - Verification       │
                         └─────────────┬─────────────┘
                                       │
                    ┌──────────────────┼──────────────────┐
                    │                  │                  │
                    ▼                  ▼                  ▼
            ┌────────────────┐  ┌────────────────┐  ┌────────────────┐
            │ LLM Agents     │  │ SQLite DB      │  │ Streamlit UI   │
            │ (LiteLLM)      │  │ Workflow State │  │ (8501)         │
            │                │  │                │  │                │
            │ 4 Roles:       │  │ • Catalog      │  │ Dashboard      │
            │ • Investigator │  │ • Requests     │  │ • Model Select │
            │ • Reviewer     │  │ • Records      │  │ • Investigation│
            │ • Judge        │  │ • Edges        │  │ • Approval     │
            │ • Auditor      │  │ • Reviews      │  │ • Verification│
            └────────┬───────┘  └────────────────┘  └────────────────┘
                     │
                     ▼
            ┌────────────────┐
            │ Ollama Server  │
            │ (localhost)    │
            │                │
            │ Models:        │
            │ • phi (2.7B)   │
            │ • orca-mini    │
            │ • mistral      │
            │ • neural-chat  │
            │ • mixtral      │
            └────────────────┘
```

## Workflow: Investigation & Withdrawal

```
╔═════════════════════════════════════════════════════════════════════════════╗
║                     DATA WITHDRAWAL WORKFLOW                                 ║
╚═════════════════════════════════════════════════════════════════════════════╝

1️⃣  USER GIVES CONSENT
    ┌──────────────────────────────────────────────┐
    │ Club Portal (8101)                           │
    │ User: Give Consent                           │
    │ → Data shared to other services              │
    └──────────────────────────────────────────────┘
                            │
                            ▼
    Data Visible in:
    ├─ Class Booking (8102): T1 (class preferences)
    └─ Member Offers (8103): V1 (personalized offers)

2️⃣  USER REQUESTS WITHDRAWAL  
    ┌──────────────────────────────────────────────┐
    │ Recall Dashboard (8501)                      │
    │ User: "Investigate data trail"               │
    │ Request: Withdraw D1 questionnaire           │
    └──────────────────────────────────────────────┘
                            │
                            ▼

3️⃣  INVESTIGATION PHASE (LLM Multi-Agent)
    
    ┌─ Investigator Agent ─────────────────────────┐
    │ 1. discover_records("D1")                    │
    │    → Finds: D1 (documents service)           │
    │                                              │
    │ 2. trace_lineage("D1")                       │
    │    → Finds: D1 → T1 → V1 (dependency graph) │
    │                                              │
    │ 3. inspect_service(each_record)              │
    │    → Checks: All records present             │
    └──────────────────────────────────────────────┘
                            │
                            ▼
    
    ┌─ Scope Reviewer Agent ────────────────────────┐
    │ Reviews investigator's findings              │
    │ Challenges:                                  │
    │ • Is scope correct?                         │
    │ • Are dependencies complete?                │
    │ • Could anything be missed?                 │
    └──────────────────────────────────────────────┘
                            │
                            ▼
    
    ┌─ Judge Agent ─────────────────────────────────┐
    │ Evaluates proposal against evidence          │
    │ Determines:                                  │
    │ • Is the plan sound?                        │
    │ • Are there risks?                          │
    │ • Should it proceed?                        │
    └──────────────────────────────────────────────┘
                            │
                            ▼

4️⃣  USER REVIEWS PROPOSAL
    ┌──────────────────────────────────────────────┐
    │ Recall Dashboard (8501)                      │
    │ Shows:                                       │
    │ • Evidence trail (diagram)                   │
    │ • Records to delete (D1, T1, V1)             │
    │ • Findings from all agents                   │
    │                                              │
    │ User Decision:                               │
    │ ✓ Approve & Withdraw                         │
    └──────────────────────────────────────────────┘
                            │
                            ▼

5️⃣  EXECUTION PHASE
    
    ┌─ Safety Gates ────────────────────────────────┐
    │ ✓ Check user approval                        │
    │ ✓ Verify request is current                  │
    │ ✓ Confirm targets match approval             │
    │ ✓ Enforce retry limits (3 max per record)    │
    └──────────────────────────────────────────────┘
                            │
                            ▼
    
    ┌─ Deletion Execution ──────────────────────────┐
    │ For each record (D1, T1, V1):                │
    │                                              │
    │ Service Call: DELETE /record/{id}            │
    │ └─ If fails: Retry up to 3x                 │
    │                                              │
    │ Timeline:                                    │
    │ • D1 deleted from documents (8101)          │
    │ • T1 deleted from search (8102)             │
    │ • V1 deleted from personalization (8103)    │
    └──────────────────────────────────────────────┘
                            │
                            ▼

6️⃣  VERIFICATION PHASE
    
    ┌─ Auditor Agent ───────────────────────────────┐
    │ For each record:                             │
    │ 1. inspect_service(record_id)                │
    │    → Confirms: state == "absent"             │
    │                                              │
    │ 2. Run behavior checks:                      │
    │    • Consent withdrawn: ✓                    │
    │    • Re-ingestion blocked: ✓                 │
    │    • Data inaccessible: ✓                    │
    │                                              │
    │ 3. Generate audit report                     │
    └──────────────────────────────────────────────┘
                            │
                            ▼
    
    ┌──────────────────────────────────────────────┐
    │ Recall Dashboard (8501)                      │
    │ Shows: Verification Receipt                  │
    │ ✓ 2 / 2 records independently verified       │
    │ ✓ Withdrawal completed successfully          │
    │ ✓ Data cannot be re-added                    │
    │                                              │
    │ User can:                                    │
    │ • Download receipt (JSON)                    │
    │ • Verify in other services                   │
    │ • Check re-ingestion is blocked              │
    └──────────────────────────────────────────────┘

✅ WORKFLOW COMPLETE
```

## Component Interaction

```
┌───────────────────────────────────────────────────────────────────────────────┐
│                          COMPONENT COMMUNICATION                               │
└───────────────────────────────────────────────────────────────────────────────┘

Streamlit (8501)
     │
     ├─ Renders UI
     ├─ Handles user interactions
     ├─ Displays agent findings
     └─ Shows verification results
            │
            ▼
    ┌─ Engine (core.py)
    │  ├─ Manages consent state
    │  ├─ Coordinates workflow
    │  ├─ Enforces approval gates
    │  └─ Tracks request lifecycle
    │         │
    │         ├────────────────┬────────────────┬────────────────┐
    │         │                │                │                │
    │         ▼                ▼                ▼                ▼
    │    ┌────────────┐   ┌────────────┐  ┌────────────┐   ┌────────────┐
    │    │ Investigator    │   │ Scope Reviewer  │  │Judge       │   │ Auditor
    │    │ Agent      │   │ Agent       │  │Agent      │   │ Agent
    │    │ (phi)      │   │ (orca-mini) │  │(phi)      │   │ (phi)
    │    └────────────┘   └────────────┘  └────────────┘   └────────────┘
    │         │                │                │                │
    │         └────────────────┴────────────────┴────────────────┘
    │                          │
    │                          ▼
    │                 LiteLLM Proxy (4000)
    │                 OpenAI Compatible API
    │                          │
    │                          ▼
    │                    Ollama Server
    │                    (Local Inference)
    │
    ├─ Services (services.py)
    │  ├─ Proxies HTTP calls
    │  ├─ Enforces auth
    │  └─ Aggregates responses
    │         │
    │         ├─────────────┬─────────────┬─────────────┐
    │         │             │             │             │
    │         ▼             ▼             ▼             ▼
    │    ┌────────────┐ ┌────────────┐ ┌────────────┐
    │    │Club Portal │ │Class Booking│ │Member Offers
    │    │(8101)      │ │(8102)       │ │(8103)
    │    │Documents DB│ │Search DB   │ │Personalization
    │    └────────────┘ └────────────┘ └────────────┘
    │
    └─ Database (SQLite)
       ├─ Catalog (all records)
       ├─ Requests (workflow state)
       ├─ Targets (records to delete)
       ├─ Edges (dependencies)
       └─ Reviews (agent findings)
```

## Data Dependencies

```
ROOT RECORD (Questionnaire)
    │
    D1 (Fitness Questionnaire)
    ├─ User ID: U1
    ├─ Service: documents
    ├─ Title: "Club Questionnaire"
    └─ version: 1
            │
            ├─ Derived From:
            │  └─ User input in Club Portal
            │
            ├─ Linked To:
            │  └─ T1 (Class preferences)
            │
            └─ Implies:
               └─ User's fitness level
                  User's availability
                  User's interests
                       │
                       ├─ Used by: Class Booking
                       │  └─ T1 (Class Preferences)
                       │     ├─ User: U1
                       │     ├─ Service: search
                       │     ├─ Derived From: D1
                       │     └─ version: 1
                       │            │
                       │            └─ Used by: Member Offers
                       │               └─ V1 (Personalized Offers)
                       │                  ├─ User: U1
                       │                  ├─ Service: personalization
                       │                  ├─ Derived From: T1
                       │                  └─ version: 3
                       │
                       └─ Accessible by: Member Offers
                          └─ V1 (Personalized Offers)
                             ├─ Shows: Fitness-related promotions
                             └─ Based on: D1 → T1 analysis

WITHDRAWAL IMPACT:
    D1 deleted → T1 must be deleted → V1 must be deleted
    Chain reaction prevents orphaned or stale data
    User's fitness profile completely removed
```

## Multi-Agent Reasoning Flow

```
┌─────────────────────────────────────────────────────────────────────┐
│                   MULTI-AGENT DECISION FLOW                         │
└─────────────────────────────────────────────────────────────────────┘

           INVESTIGATOR AGENT
           ┌─────────────────────────┐
           │ Discovers: D1, T1, V1    │
           │ Traces: Dependencies     │
           │ Inspects: Current state  │
           │ Findings:                │
           │ ✓ All records found      │
           │ ✓ Dependencies traced    │
           │ ✓ All present            │
           └──────────────┬───────────┘
                          │
                          ▼ PASS TO REVIEWER
           
           SCOPE REVIEWER AGENT
           ┌─────────────────────────┐
           │ Reviews investigator's   │
           │ findings for:            │
           │ • Completeness           │
           │ • Scope correctness      │
           │ • Missed dependencies    │
           │ • Safety concerns        │
           │                          │
           │ Possible outcomes:       │
           │ ✓ Approved: Proceed      │
           │ ⚠ Challenge: Flag issue  │
           │ ✗ Reject: Stop workflow  │
           └──────────────┬───────────┘
                          │
                          ▼ PASS TO JUDGE
           
           JUDGE AGENT
           ┌─────────────────────────┐
           │ Final evaluation of      │
           │ proposal:                │
           │ • Against evidence       │
           │ • Against policy         │
           │ • Risk assessment        │
           │                          │
           │ Determines:              │
           │ ✓ Safe to proceed        │
           │ ⚠ Needs more review     │
           │ ✗ Should be blocked      │
           └──────────────┬───────────┘
                          │
                          ▼
           
           USER SEES ALL FINDINGS
           
           User can:
           ├─ Approve (all agents passed)
           ├─ Clarify (if asked by reviewer)
           └─ Reject (user discretion)
                          │
                          ▼ IF APPROVED
           
           EXECUTION + AUDITOR VERIFICATION
           
           Delete records, then:
           ┌─────────────────────────┐
           │ AUDITOR AGENT           │
           │ Independently verifies: │
           │ ✓ D1 absent             │
           │ ✓ T1 absent             │
           │ ✓ V1 absent             │
           │ ✓ Cannot be re-ingested │
           │ ✓ No side effects       │
           └─────────────────────────┘

SAFETY PRINCIPLE:
   Multiple independent agents review before deletion
   No single agent can authorize deletion alone
   User has final approval authority
   Post-deletion verification is mandatory
```

## Error Handling

```
┌───────────────────────────────────────────────────────────────────────┐
│                    ERROR HANDLING & RECOVERY                          │
└───────────────────────────────────────────────────────────────────────┘

Service Unavailable During Investigation
    ├─ inspect_service() returns "unknown"
    ├─ Workflow continues (doesn't block)
    ├─ User is informed of uncertain state
    └─ Deletion still proceeds (service may recover)

Service Fails During Deletion
    ├─ First attempt: Call DELETE
    ├─ If 4xx/5xx error:
    │  └─ Retry up to 3 times (backoff)
    ├─ If all retries fail:
    │  ├─ Mark record as "failed"
    │  ├─ Stop deletion of dependent records
    │  └─ Report to user for manual intervention
    └─ User can retry after fixing issue

Approval Expires (24 hours)
    ├─ Request not started within 24h
    ├─ Approval becomes invalid
    ├─ User must request withdrawal again
    └─ Prevents stale approvals

Approval Revoked Mid-Execution
    ├─ User can revoke at any time
    ├─ Stops ongoing deletion
    ├─ Preserves deleted records (if possible)
    └─ Allows full retry from start

Model Inference Timeout
    ├─ LLM call exceeds 45s
    ├─ Investigation fails
    ├─ User can retry with smaller model
    └─ Or manually approve based on available info
```

---

**Last Updated**: 2026-09-16  
**Version**: 1.0.0
