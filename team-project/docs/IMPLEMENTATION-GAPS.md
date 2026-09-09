# Implementation Gaps - Design Resolutions

This document provides detailed design specifications to resolve the 5 gaps identified in the Technical Architecture Document. All gaps are resolvable during Day 1 implementation without extending the timeline.

---

## GAP 1: PostgreSQL Schema Design

### Current State
OpenSpec planning mentions "content, performance_metrics, decisions" tables but doesn't specify exact schema (columns, indexes, constraints).

### Design Recommendation

```sql
-- Table 1: content (stores all posts, historical and new)
CREATE TABLE content (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW(),
  
  -- Core content data
  content_text TEXT NOT NULL,
  platform VARCHAR(50) NOT NULL, -- 'linkedin', 'twitter', 'blog', 'newsletter'
  status VARCHAR(50) DEFAULT 'draft', -- 'draft', 'published', 'archived'
  
  -- Metadata
  title VARCHAR(200),
  topic VARCHAR(100), -- e.g. 'AI', 'Productivity', 'Leadership'
  content_type VARCHAR(50), -- 'text', 'thread', 'article', 'poll'
  
  -- For voice samples
  is_voice_sample BOOLEAN DEFAULT FALSE,
  
  -- For tracking (populated when published)
  external_id VARCHAR(200), -- LinkedIn post ID, Twitter tweet ID, etc.
  published_at TIMESTAMP,
  
  -- Search & indexing
  embedding_model VARCHAR(50), -- e.g. 'openai-text-embedding-3-small'
  embedding_vector VECTOR(1536), -- Will need pgvector extension for local search
  
  -- Metadata for Pinecone filtering
  metadata JSONB DEFAULT '{}', -- Stores flexible metadata
  
  CONSTRAINT content_status_valid CHECK (status IN ('draft', 'published', 'archived')),
  CONSTRAINT platform_valid CHECK (platform IN ('linkedin', 'twitter', 'blog', 'newsletter', 'email'))
);

CREATE INDEX idx_content_platform ON content(platform);
CREATE INDEX idx_content_status ON content(status);
CREATE INDEX idx_content_is_voice_sample ON content(is_voice_sample);
CREATE INDEX idx_content_published_at ON content(published_at DESC);
CREATE INDEX idx_content_topic ON content(topic);

-- Table 2: performance_metrics (engagement data for published content)
CREATE TABLE performance_metrics (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW(),
  
  content_id UUID NOT NULL REFERENCES content(id) ON DELETE CASCADE,
  
  -- Engagement metrics
  impressions INTEGER DEFAULT 0,
  clicks INTEGER DEFAULT 0,
  reactions INTEGER DEFAULT 0, -- likes + other reactions
  comments INTEGER DEFAULT 0,
  shares INTEGER DEFAULT 0,
  reposts INTEGER DEFAULT 0,
  follows_gained INTEGER DEFAULT 0,
  
  -- Calculated metrics
  engagement_rate FLOAT COMPUTED (
    CASE WHEN impressions > 0 
      THEN ((reactions + comments + shares + reposts) * 100.0) / impressions 
      ELSE 0 
    END
  ) STORED,
  
  -- Time window (for tracking trends over time)
  measured_at TIMESTAMP NOT NULL,
  time_since_published_hours INTEGER, -- hours after publication
  
  -- Source of data
  data_source VARCHAR(50), -- 'api', 'manual', 'scrape'
  
  CONSTRAINT positive_engagement CHECK (impressions >= 0 AND clicks >= 0)
);

CREATE INDEX idx_perf_content_id ON performance_metrics(content_id);
CREATE INDEX idx_perf_measured_at ON performance_metrics(measured_at DESC);
CREATE INDEX idx_perf_engagement_rate ON performance_metrics(engagement_rate DESC);

-- Table 3: decisions (user approval/rejection/modification logs)
CREATE TABLE decisions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  created_at TIMESTAMP DEFAULT NOW(),
  
  workflow_id UUID NOT NULL, -- groups all decisions in one workflow run
  stage VARCHAR(50) NOT NULL, -- 'strategy_gate', 'final_review_gate'
  action VARCHAR(50) NOT NULL, -- 'approve', 'reject', 'modify', 'revise'
  
  -- Input to this gate
  content_id UUID REFERENCES content(id),
  strategist_recommendation JSONB, -- full recommendation object
  creator_draft TEXT, -- full draft text
  
  -- User decision details
  user_feedback TEXT, -- optional notes from user
  user_modifications JSONB, -- if action='modify', contains user edits
  
  -- Quality metrics at decision time
  quality_score FLOAT, -- from reviewer agent, NULL if before review
  confidence_score FLOAT, -- from strategist agent
  
  -- Outcome
  outcome_status VARCHAR(50), -- 'pending', 'completed', 'rolled_back'
  next_stage VARCHAR(50), -- which stage executes next based on decision
  
  CONSTRAINT stage_valid CHECK (stage IN ('strategy_gate', 'final_review_gate')),
  CONSTRAINT action_valid CHECK (action IN ('approve', 'reject', 'modify', 'revise', 'start_over')),
  CONSTRAINT outcome_valid CHECK (outcome_status IN ('pending', 'completed', 'rolled_back'))
);

CREATE INDEX idx_decisions_workflow_id ON decisions(workflow_id);
CREATE INDEX idx_decisions_stage ON decisions(stage);
CREATE INDEX idx_decisions_created_at ON decisions(created_at DESC);

-- Table 4: voice_samples (curated examples of user's voice)
CREATE TABLE voice_samples (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  created_at TIMESTAMP DEFAULT NOW(),
  
  content_id UUID NOT NULL REFERENCES content(id) ON DELETE CASCADE,
  
  -- Metadata about this sample
  sample_order INTEGER, -- 1, 2, 3 for retrieval priority (top 3-5 used by Creator agent)
  sample_category VARCHAR(50), -- 'professional', 'casual', 'storytelling', 'technical'
  extraction_method VARCHAR(50), -- 'manual_selection' or 'auto_extracted' (phase 2)
  
  -- Optional analysis (populated in Phase 2)
  tone VARCHAR(100),
  primary_vocabulary_themes JSONB, -- e.g. ["technical", "accessible", "humor"]
  sentence_structure_notes TEXT,
  
  CONSTRAINT sample_order_positive CHECK (sample_order > 0)
);

CREATE INDEX idx_voice_samples_content_id ON voice_samples(content_id);
CREATE INDEX idx_voice_samples_order ON voice_samples(sample_order);

-- Table 5: workflow_runs (track end-to-end workflow executions)
CREATE TABLE workflow_runs (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW(),
  
  -- Input
  input_content TEXT NOT NULL,
  input_source VARCHAR(50), -- 'webinar_notes', 'user_paste', 'linkedin_auto'
  
  -- Execution
  status VARCHAR(50), -- 'in_progress', 'completed', 'failed', 'cancelled'
  current_stage VARCHAR(50), -- which stage are we at
  
  -- Outputs
  final_draft TEXT, -- approved final draft
  strategist_recommendation JSONB,
  creator_draft TEXT,
  reviewer_score FLOAT,
  
  -- Timing
  total_duration_seconds FLOAT,
  
  -- Observability
  langsmith_trace_id VARCHAR(200), -- for linking to LangSmith
  sentry_issue_id VARCHAR(200), -- if error occurred
  
  CONSTRAINT status_valid CHECK (status IN ('in_progress', 'completed', 'failed', 'cancelled'))
);

CREATE INDEX idx_workflow_runs_status ON workflow_runs(status);
CREATE INDEX idx_workflow_runs_created_at ON workflow_runs(created_at DESC);
CREATE INDEX idx_workflow_runs_langsmith_trace ON workflow_runs(langsmith_trace_id);
```

