# Design: Production Content Strategist MVP

## Context

Building a production-grade agentic system in 2-3 days requires strategic choices to balance:
- **Real infrastructure** (PostgreSQL, Pinecone, Redis) for production readiness
- **Golden dataset** (seeded mock data) for demo speed without API integrations
- **Human feedback loops** at strategy and final review gates for responsible AI
- **Built-in observability** (LangSmith, Sentry, PostHog) for validation and debugging

The MVP prioritizes demonstrating the complete agentic workflow with real databases and observability, deferring real API integrations (LinkedIn, Substack) to Phase 2.

## Goals / Non-Goals

**Goals:**
- Build end-to-end agentic system (3 agents + 2 human gates) in 2-3 days
- Use production infrastructure (PostgreSQL, Pinecone, Redis) to prove scalability
- Demonstrate both workflows (LinkedIn-like + Webinar Notes)
- Include quality metrics (evals) and observability (tracing, errors, analytics)
- Establish clear Phase 2 upgrade path (real APIs, rich file formats, auto-extraction)
- Deploy to cloud (Replit + Vercel) with live demo links

**Non-Goals:**
- Real LinkedIn API integration (Phase 2)
- PDF/DOCX parsing (Phase 2)
- Automatic voice characteristic extraction (Phase 2)
- Real-time performance tracking (Phase 2)
- Multi-user workspaces (Phase 3)
- Fine-tuned models (Phase 4)

## Decisions

### 1. Golden Dataset Approach (MVP)
**Decision:** Seed PostgreSQL + Pinecone with 15 realistic pre-generated LinkedIn posts and engagement metrics. All workflows operate against this golden dataset.

**Rationale:**
- Eliminates need for LinkedIn API approval (enterprise-only, time-consuming)
- Enables complete end-to-end demo in 2-3 days
- Demonstrates system works end-to-end with realistic data
- Easy to transition to real APIs in Phase 2 (same database schema)

**Alternatives considered:**
- ❌ Real LinkedIn API: Requires enterprise approval, impossible in 2-3 days
- ❌ Unofficial scraping: Violates ToS, fragile, not production-ready
- ✅ Golden dataset with Phase 2 plan: Realistic, extensible, demo-ready

**Trade-off:** MVP won't track real user posts. Phase 2 replaces golden data with real LinkedIn posts.

---

### 2. Text-Only Input for MVP (Webinar Notes Workflow)
**Decision:** Accept text input only (paste or .txt file) for MVP. Phase 2 adds PDF/DOCX.

**Rationale:**
- PDF/DOCX parsing adds 3+ library dependencies (pypdf, python-docx)
- Text extraction is fragile and adds complexity
- Text-only is sufficient for demo (users paste content)
- Clear Phase 2 path with dedicated libraries

**Alternatives considered:**
- ❌ PDF/DOCX in MVP: Adds complexity, fragile parsing, extends timeline
- ✅ Text-only MVP + Phase 2 rich formats: Simple, extensible

