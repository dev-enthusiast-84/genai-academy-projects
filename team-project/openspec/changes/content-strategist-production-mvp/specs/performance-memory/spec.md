## Purpose

Maintains a vector-indexed database of user's historical content with performance metrics, enabling semantic similarity search to inform strategic recommendations.

## ADDED Requirements

### Requirement: Content embedding and indexing
The system SHALL generate vector embeddings for all stored content and maintain them in Pinecone for semantic search.

#### Scenario: Post embedding
- **WHEN** new content is stored (published or ingested)
- **THEN** system generates embedding using OpenAI/Claude embeddings API and stores in Pinecone with metadata

#### Scenario: Batch reindexing
- **WHEN** system starts
- **THEN** it ensures all historical posts in PostgreSQL are indexed in Pinecone

### Requirement: Semantic similarity search
The system SHALL support efficient semantic similarity queries to find content similar to new submissions.

#### Scenario: Similarity retrieval
- **WHEN** Strategist agent analyzes new content
- **THEN** it queries Pinecone for top-K similar posts (K=5) using cosine similarity on embeddings

#### Scenario: Metadata filtering
- **WHEN** searching for similar posts
- **THEN** Strategist can optionally filter by topic, format, or date range to refine results

### Requirement: Performance data association
The system SHALL associate performance metrics with each indexed post for pattern analysis.

#### Scenario: Performance-annotated search
- **WHEN** Strategist retrieves similar posts
- **THEN** each result includes engagement metrics: impressions, reactions, engagement_rate, etc.

#### Scenario: Pattern analysis
- **WHEN** Strategist analyzes similar posts
- **THEN** it can identify patterns (e.g., "long-form technical posts average 2100 impressions")

### Requirement: Memory growth and maintenance
The system SHALL efficiently handle growing memory without degrading search performance.

#### Scenario: Incremental indexing
- **WHEN** new posts are added
- **THEN** they are incrementally indexed in Pinecone without requiring full re-indexing

#### Scenario: Pruning old data (optional)
- **WHEN** memory reaches size limits (configurable)
- **THEN** system can archive old posts and remove from active Pinecone index

### Requirement: Voice profile management (MVP)
The system SHALL manage voice profiles from user-provided content samples for consistency checking and generation.

#### Scenario: Voice sample ingestion
- **WHEN** user identifies representative posts as "voice samples"
- **THEN** system stores them in PostgreSQL marked as voice_samples for Creator reference

#### Scenario: Voice profile for Creator
- **WHEN** Creator generates new content
- **THEN** it retrieves stored voice samples (top 3-5) from PostgreSQL and includes them in generation prompt

## IMPLEMENTATION DETAIL: PostgreSQL Schema

The system SHALL use PostgreSQL tables for structured storage with the following schema:

```sql
-- Main content table (historical + new posts)
CREATE TABLE content (
  id UUID PRIMARY KEY,
  created_at TIMESTAMP,
  content_text TEXT NOT NULL,
  platform VARCHAR(50), -- 'linkedin', 'twitter', 'blog', 'newsletter'
  topic VARCHAR(100),
  is_voice_sample BOOLEAN DEFAULT FALSE,
  published_at TIMESTAMP,
  embedding_vector VECTOR(1536) -- For Pinecone sync
);

-- Engagement metrics for published content
CREATE TABLE performance_metrics (
  id UUID PRIMARY KEY,
  content_id UUID REFERENCES content(id),
  impressions INTEGER,
  reactions INTEGER,
  comments INTEGER,
  shares INTEGER,
  engagement_rate FLOAT,
  measured_at TIMESTAMP
);

-- Voice samples (user-marked posts for style reference)
CREATE TABLE voice_samples (
  id UUID PRIMARY KEY,
  content_id UUID REFERENCES content(id),
  sample_order INTEGER, -- 1-5, sorted by priority
  sample_category VARCHAR(50), -- 'professional', 'casual', etc
  extraction_method VARCHAR(50) -- 'manual_selection' or 'auto_extracted'
);
```

## IMPLEMENTATION DETAIL: Voice Sample Management Workflow

### Requirement: Voice sample ingestion
The system SHALL provide a workflow for users to mark content as voice samples for Creator reference.

#### Scenario: Mark as voice sample (MVP)
- **WHEN** user browses past posts in UI
- **THEN** user can mark 3-5 posts with checkbox "Use as voice sample"
- **AND** system stores marked posts in voice_samples table with sample_order

#### Scenario: Retrieve voice samples for Creator
- **WHEN** Creator agent runs
- **THEN** system queries: `SELECT * FROM voice_samples ORDER BY sample_order LIMIT 5`
- **AND** includes full text in Creator prompt: "Write in this voice/style..."

#### Scenario: Voice sample categories (Phase 2 enhancement)
- **WHEN** marking voice sample, user can tag: 'professional', 'casual', 'storytelling', 'technical'
- **THEN** system filters by category when user specifies tone preference

## PHASE 2: Automatic Voice Extraction (Future Improvement)

### Requirement: Voice characteristic extraction
The system SHALL automatically extract and index voice characteristics from historical content.

#### Scenario: Automatic extraction
- **WHEN** posts are added to memory
- **THEN** system analyzes tone, vocabulary, sentence structure, and stores extracted voice characteristics

#### Scenario: Continuous voice refinement
- **WHEN** more content is added over time
- **THEN** system refines voice profile based on patterns in actual published content (user's evolving voice)
