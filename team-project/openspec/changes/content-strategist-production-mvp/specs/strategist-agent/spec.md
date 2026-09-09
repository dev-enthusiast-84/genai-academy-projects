## Purpose

Analyzes content against historical performance data and recommends optimal actions for repurposing or publishing, using semantic similarity search and performance pattern recognition.

## ADDED Requirements

### Requirement: Content analysis with semantic search
The system SHALL analyze submitted content by querying the performance memory (via Pinecone) for semantically similar past posts and their engagement metrics.

#### Scenario: Similarity search retrieval
- **WHEN** Strategist analyzes a new post about "AI in product development"
- **THEN** it retrieves top 5 similar posts from Pinecone and fetches their engagement metrics from PostgreSQL

#### Scenario: Pattern identification
- **WHEN** similar posts show consistent patterns (e.g., technical deep-dives average 15% engagement)
- **THEN** the agent identifies and uses those patterns in recommendation reasoning

### Requirement: Action recommendation
The system SHALL recommend one of five actions: Publish, Repurpose, Rework, Combine, or Skip, with reasoning based on performance history.

#### Scenario: Successful recommendation
- **WHEN** Strategist analyzes content matching high-performing patterns
- **THEN** it recommends an action (e.g., "Repurpose to blog post") with confidence score and historical reasoning

#### Scenario: Low-confidence recommendation
- **WHEN** content is dissimilar to historical posts (confidence <60%)
- **THEN** the agent flags low confidence and suggests content improvements before deciding

### Requirement: Recommendation with context
The system SHALL return recommendations with sufficient context for user decision-making (reasoning, similar posts, engagement data, suggested format/platform).

#### Scenario: Full recommendation context
- **WHEN** user receives a recommendation
- **THEN** it includes: action, confidence score, 2-3 similar high-performing posts, suggested format/platform, and reasoning explanation

### Requirement: Feedback incorporation
The system SHALL accept user feedback on recommendations and adjust its decision-making for subsequent analyses.

#### Scenario: Feedback routing
- **WHEN** user rejects a recommendation or provides feedback
- **THEN** the feedback is logged and routed back to Strategist for alternative recommendation generation