**Trade-off:** Users must paste content (can't drag PDF). Phase 2 adds file upload support.

---

### 3. LangGraph for Orchestration (vs. Direct Calls)
**Decision:** Use LangGraph state machine for agent orchestration, not direct LLM calls.

**Rationale:**
- Provides structured state management for multi-agent workflow
- Human gates implemented as conditional edges (pause/resume)
- Full trace in LangSmith for debugging
- Same code runs on Replit (MVP) or Cloud Run (Phase 2)
- Enables complex feedback loops (rejection → retry)

**Alternatives considered:**
- ❌ Direct Claude API calls: No state management, harder to debug, can't pause
- ✅ LangGraph state machine: Clean, testable, production-pattern

**Trade-off:** Slightly more code than direct calls, but enables complex workflows.

---

### 4. LiteLLM for LLM Abstraction
**Decision:** Use LiteLLM as unified LLM interface routing to Claude via OpenRouter or direct API.

**Rationale:**
- Single interface for all agent LLM calls
- Easy fallback to alternative models (GPT, Gemini) if needed
- Built-in rate limiting, cost tracking, error handling
- Provider-agnostic (can switch from Claude → GPT during demo if Claude API fails)
- Integrated logging for observability

**Alternatives considered:**
- ❌ Direct Claude API: No fallback, no rate limiting, vendor lock-in
- ✅ LiteLLM: Flexible, resilient, Observable

**Trade-off:** One additional abstraction layer, but worth the resilience.

---

### 5. Pinecone + PostgreSQL (vs. Pinecone-only or Vector Search in DB)
**Decision:** Separate concerns: Pinecone for vector search, PostgreSQL for structured data.

**Rationale:**
- **Pinecone:** Semantic search (similarity), with metadata filtering
- **PostgreSQL:** Content, performance metrics, decisions, user data
- Each tool optimized for its job
- Clear separation of concerns
- Both scale independently

**Alternatives considered:**
- ❌ Pinecone only: Can't store structured metrics efficiently
- ❌ PostgreSQL pgvector only: Slower for large-scale vector search, not designed for it
- ✅ Pinecone + PostgreSQL: Best of both, clear separation

**Trade-off:** Two databases (vs. one), but each is simple to manage.

---

### 6. Supabase for PostgreSQL (vs. Self-hosted or Other Managed Services)
**Decision:** Use Supabase (managed PostgreSQL) with free tier for MVP.

**Rationale:**
- Free tier: 500MB storage, 100 connections (enough for demo)
- Built-in auth (for Phase 2)
- Built-in pgvector for future hybrid search
- Auto-backups, simple SSL
- Easy upgrade path (paid tier for Phase 2+)

**Alternatives considered:**
- ❌ Self-hosted PostgreSQL: Ops overhead, harder to deploy
- ❌ AWS RDS: Overkill for MVP, not free tier
- ✅ Supabase free tier: Simple, sufficient, scalable

**Trade-off:** Locked into Supabase, but can migrate to self-hosted if needed.

---

### 7. Replit for Backend (vs. Cloud Run or Local)
**Decision:** Deploy backend to Replit Hobby (free tier) for MVP. Phase 2 upgrades to Cloud Run.

**Rationale:**
- Free tier runs FastAPI fine
- Simple deployment (push to git)
- Can upgrade to Replit Starter ($7/month) if needed
- Clear upgrade path to Cloud Run (same Docker setup)

**Alternatives considered:**
- ❌ Cloud Run: More complex, slower to set up
- ❌ Local/ngrok: Not suitable for production demo
- ✅ Replit free with Cloud Run path: Fast to set up, upgrade path

**Trade-off:** Replit may sleep if idle. Mitigation: upgrade to Starter if needed.

---

### 8. Human Gates at Strategy & Final Review (vs. More/Fewer Gates)
**Decision:** Two decision points: (1) Strategy approval, (2) Final review. No gate after Creator.

**Rationale:**
- Strategy gate: User approves direction before expensive generation
- Final gate: User approves before publishing (responsible AI)
- No intermediate gate: Creator can iterate without gate (feedback routing handles it)
- Balances user control + workflow speed

**Alternatives considered:**
- ❌ No gates: Risky for AI-generated content
- ❌ Gate after Creator: Slows workflow unnecessarily
- ✅ Gates at strategy & final: Right balance

**Trade-off:** User must approve twice. Mitigation: quick approval flow.

---

### 9. Observability Stack (LangSmith + Sentry + PostHog)
**Decision:** Three-layer observability for debugging, error tracking, and analytics.

**Rationale:**
- **LangSmith:** Agent execution tracing (what did each agent do?)
- **Sentry:** Error tracking (what went wrong?)
- **PostHog:** User analytics (what did users do?)
- All three are free tier sufficient for MVP
- Critical for debugging during demo

**Alternatives considered:**
- ❌ No observability: Can't debug issues during demo
- ❌ Logging only: No structured tracing or analytics
- ✅ LangSmith + Sentry + PostHog: Complete visibility

**Trade-off:** Setup complexity (3 SDKs). Mitigation: minimal config (10 mins each).

---

### 10. Evals Framework (Accuracy + Quality + Latency)
**Decision:** Implement manual evals: recommendation accuracy (10 scenarios), draft quality (LLM-as-judge), latency testing.

**Rationale:**
- Recommendation accuracy: Validate agent makes right choices (manual check: 15 mins)
- Draft quality: LLM-as-judge scores drafts (run as part of QA: 20 mins)
- Latency: Measure end-to-end + per-agent (automated: 10 mins)
- Results provide confidence metrics for demo

**Alternatives considered:**
- ❌ No evals: Can't validate quality
- ❌ Full automated test suite: Too complex for 2-3 days
- ✅ Lightweight manual evals + latency: Sufficient for demo validation

**Trade-off:** Manual eval work (~45 mins). Mitigation: Automate in Phase 2.

---

## Risks / Trade-offs

### Risk: Golden Dataset Doesn't Match Real User Behavior
**Mitigation:**
- Generate realistic dataset from actual LinkedIn post patterns
- Document assumptions about engagement rates
- Phase 2 replaces with real data
- Demo acknowledges "using sample data for testing"

---

### Risk: Replit Backend May Sleep During Demo
**Mitigation:**
- Option 1: Upgrade to Replit Starter ($7/month for demo day)
- Option 2: Keep frontend on Vercel (always fast), pre-warm backend before demo
- Phase 2: Move to Cloud Run (always on)

---

### Risk: Pinecone Credits Run Out
**Mitigation:**
- Test locally first with full demo volume (50+ queries)
- Monitor credit usage in real-time
- PostgreSQL pgvector as fallback (slower, but works)
- Phase 2: Use real API with metered billing

---

### Risk: Claude API Rate Limits During Demo
**Mitigation:**
- LiteLLM handles rate limiting automatically
- Cache system prompts (save 90% on repeated tokens)
- Pre-compute some responses (Strategist recommendations for 3 demo scenarios)
- Fallback to cached responses if needed

---

### Risk: Voice Consistency Hard Without Real Samples
**Mitigation:**
- Manually curate 3-5 "voice sample" posts for demo user
- Document this as MVP limitation
- Phase 2: Auto-extract voice characteristics from user's actual posts

---

### Risk: Workflow Too Complex for 2-3 Days
**Mitigation:**
- Clear scope: MVP = 3 agents + 2 gates + golden data
- Phase 2 = real APIs, file formats, auto-extraction
- Use boilerplate: copy LangGraph patterns from documentation
- Clear task breakdown (see tasks.md)

---

## Migration Plan

### Phase 1 → Phase 2 (Day 3-7)
1. Replace golden dataset with real LinkedIn API polling
2. Add PDF/DOCX parsing (pypdf, python-docx)
3. Auto-extract voice characteristics
4. Add real performance metric tracking
5. Upgrade backend from Replit to Cloud Run
6. Upgrade database from Supabase free to paid tier

### Code changes required:
- `workflow_management/linkedin_auto.py`: Add LinkedIn API client
- `workflow_management/webinar_notes.py`: Add file parsers
- `performance_memory/`: Add auto-extraction logic
- Infrastructure: Cloud Run deployment config

### No architecture changes needed:
- LangGraph patterns stay the same
- Database schema compatible
- Agent code reusable
- Observability stack scales up

---

## Parallel Execution Strategy

### Task Parallelization (Reduces 2-3 days to ~1.5 days)

**Day 1 can run tasks in parallel:**
```
TIME: Day 1 00:00-04:00 (4 hours) - PARALLEL
├─ Setup Stream: Environment, Docker setup, dependency install
├─ Cloud DB Stream: Supabase setup, Pinecone setup, seed golden data
└─ Secrets Stream: Configure env vars, validate API keys

TIME: Day 1 04:00-08:00 (4 hours) - SEQUENTIAL (depends on Day 1 early)
└─ Backend: LangGraph, agents, orchestration (can't parallelize - dependent)

TIME: Day 1 08:00-12:00 (4 hours) - PARALLEL
├─ Database Stream: Schema, indexing, voice samples
└─ Frontend Stream: UI pages, components, styling (independent)

TIME: Day 1 12:00-14:00 (2 hours) - SEQUENTIAL (depends on both streams)
└─ Integration: Connect frontend to backend APIs

TIME: Day 1 14:00-18:00 (4 hours) - PARALLEL
├─ Observability Stream: LangSmith, Sentry, PostHog setup
└─ Evals Stream: Build eval scripts, run tests (independent)

TIME: Day 1/2 18:00-24:00 (6 hours) - SEQUENTIAL
└─ Deployment: Deploy backend → deploy frontend → verify
```

**Makefile target for parallel execution:**
```bash
make create-parallel  # Spawns parallel job streams with automatic dependency management
```

**Time savings:** 2-3 days → ~1.5 days by executing independent streams simultaneously.

---

### Unified Configuration & Secrets Management

**Single Configuration File Approach:**
- User creates ONE file: `.env.production` (for cloud) or `.env.local` (for local dev)
- All IaC scripts read from this single file
- Format: KEY=VALUE pairs, comments supported
- File contains everything: API keys, database URLs, service credentials, deployment targets

**Template (.env.example):**
```bash
# API Keys (required for all environments)
ANTHROPIC_API_KEY=sk-...
OPENROUTER_API_KEY=...
LITELLM_API_KEY=...
PINECONE_API_KEY=...

# Database (Supabase)
SUPABASE_URL=https://....supabase.co
SUPABASE_KEY=...
DATABASE_URL=postgresql://...

# Deployment Targets
VERCEL_TOKEN=...
VERCEL_PROJECT_ID=...
REPLIT_TOKEN=...
REPLIT_PROJECT_ID=...

# Cloud Credentials (if deploying to AWS/GCP instead of Replit)
AWS_ACCESS_KEY_ID=...
AWS_SECRET_ACCESS_KEY=...
AWS_REGION=us-east-1

# Observability
LANGSMITH_API_KEY=...
SENTRY_DSN=...
POSTHOG_API_KEY=...

# Configuration
ENVIRONMENT=production  # or 'development' or 'local'
LOG_LEVEL=INFO
```

**Secrets Management Strategy:**

1. **Local Development:**
   - User creates `.env.local` from `.env.example`
   - Add API keys manually (one-time setup)
   - IaC scripts read from `.env.local`
   - `.env*` files are in .gitignore (never committed)

2. **Cloud Deployment:**
   - Use platform-specific secret managers:
     - Vercel: Secrets stored in Vercel dashboard (accessed via `vercel env pull`)
     - Replit: Secrets stored in Replit dashboard (accessed via Replit API)
   - IaC scripts pull secrets from platform → write to `.env.cloud` (temporary, not committed)
   - Alternative: User can provide `.env.production` file to `make deploy`

3. **CI/CD (GitHub Actions):**
   - Store secrets in GitHub Secrets
   - Deploy workflow pulls from GitHub Secrets → sets Vercel/Replit secrets
   - No .env file ever in git

4. **Secrets Rotation:**
   - `make rotate-secrets` target: regenerate all API keys (with user confirmation)
   - Update `.env.local` and cloud platform secrets
   - Verify all services still work after rotation

---

### IaC Scripts with Unified Config

**Pattern: All scripts read from single .env file**

Example: `create-resources.sh` reads .env and passes values to subscripts
```bash
#!/bin/bash
source .env.local  # or .env.production

# Each subscript reads from environment variables
./scripts/create-supabase.sh  # Uses $SUPABASE_URL, $SUPABASE_KEY, $DATABASE_URL
./scripts/create-pinecone.sh  # Uses $PINECONE_API_KEY
./scripts/deploy-replit.sh    # Uses $REPLIT_TOKEN, $REPLIT_PROJECT_ID
./scripts/deploy-vercel.sh    # Uses $VERCEL_TOKEN, $VERCEL_PROJECT_ID
```

**Uninterrupted Execution:**
```bash
# Single command: reads config, creates resources, validates, deploys
make create-all

# Or with custom config file
make create-all CONFIG=.env.staging

# Stops immediately if any validation fails (with clear error message)
# Resume from last successful step with:
make create-all RESUME=true
```

**Configuration Validation:**
- Before starting: `validate-config.sh` checks all required variables are set
- If missing: script lists which ones and exits with clear error
- User updates .env file and reruns

---

## Open Questions

1. **LinkedIn API approval timeline:** When will official approval be ready? (Can schedule for Phase 2 once approved)
2. **File size limits:** What's max file size for PDF uploads? (Design constraint for Phase 2)
3. **User session duration:** How long should session state persist? (Design for Phase 2 persistence layer)
4. **Parallel execution environment:** Should parallel streams run in separate docker containers or same host? (Recommend separate containers for isolation)