### Rationale
- **Separation**: Content (what was written), Metrics (how it performed), Decisions (what user chose)
- **Flexibility**: `metadata` JSONB column allows extending without schema changes
- **Performance**: Indexes on frequently queried columns (platform, status, engagement_rate, dates)
- **Referential Integrity**: Foreign keys prevent orphaned records
- **Observability**: Workflow tracking for debugging and audit trails
- **Voice Samples**: Structured for easy retrieval by Creator agent (sorted by sample_order)

### Implementation Checklist
- [ ] Create schema.sql file with above DDL
- [ ] Run migration to create tables
- [ ] Create indexes for query performance
- [ ] Seed golden dataset (15 posts with realistic metrics)
- [ ] Verify pgvector extension available (or skip embedding_vector for MVP)

---

## GAP 2: Frontend UI Specification

### Current State
Spec mentions "input form → recommendation display → draft editor" but no component breakdown or wireframes.

### Design Recommendation

#### Component Hierarchy
```
<App>
  ├─ <Header> (branding, theme toggle)
  ├─ <MainLayout>
  │  ├─ <Sidebar> (navigation, status)
  │  └─ <ContentArea>
  │     ├─ <InputStage>
  │     │  ├─ <TextInput> (textarea for content)
  │     │  ├─ <SourceSelect> (webinar-notes, paste, etc)
  │     │  └─ <AnalyzeButton>
  │     │
  │     ├─ <StrategyGateStage>
  │     │  ├─ <RecommendationCard>
  │     │  │  ├─ <ActionBadge> (Publish/Repurpose/Rework/etc)
  │     │  │  ├─ <ConfidenceScore>
  │     │  │  ├─ <ReasoningText>
  │     │  │  └─ <SimilarPostsList>
  │     │  │     └─ <SimilarPostItem> x5
  │     │  │
  │     │  ├─ <ApprovalControls>
  │     │  │  ├─ <ApproveButton>
  │     │  │  ├─ <RejectButton> (triggers Strategist retry)
  │     │  │  └─ <ModifyInput> (edit recommendation)
  │     │
  │     ├─ <CreationStage>
  │     │  └─ <LoadingSpinner> ("Generating draft...")
  │     │
  │     ├─ <ReviewerStage>
  │     │  └─ <LoadingSpinner> ("Checking quality...")
  │     │
  │     └─ <FinalReviewStage>
  │        ├─ <DraftDisplay>
  │        │  ├─ <QualityScore>
  │        │  ├─ <ReviewerSuggestions>
  │        │  └─ <DraftText>
  │        │
  │        └─ <ApprovalControls>
  │           ├─ <ApproveButton>
  │           ├─ <ReviseButton>
  │           ├─ <StartOverButton>
  │           └─ <CopyButton>
  │
  └─ <Footer> (observability links, GitHub)
```

