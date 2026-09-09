# Tasks: Production Content Strategist MVP

---

## ⚡ MINIMALISTIC IMPLEMENTATION PATH (Fastest to Working Demo)

### Critical Path to Working System (~6-8 hours with parallel execution)

**Absolute Minimum:**
1. **Config Setup (30 mins):** Create `.env.local` with all API keys
2. **Backend Core (3 hours, parallel):**
   - Setup FastAPI + LangGraph
   - Implement Strategist agent (with hardcoded responses for demo)
   - Implement Creator agent (with template responses)
   - Create `/analyze` endpoint
3. **Frontend MVP (2 hours, parallel):**
   - Create single page: input form → recommendation → draft
   - Connect to backend `/analyze`
4. **Golden Data (1 hour):**
   - Seed 15 demo posts in PostgreSQL
   - Upload embeddings to Pinecone
5. **Test Workflow (1 hour, parallel):**
   - Test end-to-end with 3 scenarios
   - Verify no critical errors
6. **Local Deploy (30 mins, sequential):**
   - Run locally with `docker-compose up`
   - Test on localhost:3000

**Total: ~6-8 hours with parallel execution**

**What this skips (add later):**
- Reviewer agent (use stub)
- Observability (LangSmith, Sentry, PostHog)
- Evals framework
- Cloud deployment (can demo locally)
- Comprehensive validation scripts

---

### Full Production MVP (~1.5-2 days with parallel execution)

All tasks below, executed in parallel streams where possible.

---

## Day 1 Early Morning: Infrastructure Automation Setup (1 hour)

### 0.1 Makefile & Scripts Foundation
- [ ] 0.1.1 Create Makefile in project root with targets: install, dev, test, deploy-backend, deploy-frontend, clean; verify `make help` lists all targets
- [ ] 0.1.2 Create scripts/ directory with: setup-env.sh, deploy.sh, cleanup.sh, local-dev.sh; verify scripts are executable
- [ ] 0.1.3 Create .env.example with all required variables (ANTHROPIC_KEY, PINECONE_KEY, DATABASE_URL, LITELLM_KEY, SUPABASE_URL, etc.); verify template is complete
- [ ] 0.1.4 Add .gitignore entries for .env, .env.local, /node_modules, /venv, __pycache__; verify sensitive files are ignored

### 0.2 CLI-Based Resource Management Scripts
- [ ] 0.2.1 Create supabase-setup.sh: create database, create tables, seed golden data via SQL files; verify script is idempotent (safe to run multiple times)
- [ ] 0.2.2 Create pinecone-setup.sh: create index via Pinecone CLI, upload embeddings, verify index is ready; include cleanup function
- [ ] 0.2.3 Create vercel-deploy.sh: deploy frontend to Vercel via CLI, set environment variables; include rollback function
- [ ] 0.2.4 Create replit-deploy.sh: push to Replit git, configure environment variables via Replit API; include deployment verification

### 0.3 Containerization Setup
- [ ] 0.3.1 Create Dockerfile for backend: Python 3.11 slim base, install requirements, expose port 8000, health check endpoint; verify `docker build -t content-api:latest .` succeeds
- [ ] 0.3.2 Create docker-compose.yml: services for backend (FastAPI), frontend (Next.js), PostgreSQL (optional), Redis (optional); verify `docker-compose up` starts all services
- [ ] 0.3.3 Add health checks to docker-compose.yml: backend checks /health endpoint, frontend checks localhost:3000, database checks connection; verify health checks pass
- [ ] 0.3.4 Add .dockerignore: exclude node_modules, __pycache__, .env files; verify unnecessary files aren't copied into image

### 0.4 Local Development Automation
- [ ] 0.4.1 Create local-dev.sh: option 1 (Docker): `docker-compose up`, option 2 (manual): install venv + deps; verify one command starts everything
- [ ] 0.4.2 Create verify-local-env.sh: check Docker installed, check Python version, check Node version, validate .env.local exists with all keys; verify all checks pass
- [ ] 0.4.3 Add `make dev-local` target: runs docker-compose or manual setup; add `make dev-clean` to stop containers; verify both work
- [ ] 0.4.4 Test development loop: edit code → auto-reload → verify changes appear in browser; works for both backend and frontend

---

## Day 1 Morning: Infrastructure & Setup (4 hours)

### 1.1 Database Setup
- [ ] 1.1.1 Create Supabase project and obtain connection string; verify connection via psql or GUI
- [ ] 1.1.2 Create PostgreSQL schema (content, performance_metrics, decisions tables) and verify tables exist with `\dt`
- [ ] 1.1.3 Seed golden dataset: insert 15 realistic LinkedIn posts with engagement metrics; verify row count with `SELECT COUNT(*) FROM content` = 15
- [ ] 1.1.4 Generate embeddings for golden posts and verify all 15 posts have embeddings computed

