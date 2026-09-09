# Production MVP: Content Strategist with Full Agentic Workflow

## Why

Content creators manually decide how to repurpose ideas across platforms, losing opportunities to maximize engagement based on what actually works with their audience. A production-grade agentic system with real observability and human-in-the-loop design can deliver AI-driven content strategy while maintaining reliability and extensibility.

The system needs to:
- Implement a **complete agentic workflow** (all 3 agents functioning end-to-end)
- Use **production infrastructure** (PostgreSQL, Pinecone, LangGraph) for scalability
- Include **human review checkpoints** to maintain responsible AI design
- Support **both core workflows** (LinkedIn auto-trigger + webinar notes ingestion)
- Have **built-in quality metrics** (evals + observability) for validation and debugging

## What Changes

### System Architecture
- **3-agent orchestration pipeline** via LangGraph state machine:
  - **Strategist Agent**: Analyzes content against performance history (Pinecone semantic search) + recommends action
  - **Creator Agent**: Generates draft in user's voice using approved brief
  - **Reviewer Agent**: Quality checks (tone, clarity, generic phrase detection)
  
- **Human review gates** integrated into workflow:
  - **Strategy Approval Gate** (after Strategist): User approves/modifies recommendation before content generation
  - **Final Review Gate** (after Reviewer): User reviews draft, approves for publish, or requests revision

- **Dual-workflow support**:
  - **Workflow A (LinkedIn Auto)**: Auto-detect published posts → ingest → track performance → update memory → improve future recommendations
  - **Workflow B (Webinar Notes)**: User uploads notes → analyze → run strategist → user reviews → creator generates → reviewer checks → user approves
  
- **Real databases** (production-ready):
  - PostgreSQL (Supabase): Content, decisions, metadata
  - Pinecone: Vector embeddings for semantic search of similar posts
  - Redis: Caching for performance

- **Observability & Evaluation built-in**:
  - LangSmith: Full trace of agent execution
  - Sentry: Error tracking + validation
  - PostHog: User action analytics
  - Evals framework: Recommendation accuracy, draft quality, latency testing

### LLM Integration Layer
- **LiteLLM** abstraction for unified LLM provider access:
  - Supports Claude (via OpenRouter or direct), GPT, Gemini, etc.
  - Built-in rate limiting, fallback handling, cost tracking
  - Single interface for all agent LLM calls
  - Easy provider switching (useful for hackathon fallbacks)
  - Integrated logging + observability

### Deployment
- Backend: FastAPI on Replit (free tier for demo, upgrade path to Cloud Run)
- Frontend: Next.js on Vercel (auto-deploy)
- Cloud infrastructure: Production-grade (same as phase 2+)
- LLM routing: LiteLLM → Claude via OpenRouter (with fallback support)

## Capabilities

### New Capabilities

- `agent-orchestration`: LangGraph-based state machine for coordinating multi-agent workflow with human feedback loops
- `strategist-agent`: Content analysis and recommendation engine with performance-aware decision making (queries Pinecone + PostgreSQL)
- `creator-agent`: Agentic content generation with voice/style consistency (trained on user samples)
- `reviewer-agent`: Quality and tone validation for generated content
- `human-gates`: Strategy approval and final review decision points with feedback routing
- `workflow-management/linkedin-auto`: Automatic ingestion and performance tracking for published LinkedIn posts
- `workflow-management/webinar-notes`: Manual upload and analysis pipeline for content ideas
- `performance-memory`: Vector-based semantic search and retrieval of similar high-performing content
- `evals-framework`: Quality metrics (accuracy, latency, error rate) + LLM-as-judge scoring
- `observability-stack`: Integrated tracing (LangSmith), error tracking (Sentry), analytics (PostHog)

### Modified Capabilities

None (greenfield system)

## Impact

- **New**: End-to-end agentic workflow for content strategy, production databases, human-in-the-loop design
- **Deliverable**: Complete, working system with real cloud deployment and measurable quality metrics
- **Extensibility**: Zero rework needed; extend by adding LinkedIn API integration (Workflow A auto-trigger), real data collection, fine-tuning
- **Technical Stack**: FastAPI, LangGraph, LiteLLM, PostgreSQL, Pinecone, Redis, Next.js, Vercel, Replit
- **Time to Build**: 2-3 days (all infrastructure + all 3 agents + human gates + evals + observability)
- **Cost**: Minimal (LiteLLM routing through OpenRouter or direct API; all infrastructure on free tiers or user credits)