#### Page Layout
```
┌─────────────────────────────────────────────────────────┐
│ HEADER: "Content Strategist" | 🌙 | GitHub | Status    │
├─────────────────────────────────────────────────────────┤
│         │                                               │
│SIDEBAR  │              MAIN CONTENT AREA                │
│         │                                               │
│ Nav     │  ┌─────────────────────────────────────────┐ │
│ ───     │  │ STAGE: Input / Strategy Gate / Draft /   │ │
│ Status  │  │ Final Review                            │ │
│         │  │                                          │ │
│ Active  │  │ [Input/Output Components for Stage]     │ │
│ Stage   │  │                                          │ │
│         │  │ [Controls (Approve/Reject/Modify)]      │ │
│ ───     │  └─────────────────────────────────────────┘ │
│ Logs    │                                               │
│         │  Progress: ████░░░░░░ 40% (Strategy Gate)   │
│         │                                               │
└─────────────────────────────────────────────────────────┘
```

#### Component Details

**InputStage**
```
Input Content Analysis
─────────────────────
[Textarea: "Paste webinar notes or content ideas here..."]

Source: [Dropdown: Webinar Notes / User Paste / LinkedIn Auto]

[ANALYZE BUTTON] (disabled until text entered)
```

**RecommendationCard** (Strategy Gate Output)
```
Recommendation
─────────────
Action: [🟢 REPURPOSE] (color-coded badge)
Confidence: 87% (progress bar)

"Your content matches successful technical posts. Recommend 
repurposing as a LinkedIn thread with expanded examples."

Similar High-Performing Posts (Top 5):
┌─────────────────────────────────────┐
│ "AI in Product Development"         │
│ Impressions: 2,100 | Engagement: 12%│
└─────────────────────────────────────┘
(... 4 more items)

[APPROVE] [REJECT] [MODIFY: ___________]
```

**DraftDisplay** (Final Review)
```
Generated Draft
───────────────
Quality Score: ★★★★☆ 4.2/5.0

Quality Notes: ✓ Clear & concise | ✓ No generic phrases

───────────────────────────────────────
Generated draft text (editable)...
───────────────────────────────────────

[APPROVE FOR PUBLISH] [REVISE DRAFT] [START OVER] [COPY]
```

#### State Management (React Query Pattern)
```typescript
// Main workflow state
const { data: workflowState, status } = useQuery('workflow-state', () =>
  fetch('/api/workflow/state').then(r => r.json())
);

// Mutations for each gate
const approveStrategy = useMutation(() =>
  fetch('/api/workflow/gate/strategy-approve', { method: 'POST' })
);

const approveFinal = useMutation(() =>
  fetch('/api/workflow/gate/final-approve', { method: 'POST' })
);
```

### Implementation Checklist
- [ ] Create component file structure (components/InputStage, components/RecommendationCard, etc)
- [ ] Build InputStage with textarea and source selector
- [ ] Build RecommendationCard displaying Strategist output
- [ ] Implement approval/rejection controls with API calls
- [ ] Build DraftDisplay with quality score and suggestions
- [ ] Add state management with React Query
- [ ] Add error boundaries for graceful error display
- [ ] Add loading spinners for LLM processing stages