### 1.2 Vector Database Setup  
- [ ] 1.2.1 Create Pinecone project, create index with 1536 dimensions; verify index is active in Pinecone dashboard
- [ ] 1.2.2 Upload embeddings for 15 golden posts to Pinecone with metadata (topic, engagement_rate); verify `query_vector([1,0,...])` returns results
- [ ] 1.2.3 Test similarity search: query with a test vector and verify top 5 results are reasonable; document sample query results

### 1.3 Backend Project Setup
- [ ] 1.3.1 Create FastAPI project structure; verify `uvicorn main:app --reload` starts server on localhost:8000
- [ ] 1.3.2 Add requirements.txt with: fastapi, uvicorn, anthropic, pinecone, psycopg2, langgraph, pydantic, litellm, python-dotenv; verify `pip install -r requirements.txt` completes
- [ ] 1.3.3 Create .env.local with API keys (ANTHROPIC_KEY, PINECONE_KEY, DATABASE_URL, LITELLM_KEY); verify `python -c "import os; os.getenv('ANTHROPIC_KEY')"` returns key
- [ ] 1.3.4 Test LiteLLM connection to Claude via OpenRouter; verify successful LLM call logs response

### 1.4 Frontend Project Setup
- [ ] 1.4.1 Create Next.js project with `create-next-app`; verify `npm run dev` starts dev server on localhost:3000
- [ ] 1.4.2 Set NEXT_PUBLIC_API_URL=http://localhost:8000 in .env.local; verify frontend can reach backend (test with fetch)
- [ ] 1.4.3 Deploy frontend to Vercel and document live URL; verify `curl https://<url>` returns 200

---

## Day 1 Afternoon: Backend Core (4 hours)

### 2.1 LangGraph Orchestration
- [ ] 2.1.1 Define StateGraph with state: content, strategist_output, creator_output, reviewer_output; verify state structure in `langgraph/graph.py`
- [ ] 2.1.2 Add workflow nodes: strategist_node, creator_node, reviewer_node as async functions; verify `async def strategist_node(state)` exists
- [ ] 2.1.3 Connect edges: strategist → creator → reviewer; verify `workflow.add_edge()` calls present
- [ ] 2.1.4 Compile workflow and test state machine: invoke with test content, verify state transitions; check logs for all 3 nodes executing

### 2.2 Strategist Agent
- [ ] 2.2.1 Implement strategist_node: embed user content, query Pinecone for top 5 similar; verify Pinecone query returns 5 results
- [ ] 2.2.2 Fetch performance metrics for similar posts from PostgreSQL; verify metrics are retrieved and formatted correctly
- [ ] 2.2.3 Call Claude via LiteLLM with context (content + similar posts + metrics); verify LLM response includes action (publish/repurpose/rework/combine/skip)
- [ ] 2.2.4 Parse LLM response to structured output {action, reasoning, confidence}; verify JSON parsing succeeds
- [ ] 2.2.5 Test with 3 demo scenarios (technical post, opinion, personal story); verify each gets appropriate recommendation

### 2.3 Creator Agent  
- [ ] 2.3.1 Implement creator_node: accept approved brief from state; verify state contains strategist_output
- [ ] 2.3.2 Fetch voice samples from PostgreSQL (manually curated); verify 3-5 samples retrieved
- [ ] 2.3.3 Call Claude via LiteLLM with voice samples + brief; verify LLM generates draft
- [ ] 2.3.4 Parse response to {title, body, word_count, reading_time}; verify structure is correct and word_count > 0
- [ ] 2.3.5 Test with approved recommendations from 2.2.5; verify drafts are generated in appropriate format

### 2.4 Reviewer Agent
- [ ] 2.4.1 Implement reviewer_node: accept draft from state; verify state contains creator_output
- [ ] 2.4.2 Call Claude via LiteLLM as quality judge; ask for tone, clarity, generic phrase scores; verify LLM returns scores
- [ ] 2.4.3 Parse response to {tone_score, clarity_score, generic_phrases, quality_verdict}; verify all fields present
- [ ] 2.4.4 Test with drafts from 2.3.5; verify quality scores are reasonable (7-9 range for good drafts)

### 2.5 Error Handling & Logging
- [ ] 2.5.1 Add try/catch around all LLM calls with proper error logging; verify errors are logged to stdout with timestamp and agent name
- [ ] 2.5.2 Add timeout handling (30s limit) for LLM calls; verify timeout errors are caught and logged
- [ ] 2.5.3 Add validation for LLM response parsing; verify malformed responses don't crash, instead log error

---

## Day 1 Evening: Database & Memory Setup (4 hours)

### 3.1 Database Schema & Seeding
- [ ] 3.1.1 Review golden dataset format; verify 15 posts have: text, topics, tone, format, impressions, engagement_rate
- [ ] 3.1.2 Insert golden posts into PostgreSQL content table; verify `SELECT COUNT(*) FROM content` = 15
- [ ] 3.1.3 Insert corresponding performance metrics; verify performance_metrics table has 15 rows

