## Purpose

Defines the golden dataset for MVP demo and schema initialization strategy for production readiness.

## ADDED Requirements

### Requirement: Golden dataset initialization
The system SHALL seed 15 realistic LinkedIn posts with varied topics and engagement patterns for MVP demonstration.

#### Scenario: Dataset composition
- **GIVEN** 5 topic categories: AI/Tech, Productivity, Leadership, Learning, Misc
- **WHEN** system initializes
- **THEN** database is populated with 3 posts per category (15 total)
- **AND** each post has realistic engagement metrics (impressions, reactions, comments, shares)
- **AND** engagement rates reflect realistic LinkedIn patterns (2%-18%)

#### Scenario: Engagement pattern variety
- **WHEN** golden dataset is created
- **THEN** posts include low-engagement (2%-5%), medium (8%-12%), and high (12%-18%) performers
- **AND** Strategist agent can identify and use patterns in recommendations
- **AND** different topics show different average engagement to test topic-aware recommendations

#### Scenario: Embeddings generation
- **WHEN** dataset is seeded
- **THEN** system generates vector embeddings for all 15 posts (via OpenAI API)
- **AND** embeddings are stored in both PostgreSQL and Pinecone
- **AND** similarity search can retrieve semantically related posts for test scenarios

### Requirement: Schema versioning and migrations
The system SHALL support schema migrations for safe database updates.

#### Scenario: Initial schema creation
- **WHEN** system starts for first time
- **THEN** it automatically runs schema.sql to create all tables
- **AND** indexes are created for performance optimization
- **AND** schema version is recorded for future migrations

#### Scenario: Idempotent migrations
- **WHEN** deployment process runs
- **THEN** it checks schema version and only applies new migrations
- **AND** migrations can be safely re-run without data loss (idempotent)

## IMPLEMENTATION DETAIL: Golden Dataset Specification

### Dataset Structure
```json
{
  "posts": [
    {
      "id": "post-ai-001",
      "topic": "AI",
      "title": "How we use Claude API for content analysis",
      "content": "Just shipped a feature using Claude API...",
      "platform": "linkedin",
      "content_type": "article",
      "impressions": 2400,
      "reactions": 287,
      "comments": 42,
      "shares": 18,
      "engagement_rate": 14.2,
      "published_at": "2024-09-01T10:00:00Z"
    },
    // ... 14 more posts
  ]
}
```

### Topic Distribution
- **AI & Tech (3)**: Deep technical, product updates, framework tutorials
  - Avg engagement: 14-16%
  - Use case: High performers, good for repurposing strategy

- **Productivity (3)**: Time management, workflow hacks, tools reviews
  - Avg engagement: 9-12%
  - Use case: Medium performers, good for thread format

- **Leadership (3)**: Management tips, team building, career advice
  - Avg engagement: 8-11%
  - Use case: Moderate engagement, good for personal brand

- **Learning (3)**: Skill-building, course reviews, growth mindset
  - Avg engagement: 10-13%
  - Use case: Solid performers across audience

- **Misc/Personal (3)**: Stories, reflections, community posts
  - Avg engagement: 5-10%
  - Use case: Lower engagement baseline for comparison

### Engagement Ranges (Realistic LinkedIn)
- **Low engagement**: 200-800 impressions, 2-5% rate
- **Medium engagement**: 1000-2500 impressions, 8-12% rate
- **High engagement**: 2000-5000 impressions, 12-18% rate

## IMPLEMENTATION DETAIL: Schema and Initialization SQL

See `schema.sql` in project root for complete DDL:
- `content` table: Posts with embeddings
- `performance_metrics` table: Engagement data
- `voice_samples` table: User-marked style examples
- `decisions` table: User approval/rejection logs
- `workflow_runs` table: Execution tracking

Initialization process:
1. Run `schema.sql` → Creates all tables
2. Run `seed_data.py` → Generates 15 posts + metrics
3. Call OpenAI embeddings API → Create vectors
4. Upload to Pinecone → Populate vector index
5. Verify: Semantically search 5 test queries → Confirm retrieval works

## Phase 2: Real Data Integration

### Requirement: Replace golden data with real LinkedIn API
In Phase 2, golden dataset is replaced with real LinkedIn posts via API polling (requires enterprise approval).

#### Migration path:
- Same PostgreSQL schema (no changes needed)
- Same Pinecone index (just different embeddings)
- Strategist agent code unchanged
- Only data source changes (API vs seed file)