---

## GAP 3: LiteLLM Configuration Decision

### Current State
Architecture recommends LiteLLM wrapper for provider abstraction. OpenSpec planning assumes direct Claude/GPT SDK access.

### Design Recommendation: **USE LiteLLM**

#### Rationale
1. **Provider Flexibility**: Swap Claude ↔ GPT mid-demo without code changes (just env var)
2. **Automatic Fallback**: If Claude API fails, auto-retry with GPT
3. **Built-in Rate Limiting**: LiteLLM handles backoff, retries, token counting
4. **Cost Tracking**: Logs token usage and cost per call (useful for monitoring)
5. **Minimal Overhead**: ~5 additional lines per agent call vs direct SDK

#### Implementation Pattern
```python
# Instead of:
from anthropic import Anthropic
client = Anthropic(api_key="sk-...")
response = client.messages.create(...)

# Do this:
from litellm import completion

response = completion(
  model="claude-3-5-sonnet-20241022",  # Or "gpt-4" via env var
  messages=[{"role": "user", "content": "..."}],
  temperature=0.7,
  api_key=os.getenv("ANTHROPIC_API_KEY"),  # Or handled via LiteLLM env config
  fallback_list=["gpt-4-turbo"],  # Fallback if Claude fails
)
```

#### Configuration (.env)
```bash
# Primary provider
LLM_MODEL=claude-3-5-sonnet-20241022
ANTHROPIC_API_KEY=sk-...

# Fallback (if primary fails)
FALLBACK_MODEL=gpt-4-turbo
OPENAI_API_KEY=sk-...

# Optional: LiteLLM cloud proxy (for production)
# LITELLM_API_KEY=...
```

### Decision: **APPROVED** ✅
No additional approval needed. LiteLLM wrapper is low-risk, high-benefit.

### Implementation Checklist
- [ ] Add litellm to requirements.txt
- [ ] Create LLM client wrapper (litellm_client.py) that all agents use
- [ ] Configure fallback models in .env
- [ ] Test provider switching by changing LLM_MODEL env var
- [ ] Verify cost tracking logs in LangSmith

---

## GAP 4: Voice Sample Management Workflow

### Current State
Design says "manual voice samples" but doesn't specify how users provide them or how ingestion works.

### Design Recommendation

#### MVP Workflow
1. **User marks posts as voice samples** → UI shows checkbox on content preview
2. **System stores in voice_samples table** → Associates with content_id
3. **Creator agent retrieves** → Top 3-5 samples (sorted by sample_order)
4. **Included in prompt** → "Write in this voice/style..."

#### Implementation Flow
```
Step 1: Voice Sample Selection UI
─────────────────────────────────
[Frontend] User browses past posts, marks 3-5 as "Voice Sample"
   └─> POST /api/voice-samples/mark
       Body: { content_id: "...", category: "professional" }

Step 2: Backend stores sample
─────────────────────────────
[Backend] Inserts into voice_samples table
  ├─ content_id (references existing post)
  ├─ sample_order (1, 2, 3, ...)
  ├─ sample_category ("professional", "casual", etc)
  └─ extraction_method ("manual_selection")

Step 3: Creator agent retrieves
────────────────────────────────
[Backend] SELECT * FROM voice_samples 
          WHERE content_id IN (user's posts)
          ORDER BY sample_order
          LIMIT 5

Step 4: Included in prompt
──────────────────────────
[Creator Agent] "Based on these voice samples from the user:
  
  [Sample 1 text]
  [Sample 2 text]
  [Sample 3 text]
  
  Write a similar post about: ..."
```

#### Phase 2: Automatic Extraction
```python
# Phase 2 addition (NOT MVP):
def extract_voice_characteristics(posts: List[str]) -> VoiceProfile:
    """Analyze user's posts to extract voice automatically"""
    analysis = llm.analyze(f"""
      Analyze these {len(posts)} posts for:
      1. Tone (professional, casual, humorous, etc)
      2. Sentence structure (long/short, complex/simple)
      3. Vocabulary themes (technical, conversational, etc)
      4. Repetitive phrases or patterns
      
      Posts:
      {"\n".join(posts)}
    """)
    
    return VoiceProfile(
      tone=analysis.tone,
      vocabulary=analysis.vocabulary,
      structure=analysis.structure,
      patterns=analysis.patterns,
    )
```