### 3.2 Vector Embedding & Indexing
- [ ] 3.2.1 Generate OpenAI/Claude embeddings for all 15 golden posts; verify embeddings are 1536-dimensional vectors
- [ ] 3.2.2 Upload embeddings to Pinecone with metadata {post_id, topic, engagement_rate}; verify Pinecone index count = 15
- [ ] 3.2.3 Test similarity search end-to-end: embed test content, search Pinecone, retrieve from PostgreSQL; verify results are semantically similar

### 3.3 Voice Samples Setup
- [ ] 3.3.1 Manually curate 5 voice sample posts from golden dataset (one technical, one opinion, one personal, two mixed); store post IDs
- [ ] 3.3.2 Tag these posts as voice_samples in PostgreSQL; verify voice sample posts are queryable

### 3.4 Integration Testing
- [ ] 3.4.1 Test full workflow locally: orchestrate strategist → creator → reviewer with demo content; verify all 3 agents execute
- [ ] 3.4.2 Verify state transitions: strategist output → creator input, creator output → reviewer input; check state object flow
- [ ] 3.4.3 Test error cases: invalid content, LLM timeout, empty Pinecone results; verify graceful degradation

---

## Day 2 Morning: Frontend & API Routes (4 hours)

### 4.1 FastAPI Routes & Schema
- [ ] 4.1.1 Create Pydantic models: AnalyzeRequest {content, content_type}, AnalyzeResponse {recommendation, similar_posts}; verify model validation works
- [ ] 4.1.2 Create POST /analyze route: accept AnalyzeRequest, call strategist workflow, return AnalyzeResponse; test with curl
- [ ] 4.1.3 Create POST /create-draft route: accept approved brief, call creator, return draft; test with curl
- [ ] 4.1.4 Create POST /save-decision route: accept user decision (approve/reject), store in PostgreSQL; verify record inserted

### 4.2 CORS & Health Check
- [ ] 4.2.1 Add CORS middleware to FastAPI for frontend domain; test OPTIONS request from localhost:3000
- [ ] 4.2.2 Create GET /health endpoint returning {status, dependencies_status}; verify returns 200 with healthy status

### 4.3 Frontend UI (4 Pages)
- [ ] 4.3.1 Build Page 1 (Input): form to paste content, submit button; test form submission calls /analyze
- [ ] 4.3.2 Build Page 2 (Recommendation): display action, reasoning, similar posts, approve/modify/reject buttons; test state flow
- [ ] 4.3.3 Build Page 3 (Draft): display generated draft with quality scores, approve/edit/rework buttons; test state flow
- [ ] 4.3.4 Build Page 4 (Review): show final confirmation, publish/save buttons; test state completion

### 4.4 API Integration
- [ ] 4.4.1 Connect frontend form to backend /analyze endpoint via fetch; test request/response cycle with demo content
- [ ] 4.4.2 Connect recommendation buttons to /create-draft and /save-decision endpoints; test all approval flows
- [ ] 4.4.3 Add loading states and error messages on frontend; test error handling with invalid inputs

---

## Day 2 Afternoon: Observability & Testing (4 hours)

### 5.1 LangSmith Integration
- [ ] 5.1.1 Add LangSmith SDK to backend (import langsmith, set API key); verify LangSmith environment variable is set
- [ ] 5.1.2 Wrap agent nodes with @langsmith.traceable decorator; run workflow and verify traces appear in LangSmith dashboard
- [ ] 5.1.3 Verify full trace shows strategist → creator → reviewer pipeline; check input/output for each node

### 5.2 Sentry Integration
- [ ] 5.2.1 Initialize Sentry in FastAPI app; verify Sentry DSN is set
- [ ] 5.2.2 Capture intentional error (e.g., divide by zero) and verify it appears in Sentry dashboard
- [ ] 5.2.3 Test LLM timeout error handling; verify timeout errors are logged to Sentry

### 5.3 PostHog Analytics
- [ ] 5.3.1 Initialize PostHog client in frontend and backend; verify API key is configured
- [ ] 5.3.2 Add event tracking: on content upload, on recommendation approval, on final approval; test locally
- [ ] 5.3.3 Verify events appear in PostHog dashboard with correct properties (event_type, user_id, content_metadata)

### 5.4 Evals & Testing
- [ ] 5.4.1 Create eval script: run 10 test scenarios through strategist, check if recommendations match expected actions; verify script runs
- [ ] 5.4.2 Create quality eval: run 5 generated drafts through LLM-as-judge scoring; verify average quality score is recorded
- [ ] 5.4.3 Create latency test: measure end-to-end workflow time, per-agent latencies; verify all agents complete under 6s total
- [ ] 5.4.4 Run full eval suite and document results (accuracy, quality, latency); verify all metrics are within targets