### Implementation Checklist
- [ ] Add voice_samples table to PostgreSQL schema
- [ ] Create /api/voice-samples/mark endpoint (POST)
- [ ] Create /api/voice-samples/list endpoint (GET)
- [ ] Modify Creator agent prompt to include retrieved samples
- [ ] Build "Mark as Voice Sample" checkbox UI in content preview
- [ ] Test: Mark 5 samples → Creator retrieves them → Uses in prompt

---

## GAP 5: Golden Dataset Creation

### Current State
Design says "15 realistic LinkedIn posts with engagement metrics" but doesn't specify actual content or metrics.

### Design Recommendation

#### Dataset Structure
Create 15 diverse posts across 5 topics, each with realistic engagement patterns:

**Topic: AI & Tech (3 posts)**
```json
{
  "title": "AI in Product Development",
  "content": "Just shipped a feature using Claude API for content analysis...",
  "platform": "linkedin",
  "topic": "AI",
  "content_type": "article",
  "impressions": 2100,
  "clicks": 156,
  "reactions": 287,
  "comments": 42,
  "shares": 18,
  "engagement_rate": 15.8,
  "published_at": "2024-09-01T10:00:00Z"
}
```

**Topic: Productivity (3 posts)**
**Topic: Leadership (3 posts)**
**Topic: Learning (3 posts)**
**Topic: Misc/Personal (3 posts)**

#### Realistic Engagement Ranges (LinkedIn)
- **Low engagement post:** 200-500 impressions, 2-5% engagement rate
- **Medium engagement post:** 1000-2000 impressions, 8-12% engagement rate
- **High engagement post:** 2000-5000 impressions, 12-18% engagement rate

#### Sample Golden Dataset
```
POST 1: "How we use AI to scale content"
├─ Topic: AI
├─ Type: Article/Thread
├─ Impressions: 2,400
├─ Engagement Rate: 14.2%
└─ Use case: Strategist recommends "Repurpose as blog post"

POST 2: "Deep dive: Vector databases explained"
├─ Topic: AI
├─ Type: Technical
├─ Impressions: 3,100
├─ Engagement Rate: 16.8%
└─ Use case: High performer

POST 3: "5 AI tools I use daily"
├─ Topic: AI
├─ Type: List/Quick read
├─ Impressions: 1,800
├─ Engagement Rate: 9.3%
└─ Use case: Medium performer

... (12 more posts)
```

### Implementation Approach

**Option A: Generate Programmatically (Recommended)**
```python
# seed_data.py
GOLDEN_DATASET = [
  {
    "topic": "AI",
    "title": "...",
    "content": "...",
    "engagement_pattern": "high",  # Maps to realistic ranges
  },
  # ... 14 more
]

def seed_database():
    for post in GOLDEN_DATASET:
        # Insert into content table
        # Generate realistic metrics based on pattern
        # Create embeddings via OpenAI API
        # Upload to Pinecone
```

**Option B: Create JSON File + Seed Script**
```
seed_data/
├─ posts.json (15 posts with content + metrics)
└─ seed.sql (INSERT statements)
```

### Implementation Checklist
- [ ] Create 15 diverse posts (CSV or JSON)
- [ ] Add realistic engagement metrics (based on topic/type)
- [ ] Generate embeddings for each post (OpenAI API)
- [ ] Seed PostgreSQL with content + metrics
- [ ] Upload embeddings to Pinecone
- [ ] Verify: Can Strategist query and find similar posts?
- [ ] Test: Strategist makes reasonable recommendations on demo scenarios

---

## Summary Table

| Gap | Status | Resolution | Effort | Timeline |
|-----|--------|-----------|--------|----------|
| PostgreSQL Schema | Designed | Use DDL above | 1-2 hrs | Day 1 morning |
| Frontend UI | Designed | Build components from spec | 3-4 hrs | Day 1 afternoon |
| LiteLLM Config | Approved | Implement wrapper pattern | 0.5-1 hr | Day 1 morning |
| Voice Samples | Designed | Implement mark/retrieve flow | 1-2 hrs | Day 1 afternoon |
| Golden Dataset | Designed | Generate 15 posts + seed | 1-2 hrs | Day 1 morning (parallel) |
| **TOTAL** | **All Resolved** | **Ready for implementation** | **7-11 hrs** | **Day 1** |

---

## Next Steps

1. **Approval Needed?** Review each gap resolution. Any changes or preferences?
2. **Questions?** Ask about any specific design choices
3. **Ready to Implement?** All gaps resolved, ready to code

---

*Document Version: 1.0 | Generated with OpenSpec + Claude Code*