---

## Day 2 Evening: Deployment & Polish (2-4 hours)

### 6.1 Backend Deployment
- [ ] 6.1.1 Create Replit project and push FastAPI code; verify `git push` succeeds
- [ ] 6.1.2 Configure environment variables in Replit (API keys, database URL); verify backend starts on Replit
- [ ] 6.1.3 Test backend API endpoints from Replit URL; verify /health returns 200, /analyze works
- [ ] 6.1.4 Document backend URL (https://replit-project-url.repl.co)

### 6.2 Frontend Deployment
- [ ] 6.2.1 Update NEXT_PUBLIC_API_URL to point to Replit backend URL; verify env var is set in Vercel
- [ ] 6.2.2 Deploy frontend to Vercel (already done in 1.4.3); verify frontend can reach Replit backend
- [ ] 6.2.3 Test full workflow end-to-end on live URLs; verify all 4 pages work

### 6.3 Demo Scenario Prep
- [ ] 6.3.1 Prepare 3 demo scenarios: technical post, opinion piece, personal story with expected outcomes documented
- [ ] 6.3.2 Test each scenario end-to-end on live system; verify recommendations are sensible, drafts are high quality
- [ ] 6.3.3 Document demo script (5-minute walkthrough); include screenshots and expected output

### 6.4 Documentation
- [ ] 6.4.1 Write README with: setup instructions, API endpoints, demo scenarios, known limitations, Phase 2 roadmap
- [ ] 6.4.2 Create ARCHITECTURE.md with: system diagram, component descriptions, data flow
- [ ] 6.4.3 Update OpenSpec specs if any Phase 2 items emerge during testing; document as future improvements

---

## Day 3 (Optional): Final Polish & Refinement

### 7.1 Performance Tuning
- [ ] 7.1.1 Profile backend endpoints; identify any >1s bottlenecks; optimize if needed (caching, query optimization)
- [ ] 7.1.2 Measure database query performance; add indexes if needed; verify query times <100ms
- [ ] 7.1.3 Test under load (simulate 5 concurrent users); verify no timeouts or failures

### 7.2 Bug Fixes & Edge Cases
- [ ] 7.2.1 Test with edge cases: empty input, very long content (10K+ tokens), special characters; verify graceful handling
- [ ] 7.2.2 Test rejection paths: user rejects recommendation, requests rework; verify feedback routing works
- [ ] 7.2.3 Run eval suite one more time; document final metrics

### 7.3 Demo Day Readiness
- [ ] 7.3.1 Create demo checklist: URLs working, LangSmith accessible, Sentry showing no errors, PostHog showing events
- [ ] 7.3.2 Record demo video (optional): 5-minute walkthrough for fallback if live demo fails
- [ ] 7.3.3 Prepare talking points: system architecture, key decisions, Phase 2 roadmap, lessons learned

---

## Day 2/3: Infrastructure Automation & CI/CD

### 8.1 Deployment Automation Scripts
- [ ] 8.1.1 Create deploy.sh: orchestrate all deployment steps (backend → Replit, frontend → Vercel); verify one command deploys entire system
- [ ] 8.1.2 Add rollback.sh: revert to previous version on backend and frontend; verify rollback returns system to previous stable state
- [ ] 8.1.3 Create health-check.sh: verify all services are running (backend, frontend, database, Pinecone); test with curl/API calls
- [ ] 8.1.4 Create monitor.sh: tail logs from backend and frontend in real-time; useful for debugging during demo

### 8.2 Resource Cleanup & Teardown
- [ ] 8.2.1 Create cleanup.sh: delete Supabase database, delete Pinecone index, undeploy from Replit/Vercel (optional with confirmation)
- [ ] 8.2.2 Create local-cleanup.sh: delete venv, node_modules, .env.local, stop Docker containers; verify clean state after running
- [ ] 8.2.3 Add `make clean-all` target: runs full cleanup (both local and cloud optional); confirm before destructive actions

### 8.2.1 Resource Creation Orchestration (Selective & One-Shot)
- [ ] 8.2.1.1 Create create-resources.sh with stages (can be run individually or together):
  - Stage 1: Local resources (Docker, volumes, networks)
  - Stage 2: Cloud databases (Supabase PostgreSQL, Pinecone index)
  - Stage 3: Cloud infrastructure (Replit backend, Vercel frontend)
  - Stage 4: Seed data (golden dataset, embeddings)
  - Verify script is modular: `./create-resources.sh --stage 2` creates only Supabase/Pinecone
- [ ] 8.2.1.2 Add validation after each stage:
  - Stage 1: verify Docker service is running, images build successfully
  - Stage 2: verify Supabase and Pinecone credentials work, test connection
  - Stage 3: verify Replit and Vercel CLI authentication works, URLs are accessible
  - Stage 4: verify golden dataset has 15 rows, embeddings are indexed in Pinecone
- [ ] 8.2.1.3 Create Makefile targets for selective creation:
  - `make create-local` - Stage 1 only
  - `make create-cloud-db` - Stage 2 only
  - `make create-cloud-deploy` - Stage 3 only
  - `make create-all` - All stages (one-shot)
  - Verify each target works independently

### 8.2.2 Resource Update Orchestration (Selective & One-Shot)
- [ ] 8.2.2.1 Create update-resources.sh with selective updates:
  - Update database schema (idempotent SQL migrations)
  - Update golden dataset (re-seed if needed)
  - Update backend deployment (re-deploy to Replit without recreating DB)
  - Update frontend deployment (re-deploy to Vercel)
  - Verify script validates what needs updating before making changes
- [ ] 8.2.2.2 Add validation after each update:
  - Schema update: verify schema version matches expected, run migration tests
  - Data update: verify row count is correct, spot-check sample rows
  - Backend update: verify backend service is running, /health returns 200
  - Frontend update: verify frontend loads without errors
- [ ] 8.2.2.3 Create Makefile targets for selective updates:
  - `make update-db` - update schema only
  - `make update-data` - re-seed golden data
  - `make update-backend` - redeploy backend
  - `make update-frontend` - redeploy frontend
  - `make update-all` - all updates (one-shot)
  - Verify each target is idempotent (safe to run multiple times)

### 8.2.3 Resource Cleanup Orchestration (Ordered One-Shot)
- [ ] 8.2.3.1 Create cleanup-resources.sh with proper order of destruction:
  - Step 1: Stop running services (docker-compose down, stop Replit)
  - Step 2: Undeploy cloud services (undeploy from Vercel, remove from Replit)
  - Step 3: Delete cloud databases (delete Pinecone index, delete Supabase database)
  - Step 4: Clean local resources (remove Docker volumes, remove .env files)
  - Step 5: Delete git history/branches (optional)
  - Verify script prompts for confirmation before each destructive step
- [ ] 8.2.3.2 Add validation before each cleanup step:
  - Before stopping services: verify services are actually running (check docker ps)
  - Before undeploying: verify services are actually deployed (check Vercel/Replit)
  - Before deleting DB: verify data is backed up (prompt user)
  - Before cleaning local: verify nothing uncommitted will be lost (check git status)
- [ ] 8.2.3.3 Add rollback capability:
  - If cleanup fails at any step, document what was cleaned, suggest manual recovery
  - Create recovery-steps.txt documenting what to redo manually if needed
  - Verify cleanup failures don't cascade to later steps
- [ ] 8.2.3.4 Create Makefile target:
  - `make clean-all` - runs full cleanup with prompts at each step
  - Add `make clean-all-force` - runs without prompts (dangerous, requires confirmation)
  - Verify cleanup is reversible (can recreate with `make create-all`)

### 8.3 Makefile Consolidation with Verification
- [ ] 8.3.1 Create Makefile with resource creation targets:
  - `make create-local` - create local Docker resources
  - `make create-cloud-db` - create cloud databases (Supabase, Pinecone)
  - `make create-cloud-deploy` - deploy to cloud (Replit, Vercel)
  - `make create-all` - create everything in correct order
  - Verify each target validates creation with checks (see 8.2.1.2)
- [ ] 8.3.2 Create Makefile with resource update targets:
  - `make update-db` - update database schema
  - `make update-data` - re-seed golden data
  - `make update-backend` - redeploy backend
  - `make update-frontend` - redeploy frontend
  - `make update-all` - update everything
  - Verify each update is idempotent (safe to run repeatedly)
- [ ] 8.3.3 Create Makefile with cleanup targets:
  - `make clean-local` - clean local resources (Docker, .env)
  - `make clean-cloud` - clean cloud resources (interactive)
  - `make clean-all` - complete cleanup with prompts
  - `make clean-all-force` - cleanup without prompts (dangerous)
  - Verify cleanup follows proper dependency order (see 8.2.3.1)
- [ ] 8.3.4 Create Makefile with utility targets:
  - `make help` - show all available targets
  - `make install` - install dependencies
  - `make dev-local` - run locally
  - `make test` - run evals
  - `make status` - show health
  - `make monitor` - tail logs
  - `make rollback` - rollback to previous
  - Verify `make help` lists all targets with descriptions
- [ ] 8.3.5 Add verification to Makefile:
  - Each target runs appropriate validation script after completion
  - Targets fail early if prerequisites aren't met (e.g., Docker not installed)
  - Verification results are logged to makefile.log for audit trail
  - Verify log file is created and contains all step results

### 8.4 Environment Management
- [ ] 8.4.1 Create env-setup.sh: copy .env.example to .env.local, prompt for API keys interactively, validate keys work; verify credentials are set
- [ ] 8.4.2 Create env-sync.sh: sync environment variables between local .env.local and cloud (Vercel/Replit); ensure consistency
- [ ] 8.4.3 Add secret management: use Vercel/Replit CLI to manage secrets (not in git); verify secrets are accessible at runtime

### 8.5 Documentation
- [ ] 8.5.1 Create DEPLOYMENT.md with sections:
  - Quick start (one-liner to deploy): `make deploy`
  - Local development: `make dev-local`, `make clean-local`
  - Cloud deployment: `make deploy`, `make status`, `make rollback`
  - Troubleshooting: common issues and how to debug
  - Manual override options (if automation fails)
- [ ] 8.5.2 Create INFRASTRUCTURE.md with:
  - Architecture diagram (local vs cloud)
  - Service dependencies
  - API credentials needed
  - Cost breakdown
  - Scaling considerations
- [ ] 8.5.3 Create scripts/README.md with: description of each script, when to use manually vs via Makefile, troubleshooting

### 8.8.1 CI/CD Pipeline (GitHub Actions, optional)
- [ ] 8.8.1.1 Create .github/workflows/deploy.yml: on push to main:
  - Run pre-deploy.sh (validate all prerequisites)
  - Run tests and evals (make test)
  - Run deploy (make deploy)
  - Run post-deploy.sh (validate deployment success)
  - Report to #deployments Slack channel (success/failure)
  - Verify workflow triggers and deploys without manual intervention
- [ ] 8.8.1.2 Create .github/workflows/rollback.yml: manual trigger to rollback:
  - Prompt for version to rollback to
  - Run rollback script
  - Verify rollback with post-deploy.sh
  - Report to #deployments Slack channel
  - Verify rollback can be triggered from GitHub web UI
- [ ] 8.8.1.3 Create .github/workflows/health-check.yml: scheduled daily:
  - Run health-check.sh
  - If any service is down, alert #ops-alerts Slack channel
  - Log results to health.log artifact
  - Verify workflow runs on schedule

### 8.8.2 Documentation & Runbooks
- [ ] 8.8.2.1 Update DEPLOYMENT.md with verification steps:
  - Add "Verification Checklist" section with pre-deploy and post-deploy steps
  - Add "How to troubleshoot deployment failures" section with common issues
  - Add "How to rollback if deployment fails" section with step-by-step instructions
  - Document what each validation script checks and how to interpret results
- [ ] 8.8.2.2 Create RUNBOOK.md with operational procedures:
  - Daily health checks and what to do if something is down
  - How to scale resources if needed
  - How to update just one component (backend, frontend, database)
  - Emergency cleanup procedure if resources get corrupted
  - How to recover from backup if data is lost

### 8.7 Comprehensive Verification & Validation Framework

#### 8.7.1 Pre-Deployment Validation
- [ ] 8.7.1.1 Create pre-deploy.sh: runs all checks before deployment:
  - Verify Docker is installed and running
  - Verify Python version and venv active
  - Verify Node version and npm installed
  - Verify all required environment variables are set
  - Verify API keys work (test Claude, Pinecone, Supabase connections)
  - Verify no uncommitted changes in git (or prompt to commit)
  - Verify all unit tests pass
  - Verify all evals pass (accuracy, quality, latency)
  - If any check fails, report which one and halt deployment
- [ ] 8.7.1.2 Add to `make deploy` pre-check: run pre-deploy.sh and verify all checks pass before proceeding

#### 8.7.2 Post-Deployment Validation
- [ ] 8.7.2.1 Create post-deploy.sh: runs all checks after deployment:
  - Verify backend is responsive (GET /health returns 200)
  - Verify frontend is accessible (GET / returns 200)
  - Verify database connection works (test query to PostgreSQL)
  - Verify Pinecone is accessible (test similarity search)
  - Verify LangSmith is receiving traces (check for recent traces)
  - Verify Sentry is receiving errors (optional test error)
  - Verify PostHog is tracking events (test event)
  - Verify golden dataset is intact (count rows in content table)
  - Verify all 3 agents can be invoked (test Strategist → Creator → Reviewer)
  - Report success/failure for each check
- [ ] 8.7.2.2 Add to all deploy targets: run post-deploy.sh and report results

#### 8.7.3 Health Check Monitoring
- [ ] 8.7.3.1 Create health-check.sh: continuous monitoring script that:
  - Runs every 5 minutes (configurable)
  - Checks all endpoints and services
  - Logs results to health.log with timestamps
  - Alerts (email/Slack) if any service is down (future enhancement)
  - Reports summary: "All green" or lists failed services
- [ ] 8.7.3.2 Add `make monitor-health` target: runs health-check.sh in background; can be stopped with Ctrl+C

#### 8.7.4 Data Integrity Validation
- [ ] 8.7.4.1 Create validate-data.sh: checks data consistency:
  - Verify golden dataset has exactly 15 posts with valid metrics
  - Verify all posts have embeddings in Pinecone (15 vectors)
  - Verify voice samples are properly tagged in PostgreSQL
  - Verify no orphaned data (decisions without corresponding content)
  - Check for data corruption (NULL values in required fields)
  - Report any data issues found
- [ ] 8.7.4.2 Add to `make update-data`: verify data integrity after re-seeding

#### 8.7.5 Performance & Load Validation
- [ ] 8.7.5.1 Create load-test.sh: validate system can handle load:
  - Simulate 5 concurrent users making requests
  - Measure response times (target: <3s per request)
  - Measure error rate (target: 0%)
  - Measure peak memory usage
  - Report results: pass/fail with metrics
- [ ] 8.7.5.2 Add to `make test`: run load-test.sh before evals

#### 8.7.6 Security Validation
- [ ] 8.7.6.1 Create security-check.sh: validates security setup:
  - Verify no API keys are in git (check .gitignore)
  - Verify .env files are excluded from Docker image
  - Verify CORS is configured correctly (test from different origin)
  - Verify secrets are stored securely (not in code)
  - Verify HTTPS is enforced (check Vercel/Replit settings)
  - Report security issues found
- [ ] 8.7.6.2 Add to `make deploy` pre-check: run security-check.sh

#### 8.7.7 Rollback Validation
- [ ] 8.7.7.1 Create test-rollback.sh: verify rollback procedure works:
  - Deploy current version
  - Note current version hash
  - Simulate a change (can be a dummy change)
  - Deploy new version
  - Verify new version is live
  - Execute rollback
  - Verify previous version is restored
  - Verify no data loss during rollback
- [ ] 8.7.7.2 Add to pre-release testing: test-rollback.sh validates rollback works

#### 8.7.8 Cleanup Validation
- [ ] 8.7.8.1 Create verify-cleanup.sh: confirms nothing is left after cleanup:
  - Verify Docker containers are stopped
  - Verify Docker volumes are deleted
  - Verify Vercel deployment is removed
  - Verify Replit project is cleaned
  - Verify Supabase database is deleted
  - Verify Pinecone index is deleted
  - Verify local .env and secrets are removed
  - Verify git is clean (no extra files)
  - Report cleanup status: "fully cleaned" or lists remaining resources
- [ ] 8.7.8.2 Add to `make clean-all`: run verify-cleanup.sh and confirm all resources are gone

### 8.8 Local Development Experience
- [ ] 8.7.1 Test `make install` from clean state; verify all dependencies are installed in correct order
- [ ] 8.7.2 Test `make dev-local` startup time; verify both backend and frontend are ready in <2 minutes
- [ ] 8.7.3 Test developer workflows: edit code → auto-reload → see changes; verify hot reload works for Python and JavaScript
- [ ] 8.7.4 Create development guide: IDE setup (VS Code), recommended extensions, debugging tips; document for team

---

## Infrastructure & Deployment Automation Summary

### One-Shot Workflows

**Creation (Selective & One-Shot):**
```bash
make create-local              # Create local Docker resources only
make create-cloud-db           # Create cloud databases (Supabase, Pinecone) only
make create-cloud-deploy       # Deploy to cloud (Replit, Vercel) only
make create-all                # Create everything in correct order (one-shot)
```
Each step validates before proceeding. Can re-run safely (idempotent).

**Updates (Selective & One-Shot):**
```bash
make update-db                 # Update database schema only
make update-data               # Re-seed golden data only
make update-backend            # Redeploy backend only
make update-frontend           # Redeploy frontend only
make update-all                # Update everything (one-shot)
```
Each step validates changes. Can re-run without data loss.

**Cleanup (Ordered One-Shot):**
```bash
make clean-local               # Clean local resources only
make clean-cloud               # Clean cloud resources (interactive)
make clean-all                 # Complete cleanup with safety prompts
make clean-all-force           # Cleanup without prompts (dangerous)
```
Proper dependency order: stops services → undeployed → deletes data → cleans local.

**Development & Operations:**
```bash
make install                   # Install all dependencies
make dev-local                 # Run everything locally
make test                      # Run evals and tests
make status                    # Show health status
make monitor                   # Tail logs in real-time
make rollback                  # Rollback to previous version
make help                      # Show all targets
```

### Verification & Validation at Every Step

**Pre-Deployment Checks:**
- Docker/Python/Node installed and correct versions
- All environment variables set and API keys working
- No uncommitted changes in git
- All unit tests pass
- All evals pass (accuracy, quality, latency)
- Deployment halts if any check fails

**Post-Deployment Checks:**
- Backend /health endpoint returns 200
- Frontend loads without errors
- Database connections work
- Pinecone searches work
- LangSmith receives traces
- Sentry receives errors
- PostHog tracks events
- Golden dataset is intact (15 rows)
- All 3 agents can be invoked end-to-end

**Continuous Monitoring:**
- Health checks run every 5 minutes (configurable)
- Data integrity validated after updates
- Load tests verify system can handle concurrent users
- Security checks verify no API keys in code
- Rollback procedure validated before release

**Cleanup Verification:**
- Confirms nothing is left after cleanup
- Lists any remaining resources
- Validates git is clean

### Container-Based Management

**Docker Benefits:**
- ✅ Consistent environment (same setup everywhere)
- ✅ Easy to start/stop services
- ✅ Health checks built-in
- ✅ No dependency conflicts
- ✅ One-command local dev: `docker-compose up`

**Key automation benefits:**
- ✅ Zero manual infrastructure setup (everything scripted)
- ✅ Reproducible deployments (same steps every time)
- ✅ Selective resource management (create/update individual components or all)
- ✅ Validated at every step (pre/post checks catch issues early)
- ✅ Easy rollbacks (one command with verification)
- ✅ Minimal maintenance (automated health checks and monitoring)
- ✅ Clear documentation (Makefile targets + runbooks)

---

## Task Parallelization Matrix

### Day 1: Parallel Execution Plan (4 + 4 + 4 + 2 = 14 hours sequential time, ~8 hours wall-clock with parallelization)

**Phase 1A (Hours 0-4): Setup Streams - RUN IN PARALLEL**
```
Stream 1 (Environment):     0.1.1 → 0.1.2 → 0.1.3 → 0.1.4
Stream 2 (Cloud DB):        1.2.1 → 1.2.2 → 1.3.1 → 3.1.1 → 3.1.2 → 3.1.3 → 3.2.1
Stream 3 (Secrets):         0.4.1 → env-setup validation
Bottleneck: None, all independent
Sync Point: All streams complete before Phase 1B
```

**Phase 1B (Hours 4-8): Backend Core - SEQUENTIAL (depends on Phase 1A)**
```
Cannot parallelize: LangGraph → Strategist → Creator → Reviewer are sequential
Stream: 2.1.1 → 2.1.2 → 2.1.3 → 2.1.4 → 2.2.* → 2.3.* → 2.4.*
Bottleneck: LLM call latency (mitigated by batch requests)
```

**Phase 2A (Hours 8-12): Frontend & Data - RUN IN PARALLEL**
```
Stream 1 (Frontend):        4.3.1 → 4.3.2 → 4.3.3 → 4.3.4 → 4.4.*
Stream 2 (Database):        3.2.2 → 3.2.3 → 3.3.1 → 3.3.2 → 3.4.*
Bottleneck: None, all independent
Sync Point: Both complete before Phase 2B
```

**Phase 2B (Hours 12-14): Integration - SEQUENTIAL**
```
Depends on Phase 1B (backend) and Phase 2A (frontend)
Connect frontend to backend: 4.4.1 → 4.4.2 → 4.4.3
```

**Phase 3A (Hours 14-18): Observability & Evals - RUN IN PARALLEL**
```
Stream 1 (Observability):   5.1.* → 5.2.* → 5.3.*
Stream 2 (Evals):           5.4.* → 5.5.*
Bottleneck: None, all independent
```

**Phase 3B (Hours 18-24): Deployment & Polish - SEQUENTIAL**
```
Depends on all previous phases
Deploy: 6.1.* → 6.2.* → 6.3.* → 6.4.*
```

### Time Optimization

**Sequential (naive):** 24+ hours  
**With smart parallelization:** 12-16 hours (wall-clock time, ~1.5-2 days)  
**With minimalistic path:** 6-8 hours (skip observability, evals, cloud deployment)

### Automatic Dependency Detection

```bash
# Makefile automatically detects parallel-safe tasks:
make create-all --parallel=4     # Run up to 4 independent tasks simultaneously
make create-all --parallel=auto  # Auto-detect CPU cores and run safely in parallel
```

Script: `detect-dependencies.sh` analyzes task.md, identifies parallelizable sections, generates `Makefile.parallel` with optimal job layout.

---

## Verification Criteria

**System is production-ready when:**
- ✅ All 3 agents (Strategist, Creator, Reviewer) execute end-to-end
- ✅ Human approval gates work (strategy approval, final review)
- ✅ Golden dataset queries return relevant results (Pinecone + PostgreSQL)
- ✅ LangSmith shows full execution traces
- ✅ Sentry captures errors (if any occur)
- ✅ PostHog tracks user events
- ✅ Evals pass: accuracy 80%+, quality 7/10+, latency <6s
- ✅ Backend deployed to Replit and responsive
- ✅ Frontend deployed to Vercel and functional
- ✅ Full workflow demo succeeds with 3 scenarios
- ✅ README and documentation complete
- ✅ No critical bugs or errors in logs
